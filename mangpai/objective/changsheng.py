"""
changsheng — 盲派十二长生（阴阳同生同死）

理论来源：阴阳同生同死首倡于沈孝瞻《子平真诠》，盲派沿用此论（段建业《段氏理象学》载录盲师口传体系）
流派共识：盲派认为阴干阳干同生同死，即阴干也顺行（与书房派阴干逆行不同）
已知争议：盲派内部对"阴阳同生同死"的起算点有细微分歧，本模块采用五行同生论
置信度：中（盲派内部有少数异议）

盲派只用5个关键长生位：长生、禄旺、死、墓、绝
"""
from typing import Dict

from mangpai.objective.constants import (
    CHANGSHENG_START_MANGPAI, KEY_STAGES, DI_ZHI, _STAGE_ALIASES,
)

_TWELVE_STAGES: list = [
    '长生', '沐浴', '冠带', '临官', '帝旺',
    '衰', '病', '死', '墓', '绝', '胎', '养',
]


def get_changsheng_mangpai(day_gan: str, zhi: str) -> str:
    """计算盲派十二长生阶段（阴阳同生同死）。

    盲派与书房派区别：阴干顺行（与阳干同方向），不逆行。

    Args:
        day_gan: 天干
        zhi: 地支

    Returns:
        十二长生阶段名称；无效输入返回空字符串
    """
    if day_gan not in CHANGSHENG_START_MANGPAI:
        return ''
    if zhi not in DI_ZHI:
        return ''
    start_zhi: str = CHANGSHENG_START_MANGPAI[day_gan]
    start_idx: int = DI_ZHI.index(start_zhi)
    target_idx: int = DI_ZHI.index(zhi)
    offset: int = (target_idx - start_idx) % 12
    return _TWELVE_STAGES[offset]


def is_key_stage(stage: str) -> bool:
    """判断是否为盲派重点长生位。

    盲派只看5个关键位：长生、禄旺、死、墓、绝
    "禄旺"是盲派统称，对应十二长生表中的"临官"和"帝旺"。
    """
    if stage in KEY_STAGES:
        return True
    alias = _STAGE_ALIASES.get(stage)
    return alias is not None and alias in KEY_STAGES


def get_changsheng_all(day_gan: str) -> Dict[str, str]:
    """获取天干在所有12地支上的长生阶段。

    Args:
        day_gan: 天干

    Returns:
        {地支: 长生阶段} 字典；无效天干返回空字典
    """
    if day_gan not in CHANGSHENG_START_MANGPAI:
        return {}
    return {zhi: get_changsheng_mangpai(day_gan, zhi) for zhi in DI_ZHI}
