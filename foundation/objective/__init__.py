"""foundation.objective - 中性客观层

流派无关的客观规则与纯计算。当前包含：
    - ganqing：滴天髓干支性情赋（任铁樵《滴天髓阐微》天干/地支章），
      结构化为「条件 -> 行为」规则，附原注与任氏曰发挥。
    - nayin ：六十甲子纳音表与干支->纳音映射（纯计算，不含盲派权重）。

中性原则：本层只做检测/查表/规则匹配，不做流派特异的解释性判断。
"""
from foundation.objective.ganqing import (
    GAN_FU, ZHI_FU,
    GAN_YUANZHU, GAN_RENSHI,
    ZHI_YUANZHU, ZHI_RENSHI,
    GanQingRule,
    GAN_QING_RULES, ZHI_QING_RULES,
    get_ganqing, match_ganqing, match_zhiqing,
    season_of, is_yang_zhi,
)
from foundation.objective.nayin import (
    NAYIN_TABLE, NAYIN_WUXING, get_nayin,
)

__all__ = [
    # ganqing
    'GAN_FU', 'ZHI_FU',
    'GAN_YUANZHU', 'GAN_RENSHI',
    'ZHI_YUANZHU', 'ZHI_RENSHI',
    'GanQingRule',
    'GAN_QING_RULES', 'ZHI_QING_RULES',
    'get_ganqing', 'match_ganqing', 'match_zhiqing',
    'season_of', 'is_yang_zhi',
    # nayin
    'NAYIN_TABLE', 'NAYIN_WUXING', 'get_nayin',
]
