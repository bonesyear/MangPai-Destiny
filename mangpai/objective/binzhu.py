"""
binzhu — 盲派宾主分析

理论来源：段建业《段氏理象学》宾主篇
核心思想：盲派将四柱分为主和宾，看日柱做功方向是取外物还是内聚。
  3层模型（默认 layers=3，段氏完整框架）：
    Layer 1 (主)：日柱 + 时柱 — 自我、内圈、行动
    Layer 2 (宾)：月柱 — 父母、兄弟、近亲
    Layer 3 (远宾)：年柱 — 祖辈、社会、外部
  2层模型（layers=2，部分盲派简并用法）：
    Layer 1 (体)：日柱 + 时柱 — 自我、内圈
    Layer 2 (宾)：月柱 + 年柱 — 父母兄弟、祖辈社会
已知争议：2层与3层之争；2层将月年合并为宾，3层细分近宾/远宾
置信度：中
"""
from typing import Dict, List

from mangpai.objective.constants import is_pillars


def analyze_binzhu(
    year_zhi: str = '', month_zhi: str = '', day_zhi: str = '', hour_zhi: str = '',
    year_gan: str = '', month_gan: str = '', day_gan: str = '', hour_gan: str = '',
    layers: int = 3,
) -> Dict:
    """分析四柱宾主关系。

    layers=3（默认，段氏完整框架）3层宾主划分：
    - 主（layer1）：日柱 + 时柱
    - 宾（layer2）：月柱
    - 远宾（layer3）：年柱

    layers=2 时退化为2层模型（部分盲派简并用法）：
    - 体（layer1）：日柱 + 时柱
    - 宾（layer2）：月柱 + 年柱

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        year_zhi: 年支（或 Pillars 对象）
        month_zhi: 月支
        day_zhi: 日支
        hour_zhi: 时支
        year_gan: 年干
        month_gan: 月干
        day_gan: 日干
        hour_gan: 时干
        layers: 划分层数；3=三层（默认，主/宾/远宾），2=两层（体/宾）。
            非2值均按默认3层处理，保持旧行为不变。

    Returns:
        宾主分析结果；layers=3 含 layer1/layer2/layer3，
        layers=2 含 layer1（体）/layer2（宾）
    """
    if is_pillars(year_zhi):
        p = year_zhi
        year_zhi, month_zhi, day_zhi, hour_zhi = p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi
        year_gan, month_gan, day_gan, hour_gan = p.year_gan, p.month_gan, p.day_gan, p.hour_gan

    if layers == 2:
        # 2层简并模型：日时为体（主位），年月为宾（用位）
        return {
            'layer1': {
                'label': '体',
                'pillars': ['日', '时'],
                'gans': [day_gan, hour_gan],
                'zhis': [day_zhi, hour_zhi],
                'desc': '日柱时柱为体，代表自我与内圈',
            },
            'layer2': {
                'label': '宾',
                'pillars': ['月', '年'],
                'gans': [month_gan, year_gan],
                'zhis': [month_zhi, year_zhi],
                'desc': '月柱年柱为宾，代表父母兄弟与祖辈社会',
            },
        }

    # 默认3层模型（段氏完整框架）
    return {
        'layer1': {
            'label': '主',
            'pillars': ['日', '时'],
            'gans': [day_gan, hour_gan],
            'zhis': [day_zhi, hour_zhi],
            'desc': '日柱时柱为主，代表自我与内圈',
        },
        'layer2': {
            'label': '宾',
            'pillars': ['月'],
            'gans': [month_gan],
            'zhis': [month_zhi],
            'desc': '月柱为宾，代表父母兄弟近亲',
        },
        'layer3': {
            'label': '远宾',
            'pillars': ['年'],
            'gans': [year_gan],
            'zhis': [year_zhi],
            'desc': '年柱为远宾，代表祖辈社会外部',
        },
    }
