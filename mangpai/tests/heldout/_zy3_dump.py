# -*- coding: utf-8 -*-
"""职业批3 dump：在 _zy_all_dump 基础上增方向信号/强弱/主气/动作对，供 _zy3_sim 规则网格。"""
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
from mangpai.subjective.zhiye import (
    _pillar_cats, _main_qi_cats, _main_qi_char_count, _pos_idx,
    _HE_TYPES, _ZHI_TYPES)
from mangpai.subjective.yongshen import assess_direction_signals, classify_strength
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
        try:
            ss = compute_shensha_ext(day_gan, zhis)
        except Exception:
            ss = {}
        rel = res.get('relations') or {}
        wa = rel.get('work_actions') or []
        non_aux = [a for a in wa if not a.get('auxiliary')]
        pairs = []
        for a in non_aux:
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi < 0 or ti < 0:
                continue
            pairs.append({'t': a.get('type', ''),
                          'fp': a.get('from_pos', ''), 'tp': a.get('to_pos', ''),
                          'fz': zhis[fi], 'tz': zhis[ti],
                          'fg': gans[fi] if a.get('from_pos', '').endswith('_gan') else '',
                          'tg': gans[ti] if a.get('to_pos', '').endswith('_gan') else ''})
        try:
            ds = assess_direction_signals(
                day_gan, gans, zhis, relations=rel,
                yunfan_result=res.get('yunfan_current'))
        except Exception:
            ds = {}
        try:
            strength = str(classify_strength(day_gan, gans, zhis))
        except Exception:
            strength = ''
        # 复刻 M2 比劫参与做功判据
        bijiao_work = False
        work_zhis = set()
        for a in non_aux:
            if a.get('type', '') not in _HE_TYPES and a.get('type', '') not in _ZHI_TYPES:
                continue
            for pos in (a.get('from_pos', ''), a.get('to_pos', '')):
                i = _pos_idx(pos)
                if i < 0:
                    continue
                work_zhis.add(zhis[i])
                if '比劫' in _pillar_cats(day_gan, gans[i], zhis[i]):
                    bijiao_work = True
        cm = res.get('caiming', {}) or {}
        out[split + ':' + c['id']] = {
            'split': split, 'id': c['id'],
            'bazi': ''.join(bd['bazi'][k] for k in PILLAR_KEYS),
            'verdict': v, 'gold': gold,
            'primary': zy.get('primary', ''),
            'scores': zy.get('scores', {}),
            'evidence': {k: v2 for k, v2 in (zy.get('evidence') or {}).items() if v2},
            'pcats': [sorted(_pillar_cats(day_gan, gans[i], zhis[i])) for i in range(4)],
            'main_qi': [sorted(_main_qi_cats(day_gan, gans, zhis, i)) for i in range(4)],
            'gs_main_char': _main_qi_char_count(day_gan, gans, zhis, '官杀'),
            'cai_main_char': _main_qi_char_count(day_gan, gans, zhis, '财'),
            'yangren': bool((ss.get('羊刃') or {}).get('in_pillars')),
            'tao': bool((ss.get('桃花') or {}).get('in_pillars')),
            'is_guanming': bool(res.get('guanming', {}).get('is_guanming')),
            'caiming_tier': cm.get('tier_static', ''),
            'methods': (cm.get('qucai_method') or {}).get('methods') or [],
            'fanju_caixing': bool(ds.get('fanju_caixing')),
            'natal_fanju': bool(ds.get('fanju')) and not bool(ds.get('suiyun_fanju')),
            'suiyun_fanju': bool(ds.get('suiyun_fanju')),
            'mingju_xiong': bool(ds.get('mingju_xiong')),
            'pocai_severe': bool(ds.get('pocai_severe')),
            'yongshen_xiong': bool(ds.get('yongshen_xiong')),
            'strength': strength,
            'bijiao_work': bijiao_work,
            'work_zhis': sorted(work_zhis),
            'pairs': pairs,
            'base_career': (zy.get('base_career') or {}).get('bucket', ''),
        }

json.dump(out, open('/tmp/zy3_all.json', 'w'), ensure_ascii=False, indent=1)
print(f'dumped {len(out)} cases -> /tmp/zy3_all.json')
n_err = sum(1 for e in out.values()
            if e['primary'] and e['primary'] not in e['gold'])
n_ok = sum(1 for e in out.values() if e['primary'] in e['gold'])
n_warn = len(out) - n_err - n_ok
print(f'total ✅{n_ok} ⚠️{n_warn} ❌{n_err}')
