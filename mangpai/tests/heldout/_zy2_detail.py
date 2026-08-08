# -*- coding: utf-8 -*-
"""职业批2逐例详查：目标❌例的主气十神/动作当事人/神煞/分桶明细。"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.subjective.zhiye import (_compute_shishen, _cat, _pillar_cats,
                                      _pos_idx, _ensure_relations)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext

d = json.load(open('/tmp/zy_all.json'))

TARGETS = sys.argv[1:] or [
    'cj-中医', 'cj-中医李阳波', 'yx-中医',
    'zj-邢铭芬', 'zj-教师无官', 'yx-梁羽生', 'cj-2097', 'cj-校长',
    'cj-组织部宣传', 'yx-书法家', 'yx-记者', 'zj-图书管理员',
    'yx-会计', 'zj-注册会计师', 'reg67-银行行长央行', 'cj-财务总监',
    'yx-14085', 'yx-3290', 'yx-科级', 'cj-2075', 'yx-2658',
    'cj-演员', 'cj-歌星', 'yx-导演', 'famous-帕瓦罗蒂', 'famous-阿炳',
    'yx-律师-2', 'yx-律师-3',
    'b67-蒋介石', 'reg67-公安', 'yx-公安', 'reg67-财制印刑警',
    'cj-农民', 'gj-煤矿工人', 'zgj-财反局苦力', 'gj-低保伤官',
    'b67-生例四企业家', 'famous-马云', 'yx-佛具',
]


def act_cats(day_gan, gans, zhis, a):
    fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
    if fi < 0 or ti < 0:
        return set(), set()

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

    return _one(a.get('from_pos', ''), fi), _one(a.get('to_pos', ''), ti)


for tid in TARGETS:
    k = 'trainset:' + tid
    e = d.get(k)
    if not e:
        print(f'== {tid}: NOT FOUND'); continue
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    rel = _ensure_relations(day_gan, gans, zhis, None)
    wa = [a for a in (rel.get('work_actions') or []) if not a.get('auxiliary')]
    try:
        ss = compute_shensha_ext(day_gan, zhis)
    except Exception:
        ss = {}
    print(f"\n== {tid} {bz} gold={','.join(e['gold'])} pri={e['primary']} "
          f"tier={e['caiming_tier']} gm={e['is_guanming']} ==")
    mq = []
    for i in range(4):
        g_ss = _compute_shishen(day_gan, gans[i]) if gans[i] else ''
        cg = get_canggan_mangpai(zhis[i])
        z_ss = _compute_shishen(day_gan, cg[0][0]) if cg else ''
        mq.append(f"{['年','月','日','时'][i]}{gans[i]}{zhis[i]}[{_cat(g_ss)}/{_cat(z_ss)}]")
    print('  主气:', ' '.join(mq))
    for a in wa:
        fa, ta = act_cats(day_gan, gans, zhis, a)
        print(f"  动作: {a.get('type')}: {a.get('from_pos')}({'/'.join(sorted(fa))})"
              f" -> {a.get('to_pos')}({'/'.join(sorted(ta))})")
    sss = []
    for name in ('羊刃', '桃花', '灾煞', '禄神'):
        v = ss.get(name) or {}
        if v.get('in_pillars'):
            sss.append(f"{name}@{','.join(v['in_pillars'])}")
    print('  神煞:', '; '.join(sss) or '无')
    sc = sorted(e['scores'].items(), key=lambda x: -x[1])
    print('  分数:', sc[:4])
    for b, s in sc[:3]:
        ev = e['evidence'].get(b) or []
        if ev:
            print(f'    {b}: ' + ' | '.join(ev))
    g0 = e['gold'][0]
    print(f"    [{g0}] ev: " + ' | '.join(e['evidence'].get(g0) or ['(无)']))
