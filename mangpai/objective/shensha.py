"""
shensha — 盲派扩展神煞

理论来源：《三命通会》《神峰通考》；盲派常用神煞
流派共识：盲派在传统神煞基础上增加羊刃、劫煞、灾煞、孤辰寡宿、桃花、驿马
已知争议：羊刃只取阳干为盲派严格做法，部分流派配阴刃；灾祸三煞书=空亡/亡神/
  劫煞（gaoji:7907-7908），灾煞三书无载（随劫煞双查保留）；戊刃书内两口径
  （理象学:2086「午、未」vs :4977/zhongji:1520「未或巳」，本模块取前者）。
神煞三层收口（高级篇灾祸章+中级篇核心5）：
  盲派核心5（禄神/羊刃/墓库/驿马/空亡）= 盲派默认取用；羊刃/驿马/马星在本模块，
    禄神=constants.LU、墓库=muku.py、空亡=detect_relations(kong_wang=) 消费侧。
  凶性三煞（空亡/亡神/劫煞/灾煞）= 应事路由灾祸模块；亡神/劫煞/灾煞在本模块。
  传统6（天乙/文昌/华盖/桃花/孤辰/寡宿）= 降级 traditional_shensha，本模块保留计算。
  本函数所算各项均带 'layer' 字段（见 SHENSHA_LAYER），供消费侧按层取用/裁剪。
置信度：中
F13（2026-08-17）：
  - 起算主支默认 year→day（gaoji:7912「先以日支（为主）查空亡、亡神、劫煞。
    年支亦需同查」）；亡神/劫煞/灾煞/桃花/驿马一律年日双查，year_ref/day_ref
    子键恒在（年日同支时省略），不再随 reference 翻转丢次柱值（旧配置断路）。
  - 劫煞/灾煞补双查（gaoji:7789「以年支或日支查，见地支即为劫煞」）。
  - 桃花重建：书桃花=「禄合财官杀伤食为桃花」（zhongji:1517/2792/4349；
    gaoji:13259-13310 禄绊桃花口诀+案例八/九）——非地支煞而是禄合十神之象，
    见 桃花['lu_ban']（detect_lu_ban_taohua_zhi 供给）；咸池五书无「咸池」
    明文，保留于传统（降级）层、日支起算。
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    BAN_HE, CANG_GAN_MANGPAI, DI_ZHI, GAN_WX, LIU_HE, LU, WX_KE, WX_SHENG,
)

_YANG_GANS = {'甲', '丙', '戊', '庚', '壬'}

_YANG_REN: Dict[str, str] = {
    '甲': '卯', '丙': '午', '戊': '午',
    '庚': '酉', '壬': '子',
}

# 段氏全刃位表（刃位检测单一事实源）。《段氏理象学》：「土之禄刃比较特殊，
# 与火接近，戊禄在巳，已禄在午，戊刃在午、未」——戊取双刃（午、未），其余
# 阳干各一刃。_YANG_REN 为主刃位单值表（旧输出契约保留）；刃位检测
# （dayun 到刃运 / yunfan 刃被冲 / 本模块羊刃 in_pillars）一律用全刃表，
# 避免「dayun 取午未双刃、shensha 仅午」的口径冲突（M2 统一）。
_YANG_REN_FULL: Dict[str, List[str]] = {
    '甲': ['卯'], '丙': ['午'], '戊': ['午', '未'],
    '庚': ['酉'], '壬': ['子'],
}

_JIE_SHA: Dict[str, str] = {
    '申': '巳', '子': '巳', '辰': '巳',
    '寅': '亥', '午': '亥', '戌': '亥',
    '巳': '寅', '酉': '寅', '丑': '寅',
    '亥': '申', '卯': '申', '未': '申',
}

_ZAI_SHA: Dict[str, str] = {
    '申': '午', '子': '午', '辰': '午',
    '寅': '子', '午': '子', '戌': '子',
    '巳': '卯', '酉': '卯', '丑': '卯',
    '亥': '酉', '卯': '酉', '未': '酉',
}

_GU_CHEN: Dict[str, str] = {
    '寅': '巳', '卯': '巳', '辰': '巳',
    '巳': '申', '午': '申', '未': '申',
    '申': '亥', '酉': '亥', '戌': '亥',
    '亥': '寅', '子': '寅', '丑': '寅',
}

_GUA_SU: Dict[str, str] = {
    '寅': '丑', '卯': '丑', '辰': '丑',
    '巳': '辰', '午': '辰', '未': '辰',
    '申': '未', '酉': '未', '戌': '未',
    '亥': '戌', '子': '戌', '丑': '戌',
}

# ── 桃花（咸池）──
# 以三合局第一位为基准，见沐浴位为桃花。⚠️批8 勘误：咸池整套段氏五书无
# 「咸池」明文（书桃花=禄合财官杀伤食，见 detect_lu_ban_taohua_zhi），
# 本表属传统（降级）层；起算以日支为主（gaoji:7912），兼看年支。
# 申子辰见酉、寅午戌见卯、亥卯未见子、巳酉丑见午
_TAO_HUA: Dict[str, str] = {
    '申': '酉', '子': '酉', '辰': '酉',
    '寅': '卯', '午': '卯', '戌': '卯',
    '亥': '子', '卯': '子', '未': '子',
    '巳': '午', '酉': '午', '丑': '午',
}

# ── 驿马 ── 段氏「三支皆马」：三合局之对冲三支皆为马。
# 申子辰马在寅午戌、寅午戌马在申子辰、巳酉丑马在亥卯未、亥卯未马在巳酉丑。
# （传统仅取长生位之冲单点；盲派段氏取对冲三支，可多马。每支映射其所属局之
#   对冲三支，故同局三支映射相同；列表首位=长生之冲，即传统单点驿马。）
_YI_MA: Dict[str, List[str]] = {
    '申': ['寅', '午', '戌'], '子': ['寅', '午', '戌'], '辰': ['寅', '午', '戌'],
    '寅': ['申', '子', '辰'], '午': ['申', '子', '辰'], '戌': ['申', '子', '辰'],
    '亥': ['巳', '酉', '丑'], '卯': ['巳', '酉', '丑'], '未': ['巳', '酉', '丑'],
    '巳': ['亥', '卯', '未'], '酉': ['亥', '卯', '未'], '丑': ['亥', '卯', '未'],
}

# ── 天乙贵人 ──
# 甲戊庚牛羊(丑未)、乙己鼠猴乡(子申)、丙丁猪鸡位(亥酉)、
# 壬癸兔蛇藏(卯巳)、六辛逢虎马(寅午)。按日干起，每干两位贵人。
_TIAN_YI: Dict[str, List[str]] = {
    '甲': ['丑', '未'], '戊': ['丑', '未'], '庚': ['丑', '未'],
    '乙': ['子', '申'], '己': ['子', '申'],
    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
    '壬': ['卯', '巳'], '癸': ['卯', '巳'],
    '辛': ['寅', '午'],
}

# ── 文昌 ──
# 甲巳乙午丙戊申、丁己酉庚亥辛子、壬寅癸卯。按日干起，每干一位。
_WEN_CHANG: Dict[str, str] = {
    '甲': '巳', '乙': '午',
    '丙': '申', '戊': '申',
    '丁': '酉', '己': '酉',
    '庚': '亥', '辛': '子',
    '壬': '寅', '癸': '卯',
}

# ── 华盖 ──
# 寅午戌见戌、申子辰见辰、巳酉丑见丑、亥卯未见未。
# 三合局墓库位即为华盖。按年柱或日柱起（日柱优先）。
_HUA_GAI: Dict[str, str] = {
    '寅': '戌', '午': '戌', '戌': '戌',
    '申': '辰', '子': '辰', '辰': '辰',
    '巳': '丑', '酉': '丑', '丑': '丑',
    '亥': '未', '卯': '未', '未': '未',
}

# ── 亡神（高级篇灾祸章补齐）──
# 亡神与劫煞为对偶凶煞：劫煞在长生后一辰，亡神在长生前一辰（帝旺对侧）。
# 申子辰→亥、寅午戌→巳、巳酉丑→申、亥卯未→寅（与驿马不同位，驿马为长生之冲）。
_WANG_SHEN: Dict[str, str] = {
    '申': '亥', '子': '亥', '辰': '亥',
    '寅': '巳', '午': '巳', '戌': '巳',
    '巳': '申', '酉': '申', '丑': '申',
    '亥': '寅', '卯': '寅', '未': '寅',
}

# ── 盲派多马星 ──
# 盲派驿马不止年/日支起，凡四柱地支各以其三合局之对冲三支为马，可多颗（多马星）。
# 查表与 _YI_MA 同（段氏三支皆马），区别在起算口径：四柱皆起、取并集。
_YI_MA_MANGPAI: Dict[str, List[str]] = dict(_YI_MA)

# ── 神煞三层收口（高级篇灾祸章 + 中级篇核心5 口径）──
#   盲派核心5：禄神/羊刃/墓库/驿马/空亡（盲派默认取用，必算）；
#   凶性三煞：空亡/亡神/劫煞（应事路由灾祸模块；空亡兼核心5，必算但凶应入灾祸）；
#   传统6（降级）：天乙/文昌/华盖/桃花/孤辰/寡宿（书房派，降级 traditional_shensha）。
#   禄神=constants.LU、墓库=muku.py、空亡=detect_relations(kong_wang=) 消费侧，
#   此三者不在本函数结果中，仅于此表标注层级；本函数所算各项均加 'layer' 字段。
SHENSHA_LAYER: Dict[str, str] = {
    # 盲派核心5
    '禄神': '盲派核心', '羊刃': '盲派核心', '墓库': '盲派核心',
    '驿马': '盲派核心', '马星': '盲派核心', '空亡': '盲派核心',
    # 凶性三煞 → 灾祸模块
    '亡神': '灾祸', '劫煞': '灾祸', '灾煞': '灾祸',
    # 传统6 → 降级 traditional_shensha
    '天乙贵人': '传统(降级)', '文昌': '传统(降级)', '华盖': '传统(降级)',
    '桃花': '传统(降级)', '孤辰': '传统(降级)', '寡宿': '传统(降级)',
}

_PILLAR_KEYS = ['year', 'month', 'day', 'hour']


def _find_in_pillars(target_zhi: str, zhis: List[str]) -> List[str]:
    return [_PILLAR_KEYS[i] for i, z in enumerate(zhis) if z == target_zhi]


def _find_any_in_pillars(target_zhis: List[str], zhis: List[str]) -> List[str]:
    """返回任一目标地支出现的柱位列表（按年月日时顺序）。"""
    target_set = set(target_zhis)
    return [_PILLAR_KEYS[i] for i, z in enumerate(zhis) if z in target_set]


def _shishen_cat(day_gan: str, gan: str) -> str:
    """十神归类（财/官杀/食伤/印/比劫）。"""
    day_wx = GAN_WX.get(day_gan, '')
    gan_wx = GAN_WX.get(gan, '')
    if not day_wx or not gan_wx:
        return ''
    if gan_wx == day_wx:
        return '比劫'
    if WX_SHENG.get(day_wx) == gan_wx:
        return '食伤'
    if WX_SHENG.get(gan_wx) == day_wx:
        return '印'
    if WX_KE.get(day_wx) == gan_wx:
        return '财'
    if WX_KE.get(gan_wx) == day_wx:
        return '官杀'
    return ''


# 书桃花（禄绊桃花）：合到伤官、官杀、财为桃花；合印/比劫不为桃花
_LU_BAN_CATS = {'财', '官杀', '食伤'}


def detect_lu_ban_taohua_zhi(day_gan: str, zhis: List[str]) -> List[Dict]:
    """禄绊桃花（书桃花口径）检测。

    zhongji:1517「合到伤官、官杀、财为禄绊桃花，禄逢三合也是桃花；合到
    夫妻宫不为桃花」、:4349「禄合印不是，是禄印相随」；gaoji:13259-13310
    口诀「日主之禄与他合，便是情缘起动关」+案例八（歌女，辰酉合禄、辰藏
    癸=食神）/案例九（卯戌合禄、戌藏财杀）。
    规则：日干之禄与他支六合/半合，且所合之支藏干十神属财/官/杀/伤/食
    → 桃花；所合之支为日支（夫妻宫）不论桃花。
    """
    hits: List[Dict] = []
    lu = LU.get(day_gan, '')
    if not lu or lu not in zhis:
        return hits
    he_pairs = {frozenset(p) for p in LIU_HE}
    he_pairs |= {frozenset(k) for k in BAN_HE}
    for i, z in enumerate(zhis):
        if not z or i == 2:  # 合到日支（夫妻宫）不为桃花
            continue
        if frozenset((lu, z)) not in he_pairs:
            continue
        cats = sorted({c for c in (_shishen_cat(day_gan, g)
                                   for g, _q in CANG_GAN_MANGPAI.get(z, []))
                       if c in _LU_BAN_CATS})
        if cats:
            hits.append({'lu': lu, 'partner': z,
                         'pillar': _PILLAR_KEYS[i], 'cats': cats})
    return hits


def compute_shensha_ext(day_gan: str, zhis: List[str], reference: str = 'day') -> Dict:
    """计算盲派扩展神煞。

    Args:
        day_gan: 日干
        zhis: 四柱地支列表 [year_zhi, month_zhi, day_zhi, hour_zhi]
        reference: 神煞参考柱，'day' 用日支（盲派做法），
            'year' 用年支（传统做法）。默认 'day'
            （gaoji:7912「先以日支（为主）查空亡、亡神、劫煞。年支亦需同查」）。

    Returns:
        含羊刃/天乙贵人/文昌/劫煞/灾煞/亡神/孤辰/寡宿/桃花/驿马/华盖/马星
        的字典；各项均带 'layer' 字段（盲派核心/灾祸/传统(降级)）。
        亡神/劫煞/灾煞/桃花/驿马恒年日双查：主键=reference 所定柱，
        次柱值在 'year_ref'/'day_ref' 子键（年日异支且查出异值时），
        键名恒定、不随 reference 翻转（F13 配置断路修复）。
    """
    year_zhi = zhis[0] if zhis else ''
    day_zhi = zhis[2] if len(zhis) >= 3 else ''
    primary_is_day = (reference == 'day')

    result: Dict = {}

    def _dual_ref(name: str, table: Dict, multi: bool = False) -> None:
        """年日双查装配（gaoji:7912 日支为主、年支同查；gaoji:7789 劫煞
        「以年支或日支查」）。multi=True 时表值为支列表（驿马三支皆马）。"""
        def _one(ref_z: str, label: str) -> Optional[Dict]:
            v = table.get(ref_z) if ref_z else None
            if not v:
                return None
            if multi:
                return {'zhi': v[0], 'zhis': v,
                        'in_pillars': _find_any_in_pillars(v, zhis),
                        'reference': label}
            return {'zhi': v, 'in_pillars': _find_in_pillars(v, zhis),
                    'reference': label}

        d = _one(day_zhi, 'day_zhi')
        y = _one(year_zhi, 'year_zhi')
        primary = (d if primary_is_day else y) or d or y
        if primary is None:
            return
        result[name] = dict(primary)
        if d and y and year_zhi != day_zhi:
            same = set(d.get('zhis', [d['zhi']])) == set(y.get('zhis', [y['zhi']]))
            if not same:
                # R2 死数据备案：year_ref/day_ref 子键多数无生产读者（驿马消费
                # 全走主键 in_pillars；亡神/劫煞/桃花读主键/day_ref；灾煞
                # year_ref 为唯一活读者 zhiye.py:955）。保留供 verify/payload。
                result[name]['year_ref'] = y
                result[name]['day_ref'] = d

    if day_gan in _YANG_REN:
        # 段氏全刃位检测：戊取午、未双刃，任一落柱皆计羊刃在局（M2 口径统一）；
        # 'zhi' 保留主刃位单值（旧输出契约），'zhi_all' 列全刃位。
        yr_zhis = _YANG_REN_FULL.get(day_gan, [_YANG_REN[day_gan]])
        in_pillars: List[str] = []
        for yz in yr_zhis:
            in_pillars.extend(_find_in_pillars(yz, zhis))
        result['羊刃'] = {
            'zhi': _YANG_REN[day_gan],
            'zhi_all': yr_zhis,
            'in_pillars': in_pillars,
        }
    else:
        result['羊刃'] = {
            'zhi': '',
            'in_pillars': [],
            'note': '阴干无羊刃（盲派严格做法）',
        }

    # ── 天乙贵人 ── 按日干起，每干两位贵人
    ty_zhis = _TIAN_YI.get(day_gan, [])
    if ty_zhis:
        result['天乙贵人'] = {
            'zhis': ty_zhis,
            'in_pillars': _find_any_in_pillars(ty_zhis, zhis),
        }
    else:
        result['天乙贵人'] = {
            'zhis': [],
            'in_pillars': [],
        }

    # ── 文昌 ── 按日干起，每干一位
    wc_zhi = _WEN_CHANG.get(day_gan, '')
    if wc_zhi:
        result['文昌'] = {
            'zhi': wc_zhi,
            'in_pillars': _find_in_pillars(wc_zhi, zhis),
        }
    else:
        result['文昌'] = {
            'zhi': '',
            'in_pillars': [],
        }

    # ── 灾祸三煞（年日双查）── gaoji:7907-7908 空亡/亡神/劫煞；
    # 灾煞三书无「灾煞」明文（灾祸章 14818-16567 零命中），随劫煞双查保留。
    _dual_ref('劫煞', _JIE_SHA)
    _dual_ref('灾煞', _ZAI_SHA)
    _dual_ref('亡神', _WANG_SHEN)

    # ── 孤辰/寡宿 ── 单参考柱（跟 reference 走；书仅歌诀提及，无双查明文）
    ref_zhi = day_zhi if primary_is_day else year_zhi
    if ref_zhi:
        gc_zhi = _GU_CHEN.get(ref_zhi, '')
        gs_zhi = _GUA_SU.get(ref_zhi, '')
        result['孤辰'] = {
            'zhi': gc_zhi,
            'in_pillars': _find_in_pillars(gc_zhi, zhis),
        }
        result['寡宿'] = {
            'zhi': gs_zhi,
            'in_pillars': _find_in_pillars(gs_zhi, zhis),
        }

    # ── 桃花 ── 两层口径：
    #   书桃花=禄绊桃花（'lu_ban' 子键）：禄合财官杀伤食为桃花
    #   （zhongji:1517/4349；gaoji:13259-13310 口诀+案例八/九），detect 见下；
    #   咸池=传统层地支煞（五书无「咸池」明文，降级），日支起算兼看年支。
    _dual_ref('桃花', _TAO_HUA)
    lu_ban_hits = detect_lu_ban_taohua_zhi(day_gan, zhis)
    if lu_ban_hits or '桃花' in result:
        result.setdefault('桃花', {})['lu_ban'] = {
            'is_lu_ban': bool(lu_ban_hits),
            'hits': lu_ban_hits,
        }

    # ── 驿马 ── 段氏三支皆马（zhongji:1563-1565/理象学:5042-5045 逐字）：
    #   年日双查（理象学:5047「以年支和日支为主」）；
    #   'zhi'=对冲三支首位（长生之冲，传统单点驿马，向后兼容）；
    #   'zhis'=对冲三支全列；'in_pillars'=四柱中落三支任一之柱位。
    _dual_ref('驿马', _YI_MA, multi=True)

    # ── 盲派多马星（盲派核心）── 四柱地支各以其三合局对冲三支为马，取并集，可多颗
    #   ⚠️ 'count'=并集马支数（恒≥3，批8 实锤死判据供给侧），消费在局马数
    #   请用 'in_pillars'（zaihuo 车祸 F13 已切换）。
    ma_zhis: List[str] = []
    ma_seen: set = set()
    for z in zhis:
        if not z:
            continue
        for m in _YI_MA_MANGPAI.get(z, []):
            if m not in ma_seen:
                ma_seen.add(m)
                ma_zhis.append(m)
    if ma_zhis:
        ma_zhis_set = set(ma_zhis)
        result['马星'] = {
            'zhis': ma_zhis,
            'in_pillars': [_PILLAR_KEYS[i] for i, z in enumerate(zhis)
                           if z in ma_zhis_set],
            'count': len(ma_zhis),
            'note': '盲派多马星（四柱各起，三支皆马，取并集）',
        }

    # ── 华盖 ── 按日柱起（日柱优先），兼看年柱
    # 寅午戌见戌、申子辰见辰、巳酉丑见丑、亥卯未见未
    if day_zhi:
        hg_day = _HUA_GAI.get(day_zhi, '')
        if hg_day:
            result['华盖'] = {
                'zhi': hg_day,
                'in_pillars': _find_in_pillars(hg_day, zhis),
                'reference': 'day_zhi',
            }
            if year_zhi and year_zhi != day_zhi:
                hg_year = _HUA_GAI.get(year_zhi, '')
                if hg_year and hg_year != hg_day:
                    # R2 死数据备案：华盖 year_ref 无生产读者（仅 verify+payload）。
                    result['华盖']['year_ref'] = {
                        'zhi': hg_year,
                        'in_pillars': _find_in_pillars(hg_year, zhis),
                        'reference': 'year_zhi',
                    }

    # ── 神煞三层收口：为本函数所算各项打 layer 标签 ──
    for name, entry in result.items():
        if isinstance(entry, dict) and 'layer' not in entry:
            entry['layer'] = SHENSHA_LAYER.get(name, '')

    return result


def resolve_shensha(
    day_gan: str, zhis: List[str],
    shensha_result: Optional[Dict] = None,
    reference: str = 'day',
) -> Dict:
    """神煞结果解析：优先用 engine 透传的 shensha_result，未传入则就地重算。

    下游主观模块（caiming/guanming/hunyin/zhiye/gongmen_wuzhi/zaihuo）经此函数
    取神煞，可避免与 engine 的 shensha_reference 口径不一致（engine 已按设定
    reference 算过一次，下游不再以默认 'day' 重算覆盖）。
    """
    if shensha_result is not None:
        return shensha_result
    return compute_shensha_ext(day_gan, zhis, reference=reference)
