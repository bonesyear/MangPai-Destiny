# -*- coding: utf-8 -*-
"""职业批2 模拟器 v3：剩余 41❌ 候选规则栈全量回归检验（基于现行 dump）。
  T4  食伤鬻文: 食主气≥3柱 且 财主气≥2柱 且 无桃花 且 印主气0 → teacher+N
      （书锚 yx-梁羽生 作家=食伤吐秀鬻文为业）
  T5  印食文墨: 印主气≥1 且 食伤主气≥1 且 木火(干或支) 且 金<3 且 官杀主气≤2
      → teacher+N（段氏教师=印[知识]+食伤[表达]+木火文象；金重归金融/律令，
      官杀成势归官）
  YM  月令印虚拟: 月令印条款命中但月干/月支本气皆非印 → teacher-1（藏干虚印不取）
  YS  月令印主气: 月干或月支本气为印 → teacher+1（真实月令印加权）
  SSK 食伤生财虚功收窄: merchant ev 有「食伤生财做功」但无真实食伤↔财动作
      （仅日主吐秀+财明现的 fallback 触发）→ merchant-2
  J9  卯酉冲酒楼门户: 卯酉冲/破动作 且 财主气≥1 → merchant+N（书锚 cj-老板酒家）
  P5  金水声音: 日主金 且 水食伤主气≥1柱 且 食伤主气≥2柱 → performer+N
      （象法 金水主声音/歌喉；书锚 cj-歌星/帕瓦罗蒂 皆金日主水食伤成势）
  P2a 桃花压平a: 「食伤+桃花+财」与「桃花+财」并中 → performer-1（一桃花一吃）
  P2b 桃花压平b: 「食伤+桃花」与「桃花居日柱」并中 → performer-1
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
                                      _ensure_relations, _action_between_cats,
                                      _HE_TYPES, _ZHI_TYPES)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.constants import GAN_WX

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
    maoyou = False
    for a in wa:
        if a.get('type') in ('冲', '破'):
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi >= 0 and ti >= 0 and \
                    frozenset({zhis[fi], zhis[ti]}) == frozenset({'卯', '酉'}):
                maoyou = True
                break
    gan_wx = [GAN_WX.get(g, '') for g in gans if g]
    zhi_wx = {'寅': '木', '卯': '木', '巳': '火', '午': '火', '申': '金',
              '酉': '金', '亥': '水', '子': '水', '辰': '土', '戌': '土',
              '丑': '土', '未': '土'}
    zwx = [zhi_wx.get(z, '') for z in zhis]
    muhuo = (('木' in gan_wx or '木' in zwx) and ('火' in gan_wx or '火' in zwx))
    # 金水声音：日主金，食伤主气之字五行为水
    shui_ss = 0
    for i in range(4):
        if '食伤' not in mq[i]:
            continue
        if (gans[i] and _cat(_compute_shishen(day_gan, gans[i])) == '食伤'
                and GAN_WX.get(gans[i]) == '水'):
            shui_ss += 1
        else:
            cg = get_canggan_mangpai(zhis[i])
            if cg and _cat(_compute_shishen(day_gan, cg[0][0])) == '食伤' \
                    and zwx[i] == '水':
                shui_ss += 1
    real_ss_cai = bool(_action_between_cats(wa, day_gan, gans, zhis, '食伤', '财',
                                            _HE_TYPES | _ZHI_TYPES))
    maoyou_chong = False
    for a in wa:
        if a.get('type') == '冲':
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi >= 0 and ti >= 0 and \
                    frozenset({zhis[fi], zhis[ti]}) == frozenset({'卯', '酉'}):
                maoyou_chong = True
                break
    n_bj = n('比劫')
    m_ev = e['evidence'].get('merchant') or []
    t_ev = e['evidence'].get('teacher') or []
    p_ev = e['evidence'].get('performer') or []
    cases[k] = {
        'split': e['split'], 'id': e['id'], 'gold': e['gold'],
        'orig': e['primary'], 'scores': dict(e['scores']),
        'n_yin': n('印'), 'n_ss': n('食伤'), 'n_cai': n('财'), 'n_gs': n('官杀'),
        'jin': sum(1 for z in zhis if z in ('申', '酉'))
               + sum(1 for g in gans if g in ('庚', '辛')),
        'tao': e['tao'], 'muhuo': muhuo,
        'month_yin_main': '印' in mq[1],
        'month_yin_virtual': any(ln.startswith('月令印星') for ln in t_ev)
        and '印' not in mq[1],
        'maoyou': maoyou,
        'ssk_cut': any(ln.startswith('食伤生财做功') for ln in m_ev)
        and not real_ss_cai,
        'maoyou_chong': maoyou_chong,
        'n_bj': n_bj,
        'gz_cut': any(ln.startswith('官杀当财被制') for ln in m_ev)
        and n('官杀') == 0,
        'jin_day': GAN_WX.get(day_gan) == '金',
        'shui_ss': shui_ss,
        'p2a': any(ln.startswith('食伤+桃花+财') for ln in p_ev)
        and any(ln.startswith('桃花+财') for ln in p_ev),
        'p2b': any(ln.startswith('食伤+桃花') for ln in p_ev)
        and any(ln.startswith('桃花居日柱') for ln in p_ev),
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
        if opt.get('t5') and c['n_yin'] >= 1 and c['n_ss'] >= 1 and c['muhuo'] \
                and c['jin'] < 3 and c['n_gs'] <= 2:
            sc['teacher'] = sc.get('teacher', 0) + opt['t5']
        if opt.get('ym') and c['month_yin_virtual']:
            sc['teacher'] = sc.get('teacher', 0) - 1
        if opt.get('ys') and c['month_yin_main']:
            sc['teacher'] = sc.get('teacher', 0) + opt['ys']
        if opt.get('ssk') and c['ssk_cut']:
            sc['merchant'] = sc.get('merchant', 0) - 2
        if opt.get('j9') and c['maoyou'] and c['n_cai'] >= 1:
            sc['merchant'] = sc.get('merchant', 0) + opt['j9']
        if opt.get('p5') and c['jin_day'] and c['shui_ss'] >= 1 \
                and c['n_ss'] >= 2:
            sc['performer'] = sc.get('performer', 0) + opt['p5']
        if opt.get('p2a') and c['p2a']:
            sc['performer'] = sc.get('performer', 0) - 1
        if opt.get('p2b') and c['p2b']:
            sc['performer'] = sc.get('performer', 0) - 1
        if opt.get('t5b') and c['n_yin'] >= 1 and c['n_ss'] >= 1 and c['muhuo'] \
                and c['jin'] < 3 and c['month_yin_main'] \
                and (c['n_gs'] <= 1 or c['n_yin'] >= 2) and not c['maoyou_chong']:
            sc['teacher'] = sc.get('teacher', 0) + opt['t5b']
        if opt.get('tabc') and c['month_yin_main'] and c['n_yin'] >= 1 \
                and c['n_ss'] >= 1 and c['muhuo'] and c['n_cai'] >= 1 \
                and c['jin'] < 3 and not c['maoyou_chong'] and (
                (c['n_gs'] == 0 and c['n_cai'] >= 2 and c['n_ss'] >= 2)
                or (c['n_gs'] == 1 and c['n_ss'] >= 3)
                or (c['n_gs'] == 2 and c['n_yin'] >= 2)):
            sc['teacher'] = sc.get('teacher', 0) + opt['tabc']
        if opt.get('gz') and c['gz_cut']:
            sc['merchant'] = sc.get('merchant', 0) - 1
        if opt.get('p5b') and c['jin_day'] and c['shui_ss'] >= 1 \
                and c['n_ss'] >= 2 and c['n_bj'] >= 3:
            sc['performer'] = sc.get('performer', 0) + opt['p5b']
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
    report('T5b+4 印食文墨窄版', {'t5b': 4})
    report('GZ 官杀当财被制主气收窄', {'gz': 1})
    report('P5b+4 金水声音身旺', {'p5b': 4})
    report('落地栈 T5b4+GZ+P5b4+T4+J9+YM',
           {'t5b': 4, 'gz': 1, 'p5b': 4, 't4': 3, 'j9': 1, 'ym': 1})
    report('TABC+4 印食文墨三型', {'tabc': 4})
    report('TABC+5', {'tabc': 5})
    report('终栈 TABC4+P5b4+T4+J9+YM', {'tabc': 4, 'p5b': 4, 't4': 3, 'j9': 1, 'ym': 1})
    report('终栈5 TABC5+P5b4+T4+J9+YM', {'tabc': 5, 'p5b': 4, 't4': 3, 'j9': 1, 'ym': 1})
