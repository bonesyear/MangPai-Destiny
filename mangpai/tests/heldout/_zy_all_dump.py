# -*- coding: utf-8 -*-
"""全量 dump：trainset+heldout 所有职业可评例的桶分/evidence/结构特征。
用途：收窄条款的回归面评估（22✅ trainset + 21✅ heldout 商人三例）。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml
from blind_eval import _bazi_data, _ZY_RULES, _ZY_EXCLUDE
from mangpai import MangpaiEngine
from mangpai.subjective.zhiye import _pillar_cats
from mangpai.objective.shensha import compute_shensha_ext

PILLAR_KEYS = ('year', 'month', 'day', 'hour')


def gold_buckets(verdict):
    buckets = set()
    for kws, bucket in _ZY_RULES:
        if any(x in verdict for x in _ZY_EXCLUDE.get(bucket, ())):
            continue
        if any(k in verdict for k in kws):
            buckets.add(bucket)
    return sorted(buckets)


out = {}
for split, path in (('trainset', os.path.join(_HERE, '..', 'trainset', 'cases.yaml')),
                    ('heldout', os.path.join(_HERE, 'cases.yaml'))):
    for c in yaml.safe_load(open(path, encoding='utf-8')):
        v = (c.get('verdicts') or {}).get('职业')
        if not v:
            continue
        gold = gold_buckets(v)
        if not gold:
            continue
        bd = _bazi_data(c)
        res = MangpaiEngine(bd).compute_all()
        zy = res.get('zhiye', {})
        gans = [bd['bazi'][k][0] for k in PILLAR_KEYS]
        zhis = [bd['bazi'][k][1] for k in PILLAR_KEYS]
        day_gan = gans[2]
        pcats = [sorted(_pillar_cats(day_gan, gans[i], zhis[i])) for i in range(4)]
        try:
            ss = compute_shensha_ext(day_gan, zhis)
        except Exception:
            ss = {}
        out[split + ':' + c['id']] = {
            'split': split, 'id': c['id'],
            'bazi': ''.join(bd['bazi'][k] for k in PILLAR_KEYS),
            'verdict': v, 'gold': gold,
            'primary': zy.get('primary', ''),
            'scores': zy.get('scores', {}),
            'evidence': {k: v2 for k, v2 in (zy.get('evidence') or {}).items() if v2},
            'pcats': pcats,
            'yangren': bool((ss.get('羊刃') or {}).get('in_pillars')),
            'tao': bool((ss.get('桃花') or {}).get('in_pillars')),
            'is_guanming': bool(res.get('guanming', {}).get('is_guanming')),
            'caiming_tier': res.get('caiming', {}).get('tier_static', ''),
        }

json.dump(out, open('/tmp/zy_all.json', 'w'), ensure_ascii=False, indent=1)
print(f'dumped {len(out)} cases -> /tmp/zy_all.json')

# heldout 商人三例专项
for k in ('heldout:ans10', 'heldout:li002', 'heldout:li131'):
    e = out.get(k)
    if not e:
        print(f'{k}: NOT FOUND'); continue
    print(f"\n== {k} {e['bazi']} verdict={e['verdict'][:30]} primary={e['primary']} ==")
    print('  scores:', e['scores'])
    print('  merchant ev:', e['evidence'].get('merchant'))
    print('  pcats:', e['pcats'])
