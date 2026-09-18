"""对已跑批次留存的 reading 离线重评分（引擎确定性重算，零 API 成本）。
用法: python3 output/_llm_batch_rescore.py output/llm_batch_20260818_v3"""
import glob, json, os, sys
from collections import Counter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import yaml
from mangpai.engine import MangpaiEngine
from mangpai.subjective import build_payload
from mangpai.subjective.llm_channel import validate_reading

batch_dir = sys.argv[1]
recs = {}
for p in sorted(glob.glob(os.path.join(batch_dir, 'batch_*.jsonl'))):
    for line in open(p, encoding='utf-8'):
        r = json.loads(line); recs[r['id']] = r
cases = {c['id']: c for c in yaml.safe_load(open(os.path.join(ROOT, 'mangpai/tests/trainset/cases.yaml'), encoding='utf-8'))}

case_layer = Counter(); by_layer = Counter(); l2_details = []
nv = 0
for cid, r in recs.items():
    if 'reading' not in r:
        continue
    c = cases[cid]
    bazi_data = {'bazi': dict(c['bazi']), 'shishen': {}, 'kong_wang': {},
                 'di_zhi_relations': {},
                 'input': {'gender': c.get('gender', '男'), 'year': c.get('year', 1960)}}
    res = MangpaiEngine(bazi_data).compute_all()
    rep = validate_reading(r['reading'], build_payload(res), res)
    nv += 1
    layers = set()
    for v in rep['violations']:
        by_layer[v['layer']] += 1; layers.add(v['layer'])
        if v['layer'] == 'L2':
            l2_details.append((cid, v['detail']))
    for L in layers:
        case_layer[L] += 1
print(f'重评分例数={nv}')
for L in ('L0', 'L1', 'L2', 'N1'):
    print(f'{L}: 违规例={case_layer[L]} ({case_layer[L]/max(nv,1)*100:.2f}%) 条数={by_layer[L]}')
print('\nL2 明细:')
for x in sorted(l2_details):
    print(' ', x[0], '|', x[1])
