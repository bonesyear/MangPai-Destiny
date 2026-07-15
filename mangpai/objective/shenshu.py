"""
shenshu — 盲派十神数量歌诀（郑民生十排歌）

理论来源：郑民生《十排歌》十神数量歌诀
核心思想：按同一个十神在八字中出现的数量分级断事。
  1个清纯好，7个成势吉，2-6个混杂病。
  统计范围：3天干（排除日主）+ 4地支本气 = 7个位置
已知争议：部分流派统计含藏干中余气，本模块仅取本气（与歌诀上限7一致）
置信度：高（歌诀为公开内容，映射明确）
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    GAN_WX, WX_KE, WX_SHENG,
    CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)

_YANG_GANS = set('甲丙戊庚壬')

# ── 郑民生十排歌：十神数量歌诀 ──
# 1清纯好 / 7成势吉 / 2-6混杂病 / 0不见
SHENSHU_GE: Dict[str, Dict[int, str]] = {
    '正财': {
        1: '一财是财',
        2: '二财是妾',
        3: '三财是色',
        4: '四财是贪',
        5: '五财聚散成灾',
        6: '六财身弱当贫',
        7: '七财从势金玉满堂',
    },
    '偏财': {
        1: '一才娇花',
        2: '二才财源',
        3: '三才贪欢',
        4: '四才孤寒',
        5: '五才买身败业',
        6: '六才刑狱牵连',
        7: '七才成势银海金山',
    },
    '正官': {
        1: '一官是官',
        2: '二官是狭',
        3: '三官是鬼',
        4: '四官是难',
        5: '五官牢刑',
        6: '六官死于非命',
        7: '七官从势反为贵',
    },
    '七杀': {
        1: '一杀为官',
        2: '二杀恶权',
        3: '三杀牢狱',
        4: '四杀伤残',
        5: '五杀短寿',
        6: '六杀儿女无传',
        7: '七杀丰厚反到王前',
    },
    '正印': {
        1: '一印是权',
        2: '二印椿萱',
        3: '三印少决',
        4: '四印伤残',
        5: '五印埋儿断后',
        6: '六印懒惰偷馋',
        7: '七印势极到佛前',
    },
    '偏印': {
        1: '一枭爹娘',
        2: '二枭多伤',
        3: '三枭换祖',
        4: '四枭凄凉',
        5: '五枭谋多成少',
        6: '六枭算进牢房',
        7: '七枭势成反坐高堂',
    },
    '食神': {
        1: '一食才子',
        2: '二食贪吃',
        3: '三食愚钝',
        4: '四食弱智',
        5: '五食败业贪欢',
        6: '六食短寿',
        7: '七食花红治世',
    },
    '伤官': {
        1: '一伤生财',
        2: '二伤卖艺',
        3: '三伤刑',
        4: '四伤破败',
        5: '五伤伤残',
        6: '六伤短命',
        7: '七伤精明得志',
    },
    '比肩': {
        1: '一比仁义',
        2: '二比争气',
        3: '三比伤尊',
        4: '四比乏利',
        5: '五比离乡背井',
        6: '六比贫困无疑',
        7: '七比势强反成名誉',
    },
    '劫财': {
        1: '一劫情谊',
        2: '二劫克妻',
        3: '三劫损财',
        4: '四劫牢狱',
        5: '五劫伤人害命',
        6: '六劫尸骨分离',
        7: '七劫从恶名霸一方',
    },
}

# 四吉宜扶 / 四凶宜制 / 中性（郑公方法论要点第3条）
JI_SHISHEN = {'正官', '正印', '食神', '正财'}
XIONG_SHISHEN = {'七杀', '伤官', '劫财', '偏印'}
ZHONGXING_SHISHEN = {'比肩', '偏财'}

# 歌诀显示顺序
_SHISHEN_ORDER = [
    '正财', '偏财', '正官', '七杀', '正印',
    '偏印', '食神', '伤官', '比肩', '劫财',
]


def _compute_shishen(day_gan: str, gan: str) -> str:
    """计算 gan 相对 day_gan 的十神。

    同阴阳 → 比肩/食神/偏印/偏财/七杀
    异阴阳 → 劫财/伤官/正印/正财/正官
    """
    day_wx = GAN_WX.get(day_gan, '')
    gan_wx = GAN_WX.get(gan, '')
    if not day_wx or not gan_wx:
        return ''
    same_polarity = (day_gan in _YANG_GANS) == (gan in _YANG_GANS)
    if gan_wx == day_wx:
        return '比肩' if same_polarity else '劫财'
    if WX_SHENG.get(day_wx) == gan_wx:
        return '食神' if same_polarity else '伤官'
    if WX_SHENG.get(gan_wx) == day_wx:
        return '偏印' if same_polarity else '正印'
    if WX_KE.get(day_wx) == gan_wx:
        return '偏财' if same_polarity else '正财'
    if WX_KE.get(gan_wx) == day_wx:
        return '七杀' if same_polarity else '正官'
    return ''


def _grade(count: int) -> str:
    """按歌诀规则分级：0不见 / 1清纯 / 2-6混杂 / 7+成势。"""
    if count == 0:
        return '不见'
    if count == 1:
        return '清纯'
    if count >= 7:
        return '成势'
    return '混杂'


def analyze_shenshu(
    day_gan: str, day_zhi: str = '',
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
    shishen: Optional[Dict[str, str]] = None,
) -> Dict:
    """十神数量歌诀分析（郑民生十排歌）。

    统计3天干（排除日主）+ 4地支本气 = 7个位置的十神出现次数，
    按歌诀映射断语：1清纯好 / 7成势吉 / 2-6混杂病 / 0不见。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        day_gan: 日干（或 Pillars 对象）
        day_zhi: 日支
        year_gan/year_zhi/month_gan/month_zhi/hour_gan/hour_zhi: 其余三柱干支
        shishen: 十神映射（可选，缺省时自动推算）

    Returns:
        十神数量歌诀分析结果，含 counts/grades/summary
    """
    if is_pillars(day_gan):
        p = day_gan
        day_gan, day_zhi = p.day_gan, p.day_zhi
        year_gan, year_zhi = p.year_gan, p.year_zhi
        month_gan, month_zhi = p.month_gan, p.month_zhi
        hour_gan, hour_zhi = p.hour_gan, p.hour_zhi

    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]

    # 收集7个位置的十神（排除日干）
    positions: List[Dict] = []
    for i, pk in enumerate(PILLAR_KEYS):
        # 天干十神（排除日干）
        if pk != 'day' and gans[i]:
            ss = ''
            if shishen:
                ss = shishen.get(f'{pk}_gan', '')
            if not ss:
                ss = _compute_shishen(day_gan, gans[i])
            if ss:
                positions.append({
                    'pillar': PILLAR_NAMES_CN[i],
                    'type': '天干',
                    'gan': gans[i],
                    'shishen': ss,
                })
        # 地支本气十神
        if zhis[i]:
            canggan = CANG_GAN_MANGPAI.get(zhis[i], [])
            if canggan:
                ben_gan = canggan[0][0]
                ss = _compute_shishen(day_gan, ben_gan)
                if ss:
                    positions.append({
                        'pillar': PILLAR_NAMES_CN[i],
                        'type': '地支本气',
                        'gan': ben_gan,
                        'zhi': zhis[i],
                        'shishen': ss,
                    })

    # 统计十神出现次数
    counts: Dict[str, int] = {}
    detail: Dict[str, List[str]] = {}
    for pos in positions:
        ss = pos['shishen']
        counts[ss] = counts.get(ss, 0) + 1
        detail.setdefault(ss, []).append(
            f"{pos['pillar']}{pos['type']}({pos.get('gan', '')})"
        )

    # 按歌诀映射断语
    results: Dict[str, Dict] = {}
    grades: Dict[str, List[str]] = {'清纯': [], '成势': [], '混杂': [], '不见': []}

    for ss in _SHISHEN_ORDER:
        count = counts.get(ss, 0)
        grade = _grade(count)
        capped = min(count, 7)
        if count == 0:
            verdict = '不见'
        else:
            verdict = SHENSHU_GE.get(ss, {}).get(capped, '')

        results[ss] = {
            'count': count,
            'grade': grade,
            'verdict': verdict,
            'positions': detail.get(ss, []),
        }
        grades[grade].append(ss)

    # 汇总：仅列出出现过的十神，按歌诀顺序
    summary_parts: List[str] = []
    for ss in _SHISHEN_ORDER:
        info = results[ss]
        if info['count'] > 0:
            summary_parts.append(f"{ss}{info['count']}({info['grade']})")

    return {
        'counts': results,
        'grades': grades,
        'summary': '、'.join(summary_parts) if summary_parts else '无十神数据',
        'position_count': len(positions),
    }
