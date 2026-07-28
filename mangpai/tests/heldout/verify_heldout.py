# -*- coding: utf-8 -*-
"""V3/K1 留出集排盘验证 — 每条案例过 MangpaiEngine.compute_all() 不炸 + 干支echo校验。

用法:
  python3 mangpai/tests/heldout/verify_heldout.py            # heldout + trainset 全验
  python3 mangpai/tests/heldout/verify_heldout.py --trainset # 仅训练侧
退出码: 全部通过 0；任何排盘异常/干支echo不符/结构缺失 1。
⚠️ 本脚本只验证「能排盘」，不比对 verdicts（留出集严禁用于修引擎）。
"""
import os, sys, traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))  # repo 根（含 mangpai 包）
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml
from mangpai import MangpaiEngine

GANS = set('甲乙丙丁戊己庚辛壬癸')
ZHIS = set('子丑寅卯辰巳午未申酉戌亥')


def check_case(c):
    """返回错误描述字符串；空串=通过。"""
    b = c['bazi']
    # 结构校验
    for pillar in ('year', 'month', 'day', 'hour'):
        gz = b.get(pillar, '')
        if len(gz) != 2 or gz[0] not in GANS or gz[1] not in ZHIS:
            return f'{pillar} 干支非法: {gz!r}'
    # 六十甲子奇偶校验
    for pillar in ('year', 'month', 'day', 'hour'):
        g, z = b[pillar]
        if (list('甲乙丙丁戊己庚辛壬癸').index(g) - list('子丑寅卯辰巳午未申酉戌亥').index(z)) % 2:
            return f'{pillar} 阴阳不配: {g}{z}'
    bazi_data = {
        'bazi': dict(b), 'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': c.get('gender', '男'), 'year': c.get('year', 1960)},
    }
    dy = c.get('dayun')
    if dy and len(dy) == 2:
        bazi_data['dayun'] = {'direction': '顺', 'start_age': 5,
                              'dayun': [{'gz': dy, 'start_age': 5}]}
    ln = c.get('liunian')
    if ln and len(ln) == 2:
        bazi_data['liunian'] = [{'gz': ln, 'year': c.get('year', 1960)}]
    try:
        res = MangpaiEngine(bazi_data).compute_all()
    except Exception:
        return 'compute_all 异常: ' + traceback.format_exc(limit=2).splitlines()[-1]
    # 干支 echo: 引擎排盘结果应含原四柱（不因输入而改动）
    echoed = res.get('bazi') or res.get('bazi_data', {}).get('bazi') or {}
    if echoed:
        for pillar in ('year', 'month', 'day', 'hour'):
            if pillar in echoed and echoed[pillar] != b[pillar]:
                return f'{pillar} echo 不符: 输入{b[pillar]} 引擎{echoed[pillar]}'
    if not isinstance(res, dict) or len(res) < 5:
        return f'compute_all 返回过薄: {len(res) if isinstance(res, dict) else type(res)}'
    return ''


def run(path, label):
    cases = yaml.safe_load(open(path, encoding='utf-8'))
    bad = []
    for c in cases:
        err = check_case(c)
        if err:
            bad.append((c['id'], err))
    print(f'[{label}] {len(cases)} 例: {len(cases) - len(bad)} 通过, {len(bad)} 失败')
    for cid, err in bad:
        print(f'  ❌ {cid}: {err}')
    return len(bad)


def main():
    n = 0
    if '--trainset' not in sys.argv:
        n += run(os.path.join(_HERE, 'cases.yaml'), 'heldout ⚠️留出集')
    n += run(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), 'trainset 训练侧')
    print('全部通过 ✅' if n == 0 else f'共 {n} 例失败 ❌')
    sys.exit(1 if n else 0)


if __name__ == '__main__':
    main()
