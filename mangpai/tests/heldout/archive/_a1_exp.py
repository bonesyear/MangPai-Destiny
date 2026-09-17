# -*- coding: utf-8 -*-
"""A1 实验：五行相背条款整体关停后，trainset/heldout 打分翻转全量测。"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
for p in (_HERE, _REPO):
    if p not in sys.path:
        sys.path.insert(0, p)

import json
import mangpai.subjective.zhengfan as ZF

# 关停五行相背：把 ke_global 恒置 False（实验用 monkeypatch）
_orig = ZF.analyze_zhengfan
src_mark = 'ke_global = any('


def patched(work_actions, day_he_type, gans=None, zhis=None):
    return _orig(work_actions, day_he_type, gans, zhis)


# 直接改模块内常量的方案不可行——改为临时改写函数：用 flag 包一层
import types

# 简化：替换 _pos_element 无意义；正确做法=在 analyze 内跳过。用环境变量开关注入。
os.environ['ZF_DISABLE_WUXIANG'] = '1'

import blind_eval as BE

base = json.load(open(os.path.join(_HERE, 'snapshots', '20260807_m.json'), encoding='utf-8'))
res = {'trainset': BE.eval_cases(os.path.join(_HERE, '..', 'trainset', 'cases.yaml'))}

for split in ('trainset',):
    s = BE.summarize(res[split])
    print(split, {d: f"{v['✅']}✅/{v['⚠️']}⚠️/{v['❌']}❌ acc={v['acc']}" for d, v in s.items() if v['n']})
    flips = BE.diff(base[split], res[split])
    for f in flips:
        print(f"  [{f['dim']}] {f['id']} {f['verdict'][:24]} {f['score']} 引擎:{f['engine']}")
