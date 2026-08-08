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
    PILLAR_KEYS, GAN_WX, ZHI_WX, WX_SHENG, WX_KE, WX_KE_ME,
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, TOMB_MAP,
)


def _ss_cat(day_gan: str, gan: str) -> str:
    """十神大类（比劫/印/食伤/财/官杀），供合对党派判别（K3-294批6）。"""
    dw, gw = GAN_WX.get(day_gan, ''), GAN_WX.get(gan, '')
    if not dw or not gw:
        return ''
    if gw == dw:
        return '比劫'
    if WX_SHENG.get(gw) == dw:
        return '印'
    if WX_SHENG.get(dw) == gw:
        return '食伤'
    if WX_KE.get(dw) == gw:
        return '财'
    if WX_KE.get(gw) == dw:
        return '官杀'
    return ''


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


def _pos_zhi(pos: str, zhis: List[str]) -> str:
    """取柱位 pos（如 'hour_zhi'/'day_zhi'）处的地支字符。"""
    if not pos or '_' not in pos:
        return ''
    pk, t = pos.split('_', 1)
    if t != 'zhi' or pk not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(pk)
    return zhis[idx] if idx < len(zhis) else ''


def _he_guan_position(day_gan: str, gans: List[str]) -> str:
    """日主合官位置判定（K2-1 合官位置区分）。

    日主与他柱干五合、且该干为官杀（克日主）时：
      合时干官 → 'hour'：被官控制，官即日主意向（时官为统领、领地支），
        须以时支（官之兵卒）做功——时支做功归日主、时支不可坏特判只在此
        位置生效（《盲派中高级命理学》正反局章）。
      合年/月干官 → 'year'/'month'：管理、控制别人之意（管理权），
        不做时支归功/不可坏特判（「如是日主合年、月上的官，则意思不一样了」）。
    争合（多柱同官）以时为先。非合官返回 ''。
    """
    if not day_gan or not gans or len(gans) < 4:
        return ''
    day_wx = GAN_WX.get(day_gan, '')
    partner = TIAN_GAN_HE.get(day_gan, '')
    if not (day_wx and partner):
        return ''
    hits: List[str] = []
    for i, pk in ((0, 'year'), (1, 'month'), (3, 'hour')):
        g = gans[i] if i < len(gans) else ''
        if g == partner and GAN_WX.get(g, '') and WX_KE.get(GAN_WX[g]) == day_wx:
            hits.append(pk)
    for pk in ('hour', 'month', 'year'):
        if pk in hits:
            return pk
    return ''


_HE_GUAN_MEANING = {
    'hour': '日主合时干官（被官控制，官代表日主意向，时支为兵卒须用之）',
    'month': '日主合月干官（管理、控制别人之意）',
    'year': '日主合年干官（管理、控制别人之意）',
}


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
    gans = gans or []
    zhis = zhis or []
    day_gan = gans[2] if len(gans) > 2 else ''

    # K2-1 合官位置区分：合时干官（被官控制）与合年/月干官（管理别人）义不同，
    # 时支归功/不可坏特判仅在合时干官下生效。
    he_guan_pos = _he_guan_position(day_gan, gans)
    he_guan_meaning = _HE_GUAN_MEANING.get(he_guan_pos, '')
    base_he_note = f'，日干{day_he_type}' if day_he_type else ''
    he_note = f'，{he_guan_meaning}' if he_guan_meaning else base_he_note

    if not work_actions:
        return {
            'configuration': '无做功，不论正反',
            'type': 'neutral',
            'qishi': qishi,
        }

    # 提取日柱做功的 target 柱位（日干合、日支冲克等均计入）
    day_targets: List[str] = []
    day_fan_targets: List[str] = []  # K2-5 精化后仍计入反局（五行方向）的日柱指向
    global_targets: List[str] = []
    _gsrc: Dict[str, tuple] = {}  # 全局指向来源动作（K3-294批6 A1 残留用）

    # K2-5 合年/月干官精化（管理、控制别人=官为我所用）：日主合年/月干官者，
    # 官杀系统为日主所用（管理权，《中高级》「如是日主合年、月上的官，则意思
    # 不一样了」）——「日主合官」之合与「官杀克日主」（身旺得官之制=授权，
    # 非相背）不再作为反局（五行方向）之日柱做功指向；日柱另有他类做功
    # （日支冲穿制、泄秀生财等）指向相克者，仍照常判反。合时干官（被官控制，
    # 官即日主意向）不在此豁免；官杀克日主非「日柱做功」（日主为受方），
    # 仅在合年/月官（官为我用结构）下排除，避免全局放宽（li101 反局不动）。
    _k25_exempt = he_guan_pos in ('year', 'month')
    _guan_wx = WX_KE_ME.get(GAN_WX.get(day_gan, ''), '') if day_gan else ''

    def _k25_skip(wa: Dict, from_pos: str, to_pos: str) -> bool:
        if not _k25_exempt:
            return False
        if wa.get('type') == '天干合':
            return {from_pos, to_pos} == {'day_gan', f'{he_guan_pos}_gan'}
        if wa.get('type') == '克' and to_pos == 'day_gan':
            return bool(_guan_wx) and _pos_element(from_pos, gans, zhis) == _guan_wx
        return False

    # 日柱主动做功存在性（R-a 门控）：非辅助动作由 day_gan/day_zhi 发起≥1
    _day_has_active_work = any(
        not wa.get('auxiliary') and wa.get('from_pos', '') in ('day_gan', 'day_zhi')
        for wa in work_actions
    )

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
                # R-a（P2 推广）：日主受克（克动作以 day_gan 为目标）不计入
                # 反局（五行方向）之日柱做功指向——「日柱做功」主语是日柱
                # 主动做功，日主被克为受方非做功（K2-5「官杀克日主非日柱
                # 做功（日主为受方）」之一般化：K2-5 限于合年/月官，此处
                # 推广至一切日主受克；li101 红线复验——其反局由杀印相生/
                # 申克卯木等余证维持，不受本推广影响）。限日柱另有主动做功
                # 者方适用（有功论功、无功论受：日柱纯受动之局——如戊午日
                # 寅午戌不入局三戊造（14期贪财坐牢），日主受杀克即局之主要
                # 动态，仍计入方向判据）。day_targets 全量仍供「无功不为局」。
                if not _k25_skip(wa, from_pos, to_pos) and not (
                        wa.get('type') == '克' and to_pos == 'day_gan'
                        and _day_has_active_work):
                    day_fan_targets.append(target)
            elif target:
                # target 也是 day 位置（日干合日支等罕见情况），跳过
                pass
        elif he_guan_pos == 'hour' and from_pos == 'hour_zhi' and to_pos:
            # K2-2 时支做功归日主：日主合时干官时，时官为统领领地支，
            # 时支（官之兵卒）发起的实质做功即日主自己做的功
            # （《中高级命理学》：「坐支是否做功，如做功，这个功也是日主自己做的功」）。
            day_targets.append(to_pos)
        else:
            # 非日柱的做功
            if to_pos:
                global_targets.append(to_pos)
                _gsrc.setdefault(to_pos, (wa.get('type', ''), from_pos))
            if from_pos:
                global_targets.append(from_pos)
                _gsrc.setdefault(from_pos, (wa.get('type', ''), to_pos))

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
    k24_chong_zhis: List[str] = []  # A15：K2-4 冲合矛盾之冲对支字
    k24_chong_zhuwei = False        # A15：冲对是否在主位（日时）

    # K2-3 时支不可坏特判：日主合时干官、时支为体（比劫/印），而时支被得势方
    # 所坏（冲/刑/穿/破/克以其为目标）→ 反局（「必须用时支，时支不可坏；
    # 因为这两个时支是劫是体，体是不可以坏的，如果时支是用就可以坏」）。
    # 坏方得势为必要条件：无势之穿刑不为坏（如制例三 己酉日甲戌时，戌穿酉
    # 制食神局为大富正例——戌得火与燥土之势为主动制者，非被坏者）。
    if he_guan_pos == 'hour' and len(zhis) == 4:
        day_wx = GAN_WX.get(day_gan, '')
        hz = zhis[3]
        hz_wx = ZHI_WX.get(hz, '')
        is_ti = bool(hz_wx and day_wx and
                     (hz_wx == day_wx or WX_SHENG.get(hz_wx) == day_wx))
        if is_ti:
            qwxs: Set[str] = set()
            if qishi:
                if qishi.get('dominant'):
                    qwxs.add(qishi['dominant'])
                qwxs |= set(qishi.get('pair') or [])
            if qwxs:
                for wa in work_actions:
                    if wa.get('auxiliary'):
                        continue
                    if wa.get('type') not in ('冲', '刑', '穿', '破', '克'):
                        continue
                    if wa.get('to_pos') != 'hour_zhi':
                        continue
                    actor_pos = wa.get('from_pos', '')
                    actor_wx = _pos_element(actor_pos, gans, zhis)
                    actor_zhi = _pos_zhi(actor_pos, zhis)
                    # 坏方得势：actor 五行为气势五行，或 actor 支为气势五行之库
                    # （如丑为金库，丑借金水之势刑戌——《命术轶闻》反局例）。
                    de_shi = actor_wx in qwxs or bool(
                        actor_zhi in TOMB_MAP
                        and set(TOMB_MAP[actor_zhi]) & qwxs)
                    if de_shi:
                        fan_reason = (
                            f'日主合时干官，时支{hz}为体（印/劫）不可坏，'
                            f'被{_pos_zhi(actor_pos, zhis) or actor_pos}'
                            f'{wa.get("type","")}得势所坏——时支坏则反局{he_note}'
                        )
                        break

    # K2-4 年月 vs 日时冲合矛盾：年月两柱与日时两柱各成相反的做功方式
    # （一冲一合），整个八字自乱 → 反局（「日时是冲局，年月反是合局；
    # 或日时为合局，年月反是冲局，整个八字本身就乱了，是反局八字」）。
    if not fan_reason and len(zhis) == 4:
        def _pair_rel(a: str, b: str) -> str:
            if (a, b) in LIU_CHONG or (b, a) in LIU_CHONG:
                return '冲'
            if (a, b) in LIU_HE or (b, a) in LIU_HE:
                return '合'
            return ''
        ym_rel = _pair_rel(zhis[0], zhis[1])
        dh_rel = _pair_rel(zhis[2], zhis[3])
        if (ym_rel, dh_rel) in (('冲', '合'), ('合', '冲')):
            # 冲合联网守卫（中级冲合并见/贪合忘冲锚，K3 批1）：冲对与合对共享
            # 支字者，两种关系同属一个做功网络（同链制化/合解冲），非两党自乱
            # ——真反局=四支全异、主宾两党一边冲一边合（zgj-财反局苦力书明文
            # 「财星反局主大凶」：申巳合 vs 子午冲四支全异=真阳锚）；共享支者
            # 如两申制寅+巳申合（reg67-例9书明文三层功数十亿）、酉卯冲+戌卯合
            # （合例六书明文日支合财「富的意思」）皆同链做功，不判反局。
            if not ({zhis[0], zhis[1]} & {zhis[2], zhis[3]}):
                fan_reason = (
                    f'年月{zhis[0]}{zhis[1]}相{ym_rel}、日时{zhis[2]}{zhis[3]}相{dh_rel}，'
                    f'冲合做功方式自相矛盾，八字自乱{he_note}'
                )
                # K3-294批5 A15：记录冲对支字（供「财星反局」severe 判——
                # 财本气支在主位（日时）冲对中被冲坏，书明文「财星反局主大凶」
                # 封顶贫；宾位年月冲对不 severe——cj-平财不大书判平/小康）
                k24_chong_zhis = [zhis[0], zhis[1]] if ym_rel == '冲' \
                    else [zhis[2], zhis[3]]
                k24_chong_zhuwei = dh_rel == '冲'

    # 反局（五行方向）：日柱做功目标五行 vs 全局做功主要目标五行，相克即相背。
    #   比和（同五行）/相生为同向、顺势，不判反局；五行信息缺失则不论。
    #   （旧实现按柱位比对--日柱指向时柱、全局指向月柱即判相背--已弃用：
    #    柱位相异不等于五行方向相背，须以五行生克论同向/相背。）
    if not fan_reason and global_targets:
        target_counts: Dict[str, int] = {}
        for t in global_targets:
            target_counts[t] = target_counts.get(t, 0) + 1
        global_main_target = max(target_counts, key=target_counts.get)
        global_main_elem = _pos_element(global_main_target, gans, zhis)
        # K2-5：反局方向证据用精化后的 day_fan_targets（合年/月官之合官、
        # 官杀克日主已排除）；day_targets 仍全量供「无功不为局」判定。
        # 「相克须做功指向成立」（K3 批1，旧 any 相克口径 6/6 假阳收敛）：
        # 相背证据限日柱制式做功（克/冲/穿/刑/破）所指向的五行——生合化泄、
        # 杀印相生等和合之功与全局主指向相克者，为做功内部自然生克，不构
        # 相背；日主（day_gan）之克恒为克财（我克者为财），克财=求财之意，
        # 亦不构相背。
        #   锚：理象学资本运营例书明文「反向做功，功量很大…亿万巨富」、
        #   复例四书明文「此命有两个不同的功」、yx-富富有百万例书明文
        #   「戊喜见甲为财富」——此类盘日柱做功指向常含 2-3 个五行，
        #   旧 any(相克) 几乎必中（6/6 全假阳）。
        #   真阳边界：日柱受制式做功之指向与全局相背仍照常判反
        #   （li101 穷命红线复验：申克卯木（印制食伤）之制式指向犹在，
        #   反局不动）。
        day_elems: Set[str] = set()
        for wa in work_actions:
            if wa.get('auxiliary'):
                continue
            if wa.get('type') not in ('克', '冲', '穿', '刑', '破'):
                continue
            fp, tp = wa.get('from_pos', ''), wa.get('to_pos', '')
            if 'day' in fp:
                if fp == 'day_gan':
                    continue  # 日主之克=克财求财，不构相背
                ev_pos = tp  # 日柱主动制：证据=被制者五行
            elif 'day' in tp:
                if _k25_skip(wa, fp, tp):
                    continue
                if (wa.get('type') == '克' and tp == 'day_gan'
                        and _day_has_active_work):
                    continue  # R-a：有功论功无功论受（同 day_fan_targets 口径）
                ev_pos = fp  # 日柱受制：证据=制者五行
            else:
                continue  # 非日柱之制
            if ev_pos and 'day' not in ev_pos:
                elem = _pos_element(ev_pos, gans, zhis)
                if elem:
                    day_elems.add(elem)
        # K2-6 单向旺势同党豁免（P2，理象学制例一奥纳西斯锚）：全局单向旺
        # 成势（qishi.dominant）时，日柱做功指向五行为气势本行（==dominant）
        # 或原神（生dominant）者，与气势同党——势内之功非相背（巳午未火与
        # 燥土成势，日支未冲丑制库、未午合皆势内之功，书判巨富正局），
        # 不计入相克判据；泄势/克势/被势克之指向照常计入（保守不豁免——
        # li101 红线复验：申克卯木（木）/杀印相生（土）等指向犹在，反局不动）。
        if qishi and qishi.get('kind') == '单向' and qishi.get('dominant'):
            _dq = qishi['dominant']
            day_elems = {de for de in day_elems
                         if not (de == _dq or WX_SHENG.get(de) == _dq)}
        if global_main_elem and day_elems:
            # K3-294批6 A1 残留二道豁免（批1 any→制式收窄后的残留面，书锚双端）：
            # (a) 合局同党：全局主指向来自**三合局**（成势以参与字记指向本就宽泛，
            #   参与字非方向本身）而日柱制式指向已含该字五行者——同一成势做功
            #   网络，非相背（gj-公门转商 寅午戌火局主指向戌土∈日柱指向{火木土}，
            #   书明文「五行流转有情，故能成小富之局」；反锚 famous-李昌镐：
            #   主指向来自天干五合不在此列，其官命否决由反局维持=否·不入仕途）。
            # (b) 合链同战：全局主指向来自五合/合族（合制做功），而合之他方五行
            #   恰为日柱制式指向者——合动作把两党绑于一条合链，日柱所制与全局
            #   所制同属一役，非相背。限**官劫相缠**之合（合对两干十神为
            #   官杀×比劫——官杀制比劫之战；书锚 cj-富发财 壬丁合=官合劫，
            #   日柱辰制子水=官，书明文「官杀制比劫…发财」；reg67-乾隆 辛丙
            #   合=劫合杀同理）。反锚：zj-注册会计师 丁壬合=官×食（非官劫），
            #   li101-穷命 癸戊合之他方水∉日柱指向{木,火}，反局俱不动。
            _g_exempt = False
            _gs = _gsrc.get(global_main_target)
            if _gs:
                _gt, _gp = _gs
                _gp_elem = _pos_element(_gp, gans, zhis) if _gp else ''
                if _gt == '三合局' and global_main_elem in day_elems:
                    _g_exempt = True
                elif _gt in ('天干合', '地支合', '暗合', '半合') \
                        and _gp_elem and _gp_elem in day_elems:
                    _cats = set()
                    for _p in (global_main_target, _gp):
                        if _p.endswith('_gan'):
                            _gi = ('year', 'month', 'day', 'hour').index(_p[: -4])
                            _cats.add(_ss_cat(day_gan, gans[_gi]))
                    if _cats == {'官杀', '比劫'}:
                        _g_exempt = True
            ke_global = not _g_exempt and any(
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
            'k24_chong_zhis': k24_chong_zhis,
            'k24_chong_zhuwei': k24_chong_zhuwei,
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
