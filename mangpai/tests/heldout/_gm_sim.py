# -*- coding: utf-8 -*-
"""官命候选修法双侧翻转模拟（纯文本解析 dump，不改引擎）。"""
import json
import re
from collections import Counter

d = json.load(open('/tmp/gm_all.json'))

COMBO_KEYS = ['合制·伤食制官杀', '伤食制官杀', '合制·劫刃制官杀', '劫刃制官杀',
              '合制·官杀制比劫', '官杀制比劫', '合制·印制伤食', '印制伤食',
              '合制·财制印', '财制印', '合制·劫刃制财', '劫刃制财', '合制·自合制官']
YIN_COMBOS = {'财制印', '印制伤食', '合制·财制印', '合制·印制伤食'}


def parse(cid, e):
    """accepted combos 以 e['combos'] 为准；details 仅取方向与 blocked 原因。"""
    dir_map = {}
    blk = []
    g6 = zangsha = False
    for line in e['details']:
        if line.startswith('官星被制空亡'):
            g6 = True
            continue
        if line.startswith('官杀藏'):
            zangsha = True
            continue
        for k in COMBO_KEYS:
            if line.startswith(k):
                rest = line[len(k):]
                m = re.match(r'（(主制宾|宾制主|同侧制)，', rest)
                if m and k not in dir_map:
                    dir_map[k] = m.group(1)
                elif rest.startswith('：') and k not in e['combos']:
                    blk.append((k, rest[:30]))
                break
    acc = [(k, dir_map.get(k, '?')) for k in e['combos']]
    return {'acc': acc, 'blk': blk, 'g6': g6, 'zangsha': zangsha,
            'shengyong': e['shengyong'], 'has_guansha': e['has_guansha'],
            'veto_reasons': e['veto_reasons']}


def decide(p, rules):
    acc = [(k, dr) for k, dr in p['acc']]
    if 'DIR' in rules:  # 伤食制官杀/财制印/印制伤食 须主制宾
        acc = [(k, dr) for k, dr in acc
               if k.replace('合制·', '') not in ('伤食制官杀', '财制印', '印制伤食')
               or dr == '主制宾']
    if 'G7YIN' in rules:  # G7 不挡印制伤食（恢复被挡者，方向未知按主制宾?保守按原方向不明→计入）
        for k, r in p['blk']:
            if '印制伤食' in k and '围制财源' in r:
                acc.append((k, '主制宾'))
    if 'G1X' in rules:  # 撤 G1 例外：劫刃制财一律不入官命
        acc = [(k, dr) for k, dr in acc if '劫刃制财' not in k]
    if 'ZANGSHA' in rules and p['zangsha']:  # 藏杀被制=官命组合
        acc.append(('藏杀被制', '?'))
    combos = [k for k, _ in acc]
    sy_core = [s for s in p['shengyong'] if s == '印化官杀']
    has_g = p['has_guansha']
    if 'YIN' in rules and not has_g:  # 印类combo豁免has_guansha
        if any(k in YIN_COMBOS for k in combos):
            has_g = True
    g6 = p['g6']
    if g6 and 'G6TOU' in rules:
        g6 = False  # 仅对官杀透干者豁免——调用方先过滤
    raw = bool(combos or sy_core) and (has_g or bool(p['shengyong'])) and not g6
    vetoes = list(p['veto_reasons'])
    if 'R1GUAN' in rules and any('官杀制比劫' in k for k in combos):
        vetoes = [v for v in vetoes if not v.startswith('比劫夺财')]
    if 'YUNFAN' in rules:
        vetoes = [v for v in vetoes if not v.startswith('岁运')]
    vetoed = raw and bool(vetoes)
    return raw and not vetoed


def run(rules, g6tou_ids=None):
    flips = []
    for cid, e in d.items():
        p = parse(cid, e)
        r = set(rules)
        if 'G6TOU' in r and (not g6tou_ids or cid not in g6tou_ids):
            r.discard('G6TOU')
        got = decide(p, r)
        cur = e['is_guanming']
        if got != cur:
            flips.append((cid, e['expect'], cur, got,
                          '✅→❌' if cur == e['expect'] else '❌→✅'))
    good = [f for f in flips if f[4] == '❌→✅']
    bad = [f for f in flips if f[4] == '✅→❌']
    return good, bad


# 基线自洽校验：无规则时 decide 须复现引擎结果
mismatch = [cid for cid, e in d.items() if decide(parse(cid, e), set()) != e['is_guanming']]
print('基线自洽 mismatch:', mismatch)

# G6 官杀透干集合（从八字算）
GAN_WX = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土', '己': '土',
          '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
WX_KE_ME = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
g6tou = []
for cid, e in d.items():
    if any(x.startswith('官星被制空亡') for x in e['details']):
        day_wx = GAN_WX[e['bazi'][4]]
        guan_wx = WX_KE_ME[day_wx]
        gans = e['bazi'][0::2]
        if any(GAN_WX[g] == guan_wx for i, g in enumerate(gans) if i != 2):
            g6tou.append(cid)
print('G6触发例:', [cid for cid, e in d.items() if any(x.startswith('官星被制空亡') for x in e['details'])])
print('G6且官杀透干:', g6tou)

for name, rules, kw in [
    ('G6透干豁免', ['G6TOU'], {}),
    ('印类combo豁免has_guansha', ['YIN'], {}),
    ('G7不挡印制伤食', ['G7YIN'], {}),
    ('YIN+G7YIN', ['YIN', 'G7YIN'], {}),
    ('藏杀被制=combo', ['ZANGSHA'], {}),
    ('R1官杀制劫豁免', ['R1GUAN'], {}),
    ('岁运反局不否决官命', ['YUNFAN'], {}),
    ('方向门(伤食/财印类主制宾)', ['DIR'], {}),
    ('撤G1例外', ['G1X'], {}),
]:
    good, bad = run(rules, g6tou)
    print(f'\n[{name}] ❌→✅ {len(good)}: {[g[0] for g in good]}')
    print(f'  ✅→❌ {len(bad)}: {[b[0] for b in bad]}')
