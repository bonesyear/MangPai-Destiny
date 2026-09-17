# -*- coding: utf-8 -*-
"""职业批2模拟器 v2：干净候选规则栈全量回归检验。
  T4 食伤鬻文: 食主气≥3柱 且 财主气≥2柱 且 无桃花 且 印主气0 → teacher+N
  YM 月令印主气化: 月令印条款命中但月干十神/月支本气皆非印 → teacher-1（藏干虚印不取）
  A1 水财算帐: 财五行=水 且 财主气≥1 且 亥子辰≥1 且 食伤主气≥1 且 金<3 → accountant+N
  J9 卯酉冲酒楼门户: 卯酉/酉卯冲动作 且 财主气≥1 → merchant+N
  M2 官商之间: 官杀主气≥2 且 坐根制财已触发 → merchant+N
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.subjective.zhiye import (_compute_shishen, _cat, _pos_idx,
                                      _ensure_relations)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.constants import GAN_WX, WX_KE

d = json.load(open('/tmp/zy_all.json'))
_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')

cases = {}
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    mq = []
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
    rel = _ensure_relations(day_gan, gans, zhis, None)
    wa = [a for a in (rel.get('work_actions') or []) if not a.get('auxiliary')]
    # 卯酉冲
    maoyou = False
    for a in wa:
        if a.get('type') in ('冲', '破'):
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi >= 0 and ti >= 0 and \
                    frozenset({zhis[fi], zhis[ti]}) == frozenset({'卯', '酉'}):
                maoyou = True
                break
    zuogen = any('坐根制财' in ln for ln in (e['evidence'].get('merchant') or []))
    month_yin_virtual = any(ln.startswith('月令印星') for ln in (e['evidence'].get('teacher') or [])) \
        and '印' not in mq[1]
    cases[k] = {
        'split': e['split'], 'id': e['id'], 'gold': e['gold'],
        'orig': e['primary'], 'scores': dict(e['scores']),
        'n_yin': n('印'), 'n_ss': n('食伤'), 'n_cai': n('财'), 'n_gs': n('官杀'),
        'jin': sum(1 for z in zhis if z in ('申', '酉'))
               + sum(1 for g in gans if g in ('庚', '辛')),
        'tao': e['tao'],
        'cai_shui': WX_KE.get(GAN_WX.get(day_gan, ''), '') == '水',
        'hzc': any(z in ('亥', '子', '辰') for z in zhis),
        'maoyou': maoyou, 'zuogen': zuogen,
        'month_yin_virtual': month_yin_virtual,
    }


def primary_of(scores):
    p = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return p if scores[p] >= 6 else ''


def simulate(opt):
    flips = []
    for k, c in cases.items():
        sc = dict(c['scores'])
        if opt.get('t4') and c['n_ss'] >= 3 and c['n_cai'] >= 2 and not c['tao'] \
                and c['n_yin'] == 0:
            sc['teacher'] = sc.get('teacher', 0) + opt['t4']
        if opt.get('ym') and c['month_yin_virtual']:
            sc['teacher'] = sc.get('teacher', 0) - 1
        if opt.get('a1') and c['cai_shui'] and c['n_cai'] >= 1 and c['hzc'] \
                and c['n_ss'] >= 1 and c['jin'] < 3:
            sc['accountant'] = sc.get('accountant', 0) + opt['a1']
        if opt.get('j9') and c['maoyou'] and c['n_cai'] >= 1:
            sc['merchant'] = sc.get('merchant', 0) + opt['j9']
        if opt.get('m2') and c['n_gs'] >= 2 and c['zuogen']:
            sc['merchant'] = sc.get('merchant', 0) + opt['m2']
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
    print(f'== {name}: 翻转{len(flips)} ✅回归{len(reg)} 增益{len(gain)} ==')
    for f in flips:
        tag = '💥' if f[4] == '✅' else ('🎯' if f[5] == '✅' else '  ')
        print(f'  {tag} [{f[1]}] {f[0][:26]} {f[2] or "(空)"}->{f[3] or "(空)"} '
              f'{f[4]}->{f[5]} Δ{f[6]}')
    return flips


if __name__ == '__main__':
    report('T4+3', {'t4': 3})
    report('YM', {'ym': 1})
    report('A1+3', {'a1': 3})
    report('J9+1', {'j9': 1})
    report('M2+2', {'m2': 2})
    report('全栈 T4=3 YM A1=3 J9=1 M2=2', {'t4': 3, 'ym': 1, 'a1': 3, 'j9': 1, 'm2': 2})
