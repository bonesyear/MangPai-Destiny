"""
anhe — 盲派暗合

理论来源：段建业《段氏理象学》暗合篇
核心思想：盲派独有概念。某些地支之间存在暗合关系，
          代表私下联系、暗中往来、隐秘之事。
暗合组合：寅丑、午亥、卯申、子巳（共4组）
已知争议：暗合的原理有多种解释（藏干互合说、象法说），各盲师侧重不同
置信度：中（暗合存在性无争议，但具体应事有流派差异）
"""
from typing import Dict, List

from mangpai.objective.constants import AN_HE, is_pillars


def analyze_anhe(
    year_zhi: str = '', month_zhi: str = '', day_zhi: str = '', hour_zhi: str = '',
) -> Dict:
    """分析四柱中的暗合关系。

    暗合：寅丑、午亥、卯申、子巳。
    盲派认为暗合是一种隐秘的关系，代表私下联系、暗中往来。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        year_zhi: 年支（或 Pillars 对象）
        month_zhi: 月支
        day_zhi: 日支
        hour_zhi: 时支

    Returns:
        {'anhe': 暗合关系列表}
    """
    if is_pillars(year_zhi):
        p = year_zhi
        year_zhi, month_zhi, day_zhi, hour_zhi = p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi

    zhis = [('年支', year_zhi), ('月支', month_zhi),
            ('日支', day_zhi), ('时支', hour_zhi)]
    results: List[Dict] = []
    for i in range(len(zhis)):
        for j in range(i + 1, len(zhis)):
            n1, z1 = zhis[i]
            n2, z2 = zhis[j]
            if AN_HE.get(z1) == z2:
                results.append({
                    'type': '暗合',
                    'from': f'{n1}({z1})',
                    'to': f'{n2}({z2})',
                    'desc': f'{z1}{z2}暗合，主私下联系、暗中交合',
                })
    return {'anhe': results}
