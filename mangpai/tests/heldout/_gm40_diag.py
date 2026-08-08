# -*- coding: utf-8 -*-
"""官命40❌诊断：重跑引擎，输出 combo/veto/level 全量明细。纯分析用。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml
from blind_eval import _bazi_data, score_guanming
from mangpai import MangpaiEngine

snap = json.load(open(os.path.join(_HERE, 'snapshots', '20260808_p.json')))
bad_ids = [k for k, v in snap['trainset'].items()
           if v.get('scores', {}).get('官命') == '❌']
print(f'❌ count={len(bad_ids)}')

cases = {c['id']: c for c in yaml.safe_load(
    open(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), encoding='utf-8'))}

out = {}
for cid in bad_ids:
    c = cases[cid]
    bd = _bazi_data(c)
    res = MangpaiEngine(bd).compute_all()
    gm = res.get('guanming', {})
    verdict = c.get('verdicts', {}).get('官命', '')
    expect = verdict.startswith('是')
    got = bool(gm.get('is_guanming'))
    fpfn = 'fp' if (got and not expect) else ('fn' if (expect and not got) else '??')
    combo = gm.get('combo', {})
    lvl = gm.get('level', {})
    bz = bd['bazi']
    out[cid] = {
        'bazi': bz['year'] + bz['month'] + bz['day'] + bz['hour'],
        'gender': bd.get('input', {}).get('gender', ''),
        'dayun': c.get('dayun', ''), 'liunian': c.get('liunian', ''),
        'verdict': verdict,
        'fpfn': fpfn,
        'is_guanming': got,
        'vetoed': gm.get('vetoed'),
        'veto_reasons': gm.get('veto_reasons'),
        'combos': combo.get('zhiyong_combos'),
        'shengyong': combo.get('shengyong_huayong'),
        'has_guansha': combo.get('has_guansha'),
        'combo_details': combo.get('details'),
        'guancai_daimao': gm.get('guancai_daimao', {}).get('found'),
        'level_grade': lvl.get('grade'),
        'level_num': lvl.get('level'),
        'authority': lvl.get('authority'),
        'summary': gm.get('summary'),
        # 联动面
        'caiming_tier': (res.get('caiming', {}) or {}).get('tier_static')
                        or (res.get('caiming', {}) or {}).get('tier'),
        'zhiye_primary': (res.get('zhiye', {}) or {}).get('primary'),
        'other_verdicts': {k: v for k, v in c.get('verdicts', {}).items()
                           if k != '官命'},
        'other_scores': snap['trainset'][cid].get('scores', {}),
    }

json.dump(out, open('/tmp/gm40.json', 'w'), ensure_ascii=False, indent=1)
for cid, e in out.items():
    print(f"\n=== {cid} [{e['fpfn']}] {e['bazi']} {e['gender']} 运:{e['dayun'] or '-'} 年:{e['liunian'] or '-'}")
    print(f"  verdict: {e['verdict']}  | engine is_guanming={e['is_guanming']} vetoed={e['vetoed']}")
    print(f"  combos={e['combos']} shengyong={e['shengyong']} has_guansha={e['has_guansha']} guancai={e['guancai_daimao']}")
    print(f"  level={e['level_num']} {e['level_grade']} | {e['authority']}")
    if e['veto_reasons']:
        for r in e['veto_reasons']:
            print(f"  VETO: {r[:150]}")
    print(f"  联动: 财={e['caiming_tier']} 职={e['zhiye_primary']} | other_verdicts={json.dumps(e['other_verdicts'], ensure_ascii=False)} | other_scores={e['other_scores']}")
