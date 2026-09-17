# -*- coding: utf-8 -*-
"""职业批4 模拟器：基于 _zy3_dump（/tmp/zy3_all.json）候选规则网格。
  WENREN  纯食伤文人 teacher+5：食伤主气≥3字+印主气0字+财主气0字
          （书锚 yx-记者「高级记者、编辑、著名报人」：食伤吐秀之极而无财无印，
          纯以文笔为业；梁羽生鬻文通道之无财对偶）
  SHUIJU  水局成势会计+4：亥子辰支≥2 + 申子辰水局（三合/半合）+ 财主气明现
          （书锚 yx-科级「做会计的，后来做审计了」：申子辰水局成势，数字之象
          成局；7.3 会计「亥子辰水，数字象」之成势版）
  ACCM2   财入印墓+食伤生财复合 accountant+2（书锚 zj-注册会计师原话
          「食生财，财入墓，做帐的」——复合即做帐）
  TAOMU   桃花豁免收窄：财入印墓宾位命中者，performer 桃花诸条 -3
          （同书锚：有桃花而财入印墓者以帐房论不以艺论）
  CONGJIN 从强金财金融 accountant+5：金财（申酉为财）≥2位 + 从强
          （yx-3290「银行官员」：从强印比为用，金财为忌被制=金融机器中
          管非己之财）
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.objective.constants import GAN_WX, ZHI_WX, WX_KE
from mangpai.objective.canggan import get_canggan_mangpai

d = json.load(open('/tmp/zy3_all.json'))
_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')
_TOMB = {'木': '未', '火': '戌', '金': '丑', '水': '辰', '土': '辰'}


def _ss_char(gans, zhis, day_gan, cat):
    from mangpai.subjective.zhiye import _main_qi_char_count
    return _main_qi_char_count(day_gan, gans, zhis, cat)


cases = {}
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    ss_cai_work = any('食伤生财做功' in ln for ln in e['evidence'].get('merchant', []))
    acc_mu = any('财入印墓' in ln for ln in e['evidence'].get('accountant', []))
    shui_zhi_n = sum(1 for z in zhis if z in ('亥', '子', '辰'))
    shui_ju = False
    for p2 in e['pairs']:
        if p2['t'] in ('三合局', '半合'):
            pair = {p2['fz'], p2['tz']}
            if pair & {'申', '子', '辰'} and pair <= {'申', '子', '辰'}:
                shui_ju = True
    jin_cai_n = (sum(1 for z in zhis if z in ('申', '酉') and cai_wx == '金')
                 + sum(1 for g in gans if g in ('庚', '辛') and cai_wx == '金'))
    cases[k] = {
        'split': e['split'], 'id': e['id'], 'gold': e['gold'],
        'orig': e['primary'], 'scores': dict(e['scores']),
        'wenren': (_ss_char(gans, zhis, day_gan, '食伤') >= 3
                   and _ss_char(gans, zhis, day_gan, '印') == 0
                   and _ss_char(gans, zhis, day_gan, '财') == 0),
        'shuiju': shui_zhi_n >= 2 and shui_ju
                  and _ss_char(gans, zhis, day_gan, '财') >= 1,
        'acc_m2': acc_mu and ss_cai_work,
        'acc_mu': acc_mu,
        'congjin': jin_cai_n >= 2 and e['strength'] == '从强',
        'tao': e['tao'],
    }


def primary_of(scores):
    p = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return p if scores[p] >= 6 else ''


def simulate(opt):
    flips = []
    for k, c in cases.items():
        sc = dict(c['scores'])
        if opt.get('wenren') and c['wenren']:
            sc['teacher'] = sc.get('teacher', 0) + 5
        if opt.get('shuiju') and c['shuiju']:
            sc['accountant'] = sc.get('accountant', 0) + 4
        if opt.get('acc_m2') and c['acc_m2']:
            sc['accountant'] = sc.get('accountant', 0) + 2
        if opt.get('taomu') and c['acc_mu'] and c['tao']:
            sc['performer'] = sc.get('performer', 0) - 3
        if opt.get('congjin') and c['congjin']:
            sc['accountant'] = sc.get('accountant', 0) + 5
        p = primary_of(sc)
        orig = c['orig']
        eff = p
        if not eff and orig in ('laborer', 'unemployed'):
            eff = orig
        if eff != orig:
            was = '✅' if orig in c['gold'] else ('⚠️' if not orig else '❌')
            now = '✅' if eff in c['gold'] else ('⚠️' if not eff else '❌')
            flips.append((c['id'], c['split'], orig, eff, was, now,
                          {b: sc[b] for b in sc if sc[b] != c['scores'].get(b, 0)},
                          c['gold']))
    return flips


def report(name, opt):
    flips = simulate(opt)
    reg = [f for f in flips if f[4] == '✅']
    gain = [f for f in flips if f[5] == '✅' and f[4] != '✅']
    hd = [f for f in flips if f[1] == 'heldout']
    print(f'== {name}: 翻转{len(flips)} ✅回归{len(reg)} 增益{len(gain)} heldout触{len(hd)} ==')
    for f in flips:
        tag = '💥' if f[4] == '✅' else ('🎯' if f[5] == '✅' else '  ')
        print(f'  {tag} [{f[1]}] {f[0][:24]} {f[2] or "(空)"}->{f[3] or "(空)"} '
              f'{f[4]}->{f[5]} Δ{f[6]} gold={f[7]}')
    return flips


if __name__ == '__main__':
    report('WENREN 纯食伤文人+5', {'wenren': 1})
    report('SHUIJU 水局成势+4', {'shuiju': 1})
    report('ACCM2 财入印墓复合+2', {'acc_m2': 1})
    report('TAOMU 财入印墓者桃花-3', {'taomu': 1})
    report('CONGJIN 从强金财+5', {'congjin': 1})
    report('组合 WENREN+SHUIJU', {'wenren': 1, 'shuiju': 1})
    report('组合 WENREN+SHUIJU+ACCM2+TAOMU', {'wenren': 1, 'shuiju': 1, 'acc_m2': 1, 'taomu': 1})
