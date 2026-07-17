"""
shensha — 盲派扩展神煞

理论来源：《三命通会》《神峰通考》；盲派常用神煞
流派共识：盲派在传统神煞基础上增加羊刃、劫煞、灾煞、孤辰寡宿、桃花、驿马
已知争议：羊刃只取阳干为盲派严格做法，部分流派配阴刃；桃花盲派通常以日支起
神煞三层收口（高级篇灾祸章+中级篇核心5）：
  盲派核心5（禄神/羊刃/墓库/驿马/空亡）= 盲派默认取用；羊刃/驿马/马星在本模块，
    禄神=constants.LU、墓库=muku.py、空亡=detect_relations(kong_wang=) 消费侧。
  凶性三煞（空亡/亡神/劫煞/灾煞）= 应事路由灾祸模块；亡神/劫煞/灾煞在本模块。
  传统6（天乙/文昌/华盖/桃花/孤辰/寡宿）= 降级 traditional_shensha，本模块保留计算。
  本函数所算各项均带 'layer' 字段（见 SHENSHA_LAYER），供消费侧按层取用/裁剪。
置信度：中
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import DI_ZHI

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
# 以三合局第一位为基准，见沐浴位为桃花。盲派通常以日支起桃花。
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


def compute_shensha_ext(day_gan: str, zhis: List[str], reference: str = 'year') -> Dict:
    """计算盲派扩展神煞。

    Args:
        day_gan: 日干
        zhis: 四柱地支列表 [year_zhi, month_zhi, day_zhi, hour_zhi]
        reference: 神煞参考柱，'year' 用年支（传统做法），
            'day' 用日支（盲派做法）。默认 'year'。

    Returns:
        含羊刃/天乙贵人/文昌/劫煞/灾煞/亡神/孤辰/寡宿/桃花/驿马/华盖/马星
        的字典；各项均带 'layer' 字段（盲派核心/灾祸/传统(降级)）。
    """
    year_zhi = zhis[0] if zhis else ''
    day_zhi = zhis[2] if len(zhis) >= 3 else ''

    if reference == 'day':
        ref_zhi = day_zhi
        ref_label = 'day_zhi'
        other_zhi = year_zhi
        other_key = 'year_ref'
        other_label = 'year_zhi'
    else:
        ref_zhi = year_zhi
        ref_label = 'year_zhi'
        other_zhi = day_zhi
        other_key = 'day_ref'
        other_label = 'day_zhi'

    result: Dict = {}

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

    if ref_zhi:
        js_zhi = _JIE_SHA.get(ref_zhi, '')
        result['劫煞'] = {
            'zhi': js_zhi,
            'in_pillars': _find_in_pillars(js_zhi, zhis),
        }

        zs_zhi = _ZAI_SHA.get(ref_zhi, '')
        result['灾煞'] = {
            'zhi': zs_zhi,
            'in_pillars': _find_in_pillars(zs_zhi, zhis),
        }

        # ── 亡神（凶性三煞，高级篇灾祸章）── 与劫煞对偶，跟 reference 走兼看另一柱
        ws_zhi = _WANG_SHEN.get(ref_zhi, '')
        if ws_zhi:
            result['亡神'] = {
                'zhi': ws_zhi,
                'in_pillars': _find_in_pillars(ws_zhi, zhis),
                'reference': ref_label,
            }
            if other_zhi and other_zhi != ref_zhi:
                ws_zhi_o = _WANG_SHEN.get(other_zhi, '')
                if ws_zhi_o and ws_zhi_o != ws_zhi:
                    result['亡神'][other_key] = {
                        'zhi': ws_zhi_o,
                        'in_pillars': _find_in_pillars(ws_zhi_o, zhis),
                        'reference': other_label,
                    }

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

    # ── 桃花（咸池）── 跟 reference 走，兼看另一柱
    # 段建业《段氏理象学》以日支为主；卜文《命理瑰宝》提及年支亦可用
    if ref_zhi:
        th_zhi = _TAO_HUA.get(ref_zhi, '')
        if th_zhi:
            result['桃花'] = {
                'zhi': th_zhi,
                'in_pillars': _find_in_pillars(th_zhi, zhis),
                'reference': ref_label,
            }
            if other_zhi and other_zhi != ref_zhi:
                th_zhi_o = _TAO_HUA.get(other_zhi, '')
                if th_zhi_o and th_zhi_o != th_zhi:
                    result['桃花'][other_key] = {
                        'zhi': th_zhi_o,
                        'in_pillars': _find_in_pillars(th_zhi_o, zhis),
                        'reference': other_label,
                    }

    # ── 驿马 ── 段氏三支皆马：跟 reference 走，兼看另一柱
    #   'zhi'=对冲三支首位（长生之冲，传统单点驿马，向后兼容）；
    #   'zhis'=对冲三支全列；'in_pillars'=四柱中落三支任一之柱位。
    if ref_zhi:
        ym_zhis = _YI_MA.get(ref_zhi, [])
        if ym_zhis:
            result['驿马'] = {
                'zhi': ym_zhis[0],
                'zhis': ym_zhis,
                'in_pillars': _find_any_in_pillars(ym_zhis, zhis),
                'reference': ref_label,
            }
            if other_zhi and other_zhi != ref_zhi:
                ym_zhis_o = _YI_MA.get(other_zhi, [])
                if ym_zhis_o and set(ym_zhis_o) != set(ym_zhis):
                    result['驿马'][other_key] = {
                        'zhi': ym_zhis_o[0],
                        'zhis': ym_zhis_o,
                        'in_pillars': _find_any_in_pillars(ym_zhis_o, zhis),
                        'reference': other_label,
                    }

    # ── 盲派多马星（盲派核心）── 四柱地支各以其三合局对冲三支为马，取并集，可多颗
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
    reference: str = 'year',
) -> Dict:
    """神煞结果解析：优先用 engine 透传的 shensha_result，未传入则就地重算。

    下游主观模块（caiming/guanming/hunyin/zhiye/gongmen_wuzhi/zaihuo）经此函数
    取神煞，可避免与 engine 的 shensha_reference 口径不一致（engine 已按设定
    reference 算过一次，下游不再以默认 'year' 重算覆盖）。
    """
    if shensha_result is not None:
        return shensha_result
    return compute_shensha_ext(day_gan, zhis, reference=reference)
