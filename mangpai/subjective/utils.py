# -*- coding: utf-8 -*-
"""utils - subjective 层公共 helper（H-fix-4b 下沉统一）。

ensure_relations 原 10 处复制（caiming/guanming/hunyin/xiangfa_ops/zhiye/
liuqin/laoyu/zaihuo/xueli/gongmen_wuzhi），ensure_muku 原 2 处复制
（caiming/xiangfa_ops）——逐字等价（差异分析见
docs/tasks/codehygiene-fix-backlog.md H-fix-4b 节）。

只依赖 objective 层，单向分层不破。
"""
from mangpai.objective.constants import PILLAR_KEYS
from mangpai.objective.muku import analyze_muku
from mangpai.objective.zuogong_detect import detect_relations


def ensure_relations(day_gan, gans, zhis, relations):
    """缺 relations 时自调 detect_relations；输入不全返回 {}。"""
    if relations is not None:
        return relations
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {}
    return detect_relations(
        day_gan, zhis[PILLAR_KEYS.index('day')],
        gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
    )


def ensure_muku(gans, zhis, muku_result):
    """缺 muku 结果时自调 analyze_muku（需 gans 判透干引拔）。"""
    if muku_result is not None:
        return muku_result
    if len(zhis) != 4:
        return {}
    return analyze_muku(zhis, gans)
