"""
guanming - 盲派官命定性·主观层（subjective）

理论来源：段建业《盲派中级命理学》第九章「官命看法」（源文 3676-4269 行）
核心思想：官命=命局以「官杀/印/禄」为核心做功、得权得职之命。判定看做功组合
          （制用四类/生用化用）+ 带帽（管财的官）+ 行业取象。

一、制用做功四类组合（体制用，制官得官/制杀得权）：
  1. 官杀+伤食：伤食制官杀 -> 制官得官，主执法/管理/技术官；
  2. 官杀+劫刃：劫刃（比劫/羊刃）制官杀 -> 制杀得权，主军警/武职/竞争掌权；
  3. 印+财：财制印（段氏做功五配置之一，财印相战）-> 财印制用组合；
  4. 印+伤食：印制伤食（印制伤官以护官）-> 护官得官，主文职/行政。
  四类皆须主位（日时）制宾位（年月）方为得，宾制主为失。

二、生用化用（不以制得，以生化得官权）：
  1. 印化官杀：杀印相生（官杀->印->日主），化杀为印、化印为身 -> 文职/职权；
  2. 官禄格：官星坐禄/建禄（官星天干坐其禄位地支）-> 正统官职；
  3. 印带官帽：官杀天干坐印地支（带象，见 xiangfa_ops.daixiang）-> 有学历任官。

三、管财的官带帽：官带财帽（财天干坐官杀地支，带象财帽+官杀身）-> 管财之官
    （财政/金融/税务/企业管理）。

四、行业取象：依做功组合 + 干支象定行业（执法/军警/文教/财政/行政等）。

消费关系：
  - objective.zuogong_detect.detect_relations（制用/杀印相生关系）
  - objective.binzhu.analyze_binzhu（主宾，制用方向）
  - subjective.xiangfa_ops.daixiang（带帽：印带官帽/官带财帽）
  - objective.constants（LU/五行生克/藏干）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：制用四类中「印+财」段氏原列财制印（财坏印），官命语境下亦可财生官印流通，
          各师口径有异；行业取象为段氏主流口径归纳，非盲师定量表。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    LU, CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.xiangfa_ops import daixiang
from mangpai.subjective.yongshen import assess_direction_signals

_YANG_GANS = set('甲丙戊庚壬')
_ZHI_CONTROL: Set[str] = {'冲', '克', '穿', '刑', '破'}
# 合制动作（合以制之，如伤官合杀、丁亥自合）：天干合/地支合/暗合/半合
# （合化为化用、三合局为成势，不计入合制）
_HE_CONTROL: Set[str] = {'天干合', '地支合', '暗合', '半合'}


def _compute_shishen(day_gan: str, gan: str) -> str:
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


def _shishen_cat(ss: str) -> str:
    if not ss:
        return ''
    if ss in ('正官', '七杀'):
        return '官杀'
    if ss in ('正财', '偏财'):
        return '财'
    if ss in ('正印', '偏印'):
        return '印'
    if ss in ('食神', '伤官'):
        return '食伤'
    if ss in ('比肩', '劫财'):
        return '比劫'
    return ss


def _pos_main_cat(pos: str, day_gan: str, gans: List[str], zhis: List[str]) -> str:
    """pos 的**主气**十神大类（干取天干十神；支取本气藏干十神）。

    用于元素级制用动作匹配--冲克穿刑作用于地支主气五行，故以本气十神定被制之物，
    避免藏干中气/余气误配（如申藏壬印，但申主气庚官，寅申冲为官制比劫非印制伤食）。
    """
    if not pos:
        return ''
    pk = pos.split('_')[0]
    if pk not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(pk)
    if pos.endswith('_gan'):
        g = gans[idx] if idx < len(gans) else ''
        return _shishen_cat(_compute_shishen(day_gan, g))
    z = zhis[idx] if idx < len(zhis) else ''
    canggan = get_canggan_mangpai(z)
    if not canggan:
        return ''
    return _shishen_cat(_compute_shishen(day_gan, canggan[0][0]))


def _is_zhu(pos: str) -> bool:
    return pos.split('_')[0] in ('day', 'hour')


def _ensure_relations(day_gan, gans, zhis, relations):
    if relations is not None:
        return relations
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {}
    try:
        return detect_relations(
            day_gan, zhis[PILLAR_KEYS.index('day')],
            gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
    except Exception:
        return {}


# ───────────────────── 制用做功四类 + 生用化用 ─────────────────────

def classify_guanming_combo(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """官命做功组合判定：制用四类 + 生用化用。

    制用四类（主制宾=得，宾制主=失/被制）：
      - 伤食制官杀（官杀+伤食）
      - 劫刃制官杀（官杀+劫刃）
      - 财制印（印+财）
      - 印制伤食（印+伤食，护官）
    生用化用：
      - 印化官杀（杀印相生，detect_relations type='杀印相生'）
      - 官禄格（官星天干坐其禄位）
      - 印带官帽（xiangfa_ops.daixiang 官杀帽+印身）

    Returns:
        {
          'zhiyong_combos': [str],     # 命中制用组合
          'shengyong_huayong': [str],  # 命中生用化用
          'is_guanming': bool,         # 是否官命（任一组合+官杀明现/印权）
          'has_guansha': bool,
          'details': [str],
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'zhiyong_combos': [], 'shengyong_huayong': [], 'is_guanming': False,
                'has_guansha': False, 'details': ['四柱不全']}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    # 官杀明现（天干/地支主气）
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    has_guansha = False
    for i in range(4):
        if GAN_WX.get(gans[i]) == guan_wx:
            has_guansha = True
            break
        if ZHI_WX.get(zhis[i]) == guan_wx:
            has_guansha = True
            break

    combos: List[str] = []
    details: List[str] = []

    # 制用四类（含反向 + 合制）：遍历制用/合制动作，按 from/to 主气十神大类归类。
    # 段氏制用 = 五行相克（制=克），十神大类间克链双向皆可为功：
    #   伤食制官杀（食伤克官杀）/ 官杀制比劫（官杀克比劫，七杀制羊刃）/
    #   印制伤食（印克食伤）/ 财制印（财克印）/ 劫刃制财（比劫克财）。
    # 合制（合以制之，如伤官合杀、食神合官）同按 from/to 大类匹配，标「合制·」前缀。
    _CONTROL_PATTERNS = [
        ('食伤', '官杀', '伤食制官杀', '制官{verb}官，主执法/管理/技术官'),
        ('比劫', '官杀', '劫刃制官杀', '制杀{verb}权，主军警/武职/竞争掌权'),
        ('官杀', '比劫', '官杀制比劫', '七杀制羊刃{verb}权，主军警/武职/威权'),
        ('印', '食伤', '印制伤食', '印制伤官护官，{verb}官，主文职/行政'),
        ('财', '印', '财制印', '财印相战制用'),
        ('比劫', '财', '劫刃制财', '劫刃制财{verb}财，主争财/竞争求财'),
    ]
    for a in wa:
        _atype = a.get('type', '')
        is_he = _atype in _HE_CONTROL
        if _atype not in _ZHI_CONTROL and not is_he:
            continue
        from_pos, to_pos = a.get('from_pos', ''), a.get('to_pos', '')
        if not from_pos or not to_pos:
            continue
        f_cat = _pos_main_cat(from_pos, day_gan, gans, zhis)
        t_cat = _pos_main_cat(to_pos, day_gan, gans, zhis)
        if not f_cat or not t_cat:
            continue
        direction = '主制宾' if (_is_zhu(from_pos) and not _is_zhu(to_pos)) else (
            '宾制主' if (_is_zhu(to_pos) and not _is_zhu(from_pos)) else '同侧制'
        )
        verb = '得' if direction == '主制宾' else ('失' if direction == '宾制主' else '得（内部）')
        for pf, pt, pkey, pdesc in _CONTROL_PATTERNS:
            if f_cat == pf and t_cat == pt:
                key = ('合制·' if is_he else '') + pkey
                if key not in combos:
                    combos.append(key)
                    act_label = '合制' if is_he else '制用'
                    details.append(
                        f'{key}（{direction}，{act_label}）：{a.get("desc","")}，'
                        + pdesc.format(verb=verb)
                    )
                break

    # 生用化用
    shengyong: List[str] = []
    # 印化官杀（杀印相生）
    if any(a.get('type') == '杀印相生' for a in wa):
        shengyong.append('印化官杀')
        details.append('印化官杀（杀印相生）：官杀->印->日主，化杀为印，主文职/职权')
    # 官禄格：官星天干坐其禄位地支
    for i in range(4):
        g = gans[i]
        if GAN_WX.get(g) == guan_wx:  # 官星天干
            lu = LU.get(g, '')
            if lu and zhis[i] == lu:
                shengyong.append('官禄格')
                details.append(f'官禄格：{PILLAR_NAMES_CN[i]}干{g}（官）坐其禄{zhis[i]}，正统官职')
                break
    # 印带官帽（xiangfa_ops.daixiang）
    dai = daixiang(day_gan, gans, zhis)
    for d in dai:
        if d.get('combo') == '印带官帽':
            shengyong.append('印带官帽')
            details.append(f'印带官帽：{d.get("desc","")}，有学历任官')
            break

    # 官命成立：任一制用/生用组合命中（且官杀明现或印权在场）
    is_guanming = bool(combos or shengyong) and (has_guansha or '印化官杀' in shengyong or '印带官帽' in shengyong)

    return {
        'zhiyong_combos': combos,
        'shengyong_huayong': shengyong,
        'is_guanming': is_guanming,
        'has_guansha': has_guansha,
        'details': details,
    }


# ───────────────────── 管财的官带帽 ─────────────────────

def detect_guancai_daimao(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
) -> Optional[Dict]:
    """管财的官带帽检测：官带财帽（财+官杀带象）。

    财（帽/天干）坐官杀（身/地支藏干）-> 官带财帽，主管财之官
    （财政/金融/税务/企业管理）。复用 xiangfa_ops.daixiang 的「官带财帽」组合。

    Returns:
        命中记录或 None。
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    dai = daixiang(day_gan, gans or [], zhis or [])
    for d in dai:
        if d.get('combo') == '官带财帽':
            return {
                'found': True,
                'pillar': d.get('pillar'),
                'desc': d.get('desc'),
                'subject': '管财的官',
                'industry': '财政/金融/税务/企业管理',
            }
    return {'found': False}


# ───────────────────── 行业取象 ─────────────────────

# 干支象 -> 行业（段氏取象主流口径，官命行业映射）
_GAN_HANGYE: Dict[str, str] = {
    '甲': '林业/教育/行政', '乙': '园艺/纺织/文化',
    '丙': '能源/电力/传媒', '丁': '电子/照明/餐饮',
    '戊': '地产/建筑/农业', '己': '农业/陶瓷/服务',
    '庚': '军警/机械/五金', '辛': '珠宝/医疗/法律',
    '壬': '水利/交通/航运', '癸': '旅游/酒类/玄学',
}

def classify_hangye_xiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    combo_result: Optional[Dict] = None,
) -> Dict:
    """行业取象：依官命做功组合 + 干支象定行业。

    优先按做功组合定行业大类，辅以官杀所在柱天干象细化：
      - 伤食制官杀 -> 执法/司法/管理/技术官
      - 劫刃制官杀 -> 军警/武职/竞争性行业
      - 印制伤食/印化官杀/印带官帽 -> 文职/教育/行政/文书
      - 官禄格 -> 正统官职/公务员
      - 官带财帽（管财的官）-> 财政/金融/税务/企业管理

    Returns:
        {'primary': str, 'by_combo': [str], 'by_ganxiang': str, 'details': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    if combo_result is None:
        combo_result = classify_guanming_combo(day_gan, gans or [], zhis or [])
    combos = combo_result.get('zhiyong_combos', [])
    shengyong = combo_result.get('shengyong_huayong', [])

    by_combo: List[str] = []
    combo_hangye = {
        '伤食制官杀': '执法/司法/管理/技术官',
        '劫刃制官杀': '军警/武职/竞争性行业',
        '印制伤食': '文职/教育/行政',
        '财制印': '财经/管理',
        '印化官杀': '文职/教育/行政/文书',
        '官禄格': '正统官职/公务员',
        '印带官帽': '文职/教育/行政（有学历任官）',
    }
    for c in combos + shengyong:
        h = combo_hangye.get(c)
        if h and h not in by_combo:
            by_combo.append(h)

    # 官带财帽 -> 管财行业
    guancai = detect_guancai_daimao(day_gan, gans or [], zhis or [])
    if guancai and guancai.get('found'):
        if guancai['industry'] not in by_combo:
            by_combo.append(guancai['industry'])

    # 官杀所在柱天干象细化
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    by_ganxiang = ''
    for i in range(4):
        if GAN_WX.get(gans[i]) == guan_wx:
            by_ganxiang = _GAN_HANGYE.get(gans[i], '')
            break

    primary = by_combo[0] if by_combo else (by_ganxiang or '未明')
    details = []
    if by_combo:
        details.append('做功组合定行业：' + '、'.join(by_combo))
    if by_ganxiang:
        details.append(f'官杀干{gans[i]}象主{_GAN_HANGYE.get(gans[i],"")}')
    if not details:
        details.append('无明显官命做功，行业未明')

    return {
        'primary': primary,
        'by_combo': by_combo,
        'by_ganxiang': by_ganxiang,
        'details': details,
    }


# ───────────────────── 层次量化 + 有根判据（高级篇 8.3） ─────────────────────

def detect_guansha_yougen(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """官杀有根判据（高级篇 8.3）：官杀地支见根=实权落实，虚透天干无根=虚名。

    官杀（克我者）五行在地支本气/中气见同五行，即为有根；仅透天干而地支无根
    为「虚透」，主名气荣誉、非实权管理之职。复用于军官层次与官命层次量化。

    Returns:
        {
          'you_gen': bool, 'xutou': bool, 'root_pillars': [str],
          'gan_pillars': [str], 'desc': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    root_pillars: List[str] = []
    gan_pillars: List[str] = []
    if guan_wx:
        for i in range(4):
            if GAN_WX.get(gans[i]) == guan_wx:
                gan_pillars.append(PILLAR_NAMES_CN[i])
            if ZHI_WX.get(zhis[i]) == guan_wx:
                root_pillars.append(PILLAR_NAMES_CN[i])
                continue
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx <= 1 and GAN_WX.get(cg) == guan_wx:
                    root_pillars.append(PILLAR_NAMES_CN[i])
                    break
    you_gen = bool(root_pillars)
    xutou = bool(gan_pillars) and not you_gen
    if xutou:
        desc = f'官杀虚透天干（{"".join(gan_pillars)}柱），名气荣誉，非实权'
    elif you_gen:
        desc = f'官杀地支有根（{"".join(root_pillars)}柱），落实管理之职，掌实权'
    else:
        desc = '官杀不明现'
    return {
        'you_gen': you_gen,
        'xutou': xutou,
        'root_pillars': root_pillars,
        'gan_pillars': gan_pillars,
        'desc': desc,
    }


def assess_guanming_level(
    day_gan: str, gans: List[str], zhis: List[str],
    gongliang_result: Optional[Dict] = None,
) -> Dict:
    """官命层次量化（高级篇 8.3）：消费 gongliang 四档定性 + 有根判据。

    层次映射（段氏主流）：
      gongliang level 4 → 高官（厅局以上/极品）；3 → 中高（处级）；
      2 → 中（科级）；1 → 基层/员。
    叠加虚透判据：有根=实权落实；虚透=虚名（名誉职位非实权）。

    Returns:
        {
          'level': int, 'grade': str, 'you_gen': bool, 'xutou': bool,
          'authority': str,  # 实权/虚名/不明
          'desc': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gl = gongliang_result or {}
    level = gl.get('level', 0) if gl else 0
    grade_map = {4: '高官（厅局以上）', 3: '中高（处级）',
                 2: '中（科级）', 1: '基层/员'}
    grade = grade_map.get(level, '未定（缺 gongliang 功量层）')

    yg = detect_guansha_yougen(day_gan, gans or [], zhis or [])
    if yg['xutou']:
        authority = '虚名（名誉职位非实权）'
    elif yg['you_gen']:
        authority = '实权（落实管理之职）'
    else:
        authority = '不明'

    parts = [f'层次：{grade}', f'权柄：{authority}']
    parts.append(yg.get('desc', ''))
    return {
        'level': level,
        'grade': grade,
        'you_gen': yg['you_gen'],
        'xutou': yg['xutou'],
        'authority': authority,
        'desc': '；'.join(parts),
    }


# ───────────────────── 聚合 ─────────────────────

def _has_positive_guanming(
    day_gan: str, gans: List[str], zhis: List[str],
    combo: Dict, guancai: Dict,
) -> bool:
    """正向官命结构判据（反局否决门槛）。

    正向官命结构 = 官杀有根 / 官印相生(印化官杀) / 官带财帽 / 官禄格 / 印带官帽，
    任一命中即「正向」。「正向」须官杀为用神方成立--从强格官杀为忌神（逆势破格），
    其官杀有根/官印相生等属忌神现象，非正向官命（如贪财坐牢例：从强+反局=坐牢，
    虽具官杀有根/印化官杀，反局否决仍当生效）。身强/中和/从弱官杀可为用神，结构正向。

    Returns: True=有正向官命结构（反局不该否决官命）；False=无（反局可否决）。
    """
    from mangpai.subjective.yongshen import classify_strength
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return False
    strength = classify_strength(day_gan, gans, zhis)
    if strength == '从强':
        # 官杀为忌神，官命结构非正向，反局否决仍生效
        return False
    shengyong = combo.get('shengyong_huayong', []) or []
    if '印化官杀' in shengyong:      # 官印相生 / 杀印相生
        return True
    if '官禄格' in shengyong or '印带官帽' in shengyong:
        return True
    if guancai.get('found'):          # 官带财帽
        return True
    yg = detect_guansha_yougen(day_gan, gans, zhis)
    if yg.get('you_gen'):             # 官杀有根
        return True
    return False


def analyze_guanming(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    gongliang_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
) -> Dict:
    """官命综合：做功组合 + 管财官带帽 + 行业取象 + 层次量化。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    gongliang_result 缺省时自动调用 gongliang.analyze_gongliang 取四档定性。
    shensha_result: engine 透传的神煞结果（预留，官命尚未直接消费；备后用）。
    yunfan_result: 「当前运岁」反局切片（yunfan.current_fan_slice 产出，A1）。
      岁运反局入凶向否决链，与原局反局同受正向官命结构门槛保护。

    Returns:
        {
          'combo': {...},          # 制用四类+生用化用
          'guancai_daimao': {...}, # 管财的官带帽
          'hangye': {...},         # 行业取象
          'level': {...},          # 层次量化+有根判据
          'is_guanming': bool,
          'primary_combo': str,    # 主做功组合
          'primary_hangye': str,   # 主行业
          'summary': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    combo = classify_guanming_combo(day_gan, gans or [], zhis or [], relations)
    guancai = detect_guancai_daimao(day_gan, gans or [], zhis or [])
    hangye = classify_hangye_xiang(day_gan, gans or [], zhis or [], combo)

    # gongliang 缺省自调（只读消费，不改功量层）
    gl = gongliang_result
    if gl is None:
        try:
            from mangpai.subjective.gongliang import analyze_gongliang
            from mangpai.subjective.zuogong_confirm import analyze_zuogong
            zg = analyze_zuogong(
                day_gan, zhis[PILLAR_KEYS.index('day')],
                gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
            )
            gl = analyze_gongliang(zg, day_gan, gans, zhis)
        except Exception:
            gl = {}
    level = assess_guanming_level(day_gan, gans or [], zhis or [], gl)

    # ── 官命否决（P0 B 反 over-fire）：反局/牢狱/比劫夺财破财/过河拆桥破财
    # 任一凶向命中即否决官命（坐牢的、破财的、乞丐不当官）。凶向信号缺省自调
    # zhengfan/laoyu/R1（engine 未透传 laoyu，calib 直调亦可用）。
    direction = assess_direction_signals(
        day_gan, gans or [], zhis or [],
        relations=relations, gongliang_result=gl,
        yunfan_result=yunfan_result,
    )
    is_guanming_raw = bool(combo.get('is_guanming', False))
    all_reasons = direction.get('reasons', [])
    # 反局否决加门槛：反局 + 无正向官命结构 -> 才否决官命。
    # 正向官命结构（官杀有根/官印相生/官带财帽等，见 _has_positive_guanming）任一命中
    # 即保留官命判断，避免反局判据对印带官帽/七杀入墓等正当官命的系统性误否决。
    # 岁运反局（A1）与原局反局同受门槛保护（岁运双冲/三刑可为正当官命之应期触发，
    # 如厅级例壬午年升）；破财否决（比劫夺财/过河拆桥）不受门槛约束：破财/乞丐本非官命。
    veto_reasons = list(all_reasons)
    if direction.get('fanju') and is_guanming_raw and \
            _has_positive_guanming(day_gan, gans or [], zhis or [], combo, guancai):
        veto_reasons = [r for r in veto_reasons
                        if not r.startswith('反局') and not r.startswith('岁运')]
    vetoed = is_guanming_raw and bool(veto_reasons)
    is_guanming = is_guanming_raw and not vetoed
    if vetoed:
        # 否决后层次/权柄降为非官命
        level = dict(level)
        level['grade'] = '非官命（凶向否决）'
        level['authority'] = '无（反局/牢狱/破财否决官命）'
        level['desc'] = '；'.join(
            [f'层次：{level["grade"]}', f'权柄：{level["authority"]}']
            + (['否决依据：' + '；'.join(veto_reasons)] if veto_reasons else [])
        )
    elif not is_guanming:
        # 非官命（无官做功结构、未触发凶向否决）：官阶（高官/处级/科级/基层）为
        # 官命专用映射，对非官命（纯财命/商贾/普通人）标官阶属误标，统一纠正为
        # 「非官命」（与凶向否决分支一致）；实权权柄同步纠正为无/不明。有根/虚透
        # 判据仍保留于 desc 作参考，但不改官阶标签。
        level = dict(level)
        level['grade'] = '非官命'
        if level.get('authority') == '实权（落实管理之职）':
            level['authority'] = '无（非官命）'
        kept = [p for p in level.get('desc', '').split('；')
                if p and not p.startswith('层次：') and not p.startswith('权柄：')]
        level['desc'] = '；'.join(
            [f'层次：{level["grade"]}', f'权柄：{level["authority"]}'] + kept
        )

    all_combos = combo.get('zhiyong_combos', []) + combo.get('shengyong_huayong', [])
    primary_combo = all_combos[0] if all_combos else ''
    summary = (f'官命：{("是" if is_guanming else "否")}；'
               f'主做功：{primary_combo or "无"}；主行业：{hangye.get("primary","未明")}；'
               f'{level.get("desc","")}')
    if guancai.get('found'):
        summary += '；管财的官（官带财帽）'

    return {
        'combo': combo,
        'guancai_daimao': guancai,
        'hangye': hangye,
        'level': level,
        'is_guanming': is_guanming,
        'vetoed': vetoed,
        'veto_reasons': veto_reasons,
        'primary_combo': primary_combo,
        'primary_hangye': hangye.get('primary', ''),
        'summary': summary,
    }


__all__ = [
    'classify_guanming_combo',
    'detect_guancai_daimao',
    'classify_hangye_xiang',
    'detect_guansha_yougen',
    'assess_guanming_level',
    'analyze_guanming',
]
