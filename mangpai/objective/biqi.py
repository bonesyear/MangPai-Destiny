"""
biqi — 盲派闭气

理论来源：盲师口传闭气体系
核心思想：六合中某些组合会使墓库中的藏干被闭住，无法发挥作用。
          闭气只有逢冲才能解开。
闭气规则：
  子丑合闭丑中金
  辰酉合闭辰中水
  午未合闭未中木
  卯戌合闭戌中火
已知争议：部分盲派对"闭"的方向有不同说法（闭谁/被闭），本模块采用主流说法
置信度：中
"""
from typing import Dict, List

from mangpai.objective.constants import BI_QI, LIU_HE, is_pillars


def analyze_biqi(
    year_zhi: str = '', month_zhi: str = '', day_zhi: str = '', hour_zhi: str = '',
) -> Dict:
    """分析四柱中的闭气关系。

    闭气：六合中某些组合会使墓库中的藏干被闭住，无法发挥作用。
    子丑合闭丑中金、辰酉合闭辰中水、午未合闭未中木、卯戌合闭戌中火。
    闭气只有逢冲才能解开。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        year_zhi: 年支（或 Pillars 对象）
        month_zhi: 月支
        day_zhi: 日支
        hour_zhi: 时支

    Returns:
        {'biqi': 闭气关系列表}
    """
    if is_pillars(year_zhi):
        p = year_zhi
        year_zhi, month_zhi, day_zhi, hour_zhi = p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi

    zhis = {
        '年支': year_zhi, '月支': month_zhi,
        '日支': day_zhi, '时支': hour_zhi,
    }
    results: List[Dict] = []

    for a, b in LIU_HE:
        a_pillars = [k for k, v in zhis.items() if v == a]
        b_pillars = [k for k, v in zhis.items() if v == b]
        if a_pillars and b_pillars:
            key = f'{a}{b}'
            alt_key = f'{b}{a}'
            bi = BI_QI.get(key) or BI_QI.get(alt_key)
            if bi:
                # 多柱同支全部报告
                for ap in a_pillars:
                    for bp in b_pillars:
                        results.append({
                            'type': '闭气',
                            'from': f'{ap}({a})',
                            'to': f'{bp}({b})',
                            'closed_zhi': bi['闭'],
                            'closed_qi': bi['闭气'],
                            'desc': f'{a}{b}合闭{bi["闭"]}中{bi["闭气"]}，逢冲方解',
                        })
    return {'biqi': results}
