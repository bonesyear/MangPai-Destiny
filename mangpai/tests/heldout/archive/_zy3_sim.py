# -*- coding: utf-8 -*-
"""职业批3 模拟器：基于 _zy3_dump（/tmp/zy3_all.json）的候选规则栈全量回归检验。
  A1a   水财算帐通道收窄（任务0）：透干水财之通根支（亥子丑辰申）全部被冲 → 撤+3
        （书锚 ans12-下岗穷命自证「财星太弱，财根被破，想赚钱又得不到钱」；
        财根被冲坏者非「坐实」，不为雇员帐房之象）
  A1b   金成势金融收窄（任务0）：金须为日主之印（金=印方成「金融机构管公家钱」；
        金为比劫者自身之金成势，非机构——yx-中介 庚日金=比劫）
  FANCAI 财星反局 merchant gating（书锚 zgj-财反局苦力「财星反局财大凶…干苦力活」，
        A15 fanju_caixing severe 命中者财做功为虚，不以经营成象）
  GSKE  官杀为忌克身贫贱 gating：官杀主气≥3字 + 身弱/从弱 + tier 贫/小康
        → military/lawyer 撤（书锚 gj-煤矿工人「官杀重重克身…比劫助身抗杀，
        体力取财，贫贱之命」——官杀为忌克身者不以武职/律职成象）
  ACCMU 财入印墓于宾位 +3（书锚 zj-注册会计师「财星入印墓在宾位，是替别人做
        智力服务的…食生财，财入墓，做帐的」）
  ACCGK 日支坐财库+官杀透干+财库支被合闭 +2（书锚 cj-财务总监：未财库坐日支，
        丙官透月，午未合闭——在单位管公家之财）
  MJGATE mingju_xiong 撤 merchant/performer（破格困顿者不以经营/技艺成象，
        书锚 gj-低保伤官「伤官见官为忌…靠低保维生」）
"""
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai.objective.constants import GAN_WX, WX_KE, WX_SHENG

d = json.load(open('/tmp/zy3_all.json'))
_TIE_PRI = ('performer', 'military', 'merchant', 'accountant', 'doctor',
            'teacher', 'lawyer')
_TOMB = {'木': '未', '火': '戌', '金': '丑', '水': '辰', '土': '辰'}
_SHUI_ROOTS = {'亥', '子', '丑', '辰', '申'}

cases = {}
for k, e in d.items():
    bz = e['bazi']
    gans = [bz[0], bz[2], bz[4], bz[6]]
    zhis = [bz[1], bz[3], bz[5], bz[7]]
    day_gan = gans[2]
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    chong_zhis = set()
    he_day_zhi = False
    for p2 in e['pairs']:
        if p2['t'] == '冲':
            chong_zhis.add(p2['fz'])
            chong_zhis.add(p2['tz'])
        if p2['t'] in ('地支合', '半合', '暗合'):
            if p2['fp'] == 'day_zhi' or p2['tp'] == 'day_zhi':
                he_day_zhi = True
    shui_roots = {z for z in zhis if z in _SHUI_ROOTS}
    acc_ev = e['evidence'].get('accountant') or []
    cases[k] = {
        'split': e['split'], 'id': e['id'], 'gold': e['gold'],
        'orig': e['primary'], 'scores': dict(e['scores']),
        'a1a_cut': any('水财坐实' in ln for ln in acc_ev)
                   and bool(shui_roots) and shui_roots <= chong_zhis,
        'a1b_cut': any('金成势' in ln for ln in acc_ev) and day_wx != '水',
        'fanju_caixing': e['fanju_caixing'],
        'gske': e['gs_main_char'] >= 3 and e['strength'] in ('身弱', '从弱')
                and e['caiming_tier'] in ('贫', '小康'),
        'mingju': e['mingju_xiong'],
        'acc_mu': bool(cai_wx) and _TOMB.get(cai_wx) in zhis[:2]
                  and e['cai_main_char'] >= 1
                  and any('印' in e['main_qi'][i] for i in range(2)
                          if zhis[i] == _TOMB.get(cai_wx)),
        'acc_gk': bool(cai_wx) and zhis[2] == _TOMB.get(cai_wx)
                  and any(g and WX_KE.get(GAN_WX.get(g, ''), '') == day_wx
                          for g in gans)
                  and he_day_zhi,
    }


def primary_of(scores):
    p = max(scores, key=lambda k: (scores[k], -_TIE_PRI.index(k)))
    return p if scores[p] >= 6 else ''


def simulate(opt):
    flips = []
    for k, c in cases.items():
        sc = dict(c['scores'])
        if opt.get('a1a') and c['a1a_cut']:
            sc['accountant'] = sc.get('accountant', 0) - 3
        if opt.get('a1b') and c['a1b_cut']:
            sc['accountant'] = sc.get('accountant', 0) - 6
        if opt.get('fancai') and c['fanju_caixing']:
            sc['merchant'] = 0
        if opt.get('gske') and c['gske']:
            sc['military'] = 0
            sc['lawyer'] = 0
        if opt.get('mjgate') and c['mingju']:
            sc['merchant'] = 0
            sc['performer'] = 0
        if opt.get('acc_mu') and c['acc_mu']:
            sc['accountant'] = sc.get('accountant', 0) + 3
        if opt.get('acc_gk') and c['acc_gk']:
            sc['accountant'] = sc.get('accountant', 0) + 2
        p = primary_of(sc)
        orig = c['orig']
        # fallback 后基础类目可达性粗判（与 _classify_base_career 同口径：
        # 反局/非贫小康/工薪经营风险路径 阻断；此处仅以 dump 字段近似）
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
    print(f'== {name}: 翻转{len(flips)} ✅回归{len(reg)} 增益{len(gain)} ==')
    for f in flips:
        tag = '💥' if f[4] == '✅' else ('🎯' if f[5] == '✅' else '  ')
        print(f'  {tag} [{f[1]}] {f[0][:24]} {f[2] or "(空)"}->{f[3] or "(空)"} '
              f'{f[4]}->{f[5]} Δ{f[6]} gold={f[7]}')
    return flips


if __name__ == '__main__':
    report('A1a 水财根冲收窄', {'a1a': 1})
    report('A1b 金=印收窄', {'a1b': 1})
    report('FANCAI 财反局撤merchant', {'fancai': 1})
    report('GSKE 官杀为忌克身撤military/lawyer', {'gske': 1})
    report('ACCMU 财入印墓宾位+3', {'acc_mu': 1})
    report('ACCGK 日支财库+官透+合闭+2', {'acc_gk': 1})
    report('MJGATE mingju撤merchant/performer', {'mjgate': 1})
    report('全栈', {'a1a': 1, 'a1b': 1, 'fancai': 1, 'gske': 1,
                  'acc_mu': 1, 'acc_gk': 1})
