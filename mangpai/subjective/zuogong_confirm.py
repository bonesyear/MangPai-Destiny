"""
zuogong_confirm - 盲派做功引擎·做功成立确认层（subjective）

理论来源：段建业《段氏理象学》做功篇
核心思想：做功是盲派分析命局的核心。日柱通过制、合、墓、生、化五种方式
          对其他柱做功，做功的效率和层次决定命局格局高低。
  制用：克、冲、刑、破、穿
  合用：六合、天干五合、暗合、半合、合化（天干五合化气，原误作化用，已归入合用）
  墓用：入墓（制住入墓）
  生用：食伤泄秀（日干生出食神/伤官，食伤再生财或制杀方为做功）
  化用：杀印相生（官杀->印->日主链，化杀为印、化印为身方为做功）
  成势：三合局成势做功
做功优先级链（盲派铁律，级联判定主做功）：
  1. 日干合（合官/合财）-> 有则以合为主做功
  2. 日干生（食伤泄秀）-> 有则以生出之食伤做功为主
  2a. 化用（杀印相生）-> 纯杀印链命局以化杀为印做功为主（化用成局高层功量）
  3. 弃干看支（日支的刑冲破害墓）
  4. 日干支都不做功 -> 看禄/比劫
党势铁律（段氏）：须一方成党势、强方制弱方才算功。日柱所在方党羽数不足
  （孤身无党）者，其制用做功无力，降为辅助（auxiliary）。

分层说明（objective/subjective 重构）：
  本模块为"解释性判断"层：消费 objective.zuogong_detect 的纯关系检测结果，
  做党势强弱判定、做功成立确认、primary_work 优先级链、做功效率/层次/主被动
  评估。assess_work_level（做功层次 0-5 评估）亦属解释性判断，故由原
  objective/work_level 合并至此。判断含置信度（中）。
  依赖方向单向：subjective -> objective（本模块只 import objective，不反向）。
已知争议：做功的判定条件和范围、层次划分标准各盲师有不同，本模块采用类型
          数量+结构+主被动+方向综合判定
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.zuogong_detect import detect_relations, _day_faction
from mangpai.objective.gongfei import classify_gongshen
from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG, LU,
    PILLAR_NAMES_CN, PILLAR_KEYS, is_pillars,
    EFFICIENCY_HIGH_ACTION_COUNT, EFFICIENCY_HIGH_TYPE_COUNT,
    EFFICIENCY_MID_ACTION_COUNT,
)
from mangpai.objective.binzhu import analyze_binzhu
from mangpai.objective.tiyong import classify_tiyong
from mangpai.objective.wood_type import analyze_wood_type
from mangpai.objective.soil_type import analyze_soil
from mangpai.objective.virtual_solid import analyze_virtual_solid

# ── 做功层次评估（原 objective/work_level，解释性判断，置信度中）──
# Level 0: 无功（废神多，需看大运激发）
# Level 1: 单层做功（单一类型/单一路径）
# Level 2: 双层做功（多类型叠加，效率较高）
# Level 3: 叠加功量（三类型以上或包围制等高效率结构）
# Level 4: 化用成局或制局（化用成功 + 多类型叠加≥3）
# Level 5: 连珠做功或全局成势做功（三合局成势 + 功神占比>70%）
# 主动做功多->格局加分；被动受制多->格局减分
# 被动合/被动生不减分（财来合我、印来生我可为吉）
# 反向做功（用在主位制体在宾位）效率高，但段氏无明确加成依据，
# 仅在描述中加注"含反向做功"作参考信号，不直接调整层次
_TIER_MAP = {
    0: '无功',
    1: '单层做功',
    2: '双层做功',
    3: '叠加功量',
    4: '化用成局',
    5: '连珠成势',
}


def assess_work_level(
    work_types: List[str],
    work_actions: List[Dict],
    tomb_works_count: int,
    day_he_type: Optional[str],
    active_work_count: int = 0,
    passive_work_count: int = 0,
    passive_control_count: int = 0,
    hua_success: bool = False,
    san_he_formed: bool = False,
    gong_shen_ratio: float = 0.0,
    reverse_work_count: int = 0,
    efficiency_discount_count: int = 0,
    chengshi_primary: bool = False,
) -> Dict:
    """评估做功层次。

    Args:
        work_types: 做功类型列表（制用/合用/墓用/生用/化用/成势）
        work_actions: 做功动作列表
        tomb_works_count: 墓用做功数量
        day_he_type: 日干合类型
        active_work_count: 日柱主动做功数量（from_pos 以 day_ 开头）
        passive_work_count: 日柱被动被做功数量（to_pos 以 day_ 开头）
        passive_control_count: 日柱被动受制数量（被克/冲/穿/刑/破/入墓）
        hua_success: 天干合化是否成功（化用成局条件之一）
        san_he_formed: 是否三合局成势（连珠成势条件之一）
        gong_shen_ratio: 功神占全部干支的比例（0-1）
        reverse_work_count: 反向做功数量（用在主位制体在宾位）；仅作参考信号加注，不调整 level
        efficiency_discount_count: 因长生/天干入墓而效率打折的动作数
        chengshi_primary: 主做功是否为成势（三合局做功为主）。连珠成势(L5)须成势本身
            为命局主功方成立--三合局仅为 incidental 之命（主功在制/合/生）不升至 L5，
            避免层次虚高（制例二 寅午戌火局成势但主功在寅克丑戌之制用，非连珠成势）

    Returns:
        {'level': int, 'desc': str, 'tier': str,
         'has_severe_harm': bool, 'has_active_harm': bool}
    """
    if not work_types:
        return {
            'level': 0,
            'tier': '无功',
            'desc': '无功（废神多，需看大运激发）',
            'has_severe_harm': False,
            'has_active_harm': False,
        }

    type_count = len(work_types)

    # ── 穿的区分（段建业《段氏理象学》穿篇）──
    # 盲派认为穿比冲更凶，"穿坏即灾"。但穿有方向性区分：
    # 被动穿（别人穿我，to_pos含day）-> 严重损害日柱做功质量
    # 主动穿（我穿别人，from_pos含day）-> 仍属制用做功，但穿为暗伤，
    #   不如冲/克效率高，做功有暗损（段氏："穿是暗中破坏，虽制犹伤"）
    # 非日柱穿 -> 不直接影响日柱做功
    has_severe_harm = any(
        wa.get('type') == '穿'
        and wa.get('severity') == 'high'
        and wa.get('to_pos', '').startswith('day_')
        for wa in work_actions
    )
    has_active_harm = any(
        wa.get('type') == '穿'
        and wa.get('severity') == 'high'
        and wa.get('from_pos', '').startswith('day_')
        for wa in work_actions
    )
    if has_severe_harm:
        harm_note = '（日柱被穿，做功质量严重受损）'
    elif has_active_harm:
        harm_note = '（日柱穿他柱，做功有暗损）'
    else:
        harm_note = ''

    # ── 基础层次（按类型数量+结构判定）──
    # 阈值经微调：Level 3 不只看类型数，也认可"双类型 + 强主动"等高效率结构，
    # 避免所有命局堆在 1-2 层。Level 4/5 为特殊层次，须满足专门条件方可达到。
    if san_he_formed and gong_shen_ratio > 0.7 and chengshi_primary:
        base_level = 5
        base_desc = '三合局成势且功神占比>70%，连珠成势做功，层次极高'
    elif hua_success and type_count >= 3:
        base_level = 4
        base_desc = '化用成局且多类型叠加（化用+' + '+'.join(work_types) + '），层次甚高'
    elif type_count >= 3:
        base_level = 3
        base_desc = f'三类型以上做功（{"+".join(work_types)}），叠加功量，效率极高'
    elif type_count >= 2 and active_work_count >= 3:
        base_level = 3
        base_desc = f'多类型做功（{"+".join(work_types)}）且日柱强主动，叠加功量'
    elif type_count >= 2:
        base_level = 2
        base_desc = f'多类型做功（{"+".join(work_types)}），效率较高'
    elif tomb_works_count >= 2:
        base_level = 1
        base_desc = '墓用做功，层次中等'
    elif day_he_type:
        base_level = 1
        base_desc = f'日干{day_he_type}做功，层次因合局完整度而异'
    else:
        base_level = 1
        base_desc = '单一类型做功，层次普通'

    # ── 主动/被动/反向做功调整 ──
    # 主动做功多->格局加分（我取外物）
    # 被动受制多->格局减分（被克/冲/穿/刑/破/入墓）
    # 被动合/被动生不减分（财来合我、印来生我可为吉）
    # 反向做功（用在主位制体在宾位）效率高，但段氏无"反向做功->层次+1"的明确依据，
    # 故不直接调整 level，仅在描述中加注"含反向做功"作为参考信号。
    # 注：效率加成/减损仅在 0-3 常规 band 内生效；Level 4/5 为特殊层次（化用成局/连珠成势），
    # 须由专门条件达到，效率加成不再上推，以保证层次标签与达成路径一致。
    level = base_level
    direction_note = ''
    passive_benefit_count = passive_work_count - passive_control_count
    if level < 4:
        if active_work_count >= 2 and active_work_count > passive_control_count:
            level = min(level + 1, 3)
            direction_note = '，主动做功为主，格局加成'
        elif passive_control_count >= 2 and passive_control_count > active_work_count:
            level = max(level - 1, 0)
            direction_note = '，被动受制为主，格局减损'
        elif passive_benefit_count >= 2:
            direction_note = '，被动合/生为主（财来合我、印来生我），为吉象'
        # 长生/天干入墓折扣动作过多（≥非辅助做功半数）-> 层次降一级
        # 效率减损仅在 0-3 常规 band 内生效，不波及 Level 4/5 特殊层次
        if (efficiency_discount_count > 0 and work_actions
                and efficiency_discount_count * 2 >= len(work_actions)):
            level = max(0, level - 1)
            disc_note = '，做功折扣多，效率减损'
            direction_note = (direction_note + disc_note) if direction_note else disc_note
    # 反向做功：仅作参考信号加注，不调整 level（段氏无明确加成依据）
    if reverse_work_count >= 1:
        rev_note = f'，含反向做功{reverse_work_count}项(参考信号)'
        direction_note = (direction_note + rev_note) if direction_note else rev_note

    tier = _TIER_MAP[level]

    return {
        'level': level,
        'tier': tier,
        'desc': f'{base_desc}{harm_note}{direction_note}',
        'has_severe_harm': has_severe_harm,
        'has_active_harm': has_active_harm,
    }


# ── 做功成立确认（原 objective/zuogong 的 confirm 层）──
# 主位（体之位）：日柱 + 时柱；宾位（用之位）：年柱 + 月柱
_ZHU_PILLARS = {'day', 'hour'}
# 被动受制类型（计入 passive_control，格局减分）
_PASSIVE_CONTROL_TYPES = {'冲', '克', '穿', '刑', '破', '墓用'}
# 做功动作 type -> 做功方式 label（work_types 集合元素）。
# work_types 仅从非辅助动作提取（见 analyze_zuogong 末尾），S1 去重/S2 降级
# 动作虽在建阶段 add 了 label，最终以 non_aux 重算为准，避免 type_count 虚高。
_WORK_TYPE_LABEL = {
    '冲': '制用', '克': '制用', '穿': '制用', '刑': '制用', '破': '制用',
    '天干合': '合用', '地支合': '合用', '暗合': '合用', '半合': '合用',
    '合化': '合用',
    '杀印相生': '化用',
    '食伤': '生用',
    '三合局': '成势',
    '墓用': '墓用',
    '禄': '禄',
}
# 党势阈值：日柱所在方须至少有 N 个党羽（比劫/印，不含日干自身）方成党势。
# 党羽数不足（孤身无党）者，其日柱制用做功无力，降为辅助。
_DANGSHI_MIN_SUPPORTERS = 1


def _pillar_of(pos: str) -> str:
    """from_pos/to_pos -> 柱位键，如 'day_gan' -> 'day'。"""
    if not pos or '_' not in pos:
        return ''
    return pos.split('_')[0]


def _elem_of(pos: str, gans: List[str], zhis: List[str]) -> str:
    """from_pos/to_pos -> 对应的天干或地支字符。"""
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    if p not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(p)
    return gans[idx] if t == 'gan' else zhis[idx]


def _hua_is_chengju(day_gan: str, gans: List[str],
                    zhis: Optional[List[str]] = None,
                    day_zhi_he_center: bool = False) -> bool:
    """化用成局判定：月令司令之印透干（月干为印）或坐下印星贴身（日支本气印）。

    化用（杀印相生）做主功属化用成局之高层功量，要求印有力化杀为权：
    月干为印（司令透干）或日支本气为印（坐下印星贴身化杀，如化例二 丙日坐寅
    木印化壬水杀）方为化用成局。时上印、月令藏印力弱，不构成化用成局，
    不夺命局主功（避免误抢自坐禄/天干克 fallback 之命局）。

    坐下印须为"专司化杀"之印：日支若参六合/暗合（合中心），其力归于合用而非
    化杀，不构成化用成局（合例六 庚日坐戌土印，但戌参卯戌合为主功合用，非化用）。
    """
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx:
        return False
    yin_wx = next((wx for wx, prod in WX_SHENG.items() if prod == day_wx), '')
    if not yin_wx or len(gans) < 2:
        return False
    if GAN_WX.get(gans[1], '') == yin_wx:
        return True  # 月干为印（司令透干）
    if (zhis and ZHI_WX.get(zhis[2], '') == yin_wx
            and not day_zhi_he_center):
        return True  # 坐下印（日支本气印，且非合中心）
    return False


def _tiyong_of(day_gan: str, elem: str) -> str:
    """根据五行判定 elem 相对 day_gan 属体属用。

    体 = 同我(比劫) + 生我(印) + 我生(食伤) + 日主
    用 = 我克(财) + 克我(官杀)
    地支无十神，以五行生克关系等同判定。
    """
    day_wx = GAN_WX.get(day_gan, '')
    wx = GAN_WX.get(elem, '') or ZHI_WX.get(elem, '')
    if not day_wx or not wx:
        return ''
    if wx == day_wx:
        return '体'  # 比劫
    if WX_SHENG.get(wx) == day_wx:
        return '体'  # 印（生我）
    if WX_SHENG.get(day_wx) == wx:
        return '体'  # 食伤（我生）
    if WX_KE.get(day_wx) == wx:
        return '用'  # 财（我克）
    if WX_KE.get(wx) == day_wx:
        return '用'  # 官杀（克我）
    return ''


def analyze_zuogong(
    day_gan: str, day_zhi: str,
    year_gan: str = '', year_zhi: str = '',
    month_gan: str = '', month_zhi: str = '',
    hour_gan: str = '', hour_zhi: str = '',
    shishen: Optional[Dict[str, str]] = None,
    kong_wang=None,
) -> Dict:
    """盲派做功分析。

    检测四柱中的制用、合用、墓用、生用、化用、成势六类做功方式，
    依优先级链判定主做功，分类功神废神，评估做功层次。

    分层：纯关系检测交由 objective.zuogong_detect.detect_relations 完成；
    本函数做党势强弱判定、做功成立确认、primary_work、效率/层次/主被动评估。

    支持两种调用签名（P2-1 统一 API）：
      1. 旧签名：analyze_zuogong(day_gan, day_zhi, year_gan, year_zhi,
                                 month_gan, month_zhi, hour_gan, hour_zhi,
                                 shishen=None, kong_wang=None)
      2. Pillars 对象：analyze_zuogong(pillars, shishen=None, kong_wang=None)

    Args:
        day_gan: 日干（或 Pillars 对象）
        day_zhi: 日支
        year_gan/year_zhi/month_gan/month_zhi/hour_gan/hour_zhi: 其余三柱干支
        shishen: 十神映射（可选，用于体用分类；缺省时按五行推算）
        kong_wang: 空亡数据（可选，地支列表或含地支列表的 dict；
            空亡地支参与做功 -> efficiency_discount 打折）

    Returns:
        做功分析结果字典
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
    day_wx = GAN_WX.get(day_gan, '')

    # ── 纯关系检测（objective 层）──
    # 冲合刑害穿破生克墓暗合等纯规则检测 + 长生/空亡/天干入墓原始事实，
    # 全部由 detect_relations 产出；本函数不再做任何检测，仅做解释性判断。
    det = detect_relations(
        day_gan, day_zhi,
        year_gan, year_zhi, month_gan, month_zhi, hour_gan, hour_zhi,
        kong_wang=kong_wang,
    )
    work_actions: List[Dict] = det['work_actions']
    tomb_works: List[Dict] = det['tomb_works']
    sheng_yong_actions: List[Dict] = det['sheng_yong_actions']
    day_he_type: Optional[str] = det['day_he_type']
    san_he_formed: bool = det['san_he_formed']
    zheng_he: bool = det['zheng_he']
    day_changsheng: Dict[str, str] = det['day_changsheng']
    day_weak_zhis: Set[str] = det['day_weak_zhis']
    kong_wang_zhis: Set[str] = det['kong_wang_zhis']
    entombed_gan_pillars: Set[str] = det['entombed_gan_pillars']

    # ── S1 重复计数去重 ──
    # 同一地支对可能被冲/克/刑/穿/破/合多条匹配，按段氏关系优先级只保留一条
    # 优先级: 冲>刑>穿>破>合>克>生；天干合/合化/三合局/半合/暗合/墓用不参与
    # 注：六合的 type 是 '地支合'（非 '合'），故去重类型集合须用 '地支合'
    # 合克属合不属克（《三命通会》论合克：合先于克，以合论不以克论）：地支同时
    # 满足合与克时优先归类为合。六合中带克的只有子丑/卯戌/巳申（合克对），
    # 故"地支合>克"只作用于合克对--与天干克"合对以合论不计克"统一处理。
    # 冲/刑/穿/破 仍高于地支合，故巳申（合+克+刑+破）仍以刑胜出，不受影响。
    _DEDUP_PRIORITY = {'冲': 7, '刑': 6, '穿': 5, '破': 4, '地支合': 3, '克': 2, '生': 1}
    _DEDUP_TYPES = {'冲', '克', '刑', '穿', '破', '地支合', '生'}
    # 穿（severity=high）即使被去重也不标 auxiliary：穿为暗伤，其 harm 信号必须
    # 透传到 assess_work_level 的 has_severe_harm/has_active_harm 判断。
    # 被动穿（to_pos 含 day_）-> has_severe_harm；主动穿（from_pos 含 day_）-> has_active_harm。
    # 寅巳对同时为刑(pri6)与穿(pri5)，刑胜出时穿被去重--若不保护，主动穿漏标
    # has_active_harm（被动穿已由 _is_passive_chuan 保护，_is_active_chuan 对称补全）。
    def _is_passive_chuan(wa):
        return (wa.get('type') == '穿' and wa.get('severity') == 'high'
                and wa.get('to_pos', '').startswith('day_'))

    def _is_active_chuan(wa):
        return (wa.get('type') == '穿' and wa.get('severity') == 'high'
                and wa.get('from_pos', '').startswith('day_'))

    def _is_protected_chuan(wa):
        return _is_passive_chuan(wa) or _is_active_chuan(wa)

    # 去重键用无序 frozenset({from_pos, to_pos})：克的 from/to 方向与冲/刑相反
    # （克方为"我克者"在先，冲/刑按柱序），有序 (from_pos, to_pos) 无法把同一对合并
    _best: Dict[frozenset, tuple] = {}  # frozenset({fpos, tpos}) -> (priority, index)
    for _idx, _wa in enumerate(work_actions):
        if _wa.get('auxiliary') or _wa.get('type') not in _DEDUP_TYPES:
            continue
        _pair = frozenset((_wa.get('from_pos', ''), _wa.get('to_pos', '')))
        if not _pair or '' in _pair:
            continue
        _pri = _DEDUP_PRIORITY.get(_wa.get('type', ''), 0)
        if _pair in _best and _pri <= _best[_pair][0]:
            if not _is_protected_chuan(_wa):
                _wa['auxiliary'] = True
                _wa['dedup_removed'] = True
        else:
            if _pair in _best:
                _old_idx = _best[_pair][1]
                if not _is_protected_chuan(work_actions[_old_idx]):
                    work_actions[_old_idx]['auxiliary'] = True
                    work_actions[_old_idx]['dedup_removed'] = True
            _best[_pair] = (_pri, _idx)

    # S1 dedup placeholder
    work_actions.extend(tomb_works)

    # ── S2 宾宾交互过滤 ──
    # 日柱不参与的地支互动（from_pos/to_pos 都不含 day_）降级为辅助
    # 天干合/合化/三合局不受此限制
    _DAY_REQUIRED_TYPES = {'冲', '克', '刑', '穿', '破', '合', '生', '墓用', '暗合', '半合'}
    for _wa in work_actions:
        if _wa.get('auxiliary'):
            continue
        _tp = _wa.get('type', '')
        if _tp in ('天干合', '合化', '杀印相生', '三合局'):
            continue
        _fp = _wa.get('from_pos', '')
        _tp2 = _wa.get('to_pos', '')
        if not _fp.startswith('day_') and not _tp2.startswith('day_'):
            _wa['auxiliary'] = True
            _wa['global_qi'] = True

    # ── S3 党势强弱判定（段氏铁律：强方制弱方才算功）──
    # 须一方成党势方有制用之力。统计日柱所在方党羽数（比劫+印，不含日干自身），
    # 党羽数不足（孤身无党）者，其日柱主动制用（冲/克/刑/破）做功无力，降为辅助。
    # 穿（severity=high）携 harm 信号，不在此降级，避免漏标 has_active_harm。
    # 被动受制（to_pos=day_）属强方制弱方之"制弱"，不降级。
    if day_wx:
        _yin_wx_ds, _sha_wx_ds, _day_supporters = _day_faction(day_gan, gans, zhis)
        if _day_supporters < _DANGSHI_MIN_SUPPORTERS:
            for _wa in work_actions:
                if _wa.get('auxiliary'):
                    continue
                if _wa.get('type') not in ('冲', '克', '刑', '破'):
                    continue  # 仅制用（穿除外，见上注）
                if not _wa.get('from_pos', '').startswith('day_'):
                    continue  # 仅日柱主动做功
                _wa['auxiliary'] = True
                _wa['weak_faction'] = True

    # ── 正向/反向做功方向（P1-2，消费 tiyong + binzhu）──
    # 主位=日时（体之位），宾位=年月（用之位）
    # 正向：from=体在主位 + to=用在宾位（我以体之工具取宾位之用）
    # 反向：from=用在主位 + to=体在宾位（反向做功，效率高）
    # 与下方 ti_result 守卫风格对齐：analyze_binzhu 异常时留空，
    # 由下方 isinstance(binzhu_result, dict) 判空 -> binzhu_zhu/binzhu_bin 留空
    # -> 自动触发回退到硬编码 _ZHU_PILLARS，不致整体做功分析崩溃。
    try:
        binzhu_result = analyze_binzhu(year_zhi, month_zhi, day_zhi, hour_zhi,
                                       year_gan, month_gan, day_gan, hour_gan)
    except Exception:
        binzhu_result = None
    # 由 binzhu 三层模型推导主/宾柱位（替代硬编码 _ZHU_PILLARS）：
    #   主位 = layer1（日、时）；宾位 = layer2 近宾 + layer3 远宾（年、月）
    # 远宾仍属宾，故宾位取 layer2∪layer3，保持原"主=日时、宾=年月"语义。
    _cn_to_pillar = dict(zip(PILLAR_NAMES_CN, PILLAR_KEYS))
    binzhu_zhu: Set[str] = set()
    binzhu_bin: Set[str] = set()
    if isinstance(binzhu_result, dict):
        for cn in (binzhu_result.get('layer1') or {}).get('pillars', []):
            k = _cn_to_pillar.get(cn)
            if k:
                binzhu_zhu.add(k)
        for _lk in ('layer2', 'layer3'):
            for cn in (binzhu_result.get(_lk) or {}).get('pillars', []):
                k = _cn_to_pillar.get(cn)
                if k:
                    binzhu_bin.add(k)
    # 回退：binzhu 无 layer 信息时沿用原硬编码逻辑
    if not binzhu_zhu:
        binzhu_zhu = set(_ZHU_PILLARS)
    if not binzhu_bin:
        binzhu_bin = set(PILLAR_KEYS) - binzhu_zhu
    ti_result: Optional[Dict] = None
    if shishen:
        try:
            ti_result = classify_tiyong(shishen, day_gan)
        except Exception:
            ti_result = None
    # 深度消费 ti_result：按各柱十神聚合体/用元素集合，供正反向做功补充判定。
    # 食伤为中性居体用之间，消费其 bias：食神偏体(入 ti)、伤官偏用(入 yong)，
    # 使体用元素集完整（旧实现中性食伤不入任一集，bias 信号闲置为装饰性数据）。
    # ti/yong 落 sorted list 而非 set：保证 zuogong 结果经 assemble json.dumps 可序列化。
    if ti_result:
        _ti_elems: Set[str] = set()
        _yong_elems: Set[str] = set()
        _bias_summary = {'食神偏体': [], '伤官偏用': []}
        for _key, _info in ti_result.items():
            if not isinstance(_info, dict):
                continue
            _elem = _elem_of(_key, gans, zhis)
            if not _elem:
                continue
            _cat = _info.get('category')
            if _cat == '体':
                _ti_elems.add(_elem)
            elif _cat == '用':
                _yong_elems.add(_elem)
            elif _cat == '中性':
                # 消费 bias：食神偏体入体集、伤官偏用入用集
                _bias = _info.get('bias')
                if _bias == '体':
                    _ti_elems.add(_elem)
                    _bias_summary['食神偏体'].append(_key)
                elif _bias == '用':
                    _yong_elems.add(_elem)
                    _bias_summary['伤官偏用'].append(_key)
        ti_result['ti'] = sorted(_ti_elems)
        ti_result['yong'] = sorted(_yong_elems)
        ti_result['bias_summary'] = _bias_summary
    reverse_work_count = 0
    for wa in work_actions:
        if wa.get('auxiliary'):
            continue
        fpos, tpos = wa.get('from_pos', ''), wa.get('to_pos', '')
        if not fpos or not tpos:
            continue
        f_elem = _elem_of(fpos, gans, zhis)
        t_elem = _elem_of(tpos, gans, zhis)
        if not f_elem or not t_elem:
            continue
        f_ty = _tiyong_of(day_gan, f_elem)
        t_ty = _tiyong_of(day_gan, t_elem)
        # ti_result 体用分类作为 _tiyong_of 的补充（不替换）：仅在 _tiyong_of 缺判时补位
        if ti_result:
            if not f_ty:
                if f_elem in ti_result.get('ti', ()):
                    f_ty = '体'
                elif f_elem in ti_result.get('yong', ()):
                    f_ty = '用'
            if not t_ty:
                if t_elem in ti_result.get('ti', ()):
                    t_ty = '体'
                elif t_elem in ti_result.get('yong', ()):
                    t_ty = '用'
        f_zhu = _pillar_of(fpos) in binzhu_zhu
        t_bin = _pillar_of(tpos) in binzhu_bin
        if f_ty == '体' and f_zhu and t_ty == '用' and t_bin:
            wa['direction'] = '正向'
        elif f_ty == '用' and f_zhu and t_ty == '体' and t_bin:
            wa['direction'] = '反向'
            reverse_work_count += 1

    # ── 长生数据接入做功效率（P2-3）──
    # 日干在某地支上处死/墓/绝 -> 该地支参与做功效率打折。
    # day_weak_zhis 已由 detect_relations 算出（纯查表事实），此处仅做折扣标注。
    for wa in work_actions:
        if wa.get('auxiliary'):
            continue
        for pos_field in ('from_pos', 'to_pos'):
            pos = wa.get(pos_field, '')
            if not pos.endswith('_zhi'):
                continue
            elem = _elem_of(pos, gans, zhis)
            if elem in day_weak_zhis:
                wa['efficiency_discount'] = True
                break

    # ── 天干入墓（M4）：天干坐于自身墓库地支 -> 做事能力受限 ──
    # 天干入墓属天干层面，不计入 tomb_works（地支层面）；
    # 但 from_pos 所在柱的天干若入墓，该柱主动做功能力打折。
    # entombed_gan_pillars 已由 detect_relations 算出，此处仅做折扣标注。
    for wa in work_actions:
        if wa.get('auxiliary'):
            continue
        f_pillar = _pillar_of(wa.get('from_pos', ''))
        t_pillar = _pillar_of(wa.get('to_pos', ''))
        # 该天干对应的做功动作（from 或 to 所在柱天干入墓）标记入墓并打折
        if f_pillar in entombed_gan_pillars or t_pillar in entombed_gan_pillars:
            wa['gan_entombed'] = True
            wa['efficiency_discount'] = True

    # ── 空亡接入做功效率（P1-1）──
    # 段氏：空亡之地做事落空，做功减损。空亡地支参与做功 -> efficiency_discount 打折。
    # 仅地支层面：from_pos/to_pos 为 _zhi 且该地支属空亡方标记（与长生折扣同口径，
    # 天干层面动作非地支参与，不标）。
    # kong_wang_zhis 已由 detect_relations 算出，此处仅做折扣标注。
    if kong_wang_zhis:
        for wa in work_actions:
            if wa.get('auxiliary'):
                continue
            for pos_field in ('from_pos', 'to_pos'):
                pos = wa.get(pos_field, '')
                if not pos.endswith('_zhi'):
                    continue
                if _elem_of(pos, gans, zhis) in kong_wang_zhis:
                    wa['efficiency_discount'] = True
                    wa['kong_wang'] = True
                    break

    # ── 做功优先级链：判定主做功（primary_work）──
    primary_work: Optional[Dict] = None
    primary_action: Optional[Dict] = None
    # 食伤合制（伤官合杀/食神合官）：非日干天干合中食伤一侧合官杀。食伤既用于
    # 合制，便不再以泄秀做生用--生用应让位于合用/制用（复例四 戊癸合伤官合杀，
    # 不应以辰藏戊制杀之生用夺主功；制例一 乙庚合食伤合官同理，主功在丑未冲制用）。
    _shi_wx = WX_SHENG.get(day_wx, '')
    _has_shi_hezhi = False
    if _shi_wx:
        for wa in work_actions:
            if wa.get('type') != '天干合':
                continue
            if (wa.get('from_pos', '').startswith('day_')
                    or wa.get('to_pos', '').startswith('day_')):
                continue  # 日干合非食伤合制
            for _pf in ('from_pos', 'to_pos'):
                _pos = wa.get(_pf, '')
                if _pos.endswith('_gan') and GAN_WX.get(_elem_of(_pos, gans, zhis), '') == _shi_wx:
                    _has_shi_hezhi = True
                    break
            if _has_shi_hezhi:
                break
    he_actions = [
        wa for wa in work_actions
        if wa.get('type') == '天干合' and wa.get('from_pos', '').startswith('day_')
    ]
    # ── 制例三（癸戊己甲/卯午酉戌）：日支涉 high 穿（酉戌穿·火土势穿制食神局），
    #    穿制为主功，日干合（合官）让位；其日支食伤（酉藏辛）被穿制、不做泄秀
    #    功，亦让位予弃干看支之穿制。仅当日干合与日支 high 穿并存时触发--无合
    #    之命（如 verify zg7/zg8 寅巳穿）不受影响，其穿制/食伤逻辑各自独立。──
    _chuan_yields = bool(he_actions) and any(
        wa.get('type') == '穿' and wa.get('severity') == 'high'
        and ('day_zhi' in wa.get('from_pos', '') or 'day_zhi' in wa.get('to_pos', ''))
        for wa in work_actions
    )
    # 坐下印是否为合中心：日支参六合/暗合（合用）则其力归合非化杀，不构成化用成局。
    _day_zhi_he_center = any(
        wa.get('type') in ('地支合', '暗合')
        and ('day_zhi' in wa.get('from_pos', '') or 'day_zhi' in wa.get('to_pos', ''))
        for wa in work_actions
    )
    _hua_chengju = (any(wa.get('type') == '杀印相生' and not wa.get('auxiliary')
                        for wa in work_actions)
                    and _hua_is_chengju(day_gan, gans, zhis, _day_zhi_he_center))
    # 争合判定：日干合两柱同被合（如己合年甲+时甲），合用之力分散减弱。化用成局
    # （月干司令透干之印化杀=当官之命）为高层功量，争合合用须让位予化用成局
    # （化例三中堂 己合甲争合，主功在月干丙印化甲杀之化用成局，非争合合用）。
    # 日干合两柱必为同气之争（日干仅合一干），故 he_actions>=2 即争合。
    _zheng_he = len(he_actions) >= 2
    if he_actions and not _chuan_yields and not (_hua_chengju and _zheng_he):
        primary_action = he_actions[0]
        primary_work = {'type': '合用', 'path': '日干合（合财/合官）'}
    elif _hua_chengju and not _chuan_yields:
        # 化用成局做主功：印得令透干或坐下印贴身化杀为权（化杀为印、泄官杀生身，
        # 段氏论为当官之命），为高层功量，优先于食伤泄秀之生用。命局为纯杀印链
        # （detect 阶段已剔除有非印涉日支制用/墓用之命的化用，此处化用 in types 即
        # 真化用）。日干合更贴身者仍居其前（化例三 日干合居首）。化用成局须印得力
        # （月干印/坐下印）：时上印、月令藏印力弱不构成成局，不夺生用主功
        # （避免误抢自坐禄/天干克 fallback 之命局主功）。
        hua_actions = [
            wa for wa in work_actions
            if wa.get('type') == '杀印相生' and not wa.get('auxiliary')
        ]
        primary_action = hua_actions[0]
        primary_work = {'type': '化用', 'path': '杀印相生（化杀为印·泄官杀生身）'}
    elif ([a for a in sheng_yong_actions
           if not a.get('auxiliary')
           and not a.get('gan_entombed')
           and not (_chuan_yields and a.get('to_pos') == 'day_zhi')]
          and not _has_shi_hezhi):
        # 食伤泄秀之伤官/食神若入墓（gan_entombed），泄秀之器受制无力泄秀，生用
        # 不当主功，让位予弃干看支之制用（制例二 戊日伤官辛入墓，主功在日支寅克
        # 丑/戌之制用，非辛泄秀之生用）。未入墓之食伤泄秀仍居其位（生例一/二/四）。
        primary_action = [a for a in sheng_yong_actions
                          if not a.get('auxiliary')
                          and not a.get('gan_entombed')
                          and not (_chuan_yields and a.get('to_pos') == 'day_zhi')][0]
        primary_work = {'type': '生用', 'path': '日干生（食伤泄秀）'}
    else:
        # 弃干看支：日支的刑冲破害墓合（含被动受制/合制）
        zhi_actions = [
            wa for wa in work_actions
            if not wa.get('auxiliary')
            and (wa.get('from_pos', '').startswith('day_zhi')
                 or wa.get('to_pos', '').startswith('day_zhi'))
            and wa.get('action') in ('冲', '克', '穿', '刑', '破', '墓用', '半成势', '合用')
        ]
        if zhi_actions:
            active_zhi = [
                wa for wa in zhi_actions
                if wa.get('from_pos', '').startswith('day_zhi')
            ]
            primary_action = (active_zhi or zhi_actions)[0]
            _pa_action = primary_action.get('action')
            if _pa_action == '墓用':
                ptype = '墓用'
                _path = '弃干看支（日支墓用做功）'
            elif _pa_action == '合用':
                ptype = '合用'
                _path = '弃干看支（日支合用做功）'
            else:
                ptype = '制用'
                _path = '弃干看支（日支刑冲破害做功）'
            primary_work = {'type': ptype, 'path': _path}
    if primary_action is None:
        # 日干支俱不做功 -> 看禄/比劫：查日干禄位是否在主位（日支/时支）。
        # 段氏：禄在主位（自坐禄/时禄）为禄做功；禄在宾位则无主位之禄可凭。
        # 若禄在主位，primary_work 由"禄比"label 升级为实际禄做功检测。
        lu_zhi = LU.get(day_gan, '')
        lu_in_zhu = bool(lu_zhi) and lu_zhi in (day_zhi, hour_zhi)
        # 禄分支前置守卫：上方 zhi_actions 过滤器（弃干看支）只认
        # 冲/克/穿/刑/破/墓用/半成势，不认日支六合(地支合)/暗合，也不认日干
        # 主动克(天干克)。这些同样是日柱做功--若已存在则不应触发禄分支，
        # 否则会追加伪禄 action、误标 primary_work=禄做功，或在禄不在主位时
        # 误写"俱不做功"（实际有制用/合用）。
        # 仅日干主动克(from_pos=day_gan)算日柱做功：被动受克(to_pos=day_gan)
        # 是日柱受制而非做功，不抑制禄（自坐禄逢官杀克身仍可凭禄做功）。
        day_work_actions = [
            wa for wa in work_actions
            if not wa.get('auxiliary')
            and (
                (wa.get('type') in ('地支合', '暗合')
                 and (wa.get('from_pos', '').startswith('day_')
                      or wa.get('to_pos', '').startswith('day_')))
                or (wa.get('type') == '克' and wa.get('from_pos') == 'day_gan')
            )
        ]
        has_day_zuo_gong = bool(day_work_actions)
        if lu_in_zhu and not has_day_zuo_gong:
            lu_pos = 'day_zhi' if lu_zhi == day_zhi else 'hour_zhi'
            lu_pillar_cn = '日' if lu_pos == 'day_zhi' else '时'
            lu_action = {
                'type': '禄',
                'action': '禄做功',
                'from': f'日干({day_gan})',
                'to': f'{lu_pillar_cn}支({lu_zhi})',
                'from_pos': 'day_gan',
                'to_pos': lu_pos,
                'desc': f'日干{day_gan}禄在{lu_zhi}（主位{lu_pillar_cn}支），禄做功',
            }
            work_actions.append(lu_action)
            # 禄 action 追加晚于长生/天干入墓/空亡三个折扣循环，此处补标
            # efficiency_discount（与上方折扣循环同口径），避免禄做功漏标折扣。
            for _lu_pos_field in ('from_pos', 'to_pos'):
                _lu_pos = lu_action.get(_lu_pos_field, '')
                if not _lu_pos.endswith('_zhi'):
                    continue
                _lu_zhi_char = _elem_of(_lu_pos, gans, zhis)
                if _lu_zhi_char in day_weak_zhis:
                    lu_action['efficiency_discount'] = True
                if kong_wang_zhis and _lu_zhi_char in kong_wang_zhis:
                    lu_action['efficiency_discount'] = True
                    lu_action['kong_wang'] = True
            _lu_f_pillar = _pillar_of(lu_action.get('from_pos', ''))
            _lu_t_pillar = _pillar_of(lu_action.get('to_pos', ''))
            if _lu_f_pillar in entombed_gan_pillars or _lu_t_pillar in entombed_gan_pillars:
                lu_action['gan_entombed'] = True
                lu_action['efficiency_discount'] = True
            primary_action = lu_action
            primary_work = {
                'type': '禄比',
                'path': f'日干{day_gan}禄在{lu_zhi}（主位），禄做功',
                'lu_in_zhu': True,
                'lu_zhi': lu_zhi,
            }
        elif has_day_zuo_gong:
            # 日柱已有六合/暗合/天干克做功 -> primary_work 反映实际做功方式，
            # 不追加伪禄 action，不标禄做功，亦不误写"俱不做功"
            _dw = day_work_actions[0]
            if _dw.get('type') == '克':
                primary_work = {'type': '制用',
                                'path': f'日干克做功（{_dw.get("desc", "")}）'}
            else:
                primary_work = {'type': '合用',
                                'path': f'日支合用做功（{_dw.get("desc", "")}）'}
        else:
            primary_work = {'type': '禄比', 'path': '日干支俱不做功，看禄/比劫'}
    if primary_action is not None:
        primary_action['primary'] = True

    # ── 装饰性信号接线：消费 wood_type / soil / virtual_solid 信号（P0）──
    # 这三个 objective 模块产结构化信号但原本不被 zuogong 消费（"模块对、接线断"，
    # 审计 P0 装饰性信号集成断层）。此处自算（与 binzhu/tiyong 同样的自算 + try/except
    # 守卫，单模块失败不影响做功分析）并把信号接入做功动作标注与效率评估：
    #   wood_type.fear_metal     活木见金坏根 -> 日柱主动做功打折（efficiency_discount）
    #   wood_type.fire_xiuxiu    活木见火泄秀(吉)/死木见火反焚 -> 标注食伤泄秀吉凶
    #   wood_type.control_water  死木以制水为功/活木不制水 -> 做功策略信号
    #   soil.shengke_behavior    四土燥湿生克分流（湿土克水弱 -> 做功打折；燥土脆金等标注）
    #   virtual_solid.vulnerable_to_ke  虚透天干被克 -> 损害加重标注
    try:
        wood_result = analyze_wood_type(day_gan, year_zhi, month_zhi, day_zhi, hour_zhi)
    except Exception:
        wood_result = {}
    try:
        soil_result = analyze_soil(year_zhi, month_zhi, day_zhi, hour_zhi)
    except Exception:
        soil_result = {}
    try:
        vs_result = analyze_virtual_solid(
            day_gan, day_zhi, year_gan, year_zhi, month_gan, month_zhi, hour_gan, hour_zhi)
    except Exception:
        vs_result = {}

    wood_signals = {
        'is_wood': wood_result.get('is_wood', False),
        'wood_type': wood_result.get('wood_type', ''),
        'fear_metal': wood_result.get('fear_metal', False),
        'control_water': wood_result.get('control_water', False),
        'fire_xiuxiu': wood_result.get('fire_xiuxiu', False),
    }
    # soil 燥湿生克索引：支 -> shengke_behavior
    _soil_signals: Dict[str, Dict] = {}
    for _entry in (soil_result.get('soil_entries') or []):
        _z = _entry.get('zhi')
        if _z:
            _soil_signals[_z] = _entry.get('shengke', {}) or {}
    # virtual_solid 虚透天干索引：柱位 -> vulnerable_to_ke
    _VS_PILLAR_KEY = {'年柱': 'year', '月柱': 'month', '时柱': 'hour'}
    _vs_by_pillar: Dict[str, Dict] = {}
    vulnerable_gans: List[Dict] = []
    for _vs in (vs_result.get('virtual_solid') or []):
        _pkey = _VS_PILLAR_KEY.get(_vs.get('pillar', ''))
        _vuln = _vs.get('vulnerable_to_ke', {}) or {}
        if _pkey:
            _vs_by_pillar[_pkey] = _vuln
        if _vuln.get('vulnerable'):
            vulnerable_gans.append({
                'pillar': _vs.get('pillar', ''),
                'gan': _vs.get('gan', ''),
                'level': _vuln.get('level', ''),
                'reason': _vuln.get('reason', ''),
            })

    signal_notes: List[str] = []
    _is_wood = wood_signals['is_wood']
    _fear_metal = wood_signals['fear_metal']
    _fire_xiuxiu = wood_signals['fire_xiuxiu']
    _control_water = wood_signals['control_water']

    for wa in work_actions:
        if wa.get('auxiliary'):
            continue
        # wood_type.fear_metal：活木见金坏根 -> 日柱主动做功打折
        if _fear_metal and wa.get('from_pos', '').startswith('day_'):
            wa['wood_fear_metal'] = True
            wa['efficiency_discount'] = True
        # wood_type.fire_xiuxiu：食伤泄秀按活死木标吉凶
        if _is_wood and wa.get('type') == '食伤':
            wa['wood_fire_xiuxiu'] = (
                '泄秀吉（活木见火开花）' if _fire_xiuxiu
                else '见火反焚（死木忌旺火）')
        # soil.shengke_behavior：四土参与动作按燥湿标实际生克
        for _pf in ('from_pos', 'to_pos'):
            _pos = wa.get(_pf, '')
            if not _pos.endswith('_zhi'):
                continue
            _elem = _elem_of(_pos, gans, zhis)
            _sk = _soil_signals.get(_elem)
            if not _sk:
                continue
            wa.setdefault('soil_shengke', {})[_elem] = {
                'wet': _sk.get('wet'),
                'sheng_jin': _sk.get('sheng_jin'),
                'cui_jin': _sk.get('cui_jin'),
                'ke_shui': _sk.get('ke_shui'),
                'hui_huo': _sk.get('hui_huo'),
            }
            # 湿土克水力弱：湿土为克之源、目标为水 -> 该克做功打折
            if _sk.get('wet') and wa.get('type') == '克' and _pf == 'from_pos':
                _t_elem = _elem_of(wa.get('to_pos', ''), gans, zhis)
                if ZHI_WX.get(_t_elem, '') == '水':
                    wa['efficiency_discount'] = True
                    wa['soil_weak_ke_shui'] = True
        # virtual_solid.vulnerable_to_ke：虚透天干被克 -> 损害加重标注
        if wa.get('type') == '克' and wa.get('to_pos', '').endswith('_gan'):
            _t_pillar = _pillar_of(wa.get('to_pos', ''))
            _vuln = _vs_by_pillar.get(_t_pillar)
            if _vuln and _vuln.get('vulnerable'):
                wa['target_vulnerable'] = _vuln.get('level')  # '轻'/'重'

    # ── tiyong.bias 消费：食神偏体/伤官偏用标注食伤做功 ──
    # 食伤动作 to_pos 指向食伤所在柱天干，ti_result 已存其 category(中性)+bias。
    if ti_result:
        for wa in work_actions:
            if wa.get('auxiliary') or wa.get('type') != '食伤':
                continue
            _info = ti_result.get(wa.get('to_pos', ''))
            if isinstance(_info, dict) and _info.get('category') == '中性':
                _b = _info.get('bias')
                if _b == '体':
                    wa['tiyong_bias'] = '食神偏体'
                elif _b == '用':
                    wa['tiyong_bias'] = '伤官偏用'

    # ── signal_notes 汇总（消费可见性，接入做功叙述）──
    if _fear_metal:
        signal_notes.append('活木见金坏根：日柱主动做功打折')
    if _is_wood:
        signal_notes.append(
            '活木见火为泄秀（吉），食伤泄秀做功得力' if _fire_xiuxiu
            else '死木见火反焚，食伤泄秀做功有损')
        signal_notes.append(
            '死木无印可生，可以制水为功' if _control_water
            else '活木以水为印生身，不以制水为做功')
    if vulnerable_gans:
        signal_notes.append('虚透天干怕克：' + '、'.join(
            f"{v['pillar']}{v['gan']}({v['level']})" for v in vulnerable_gans))
    if ti_result:
        _bs = ti_result.get('bias_summary', {}) or {}
        if _bs.get('食神偏体') or _bs.get('伤官偏用'):
            _parts = []
            if _bs.get('食神偏体'):
                _parts.append(f"食神偏体({','.join(_bs['食神偏体'])})")
            if _bs.get('伤官偏用'):
                _parts.append(f"伤官偏用({','.join(_bs['伤官偏用'])})")
            signal_notes.append('体用偏性：' + '、'.join(_parts))

    # ── 做功效率（仅计非辅助做功）──
    non_aux = [wa for wa in work_actions if not wa.get('auxiliary')]
    # work_types 以 non_aux 为准重算：S1 去重/S2 降级动作的 type 不计入，
    # 避免宾宾半合/宾宾制用等降级动作虚增 type_count（建阶段的 add 为 provisional）。
    work_types = {_WORK_TYPE_LABEL[wa.get('type', '')]
                  for wa in non_aux if wa.get('type', '') in _WORK_TYPE_LABEL}
    action_count = len(non_aux)
    type_count = len(work_types)
    if action_count >= EFFICIENCY_HIGH_ACTION_COUNT or type_count >= EFFICIENCY_HIGH_TYPE_COUNT:
        efficiency = '高'
    elif action_count >= EFFICIENCY_MID_ACTION_COUNT:
        efficiency = '中'
    else:
        efficiency = '低'
    # 长生/天干入墓折扣动作过多 -> 效率降一级（高->中、中->低、低不变）
    efficiency_discount_count = sum(1 for wa in non_aux if wa.get('efficiency_discount'))
    if action_count > 0 and efficiency_discount_count * 2 >= action_count:
        if efficiency == '高':
            efficiency = '中'
        elif efficiency == '中':
            efficiency = '低'
        # 低不变

    # ── 主动/被动做功分析（仅计非辅助做功）──
    # 主动做功：from_pos 以 day_ 开头 -> 日柱主动做功（我取外物，格局高）
    # 被动做功：to_pos 以 day_ 开头 -> 日柱被动被做功
    # 被动细分：被动制（被克/冲/穿/刑/破/入墓）-> 格局减分
    #           被动合（被合）-> 中性（财来合我可为吉）
    #           被动生（被生）-> 中性偏吉（印来生我）
    # 方向性互斥：同一动作不应既出又入。自坐禄 from_pos=day_gan、to_pos=day_zhi
    # 同属 day_，本质是日干凭禄主动做功（非被动承受），故被动集合排除已属主动者，
    # 避免禄 action 同时计入 active_work + passive_work 双计。
    active_work = [
        wa for wa in non_aux
        if wa.get('from_pos', '').startswith('day_')
    ]
    passive_work = [
        wa for wa in non_aux
        if wa.get('to_pos', '').startswith('day_')
        and not wa.get('from_pos', '').startswith('day_')
    ]
    passive_control = [
        wa for wa in passive_work
        if wa.get('type') in _PASSIVE_CONTROL_TYPES
    ]

    # ── 化用是否成功（供 work_level 判 Level 4）──
    hua_success = '化用' in work_types

    # ── 功神占比（供 work_level 判 Level 5）──
    gs_result = classify_gongshen(work_actions, pillar_keys, gans, zhis)
    gong_count = len(gs_result['gong_shen'])
    total_positions = sum(1 for g in gans if g) + sum(1 for z in zhis if z)
    gong_shen_ratio = (gong_count / total_positions) if total_positions else 0.0

    # ── 做功层次评估（本模块内 assess_work_level）──
    # 连珠成势(L5)须成势本身为主功：主做功动作是否为三合局。serial chain 不以三合局
    # 为 primary_action（成势多属 incidental），故 incidental 三合局命不升至 L5。
    _chengshi_primary = (primary_action is not None
                         and primary_action.get('type') == '三合局')
    level_result = assess_work_level(
        list(work_types), non_aux, len(tomb_works), day_he_type,
        active_work_count=len(active_work),
        passive_work_count=len(passive_work),
        passive_control_count=len(passive_control),
        hua_success=hua_success,
        san_he_formed=san_he_formed,
        gong_shen_ratio=gong_shen_ratio,
        reverse_work_count=reverse_work_count,
        efficiency_discount_count=efficiency_discount_count,
        chengshi_primary=_chengshi_primary,
    )
    level = level_result['level']
    work_tier = level_result['tier']
    work_level_desc = level_result.get('desc', '')
    has_severe_harm = level_result.get('has_severe_harm', False)
    has_active_harm = level_result.get('has_active_harm', False)

    return {
        'work_actions': work_actions,
        'work_types': sorted(work_types),
        'work_efficiency': efficiency,
        'work_level': level,
        'work_tier': work_tier,
        'work_level_desc': work_level_desc,
        'has_severe_harm': has_severe_harm,
        'has_active_harm': has_active_harm,
        'day_he_type': day_he_type,
        'primary_work': primary_work,
        'active_work': active_work,
        'passive_work': passive_work,
        'passive_control': passive_control,
        'gong_shen': gs_result['gong_shen'],
        'fei_shen': gs_result['fei_shen'],
        'gong_shen_ratio': round(gong_shen_ratio, 3),
        'tomb_works': tomb_works,
        'san_he_formed': san_he_formed,
        'reverse_work_count': reverse_work_count,
        'zheng_he': zheng_he,
        'day_changsheng': day_changsheng,
        'tiyong': ti_result,
        'wood_signals': wood_signals,
        'vulnerable_gans': vulnerable_gans,
        'signal_notes': signal_notes,
        'kong_wang_zhis': sorted(kong_wang_zhis),
    }
