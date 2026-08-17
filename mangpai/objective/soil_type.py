"""
soil_type - 盲派四土燥湿

理论来源：盲师口传燥湿理论，段建业《段氏理象学》
核心思想：四土（辰戌丑未）有燥湿之分，生克能力不同。
  辰=湿土、丑=寒湿土 -> 可生金、不克水或克水力弱、可晦火
  未=热燥土、戌=燥土 -> 不生金反脆金、克水力强、几乎不晦火
已知争议：辰土是否"寒"有不同说法，部分流派认为辰只"湿"不"寒"
置信度：中

生克信号（供 zuogong 将来查询，本模块只暴露不改 zuogong）：
  一般五行认为"土生金、土克水、火生土"对四土统一成立，但盲派燥湿理论
  将四土对金/水/火三者的生克行为按燥湿分流：
    湿土(辰、丑)：生金 / 不克水（克水力弱）/ 晦火（火生湿土，湿土晦其火）
    燥土(未、戌)：不生金反脆金 / 克水力强 / 几乎不晦火
  即同一"土"在不同燥湿下，对金的生克（生 vs 脆）、对水的克制（弱 vs 强）、
  对火的承接（晦 vs 不晦）均不同。soil_shengke_behavior() 暴露该结构化信号。
"""
from typing import Dict, List

from mangpai.objective.constants import SOIL_TYPE, is_pillars

_KU_ZHI = {'辰', '戌', '丑', '未'}


def _soil_rules(soil_type: str) -> List[str]:
    """根据燥湿类型返回人类可读的生克规则列表。"""
    if '湿' in soil_type:
        return ['可生金', '克水力弱或不克', '可晦火']
    return ['不生金反脆金', '克水力强', '几乎不晦火']


def soil_shengke_behavior(zhi: str) -> Dict:
    """返回单个土支的盲派燥湿生克行为字典（供 zuogong 将来查询）。

    盲派四土燥湿理论下，土支对金/水/火的生克能力与一般五行不同：
      湿土(辰、丑)：生金 / 不克水（克水力弱）/ 晦火（火生湿土，湿土晦其火）
      燥土(未、戌)：不生金反脆金 / 克水力强 / 几乎不晦火

    Args:
        zhi: 地支（辰戌丑未之一）；非土支返回空 dict。

    Returns:
        生克行为字典，键：
          zhi       : 该地支
          soil_type : 燥湿类型（湿土/寒湿土/热燥土/燥土）
          wet       : 是否湿土（辰丑 True，未戌 False）
          sheng_jin : 是否生金（湿土 True，燥土 False；燥土不生金）
          cui_jin   : 是否脆金（燥土 True，湿土 False；燥土不生金反脆金）
          ke_shui   : 克水强度（湿土 '弱'，燥土 '强'）
          hui_huo   : 是否晦火（湿土 True，燥土 False；燥土几乎不晦火）
          rules     : 人类可读规则列表
        非土支返回空 dict {}。
    """
    s_type = SOIL_TYPE.get(zhi, '')
    if not s_type:
        return {}
    wet = '湿' in s_type
    return {
        'zhi': zhi,
        'soil_type': s_type,
        'wet': wet,
        'sheng_jin': wet,                    # 湿土生金，燥土不生金
        'cui_jin': not wet,                  # 燥土脆金，湿土不脆
        'ke_shui': '弱' if wet else '强',    # 湿土克水力弱或不克，燥土克水力强
        'hui_huo': wet,                      # 湿土晦火，燥土几乎不晦火
        'rules': _soil_rules(s_type),
    }


def analyze_soil(
    year_zhi: str = '', month_zhi: str = '', day_zhi: str = '', hour_zhi: str = '',
) -> Dict:
    """分析四柱中四土的燥湿性质。

    盲派燥湿理论：
    辰=湿土、丑=寒湿土 -> 可生金、不克水或克水力弱、可晦火
    未=热燥土、戌=燥土 -> 不生金反脆金、克水力强、几乎不晦火

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        year_zhi: 年支（或 Pillars 对象）
        month_zhi: 月支
        day_zhi: 日支
        hour_zhi: 时支

    Returns:
        土性分析结果，含：
          soil_entries : 各柱土支信息（含生克行为 shengke），同名土支多柱并
                         存不覆盖（以柱位为键）
          wet_soil     : 出现的湿土支集合（去重，按支）
          dry_soil     : 出现的燥土支集合（去重，按支）
    """
    if is_pillars(year_zhi):
        p = year_zhi
        year_zhi, month_zhi, day_zhi, hour_zhi = p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi

    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    pillar_names = ['年柱', '月柱', '日柱', '时柱']

    # 以柱位为键，避免同名土支（如两辰分现年柱与日柱）以支为键时后者覆盖前者。
    soil_info: Dict[str, Dict] = {}
    for i, z in enumerate(zhis):
        if z in _KU_ZHI:
            s_type = SOIL_TYPE.get(z, '')
            soil_info[pillar_names[i]] = {
                'pillar': pillar_names[i],
                'zhi': z,
                'type': s_type,
                'rules': _soil_rules(s_type),
                'shengke': soil_shengke_behavior(z),
            }

    # F1 标注：wet_soil/dry_soil 两键无 Python 消费（prompt-only）；
    # zuogong_confirm 自算土性不读本结果（engine↔zuogong 双轨，批9 备案）。
    return {
        'soil_entries': list(soil_info.values()),
        'wet_soil': sorted([z for z in _KU_ZHI if z in zhis and '湿' in SOIL_TYPE.get(z, '')]),
        'dry_soil': sorted([z for z in _KU_ZHI if z in zhis and '燥' in SOIL_TYPE.get(z, '')]),
    }
