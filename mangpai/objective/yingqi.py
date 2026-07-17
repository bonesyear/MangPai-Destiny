"""
yingqi - 盲派应期客观检测·客观层（objective）

理论来源：段建业《盲派中级命理学》第二章「应期」（源文 645-1309 行）
核心思想：应期=命局结构在时间轴上的兑现点。本模块实现三种**客观检测**机制，
          只产出原始事实（哪柱对应哪大限 / 哪些柱见禄原身 / 哪些藏干可透流年），
          不做应期推断与优先性判断（交 subjective.yingqi_subj）。

三种机制：
  1. 大限映射：四柱对应人生时段，纯位置-时段映射，与书中大限一致：
       年柱 -> 1-18 岁（少年）   月柱 -> 18-35 岁（青年）
       日柱 -> 35-55 岁（中年）  时柱 -> 55 岁+（晚年）
     原局某柱的结构（如某柱做功、某柱被制）落在该柱大限时段兑现。
     ⚠ 宫位年龄统一决定（2026-07 收口）：全引擎宫位年龄统一为书中大限值
       （1-18/18-35/35-55/55+），xiangfa.py 的 GONG_WEI_XIANG 已同步改采本套，
       原六亲口径（1-15/16-30/31-50/50+）废弃，见 MODULE_ATTRS.md。

  2. 禄与原身：禄为天干在地支的临官位，即天干之「原身」；天干为「原神」。
       见禄=原身见原神（地支禄位现=天干原神到场）。
       四库辰戌丑未无天干禄位（LU 表已编码：禄仅落寅卯巳午申酉亥子，即四生+四正），
       故四库无原身--此为客观事实，由 LU 表自然保证，无须特判。

  3. 遁藏透干：地支藏干透出流年天干=应期。藏干透流年天干，原局潜伏之气到场。
       寅藏丙甲戊（段氏透出顺序，见源文应期篇）；藏干顺序由 CANG_GAN_MANGPAI 给出，
       本模块保留各藏干的本/中/余气顺序供上层判优先（透本气先于余气）。

依赖方向单向：objective <- constants/canggan；不反向依赖 subjective。
已知争议已收口：大限年龄区间曾有 1-15/16-30/... 与 1-18/18-35/... 两套，
          2026-07 统一为书中大限套（本套），xiangfa.GONG_WEI_XIANG 同。
置信度：中
"""
from typing import Dict, List, Optional, Union

from mangpai.objective.constants import (
    LU, CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai

# ── 大限映射：柱位 -> 年龄区间（段氏《盲派中级命理学》应期篇大限值）──
# 与书中大限一致：年1-18 / 月18-35 / 日35-55 / 时55+。
# 全引擎宫位年龄统一套（2026-07 收口）：xiangfa.GONG_WEI_XIANG 亦改采本套，
# 原六亲宫位口径（1-15/16-30/31-50/50+）废弃（见 MODULE_ATTRS.md 统一决定）。
DAXIAN_MAP: Dict[str, Dict] = {
    'year': {
        'pillar': '年柱', 'age_range': (1, 18), 'stage': '少年', 'desc': '1-18岁（少年大限）',
    },
    'month': {
        'pillar': '月柱', 'age_range': (18, 35), 'stage': '青年', 'desc': '18-35岁（青年大限）',
    },
    'day': {
        'pillar': '日柱', 'age_range': (35, 55), 'stage': '中年', 'desc': '35-55岁（中年大限）',
    },
    'hour': {
        'pillar': '时柱', 'age_range': (55, 120), 'stage': '晚年', 'desc': '55岁+（晚年大限）',
    },
}

# ── 禄反查表：地支 -> 以其为禄的天干（原神）──
# 由 LU 表反转构建。四库辰戌丑未不在 LU 值域，故不在此表（四库无原身，客观事实）。
_ZHI_LU_OF: Dict[str, List[str]] = {}
for _g, _z in LU.items():
    _ZHI_LU_OF.setdefault(_z, []).append(_g)


def detect_daxian() -> Dict:
    """返回四柱大限映射（纯位置-时段，与书中大限一致）。

    Returns:
        {'year': {...}, 'month': {...}, 'day': {...}, 'hour': {...}}，
        每项含 pillar/age_range/stage/desc。
    """
    return {k: dict(v) for k, v in DAXIAN_MAP.items()}


def daxian_of_age(age: Union[int, float]) -> Optional[str]:
    """年龄 -> 所在大限柱位键（year/month/day/hour）。

    边界按书中大限区间：1-18 含 1 不含 18，18-35 含 18 不含 35，依此类推；
    55+ 含 55。越界（age<1）返回 None。

    Args:
        age: 年龄

    Returns:
        柱位键 'year'/'month'/'day'/'hour'，或 None（age<1）
    """
    if age is None or age < 1:
        return None
    for key, info in DAXIAN_MAP.items():
        lo, hi = info['age_range']
        if lo <= age < hi:
            return key
    # age>=55+ 上界 120 兜底归时柱
    if age >= 55:
        return 'hour'
    return None


def detect_lu_yuanshen(
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    day_gan: str = '',
) -> Dict:
    """检测禄与原身（见禄=原身见原神）。

    禄为天干之原身、天干为原神。某柱地支恰为某天干之禄 -> 该柱见禄（原神到场）。
    四库辰戌丑未无天干禄位（_ZHI_LU_OF 不含四库），故四库永不见禄、无原身。

    支持两种签名：旧位置参数（gans/zhis/day_gan），或首个参数为 Pillars 对象。

    Args:
        gans: 四柱天干 [year, month, day, hour]（或 Pillars 对象）
        zhis: 四柱地支 [year, month, day, hour]
        day_gan: 日干（缺省由 gans[day] 推导）

    Returns:
        {
          'lu_pillars': [见禄记录],     # 各柱见禄记录，每项含 pillar/zhi/lu_of(原神)/pos/order
          'day_lu_seen': bool,         # 日干之禄是否在局
          'day_lu_zhi': str,           # 日干禄地支（无则空串）
          'yuanshen_via_lu': [str],    # 经禄位现身的原神天干（去重）
          'no_yuanshen_zhis': [str],   # 局中四库地支（无原身者）
        }
    """
    if is_pillars(gans):
        p = gans
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        if not day_gan:
            day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []
    if not day_gan and len(gans) == 4:
        day_gan = gans[PILLAR_KEYS.index('day')]

    lu_pillars: List[Dict] = []
    yuanshen_via_lu: List[str] = []
    no_yuanshen_zhis: List[str] = []
    seen_zhis: set = set()

    for i, z in enumerate(zhis):
        if not z:
            continue
        seen_zhis.add(z)
        if z not in _ZHI_LU_OF:
            # 四库（辰戌丑未）无原身：记录但不算见禄
            if z in ('辰', '戌', '丑', '未'):
                no_yuanshen_zhis.append(z)
            continue
        for gan_yuanshen in _ZHI_LU_OF[z]:
            lu_pillars.append({
                'pillar': PILLAR_NAMES_CN[i],
                'pos': f'{PILLAR_KEYS[i]}_zhi',
                'zhi': z,
                'lu_of': gan_yuanshen,  # 原神（此禄所属天干）
                'desc': f'{PILLAR_NAMES_CN[i]}支{z}为{gan_yuanshen}之禄（原身见原神）',
            })
            if gan_yuanshen not in yuanshen_via_lu:
                yuanshen_via_lu.append(gan_yuanshen)

    day_lu_zhi = LU.get(day_gan, '')
    day_lu_seen = bool(day_lu_zhi) and day_lu_zhi in seen_zhis

    return {
        'lu_pillars': lu_pillars,
        'day_lu_seen': day_lu_seen,
        'day_lu_zhi': day_lu_zhi,
        'yuanshen_via_lu': yuanshen_via_lu,
        'no_yuanshen_zhis': no_yuanshen_zhis,
    }


def detect_duncang_tougan(
    zhis: Optional[List[str]] = None,
    target_gans: Optional[Union[List[str], str]] = None,
    gans: Optional[List[str]] = None,
) -> Dict:
    """检测地支藏干透出目标天干（遁藏透干=应期）。

    遁藏透干：地支藏干透出天干即为应期信号。流年/大运天干恰为某柱地支藏干 ->
    该柱潜伏之气到场兑现。藏干顺序由 CANG_GAN_MANGPAI 给出（本气/中气/余气），
    透本气优先于余气（order 越小越先），供上层判应期先後。
    寅藏甲(本)丙(中)戊(余)即段氏「寅藏丙甲戊」之透出序（本中余气序）。

    支持两种签名：旧位置参数（zhis/target_gans/gans），或首个参数为 Pillars 对象
    （此时 target_gans 须显式传入）。

    Args:
        zhis: 四柱地支（或 Pillars 对象）
        target_gans: 目标天干（流年干/大运干），单个字符或列表
        gans: 四柱天干（可选，透干引拔用；目前仅记录，不阻断检测）

    Returns:
        {
          'tougan_hits': [透干命中记录],  # 每项含 pillar/zhi/canggan/hit_gan/pos/order
          'hit_gans': [str],            # 命中的目标天干（去重，按命中顺序）
        }
    """
    if is_pillars(zhis):
        p = zhis
        if gans is None:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]

    zhis = zhis or []
    if target_gans is None:
        target_set: set = set()
    elif isinstance(target_gans, str):
        target_set = {target_gans}
    else:
        target_set = set(target_gans)

    tougan_hits: List[Dict] = []
    hit_gans: List[str] = []

    for i, z in enumerate(zhis):
        if not z:
            continue
        canggan = get_canggan_mangpai(z)  # [(干, 气名), ...] 本/中/余气序
        for order, (cg, qi) in enumerate(canggan):
            if cg in target_set:
                tougan_hits.append({
                    'pillar': PILLAR_NAMES_CN[i],
                    'pos': f'{PILLAR_KEYS[i]}_zhi',
                    'zhi': z,
                    'canggan': [c[0] for c in canggan],
                    'hit_gan': cg,
                    'qi': qi,           # 本气/中气/余气
                    'order': order,     # 藏干序：0=本气最先透
                    'desc': f'{PILLAR_NAMES_CN[i]}支{z}藏{cg}（{qi}）透干，应期',
                })
                if cg not in hit_gans:
                    hit_gans.append(cg)

    return {
        'tougan_hits': tougan_hits,
        'hit_gans': hit_gans,
    }


def detect_yingqi(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    target_gans: Optional[Union[List[str], str]] = None,
    age: Optional[Union[int, float]] = None,
) -> Dict:
    """应期客观检测聚合：大限映射 + 禄与原身 + 遁藏透干。

    一次性产出三种应期机制的原始事实，交 subjective.yingqi_subj 做优先性与综合推断。
    本函数纯检测、无解释；缺省字段静默跳过。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    analyze_yingqi(pillars, target_gans='甲', age=20) 等价展开四柱。

    Args:
        day_gan: 日干（或 Pillars 对象）
        gans: 四柱天干
        zhis: 四柱地支
        target_gans: 目标天干（流年/大运干），单个或列表
        age: 当前年龄（用于定位所在大限柱）

    Returns:
        {
          'daxian': {...},            # detect_daxian() 全映射
          'active_daxian': str|None,  # age 所在大限柱位键
          'lu_yuanshen': {...},       # detect_lu_yuanshen() 结果
          'duncang_tougan': {...},    # detect_duncang_tougan() 结果
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        if not day_gan or (gans and not any(g == day_gan for g in gans)):
            day_gan = p.day_gan
        else:
            day_gan = p.day_gan

    return {
        'daxian': detect_daxian(),
        'active_daxian': daxian_of_age(age) if age is not None else None,
        'lu_yuanshen': detect_lu_yuanshen(gans, zhis, day_gan),
        'duncang_tougan': detect_duncang_tougan(zhis, target_gans, gans),
    }


__all__ = [
    'DAXIAN_MAP',
    'detect_daxian',
    'daxian_of_age',
    'detect_lu_yuanshen',
    'detect_duncang_tougan',
    'detect_yingqi',
]
