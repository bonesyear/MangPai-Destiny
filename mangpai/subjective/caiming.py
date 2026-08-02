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

贫富三要素（M2 财星源头/路径检测，段氏「八字有财，伤食是其原神」）：
  1. 财星是否有原神：食伤明现生财=有源头；无原神且财不在主位（日/时）=浮财
     （虚透不聚）-> 层级降一阶；
  2. 生财路径是否畅通：明现财星被紧贴合绊（受害方口径同 yongshen R3）或
     财星本气支入墓未开 -> 各降一阶（官杀当财/制不尽当财路径不适用）；
  3. 制财得财 vs 制不净破财：过河拆桥（制尽=富格/制不尽=破财）已有，与浮财/
     阻通同汇入 level.blockers；tier 输出扩展为「档位 + 生财路径(path) + 阻因
     (blockers)」三件套。

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
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME, TIAN_GAN_HE,
    LU, CANG_GAN_MANGPAI, TOMB_MAP, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
    SAN_HE, BAN_HE, LIU_CHONG, XING_PAIRS,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.binzhu import analyze_binzhu
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.objective.muku import analyze_muku
from mangpai.subjective.yongshen import assess_direction_signals, _LIUHE_VICTIMS

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


def _tomb_chong_xing_open(zhi: str, zhis: List[str]) -> bool:
    """墓库支是否被他支冲/刑触动（动库，不论透干引拔）。

    段氏「不冲不刑是墓（死的）」之逆——逢冲/刑则库动而非死墓；
    《中级》「丑未冲开一点点」明示冲开无须透干（透干引拔管库中余气
    「引出方有用」，是另一层：全开出尽 vs 动而不尽）。
    """
    for z in zhis:
        if not z or z == zhi:
            continue
        if (z, zhi) in LIU_CHONG or (zhi, z) in LIU_CHONG \
                or (z, zhi) in XING_PAIRS or (zhi, z) in XING_PAIRS:
            return True
    return False


def _detect_zhiku_decai(
    day_gan: str, gans: List[str], zhis: List[str],
    muku_result: Optional[Dict] = None,
) -> Dict:
    """制库得财（《段氏理象学》制例一，奥纳西斯书锚）。

    月令墓库被主位（日/时）支冲/刑而开（muku 判开库=透干引拔，库物出而
    可用），且库中藏干同含「财」与「财之原神（食伤）」——书「丑未冲，
    主位之未杀库制月令丑土，月令之财与财的原神被制」「开库的同时将库
    中的伤官与财星全制服了，所以能成巨富」：财与原神同库俱制 = 净制
    （量级同制尽），为制尽级财命定式，非禄/食伤当财之量级有限路径。

    判据（四要件俱备方立，宁窄勿滥）：
      1. 月令支为墓库（提纲得令之库，量级大）；
      2. 被主位（日支/时支）冲或刑（主位制宾库，主得之；自刑伏吟不论）；
      3. muku 判开库（透干引拔，库中之物出而可用）；
      4. 库藏干同含财与食伤（财与原神同库，冲制则俱制=净制）。

    Returns:
        {'found': bool, 'tomb': str, 'detail': str}
    """
    out = {'found': False, 'tomb': '', 'detail': ''}
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return out
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')       # 财五行（我克）
    yuan_wx = WX_SHENG.get(day_wx, '')   # 财之原神=食伤五行（我生）
    month_zhi = zhis[1] if len(zhis) > 1 else ''
    if not (cai_wx and yuan_wx and month_zhi and month_zhi in TOMB_MAP):
        return out
    # 要件2：主位（日/时）支冲/刑月令库（自刑伏吟不论——段氏开库须他支冲/刑
    # 「丑未冲开一点点」、丑戌未三刑；辰辰/午午/酉酉/亥亥自刑即伏吟，主重复
    # 痛苦而非开库，与 _tomb_chong_xing_open 排同支口径对齐。qi07 辰辰自刑
    # 过冲实证：书判「平·发财后赔光欠债」，自刑开库直推巨富 overshoot）
    opener = ''
    for z in (zhis[2], zhis[3]):
        if z and z != month_zhi and (
                (z, month_zhi) in LIU_CHONG or (month_zhi, z) in LIU_CHONG
                or (z, month_zhi) in XING_PAIRS or (month_zhi, z) in XING_PAIRS):
            opener = z
            break
    if not opener:
        return out
    # 要件3：muku 判开库（透干引拔）
    mu = _ensure_muku(gans, zhis, muku_result)
    opened = any(t.get('zhi') == month_zhi and t.get('status') == '开库'
                 for t in (mu.get('tombs') or []))
    if not opened:
        return out
    # 要件4：库藏干同含财与食伤（财与原神同库）
    ku_gans = {cg for cg, _q in get_canggan_mangpai(month_zhi)}
    has_cai_in_ku = any(GAN_WX.get(cg, '') == cai_wx for cg in ku_gans)
    has_yuan_in_ku = any(GAN_WX.get(cg, '') == yuan_wx for cg in ku_gans)
    if not (has_cai_in_ku and has_yuan_in_ku):
        return out
    out['found'] = True
    out['tomb'] = month_zhi
    out['detail'] = (f'月令{month_zhi}库藏财（{cai_wx}）与原神食伤（{yuan_wx}），'
                     f'主位{opener}冲/刑开库，开库同制财与原神俱制——'
                     f'制库得财，量级同制尽（理象学制例一奥纳西斯「月令之财与财的'
                     f'原神被制…有四层功量，所以成巨富」）')
    return out


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


def _assess_caixing_path(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    prom: List[Dict[str, str]],
    wa: List[Dict],
    muku_result: Optional[Dict],
) -> Dict:
    """财星源头与生财路径评估（段氏贫富三要素之前二，财星当财路径专用）。

    段氏口径：
      - 「八字有财，伤食是其原神」（《中级》财命专辑）——财有原神（食伤明现）
        为有源头之财（投资/经营之本）；无原神为浮财，财来财去不聚。
      - 财星须归主位（日/时柱）方为我有；虚透宾位（年/月）而无主位之根，
        为他人之财、过手之财。
      - 生财路径阻断：明现财星被紧贴合绊（段氏「两个字紧贴相合为绊…失去
        原性」，受害方口径同 yongshen R3 之 _LIUHE_VICTIMS），或财星本气支
        入墓未开（财被收藏、流通受阻；开库则墓中财复出，不论阻）。
      - 透干财之五合绊仅判年×月（他干紧贴互绊）；日干合财为日主合财得财
        （合财格），不论绊（同 R3 口径）。
      - 冲/穿做功参与抑制：财方已入局交战者未「失去原性」，不论绊（同 R3）。

    Returns:
        {
          'has_yuanshen': bool,   # 财有原神（食伤明现）
          'zhuwei_cai': bool,     # 主位（日/时柱）有明现财
          'fucai': bool,          # 浮财：有明现财但无原神且不在主位
          'heban': [str],         # 财星被合绊明细
          'rumu': [str],          # 财星入墓未开明细
          'blockers': [str],      # 阻因汇总（浮财/合绊/入墓）
        }
    """
    out: Dict = {'has_yuanshen': False, 'zhuwei_cai': False, 'fucai': False,
                 'heban': [], 'rumu': [], 'hecai_work': False, 'blockers': [],
                 'rumu_bankai': False}
    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    if not cai_wx or len(gans) != 4 or len(zhis) != 4:
        return out

    # 明现财位（透干/本气/中气）；主位=日/时柱
    mingxian_gan: Set[int] = set()   # 透干财的柱 index
    mingxian_zhi: Set[int] = set()   # 本/中气含财的柱 index
    for i, p in enumerate(prom):
        if '财' in p and p['财'] in _MINGXIAN:
            if p['财'] == 'gan':
                mingxian_gan.add(i)
            else:
                mingxian_zhi.add(i)
    if not (mingxian_gan or mingxian_zhi):
        return out  # 无明现财，财源路径不成立（禄/食伤/官杀当财路径另行判定）

    out['has_yuanshen'] = any('食伤' in p and p['食伤'] in _MINGXIAN for p in prom)
    out['zhuwei_cai'] = bool((mingxian_gan | mingxian_zhi) & {2, 3})
    out['fucai'] = (not out['has_yuanshen']) and (not out['zhuwei_cai'])
    if out['fucai']:
        out['blockers'].append('财星无原神且不在主位（浮财无源，财来财去不聚）')

    # 冲/穿做功参与抑制（同 R3：已入局交战之财未失去原性，不论绊）；
    # 合做功抑制：同一合对若被 zuogong 检为非辅助「合用/合制」做功，则该合为
    # 得财之道（段氏合财格/合制得财），不再论绊（解「合绊 vs 合做功」口径张力，
    # M1 备案：R3 天干五合与段氏合制/合象做功的张力在财命侧以此收口）。
    engaged: Set[str] = set()
    he_work_pairs: Set[frozenset] = set()
    for a in wa:
        if a.get('auxiliary'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if a.get('type', '') in ('冲', '穿'):
            for pos in (fp, tp):
                if pos:
                    engaged.add(pos)
        if a.get('type', '') in _HE_CONTROL and fp and tp:
            he_work_pairs.add(frozenset((fp, tp)))

    # 财星被合绊（仅取本气为财之支与透干财；藏干中气之财不单独论绊）
    heban: List[str] = out['heban']
    # G9 自合柱财绊（48期）：非日柱之激活自合柱，柱上之干被坐支藏干合绊
    # 失用——该干为财者财被合绊（ans12-下岗穷命 壬戌时，戌逢辰冲激活，
    # 壬财被戌中丁合绊，「想赚钱又得不到钱」）。日柱自合不在此列（日主
    # 自合=日主合财/合官做功，见下方 hecai_work）。
    # 豁免（48期「财来就我」）：支中合神与日主同五行者（日主/比劫=我方），
    # 财星被我方合入=财合日主、反为得财，不论合绊失用，视同合财做功
    # （li263 戊日主年柱癸巳：巳中戊合癸财=财来就我；li128 己日主月柱
    # 癸巳同例）。合神非我方者（壬戌之丁火合壬财）仍论绊。
    _cailai_jiuwo = False
    try:
        from mangpai.objective.zihe import detect_zihe
        _zihe = detect_zihe(gans, zhis)
        for _prec in _zihe.get('pillars') or []:
            if _prec.get('is_day') or not _prec.get('activated'):
                continue
            _gi = _prec.get('idx', -1)
            if not (_gi >= 0 and GAN_WX.get(gans[_gi], '') == cai_wx
                    and _gi in mingxian_gan):
                continue
            if GAN_WX.get(_prec.get('he_shen', ''), '') == day_wx:
                _cailai_jiuwo = True
                continue
            _zg = gans[_gi] + zhis[_gi]
            heban.append(f'{PILLAR_NAMES_CN[_gi]}干{gans[_gi]}（财）坐{_zg}自合柱，'
                         f'被支中藏干合绊失用（48期天地合）')
    except Exception:
        _zihe = {}
    for i in range(3):
        a, b = zhis[i], zhis[i + 1]
        if not a or not b:
            continue
        victims = _LIUHE_VICTIMS.get(frozenset(a + b))
        if not victims:
            continue
        for j, z in ((i, a), (i + 1, b)):
            pk = PILLAR_KEYS[j]
            pk_other = PILLAR_KEYS[i + 1 if j == i else i]
            if (z in victims and ZHI_WX.get(z, '') == cai_wx
                    and f'{pk}_zhi' not in engaged
                    and frozenset((f'{pk}_zhi', f'{pk_other}_zhi')) not in he_work_pairs):
                heban.append(f'{PILLAR_NAMES_CN[j]}支{z}（财）被{a}{b}合绊，失去原性')
    g0, g1 = gans[0], gans[1]
    if g0 and g1 and TIAN_GAN_HE.get(g0) == g1:
        for j, g in ((0, g0), (1, g1)):
            pk = PILLAR_KEYS[j]
            pk_other = PILLAR_KEYS[1 - j]
            if (GAN_WX.get(g, '') == cai_wx and j in mingxian_gan
                    and f'{pk}_gan' not in engaged
                    and frozenset((f'{pk}_gan', f'{pk_other}_gan')) not in he_work_pairs):
                heban.append(f'{PILLAR_NAMES_CN[j]}干{g}（财）被{g0}{g1}合绊，失去原性')
    if heban:
        out['blockers'].append('财星被合绊（' + '；'.join(heban) + '），生财路径阻断')

    # 合财做功（段氏：日主合财=直接承载财富；主位合宾财=合得他人之财，多主经商
    # 取利）：非辅助合动作一端为明现财位（透干财/本气财支）、另一端在主位或
    # 涉及日干的，为合财做功。
    cai_positions: Set[str] = set()
    for i in mingxian_gan:
        cai_positions.add(f'{PILLAR_KEYS[i]}_gan')
    for i in mingxian_zhi:
        if ZHI_WX.get(zhis[i], '') == cai_wx:
            cai_positions.add(f'{PILLAR_KEYS[i]}_zhi')
    hecai_work = False
    for fp, tp in he_work_pairs:
        ends = [fp, tp]
        if not any(p in cai_positions for p in ends):
            continue
        other = [p for p in ends if p not in cai_positions]
        if any(_is_zhu(p) for p in ends):
            hecai_work = True
            break
        if other and _is_zhu(other[0]):
            hecai_work = True
            break
    out['hecai_work'] = hecai_work or _cailai_jiuwo

    # G9 日主自合合财（48期「日主因合而从支」）：日主坐激活自合柱且支中
    # 合神为财者（戊子/甲午/壬午/丙戌/壬戌型日主），日主合财=直接承载财富
    # ——视同合财做功（例133 戊子日，身旺财旺，房地产倒卖发财）。
    try:
        _dz = (_zihe or {}).get('day_zihe')
        if _dz and _dz.get('activated'):
            if GAN_WX.get(_dz.get('he_shen', ''), '') == cai_wx:
                out['hecai_work'] = True
    except Exception:
        pass

    # 财星本气支入墓未开（开库则墓中财复出，不论阻；戌冲/刑开则不入墓，
    # muku.is_entomb 已特判）
    mu = _ensure_muku(gans, zhis, muku_result)
    tomb_status: Dict[str, str] = {t.get('zhi', ''): t.get('status', '')
                                   for t in (mu.get('tombs') or [])}
    rumu: List[str] = out['rumu']
    for rel in (mu.get('tomb_relations') or []):
        fz = (rel.get('from') or {}).get('zhi', '')
        tz = (rel.get('to') or {}).get('zhi', '')
        if not fz or ZHI_WX.get(fz, '') != cai_wx:
            continue
        if tomb_status.get(tz) == '开库':
            continue  # 开库发财，非阻
        if tz and _tomb_chong_xing_open(tz, zhis):
            # 冲/刑动库半开（《中级》「丑未冲开一点点」「不冲不刑是墓」）：
            # 库逢冲/刑则动而非死墓，财不死藏——不论「收藏难取」之阻；
            # 唯无透干引拔则财未全出（理象学「墓中余气透干引出方有用，
            # 不透干也无用」），记 rumu_bankai——基阶不压、升档不升。
            out['rumu_bankai'] = True
            continue
        rumu.append(rel.get('relation', f'{fz}入{tz}墓'))
    if rumu:
        out['blockers'].append('财星入墓未开（' + '；'.join(rumu) + '），财被收藏难取')
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
    # 明现计数：财/官杀 须透干或本/中气（余气不算明现）。
    # 库财豁免（段氏第4期「此造八字无财」）：墓库所藏之财（藏干五行入该支
    # 之墓者，如未中乙木为木之墓藏、戌中丁火为火之墓藏）为「库财」，归
    # 财库收藏口径（见下方 caiku 开闭），不计明财——丁未丙午庚申丁丑造
    # 未中乙木不以财论，书判「八字无财」以禄当财。支本气财不在此限
    # （辰戌丑未本气皆土，土为其体非所藏）。
    # 库财活化三式（库财复出/成局/得令则计明现）：
    #   (a) 库逢冲刑开（muku 判开库）——「墓中之财复出，主大发」；
    #   (b) 库支参与三合/半合而局五行=财五行——库财成局透出（须 BAN_HE
    #       正半合，拱合不论）；
    #   (c) 库支居月令——提纲得令、库藏当令（金昌盛造：丑月令金库为用神，
    #       巳酉丑金局发财，书以丑土/土金为用不论无财）。
    _cai_wx = WX_KE.get(GAN_WX.get(day_gan, ''), '')
    _active_ku: Set[str] = set()
    if _cai_wx:
        try:
            _mu = _ensure_muku(gans, zhis, muku_result)
            for _tb in _mu.get('tombs', []) or []:
                if _tb.get('status') == '开库' and _cai_wx in (_tb.get('element_tombed') or []):
                    _active_ku.add(_tb.get('zhi', ''))
        except Exception:
            pass
        for _he, _wx in SAN_HE.items():
            if _wx == _cai_wx and all(z in zhis for z in _he):
                _active_ku.update(z for z in _he if z in TOMB_MAP)
        for _he, _wx in BAN_HE.items():
            if _wx == _cai_wx and _he[0] in zhis and _he[1] in zhis:
                _active_ku.update(z for z in _he if z in TOMB_MAP)
        if len(zhis) > 1 and zhis[1] in TOMB_MAP and _cai_wx in TOMB_MAP.get(zhis[1], []):
            _active_ku.add(zhis[1])
    cai_count = 0
    for i in range(4):
        if i < len(gans) and gans[i] and _wx_to_cat(day_gan, GAN_WX.get(gans[i], '')) == '财':
            cai_count += 1
            continue
        if i < len(zhis) and zhis[i]:
            if _wx_to_cat(day_gan, ZHI_WX.get(zhis[i], '')) == '财':
                cai_count += 1
                continue
            for idx, (cg, _q) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break  # 余气不算明现
                if _wx_to_cat(day_gan, GAN_WX.get(cg, '')) == '财':
                    if GAN_WX.get(cg, '') not in TOMB_MAP.get(zhis[i], []) \
                            or zhis[i] in _active_ku:
                        cai_count += 1
                    break
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

    # 2. 禄神当财（局无财星，见禄）——段氏「八字无财时，禄可以当财看」
    # （《中级》禄神当财节；第4期「此造八字无财…以禄当财」）。财弱（1位）
    # 不在此列——财在则以财论，禄为辅助（防李嘉诚类巨富局误挂禄财下浮）。
    if has_lu and not has_cai:
        views.append('禄神当财')
        details.append('禄=身体力行，禄当财主体力/工薪取财')

    # 3. 伤食当财（局无财星，有食伤）
    if has_shishang and not has_cai:
        views.append('伤食当财')
        details.append('局无财星而有食伤，食伤=技术/智力，智力取财')

    # 4. 官杀当财两式（官杀多且制官杀成立）。
    # 财统官须财在（cai_count>=1）：段氏「官多财少，财可统官」——无财则
    # 无可统之财、无财生官之相连（注：少指只有一个，且财官必须相连，即
    # 财生官），零财之局官杀当财不成立（《中级》己酉戊辰壬申癸卯造：
    # 辰被卯穿「坏了，不为官了」，以伤官当财，非财统官）。
    zhi_guan_controlled = False  # 宾官被制（主制宾官）
    for a in wa:
        if a.get('auxiliary'):
            continue  # 非做功动作（宾位干克/宾位入墓等 M4 扩展检出）不证"被制"
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
        if guan_count > cai_count and cai_count >= 1:
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

    # 7. 财星源头与生财路径（段氏贫富三要素：原神/主位定浮实，合绊/入墓定阻通）
    caixing_path = _assess_caixing_path(day_gan, gans, zhis, prom, wa, muku_result)
    if caixing_path.get('has_yuanshen') and has_cai:
        details.append('财有原神（食伤明现生财），财有源头')
    for blk in caixing_path.get('blockers') or []:
        details.append('阻因：' + blk)

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
        'caixing_path': caixing_path,        # 财星源头/路径（原神/主位/合绊/入墓）
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

    制尽判据重修（P1，trainset b67 实锤锚）：主位（日/时）支中**藏干**官
    不计「残存同党」——藏而不透之官附于主位（日支/时支本中气所藏，如日支
    财支中气藏官=财之附属），非宾官夺财之党；主位**透干**官杀明现有力，
    仍计残存（qi05 时干癸杀透干，制不尽成立）。b67 森田健（辛戊己癸/卯戌
    亥酉）：日支亥中气甲（官）被旧判据计为残存 -> 误判制不尽破财（gold
    富·壬申癸酉年发财）；修法后宾官卯俱被月戌合制 -> 制尽富格。
    """
    mingxian = _guan_mingxian_positions(day_gan, gans, zhis, guan_wx)
    mingxian = {p for p in mingxian
                if not (p.endswith('_zhi') and _pos_pillar(p) in ('day', 'hour'))}
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
    # 枭神生劫·不劳而获（标注级，不抢主取、不定档）：段氏诀「枭神生劫不劳
    # 而获」（11期贱命无赖「一生靠劫取他人财为生」），同诀系于虎应造
    # 「靠绊大款为生，也为个劳而获」（甲丁丙甲/寅卯寅午，同为枭透劫财明现）
    # ——枭神（偏印）透干生劫财，劫财得枭生则有源，靠劫取/合绊（绊大款）
    # 他人之财为生，即合绊取财/不劳而获型。判据：偏印透干 + 劫财明现
    # （透干或支本气）。仅作取财性质识别（methods 尾位标注），不参与定档
    # ——档位仍由功量/财源主线判定（ans12 已批损失面与批B R3 豁免口径不动）。
    _xiao_tou = any(_compute_shishen(day_gan, g) == '偏印' for g in gans if g)
    _jiecai_mx = any(_compute_shishen(day_gan, g) == '劫财' for g in gans if g) or \
        any(_compute_shishen(day_gan, get_canggan_mangpai(z)[0][0]) == '劫财'
            for z in zhis if z)
    if _xiao_tou and _jiecai_mx and '不劳而获' not in methods:
        methods.append('不劳而获')
        details.append('枭神生劫，不劳而获——劫财得枭生有源，靠劫取/合绊'
                       '他人之财为生（段氏诀「枭神生劫不劳而获」，绊大款/依附取财型）')
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


def _zeishen_jingzhi(day_gan: str, gans: List[str], zhis: List[str]) -> bool:
    """贼神捕神净制判定（段氏理象学）：净=贼神原神俱制、制之干净，量级同制尽。

    zhibujin 封顶富的豁免判据——软依赖 zeishen_bushen，异常一律按不净（封顶）。
    """
    try:
        from mangpai.subjective.zeishen_bushen import analyze_zeishen_bushen
        r = analyze_zeishen_bushen(day_gan, gans, zhis)
        return bool((r.get('zeishen_bushen') or {}).get('jing_zhi') == '净')
    except Exception:
        return False


def assess_caiming_level(
    day_gan: str, gans: List[str], zhis: List[str],
    gongliang_result: Optional[Dict] = None,
    caifu_view: Optional[Dict] = None,
    muku_result: Optional[Dict] = None,
    direction_signals: Optional[Dict] = None,
    qucai_method: Optional[Dict] = None,
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
    # 制库得财（理象学制例一）：月令墓库被主位冲/刑开，库中财与原神同制
    # ——制尽级财命定式，量级同制尽（书锚=奥纳西斯船王巨富）。
    has_zhiku = _detect_zhiku_decai(day_gan, gans or [], zhis or [],
                                    muku_result).get('found', False)
    # 财库开闭（已由 classify_caifu_view 据传入 muku_result 检出，亦可直接读 caiku）
    has_open_caiku = bool(caifu_view.get('has_open_caiku'))
    # 财星源头/路径（M2：贫富三要素——原神/主位定浮实，合绊/入墓定阻通）
    cxp = caifu_view.get('caixing_path') or {}
    blockers: List[str] = list(cxp.get('blockers') or [])
    if guohe_pocai:
        blockers.append('过河拆桥，财流失')
    # 从格（从财/从弱/从强）豁免：从格以所从之神为局主，扶抑系「浮财/身财平衡」
    # 口径不适用（段氏从财格=财成势从之，巨富潜质，非浮财）。
    strength = ''
    try:
        from mangpai.subjective.yongshen import classify_strength
        strength = str(classify_strength(day_gan, gans or [], zhis or []))
    except Exception:
        pass
    cong_ge = strength.startswith('从')
    # 凶向信号（反局/破财/过河拆桥/用忌受制绊）：浮财升档抑制与下方封顶共用
    ds = direction_signals or {}
    ds_xiong = bool(ds.get('fanju') or ds.get('pocai') or ds.get('guohe_pocai')
                    or ds.get('yongshen_xiong') or ds.get('mingju_xiong'))

    # 基阶：level 4→富(偏巨富), 3→富, 2→小康, 1→贫/普通
    # 用 1-4 整数阶表示 贫(1)/小康(2)/富(3)/巨富(4)
    tier_idx = max(1, min(4, base_level)) if base_level else 2
    adjust = '持平'
    # ── 从财格顺势档（D类从格细则，段氏从财书例直判）──
    # 从弱且财为所从（财为最大异党明现）：扶抑浮财口径本不适用（下方豁免），
    # 但「从格豁免」不等于档位留白——从财之贫富按从财自身成势直判：
    #   财成局（三合/半合局五行=财）：「巳酉丑合财局…日主发大财」（例200），
    #     基阶不落下富；
    #   财有原神（食伤明现生财）且财明现≥2：从财得财有转化（22期例1
    #     「庚金无根…作从财格看，用神是水木，乙亥年发财」），基阶不落下富；
    #   财伏吟单一（同名财支≥3）而无合局转化：「卯财是单个的，没有转化，
    #     缺乏连贯性」（例141 从财非常穷），从财亦贫。
    # 凶向命中者不升（同校准一/升档抑制口径），伏吟压贫不受升档影响。
    cong_cai_pin = False
    if strength == '从弱' and not ds_xiong:
        _cai_wx_cc = WX_KE.get(GAN_WX.get(day_gan, ''), '')
        if _cai_wx_cc:
            _wx_counts = {}
            for wx in ('金', '木', '水', '火', '土'):
                _wx_counts[wx] = sum(1 for g in (gans or []) if GAN_WX.get(g) == wx) + \
                                 sum(1 for z in (zhis or []) if ZHI_WX.get(z) == wx)
            _cai_lead = _cai_wx_cc and _wx_counts.get(_cai_wx_cc, 0) >= 2 and \
                _wx_counts[_cai_wx_cc] == max(_wx_counts.values())
            if _cai_lead:
                # 伏吟单一：同名财支≥3 且无合局
                _same_zhi = [z for z in (zhis or []) if ZHI_WX.get(z) == _cai_wx_cc]
                _fuyin = len(_same_zhi) >= 3 and len(set(_same_zhi)) == 1
                _cai_ju = False
                for _he, _wx in SAN_HE.items():
                    if _wx == _cai_wx_cc and all(z in (zhis or []) for z in _he):
                        _cai_ju = True
                        break
                if not _cai_ju:
                    for _he, _wx in BAN_HE.items():
                        if _wx == _cai_wx_cc and _he[0] in (zhis or []) and _he[1] in (zhis or []):
                            _cai_ju = True
                            break
                if _fuyin and not _cai_ju:
                    tier_idx = 1
                    cong_cai_pin = True
                    adjust = (adjust + '；' if adjust != '持平' else '') + \
                        '从财伏吟单一无转化（段氏「没有转化，缺乏连贯性」），从财亦贫'
                else:
                    _ss_wx = WX_SHENG.get(GAN_WX.get(day_gan, ''), '')
                    _yuanshen_mx = any(GAN_WX.get(g, '') == _ss_wx for g in (gans or [])) or \
                        any(ZHI_WX.get(z, '') == _ss_wx or
                            any(GAN_WX.get(cg, '') == _ss_wx
                                for idx, (cg, _q) in enumerate(get_canggan_mangpai(z)) if idx <= 1)
                            for z in (zhis or []) if z)
                    if _cai_ju:
                        tier_idx = max(tier_idx, 3)
                        adjust = (adjust + '；' if adjust != '持平' else '') + \
                            '从财成局（段氏「巳酉丑合财局…发大财」），基阶不落下富'
                    elif _yuanshen_mx >= 1:
                        tier_idx = max(tier_idx, 3)
                        adjust = (adjust + '；' if adjust != '持平' else '') + \
                            '从财有原神转化（22期例1从财格乙亥年发财），基阶不落下富'

    # ── 从儿格顺势档（G5，22期所从分类「首先看从了什么」）──
    # 从弱所从=食伤（从儿）：食伤成势（干支主气≥3）且局有明财（儿又生儿，
    # 食伤生财流通）者，从儿得财——基阶不落下富（qi50 诊所效益极好、
    # li213 董竹君从儿企业家）。凶向命中者不升（同从财格口径）。
    # 「明财」门控：限天干透财/支本气财——藏干中气财非明现，不能任
    # 「儿又生儿」之流通；从儿无财者儿不生儿、不流通，基阶不升（22期）。
    if strength == '从弱' and not ds_xiong and not cong_cai_pin:
        try:
            from mangpai.subjective.yongshen import classify_cong_target
            _ct = classify_cong_target(day_gan, gans or [], zhis or [], strength)
        except Exception:
            _ct = {}
        if _ct.get('label') == '从儿':
            _ss_wx_c = WX_SHENG.get(GAN_WX.get(day_gan, ''), '')
            _ss_cnt = sum(1 for g in (gans or []) if GAN_WX.get(g) == _ss_wx_c) + \
                      sum(1 for z in (zhis or []) if ZHI_WX.get(z) == _ss_wx_c)
            _cai_wx_ce = WX_KE.get(GAN_WX.get(day_gan, ''), '')
            _ming_cai = bool(_cai_wx_ce) and (
                any(GAN_WX.get(g, '') == _cai_wx_ce for g in (gans or [])) or
                any(ZHI_WX.get(z, '') == _cai_wx_ce for z in (zhis or []) if z))
            if _ss_cnt >= 3 and _ming_cai:
                tier_idx = max(tier_idx, 3)
                adjust = (adjust + '；' if adjust != '持平' else '') + \
                    '从儿格食伤成势且有财流通（儿又生儿），基阶不落下富'

    # ── G9 日主自合合财升档（48期「日主因合而从支」）──
    # 日主坐激活自合柱、支中合神为财者，日主合财=财为我所合得（视同合财
    # 做功）；身强能担且财明现≥2（财旺）者上浮一阶（例133 戊子日身旺财旺，
    # 房地产倒卖发财）。身弱合财=财多身累不升；凶向命中者不升。
    _g9_up = False  # G9 已升标记：财源上浮与 G9 同源（财为我所及+有原神），
                    # 一事不二升（例134 身旺财旺自合合财=富，非巨富），防叠加
    if not ds_xiong and not cong_ge and strength == '身强':
        try:
            from mangpai.objective.zihe import detect_zihe
            _dz2 = detect_zihe(gans or [], zhis or []).get('day_zihe')
        except Exception:
            _dz2 = None
        if _dz2 and _dz2.get('activated'):
            _cai_wx_g9 = WX_KE.get(GAN_WX.get(day_gan, ''), '')
            if (GAN_WX.get(_dz2.get('he_shen', ''), '') == _cai_wx_g9
                    and (caifu_view or {}).get('cai_count', 0) >= 2 and tier_idx < 4):
                tier_idx += 1
                _g9_up = True
                adjust = (adjust + '；' if adjust != '持平' else '') + \
                    '上浮（日主自合合财，48期「日主因合而从支」，财为我合得）'

    # 基阶校准一（P1-a）：段氏一层功=小富小贵（百万级），非贫——有功一层
    # （gong_points>0 且非「无功」降档）基阶小康；无功/半层者仍为贫（乞丐口径）。
    # 凶向命中者不校准（方向封顶随后收尾，校准徒留「升后复降」矛盾文本）。
    if base_level == 1 and tier_idx == 1 and gl and not ds_xiong and not cong_cai_pin:
        _pts = gl.get('gong_points', 0) or 0
        if _pts > 0 and gl.get('penalty') != '无功':
            tier_idx = 2
            adjust = '基阶校准（一层功=小富小贵，百万级非贫）'
    # 制库得财直判 floor 富（P2，trainset b67-制例一奥纳西斯锚：船王巨富
    # 旧判贫——局无明财落禄/伤食当财被 -1 下浮；书锚=月令之财与财的原神
    # 同库被制，净制量级同制尽，与过河拆桥·富格同级财命定式）：基阶不落
    # 富下，抗功量层低估；升档走下方财源 +1（仅 +1 不越级）。凶向封顶链
    # 在下方收尾，不受此 floor 影响（同富格口径：floor 只抗低估不抗方向）。
    if has_zhiku and tier_idx < 3 and not cong_cai_pin:
        tier_idx = 3
        adjust = (adjust + '；' if adjust != '持平' else '') + \
            '制库得财直判（月令财与原神同库被制，净制同制尽），基阶不落下富'
    # 财源上浮
    # C批收敛一（零财 guard，与 classify_caifu_view 财统官 guard 同锚）：
    # 段氏「官多财少，财可统官」以财在局为前提——零财之局官杀当财不成立
    # （《中级》己酉戊辰壬申癸卯造：辰被卯穿「坏了，不为官了」，以伤官当财），
    # 制不尽残杀当财同属官杀当财诸式，零财者不带上浮，落回禄/伤食当财口径。
    _zbj_ok = has_zhibujin and (caifu_view or {}).get('cai_count', 0) >= 1
    _liangji_cap = False  # 封顶富（量级不足）标记：后续上浮链（开财库）不得翻越
    if (has_guancai or _zbj_ok or has_zhiku) and tier_idx < 4 and not cong_cai_pin:
        tier_idx += 1
        # P1-4 财统官 3->4 须财量级证据（段氏「官多财少，财可统官」+ 量级口径）：
        # 财统官以少财统多官，财之量级本疑——财无原神或不归主位（浮财统官）
        # 者量级不足，纵统官成立升档亦封顶「富」不到巨富；财有原神且归主位
        # （贫富三要素之浮实判据：财有源头且为我所及），或贼神捕神净制
        # （量级同制尽）者，方证财量级可任巨富。官统财（财多官少，财量级
        # 自证）与过河拆桥·富格（制尽路径）不在此限。
        _caitongguan = ('财统官' in views
                        and '官统财（官杀当财）' not in views
                        and not any(v.startswith('过河拆桥·富格') for v in views))
        if _caitongguan and tier_idx > 3:
            _cai_liangji = bool(cxp.get('has_yuanshen') and cxp.get('zhuwei_cai'))
            if _cai_liangji or _zeishen_jingzhi(day_gan, gans or [], zhis or []):
                adjust = '上浮（官杀当财量级高；财有原神且归主位/净制，财量级可任）'
            else:
                tier_idx = 3
                _liangji_cap = True
                adjust = '上浮（官杀当财量级高；财统官须财量级支撑，财无原神或不归主位量级不足，封顶富）'
        # zhibujin（制不尽当财）量级低于制尽得权（段氏做功量级口径：制尽方得
        # 全权，制不尽量级不足）——独力上浮封顶「富」，不到巨富；官统财/财统官/
        # 过河拆桥·富格（制尽路径）上浮不在此限。
        # 豁免（贼神捕神净制，段氏理象学主线）：净制=贼神原神俱制、制之干净，
        # 量级同制尽，纵 zbj 口径判「不尽」亦可达巨富——李嘉诚/保尔森书锚
        # 「财与财的原神同时被制，财富级别可见一斑」；不净者（原神残存）模块
        # 自注「封顶三层」，与封顶富同口径。
        elif _zbj_ok and not has_guancai and tier_idx > 3:
            if _zeishen_jingzhi(day_gan, gans or [], zhis or []):
                adjust = '上浮（官杀当财量级高；贼神捕神净制，量级同制尽）'
            else:
                tier_idx = 3
                _liangji_cap = True
                adjust = '上浮（官杀当财量级高；制不尽量级不足，封顶富）'
        # C批收敛二：过河拆桥·富格独力上浮（无官统财/财统官）封顶「富」——
        # 富格书锚（b67 trainset）直判 floor 富（P1），段氏巨富诸例皆净制
        # （李嘉诚/保尔森「财与财的原神同时被制」）或制库（奥纳西斯四层功量），
        # 无富格独力至巨富书锚；净制者量级同制尽，不在此限（同 zbj 豁免口径）。
        elif (any(v.startswith('过河拆桥·富格') for v in views)
                and '官统财（官杀当财）' not in views and '财统官' not in views
                and tier_idx > 3):
            if _zeishen_jingzhi(day_gan, gans or [], zhis or []):
                adjust = '上浮（官杀当财量级高；贼神捕神净制，量级同制尽）'
            else:
                tier_idx = 3
                _liangji_cap = True
                adjust = '上浮（官杀当财量级高；过河拆桥富格制官得财，非净制量级不及巨富，封顶富）'
        elif has_zhiku and not (has_guancai or _zbj_ok):
            adjust = (adjust + '；' if adjust != '持平' else '') + \
                '上浮（制库得财，开库同制财与原神，量级同制尽）'
        else:
            adjust = '上浮（官杀当财量级高）'
    elif has_lu_or_shishang and tier_idx > 1 and not cong_cai_pin:
        tier_idx -= 1
        adjust = '下浮（禄/食伤当财量级有限）'
    # 过河拆桥·富格直判 floor 富（P1，trainset b67 锚）：富格=制尽净制、制官
    # 得财之财命定式（高级篇），纵功量层低估（无功/一层功）亦不落贫/小康下；
    # 升档仍走上方官杀当财 +1（仅 +1 不越级）。凶向封顶链在下方收尾，不受
    # 此 floor 影响（真凶向命中者仍封顶——floor 只抗功量低估，不抗方向）。
    if (caifu_view.get('guohe_chaiqiao_type') == '富格'
            and tier_idx < 3 and not cong_cai_pin):
        tier_idx = 3
        adjust = (adjust + '；' if adjust != '持平' else '') + \
            '过河拆桥富格直判（制尽净制，制官得财定式），基阶不落下富'
    # 制尽/破财调整（-1 去重）：方向信号已携带过河拆桥破财时由下方凶向封顶链
    # 统一处理（封顶小康），此处不再重复 -1——双计会把本在 cap 上的档再压一阶，
    # 且封顶链「下浮封顶」文本因档已低于 cap 不再触发（凶向标记丢失）。
    if guohe_pocai and tier_idx > 1 and not ds.get('guohe_pocai'):
        tier_idx -= 1
        adjust = (adjust + '；' if adjust != '持平' else '') + '下浮（过河拆桥破财）'
    # 开财库上浮（墓中之财复出主大发）
    # C批收敛三：开库大发须财有原神（段氏「有财则伤食是其原神，可以当投资之
    # 财」——财无原神=浮财无源，纵开库复出亦弱而难发，30期ans29书文「水弱
    # 被制无原神所以会穷」即此）；量级封顶（封顶富）者不开（封顶不得翻越）。
    if has_open_caiku and tier_idx < 4 and not _liangji_cap and cxp.get('has_yuanshen'):
        tier_idx += 1
        adjust = (adjust + '；' if adjust != '持平' else '') + '上浮（开财库，墓中之财复出主大发）'
    # 财星当财路径的源头/阻通调整（M2）：官杀当财/制不尽当财者财源非财星、
    # 从格者扶抑浮财口径不适用，二者俱豁免。
    #   升档：财有原神（食伤明现生财）+ 财为我所及（财在主位，或合财做功——日主
    #     合财=直接承载、主位合宾财=合得他人之财）+ 无合绊/入墓阻断 -> 财有源头
    #     且路径畅通，段氏「有财则伤食是其原神，可以当投资之财」，上浮一阶。
    #     升档量级上限「富」（巨富档校准，第十七批）：投资/经营之财量级至富；
    #     巨富档须制级锚（制尽/净制/制库），各有专支上浮（官杀当财 +1 豁免链、
    #     制库得财 +1），财源上浮不越巨富。li128 实证：base3 财源上浮 3->4
    #     过冲，书判「丙申运做地产生意很有钱」=富非巨富。
    #     三道抑制：凶向命中者财源已断不升（避免升后触发封顶文本徒增凶向标记）；
    #     身弱财旺（段氏高级篇「身弱财旺：非但不能得财，反为财所累…富屋贫人」）
    #     不升——财多身弱无源可任，原神流通亦难致富；冲/刑动库半开之财
    #     （rumu_bankai：无透干引拔，财未全出，「不透干也无用」）不升——
    #     半开不死藏（不压），亦不足以升档大发（不升）。
    #   降档（封顶小康，段氏高级篇「身旺财弱：不发大财，但也不缺钱花，属于小康
    #     或普通富裕」——浮财/路径受阻=财能量小、难取，难富而未必要贫）：
    #     浮财（无原神且不在主位）/财被合绊/财入墓未开，任一命中封顶小康。
    shenruo_caiwang = bool(strength == '身弱' and caifu_view.get('cai_count', 0) >= 2)
    # 基阶校准二（P1-a）：财星当财·经营带原神+主位者基阶不落下富（3）。
    # 段氏「有财则伤食是其原神，可以当投资之财」——财有原神、归主位、有经营
    # 做功（合财/制财）者，财有源头且为我所及，纵功量层低估（无功/一层功）
    # 亦不落贫/小康。豁免：身弱财旺（富屋贫人）；凶向命中（财源已断，同升档
    # 两道抑制口径——乞丐夺财局纵有财星结构亦论贫）；官杀当财/制不尽/
    # 从格走各自财源路径（从财格由上方「从财格顺势档」直判，不走校准二）。
    # 浮财/合绊/入墓阻断由下方降档封顶小康。基阶校准生效时
    # 下方升档跳过（不叠加巨富）。
    _qm_methods = (qucai_method or {}).get('methods') or []
    jingying = bool(cxp.get('hecai_work')) or ('经营' in _qm_methods)
    solid_caishang = bool('财星当财' in views and cxp.get('has_yuanshen')
                          and cxp.get('zhuwei_cai') and jingying
                          and not shenruo_caiwang and not ds_xiong)
    floor_applied = False
    if (solid_caishang and tier_idx < 3
            and not (has_guancai or has_zhibujin or cong_ge or cong_cai_pin)):
        tier_idx = 3
        floor_applied = True
        adjust = (adjust + '；' if adjust != '持平' else '') + \
            '基阶校准（财星当财·经营带原神+主位，基阶不落下富）'
    fucai_capped = False
    if not (has_guancai or has_zhibujin or cong_ge) and '财星当财' in views:
        blocked = bool(cxp.get('fucai') or cxp.get('heban') or cxp.get('rumu'))
        cai_reachable = bool(cxp.get('zhuwei_cai') or cxp.get('hecai_work'))
        if (not blocked and not ds_xiong and not shenruo_caiwang
                and cxp.get('has_yuanshen') and cai_reachable
                and not cxp.get('rumu_bankai')
                and tier_idx < 3 and not floor_applied and not _g9_up):
            tier_idx += 1
            adjust = (adjust + '；' if adjust != '持平' else '') + \
                '上浮（财有原神且为我所及，源头畅通）'
        elif blocked and tier_idx > 2:
            tier_idx = 2
            fucai_capped = True
            why = ('财星无原神且不在主位，浮财无源' if cxp.get('fucai')
                   else '财星被合绊，生财路径阻断' if cxp.get('heban')
                   else '财星入墓未开，财被收藏难取')
            adjust = (adjust + '；' if adjust != '持平' else '') + f'下浮（{why}，封顶小康）'
    # 浮财/阻通降档后富档跟随（同凶向下浮口径：降档仍标高富档则自相矛盾）
    if fucai_capped and tier_idx < base_level:
        wealth_grade = ''
    # 吉凶方向封顶（P0 A + M1 + N1/N2/N3）：反局/牢狱/比劫夺财破财/过河拆桥破财
    # /忌神制用神(R2)/用神被合绊(R3)/原局凶向三式（伤官见官为忌/财生杀攻身/官杀入墓）
    # 任一凶向命中，财命按严重度封顶--severe（比劫夺财严重/财生杀攻身因财致祸）
    # ->贫(1)，余->小康下(2)。
    # 段氏功量层只判「做了什么」，凶向反哺「该不该做」：制用神/反局破财不得
    # 记为富（如第9期比劫夺财清家荡产、第8期贪财坐牢、忌神制用神/用神被合绊
    # 则财源断而难富）。
    if ds.get('fanju') or ds.get('pocai') or ds.get('guohe_pocai') \
            or ds.get('yongshen_xiong') or ds.get('mingju_xiong'):
        cap = 1 if (ds.get('pocai_severe') or ds.get('mingju_xiong_severe')) else 2
        if tier_idx > cap:
            tier_idx = cap
            sev = '严重' if cap == 1 else '一般'
            adjust = (adjust + '；' if adjust != '持平' else '') + \
                f'下浮封顶{cap}阶（{sev}凶向：' + '；'.join(ds.get('reasons') or []) + '）'
        # 富档跟随凶向（避免坐牢破财仍标千万-亿级荒谬）：凶向命中即抹富档——
        # 阶位被压者自不待言，本在低位者（乞丐/清家荡产）亦不标百万级；
        # 岁运反局（全量轨）同口径。
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
        'blockers': blockers,      # 阻因（浮财/合绊/入墓/过河拆桥）
        'path': '',                # 生财路径描述（analyze_caiming 装配）
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
          'level': {...},        # 层级四阶（含岁运 delta 轨）
          'level_static': {...}, # 层级四阶（原局轨，P0-a：岁运反局不入链）
          'primary_view': str,    # 主取财看法
          'primary_method': str,  # 主取财法
          'tier': str,           # 财命层级（含岁运 delta，流年事件断语用）
          'tier_static': str,    # 原局层级（P0-a，原局断语用）
          'yunsui_delta': dict|None,  # 岁运反局增量（P0-a；None=无岁运反局）
          'summary': str,        # 一句话财命定性（含岁运 delta）
          'summary_static': str, # 原局轨定性（P0-a）
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
    # 凶向信号（反局/牢狱/比劫夺财/过河拆桥破财）——双轨（P0-a 原局/运岁分离）：
    #   direction_natal: 原局级凶向（yunfan_result=None，岁运反局不入链）-> tier_static；
    #   direction_full : 含「当前运岁」反局切片（A1）-> tier（含 delta，流年事件用）。
    # 原局断语（财富层级）评原局轨，流年事件断语（某年破财/凶）评含 delta 轨，
    # 避免岁运反局 artifact 压原局档位（假阴）或偶然供给凶向标记（假阳）。
    direction_natal = assess_direction_signals(
        day_gan, gans or [], zhis or [],
        relations=relations, gongliang_result=gl,
        yunfan_result=None,
    )
    direction = assess_direction_signals(
        day_gan, gans or [], zhis or [],
        relations=relations, gongliang_result=gl,
        yunfan_result=yunfan_result,
    )
    # 过河拆桥破财由 caifu_view 检出，补入方向信号（双轨同补——原局定式两轨皆入）
    if cv.get('guohe_chaiqiao_type') == '破财':
        direction_natal = dict(direction_natal)
        direction_natal['guohe_pocai'] = True
        direction_natal['pocai'] = True
        if '过河拆桥破财' not in (direction_natal.get('reasons') or []):
            direction_natal['reasons'] = list(direction_natal.get('reasons') or []) + ['过河拆桥破财']
        direction = dict(direction)
        direction['guohe_pocai'] = True
        direction['pocai'] = True
        if '过河拆桥破财' not in (direction.get('reasons') or []):
            direction['reasons'] = list(direction.get('reasons') or []) + ['过河拆桥破财']
    level_static = assess_caiming_level(day_gan, gans or [], zhis or [], gl, cv,
                                        muku_result=muku_result,
                                        direction_signals=direction_natal,
                                        qucai_method=qm)
    level = assess_caiming_level(day_gan, gans or [], zhis or [], gl, cv,
                                  muku_result=muku_result,
                                  direction_signals=direction,
                                  qucai_method=qm)

    # 生财路径描述（M2：tier 由单一结论扩展为「档位 + 生财路径 + 阻因」）
    # 路径 = 主取财看法 · 主取财法 + 财源状态（有原神=有源头 / 浮财 / 官杀当财量级）
    cxp = cv.get('caixing_path') or {}
    path = f'{cv.get("primary", "未明")}·{qm.get("primary", "未明")}取财'
    pv = cv.get('primary', '')
    if pv.startswith(('官统财', '财统官')):
        path += '（制杀得财，量级高于财星当财）'
    elif pv.startswith('过河拆桥'):
        path += '（制尽净制，制官得财）' if cv.get('guohe_chaiqiao_type') == '富格' \
            else '（制不尽，财流失）'
    elif pv == '财星当财':
        if cxp.get('fucai'):
            path += '（财无原神且不在主位，浮财无源）'
        elif cxp.get('has_yuanshen'):
            path += '（财有原神，食伤生财有源头）'
    elif pv == '禄神当财':
        path += '（身体力行，辛苦求财）'
    elif pv == '伤食当财':
        path += '（技术/智力，食伤为财之源头）'
    level['path'] = path
    level_static['path'] = path
    blockers = level.get('blockers') or []

    # yunsui_delta（P0-a）：岁运反局对原局档位的增量影响（流年事件断语评分用）。
    # 原局断语（财富层级）消费 tier_static/summary_static，不吃此 delta。
    yunsui_delta: Optional[Dict] = None
    if direction.get('suiyun_fanju'):
        _wg_erased = bool(level_static.get('wealth_grade')) and not level.get('wealth_grade')
        yunsui_delta = {
            'suiyun_fanju': True,
            'tier_static': level_static.get('tier', ''),
            'tier_final': level.get('tier', ''),
            'capped': level.get('tier') != level_static.get('tier'),
            'wealth_grade_erased': _wg_erased,
            'reasons': list(direction.get('suiyun_reasons') or []),
            'desc': (f'岁运反局：原局档{level_static.get("tier", "")}'
                     + (f'->封顶{level.get("tier", "")}' if level.get('tier') != level_static.get('tier') else '（档位未动）')
                     + ('，富档抹除' if _wg_erased else '')),
        }

    def _assemble_summary(lv: Dict) -> str:
        s = f'主取财看法：{cv.get("primary","未明")}；主取财法：{qm.get("primary","未明")}；{lv.get("desc","")}'
        s += f'；生财路径：{path}'
        if lv.get('blockers'):
            s += '；阻因：' + '、'.join(lv['blockers'])
        # 破财信号文本仅属「制不尽」分键：富格（制尽净制，制官得财）非破财，
        # 无条件下挂会把「破财」标记词泄入 summary 误杀评分（qi41 富格泄漏）。
        if cv.get('guohe_chaiqiao_type') == '破财':
            s += '；伴过河拆桥破财信号'
        if zbj.get('found'):
            s += '；制不尽当财（残存官杀作财看）'
        for ck in caiku:
            s += f'；{ck["view"]}（{ck["zhi"]}）'
        return s

    caiku = cv.get('caiku', [])
    summary = _assemble_summary(level)
    # 凶向在档强制标注（仅全量轨）：凶向命中但档位本已在封顶之下（capped=False，
    # 未触发「下浮封顶」文本）时，全量轨 summary 仍携带凶向理由——流年事件断语
    # （破财/凶）评分依赖全量轨凶向标记。严禁写入静态轨（P0-a 假阳陷阱：原局
    # 层级断语评 summary_static，静态轨误入凶向词会把 ⚠️ 误杀 ❌）。
    if (direction.get('fanju') or direction.get('pocai') or direction.get('guohe_pocai')
            or direction.get('yongshen_xiong') or direction.get('mingju_xiong')) \
            and '下浮封顶' not in (level.get('desc') or ''):
        _xr = '；'.join(direction.get('reasons') or [])
        summary += f'；凶向在档（{_xr}）' if _xr else '；凶向在档'
    summary_static = _assemble_summary(level_static)
    # 官非牢狱（N4 复合）静态轨标注：N4=魁罡逢冲官∧枭神夺食，原局定性信号
    # （非岁运 artifact），其「凶」断语（走私坐牢/为财坐牢）多评原局轨
    # （summary_static）——全量轨「凶向在档」标注够不到。N4 命中面极窄
    # （全库实测 4 例，无层级断语财命），静态轨标注不重开 P0-a 假阳陷阱
    # （岁运反局等仍严禁入静态轨）。档位已被压者（下浮封顶文本携理由）
    # 不重复标注。
    if (direction_natal.get('guanfei_laoyu') or {}).get('detected') \
            and '官非牢狱' not in summary_static:
        summary_static += ('；官非牢狱在档（'
                           + (direction_natal['guanfei_laoyu'].get('reason')
                              or '魁罡逢冲官兼枭神夺食') + '）')

    return {
        'caifu_view': cv,
        'qucai_method': qm,
        'zhibujin_dangcai': zbj,
        'level': level,
        'level_static': level_static,      # 原局轨层级（P0-a，岁运反局不入链）
        'primary_view': cv.get('primary', ''),
        'primary_method': qm.get('primary', ''),
        'tier': level.get('tier', ''),              # 含岁运 delta 的最终档（流年事件用）
        'tier_static': level_static.get('tier', ''),  # 原局档（原局断语用，P0-a）
        'yunsui_delta': yunsui_delta,        # 岁运反局增量（None=无岁运反局）
        'path': path,                        # 生财路径描述（M2）
        'blockers': blockers,                # 阻因列表（M2）
        'summary': summary,                  # 含岁运 delta 的全量定性
        'summary_static': summary_static,    # 原局轨定性（P0-a）
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
