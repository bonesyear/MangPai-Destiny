# -*- coding: utf-8 -*-
"""用神/忌神方向判定（扶抑框架）+ 凶向信号聚合。

段氏功量层（gongliang）能检测「做了什么功」，但不知「该不该做」。
本模块补吉凶方向判定：

1. **比劫夺财（R1）**——段氏「制财得财」成立的前提是功神非比劫；
   功神=比劫制财（尤以身强财为用神、财弱孤）为「比劫夺财」=破财凶，
   与「印/食伤/官制财=得财吉」对立。典型：第9期 子(比劫)冲午(财) =>
   清家荡产；区别于蒋介石 巳(印)冲亥(财)=得财贵（功神=印非比劫）。

2. **忌神制用神（R2）**——段氏「八字中弱的忌神用旺的用神去之则吉」的
   逆命题：忌神制用神=凶。两个子型（扶抑定用忌，见 _yongshen_cats）：
   - R2a 财坏印：身弱/从强（印为用神、财为忌神），财制印（冲/克/穿/破/刑
     功神=财、被制=印）=贪财坏印凶（印主学业/名誉/单位/职位）；
   - R2b 印夺食：身强/从弱（食伤为用神、印为忌神），印制食伤=枭神夺食凶
     （食伤主财源/自由/子女，《授课教程》「癸酉运枭神夺食，子死于非命」）。
   反方向（用神制忌神，如从弱财制印=官命、身弱印制伤官=伤官佩印）不触发——
   与 GUAN 书例「财制印=官」（从弱印为忌）口径一致。

3. **用神被合绊（R3）**——段氏「命局中两个字紧贴相合为绊」「合绊就象两个
   人拥抱一样，谁都无法发挥作用，为失去原性」。用神被合绊=凶向；忌神被
   合绊=吉（不触发，如李嘉诚丙寅运寅亥合绊亥水忌神无往而不胜——运岁级，
   本规则只扫原局）。判定口径：
   - 只取**紧贴**（相邻柱）六合/五合（段氏原文「紧贴相合为绊」）；
   - 地支六合按受害方判定（与 objective.he_types 合克/合伤/闭气口径一致：
     子丑=两伤、卯戌=戌伤、巳申=申伤、辰酉=辰伤、寅亥=寅伤、午未=未伤），
     受害方十神为用神才触发——森田健「卯戌合绊，戌根失去力量」（戌为受害
     方）正例；午未闭气受害方为未（库），午不受绊，故李嘉诚未午合不触发；
   - 天干五合互绊（合即互绊失去原性），但只判他干紧贴（年干×月干），
     日干参与之合（合财/合官）属 zuogong「合用」做功层，不在此论；
   - 中和/不明不定用忌，不触发（防过火）。

4. **凶向信号聚合**——反局(fan)/坐牢(laoyu)/比劫夺财/过河拆桥破财
   /忌神制用神(R2)/用神被合绊(R3) 任一命中即「凶向」，供 caiming/guanming
   /zhiye 反哺降档/否决。

设计约束（见 memory: mangpai-objective-subjective-refactor）：
  - 本模块属 subjective 判断层，单向消费 objective 检测 + 同层 zuogong/zhengfan/laoyu；
  - 缺省自调（_ensure_*），engine 透传或 calib 直调均可用；
  - 不改 gongliang 功量点累加，仅在其后施加方向性封顶/标记。
"""

from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, TIAN_GAN_HE, HUA_YONG_MAP,
)

# 十神大类 <-> 日干五行
def _wx_cat(day_wx: str, wx: str) -> str:
    if wx == day_wx:
        return '比劫'
    if WX_SHENG.get(wx) == day_wx:
        return '印'
    if WX_SHENG.get(day_wx) == wx:
        return '食伤'
    if WX_KE.get(day_wx) == wx:
        return '财'
    if WX_KE.get(wx) == day_wx:
        return '官杀'
    return ''


def _yin_wx(day_wx: str) -> str:
    for w, c in WX_SHENG.items():
        if c == day_wx:
            return w
    return ''


def _pillar_wx(i: int, gans: List[str], zhis: List[str]) -> str:
    """第 i 柱天干五行（透干优先用于「明现」计数）。"""
    if i < len(gans) and gans[i]:
        return GAN_WX.get(gans[i], '')
    return ''


def _pos_main_wx(pos: str, gans: List[str], zhis: List[str]) -> str:
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    idx = ['year', 'month', 'day', 'hour'].index(p) if p in ('year', 'month', 'day', 'hour') else -1
    if idx < 0:
        return ''
    if t == 'gan':
        return GAN_WX.get(gans[idx], '') if idx < len(gans) else ''
    return ZHI_WX.get(zhis[idx], '') if idx < len(zhis) else ''


def _cong_gen_fu_state(day_gan: str, gans: List[str], zhis: List[str]) -> Dict:
    """日主根扶状态（段氏22期从格四规则之机械口径）。

    根=地支藏干（含余气——例5「辰中癸水」余气算根）含日主五行；
    扶（印）明现=透干/本气/中气；印根=地支藏干**本气/中气**含印五行
    （余气假根不算——例1 己印坐寅中戊余气书判「印也无根」、例2 辰印
    被旺木穿坏书判从财，与日主根计余气[例5]为书内两套并存口径）。
    根被坏（「强有力邻支冲掉 / 合会局转化失原性」，例3 巳刑寅+寅午半会）：
      - 双夹冲：根支左右两邻支俱冲之（例4 三戌冲辰方坏；例5 一戌紧贴
        一戌不贴则冲不坏——单夹冲不算坏）；
      - 单点刑/穿：根支被邻支刑/穿（例2 卯辰穿坏辰、例3 巳刑寅）；
      - 合会转化：根支参与三合/半合且局五行 ≠ 日主五行（失原性）。
    根远近：唯年支根为「根远」（「年支根远…根远者日主无法依托，往往会从」）。

    Returns: {'roots': [int], 'roots_broken': bool, 'far_root_only': bool,
              'has_yin': bool, 'yin_rooted': bool, 'yin_root_broken': bool,
              'yue_broken': bool}
    """
    from mangpai.objective.canggan import get_canggan_mangpai
    from mangpai.objective.constants import (
        LIU_CHONG, XING_PAIRS, SAN_HE, BAN_HE, LIU_HAI,
    )
    from mangpai.objective.zihe import detect_zihe
    dw = GAN_WX.get(day_gan, '')
    yin = _yin_wx(dw)
    # G9（48期）：日主坐自合柱（如己亥）者「日主因合而从支/被支制」——
    # 不受印生（例2 己坐亥自合，不受丁火之生，从官），印扶视同失效。
    day_zihe = bool(detect_zihe(gans, zhis).get('day_zihe'))

    def _has_wx_cang(i: int, wx: str, max_idx: int = 99) -> bool:
        """i 支藏干含 wx 五行。max_idx 限气位：默认全取（含余气）；1=本/中气。"""
        if i >= len(zhis) or not zhis[i]:
            return False
        for idx, (cg, _q) in enumerate(get_canggan_mangpai(zhis[i])):
            if idx > max_idx:
                break
            if GAN_WX.get(cg, '') == wx:
                return True
        return False

    roots = [i for i in range(4) if _has_wx_cang(i, dw)]
    yin_roots = [i for i in range(4) if _has_wx_cang(i, yin, max_idx=1)]
    # 印明现（透干/本气/中气）
    has_yin = False
    if yin:
        for i in range(4):
            if i < len(gans) and gans[i] and GAN_WX.get(gans[i]) == yin:
                has_yin = True
                break
            if i < len(zhis) and zhis[i]:
                if ZHI_WX.get(zhis[i]) == yin:
                    has_yin = True
                    break
                for idx, (cg, _q) in enumerate(get_canggan_mangpai(zhis[i])):
                    if idx > 1:
                        break
                    if GAN_WX.get(cg, '') == yin:
                        has_yin = True
                        break
                if has_yin:
                    break

    def _pair_hit(a: str, b: str, pairs) -> bool:
        return (a, b) in pairs or (b, a) in pairs or \
            (frozenset((a, b)) in pairs) or (a + b in pairs) or (b + a in pairs)

    def _broken(i: int) -> bool:
        """i 支被坏：双夹冲 / 单点刑穿 / 合会转化（局五行≠日主五行）。"""
        if i >= len(zhis) or not zhis[i]:
            return False
        z = zhis[i]
        neighbors = [zhis[j] for j in (i - 1, i + 1) if 0 <= j < len(zhis) and zhis[j]]
        # 双夹冲（左右俱冲）
        chong_hit = sum(1 for w in neighbors if _pair_hit(z, w, LIU_CHONG))
        if chong_hit >= 2:
            return True
        # 单点刑/穿（邻支）
        for w in neighbors:
            if _pair_hit(z, w, XING_PAIRS) or _pair_hit(z, w, LIU_HAI):
                return True
        # 合会转化（三合/半合，局五行为异党（非日主非印）方失原性——
        # 例3 寅午会火于甲日=木泄为火（异党）故坏；午戌会火于己日=火印
        # 生身（自党）则根反固，不坏）。
        self_set = {dw, yin}
        for he, wx in SAN_HE.items():
            if z in he and wx not in self_set and all(p in zhis for p in he):
                return True
        for he, wx in BAN_HE.items():
            if z in he and wx not in self_set and he[0] in zhis and he[1] in zhis:
                return True
        return False

    def _double_chong(i: int) -> bool:
        """i 支被左右两邻支俱冲（双夹冲——「强有力邻支冲掉」，例4 三戌冲辰）。"""
        if i >= len(zhis) or not zhis[i]:
            return False
        z = zhis[i]
        neighbors = [zhis[j] for j in (i - 1, i + 1) if 0 <= j < len(zhis) and zhis[j]]
        return sum(1 for w in neighbors if _pair_hit(z, w, LIU_CHONG)) >= 2

    return {
        'roots': roots,
        'roots_broken': bool(roots) and all(_broken(i) for i in roots),
        'roots_double_chong': bool(roots) and all(_double_chong(i) for i in roots),
        'far_root_only': roots == [0],
        'has_yin': has_yin,
        'yin_rooted': bool(yin_roots),
        'yin_root_broken': bool(yin_roots) and all(_broken(i) for i in yin_roots),
        'yue_broken': _broken(1) if len(zhis) > 1 else False,
        'day_zihe': day_zihe,  # G9：日主自合柱（不受印生，印扶失效）
    }


def classify_strength(day_gan: str, gans: List[str], zhis: List[str]) -> str:
    """扶抑身强弱粗分（势-based，非精细得令透干）。

    段氏22期从格细则（additive——只在粗判 身强/身弱/中和/不明 上补从格
    判定，不反向改判既有从格标签）：
      从弱侧（selfc≤3）：①日主无根无扶者从；③无根有印而印无根者从；
        ④无根印有根而印根被坏者从；②有根（俱被坏）无生扶者从；
        唯年支根远且无扶者从（「根远者日主无法依托，往往会从」）。
      从强侧/从旺从禄（selfc≥5 且 conc≤3）：月令为异党而月令被坏
        （双夹冲/邻支刑穿/合会转化入异局）——月令不能拮抗，从旺论
        （从禄格例：丁未壬寅己巳庚午，月令寅官被巳刑坏，书判从禄格，
        壬水与庚金为忌神）。

    Returns: '身强'|'身弱'|'中和'|'从强'|'从弱'|'不明'
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return '不明'
    dw = GAN_WX.get(day_gan, '')
    if not dw:
        return '不明'
    yin = _yin_wx(dw)
    self_wx = {dw, yin}
    selfc = sum(1 for g in gans if GAN_WX.get(g) in self_wx) + \
            sum(1 for z in zhis if ZHI_WX.get(z) in self_wx)
    conc = 8 - selfc
    yue_wx = ZHI_WX.get(zhis[1], '')
    yue_self = yue_wx in self_wx
    if selfc >= 6 or (selfc >= 5 and yue_self and conc <= 2):
        return '从强'
    if conc >= 6 or (conc >= 5 and not yue_self and selfc <= 2):
        return '从弱'
    base = '中和' if abs(selfc - conc) <= 1 else ('身强' if selfc > conc else '身弱')
    # ── 22期从格细则（additive）──
    try:
        st = _cong_gen_fu_state(day_gan, gans, zhis)
    except Exception:
        return base
    # 从格须一方成势（段氏势论：从格=从其旺势）——异党单五行干支主气≥3
    # 方有势可从；水木两停/火土各半者非从（生例一富婆 亥子寅卯两停=生用
    # 做功，不从；22期 例1-4 异党俱≥3 方从）。
    self_set0 = {dw, yin}
    yidang_shi = 0
    for wx in ('金', '木', '水', '火', '土'):
        if wx in self_set0:
            continue
        n = sum(1 for g in gans if GAN_WX.get(g) == wx) + \
            sum(1 for z in zhis if ZHI_WX.get(z) == wx)
        yidang_shi = max(yidang_shi, n)
    # G9：日主自合柱者，合局化势计入成势闸（48期例2 亥卯半合化木，官势实3
    # 而主气仅2——日主既已自合失扶，所从之势按合局后五行量）。
    # G5 扩展（22期例6）：异党数量占优（selfc<conc，非两停）者同用化势
    # 宽口径——例6 从官格 癸乙丙丙/酉丑子申，异党5:3，酉丑半合金则金实3
    # 成势（主气仅2），从官。两停局（selfc==conc，生例一富婆水木各半）
    # 维持主气计数，防两停误判从。
    if st.get('day_zihe') or selfc < conc:
        from mangpai.objective.constants import SAN_HE as _SH2, BAN_HE as _BH2
        zhi_wx_eff = [ZHI_WX.get(z, '') for z in zhis]
        for _he, _wx in _SH2.items():
            if all(p in zhis for p in _he):
                for p in _he:
                    zhi_wx_eff[zhis.index(p)] = _wx
        for _he, _wx in _BH2.items():
            if _he[0] in zhis and _he[1] in zhis:
                zhi_wx_eff[zhis.index(_he[0])] = _wx
                zhi_wx_eff[zhis.index(_he[1])] = _wx
        for wx in ('金', '木', '水', '火', '土'):
            if wx in self_set0:
                continue
            n = sum(1 for g in gans if GAN_WX.get(g) == wx) + \
                sum(1 for w in zhi_wx_eff if w == wx)
            yidang_shi = max(yidang_shi, n)
    if selfc <= 4 and yidang_shi >= 3:
        # 从弱侧四规则 + 根远（例2「天干比肩再多也无用」——从格看根气，
        # 不数天干比劫，故门槛取 selfc≤4 而非计数强弱势）
        # G9（48期例2）：日主自合柱者不受印生——印扶视同失效（有印如无印），
        # 印之根扶一并失效（己坐亥自合不受丁火之生，从官）。
        no_yinfu = bool(st.get('day_zihe'))
        has_yin_eff = st['has_yin'] and not no_yinfu
        yin_rooted_eff = st['yin_rooted'] and not no_yinfu
        if not st['roots']:
            if not has_yin_eff:
                return '从弱'                      # ① 无根无扶
            if not yin_rooted_eff:
                return '从弱'                      # ③ 无根印亦无根
            if st['yin_root_broken']:
                return '从弱'                      # ④ 印根被坏
        else:
            yin_shengfu = has_yin_eff and yin_rooted_eff and not st['yin_root_broken']
            if st['roots_broken'] and (not yin_shengfu or st.get('roots_double_chong')):
                return '从弱'                      # ② 有根无生扶根被坏；
                                                   #   双夹冲强力坏根者印难救（例4三戌冲辰）
            if st['far_root_only'] and not has_yin_eff:
                return '从弱'                      # 根远难依托
    elif selfc >= 5 and conc <= 3 and not yue_self and st['yue_broken']:
        # 从旺/从禄：月令异党被坏（不能拮抗）且异党天干俱无本气根（无所依托）。
        # 反例（乞丐 壬子癸卯壬子丙午）：月令卯被子刑似破，然异党丙火根在午
        # （本气刃根）有所依托，身强不论从——书判比劫夺财身强局。
        self_set = {dw, yin}
        yidang_rooted = any(
            GAN_WX.get(g, '') not in self_set and ZHI_WX.get(z, '') == GAN_WX.get(g, '')
            for i, g in enumerate(gans) if g and i != 2
            for z in zhis
        )
        if not yidang_rooted:
            return '从强'                          # 从旺/从禄（月令异党被坏且异党无依托）
    return base


def _ensure_work_actions(day_gan: str, gans: List[str], zhis: List[str],
                         work_actions: Optional[List[Dict]]) -> List[Dict]:
    if work_actions:
        return work_actions
    try:
        from mangpai.subjective.zuogong_confirm import analyze_zuogong
        zg = analyze_zuogong(
            day_gan, zhis[2], gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
        return zg.get('work_actions') or []
    except Exception:
        return []


def _tiejie_heban_positions(gans: List[str], zhis: List[str]) -> Set[str]:
    """紧贴（相邻柱）合绊中**失能方**位置集合。

    段氏「命局中两个字紧贴相合为绊…谁都无法发挥作用，为失去原性」；
    《授课教程》qi03「六合能解三合…两忌神相合为忌神合绊，不克害用神」——
    被绊失能之字不能夺财克害。口径（与 R3 受害方判定一致）：
      - 地支六合：只取**受害方**（_LIUHE_VICTIMS：合克/合伤/闭气之被伤侧）。
        非受害方不失能——如辰酉合化金反助酉金（酉非受害方，王亚樵造酉刃
        夺财之能不因辰酉合而失），寅亥合受害方为寅（亥克寅中丙火）；
      - 天干五合：互绊（合即双方失去原性），两方俱取。
    """
    pos: Set[str] = set()
    for i in range(3):
        a, b = zhis[i], zhis[i + 1]
        victims = _LIUHE_VICTIMS.get(frozenset(a + b)) if a and b else None
        if victims:
            for j, z in ((i, a), (i + 1, b)):
                if z in victims:
                    pos.add(f'{_PK4[j]}_zhi')
        ga, gb = gans[i], gans[i + 1]
        if ga and gb and TIAN_GAN_HE.get(ga) == gb:
            pos.add(f'{_PK4[i]}_gan')
            pos.add(f'{_PK4[i + 1]}_gan')
    return pos


def detect_bijiao_duocai(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """比劫夺财检测（R1）。

    判定：身强（财为扶抑用神、财孤可夺）+ 存在 冲/克/穿/破/刑 非辅助做功
    其功神(from_pos 主气)=比劫、被制(to_pos 主气)=财，且财弱（明现≤1柱）。
    严重度：比劫≥2柱 或 财被≥2处比劫制 -> severe（清家荡产/贫）。

    段氏「制财得财」以功神非比劫为前提；功神=比劫即「夺财」破财，与
    蒋介石（印制财=得财）、LIU8（印制财=七杀当财）相区别。

    两道书锚豁免（G0-G5 模式，precision pass）：
      R1a 财旺夺不动：身强而财明现≥2柱（财有众），比劫夺之不动——
        《授课教程》例134「身旺财旺…搞倒卖成了房地产倒卖商而发财」，
        夺财成立须财孤可夺（第9期 午财孤悬，子水群劫夺之=清家荡产）；
        从弱不在此限（顺势之财不论旺弱，比劫逆势破格即凶，第8/1期口径）。
      R1b 功神被合绊：比劫功神位为紧贴合绊之**受害方**（六合受害方口径
        同 R3/ he_types；天干五合互绊）者失去原性、不能夺财（qi03
        「合绊…不克害用神」；《授课教程》例「寅亥合」之理财女强人/得200万
        造，寅劫被亥合伤，不论夺财；辰酉合酉非受害方，合化反助不豁免）。

    Returns:
        {'detected': bool, 'severity': 'severe'|'normal'|None,
         'strength': str, 'cai_pillars': int, 'bijiao_pillars': int,
         'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'severity': None, 'reason': ''}
    dw = GAN_WX.get(day_gan, '')
    strength = classify_strength(day_gan, gans, zhis)
    caiwx = next((w for w in GAN_WX.values() if _wx_cat(dw, w) == '财'), '')
    if not caiwx:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}

    cai_pillars = sum(1 for i in range(4)
                      if GAN_WX.get(gans[i]) == caiwx or ZHI_WX.get(zhis[i]) == caiwx)
    # 比劫柱数只算他柱比劫星：日主（day_gan，柱序 i==2）是「我」本身，非比劫星，
    # 不计入；日支本气为比劫（配偶宫比劫星）仍计。段氏「比劫夺财」特指同辈夺财，
    # 日主克财=正常「我克者财」（得财），不可与夺财混计。
    _DAY = 2
    bijiao_pillars = sum(1 for i in range(4)
                         if (i != _DAY and GAN_WX.get(gans[i]) == dw)
                         or ZHI_WX.get(zhis[i]) == dw)

    wa = _ensure_work_actions(day_gan, gans, zhis, work_actions)
    heban_pos = _tiejie_heban_positions(gans, zhis)
    # G9（48期）：非日柱之激活自合柱，柱上之干被坐支藏干合绊失用
    # （康熙型「甲被午中己合绊」）——与 R1b 受害方口径统一：失用之干
    # 不能做功夺财。日柱自合不在此列（日主自合=日主从支，非比劫夺财域）。
    try:
        from mangpai.objective.zihe import detect_zihe
        heban_pos |= set(detect_zihe(gans, zhis).get('ban_gan_positions') or [])
    except Exception:
        pass
    duocai_hits = 0
    hit_descs: List[str] = []
    for a in wa:
        if a.get('auxiliary'):
            continue
        t = a.get('type', '')
        if t not in ('冲', '克', '穿', '破', '刑'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if not (fp and tp):
            continue
        # 排除 day_gan 作比劫 actor：日主克财=「我克者财」（得财），非比劫夺财。
        # 段氏夺财特指他柱同辈（比劫星）制财；day_gan 命中一律跳过。
        if fp == 'day_gan':
            continue
        # R1b：比劫功神位为紧贴合绊之受害方者失去原性，不能夺财
        # （合绊者不克害；辰酉合等非受害方不受此限——合化反助者不豁免）。
        if fp in heban_pos:
            continue
        # R1c（从弱·D类从格细则）：从弱财为顺势，比劫须「逆势有力」方破格。
        # 功神干虚透无本气根者从化无力（《授课》「天干比肩再多也无用」，
        # 22期例1 辛劫虚透、从财格乙亥年发财）；功神支入三合/半合而局五行
        # =财者，比劫从化入财势（「巳顺从酉势」，例199/200 从财富有/发大财），
        # 俱非逆势破格，不论夺财。
        if strength == '从弱':
            fp_elem = _pos_main_wx(fp, gans, zhis)
            if fp.endswith('_gan'):
                if not any(ZHI_WX.get(z, '') == fp_elem for z in zhis):
                    continue  # 虚透无根，从化无力
            elif fp.endswith('_zhi'):
                _cong_hua = False
                from mangpai.objective.constants import SAN_HE as _SH, BAN_HE as _BH
                _fz = zhis[_PK4.index(fp.split('_')[0])] if fp.split('_')[0] in _PK4 else ''
                for _he, _wx in _SH.items():
                    if _fz and _fz in _he and _wx == caiwx and all(p in zhis for p in _he):
                        _cong_hua = True
                        break
                if not _cong_hua:
                    for _he, _wx in _BH.items():
                        if _fz and _fz in _he and _wx == caiwx \
                                and _he[0] in zhis and _he[1] in zhis:
                            _cong_hua = True
                            break
                if _cong_hua:
                    continue  # 比劫从化入财势
        fc = _wx_cat(dw, _pos_main_wx(fp, gans, zhis))
        tc = _wx_cat(dw, _pos_main_wx(tp, gans, zhis))
        if fc == '比劫' and tc == '财':
            duocai_hits += 1
            hit_descs.append(f'{t} {fp}(比劫)→{tp}(财)')

    # R1a：身强须财孤（明现≤1柱）方可夺；财明现≥2柱为财有众，比劫夺之
    # 不动（「身旺财旺…发财」，例134），其制财动作归「制财得财」财命域。
    # 从弱财为顺势，不论旺弱，比劫逆势破格即凶（第8/1期），不在此限。
    detected = bool(hit_descs) and (
        (strength == '身强' and cai_pillars <= 1) or strength == '从弱'
    )
    severity = None
    reason = ''
    if detected:
        severe = bijiao_pillars >= 2 or duocai_hits >= 2
        severity = 'severe' if severe else 'normal'
        # 身强/从弱财俱为用神、比劫俱为忌神（身强财耗身、从弱财顺势），功神=比劫
        # 制财即忌神克用神=夺财破财凶。从弱财旺为顺势之常，不以财弱为门槛（比劫
        # 逆势破格即凶，如第8/1期）。蒋介石印制财（功神=印非比劫）不在此列。
        sz = '清家荡产/贫' if severe else '破财/小康下'
        reason = (f'比劫夺财·破财：{strength}财为用神，{duocai_hits}处比劫制财'
                  f'（比劫{bijiao_pillars}柱），'
                  f'段氏「制财得财」以功神非比劫为前提，功神=比劫即夺财凶（{sz}）')
    return {
        'detected': detected, 'severity': severity, 'strength': strength,
        'cai_pillars': cai_pillars, 'bijiao_pillars': bijiao_pillars,
        'hits': hit_descs, 'reason': reason,
    }


def classify_cong_target(
    day_gan: str, gans: List[str], zhis: List[str],
    strength: Optional[str] = None,
) -> Dict:
    """从格所从分类（G5，22期「看从格首先看从了什么」）。

    从弱侧：异党单五行干支主气最大者为所从——财=从财、官杀=从官杀、
    食伤=从儿、印=从印；从强侧：自党成势，日主之禄在局者记从禄
    （ans30 从禄格例：丁未壬寅己巳庚午，己禄在午）。
    所从定喜忌：从财怕官运（官泄财气，22期例2）、从儿喜财（儿又生儿）、
    从强忌异党得根（破从，qi02 家业破尽）；非从格返回中性。

    Returns:
        {'strength': str, 'is_cong': bool, 'label': str,
         'suo_cong_wx': str,   # 所从五行（从强=自党主势五行）
         'ji_wx': [str],       # 忌神五行（从强=异党全部；从弱=印比）
         'detail': str}
    """
    neutral = {'strength': strength or '', 'is_cong': False, 'label': '',
               'suo_cong_wx': '', 'ji_wx': [], 'detail': ''}
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return neutral
    dw = GAN_WX.get(day_gan, '')
    if not dw:
        return neutral
    if strength is None:
        strength = classify_strength(day_gan, gans, zhis)
    yin = _yin_wx(dw)
    self_set = {dw, yin}
    out = dict(neutral)
    out['strength'] = strength

    def _count(wx: str) -> int:
        return sum(1 for g in gans if GAN_WX.get(g) == wx) + \
               sum(1 for z in zhis if ZHI_WX.get(z) == wx)

    if strength == '从弱':
        # 异党最大五行为所从（ties 取计数序先至者——金木水火土）
        best_wx, best_n = '', 0
        for wx in ('金', '木', '水', '火', '土'):
            if wx in self_set:
                continue
            n = _count(wx)
            if n > best_n:
                best_wx, best_n = wx, n
        cat = _wx_cat(dw, best_wx) if best_wx else ''
        label = {'财': '从财', '官杀': '从官杀', '食伤': '从儿', '印': '从印'}.get(cat, '从弱')
        out.update({
            'is_cong': True, 'label': label, 'suo_cong_wx': best_wx,
            'ji_wx': sorted(self_set),
            'detail': (f'从格所从：异党{best_wx}（{cat}）成势({best_n})，'
                       f'日主从之={label}（22期「看从格首先看从了什么」）'
                       if best_wx else '从弱，异党无所从之势'),
        })
        return out
    if strength == '从强':
        from mangpai.objective.constants import LU
        bijie_n, yin_n = _count(dw), _count(yin)
        suo = dw if bijie_n >= yin_n else yin
        lu_zhi = LU.get(day_gan, '')
        label = '从禄' if (lu_zhi and lu_zhi in zhis) else '从强'
        out.update({
            'is_cong': True, 'label': label, 'suo_cong_wx': suo,
            'ji_wx': [w for w in ('金', '木', '水', '火', '土') if w not in self_set],
            'detail': (f'{label}：自党（{suo}）成势，忌异党（'
                       f'{"、".join(out["ji_wx"])}）得根/得势（破从凶）'),
        })
        return out
    return out


def _yongshen_cats(strength: str) -> tuple:
    """扶抑用忌十神分类（R2/R3 共用）。

    身强：财官食伤为用（耗泄克），印比劫为忌；
    身弱/从强：印比劫为用，财官食伤为忌；
    从弱：财官食伤为用，印比劫为忌；
    中和/不明：不定用忌（返回空集，调用方不触发，防过火）。

    Returns: (yongshen_categories, jishen_categories)
    """
    if strength == '身强':
        return {'财', '官杀', '食伤'}, {'印', '比劫'}
    if strength in ('身弱', '从强'):
        return {'印', '比劫'}, {'财', '官杀', '食伤'}
    if strength == '从弱':
        return {'财', '官杀', '食伤'}, {'印', '比劫'}
    return set(), set()


def detect_jishen_zhiyongshen(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """忌神制用神检测（R2：财坏印 / 印夺食）。

    判定（与 R1 同构：非辅助做功 + 功神/被制十神方向 + 扶抑用忌）：
      R2a 财坏印：身弱/从强（印=用神，财=忌神），存在 冲/克/穿/破/刑
        非辅助做功，功神(from_pos 主气)=财、被制(to_pos 主气)=印；
      R2b 印夺食：身强/从弱（食伤=用神，印=忌神），同上前缀，功神=印、
        被制=食伤。
    排除 day_gan 作功神（日主之克=「我」之行为，非忌神制用神，同 R1 口径）；
    非日柱参与的做功（宾宾）confirm 层已降 auxiliary，天然不触发（故阎锡山
    癸(印)克丁(食) 宾位干克不命中）。反方向（从弱财制印、身弱印制伤官）为
    用神制忌神=吉，不触发。
    严重度：忌神（R2a=财/R2b=印）≥2柱 或 命中≥2处 -> severe。

    忌神失能三道豁免（K3-294批4，与 R1b 同书锚族）：忌神被紧贴合绊失能
    （巨富丑运 戌印被卯戌合绊，书明文丑印运发财）/贪合忘克·同入三合全
    局内不论克（cj-老师 亥卯未全，未印不夺亥食）/日支自合柱合神即忌神
    同类=为我所得（yx-煤矿-2 壬午日丁财自合，书明文壬午财运发财十亿）。

    Returns:
        {'detected': bool, 'kind': '财坏印'|'印夺食'|None,
         'severity': 'severe'|'normal'|None, 'strength': str,
         'hits': [str], 'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'kind': None, 'severity': None, 'reason': ''}
    dw = GAN_WX.get(day_gan, '')
    strength = classify_strength(day_gan, gans, zhis)
    if strength in ('身弱', '从强'):
        kind, js_cat, ys_cat = '财坏印', '财', '印'
    elif strength in ('身强', '从弱'):
        kind, js_cat, ys_cat = '印夺食', '印', '食伤'
    else:
        return {'detected': False, 'kind': None, 'severity': None,
                'reason': '', 'strength': strength}

    # 孤忌犯众用豁免（段氏「八字中弱的忌神用旺的用神去之则吉」之正命题）：
    # 忌神孤（明现≤1柱）而用神众（明现≥2柱），孤忌犯众=自取其辱，实则
    # 众用反制孤忌、忌神被制化失能——如张克东造「财被两酉夹合而化，原气
    # 尽失，无可用之理」（从强三金印众，巳财孤犯众印），不论忌神制用神。
    js_mx = _mingxian_cat_count(day_gan, gans, zhis, js_cat)
    ys_mx = _mingxian_cat_count(day_gan, gans, zhis, ys_cat)
    if strength in ('从强', '从弱'):
        # 从格看势以主气论（22期成势闸同口径：异党单五行干支主气≥3 方有势）：
        # 中/余气藏干不成势，难破格——忌神孤众之判按主气（透干/支本气）计。
        # qi40 从儿格：巳中戊印仅中气藏干（巳又被两亥冲去），实惟丑印一柱
        # 孤立犯众水（土荡自败），不论印夺食，书判「家道丰盈」。
        js_mx = _zhuqi_cat_count(day_gan, gans, zhis, js_cat)
    if js_mx <= 1 and ys_mx >= 2:
        return {'detected': False, 'kind': None, 'severity': None,
                'reason': f'孤忌犯众用：{js_cat}明现仅{js_mx}柱而{ys_cat}{ys_mx}柱，'
                          f'孤忌犯众自败（忌神被制化失能），不论{kind}',
                'strength': strength, 'hits': []}

    wa = _ensure_work_actions(day_gan, gans, zhis, work_actions)

    # ── 忌神失能三道豁免（K3-294批4，A2 假阳簇）──
    # R2 前提是忌神有力能制用神；忌神自身失原性/为我所得者不能制——
    # 与 R1b 功神被合绊失能（qi03「合绊…不克害用神」）同书锚族。
    # (a) 忌神被合绊：功神位为紧贴合绊失能方（六合受害方/天干五合互绊，
    #     口径同 _tiejie_heban_positions）——yx-巨富丑运 戌印被卯戌合绊，
    #     书明文丑运（印）发财几千万，印非夺食之忌神。
    _js_heban = _tiejie_heban_positions(gans, zhis)
    # (b) 贪合忘克：功神与被制者同入三字全之三合局，合化一行、局内不论
    #     相克——cj-老师 未印「克」亥食伤，然亥卯未全、未随局化财，
    #     书明文官统财合到主位、午运发财。
    from mangpai.objective.constants import SAN_HE as _SAN_HE
    _zhis_set = set(z for z in zhis if z)

    def _same_sanhe(pa: str, pb: str) -> bool:
        if not (pa.endswith('_zhi') and pb.endswith('_zhi')):
            return False
        za = zhis[_PK4.index(pa.rsplit('_', 1)[0])]
        zb = zhis[_PK4.index(pb.rsplit('_', 1)[0])]
        for grp in _SAN_HE:
            if len(grp) == 3 and za in grp and zb in grp and all(z in _zhis_set for z in grp):
                return True
        return False

    # (c) 自合柱之财为我得（G9 口径）：日支自合柱激活且支中合神即忌神
    #     同类（财）者，财合日主=财来就我、承载日主取用，非忌神坏印——
    #     yx-煤矿-2 壬午日午中丁财自合，书明文壬午运（财）发财十亿。
    _zihe_js_dayzhi = False
    try:
        from mangpai.objective.zihe import detect_zihe
        _dzh = detect_zihe(gans, zhis).get('day_zihe')
        _zihe_js_dayzhi = bool(
            _dzh and _dzh.get('activated')
            and _wx_cat(dw, GAN_WX.get(_dzh.get('he_shen', ''), '')) == js_cat)
    except Exception:
        pass

    hits: List[str] = []
    for a in wa:
        if a.get('auxiliary'):
            continue
        t = a.get('type', '')
        if t not in ('冲', '克', '穿', '破', '刑'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if not (fp and tp) or fp == 'day_gan':
            continue
        if fp in _js_heban:
            continue  # (a) 忌神被合绊失能，不能制用神
        if fp == 'day_zhi' and _zihe_js_dayzhi:
            continue  # (c) 日主自合之财（忌神同类）为我所得，不论忌神制用神
        fc = _wx_cat(dw, _pos_main_wx(fp, gans, zhis))
        tc = _wx_cat(dw, _pos_main_wx(tp, gans, zhis))
        if fc == js_cat and tc == ys_cat:
            if _same_sanhe(fp, tp):
                continue  # (b) 贪合忘克：同入三合局，局内不论相克
            hits.append(f'{t} {fp}({js_cat})→{tp}({ys_cat})')

    detected = bool(hits)
    severity = None
    reason = ''
    if detected:
        js_pillars = sum(1 for i in range(4)
                         if _wx_cat(dw, GAN_WX.get(gans[i], '')) == js_cat
                         or _wx_cat(dw, ZHI_WX.get(zhis[i], '')) == js_cat)
        severity = 'severe' if (js_pillars >= 2 or len(hits) >= 2) else 'normal'
        yx = {'财坏印': '贪财坏印（印主学业/名誉/单位/职位）',
              '印夺食': '枭神夺食（食伤主财源/自由/子女）'}[kind]
        reason = (f'忌神制用神·{kind}：{strength}{ys_cat}为用神、{js_cat}为忌神，'
                  f'{len(hits)}处{js_cat}制{ys_cat}（{js_cat}{js_pillars}柱），'
                  f'段氏「用神制忌神则吉」之逆=忌神制用神凶（{yx}）')
    return {
        'detected': detected, 'kind': kind if detected else None,
        'severity': severity, 'strength': strength,
        'hits': hits, 'reason': reason,
    }


def _zhuqi_cat_count(
    day_gan: str, gans: List[str], zhis: List[str], cat: str,
) -> int:
    """十神大类主气柱数（透干/支本气；藏干中余气不计——从格看势口径）。"""
    dw = GAN_WX.get(day_gan, '')
    n = 0
    for i in range(4):
        if i < len(gans) and gans[i] and _wx_cat(dw, GAN_WX.get(gans[i], '')) == cat:
            n += 1
            continue
        if i < len(zhis) and zhis[i] and _wx_cat(dw, ZHI_WX.get(zhis[i], '')) == cat:
            n += 1
    return n


# 地支六合受害方（R3 用）：与 objective.he_types 合克/合伤/闭气口径一致。
#   子丑：丑克子（子伤）+ 闭丑金库（丑伤）-> 两伤
#   卯戌：卯克戌 + 闭戌火库 -> 戌伤（《中级》「卯戌合绊了戌土」）
#   巳申：巳克申 -> 申伤
#   辰酉：酉克辰中乙木 + 闭辰水库 -> 辰伤
#   寅亥：亥克寅中丙火 -> 寅伤
#   午未：闭未木库 -> 未伤（午不受绊——李嘉诚未午合，午为用神仍合去亥水，
#         受害方是未（忌神），不触发 R3）
_LIUHE_VICTIMS: Dict[frozenset, frozenset] = {
    frozenset('子丑'): frozenset('子丑'),
    frozenset('寅亥'): frozenset('寅'),
    frozenset('卯戌'): frozenset('戌'),
    frozenset('辰酉'): frozenset('辰'),
    frozenset('巳申'): frozenset('申'),
    frozenset('午未'): frozenset('未'),
}

# 地支六合化气（合化方向，R3 合化豁免用）：子丑化土、寅亥化木、卯戌化火、
# 辰酉化金、巳申化水、午未化土。天干五合化气用 constants.HUA_YONG_MAP。
_LIUHE_HUAQI: Dict[frozenset, str] = {
    frozenset('子丑'): '土',
    frozenset('寅亥'): '木',
    frozenset('卯戌'): '火',
    frozenset('辰酉'): '金',
    frozenset('巳申'): '水',
    frozenset('午未'): '土',
}

_YANG_GANS = set('甲丙戊庚壬')
_PK4 = ['year', 'month', 'day', 'hour']
_PK4_CN = ['年', '月', '日', '时']


def _shishen_full(day_gan: str, gan: str) -> str:
    """gan 相对 day_gan 的十神（细分到正偏，伤官/正官判别用）。"""
    day_wx = GAN_WX.get(day_gan, '')
    g_wx = GAN_WX.get(gan, '')
    if not day_wx or not g_wx:
        return ''
    same = (day_gan in _YANG_GANS) == (gan in _YANG_GANS)
    if g_wx == day_wx:
        return '比肩' if same else '劫财'
    if WX_SHENG.get(day_wx) == g_wx:
        return '食神' if same else '伤官'
    if WX_SHENG.get(g_wx) == day_wx:
        return '偏印' if same else '正印'
    if WX_KE.get(day_wx) == g_wx:
        return '偏财' if same else '正财'
    if WX_KE.get(g_wx) == day_wx:
        return '七杀' if same else '正官'
    return ''


def _mingxian_shishen_positions(
    day_gan: str, gans: List[str], zhis: List[str], targets: Set[str],
) -> Set[str]:
    """十神细分（如 伤官/正官/七杀）明现位 pos 集合（透干/本气/中气；余气不算）。"""
    from mangpai.objective.canggan import get_canggan_mangpai
    pos: Set[str] = set()
    for i, pk in enumerate(_PK4):
        if i < len(gans) and gans[i] and _shishen_full(day_gan, gans[i]) in targets:
            pos.add(f'{pk}_gan')
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _q) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break  # 余气不算明现
                if _shishen_full(day_gan, cg) in targets:
                    pos.add(f'{pk}_zhi')
                    break
    return pos


def _mingxian_cat_count(
    day_gan: str, gans: List[str], zhis: List[str], cat: str,
) -> int:
    """十神大类明现柱数（透干/本气/中气；一柱只计一次）。"""
    from mangpai.objective.canggan import get_canggan_mangpai
    dw = GAN_WX.get(day_gan, '')
    n = 0
    for i in range(4):
        found = False
        if i < len(gans) and gans[i]:
            found = _wx_cat(dw, GAN_WX.get(gans[i], '')) == cat
        if not found and i < len(zhis) and zhis[i]:
            if _wx_cat(dw, ZHI_WX.get(zhis[i], '')) == cat:
                found = True
            else:
                for idx, (cg, _q) in enumerate(get_canggan_mangpai(zhis[i])):
                    if idx > 1:
                        break
                    if _wx_cat(dw, GAN_WX.get(cg, '')) == cat:
                        found = True
                        break
        if found:
            n += 1
    return n


# ───────────────────── 原局级凶向三式（N1/N2/N3，段氏高级篇锚定） ─────────────────────

def detect_shangguan_jianguan(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """伤官见官为忌检测（N1）。

    段氏锚定：《高级内容篇》「财星坏印是大忌，伤官见官贵气损」「伤官旺而无制，
    特别是伤官见官，主叛逆、反抗权（官非）」；与「伤官去官格」（官星为忌、
    伤官将其克去=得官吉）对偶——同一伤官见官，官为用神被伤则贵气受损为凶，
    官为忌神被去则吉。故以扶抑用忌定吉凶向：

    判定：官杀为扶抑用神（身强/从弱）+ 伤官明现 + 正官明现 + 存在非辅助
    冲/克/穿/破/刑 做功使伤官实伤其官（冲/穿双向，余取 from=伤官位 to=正官位）。
    只取伤官（非食神）对正官（非七杀）：食神制官、伤官驾杀为段氏职业正途
    （律师/公检法/武职），不以凶论。身弱/从强（官为忌，伤官去官=吉）与
    中和/不明（不定用忌）俱不触发，防过火。

    Returns:
        {'detected': bool, 'severity': 'normal'|None, 'strength': str,
         'hits': [str], 'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'severity': None, 'reason': ''}
    strength = classify_strength(day_gan, gans, zhis)
    ys, _js = _yongshen_cats(strength)
    if '官杀' not in ys:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}
    shang_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'伤官'})
    guan_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'正官'})
    if not (shang_pos and guan_pos):
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}

    wa = _ensure_work_actions(day_gan, gans, zhis, work_actions)
    hits: List[str] = []
    for a in wa:
        if a.get('auxiliary'):
            continue
        t = a.get('type', '')
        if t not in ('冲', '克', '穿', '破', '刑'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if not (fp and tp):
            continue
        if t in ('冲', '穿'):
            if (fp in shang_pos and tp in guan_pos) or (fp in guan_pos and tp in shang_pos):
                hits.append(f'{t} {fp}(伤官)×{tp}(正官)')
        elif fp in shang_pos and tp in guan_pos:
            hits.append(f'{t} {fp}(伤官)→{tp}(正官)')

    # ── 书锚豁免（段氏总诀「伤官见官分宜畏，全在五行与节令」）──
    exemption = ''
    if hits:
        # 豁免一：伤官诀五类（juefa.py 已实现五行×节令分向）——金水伤官喜见官
        # （调候暖局）、水木伤官喜财官（财官相佐）、伤官佩印（印来制伤贵气生）
        # 者，见官为格局所需，非「贵气损」。
        try:
            from mangpai.subjective.juefa import analyze_juefa
            sg = analyze_juefa(gans, zhis, day_gan).get('shangguan_jue') or {}
        except Exception:
            sg = {}
        vd = sg.get('verdict', '') if sg.get('matched') else ''
        for key in ('喜见官', '喜财官', '伤官佩印'):
            if key in vd:
                exemption = (f'伤官诀·{sg.get("type", "")}「{vd}」：'
                             f'见官为格局所需（总诀「分宜畏，全在五行与节令」），'
                             f'不以贵气损论')
                break
        # 豁免二：伤官配印——印明现且印制伤官做功（非辅助 冲/克/穿/破/刑，
        # 冲穿双向），伤官被制伏，见官不凶（「印来制伤贵气生」，伤官配印贵格）。
        # 印位须为第三方纯印位（排除官位/伤官位兼带印气的同柱——如同一午火
        # 既为正官又藏己印，官伤之战不可误读为印制伤）。
        if not exemption:
            yin_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'正印', '偏印'})
            yin_pure = yin_pos - guan_pos - shang_pos
            if yin_pure:
                for a in wa:
                    if a.get('auxiliary'):
                        continue
                    t = a.get('type', '')
                    if t not in ('冲', '克', '穿', '破', '刑'):
                        continue
                    fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
                    if t in ('冲', '穿'):
                        if (fp in yin_pure and tp in shang_pos) or (fp in shang_pos and tp in yin_pure):
                            exemption = '伤官配印：印明现制伏伤官，见官不凶（印来制伤贵气生）'
                            break
                    elif fp in yin_pure and tp in shang_pos:
                        exemption = '伤官配印：印明现制伏伤官，见官不凶（印来制伤贵气生）'
                        break
        # 豁免三：财星通关——财明现且伤官见官动作非冲/穿实战（克/刑/破为
        # 可流转之战），伤官贪生财而忘克官（水木伤官「财官相佐福禄盈」、
        # 伤官生财财转生官通关）。
        if not exemption:
            cai_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'正财', '偏财'})
            if cai_pos and not any(h.startswith(('冲', '穿')) for h in hits):
                exemption = '财星通关：财明现，伤官贪生财忘克官（财官相佐），见官不凶'

    detected = bool(hits) and not exemption
    reason = ''
    if detected:
        reason = (f'伤官见官为忌：{strength}正官为用神，伤官明现实伤其官'
                  f'（{len(hits)}处），段氏「伤官见官贵气损」'
                  f'（官非/贵气受损；官为忌神之伤官去官格不在此列）')
    return {'detected': detected, 'severity': 'normal' if detected else None,
            'strength': strength, 'hits': hits, 'exemption': exemption,
            'reason': reason}


def detect_caisheng_sha_gongshen(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """财生杀攻身检测（N2，severe）。

    段氏锚定：《高级内容篇》「身弱财官旺，财生官杀而攻身，为财党杀、杀攻身」
    （案例四 甲寅丙寅庚辰戊寅：财旺生杀、杀攻身而印星救应无力，因财致祸凶格）；
    《理象学》「财生杀为忌」。对偶豁免：从弱/从财格杀为用神（财生杀=生用，
    「财生杀局官杀当财看为巨富之潜质」）、身强能担、杀有制（制杀得财）、
    印化杀有力（杀印相生贵格）俱不论凶。

    判定：身弱（仅身弱——从弱杀为用不攻身，中和不定防过火）+ 财明现≥2位
    （财旺生杀有力）+ 七杀明现且贴身（月/日/时柱，攻身须贴身，年杀不论）
    + 杀无制（无非辅助制杀动作）+ 印化无力（印不明现，或印明现但被财制——
    段氏「印星救应无力」）。

    Returns:
        {'detected': bool, 'severity': 'severe'|None, 'strength': str,
         'hits': [str], 'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'severity': None, 'reason': ''}
    dw = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(dw, '')
    sha_wx = ''
    for w, c in WX_KE.items():
        if c == dw:
            sha_wx = w  # 克我者=官杀五行
            break
    strength = classify_strength(day_gan, gans, zhis)
    if strength != '身弱' or not cai_wx or not sha_wx:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}
    if WX_SHENG.get(cai_wx) != sha_wx:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}

    cai_cnt = _mingxian_cat_count(day_gan, gans, zhis, '财')
    if cai_cnt < 2:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}
    sha_all = _mingxian_shishen_positions(day_gan, gans, zhis, {'七杀'})
    sha_tie = {p for p in sha_all if not p.startswith('year_')}  # 贴身=月/日/时
    if not sha_tie:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}

    wa = _ensure_work_actions(day_gan, gans, zhis, work_actions)
    # 杀无制：无非辅助 冲/克/穿/破/刑 以杀位为被制方（to_pos；冲/穿双向）；
    # 合杀同论——合以制之/合去（《授课教程》「癸水杀星为忌虚透，戊癸合去之
    # 无害」；巾箱诀「食神制杀合杀贵…制住忌神便成名」），杀被合制/合去即
    # 有制化，不攻身。
    sha_zhi = False
    for a in wa:
        if a.get('auxiliary'):
            continue
        t = a.get('type', '')
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if t in ('冲', '克', '穿', '破', '刑'):
            if t in ('冲', '穿'):
                if fp in sha_tie or tp in sha_tie:
                    sha_zhi = True
                    break
            elif tp in sha_tie:
                sha_zhi = True
                break
        elif t in ('天干合', '地支合', '暗合', '半合'):
            if fp in sha_tie or tp in sha_tie:
                sha_zhi = True
                break
    if sha_zhi:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}
    # 印化无力判定：印明现且未被财制 -> 杀印相生有救应，不触发
    yin_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'正印', '偏印'})
    if yin_pos:
        cai_pos = _mingxian_shishen_positions(day_gan, gans, zhis, {'正财', '偏财'})
        yin_zhi = False
        for a in wa:
            if a.get('auxiliary'):
                continue
            t = a.get('type', '')
            if t not in ('冲', '克', '穿', '破', '刑'):
                continue
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            if t in ('冲', '穿'):
                if (fp in cai_pos and tp in yin_pos) or (fp in yin_pos and tp in cai_pos):
                    yin_zhi = True
                    break
            elif fp in cai_pos and tp in yin_pos:
                yin_zhi = True
                break
        if not yin_zhi:
            return {'detected': False, 'severity': None, 'reason': '',
                    'strength': strength}

    hits = [f'财{cai_cnt}位生杀，七杀贴身无制（{sorted(sha_tie)}）']
    reason = (f'财生杀攻身：身弱财旺（明现{cai_cnt}位）生七杀贴身、杀无制、'
              f'印化无力，段氏「财党杀、杀攻身」因财致祸凶格')
    # 严重度 normal（封顶小康）：财生杀局亦可为大富潜质（段氏案例二从弱巨富；
    # 身弱者有制杀之运仍发——凶向标记供「因财致祸」断语，不强行压贫）
    return {'detected': True, 'severity': 'normal', 'strength': strength,
            'hits': hits, 'reason': reason}


def detect_guansha_rumu_xiong(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """官杀入墓为忌检测（N3）。

    段氏锚定：《高级内容篇》「官杀入墓：官杀星入辰戌丑未墓库，墓库不开，
    反主被官方收藏、关押」（官非牢狱之象）。判定限**身弱**（杀为忌神）：
    杀攻身而身被官所收=被关押之凶；身强官为用神入墓（失权罢官）属官运域
    判断，且富贵局上系统性过火（同 laoyu 不计入否决链之鉴），不入财命
    凶向链。从格（从杀/从弱统杀为权——阎锡山丑统命局七杀掌兵权）与
    中和/不明（不定用忌）俱不论凶。

    判定：身弱 + 官杀明现 + 官杀五行入墓且墓未开
    （消费 laoyu.detect_guansha_rumu 同口径）。

    Returns:
        {'detected': bool, 'severity': 'normal'|None, 'strength': str,
         'hits': [str], 'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'severity': None, 'reason': ''}
    strength = classify_strength(day_gan, gans, zhis)
    if strength != '身弱':
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}
    try:
        from mangpai.subjective.laoyu import detect_guansha_rumu
        r = detect_guansha_rumu(day_gan, gans, zhis, relations=relations)
    except Exception:
        r = {}
    detected = bool(r.get('laoyu_signal'))
    # 墓之宾主归属（高级篇 2.5「以主位之墓库，去收藏、控制…墓库制忌，其祸
    # 自消」）：杀（忌）入主位（日/时）之墓=我把忌神困入牢笼=制忌自消（主位
    # 之墓为我所掌控，如官杀入墓类象「权力中心/军队营地」）；杀入宾位（年/月）
    # 之墓方为「被官方收藏、关押」。故墓在主位者不入凶向链。
    exemption = ''
    tomb_zhi = r.get('tomb_zhi', '')
    if detected and tomb_zhi and tomb_zhi in (zhis[2], zhis[3]):
        detected = False
        exemption = (f'墓在主位（{tomb_zhi}为日/时支）：杀忌入主位之墓=制忌自消'
                     f'（主位墓库为我所掌控），非被官方关押，不论凶')
    reason = ''
    hits: List[str] = []
    if detected:
        hits = list(r.get('details') or [])
        reason = (f'官杀入墓：{strength}，官杀（{r.get("guan_wx", "")}五行）入墓'
                  f'{r.get("tomb_zhi", "")}未开，段氏「墓库不开，反主被官方收藏、关押」'
                  f'（官非失权；从格统杀为权不在此列）')
    return {'detected': detected, 'severity': 'normal' if detected else None,
            'strength': strength, 'hits': hits, 'exemption': exemption,
            'reason': reason}


def detect_heban_yongshen(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """用神被合绊检测（R3）。

    判定：扶抑定用忌（中和/不明不定，不触发）；扫原局**紧贴**（相邻柱）合：
      - 地支六合：受害方（_LIUHE_VICTIMS，合克/合伤/闭气之被伤侧）十神为
        用神 -> 命中（化例三中堂 子丑合绊丑根 正例；受害方为忌神=忌神被绊吉，
        不触发，如 李嘉诚 未午合）；
      - 天干五合：互绊（合即双方失去原性），但只判他干紧贴（年干×月干）；
        日干参与之合属 zuogong「合用」做功层（合财/合官），不在此论。
    **做功参与抑制**：受绊方若同时参与非辅助**冲/穿**（from/to 任一），则该神
    已入局交战、未「失去原性」，合不能废其用——不触发（段氏「相冲可破局破合…
    相合与相冲兼论」之义；奥纳西斯 未午合而未入丑未冲做功，段氏论巨富不论绊）。
    克/刑/破不参与抑制：克为单向施力，被克非入局、克他亦不证其用。
    **合化出喜用豁免（P1）**：合之化气五行属喜用类且异于受害方本行者，合非
    「绊住失用」而是「向化喜用」，不论凶绊（森田健 卯戌合化火=印——段氏论
    此造「卯戌合绊，戌根失去力量」是说身弱，又明文「需行火运生扶日主则好」，
    合之化气正是其所喜；合绊计入身弱后不再双重计入凶向，其造 gold=富）。
    化气仍为受害方本行者合仅是绊（qi03 寅亥合化木、寅本木，「故不吉」），
    化出忌神者更不豁免。
    严重度：命中≥2处 -> severe。

    Returns:
        {'detected': bool, 'severity': 'severe'|'normal'|None,
         'strength': str, 'hits': [str], 'reason': str}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'detected': False, 'severity': None, 'reason': ''}
    dw = GAN_WX.get(day_gan, '')
    strength = classify_strength(day_gan, gans, zhis)
    ys, _js = _yongshen_cats(strength)
    if not ys:
        return {'detected': False, 'severity': None, 'reason': '', 'strength': strength}

    # 做功参与抑制：收集非辅助冲/穿的参与柱位（from/to 任一，双向交战）
    engaged: Set[str] = set()
    for a in _ensure_work_actions(day_gan, gans, zhis, work_actions):
        if a.get('auxiliary'):
            continue
        if a.get('type', '') not in ('冲', '穿'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if fp:
            engaged.add(fp)
        if tp:
            engaged.add(tp)

    hits: List[str] = []
    _PK = ['year', 'month', 'day', 'hour']
    _PK_CN = ['年', '月', '日', '时']
    # ── 地支六合（紧贴，受害方判定）──
    # 双侧顺势豁免：受害方为用神，但合之对方亦属用神类（顺势）者——两用神
    # 相合为顺势内部生合（如原神合财：从财格亥合寅，原神生财非失用，22期
    # 例1 乙亥年发财正例），不论绊；合之对方为忌神者方论绊（qi03「戊寅年
    # 本寅为喜神来生火，逢寅亥相合，喜神被合绊，故不吉」——彼造亥为忌神）。
    # 从格异党合去豁免（G5，30期作业答案 ans30 从禄格「丁火合去壬水财星」/
    # 32期「两忌神合绊主吉」）：从格一方成势，合对中异党（忌神）方**孤立**
    # （明现≤1）者，合去即成净——忌神被合去为主导语义（去忌得忌喜），不单论
    # 用神侧受绊（势在局不在字，一合不能损其势）；异党多现者合去不尽，仍论绊。
    ys, js = _yongshen_cats(strength)
    cong_hequ_exempt = strength in ('从强', '从弱')

    # G9 财合日主豁免（48期自合柱 + 《授课教程》例134 戊子日）：日支为激活
    # 自合柱且支中合神为财者，日主合财=财为我所合得（视同合财做功——该财正
    # 承载日主取用，未「失去原性」），邻支六合不能夺其用：例134 子丑合书
    # 明读「丑土不克水」——受绊失能者是克财之比劫（忌神侧），日支自合之财
    # 不失用（身旺财旺发财）。与 caiming G9 日主自合合财升档同口径。
    _day_cai_zihe = False
    try:
        from mangpai.objective.zihe import detect_zihe
        _dzh = detect_zihe(gans, zhis).get('day_zihe')
        _day_cai_zihe = bool(
            _dzh and _dzh.get('activated')
            and _wx_cat(dw, GAN_WX.get(_dzh.get('he_shen', ''), '')) == '财')
    except Exception:
        pass

    def _huaqi_exempt(huaqi: str, victim_wx: str) -> bool:
        """合化出喜用豁免（P1 R3 精化）：合之化气五行属喜用类且异于受害方
        本行者，合非「绊住失用」而是「向化喜用」——受害方经合转化为喜用
        之气，不论凶绊（森田健卯戌合化火=印，段氏明文「需行火运生扶日主
        则好」；下岗财会丁壬合化木=印；li002 丙辛合化水=财）。
        化气仍为受害方本行者，合仅是绊住本字（qi03 寅亥合化木、寅本木，
        段氏明文「喜神被合绊，故不吉」）；化出忌神者更不豁免。"""
        return bool(huaqi) and huaqi != victim_wx and _wx_cat(dw, huaqi) in ys

    def _ji_isolated(wx: str) -> bool:
        """忌神五行孤立（明现≤1：透干或支主气）：孤立者被合去即成净
        （段氏「合去」=去除——ans30 壬财孤立，丁合去之则忌神净；乙财两见
        者合去一处仍有余，不尽，不论合去）。
        从格日主不计同党之援（K3-294批4）：从格日主无根不能自立、其气
        已从势，非异党之根援——cj-富发财 从弱，丙日主不计火党，丁劫
        孤立被壬杀合去=忌神净吉（书明文戊申运会官杀局制劫发财）。"""
        n = sum(1 for k, g in enumerate(gans)
                if k != 2 and GAN_WX.get(g) == wx) + \
            sum(1 for z in zhis if ZHI_WX.get(z) == wx)
        return n <= 1
    for i in range(3):
        a, b = zhis[i], zhis[i + 1]
        victims = _LIUHE_VICTIMS.get(frozenset(a + b)) if a and b else None
        if not victims:
            continue
        for j, z in ((i, a), (i + 1, b)):
            if z in victims and f'{_PK[j]}_zhi' not in engaged:
                cat = _wx_cat(dw, ZHI_WX.get(z, ''))
                if j == 2 and _day_cai_zihe and cat == '财':
                    continue  # G9 财合日主：日支自合之财已合入我身，邻合不夺其用
                if cat in ys:
                    partner = zhis[i + 1] if j == i else zhis[i]
                    pcat = _wx_cat(dw, ZHI_WX.get(partner, ''))
                    if pcat in ys:
                        continue  # 双侧顺势生合，不论绊
                    if cong_hequ_exempt and pcat in js \
                            and _ji_isolated(ZHI_WX.get(partner, '')):
                        continue  # 从格异党孤立合去=吉（忌神被合去成净），不论绊
                    if _huaqi_exempt(_LIUHE_HUAQI.get(frozenset(a + b), ''),
                                     ZHI_WX.get(z, '')):
                        continue  # 合化出喜用（化气≠本行且属喜用类），不论凶绊
                    hits.append(f'{a}{b}合绊 {_PK_CN[j]}支{z}({cat}为用神受绊)')
    # ── 天干五合（他干紧贴=年干×月干，互绊）──
    # 日主争合整对豁免（K3-294批4，限扶抑格）：日主与该五合之一方相合者，
    # 合对两干皆在日主争合/合用之境（zuogong「合用」做功层：合财/合官），
    # 未「失去原性」，整对不论绊——yx-医师（身弱）两壬争合丁财，年干比肩
    # 为日主争财之援非受绊（书明文卯运伤官生财年入百万）。**从格不论**：
    # 从格论势不论争合取用，异党相缠非「我取之用」（庚乙庚乙从强比劫包局
    # 锚：年干庚被乙财合仍论绊）；从格仅保留 j==1 日主合用单点抑制
    # （丙申辛丑丙申己亥从财格日主合辛财=得财，不触发）。
    # 从格异党合去豁免（G5）：合对一方为异党（忌神）者，忌神被合去=吉
    # （ans30 从禄格 丁壬合去壬财忌神），不单论用神侧受绊。
    g0, g1 = gans[0], gans[1]
    _zhenghe_pair_exempt = strength not in ('从强', '从弱') \
        and TIAN_GAN_HE.get(day_gan) in (g0, g1)
    if g0 and g1 and TIAN_GAN_HE.get(g0) == g1 and not _zhenghe_pair_exempt:
        for j, g in ((0, g0), (1, g1)):
            cat = _wx_cat(dw, GAN_WX.get(g, ''))
            if cat in ys and f'{_PK[j]}_gan' not in engaged:
                if j == 1 and TIAN_GAN_HE.get(day_gan) == g:
                    continue  # 日主合用做功（从格顺势合财=得财），月干用神未失原性
                if cong_hequ_exempt:
                    partner_g = g1 if j == 0 else g0
                    if _wx_cat(dw, GAN_WX.get(partner_g, '')) in js \
                            and _ji_isolated(GAN_WX.get(partner_g, '')):
                        continue  # 从格异党孤立合去=吉，不论绊
                if _huaqi_exempt(HUA_YONG_MAP.get((g0, g1), ''), GAN_WX.get(g, '')):
                    continue  # 合化出喜用（化气≠本行且属喜用类），不论凶绊
                hits.append(f'{g0}{g1}合 {_PK_CN[j]}干{g}({cat}为用神受绊)')

    detected = bool(hits)
    severity = None
    reason = ''
    if detected:
        severity = 'severe' if len(hits) >= 2 else 'normal'
        reason = (f'用神被合绊：{strength}，{len(hits)}处用神紧贴受合'
                  f'（段氏「紧贴相合为绊，谁都无法发挥作用，为失去原性」，'
                  f'用神失用凶；忌神受绊为吉不触发）')
    return {
        'detected': detected, 'severity': severity, 'strength': strength,
        'hits': hits, 'reason': reason,
    }


def _ensure_zhengfan(day_gan: str, gans: List[str], zhis: List[str],
                     relations: Optional[Dict]) -> Dict:
    try:
        from mangpai.subjective.zhengfan import analyze_zhengfan
        from mangpai.subjective.zuogong_confirm import analyze_zuogong
        zg = analyze_zuogong(
            day_gan, zhis[2], gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
        wa = zg.get('work_actions') or []
        # day_he_type 简单留空（zhengfan 容许 None）
        return analyze_zhengfan(wa, None, gans, zhis)
    except Exception:
        return {}


def _ensure_laoyu(day_gan: str, gans: List[str], zhis: List[str],
                  relations: Optional[Dict]) -> Dict:
    try:
        from mangpai.subjective.laoyu import analyze_laoyu
        return analyze_laoyu(day_gan, gans, zhis, relations=relations)
    except Exception:
        return {}


# ───────────────────── G1 十干喜忌（11期，标注层） ─────────────────────
# 《授课教程》第十一期「十干喜忌概论」：郝先生口诀「甲生酉月喜水润，乙生酉月
# 用火攻」。段氏明示「切不可用作死套」「不可用一种衰旺的模子来套」——故本表
# 只作**标注层**（direction 总线小权重辅助票/注记），不作扶抑用神主判据。
# 结构：干 -> {季节 -> (喜[五行], 忌[五行], 注)}；'all'=四季通论。
# 季节：寅卯辰=春，巳午未=夏，申酉戌=秋，亥子丑=冬。
_GAN_XIJI: Dict[str, Dict[str, tuple]] = {
    '甲': {
        '春': (['水', '火'], ['金'], '春木喜水火有节，脱胎要火、春不容金'),
        '夏': (['水'], [], '夏木为禾稼最宜水，有水则贵无水则贫'),
        '秋': (['水'], ['土'], '甲生酉月喜水润（喜水怕土）'),
        '冬': (['火'], [], '冬木为寒木，最喜火暖局调候，无火则贫贱'),
    },
    '乙': {
        '春': (['水'], ['火'], '春乙宜水不宜火，宜结党会局'),
        '夏': (['水'], [], '夏木为禾稼最宜水'),
        '秋': (['火'], ['水'], '乙生酉月用火攻（喜火怕水）'),
        '冬': (['火'], [], '寒木喜火调候'),
    },
    '丙': {
        'all': (['木'], ['土'], '丙如太阳，怕湿土/燥土晦火，遇之则喜木；要抑其性不可助其威'),
    },
    '丁': {
        'all': (['木'], ['土'], '丁如烛灯，衰时宜甲乙生助；怕湿土/燥土晦火；忌透丙夺光'),
    },
    '戊': {
        '春': (['火'], [], '春戊为薄土，最爱丙火太阳普照'),
        '秋': (['火'], [], '秋戊（不含戌月）为薄土喜丙；戌月通根顽固怕火，宜泄宜耗'),
        '冬': (['火'], [], '冬戊更喜见丙'),
        '夏': ([], [], '夏戊很少能有贵格'),
    },
    '己': {
        'all': (['金', '火'], [], '己土旺则喜辛金，衰则喜禄（丁为己禄，多喜丁火）'),
    },
    '庚': {
        'all': (['火', '水', '土'], [], '庚要么顺其性要么逆其性：克用旺火、泄用旺水、生用旺湿土；不可亦顺亦逆'),
    },
    '辛': {
        '夏': (['水'], [], '夏辛遭克，最喜见癸水'),
        '冬': (['火'], [], '冬辛遇寒，最宜见丁火'),
        'all': ([], ['土'], '辛怕土重埋没无光；爱食神与禄神，少爱印绶'),
    },
    '壬': {
        'all': (['木'], [], '壬水最爱寅木（依托/泄秀），喜甲不喜卯乙'),
    },
    '癸': {
        'all': (['木', '火'], [], '癸水从木火或化气最好；见庚辛申酉扶助不过平常'),
    },
}

_SEASON_OF_ZHI: Dict[str, str] = {
    '寅': '春', '卯': '春', '辰': '春',
    '巳': '夏', '午': '夏', '未': '夏',
    '申': '秋', '酉': '秋', '戌': '秋',
    '亥': '冬', '子': '冬', '丑': '冬',
}


def gan_xiji_annotate(day_gan: str, month_zhi: str) -> Dict:
    """十干喜忌标注（G1，11期）：日主×月令 -> 喜/忌五行注记。

    返回 {'season', 'xi', 'ji', 'month_wx', 'month_fit', 'note'}：
    month_fit ∈ {'喜','忌','平',''} ——月令本气五行是否落在该干当月喜/忌栏
    （标注层辅助票，不作扶抑用神主判据——段氏「不可用作死套」）。
    """
    out = {'season': '', 'xi': [], 'ji': [], 'month_wx': '', 'month_fit': '', 'note': ''}
    tbl = _GAN_XIJI.get(day_gan)
    if not tbl:
        return out
    season = _SEASON_OF_ZHI.get(month_zhi, '')
    month_wx = ZHI_WX.get(month_zhi, '')
    xi: List[str] = []
    ji: List[str] = []
    notes: List[str] = []
    for key in (season, 'all'):
        ent = tbl.get(key)
        if ent:
            xi.extend(w for w in ent[0] if w not in xi)
            ji.extend(w for w in ent[1] if w not in ji)
            if ent[2]:
                notes.append(ent[2])
    fit = ''
    if month_wx:
        if month_wx in xi:
            fit = '喜'
        elif month_wx in ji:
            fit = '忌'
        else:
            fit = '平'
    out.update({
        'season': season, 'xi': xi, 'ji': ji, 'month_wx': month_wx,
        'month_fit': fit,
        'note': f'{day_gan}生{season}（{month_zhi}月）：喜{"、".join(xi) or "—"}'
                f'，忌{"、".join(ji) or "—"}；月令{month_wx}={fit}（11期十干喜忌·'
                f'标注层不作主判据：{"；".join(notes)}）' if season else '',
    })
    return out


def direction_brief(direction_result: Optional[Dict]) -> Dict:
    """方向总线·精简切片（A3）：供各领域模块录入输出的标准形态。

    assess_direction_signals 的全量字典含子结构（bijiao_duocai/suiyun_reasons
    等），领域模块输出只需精简方向切片：方向、是否反局/岁运反局、是否破财、
    是否用忌神向（R2/R3）、严重度与理由。缺省/异常输入安全返回中性。
    """
    d = direction_result or {}
    return {
        'direction': d.get('direction', '中性'),
        'fanju': bool(d.get('fanju')),
        'suiyun_fanju': bool(d.get('suiyun_fanju')),
        'pocai': bool(d.get('pocai')),
        'pocai_severe': bool(d.get('pocai_severe')),
        'yongshen_xiong': bool(d.get('yongshen_xiong')),
        'mingju_xiong': bool(d.get('mingju_xiong')),
        'reasons': list(d.get('reasons') or []),
        # G5/G1 标注（不影响吉凶判定）
        'cong_label': (d.get('cong_target') or {}).get('label', ''),
        'gan_xiji_fit': (d.get('gan_xiji') or {}).get('month_fit', ''),
    }


def assess_direction_signals(
    day_gan: str, gans: List[str], zhis: List[str],
    *,
    relations: Optional[Dict] = None,
    gongliang_result: Optional[Dict] = None,
    zhengfan_result: Optional[Dict] = None,
    laoyu_result: Optional[Dict] = None,
    work_actions: Optional[List[Dict]] = None,
    yunfan_result: Optional[Dict] = None,
) -> Dict:
    """聚合「凶向」信号，供 caiming/guanming/zhiye 反哺降档/否决。

    凶向 = 反局(fan，原局反局 OR 当前运岁反局) OR 坐牢(risk≥中) OR 比劫夺财(R1)
    OR 过河拆桥破财 OR 忌神制用神(R2) OR 用神被合绊(R3)。

    yunfan_result（A1）：「当前运岁」反局切片（yunfan.current_fan_slice 产出，
    含 dayun_fan/liunian_fan/sui_yun_liandong 三键）。原局本正而运岁引动反局
    者，其岁为凶（《高级命理学》3.3「变而反局，灾祸立现」）——与原局反局同链
    消费：财命封顶/官命否决（同受正向官命结构门槛保护）/军警 gating。

    Returns:
        {'direction': '吉'|'凶'|'中性',
         'fanju': bool, 'suiyun_fanju': bool, 'laoyu_risk': str,
         'bijiao_duocai': {...}, 'pocai': bool, 'pocai_severe': bool,
         'guohe_pocai': bool,
         'jishen_zhiyongshen': {...}, 'heban_yongshen': {...},
         'yongshen_xiong': bool, 'reasons': [str], 'suiyun_reasons': [str]}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'direction': '中性', 'fanju': False, 'suiyun_fanju': False,
                'laoyu_risk': '无',
                'bijiao_duocai': {}, 'pocai': False, 'pocai_severe': False,
                'guohe_pocai': False,
                'jishen_zhiyongshen': {}, 'heban_yongshen': {},
                'yongshen_xiong': False, 'reasons': [], 'suiyun_reasons': []}

    gl = gongliang_result or {}
    # R1：优先读 gongliang 已算得的 pocai_signal；缺省自算
    bijiao = {}
    if gl.get('pocai_signal'):
        bijiao = {'detected': True, 'severity': gl.get('pocai_severity') or 'normal',
                  'reason': gl.get('pocai_reason', '')}
    else:
        bijiao = detect_bijiao_duocai(day_gan, gans, zhis, work_actions)

    # R2/R3：忌神制用神（财坏印/印夺食）+ 用神被合绊（缺省自算，做功数据复用 R1 链）
    r2 = detect_jishen_zhiyongshen(day_gan, gans, zhis, work_actions)
    r3 = detect_heban_yongshen(day_gan, gans, zhis, work_actions)
    yongshen_xiong = bool(r2.get('detected')) or bool(r3.get('detected'))

    # N1/N2/N3：原局级凶向三式（伤官见官为忌/财生杀攻身/官杀入墓，段氏高级篇锚定）
    # 补原局层凶向检测——此前凶✅多靠评测器喂入运岁触发岁运反局 artifact 偶然供给，
    # 原局级只抓极少数；三式皆原局结构，与岁运无涉。
    n1 = detect_shangguan_jianguan(day_gan, gans, zhis, work_actions)
    n2 = detect_caisheng_sha_gongshen(day_gan, gans, zhis, work_actions)
    n3 = detect_guansha_rumu_xiong(day_gan, gans, zhis, relations)
    # N4：官非牢狱复合（段氏牢狱五法「命中占其一即有牢狱之象，占多者灾重」
    # 收口——五法单式泛火严重，laoyu 聚合 risk 在富贵局系统性过火，故仅以
    # 「最特异两法俱中」为官非牢狱凶向：魁罡逢冲官（庚辰/壬辰/庚戌/戊戌日
    # 逢刑冲官杀，高级篇 ch11）∧ 枭神夺食（食伤做功之神被夺，失去自由坐牢，
    # 中级牢狱专辑法三）。全库命中面实测仅 4 例（li094/ans31 两牢狱金标在内，
    # famous23 与 trainset 零命中），方入凶向链。缺省自调 laoyu（与 ly 同链，
    # 不重复计算——见下方 laoyu_result 处理，此处先置 None 待 ly 就绪后补判）。
    n4: Dict = {'detected': False, 'severity': 'normal', 'reason': ''}
    mingju_xiong = bool(n1.get('detected')) or bool(n2.get('detected')) \
        or bool(n3.get('detected'))
    # severe 预留（当前三式俱 normal——凶向标记供「因财致祸/官非」断语，
    # 不强行压贫；severe 封顶贫仍由比劫夺财 pocai_severe 承担）
    mingju_xiong_severe = any(n.get('severity') == 'severe' for n in (n1, n2, n3))

    zf = zhengfan_result or _ensure_zhengfan(day_gan, gans, zhis, relations)
    ly = laoyu_result or _ensure_laoyu(day_gan, gans, zhis, relations)

    # N4 补判（ly 就绪后）：魁罡逢冲官 ∧ 枭神夺食 两法俱中 = 占多灾重之
    # 官非牢狱（判据与命中面见上方 N4 注释；severity 同 N1/N2/N3 俱 normal）。
    if ly:
        _kg = (ly.get('kuigang') or {})
        _xd = (ly.get('xiao_duo_shi') or {})
        if _kg.get('laoyu_signal') and _xd.get('xiao_duo_shi'):
            n4 = {'detected': True, 'severity': 'normal',
                  'reason': '官非牢狱·魁罡逢冲官兼枭神夺食（段氏牢狱五法占多灾重）'}
            mingju_xiong = True

    natal_fanju = bool(zf and zf.get('type') == 'fan')

    # 岁运反局（A1）：当前运/岁反局 + 岁运联动，接入同一否决链。
    # 流年 fans 内已含岁运联动条目（fans.extend(sui_fans)），故流年段跳过
    # 「岁运联动」前缀，联动单独列段，避免同一信号双计。
    suiyun_reasons: List[str] = []
    sy = yunfan_result or {}
    for d in (sy.get('dayun_fan') or []):
        for f in (d.get('fans') or []):
            suiyun_reasons.append(f"岁运反局·大运{d.get('gz', '')}：{f.get('fan_type', '')}")
    for d in (sy.get('liunian_fan') or []):
        for f in (d.get('fans') or []):
            ft = f.get('fan_type', '')
            if ft.startswith('岁运联动'):
                continue
            suiyun_reasons.append(f"岁运反局·流年{d.get('gz', '')}({d.get('year', '')})：{ft}")
    for d in (sy.get('sui_yun_liandong') or []):
        for f in (d.get('liandong') or []):
            suiyun_reasons.append(f"岁运联动·{d.get('gz', '')}({d.get('year', '')})：{f.get('fan_type', '')}")
    suiyun_fanju = bool(suiyun_reasons)
    # G5 岁运吉向标注（合去/合绊忌神=去忌得忌喜；标注层，不入凶向否决链）
    suiyun_ji_reasons: List[str] = []
    for d in (sy.get('dayun_ji') or []):
        for f in (d.get('jis') or []):
            suiyun_ji_reasons.append(f"岁运吉向·大运{d.get('gz', '')}：{f.get('ji_type', '')}")
    for d in (sy.get('liunian_ji') or []):
        for f in (d.get('jis') or []):
            suiyun_ji_reasons.append(f"岁运吉向·流年{d.get('gz', '')}({d.get('year', '')})：{f.get('ji_type', '')}")

    fanju = natal_fanju or suiyun_fanju
    laoyu_risk = ly.get('risk', '无') if ly else '无'
    # 注：laoyu(牢狱)检测在富贵局上系统性过火（如李嘉诚/克林顿/例八皆判 risk=高
    # 而实非牢狱），故仅作信息保留，不计入凶向否决/降档触发，避免误伤正当富贵。
    laoyu_hit = False

    # 过河拆桥破财（gongliang_result 未带时留 False；caiming 自算 guohe 透传）
    guohe_pocai = bool(gl.get('guohe_pocai'))

    pocai = bool(bijiao.get('detected')) or guohe_pocai
    pocai_severe = (bijiao.get('severity') == 'severe')

    reasons: List[str] = []
    if natal_fanju:
        reasons.append(f"反局（{zf.get('configuration', '')}）")
    if suiyun_fanju:
        # 岁运反局条目多（一运/岁可命中多类型），截取前 3 条示意见 suiyun_reasons
        reasons.extend(suiyun_reasons[:3])
        if len(suiyun_reasons) > 3:
            reasons.append(f'岁运反局等共{len(suiyun_reasons)}条')
    if bijiao.get('detected'):
        reasons.append(bijiao.get('reason', '比劫夺财破财'))
    if guohe_pocai:
        reasons.append('过河拆桥破财')
    if r2.get('detected'):
        reasons.append(r2.get('reason', '忌神制用神'))
    if r3.get('detected'):
        reasons.append(r3.get('reason', '用神被合绊'))
    for n in (n1, n2, n3, n4):
        if n.get('detected'):
            reasons.append(n.get('reason', '原局凶向'))

    direction = '凶' if (fanju or pocai or yongshen_xiong or mingju_xiong) else '中性'
    # G5/G1 标注层：从格所从分类（22期「首先看从了什么」）+ 十干喜忌月令票
    # （11期口诀，段氏否决其作扶抑主判据——仅小权重辅助票/注记，不改吉凶链）
    cong_target = classify_cong_target(day_gan, gans, zhis)
    gan_xiji = gan_xiji_annotate(day_gan, zhis[1] if len(zhis) > 1 else '')
    return {
        'direction': direction,
        'fanju': fanju,
        'suiyun_fanju': suiyun_fanju,
        'laoyu_risk': laoyu_risk,
        'laoyu_hit': laoyu_hit,
        'bijiao_duocai': bijiao,
        'pocai': pocai,
        'pocai_severe': pocai_severe,
        'guohe_pocai': guohe_pocai,
        'jishen_zhiyongshen': r2,
        'heban_yongshen': r3,
        'yongshen_xiong': yongshen_xiong,
        'shangguan_jianguan': n1,          # N1 伤官见官为忌
        'caisheng_sha_gongshen': n2,       # N2 财生杀攻身（severe）
        'guansha_rumu': n3,                # N3 官杀入墓为忌
        'guanfei_laoyu': n4,               # N4 官非牢狱复合（魁罡逢冲官∧枭神夺食）
        'mingju_xiong': mingju_xiong,      # 原局级凶向四式任一命中
        'mingju_xiong_severe': mingju_xiong_severe,
        'cong_target': cong_target,        # G5 从格所从分类（标注/消费两用）
        'gan_xiji': gan_xiji,              # G1 十干喜忌月令标注（辅助票）
        'reasons': reasons,
        'suiyun_reasons': suiyun_reasons,
        'suiyun_ji_reasons': suiyun_ji_reasons,  # G5 岁运吉向标注（不入凶链）
    }
