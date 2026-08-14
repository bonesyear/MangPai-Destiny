# -*- coding: utf-8 -*-
"""diag_case — 单盘诊断工具（原 _p2_diag.py 转正）：任意四柱跑引擎，
dump caiming/gongliang/guanming/zhiye 内部状态，供规则调试与书例探索。

案例数据装配复用 blind_eval._bazi_data（含 dayun 支-only 补 'z' 键的坑处理）。

用法:
  python3 diag_case.py 乙己己庚 巳丑未午                  # 干4字 支4字
  python3 diag_case.py 乙己己庚 巳丑未午 --gender 女 --dayun 丙申 --liunian 庚子
  python3 diag_case.py          # 无参跑内置示例（b67-制例一奥纳西斯，gold 巨富·船王）
"""
import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

from blind_eval import _bazi_data  # noqa: E402
from mangpai import MangpaiEngine  # noqa: E402


def run(gans, zhis, gender='男', dayun=None, liunian=None, label=''):
    case = {'id': label or 'adhoc', 'gender': gender,
            'bazi': {'year': gans[0] + zhis[0], 'month': gans[1] + zhis[1],
                     'day': gans[2] + zhis[2], 'hour': gans[3] + zhis[3]}}
    if dayun:
        case['dayun'] = dayun
    if liunian:
        case['liunian'] = liunian
    res = MangpaiEngine(_bazi_data(case)).compute_all()
    gl = res.get('gongliang', {})
    cm = res.get('caiming', {})
    ls = cm.get('level_static', {}) or {}
    print(f'=== {label} {" ".join(gans)}/{" ".join(zhis)}')
    print('gongliang: level=%s grade=%s points=%s penalty=%s primary=%s' % (
        gl.get('level'), gl.get('wealth_grade'), gl.get('gong_points'),
        gl.get('penalty'), gl.get('primary_action')))
    print('caiming: tier_static=%s tier=%s base=%s grade=%s' % (
        cm.get('tier_static'), ls.get('tier'), ls.get('base_level'),
        ls.get('wealth_grade')))
    print('adjust_static:', ls.get('adjust'))
    print('views:', (cm.get('caifu_view') or {}).get('views'))
    print('primary_view:', cm.get('primary_view'),
          '| primary_method:', cm.get('primary_method'))
    print('guohe_type:', (cm.get('caifu_view') or {}).get('guohe_chaiqiao_type'),
          '| cai_count:', (cm.get('caifu_view') or {}).get('cai_count'),
          '| guan_count:', (cm.get('caifu_view') or {}).get('guan_count'),
          '| open_caiku:', (cm.get('caifu_view') or {}).get('has_open_caiku'))
    print('blockers:', ls.get('blockers'))
    gm, zy = res.get('guanming', {}), res.get('zhiye', {})
    print('guanming: is_guanming=%s veto=%s' % (
        gm.get('is_guanming'), gm.get('veto_reasons')))
    print('zhiye: primary=%s label=%s' % (
        zy.get('primary'), zy.get('primary_label')))
    return res


def main():
    ap = argparse.ArgumentParser(description='单盘诊断：dump 引擎内部状态')
    ap.add_argument('gans', nargs='?', help='天干4字，如 乙己己庚')
    ap.add_argument('zhis', nargs='?', help='地支4字，如 巳丑未午')
    ap.add_argument('--gender', default='男')
    ap.add_argument('--dayun', default=None)
    ap.add_argument('--liunian', default=None)
    ap.add_argument('--label', default='')
    args = ap.parse_args()
    if args.gans and args.zhis:
        run(list(args.gans), list(args.zhis), gender=args.gender,
            dayun=args.dayun, liunian=args.liunian, label=args.label)
    else:
        run(['乙', '己', '己', '庚'], ['巳', '丑', '未', '午'],
            label='b67-奥纳西斯')


if __name__ == '__main__':
    main()
