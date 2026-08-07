# -*- coding: utf-8 -*-
"""A1 诊断：列出 heldout+trainset 全部 zhengfan 反局命中，按条款分类。"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml

from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _bazi(c):
    b = c['bazi']
    gans = [b['year'][0], b['month'][0], b['day'][0], b['hour'][0]]
    zhis = [b['year'][1], b['month'][1], b['day'][1], b['hour'][1]]
    return gans, zhis


def run(path, label):
    cases = yaml.safe_load(open(path, encoding='utf-8'))
    for c in cases:
        gans, zhis = _bazi(c)
        zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                             gans[1], zhis[1], gans[3], zhis[3])
        zf = analyze_zhengfan(zg.get('work_actions', []),
                              zg.get('day_he_type'), gans, zhis)
        if zf.get('type') == 'fan':
            reason = zf.get('reason', '')
            clause = ('K2-3时支坏' if '时支' in reason and '不可坏' in reason
                      else 'K2-4冲合' if '冲合' in reason or '矛盾' in reason
                      else '五行相背' if '五行相克相背' in reason
                      else '气势克破' if '克破' in reason else '其他')
            v = (c.get('verdicts') or {}).get('财命', '')
            print(f'{label} {c["id"]} [{clause}] 断语={v[:30]}')
            print(f'    {reason[:110]}')


run(os.path.join(_HERE, 'cases.yaml'), 'H')
run(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), 'T')
