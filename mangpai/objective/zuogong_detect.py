"""
zuogong_detect - 盲派做功·纯关系检测层（objective）

理论来源：段建业《段氏理象学》做功篇
职责：仅做"四柱间存在哪些关系"的纯规则检测，不做任何做功成立判定、
      党势强弱判定、层次评估或吉凶解释。检测产出原始 work_actions /
      tomb_works / 食伤动作 / 长生·空亡·天干入墓等原始事实，交由
      subjective.zuogong_confirm 做解释性判断。

本模块为纯规则层：仅依赖 constants / muku / changsheng 等确定性查表，
无歧义、无置信度，可独立测试。
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    HUA_YONG_MAP, TOMB_MAP, GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG,
    LIU_CHONG, LIU_HE, LIU_HAI, LIU_PO, XING_PAIRS, TIAN_GAN_HE, AN_HE,
    SAN_HE, BAN_HE, LU, CANG_GAN_MANGPAI,
    PILLAR_NAMES_CN, PILLAR_KEYS,
)
from mangpai.objective.muku import is_entomb, analyze_muku, is_gan_entombed
from mangpai.objective.changsheng import get_changsheng_mangpai
from mangpai.objective.shensha import _YANG_REN as _YANG_REN_MAP

_YANG_GANS = set('甲丙戊庚壬')


def _check_pair(a: str, b: str, pairs) -> bool:
    return (a, b) in pairs or (b, a) in pairs


def _shishang_of(day_gan: str, other_gan: str) -> Optional[str]:
    """返回 other_gan 相对 day_gan 是食神/伤官，否则 None。

    食伤 = 日干所生之五行（我生）。同阴阳 polarity -> 食神，异 -> 伤官。
    """
    day_wx = GAN_WX.get(day_gan, '')
    other_wx = GAN_WX.get(other_gan, '')
    if not day_wx or not other_wx:
        return None
    if WX_SHENG.get(day_wx) != other_wx:
        return None  # 非"我生"，不是食伤
    day_yang = day_gan in _YANG_GANS
    other_yang = other_gan in _YANG_GANS
    return '食神' if day_yang == other_yang else '伤官'


def _day_faction(day_gan: str, gans: List[str], zhis: List[str]) -> tuple:
    """日柱所在方（党）五行与党羽数。

    党 = 同我（比劫，与日干同五行）+ 生我（印，生日干之五行）。
    返回 (印五行, 官杀五行, 党羽数)。党羽数不含日干自身（只计其余柱位的
    比劫/印），用于党势强弱判定：孤身无党者无力制用做功。
    """
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx:
        return '', '', 0
    yin_wx = ''
    for _w, _gen in WX_SHENG.items():
        if _gen == day_wx:
            yin_wx = _w  # 印 = 生我之五行
            break
    sha_wx = WX_KE_ME.get(day_wx, '')  # 官杀 = 克我之五行
    supporters = 0
    for i, g in enumerate(gans):
        if i == 2 or not g:  # 跳过日干自身
            continue
        wx = GAN_WX.get(g, '')
        if wx == day_wx or wx == yin_wx:
            supporters += 1
    for i, z in enumerate(zhis):
        if not z:
            continue
        wx = ZHI_WX.get(z, '')
        if wx == day_wx or wx == yin_wx:
            supporters += 1
    return yin_wx, sha_wx, supporters


def _pos_wx(pos: str, gans: List[str], zhis: List[str]) -> str:
    """由做功 from_pos/to_pos（如 'day_zhi'/'month_gan'）取该柱位天干或地支之五行。"""
    if not pos:
        return ''
    for idx, key in enumerate(PILLAR_KEYS):
        if pos == f'{key}_gan':
            return GAN_WX.get(gans[idx], '')
        if pos == f'{key}_zhi':
            return ZHI_WX.get(zhis[idx], '')
    return ''


def _kong_wang_zhis(kong_wang) -> Set[str]:
    """从 kong_wang 参数提取空亡地支集合。

    兼容多种传入形态（calc_bazi_full 的 kong_wang 各实现不一）：
      - None / 空值 -> 空集
      - list/tuple/set of 地支 -> 直接取其中的地支
      - dict -> 依次取 'zhi'/'kong'/'kong_wang_zhi'/'kong_wang'/'kong_zhi'/'空亡'
        键下的列表；若无，取第一个 list/tuple/set 值；再无则取值为地支的项
    仅保留合法地支（ZHI_WX 中存在），过滤脏数据。
    """
    if not kong_wang:
        return set()
    if isinstance(kong_wang, dict):
        for k in ('zhi', 'kong', 'kong_wang_zhi', 'kong_wang', 'kong_zhi', '空亡'):
            v = kong_wang.get(k)
            if isinstance(v, (list, tuple, set)):
                return {z for z in v if isinstance(z, str) and z in ZHI_WX}
        for v in kong_wang.values():
            if isinstance(v, (list, tuple, set)):
                return {z for z in v if isinstance(z, str) and z in ZHI_WX}
        return {z for z in kong_wang.values()
                if isinstance(z, str) and z in ZHI_WX}
    if isinstance(kong_wang, (list, tuple, set)):
        return {z for z in kong_wang if isinstance(z, str) and z in ZHI_WX}
    return set()


def detect_relations(
    day_gan: str, day_zhi: str,
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
    kong_wang=None,
) -> Dict:
    """纯关系检测：扫描四柱间的冲合刑害穿破生克墓暗合等关系。

    不做做功成立判定、不做党势/层次/吉凶判断--仅产出原始关系动作与
    原始事实数据（长生/空亡/天干入墓/墓库闭库），交由上层 confirm 解释。

    Args:
        day_gan: 日干
        day_zhi: 日支
        year_gan/year_zhi/month_gan/month_zhi/hour_gan/hour_zhi: 其余三柱干支
        kong_wang: 空亡数据（可选，地支列表或含地支列表的 dict）

    Returns:
        原始检测结果字典：
          work_actions: 所有检出关系动作（含 type/action/from/to/from_pos/
                        to_pos/desc/severity；生扶/伏吟/反吟带 auxiliary=True）。
                        未经去重/降级/折扣标注。
          tomb_works: 墓用动作（独立列表，由 confirm 决定何时并入 work_actions）
          sheng_yong_actions: 食伤泄秀动作引用（供 confirm 优先级链判定主做功）
          day_he_type: 日干合类型（合财/合官/合）或 None
          san_he_formed: 三合局是否成势
          zheng_he: 是否争合（两干以上与日干合）
          day_changsheng: 日干在各支的长生阶段（原始事实，回传最终结果）
          day_weak_zhis: 日干处死/墓/绝的地支集合（供折扣标注）
          kong_wang_zhis: 空亡地支集合（供折扣标注 + 回传）
          entombed_gan_pillars: 天干入墓所在柱集合（供折扣标注）
    """
    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    pillar_keys = PILLAR_KEYS
    day_wx = GAN_WX.get(day_gan, '')

    work_actions: List[Dict] = []
    # work_types 此处为建阶段 provisional 集合，仅供循环内 .add 调用保持自洽；
    # confirm 阶段会以 non_aux 重算最终 work_types（见 zuogong_confirm），
    # 故本集合不回传、不被消费。
    work_types: Set[str] = set()
    tomb_works: List[Dict] = []
    sheng_yong_actions: List[Dict] = []
    day_he_type: Optional[str] = None
    san_he_formed = False

    # ── 天干五合（日干合）──
    he_gan = TIAN_GAN_HE.get(day_gan, '')
    # 争合：两个或以上相同天干与日干合 -> 不化
    he_gan_count = sum(1 for g in gans if g and g == he_gan)
    zheng_he = he_gan_count >= 2

    for i, gan in enumerate(gans):
        pk = pillar_keys[i]
        if pk == 'day' or not gan:
            continue
        if TIAN_GAN_HE.get(day_gan) == gan:
            other_wx = GAN_WX.get(gan, '')
            if day_wx and WX_KE.get(day_wx) == other_wx:
                day_he_type = '合财'
            elif day_wx and WX_KE.get(other_wx) == day_wx:
                day_he_type = '合官'
            else:
                day_he_type = '合'

            work_actions.append({
                'type': '天干合',
                'action': '合用',
                'from': f'日干({day_gan})',
                'to': f'{PILLAR_NAMES_CN[i]}干({gan})',
                'from_pos': 'day_gan',
                'to_pos': f'{pk}_gan',
                'desc': f'{day_gan}{gan}合，{day_he_type}' + ('（争合）' if zheng_he else ''),
            })
            work_types.add('合用')

            # ── 合化判断（天干五合化气，归入合用）──
            # 段氏化用本为杀印相生（见下方 _detect 杀印相生），天干五合化气属合之延伸，
            # 故化气成功者标"合化"并入合用，不再冒用化用之名。
            # 合化条件：1)两干相邻（与日干索引差1）2)月令为化气五行 3)无克破 4)无争合
            # 日干索引为2，相邻即月干(1)或时干(3)；年干(0)隔位不合化
            #
            # 功能归类：type='合化'、work_types 累入'合用'（非'化用'），故不触发
            # hua_success/化用成局--化用之名现仅属杀印相生。action 字段保留旧值
            # '化用'仅为兼容 verify_mangpai 合化条件用例对 action=='化用'的过滤
            # （action 纯标签，不介入去重/层次/效率/primary_work 等任何判定）。
            if abs(i - 2) == 1 and not zheng_he:
                hua_pair = (day_gan, gan)
                if hua_pair in HUA_YONG_MAP:
                    hua_wx = HUA_YONG_MAP[hua_pair]
                    month_zhi_wx = ZHI_WX.get(month_zhi, '')
                    if month_zhi_wx == hua_wx:
                        # 检查无克破：化气五行被克则破
                        ke_hua_wx = WX_KE_ME.get(hua_wx, '')
                        has_ke_po = False
                        # 地支克破检查（月令本身为化气之地，不参与克破）
                        for j, z in enumerate(zhis):
                            if j == 1:
                                continue
                            if ZHI_WX.get(z, '') == ke_hua_wx:
                                has_ke_po = True
                                break
                        # 天干克破检查（跳过合化两方）
                        if not has_ke_po:
                            for j, g in enumerate(gans):
                                if j == 2 or j == i:
                                    continue
                                if GAN_WX.get(g, '') == ke_hua_wx:
                                    has_ke_po = True
                                    break
                        if not has_ke_po:
                            work_actions.append({
                                'type': '合化',
                                'action': '化用',
                                'from': f'日干({day_gan})',
                                'to': f'{PILLAR_NAMES_CN[i]}干({gan})',
                                'from_pos': 'day_gan',
                                'to_pos': f'{pk}_gan',
                                'desc': f'{day_gan}{gan}合化{hua_wx}，月令{month_zhi}为{hua_wx}气，无克破',
                            })
                            work_types.add('合用')

    # ── 非日干天干合（伤官合杀/食神合官/羊刃合杀等，合制做功）──
    # 段氏：天干合不限于日干，伤官合杀、食神合官、羊刃合杀等非日干合亦为合制做功
    # （如 day=丁 戊癸合=伤官合杀）。M4：放开涉时干限制——年月（宾宾）合制同为
    # 真实关系，一并检出；做功权重（主宾/远近）由 confirm 层判定，本层只检不判。
    # 非合制之合（如印合食伤）仍不计，避免误改功神/废神。
    if day_wx:
        _guan_wx = WX_KE_ME.get(day_wx, '')      # 官杀五行（克我）
        _shi_wx = WX_SHENG.get(day_wx, '')       # 食伤五行（我生）
        _bi_wx = day_wx                          # 比劫五行（同我）
        for i in range(4):
            if i == 2:
                continue
            for j in range(i + 1, 4):
                if j == 2:
                    continue
                # M4：放开涉时干限制（原要求至少一方时干，宾宾年月合制漏检）
                gi, gj = gans[i], gans[j]
                if not gi or not gj:
                    continue
                if TIAN_GAN_HE.get(gi) != gj:
                    continue
                gi_wx, gj_wx = GAN_WX.get(gi, ''), GAN_WX.get(gj, '')
                # 合制：一方官杀，另一方食伤/比劫（制杀/制官之合）
                _is_hezhi = False
                if _guan_wx and gi_wx == _guan_wx and gj_wx in (_shi_wx, _bi_wx):
                    _is_hezhi = True
                elif _guan_wx and gj_wx == _guan_wx and gi_wx in (_shi_wx, _bi_wx):
                    _is_hezhi = True
                if not _is_hezhi:
                    continue
                pk_i, pk_j = pillar_keys[i], pillar_keys[j]
                _bin_bin = (i != 3 and j != 3)  # M4：宾宾（年月）合制，不做主功
                work_actions.append({
                    'type': '天干合',
                    'action': '合用',
                    'from': f'{PILLAR_NAMES_CN[i]}干({gi})',
                    'to': f'{PILLAR_NAMES_CN[j]}干({gj})',
                    'from_pos': f'{pk_i}_gan',
                    'to_pos': f'{pk_j}_gan',
                    'desc': f'{gi}{gj}合（非日干合，合制做功）'
                            + ('（宾宾合制，不做主功）' if _bin_bin else ''),
                    # M4：宾宾合制检出但标 auxiliary（时干主位合制照旧计入）
                    **({'auxiliary': True, 'bin_bin_hezhi': True} if _bin_bin else {}),
                })
                work_types.add('合用')

    # ── 生用（食伤泄秀）──
    # 盲派生用 = 食伤泄秀：日干有食神/伤官贴近日干（天干月干/时干，或地支月支/日支
    # 藏干食伤），且该食伤再去生财或制杀，方为做功。无财杀目标者仅泄秀，不做功。
    # 食伤在地支（如坐支食神、月支食神）亦为泄秀做功（宾来生主之食伤生财）。
    # M4：补年干食伤漏检——年干（宾位远干）食伤生财/制杀同为真实关系，检出但
    # 标 auxiliary（远干泄秀力弱，不做主功；段氏生例皆月/时干或月/日支贴身食伤），
    # 做功权重交 confirm 判定。
    if day_wx:
        cai_wx = WX_KE.get(day_wx, '')      # 财五行 = 我克
        sha_wx = WX_KE_ME.get(day_wx, '')   # 杀五行 = 克我
        for idx in (0, 1, 3):  # 年干(M4补)、月干、时干
            other_gan = gans[idx]
            if not other_gan:
                continue
            ss = _shishang_of(day_gan, other_gan)
            if ss is None:
                continue
            pk = pillar_keys[idx]
            sheng_cai_targets: List[str] = []
            zhi_sha_targets: List[str] = []
            # 食伤生财：天干或地支中有财
            for j, g in enumerate(gans):
                if j == 2 or not g:
                    continue
                if GAN_WX.get(g, '') == cai_wx:
                    sheng_cai_targets.append(f'{PILLAR_NAMES_CN[j]}干{g}')
            for j, z in enumerate(zhis):
                if not z:
                    continue
                if ZHI_WX.get(z, '') == cai_wx:
                    sheng_cai_targets.append(f'{PILLAR_NAMES_CN[j]}支{z}')
            # 食伤制杀：天干或地支中有杀
            for j, g in enumerate(gans):
                if j == 2 or not g:
                    continue
                if GAN_WX.get(g, '') == sha_wx:
                    zhi_sha_targets.append(f'{PILLAR_NAMES_CN[j]}干{g}')
            for j, z in enumerate(zhis):
                if not z:
                    continue
                if ZHI_WX.get(z, '') == sha_wx:
                    zhi_sha_targets.append(f'{PILLAR_NAMES_CN[j]}支{z}')
            sub_parts: List[str] = []
            subtype = '食伤泄秀'
            if sheng_cai_targets:
                sub_parts.append('生财(' + '、'.join(sheng_cai_targets) + ')')
                subtype = '食伤生财'
            if zhi_sha_targets:
                sub_parts.append('制杀(' + '、'.join(zhi_sha_targets) + ')')
                if subtype == '食伤泄秀':
                    subtype = '食伤制杀'
            if not sub_parts:
                # 食伤贴身但无财杀目标，仅泄秀不做功
                continue
            action = {
                'type': '食伤',
                'action': '生用',
                'subtype': subtype,
                'from': f'日干({day_gan})',
                'to': f'{PILLAR_NAMES_CN[idx]}干({other_gan})',
                'from_pos': 'day_gan',
                'to_pos': f'{pk}_gan',
                'desc': f'{ss}{other_gan}泄秀，' + '、'.join(sub_parts),
            }
            if idx == 0:
                # M4 年干食伤：宾位远干泄秀力弱，检出标 auxiliary 不做主功
                action['auxiliary'] = True
                action['year_gan_shengyong'] = True
                action['desc'] += '（年干远泄，不做主功）'
            work_actions.append(action)
            sheng_yong_actions.append(action)
            work_types.add('生用')

        # 地支食伤（月支/日支藏干食伤贴身，泄秀做功；食伤藏支生财/制杀同属生用）
        # 仅取本气藏干：中气/余气食伤过弱且易误检（如申中壬、巳中戊），与制用本气口径一致。
        for idx in (1, 2):  # 月支、日支
            _zhi = zhis[idx]
            if not _zhi:
                continue
            _cang = CANG_GAN_MANGPAI.get(_zhi, [])
            if not _cang:
                continue
            _ss_gan = _cang[0][0]  # 本气藏干
            if _shishang_of(day_gan, _ss_gan) is None:
                continue  # 本气非食伤，不做生用
            # 入墓之物不做功：食伤地支若被墓库所收，其食伤被困，不应泄秀做生用。
            # （如数学家 亥入辰墓，亥藏壬食伤不做生用，主功在制用+墓用；富婆 子不入墓，正常生用。）
            if any(zk and zk != _zhi and zk in TOMB_MAP and is_entomb(_zhi, zk, zhis, gans)
                   for zk in zhis):
                continue
            _ss = _shishang_of(day_gan, _ss_gan)
            _pk = pillar_keys[idx]
            # 做功须涉主宾交换：食伤在宾(月)则目标须在主(日/时)，食伤在主(日)则目标须在宾(年/月)。
            # 主主(日支食伤生时支财)/宾宾(月支食伤生年支财)为内部流转，非做功。
            _target_idx = {2, 3} if idx in (0, 1) else {0, 1}
            _sheng_cai_t: List[str] = []
            _zhi_sha_t: List[str] = []
            for _j, _g in enumerate(gans):
                if _j == 2 or not _g or _j not in _target_idx:
                    continue
                if GAN_WX.get(_g, '') == cai_wx:
                    _sheng_cai_t.append(f'{PILLAR_NAMES_CN[_j]}干{_g}')
            for _j, _z in enumerate(zhis):
                if not _z or _j not in _target_idx:
                    continue
                if ZHI_WX.get(_z, '') == cai_wx:
                    _sheng_cai_t.append(f'{PILLAR_NAMES_CN[_j]}支{_z}')
            for _j, _g in enumerate(gans):
                if _j == 2 or not _g or _j not in _target_idx:
                    continue
                if GAN_WX.get(_g, '') == sha_wx:
                    _zhi_sha_t.append(f'{PILLAR_NAMES_CN[_j]}干{_g}')
            for _j, _z in enumerate(zhis):
                if not _z or _j not in _target_idx:
                    continue
                if ZHI_WX.get(_z, '') == sha_wx:
                    _zhi_sha_t.append(f'{PILLAR_NAMES_CN[_j]}支{_z}')
            _sub_parts: List[str] = []
            _subtype = '食伤泄秀'
            if _sheng_cai_t:
                _sub_parts.append('生财(' + '、'.join(_sheng_cai_t) + ')')
                _subtype = '食伤生财'
            if _zhi_sha_t:
                _sub_parts.append('制杀(' + '、'.join(_zhi_sha_t) + ')')
                if _subtype == '食伤泄秀':
                    _subtype = '食伤制杀'
            if not _sub_parts:
                continue  # 食伤藏支但无财杀目标，仅泄秀不做功
            _action = {
                'type': '食伤',
                'action': '生用',
                'subtype': _subtype,
                'from': f'日干({day_gan})',
                'to': f'{PILLAR_NAMES_CN[idx]}支({_zhi}藏{_ss_gan})',
                'from_pos': 'day_gan',
                'to_pos': f'{_pk}_zhi',
                'desc': f'{_zhi}藏{_ss}({_ss_gan})泄秀，' + '、'.join(_sub_parts),
            }
            work_actions.append(_action)
            sheng_yong_actions.append(_action)
            work_types.add('生用')

        # ── 内食神格（食神藏财·主位时支食伤本气坐藏财，无明财）──
        # 段氏"内食神成格"为企业之命（郝金阳：内食神者被人吃，为社会创造财富的
        # 企业家）：食伤居主位时支本气，其坐支藏财（食神生财，财以才华看），天干
        # 无明财（无可生之明财，惟生坐支藏财），方为内食神生用做功。原月/日支食伤
        # 扫描仅认主宾交换目标，对此"食神藏财"主主内化之格漏检（生例四 企业家
        # 壬癸壬壬/寅卯子寅，时支寅藏甲食神、藏丙财，无明财）。入墓之物不做功
        # （复例一 亥入辰墓，食伤被困不泄秀）。仅补时支(idx=3)，与月/日支扫描不重叠。
        if day_wx:
            _nshi_idx = 3  # 时支（主位）
            _nshi_zhi = zhis[_nshi_idx]
            if _nshi_zhi:
                _nshi_cang = CANG_GAN_MANGPAI.get(_nshi_zhi, [])
                if _nshi_cang:
                    _nshi_ben = _nshi_cang[0][0]
                    if (_shishang_of(day_gan, _nshi_ben) is not None
                            and not any(zk and zk != _nshi_zhi and zk in TOMB_MAP
                                        and is_entomb(_nshi_zhi, zk, zhis, gans) for zk in zhis)
                            and any(GAN_WX.get(g, '') == cai_wx for g, _ in _nshi_cang)
                            and not any(GAN_WX.get(g, '') == cai_wx for g in gans)):
                        _nshi_ss = _shishang_of(day_gan, _nshi_ben)
                        _nshi_action = {
                            'type': '食伤',
                            'action': '生用',
                            'subtype': '食伤生财',
                            'from': f'日干({day_gan})',
                            'to': f'{PILLAR_NAMES_CN[_nshi_idx]}支({_nshi_zhi}藏{_nshi_ben})',
                            'from_pos': 'day_gan',
                            'to_pos': f'{pillar_keys[_nshi_idx]}_zhi',
                            'desc': f'{_nshi_zhi}藏{_nshi_ss}({_nshi_ben})泄秀，内食神生坐支藏财（食神藏财·才华）',
                        }
                        work_actions.append(_nshi_action)
                        sheng_yong_actions.append(_nshi_action)
                        work_types.add('生用')

    # ── 化用（杀印相生：官杀->印->日主链）──
    # 段氏《段氏理象学》化用即杀印相生：官杀(克我)生印(生我)生日主，化杀为印、
    # 化印为身方为做功（原实现误以天干合化为化用，已将合化归入合用）。
    # 五行循环中官杀恒生印、印恒生日主，故链路成立性取决于官杀与印是否同现。
    # 做功要求印须"主动"以化杀：印透干或印居月令（司令之印）方为真化用做功；
    # 官杀须透干（明杀受化）。杀印双透/印令即化用成局之象。
    if day_wx:
        yin_wx, sha_wx, _supporters = _day_faction(day_gan, gans, zhis)
        if sha_wx and yin_wx:
            sha_gan_idx = -1  # 透干官杀所在柱（非日干）
            for i, g in enumerate(gans):
                if not g or i == 2:
                    continue
                if GAN_WX.get(g, '') == sha_wx:
                    sha_gan_idx = i
                    break
            yin_active = False
            for i, g in enumerate(gans):
                if not g or i == 2:
                    continue  # 日干非印，跳过
                if GAN_WX.get(g, '') == yin_wx:
                    yin_active = True  # 印透干
                    break
            if not yin_active and ZHI_WX.get(month_zhi, '') == yin_wx:
                yin_active = True  # 印居月令（司令之印）
            # 坐下印（日支本气印）：日支为印即印星贴身化杀，如化例二 丙日坐寅木印化壬水杀。
            # 段氏"坐下印星化杀生身"即此象，与透干/月令印同为真化用做功之印。
            if not yin_active and ZHI_WX.get(day_zhi, '') == yin_wx:
                yin_active = True  # 坐下印（日支本气印）
            if sha_gan_idx >= 0 and yin_active:
                si = sha_gan_idx
                sha_gan = gans[si]
                work_actions.append({
                    'type': '杀印相生',
                    'action': '化用',
                    'from': f'日干({day_gan})',
                    'to': f'{PILLAR_NAMES_CN[si]}干({sha_gan})',
                    'from_pos': 'day_gan',
                    'to_pos': f'{pillar_keys[si]}_gan',
                    'desc': f'官杀({sha_gan}{sha_wx})生印({yin_wx})生日主({day_gan}{day_wx})，杀印相生化用做功',
                })
                work_types.add('化用')

    # ── 地支六合（做功）──
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if _check_pair(z1, z2, LIU_HE):
                is_day = (i == 2 or j == 2)
                work_actions.append({
                    'type': '地支合',
                    'action': '合用',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}合' + ('（日支参与）' if is_day else ''),
                })
                work_types.add('合用')

    # ── 暗合（合用）──
    # 盲派独有：日支通过暗合获取远方之物，段建业《段氏理象学》做功篇将暗合列为合用。
    # 暗合组合：寅丑、午亥、卯申（共3组，AN_HE 表已双向映射；初级:3218「只有三个」排他）
    # 做功要求日支参与--日支暗合远方柱支为隐秘做功
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if AN_HE.get(z1) == z2 and (i == 2 or j == 2):
                work_actions.append({
                    'type': '暗合',
                    'action': '合用',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}暗合（日支参与），主隐秘做功、暗中获取',
                })
                work_types.add('合用')

    # ── 三合局 / 半合（成势做功）──
    # 三合三字齐现 -> 成局成势；半合（生旺/旺墓相邻二字）-> 半成势
    zhis_set = [z for z in zhis if z]
    san_he_participants: List[str] = []
    for group, wx in SAN_HE.items():
        members = list(group)
        present_members = [m for m in members if m in zhis_set]
        if len(present_members) == len(members):
            # 成局：三合三字齐现、或四库会局四字齐现 -> 化该五行之气成势
            san_he_formed = True
            parts: List[str] = []
            for m in members:
                idx = zhis.index(m)
                parts.append(f'{PILLAR_NAMES_CN[idx]}支({m})')
                san_he_participants.append(f'{pillar_keys[idx]}_zhi')
            work_actions.append({
                'type': '三合局',
                'action': '成势做功',
                'from': parts[0],
                'to': parts[-1],
                'from_pos': san_he_participants[0],
                'to_pos': san_he_participants[-1],
                'participants': list(san_he_participants),
                'desc': f'{group}{wx}局成势，参与字均为功神',
            })
            work_types.add('成势')
        elif len(present_members) == 2:
            pair_str = ''.join(present_members)
            if pair_str in BAN_HE:
                # 半合（生旺/旺墓相邻对）；三合未全，气未成局
                a, b = present_members[0], present_members[1]
                ia, ib = zhis.index(a), zhis.index(b)
                work_actions.append({
                    'type': '半合',
                    'action': '半成势',
                    'from': f'{PILLAR_NAMES_CN[ia]}支({a})',
                    'to': f'{PILLAR_NAMES_CN[ib]}支({b})',
                    'from_pos': f'{pillar_keys[ia]}_zhi',
                    'to_pos': f'{pillar_keys[ib]}_zhi',
                    'participants': [f'{pillar_keys[ia]}_zhi', f'{pillar_keys[ib]}_zhi'],
                    'desc': f'{a}{b}半合{BAN_HE[pair_str]}局，气未全',
                })
                work_types.add('合用')

    # ── 六冲（制用）──
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if _check_pair(z1, z2, LIU_CHONG):
                work_actions.append({
                    'type': '冲',
                    'action': '冲',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}冲',
                    'severity': 'normal',
                })
                work_types.add('制用')

    # ── 克（制用）──
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            wx1 = ZHI_WX.get(z1, '')
            wx2 = ZHI_WX.get(z2, '')
            if wx1 and wx2:
                if WX_KE.get(wx1) == wx2:
                    work_actions.append({
                        'type': '克',
                        'action': '克',
                        'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                        'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                        'from_pos': f'{pillar_keys[i]}_zhi',
                        'to_pos': f'{pillar_keys[j]}_zhi',
                        'desc': f'{z1}{wx1}克{z2}{wx2}',
                        'severity': 'normal',
                    })
                    work_types.add('制用')
                elif WX_KE.get(wx2) == wx1:
                    work_actions.append({
                        'type': '克',
                        'action': '克',
                        'from': f'{PILLAR_NAMES_CN[j]}支({z2})',
                        'to': f'{PILLAR_NAMES_CN[i]}支({z1})',
                        'from_pos': f'{pillar_keys[j]}_zhi',
                        'to_pos': f'{pillar_keys[i]}_zhi',
                        'desc': f'{z2}{wx2}克{z1}{wx1}',
                        'severity': 'normal',
                    })
                    work_types.add('制用')

    # ── 天干克（制用）──
    # 遍历天干，用 GAN_WX 判两干生克；日干参与的克加 type=克（与支克共用同名 type）。
    # 天干五合之对（甲己/乙庚/丙辛/丁壬/戊癸）亦含单向克，但合为主动关系，
    # 段氏以合论不以克论，故合对不再计天干克，避免与天干合重复。
    # M4：放开日干参与限制——他干之间相克（年月/年时/月时）同为真实关系，一并
    # 检出；主宾/做功权重由 confirm S2 宾宾过滤判定（非日柱参与者降 auxiliary）。
    for i in range(4):
        for j in range(i + 1, 4):
            g1, g2 = gans[i], gans[j]
            if not g1 or not g2:
                continue
            if TIAN_GAN_HE.get(g1) == g2:
                continue  # 合对以合论，不计天干克
            gw1, gw2 = GAN_WX.get(g1, ''), GAN_WX.get(g2, '')
            if WX_KE.get(gw1) == gw2:
                fg, tg, f_idx, t_idx = g1, g2, i, j
            elif WX_KE.get(gw2) == gw1:
                fg, tg, f_idx, t_idx = g2, g1, j, i
            else:
                continue  # 须天干相克
            _non_day = not (f_idx == 2 or t_idx == 2)
            work_actions.append({
                'type': '克',
                'action': '克',
                'from': f'{PILLAR_NAMES_CN[f_idx]}干({fg})',
                'to': f'{PILLAR_NAMES_CN[t_idx]}干({tg})',
                'from_pos': f'{pillar_keys[f_idx]}_gan',
                'to_pos': f'{pillar_keys[t_idx]}_gan',
                'desc': f'{fg}{GAN_WX.get(fg, "")}克{tg}{GAN_WX.get(tg, "")}'
                        + ('（宾位干相克，不做主功）' if _non_day else ''),
                'severity': 'normal',
                # M4：非日柱天干克（宾宾/宾主他干）检出但标 auxiliary，
                # 与 confirm S2 宾宾过滤同口径提前标注，保护 raw 消费方
                **({'auxiliary': True, 'non_day_ganke': True} if _non_day else {}),
            })
            work_types.add('制用')

    # ── 刑（制用，含自刑）──
    # 自刑（辰辰/午午/酉酉/亥亥）只在同一地支出现在不同柱时触发（i<j 天然要求两柱）
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if _check_pair(z1, z2, XING_PAIRS):
                is_zi_xing = (z1 == z2)
                work_actions.append({
                    'type': '刑',
                    'action': '刑',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}刑' + ('（自刑）' if is_zi_xing else ''),
                    'severity': 'normal',
                })
                work_types.add('制用')

    # ── 穿/害（制用）──
    # 盲派最重视的破坏性关系之一--"穿坏即灾"。
    # 穿比冲更凶：冲是正面对抗，穿是暗中破坏。段建业《段氏理象学》用大量篇幅讲穿。
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if _check_pair(z1, z2, LIU_HAI):
                work_actions.append({
                    'type': '穿',
                    'action': '穿',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}穿',
                    'severity': 'high',
                })
                work_types.add('制用')

    # ── 六破（制用）──
    # 破与穿同为暗中破坏，severity='high'。盲派原典六破应事较轻，但既落地则与穿同级标记。
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if _check_pair(z1, z2, LIU_PO):
                work_actions.append({
                    'type': '破',
                    'action': '破',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z1}{z2}破',
                    'severity': 'high',
                })
                work_types.add('制用')

    # ── 生（生扶，辅助标记）──
    # 注意：盲派"生用"专指食伤泄秀（见上文），地支五行相生仅为生扶帮扶，
    # 不计为"生用"做功，降级为辅助标记（auxiliary）。保留 type='生' 以区分被动生扶。
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            wx1 = ZHI_WX.get(z1, '')
            wx2 = ZHI_WX.get(z2, '')
            if wx1 and wx2 and (i == 2 or j == 2):
                if WX_SHENG.get(wx1) == wx2:
                    work_actions.append({
                        'type': '生',
                        'action': '生扶',
                        'auxiliary': True,
                        'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                        'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                        'from_pos': f'{pillar_keys[i]}_zhi',
                        'to_pos': f'{pillar_keys[j]}_zhi',
                        'desc': f'{z1}{wx1}生{z2}{wx2}（生扶，非做功）',
                    })
                elif WX_SHENG.get(wx2) == wx1:
                    work_actions.append({
                        'type': '生',
                        'action': '生扶',
                        'auxiliary': True,
                        'from': f'{PILLAR_NAMES_CN[j]}支({z2})',
                        'to': f'{PILLAR_NAMES_CN[i]}支({z1})',
                        'from_pos': f'{pillar_keys[j]}_zhi',
                        'to_pos': f'{pillar_keys[i]}_zhi',
                        'desc': f'{z2}{wx2}生{z1}{wx1}（生扶，非做功）',
                    })

    # ── 墓用 ──
    # 入墓遵循盲派规则：四生入墓、四库之土直接入辰墓、四正/四库见戌多而墓之
    # （天干地支合计数，见 muku.is_entomb）
    # from=墓库(做功方/功神)，to=入墓方(被做功方)
    # 日柱为墓库->主动做功；日柱被入墓->被动受制
    # 闭库之墓不收纳：墓库逢合则闭，闭则不能收物入库（见 muku.analyze_muku）
    # 透干引拔：逢冲无透干亦闭（muku.analyze_muku 据天干透出判定开闭）
    # M4：放开日柱参与限制——非日柱入墓（如李嘉诚亥入辰、蒋介石午入戌）同为
    # 真实墓库关系，一并检出；主被动/宾宾权重由 confirm S2 过滤判定。
    muku_analysis = analyze_muku(zhis, gans)
    closed_tomb_zhis = {t['zhi'] for t in muku_analysis.get('closed_tombs', [])}
    for i in range(4):
        z = zhis[i]
        if not z or z not in TOMB_MAP:
            continue
        if z in closed_tomb_zhis:
            continue  # 闭库之墓不收纳
        for j in range(4):
            if i == j:
                continue
            z2 = zhis[j]
            if not z2:
                continue
            if is_entomb(z2, z, zhis, gans):  # M4：不再要求日柱参与（i==2 or j==2）
                _non_day_tomb = not (i == 2 or j == 2)
                tomb_works.append({
                    'type': '墓用',
                    'action': '墓用',
                    'from': f'{PILLAR_NAMES_CN[i]}支({z})',
                    'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                    'from_pos': f'{pillar_keys[i]}_zhi',
                    'to_pos': f'{pillar_keys[j]}_zhi',
                    'desc': f'{z2}({ZHI_WX.get(z2, "")})入{z}墓'
                            + ('（宾位入墓，不做主功）' if _non_day_tomb else ''),
                    # M4：非日柱入墓检出但标 auxiliary（与 confirm S2 同口径提前）
                    **({'auxiliary': True, 'non_day_tomb': True} if _non_day_tomb else {}),
                })
                work_types.add('墓用')

    # ── 化用前置校准（P0 1：无真实制用目标 + 纯杀印链，与入墓去重）──
    # 段氏化用（杀印相生）为做功仅当命局为纯杀印链--无真实制用目标且无入墓做功时方为
    # 真化用；若命局已有真实制用/墓用做功，则杀印相生为附属之象（命局主功在制/墓，非
    # 化用路径），降为 auxiliary：保留于 work_actions 供 guanming/xiangfa/verify 消费，
    # 但不计入 work_types，故 confirm 阶段 hua_success=False，避免 zuogong 层次因伪化用
    # 虚高至 L4（制例三/合例六/墓例一/复例二）。与墓用去重：有墓用做功时杀印相生同降
    # auxiliary，不与墓用双计。
    # "真实制用"仅指地支之制（冲/穿/刑/破/地支克）且涉日支（主位之制）或墓用；天干克
    # （日干克财/被动受克）力弱且多为制财/受制，不涉日支之宾位破（如午卯破）亦非命局主
    # 功，均不构成真实制用目标，不抑制化用（如壬丙戊乙 戊克壬制财+午卯破，书仍以杀印
    # 相生化用为主功）。
    if '化用' in work_types:
        # "印星化用路径内之制"：涉日支之制（冲/穿/刑/破/克）两端若有一为印星五行
        # （yin_wx），属财冲坏印/印克食伤等印星自身动作或坏印，非独立制用结构，
        # 不抑制化用。仅两端皆非印星之涉日支制用方为独立"真实制用目标"可抑制化用
        # （化例二 丙日坐寅印、申财冲寅坏印+寅印克戌辰，书仍以坐下印化杀为化用主功；
        # 制例三 酉戌穿两端皆非印火，仍为独立制用抑制化用）。
        _yin_wx_hua, _, _ = _day_faction(day_gan, gans, zhis)
        _has_real_zhiyong = any(
            not _wa.get('auxiliary')
            and _wa.get('type') in ('冲', '穿', '刑', '破', '克')
            and ('day_zhi' in _wa.get('from_pos', '')
                 or 'day_zhi' in _wa.get('to_pos', ''))
            and _pos_wx(_wa.get('from_pos', ''), gans, zhis) != _yin_wx_hua
            and _pos_wx(_wa.get('to_pos', ''), gans, zhis) != _yin_wx_hua
            for _wa in work_actions
        )
        # 化用成局（月令司令之印透干=月干为印）为高层功量，化杀为权之力胜于涉日支
        # 之零星制用，不因 _has_real_zhiyong 降级（化例三中堂 己日坐丑、月干丙印化
        # 年/时甲杀，虽寅克丑涉日支制用，主功仍在月干印化杀成局，非争合合用）。坐
        # 下印/时上印力弱，仍依原规则降级。墓用双计去重不受此豁免（墓用主功命非化用）。
        _hua_chengju_yueyin = (bool(gans[1])
                               and GAN_WX.get(gans[1], '') == _yin_wx_hua)
        # 墓用双计去重仅认主功级墓用（非 auxiliary）：auxiliary 墓用=宾位入墓
        # 「不做主功」，不构成命局主功在墓，不抑制化用（化例二 丙日坐寅印化杀，
        # F2 书:3008 戌直接入辰墓后新增宾位墓用曾误降化用为主制用）。
        _has_tomb_main = any(not _tw.get('auxiliary') for _tw in tomb_works)
        if (_has_real_zhiyong and not _hua_chengju_yueyin) or _has_tomb_main:
            for _wa in work_actions:
                if _wa.get('type') == '杀印相生':
                    _wa['auxiliary'] = True
            work_types.discard('化用')

    # ── 日支合中心·食伤不作生用（复例二 副总：丑三种合）──
    # 段氏《段氏理象学》复例二："丑有三种合，这是三种不同的功……论功量只有一层"。
    # 日支若为合中心（涉≥3 合：地支合/暗合/半合），其力尽归于合，所藏食伤不再
    # 以泄秀制杀做生用--否则食伤生用叠加三种合致 type_count 虚高、层次浮夸（书
    # 一层，引擎三层）。合中心之食伤生用降为 auxiliary（不计入 work_types），
    # 主功归合用。仅涉日支之食伤（to_pos=day_zhi）适用，月支食伤不在此列。
    _day_zhi_he_count = sum(
        1 for _wa in work_actions
        if not _wa.get('auxiliary')
        and _wa.get('type') in ('地支合', '暗合', '半合')
        and ('day_zhi' in _wa.get('from_pos', '')
             or 'day_zhi' in _wa.get('to_pos', ''))
    )
    if _day_zhi_he_count >= 3:
        for _wa in work_actions:
            if (_wa.get('type') == '食伤'
                    and _wa.get('to_pos') == 'day_zhi'
                    and not _wa.get('auxiliary')):
                _wa['auxiliary'] = True
                _wa['he_center_skip'] = True
        if not any(_wa.get('type') == '食伤' and not _wa.get('auxiliary')
                   for _wa in work_actions):
            work_types.discard('生用')

    # ── 伏吟（两柱地支相同，日柱参与）──
    # 段氏：伏吟为原地伏滞之象。自刑（辰辰/午午/酉酉/亥亥）已计 type=刑，
    # 此处只对非自刑的同支异柱加 type=伏吟，不与自刑重复。
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or z1 != z2:
                continue
            if not (i == 2 or j == 2):
                continue  # 日柱参与
            if _check_pair(z1, z2, XING_PAIRS):
                continue  # 自刑四支已有 type=刑，不重复加伏吟
            work_actions.append({
                'type': '伏吟',
                'action': '伏吟',
                'auxiliary': True,
                'from': f'{PILLAR_NAMES_CN[i]}支({z1})',
                'to': f'{PILLAR_NAMES_CN[j]}支({z2})',
                'from_pos': f'{pillar_keys[i]}_zhi',
                'to_pos': f'{pillar_keys[j]}_zhi',
                'desc': f'{z1}{z2}伏吟（日柱参与，原地伏滞）',
            })

    # ── 反吟（天克地冲，日柱参与）──
    # 段氏：反吟即天克地冲--两柱天干相克且地支相冲，主动荡反复。
    # 天干相克（WX_KE 任一方向）+ 地支六冲，日柱参与 -> severity=high。
    for i in range(4):
        for j in range(i + 1, 4):
            if not (i == 2 or j == 2):
                continue  # 日柱参与
            g1, g2 = gans[i], gans[j]
            z1, z2 = zhis[i], zhis[j]
            if not g1 or not g2 or not z1 or not z2:
                continue
            if not _check_pair(z1, z2, LIU_CHONG):
                continue  # 须地支相冲
            gw1, gw2 = GAN_WX.get(g1, ''), GAN_WX.get(g2, '')
            if not (WX_KE.get(gw1) == gw2 or WX_KE.get(gw2) == gw1):
                continue  # 须天干相克（天克）
            work_actions.append({
                'type': '反吟',
                'action': '反吟',
                'severity': 'high',
                'auxiliary': True,
                'from': f'{PILLAR_NAMES_CN[i]}({g1}{z1})',
                'to': f'{PILLAR_NAMES_CN[j]}({g2}{z2})',
                'from_pos': f'{pillar_keys[i]}_zhi',
                'to_pos': f'{pillar_keys[j]}_zhi',
                'desc': f'{g1}{z1}与{g2}{z2}天克地冲（反吟，动荡反复）',
            })

    # ── 原始事实数据（长生 / 空亡 / 天干入墓），供 confirm 折扣标注 ──
    # 这些是纯查表事实（与做功判定无关），在检测层一次算出，避免 confirm 重复推算。
    # 日干在某地支上处死/墓/绝 -> 该地支参与做功效率打折（折扣标注由 confirm 完成）
    day_changsheng: Dict[str, str] = {}
    day_weak_zhis: Set[str] = set()
    if day_gan:
        for z in zhis:
            if not z:
                continue
            stage = get_changsheng_mangpai(day_gan, z)
            if stage:
                day_changsheng[z] = stage
                if stage in ('死', '墓', '绝'):
                    day_weak_zhis.add(z)

    # 天干入墓（M4）：天干坐于自身墓库地支 -> 做事能力受限
    # 墓位依 muku.is_gan_entombed（《五行精纪》戊寄戌、己寄辰，严格区分戊/己墓位）
    entombed_gan_pillars: Set[str] = set()
    for i, g in enumerate(gans):
        z = zhis[i]
        if not g or not z:
            continue
        if is_gan_entombed(g, z):
            entombed_gan_pillars.add(pillar_keys[i])

    # 空亡地支集合（段氏：空亡之地做事落空，做功减损；折扣标注由 confirm 完成）
    kong_wang_zhis = _kong_wang_zhis(kong_wang)

    return {
        'work_actions': work_actions,
        'tomb_works': tomb_works,
        'sheng_yong_actions': sheng_yong_actions,
        'day_he_type': day_he_type,
        'san_he_formed': san_he_formed,
        'zheng_he': zheng_he,
        'day_changsheng': day_changsheng,
        'day_weak_zhis': day_weak_zhis,
        'kong_wang_zhis': kong_wang_zhis,
        'entombed_gan_pillars': entombed_gan_pillars,
    }


# ──────────────────────────────────────────────────────────────────────
# 夹局检测（高级篇 2.6 + 6.6）
# ──────────────────────────────────────────────────────────────────────
# 段氏夹局：日主或某一关键字（多为日支），被其左右相邻的两柱地支「夹」住。
#   两夹支五行相同或相生，形成一股针对被夹之字的局部势力（源文 2794-2797）。
#   四形态（源文 2799-2821）：
#     ①夹禄/夹刃——日主之禄神或羊刃被夹；
#     ②夹财/夹官——财星或官星被夹；
#     ③夹库——墓库被夹；
#     ④夹冲/夹合——被夹之字同时受左右两边的冲或合。
#   纯结构检测：产出夹局结构事实（哪两柱夹哪一柱、夹支关系、四形态归类），
#   象意吉凶交 subjective.xiangfa_ops.juxiang 消费。本函数不做吉凶判断。
#
# 夹结构的柱位定义：两夹支 i<j 且 j-i>=2（中间至少夹一柱）；被夹柱 = i、j
#   之间严格居中的柱位集合。可行夹对（四柱）：
#     (year,day)夹month / (year,hour)夹month+day / (month,hour)夹day
#   源文案例：乙巳丙戌辛亥戊戌（月戌+时戌夹日亥）；甲辰癸酉庚辰甲申
#   （年辰+日辰夹月酉）；甲午壬申癸卯甲寅（年甲午+时甲寅夹月日）。

# 夹对（i, j）及其所夹柱位索引列表
_JIA_PAIRS: List[Tuple[int, int, Tuple[int, ...]]] = [
    (0, 2, (1,)),       # 年、日 夹 月
    (0, 3, (1, 2)),     # 年、时 夹 月、日
    (1, 3, (2,)),       # 月、时 夹 日
]


def _chong_pair(a: str, b: str) -> bool:
    return (a, b) in LIU_CHONG or (b, a) in LIU_CHONG


def _he_pair(a: str, b: str) -> bool:
    return (a, b) in LIU_HE or (b, a) in LIU_HE


def detect_jia_ju(
    day_gan: str, day_zhi: str,
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
) -> Dict:
    """纯关系检测：四柱夹局结构（高级篇 2.6 + 6.6）。

    扫描四柱地支，找出「两夹支同五行或相生、中间夹≥1柱」的夹局结构，
    并按被夹之字归类四形态（夹禄/夹刃/夹财/夹官/夹库/夹冲/夹合）。
    纯检测：不判吉凶，吉凶象意交 xiangfa_ops.juxiang。

    Args:
        各柱干支（与 detect_relations 同签名）。

    Returns:
        {'jia_ju': [ {subtype, wrap_pillars, wrapped_pillars, wrap_zhis,
                      wrapped_zhis, relation, chong, he, desc} ... ]}
        relation ∈ {'同五行','相生'}；chong/he 为 bool（被夹字是否同时被两夹支冲/合）。
        subtype ∈ {'夹禄','夹刃','夹财','夹官','夹库','夹冲','夹合','夹局'}。
    """
    gans = [year_gan, month_gan, day_gan, hour_gan]
    zhis = [year_zhi, month_zhi, day_zhi, hour_zhi]
    day_wx = GAN_WX.get(day_gan, '')
    lu_zhi = LU.get(day_gan, '')
    # 夹刃取主刃位（戊=午），不扩至段氏全刃表（戊午未双刃见
    # shensha._YANG_REN_FULL）：夹局为原局做功结构判据，扩刃会改变既有
    # 命例的夹刃检出，保守不扩（M2 注记）。
    ren_zhi = _YANG_REN_MAP.get(day_gan, '')  # 阴干无刃
    # 财五行=我克，官五行=克我
    cai_wx = WX_KE.get(day_wx, '') if day_wx else ''
    guan_wx = WX_KE_ME.get(day_wx, '') if day_wx else ''

    findings: List[Dict] = []

    for i, j, wrapped_idx in _JIA_PAIRS:
        zi, zj = zhis[i], zhis[j]
        if not zi or not zj:
            continue
        wi, wj = ZHI_WX.get(zi, ''), ZHI_WX.get(zj, '')
        if not wi or not wj:
            continue
        # 夹支须同五行或相生（任一方向）
        if wi == wj:
            relation = '同五行'
        elif WX_SHENG.get(wi) == wj or WX_SHENG.get(wj) == wi:
            relation = '相生'
        else:
            continue  # 夹支既不同气亦不相生，不成夹势

        wrapped_zhis = [zhis[k] for k in wrapped_idx if zhis[k]]
        if not wrapped_zhis:
            continue

        # 被夹字是否同时被两夹支冲 / 合（夹冲合形态）
        chong_flag = all(_chong_pair(zi, w) and _chong_pair(zj, w)
                         for w in wrapped_zhis if w)
        he_flag = (not chong_flag) and all(
            _he_pair(zi, w) and _he_pair(zj, w) for w in wrapped_zhis if w
        )

        # 四形态归类（按被夹字属性，优先禄/刃/库/财/官，再冲合，末为普通夹）
        subtype = '夹局'
        for w in wrapped_zhis:
            if lu_zhi and w == lu_zhi:
                subtype = '夹禄'
                break
            if ren_zhi and w == ren_zhi:
                subtype = '夹刃'
                break
            if w in TOMB_MAP:
                subtype = '夹库'
                break
            ww = ZHI_WX.get(w, '')
            if ww and cai_wx and ww == cai_wx:
                subtype = '夹财'
                break
            if ww and guan_wx and ww == guan_wx:
                subtype = '夹官'
                break
        if subtype == '夹局':
            if chong_flag:
                subtype = '夹冲'
            elif he_flag:
                subtype = '夹合'

        wrap_pillar_names = [PILLAR_NAMES_CN[i], PILLAR_NAMES_CN[j]]
        wrapped_pillar_names = [PILLAR_NAMES_CN[k] for k in wrapped_idx]
        desc = (
            f'{wrap_pillar_names[0]}支{zi}、{wrap_pillar_names[1]}支{zj}'
            f'（{relation}）夹{"".join(wrapped_pillar_names)}'
            f'（{"".join(wrapped_zhis)}），{subtype}'
        )
        if chong_flag and subtype not in ('夹冲',):
            desc += '（兼夹冲）'
        if he_flag and subtype not in ('夹合',):
            desc += '（兼夹合）'

        findings.append({
            'subtype': subtype,
            'wrap_pillars': [PILLAR_KEYS[i], PILLAR_KEYS[j]],
            'wrapped_pillars': [PILLAR_KEYS[k] for k in wrapped_idx],
            'wrap_zhis': [zi, zj],
            'wrapped_zhis': wrapped_zhis,
            'relation': relation,
            'chong': chong_flag,
            'he': he_flag,
            'desc': desc,
        })

    return {'jia_ju': findings}
