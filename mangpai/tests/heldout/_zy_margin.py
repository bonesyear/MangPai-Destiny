# -*- coding: utf-8 -*-
"""merchant 三条款收窄变体逐例测算（action 级真实重算，非 evidence 文本近似）。
门户主气粒度 / 官杀当财主气粒度 / 内食神须做功 —— 逐例翻转方向+边际。"""
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
from mangpai.subjective.zhiye import (_compute_shishen, _cat, _pillar_cats,
                                      _pos_idx, _ensure_relations)
from mangpai.objective.constants import PILLAR_KEYS
from mangpai.objective.canggan import get_canggan_mangpai

d = json.load(open('/tmp/zy_all.json'))


def act_cats(day_gan, gans, zhis, a):
    """复刻 _score_merchant._act_cats（当事人主气粒度）。"""
    fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
    if fi < 0 or ti < 0:
        return fi, ti, set(), set()

    def _one(pos, i):
        if pos == 'day_gan':
            return {'日主'}
        if pos.endswith('_gan'):
            return {_cat(_compute_shishen(day_gan, gans[i]))} - {''}
        cg = get_canggan_mangpai(zhis[i])
        if not cg:
            return set()
        if a.get('type') == '暗合':
            return {_cat(_compute_shishen(day_gan, g)) for g, _ in cg[:2]} - {''}
        return {_cat(_compute_shishen(day_gan, cg[0][0]))} - {''}

    return fi, ti, _one(a.get('from_pos', ''), fi), _one(a.get('to_pos', ''), ti)


def zhu_qi_cat(day_gan, gans, zhis, i):
    """柱主气十神集合：干本身 + 支本气。"""
    out = set()
    if gans[i]:
        out.add(_cat(_compute_shishen(day_gan, gans[i])))
    cg = get_canggan_mangpai(zhis[i])
    if cg:
        out.add(_cat(_compute_shishen(day_gan, cg[0][0])))
    return out - {''}


_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')

rows = []
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    rel = _ensure_relations(day_gan, gans, zhis, None)
    wa = [a for a in (rel.get('work_actions') or []) if not a.get('auxiliary')]
    ev = e['evidence'].get('merchant', [])
    fired = {ln.split('（')[0] for ln in ev}
    # 门户主气粒度
    hour_main = zhu_qi_cat(day_gan, gans, zhis, 3)
    portal_main = bool({'财', '印'} & hour_main)
    # 官杀当财主气粒度：克动作两端主气为 官杀/食伤
    gs_main = any(
        a.get('type') == '克' and
        ({'官杀'} & act_cats(day_gan, gans, zhis, a)[2] and
         {'食伤'} & act_cats(day_gan, gans, zhis, a)[3] or
         {'食伤'} & act_cats(day_gan, gans, zhis, a)[2] and
         {'官杀'} & act_cats(day_gan, gans, zhis, a)[3])
        for a in wa)
    # 内食神须做功：藏食神本气支参与非aux动作
    inner_zhis = [z for z in zhis if get_canggan_mangpai(z)
                  and _compute_shishen(day_gan, get_canggan_mangpai(z)[0][0]) == '食神']
    gan_has_shishen = any(_compute_shishen(day_gan, g) == '食神' for g in gans if g)
    inner_work = False
    if inner_zhis and not gan_has_shishen:
        for a in wa:
            for pos in (a.get('from_pos', ''), a.get('to_pos', '')):
                i = _pos_idx(pos)
                if i >= 0 and pos.endswith('_zhi') and zhis[i] in inner_zhis:
                    inner_work = True
    # 边际：merchant 分 - 次高分（他桶最高）
    ms = e['scores'].get('merchant', 0)
    other = max((v for b, v in e['scores'].items() if b != 'merchant'), default=0)
    rows.append({
        'k': k, 'gold': e['gold'], 'primary': e['primary'], 'ms': ms,
        'margin': ms - other, 'fired': sorted(fired),
        'portal_main': portal_main, 'gs_main': gs_main,
        'inner_work': inner_work,
        'has_inner': bool(inner_zhis) and not gan_has_shishen,
    })

json.dump(rows, open('/tmp/zy_margin.json', 'w'), ensure_ascii=False, indent=1)

# 汇总：三条款 现行命中 vs 变体命中 交叉（按 primary==merchant / 金标merchant 分组）
def grp(r):
    if r['primary'] == 'merchant' and 'merchant' in r['gold']:
        return 'TM'   # 真商人✅
    if r['primary'] == 'merchant':
        return 'FM'   # 假商人（merchant fp）
    if 'merchant' in r['gold']:
        return 'FN'   # 漏判商人
    return 'OT'


from collections import Counter
for clause, cur_key, var_key in (('门户', '财/印在时柱门户', 'portal_main'),
                                 ('官杀当财', '官杀当财被制', 'gs_main'),
                                 ('内食神', '内食神格', 'inner_work')):
    print(f'\n== {clause}: 现行命中->变体仍命中 按组 ==')
    m = Counter()
    for r in rows:
        cur = cur_key in r['fired']
        m[(grp(r), cur, r[var_key])] += 1
    for (g, cur, var), n in sorted(m.items()):
        print(f'  {g} 现行={int(cur)} 变体={int(var)}: {n}')
