# -*- coding: utf-8 -*-
"""职业批2模拟器：137 可评例主气粒度特征 + 候选规则栈组合网格。
约束=两集 ✅ 零回退；目标=trainset ❌/⚠️→✅ 最大化。
候选规则（全部主气粒度）：
  T1 印食传道: 印主气≥1 且 食主气≥1 且 金<3 → teacher+N
  T2 印成势:   印主气≥3 且 食主气≥1 → teacher+N（叠T1）
  T3 食势配印: 食主气≥3 且 印主气≥1 且 财主气≥1 → teacher+N（叠T1）
  T4 食伤鬻文: 食主气≥3 且 财主气≥2 且 无桃花 且 印主气=0 → teacher+N
  P1 食势之艺: 食主气≥3 且 无桃花 且 财主气=0 → performer+N
  A1 水财双现: 水财主气≥2 且 食伤主气≥1 且 金<3 → accountant+N
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.subjective.zhiye import _compute_shishen, _cat
from mangpai.objective.canggan import get_canggan_mangpai

d = json.load(open('/tmp/zy_all.json'))

_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')

cases = {}
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    mq = []  # 主气十神 per pillar (干十神 + 支本气)
    for i in range(4):
        s = set()
        if gans[i]:
            s.add(_cat(_compute_shishen(day_gan, gans[i])))
        cg = get_canggan_mangpai(zhis[i])
        if cg:
            s.add(_cat(_compute_shishen(day_gan, cg[0][0])))
        s.discard('')
        mq.append(s)
    n = lambda cat: sum(1 for s in mq if cat in s)
    # 财主气的五行（水财判据）
    cai_wx = ''
    from mangpai.objective.constants import GAN_WX, WX_KE
    cai_wx = WX_KE.get(GAN_WX.get(day_gan, ''), '')
    cases[k] = {
        'split': e['split'], 'id': e['id'], 'gold': e['gold'],
        'orig': e['primary'], 'scores': dict(e['scores']),
        'n_yin': n('印'), 'n_ss': n('食伤'), 'n_cai': n('财'),
        'n_gs': n('官杀'),
        'jin': sum(1 for z in zhis if z in ('申', '酉'))
               + sum(1 for g in gans if g in ('庚', '辛')),
        'tao': e['tao'],
        'cai_shui': cai_wx == '水',
    }


def primary_of(scores):
    p = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return p if scores[p] >= 6 else ''


def simulate(opt):
    flips = []
    for k, c in cases.items():
        sc = dict(c['scores'])
        # T1 印食传道
        if opt.get('t1') and c['n_yin'] >= 1 and c['n_ss'] >= 1 and c['jin'] < 3:
            sc['teacher'] = sc.get('teacher', 0) + opt['t1']
        # T2 印成势
        if opt.get('t2') and c['n_yin'] >= 3 and c['n_ss'] >= 1 and c['jin'] < 3:
            sc['teacher'] = sc.get('teacher', 0) + opt['t2']
        # T3 食势配印
        if opt.get('t3') and c['n_ss'] >= 3 and c['n_yin'] >= 1 and c['n_cai'] >= 1 \
                and c['jin'] < 3:
            sc['teacher'] = sc.get('teacher', 0) + opt['t3']
        # T4 食伤鬻文
        if opt.get('t4') and c['n_ss'] >= 3 and c['n_cai'] >= 2 and not c['tao'] \
                and c['n_yin'] == 0:
            sc['teacher'] = sc.get('teacher', 0) + opt['t4']
        # P1 食势之艺
        if opt.get('p1') and c['n_ss'] >= 3 and not c['tao'] and c['n_cai'] == 0:
            sc['performer'] = sc.get('performer', 0) + opt['p1']
        # A1 水财双现
        if opt.get('a1') and c['cai_shui'] and c['n_cai'] >= 2 and c['n_ss'] >= 1 \
                and c['jin'] < 3:
            sc['accountant'] = sc.get('accountant', 0) + opt['a1']
        p = primary_of(sc)
        orig = c['orig']
        eff = p if p else (orig if orig in ('laborer', 'unemployed') else '')
        if eff != orig:
            was = '✅' if orig in c['gold'] else ('⚠️' if not orig else '❌')
            now = '✅' if eff in c['gold'] else ('⚠️' if not eff else '❌')
            flips.append((c['id'], c['split'], orig, eff, was, now,
                          {b: sc[b] for b in sc if sc[b] != c['scores'].get(b, 0)}))
    return flips


def report(name, opt):
    flips = simulate(opt)
    reg = [f for f in flips if f[4] == '✅']
    gain = [f for f in flips if f[5] == '✅' and f[4] != '✅']
    print(f'\n== {name}: 翻转{len(flips)} ✅回归{len(reg)} '
          f'增益{len(gain)} ==')
    for f in flips:
        tag = '💥' if f[4] == '✅' else ('🎯' if f[5] == '✅' else '  ')
        print(f'  {tag} [{f[1]}] {f[0][:24]} {f[2] or "(空)"}->{f[3] or "(空)"} '
              f'{f[4]}->{f[5]} Δ{f[6]}')
    return flips


if __name__ == '__main__':
    report('T1+2 单发', {'t1': 2})
    report('T1+2 T2+2', {'t1': 2, 't2': 2})
    report('T1+2 T2+2 T3+2', {'t1': 2, 't2': 2, 't3': 2})
    report('T4+3 单发', {'t4': 3})
    report('P1+3 单发', {'p1': 3})
    report('A1+3 单发', {'a1': 3})
    report('全栈 T1T2T3=2 T4=3 P1=3 A1=3', {'t1': 2, 't2': 2, 't3': 2,
                                            't4': 3, 'p1': 3, 'a1': 3})
