"""
gongshen - 盲派宫身（宫位六亲）分析

理论来源：段建业《段氏理象学》宫位篇
核心思想：
  宫位是六亲的"位置"与"时限"载体——年柱祖辈、月柱父母、日柱配偶（日支为
  夫妻宫）、时柱子女；宫位亦主身体部位与人生阶段。星（十神）是六亲之"人"，
  星与宫配合看六亲吉凶：
    星宫同位（六亲星坐本命宫位）-> 该六亲正位得地，吉；
    星宫异位（六亲星游走他宫）-> 该六亲不在其位，缘薄或不稳。
  夫妻宫（日支）被冲/合/穿/刑 -> 婚姻动向（动荡、合绊、受损、刑伤）。
  柱间冲合穿刑 -> 对应两宫所主六亲与身体部位受累。

  与 gongfei（功神/废神）的区别：功神废神论"做功效率"（哪些干支参与做功），
  宫身论"六亲位置"（星与宫的配合）；二者音近而实异，故分置两模块。

已知争议：
  - 六亲星表各师有别（如父星有偏财/正财两说，本模块取段氏主流：偏财为父）。
  - 星宫异位未必皆凶（星游他宫亦可主该六亲远游、外发展），本模块作基础吉凶
    判断，标"不稳"而非直断"凶"。
  - 寅巳等既穿又刑，沿用 zuogong"刑去重穿"约定（以刑论，穿不重复计）。
置信度：中（宫位六亲为盲派共识框架，细节取象有解释空间）
"""
from typing import Dict, List, Optional

from mangpai.objective.constants import (
    PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
    LIU_CHONG, LIU_HE, LIU_HAI, XING_PAIRS,
)
from mangpai.objective.xiangfa import (
    get_gan_xiang, get_zhi_xiang, get_gongwei_xiang,
)


# ── 宫位名（柱位 -> 六亲宫）──
_PALACE_NAME: Dict[str, str] = {
    'year': '祖辈宫',
    'month': '父母宫',
    'day': '配偶宫',
    'hour': '子女宫',
}

# ── 柱位身体部位（段氏：年主头颈、月主胸背、日主腹腰、时主腿足）──
_PILLAR_BODY: Dict[str, str] = {
    'year': '头、颈',
    'month': '胸、背、上肢',
    'day': '腹、腰',
    'hour': '腿、足、下阴',
}

# ── 六亲星 -> (本命宫位, 六亲名) ──
# 段氏六亲星：正印母、偏财父；男命正财妻、官杀子女；女命正官夫、食伤子女；
# 比劫兄弟姊妹（居父母兄弟宫）。配偶星本命宫位为日柱（夫妻宫=日支）。
_LIUQING_MALE: Dict[str, tuple] = {
    '正印': ('month', '母亲'),
    '偏财': ('month', '父亲'),
    '正财': ('day', '妻子'),
    '正官': ('hour', '女儿'),
    '七杀': ('hour', '儿子'),
    '比肩': ('month', '兄弟'),
    '劫财': ('month', '姐妹'),
}
_LIUQING_FEMALE: Dict[str, tuple] = {
    '正印': ('month', '母亲'),
    '偏财': ('month', '父亲'),
    '正官': ('day', '丈夫'),
    '七杀': ('day', '偏夫/情人'),
    '食神': ('hour', '儿子'),
    '伤官': ('hour', '女儿'),
    '比肩': ('month', '姐妹'),
    '劫财': ('month', '兄弟'),
}

# ── 两宫互动释义（柱位对 -> 两宫名），键为排序后的柱位对 ──
_PALACE_PAIR: Dict[tuple, tuple] = {
    ('month', 'year'): ('祖辈宫', '父母宫'),
    ('day', 'year'): ('祖辈宫', '配偶宫'),
    ('hour', 'year'): ('祖辈宫', '子女宫'),
    ('day', 'month'): ('父母宫', '配偶宫'),
    ('hour', 'month'): ('父母宫', '子女宫'),
    ('day', 'hour'): ('配偶宫', '子女宫'),
}

# ── 关系类型 -> (动词, 取象) ──
_RELATION_IMPACT: Dict[str, tuple] = {
    '冲': ('相冲', '动荡、分离、变动之象'),
    '合': ('相合', '牵绊、合化、外缘介入之象'),
    '穿': ('相穿', '暗损、不和、刑伤之象'),
    '刑': ('相刑', '刑伤、口舌、官非之象'),
}

# ── 夫妻宫（日支）被 relations -> (标签, 婚姻动向, 吉凶) ──
_SPOUSE_IMPACT: Dict[str, tuple] = {
    '冲': ('配偶宫被冲', '婚姻动荡、易生分离变动', '凶'),
    '合': ('配偶宫被合', '配偶被合绊或外缘介入', '动'),
    '穿': ('配偶宫被穿', '婚姻受损、夫妻不和', '凶'),
    '刑': ('配偶宫被刑', '婚姻有刑伤、口舌是非', '凶'),
}


def _check_pair(a: str, b: str, pairs) -> bool:
    """双向判定 (a,b) 是否属于 pairs（与 zuogong 同名 helper 一致）。"""
    return (a, b) in pairs or (b, a) in pairs


def _detect_zhi_relations(zhis: List[str]) -> List[Dict]:
    """检测四支两两之间的 冲/合/穿/刑 关系。

    返回 [{'type','i','j','z1','z2'}]，i<j 为柱索引（0年1月2日3时）。
    寅巳等既穿又刑者，沿用"刑去重穿"约定（以刑论，穿不重复计）。
    """
    relations: List[Dict] = []
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            types: List[str] = []
            if _check_pair(z1, z2, LIU_CHONG):
                types.append('冲')
            if _check_pair(z1, z2, LIU_HE):
                types.append('合')
            if _check_pair(z1, z2, LIU_HAI):
                types.append('穿')
            if _check_pair(z1, z2, XING_PAIRS):
                types.append('刑')
            # 刑去重穿（与 zuogong 一致：寅巳等既穿又刑，以刑论）
            if '刑' in types and '穿' in types:
                types.remove('穿')
            for t in types:
                relations.append({'type': t, 'i': i, 'j': j, 'z1': z1, 'z2': z2})
    return relations


def analyze_gongshen(
    day_gan: str, day_zhi: str,
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
    shishen: Optional[Dict[str, str]] = None,
    gender: str = '男',
) -> Dict:
    """段氏宫身（宫位六亲）分析。

    四层分析：
      1. 宫位六亲/身体/人生阶段（基于 GONG_WEI_XIANG + 干支身体象 + 柱位身段）
      2. 星宫关系（六亲星与所在宫位同位/异位 -> 六亲吉凶）
      3. 日支夫妻宫专断（夫妻宫被冲合穿刑 -> 婚姻动向）
      4. 宫位互动（柱间冲合穿刑 -> 对应六亲/身体部位受损）

    支持两种调用签名（与 analyze_zuogong 等一致）：
      1. 旧签名：analyze_gongshen(day_gan, day_zhi, year_gan, year_zhi,
                                  month_gan, month_zhi, hour_gan, hour_zhi,
                                  shishen=None, gender='男')
      2. Pillars 对象：analyze_gongshen(pillars, shishen=None, gender='男')

    Args:
        day_gan: 日干（或 Pillars 对象）
        day_zhi: 日支（夫妻宫）
        year_gan/year_zhi/month_gan/month_zhi/hour_gan/hour_zhi: 其余三柱干支
        shishen: 十神映射（如 {'year_gan':'正财', ...}），缺省则星宫层空
        gender: '男' 或 '女'，决定配偶星/子女星表（默认 '男'）

    Returns:
        {'palaces', 'star_palace', 'spouse_palace', 'palace_interactions',
         'summary'}
    """
    # ── Pillars 对象签名支持 ──
    if is_pillars(day_gan):
        p = day_gan
        day_gan, day_zhi = p.day_gan, p.day_zhi
        year_gan, year_zhi = p.year_gan, p.year_zhi
        month_gan, month_zhi = p.month_gan, p.month_zhi
        hour_gan, hour_zhi = p.hour_gan, p.hour_zhi

    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    pillar_keys = PILLAR_KEYS
    shishen = shishen or {}

    # ── 1. 宫位分析（六亲 / 身体 / 人生阶段）──
    palaces: Dict[str, Dict] = {}
    for idx, pk in enumerate(pillar_keys):
        gan, zhi = gans[idx], zhis[idx]
        pillar_cn = PILLAR_NAMES_CN[idx]
        gan_body = get_gan_xiang(gan).get('body', '')
        zhi_body = get_zhi_xiang(zhi).get('body', '')
        palaces[pk] = {
            'pillar': pillar_cn,
            'palace': _PALACE_NAME[pk],
            'gan': gan,
            'zhi': zhi,
            'gongwei': get_gongwei_xiang(f'{pillar_cn}柱'),
            'gan_body': gan_body,
            'zhi_body': zhi_body,
            'pillar_body': _PILLAR_BODY[pk],
        }

    # ── 2. 星宫关系（六亲星与所在宫位同位/异位）──
    star_table = _LIUQING_FEMALE if gender == '女' else _LIUQING_MALE
    star_palace: List[Dict] = []
    for pos, ss in shishen.items():
        if not ss or ss == '日主':
            continue  # 日主为自己，非六亲星
        if ss not in star_table:
            continue
        own_palace, liuqing = star_table[ss]
        actual_pillar = pos.split('_')[0] if '_' in pos else ''
        if actual_pillar not in _PALACE_NAME:
            continue
        same = (actual_pillar == own_palace)
        own_name = _PALACE_NAME[own_palace]
        actual_name = _PALACE_NAME[actual_pillar]
        if same:
            desc = f'{liuqing}星({ss})在{pos}（{actual_name}），星宫同位、正位得地--吉'
        else:
            desc = (f'{liuqing}星({ss})在{pos}（{actual_name}），'
                    f'星宫异位、不在本命{own_name}--该六亲位不稳')
        star_palace.append({
            'star': ss,
            'liuqing': liuqing,
            'position': pos,
            'own_palace': own_name,
            'actual_palace': actual_name,
            'same_position': same,
            'auspicious': '吉' if same else '不稳',
            'desc': desc,
        })

    # ── 3. 柱间关系检测（冲/合/穿/刑）──
    relations = _detect_zhi_relations(zhis)

    # ── 4. 宫位互动（柱间冲合穿刑 -> 两宫所主六亲/身体部位受累）──
    palace_interactions: List[Dict] = []
    for r in relations:
        i, j = r['i'], r['j']
        pair = tuple(sorted((pillar_keys[i], pillar_keys[j])))
        pal_pair = _PALACE_PAIR.get(pair)
        if not pal_pair:
            continue
        verb, impl = _RELATION_IMPACT[r['type']]
        body_i = get_zhi_xiang(r['z1']).get('body', '')
        body_j = get_zhi_xiang(r['z2']).get('body', '')
        body_parts = [b for b in (body_i, body_j) if b]
        body_str = '、'.join(body_parts)
        desc = f'{pal_pair[0]}与{pal_pair[1]}{verb}：{impl}'
        if body_str:
            desc += f'；身体{body_str}受累'
        palace_interactions.append({
            'type': r['type'],
            'from': f'{PILLAR_NAMES_CN[i]}支({r["z1"]})',
            'to': f'{PILLAR_NAMES_CN[j]}支({r["z2"]})',
            'palaces': f'{pal_pair[0]}与{pal_pair[1]}',
            'relation': verb,
            'implication': impl,
            'body_affected': body_str,
            'desc': desc,
        })

    # ── 5. 日支夫妻宫专断（夫妻宫被冲合穿刑 -> 婚姻动向）──
    spouse_signals: List[Dict] = []
    for r in relations:
        if r['i'] != 2 and r['j'] != 2:
            continue  # 须日支（索引2）参与
        other_idx = r['j'] if r['i'] == 2 else r['i']
        other_zhi = r['z2'] if r['i'] == 2 else r['z1']
        impact = _SPOUSE_IMPACT.get(r['type'])
        if not impact:
            continue
        label, trend, level = impact
        spouse_signals.append({
            'type': r['type'],
            'with_pillar': PILLAR_NAMES_CN[other_idx],
            'with_zhi': other_zhi,
            'label': label,
            'trend': trend,
            'level': level,
            'desc': f'日支（夫妻宫）与{PILLAR_NAMES_CN[other_idx]}支({other_zhi}){r["type"]}：{trend}',
        })

    if spouse_signals:
        marriage_trend = '；'.join(s['trend'] for s in spouse_signals)
    else:
        marriage_trend = '夫妻宫安静无冲合穿刑，婚姻平稳'

    # ── summary ──
    parts: List[str] = []
    if star_palace:
        same_cnt = sum(1 for s in star_palace if s['same_position'])
        parts.append(f'星宫同位{same_cnt}/{len(star_palace)}')
    parts.append('夫妻宫安静' if not spouse_signals else f'夫妻宫：{marriage_trend}')
    if palace_interactions:
        parts.append(f'宫位互动{len(palace_interactions)}处')

    return {
        'palaces': palaces,
        'star_palace': star_palace,
        'spouse_palace': {
            'interactions': spouse_signals,
            'marriage_trend': marriage_trend,
            'quiet': len(spouse_signals) == 0,
        },
        'palace_interactions': palace_interactions,
        'summary': '；'.join(parts),
    }


__all__ = ['analyze_gongshen']
