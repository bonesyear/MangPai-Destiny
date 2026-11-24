"""补跑最新记录中的失败例，保留所有尝试；按 run_id/timestamp 合并。
用法: LLM_BATCH_DIR=output/<批次目录> python3 output/_llm_batch_retry.py"""
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _llm_batch_trainset as bt
import yaml

from _eval_common import load_batch, summarize_costs

attempts, latest = load_batch(bt.OUT_DIR)
todo = {r['id'] for r in latest
        if 'api_error' in r or 'engine_error' in r or 'parse_error' in r}
with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'), encoding='utf-8') as f:
    cases = [c for c in yaml.safe_load(f) if c['id'] in todo]
print(f'retry {len(cases)} cases in {bt.OUT_DIR}')
if not cases:
    sys.exit(0)

state = bt._budget_state(attempts)
with ThreadPoolExecutor(max_workers=8) as ex:
    recs = list(ex.map(lambda c: bt.run_case(c, state), cases))
out = os.path.join(bt.OUT_DIR, 'batch_retry.jsonl')
with open(out, 'a', encoding='utf-8') as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
        f.flush()
n_err = sum(1 for r in recs
            if 'api_error' in r or 'engine_error' in r or 'parse_error' in r)
costs = summarize_costs(attempts + recs)
print(f'done -> {out} | still_error={n_err} '
      f'cost=¥{costs["cost_cny"]:.2f} + ${costs["cost_usd"]:.4f}（分币别）')
