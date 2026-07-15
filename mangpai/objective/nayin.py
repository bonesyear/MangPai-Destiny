"""
nayin - 盲派纳音（含权重）

理论来源：《鬼谷子》《珞琭子》，段建业《段氏理象学》纳音篇
流派共识：60甲子纳音表固定无争议。盲派在纳音基础上增加权重概念，
          用于判断做功效率和命局气数强弱。
已知争议：纳音权重的具体数值为后人工程化归纳，段氏原典仅有定性描述
          （如"剑锋金最利"），非盲师口传定量表
置信度：高（纳音表）/ 低（权重表）

迁移说明：纯计算逻辑（六十甲子纳音表 NAYIN_TABLE、纳音五行归类 NAYIN_WUXING、
          干支->纳音映射 get_nayin）为流派中性，已上移至 foundation.objective.nayin。
          本模块只保留盲派特有的「纳音权重」概念及其做功分析（get_nayin_mangpai /
          get_nayin_weight / analyze_nayin_work），并通过 `from foundation.objective.nayin
          import *` 重新导出纯计算，使原有导入路径（from mangpai.objective.nayin import
          get_nayin / NAYIN_TABLE …）不断。
"""
from typing import Dict, List

# 纯计算逻辑已迁移至 foundation 中性层；此处 re-export 以保持原有导入路径
from foundation.objective.nayin import *  # noqa: F401,F403  -> NAYIN_TABLE, NAYIN_WUXING, get_nayin, get_nayin_wuxing
from foundation.objective.nayin import NAYIN_TABLE, NAYIN_WUXING, get_nayin  # 显式再导出，便于静态查找

# 盲派特异：纳音权重（后人工程化归纳，非原典定量表）
from mangpai.objective.constants import NAYIN_WEIGHT


def get_nayin_mangpai(gz_str: str) -> Dict:
    """获取盲派纳音信息（含权重和五行）。

    Args:
        gz_str: 干支字符串，如 '甲子'

    Returns:
        {'name': 纳音名, 'wuxing': 纳音五行, 'weight': 权重}
    """
    name = get_nayin(gz_str)
    return {
        'name': name,
        'wuxing': NAYIN_WUXING.get(name, ''),
        'weight': NAYIN_WEIGHT.get(name, 2),
    }


def get_nayin_weight(nayin_name: str) -> int:
    """获取纳音权重。

    权重范围 2-4：
    - 4: 气势最强（如剑锋金、天河水、天上火、松柏木）
    - 3: 气势较强
    - 2: 气势一般（默认/缺省值）
    """
    return NAYIN_WEIGHT.get(nayin_name, 2)


def analyze_nayin_work(pillar_gzs: List[str]) -> Dict:
    """盲派纳音做功分析。

    分析四柱纳音的五行分布、总权重、主导纳音五行，
    用于辅助判断命局气数和做功效率。

    主导五行按总权重排序，而非单纯数量。

    Args:
        pillar_gzs: 四柱干支列表，如 ['甲子', '丙寅', '戊辰', '庚午']

    Returns:
        纳音分析结果字典
    """
    # 过滤非法干支：name 为空（查表未命中）者不进 nayins、不计 total_weight，
    # 否则 get_nayin_mangpai 的缺省权重 2 会凭空计入（幽灵权重）。
    nayins = [get_nayin_mangpai(gz) for gz in pillar_gzs if gz and get_nayin(gz)]

    wx_count: Dict[str, int] = {}
    wx_weight: Dict[str, int] = {}
    for n in nayins:
        wx = n['wuxing']
        if wx:
            wx_count[wx] = wx_count.get(wx, 0) + 1
            wx_weight[wx] = wx_weight.get(wx, 0) + n['weight']

    total_weight = sum(n['weight'] for n in nayins)
    # 按 weight 排序主导五行，weight 相同时按数量排序
    if wx_weight:
        dominant_wuxing = max(
            wx_weight,
            key=lambda w: (wx_weight[w], wx_count.get(w, 0)),
        )
    else:
        dominant_wuxing = ''

    return {
        'nayins': nayins,
        'total_weight': total_weight,
        'dominant_wuxing': dominant_wuxing,
        'wx_count': wx_count,
        'wx_weight': wx_weight,
    }
