"""trainset 批量过 llm_channel（validate=mark），每例完成即追加落盘。
用法: python3 output/_llm_batch_trainset.py [start] [end]
默认每次使用独立目录；LLM_BATCH_DIR 可显式指定，LLM_BATCH_RUN_ID 可指定运行号。
"""
import hashlib
import json
import os
import sys
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import yaml

from _eval_common import (
    FEWSHOT_CONTAMINATED_IDS, engine_fe, load_batch, summarize_costs)
from mangpai.subjective.llm_backend import (
    call_deepseek, LLMBackendError, _API_URL, _env_value)
from mangpai.subjective.llm_channel import build_prompts, validate_reading
from mangpai.tests.heldout.blind_eval import _git_sha, _worktree_meta

RUN_ID = os.environ.get('LLM_BATCH_RUN_ID') or datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
OUT_DIR = os.environ.get('LLM_BATCH_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), f'llm_batch_{RUN_ID}')
AS_OF_YEAR = int(os.environ.get('MANGPAI_AS_OF_YEAR', datetime.now().year))
ENGINE_SHA = {'git_sha': _git_sha(), **_worktree_meta()}


def _budget_state(records=()):
    return {
        'cap': float(os.environ.get('MANGPAI_LLM_BUDGET_CNY', '0') or 0),
        'spent': sum(r.get('cost_cny') or 0 for r in records),
        'lock': threading.Lock(),
    }


def _account(rec, state):
    if state:
        with state['lock']:
            state['spent'] += rec.get('cost_cny') or 0


def run_case(case, state=None):
    rec = {
        'id': case['id'], 'name': case.get('name', ''), 'run_id': RUN_ID,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'engine_sha': ENGINE_SHA, 'as_of_year': case.get('as_of_year', AS_OF_YEAR),
        'fewshot_contamination': case['id'] in FEWSHOT_CONTAMINATED_IDS,
    }
    try:
        if state and state['cap'] > 0:
            with state['lock']:
                if state['spent'] >= state['cap']:
                    rec['api_error'] = '累计费用预算已耗尽'
                    rec['budget_exceeded'] = True
                    return rec
        case = dict(case, as_of_year=rec['as_of_year'])
        try:
            res, features = engine_fe(case)
        except Exception as e:
            rec['engine_error'] = repr(e)
            return rec
        rec['features'] = features
        system, user = build_prompts(res)
        rec['prompt_sha256'] = hashlib.sha256(system.encode('utf-8')).hexdigest()
        t0 = time.monotonic()
        try:
            resp = call_deepseek(system, user)
        except LLMBackendError as e:
            rec['api_error'] = str(e)
            if hasattr(e, 'usage'):
                rec['usage'] = e.usage
                rec['cost_cny'] = e.cost_cny
            return rec
        rec['usage'] = resp['usage']
        rec['cost_cny'] = resp['cost_cny']
        rec['elapsed_s'] = round(time.monotonic() - t0, 2)
        rec['model'] = resp['model']
        rec['requested_model'] = resp.get('requested_model', resp['model'])
        endpoint = resp.get('endpoint') or _env_value('MANGPAI_LLM_BASE_URL', '') or _API_URL
        rec['endpoint_host'] = urllib.parse.urlsplit(endpoint).hostname or ''
        rec['thinking'] = resp.get(
            'thinking', (_env_value('MANGPAI_LLM_THINKING', '1') or '1') != '0')
        try:
            data = json.loads(resp['text'])
        except json.JSONDecodeError as e:
            rec['parse_error'] = str(e)
            rec['raw'] = resp['text'][:500]
            return rec
        report = validate_reading(data, features, res)
        rec['ok'] = report['ok']
        rec['violations'] = report['violations']
        rec['reading'] = data
        return rec
    finally:
        _account(rec, state)


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
    with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
              encoding='utf-8') as f:
        cases = yaml.safe_load(f)[start:end]
    os.makedirs(OUT_DIR, exist_ok=True)
    attempts, _ = load_batch(OUT_DIR)
    state = _budget_state(attempts)
    out_path = os.path.join(OUT_DIR, f'batch_{start}_{start + len(cases)}.jsonl')
    recs = []
    with ThreadPoolExecutor(max_workers=8) as ex, open(out_path, 'a', encoding='utf-8') as f:
        futures = [ex.submit(run_case, case, state) for case in cases]
        for future in as_completed(futures):
            rec = future.result()
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            f.flush()
            recs.append(rec)
    n_err = sum(1 for r in recs if 'api_error' in r or 'engine_error' in r)
    n_parse = sum(1 for r in recs if 'parse_error' in r)
    n_bad = sum(1 for r in recs if not r.get('ok', True) and 'violations' in r)
    costs = summarize_costs(attempts + recs)
    print(f'done {len(recs)} cases -> {out_path} | run_id={RUN_ID}')
    print(f'api/engine errors={n_err} parse_errors={n_parse} violating={n_bad} '
          f'cost=¥{costs["cost_cny"]:.2f} + ${costs["cost_usd"]:.4f}（分币别）')
    err_ids = [r['id'] for r in recs if 'api_error' in r or 'engine_error' in r]
    if err_ids:
        print(f'!! 失败案例({len(err_ids)}): {", ".join(err_ids)}')


if __name__ == '__main__':
    main()
