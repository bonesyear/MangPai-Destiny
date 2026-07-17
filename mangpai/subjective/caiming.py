"""
caiming - 盲派财命定性·主观层（subjective）

理论来源：段建业《盲派中级命理学》第八章「财命专辑」（源文 2593-3675 行）
          第一节「财富看法」(2598-3035) + 第二节「取财方法」(3036-3675)
核心思想：盲派财命不只看财星，而看「什么当财」+「如何取财」。财星未必是财，
          禄/食伤/官杀皆可当财；取财方式定贫富性质（体力/智力/经营/风险/工薪）。

财富看法五式（第一节）：
  1. 财星当财：财星明现，常规财富（最基础）。
  2. 禄神当财：局无财星（或财弱）而见禄 -> 禄=身体力行，体力/工薪取财。
     禄是日主的身体、临官位，禄当财即用身体劳动换财。
  3. 伤食当财：局无财星而有食伤 -> 食伤=技术/智力，智力取财（食伤生财之源）。
  4. 官杀当财两式（源文2817-2819：官多财少->财统官，财多官少->官统财，二者皆官杀当财）：
       财统官--官杀多而财少，财统御官，官杀当财（七杀当财，量级高于财当财）；
       官统财--财多而官杀少，官统御财，官杀当财（七杀当财，量级高于财当财）。
  5. 过河拆桥：主位（日支或时支）财生宾位官杀，宾官又被宾字合/制 -> 主位财
     过河（生宾官）后桥（宾官）被拆，财流失/被他人所得，主破财。核心是「宾字
     合/制桥（宾官）」，合用对称（六合/暗合两端皆试），制用取被制方；官统财/
     财统官（主制宾官得财）与之互斥，不并存。

取财五法（第二节）：经营 / 风险 / 智力 / 体力 / 工薪
  - 经营：财星明现 + 合财/制财做功，商人经营取财；
  - 风险：七杀当财 / 劫刃羊刃取财，风险求财（投机/武职/偏门）；
  - 智力：食伤当财 / 食伤生财，技术智力取财；
  - 体力：禄神当财，身体力行体力取财；
  - 工薪：官杀/印星 + 制官得官/印，正当职业工薪取财。

消费关系：
  - objective.zuogong_detect.detect_relations（合/制关系，过河拆桥/取财做功用）
  - objective.tiyong.classify_tiyong（体用，财官分类）
  - objective.binzhu.analyze_binzhu（主宾，过河拆桥方向用）
  - subjective.xiangfa_ops（带帽/制象，财带官帽/制财得财用）
  - objective.constants（LU/五行生克/藏干）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：官统财/财统官的「多/少」阈值为工程化启发式（段氏以气势论，非计数定量）；
          取财五法优先级为段氏主流口径归纳。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    LU, CANG_GAN_MANGPAI, TOMB_MAP, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.binzhu import analyze_binzhu
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.objective.muku import analyze_muku
from mangpai.subjective.yongshen import assess_direction_signals

_YANG_GANS = set('甲丙戊庚壬')
_PILLAR_NAME: Dict[str, str] = {k: v for k, v in zip(PILLAR_KEYS, ['年柱', '月柱', '日柱', '时柱'])}
_ZHI_CONTROL: Set[str] = {'冲', '克', '穿', '刑', '破'}
_HE_CONTROL: Set[str] = {'天干合', '地支合', '暗合', '半合'}


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


def _wx_to_cat(day_gan: str, wx: str) -> str:
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx or not wx:
        return ''
    if wx == day_wx:
        return '比劫'
    if WX_SHENG.get(day_wx) == wx:
        return '食伤'
    if WX_SHENG.get(wx) == day_wx:
        return '印'
    if WX_KE.get(day_wx) == wx:
        return '财'
    if WX_KE.get(wx) == day_wx:
        return '官杀'
    return ''


def _pillar_cats(day_gan: str, gans: List[str], zhis: List[str]) -> List[Set[str]]:
    """逐柱十神大类集合（天干 + 藏干，含余气；用于做功/制位判定）。"""
    out: List[Set[str]] = []
    for i in range(4):
        cats: Set[str] = set()
        if i < len(gans) and gans[i]:
            c = _shishen_cat(_compute_shishen(day_gan, gans[i]))
            if c:
                cats.add(c)
        if i < len(zhis) and zhis[i]:
            cats.add(_wx_to_cat(day_gan, ZHI_WX.get(zhis[i], '')))  # 地支主气五行
            for cg, _ in get_canggan_mangpai(zhis[i]):
                c2 = _shishen_cat(_compute_shishen(day_gan, cg))
                if c2:
                    cats.add(c2)
        cats.discard('')
        out.append(cats)
    return out


def _cat_prominence(day_gan: str, gans: List[str], zhis: List[str]) -> List[Dict[str, str]]:
    """逐柱 -> {十神大类: 气位}，气位 ∈ {'gan','benqi','zhongqi','yuqi'}。

    天干='gan'；藏干按本/中/余气序。同一大类取最高气位（gan>benqi>zhongqi>yuqi）。
    用于「明现」判定：明现 = gan/benqi/zhongqi（透干或本中气），余气(yuqi)不算明现。
    """
    order = {'gan': 0, 'benqi': 1, 'zhongqi': 2, 'yuqi': 3}
    out: List[Dict[str, str]] = []
    for i in range(4):
        best: Dict[str, str] = {}
        if i < len(gans) and gans[i]:
            c = _shishen_cat(_compute_shishen(day_gan, gans[i]))
            if c:
                best[c] = 'gan'
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _qi) in enumerate(get_canggan_mangpai(zhis[i])):
                c = _shishen_cat(_compute_shishen(day_gan, cg))
                if not c:
                    continue
                prom = {0: 'benqi', 1: 'zhongqi', 2: 'yuqi'}.get(idx, 'yuqi')
                if c not in best or order[prom] < order[best[c]]:
                    best[c] = prom
        out.append(best)
    return out


_MINGXIAN = {'gan', 'benqi', 'zhongqi'}  # 明现气位（透干/本气/中气），余气不算


def _pos_pillar(pos: str) -> str:
    return pos.split('_')[0] if pos else ''


def _is_zhu(pos: str) -> bool:
    return _pos_pillar(pos) in ('day', 'hour')


def _pos_element(pos: str, gans: List[str], zhis: List[str]) -> str:
    """pos 的五行（gan 取天干五行，zhi 取地支主气五行）。"""
    pk = _pos_pillar(pos)
    if pk not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(pk)
    if pos.endswith('_gan'):
        return GAN_WX.get(gans[idx], '') if idx < len(gans) else ''
    return ZHI_WX.get(zhis[idx], '') if idx < len(zhis) else ''


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


def _ensure_muku(gans: List[str], zhis: List[str], muku_result: Optional[Dict]) -> Dict:
    """缺 muku 结果时自调 analyze_muku（需 gans 判透干引拔）。"""
    if muku_result is not None:
        return muku_result
    if len(zhis) != 4:
        return {}
    try:
        return analyze_muku(zhis, gans)
    except Exception:
        return {}


def _detect_caiku(
    day_gan: str, gans: List[str], zhis: List[str], muku_result: Optional[Dict],
) -> List[Dict]:
    """财库开闭检测：墓库所收五行含日主之财(我克=WX_KE[day_wx])者为财库。

    消费 analyze_muku 的 tombs[].status：
      开库 -> 墓中之财复出，开财库主大发（发财之象）；
      闭库 -> 财被收藏，闭财库主守财储蓄；
      墓库(未开未闭) -> 财入库，守而不发。
    段氏：财喜藏（入库守财）亦喜开（开库发财），开闭状态定财之聚散。

    Returns:
        财库记录列表，每项 {zhi, status, pillar, view, desc}。
        view ∈ {'开财库', '闭财库', '财入库'}。
    """
    if not (day_gan and len(zhis) == 4):
        return []
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')  # 我克=财五行
    if not cai_wx:
        return []
    mu = _ensure_muku(gans, zhis, muku_result)
    out: List[Dict] = []
    for tomb in mu.get('tombs', []) or []:
        z = tomb.get('zhi', '')
        entombed = tomb.get('element_tombed') or []
        if cai_wx not in entombed:
            continue  # 非财库
        status = tomb.get('status', '墓库')
        if status == '开库':
            view = '开财库'
            desc = f'{tomb.get("pillar", "")}{z}为财库（{cai_wx}）逢开，墓中之财复出，主大发'
        elif status == '闭库':
            view = '闭财库'
            desc = f'{tomb.get("pillar", "")}{z}为财库（{cai_wx}）逢闭，财被收藏，主守财储蓄'
        else:
            view = '财入库'
            desc = f'{tomb.get("pillar", "")}{z}为财库（{cai_wx}）未开，财入库守而不发'
        out.append({'zhi': z, 'status': status, 'pillar': tomb.get('pillar', ''),
                    'view': view, 'desc': desc})
    return out


# ───────────────────── 财富看法 ─────────────────────

def classify_caifu_view(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
    muku_result: Optional[Dict] = None,
) -> Dict:
    """财富看法定性：什么当财。

    判定序（段氏第一节口径）：
      1. 财星明现 -> 财星当财（基础）；
      2. 局无财星而见禄 -> 禄神当财（体力/工薪）；
      3. 局无财星而有食伤 -> 伤食当财（技术/智力）；
      4. 官杀当财两式：官杀多（≥2位）且制官杀成立 ->
         财统官（官杀>财）/ 官统财（财>官杀），二者皆官杀当财；
      5. 过河拆桥：主位财生宾官、宾官被宾字合/制 -> 制尽（净制）为富格（巨富，
         高级篇口径），制不尽为破财（财流失，中级篇口径）；与官统财/财统官互斥
         （主制宾官得财则不判破财）。主取优先序：官统财/财统官 > 过河拆桥 > 财星 >
         禄 > 食伤；财库开闭为聚散信号并列（不竞争主取）。
    一局可多重命中（如既有财星又官杀当财），全部列出，标主取。

    Returns:
        {
          'primary': str,            # 主取财看法
          'views': [str],            # 全部命中看法
          'cai_count': int,          # 财位计数
          'guan_count': int,         # 官杀位计数
          'has_cai': bool,
          'has_lu': bool,
          'has_shishang': bool,
          'guohe_chaiqiao': bool,    # 过河拆桥
          'guohe_chaiqiao_type': str|None,  # '富格'(制尽巨富)/'破财'(制不尽)
          'details': [str],          # 各看法依据
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
        return {'primary': '', 'views': [], 'details': ['四柱不全，无法定性']}

    cats = _pillar_cats(day_gan, gans, zhis)
    prom = _cat_prominence(day_gan, gans, zhis)
    # 明现计数：财/官杀 须透干或本/中气（余气不算明现）
    cai_count = sum(1 for p in prom if '财' in p and p['财'] in _MINGXIAN)
    guan_count = sum(1 for p in prom if '官杀' in p and p['官杀'] in _MINGXIAN)
    has_cai = cai_count > 0
    has_shishang = any('食伤' in p and p['食伤'] in _MINGXIAN for p in prom)

    # 禄检测：日干之禄在局（自身原神到场）；或任一柱天干之禄落**主位**（日时）
    # 段氏「禄在主位可做功」--主位禄方为日主取财之工具，宾位禄为他人之禄不直接当财。
    day_lu_zhi = LU.get(day_gan, '')
    all_zhis_set = set(z for z in zhis if z)
    has_lu = bool(day_lu_zhi) and day_lu_zhi in all_zhis_set
    if not has_lu and len(zhis) == 4:
        zhu_zhis = {zhis[2], zhis[3]}  # 日支、时支（主位）
        for g in gans:
            lz = LU.get(g, '')
            if lz and lz in zhu_zhis:
                has_lu = True
                break

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    views: List[str] = []
    details: List[str] = []

    # 1. 财星当财
    if has_cai:
        views.append('财星当财')
        details.append(f'局有财星（{cai_count}位），财星明现当财')

    # 2. 禄神当财（局无财星或财弱，见禄）
    if has_lu and (not has_cai or cai_count <= 1):
        views.append('禄神当财')
        details.append('禄=身体力行，禄当财主体力/工薪取财')

    # 3. 伤食当财（局无财星，有食伤）
    if has_shishang and not has_cai:
        views.append('伤食当财')
        details.append('局无财星而有食伤，食伤=技术/智力，智力取财')

    # 4. 官杀当财两式（官杀多且制官杀成立）
    zhi_guan_controlled = False  # 宾官被制（主制宾官）
    for a in wa:
        if a.get('type') in (_ZHI_CONTROL | _HE_CONTROL):
            to_pos = a.get('to_pos', '')
            from_pos = a.get('from_pos', '')
            to_cats = set()
            pk_to = _pos_pillar(to_pos)
            if pk_to in PILLAR_KEYS:
                idx = PILLAR_KEYS.index(pk_to)
                to_cats = cats[idx]
            if '官杀' in to_cats and _is_zhu(from_pos) and not _is_zhu(to_pos):
                zhi_guan_controlled = True
                break
    if guan_count >= 2 and zhi_guan_controlled:
        if guan_count > cai_count:
            views.append('财统官')
            details.append(f'官杀多（{guan_count}位）而财少（{cai_count}位），财统官，官杀当财（七杀当财量级高）')
        elif cai_count > guan_count:
            views.append('官统财（官杀当财）')
            details.append(f'财多（{cai_count}位）而官杀少（{guan_count}位），官统财，官杀当财（七杀当财量级高）')

    # 5. 过河拆桥（制尽=富格巨富 / 制不尽=破财，高级篇分键）
    # 官统财/财统官（主制宾官得财）与过河拆桥（宾字拆宾官破财）为对偶互斥财命定式：
    # 主位已制宾官得财（官杀当财）则不再判过河拆桥破财，避免矛盾破财信号。
    guohe = {}
    if '财统官' not in views and '官统财（官杀当财）' not in views:
        guohe = _detect_guohe_chaiqiao(day_gan, gans, zhis, cats, wa)
    guohe_type = guohe.get('type') if guohe else None
    if guohe:
        views.append(f'过河拆桥·{guohe_type}')
        details.append(guohe['detail'])

    # 6. 财库开闭（消费 muku：墓库所收五行含日主之财者为财库，开闭定财之聚散）
    caiku = _detect_caiku(day_gan, gans, zhis, muku_result)
    has_open_caiku = False
    for ck in caiku:
        views.append(ck['view'])
        details.append(ck['desc'])
        if ck['view'] == '开财库':
            has_open_caiku = True

    # 主取：官统财/财统官（官杀当财量级最高）> 过河拆桥（财命定式，宾官被拆）>
    # 财星 > 禄 > 食伤；财库开闭为聚散信号并列（不竞争主取）。
    primary = ''
    for v in ('官统财（官杀当财）', '财统官'):
        if v in views:
            primary = v
            break
    if not primary:
        guohe_view = next((v for v in views if v.startswith('过河拆桥')), '')
        if guohe_view:
            primary = guohe_view
    if not primary:
        for v in ('财星当财', '禄神当财', '伤食当财'):
            if v in views:
                primary = v
                break

    return {
        'primary': primary,
        'views': views,
        'cai_count': cai_count,
        'guan_count': guan_count,
        'has_cai': has_cai,
        'has_lu': has_lu,
        'has_shishang': has_shishang,
        'guohe_chaiqiao': bool(guohe),
        'guohe_chaiqiao_type': guohe_type,  # '富格'(制尽巨富)/'破财'(制不尽)/None
        'caiku': caiku,                      # 财库开闭记录（消费 muku）
        'has_open_caiku': has_open_caiku,    # 开财库（发财）信号
        'details': details,
    }


def _guan_mingxian_positions(
    day_gan: str, gans: List[str], zhis: List[str], guan_wx: str,
) -> Set[str]:
    """官杀明现位（透干或地支本/中气）的 pos 集合。"""
    pos: Set[str] = set()
    for idx, pk in enumerate(PILLAR_KEYS):
        if idx >= len(gans):
            continue
        if GAN_WX.get(gans[idx]) == guan_wx:
            pos.add(f'{pk}_gan')
        if idx < len(zhis) and zhis[idx]:
            for cg, src in get_canggan_mangpai(zhis[idx]):
                if src in ('本气', '中气') and GAN_WX.get(cg) == guan_wx:
                    pos.add(f'{pk}_zhi')
                    break
    return pos


def _controlled_guan_positions(
    wa: List[Dict], gans: List[str], zhis: List[str], guan_wx: str,
) -> Set[str]:
    """被制官杀位（制用/合制动作 to_pos，目标五行=官五行）。"""
    pos: Set[str] = set()
    for a in wa:
        if a.get('type') not in (_ZHI_CONTROL | _HE_CONTROL):
            continue
        to_pos = a.get('to_pos', '')
        if to_pos and _pos_element(to_pos, gans, zhis) == guan_wx:
            pos.add(to_pos)
    return pos


def _is_zhi_jin(
    day_gan: str, gans: List[str], zhis: List[str],
    cats: List[Set[str]], wa: List[Dict], guan_wx: str,
) -> bool:
    """过河拆桥宾官是否制尽（净制判据）。

    段氏过河拆桥分两路（高级篇财命章）：
      - 制尽（净制）：宾官被制且官杀方俱制无残存同党 -> 制官得财，
        七杀当财量级，过河拆桥富格（巨富）。
      - 制不尽：宾官被制但官杀残存 -> 财过河生宾官、宾官未制尽反夺财，
        破财（中级篇口径）。
    工程化启发式：以「官杀明现位俱为制用/合制目标（无残存）」为制尽判据；
    成势制尽须贼神捕神/净制模块判党势，此处保守以位置覆盖度兜底，可能偏宽。
    """
    mingxian = _guan_mingxian_positions(day_gan, gans, zhis, guan_wx)
    if not mingxian:
        return False
    controlled = _controlled_guan_positions(wa, gans, zhis, guan_wx)
    return mingxian <= controlled  # 明现官杀位俱被制方为制尽


def _detect_guohe_chaiqiao(
    day_gan: str, gans: List[str], zhis: List[str],
    cats: List[Set[str]], wa: List[Dict],
) -> Dict:
    """过河拆桥检测：主位财生宾官、宾官被宾字合/制，按制尽/制不尽分键。

    段氏过河拆桥核心是「宾字合/制桥（宾官）」：主位（日支或时支）财 -> 生 ->
    宾位（年/月）官杀（五行：财五行生官五行），且该宾官被另一宾字合/制 ->
    财过河生宾官、桥（宾官）被拆。
    - 主位财：放宽「日支必为财」硬前置 -> 日支或时支有财即可（主位财过河）；
    - 合用对称：六合/暗合/半合 from/to 无方向语义，两端皆试（宾官可在 from 端）；
      制用方向明确，取 to_pos（被制方=宾官）。
    官统财/财统官（主制宾官得财）与本检测互斥，由调用方据 views 守门，避免矛盾破财信号。

    Returns:
        {} 或 {'type': '富格'|'破财', 'detail': str}
        富格=制尽净制（巨富，高级篇）；破财=制不尽（财流失，中级篇）。
    """
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx:
        return {}
    cai_wx = WX_KE.get(day_wx, '')     # 财五行=我克
    guan_wx = WX_KE_ME.get(day_wx, '')  # 官五行=克我
    if not cai_wx or not guan_wx:
        return {}
    # 财生官须五行成立：WX_SHENG[财五行]==官五行
    if WX_SHENG.get(cai_wx) != guan_wx:
        return {}

    # 主位（日支或时支）有财：段氏过河拆桥核心是「宾字合/制桥（宾官）」，
    # 「日支财生宾官」为经典「财过河」结构；时支同主位，时支财过河生宾官亦成立。
    # 放宽「日支必为财」硬前置 -> 主位有财即可，避免漏检时支财过河之桥被拆。
    if len(zhis) != 4:
        return {}

    def _zhi_has_wx(zhi: str, wx: str) -> bool:
        return (ZHI_WX.get(zhi) == wx) or any(
            GAN_WX.get(cg) == wx for cg, _ in get_canggan_mangpai(zhi)
        )

    cai_pos_cn = ''
    cai_zhi = ''
    for pk in ('day', 'hour'):
        idx = PILLAR_KEYS.index(pk)
        if idx < len(zhis) and zhis[idx] and _zhi_has_wx(zhis[idx], cai_wx):
            cai_pos_cn = PILLAR_NAMES_CN[idx]
            cai_zhi = zhis[idx]
            break
    if not cai_pos_cn:
        return {}

    # 宾位（年/月）官杀：天干或地支主气为官五行（明现官，余气藏官不算过河宾官）
    bin_guan_pillars: List[int] = []
    for idx in (0, 1):  # 年、月
        if idx >= len(gans):
            continue
        gan_is_guan = GAN_WX.get(gans[idx]) == guan_wx
        zhi_is_guan = (idx < len(zhis) and ZHI_WX.get(zhis[idx]) == guan_wx)
        if gan_is_guan or zhi_is_guan:
            bin_guan_pillars.append(idx)
    if not bin_guan_pillars:
        return {}

    # 该宾官被另一宾字合/制（桥被拆）；两端皆须宾位（宾字合/制宾官）。
    # 制用方向明确（from 制方 -> to 被制方=宾官）；合用（天干合/地支合/暗合/半合）
    # 为对称关系，from/to 无方向语义，须两端皆试--宾官可在 from 端（如卯戌合，
    # 引擎记 from=年卯 to=月戌，宾官卯在 from 端），仅查 to_pos 致六合对称方向漏检。
    # 制/合之目标五行须为官五行（克同柱他五行不算制官，避免藏官柱被克财误判）。
    found_action: Optional[Dict] = None
    bridge_pos = ''
    for a in wa:
        if a.get('type') not in (_ZHI_CONTROL | _HE_CONTROL):
            continue
        from_pos, to_pos = a.get('from_pos', ''), a.get('to_pos', '')
        if _is_zhu(from_pos) or _is_zhu(to_pos):
            continue  # 须宾字合/制宾官（两端皆宾位）
        is_he = a.get('type') in _HE_CONTROL
        # 制用取 to_pos（被制方）；合用对称，两端皆试
        candidates = [to_pos, from_pos] if is_he else [to_pos]
        hit = ''
        for pos in candidates:
            pk = _pos_pillar(pos)
            if pk not in PILLAR_KEYS:
                continue
            if PILLAR_KEYS.index(pk) not in bin_guan_pillars:
                continue
            if _pos_element(pos, gans, zhis) != guan_wx:
                continue
            hit = pos
            break
        if hit:
            found_action = a
            bridge_pos = hit
            break
    if not found_action:
        return {}

    bridge_pk = _pos_pillar(bridge_pos)
    bridge_idx = PILLAR_KEYS.index(bridge_pk) if bridge_pk in PILLAR_KEYS else -1
    pos_cn = PILLAR_NAMES_CN[bridge_idx] if bridge_idx >= 0 else ''
    desc = found_action.get('desc', '制')
    # 制尽/制不尽分键（高级篇富格 vs 中级篇破财）
    if _is_zhi_jin(day_gan, gans, zhis, cats, wa, guan_wx):
        return {'type': '富格', 'detail': (
            f'{cai_pos_cn}{cai_zhi}（财）生宾位{pos_cn}官杀，宾官又被宾字{desc}且制尽（净制），'
            f'过河拆桥富格——制官得财（七杀当财量级），巨富')}
    return {'type': '破财', 'detail': (
        f'{cai_pos_cn}{cai_zhi}（财）生宾位{pos_cn}官杀，宾官被宾字{desc}但制不尽'
        f'（官杀残存），过河拆桥，财流失破财')}


# ───────────────────── 取财五法 ─────────────────────

def classify_qucai_method(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
    caifu_view: Optional[Dict] = None,
) -> Dict:
    """取财五法分类：经营/风险/智力/体力/工薪。

    依据「什么当财」+「做功方式」定主取财方法：
      - 体力：禄神当财 -> 禄=身体力行；
      - 智力：伤食当财 / 食伤生财 -> 技术/智力；
      - 经营：财星当财 + 合财/制财做功 -> 商人经营；
      - 风险：官杀当财 / 劫刃羊刃取财 -> 风险求财（投机/武职）；
      - 工薪：官杀/印 + 制官得官/印 -> 正当职业工薪。
    多重命中并列，标主取。

    Returns:
        {
          'primary': str,        # 主取财法
          'methods': [str],      # 全部命中取财法
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
        return {'primary': '', 'methods': [], 'details': ['四柱不全']}

    if caifu_view is None:
        caifu_view = classify_caifu_view(day_gan, gans, zhis, relations)
    views = caifu_view.get('views', [])
    cats = _pillar_cats(day_gan, gans, zhis)
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    # 做功：是否合财/制财（主制宾财 or 合财）
    control_cai = False  # 制财
    he_cai = False       # 合财
    for a in wa:
        t = a.get('type', '')
        to_pos = a.get('to_pos', '')
        from_pos = a.get('from_pos', '')
        to_pk = _pos_pillar(to_pos)
        if to_pk not in PILLAR_KEYS:
            continue
        to_idx = PILLAR_KEYS.index(to_pk)
        if '财' in cats[to_idx]:
            if t in _ZHI_CONTROL and _is_zhu(from_pos) and not _is_zhu(to_pos):
                control_cai = True
            if t in _HE_CONTROL:
                he_cai = True
    # 食伤生财做功
    shishang_sheng_cai = any(a.get('type') == '食伤' for a in wa)
    # 制官得官（主制宾官，非官统财语境）
    zhi_guan_for_gong = False
    for a in wa:
        if a.get('type') in _ZHI_CONTROL:
            to_pk = _pos_pillar(a.get('to_pos', ''))
            if to_pk in PILLAR_KEYS and '官杀' in cats[PILLAR_KEYS.index(to_pk)]:
                if _is_zhu(a.get('from_pos', '')) and not _is_zhu(a.get('to_pos', '')):
                    zhi_guan_for_gong = True
                    break
    # 劫刃制财
    jieyang_zhi_cai = False
    for a in wa:
        if a.get('type') in _ZHI_CONTROL:
            from_pk = _pos_pillar(a.get('from_pos', ''))
            to_pk = _pos_pillar(a.get('to_pos', ''))
            if from_pk in PILLAR_KEYS and to_pk in PILLAR_KEYS:
                if '比劫' in cats[PILLAR_KEYS.index(from_pk)] and '财' in cats[PILLAR_KEYS.index(to_pk)]:
                    jieyang_zhi_cai = True
                    break

    # 视图优先序 -> 取财法映射；primary_method 跟随 primary_view
    # 官统财/财统官二者皆官杀当财（源文2819），取财法同为风险（七杀当财，投机/武职/偏门）
    view_method_order = [
        ('官统财（官杀当财）', '风险', '财多官少，官统财，官杀当财（制杀得财），风险求财（投机/武职/偏门）'),
        ('财统官', '风险', '官多财少，财统官，官杀当财（制杀得财），风险求财（投机/武职/偏门）'),
        ('财星当财', '经营', None),  # detail 视制/合而定，下方补
        ('禄神当财', '体力', '禄神当财，禄=身体力行，体力取财'),
        ('伤食当财', '智力', '食伤当财/食伤生财，技术智力取财'),
    ]

    methods: List[str] = []
    details: List[str] = []
    for view, method, detail in view_method_order:
        if view not in views:
            continue
        if view == '财星当财':
            if control_cai or he_cai:
                d = '财星明现且' + ('制财' if control_cai else '') + ('合财' if he_cai else '') + '做功，商人经营取财'
            else:
                d = '财星明现，倾向经营取财'
        elif view == '伤食当财' and shishang_sheng_cai and not any('伤食当财' in v for v in views):
            continue
        else:
            d = detail
        if method not in methods:
            methods.append(method)
            details.append(d)

    # 食伤生财做功（无食伤当财看法时补智力）
    if shishang_sheng_cai and '智力' not in methods:
        methods.append('智力')
        details.append('食伤生财做功，技术智力取财')
    # 劫刃制财 -> 风险
    if jieyang_zhi_cai and '风险' not in methods:
        methods.append('风险')
        details.append('劫刃制财，风险求财')
    # 制官得官（非官杀当财）-> 工薪
    if zhi_guan_for_gong and '官统财（官杀当财）' not in views and '财统官' not in views and '工薪' not in methods:
        methods.append('工薪')
        details.append('制官得官，正当职业工薪取财')

    if not methods:
        methods.append('未明')
        details.append('无明显取财做功，取财方式不明')

    primary = methods[0]
    return {'primary': primary, 'methods': methods, 'details': details}


# ───────────────────── 制不尽当财 + 财命层级四阶（高级篇 ch8） ─────────────────────

def detect_zhibujin_dangcai(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """制不尽当财（高级篇 ch8）：官杀被制但不尽，残存官杀作财看。

    段氏 ch8 核心对偶：制尽=权（官命，见 guanming），制不尽=当财（财命）。
    即官杀被制用/合制动作引动，但未净制（明现官杀位有残存未被制覆盖），
    则该残存官杀不当权而「当财」——制杀不尽反取其财，量级低于制尽得权，
    高于寻常财星当财。

    与 classify_caifu_view 的「官统财」区别：官统财须官杀多（≥2位）且被制；
    本函数不要求多寡，只判「被制且制不尽」即当财，是更基础的制不尽口径。

    Returns:
        {
          'found': bool, 'guan_wx': str, 'controlled_but_not_jin': bool,
          'detail': str,
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
        return {'found': False, 'detail': '四柱不全'}
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    if not guan_wx:
        return {'found': False, 'detail': '五行不全'}
    cats = _pillar_cats(day_gan, gans, zhis)
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    mingxian = _guan_mingxian_positions(day_gan, gans, zhis, guan_wx)
    controlled = _controlled_guan_positions(wa, gans, zhis, guan_wx)
    # 被制且制不尽：有明现官杀被制动作，但明现位未俱被覆盖
    has_control = bool(controlled & mingxian)
    is_jin = bool(mingxian) and mingxian <= controlled
    found = has_control and not is_jin
    detail = ''
    if found:
        resid = mingxian - controlled
        detail = (f'官杀（{guan_wx}五行）被制但制不尽（残存{len(resid)}位未净制），'
                  f'残存官杀当财看——制杀不尽反取其财，量级低于制尽得权、高于财星当财')
    return {
        'found': found,
        'guan_wx': guan_wx,
        'controlled_but_not_jin': found,
        'detail': detail,
    }


def assess_caiming_level(
    day_gan: str, gans: List[str], zhis: List[str],
    gongliang_result: Optional[Dict] = None,
    caifu_view: Optional[Dict] = None,
    muku_result: Optional[Dict] = None,
    direction_signals: Optional[Dict] = None,
) -> Dict:
    """财命层级四阶（高级篇 ch8）：巨富 / 富 / 小康 / 贫。

    量级来源（四叠加）：
      1. gongliang 四档定性 wealth_grade/level（功量层主定基阶）；
      2. 财源清浊：官杀当财（官统财/制不尽当财）量级最高，财星当财次之，
         禄/食伤当财偏下（体力/智力取财量级有限）；
      3. 制尽程度：制尽净制上浮一阶，制不尽/过河拆桥破财下浮一阶；
      4. 财库开闭（消费 muku）：开财库（墓中之财复出）上浮一阶主大发，
         闭财库/财入库持平（守财储蓄，聚而不散）。

    Returns:
        {
          'tier': str,            # 巨富/富/小康/贫
          'base_level': int,      # gongliang level
          'wealth_grade': str,    # gongliang 富量级
          'adjust': str,          # 上浮/下浮/持平
          'desc': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gl = gongliang_result or {}
    base_level = gl.get('level', 0) if gl else 0
    wealth_grade = gl.get('wealth_grade', '') if gl else ''

    if caifu_view is None:
        caifu_view = classify_caifu_view(day_gan, gans or [], zhis or [],
                                         muku_result=muku_result)
    views = caifu_view.get('views', [])
    # 财源量级：官杀当财（官统财/财统官皆属）> 财星 > 禄/食伤
    has_guancai = any(v.startswith('官统财') or v.startswith('财统官')
                      or v.startswith('过河拆桥·富格') for v in views)
    has_zhibujin = False
    try:
        has_zhibujin = detect_zhibujin_dangcai(day_gan, gans or [], zhis or []).get('found', False)
    except Exception:
        pass
    has_lu_or_shishang = any(v in views for v in ('禄神当财', '伤食当财'))
    guohe_pocai = caifu_view.get('guohe_chaiqiao_type') == '破财'
    # 财库开闭（已由 classify_caifu_view 据传入 muku_result 检出，亦可直接读 caiku）
    has_open_caiku = bool(caifu_view.get('has_open_caiku'))

    # 基阶：level 4→富(偏巨富), 3→富, 2→小康, 1→贫/普通
    # 用 1-4 整数阶表示 贫(1)/小康(2)/富(3)/巨富(4)
    tier_idx = max(1, min(4, base_level)) if base_level else 2
    adjust = '持平'
    # 财源上浮
    if (has_guancai or has_zhibujin) and tier_idx < 4:
        tier_idx += 1
        adjust = '上浮（官杀当财量级高）'
    elif has_lu_or_shishang and tier_idx > 1:
        tier_idx -= 1
        adjust = '下浮（禄/食伤当财量级有限）'
    # 制尽/破财调整
    if guohe_pocai and tier_idx > 1:
        tier_idx -= 1
        adjust = (adjust + '；' if adjust != '持平' else '') + '下浮（过河拆桥破财）'
    # 开财库上浮（墓中之财复出主大发）
    if has_open_caiku and tier_idx < 4:
        tier_idx += 1
        adjust = (adjust + '；' if adjust != '持平' else '') + '上浮（开财库，墓中之财复出主大发）'
    # 吉凶方向封顶（P0 A）：反局/牢狱/比劫夺财破财/过河拆桥破财任一凶向命中，
    # 财命按严重度封顶--severe（比劫夺财严重/牢狱高）->贫(1)，余->小康下(2)。
    # 段氏功量层只判「做了什么」，凶向反哺「该不该做」：制用神/反局破财不得
    # 记为富（如第9期比劫夺财清家荡产、第8期贪财坐牢）。
    ds = direction_signals or {}
    if ds.get('fanju') or ds.get('pocai') or ds.get('guohe_pocai'):
        cap = 1 if ds.get('pocai_severe') else 2
        if tier_idx > cap:
            tier_idx = cap
            sev = '严重' if cap == 1 else '一般'
            adjust = (adjust + '；' if adjust != '持平' else '') + \
                f'下浮封顶{cap}阶（{sev}凶向：' + '；'.join(ds.get('reasons') or []) + '）'
        # 富档跟随下浮后的 tier（避免坐牢破财仍标千万-亿级荒谬）；岁运反局
        # 命中者即便阶位未动（本在低位），富档亦不再标注——乞丐不标千万级。
        if tier_idx < base_level or ds.get('suiyun_fanju'):
            wealth_grade = ''
    tier_map = {1: '贫', 2: '小康', 3: '富', 4: '巨富'}
    tier = tier_map.get(tier_idx, '小康')
    parts = [f'财命层级：{tier}']
    if wealth_grade:
        parts.append(f'功量富档：{wealth_grade}')
    if adjust != '持平':
        parts.append(adjust)
    return {
        'tier': tier,
        'base_level': base_level,
        'wealth_grade': wealth_grade,
        'adjust': adjust,
        'desc': '；'.join(parts),
    }


# ───────────────────── 聚合 ─────────────────────

def analyze_caiming(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    gongliang_result: Optional[Dict] = None,
    muku_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    yunfan_result: Optional[Dict] = None,
) -> Dict:
    """财命综合：财富看法 + 取财方法 + 制不尽当财 + 层级四阶。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    gongliang_result 缺省时自动调用 gongliang.analyze_gongliang 取四档定性。
    muku_result 缺省时自动调用 muku.analyze_muku 取财库开闭（缺省自调，只读消费）。
    shensha_result: engine 透传的神煞结果（预留，财命尚未直接消费；备后用）。
    yunfan_result: 「当前运岁」反局切片（yunfan.current_fan_slice 产出，A1）。
      岁运反局命中即入凶向否决链（层级封顶/富档抹除），与原局反局同口径。

    Returns:
        {
          'caifu_view': {...},    # 财富看法（什么当财，含财库开闭）
          'qucai_method': {...},  # 取财五法
          'zhibujin_dangcai': {...},  # 制不尽当财
          'level': {...},        # 层级四阶
          'primary_view': str,    # 主取财看法
          'primary_method': str,  # 主取财法
          'tier': str,           # 财命层级
          'summary': str,        # 一句话财命定性
          'guohe_chaiqiao': bool, # 过河拆桥破财信号
          'caiku': [...],        # 财库开闭记录（消费 muku）
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    cv = classify_caifu_view(day_gan, gans or [], zhis or [], relations,
                              muku_result=muku_result)
    qm = classify_qucai_method(day_gan, gans or [], zhis or [], relations, cv)
    zbj = detect_zhibujin_dangcai(day_gan, gans or [], zhis or [], relations)

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
    # 凶向信号（反局/牢狱/比劫夺财/过河拆桥破财 + 岁运反局 A1）--缺省自调，供层级封顶
    direction = assess_direction_signals(
        day_gan, gans or [], zhis or [],
        relations=relations, gongliang_result=gl,
        yunfan_result=yunfan_result,
    )
    # 过河拆桥破财由 caifu_view 检出，补入方向信号
    if cv.get('guohe_chaiqiao_type') == '破财':
        direction = dict(direction)
        direction['guohe_pocai'] = True
        direction['pocai'] = True
        direction.setdefault('reasons', [])
        if '过河拆桥破财' not in direction['reasons']:
            direction['reasons'] = list(direction['reasons']) + ['过河拆桥破财']
    level = assess_caiming_level(day_gan, gans or [], zhis or [], gl, cv,
                                  muku_result=muku_result,
                                  direction_signals=direction)

    summary = f'主取财看法：{cv.get("primary","未明")}；主取财法：{qm.get("primary","未明")}；{level.get("desc","")}'
    if cv.get('guohe_chaiqiao'):
        summary += '；伴过河拆桥破财信号'
    if zbj.get('found'):
        summary += '；制不尽当财（残存官杀作财看）'
    caiku = cv.get('caiku', [])
    for ck in caiku:
        summary += f'；{ck["view"]}（{ck["zhi"]}）'

    return {
        'caifu_view': cv,
        'qucai_method': qm,
        'zhibujin_dangcai': zbj,
        'level': level,
        'primary_view': cv.get('primary', ''),
        'primary_method': qm.get('primary', ''),
        'tier': level.get('tier', ''),
        'summary': summary,
        'guohe_chaiqiao': cv.get('guohe_chaiqiao', False),
        'caiku': caiku,
    }


__all__ = [
    'classify_caifu_view',
    'classify_qucai_method',
    'detect_zhibujin_dangcai',
    'assess_caiming_level',
    'analyze_caiming',
]
