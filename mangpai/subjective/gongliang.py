"""
gongliang - 段氏做功等级量化（四层功量）·主观层

理论来源：段建业《段氏理象学-盲派命理研究》第六章「看四柱做功的等级」
          （源文件 mangpai/docs/duan-books/duan-shi-lixiangxue-yanjiu.txt
           6077-6376 行）

核心思想（段氏四层功，与 zuogong_confirm.assess_work_level 并行的另一套体系）：
  段氏以「功量」(做功等级) 量化命局富贵层次，最多四层功：
    一层功：小富小贵（富=百万级，贵=科级到处级）
    二层功：中富中贵（富=千万到亿级，贵=处级到厅级）
    三层功：大富大贵（富=亿到数十亿级，贵=厅级到省部级）
    四层功：极富极贵（富=百亿到千亿级，贵=总理或元首级）
  普通百姓能达到一层功量就很不错了，有的命只有半层功或根本无功。

功量计算（累加「功量点」，源于源文 6108-6127、6133-6280 行命例）：
  1. 原神用神同制 -> +2 点（核心铁律）
     制局中被制之「用神」与其「原神」(生用神者) 同制，方为两层功。
       财 + 财的原神(食伤) 同制 -> 千万级富翁
       官 + 官的原神(财)   同制 -> 厅级以上官员
     （印+印原神(官杀)、食伤+食伤原神(比劫) 同制同理，唯源文未单列富贵量级。）
     多候选位时偏好「财/官杀」为用神（段氏富贵用神），其次偏好含官杀之位
     （利七杀当财叠加），如例八寅(食伤+比劫)与申(财+食伤)同现取申方达三层。
  2. 制墓库 -> +2 点（成势制墓库地支为功量也是两层；保守须 san_he_formed）
  3. 七杀当财 -> +1 点（七杀当财富比财当财富量级高一层；官杀透干且与制局目标同根）
  4. 入墓为功 -> +1 点（局中有入墓(墓用)做功者，算一层功量）
  5. 库源/连墓 -> +1 点（被制元素之墓库在局，源头得库加一层；须原神用神同制成立）
  6. 包局/包制 -> +1 点（三合成势围制，段氏包制为围猎式合围，须成势方可）
  7. 层层相制 -> +1 点（克链长≥2，乾隆式金字塔逐级相制；保守仅认有向「克」链）
  7b. 带象 -> +1 点（高级篇1.4 补齐：干生支之柱承财/官/印象且参与做功；原神用神
      同制不成立时方计，避免与核心 +2 双计）
  7c. 官统财/财统官 -> +1 点（高级篇1.4 补齐：官杀与财互统摄；原神用神同制不成立
      时方计，消费 caiming.classify_caifu_view）
  8. 制净程度 -> 调节封顶（不加点）
     制之干净(用神与其原神俱制、无残存同党) -> 可达高层；
     制之不净(原神残存透干/同党废神/日柱被穿/折扣动作) -> 封顶于三层
     （蒋介石伤官制之不净，达不到四层）。
  层次映射：点数≥4->四层，≥3->三层，≥2->二层，否则一层；再依制净/普通降档封顶。

普通四柱（小功，源文 6282-6376 行）：
  - 形不成气势但主位有功 -> 功不大
  - 有气势但气势浪费(做功少) -> 功小（须贼神捕神/净制判党势，本模块暂不判，见局限）
  - 只有相克之制(无冲/合/穿/包制) -> 封顶二层（相克之制，功量较小但仍可达两层）
  - 仅以相生做功(无制用) -> 封顶一层（相生之功，效率低=普通，源文普通例二）

已知局限（待 P0 引擎更新：贼神捕神/净制/象法回退/领域应期）：
  本模块消费 zuogong 的 work_actions 做二次量化，但 zuogong 对以下结构的检出不足，
  导致部分源文命例功量偏低（已记入 reasons，不致误升）：
    - 入墓为功（tomb_works）：蒋介石(巳午入戌)、岳飞(未为羊刃墓)、李嘉诚(未入辰)；
    - 包制（须三合成势）：克林顿(寅戌火局包制申丑，非标准三合)；
    - 层层相制（冲链）：乾隆(子午卯酉金字塔，冲为互向、势方向须党势判定)。
  真实制局与相生/偶然共现的区分、强方制弱方的势方向判定，须依赖贼神捕神
  (党势-孤立目标)模块，本模块不臆断，以保守启发式（强制参与位+单点位原神用神同制）
  兜底。源文第6章 14 例回归：10 例层数与源文一致，余 4 例（乾隆/克林顿/蒋介石/岳飞）
  均因上述 zuogong 检出不足而偏低一层，属已知局限。

与 zuogong_confirm.assess_work_level 的区别（两套体系并行，互不覆盖）：
  assess_work_level：基于「做功类型数 + 主被动 + 结构」打 0-5 层（做功成立/效率视角）。
  本模块 gongliang   ：基于「原神用神同制 + 制净程度 + 功量累加」打 1-4 层
                       （段氏富贵量级视角），消费 zuogong 的 work 数据做二次量化。

分层位置：subjective/，import subjective.zuogong_confirm 获取做功数据
          （zuogong_result 为 analyze_zuogong 输出；缺省时本函数可自调 analyze_zuogong）。
依赖方向单向：subjective -> objective（constants）；本模块不反向依赖。
已知争议：原神用神同制/制净程度的判定需十神+藏干推断，各盲师口径有异；
          包制/层层相制/七杀当财为结构启发式，非盲师口传定量表。
置信度：中
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_KE_ME, WX_SHENG,
    CANG_GAN_MANGPAI, TOMB_MAP, PILLAR_KEYS,
    is_pillars,
)
from mangpai.subjective.zuogong_confirm import analyze_zuogong
from mangpai.subjective.caiming import classify_caifu_view
from mangpai.subjective.yongshen import detect_bijiao_duocai

# ── 四层功 tier 名（段氏富贵量级）──
_TIER_NAMES: Dict[int, str] = {
    1: '小富小贵',
    2: '中富中贵',
    3: '大富大贵',
    4: '极富极贵',
}

# ── 制用动作 type 集合（冲克穿刑破，纯制家族）──
_ZHI_TYPES: Set[str] = {'冲', '克', '穿', '刑', '破'}
# ── 合制动作 type 集合（合以制之，段氏视合制为制，如丁亥自合制亥）──
_HE_ZHI_TYPES: Set[str] = {'天干合', '地支合', '暗合', '半合'}
# ── 计入「被制方」的动作 type（制用 + 合制 + 墓用）──
_CONTROL_TYPES: Set[str] = _ZHI_TYPES | _HE_ZHI_TYPES | {'墓用'}

# ── 原神-用神 十神配对（原神 = 生用神者）──
#   财的原神=食伤(食伤生财)；官的原神=财(财生官)；
#   印的原神=官杀(官杀生印)；食伤的原神=比劫(比劫生食伤)
_YUANSHEN_PAIRS: List[Tuple[str, str]] = [
    ('财', '食伤'),     # 用神=财, 原神=食伤
    ('官杀', '财'),     # 用神=官杀, 原神=财
    ('印', '官杀'),     # 用神=印, 原神=官杀
    ('食伤', '比劫'),   # 用神=食伤, 原神=比劫
]

# ── level -> 分数区间（score 在层内连续刻画强弱）──
_SCORE_BAND: Dict[int, Tuple[int, int]] = {
    1: (0, 39),
    2: (40, 67),
    3: (68, 89),
    4: (90, 100),
}
_SCORE_BASE: Dict[int, int] = {1: 12, 2: 50, 3: 74, 4: 92}

# ── 高级篇1.4 补齐：带象所承之象限为 财/官杀/印（源文「其承载的象（财、官、印）」）──
_DAIXIANG_XIANG: Set[str] = {'财', '官杀', '印'}

# ── 高级篇1.4 补齐：富贵贫贱四档定性（与上文四层功 tier 表同口径，按 level 落档）──
#   源文将富贵贫贱分四档（非三档），富/贵各按层功量化；此处把第六章 tier 表
#   物化为结果字段，供领域层（财命/官命）直接消费。
_WEALTH_GRADE: Dict[int, str] = {
    1: '百万级', 2: '千万-亿级', 3: '亿-数十亿级', 4: '百亿-千亿级',
}
_RANK_GRADE: Dict[int, str] = {
    1: '科级-处级', 2: '处级-厅级', 3: '厅级-省部级', 4: '总理-元首级',
}
_FUGUI_PINJIAN: Dict[int, str] = {
    1: '第一档·小富小贵（普通偏上）',
    2: '第二档·中富中贵',
    3: '第三档·大富大贵',
    4: '第四档·极富极贵',
}


# ── 基础工具 ──
def _pillar_of(pos: str) -> str:
    """from_pos/to_pos -> 柱位键，如 'day_gan' -> 'day'。"""
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
    return gans[idx] if t == 'gan' else zhis[idx]


def _wx_of(elem: str) -> str:
    """天干或地支 -> 五行。"""
    return GAN_WX.get(elem, '') or ZHI_WX.get(elem, '')


def _shishen_cat(day_wx: str, wx: str) -> str:
    """五行 -> 相对日主的十神大类（比劫/印/食伤/财/官杀）。

    与 zuogong_confirm._tiyong_of 同口径（纯五行生克，不用十神表）：
      体 = 比劫(同我) + 印(生我) + 食伤(我生)；
      用 = 财(我克) + 官杀(克我)。
    """
    if not day_wx or not wx:
        return ''
    if wx == day_wx:
        return '比劫'
    if WX_SHENG.get(wx) == day_wx:
        return '印'        # 生我
    if WX_SHENG.get(day_wx) == wx:
        return '食伤'      # 我生
    if WX_KE.get(day_wx) == wx:
        return '财'        # 我克
    if WX_KE.get(wx) == day_wx:
        return '官杀'      # 克我
    return ''


def _elem_cats(day_wx: str, elem: str, include_canggan: bool = True) -> Set[str]:
    """单个干支元素 -> 十神大类集合（地支含藏干）。

    藏干是「原神用神同制」判定的关键：如亥含甲(官)又主气水(财)，
    制亥即同时制官与官之原神财（蒋介石例）。故地支须展开藏干。
    """
    cats: Set[str] = set()
    wx = _wx_of(elem)
    c = _shishen_cat(day_wx, wx)
    if c:
        cats.add(c)
    if include_canggan and elem in CANG_GAN_MANGPAI:
        for cg, _qi in CANG_GAN_MANGPAI[elem]:
            cw = GAN_WX.get(cg, '')
            cc = _shishen_cat(day_wx, cw)
            if cc:
                cats.add(cc)
    return cats


def _is_tomb(zhi: str) -> bool:
    """是否墓库地支（辰戌丑未）。"""
    return zhi in TOMB_MAP


def _tomb_wx(zhi: str) -> List[str]:
    """墓库地支所墓五行（辰同时为水墓与土墓）。"""
    return TOMB_MAP.get(zhi, [])


# ── 核心分析 ──
def analyze_gongliang(
    zuogong_result: Optional[Dict] = None,
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    work_actions: Optional[List[Dict]] = None,
    work_types: Optional[List[str]] = None,
    fei_shen: Optional[List[str]] = None,
    gong_shen: Optional[List[str]] = None,
    zeishen_bushen_result: Optional[Dict] = None,
) -> Dict:
    """段氏四层功量评估。

    消费 zuogong 的做功数据，按段氏「原神用神同制 + 制净程度 + 功量累加」
    铁律量化命局富贵层次（1-4 层功），与 assess_work_level 并行，不覆盖。

    两种调用方式：
      1. 传 zuogong_result（analyze_zuogong 输出）+ day_gan/gans/zhis（十神推断所需）：
         analyze_gongliang(zg, day_gan='庚', gans=[...], zhis=[...])
      2. 直接传四柱（无 zuogong_result 时本函数自调 analyze_zuogong 取做功数据）：
         analyze_gongliang(day_gan='庚', gans=[...], zhis=[...])
      3. 亦可直接传 work_actions/work_types/fei_shen/gong_shen 显式覆盖。

    Args:
        zuogong_result: analyze_zuogong 输出（含 work_actions/work_types/gong_shen/
            fei_shen/tomb_works/san_he_formed/has_severe_harm 等）。缺省则自调。
        day_gan: 日干（十神推断必需）。缺省时由 gans[day] 推导。
        gans: 四柱天干 [year, month, day, hour]。
        zhis: 四柱地支 [year, month, day, hour]。
        work_actions/work_types/fei_shen/gong_shen: 显式覆盖 zuogong_result 对应字段。

    Returns:
        {
          'level': 1-4,                  # 段氏四层功
          'tier_name': '小富小贵'|...,    # 富贵量级名
          'score': 0-100,                # 层内连续强弱
          'gong_points': float,          # 原始功量点（累加，未封顶）
          'reasons': [str, ...],         # 各功量点的判定理由（透传源文规则）
          'zhi_jing': '净'|'不净'|'无制', # 制净程度
          'yuanshen_yongshen': str|None, # 命中的原神用神同制配对（如 '财+食伤'）
          'controls': [str, ...],        # 被制方十神大类
          'gong_shen_cats': [str, ...],  # 功神十神大类
          'chain_length': int,           # 层层相制最长链长
          'penalty': str|None,           # 普通四柱降档原因
          'wealth_grade': str,           # 富量级（高级篇1.4 富贵贫贱四档）
          'rank_grade': str,             # 贵量级（高级篇1.4 富贵贫贱四档）
          'fugui_pinjian': str,          # 富贵贫贱档名（四档定性，按 level 落档）
          'confidence': '中',
        }
    """
    # ── Pillars 对象签名支持（与全库统一）──
    if is_pillars(zuogong_result):
        p = zuogong_result
        if not gans or not zhis:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        if not day_gan:
            day_gan = p.day_gan
        zuogong_result = None

    # ── 缺 zuogong_result 时自调 analyze_zuogong（消费四柱）──
    if zuogong_result is None:
        if gans and zhis and len(gans) == 4 and len(zhis) == 4:
            if not day_gan:
                day_gan = gans[PILLAR_KEYS.index('day')]
            try:
                zuogong_result = analyze_zuogong(
                    day_gan, zhis[PILLAR_KEYS.index('day')],
                    gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
                )
            except Exception:
                zuogong_result = {}
        else:
            zuogong_result = {}

    zg: Dict = zuogong_result or {}
    wa_list: List[Dict] = work_actions if work_actions is not None else (zg.get('work_actions') or [])
    wtypes: List[str] = work_types if work_types is not None else (zg.get('work_types') or [])
    fei: List[str] = fei_shen if fei_shen is not None else (zg.get('fei_shen') or [])
    gshen: List[str] = gong_shen if gong_shen is not None else (zg.get('gong_shen') or [])
    tomb_works: List[Dict] = zg.get('tomb_works') or []
    san_he_formed: bool = bool(zg.get('san_he_formed'))
    has_severe_harm: bool = bool(zg.get('has_severe_harm'))

    # ── 贼神捕神上游信号（净制/包制/冲链）消费 ──
    # zeishen_bushen 为本模块上游：其 jing_zhi(净制 党势-孤立判定) 用于增强本模块
    # 的「制净程度」判定（本模块 _assess_zhi_jing 为保守位置启发式，无制局信号时
    # 采纳 zb 的 党势判定）。bao_zhi/chong_lian 检出仅作上游参考录入输出，不重复
    # 计入功量点——zb 的包制/冲链启发式存在误检（如例六包制、普通4冲链），盲目 +1
    # 会与源文层数相悖，故功量点仍以本模块 san_he_formed / _chain_length 保守判为准。
    if zeishen_bushen_result is None and day_gan and gans and zhis and len(gans) == 4:
        try:
            from mangpai.subjective.zeishen_bushen import analyze_zeishen_bushen
            zeishen_bushen_result = analyze_zeishen_bushen(day_gan, gans, zhis, zg)
        except Exception:
            zeishen_bushen_result = None
    _zb = zeishen_bushen_result or {}
    _zb_sub: Dict = _zb.get('zeishen_bushen') or {}
    _zb_bao = _zb.get('bao_zhi')
    _zb_clian = _zb.get('chong_lian')
    _zb_jing: str = _zb_sub.get('jing_zhi', '') if _zb_sub else ''

    # 推导 day_gan / gans / zhis（十神推断必需）
    if (not day_gan or not gans or not zhis) and wa_list:
        # 由 work_actions 的 from_pos/to_pos 反推 gans/zhis 不可靠，仅尽力推导 day_gan
        pass
    if gans and zhis and not day_gan:
        day_gan = gans[PILLAR_KEYS.index('day')]
    day_wx = GAN_WX.get(day_gan, '')

    reasons: List[str] = []
    points: float = 0.0

    # 数据完全缺失 -> 无功
    if not wa_list and not wtypes:
        return _build_result(
            level=1, points=0.0, score=0,
            reasons=['命局无做功数据，功量微弱（半层/无功），普通百姓层次'],
            zhi_jing='无制', controls=[], gong_cats=[], chain=0,
            penalty='无功', day_wx_ok=bool(day_wx),
        )

    # ── 非辅助做功动作 ──
    non_aux = [wa for wa in wa_list if not wa.get('auxiliary')]

    # ── 制局涉及位置（from + to 双方）──
    # 段氏制局：冲/克/穿/刑/破/合制/墓用 的双方均参与制局。取「双方」而非仅
    # to_pos——势-based 制局中 zuogong 的冲/克方向（按柱序/五行克）未必与
    # 「强方制弱方」的势方向一致（如蒋介石 亥冲巳，实为火土势制亥），故取双方
    # 以覆盖被制方的十神大类（含藏干：亥含甲(官)又主气水(财)，制亥即制官与官之
    # 原神财，蒋介石两层功即此）。
    involved_positions: Set[str] = set()
    # 严格制用目标：to_pos of 冲克穿刑破（用于制墓库/制净的「被制」判定）
    zhi_targets: Set[str] = set()
    control_action_count = 0
    for wa in non_aux:
        tp = wa.get('type', '')
        if tp not in _CONTROL_TYPES:
            continue
        f, t = wa.get('from_pos', ''), wa.get('to_pos', '')
        if f:
            involved_positions.add(f)
        if t:
            involved_positions.add(t)
            control_action_count += 1
        if tp in _ZHI_TYPES and t:
            zhi_targets.add(t)
    # 墓用做功：入墓目标亦属被制方（被墓制）。
    # M4 注记：detect 已放开日柱参与限制（宾位入墓亦检出），confirm S2 将非日柱
    # 入墓标 auxiliary（global_qi）。本模块功量只认 confirm 判定为真做功之墓用
    # （非 auxiliary），宾位入墓（如普例3 戌入辰）仅作结构事实，不加点、不入被制方。
    active_tomb_works = [tw for tw in tomb_works if not tw.get('auxiliary')]
    for tw in active_tomb_works:
        for fld in ('to_pos', 'entombed_pos', 'pos'):
            v = tw.get(fld, '')
            if v:
                involved_positions.add(v)
                zhi_targets.add(v)

    # 制局涉及十神大类（含藏干，用于原神用神同制判定）
    involved_cats: Set[str] = set()
    if day_wx and gans and zhis:
        for pos in involved_positions:
            elem = _elem_of(pos, gans, zhis)
            if elem:
                involved_cats |= _elem_cats(day_wx, elem)
    # 功神十神大类（主气+透干，不含藏干；用于七杀当财等判定）
    gong_cats: Set[str] = set()
    if day_wx and gans and zhis:
        for pos in gshen:
            elem = _elem_of(pos, gans, zhis)
            if elem:
                gong_cats |= _elem_cats(day_wx, elem, include_canggan=False)
    # 透干十神大类（pos -> cats，用于制净：透干原神未被制）
    gan_cats: Dict[str, Set[str]] = {}
    if day_wx and gans:
        for pk in PILLAR_KEYS:
            idx = PILLAR_KEYS.index(pk)
            if idx < len(gans) and gans[idx]:
                gan_cats[f'{pk}_gan'] = _elem_cats(day_wx, gans[idx], include_canggan=False)
    # 废神十神大类（主气+透干，用于制净：同党废神残存）
    fei_cats: Set[str] = set()
    if day_wx and gans and zhis:
        for pos in fei:
            elem = _elem_of(pos, gans, zhis)
            if elem:
                fei_cats |= _elem_cats(day_wx, elem, include_canggan=False)

    # 强制参与位置：经 冲/克/穿/合制 作用的位置（from 或 to）。
    # 段氏原神用神同制须落在一个真实制局目标上--强方制弱方经冲克穿合实现，
    # 刑/破/墓用偏弱或为相生/孤立结构（如普通例三未土经刑/墓用而实为相生命），
    # 不单独支撑原神用神同制，故仅认强制参与位。
    _STRONG_TYPES: Set[str] = (_ZHI_TYPES | _HE_ZHI_TYPES) - {'刑', '破'}
    strong_positions: Set[str] = set()
    for wa in non_aux:
        if wa.get('type') not in _STRONG_TYPES:
            continue
        f, t = wa.get('from_pos', ''), wa.get('to_pos', '')
        if f:
            strong_positions.add(f)
        if t:
            strong_positions.add(t)

    # ── 1. 原神用神同制 -> +2（核心铁律）──
    # 判定：存在一个强制参与位，其干支(含藏干)同时含「用神」与「原神」十神大类。
    # 如亥含甲(官)又主气水(财) -> 制亥即制官与官之原神财(蒋介石两层功)；
    #   申含庚(财)与壬(食伤/财之原神) -> 制申即财与财之原神同制(例七两层功)。
    # 单点位判定避免「财透干 + 某支藏食伤」式的偶然共现误判。
    # 多候选时偏好「财/官杀」为用神（段氏富贵用神：财+食伤=富，官杀+财=贵），
    # 其次偏好含官杀之位（利七杀当财叠加），如例八寅(食伤+比劫)与申(财+食伤)
    # 同现时取申，方可叠加七杀当财达三层。
    yuanshen_hit: Optional[str] = None
    yuanshen_pos: Optional[str] = None
    if day_wx and gans and zhis and strong_positions:
        candidates: List[Tuple[str, str, str]] = []  # (pos, yong, yuan)
        for pos in strong_positions:
            elem = _elem_of(pos, gans, zhis)
            if not elem:
                continue
            pos_cats = _elem_cats(day_wx, elem)
            for yong, yuan in _YUANSHEN_PAIRS:
                if yong in pos_cats and yuan in pos_cats:
                    candidates.append((pos, yong, yuan))
        if candidates:
            def _rank(c: Tuple[str, str, str]) -> Tuple[int, int]:
                pos, yong, _yuan = c
                yong_prio = 0 if yong in ('财', '官杀') else 1
                el = _elem_of(pos, gans, zhis)
                has_gs = bool(el) and '官杀' in _elem_cats(day_wx, el)
                return (yong_prio, 0 if has_gs else 1)
            candidates.sort(key=_rank)
            pos, yong, yuan = candidates[0]
            elem = _elem_of(pos, gans, zhis)
            points += 2
            yuanshen_hit = f'{yong}+{yuan}'
            yuanshen_pos = pos
            tier_hint = ('千万-亿级富命' if yong == '财'
                         else '厅级以上贵命' if yong == '官杀' else '两层功量')
            reasons.append(
                f'原神用神同制：{pos}({elem})含用神「{yong}」与原神「{yuan}」'
                f'同制（+2层，{tier_hint}）'
            )

    # ── 2. 制墓库 -> +2（制局中制墓库地支为两层功）──
    #   保守判定：须三合成势(成势制库)且墓库为制用目标(to_pos of 冲克穿刑破)。
    #   无成势时墓库被冲克多为偶然（如例七寅克戌），不计制墓库，避免误加。
    if san_he_formed and day_wx and gans and zhis:
        for pos in zhi_targets:
            elem = _elem_of(pos, gans, zhis)
            if elem and _is_tomb(elem):
                points += 2
                reasons.append(f'制墓库：成势制墓库「{elem}」（+2层）')
                break

    # ── 3. 七杀当财 -> +1（七杀当财富比财当财量级高一层）──
    #   判定：原神用神同制成立(已有真实制局) + 官杀透干 + 其根(含官杀藏干之地支)
    #   即原神用神同制位(官杀与用神同根于制局目标，如例八申中壬水七杀当财)。
    if yuanshen_hit and yuanshen_pos and day_wx and gans and zhis:
        guansha_gan: Optional[str] = None
        for gpos, gcats in gan_cats.items():
            if '官杀' in gcats:
                guansha_gan = gpos
                break
        if guansha_gan:
            ys_elem = _elem_of(yuanshen_pos, gans, zhis)
            if ys_elem and '官杀' in _elem_cats(day_wx, ys_elem):
                points += 1
                reasons.append(
                    f'七杀当财：官杀透干({guansha_gan})与制局目标({yuanshen_pos}/{ys_elem})'
                    f'同根，七杀当财（+1层）'
                )

    # ── 4. 入墓为功 -> +1（局中有入墓(墓用)做功者算一层功）──
    #   只认 confirm 判定之真墓用（非 auxiliary，M4 放开后宾位入墓不计）。
    if active_tomb_works:
        points += 1
        reasons.append(f'入墓为功：局中墓用做功{len(active_tomb_works)}处（+1层）')

    # ── 5. 库源/连墓 -> +1（被制元素之墓库在局，源头得库加一层）──
    #   源文（李嘉诚例）：「亥出自辰，从辰墓中引出，亥水有源头得到一个大的库，
    #   再加一层功量」。须原神用神同制成立(真实制局)方计，被制元素之墓库在局即此。
    if yuanshen_hit and yuanshen_pos and day_wx and gans and zhis:
        ys_elem = _elem_of(yuanshen_pos, gans, zhis)
        if ys_elem:
            ys_wx = _wx_of(ys_elem)
            for pk in PILLAR_KEYS:
                idx = PILLAR_KEYS.index(pk)
                z = zhis[idx] if idx < len(zhis) else ''
                if z and _is_tomb(z) and ys_wx in _tomb_wx(z):
                    points += 1
                    reasons.append(
                        f'库源/连墓：制局目标「{ys_elem}({ys_wx})」之墓库「{z}」在局，'
                        f'源头得库（+1层）'
                    )
                    break

    # ── 6. 包局/包制 -> +1（年时包局或包制之局加一层）──
    #   判定：三合局成势（围制）。段氏包制为围猎式合围，须成势方可，单凭多柱
    #   制用不足以判定（避免误加），故仅认 san_he_formed。
    if san_he_formed:
        points += 1
        reasons.append('包局/包制：三合局成势围制（+1层）')

    # ── 7. 层层相制 -> +1（乾隆式金字塔逐级相制，保守判定）──
    #   仅认有向「克」链（克方->被克方方向明确）≥2 级。冲为互向、其势方向须
    #   党势判定（属贼神捕神/净制模块），本模块不臆断，故不计入链。
    chain_len = _chain_length(non_aux)
    if chain_len >= 2:
        points += 1
        reasons.append(f'层层相制：克链长{chain_len}级，逐级相制（+1层）')

    # ── 7'. 贼神捕神包制/冲链有条件计入（distrust 有条件翻转）──
    #   段氏包制为围猎式合围（如克林顿寅戌火局+两丙围制申官杀），本模块 san_he_formed
    #   仅认标准三合，非标准三合之包制（寅戌缺午）漏检；zb 的 bao_zhi 启发式能捕获此类
    #   围制，但存在误检（如例六包制、普通4冲链），盲目 +1 与源文相悖。故仅当 zb 同时
    #   判「净制」（jing_zhi=净）时方采信其 bao_zhi--净制为党势-孤立判定之强信号，证
    #   围制之制为真（克林顿/岳飞 净，例六不成）。采信 bao 时其冲链（围制之逐级相制）
    #   一并计入：冲链为围制之子结构，同一净制佐证下不重计误检（普通4冲链无 bao 配合
    #   故不采信）。本模块 san_he_formed / _chain_length 已计者不重计。
    _zb_bao_counted = False
    _zb_boost = 0.0  # bao/clian 计入的功量点（供边界判定：翻转是否 decisive）
    if (_zb_bao and _zb_bao.get('detected') and _zb_jing == '净'
            and not san_he_formed):
        points += 1
        _zb_boost += 1
        _zb_bao_counted = True
        reasons.append('包局/包制：zb 净制佐证下采信围制（+1层）')
        if (_zb_clian and _zb_clian.get('detected') and chain_len < 2):
            points += 1
            _zb_boost += 1
            reasons.append('层层相制：zb 净制佐证下采信冲链（+1层）')

    # ── 7b. 带象 -> +1（高级篇1.4 补齐：干生支之柱为带象，参与做功则其承象计一层）──
    #   源文「干生支之柱为带象，若此带象之字参与做功，则其承载的象（财、官、印）
    #   可直接视为一层功」。去重口径：原神用神同制成立时，制局用神字之象已被 +2
    #   核心铁律覆盖（带象为同制局之子结构），不再单计；仅原神用神同制不成立时，
    #   带象字独立承象方计一层（避免与第六章 14 例回归跨书双计）。
    if yuanshen_hit is None and day_wx and gans and zhis:
        active_pos = set(gshen) | involved_positions
        for i, pk in enumerate(PILLAR_KEYS):
            if i >= len(gans) or i >= len(zhis):
                continue
            gg, zz = gans[i], zhis[i]
            if not gg or not zz:
                continue
            gw, zw = GAN_WX.get(gg, ''), ZHI_WX.get(zz, '')
            if not gw or not zw or WX_SHENG.get(gw) != zw:
                continue  # 非干生支
            xiang = _shishen_cat(day_wx, gw)  # 干之十神=所承之象
            if xiang not in _DAIXIANG_XIANG:
                continue
            if f'{pk}_gan' in active_pos or f'{pk}_zhi' in active_pos:
                points += 1
                reasons.append(
                    f'带象：{pk}柱{gg}{zz}干生支，承「{xiang}」象且参与做功（+1层）'
                )
                break

    # ── 7c. 官统财/财统官 -> +1（高级篇1.4 补齐：官杀与财互统，统摄方计一层）──
    #   源文「官杀多而财少为财统官，财多而官杀少为官统财」（二者皆官杀当财），统摄关系
    #   为一层功。去重口径：官杀+财 正是原神用神同制配对之一，同制成立时已被 +2
    #   覆盖；仅同制不成立时，统摄独立计一层。消费 caiming.classify_caifu_view。
    if yuanshen_hit is None and day_gan and gans and zhis and len(gans) == 4:
        try:
            cf = classify_caifu_view(day_gan, gans, zhis)
        except Exception:
            cf = {}
        tong = [v for v in (cf.get('views') or []) if '统' in v]
        if tong:
            points += 1
            reasons.append(f'统：{tong[0]}，官杀与财互统摄（+1层）')

    # ── M5 高级篇层功四余项（源文 mangpai-gaoji-ocr.txt 828-872「层功计算之基本法则」）──
    # 7e. 月令做功 -> +0.5（法则7「月令做功，加半层功：月令为提纲，能量最为强旺。
    #   若月令直接参与核心做功（为主要功神），则其做功效率因其得时得令而更高」）。
    #   判定：月令支出现在核心做功动作双方（involved_positions，非辅助制/合/墓）。
    #   +0.5 为半层加权，不单独跨档（须与他项累加方显），故不设同制门。
    if day_wx and gans and zhis and len(zhis) > 1:
        _yue_pos = {'month_zhi', 'month_gan'}
        if _yue_pos & involved_positions:
            points += 0.5
            reasons.append(
                f'月令做功：月令{zhis[1]}直接参与核心做功，提纲得时得令（+0.5层）'
            )

    # 7f. 墓库属性 -> +1（法则5「墓库本身，加一层功：墓库参与做功，无论作为体之库
    #   （比劫库、食伤库）还是用之库（财库、官杀库），其库之属性本身就增加一层功
    #   的权重」）。去重口径（与带象/统同例，保理象学6章14例不跨书双计）：
    #   原神用神同制成立时，同制位若为墓库其库性已含于 +2 核心铁律，不再单计；
    #   入墓为功/制墓库已计者同为墓库之功，亦不重复。仅「墓库参与做功而三者俱未
    #   计」（如体之库作功神）方独立加层。
    _tomb_elems_involved: List[str] = []
    if day_wx and gans and zhis:
        for pos in (involved_positions | set(gshen)):
            el = _elem_of(pos, gans, zhis)
            if el and _is_tomb(el) and el not in _tomb_elems_involved:
                _tomb_elems_involved.append(el)
    _rumu_counted = bool(active_tomb_works)   # 入墓为功已计（block 4）
    _zhiku_counted = any('制墓库' in r for r in reasons)  # 制墓库已计（block 2）
    if (yuanshen_hit is None and not _rumu_counted and not _zhiku_counted
            and _tomb_elems_involved):
        points += 1
        reasons.append(
            f'墓库属性：墓库「{"、".join(_tomb_elems_involved)}」参与做功，'
            f'库之属性加层（+1层）'
        )

    # 7g. 开库 -> +1（法则5「若再逢刑冲开库，则功上加功」）。
    #   判定：墓库功已成立（入墓为功或制墓库已计），且该墓库被非辅助刑/冲动作
    #   开之（日柱参与之刑冲方为真开库做功；宾位冲开仅结构事实，不加点）。
    if (_rumu_counted or _zhiku_counted) and gans and zhis:
        _work_tombs: Set[str] = set()
        for tw in active_tomb_works:
            el = _elem_of(tw.get('from_pos', ''), gans, zhis)
            if el and _is_tomb(el):
                _work_tombs.add(el)
        if _zhiku_counted:
            for pos in zhi_targets:
                el = _elem_of(pos, gans, zhis)
                if el and _is_tomb(el):
                    _work_tombs.add(el)
        _opened = False
        for wa in non_aux:
            if wa.get('type') not in ('冲', '刑'):
                continue
            for pk in (wa.get('from_pos', ''), wa.get('to_pos', '')):
                el = _elem_of(pk, gans, zhis)
                if el and el in _work_tombs:
                    _opened = True
                    break
            if _opened:
                break
        if _opened:
            points += 1
            reasons.append(
                f'开库加层：做功墓库「{"、".join(sorted(_work_tombs))}」逢刑冲开库，'
                f'功上加功（+1层）'
            )

    # ── 7d. 化用成局/从杀格 -> +2（化用成局为高层功量，与做功层次 L4 对齐）──
    #   段氏化用成局（zuogong_confirm 的 Level 4）为高层功量：杀印相生（官杀->印->
    #   日主链）化用成功、官杀五行成党势(≥3字)、日主(比劫)无根从弱(≤2字)，且原神
    #   用神同制未成立（纯化用/从杀路径，非制局）-> 化用成局计 +2 层。
    #   权重校准：原 +3 过计（阎锡山造 +1 偏高），降为 +2。
    #   检测独立性：杀印相生链（官杀透干+印透干/印居月令）+ 从杀格（官杀党势≥3、
    #   日主比劫≤2）独立判定，不依赖 work_actions 的 auxiliary 标记--即使命局另有
    #   制用/墓用做功（杀印相生被 zuogong_detect 标 auxiliary），从杀格之化用成局
    #   功量仍独立计 +2（如阎锡山造：制用+墓用基底+1，化用成局+2，合三层）。
    hua_chengju = False
    if yuanshen_hit is None and day_wx and gans and zhis and len(gans) == 4:
        _yin_wx_7d = ''
        for _w, _gen in WX_SHENG.items():
            if _gen == day_wx:
                _yin_wx_7d = _w  # 印五行（生我者）
                break
        _sha_wx_7d = WX_KE_ME.get(day_wx, '')  # 官杀五行（克我者）
        _sha_gan_idx_7d = -1
        if _sha_wx_7d:
            for _i, _g in enumerate(gans):
                if not _g or _i == 2:
                    continue
                if GAN_WX.get(_g, '') == _sha_wx_7d:
                    _sha_gan_idx_7d = _i  # 官杀透干（非日干）
                    break
        _yin_active_7d = False
        if _yin_wx_7d:
            for _i, _g in enumerate(gans):
                if not _g or _i == 2:
                    continue
                if GAN_WX.get(_g, '') == _yin_wx_7d:
                    _yin_active_7d = True  # 印透干
                    break
            if not _yin_active_7d and ZHI_WX.get(zhis[1], '') == _yin_wx_7d:
                _yin_active_7d = True  # 印居月令（司令之印）
        if _sha_gan_idx_7d >= 0 and _yin_active_7d and _sha_wx_7d:
            sha_cnt = sum(1 for gg in gans if GAN_WX.get(gg) == _sha_wx_7d)
            sha_cnt += sum(1 for zz in zhis if ZHI_WX.get(zz) == _sha_wx_7d)
            sha_cnt += sum(1 for zz in zhis
                           for cg, _ in CANG_GAN_MANGPAI.get(zz, [])
                           if GAN_WX.get(cg) == _sha_wx_7d)
            dm_cnt = sum(1 for gg in gans if GAN_WX.get(gg) == day_wx)
            dm_cnt += sum(1 for zz in zhis if ZHI_WX.get(zz) == day_wx)
            if sha_cnt >= 3 and dm_cnt <= 2:
                points += 2
                reasons.append(
                    f'化用成局/从杀格：杀印相生化用、官杀「{_sha_wx_7d}」党势成({sha_cnt}字)、'
                    f'日主从弱(比劫{dm_cnt}字)，纯化用路径（+2层，化用成局为高层功量）'
                )
                # hua_chengju 豁免制不净封顶 + 高层功量加分（化用路径可达四层）：
                # (1) 真从杀格（杀党势>=5，杀极旺日主极弱）为纯化用路径——7d 块仅在
                #     yuanshen_hit=None（无原神用神同制）时运行，杀党势>=5 时无制用可
                #     与之竞争，如阎锡山造（杀金6字）半壁天下。杀党势3-4 为偏从杀，
                #     可能有制用并存，保守不豁免。
                # (2) 杀印相生为显式真做功（非 auxiliary）。
                # 制用为主的命（复例二：原神用神同制+2）yuanshen_hit 已设 -> 7d 块被
                # 跳过，不至此处；普通四柱（PUTONG）虽偶触发从杀格启发式但被普通四柱
                # 降档封顶覆盖，不受加分影响。
                if sha_cnt >= 5 or any(wa.get('type') == '杀印相生'
                                       and not wa.get('auxiliary') for wa in non_aux):
                    hua_chengju = True
                    # 纯化用成局为高层功量：杀印相生无制用竞争，化用路径能量效率高于
                    # 制局（段氏：化用成局可达四层，如阎锡山造半壁天下）。+1 层使纯化用
                    # 命越过制用三层天花板。普通四柱（PUTONG）虽偶触发从杀格启发式，
                    # 但被普通四柱降档封顶覆盖，不受此加分影响。
                    points += 1
                    reasons.append('化用成局高层功量：纯杀印相生化用、无制用做功竞争，'
                                   '化用路径效率高于制局（+1层，可达四层）')

    # ── 8. 制净程度（调节封顶，不加点）──
    zhi_jing, jing_note = _assess_zhi_jing(
        day_wx, involved_cats, zhi_targets, gan_cats, fei_cats, non_aux, has_severe_harm,
    )
    # 贼神捕神净制增强：本模块保守启发式判「无制」时，采纳 zb 的 党势-孤立净制
    # 判定（zb 检出制局而本模块位置启发式未捕获，故据 zb 补 净/不净）。其余情形
    # （本模块已判 净/不净）不覆盖——本模块的位置缺陷信号（日柱被穿/透干原神残存
    # /折扣动作）与 zb 的 党势视角各有所长，并存不覆，避免误升/误降（如例六日柱被穿
    # 本模块判不净，zb 判净，二者并存不覆，层数不变）。
    zb_jing_adopted = False
    if zhi_jing == '无制' and _zb_jing in ('净', '不净'):
        zhi_jing = _zb_jing
        zb_jing_adopted = True
        jing_note = (jing_note + '；' if jing_note else '') + '贼神捕神党势判定' + (
            '：制之干净' if _zb_jing == '净' else '：原神残存未净制')
    # 包制（围制官杀）结构下，zb 的党势-孤立净制判定比本模块位置启发式更可靠--
    # 围制为合围式彻底之制（段氏：制之彻底能成大富/大官），本模块「食伤透干未净制」
    # 等位置缺陷信号在此结构下为伪不净（克林顿申官杀被寅戌火局围制入丑墓，书判
    # 制之彻底、净）。故 bao+zb 净双佐证时，覆本模块「不净」为「净」（仅克林顿/
    # 岳飞两例具此组合，例六 zb 不成故不覆）。
    if (zhi_jing == '不净' and _zb_jing == '净' and _zb_bao_counted):
        zhi_jing = '净'
        zb_jing_adopted = True
        jing_note = (jing_note + '；' if jing_note else '') + '包制围制下采信贼神捕神党势净制：制之干净'
    if zhi_jing == '净' and involved_cats:
        reasons.append('制净：被制用神与其原神俱制、无残存，制之干净')
    elif zhi_jing == '不净':
        if hua_chengju:
            reasons.append('制不净：' + jing_note + '（化用成局/从杀格为化用路径，制净框架不适用，不封顶）')
        else:
            reasons.append('制不净：' + jing_note + '，封顶于三层（达不到四层）')

    # ── 普通四柱降档（压低分数、封顶低层）──
    penalty, penalty_note = _assess_penalty(
        wtypes, non_aux, gshen, fei, control_action_count,
        zb_jing=_zb_jing, yuanshen_hit=yuanshen_hit, hua_chengju=hua_chengju,
    )
    if penalty:
        reasons.append('普通四柱特征：' + penalty_note)

    # ── 层次映射 + 封顶 ──
    raw_level = 4 if points >= 4 else 3 if points >= 3 else 2 if points >= 2 else 1
    level = raw_level
    # 制不净 -> 封顶三层（段氏：制之不净达不到四层，如蒋介石）；
    #   化用成局/从杀格为化用路径非制局，制净框架不适用，不受此封顶。
    if zhi_jing == '不净' and level > 3 and not hua_chengju:
        level = 3
    # 普通四柱降档封顶（源文 6282-6376 三种小功情形）：
    #   相生之功 -> 封顶一层（相生效率低，源文普通例二「相生之功，功不算大」=普通）；
    #   相克之制 -> 封顶二层（仅相克无冲合穿包，功量较小但仍可达两层，源文普通例五=两层）。
    if penalty == '相生之功' and level > 1:
        level = 1
    elif penalty and level > 2:
        level = 2

    # ── 吉凶方向：比劫夺财封顶（R1，见 yongshen.detect_bijiao_duocai）──
    # 段氏「制财得财」以功神非比劫为前提；功神=比劫制财（身强财为用神、财弱孤）
    # 即「比劫夺财」=破财凶，与印/食伤/官制财=得财吉对立（蒋介石印制财=贵，
    # 第9期比劫子冲午财=清家荡产）。命中即按严重度封顶：severe→一层（贫），
    # 否则→二层（小康下），wealth_grade 随 level 落档自动跟随。
    pocai_signal = False
    pocai_severity: Optional[str] = None
    pocai_reason = ''
    _bao_suppress_pocai = _zb_bao_counted
    if day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4:
        bj = detect_bijiao_duocai(day_gan, gans, zhis, wa_list)
        if bj.get('detected') and not _bao_suppress_pocai:
            pocai_signal = True
            pocai_severity = bj.get('severity') or 'normal'
            pocai_reason = bj.get('reason', '')
            cap = 1 if pocai_severity == 'severe' else 2
            if level > cap:
                level = cap
            reasons.append(
                f'比劫夺财·破财（功神=比劫制财，身强财为用神且财弱孤；'
                f'封顶{cap}层，段氏制财得财以功神非比劫为前提）'
            )
        elif bj.get('detected') and _bao_suppress_pocai:
            pocai_reason = '比劫夺财抑制：包制（围制官杀）结构下比劫为围制之一员（合杀库/制官杀），非夺财破财（不封顶）'
            reasons.append(
                '比劫夺财抑制：命局为包制（围制官杀）结构，比劫作围制之一员'
                '（合杀库/制官杀），段氏「制财得财」之夺财不适用，不封顶'
            )

    # ── 分数（层内连续刻画强弱）──
    score = _compute_score(level, raw_level, points, zg, gshen, fei, non_aux,
                           zhi_jing, penalty)

    # ── 边界区标注（L2/L3/L4 不强制二选一）──
    boundary = _compute_boundary(level, score, points, _zb_bao_counted, _zb_boost)
    if boundary:
        reasons.append(f'边界区：score={score} 落 {boundary}（不强制二选一，宜结合制净/做功细辨）')

    result = _build_result(
        level=level, points=points, score=score, reasons=reasons, zhi_jing=zhi_jing,
        controls=sorted(involved_cats), gong_cats=sorted(gong_cats),
        chain=chain_len, penalty=penalty, yuanshen_hit=yuanshen_hit,
        day_wx_ok=bool(day_wx), boundary=boundary, raw_level=raw_level,
    )

    # ── M5 双轨对账：gongliang.level（富贵量级）vs zuogong.work_level（做功效率）──
    # 两套体系并行（模块 docstring）：work_level 0-5 层看「做功成立/效率」，
    # gongliang 1-4 层看「富贵量级」。差≥2 层为视角背离，标冲突供复核（只标注，
    # 不改任一层数——如普例1 做功效率高而富贵量级被普通四柱降档，即合理背离）。
    _wl = zg.get('work_level')
    if isinstance(_wl, int) and _wl > 0:
        _diff = level - _wl
        _duizhang = {
            'work_level': _wl,
            'gongliang_level': level,
            'diff': _diff,
            'conflict': abs(_diff) >= 2,
        }
        if abs(_diff) >= 2:
            _duizhang['note'] = (
                f'双轨冲突：做功层次L{_wl}（效率视角）与功量L{level}（富贵量级）'
                f'差{abs(_diff)}层，宜复核（降档/封顶/体系口径差异）'
            )
            result['reasons'].append('双轨对账：' + _duizhang['note'])
        result['work_level_duizhang'] = _duizhang

    # 比劫夺财破财方向信号（供 caiming/guanming/zhiye 反哺降档/否决）
    result['pocai_signal'] = pocai_signal
    result['pocai_severity'] = pocai_severity
    result['pocai_reason'] = pocai_reason

    # 贼神捕神上游信号录入输出（已消费：净制增强 zhi_jing；包制/冲链作参考信号）。
    # 不重复计入功量点（zb 包制/冲链启发式有误检，盲目 +1 与源文层数相悖）。
    zb_bao_on = bool(_zb_bao and _zb_bao.get('detected'))
    zb_clian_on = bool(_zb_clian and _zb_clian.get('detected'))
    result['zeishen_jing_zhi'] = _zb_jing
    result['zeishen_bao_zhi'] = bool(_zb_bao) and zb_bao_on
    result['zeishen_chong_lian'] = bool(_zb_clian) and zb_clian_on
    if zb_jing_adopted or zb_bao_on or zb_clian_on or (_zb_jing and _zb_jing != '无制'):
        sig = []
        if _zb_jing and _zb_jing != '无制':
            sig.append(f'净制={_zb_jing}')
        if zb_bao_on:
            sig.append('包制检出')
        if zb_clian_on:
            sig.append('冲链检出')
        if zb_jing_adopted:
            sig.append('已据净制增强制净判定')
        result['reasons'].append(
            f'贼神捕神上游信号（{"、".join(sig)}；包制/冲链不重复计入功量点，以本模块保守判为准）'
        )
    return result


# ── 制净程度判定 ──
def _assess_zhi_jing(
    day_wx: str,
    involved_cats: Set[str],
    zhi_targets: Set[str],
    gan_cats: Dict[str, Set[str]],
    fei_cats: Set[str],
    non_aux: List[Dict],
    has_severe_harm: bool,
) -> Tuple[str, str]:
    """判定制净程度（段氏：制之干净方达高层，制之不净封顶三层）。

    用神限定「财/官杀」（段氏富贵用神）。判定不净的四种信号：
      (1) 日柱被穿（has_severe_harm）-> 做功质量受损；
      (2) 透干原神未被制：被制用神 C 之原神透干(天干)且该天干非制用目标
          (to_pos of 冲克穿刑破)--如蒋介石伤官庚金(财之原神)透干未净制；
      (3) 同党废神：被制用神 C 出现于废神位(未参与做功的闲置同党)--如普通例四
          巳火官杀无制(废神)而午火官星制之不净；
      (4) 制用动作含空亡/长生/天干入墓折扣 -> 制之未尽。
    无以上信号则净。

    Returns:
        (程度, 说明)  程度 ∈ {'净','不净','无制'}
    """
    if not involved_cats or not day_wx:
        return '无制', ''
    if has_severe_harm:
        return '不净', '日柱被穿，做功质量受损'

    yuan_map = dict(_YUANSHEN_PAIRS)  # 用神 -> 原神
    yongshen = {c for c in ('财', '官杀') if c in involved_cats}

    # (2) 透干原神未被制
    for c in yongshen:
        yuan = yuan_map.get(c)
        if not yuan:
            continue
        for gpos, gcats in gan_cats.items():
            if yuan in gcats and gpos not in zhi_targets:
                return '不净', f'用神「{c}」之原神「{yuan}」透干({gpos})未被净制'

    # (3) 同党废神残存
    for c in yongshen:
        if c in fei_cats:
            return '不净', f'用神「{c}」有同党废神残存未制'

    # (4) 折扣动作
    if any(wa.get('efficiency_discount') for wa in non_aux
           if wa.get('type') in _CONTROL_TYPES):
        return '不净', '制用动作含空亡/长生折扣，制之未尽'

    return '净', ''


# ── 普通四柱降档判定 ──
def _assess_penalty(
    wtypes: List[str],
    non_aux: List[Dict],
    gshen: List[str],
    fei: List[str],
    control_action_count: int,
    *,
    zb_jing: str = '',
    yuanshen_hit: Optional[str] = None,
    hua_chengju: bool = False,
) -> Tuple[Optional[str], str]:
    """判定普通四柱降档原因（源文 6282-6376 三种小功情形）。"""
    wset = set(wtypes)
    zhi_types_present = {wa.get('type') for wa in non_aux
                         if wa.get('type') in _ZHI_TYPES and not wa.get('auxiliary')}
    he_types_present = {wa.get('type') for wa in non_aux
                        if wa.get('type') in _HE_ZHI_TYPES and not wa.get('auxiliary')}
    has_mu = '墓用' in wset
    has_chengshi = '成势' in wset

    # 三：只有相克之制（无冲/穿/刑/破/合制/墓用/成势）-> 功量较小
    only_ke = (zhi_types_present <= {'克'}) and not he_types_present and not has_mu and not has_chengshi
    if only_ke and '制用' in wset:
        return '相克之制', '仅有相克之制，无冲/合/穿/包制，功量较小'

    # 三：仅以相生做功（生用/化用，无制用）-> 功量较小
    if wset and '制用' not in wset and (wset & {'生用', '化用', '禄', '合用'}):
        return '相生之功', '仅以相生做功，无制局，功量较小'

    # 二：有气势但气势浪费（做功少）-> 功小（M5：回接 zeishen_bushen 党势判定）
    #   有气势（成势或功神成党≥3）而实制动作稀缺（控制类动作≤1）、zb 党势判
    #   净制不成、原神用神同制不成立、非化用成局——方为气势浪费；制局已成
    #   （zb 净）或同制/化用成立者气势未浪费，不降档。
    has_qishi = has_chengshi or len(gshen) >= 3
    if (wset and has_qishi and control_action_count <= 1
            and zb_jing != '净' and yuanshen_hit is None and not hua_chengju):
        return '气势浪费', '有气势但气势浪费（功神多而实制少，贼神捕神判净制不成），功小'

    return None, ''


# ── 层层相制链长（保守：仅认有向「克」链）──
def _chain_length(non_aux: List[Dict]) -> int:
    """计算有向「克」链最长长度（A克B、B克C、C克D -> 3）。

    仅取 type='克'（克方->被克方方向明确）建图求最长简单路径边数。
    冲为互向、其势方向须党势(贼神捕神)判定，本模块不臆断，故不计入链。
    乾隆式金字塔(子制午、午制酉、酉制卯)多为冲/势结构，克链未必覆盖，
    属已知局限（见模块 docstring）。
    """
    edges: Dict[str, Set[str]] = {}
    for wa in non_aux:
        if wa.get('type') != '克':
            continue
        f, t = wa.get('from_pos', ''), wa.get('to_pos', '')
        if f and t and f != t:
            edges.setdefault(f, set()).add(t)

    best = 0
    # 最长路径（图小，DFS 即可；防环用 visited）
    def _dfs(node: str, visited: Set[str]) -> int:
        depth = 0
        for nxt in edges.get(node, ()):
            if nxt in visited:
                continue
            visited.add(nxt)
            depth = max(depth, 1 + _dfs(nxt, visited))
            visited.discard(nxt)
        return depth

    for start in edges:
        best = max(best, _dfs(start, {start}))
    return best


# ── 边界区标注 ──
def _compute_boundary(
    level: int,
    score: Optional[int],
    points: float,
    bao_counted: bool,
    bao_boost: float,
) -> Optional[str]:
    """层边界标注：返回 'L{n}/L{n+1}边界' 或 None。

    段氏四层功 L2/L3/L4 原为硬切，score 落在层边界 ±5 内时不强制二选一，
    标注边界区。两种触发（前者为 spec 机制，后者为判定性翻转的边界外延）：

    (1) score 距当前层下沿(lo)≤5 -> 与下层 L{level-1}/L{level} 交界
        （score 微降即跌入下层）；距上沿(hi)≤5 -> 与上层 L{level}/L{level+1} 交界。
        L1 无下邻、L4 无上邻，仅判有邻一侧。此为「score 在边界 ±5 内」的主机制。
    (2) 包制 distrust 翻转 decisive（bao_counted 且翻转前功量点不足以维系本层）->
        实为 L{level-1}/L{level} 边界：翻转采信前本可降一层（如克林顿寅戌火局围制
        申官杀、岳飞包制），score 经加分后落层中段、不再显露边界，故据翻转标注其
        与下层之交。decisive 判定：(points - bao_boost) < level，即剔除翻转加分后
        功量点达不到本层门槛，证翻转为本层之决定性加分（非锦上添花）。

    注：封顶降档（raw_level>level，如蒋介石制不净/普例相生降档）不单列边界条件--
    封顶将 score 压向层下沿，距下沿≤5 者已由 (1) 标注（如蒋介石 score70 标 L2/L3）；
    多级封顶（普例1 raw4->L1、乞丐 raw2->L1）score 落层底、远离上沿，非边界。
    """
    if score is None:
        score = 0
    lo, hi = _SCORE_BAND[level]
    # (1) score 距层沿 ≤5（spec 机制）
    if level > 1 and (score - lo) <= 5:
        return f'L{level-1}/L{level}边界'
    if level < 4 and (hi - score) <= 5:
        return f'L{level}/L{level+1}边界'
    # (2) 包制 distrust 翻转 decisive -> 与下层交界
    if bao_counted and level >= 2 and (points - bao_boost) < level:
        return f'L{level-1}/L{level}边界'
    return None


# ── 分数计算 ──
def _compute_score(
    level: int,
    raw_level: int,
    points: float,
    zg: Dict,
    gshen: List[str],
    fei: List[str],
    non_aux: List[Dict],
    zhi_jing: str,
    penalty: Optional[str],
) -> int:
    """层内连续分数（0-100）。

    base 取该层区间中点偏下，再按 功神占比/制净/折扣/势成/降档 微调，
    最终 clamp 到 [lo, hi] 层区间。raw_level>level（被封顶）时压向层区间上沿之下。
    """
    lo, hi = _SCORE_BAND[level]
    base = _SCORE_BASE[level]
    adj = 0.0

    # 功神占比高 -> 效率高
    total_positions = len(gshen) + len(fei)
    if total_positions > 0:
        adj += (len(gshen) / total_positions) * 8
    # 制净加分 / 不净减分
    if zhi_jing == '净':
        adj += 6
    elif zhi_jing == '不净':
        adj -= 6
    # 势成（三合局/成势）加分
    if zg.get('san_he_formed') or '成势' in (zg.get('work_types') or []):
        adj += 4
    # 折扣动作多 -> 减分
    disc = sum(1 for wa in non_aux if wa.get('efficiency_discount'))
    if disc:
        adj -= min(disc * 2, 8)
    # 普通四柱降档 -> 强力压低
    if penalty:
        adj -= 10
    # 被封顶（raw_level>level）-> 压向层区间下沿
    if raw_level > level:
        adj -= 8

    score = int(round(base + adj))
    return max(lo, min(hi, score))


# ── 结果装配 ──
def _build_result(
    level: int,
    points: float,
    score: Optional[int],
    reasons: List[str],
    zhi_jing: str,
    controls: List[str],
    gong_cats: List[str],
    chain: int,
    penalty: Optional[str],
    yuanshen_hit: Optional[str] = None,
    day_wx_ok: bool = True,
    boundary: Optional[str] = None,
    raw_level: Optional[int] = None,
) -> Dict:
    tier = _TIER_NAMES.get(level, '小富小贵')
    wealth_grade = _WEALTH_GRADE.get(level, '')
    rank_grade = _RANK_GRADE.get(level, '')
    fugui_pinjian = _FUGUI_PINJIAN.get(level, '')
    lo, hi = _SCORE_BAND[level]
    if score is None:
        # 兜底：未预算分数时按功量点在层区间内插值
        span = hi - lo
        p_lo = {1: 0, 2: 2, 3: 3, 4: 4}.get(level, 0)
        p_hi = {1: 1.99, 2: 2.99, 3: 3.99, 4: 6}.get(level, p_lo + 2)
        frac = max(0.0, min(1.0, (points - p_lo) / max(p_hi - p_lo, 1)))
        score = lo + int(round(span * (0.3 + 0.6 * frac)))
        score = max(lo, min(hi, score))
    if not day_wx_ok and not reasons:
        reasons = ['缺日干/四柱，十神推断不可用，仅按结构信号评估，置信度低']

    return {
        'level': level,
        'tier_name': tier,
        'score': score,
        'gong_points': round(points, 2),
        'reasons': reasons,
        'zhi_jing': zhi_jing,
        'yuanshen_yongshen': yuanshen_hit,
        'controls': controls,
        'gong_shen_cats': gong_cats,
        'chain_length': chain,
        'penalty': penalty,
        'confidence': '中' if day_wx_ok else '低',
        'wealth_grade': wealth_grade,
        'rank_grade': rank_grade,
        'fugui_pinjian': fugui_pinjian,
        'boundary': boundary,
        'raw_level': raw_level if raw_level is not None else level,
    }
