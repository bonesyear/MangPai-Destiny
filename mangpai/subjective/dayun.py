"""
dayun - 盲派大运分析·主观判断层（subjective）

理论来源：段建业《段氏理象学》宾主第三层、做功篇

分层说明（objective/subjective 重构）：
  消费 objective.dayun._analyze_pillar_interaction 的纯检测结果，产出吉凶信号
  （positive_signals/negative_signals）、overall（吉/凶/吉凶参半/平）与 desc 等
  解释性判断；并汇总多步大运为 analyze_dayun_mangpai。
  依赖方向单向：subjective -> objective（本模块只 import objective，不反向）。
置信度：中
"""
from typing import Dict, List, Optional, Any

from mangpai.objective.dayun import _analyze_pillar_interaction


def judge_pillar_signals(interaction: Dict) -> Dict:
    """从纯检测的 interaction 产出吉凶信号/overall/desc（解释性判断）。

    消费 _analyze_pillar_interaction 返回的检测事实（relations/tomb_effect/
    fei_shen_activated/qishi_change/lu_blade/changsheng/is_kong_wang/work_types/
    has_*），按段氏理法映射为正/负信号与综合吉凶。

    Returns:
        {'positive_signals': [...], 'negative_signals': [...],
         'overall': '吉'|'凶'|'吉凶参半'|'平', 'desc': '...'}
    """
    has_chong = interaction.get('has_chong', False)
    has_chuan = interaction.get('has_chuan', False)
    has_xing = interaction.get('has_xing', False)
    work_types: List[str] = interaction.get('work_types', [])
    lu_blade = interaction.get('lu_blade')
    tomb_effect = interaction.get('tomb_effect')
    fei_shen_activated: List[Dict] = interaction.get('fei_shen_activated', [])
    qishi_change = interaction.get('qishi_change')
    changsheng: Dict = interaction.get('changsheng', {})
    is_kong = interaction.get('is_kong_wang', False)
    tiyong: Dict = interaction.get('tiyong_import', {})

    positive_signals: List[str] = []
    negative_signals: List[str] = []

    if lu_blade:
        if lu_blade['type'] == '禄':
            positive_signals.append('到禄位，日主得根')
        else:
            negative_signals.append('到羊刃位，注意灾咎')

    if tomb_effect:
        for o in tomb_effect.get('opens', []):
            positive_signals.append(o['desc'])
        for c in tomb_effect.get('closes', []):
            negative_signals.append(c['desc'])

    if fei_shen_activated:
        positive_signals.append(f'激活{len(fei_shen_activated)}个废神->新做功')

    if qishi_change and qishi_change.get('changed'):
        positive_signals.append(qishi_change['desc'])

    cs_stage = changsheng.get('stage')
    if cs_stage == '长生' and changsheng.get('weak'):
        negative_signals.append(f'日主{cs_stage}位，相克弱长生，气弱')
    elif cs_stage in ('长生', '临官', '帝旺', '冠带', '养'):
        positive_signals.append(f'日主{cs_stage}位，气旺')
    elif cs_stage in ('死', '墓', '绝', '病'):
        negative_signals.append(f'日主{cs_stage}位，气弱')

    if is_kong:
        negative_signals.append('大运地支空亡，效应打折')

    if has_chong:
        negative_signals.append('大运冲命局，变动多')
    if has_chuan:
        negative_signals.append('大运穿命局，暗损')
    if has_xing:
        negative_signals.append('大运刑命局，是非')

    ss = tiyong.get('shishen', '')
    if ss in ('正财', '偏财', '正官'):
        positive_signals.append(f'{ss}运，利财官')
    elif ss in ('七杀', '伤官', '劫财'):
        negative_signals.append(f'{ss}运，须防官非破财')
    elif ss in ('正印', '食神'):
        positive_signals.append(f'{ss}运，利学业福寿')

    if positive_signals and not negative_signals:
        overall = '吉'
    elif negative_signals and not positive_signals:
        overall = '凶'
    elif positive_signals and negative_signals:
        overall = '吉凶参半'
    else:
        overall = '平'

    desc_parts: List[str] = []
    desc_parts.append(tiyong.get('desc', ''))
    if changsheng.get('stage'):
        cs_label = changsheng['stage']
        if changsheng.get('weak'):
            cs_label += '(相克弱长生)'
        desc_parts.append(f'日主{cs_label}')
    if lu_blade:
        desc_parts.append(lu_blade['desc'])
    if work_types:
        desc_parts.append(f'做功：{"、".join(work_types)}')
    if tomb_effect:
        for o in tomb_effect.get('opens', []):
            desc_parts.append(o['desc'])
        for c in tomb_effect.get('closes', []):
            desc_parts.append(c['desc'])
    if fei_shen_activated:
        desc_parts.append(f'激活{len(fei_shen_activated)}废神')
    if qishi_change:
        desc_parts.append(qishi_change['desc'])
    if is_kong:
        desc_parts.append('地支空亡')
    desc_parts.append(f'综合：{overall}')

    return {
        'positive_signals': positive_signals,
        'negative_signals': negative_signals,
        'overall': overall,
        'desc': '；'.join(p for p in desc_parts if p),
    }


def _analyze_pillar_with_signals(
    pillar_gan: str,
    pillar_zhi: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    natal_fei_shen: Optional[List[str]] = None,
    kong_wang: Any = None,
    tomb_extra_gans: Optional[List[str]] = None,
) -> Dict:
    """检测 + 吉凶信号（dayun/liunian 共用入口）。

    objective._analyze_pillar_interaction 产出纯检测事实，本函数叠加
    judge_pillar_signals 的解释性判断，返回含 positive_signals/negative_signals/
    overall/desc 的完整单柱结果。
    """
    result = _analyze_pillar_interaction(
        pillar_gan, pillar_zhi, natal_gans, natal_zhis, day_gan,
        natal_fei_shen=natal_fei_shen,
        kong_wang=kong_wang,
        tomb_extra_gans=tomb_extra_gans,
    )
    result.update(judge_pillar_signals(result))
    return result


def analyze_dayun_mangpai(
    dayun_list: List[Dict],
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    natal_fei_shen: Optional[List[str]] = None,
    kong_wang: Any = None,
) -> Dict:
    """分析大运与本命的互动（盲派视角）。

    盲派大运分析核心：
    1. 大运为宾，来主位（日时）做功
    2. 大运激活废神->新做功
    3. 大运冲开墓库->墓中之物可用
    4. 大运合闭墓库->墓中之物被困
    5. 大运改变气势->正反局变化
    6. 大运到禄位->禄做功
    7. 大运带十神->看带来什么

    Args:
        dayun_list: 大运柱列表，每项含 gz（如'甲子'）或 gan/zhi，
                    以及 start_age/end_age（可选）
        natal_gans: 四柱天干 [year_gan, month_gan, day_gan, hour_gan]
        natal_zhis: 四柱地支 [year_zhi, month_zhi, day_zhi, hour_zhi]
        day_gan: 日干
        natal_fei_shen: 本命废神位置列表（来自 zuogong.fei_shen）
        kong_wang: 空亡数据

    Returns:
        {'dayun': [per-pillar analysis...], 'summary': '...'}
    """
    analyses: List[Dict] = []

    for entry in dayun_list:
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
        )
        result['start_age'] = entry.get('start_age', 0)
        result['end_age'] = entry.get('end_age', 0)
        result['order'] = entry.get('order', len(analyses) + 1)
        analyses.append(result)

    ji_count = sum(1 for a in analyses if a['overall'] == '吉')
    xiong_count = sum(1 for a in analyses if a['overall'] == '凶')
    banfeng_count = sum(1 for a in analyses if a['overall'] == '吉凶参半')

    summary_parts: List[str] = []
    summary_parts.append(f'共{len(analyses)}步大运')
    if ji_count:
        summary_parts.append(f'吉运{ji_count}步')
    if xiong_count:
        summary_parts.append(f'凶运{xiong_count}步')
    if banfeng_count:
        summary_parts.append(f'吉凶参半{banfeng_count}步')

    best_dy: Optional[Dict] = None
    worst_dy: Optional[Dict] = None
    for a in analyses:
        if a['overall'] == '吉' and (best_dy is None or a['start_age'] < best_dy['start_age']):
            best_dy = a
        if a['overall'] == '凶' and (worst_dy is None or a['start_age'] < worst_dy['start_age']):
            worst_dy = a

    if best_dy:
        summary_parts.append(f'最吉：{best_dy["gz"]}({best_dy["start_age"]}岁)')
    if worst_dy:
        summary_parts.append(f'最凶：{worst_dy["gz"]}({worst_dy["start_age"]}岁)')

    return {
        'dayun': analyses,
        'ji_count': ji_count,
        'xiong_count': xiong_count,
        'banfeng_count': banfeng_count,
        'summary': '；'.join(summary_parts),
    }


__all__ = ['analyze_dayun_mangpai', 'judge_pillar_signals', '_analyze_pillar_with_signals']
