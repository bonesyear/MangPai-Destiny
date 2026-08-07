# -*- coding: utf-8 -*-
"""A1 诊断2：五行相背命中案例的做功指向明细（日柱指向 vs 全局指向，ke 方向）。"""
import os
import sys
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml

from mangpai.objective.constants import GAN_WX, ZHI_WX, WX_KE, PILLAR_KEYS
from mangpai.subjective import zhengfan as ZF
from mangpai.subjective.zuogong_confirm import analyze_zuogong

IDS = ['reg67-复例四老师经商', 'reg67-资本运营', 'yx-富富有百万', 'yx-经理-2',
       'yx-经理-4', 'cj-富发财', 'shouke-li101-穷命', 'shouke-li139-靠丈夫富',
       'shouke-qi02-禄当财被欠债', 'zhenbao-14b', 'zj-平常八字', 'zj-注册会计师',
       'yx-木匠', 'cj-富发财上千万', 'reg67-伤食当财', 'gj-公门转商', 'yx-经理']


def _elem(pos, gans, zhis):
    return ZF._pos_element(pos, gans, zhis)


def run(path, label):
    cases = yaml.safe_load(open(path, encoding='utf-8'))
    for c in cases:
        if c['id'] not in IDS:
            continue
        b = c['bazi']
        gans = [b['year'][0], b['month'][0], b['day'][0], b['hour'][0]]
        zhis = [b['year'][1], b['month'][1], b['day'][1], b['hour'][1]]
        zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                             gans[1], zhis[1], gans[3], zhis[3])
        wa = zg.get('work_actions', [])
        zf = ZF.analyze_zhengfan(wa, zg.get('day_he_type'), gans, zhis)
        if zf.get('type') != 'fan' or '五行相克相背' not in zf.get('reason', ''):
            continue
        v = (c.get('verdicts') or {}).get('财命', '')
        print(f"== {label} {c['id']} 断语={v[:26]}")
        print(f"   八字: {b['year']} {b['month']} {b['day']} {b['hour']}")
        qishi = zf.get('qishi')
        print(f"   气势: {qishi and qishi.get('desc')}")
        for a in wa:
            if a.get('auxiliary'):
                continue
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            fe, te = _elem(fp, gans, zhis), _elem(tp, gans, zhis)
            side = '日' if ('day' in fp or 'day' in tp) else '局'
            print(f"   [{side}] {a.get('type')}: {fp}({fe}) -> {tp}({te})")


run(os.path.join(_HERE, 'cases.yaml'), 'H')
run(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), 'T')
