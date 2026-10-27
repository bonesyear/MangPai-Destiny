"""
he_types - 盲派合的类型细分

理论来源：段建业《段氏理象学》合论篇
核心思想：盲派将"合"按性质细分为多种类型，不同类型应事不同。

  地支六合--按性质细分五种：
    合绊：相合双方相互羁绊，失去原有特性
    合克/合制：合中带克（卯戌合克戌土、巳申合克申金、子丑合克子水）
    合伤：合中伤及藏干（辰酉合伤辰中木、寅亥合伤寅中火）
    闭气：六合闭住墓库藏干（子丑闭丑金、辰酉闭辰水、午未闭未木、卯戌闭戌火）
    合去：某一字太弱（周围克泄交加），合即被去（消失）

  天干五合：按生克分合财/合官/合，只合不化（初级:2663）
  三合局/半合：三字齐现成局 / 相邻二字半合（气未全）
  拱局：亥未拱木、寅戌拱火、巳丑拱金、申辰拱水（理象学:2498）
  暗合：寅丑、午亥、卯申（盲派独有，主暗中往来；仅三对，初级:3218 排他）

多重属性并报：六合常兼具多种属性（子丑=合克+闭气、辰酉=合伤+闭气、
  卯戌=合克+闭气），故各属性以独立 if 判定并报，不以 elif 互斥。
  合去为特例：弱方既被合去，克/伤/闭气不论（弱方既去，他效不存）。

已知争议：合去的判定条件各盲师有不同标准，本模块采用"周围克泄"判定法
置信度：中
"""
from typing import Dict, List, Optional, Tuple

from mangpai.objective.constants import (
    ZHI_WX, WX_KE_ME, WX_KE, LIU_HE, TIAN_GAN_HE, GAN_WX,
    SAN_HE, BAN_HE, AN_HE, BI_QI, PILLAR_KEYS,
)
from mangpai.objective.bazi_calc import get_di_zhi_relations
from mangpai.objective.muku import sanhe_tomb_priority

# 六合中带克（合克/合制）：双向各存一份便于查表
_HE_KE: Dict[str, str] = {
    '卯戌': '卯克戌(木克土)', '戌卯': '卯克戌(木克土)',
    '巳申': '巳克申(火克金)', '申巳': '巳克申(火克金)',
    '子丑': '丑克子(土克水)', '丑子': '丑克子(土克水)',
}

# 六合中伤及藏干（合伤）
_HE_SHANG: Dict[str, str] = {
    '辰酉': '酉克辰中乙木', '酉辰': '酉克辰中乙木',
    '寅亥': '亥克寅中丙火', '亥寅': '亥克寅中丙火',
}

_GAN_PILLAR_NAMES = ['年干', '月干', '日干', '时干']
_ZHI_PILLAR_NAMES = ['年支', '月支', '日支', '时支']


def _is_weak(zhi: str, all_zhis: List[str]) -> bool:
    """判断地支是否太弱（周围克泄交加）。

    条件：同五行地支≤1个，且克它的五行地支≥2个
    """
    target_wx = ZHI_WX.get(zhi, '')
    if not target_wx:
        return False
    ke_wx = WX_KE_ME.get(target_wx, '')
    if not ke_wx:
        return False

    same_count = sum(1 for z in all_zhis if ZHI_WX.get(z, '') == target_wx)
    ke_count = sum(1 for z in all_zhis if ZHI_WX.get(z, '') == ke_wx)

    return same_count <= 1 and ke_count >= 2


def _liu_he_attrs(a: str, b: str, all_zhis: List[str]) -> List[Tuple[str, str]]:
    """返回某六合的多重属性列表 (he_type, desc)，独立判定可并报。

    合去为特例：弱方被合去则克/伤/闭气不论（弱方既去，他效不存）。
    其余属性（合克/合伤/闭气）以独立判定并报，故子丑(合克+闭气)、
    辰酉(合伤+闭气)、卯戌(合克+闭气)等多重属性不再被 elif 互斥吞掉；
    均不适用时回落合绊。
    """
    pair = f'{a}{b}'
    pair_rev = f'{b}{a}'

    a_weak = _is_weak(a, all_zhis)
    b_weak = _is_weak(b, all_zhis)
    if a_weak or b_weak:
        weak_side = a if a_weak else b
        return [('合去', f'{a}{b}合，{weak_side}太弱被合去')]

    attrs: List[Tuple[str, str]] = []
    ke_desc = _HE_KE.get(pair) or _HE_KE.get(pair_rev)
    if ke_desc:
        attrs.append(('合克/合制', f'{a}{b}合，{ke_desc}'))
    shang_desc = _HE_SHANG.get(pair) or _HE_SHANG.get(pair_rev)
    if shang_desc:
        attrs.append(('合伤', f'{a}{b}合，{shang_desc}，伤藏干'))
    bi = BI_QI.get(pair) or BI_QI.get(pair_rev)
    if bi:
        attrs.append(('闭气', f'{a}{b}合绊，闭{bi["闭"]}中{bi["闭气"]}气'))
    if not attrs:
        attrs.append(('合绊', f'{a}{b}合绊，双方羁绊'))
    return attrs


def _gan_he_sub_type(day_gan: str, other_gan: str) -> str:
    """天干五合分类：日干克所合之干为合财，所合之干克日干为合官，否则为合。

    五对天干五合皆含克关系（甲己木克土、乙庚金克木、丙辛火克金、
    丁壬水克火、戊癸土克水），故实务中只出合财/合官，"合"为兜底。
    """
    day_wx = GAN_WX.get(day_gan, '')
    other_wx = GAN_WX.get(other_gan, '')
    if day_wx and other_wx:
        if WX_KE.get(day_wx) == other_wx:
            return '合财'
        if WX_KE.get(other_wx) == day_wx:
            return '合官'
    return '合'


def _ban_he_wx(a: str, b: str) -> Optional[str]:
    """半合五行（生旺/旺墓相邻对）；非半合返回 None。"""
    pair = f'{a}{b}'
    if pair in BAN_HE:
        return BAN_HE[pair]
    rev = f'{b}{a}'
    if rev in BAN_HE:
        return BAN_HE[rev]
    return None


def _classify_gan_he(gans: List[str], results: List[Dict]) -> None:
    """天干五合只分合财/合官/合；初级:2663 明言不讲合化。"""
    day_gan = gans[2]
    if not day_gan:
        return
    he_gan = TIAN_GAN_HE.get(day_gan, '')
    if not he_gan:
        return
    zheng_he = sum(1 for g in gans if g and g == he_gan) >= 2

    for i, gan in enumerate(gans):
        if i == 2 or not gan:
            continue
        if TIAN_GAN_HE.get(day_gan) != gan:
            continue
        sub = _gan_he_sub_type(day_gan, gan)
        results.append({
            'he_type': f'天干五合·{sub}',
            'from': f'日干({day_gan})',
            'to': f'{_GAN_PILLAR_NAMES[i]}({gan})',
            'desc': f'{day_gan}{gan}合，{sub}' + ('（争合）' if zheng_he else ''),
        })


def classify_he_types(
    day_zhi: str,
    year_zhi: str, month_zhi: str, hour_zhi: str,
    year_gan: str = '', month_gan: str = '', day_gan: str = '', hour_gan: str = '',
) -> Dict:
    """对四柱中的合进行分类。

    覆盖地支六合、天干五合、三合局/半合、拱局与暗合；天干五合不讲合化。

    六合多重属性并报：子丑(合克+闭气)、辰酉(合伤+闭气)、卯戌(合克+闭气)
    等以独立 if 判定并报，不以 elif 互斥；合去为特例，弱方既去则不论克/伤/闭气。

    Args:
        day_zhi: 日支
        year_zhi: 年支
        month_zhi: 月支
        hour_zhi: 时支
        year_gan: 年干（可选，提供后启用天干五合判定，只合不化）
        month_gan: 月干（可选）
        day_gan: 日干（可选）
        hour_gan: 时干（可选）

    Returns:
        {'he_types': 合类型列表}，每项含 he_type/from/to/desc
    """
    results: List[Dict] = []
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    gans = [year_gan, month_gan, day_gan, hour_gan]
    all_zhis = [z for z in zhis if z]

    # ── 地支六合 ──
    # 多柱同支全部报告：先建"支 -> 出现柱位"索引，再对每对柱位并报全部属性
    pos_of: Dict[str, List[int]] = {}
    for i, z in enumerate(zhis):
        if z:
            pos_of.setdefault(z, []).append(i)
    for a, b in LIU_HE:
        a_pos = pos_of.get(a, [])
        b_pos = pos_of.get(b, [])
        if not a_pos or not b_pos:
            continue
        attrs = _liu_he_attrs(a, b, all_zhis)
        for ia in a_pos:
            for ib in b_pos:
                a_label = f'{_ZHI_PILLAR_NAMES[ia]}({a})'
                b_label = f'{_ZHI_PILLAR_NAMES[ib]}({b})'
                for he_type, desc in attrs:
                    results.append({
                        'he_type': he_type,
                        'from': a_label,
                        'to': b_label,
                        'desc': desc,
                    })

    # ── 天干五合（只合不化）──
    if any(gans):
        _classify_gan_he(gans, results)

    # ── 三合局 / 半合：原始事实同源，多而墓按直接书例优先 ──
    raw = get_di_zhi_relations(zhis)
    zhis_set = set(all_zhis)
    for group, wx in SAN_HE.items():
        if sanhe_tomb_priority(group, zhis, gans):
            continue
        members = list(group)
        present = [m for m in members if m in zhis_set]
        if len(present) == len(members) and (len(members) > 3 or group in raw['三合']):
            positions = [(m, zhis.index(m)) for m in members]
            parts = [f'{_ZHI_PILLAR_NAMES[idx]}({m})' for m, idx in positions]
            results.append({
                'he_type': '三合局',
                'from': parts[0],
                'to': parts[-1],
                'desc': f'{group}{wx}局成势，{len(members)}字齐现',
            })
        elif len(present) == 2:
            a, b = present[0], present[1]
            wx_ban = _ban_he_wx(a, b)
            if wx_ban and any({r['from']['zhi'], r['to']['zhi']} == {a, b}
                              for r in raw['半三合']):
                ia, ib = zhis.index(a), zhis.index(b)
                results.append({
                    'he_type': '半合',
                    'from': f'{_ZHI_PILLAR_NAMES[ia]}({a})',
                    'to': f'{_ZHI_PILLAR_NAMES[ib]}({b})',
                    'desc': f'{a}{b}半合{wx_ban}局，气未全',
                })

    # ── 拱局（关系/取象事实，不直接判做功）──
    for record in raw['拱局']:
        a, b = record['from']['zhi'], record['to']['zhi']
        ia = PILLAR_KEYS.index(record['from']['pillar'])
        ib = PILLAR_KEYS.index(record['to']['pillar'])
        results.append({
            'he_type': '拱局',
            'from': f'{_ZHI_PILLAR_NAMES[ia]}({a})',
            'to': f'{_ZHI_PILLAR_NAMES[ib]}({b})',
            'desc': f'{a}{b}拱{record["wuxing"]}局',
        })

    # ── 暗合 ──
    # 寅丑、午亥、卯申（仅三对，初级:3218 排他）；双向表，i<j 遍历避免重复
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if AN_HE.get(z1) == z2:
                results.append({
                    'he_type': '暗合',
                    'from': f'{_ZHI_PILLAR_NAMES[i]}({z1})',
                    'to': f'{_ZHI_PILLAR_NAMES[j]}({z2})',
                    'desc': f'{z1}{z2}暗合，主私下联系、暗中交合',
                })

    return {'he_types': results}
