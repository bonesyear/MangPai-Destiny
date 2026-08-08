# -*- coding: utf-8 -*-
"""职业55❌全量 dump：逐例桶分/evidence/方向信号/官命联动。纯分析用。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml
from blind_eval import _bazi_data, score_zhiye, _ZY_RULES, _ZY_EXCLUDE
from mangpai import MangpaiEngine
from mangpai.subjective.yongshen import assess_direction_signals
from mangpai.objective.zuogong_detect import detect_relations

snap = json.load(open(os.path.join(_HERE, 'snapshots', '20260808_q.json'), encoding='utf-8'))
ts = snap['trainset']
bad_ids = [cid for cid, e in ts.items() if (e.get('scores') or {}).get('职业') == '❌']
assert len(bad_ids) == 55, len(bad_ids)

cases = {c['id']: c for c in yaml.safe_load(
    open(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), encoding='utf-8'))}


def gold_buckets(verdict):
    buckets = set()
    for kws, bucket in _ZY_RULES:
        if any(x in verdict for x in _ZY_EXCLUDE.get(bucket, ())):
            continue
        if any(k in verdict for k in kws):
            buckets.add(bucket)
    return sorted(buckets)


out = {}
PILLAR_KEYS = ('year', 'month', 'day', 'hour')
for cid in bad_ids:
    c = cases[cid]
    bd = _bazi_data(c)
    res = MangpaiEngine(bd).compute_all()
    zy = res.get('zhiye', {})
    gm = res.get('guanming', {})
    cm = res.get('caiming', {})
    gans = [bd['bazi'][k][0] for k in PILLAR_KEYS]
    zhis = [bd['bazi'][k][1] for k in PILLAR_KEYS]
    day_gan = gans[2]
    try:
        rel = detect_relations(day_gan, zhis[2], gans[0], zhis[0],
                               gans[1], zhis[1], gans[3], zhis[3])
        wa = rel.get('work_actions') or []
        ds = assess_direction_signals(day_gan, gans, zhis, relations=rel)
    except Exception as e:
        wa, ds = [], {'err': repr(e)}
    verdict = c.get('verdicts', {}).get('职业', '')
    out[cid] = {
        'bazi': ''.join(bd['bazi'][k] for k in PILLAR_KEYS),
        'gender': bd.get('input', {}).get('gender', ''),
        'verdict': verdict,
        'gold_buckets': gold_buckets(verdict),
        'primary': zy.get('primary', ''),
        'primary_label': zy.get('primary_label', ''),
        'scores': zy.get('scores', {}),
        'evidence': {k: v for k, v in (zy.get('evidence') or {}).items() if v},
        'hint_bucket': zy.get('hint_bucket', ''),
        'fallback': zy.get('fallback_no_clear'),
        'base_career': zy.get('base_career') or {},
        'corroborate': zy.get('xiangfa_corroborate') or [],
        'liushi_hints': zy.get('liushi_hints') or [],
        'is_guanming': bool(gm.get('is_guanming')),
        'gm_veto': gm.get('veto_reasons') or [],
        'caiming_tier': cm.get('tier_static') or cm.get('tier', ''),
        'ds': {k: ds.get(k) for k in ('fanju', 'pocai', 'pocai_severe',
                                      'yongshen_xiong', 'mingju_xiong',
                                      'guohe_pocai') if ds.get(k)},
        'ds_reasons': ds.get('reasons') or [],
        'work_actions': [f"{a.get('type')}:{a.get('from_pos')}->{a.get('to_pos')}"
                         + ('(aux)' if a.get('auxiliary') else '') for a in wa],
    }

json.dump(out, open('/tmp/zy55.json', 'w'), ensure_ascii=False, indent=1)

# 汇总：confusion 矩阵（gold -> engine primary）
from collections import Counter
conf = Counter()
gold_dist = Counter()
eng_dist = Counter()
for cid, e in out.items():
    g = '+'.join(e['gold_buckets']) or '?'
    gold_dist[g] += 1
    eng_dist[e['primary'] or '(空)'] += 1
    conf[(g, e['primary'] or '(空)')] += 1
print('== 金标桶分布 ==')
for k, v in gold_dist.most_common():
    print(f'  {k}: {v}')
print('== 引擎 primary 分布 ==')
for k, v in eng_dist.most_common():
    print(f'  {k}: {v}')
print('== confusion (gold -> engine) ==')
for (g, p), v in conf.most_common():
    print(f'  {g} -> {p}: {v}')
