# -*- coding: utf-8 -*-
"""A14 岁运反局误触诊断：12例 + 2真阳锚，逐例打印 yunfan 命中的 fan_type。"""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)
import yaml
from blind_eval import _bazi_data
from mangpai import MangpaiEngine

CASES = [  # (id, 书明文运 or None=yaml已喂, 真阳?)
    ('reg67-复例四老师经商', None, False),
    ('reg67-资本运营', None, False),
    ('cj-包工头', None, False),
    ('cj-富发财', None, False),
    ('yx-经理-2', None, False),
    ('yx-经理-4', None, False),
    ('yx-富发财数千万', None, False),
    ('yx-煤矿-2', None, False),
    ('cj-老师', '午', False),
    ('yx-医师', '卯', False),
    ('yx-煤矿', '戌', False),
    ('yx-巨富丑运发财几千', None, True),   # 丙子运 书明文入狱=真阳
    ('yx-破财工程被强拆反', None, True),   # 酉运 书明文强拆赔钱=真阳
]

cases = {c['id']: c for c in yaml.safe_load(
    open(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'), encoding='utf-8'))}

for cid, dy, zhenyang in CASES:
    c = dict(cases[cid])
    if dy:
        c['dayun'] = dy
    res = MangpaiEngine(_bazi_data(c)).compute_all()
    yf = res.get('yunfan', {})
    tag = '真阳' if zhenyang else '假阳?'
    print(f"\n=== {cid} dayun={c.get('dayun', '-')} [{tag}]")
    for d in yf.get('dayun_fan', []):
        for f in d.get('fans', []):
            print(f"  大运{d.get('gz')}: {f.get('fan_type')} [{f.get('severity')}]  {f.get('reason','')[:70]}")
    for d in yf.get('liunian_fan', []):
        for f in d.get('fans', []):
            print(f"  流年{d.get('gz')}: {f.get('fan_type')} [{f.get('severity')}]  {f.get('reason','')[:70]}")
