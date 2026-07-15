"""
gongfei — 盲派功神/废神分类

（原 gongshen.py：源码实现的是「功神/废神」而非「宫身」，命名错位，
  故正名为 gongfei；gongshen 之名让位于段氏宫身模块。）

理论来源：段建业《段氏理象学》功神篇
核心思想：
  功神 = 参与做功的天干地支（有目标的克制/合化/墓用等）
  废神 = 未参与做功的天干地支（闲置无用）
  功神多 → 命局效率高；废神多 → 需大运激发
已知争议：功神的定义范围各盲师有不同标准（严格派只算直接做功者）
置信度：中
"""
from typing import Dict, List, Set

from mangpai.objective.constants import PILLAR_KEYS


def _extract_positions(work_actions: List[Dict]) -> Set[str]:
    """从做功动作中提取参与做功的干支位置标识。

    直接读取 work_actions 中的结构化字段 from_pos / to_pos，
    并读取 participants 字段（三合局/半合所有参与字均为功神），不再使用正则解析字符串。
    """
    positions: Set[str] = set()
    for wa in work_actions:
        if wa.get('auxiliary'):
            # 辅助关系（如生扶）不视作功神
            continue
        for field in ('from_pos', 'to_pos'):
            val = wa.get(field, '')
            if val:
                positions.add(val)
        # 三合局/半合：所有参与字均为功神（成局功神）
        for val in wa.get('participants', []):
            if val:
                positions.add(val)
    return positions


def classify_gongshen(
    work_actions: List[Dict],
    pillar_keys: List[str],
    pillar_gans: List[str],
    pillar_zhis: List[str],
) -> Dict:
    """分类功神与废神。

    Args:
        work_actions: 做功动作列表（含 from_pos/to_pos 结构化字段）
        pillar_keys: 柱位键列表 ['year', 'month', 'day', 'hour']
        pillar_gans: 各柱天干
        pillar_zhis: 各柱地支

    Returns:
        {'gong_shen': sorted list, 'fei_shen': sorted list}
    """
    gong_shen_set = _extract_positions(work_actions)

    all_positions: Set[str] = set()
    for pk, gan, zhi in zip(pillar_keys, pillar_gans, pillar_zhis):
        if gan:
            all_positions.add(f'{pk}_gan')
        if zhi:
            all_positions.add(f'{pk}_zhi')

    fei_shen_set = all_positions - gong_shen_set

    return {
        'gong_shen': sorted(gong_shen_set),
        'fei_shen': sorted(fei_shen_set),
    }
