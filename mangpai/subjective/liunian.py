"""
liunian - 盲派流年分析·主观判断层（subjective）

理论来源：段建业《段氏理象学》流年篇
核心思想：
  流年为君，大运为臣。流年定应期，大运定方向。
  1. 流年干支与命局发生冲合穿刑破克生等关系
  2. 流年与大运的互动--大运定基调，流年触发事件
  3. 流年引动墓库开闭
  4. 流年激活废神
  5. 流年到禄刃位->应期
  6. 流年带十神->看发生什么事

分层说明（objective/subjective 重构）：
  流年单柱检测+吉凶信号复用 subjective.dayun._analyze_pillar_with_signals
  （其底层检测在 objective.dayun）。本模块在其结果上叠加「流年-大运互动」的
  吉凶调整（冲喜神反凶/冲忌神反吉等），并汇总为 analyze_liunian_mangpai。
  依赖方向单向：subjective -> objective（经 subjective.dayun 间接依赖）。
置信度：中
"""
from typing import Dict, List, Optional, Any

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG,
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI,
    XING_PAIRS, AN_HE, LU, PILLAR_KEYS,
)
from mangpai.subjective.dayun import _analyze_pillar_with_signals

_YANG_GANS = set('甲丙戊庚壬')

# 刃位单一事实源在 objective.shensha（_YANG_REN 主刃位 / _YANG_REN_FULL 段氏
# 全刃位，戊取午未双刃）；此处仅别名兼容，不再自带副本（M2 口径统一）。
from mangpai.objective.shensha import _YANG_REN, _YANG_REN_FULL  # noqa: F401


def _analyze_liunian_dayun_interaction(
    ln_gan: str,
    ln_zhi: str,
    dy_gan: str,
    dy_zhi: str,
) -> List[Dict]:
    """分析流年与大运的互动。

    大运为臣（背景），流年为君（触发）。流年与大运的关系决定：
    - 流年冲大运->运局动荡
    - 流年合大运->运局稳定/绊住
    - 流年生大运->顺应运局
    - 流年克大运->逆运局
    """
    interactions: List[Dict] = []
    ln_gan_wx = GAN_WX.get(ln_gan, '')
    dy_gan_wx = GAN_WX.get(dy_gan, '')
    ln_zhi_wx = ZHI_WX.get(ln_zhi, '')
    dy_zhi_wx = ZHI_WX.get(dy_zhi, '')

    if TIAN_GAN_HE.get(ln_gan) == dy_gan:
        interactions.append({
            'type': '天干合',
            'desc': f'流年{ln_gan}合大运{dy_gan}--运局被流年绊住',
        })

    if ln_gan_wx and dy_gan_wx:
        if WX_KE.get(ln_gan_wx) == dy_gan_wx and TIAN_GAN_HE.get(ln_gan) != dy_gan:
            interactions.append({
                'type': '天干克',
                'desc': f'流年{ln_gan}克大运{dy_gan}--流年逆运',
            })
        if WX_KE.get(dy_gan_wx) == ln_gan_wx and TIAN_GAN_HE.get(ln_gan) != dy_gan:
            interactions.append({
                'type': '天干被克',
                'desc': f'大运{dy_gan}克流年{ln_gan}--运压流年',
            })

    def _check_pair(a, b, pairs):
        return (a, b) in pairs or (b, a) in pairs

    if _check_pair(ln_zhi, dy_zhi, LIU_CHONG):
        interactions.append({
            'type': '冲',
            'desc': f'流年{ln_zhi}冲大运{dy_zhi}--运局动荡，应期将至',
        })

    if _check_pair(ln_zhi, dy_zhi, LIU_HE):
        interactions.append({
            'type': '六合',
            'desc': f'流年{ln_zhi}合大运{dy_zhi}--运局稳定',
        })

    if _check_pair(ln_zhi, dy_zhi, LIU_HAI):
        interactions.append({
            'type': '穿',
            'desc': f'流年{ln_zhi}穿大运{dy_zhi}--暗中损耗',
        })

    if _check_pair(ln_zhi, dy_zhi, XING_PAIRS):
        interactions.append({
            'type': '刑',
            'desc': f'流年{ln_zhi}刑大运{dy_zhi}--是非纠纷',
        })

    if AN_HE.get(ln_zhi) == dy_zhi:
        interactions.append({
            'type': '暗合',
            'desc': f'流年{ln_zhi}暗合大运{dy_zhi}--私下勾连',
        })

    if ln_zhi_wx and dy_zhi_wx:
        if WX_KE.get(ln_zhi_wx) == dy_zhi_wx:
            interactions.append({
                'type': '克',
                'desc': f'流年{ln_zhi}({ln_zhi_wx})克大运{dy_zhi}({dy_zhi_wx})',
            })
        if WX_SHENG.get(ln_zhi_wx) == dy_zhi_wx:
            interactions.append({
                'type': '生',
                'desc': f'流年{ln_zhi}({ln_zhi_wx})生大运{dy_zhi}({dy_zhi_wx})--顺应运局',
            })

    return interactions


def _judge_chong_xiji(
    day_gan: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    clashed_zhi: str,
) -> str:
    """判定流年冲大运时，所冲大运支对日主的喜忌方向（A3：复用 yongshen 扶抑框架）。

    段氏《段氏理象学》：「冲忌神反吉，冲喜神反凶」。所冲之物（大运支）为
    日主喜神则冲之反凶，为忌神则冲之反吉。喜忌定向复用
    yongshen.classify_strength（扶抑身强弱，方向总线统一口径）：
      身强/从强（印比党众）-> 忌体（印比），喜用（财官食伤）
      身弱/从弱（印比党寡）-> 喜体（印比），忌用（财官食伤）
    中和/不明则喜忌不明，返回空串，调用方按中性处理。

    Args:
        day_gan: 日干
        natal_gans: 四柱天干（日干在 index 2）
        natal_zhis: 四柱地支
        clashed_zhi: 被流年冲的大运支

    Returns:
        '喜' / '忌' / ''（无法判定）
    """
    from mangpai.subjective.yongshen import classify_strength
    day_wx = GAN_WX.get(day_gan, '')
    clashed_wx = ZHI_WX.get(clashed_zhi, '')
    if not day_wx or not clashed_wx:
        return ''

    # 印五行（生我）
    yin_wx = ''
    for _w, _gen in WX_SHENG.items():
        if _gen == day_wx:
            yin_wx = _w
            break

    strength = classify_strength(day_gan, natal_gans, natal_zhis)
    if strength in ('中和', '不明'):
        return ''  # 党势均衡/数据不足，喜忌不明
    clashed_is_ti = (clashed_wx == day_wx) or (clashed_wx == yin_wx)
    if strength in ('身强', '从强'):
        # 身强忌体喜用
        return '忌' if clashed_is_ti else '喜'
    # 身弱/从弱喜体忌用
    return '喜' if clashed_is_ti else '忌'


def analyze_liunian_mangpai(
    liunian_list: List[Dict],
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    current_dayun: Optional[Dict] = None,
    natal_fei_shen: Optional[List[str]] = None,
    kong_wang: Any = None,
) -> Dict:
    """分析流年与本命的互动（盲派视角）。

    盲派流年分析核心：
    1. 流年为君，定应期
    2. 流年与命局的冲合穿刑破克生
    3. 流年与大运的互动（大运为背景）
    4. 流年引动墓库开闭
    5. 流年激活废神
    6. 流年到禄刃位->应期
    7. 流年带十神->看发生什么事

    Args:
        liunian_list: 流年柱列表，每项含 gz（如'甲子'）或 gan/zhi，
                      以及 year（可选）
        natal_gans: 四柱天干
        natal_zhis: 四柱地支
        day_gan: 日干
        current_dayun: 当前大运柱 {gan, zhi} 或 {gz}（可选）
        natal_fei_shen: 本命废神位置列表
        kong_wang: 空亡数据

    Returns:
        {'liunian': [per-year analysis...], 'summary': '...'}
    """
    dy_gan = ''
    dy_zhi = ''
    if current_dayun:
        gz = current_dayun.get('gz', '')
        if gz and len(gz) >= 2:
            dy_gan, dy_zhi = gz[0], gz[1]
        else:
            dy_gan = current_dayun.get('gan', '')
            dy_zhi = current_dayun.get('zhi', '')

    analyses: List[Dict] = []

    for entry in liunian_list:
        gz = entry.get('gz', '')
        if gz and len(gz) >= 2:
            gan, zhi = gz[0], gz[1]
        else:
            gan = entry.get('gan', '')
            zhi = entry.get('zhi', '')

        if not gan or not zhi:
            continue

        result = _analyze_pillar_with_signals(
            gan, zhi, natal_gans, natal_zhis, day_gan,
            natal_fei_shen=natal_fei_shen,
            kong_wang=kong_wang,
            tomb_extra_gans=[gan],  # 流年干纳入墓库透干引拔（段氏墓库篇）
        )
        result['year'] = entry.get('year', 0)

        dy_interactions: List[Dict] = []
        if dy_gan and dy_zhi:
            dy_interactions = _analyze_liunian_dayun_interaction(
                gan, zhi, dy_gan, dy_zhi,
            )
            result['dayun_interaction'] = dy_interactions

            dy_chong = any(i['type'] == '冲' for i in dy_interactions)
            dy_he = any(i['type'] in ('六合', '天干合') for i in dy_interactions)

            if dy_chong:
                # 段氏「冲忌神反吉，冲喜神反凶」：按所冲大运支对日主的喜忌定向判断，
                # 不再机械降级（旧「冲即降级」与冲忌神反吉相悖）。
                chong_xiji = _judge_chong_xiji(day_gan, natal_gans, natal_zhis, dy_zhi)
                if chong_xiji == '忌':
                    result['positive_signals'].append(
                        f'流年冲大运{dy_zhi}，冲去忌神反吉')
                elif chong_xiji == '喜':
                    result['negative_signals'].append(
                        f'流年冲大运{dy_zhi}，冲去喜神反凶')
                    if result['overall'] == '吉':
                        result['overall'] = '吉凶参半'
                    elif result['overall'] == '平':
                        result['overall'] = '凶'
                else:
                    result['negative_signals'].append('流年冲大运，运局动荡')
            if dy_he:
                result['positive_signals'].append('流年合大运，运局稳定')

            dy_desc = '；'.join(i['desc'] for i in dy_interactions) if dy_interactions else ''
            if dy_desc:
                result['desc'] += f'；大运互动：{dy_desc}'

        analyses.append(result)

    ji_count = sum(1 for a in analyses if a['overall'] == '吉')
    xiong_count = sum(1 for a in analyses if a['overall'] == '凶')

    summary_parts: List[str] = []
    summary_parts.append(f'共{len(analyses)}年')
    if ji_count:
        summary_parts.append(f'吉年{ji_count}年')
    if xiong_count:
        summary_parts.append(f'凶年{xiong_count}年')

    return {
        'liunian': analyses,
        'ji_count': ji_count,
        'xiong_count': xiong_count,
        'summary': '；'.join(summary_parts),
    }


__all__ = ['analyze_liunian_mangpai']
