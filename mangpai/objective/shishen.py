# -*- coding: utf-8 -*-
"""shishen - 十神计算单一权威实现（H-fix-4b 下沉统一）。

原为 15 处复制：objective 层 dayun._compute_shishen / shenshu._compute_shishen
/ bazi_calc.ten_god；subjective 层 12 处 _compute_shishen（caiming/guanming/
hunyin/xiangfa_ops/gongmen_wuzhi/zhiye/liuqin/laoyu/yingqi_subj/xueli/zaihuo
等）；同族大类映射 _cat/_shishen_cat ×10、五行->大类 _wx_cat ×6。

差异分析（docs/tasks/codehygiene-fix-backlog.md H-fix-4b 节）：
  - 全部 _compute_shishen 副本逐字等价（GAN_WX/WX_SHENG/WX_KE + 阴阳判定）；
    bazi_calc.ten_god 同逻辑但非法干抛 KeyError（严格契约，bazi_calc 侧保留）。
  - _cat 两变体仅未知串 fallback 不同（return ss vs return ''）；全部调用点
    只喂十神标准名或 ''，可达输入等价 → 统一为 '' fallback。
  - _wx_cat(day_gan, wx) 四份全同；yongshen/gongliang 为 (day_wx, wx) 同逻辑
    （判定顺序不同但条件互斥，结果等价）；空守卫差异仅 ('','') 不可达输入。
"""
from mangpai.objective.constants import GAN_WX, WX_KE, WX_SHENG

YANG_GANS = frozenset('甲丙戊庚壬')


def god_from_wx(day_wx: str, other_wx: str, same_polarity: bool) -> str:
    """五行+阴阳 -> 十神全名；空/非法五行返回 ''。"""
    if not day_wx or not other_wx:
        return ''
    if other_wx == day_wx:
        return '比肩' if same_polarity else '劫财'
    if WX_SHENG.get(day_wx) == other_wx:
        return '食神' if same_polarity else '伤官'
    if WX_SHENG.get(other_wx) == day_wx:
        return '偏印' if same_polarity else '正印'
    if WX_KE.get(day_wx) == other_wx:
        return '偏财' if same_polarity else '正财'
    if WX_KE.get(other_wx) == day_wx:
        return '七杀' if same_polarity else '正官'
    return ''


def shishen_of(day_gan: str, gan: str) -> str:
    """gan 相对日主 day_gan 的十神；非法/空干返回 ''。"""
    day_wx = GAN_WX.get(day_gan, '')
    gan_wx = GAN_WX.get(gan, '')
    if not day_wx or not gan_wx:
        return ''
    return god_from_wx(day_wx, gan_wx,
                       (day_gan in YANG_GANS) == (gan in YANG_GANS))


def shishen_cat(ss: str) -> str:
    """十神全名 -> 大类（官杀/财/印/食伤/比劫）；空或未知串返回 ''。"""
    if ss in ('正官', '七杀'):
        return '官杀'
    if ss in ('正财', '偏财'):
        return '财'
    if ss in ('正印', '偏印'):
        return '印'
    if ss in ('食神', '伤官'):
        return '食伤'
    if ss in ('比肩', '劫财'):
        return '比劫'
    return ''


def wx_cat(day_wx: str, wx: str) -> str:
    """五行 wx 相对日主五行 day_wx 的十神大类；空输入返回 ''。"""
    if not day_wx or not wx:
        return ''
    if wx == day_wx:
        return '比劫'
    if WX_SHENG.get(day_wx) == wx:
        return '食伤'
    if WX_SHENG.get(wx) == day_wx:
        return '印'
    if WX_KE.get(day_wx) == wx:
        return '财'
    if WX_KE.get(wx) == day_wx:
        return '官杀'
    return ''


def gan_wx_cat(day_gan: str, wx: str) -> str:
    """(day_gan, 五行) -> 十神大类（wx_cat 的天干版包装）。"""
    return wx_cat(GAN_WX.get(day_gan, ''), wx)
