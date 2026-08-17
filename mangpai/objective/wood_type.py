"""
wood_type - 盲派木的活死判断

理论来源：段建业《段氏理象学》木性篇
核心思想：日干为木时，需判断是活木还是死木，二者行为完全不同。
  活木条件：有水生 + 有根（支中有水和木根），且水能生木之根——
    「有水有根，水不生木之根也是死木」（理象学:12613-12615）：
    水支与木根支相破（子水不生卯木，:2934-2936）、相冲（戴妃造丑冲未，
    :12615）、相穿（岳飞造子穿未，:3187-3189）则该水不生该根。
  死木条件：无水或无根，或水不生木之根
  活木见火=开花泄秀（吉）；死木见火=燃烧（凶，怕旺火）
  活木怕金坏根；死木不怕金克
  活木喜水（特别是夏生）；死木见水反坏（腐烂）
  活木不制水（水为印生身，木不以制水为做功）；死木无印可生，可制水为功
结构化信号（供 zuogong 将来查询）：
  fear_metal   命局见金且坏根（活木见金即怕坏根；死木不怕金，恒 False）
  control_water 木是否以制水为做功（活木=False 不制水；死木=True）
  fire_xiuxiu  喜火泄秀（活木=True；死木见火反焚，=False）
已知争议：部分盲派对"根"的定义有不同说法（仅本气根 vs 含中余气根）
置信度：中
"""
from typing import Dict, List

from mangpai.objective.constants import (
    ZHI_WX, CANG_GAN_MANGPAI, GAN_WX, is_pillars, LIU_CHONG, LIU_HAI,
)

# 盲派相破（理象学:2930-2932「子破卯，卯破午；也可以反过来破」）——
# 与传统六破（constants.LIU_PO）不同表，勿混用。
_MANGPAI_PO = {('子', '卯'), ('卯', '子'), ('卯', '午'), ('午', '卯')}


def _wx_zhis(zhis: List[str], target_wx: str) -> List[str]:
    """返回本气或藏干含目标五行的地支列表。"""
    out = []
    for z in zhis:
        if not z:
            continue
        if ZHI_WX.get(z, '') == target_wx:
            out.append(z)
            continue
        for gan, _qi in CANG_GAN_MANGPAI.get(z, []):
            if GAN_WX.get(gan, '') == target_wx:
                out.append(z)
                break
    return out


def _water_sheng_root(water_zhi: str, root_zhi: str) -> bool:
    """水是否生木之根：相破/相冲/相穿则不生（理象学:2934-2936 子水不生卯木；
    :3187-3189 岳飞造子破卯穿未；:12613-12615 戴妃造丑冲未）。"""
    pair = (water_zhi, root_zhi)
    if pair in _MANGPAI_PO:
        return False
    for pairs in (LIU_CHONG, LIU_HAI):
        if pair in pairs or (root_zhi, water_zhi) in pairs:
            return False
    return True


def _has_wx_root(zhis: List[str], target_wx: str) -> bool:
    """检查地支中是否有指定五行的根。

    基于藏干判断：检查地支藏干中是否有目标五行的天干。
    """
    for z in zhis:
        if not z:
            continue
        # 先查本气五行
        if ZHI_WX.get(z, '') == target_wx:
            return True
        # 再查藏干五行
        for gan, _qi in CANG_GAN_MANGPAI.get(z, []):
            if GAN_WX.get(gan, '') == target_wx:
                return True
    return False


def _has_wx(gans: List[str], zhis: List[str], target_wx: str) -> bool:
    """检查天干与地支（含藏干）中是否存在指定五行。

    天干走 GAN_WX，地支走本气+藏干（复用 _has_wx_root）。
    旧位置签名只透传日干与四支，缺其余天干时退化为仅查地支——
    于 fear_metal 无碍：坏根是地支层面（如辰酉合金铲辰中乙、申冲寅、酉冲卯）。
    """
    for g in gans:
        if GAN_WX.get(g, '') == target_wx:
            return True
    return _has_wx_root(zhis, target_wx)


def analyze_wood_type(
    day_gan: str,
    year_zhi: str = '', month_zhi: str = '', day_zhi: str = '', hour_zhi: str = '',
) -> Dict:
    """判断日干木的活死性质。

    活木条件：有水生 + 有根（同时在支中有水有根）
    死木条件：无水或无根

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        day_gan: 日干（或 Pillars 对象）
        year_zhi: 年支
        month_zhi: 月支
        day_zhi: 日支
        hour_zhi: 时支

    Returns:
        木性分析结果，含 is_wood/has_root/has_water/wood_type/rules，
        及结构化信号 fear_metal/control_water/fire_xiuxiu（供 zuogong 查询）。
    """
    if is_pillars(day_gan):
        p = day_gan
        day_gan = p.day_gan
        year_zhi, month_zhi, day_zhi, hour_zhi = p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi
        other_gans = [p.year_gan, p.month_gan, p.hour_gan]
    else:
        # 旧位置签名未透传其余天干：命局见金仅能查地支（含藏干金）。
        other_gans = []

    if day_gan not in ('甲', '乙'):
        return {
            'is_wood': False,
            'wood_type': '非木日主',
            'fear_metal': False,
            'control_water': False,
            'fire_xiuxiu': False,
        }

    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    gans = [day_gan] + [g for g in other_gans if g]

    root_zhis = _wx_zhis(zhis, '木')
    water_zhis = _wx_zhis(zhis, '水')
    has_root = bool(root_zhis)
    has_water = bool(water_zhis)
    # 「有水有根，水不生木之根也是死木」（理象学:12613-12615）：
    # 水支与木根支相破/冲/穿则该水不生该根；所有水皆不生任何根时水不计。
    water_sheng = has_root and has_water and any(
        _water_sheng_root(w, r) for w in water_zhis for r in root_zhis)

    if has_root and water_sheng:
        wood_type = '活木'
    elif has_root and has_water:
        wood_type = '死木（水不生木之根）'
    elif has_root and not has_water:
        wood_type = '死木（有根无水）'
    elif not has_root and has_water:
        wood_type = '死木（有水无根）'
    else:
        wood_type = '死木（无根无水）'

    is_living = (wood_type == '活木')

    # ── 结构化信号（源码活死判定已对，此处仅把行为信号暴露给引擎）──
    # fear_metal：活木见金即怕坏根（坏根为地支层面，由 has_metal 触发）；
    #             死木不怕金克，恒 False。
    has_metal = _has_wx(gans, zhis, '金')
    fear_metal = is_living and has_metal
    # control_water：活木以水为印生身，不以制水为做功（False）；死木反之（True）。
    control_water = not is_living
    # fire_xiuxiu：活木见火为开花泄秀（True）；死木见火反焚（False）。
    fire_xiuxiu = is_living

    rules: List[str] = []
    if is_living:
        rules.append('见火为开花泄秀，吉')
        rules.append('怕金坏根（如辰酉合金铲断辰中乙木）')
        rules.append('喜水润木')
        rules.append('活木不制水（水为印生身，不以制水为做功）')
    else:
        if has_root and has_water:
            rules.append('水与木根相破/冲/穿，水不生木之根，亦为死木（理象学:12613-12615）')
        rules.append('怕见旺火（燃烧焚尽，伤寿）')
        rules.append('不怕金克（金劈木生火）')
        rules.append('见水反坏（水多腐烂，或湿木不生火）')

    return {
        'is_wood': True,
        'day_gan': day_gan,
        'has_root': has_root,
        'has_water': has_water,
        'wood_type': wood_type,
        'fear_metal': fear_metal,
        'control_water': control_water,
        'fire_xiuxiu': fire_xiuxiu,
        'rules': rules,
    }
