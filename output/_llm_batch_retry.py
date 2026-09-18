"""补跑指定批次目录中的失败例（api_error/engine_error/parse_error），追加写 batch_retry.jsonl。
_analyze 按 id 去重后批次覆盖，retry 文件排序在最后故生效。
用法: LLM_BATCH_DIR=output/llm_batch_20260818_v4 python3 output/_llm_batch_retry.py"""
import glob
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import _llm_batch_trainset as bt  # noqa: E402  内部已把项目根插入 sys.path

import yaml  # noqa: E402

from mangpai.subjective.llm_prompt import build_system_prompt  # noqa: E402
from mangpai.subjective.prompts.hao_style_fewshot import (  # noqa: E402
    FEWSHOT_EXAMPLES, format_fewshot_block)

done = {}
for p in sorted(glob.glob(os.path.join(bt.OUT_DIR, 'batch_*.jsonl'))):
    for line in open(p, encoding='utf-8'):
        r = json.loads(line)
        done[r['id']] = r
todo = {rid for rid, r in done.items()
        if 'api_error' in r or 'engine_error' in r or 'parse_error' in r}
with open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'),
          encoding='utf-8') as f:
    cases = [c for c in yaml.safe_load(f) if c['id'] in todo]
print(f'retry {len(cases)} cases in {bt.OUT_DIR}')
if not cases:
    sys.exit(0)

system = build_system_prompt(format_fewshot_block(FEWSHOT_EXAMPLES))
with ThreadPoolExecutor(max_workers=8) as ex:
    recs = list(ex.map(lambda c: bt.run_case(c, system), cases))
out = os.path.join(bt.OUT_DIR, 'batch_retry.jsonl')
with open(out, 'a', encoding='utf-8') as f:
    for r in recs:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
n_err = sum(1 for r in recs if 'api_error' in r or 'engine_error' in r)
# S1：未知 provider cost_cny=None（未计价），不计入汇总；cost_usd=历史批兼容键
cost = sum(r.get('cost_cny') or r.get('cost_usd') or 0 for r in recs)
print(f'done -> {out} | still_error={n_err} cost=¥{cost:.2f}')
