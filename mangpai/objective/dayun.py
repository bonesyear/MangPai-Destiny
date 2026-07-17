"""
dayun - 盲派大运分析·客观检测层（objective）

理论来源：段建业《段氏理象学》宾主第三层、做功篇
核心思想：
  大运为宾，四柱为主（宾主第三层：四柱为主，大运流年为宾）。
  大运来时：
  1. 大运干支与命局发生冲合穿刑破克生等关系--看大运来做什么
  2. 大运激活命局废神->新做功（废神遇运而动）
  3. 大运冲开墓库->墓中之物可用；合闭墓库->墓中之物被困
  4. 大运改变全局气势->可能逆转正反局
  5. 大运到禄位->禄做功；到羊刃->刃应期
  6. 大运天干十神->看带来什么（财/官/印/食伤/比劫）
  7. 大运地支带长生位->看日主在该运的状态

分层说明（objective/subjective 重构）：
  本模块只做"纯关系检测"与确定性分类：检测大运干支与本命的冲合穿刑破克生、
  墓库开闭、废神激活、气势变化、禄刃、长生、空亡、十神定位。不做吉凶信号/overall/
  desc 等解释性判断--那部分已迁至 subjective.dayun.judge_pillar_signals。
  analyze_dayun_mangpai（含吉凶汇总）亦迁至 subjective.dayun。
置信度：中（检测本身确定性；吉凶判断见 subjective 层）
"""
from typing import Dict, List, Optional, Any

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    TIAN_GAN_HE, LIU_CHONG, LIU_HE, LIU_HAI, LIU_PO,
    XING_PAIRS, AN_HE, SAN_HE, BAN_HE,
    TOMB_MAP, LU, PILLAR_KEYS, PILLAR_NAMES_CN,
    SI_SHENG, SI_ZHENG, DI_ZHI,
)
from mangpai.objective.changsheng import get_changsheng_mangpai
from mangpai.objective.muku import TOMB_MAP as _TOMB_MAP
from mangpai.objective.shensha import _YANG_REN_FULL

_YANG_GANS = set('甲丙戊庚壬')

# 阳干羊刃位单一事实源：objective.shensha._YANG_REN_FULL（段氏《理象学》
# 「戊刃在午、未」双刃口径；此前本模块自带双刃副本、 shensha 仅取午，两处
# 口径冲突，M2 统一为 shensha 全刃表）。
_YANG_REN: Dict[str, List[str]] = _YANG_REN_FULL

_PILLAR_LABELS = ['年柱', '月柱', '日柱', '时柱']


def _compute_shishen(day_gan: str, gan: str) -> str:
    """计算 gan 相对 day_gan 的十神。"""
    day_wx = GAN_WX.get(day_gan, '')
    gan_wx = GAN_WX.get(gan, '')
    if not day_wx or not gan_wx:
        return ''
    same_polarity = (day_gan in _YANG_GANS) == (gan in _YANG_GANS)
    if gan_wx == day_wx:
        return '比肩' if same_polarity else '劫财'
    if WX_SHENG.get(day_wx) == gan_wx:
        return '食神' if same_polarity else '伤官'
    if WX_SHENG.get(gan_wx) == day_wx:
        return '偏印' if same_polarity else '正印'
    if WX_KE.get(day_wx) == gan_wx:
        return '偏财' if same_polarity else '正财'
    if WX_KE.get(gan_wx) == day_wx:
        return '七杀' if same_polarity else '正官'
    return ''


def _check_pair(a: str, b: str, pairs) -> bool:
    return (a, b) in pairs or (b, a) in pairs


def _analyze_gan_relations(
    dy_gan: str,
    natal_gans: List[str],
    day_gan: str,
    month_zhi: str = '',
) -> List[Dict]:
    """分析大运天干与命局天干的关系。

    日干（i==2 的日主自身）跳过：运干与日主的十神定位由 tiyong_import 专管，
    运干合/克日主不再入 relations（此前此处为死 pass，过滤从未生效——M2 修复）。
    month_zhi 用于天干合化气的月令验证（见 _check_hua）。
    """
    relations: List[Dict] = []
    dy_wx = GAN_WX.get(dy_gan, '')

    for i, ng in enumerate(natal_gans):
        if not ng or (ng == day_gan and i == 2):
            continue

        ng_wx = GAN_WX.get(ng, '')

        if TIAN_GAN_HE.get(dy_gan) == ng:
            he_wx = _check_hua(dy_gan, ng, month_zhi)
            relations.append({
                'type': '天干合',
                'target': ng,
                'target_pos': f'{PILLAR_KEYS[i]}_gan',
                'target_pillar': _PILLAR_LABELS[i],
                'hua': he_wx,
                'desc': f'大运{dy_gan}合{ng}（{_PILLAR_LABELS[i]}）' + (f'化{he_wx}' if he_wx else ''),
            })
        elif dy_wx and ng_wx and WX_KE.get(dy_wx) == ng_wx and TIAN_GAN_HE.get(dy_gan) != ng:
            relations.append({
                'type': '天干克',
                'target': ng,
                'target_pos': f'{PILLAR_KEYS[i]}_gan',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_gan}({dy_wx})克{ng}({ng_wx})（{_PILLAR_LABELS[i]}）',
            })
        elif dy_wx and ng_wx and WX_KE.get(ng_wx) == dy_wx and TIAN_GAN_HE.get(dy_gan) != ng:
            relations.append({
                'type': '天干被克',
                'target': ng,
                'target_pos': f'{PILLAR_KEYS[i]}_gan',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_gan}({dy_wx})被{ng}({ng_wx})克（{_PILLAR_LABELS[i]}）',
            })

    return relations


def _check_hua(a: str, b: str, month_zhi: str = '') -> str:
    """检查天干合是否能化（验月令：化气五行须当令方论化）。

    与 zuogong_detect 原局合化 gate 同口径：月令主气五行 == 化气五行，方标
    化气；否则合而不化（返回 ''）。month_zhi 缺省时保守不标化（旧行为不验
    月令直接标化气，属口径缺陷——M2 修复）。
    """
    from mangpai.objective.constants import HUA_YONG_MAP
    hua_wx = HUA_YONG_MAP.get((a, b), '')
    if not hua_wx or not month_zhi:
        return ''
    return hua_wx if ZHI_WX.get(month_zhi, '') == hua_wx else ''


def _analyze_zhi_relations(
    dy_zhi: str,
    natal_zhis: List[str],
) -> List[Dict]:
    """分析大运地支与命局地支的关系。"""
    relations: List[Dict] = []

    for i, nz in enumerate(natal_zhis):
        if not nz:
            continue

        if _check_pair(dy_zhi, nz, LIU_CHONG):
            relations.append({
                'type': '冲',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_zhi}冲{nz}（{_PILLAR_LABELS[i]}）',
            })

        if _check_pair(dy_zhi, nz, LIU_HE):
            he_type = _classify_he(dy_zhi, nz)
            relations.append({
                'type': '六合',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'he_type': he_type,
                'desc': f'大运{dy_zhi}合{nz}（{_PILLAR_LABELS[i]}，{he_type}）',
            })

        if _check_pair(dy_zhi, nz, LIU_HAI):
            relations.append({
                'type': '穿',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_zhi}穿{nz}（{_PILLAR_LABELS[i]}）',
            })

        if _check_pair(dy_zhi, nz, XING_PAIRS):
            is_zi_xing = dy_zhi == nz
            relations.append({
                'type': '刑',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_zhi}刑{nz}（{_PILLAR_LABELS[i]}）' + ('（自刑）' if is_zi_xing else ''),
            })

        if _check_pair(dy_zhi, nz, LIU_PO):
            relations.append({
                'type': '破',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_zhi}破{nz}（{_PILLAR_LABELS[i]}）',
            })

        if AN_HE.get(dy_zhi) == nz:
            relations.append({
                'type': '暗合',
                'target': nz,
                'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                'target_pillar': _PILLAR_LABELS[i],
                'desc': f'大运{dy_zhi}暗合{nz}（{_PILLAR_LABELS[i]}）',
            })

    dy_wx = ZHI_WX.get(dy_zhi, '')
    for i, nz in enumerate(natal_zhis):
        if not nz:
            continue
        nz_wx = ZHI_WX.get(nz, '')
        if dy_wx and nz_wx:
            if WX_KE.get(dy_wx) == nz_wx:
                existing = any(r['type'] == '克' and r['target'] == nz for r in relations)
                if not existing:
                    relations.append({
                        'type': '克',
                        'target': nz,
                        'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                        'target_pillar': _PILLAR_LABELS[i],
                        'desc': f'大运{dy_zhi}({dy_wx})克{nz}({nz_wx})（{_PILLAR_LABELS[i]}）',
                    })
            elif WX_SHENG.get(dy_wx) == nz_wx:
                existing = any(r['type'] == '生' and r['target'] == nz for r in relations)
                if not existing:
                    relations.append({
                        'type': '生',
                        'target': nz,
                        'target_pos': f'{PILLAR_KEYS[i]}_zhi',
                        'target_pillar': _PILLAR_LABELS[i],
                        'desc': f'大运{dy_zhi}({dy_wx})生{nz}({nz_wx})（{_PILLAR_LABELS[i]}）',
                    })

    for combo, wx in SAN_HE.items():
        if dy_zhi in combo:
            present = [z for z in natal_zhis if z and z in combo and z != dy_zhi]
            if len(present) >= 1:
                missing = [z for z in combo if z != dy_zhi and z not in present]
                # 成局：命局凑齐 combo 余下全部成员（dy + len(combo)-1 字）；
                # 三合即 dy+2 字、四库会即 dy+3 字；不足则半合
                formed = len(present) >= len(combo) - 1
                relations.append({
                    'type': '三合局' if formed else '半合',
                    'target': '、'.join(present),
                    'target_pos': '',
                    'target_pillar': '、'.join(_PILLAR_LABELS[i] for i, z in enumerate(natal_zhis) if z in present),
                    'combo': combo,
                    'wuxing': wx,
                    'completed': formed,
                    'desc': f'大运{dy_zhi}与{"、".join(present)}{"成" if formed else "半"}{wx}局'
                            + (f'（缺{missing[0]}）' if not formed and missing else ''),
                })

    return relations


def _classify_he(a: str, b: str) -> str:
    """分类六合类型（合绊/合克/合伤/闭气）。"""
    from mangpai.objective.constants import BI_QI
    a_wx = ZHI_WX.get(a, '')
    b_wx = ZHI_WX.get(b, '')

    key = f'{a}{b}' if f'{a}{b}' in BI_QI else f'{b}{a}'
    if key in BI_QI:
        return f'闭气（闭{BI_QI[key]["闭气"]}）'

    if a_wx and b_wx:
        if WX_KE.get(a_wx) == b_wx:
            return '合克'
        if WX_KE.get(b_wx) == a_wx:
            return '合受克'

    return '合绊'


def _analyze_tomb_effect(
    dy_zhi: str,
    natal_zhis: List[str],
    natal_gans: List[str],
    extra_gans: Optional[List[str]] = None,
) -> Optional[Dict]:
    """分析大运/流年支对命局墓库的开闭效应。

    extra_gans：透干引拔的额外天干（如流年干）。墓库所收五行若由流年干透出，
    亦当引拔（段氏墓库篇「透干引拔」）。默认 None，仅以本命天干透干引拔，
    保持大运分析既有行为。
    """
    dy_wx = ZHI_WX.get(dy_zhi, '')

    opens: List[Dict] = []
    closes: List[Dict] = []

    for i, nz in enumerate(natal_zhis):
        if not nz or nz not in TOMB_MAP:
            continue

        elements = TOMB_MAP[nz]

        # 开库触发：冲/刑皆触动墓库（段氏「不冲不刑是墓（死的）」），与
        # objective.muku 同口径；同一对可既冲又刑（如丑未），合并去重。
        # 运支与库支相同（伏吟到位/自刑）非开库触发，不计刑。
        open_kinds: List[str] = []
        if _check_pair(dy_zhi, nz, LIU_CHONG):
            open_kinds.append('冲')
        if dy_zhi != nz and _check_pair(dy_zhi, nz, XING_PAIRS):
            open_kinds.append('刑')

        if open_kinds:
            # 透干引拔：墓库逢冲/刑须天干透出所收五行方为真开，无透干则虽
            # 冲/刑亦闭（盲师口传墓库体系，与 muku.analyze_muku 同口径——
            # 旧版「冲即开库，透干仅增强」与之冲突，M2 统一为冲/刑+透干才开）。
            tou_gan_wx = {GAN_WX.get(g, '') for g in natal_gans if g}
            if extra_gans:
                tou_gan_wx |= {GAN_WX.get(g, '') for g in extra_gans if g}
            touched = [e for e in elements if e in tou_gan_wx]
            kind_str = '、'.join(open_kinds)
            if touched:
                opens.append({
                    'tomb_zhi': nz,
                    'pillar': _PILLAR_LABELS[i],
                    'elements': elements,
                    'tou_gan': touched,
                    'open_kind': kind_str,
                    'desc': f'大运{dy_zhi}{kind_str}开{nz}墓库（{_PILLAR_LABELS[i]}），'
                            f'{"、".join(touched)}透干引拔而开',
                })
            else:
                closes.append({
                    'tomb_zhi': nz,
                    'pillar': _PILLAR_LABELS[i],
                    'elements': elements,
                    'tou_gan': [],
                    'open_kind': kind_str,
                    'desc': f'大运{dy_zhi}{kind_str}{nz}墓库（{_PILLAR_LABELS[i]}），'
                            f'无透干引拔，闭而不开',
                })

        if _check_pair(dy_zhi, nz, LIU_HE):
            closes.append({
                'tomb_zhi': nz,
                'pillar': _PILLAR_LABELS[i],
                'elements': elements,
                'desc': f'大运{dy_zhi}合闭{nz}墓库（{_PILLAR_LABELS[i]}）',
            })

    if not opens and not closes:
        return None

    return {
        'opens': opens,
        'closes': closes,
    }


def _analyze_fei_shen_activation(
    dy_gan: str,
    dy_zhi: str,
    natal_fei_shen: List[str],
    natal_gans: List[str],
    natal_zhis: List[str],
) -> List[Dict]:
    """分析大运是否激活命局废神。"""
    activated: List[Dict] = []
    gan_wx = GAN_WX.get(dy_gan, '')
    zhi_wx = ZHI_WX.get(dy_zhi, '')

    for pos in natal_fei_shen:
        if not pos or '_' not in pos:
            continue
        pk, pt = pos.split('_', 1)
        if pk not in PILLAR_KEYS:
            continue
        idx = PILLAR_KEYS.index(pk)

        target = ''
        target_wx = ''
        if pt == 'gan' and idx < len(natal_gans):
            target = natal_gans[idx]
            target_wx = GAN_WX.get(target, '')
        elif pt == 'zhi' and idx < len(natal_zhis):
            target = natal_zhis[idx]
            target_wx = ZHI_WX.get(target, '')

        if not target:
            continue

        reasons: List[str] = []

        if pt == 'gan':
            if TIAN_GAN_HE.get(dy_gan) == target:
                reasons.append(f'{dy_gan}合{target}')
            if gan_wx and target_wx:
                if WX_KE.get(gan_wx) == target_wx:
                    reasons.append(f'{dy_gan}克{target}')
                if WX_KE.get(target_wx) == gan_wx:
                    reasons.append(f'{target}克{dy_gan}')
        elif pt == 'zhi':
            if _check_pair(dy_zhi, target, LIU_CHONG):
                reasons.append(f'{dy_zhi}冲{target}')
            if _check_pair(dy_zhi, target, LIU_HE):
                reasons.append(f'{dy_zhi}合{target}')
            if _check_pair(dy_zhi, target, LIU_HAI):
                reasons.append(f'{dy_zhi}穿{target}')
            if AN_HE.get(dy_zhi) == target:
                reasons.append(f'{dy_zhi}暗合{target}')
            if _check_pair(dy_zhi, target, XING_PAIRS):
                reasons.append(f'{dy_zhi}刑{target}')
            if _check_pair(dy_zhi, target, LIU_PO):
                reasons.append(f'{dy_zhi}破{target}')

        if reasons:
            activated.append({
                'position': pos,
                'pillar': _PILLAR_LABELS[idx],
                'target': target,
                'type': pt,
                'reasons': reasons,
                'desc': f'大运激活废神{_PILLAR_LABELS[idx]}{target}（{"、".join(reasons)}）',
            })

    return activated


def _analyze_tiyong_import(
    dy_gan: str,
    day_gan: str,
) -> Dict:
    """分析大运天干引入的体用。"""
    ss = _compute_shishen(day_gan, dy_gan)
    if not ss:
        return {'shishen': '', 'category': '未知', 'desc': ''}

    ti_shishen = {'正印', '偏印', '比肩', '劫财', '食神', '伤官'}
    yong_shishen = {'正财', '偏财', '正官', '七杀'}

    if ss in ti_shishen:
        category = '体'
    elif ss in yong_shishen:
        category = '用'
    else:
        category = '未知'

    desc_map = {
        '正财': '正财运（正当收入、妻子）',
        '偏财': '偏财运（意外之财、父亲）',
        '正官': '正官运（事业、地位、丈夫）',
        '七杀': '七杀运（压力、权力、灾祸）',
        '正印': '正印运（学业、长辈、保护）',
        '偏印': '偏印运（偏门学问、孤独）',
        '比肩': '比肩运（朋友、竞争、破财）',
        '劫财': '劫财运（争夺、破财、合作）',
        '食神': '食神运（才华、福寿、子女）',
        '伤官': '伤官运（才能、叛逆、官非）',
    }

    return {
        'shishen': ss,
        'category': category,
        'desc': desc_map.get(ss, ss),
    }


def _analyze_qishi_change(
    dy_gan: str,
    dy_zhi: str,
    natal_gans: List[str],
    natal_zhis: List[str],
) -> Optional[Dict]:
    """分析大运对全局气势的影响。"""
    counts: Dict[str, int] = {wx: 0 for wx in ['木', '火', '土', '金', '水']}

    for g in natal_gans:
        if g in GAN_WX:
            counts[GAN_WX[g]] += 1
    for z in natal_zhis:
        if z in ZHI_WX:
            counts[ZHI_WX[z]] += 1

    natal_total = sum(counts.values())
    natal_ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    natal_top = natal_ranked[0] if natal_ranked else ('', 0)

    dy_gan_wx = GAN_WX.get(dy_gan, '')
    dy_zhi_wx = ZHI_WX.get(dy_zhi, '')
    if dy_gan_wx:
        counts[dy_gan_wx] += 1
    if dy_zhi_wx:
        counts[dy_zhi_wx] += 1

    new_total = sum(counts.values())
    new_ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    new_top = new_ranked[0] if new_ranked else ('', 0)

    if natal_top[1] >= 4 and new_top[0] == natal_top[0]:
        return None

    if new_top[1] >= 4 and new_top[0] != natal_top[0]:
        return {
            'changed': True,
            'natal_dominant': natal_top[0],
            'new_dominant': new_top[0],
            'desc': f'大运加入{dy_gan_wx}、{dy_zhi_wx}，{new_top[0]}旺成势（原{natal_top[0]}为主）',
        }

    if natal_top[1] < 4 and new_top[1] >= 4:
        return {
            'changed': True,
            'natal_dominant': natal_top[0],
            'new_dominant': new_top[0],
            'desc': f'大运加入后{new_top[0]}达半数成势',
        }

    return None


def _analyze_lu_blade(
    dy_zhi: str,
    day_gan: str,
) -> Optional[Dict]:
    """分析大运是否到禄/刃位。"""
    lu = LU.get(day_gan, '')
    if dy_zhi == lu:
        return {
            'type': '禄',
            'desc': f'大运到禄位{dy_zhi}（{day_gan}禄在{lu}）',
        }

    if day_gan in _YANG_GANS:
        blades = _YANG_REN.get(day_gan, [])
        if dy_zhi in blades:
            return {
                'type': '羊刃',
                'desc': f'大运到羊刃位{dy_zhi}（{day_gan}刃在{"、".join(blades)}）',
            }

    return None


def _analyze_changsheng(
    dy_zhi: str,
    day_gan: str,
) -> Dict:
    """分析日主在大运地支的长生位。"""
    stage = get_changsheng_mangpai(day_gan, dy_zhi)
    if not stage:
        return {'stage': '', 'desc': ''}

    stage_desc = {
        '长生': '如初生之木，生机勃发',
        '沐浴': '如初生沐浴，稚嫩多变',
        '冠带': '如冠带成人，渐趋成熟',
        '临官': '如临官位，精力旺盛',
        '帝旺': '如帝旺极盛，气势最足',
        '衰': '如气衰渐退，力不从心',
        '病': '如病弱无力，多阻碍',
        '死': '如死地无气，做事无力',
        '墓': '如入墓困顿，才能受困',
        '绝': '如绝地无根，百事难成',
        '胎': '如胎养孕育，蓄势待发',
        '养': '如养地培育，渐有起色',
    }

    # 段氏：长生位地支五行克日干者为「相克弱长生」（如金长生在巳，巳火克金），
    # 虽名长生，实受克而气弱，不作气旺论。
    weak = False
    if stage == '长生':
        day_wx = GAN_WX.get(day_gan, '')
        zhi_wx = ZHI_WX.get(dy_zhi, '')
        weak = bool(day_wx and zhi_wx and WX_KE.get(zhi_wx) == day_wx)

    result = {
        'stage': stage,
        'desc': f'日主{day_gan}在大运{dy_zhi}为{stage}位',
        'detail': stage_desc.get(stage, ''),
    }
    if weak:
        result['weak'] = True
    return result


def _check_kong_wang(
    dy_zhi: str,
    kong_wang: Any,
) -> bool:
    """检查大运地支是否空亡。"""
    if not kong_wang:
        return False
    if isinstance(kong_wang, list):
        return dy_zhi in kong_wang
    if isinstance(kong_wang, dict):
        zhis = kong_wang.get('zhi', kong_wang.get('zhis', []))
        return dy_zhi in zhis
    return False


def _analyze_pillar_interaction(
    pillar_gan: str,
    pillar_zhi: str,
    natal_gans: List[str],
    natal_zhis: List[str],
    day_gan: str,
    natal_fei_shen: Optional[List[str]] = None,
    kong_wang: Any = None,
    tomb_extra_gans: Optional[List[str]] = None,
) -> Dict:
    """分析单个外部柱（大运/流年）与本命的互动--纯检测层。

    只产出关系检测/确定性分类事实（冲合穿刑破克生、墓库开闭、废神激活、
    气势变化、禄刃、长生、空亡、十神定位、work_types）。吉凶信号/overall/
    desc 等解释性判断由 subjective.dayun.judge_pillar_signals 消费本结果产出。

    tomb_extra_gans：透干引拔的额外天干（如流年干），纳入墓库开库引拔判定；
    默认 None 保持大运分析既有行为（仅本命天干透干引拔）。
    """
    gan_relations = _analyze_gan_relations(
        pillar_gan, natal_gans, day_gan,
        month_zhi=(natal_zhis[1] if len(natal_zhis) > 1 else ''),
    )
    zhi_relations = _analyze_zhi_relations(pillar_zhi, natal_zhis)
    tomb_effect = _analyze_tomb_effect(pillar_zhi, natal_zhis, natal_gans, tomb_extra_gans)
    tiyong = _analyze_tiyong_import(pillar_gan, day_gan)
    qishi_change = _analyze_qishi_change(pillar_gan, pillar_zhi, natal_gans, natal_zhis)
    lu_blade = _analyze_lu_blade(pillar_zhi, day_gan)
    changsheng = _analyze_changsheng(pillar_zhi, day_gan)
    is_kong = _check_kong_wang(pillar_zhi, kong_wang)

    fei_shen_activated: List[Dict] = []
    if natal_fei_shen:
        fei_shen_activated = _analyze_fei_shen_activation(
            pillar_gan, pillar_zhi, natal_fei_shen, natal_gans, natal_zhis,
        )

    all_relations = gan_relations + zhi_relations
    has_chong = any(r['type'] == '冲' for r in zhi_relations)
    has_he = any(r['type'] in ('六合', '天干合') for r in all_relations)
    has_chuan = any(r['type'] == '穿' for r in zhi_relations)
    has_xing = any(r['type'] == '刑' for r in zhi_relations)
    has_anhe = any(r['type'] == '暗合' for r in zhi_relations)

    work_types: List[str] = []
    if any(r['type'] in ('冲', '穿', '刑', '破', '克', '天干克', '天干被克') for r in all_relations):
        work_types.append('制用')
    if has_he or has_anhe:
        work_types.append('合用')
    if tomb_effect and tomb_effect.get('opens'):
        work_types.append('墓用（开库）')
    if tiyong.get('category') == '体' and tiyong.get('shishen') in ('食神', '伤官'):
        work_types.append('生用')

    return {
        'gan': pillar_gan,
        'zhi': pillar_zhi,
        'gz': f'{pillar_gan}{pillar_zhi}',
        'gan_shishen': tiyong.get('shishen', ''),
        'gan_relations': gan_relations,
        'zhi_relations': zhi_relations,
        'tomb_effect': tomb_effect,
        'fei_shen_activated': fei_shen_activated,
        'tiyong_import': tiyong,
        'qishi_change': qishi_change,
        'lu_blade': lu_blade,
        'changsheng': changsheng,
        'is_kong_wang': is_kong,
        'work_types': work_types,
        # has_* 为检测派生布尔，供主观层 judge 复用（避免重复扫描 relations）
        'has_chong': has_chong,
        'has_he': has_he,
        'has_chuan': has_chuan,
        'has_xing': has_xing,
        'has_anhe': has_anhe,
    }


__all__ = ['_analyze_pillar_interaction']
