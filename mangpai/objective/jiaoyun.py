"""
jiaoyun - 盲派交运时间模块

理论来源：段建业《段氏理象学》岁运篇「交运时间（盲派特有）」
核心思想：
  交运是"何时换运"的精确时间点，大运分析是"运内做什么"，二者互补。

段氏明训（P0 修正）：交运五行按【出生年纳音五行】定"命"，非年柱天干五行。
  如乙酉年=泉中水=水命->冬至前三天亥时交运；若误用年干乙=木则会错算成
  大寒当日寅时。故命五行一律取 NAYIN_TABLE[年干支]->NAYIN_WUXING。

段氏五行交运时间表（命五行->节气 + 时辰）：
  火命：清明前三天的午时
  土命：芒种后九天辰时
  金命：处暑当日申时
  木命：大寒当日寅时
  水命：冬至前三天亥时

交运频率（P0 修正）：每步大运十年，天干管前五年、地支管后五年，故每步
  大运有两个交运点——干交运（大运起始）与支交运（起始后五年），即每 5 年
  一次交运。换运时刻均落在命五行所对应的固定节气上。

干支与起运岁（P0 修正）：大运干支序列与起运岁均由上游 dayun_list 传入，
  本模块直接复用，不自算顺逆（顺/逆方向由上游依性别、年干阴阳排定）。
  起运岁决定首个交运年：交运年 = 出生年 + 起运虚岁 - 1 + 偏移
  （理象学:3875-3877 虚岁口径；书例 2005 生 3 虚岁 → 2007）。

实现：
  - _ming_wx() 取年干支纳音五行定命五行
  - sxtwl 求节气精确儒略日时刻，按时辰偏移与天数偏移得交运精确时刻
  - compute_jiaoyun_timeline(year, dayun_list, start_age, span) 产出各步大运
    的干/支交运时刻序列，干支与起运岁复用上游 dayun_list

置信度：高（有段氏原文支持）
"""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from mangpai.objective.constants import NAYIN_TABLE, NAYIN_WUXING

import logging

logger = logging.getLogger(__name__)

# 天干序列（constants.py 未定义，本模块需要用于六十甲子顺推）
TIAN_GAN: List[str] = [
    '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸',
]
# 地支序列（与 objective.constants.DI_ZHI 一致）
DI_ZHI: List[str] = [
    '子', '丑', '寅', '卯', '辰', '巳',
    '午', '未', '申', '酉', '戌', '亥',
]

# sxtwl 节气索引（与 fate-objective engine/dayun.py _JIE_QI_NAMES 一致）：
#   0=冬至 1=小寒 2=大寒 3=立春 4=雨水 5=惊蛰 6=春分 7=清明 8=谷雨
#   9=立夏 10=小满 11=芒种 12=夏至 13=小暑 14=大暑 15=立秋 16=处暑
#   17=白露 18=秋分 19=寒露 20=霜降 21=立冬 22=小雪 23=大雪
JIEQI_INDEX: Dict[str, int] = {
    '冬至': 0, '大寒': 2, '清明': 7, '芒种': 11, '处暑': 16,
}

# ── 命五行->交运规则 (节气名, 偏移天数, 时辰地支) ──
# offset_days: 正数=节后第 N 日, 负数=节前第 N 日, 0=当日
JIAOYUN_RULES: Dict[str, Tuple[str, int, str]] = {
    '火': ('清明', -3, '午'),   # 清明前三天的午时
    '土': ('芒种', 9, '辰'),    # 芒种后九天辰时
    '金': ('处暑', 0, '申'),    # 处暑当日申时
    '木': ('大寒', 0, '寅'),    # 大寒当日寅时
    '水': ('冬至', -3, '亥'),   # 冬至前三天亥时
}

# 时辰地支->取时辰中点的小时（精确时刻近似）
ZHI_HOUR: Dict[str, int] = {
    '子': 0, '丑': 2, '寅': 4, '卯': 6, '辰': 8, '巳': 10,
    '午': 12, '未': 14, '申': 16, '酉': 18, '戌': 20, '亥': 22,
}

# 每步大运的干/支交运点：天干管前五年（起始即交），地支管后五年（起始+5年交）
# 顺序为先干后支，二者相隔 5 年，故整体交运频率为 5 年一次。
_YUN_PARTS: List[Tuple[str, int]] = [('干', 0), ('支', 5)]


def _year_gz(year: int) -> str:
    """公历年->年柱干支。公元 4 年为甲子年，故干=(year-4)%10、支=(year-4)%12。"""
    return TIAN_GAN[(year - 4) % 10] + DI_ZHI[(year - 4) % 12]


def _ming_wx(year: int) -> str:
    """用年柱【纳音五行】定命五行（段氏明训）。

    交运五行按出生年纳音五行定，非年干五行：
      年干支 -> NAYIN_TABLE -> 纳音名 -> NAYIN_WUXING -> 五行
    如乙酉年=泉中水=水命->冬至前三天亥时交运。
    """
    nayin = NAYIN_TABLE.get(_year_gz(year), '')
    if not nayin:
        return ''
    return NAYIN_WUXING.get(nayin, '')


def _rule_desc(jieqi: str, offset_days: int, zhi: str) -> str:
    """构造规则中文描述。"""
    cn = {1: '一', 2: '二', 3: '三', 4: '四', 5: '五',
          6: '六', 7: '七', 8: '八', 9: '九', 10: '十'}
    if offset_days == 0:
        day_part = '当日'
    elif offset_days < 0:
        day_part = f'前{cn.get(abs(offset_days), str(abs(offset_days)))}天'
    else:
        day_part = f'后{cn.get(offset_days, str(offset_days))}天'
    return f'{jieqi}{day_part}{zhi}时'


def _jieqi_jd(year: int, jieqi_name: str) -> Optional[float]:
    """用 sxtwl 取 year 年 jieqi_name 节气的精确儒略日。

    注意：sxtwl.getJieQiByYear 返回的节气可能跨年（如冬至在年末、小寒大寒在次年初），
    按 jqIndex 精确匹配。
    """
    try:
        import sxtwl
    except ImportError:
        logger.warning("sxtwl 不可用，交运精确时刻无法计算")
        return None

    idx = JIEQI_INDEX.get(jieqi_name)
    if idx is None:
        return None

    candidates = [jq for jq in sxtwl.getJieQiByYear(year) if jq.jqIndex == idx]
    if not candidates:
        return None
    # 同一 jqIndex 在跨年边界可能出现两次（如立春），取该年的第一个
    return min(candidates, key=lambda j: j.jd).jd


def _jd_to_datetime(jd: float) -> Optional[datetime]:
    """儒略日->公历 datetime（秒级精度）。"""
    try:
        import sxtwl
        t = sxtwl.JD2DD(jd)
        return datetime(int(t.Y), int(t.M), int(t.D),
                        int(t.h), int(t.m), int(t.s))
    except Exception as e:
        logger.warning(f"JD->datetime 转换失败: {e}")
        return None


def _apply_offset(jieqi_dt: datetime, offset_days: int, zhi: str) -> datetime:
    """按偏移天数与时辰地支（取时辰中点）调整出交运精确时刻。"""
    adjusted = jieqi_dt + timedelta(days=offset_days)
    hour = ZHI_HOUR.get(zhi, 12)
    return adjusted.replace(hour=hour, minute=0, second=0, microsecond=0)


def _advance_gz(gz: str, step: int) -> str:
    """干支顺推 step 位（六十甲子）。step 可为负表示逆推。

    仅用于无上游 dayun_list 时的兼容退路；正常路径应直接复用上游 dayun_list，
    不在此自算顺逆。
    """
    g = TIAN_GAN.index(gz[0])
    z = DI_ZHI.index(gz[1])
    return TIAN_GAN[(g + step) % 10] + DI_ZHI[(z + step) % 12]


def _normalize_dayun_entries(
    dayun_list: Optional[List[Dict[str, Any]]],
    month_gz: Optional[str],
    span: int,
    start_age: Optional[int],
) -> List[Dict[str, Any]]:
    """归一化大运条目，供交运时刻计算复用。

    优先复用上游 dayun_list（含 gz 与 start_age，已依性别、年干阴阳排好顺逆）；
    仅当未提供 dayun_list 时，退化为从月柱顺推 span 步（兼容旧调用，非推荐路径）。

    每个归一化条目：{'gz': '丁丑', 'start_age': 5, 'order': 1}
    """
    if dayun_list:
        items = dayun_list if not span else list(dayun_list)[:span]
        entries: List[Dict[str, Any]] = []
        for i, e in enumerate(items):
            if not isinstance(e, dict):
                continue
            gz = e.get('gz', '') or f"{e.get('gan', '')}{e.get('zhi', '')}"
            if len(gz) < 2:
                continue
            sa = e.get('start_age')
            if sa is None:
                sa = (start_age if start_age is not None else 0) + 10 * i
            entries.append({
                'gz': gz,
                'start_age': int(sa),
                'order': e.get('order', i + 1),
            })
        return entries

    # 兼容退路：无上游 dayun_list，从月柱顺推 span 步
    base = start_age if start_age is not None else 0
    mg = month_gz or ''
    entries = []
    for i in range(span):
        gz = _advance_gz(mg, i + 1) if mg else ''
        entries.append({'gz': gz, 'start_age': base + 10 * i, 'order': i + 1})
    return entries


def compute_jiaoyun_timeline(
    year: int,
    dayun_list: Optional[List[Dict[str, Any]]] = None,
    start_age: Optional[int] = None,
    span: int = 9,
    month_gz: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """计算各步大运的交运时刻序列（段氏盲派交运时间）。

    用年柱【纳音五行】定命五行，按段氏五行交运时间表确定基准节气与交运
    时辰；sxtwl 求节气精确儒略日时刻，叠加天数与时辰偏移得交运精确时刻。

    每步大运十年，干管前五年、支管后五年，故每步产出两个交运点（干、支），
    整体交运频率为 5 年一次。大运干支与起运岁复用上游 dayun_list，不自算
    顺逆；交运年 = 出生年 + 起运虚岁 - 1 + 干/支偏移（理象学:3875-3877）。

    Args:
        year: 出生公历年
        dayun_list: 上游大运列表，每项含 gz（如 '丁丑'）与 start_age；
                    提供则直接复用其干支序列与起运岁（推荐路径）。
        start_age: 起运岁（上游传入）；dayun_list 条目缺 start_age 时以此兜底，
                   未提供 dayun_list 时作为首步起运岁。
        span: 计算多少步大运（每步产出干/支两个交运点）。dayun_list 不足则
              按实际条数计算。
        month_gz: 月柱干支（兼容旧调用：未提供 dayun_list 时从月柱顺推）。

    Returns:
        交运时刻列表，按时间顺序排列。每项含：
        {
            'order': 1,                  # 第几步大运（从1起）
            'point': 1,                  # 交运点全局序号（从1起）
            'part': '干',                # 该交运点属干管/分管（'干'/'支'）
            'gz': '丁丑',                # 该步大运干支
            'ming_wx': '水',             # 命五行（年柱纳音五行）
            'rule': '冬至前三天亥时',     # 交运规则描述
            'jieqi': '冬至',             # 基准节气
            'offset_days': -3,           # 节气偏移天数
            'offset_zhi': '亥',          # 交运时辰地支
            'jiaoyun_age': 5,            # 交运时岁数
            'jiaoyun_year': 2005,        # 交运所在公历年
            'jiaoyun_dt': datetime(...), # 交运精确时刻
            'jiaoyun_iso': '2005-12-19T22:00:00',
        }
        若 sxtwl 不可用或计算失败，对应项含 'error' 字段。
    """
    ming_wx = _ming_wx(year)
    rule = JIAOYUN_RULES.get(ming_wx)
    if rule is None:
        return [{'error': f'命五行 {ming_wx} 无对应交运规则', 'ming_wx': ming_wx}]

    jieqi_name, offset_days, offset_zhi = rule
    rule_desc = _rule_desc(jieqi_name, offset_days, offset_zhi)
    entries = _normalize_dayun_entries(dayun_list, month_gz, span, start_age)

    timeline: List[Dict[str, Any]] = []
    point = 0
    for e in entries:
        for part, age_off in _YUN_PARTS:
            point += 1
            age = e['start_age'] + age_off
            # 起运岁为虚岁（理象学:3875-3877）：虚岁 N → 公历年 = 出生年+N-1。
            # 书例 :3916-3922：2005 生 3 虚岁起运 → 交运年 2007（非 2008）
            jy = year + age - 1

            base: Dict[str, Any] = {
                'order': e['order'],
                'point': point,
                'part': part,
                'gz': e['gz'],
                'ming_wx': ming_wx,
                'rule': rule_desc,
                'jieqi': jieqi_name,
                'offset_days': offset_days,
                'offset_zhi': offset_zhi,
                'jiaoyun_age': age,
                'jiaoyun_year': jy,
            }

            jd = _jieqi_jd(jy, jieqi_name)
            if jd is None:
                base['error'] = f'{jy}年 {jieqi_name} 节气计算失败'
                timeline.append(base)
                continue

            jieqi_dt = _jd_to_datetime(jd)
            if jieqi_dt is None:
                base['error'] = f'{jy}年 JD->datetime 转换失败'
                timeline.append(base)
                continue

            jiaoyun_dt = _apply_offset(jieqi_dt, offset_days, offset_zhi)
            base['jiaoyun_dt'] = jiaoyun_dt
            base['jiaoyun_iso'] = jiaoyun_dt.isoformat()
            timeline.append(base)

    return timeline


def compute_jiaoyun_analysis(
    year: int,
    dayun_list: Optional[List[Dict[str, Any]]] = None,
    start_age: Optional[int] = None,
    span: int = 9,
    month_gz: Optional[str] = None,
) -> Dict[str, Any]:
    """交运分析聚合：时间线 + 摘要。

    供 MangpaiEngine.compute_all() 调用，产出 jiaoyun_analysis 字段。
    """
    ming_wx = _ming_wx(year)
    rule = JIAOYUN_RULES.get(ming_wx)
    if rule is None:
        return {'ming_wx': ming_wx, 'error': f'命五行 {ming_wx} 无对应交运规则'}

    jieqi_name, offset_days, offset_zhi = rule
    timeline = compute_jiaoyun_timeline(
        year, dayun_list=dayun_list, start_age=start_age,
        span=span, month_gz=month_gz,
    )

    valid = [t for t in timeline if 'jiaoyun_dt' in t]
    next_jiaoyun: Optional[Dict[str, Any]] = None
    now = datetime.now()
    if valid:
        future = [t for t in valid if t['jiaoyun_dt'] > now]
        if future:
            next_jiaoyun = future[0]

    n_dy = len({t.get('order') for t in timeline})
    summary_parts = [
        f"命五行：{ming_wx}（年柱纳音）",
        f"交运规则：{_rule_desc(jieqi_name, offset_days, offset_zhi)}",
        f"每5年一交（干支各一点），共{n_dy}步大运{len(timeline)}个交运点",
    ]
    if next_jiaoyun:
        summary_parts.append(
            f"下一交运：{next_jiaoyun['gz']}（{next_jiaoyun.get('part', '')}，"
            f"{next_jiaoyun['jiaoyun_iso']}）"
        )

    return {
        'ming_wx': ming_wx,
        'rule': _rule_desc(jieqi_name, offset_days, offset_zhi),
        'jieqi': jieqi_name,
        'offset_days': offset_days,
        'offset_zhi': offset_zhi,
        'timeline': timeline,
        'next_jiaoyun': next_jiaoyun,
        'summary': '；'.join(summary_parts),
    }


def safe_compute_jiaoyun(
    year: int,
    month_gz: str = '',
    dayun_list: Optional[List[Dict[str, Any]]] = None,
    start_age: Optional[int] = None,
    span: int = 9,
) -> Dict[str, Any]:
    """安全计算交运（兜底返回，供 compute_all() _safe_compute 调用）。

    前两位位置参数 (year, month_gz) 保持向后兼容（旧引擎调用）；
    上游若已排好大运，应经 dayun_list / start_age 传入以复用干支与起运岁。
    """
    try:
        return compute_jiaoyun_analysis(
            year, dayun_list=dayun_list, start_age=start_age,
            span=span, month_gz=month_gz,
        )
    except Exception as e:
        logger.warning(f"交运计算失败: {e}", exc_info=True)
        return {
            'ming_wx': _ming_wx(year) if year else '',
            'error': str(e),
        }


__all__ = [
    'compute_jiaoyun_timeline',
    'compute_jiaoyun_analysis',
    'safe_compute_jiaoyun',
    'JIAOYUN_RULES',
    'JIEQI_INDEX',
]
