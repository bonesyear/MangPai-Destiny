"""
yingqi_subj - 盲派应期主观推断·主观层（subjective）

理论来源：段建业《盲派中级命理学》第二章「应期」、第十四章流年应期总论
          （源文 645-1309、6127+ 行）
核心思想：在 objective.yingqi 的三种客观检测（大限映射/禄与原身/遁藏透干）之上，
          做应期**优先性**与**综合推断**。

两大主观规则：
  1. 禄与原身优先性：
       见禄=原身见原神，原神直接到场，为最强应期信号，优先于透干应期。
       日干之禄现身=最高优先（自身原神到场）；他干之禄=次优先（相关原神到场）；
       四库辰戌丑未无原身（LU 表已编码），不产生禄应期。
  2. 综合应期推断（大限 ∩ 大运 ∩ 流年）：
       段氏「原局是车，大运是路」--原局（车）定方向与结构、大运（路）定承载与时段、
       流年定触发点。三者交集方为真应期：
         大限（natal 柱位时段）定**什么结构在何时兑现**（车的内容）；
         大运定**10 年窗口**（路何时到）；
         流年定**精确触发年**（禄/原身/透干）。
       优先级：原局应期 > 大运应期 > 流年应期。原局无此结构，则大运流年空转（路无车可载）。

消费关系：
  - objective.yingqi（大限映射/禄与原身/遁藏透干检测）
  - objective.constants（LU/PILLAR_KEYS/GAN_WX/WX_KE 等）
  - subjective.liunian（流年-大运互动，可选）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议已收口：大限年龄区间全引擎统一为书中大限值（1-18/18-35/35-55/55+），
          原六亲宫位口径已废弃（见 objective.yingqi 与 MODULE_ATTRS.md 统一决定）。
置信度：中
"""
from typing import Dict, List, Optional, Tuple, Union

from mangpai.objective.constants import (
    GAN_WX, WX_KE, WX_SHENG,
    LU, PILLAR_KEYS, is_pillars, ZHI_WX,
    LIU_CHONG, LIU_HAI, XING_PAIRS,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.changsheng import get_changsheng_mangpai
from mangpai.objective.yingqi import (
    DAXIAN_MAP, detect_daxian, daxian_of_age,
    detect_lu_yuanshen, detect_duncang_tougan, detect_yingqi,
)

_YANG_GANS = set('甲丙戊庚壬')

# 禄反查表：地支 -> 以其为禄的天干（原神）；与 objective.yingqi._ZHI_LU_OF 同构
_ZHI_LU_OF: Dict[str, List[str]] = {}
for _g, _z in LU.items():
    _ZHI_LU_OF.setdefault(_z, []).append(_g)


def _compute_shishen(day_gan: str, gan: str) -> str:
    """计算 gan 相对 day_gan 的十神（与 dayun._compute_shishen 同口径）。"""
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


# ───────────────────── 1. 禄与原身优先性 ─────────────────────

def judge_lu_yuanshen_priority(
    lu_yuanshen: Optional[Dict] = None,
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
) -> Dict:
    """禄与原身优先性规则。

    见禄=原身见原神，原神直接到场，为最强应期信号，优先于透干应期。
    优先级分层：
      - 日干之禄现身（day_lu_seen）= 最高优先（自身原神到场，主自身应期）；
      - 他干之禄现身（yuanshen_via_lu 含非日干）= 次优先（相关六亲/十神原神到场）；
      - 四库辰戌丑未无原身（no_yuanshen_zhis），不产生禄应期（客观事实，LU 表已保证）。

    Args:
        lu_yuanshen: detect_lu_yuanshen 输出（缺省则自调）
        day_gan: 日干
        gans/zhis: 四柱（lu_yuanshen 缺省时用）

    Returns:
        {
          'day_lu_priority': '最高'|'无',   # 日干禄优先级
          'other_lu_priority': '次'|'无',   # 他干禄优先级
          'priority_signals': [str],        # 优先性信号（按优先级降序）
          'top_signal': str|None,           # 最高优先信号
          'no_yuanshen_zhis': [str],        # 无原身四库
          'desc': str,
        }
    """
    if is_pillars(lu_yuanshen):
        p = lu_yuanshen
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
        lu_yuanshen = None
    if lu_yuanshen is None:
        lu_yuanshen = detect_lu_yuanshen(gans, zhis, day_gan)

    signals: List[str] = []
    day_lu_seen = bool(lu_yuanshen.get('day_lu_seen'))
    day_lu_zhi = lu_yuanshen.get('day_lu_zhi', '')
    yuanshen_via_lu: List[str] = lu_yuanshen.get('yuanshen_via_lu', []) or []
    no_yuanshen_zhis: List[str] = lu_yuanshen.get('no_yuanshen_zhis', []) or []

    # 他干原神 = 经禄现身的原神中非日干者
    other_yuanshen = [g for g in yuanshen_via_lu if g != day_gan]

    if day_lu_seen:
        signals.append(f'最高：日干{day_gan}之禄{day_lu_zhi}现身，自身原神到场（日干应期）')
    if other_yuanshen:
        signals.append(f'次：他干之禄现身，原神{ "、".join(other_yuanshen) }到场（六亲/十神应期）')
    if no_yuanshen_zhis:
        signals.append(f'四库{ "、".join(no_yuanshen_zhis) }无原身，不产生禄应期')

    top = signals[0] if signals else None
    desc = '；'.join(signals) if signals else '局中无禄现身（或仅四库无原身），无禄与原身应期信号'

    return {
        'day_lu_priority': '最高' if day_lu_seen else '无',
        'other_lu_priority': '次' if other_yuanshen else '无',
        'priority_signals': signals,
        'top_signal': top,
        'no_yuanshen_zhis': no_yuanshen_zhis,
        'desc': desc,
    }


# ───────────────────── 2. 综合应期推断 ─────────────────────

def _lu_trigger(zhi: str, gans: List[str], day_gan: str) -> List[str]:
    """某地支（大运支/流年支）为哪些天干之禄 -> 原神到场触发列表。

    四库辰戌丑未不在 _ZHI_LU_OF，自然返回空（无原身不触发）。
    """
    if not zhi:
        return []
    return list(_ZHI_LU_OF.get(zhi, []))


def _classify_lu(ln_lu: List[str], gans: List[str], day_gan: str) -> Dict:
    """禄触发归属分类（修「他干禄误归日主」：区分日干/命局他干/外神之禄）。

    见禄=原神到场，但到场之原神须分清归属：
      - 日干之禄（day_lu）：日干自身原神到场，主日干应期，最强；
      - 命局他干之禄（natal_other）：命局所现他干之原神到场，主相关六亲/十神应期；
      - 外神之禄（foreign）：命局无此干，流年/大运携来之原神非命局原神，
        不计为日主或命局触发（他干禄误归日主之根因即此前未分外神）。

    Returns:
        {'day_lu': bool, 'natal_other': [str], 'foreign': [str],
         'who': '日干'|'他干'|'外神'|'', 'trigger': bool}
        trigger = 日干禄或命局他干禄命中（外神禄不计触发）。
    """
    gans_set = set(gans or [])
    day_lu = bool(day_gan) and day_gan in ln_lu
    natal_other = [g for g in ln_lu if g != day_gan and g in gans_set]
    foreign = [g for g in ln_lu if g != day_gan and g not in gans_set]
    if day_lu:
        who = '日干'
    elif natal_other:
        who = '他干'
    elif foreign:
        who = '外神'
    else:
        who = ''
    return {
        'day_lu': day_lu,
        'natal_other': natal_other,
        'foreign': foreign,
        'who': who,
        'trigger': day_lu or bool(natal_other),
    }


def infer_comprehensive_yingqi(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    dayun_gan: str = '',
    dayun_zhi: str = '',
    liunian_gan: str = '',
    liunian_zhi: str = '',
    age: Optional[Union[int, float]] = None,
    liunian_interaction: Optional[List[Dict]] = None,
) -> Dict:
    """综合应期推断：大限 ∩ 大运 ∩ 流年（原局是车，大运是路）。

    段氏「原局是车，大运是路」原则：
      - 原局（车）定结构与方向：大限（natal 柱位时段）指出**什么结构在哪个年龄段兑现**。
      - 大运（路）定承载与窗口：大运干支带来十神与关系，是车驶向目的地的路。
      - 流年定触发点：流年干透藏干 / 流年支到禄位 = 精确触发年。
      优先级：原局应期 > 大运应期 > 流年应期。原局无结构兑现则大运流年空转。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    infer_comprehensive_yingqi(pillars, dayun_gan='甲', dayun_zhi='子', ...) 等价展开。

    Args:
        day_gan: 日干（或 Pillars 对象）
        gans: 四柱天干
        zhis: 四柱地支
        dayun_gan/dayun_zhi: 当前大运干支
        liunian_gan/liunian_zhi: 流年干支
        age: 当前年龄（定位大限柱）
        liunian_interaction: 流年-大运互动（来自 liunian.py，可选，透传为路车配合信号）

    Returns:
        {
          'daxian_yingqi': {...},     # 大限应期（车：何结构兑现）
          'dayun_yingqi': {...},      # 大运应期（路：10年窗口带来什么）
          'liunian_yingqi': {...},    # 流年应期（触发点）
          'priority': '原局>大运>流年',
          'intersection': bool,       # 三者是否交集（真应期成立）
          'intersection_signals': [str],
          'conclusion': str,          # 综合结论
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []

    # ── 原局客观检测（车的内容）──
    yingqi = detect_yingqi(day_gan, gans, zhis, target_gans=liunian_gan, age=age)
    lu = yingqi.get('lu_yuanshen', {}) or {}
    tou = yingqi.get('duncang_tougan', {}) or {}
    active = yingqi.get('active_daxian')

    # ── 大限应期（原局=车）：何柱结构在此时段兑现 ──
    daxian_signals: List[str] = []
    daxian_content = ''
    if active:
        info = DAXIAN_MAP.get(active, {})
        idx = PILLAR_KEYS.index(active)
        gan_ss = _compute_shishen(day_gan, gans[idx]) if idx < len(gans) else ''
        daxian_content = f'{info.get("pillar")}（{info.get("desc")}）主{gan_ss or "本气"}结构兑现'
        daxian_signals.append(f'大限应期：{daxian_content}')
        # 大限柱是否含禄原身（原神在大限阶段到场）
        pillar_lu = [lp for lp in lu.get('lu_pillars', []) if lp.get('pos', '').startswith(active)]
        if pillar_lu:
            daxian_signals.append(
                f'  大限柱见禄（{ "、".join(lp["lu_of"] for lp in pillar_lu) }原身到场）'
            )
    else:
        daxian_signals.append('大限应期：未给定年龄，无法定位大限柱')

    # ── 大运应期（路）：大运干支带来什么 ──
    dayun_signals: List[str] = []
    if dayun_gan or dayun_zhi:
        dy_ss = _compute_shishen(day_gan, dayun_gan) if dayun_gan else ''
        if dy_ss:
            dayun_signals.append(f'大运应期：大运干{dayun_gan}为{dy_ss}（路带来{dy_ss}）')
        # 大运支到禄位=原神到场
        dy_lu = _lu_trigger(dayun_zhi, gans, day_gan)
        if dy_lu:
            dy_cls = _classify_lu(dy_lu, gans, day_gan)
            if dy_cls['who']:
                dayun_signals.append(
                    f'  大运支{dayun_zhi}为{ "、".join(dy_lu) }之禄，{dy_cls["who"]}原神随路到场'
                )
        # 大运支透干（大运支藏干透于原局天干）
        if dayun_zhi:
            dy_tou = detect_duncang_tougan(zhis, list(set(gans) | {dayun_gan}))
            if dy_tou.get('tougan_hits'):
                # 大运支藏干若透于原局，路激活原局潜伏之气
                dy_hidden = [cg for cg, _ in get_canggan_mangpai(dayun_zhi)]
                activated = [h for h in dy_tou['tougan_hits'] if h['hit_gan'] in dy_hidden]
                if activated:
                    dayun_signals.append(f'  大运支{dayun_zhi}藏干透原局，路激活潜伏之气')
    else:
        dayun_signals.append('大运应期：无大运干支，路未到')

    # ── 流年应期（触发点）：透干 + 禄/原身 ──
    liunian_signals: List[str] = []
    if liunian_gan or liunian_zhi:
        # 透干应期：流年干透某柱藏干
        tou_hits = tou.get('tougan_hits', []) or []
        if tou_hits:
            for h in tou_hits:
                liunian_signals.append(
                    f'流年应期：流年干{liunian_gan}透{h["pillar"]}支{h["zhi"]}藏{h["hit_gan"]}（{h["qi"]}）'
                )
        # 禄/原身应期：流年支到禄位
        ln_lu = _lu_trigger(liunian_zhi, gans, day_gan)
        if ln_lu:
            ln_cls = _classify_lu(ln_lu, gans, day_gan)
            if ln_cls['who']:
                liunian_signals.append(
                    f'流年应期：流年支{liunian_zhi}为{ "、".join(ln_lu) }之禄，{ln_cls["who"]}原神触发'
                )
        if not liunian_signals:
            liunian_signals.append('流年应期：流年干支无透干/禄触发')
    else:
        liunian_signals.append('流年应期：无流年干支')

    if liunian_interaction:
        dayun_signals.append(f'  流年-大运互动：{len(liunian_interaction)}项（路车配合）')

    # ── 交集判定（真应期成立）──
    # 禄触发归属：日干禄/命局他干禄/外神禄分清（修「他干禄误归日主」——外神禄
    #   不再混称日干/他干，仅作见禄信号计入触发，归属标签为「外神」）。
    ln_lu_all = _lu_trigger(liunian_zhi, gans, day_gan)
    ln_lu_cls = _classify_lu(ln_lu_all, gans, day_gan)
    has_daxian = active is not None
    has_dayun = bool(dayun_gan or dayun_zhi)
    # 见禄即原神到场（含外神禄），计流年触发；归属由 ln_lu_cls['who'] 标签区分。
    has_liunian_trigger = bool(tou.get('tougan_hits')) or bool(ln_lu_all)
    # 交集：大限结构兑现 + 大运路到 + 流年触发三者齐备为真应期；
    # 原局优先：大限柱见禄原身时，原局应期已强，大运流年仅作承载即可成立。
    daxian_pillar_lu = bool(active) and any(
        lp.get('pos', '').startswith(active) for lp in lu.get('lu_pillars', [])
    )
    intersection = has_daxian and has_dayun and (
        has_liunian_trigger or daxian_pillar_lu
    )

    inter_signals: List[str] = []
    if has_daxian:
        inter_signals.append('原局大限结构在兑现时段')
    if has_dayun:
        inter_signals.append('大运路已到')
    if has_liunian_trigger:
        who_tag = ln_lu_cls['who'] if (ln_lu_all and not tou.get('tougan_hits')) else ''
        inter_signals.append(
            '流年触发点到位' + (f'（禄原神归属：{who_tag}）' if who_tag else '')
        )
    if daxian_pillar_lu:
        inter_signals.append('原局大限柱见禄原身（原局应期优先成立）')

    priority = '原局>大运>流年'
    # commit 阈值：大限∩大运∩流年三要素命中其二即输出应期结论（阈值校准：
    #   原阈值过保守，检测到 trigger 仍被「无大限(age 缺省)」覆盖为无明确应期）。
    hit_count = (1 if has_daxian else 0) + (1 if has_dayun else 0) + (1 if has_liunian_trigger else 0)
    if intersection:
        conclusion = '真应期成立：原局结构（车）在大运（路）承载下、流年触发兑现'
    elif hit_count >= 2:
        hit_parts = []
        if has_daxian:
            hit_parts.append('大限结构兑现')
        if has_dayun:
            hit_parts.append('大运路到')
        if has_liunian_trigger:
            hit_parts.append('流年触发')
        conclusion = '应期成立：大限/大运/流年三要素命中其二（' + '、'.join(hit_parts) + '），结构兑现时段显现'
    elif hit_count == 1:
        if has_daxian:
            conclusion = '原局应期：结构在兑现时段，大运流年未配合（路未到/未触发）'
        elif has_dayun:
            conclusion = '待应期：大运路到，原局结构/流年触发未配合'
        else:
            conclusion = '待应期：流年触发到位，原局结构/大运未配合'
    else:
        conclusion = '无明确应期：大限/大运/流年三要素均未到位'

    return {
        'daxian_yingqi': {
            'active': active,
            'content': daxian_content,
            'signals': daxian_signals,
            'pillar_lu_seen': daxian_pillar_lu,
        },
        'dayun_yingqi': {
            'has_dayun': has_dayun,
            'signals': dayun_signals,
        },
        'liunian_yingqi': {
            'has_trigger': has_liunian_trigger,
            'signals': liunian_signals,
        },
        'liunian_trigger': has_liunian_trigger,
        'priority': priority,
        'intersection': intersection,
        'intersection_signals': inter_signals,
        'conclusion': conclusion,
    }


# ───────────────────── 3. 寿元机制推演 ─────────────────────

# 坏禄关系并集：冲/穿/刑/破（书言「子卯破」即引擎子卯刑，见 cj1:1838/cj2:5278；
#   盲派破仅子卯/卯午互破——理象学:2934-2955「子破卯，卯破午；也可以反过来破」
#   三例皆子卯/卯午，标准六破其余各对（寅亥等）无段氏书锚，不入此集；
#   自刑剔除——同字重现归「原局字到位」而非坏）
_HUAI_PAIRS = set(LIU_CHONG) | set(LIU_HAI) | {('卯', '午'), ('午', '卯')} | {
    (a, b) for a, b in XING_PAIRS if a != b
}


def _is_huai(a: str, b: str) -> bool:
    return bool(a and b) and a != b and ((a, b) in _HUAI_PAIRS or (b, a) in _HUAI_PAIRS)


def _is_zhengke(zhi: str, oz: str) -> bool:
    """zhi 被 oz 五行正克（书诀「穿害克绝命难长」gaoji:16148、「最忌寿星遭刑克」
    gaoji:16547 之「克」；书例 yx2:7486「申金到位被局中官星火正克」）。
    仅用于「到位被坏」语境——原局静克是做功常态，不计带病。"""
    return WX_KE.get(ZHI_WX.get(oz, ''), '') == ZHI_WX.get(zhi, '')


def detect_shouyuan_jixie(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    dayun_gan: str = '',
    dayun_zhi: str = '',
    liunian_gan: str = '',
    liunian_zhi: str = '',
) -> Dict:
    """寿元机制推演（只做推演验证：识别「带病逢引动」结构，不输出死亡/寿数预测）。

    段氏寿元章四类机制（书锚=备查矿书明文行号，逐条见 tests/test_yingqi_shouyuan.py）：
      - 破禄：日主/寿元星/原局他干之禄被冲破穿刑——原局带病（cj1:1838「原局子卯破
        破禄，破禄而死」）或运岁引动（cj2:5278「子卯破禄…把禄给坏了」）。
      - 禄到位：运岁支为日主或原局干之禄（「禄到为寿到」cj1:1838/cj1:2477/cj1:2741）。
        到位本身中性：原局无带病则吉（反锚 cj1:697「酉到为日主到了…高考状元」）。
      - 寿元星被坏：寿元星定位诀「食神为寿第一尊，无食看印印为根」
        （gaoji:16148/16157——无食或食伤受伤无用则印级补位；支/藏干食伤亦为寿，
        gaoji:4600/7651）；其禄/根被坏或透干坐绝（cj2:6042「癸水寿元星见子水为禄…
        被午冲」；cj2:3704「穿倒食神损寿元」；gaoji:16172「坐巳火绝地」；
        gaoji:16206-16216「印根辰被冲散…印根被拔寿星倒」）。
      - 原局字到位：运岁干/支重现原局字或透原局支藏干，引动其受坏结构
        （yx2:7486「申金到位被局中官星火正克」——到位逢正克亦计，总诀
        「最忌寿星遭刑克」gaoji:16547；cj2:4160「丁虚透为原局的戌到了」）。
      - 坏关系并集=冲/穿/刑/破；破从盲派书口径仅子卯/卯午互破
        （理象学:2934-2955），标准六破其余各对无段氏书锚不入。

    Returns:
        {'signals': [str], 'mechanisms': [str], 'risk': bool, 'desc': str}
        risk=True 仅表示「带病逢引动」推演成立，非事件预测；本函数不进 engine 消费链。
    """
    gans = list(gans or [])
    zhis = list(zhis or [])
    empty = {'signals': [], 'mechanisms': [], 'risk': False, 'desc': '四柱不全，无法推演'}
    if not day_gan or len(gans) < 4 or len(zhis) < 4:
        return empty

    _ss = lambda g: _compute_shishen(day_gan, g)
    # 寿元星定位诀：「食神为寿第一尊，无食看印印为根」（gaoji:16148）。
    # 支/藏干食伤亦为寿元星（gaoji:4600「甲寅伤官…为寿元星」、7651「日支寅木
    #   为食神…为寿元星」——不只查天干）。
    shishang = sorted({g for g in gans if _ss(g) in ('食神', '伤官')})
    shishang += [g for g in sorted({cg for z in zhis for cg, _ in get_canggan_mangpai(z)
                                    if _ss(cg) in ('食神', '伤官')}) if g not in shishang]

    def _no_root(g: str) -> bool:
        """虚浮无根：禄与藏干根均不在局。"""
        if LU.get(g, '') in zhis:
            return False
        return not any(any(cg == g for cg, _ in get_canggan_mangpai(z)) for z in zhis)

    def _sits_jue(g: str) -> bool:
        """透干而坐绝地（阴阳同生同死表；「水绝于巳」cj1:1846）。"""
        return any(gans[i] == g and get_changsheng_mangpai(g, zhis[i]) == '绝'
                   for i in range(min(len(gans), len(zhis))))

    # 「无食神或食神受伤无用，则看印星」（gaoji:16157）——受伤无用=透干而
    #   虚浮无根或坐绝地（案例二「丙坐辰土无功」gaoji:16204）；印级取透干印。
    if not shishang or all(g in gans and (_no_root(g) or _sits_jue(g)) for g in shishang):
        shishang += [g for g in sorted({g for g in gans if _ss(g) in ('正印', '偏印')})
                     if g not in shishang]

    # 寿元星之根：禄以外的藏干根支（案例二「癸水印星之根辰土」gaoji:16206-16210）
    star_roots: Dict[str, List[str]] = {
        g: sorted({z for z in zhis if any(cg == g for cg, _ in get_canggan_mangpai(z))})
        for g in shishang
    }

    # 禄主表：日干 / 寿元星（食伤，无食或食伤受伤则印）/ 原局他干（六亲星）
    lu_owners: List[Tuple[str, str]] = [('日干', LU.get(day_gan, ''))]
    lu_owners += [(f'寿元星({g})', LU.get(g, '')) for g in shishang]
    lu_owners += [(f'他干({g})', LU.get(g, ''))
                  for g in sorted(set(gans) - {day_gan} - set(shishang))]

    def _owners_of(zhi: str) -> List[str]:
        return [lbl for lbl, lz in lu_owners if lz == zhi]

    signals: List[str] = []
    mechanisms = set()
    natal_huai = False  # 原局带病
    arrived = False     # 到位（禄到位/原局字到位）
    triggered = False   # 运岁引动坏

    # 1) 原局带病：禄主之禄在原局且被原局他支坏
    for lbl, lz in lu_owners:
        if lz and lz in zhis and any(_is_huai(lz, oz) for oz in zhis):
            mechanisms.add('破禄')
            natal_huai = True
            signals.append(f'破禄（原局带病）：{lbl}之禄{lz}被原局冲破穿刑')
            if lbl.startswith('寿元星'):
                mechanisms.add('寿元星被坏')

    # 1b) 寿元星透干坐绝=带病（「最怕寿星遭刑破，穿害克绝命难长」
    #     gaoji:16148-16151；案例一「癸水食神虚浮无根，坐巳火绝地，寿星衰弱
    #     受克」gaoji:16172-16174）
    for g in shishang:
        if g in gans and _no_root(g) and _sits_jue(g):
            jz = next(zhis[i] for i in range(min(len(gans), len(zhis)))
                      if gans[i] == g and get_changsheng_mangpai(g, zhis[i]) == '绝')
            mechanisms.add('寿元星被坏')
            natal_huai = True
            signals.append(f'寿元星被坏（原局带病）：寿元星({g})虚浮无根，坐{jz}绝地')

    # 1c) 寿元星之根被原局坏=带病（案例二「癸水印星之根辰土被穿坏…印根被拔
    #     寿星倒」gaoji:16206-16216）
    for g in shishang:
        bad_pair = next(((rz, oz) for rz in star_roots.get(g, [])
                         for oz in zhis if _is_huai(rz, oz)), None)
        if bad_pair:
            mechanisms.add('寿元星被坏')
            natal_huai = True
            signals.append(
                f'寿元星被坏（原局带病）：寿元星({g})之根{bad_pair[0]}被{bad_pair[1]}坏')

    # 2) 运岁：引动坏 / 到位
    for src, yg, yz in (('大运', dayun_gan, dayun_zhi), ('流年', liunian_gan, liunian_zhi)):
        if yz:
            owners = _owners_of(yz)
            if owners:
                mechanisms.add('禄到位')
                arrived = True
                signals.append(f'禄到位：{src}支{yz}为{"、".join(owners)}之禄，原神到场')
                # 到位之禄被原局坏（如子运被原局未穿，cj1:2477；正克亦计——
                #   yx2:7486「申金到位被局中官星火正克」、总诀「最忌寿星遭刑克」）
                if any(_is_huai(yz, oz) or _is_zhengke(yz, oz) for oz in zhis):
                    mechanisms.add('破禄')
                    triggered = True
                    if any(o.startswith('寿元星') for o in owners):
                        mechanisms.add('寿元星被坏')
                    signals.append(f'破禄（到位被坏）：{src}支{yz}到位而被原局坏')
            # 运岁支坏原局禄主之禄（如子运刑卯禄，cj2:5278）
            for lbl, lz in lu_owners:
                if lz and lz in zhis and _is_huai(yz, lz):
                    mechanisms.add('破禄')
                    triggered = True
                    if lbl.startswith('寿元星'):
                        mechanisms.add('寿元星被坏')
                    signals.append(f'破禄（{src}引动）：{src}支{yz}坏{lbl}之禄{lz}')
            # 运岁支坏寿元星之根（案例二：流年甲戌冲辰，「辰中癸水印根被冲散」
            #   gaoji:16208-16210）
            for g in shishang:
                rz = next((r for r in star_roots.get(g, []) if _is_huai(r, yz)), None)
                if rz:
                    mechanisms.add('寿元星被坏')
                    triggered = True
                    signals.append(
                        f'寿元星被坏（{src}引动）：{src}支{yz}坏寿元星({g})之根{rz}')
            # 流年坏大运到位之禄（壬午年冲子运，cj2:6042）
            if src == '流年' and dayun_zhi and _is_huai(yz, dayun_zhi):
                dy_owners = _owners_of(dayun_zhi)
                if dy_owners:
                    mechanisms.add('破禄')
                    triggered = True
                    if any(o.startswith('寿元星') for o in dy_owners):
                        mechanisms.add('寿元星被坏')
                    signals.append(
                        f'破禄（流年坏运）：流年支{yz}坏大运支{dayun_zhi}'
                        f'（{"、".join(dy_owners)}之禄）')
            # 原局字到位（支重现）
            if yz in zhis:
                mechanisms.add('原局字到位')
                arrived = True
                weak = any(_is_huai(yz, oz) or _is_zhengke(yz, oz) for oz in zhis)
                if weak:
                    triggered = True
                signals.append(f'原局字到位：{src}支{yz}重现原局' + ('，其位原局已受坏' if weak else ''))
        if yg:
            # 原局字到位（干重现，或透原局支藏干——「丁虚透为戌到了」cj2:4160）
            if yg in gans:
                mechanisms.add('原局字到位')
                arrived = True
                signals.append(f'原局字到位：{src}干{yg}重现原局')
            else:
                hit = next((nz for nz in zhis
                            if any(cg == yg for cg, _ in get_canggan_mangpai(nz))), None)
                if hit:
                    mechanisms.add('原局字到位')
                    arrived = True
                    signals.append(f'原局字到位：{src}干{yg}透原局{hit}藏干')

    risk = triggered or (natal_huai and arrived)
    mech_list = [m for m in ('破禄', '寿元星被坏', '禄到位', '原局字到位') if m in mechanisms]
    if risk:
        desc = '寿元机制推演成立（带病逢引动）：' + '、'.join(mech_list)
    elif mech_list:
        desc = '见寿元相关信号但未成「带病逢引动」：' + '、'.join(mech_list)
    else:
        desc = '无寿元机制信号'
    return {'signals': signals, 'mechanisms': mech_list, 'risk': risk, 'desc': desc}


__all__ = [
    'judge_lu_yuanshen_priority',
    'infer_comprehensive_yingqi',
    'detect_shouyuan_jixie',
]
