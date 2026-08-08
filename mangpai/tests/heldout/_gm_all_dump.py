# -*- coding: utf-8 -*-
"""官命全量115例 dump：供候选修法模拟。纯分析用。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml
from blind_eval import _bazi_data
from mangpai import MangpaiEngine

cases = yaml.safe_load(open(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), encoding='utf-8'))
out = {}
for c in cases:
    v = (c.get('verdicts') or {}).get('官命')
    if not v:
        continue
    bd = _bazi_data(c)
    res = MangpaiEngine(bd).compute_all()
    gm = res.get('guanming', {})
    combo = gm.get('combo', {})
    out[c['id']] = {
        'bazi': ''.join(bd['bazi'][k] for k in ('year', 'month', 'day', 'hour')),
        'gender': bd.get('input', {}).get('gender', ''),
        'verdict': v,
        'expect': v.startswith('是'),
        'is_guanming': bool(gm.get('is_guanming')),
        'vetoed': gm.get('vetoed'),
        'veto_reasons': gm.get('veto_reasons') or [],
        'combos': combo.get('zhiyong_combos') or [],
        'shengyong': combo.get('shengyong_huayong') or [],
        'has_guansha': combo.get('has_guansha'),
        'details': combo.get('details') or [],
    }
json.dump(out, open('/tmp/gm_all.json', 'w'), ensure_ascii=False, indent=1)
n_ok = sum(1 for e in out.values() if e['is_guanming'] == e['expect'])
print(f'total={len(out)} acc={n_ok}/{len(out)} = {n_ok/len(out):.2%}')
