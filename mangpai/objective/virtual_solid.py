"""
virtual_solid - 盲派虚实分析

理论来源：段建业《段氏理象学》虚实篇
核心思想：天干的虚实取决于地支是否有同五行根。
  虚透（无根）= 才华、名气、虚名
  坐实（有根）= 实体财富、实权
  虚透怕克，坐实不怕克
已知争议：部分盲派对“根”的范围有不同说法（本气根 vs 含中余气根 vs 含生扶）
置信度：中

结构化信号（供克害引擎查询）：
  is_solid          坐实(有同五行根)与否；坐实不怕克。
  vulnerable_to_ke  虚透怕克的损害梯度：
                       坐实        -> level='无'（不怕克）
                       虚透+印生扶 -> level='轻'（印化杀生身，损害减轻）
                       虚透(无印)  -> level='重'（被克损害加重）
  has_yin_support   虚透得印生扶（生我者=印现于干支）-> 转有气偏虚。
"""
from typing import Dict, List

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, CANG_GAN_MANGPAI, WX_SHENG, is_pillars,
)
from mangpai.objective.changsheng import get_changsheng_mangpai

_GAN_WX_LOOKUP = GAN_WX

# 长生强位（生旺）-> 偏实；弱位（死墓绝）-> 偏虚
_STRONG_STAGES = {'长生', '临官', '帝旺'}
_WEAK_STAGES = {'死', '墓', '绝'}

# 生我者为印：WX_SHENG 反查（木印水、火印木、土印火、金印土、水印金）。
# 虚透得印生扶 -> 转有气偏虚；印化杀生身，被克损害由“重”减为“轻”。
_YIN_WX: Dict[str, str] = {v: k for k, v in WX_SHENG.items()}


def _has_wx_root_in_zhis(zhis: List[str], target_wx: str) -> tuple:
    """检查地支中是否有指定五行的根，返回 (是否有根, 根详情列表)。"""
    has_root = False
    root_details: List[str] = []
    for pn, pz in zhis:
        if not pz:
            continue
        # 先查本气五行
        if ZHI_WX.get(pz, '') == target_wx:
            has_root = True
            root_details.append(f'{pn}支({pz})')
        else:
            # 再查藏干五行
            for gan, _qi in CANG_GAN_MANGPAI.get(pz, []):
                if _GAN_WX_LOOKUP.get(gan, '') == target_wx:
                    has_root = True
                    root_details.append(f'{pn}支({pz}藏{gan})')
                    break
    return has_root, root_details


def _find_yin_support(
    gan: str, gan_wx: str,
    all_gans: List[tuple], all_zhis: List[tuple],
) -> tuple:
    """查找虚透天干的印生扶来源（生我者=印）。

    印可来自天干（含日干，日主亦生扶他干）或地支（本气/藏干）。
    虚透得印生扶 -> 转有气偏虚；印化杀生身，被克损害减轻。

    Returns:
        (是否有印生扶, 印来源详情列表)
    """
    yin_wx = _YIN_WX.get(gan_wx, '')
    if not yin_wx:
        return False, []
    has_yin = False
    sources: List[str] = []
    # 天干印（pg==gan 自身排除；印五行≠日干五行，故不会误纳比劫）
    for pn, pg in all_gans:
        if not pg or pg == gan:
            continue
        if _GAN_WX_LOOKUP.get(pg, '') == yin_wx:
            has_yin = True
            sources.append(f'{pn}干{pg}')
    # 地支印（本气 + 藏干）
    for pn, pz in all_zhis:
        if not pz:
            continue
        if ZHI_WX.get(pz, '') == yin_wx:
            has_yin = True
            sources.append(f'{pn}支({pz})')
        else:
            for cg, _q in CANG_GAN_MANGPAI.get(pz, []):
                if _GAN_WX_LOOKUP.get(cg, '') == yin_wx:
                    has_yin = True
                    sources.append(f'{pn}支({pz}藏{cg})')
                    break
    return has_yin, sources


def analyze_virtual_solid(
    day_gan: str, day_zhi: str,
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
) -> Dict:
    """分析十神的虚实（虚透/坐实）。

    虚实规则：
    天干虚透 = 才华、名气、虚名
    坐实（地支有同五行根）= 实体财富、实权
    长生参考（P2-3）：天干在其坐支的长生位为生旺（长生/临官/帝旺）-> 偏实，
    为死/墓/绝 -> 偏虚。长生态作为根气强弱的微调，叠加于五行通根判定之上。
    印生扶：虚透（无根）得印（生我者现于干支）-> 转有气偏虚；
    印化杀生身，被克损害由“重”减为“轻”（虚透怕克落地于 vulnerable_to_ke）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Args:
        day_gan: 日干（或 Pillars 对象）
        day_zhi: 日支
        year_gan/year_zhi/month_gan/month_zhi/hour_gan/hour_zhi: 其余三柱干支

    Returns:
        虚实分析结果（含 is_solid / vulnerable_to_ke 结构化信号）
    """
    if is_pillars(day_gan):
        p = day_gan
        day_gan, day_zhi = p.day_gan, p.day_zhi
        year_gan, year_zhi = p.year_gan, p.year_zhi
        month_gan, month_zhi = p.month_gan, p.month_zhi
        hour_gan, hour_zhi = p.hour_gan, p.hour_zhi

    pillars = [
        ('年', year_gan, year_zhi),
        ('月', month_gan, month_zhi),
        ('时', hour_gan, hour_zhi),
    ]

    all_gans = [
        ('年', year_gan), ('月', month_gan),
        ('日', day_gan), ('时', hour_gan),
    ]
    all_zhis = [
        ('年', year_zhi), ('月', month_zhi),
        ('日', day_zhi), ('时', hour_zhi),
    ]

    results: List[Dict] = []
    for pk, gan, _zhi in pillars:
        if gan == day_gan:
            continue
        gan_wx = GAN_WX.get(gan, '')
        has_root, root_details = _has_wx_root_in_zhis(all_zhis, gan_wx)
        has_yin, yin_sources = _find_yin_support(gan, gan_wx, all_gans, all_zhis)

        # 长生微调：天干在其坐支的长生位定根气偏实/偏虚
        stage = get_changsheng_mangpai(gan, _zhi) if (_zhi and gan) else ''
        if stage in _STRONG_STAGES:
            tendency = '偏实'
        elif stage in _WEAK_STAGES:
            tendency = '偏虚'
        else:
            tendency = '平'

        base_type = '坐实' if has_root else '虚透'
        # 长生弱位叠加于虚透 -> 偏虚；强位叠加于坐实 -> 偏实
        # 印生扶叠加于虚透 -> 有气偏虚（印优先于长生态判定有气）
        if has_root and tendency == '偏实':
            vtype = '坐实偏实'
        elif (not has_root) and has_yin:
            vtype = '有气偏虚'
        elif (not has_root) and tendency == '偏虚':
            vtype = '虚透偏虚'
        else:
            vtype = base_type

        # 虚透怕克结构化信号（供克害引擎查询：虚透被克 -> 损害加重）
        #   坐实(有根)        -> 不怕克（level='无'）
        #   虚透 + 印生扶      -> 印化杀生身，损害减轻（level='轻'）
        #   虚透(无印)         -> 怕克，被克损害加重（level='重'）
        if has_root:
            vuln_level = '无'
            vuln_reason = '坐实有根不怕克'
        elif has_yin:
            vuln_level = '轻'
            vuln_reason = '虚透得印生扶转有气偏虚，印化杀生身，被克损害减轻'
        else:
            vuln_level = '重'
            if tendency == '偏虚':
                vuln_reason = '虚透无根怕克（坐支死墓绝位更弱），被克损害加重'
            else:
                vuln_reason = '虚透无根怕克，被克损害加重'
        vulnerable_to_ke = {
            'vulnerable': vuln_level != '无',
            'level': vuln_level,
            'reason': vuln_reason,
        }

        desc = ('在地支有根为实，主实际财富/权力' if has_root
                else '虚透无根主才华/名气/虚名')
        if (not has_root) and has_yin:
            desc += f'；得印生扶({"/".join(yin_sources)})转有气偏虚'
        if tendency != '平':
            desc += f'（坐支{_zhi}为{gan}长生“{stage}”位，{tendency}）'

        results.append({
            'pillar': f'{pk}柱',
            'gan': gan,
            'wx': gan_wx,
            'is_solid': has_root,
            'has_yin_support': has_yin,
            'type': vtype,
            'base_type': base_type,
            'changsheng_stage': stage,
            'tendency': tendency,
            'root_details': root_details,
            'yin_sources': yin_sources,
            'vulnerable_to_ke': vulnerable_to_ke,
            'desc': desc,
        })

    # F1 标注：virtual_count/solid_count/vulnerable_count 三计数字段无消费方
    # （死字段，批9 审计）；保留不删（输出契约）。
    return {
        'virtual_solid': results,
        'virtual_count': sum(1 for r in results if not r['is_solid']),
        'solid_count': sum(1 for r in results if r['is_solid']),
        'vulnerable_count': sum(
            1 for r in results if r['vulnerable_to_ke']['vulnerable']),
    }
