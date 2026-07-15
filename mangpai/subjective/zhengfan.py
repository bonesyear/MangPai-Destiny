"""
zhengfan — 盲派正局/反局

理论来源：段建业《段氏理象学》正反局篇
核心思想：
  局 = 做功 + 气势。无功不为局，无势亦不论正反。
  正局：日柱做功方向与全局气势一致，为吉
  反局：日柱做功方向与全局气势相反，为凶
  无做功：不论正反
  日干有合（合财/合官）不自动判正局——若合方向与全局气势相背，仍为反局

全局气势（段氏"成势"）：
  单向气势：某五行独旺（≥ 半数）成势，如木旺成势
  两神成象：两五行合力主盘（合计 ≥ 6/8 字）且相生或相克，如木火相生成象、木土成象
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    PILLAR_KEYS, GAN_WX, ZHI_WX, WX_SHENG, WX_KE,
)


def _pos_element(pos: str, gans: List[str], zhis: List[str]) -> str:
    """取柱位 pos（如 'hour_zhi'/'day_gan'）处的五行。"""
    if not pos or '_' not in pos:
        return ''
    pk, t = pos.split('_', 1)
    if pk not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(pk)
    if t == 'gan' and idx < len(gans) and gans[idx]:
        return GAN_WX.get(gans[idx], '')
    if t == 'zhi' and idx < len(zhis) and zhis[idx]:
        return ZHI_WX.get(zhis[idx], '')
    return ''


def _compute_qishi(gans: Optional[List[str]],
                   zhis: Optional[List[str]]) -> Optional[Dict]:
    """计算全局气势（基于八字五行分布）。

    单向气势：某五行计数 ≥ 4（半数）→ 该五行旺而成势。
    两神成象：最多的两五行合计 ≥ 6 且相生/相克 → 两神成象。
    优先判单向（更强、更专），不满足再判两神。

    Returns:
        气势描述字典（含 desc/kind/relation 等），无气势返回 None。
    """
    if not gans and not zhis:
        return None
    counts: Dict[str, int] = {wx: 0 for wx in ['木', '火', '土', '金', '水']}
    for g in (gans or []):
        if g in GAN_WX:
            counts[GAN_WX[g]] += 1
    for z in (zhis or []):
        if z in ZHI_WX:
            counts[ZHI_WX[z]] += 1

    total = sum(counts.values())
    if total < 4:
        return None

    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    top_wx, top_cnt = ranked[0]

    # 单向气势：某五行 ≥ 半数
    if top_cnt >= 4:
        return {
            'desc': f'{top_wx}旺成势',
            'kind': '单向',
            'dominant': top_wx,
            'relation': '旺',
        }

    # 两神成象：前两五行合计 ≥ 6 且相生/相克
    second_wx, second_cnt = ranked[1]
    if top_cnt + second_cnt >= 6:
        # 相生：排出生方→被生方
        if WX_SHENG.get(top_wx) == second_wx:
            return {
                'desc': f'{top_wx}{second_wx}相生成象',
                'kind': '两神', 'relation': '生',
                'pair': [top_wx, second_wx], 'target': second_wx,
            }
        if WX_SHENG.get(second_wx) == top_wx:
            return {
                'desc': f'{second_wx}{top_wx}相生成象',
                'kind': '两神', 'relation': '生',
                'pair': [second_wx, top_wx], 'target': top_wx,
            }
        # 相克：排出克方→被克方
        if WX_KE.get(top_wx) == second_wx:
            return {
                'desc': f'{top_wx}{second_wx}成象',
                'kind': '两神', 'relation': '克',
                'pair': [top_wx, second_wx],
            }
        if WX_KE.get(second_wx) == top_wx:
            return {
                'desc': f'{second_wx}{top_wx}成象',
                'kind': '两神', 'relation': '克',
                'pair': [second_wx, top_wx],
            }

    return None


def _day_control_elements(work_actions: List[Dict],
                          gans: List[str], zhis: List[str]) -> Set[str]:
    """日柱主动制（克/冲）的目标五行集合。

    用于"克破气势"反局判定：日柱主动克冲某五行即与该五行气势相背。
    """
    elems: Set[str] = set()
    for wa in work_actions:
        if wa.get('auxiliary'):
            continue  # 辅助动作（生扶/伏吟/反吟/S1去重/S2降级）不计入正反局气势
        if wa.get('type') not in ('克', '冲'):
            continue
        from_pos = wa.get('from_pos', '')
        if not from_pos.startswith('day_'):
            continue  # 仅日柱主动发起之制
        elem = _pos_element(wa.get('to_pos', ''), gans, zhis)
        if elem:
            elems.add(elem)
    return elems


def analyze_zhengfan(
    work_actions: List[Dict],
    day_he_type: Optional[str],
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
) -> Dict:
    """判断正局/反局。

    局 = 做功 + 气势。无功不为局，无势可判则局未定。
    正局：日柱做功方向与全局气势一致
    反局：日柱做功方向与全局气势相反，为凶

    判定逻辑：
      1. 无做功 → 不论正反
      2. 日柱无做功 → 无功不为局（盲派：无功不为局）
      3. 反局（五行方向）：日柱做功目标五行与全局做功主要目标五行相克 -> 反局
      4. 反局（气势）：两神成象，日柱逆势克破（相生克任一成象五行；相克克克方）-> 反局
      5. 有气势且日柱未相背 → 正局（顺势）
      6. 无气势但全局做功与日柱同向 → 正局（做功同向）
      7. 余者无势可判 → 局未定（不自动判正局）
      日干有合不自动判正局——若合方向与全局气势相背仍为反局。

    Args:
        work_actions: 做功动作列表（含 from_pos/to_pos 结构化字段）
        day_he_type: 日干合类型（合财/合官）
        gans: 四柱天干列表（可选，用于全局气势判定）
        zhis: 四柱地支列表（可选，用于全局气势判定）

    Returns:
        正局/反局判断结果，含 qishi（全局气势，可能为 None）
    """
    qishi = _compute_qishi(gans, zhis)
    he_note = f'，日干{day_he_type}' if day_he_type else ''

    if not work_actions:
        return {
            'configuration': '无做功，不论正反',
            'type': 'neutral',
            'qishi': qishi,
        }

    # 提取日柱做功的 target 柱位（日干合、日支冲克等均计入）
    day_targets: List[str] = []
    global_targets: List[str] = []

    for wa in work_actions:
        if wa.get('auxiliary'):
            continue  # 辅助动作不计入正反局做功方向（全局气势/正反局只看实质做功）
        from_pos = wa.get('from_pos', '')
        to_pos = wa.get('to_pos', '')
        # 日柱参与的做功（from 或 to 含 'day'，涵盖 day_gan 和 day_zhi）
        if 'day' in from_pos or 'day' in to_pos:
            target = to_pos if 'day' in from_pos else from_pos
            if target and 'day' not in target:
                day_targets.append(target)
            elif target:
                # target 也是 day 位置（日干合日支等罕见情况），跳过
                pass
        else:
            # 非日柱的做功
            if to_pos:
                global_targets.append(to_pos)
            if from_pos:
                global_targets.append(from_pos)

    # 日柱无做功 → 无功不为局（盲派：无功不为局，不自动判正局）
    if not day_targets:
        return {
            'configuration': '无功不为局',
            'type': 'neutral',
            'qishi': qishi,
            'reason': f'日柱无做功，无功不为局{he_note}',
        }

    # 反局判定：日柱做功方向与全局气势相背
    fan_reason = ''

    # 反局（五行方向）：日柱做功目标五行 vs 全局做功主要目标五行，相克即相背。
    #   比和（同五行）/相生为同向、顺势，不判反局；五行信息缺失则不论。
    #   （旧实现按柱位比对--日柱指向时柱、全局指向月柱即判相背--已弃用：
    #    柱位相异不等于五行方向相背，须以五行生克论同向/相背。）
    if global_targets:
        target_counts: Dict[str, int] = {}
        for t in global_targets:
            target_counts[t] = target_counts.get(t, 0) + 1
        global_main_target = max(target_counts, key=target_counts.get)
        global_main_elem = _pos_element(global_main_target, gans or [], zhis or [])
        day_elems = {
            _pos_element(t, gans or [], zhis or []) for t in day_targets
        }
        day_elems.discard('')
        if global_main_elem and day_elems:
            ke_global = any(
                WX_KE.get(de) == global_main_elem
                or WX_KE.get(global_main_elem) == de
                for de in day_elems
            )
            if ke_global:
                fan_reason = (
                    f'日柱做功指向{",".join(sorted(day_elems))}{he_note}，'
                    f'全局做功指向{global_main_elem}，五行相克相背'
                )

    # 反局（气势）：两神成象，日柱逆势克破
    #   相生成象：克破任一成象五行即断生链 -> 逆势
    #   相克成象：仅克破克方（pair[0]，主动制者）为逆势；克被克方为顺势（助制），不判反局
    if not fan_reason and qishi and qishi.get('relation') in ('生', '克'):
        pair = qishi.get('pair', [])
        day_ctrl = _day_control_elements(work_actions, gans or [], zhis or [])
        if qishi.get('relation') == '生':
            opp = set(pair) & day_ctrl
        else:  # 相克成象：逆势 = 克破克方
            opp = {pair[0]} & day_ctrl if pair else set()
        if opp:
            fan_reason = (
                f'{qishi["desc"]}，日柱克破{",".join(sorted(opp))}，'
                f'做功与气势相背{he_note}'
            )

    if fan_reason:
        return {
            'configuration': '反局',
            'type': 'fan',
            'reason': fan_reason,
            'qishi': qishi,
        }

    # 正局：日柱做功未与气势相背
    if qishi:
        return {
            'configuration': f'正局（{qishi["desc"]}，顺势）',
            'type': 'zheng',
            'reason': f'日柱做功与{qishi["desc"]}同向{he_note}',
            'qishi': qishi,
        }

    # 无气势，但全局做功与日柱同向（柱位一致）→ 正局（做功同向）
    if global_targets:
        if len(work_actions) >= 2:
            return {
                'configuration': '正局（多路做功，方向同向）',
                'type': 'zheng',
                'reason': f'有{len(work_actions)}项做功，日柱与全局同向{he_note}',
                'qishi': qishi,
            }
        return {
            'configuration': '正局（做功同向）',
            'type': 'zheng',
            'reason': f'日柱做功与全局同向{he_note}',
            'qishi': qishi,
        }

    # 有日柱做功但无气势、无全局做功可判正反 → 局未定（不自动判正局）
    return {
        'configuration': '局未定',
        'type': 'neutral',
        'reason': f'有日柱做功，然无明确气势可判正反{he_note}',
        'qishi': qishi,
    }
