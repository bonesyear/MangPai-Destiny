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
    kong_wang: Any = None,
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

    over-fire 收口（G0-G5，段氏书锚，v2 平衡口径）：
      G0 辅助做功（auxiliary，宾位远隔）不计入官命组合（与 R2 同口径）；
      G1 劫刃制财属财命域模式（争财/竞争求财），不计入官命组合；
      G2 杀刃类（劫刃制官杀/官杀制比劫）须杀刃力量相当——「七杀制刃，要杀刃
         力量相当」（高级篇5.2）：平衡=弱方/强方>=0.5（1v1 即相当，非必双多），
         悬殊（如官3劫1 官制劫太过=被官管之平民）不成格；从格（从强去杀/从弱
         杀为用）豁免——悬殊正为去忌/顺势；
      G3 制官杀得官类（伤食制官杀/劫刃制官杀）：官弱（本气<2）为用神而被制
         =「伤官制官不为官」（授课 li263），不入官命；官为忌（身弱/从强）或
         伤官去官格（食伤明现>=3，朱元璋/qi19）者，去官反得官，保留；
      G4 象法类（官禄格/印带官帽）单独不立官命，须制用组合佐证（真做功）；
         印化官杀（杀印相生）为化用真功，单独可立；
      G5 杀刃类另须官杀有制化（食伤制杀/印化杀明现）：「杀先天无制无化，
         杀为忌，冲开则凶」（郝批初中例），无印无食伤则杀为忌非官命；
         从格（从强杀本为忌/从弱杀为用）豁免。

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

    # 官杀/比劫本气力（G2/G3 用：干支主气计数，空亡支不计，日干不计入比劫）
    _kw_zhis: List[str] = []
    if kong_wang:
        if isinstance(kong_wang, list):
            _kw_zhis = kong_wang
        elif isinstance(kong_wang, dict):
            _kw_zhis = kong_wang.get('zhi', kong_wang.get('zhis', [])) or []
    guan_strength = 0
    bijie_strength = 0
    for i in range(4):
        g_wx = GAN_WX.get(gans[i], '')
        z_wx = ZHI_WX.get(zhis[i], '') if zhis[i] not in _kw_zhis else ''
        if g_wx == guan_wx:
            guan_strength += 1
        if z_wx == guan_wx:
            guan_strength += 1
        if i != 2 and g_wx == day_wx:
            bijie_strength += 1
        if z_wx == day_wx:
            bijie_strength += 1

    # 官杀之制化（G5 用）：明现食伤（制杀）或印（化杀）干支主气。
    # 郝批（授课·壬子丙午壬辰丁未例）：「辰杀先天无制无化，辰杀为忌，冲开则凶」
    # ——杀刃组合中杀无制化则为忌，非官命（士卒/牢狱，非军官）。
    shishang_wx = WX_SHENG.get(day_wx, '')
    yin_wx = ''
    for _w, _gen in WX_SHENG.items():
        if _gen == day_wx:
            yin_wx = _w
            break
    has_shishang = False
    has_yin = False
    for i in range(4):
        if GAN_WX.get(gans[i], '') == shishang_wx or (
                zhis[i] not in _kw_zhis and ZHI_WX.get(zhis[i], '') == shishang_wx):
            has_shishang = True
        if GAN_WX.get(gans[i], '') == yin_wx or (
                zhis[i] not in _kw_zhis and ZHI_WX.get(zhis[i], '') == yin_wx):
            has_yin = True
    sha_you_zhihua = has_shishang or has_yin

    # G2/G3/G5 的方向与格局参数
    from mangpai.subjective.yongshen import classify_strength
    strength = classify_strength(day_gan, gans, zhis)
    cong_ge = strength in ('从强', '从弱')          # 从格（G2/G3/G5 豁免）
    # 官杀为忌（G3 去官得官保留）：身弱忌克/从强逆势；从弱 subtype 歧义
    # （从财喜官/从儿忌官），统一由 cong_ge 豁免，不在此列
    guan_wei_ji = strength in ('身弱', '从强')
    shishang_strength = sum(
        1 for i in range(4)
        if GAN_WX.get(gans[i], '') == shishang_wx
        or (zhis[i] not in _kw_zhis and ZHI_WX.get(zhis[i], '') == shishang_wx)
    )
    # 杀刃平衡（G2：弱方/强方>=0.5 为相当，1v1 即相当非必双多）
    sharen_balanced = (
        min(guan_strength, bijie_strength) * 2 >= max(guan_strength, bijie_strength)
    )

    # 制用四类（含反向 + 合制）：遍历制用/合制动作，按 from/to 主气十神大类归类。
    # 段氏制用 = 五行相克（制=克），十神大类间克链双向皆可为功：
    #   伤食制官杀（食伤克官杀）/ 官杀制比劫（官杀克比劫，七杀制羊刃）/
    #   印制伤食（印克食伤）/ 财制印（财克印）/ 劫刃制财（比劫克财）。
    # 合制（合以制之，如伤官合杀、食神合官）同按 from/to 大类匹配，标「合制·」前缀。
    # guan_pattern=False 者（劫刃制财）属财命域，只记录不计入官命（G1）；
    # sha_ren=True 者（杀刃类）须杀刃力量相当（G2）；制官杀类须官有力（G3）。
    _CONTROL_PATTERNS = [
        ('食伤', '官杀', '伤食制官杀', '制官{verb}官，主执法/管理/技术官',
         {'guan_pattern': True, 'sha_ren': False, 'zhi_guan': True}),
        ('比劫', '官杀', '劫刃制官杀', '制杀{verb}权，主军警/武职/竞争掌权',
         {'guan_pattern': True, 'sha_ren': True, 'zhi_guan': True}),
        ('官杀', '比劫', '官杀制比劫', '七杀制羊刃{verb}权，主军警/武职/威权',
         {'guan_pattern': True, 'sha_ren': True, 'zhi_guan': False}),
        ('印', '食伤', '印制伤食', '印制伤官护官，{verb}官，主文职/行政',
         {'guan_pattern': True, 'sha_ren': False, 'zhi_guan': False}),
        ('财', '印', '财制印', '财印相战制用',
         {'guan_pattern': True, 'sha_ren': False, 'zhi_guan': False}),
        ('比劫', '财', '劫刃制财', '劫刃制财{verb}财，主争财/竞争求财',
         {'guan_pattern': False, 'sha_ren': False, 'zhi_guan': False}),
    ]
    for a in wa:
        if a.get('auxiliary'):
            continue  # G0：辅助做功（宾位远隔）不计入官命组合
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
        for pf, pt, pkey, pdesc, pflag in _CONTROL_PATTERNS:
            if f_cat == pf and t_cat == pt:
                key = ('合制·' if is_he else '') + pkey
                # G1：劫刃制财属财命域模式，不计入官命组合；
                # 例外：比劫孤（<=1，不结党非劫夺——参 R1 比劫2柱口径）且官杀
                # 有根（>=2）者，制财为「我取财」非争财，仍计入（日禄归时贵命例）
                if not pflag['guan_pattern']:
                    if bijie_strength <= 1 and guan_strength >= 2:
                        if key not in combos:
                            combos.append(key)
                            details.append(
                                f'{key}（比劫孤{bijie_strength}不结党、官杀有根'
                                f'{guan_strength}，制财非劫夺，计入）：'
                                + pdesc.format(verb=verb))
                    else:
                        details.append(f'{key}（财命域模式，不入官命）')
                    break
                # G3：官弱（<2）为用神被制=伤官制官不为官；官为忌/从格/伤官去官
                # 格（食伤>=3）者去官得官，保留
                if pflag['zhi_guan'] and guan_strength < 2 \
                        and not guan_wei_ji and not cong_ge and shishang_strength < 3:
                    details.append(
                        f'{key}：官杀弱（{guan_strength}）为用神被制，'
                        '伤官制官不为官，不入官命')
                    break
                # G2：杀刃类须力量相当（弱/强>=0.5），从格豁免
                if pflag['sha_ren'] and not sharen_balanced and not cong_ge:
                    details.append(
                        f'{key}：杀刃力量悬殊（官杀{guan_strength}/'
                        f'比劫{bijie_strength}），制之太过/刃旺无制，不成官格')
                    break
                # G5：杀刃类另须官杀有制化（食伤制杀/印化杀明现），从格豁免
                if pflag['sha_ren'] and not sha_you_zhihua and not cong_ge:
                    details.append(
                        f'{key}：杀无制化（无印无食伤），杀为忌非官命'
                        '（郝批：杀先天无制无化，冲开则凶），不成官格')
                    break
                if key not in combos:
                    combos.append(key)
                    act_label = '合制' if is_he else '制用'
                    details.append(
                        f'{key}（{direction}，{act_label}）：{a.get("desc","")}，'
                        + pdesc.format(verb=verb)
                    )
                break

    # G9 自合柱合制（48期康熙型）：非日柱之激活自合柱，柱上官星干被坐支
    # 藏干合绊=制（「年干甲被年支午中己合绊了，是制官得官」）。官为忌神
    # （身弱/从强，guan_wei_ji）者合制得官——与 G3 去官得官同口径；官为
    # 用神被合绊者失官不录（属 R3 财/官失用域）。自合不并入 zuogong 通用
    # 合做功源（柱内干支合，非柱间做功），故在此单独检测。
    try:
        from mangpai.objective.zihe import detect_zihe
        _zihe_g = detect_zihe(gans, zhis)
        for _rec in _zihe_g.get('pillars') or []:
            if _rec.get('is_day') or not _rec.get('activated'):
                continue
            _gi = _rec['idx']
            if GAN_WX.get(gans[_gi], '') != guan_wx:
                continue  # 柱上之干非官杀不论
            if not guan_wei_ji:
                continue  # 官非忌神（身强官为用/从弱官为喜），合绊失官不录得官
            key = '合制·自合制官'
            if key not in combos:
                combos.append(key)
                details.append(
                    f'{key}（{_rec["key_cn"]}柱{_rec["gz"]}自合，{gans[_gi]}官被支中'
                    f'{_rec["he_shen"]}合绊=制）：官为忌神被合制，制官得官'
                    f'（48期康熙例：甲被午中己合绊，制官得官，级别省级）')
    except Exception:
        pass

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

    # 官命成立：制用组合或印化官杀（化用真功）命中（且官杀明现/印权在场）。
    # G4：象法类（官禄格/印带官帽）单独不立官命，须制用组合佐证（段氏象法
    # 须落在做功上，空象无实）——带帽书例（壬寅己酉壬申甲辰）本具印制伤食/
    # 官杀制比劫做功，不受影响；纯带帽无做功者（如司机例）不立官命。
    shengyong_core = [s for s in shengyong if s == '印化官杀']
    xiangfa_only = [s for s in shengyong if s in ('官禄格', '印带官帽')]
    if xiangfa_only and not combos and not shengyong_core:
        details.append(
            f'象法类（{"/".join(xiangfa_only)}）单独无做功组合佐证，不立官命（G4）')
    is_guanming = bool(combos or shengyong_core) and (
        has_guansha or bool(shengyong))

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
    kong_wang: Any = None,
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

    combo = classify_guanming_combo(day_gan, gans or [], zhis or [], relations,
                                    kong_wang=kong_wang)
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

    # ── 官命否决（P0 B 反 over-fire + M1）：反局/牢狱/比劫夺财破财/过河拆桥破财
    # /忌神制用神(R2)/用神被合绊(R3) 任一凶向命中即否决官命（坐牢的、破财的、
    # 乞丐不当官）。凶向信号缺省自调 zhengfan/laoyu/R1/R2/R3（engine 未透传
    # laoyu，calib 直调亦可用）。
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
    # 如厅级例壬午年升）；忌神制用神/用神被合绊（M1 R2/R3）同属「方向受损」类，
    # 与反局同受门槛保护（正向结构成立者，用忌小疵不夺其官）；破财否决（比劫夺财/
    # 过河拆桥）不受门槛约束：破财/乞丐本非官命。
    veto_reasons = list(all_reasons)
    if (direction.get('fanju') or direction.get('yongshen_xiong')
            or direction.get('mingju_xiong')) \
            and is_guanming_raw and \
            _has_positive_guanming(day_gan, gans or [], zhis or [], combo, guancai):
        veto_reasons = [r for r in veto_reasons
                        if not r.startswith(('反局', '岁运', '忌神制用神', '用神被合绊',
                                             '伤官见官', '财生杀', '官杀入墓'))]
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
