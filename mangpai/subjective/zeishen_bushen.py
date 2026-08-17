"""
zeishen_bushen - 段氏贼神捕神 / 净制 / 包制 / 冲链模块·主观层

理论来源：段建业《段氏理象学-盲派命理研究》第六章「看四柱做功的等级」
          及第五章第五节「贼神、捕神概念」
          （源文件 mangpai/docs/duan-books/duan-shi-lixiangxue-yanjiu.txt
           5535-5560 行 贼神捕神；6125-6230 行 包制/层层相制命例）

本模块是 gongliang.py 的上游依赖。gongliang 的功量累加中，「包制」「层层相制」
两项此前以保守启发式兜底（包制仅认 san_he_formed、层层相制仅认有向「克」链），
「制净程度」「气势浪费」亦缺党势-孤立目标的根本判定（见 gongliang docstring
已知局限）。本模块补齐这三块的结构化信号，供 gongliang 二次消费：

  1. detect_bao_zhi()        年时包局检测（+1 功量点）
  2. detect_chong_lian()     冲链检测（层层相制，+1 功量点）
  3. detect_zeishen_bushen() 贼神捕神/净制检测（制净程度 + 气势浪费封顶）

────────────────────────────────────────────────────────────────────────
一、包制 detect_bao_zhi（源文 6125、6170-6200、6210-6220 行）
────────────────────────────────────────────────────────────────────────
段氏：「年时包局，或者包制之局，又加一层功量」「克林顿命局是个围制结构，
即寅与戌之火局，加两丙透干，围制局中申与丑……我们将这类结构的制局称为包制」
「岳飞……时上巳与年上未形成财包印局，包局再加一层功」。

包制 = 围猎式合围：年、时（最外两柱）同载制方五行 W（捕神），合围夹制内柱
（月、日）中被克五行。判别铁律（三条件全满）：
  (a) W 同载于年、时两柱（本气或藏干）--两翼合围；
  (b) W 成势（党势强 = 捕神）：party(W) >= 4.0；
      ※ 成势已足以区分强方/弱方：李嘉诚辰亥同载水，但水弱(party 约 3.5)不成势，
        故不判包制（其功在午亥合制，非包制）。
  (c) W 克某内柱主气五行（土克水、火克金、……）--有被制目标。
三条件全满 -> 包制成立，+1 功量点。
pattern 标注：三合两翼（寅戌火/巳丑金/申辰水/亥未木）/ 透干成势 / 本气夹 / 成势。

────────────────────────────────────────────────────────────────────────
二、冲链 detect_chong_lian（源文 6155-6165 行 乾隆金字塔）
────────────────────────────────────────────────────────────────────────
段氏：「乾隆……做功是通过一级一级相制形成金字塔形的权力结构。子制午、午制酉、
酉制卯」。即层层相制：A制B、B制C、C制D 的有向制链（链长>=2），区别于单冲/单克。

制链边由「冲」「克」两类有向边构成，方向一律取五行克方->被克方：
  - 冲：六冲中五行异者（子午水火、卯酉金木、寅申金木、巳亥水火）方向=克方->被克方；
        辰戌、丑未同土无克向，以党势定向（势均则不计）。冲边与克边重合时标「冲」
        （冲为层层相制之骨，如乾隆子午冲、卯酉冲）。
  - 克：任两支五行相克，克方->被克方。
建图求最长简单路径边数。链长>=2 且路径含至少一条「冲」边 -> 冲链（层层相制），
+1 功量点；单冲（链长 1）不计。纯克链（无冲）不计（避免与 gongliang 既有
克链重复，且段氏层层相制以冲为骨）。

────────────────────────────────────────────────────────────────────────
三、贼神捕神 / 净制 detect_zeishen_bushen（源文 5535-5560 行）
────────────────────────────────────────────────────────────────────────
段氏：「当命局出现制局做功的情况下，被制的一方因相对孤立，而制方成党成势十分
强大，这种情况下我们一般称这类制局为净制。制方称捕神，被制方称贼神」「警察
特别强的时候，如果小偷特别少，或者没小偷，警察就没有用武之地」。

  捕神 = 制方（克方），成党成势；贼神 = 被制方（被克方），孤立无原神。
  - 净制（成）：捕神成势 + 贼神孤立（无原神 或 原神同制）+ 贼神实存（有本气地支）
        => 制之干净，可达高层（岳飞：子水贼神无原神金，未土捕神，净制）。
  - 不净（残存）：贼神有原神且原神残存未被制（透干原神尤甚）
        => 封顶三层（蒋介石：亥水贼神之原神庚金透干未净制，制之不净）。
  - 不成（气势浪费）：捕神太旺（party>=6）+ 贼神孤立 + 势力悬殊（捕神/贼神>=3，overkill）
        => 贼神几无可抓，做功落空，功小（gongliang._assess_penalty 显式 defer 的
           气势浪费情形，本模块补判）。贼神可有本气（实存），但党势远逊捕神、逐级
           overkill 即落空（区别于净制：净制势均，如岳飞捕4.5/贼4.2）。
  - 无制：命局无制局做功。

原神 = 生贼神之五行（水之原神金、金之原神土、……）。原神同制 = 原神五行亦为
制局目标（被冲/克）；原神残存 = 原神透干或本气而未被制。日主本身不作贼神原神
计（日主为做功之体，其生食伤=贼神乃做功机制，非残存之党）。

────────────────────────────────────────────────────────────────────────
分层位置：subjective/，import objective.constants；不反向依赖 gongliang/zuogong。
          可选消费 zuogong_result/work_actions（透传，不强依赖）以补全制局目标。
已知争议：党势强弱的数值阈值（party>=4 成势、>=6 太旺）为工程化启发式，非盲师
          口传定量表；土冲定向、原神「同制/残存」的边界各盲师口径有异。
置信度：中
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG,
    CANG_GAN_MANGPAI, LIU_CHONG, LIU_HE, AN_HE, TIAN_GAN_HE,
    PILLAR_KEYS, is_pillars,
)

# ── 三合两翼（生+墓两端，缺旺端）── 用于包制 pattern 标注
#   寅午戌火翼{寅,戌}、巳酉丑金翼{巳,丑}、申子辰水翼{申,辰}、亥卯未木翼{亥,未}
_SAN_HE_WINGS: Dict[frozenset, str] = {
    frozenset({'寅', '戌'}): '火',
    frozenset({'巳', '丑'}): '金',
    frozenset({'申', '辰'}): '水',
    frozenset({'亥', '未'}): '木',
}

# ── 党势强度权重 ──
_W_GAN_TG: float = 2.0     # 透干
_W_BEN_QI: float = 2.0     # 地支本气
_W_ZHONG_QI: float = 1.0   # 中气藏干
_W_YU_QI: float = 0.5      # 余气藏干
_W_YUAN: float = 0.5       # 原神（生我者）折半计入党势

# ── 阈值 ──
_CHENG_DANG: float = 4.25  # 捕神成势阈值（party >= 此值视为成党成势）
_TAI_WANG: float = 6.0     # 捕神太旺阈值（气势浪费判据之一）


# ── 基础工具 ──
def _pillar_of(pos: str) -> str:
    """from_pos/to_pos -> 柱位键，如 'day_zhi' -> 'day'。"""
    if not pos or '_' not in pos:
        return ''
    return pos.split('_')[0]


def _elem_of(pos: str, gans: List[str], zhis: List[str]) -> str:
    """from_pos/to_pos -> 对应天干或地支字符。"""
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    if p not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(p)
    arr = gans if t == 'gan' else zhis
    return arr[idx] if idx < len(arr) else ''


def _wx_of(elem: str) -> str:
    """天干或地支 -> 主气五行。"""
    return GAN_WX.get(elem, '') or ZHI_WX.get(elem, '')


def _yuan_wx(wx: str) -> str:
    """原神五行 = 生 wx 者（WX_SHENG 反查：WX_SHENG[原]=wx）。"""
    for w, born in WX_SHENG.items():
        if born == wx:
            return w
    return ''


def _wx_in_elem(wx: str, elem: str, is_gan: bool) -> float:
    """单个干/支元素中 wx 的党势权重（透干 2 / 本气 2 / 中气 1 / 余气 0.5）。"""
    if not elem:
        return 0.0
    if is_gan:
        return _W_GAN_TG if GAN_WX.get(elem) == wx else 0.0
    w = 0.0
    for cg, qi in CANG_GAN_MANGPAI.get(elem, []):
        if GAN_WX.get(cg) != wx:
            continue
        if qi == '本气':
            w += _W_BEN_QI
        elif qi == '中气':
            w += _W_ZHONG_QI
        else:  # 余气
            w += _W_YU_QI
    return w


def _party_strength(wx: str, gans: List[str], zhis: List[str],
                    include_yuan: bool = True) -> float:
    """五行 wx 在全局的党势强度（同党 + 原神）。

    同党 = 透干/本气/藏干中属 wx 者；原神 = 生 wx 者（折半）。
    用于判捕神成势、强方制弱方、贼神孤立。
    """
    w = 0.0
    for g in gans:
        w += _wx_in_elem(wx, g, is_gan=True)
    for z in zhis:
        w += _wx_in_elem(wx, z, is_gan=False)
    if include_yuan:
        yuan = _yuan_wx(wx)
        if yuan:
            for g in gans:
                w += _wx_in_elem(yuan, g, is_gan=True) * _W_YUAN
            for z in zhis:
                w += _wx_in_elem(yuan, z, is_gan=False) * _W_YUAN
    return w


def _benqi_wx(zhi: str) -> str:
    """地支本气五行。"""
    cg = CANG_GAN_MANGPAI.get(zhi, [])
    return GAN_WX.get(cg[0][0], '') if cg else ZHI_WX.get(zhi, '')


def _has_benqi_wx(wx: str, zhis: List[str]) -> bool:
    """局中是否存在以 wx 为本气的地支（贼神「实存」判据）。"""
    return any(_benqi_wx(z) == wx for z in zhis if z)


def _yuan_present(yuan_wx: str, gans: List[str], zhis: List[str]) -> bool:
    """原神五行是否透干或为本气（贼神「有原神」判据；仅藏干余气不算）。

    日主（gans[2]）不计：日主为做功之体，其生食伤=贼神乃做功机制，非残存原神
    （李嘉诚日主庚金生亥水贼神，庚不计残存，故判净）。
    """
    if not yuan_wx:
        return False
    for i, g in enumerate(gans):
        if i == 2 or not g:  # 跳过日主
            continue
        if GAN_WX.get(g) == yuan_wx:
            return True
    if any(_benqi_wx(z) == yuan_wx for z in zhis if z):
        return True
    return False


# ── 有向制边（冲/克，五行克定向）──
def _directed_control_edges(zhis: List[str], gans: Optional[List[str]] = None
                            ) -> List[Tuple[str, str, str]]:
    """四支间有向制边列表 [(from_zhi, to_zhi, link_type), ...]，link_type in {冲,克}。

    方向一律取五行克方->被克方：
      - 克：ZHI_WX[a] 克 ZHI_WX[b] -> (a, b, 克)
      - 冲：六冲且五行异 -> 克方->被克方；辰戌/丑未同土以党势定向（势均则跳过）
    冲边与克边重合时（如子午既是冲又是水克火）取「冲」标--冲为层层相制之骨
    （乾隆子午冲、卯酉冲），取冲方知链含冲。不依赖 zuogong 的 auxiliary 标记
    （zuogong 常把被冲覆盖的克标为 aux 致链断裂，见 gongliang._chain_length 对
    乾隆仅得 chain=1 的局限），直接由五行重算。
    """
    edge_type: Dict[Tuple[str, str], str] = {}
    nz = [z for z in zhis if z]

    def _add(a: str, b: str, t: str) -> None:
        # 冲 优先于 克（同边重合时标冲）
        cur = edge_type.get((a, b))
        if cur is None or (cur == '克' and t == '冲'):
            edge_type[(a, b)] = t

    # 克边（任两支五行相克）
    for a in nz:
        wa = ZHI_WX.get(a, '')
        if not wa:
            continue
        for b in nz:
            if a == b:
                continue
            wb = ZHI_WX.get(b, '')
            if wb and WX_KE.get(wa) == wb:
                _add(a, b, '克')

    # 冲边（覆盖方向：五行异者取克向；同土者党势定向）
    chong_map: Dict[str, str] = {}
    for a, b in LIU_CHONG:
        chong_map[a] = b
        chong_map[b] = a
    for a in nz:
        b = chong_map.get(a, '')
        if not b or b not in nz:
            continue
        wa, wb = ZHI_WX.get(a, ''), ZHI_WX.get(b, '')
        if wa and wb and wa != wb:
            # 五行异：克方->被克方
            if WX_KE.get(wa) == wb:
                src, dst = a, b
            elif WX_KE.get(wb) == wa:
                src, dst = b, a
            else:
                continue
            _add(src, dst, '冲')
        elif gans and wa and wb and wa == wb:
            # 同土冲（辰戌/丑未）：以本气同党+原神党势定向，势均跳过
            sa = _single_zhi_party(wa, a, zhis, gans)
            sb = _single_zhi_party(wa, b, zhis, gans)
            if sa > sb:
                src, dst = a, b
            elif sb > sa:
                src, dst = b, a
            else:
                continue
            _add(src, dst, '冲')
    return [(a, b, t) for (a, b), t in edge_type.items()]


def _single_zhi_party(wx: str, zhi: str, zhis: List[str],
                      gans: Optional[List[str]] = None) -> float:
    """某地支作为 wx 党员的局部党势（自身权重 + 全局原神加成），用于同土冲定向。"""
    w = _wx_in_elem(wx, zhi, is_gan=False)
    yuan = _yuan_wx(wx)
    if yuan:
        if gans:
            for g in gans:
                w += _wx_in_elem(yuan, g, is_gan=True) * _W_YUAN
        for z in zhis:
            w += _wx_in_elem(yuan, z, is_gan=False) * _W_YUAN
    return w


def _longest_path(edges: List[Tuple[str, str, str]]) -> Tuple[List[str], List[Tuple[str, str, str]]]:
    """有向图最长简单路径（节点=地支字符）。

    Returns: (路径节点序列, 路径边序列) ；空图返回 ([], [])。
    图至多 4 节点，DFS 即可。
    """
    adj: Dict[str, List[Tuple[str, str]]] = {}
    nodes: Set[str] = set()
    for a, b, t in edges:
        adj.setdefault(a, []).append((b, t))
        nodes.add(a)
        nodes.add(b)

    best_nodes: List[str] = []
    best_edges: List[Tuple[str, str, str]] = []

    def _dfs(node: str, path_nodes: List[str], path_edges: List[Tuple[str, str, str]]):
        nonlocal best_nodes, best_edges
        if len(path_edges) > len(best_edges):
            best_nodes = list(path_nodes)
            best_edges = list(path_edges)
        for nxt, t in adj.get(node, []):
            if nxt in path_nodes:
                continue
            path_nodes.append(nxt)
            path_edges.append((node, nxt, t))
            _dfs(nxt, path_nodes, path_edges)
            path_nodes.pop()
            path_edges.pop()

    for start in sorted(nodes):  # sorted：最长路径平局取先见者，起点须定序
        _dfs(start, [start], [])
    return best_nodes, best_edges


# ── 合制候选（合=捕获，合方制被合方）──
def _he_candidates(gans: List[str], zhis: List[str],
                   day_zhi: str, day_gan: str
                   ) -> List[Tuple[str, str, float, bool]]:
    """合制候选 [(捕神五行, 贼神五行, 捕神party, is_day_doer), ...]。

    合源：地支六合、暗合、天干合。合方(doer) 定向：
      - 日柱侧为 doer（段氏主位做功：日柱为做功之体，合宾位为正局）；
      - 否则党势强者为 doer；势均跳过。
    合方与被合方五行同者（如午未同火/土混）不计（无制向）。
    李嘉诚午亥暗合：日支午为 doer->捕火/贼水（其功在合制，非辰未土克水）。
    """
    cands: List[Tuple[str, str, float, bool]] = []
    zhi_set = {z for z in zhis if z}
    gan_set = {g for g in gans if g}

    def _add_pair(a: str, b: str, is_gan: bool) -> None:
        wa, wb = _wx_of(a), _wx_of(b)
        if not wa or not wb or wa == wb:
            return
        day_marker = day_gan if is_gan else day_zhi
        if a == day_marker:
            doer, target = a, b
        elif b == day_marker:
            doer, target = b, a
        else:
            pa = _party_strength(wa, gans, zhis)
            pb = _party_strength(wb, gans, zhis)
            if pa > pb:
                doer, target = a, b
            elif pb > pa:
                doer, target = b, a
            else:
                return
        dw = _wx_of(doer)
        tw = _wx_of(target)
        # 仅取克合（合中带制：两五行相克）；生合（相生）为和谐合，非合制
        # （李嘉诚午未火土生合不计，午亥水火克合才为合制->贼水）
        if not (WX_KE.get(dw) == tw or WX_KE.get(tw) == dw):
            return
        cands.append((dw, tw, _party_strength(dw, gans, zhis),
                      doer == day_marker))

    # 地支六合
    for a, b in LIU_HE:
        if a in zhi_set and b in zhi_set:
            _add_pair(a, b, is_gan=False)
    # 暗合（AN_HE 双向 dict，去重）
    seen: Set[Tuple[str, str]] = set()
    for a, b in AN_HE.items():
        key = tuple(sorted((a, b)))
        if key in seen:
            continue
        seen.add(key)
        if a in zhi_set and b in zhi_set:
            _add_pair(a, b, is_gan=False)
    # 天干合
    seen_tg: Set[Tuple[str, str]] = set()
    for a, b in TIAN_GAN_HE.items():
        key = tuple(sorted((a, b)))
        if key in seen_tg:
            continue
        seen_tg.add(key)
        if a in gan_set and b in gan_set:
            _add_pair(a, b, is_gan=True)
    return cands


# ──────────────────────────────────────────────────────────────────────
# 1. 包制检测
# ──────────────────────────────────────────────────────────────────────
def detect_bao_zhi(gans: List[str], zhis: List[str], day_gan: str = ''
                   ) -> Optional[Dict]:
    """年时包局检测（段氏包制，+1 功量点）。

    判定：年、时两柱同载制方五行 W（捕神），W 成势，W 克某内柱主气。
    详见模块 docstring「一、包制」。

    Args:
        gans: 四柱天干 [year, month, day, hour]。
        zhis: 四柱地支 [year, month, day, hour]。
        day_gan: 日干（保留接口，包制判定不依赖十神，纯五行党势）。

    Returns:
        命中时：
          {'detected': True, 'pattern': str, 'wrap_wx': str, 'target_wx': str,
           'wrap_pillars': ['year','hour'], 'target_pillar': str,
           'party': float, 'target_party': float, 'points': 1, 'reason': str}
        未命中返回 None。
    """
    if not zhis or len(zhis) < 4:
        return None
    year_zhi, month_zhi, day_zhi, hour_zhi = zhis[0], zhis[1], zhis[2], zhis[3]
    if not year_zhi or not hour_zhi:
        return None
    inner_zhis = [(PILLAR_KEYS[1], month_zhi), (PILLAR_KEYS[2], day_zhi)]
    gans = gans or []

    # 年、时各自所载五行集合（本气+藏干）
    def _wx_set(zhi: str) -> Set[str]:
        s: Set[str] = set()
        wx = ZHI_WX.get(zhi, '')
        if wx:
            s.add(wx)
        for cg, _qi in CANG_GAN_MANGPAI.get(zhi, []):
            cw = GAN_WX.get(cg, '')
            if cw:
                s.add(cw)
        return s

    year_set = _wx_set(year_zhi)
    hour_set = _wx_set(hour_zhi)
    shared = year_set & hour_set
    if not shared:
        return None

    wing_wx = _SAN_HE_WINGS.get(frozenset({year_zhi, hour_zhi}))

    for w in sorted(shared):  # sorted：多候选包制制局取定序首中者（M1 复跑确定性，
        # 土<火<水 按码点序；li003-七次婚姻/qi02-工商局长贪官/qi20-李连英 多候选例）
        # (c) W 克某内柱主气五行
        target_pillar = ''
        target_wx = ''
        for pk, iz in inner_zhis:
            iw = _benqi_wx(iz)
            if iw and WX_KE.get(w) == iw:
                target_pillar = pk
                target_wx = iw
                break
        if not target_pillar:
            continue

        party_w = _party_strength(w, gans, zhis)
        party_t = _party_strength(target_wx, gans, zhis)
        # (b) W 成势（捕神党势>=阈值）。李嘉诚辰亥同载水但水弱(party 约 3.5<4)，
        # 不成势故排除（其功在午亥合制，非包制）；成势已足以区分强方/弱方。
        if party_w < _CHENG_DANG:
            continue

        # pattern 标注
        if wing_wx == w:
            pattern = '三合两翼'
        elif any(GAN_WX.get(g) == w for g in gans if g):
            pattern = '透干成势'
        elif _benqi_wx(year_zhi) == w and _benqi_wx(hour_zhi) == w:
            pattern = '本气夹'
        else:
            pattern = '成势'

        reason = (
            f'包制：年({year_zhi})、时({hour_zhi})同载「{w}」成势'
            f'（party={party_w:.1f}，被克「{target_wx}」{party_t:.1f}），'
            f'围制{target_pillar}柱（{target_wx}），{pattern}（+1层）'
        )
        return {
            'detected': True,
            'pattern': pattern,
            'wrap_wx': w,
            'target_wx': target_wx,
            'wrap_pillars': ['year', 'hour'],
            'target_pillar': target_pillar,
            'party': round(party_w, 2),
            'target_party': round(party_t, 2),
            'points': 1,
            'reason': reason,
        }
    return None


# ──────────────────────────────────────────────────────────────────────
# 2. 冲链检测
# ──────────────────────────────────────────────────────────────────────
def detect_chong_lian(zhis: List[str], gans: Optional[List[str]] = None
                      ) -> Optional[Dict]:
    """冲链检测（层层相制，+1 功量点）。

    判定：四支有向制边（冲/克，五行克定向）构成最长简单路径链长>=2，且路径含
    至少一条「冲」边。详见模块 docstring「二、冲链」。

    Args:
        zhis: 四柱地支 [year, month, day, hour]。
        gans: 四柱天干（同土冲辰戌/丑未定向用，可选）。

    Returns:
        命中时：
          {'detected': True, 'length': int, 'chain': [pos, ...],
           'nodes': [zhi, ...], 'links': [(type, from_zhi, to_zhi), ...],
           'has_chong': True, 'points': 1, 'reason': str}
        未命中（无链 / 链长<2 / 纯克链无冲）返回 None。
    """
    if not zhis or len(zhis) < 4:
        return None
    zhi_to_pos: Dict[str, List[str]] = {}
    for pk, z in zip(PILLAR_KEYS, zhis):
        if z:
            zhi_to_pos.setdefault(z, []).append(pk)

    edges = _directed_control_edges(zhis, gans)
    if not edges:
        return None
    path_nodes, path_edges = _longest_path(edges)
    if len(path_edges) < 2:
        return None
    has_chong = any(t == '冲' for _, _, t in path_edges)
    if not has_chong:
        # 纯克链不计（段氏层层相制以冲为骨，且避免与 gongliang 克链重复）
        return None

    chain_pos = [zhi_to_pos.get(z, [z])[0] for z in path_nodes]
    links = [(t, a, b) for a, b, t in path_edges]
    reason = (
        f'层层相制（冲链）：{"->".join(path_nodes)}，链长{len(path_edges)}'
        f'（含冲），逐级相制（+1层）'
    )
    return {
        'detected': True,
        'length': len(path_edges),
        'chain': chain_pos,
        'nodes': path_nodes,
        'links': links,
        'has_chong': True,
        'points': 1,
        'reason': reason,
    }


# ──────────────────────────────────────────────────────────────────────
# 3. 贼神捕神 / 净制检测
# ──────────────────────────────────────────────────────────────────────
def detect_zeishen_bushen(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    *,
    work_actions: Optional[List[Dict]] = None,
    bao_zhi: Optional[Dict] = None,
    chong_lian: Optional[Dict] = None,
) -> Dict:
    """贼神捕神 / 净制检测（制净程度 + 气势浪费判据）。

    判定流程：
      1. 选定制局（捕神=制方五行，贼神=被制方五行）：
         - bao_zhi 命中 -> 用包制 W/target（包制为明确制局，优先）；
         - 否则在有向制边中取捕神党势最强者。
      2. 净/不净/不成/无制 四态判定（见模块 docstring「三、贼神捕神」）。

    Args:
        day_gan: 日干（保留接口，净制判定纯五行党势）。
        gans/zhis: 四柱天干/地支。
        work_actions: 可选，zuogong work_actions（补全制局目标，不强依赖）。
        bao_zhi: detect_bao_zhi 输出（透传制局）。
        chong_lian: detect_chong_lian 输出（透传制局）。

    Returns:
        {'jing_zhi': 净|不净|不成|无制,
         'bushen_wx': str, 'zeishen_wx': str,
         'bushen_strength': float, 'zeishen_strength': float,
         'zeishen_isolated': bool, 'zeishen_has_yuanshen': bool,
         'yuanshen_yi_zhi': bool, 'cheng_dang': bool, 'momentum_waste': bool,
         'reason': str, 'confidence': 中}
    """
    gans = gans or []
    zhis = zhis or []
    day_zhi = zhis[2] if len(zhis) > 2 else ''

    # 合制候选（复用于目标集与制局选择）
    he_cands = _he_candidates(gans, zhis, day_zhi, day_gan)

    # 制局目标五行集合（被冲/克/合方五行，含 work_actions 透传）
    target_wx_set: Set[str] = set()
    for a, b, _t in _directed_control_edges(zhis, gans):
        target_wx_set.add(ZHI_WX.get(b, ''))
    for _bw, zw, _p, _d in he_cands:
        if zw:
            target_wx_set.add(zw)
    if work_actions:
        for wa in work_actions:
            if wa.get('type') not in ('冲', '克', '穿', '刑', '破'):
                continue
            # 滤 auxiliary：宾位/非日主参与之制非真做功（书 6122-6126 蒋介石
            # 丁克庚宾位干克不得塞入制局目标集，否则原神同制误净，「制之不净达不到四层功」）
            if wa.get('auxiliary'):
                continue
            to = wa.get('to_pos', '')
            elem = _elem_of(to, gans, zhis)
            tw = _wx_of(elem)
            if tw:
                target_wx_set.add(tw)
    # 包制：内柱（月、日）皆被围制，其本气五行亦为制局目标
    # （克林顿申金贼神之原神土=丑日本气，丑在内柱被围=>原神同制=>净）
    if bao_zhi and bao_zhi.get('detected'):
        for iz in (zhis[1] if len(zhis) > 1 else '', day_zhi):
            iw = _benqi_wx(iz)
            if iw:
                target_wx_set.add(iw)

    # ── 选定主制局：捕神/贼神 ──
    # 候选 (捕神五行, 贼神五行, 捕神party, is_day_doer)
    candidates: List[Tuple[str, str, float, bool]] = []
    if bao_zhi and bao_zhi.get('detected'):
        bw = bao_zhi.get('wrap_wx', '')
        tw = bao_zhi.get('target_wx', '')
        if bw and tw:
            candidates.append((bw, tw, _party_strength(bw, gans, zhis), False))
    # 有向制边候选（克方=doer；doer 在日支则 is_day_doer）
    for a, b, _t in _directed_control_edges(zhis, gans):
        wa_w, wb_w = ZHI_WX.get(a, ''), ZHI_WX.get(b, '')
        if wa_w and wb_w:
            candidates.append((wa_w, wb_w, _party_strength(wa_w, gans, zhis),
                               a == day_zhi))
    # 合制候选
    candidates.extend(he_cands)

    if not candidates:
        return _build_zb('无制', '', '', 0.0, 0.0, False, False, False,
                         False, False, '命局无制局做功，不论净制')

    # bao 命中时以其为制局（包制为明确制局，优先）；
    # 否则优先日柱做功（段氏主位做功：日柱为做功之体，制宾位为正局），
    #   取其中捕神党势最强者；无日柱做功则取全局捕神党势最强者。
    if bao_zhi and bao_zhi.get('detected') and bao_zhi.get('wrap_wx'):
        bushen_wx = bao_zhi['wrap_wx']
        zeishen_wx = bao_zhi['target_wx']
    else:
        day_doers = [c for c in candidates if c[3]]
        pool = day_doers if day_doers else candidates
        bushen_wx, zeishen_wx, _, _ = max(pool, key=lambda c: c[2])

    bushen_str = _party_strength(bushen_wx, gans, zhis)
    zeishen_str = _party_strength(zeishen_wx, gans, zhis)
    cheng_dang = bushen_str >= _CHENG_DANG

    yuan_wx = _yuan_wx(zeishen_wx)
    zeishen_has_yuan = _yuan_present(yuan_wx, gans, zhis)
    # 原神同制 = 原神五行亦是制局目标（被冲/克）
    yuan_yi_zhi = bool(yuan_wx and yuan_wx in target_wx_set)
    zeishen_isolated = (not zeishen_has_yuan) or yuan_yi_zhi
    zeishen_real = _has_benqi_wx(zeishen_wx, zhis)

    # 不成（气势浪费）：捕神太旺 + 贼神孤立 + 势力悬殊（捕神/贼神>=3，overkill）
    # 段氏「警察特别强、小偷特别少，没小偷可抓，无用武之地」。贼神实存但党势远逊
    # 捕神，逐级 overkill，做功落空。岳飞捕神4.5/贼神4.25 势均->净制（非不成）。
    momentum_waste = (
        cheng_dang
        and zeishen_isolated
        and bushen_str >= _TAI_WANG
        and zeishen_str > 0
        and (bushen_str / zeishen_str) >= 3.0
    )

    if not cheng_dang:
        reason = (
            f'捕神「{bushen_wx}」党势 {bushen_str:.1f} 未成势（<{_CHENG_DANG}），'
            f'制局无力，未成净制'
        )
        return _build_zb('不净', bushen_wx, zeishen_wx, bushen_str, zeishen_str,
                         zeishen_isolated, zeishen_has_yuan, yuan_yi_zhi,
                         cheng_dang, momentum_waste, reason)

    if momentum_waste:
        reason = (
            f'不成（气势浪费）：捕神「{bushen_wx}」太旺（{bushen_str:.1f}），'
            f'贼神「{zeishen_wx}」孤立且党势远逊（{zeishen_str:.1f}，'
            f'捕/贼={bushen_str / zeishen_str:.1f}>=3），几无可抓，做功落空'
        )
        return _build_zb('不成', bushen_wx, zeishen_wx, bushen_str, zeishen_str,
                         zeishen_isolated, zeishen_has_yuan, yuan_yi_zhi,
                         cheng_dang, momentum_waste, reason)

    if zeishen_isolated and zeishen_real:
        why = '无原神' if not zeishen_has_yuan else '原神同制'
        reason = (
            f'净制：捕神「{bushen_wx}」成势（{bushen_str:.1f}），'
            f'贼神「{zeishen_wx}」孤立（{why}）且实存，制之干净'
        )
        return _build_zb('净', bushen_wx, zeishen_wx, bushen_str, zeishen_str,
                         zeishen_isolated, zeishen_has_yuan, yuan_yi_zhi,
                         cheng_dang, momentum_waste, reason)

    # 贼神有原神残存 -> 不净
    reason = (
        f'制不净：贼神「{zeishen_wx}」之原神「{yuan_wx}」'
        f'{"残存未被制" if not yuan_yi_zhi else "虽制未净"}，封顶三层'
    )
    return _build_zb('不净', bushen_wx, zeishen_wx, bushen_str, zeishen_str,
                     zeishen_isolated, zeishen_has_yuan, yuan_yi_zhi,
                     cheng_dang, momentum_waste, reason)


def _build_zb(jing_zhi: str, bushen_wx: str, zeishen_wx: str,
              bushen_str: float, zeishen_str: float,
              isolated: bool, has_yuan: bool, yuan_yi_zhi: bool,
              cheng_dang: bool, momentum_waste: bool, reason: str) -> Dict:
    return {
        'jing_zhi': jing_zhi,
        'bushen_wx': bushen_wx,
        'zeishen_wx': zeishen_wx,
        'bushen_strength': round(bushen_str, 2),
        'zeishen_strength': round(zeishen_str, 2),
        'zeishen_isolated': isolated,
        'zeishen_has_yuanshen': has_yuan,
        'yuanshen_yi_zhi': yuan_yi_zhi,
        'cheng_dang': cheng_dang,
        'momentum_waste': momentum_waste,
        'reason': reason,
        'confidence': '中',
    }


# ──────────────────────────────────────────────────────────────────────
# 聚合入口
# ──────────────────────────────────────────────────────────────────────
def analyze_zeishen_bushen(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    zuogong_result: Optional[Dict] = None,
    *,
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """贼神捕神/包制/冲链 聚合分析（gongliang 上游信号源）。

    一次性输出三路结构化信号，供 gongliang 消费：
      - bao_zhi:        包制 -> +1 功量点（替代 gongliang 仅认 san_he_formed 的保守判）
      - chong_lian:     冲链 -> +1 功量点（替代 gongliang _chain_length 仅认克链）
      - zeishen_bushen: 净制/不成 -> 制净程度 + 气势浪费封顶（补 gongliang defer 项）

    两种调用方式（与 analyze_gongliang 对齐）：
      1. analyze_zeishen_bushen(day_gan=庚, gans=[...], zhis=[...])
      2. analyze_zeishen_bushen(pillars)  # Pillars 对象
    zuogong_result/work_actions 可选透传，补全制局目标判定。

    Returns:
        {'bao_zhi': dict|None, 'chong_lian': dict|None, 'zeishen_bushen': dict,
         'party_strength': {wx: score}, 'points': float, 'reasons': [str],
         'confidence': 中}
        points = bao_zhi.points + chong_lian.points（净制/不成不加点，调节封顶）。
    """
    # Pillars 对象签名支持
    if is_pillars(day_gan):
        p = day_gan
        if not gans or not zhis:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []
    zg: Dict = zuogong_result or {}
    wa: Optional[List[Dict]] = (work_actions if work_actions is not None
                                else (zg.get('work_actions') or []))

    bao = detect_bao_zhi(gans, zhis, day_gan)
    clian = detect_chong_lian(zhis, gans)
    zb = detect_zeishen_bushen(
        day_gan, gans, zhis, work_actions=wa, bao_zhi=bao, chong_lian=clian,
    )

    points: float = 0.0
    reasons: List[str] = []
    if bao:
        points += bao['points']
        reasons.append(bao['reason'])
    if clian:
        points += clian['points']
        reasons.append(clian['reason'])
    if zb.get('jing_zhi') != '无制':
        reasons.append(zb['reason'])

    # 党势全表（调试/消费参考）
    party_all: Dict[str, float] = {}
    for wx in ('木', '火', '土', '金', '水'):
        party_all[wx] = round(_party_strength(wx, gans, zhis), 2)

    return {
        'bao_zhi': bao,
        'chong_lian': clian,
        'zeishen_bushen': zb,
        'party_strength': party_all,
        'points': round(points, 2),
        'reasons': reasons,
        'confidence': '中',
    }


__all__ = [
    'detect_bao_zhi',
    'detect_chong_lian',
    'detect_zeishen_bushen',
    'analyze_zeishen_bushen',
]
