"""汇总 output/llm_batch_20260818/*.jsonl → 达标判定 + 违规分布。
用法: python3 output/_llm_batch_analyze.py [batch_dir]"""
import glob
import json
import os
import re
import sys
from collections import Counter

batch_dir = (sys.argv[1] if len(sys.argv) > 1 else
             os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          'llm_batch_20260818'))
recs = []
for p in sorted(glob.glob(os.path.join(batch_dir, 'batch_*.jsonl'))):
    for line in open(p, encoding='utf-8'):
        recs.append(json.loads(line))

# 去重（按 id，后批次覆盖）
seen = {}
for r in recs:
    seen[r['id']] = r
recs = list(seen.values())

n = len(recs)
api_err = [r for r in recs if 'api_error' in r or 'engine_error' in r]
parse_err = [r for r in recs if 'parse_error' in r]
valid = [r for r in recs if 'violations' in r]

by_layer = Counter()
by_dim = Counter()
by_path = Counter()
case_layer = Counter()  # 每例是否含该层违规
n1_cases = []
for r in valid:
    layers = set()
    for v in r['violations']:
        by_layer[v['layer']] += 1
        layers.add(v['layer'])
        m = re.match(r'([^\s.：「(]+)', v['detail'])
        if m:
            by_dim[m.group(1)] += 1
        if v['layer'] == 'L1':
            pm = re.search(r': (\S+)$', v['detail'])
            if pm:
                top = pm.group(1).split('.')[0]
                by_path[top] += 1
        if v['layer'] == 'N1':
            n1_cases.append(r['id'])
    for L in layers:
        case_layer[L] += 1

nv = len(valid)
print(f'总例数={n} api/engine错误={len(api_err)} JSON解析失败(L0级)={len(parse_err)}')
print(f'有效校验例={nv}')
for L in ('L0', 'L1', 'L2', 'N1'):
    c = case_layer[L]
    print(f'{L}: 违规例={c} ({c / max(nv, 1) * 100:.2f}%) 违规条数={by_layer[L]}')
print('\n违规维度分布:', by_dim.most_common(15))
print('\nL1 无出处路径 top 键:', by_path.most_common(15))
# S1：未知 provider cost_cny=None（未计价），不计入汇总；cost_cny 为现行键；cost_usd=历史批兼容（值已是人民币口径）
cost = sum(r.get('cost_cny') or r.get('cost_usd') or 0 for r in recs)
pin = sum((r.get('usage') or {}).get('prompt_tokens', 0) for r in recs)
pout = sum((r.get('usage') or {}).get('completion_tokens', 0) for r in recs)
el = [r.get('elapsed_s', 0) for r in recs if r.get('elapsed_s')]
print(f'\n成本: ¥{cost:.2f} | tokens in={pin} out={pout}')
print(f'耗时: mean={sum(el) / max(len(el), 1):.1f}s max={max(el) if el else 0:.1f}s')
if api_err:
    print('\napi 错误例:', [(r['id'], r.get('api_error', r.get('engine_error'))[:80]) for r in api_err])
if parse_err:
    print('\n解析失败例:', [r['id'] for r in parse_err])
