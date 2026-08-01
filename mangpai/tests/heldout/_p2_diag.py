# -*- coding: utf-8 -*-
"""临时诊断脚本：跑指定四柱，输出 caiming/gongliang 内部状态。"""
import json
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from mangpai import MangpaiEngine


def run(gans, zhis, gender='男', dayun=None, liunian=None, label=''):
    bazi = {'year': gans[0] + zhis[0], 'month': gans[1] + zhis[1],
            'day': gans[2] + zhis[2], 'hour': gans[3] + zhis[3]}
    bazi_data = {'bazi': bazi, 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
                 'input': {'gender': gender, 'year': 1960}}
    if dayun:
        entry = {'gz': dayun, 'start_age': 5}
        if len(dayun) == 1:
            entry['zhi'] = dayun
        bazi_data['dayun'] = {'direction': '顺', 'start_age': 5, 'dayun': [entry]}
    if liunian and len(liunian) == 2:
        bazi_data['liunian'] = [{'gz': liunian, 'year': 1960}]
    res = MangpaiEngine(bazi_data).compute_all()
    gl = res.get('gongliang', {})
    cm = res.get('caiming', {})
    ls = cm.get('level_static', {}) or {}
    lv = cm.get('level', {}) or {}
    print(f'=== {label} {" ".join(gans)}/{" ".join(zhis)}')
    print('gongliang: level=%s grade=%s points=%s penalty=%s primary=%s' % (
        gl.get('level'), gl.get('wealth_grade'), gl.get('gong_points'),
        gl.get('penalty'), gl.get('primary_action')))
    print('caiming: tier_static=%s tier=%s base=%s grade=%s' % (
        cm.get('tier_static'), ls.get('tier'), ls.get('base_level'), ls.get('wealth_grade')))
    print('adjust_static:', ls.get('adjust'))
    print('views:', (cm.get('caifu_view') or {}).get('views'))
    print('primary_view:', cm.get('primary_view'), '| primary_method:', cm.get('primary_method'))
    print('guohe_type:', (cm.get('caifu_view') or {}).get('guohe_chaiqiao_type'),
          '| cai_count:', (cm.get('caifu_view') or {}).get('cai_count'),
          '| guan_count:', (cm.get('caifu_view') or {}).get('guan_count'),
          '| open_caiku:', (cm.get('caifu_view') or {}).get('has_open_caiku'))
    print('blockers:', ls.get('blockers'))
    return res


if __name__ == '__main__':
    # b67-制例一奥纳西斯（gold 巨富·船王）
    run(['乙', '己', '己', '庚'], ['巳', '丑', '未', '午'], label='b67-奥纳西斯')
