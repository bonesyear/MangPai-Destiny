"""trainset 294 例批量过 llm_channel（validate=mark 语义：收集违规不阻塞）。

纯评估脚本：只读引擎输出 + LLM 叙述，零引擎改动，LLM 输出不落 compute_all dict。
用法: python3 output/_llm_batch_trainset.py [start] [end]   # 例: 0 98
产出: output/llm_batch_20260818/batch_<start>_<end>.jsonl
"""
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import yaml  # noqa: E402

from mangpai.engine import MangpaiEngine  # noqa: E402
from mangpai.subjective import build_payload  # noqa: E402
from mangpai.subjective.llm_backend import call_deepseek, LLMBackendError  # noqa: E402
from mangpai.subjective.llm_channel import validate_reading  # noqa: E402
from mangpai.subjective.llm_prompt import build_system_prompt, build_user_prompt  # noqa: E402
from mangpai.subjective.narrative import _bazi_line  # noqa: E402
from mangpai.subjective.prompts.hao_style_fewshot import (  # noqa: E402
    FEWSHOT_EXAMPLES, format_fewshot_block)

OUT_DIR = os.environ.get('LLM_BATCH_DIR') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'llm_batch_20260818')


def run_case(case, system):
    rec = {'id': case['id'], 'name': case.get('name', '')}
    bazi_data = {
        'bazi': dict(case['bazi']), 'shishen': {}, 'kong_wang': {},
        'di_zhi_relations': {},
        'input': {'gender': case.get('gender', '男'), 'year': case.get('year', 1960)},
    }
    t0 = time.monotonic()
    try:
        res = MangpaiEngine(bazi_data).compute_all()
    except Exception as e:
        rec['engine_error'] = repr(e)
        return rec
    features = build_payload(res)
    features_json = json.dumps(features, ensure_ascii=False, separators=(',', ':'))
    user = build_user_prompt(features_json, _bazi_line(res), features=features)
    try:
        resp = call_deepseek(system, user)
    except LLMBackendError as e:
        rec['api_error'] = str(e)
        return rec
    rec['usage'] = resp['usage']
    rec['cost_cny'] = resp['cost_cny']
    rec['elapsed_s'] = round(time.monotonic() - t0, 2)
    rec['model'] = resp['model']
    try:
        data = json.loads(resp['text'])
    except json.JSONDecodeError as e:
        rec['parse_error'] = str(e)
        rec['raw'] = resp['text'][:500]
        return rec
    report = validate_reading(data, features, res)
    rec['ok'] = report['ok']
    rec['violations'] = report['violations']
    rec['reading'] = data  # 留存供违规分析
    return rec


def main():
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 10**9
    with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
              encoding='utf-8') as f:
        cases = yaml.safe_load(f)[start:end]
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f'batch_{start}_{start + len(cases)}.jsonl')
    system = build_system_prompt(format_fewshot_block(FEWSHOT_EXAMPLES))

    with ThreadPoolExecutor(max_workers=8) as ex:
        recs = list(ex.map(lambda c: run_case(c, system), cases))
    with open(out_path, 'w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    n_err = sum(1 for r in recs if 'api_error' in r or 'engine_error' in r)
    n_parse = sum(1 for r in recs if 'parse_error' in r)
    n_bad = sum(1 for r in recs if not r.get('ok', True) and 'violations' in r)
    # S1：未知 provider cost_cny=None（未计价），不计入汇总；cost_usd=历史批兼容键
    cost = sum(r.get('cost_cny') or r.get('cost_usd') or 0 for r in recs)
    print(f'done {len(recs)} cases -> {out_path}')
    print(f'api/engine errors={n_err} parse_errors={n_parse} '
          f'violating={n_bad} cost=¥{cost:.2f}')
    # H-fix-2c：批跑单例失败不中断整批，但不静默——失败案例清单显式列出
    err_ids = [r['id'] for r in recs if 'api_error' in r or 'engine_error' in r]
    if err_ids:
        print(f'!! 失败案例({len(err_ids)}): {", ".join(err_ids)}')


if __name__ == '__main__':
    main()
