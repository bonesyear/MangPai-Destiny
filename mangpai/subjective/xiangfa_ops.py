"""
xiangfa_ops - 盲派象法操作层·主观层（subjective）

理论来源：段建业《盲派中级命理学》第七章「象的应用」（源文 2113-2592 行）
          《段氏理象学》象法篇
核心思想：象法四层（干支象/宫位象/十神象/神煞象）为**静态数据**（见 objective.xiangfa），
          本模块实现象法七原则的**操作规则**--在四层数据上做复合取象，产出「复合象」。

象法七原则（段氏第七章）：
  1. 共象：两类及以上象（干支/宫位/十神/神煞）指向同一事物 -> 锁定（取象定论）。
  2. 合象：天干合/地支合产生**新象**（合双方之十神组合 + 合化之气）。
  3. 化象：合化成功后的**新象**（化气五行之象 + 杀印相生化象）。
  4. 墓象：入墓/开库之物象变化（财入库=守财、官入库=封存/狱象；开库=墓物复出）。
  5. 制象：制住了才有象（制官得官、制财得财）；主制宾=得，宾制主=失/被制。
  6. 带象（带帽）：天干（帽）+地支藏干（身）十神组合产生复合象（印带官帽、财带官帽…）。
  7. 借象：借邻柱/六合/通禄之象（自身无某象而借邻柱或合支之象补足）。

消费关系：
  - objective.xiangfa（四层象数据）
  - objective.zuogong_detect.detect_relations（合/化/制关系，合象/化象/制象用）
  - objective.binzhu.analyze_binzhu（主宾，制象方向用）
  - objective.canggan.get_canggan_mangpai（藏干，带象身十神用）
  - objective.muku.analyze_muku（墓库开闭/入墓，墓象用）
  - objective.shensha.compute_shensha_ext（神煞落柱，共象用）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：象法取象高度解释性，各师口传有细微差异；带帽组合/借象规则为段氏主流口径，
          主体域标签为工程化归纳（非盲师口传定量表）。
置信度：中
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    TIAN_GAN_HE, LIU_HE, AN_HE, LU, HUA_YONG_MAP,
    TOMB_MAP, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.xiangfa import (
    GAN_XIANG, ZHI_XIANG, GONG_WEI_XIANG, SHISHEN_XIANG, SHENSHA_XIANG,
    get_gan_xiang, get_zhi_xiang, get_gongwei_xiang,
    get_shishen_xiang, get_shensha_xiang,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.binzhu import analyze_binzhu
from mangpai.objective.muku import analyze_muku
from mangpai.objective.shensha import compute_shensha_ext
from mangpai.objective.zuogong_detect import detect_relations, detect_jia_ju
from mangpai.subjective.zeishen_bushen import (
    detect_zeishen_bushen, detect_bao_zhi, detect_chong_lian,
    _party_strength, _CHENG_DANG,
)

# 滴天髓干支性情（foundation 中性层）：取象时按命局上下文匹配该干性情规则，
# 其所述五行（相对日主之十神）映射为主体域，作为共象之一层参与锁定。
# 软依赖：foundation 缺失则该层降级为空，不影响其余象层。
try:
    from foundation.objective import match_ganqing, season_of as _ganqing_season_of
except Exception:  # pragma: no cover - foundation 不可用时降级
    match_ganqing = None
    _ganqing_season_of = None

_YANG_GANS = set('甲丙戊庚壬')
_YANG_ZHIS = set('子寅辰午申戌')

# ── 柱位键 -> 宫位象名 ──
_PILLAR_NAME: Dict[str, str] = {
    'year': '年柱', 'month': '月柱', 'day': '日柱', 'hour': '时柱',
}

# ── 制用动作 type 集合（冲克穿刑破，纯制家族；合制另列）──
_ZHI_CONTROL: Set[str] = {'冲', '克', '穿', '刑', '破'}
# ── 合制动作 type（合以制之）──
_HE_CONTROL: Set[str] = {'天干合', '地支合', '暗合', '半合'}

# ── 主体域（取象锁定的事物大类）──
# 干支象 nature/person/thing 字段关键词 -> 主体域（用于干支象层打标）
_DOMAIN_KW: Dict[str, List[str]] = {
    '官权': ['官', '权', '法', '纪律', '兵', '武', '管', '首', '君', '帅'],
    '财': ['财', '薪', '资', '商', '富', '投资', '存款', '赌', '借贷'],
    '印文': ['印', '文', '学', '书', '历', '师', '母', '契', '房产', '宗', '玄', '药'],
    '食艺': ['食', '艺', '才', '作品', '饮食', '发明', '口才', '律', '讼', '生'],
    '婚情': ['妻', '夫', '婚', '情', '桃', '色', '淫', '情人', '配偶', '寡', '妓'],
    '父母': ['祖', '长辈', '母', '父', '父母', '家长'],
    '子女': ['子女', '下属', '晚辈', '婢', '徒'],
    '灾刑': ['灾', '凶', '血', '伤', '病', '刑', '劫', '贼', '盗', '死', '险', '屠', '囚'],
    '动迁': ['马', '动', '迁', '车', '行', '旅', '奔波', '舟', '网'],
}

# 十神 -> 主体域（十神象层打标）
_SHISHEN_DOMAIN: Dict[str, str] = {
    '正官': '官权', '七杀': '官权',
    '正财': '财', '偏财': '财',
    '正印': '印文', '偏印': '印文',
    '食神': '食艺', '伤官': '食艺',
    '比肩': '比劫', '劫财': '比劫',
}

# 宫位 -> 主体域（宫位象层打标；日柱兼主婚情，年月主父母，时柱主子女）
_GONGWEI_DOMAIN: Dict[str, List[str]] = {
    '年柱': ['父母'],
    '月柱': ['父母'],
    '日柱': ['婚情'],
    '时柱': ['子女'],
}

# 神煞 -> 主体域（神煞象层打标）
_SHENSHA_DOMAIN: Dict[str, str] = {
    '天乙贵人': '官权', '文昌': '印文', '华盖': '印文',
    '桃花': '婚情', '驿马': '动迁',
    '劫煞': '灾刑', '灾煞': '灾刑', '羊刃': '灾刑',
    '孤辰': '婚情', '寡宿': '婚情',
}

# 十神大类 -> 主体域（干支性情象层打标：把性情所述五行相对日主转十神大类再落域）
_CAT_DOMAIN: Dict[str, str] = {
    '官杀': '官权', '财': '财', '印': '印文',
    '食伤': '食艺', '比劫': '比劫',
}


def _ganqing_layer_domains(
    gan: str, day_gan: str, gans: List[str], zhis: List[str],
) -> Set[str]:
    """滴天髓干支性情象层：按命局上下文匹配该干性情规则，取所述五行->主体域。

    每条命中规则在其 behavior/rationale 文本中提及的五行（木火土金水），
    相对日主转十神大类（_wx_to_shishen_cat）再落主体域。一干可命中多条规则，
    各规则所述五行之主体域并集为本柱性情象所涉主体域，供共象层参与锁定。

    ganqing 不可用时返回空集（该层降级，不影响其余象层）。
    """
    if not match_ganqing or not gan or not day_gan or len(zhis) != 4 or len(gans) != 4:
        return set()
    month_zhi = zhis[PILLAR_KEYS.index('month')]
    day_gz = gans[PILLAR_KEYS.index('day')] + zhis[PILLAR_KEYS.index('day')]
    season = _ganqing_season_of(month_zhi) if (_ganqing_season_of and month_zhi) else None
    try:
        rules = match_ganqing(
            gan, season=season, month_zhi=month_zhi,
            stems=gans, branches=zhis, day_gz=day_gz,
        )
    except Exception:
        return set()
    doms: Set[str] = set()
    for r in rules or []:
        text = (getattr(r, 'behavior', '') or '') + (getattr(r, 'rationale', '') or '')
        for wx in ('木', '火', '土', '金', '水'):
            if wx in text:
                dom = _CAT_DOMAIN.get(_wx_to_shishen_cat(day_gan, wx), '')
                if dom:
                    doms.add(dom)
    return doms

# ── 带帽组合：帽(天干十神) + 身(地支藏干十神) -> 复合象 ──
# 段氏带象口径（《段氏理象学》带象原则）：一柱干支，干(天干)为帽/头、支(地支藏干)
# 为身/肢体，命名作「身带帽帽」--身(地支藏干)在前、帽(天干)在后。键=(帽十神大类,
# 身十神大类)；name = f"{身}带{帽}帽"，'官杀'大类显示作'官'（书作印带官帽/官带财帽）。
# '官杀'/'财'/'印'/'食伤'/'比劫' 为十神大类。
_DAIMAO_COMBO: Dict[Tuple[str, str], Dict] = {
    ('印', '官杀'): {'name': '官带印帽', 'subject': '职权',
                       'desc': '印为帽(天干)、官杀为身(地支藏干)，官带印帽，官印相生，主有职有权'},
    ('财', '官杀'): {'name': '官带财帽', 'subject': '财权',
                       'desc': '财为帽(天干)、官杀为身(地支藏干)，官带财帽，主管理财的官、财权双得'},
    ('官杀', '印'): {'name': '印带官帽', 'subject': '职权',
                       'desc': '官杀为帽(天干)、印为身(地支藏干)，印带官帽，主有职权、任职掌印、有学历任官'},
    ('食伤', '财'): {'name': '财带食伤帽', 'subject': '技艺生财',
                       'desc': '食伤为帽(天干)、财为身(地支藏干)，财带食伤帽，主以技艺智力生财'},
    ('官杀', '财'): {'name': '财带官帽', 'subject': '官财',
                       'desc': '官杀为帽(天干)、财为身(地支藏干)，财带官帽，主公家之财、因官得财'},
    ('印', '财'): {'name': '财坏印（财带印帽）', 'subject': '破印',
                    'desc': '印为帽(天干)、财为身(地支藏干)，财带印帽，财来坏印，主薪水或学业受损、破印失信'},
    ('比劫', '官杀'): {'name': '官带比劫帽', 'subject': '竞争得权',
                        'desc': '比劫为帽(天干)、官杀为身(地支藏干)，官带比劫帽，主竞争取权、合伙任职'},
}


# ───────────────────── 基础工具 ─────────────────────

def _compute_shishen(day_gan: str, gan: str) -> str:
    """计算 gan 相对 day_gan 的十神（与 dayun._compute_shishen 同口径）。"""
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
    """十神全名 -> 大类（官杀/财/印/食伤/比劫/日主/空）。"""
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


def _wx_to_shishen_cat(day_gan: str, wx: str) -> str:
    """五行 -> 相对日主十神大类（地支五行/化气五行转十神用）。"""
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


def _pos_pillar(pos: str) -> str:
    """pos('day_gan'/'month_zhi') -> 柱位键('day'/'month')。"""
    if not pos:
        return ''
    return pos.split('_')[0]


def _is_zhu(pos: str) -> bool:
    """pos 是否在主位（日柱/时柱，binzhu 三层模型 layer1=主）。"""
    pk = _pos_pillar(pos)
    return pk in ('day', 'hour')


def _elem_of_pos(pos: str, gans: List[str], zhis: List[str]) -> str:
    """pos -> 对应天干或地支字符（gan 位取天干，zhi 位取地支）。"""
    if not pos or '_' not in pos:
        return ''
    p, t = pos.split('_', 1)
    if p not in PILLAR_KEYS:
        return ''
    idx = PILLAR_KEYS.index(p)
    if idx >= len(gans) or idx >= len(zhis):
        return ''
    return gans[idx] if t == 'gan' else zhis[idx]


def _wx_of(elem: str) -> str:
    """天干或地支 -> 五行。"""
    return GAN_WX.get(elem, '') or ZHI_WX.get(elem, '')


def _shishen_list_of_pos(
    pos: str, day_gan: str, gans: List[str], zhis: List[str],
) -> List[str]:
    """pos 的十神全名列表（gan 位单值；zhi 位取所有藏干十神，本气在先）。"""
    if not pos:
        return []
    pk = _pos_pillar(pos)
    if pk not in PILLAR_KEYS:
        return []
    idx = PILLAR_KEYS.index(pk)
    if pos.endswith('_gan'):
        g = gans[idx] if idx < len(gans) else ''
        ss = _compute_shishen(day_gan, g)
        return [ss] if ss else []
    # zhi 位：取藏干十神（本气在先，去重保序）
    z = zhis[idx] if idx < len(zhis) else ''
    out: List[str] = []
    for cg, _qi in get_canggan_mangpai(z):
        ss = _compute_shishen(day_gan, cg)
        if ss and ss not in out:
            out.append(ss)
    return out


def _domains_of_text(text: str) -> Set[str]:
    """干支象文本 -> 主体域集合（关键词扫描）。"""
    if not text:
        return set()
    return {dom for dom, kws in _DOMAIN_KW.items() if any(k in text for k in kws)}


def _domains_of_ganzhi(gan: str, zhi: str) -> Set[str]:
    """干支象层 -> 主体域集合（扫天干象+地支象的 nature/person/thing/place）。"""
    doms: Set[str] = set()
    gx = get_gan_xiang(gan)
    zx = get_zhi_xiang(zhi)
    for d in (gx, zx):
        for field in ('nature', 'person', 'thing', 'place', 'body'):
            doms |= _domains_of_text(d.get(field, ''))
    return doms


def _shensha_by_pillar(shensha_result: Optional[Dict]) -> Dict[str, List[str]]:
    """compute_shensha_ext 结果 -> {柱位键: [神煞名]}（反转 in_pillars）。

    修批B：并入 year_ref/day_ref 子键落柱——F13 后主键=reference 所定柱，
    只读主键时次柱（年支侧）命中漏进共象映射（gaoji:7912 年支同查）。"""
    by_p: Dict[str, List[str]] = {k: [] for k in PILLAR_KEYS}
    if not shensha_result:
        return by_p
    for name, info in shensha_result.items():
        if not isinstance(info, dict):
            continue
        subs = [info] + [info[k] for k in ('year_ref', 'day_ref')
                         if isinstance(info.get(k), dict)]
        for sub in subs:
            for pk in sub.get('in_pillars', []) or []:
                if pk in by_p and name not in by_p[pk]:
                    by_p[pk].append(name)
    return by_p


def _ensure_relations(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict],
) -> Dict:
    """缺 relations 时自调 detect_relations。"""
    if relations is not None:
        return relations
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {}
    idx_day = PILLAR_KEYS.index('day')
    try:
        return detect_relations(
            day_gan, zhis[idx_day],
            gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
    except Exception:
        return {}


def _ensure_muku(gans: List[str], zhis: List[str], muku_result: Optional[Dict]) -> Dict:
    """缺 muku 结果时自调 analyze_muku。"""
    if muku_result is not None:
        return muku_result
    if len(zhis) != 4:
        return {}
    try:
        return analyze_muku(zhis, gans)
    except Exception:
        return {}


# ───────────────────── 1. 共象 ─────────────────────

def gongxiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    shensha_result: Optional[Dict] = None,
) -> List[Dict]:
    """共象原则：两类及以上象指向同一事物 -> 锁定。

    逐柱聚合四层象（干支象/宫位象/十神象/神煞象），按主体域打标；
    同一主体域被 ≥2 层指向 -> 锁定该事物（取象定论）。

    Returns:
        共象锁定记录列表，每项含 subject/domain/layers/pillar/pos/evidence/locked/desc。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings

    shen_by_p = _shensha_by_pillar(shensha_result)

    for i, pk in enumerate(PILLAR_KEYS):
        gan, zhi = gans[i], zhis[i]
        pname = _PILLAR_NAME[pk]
        pos_gan = f'{pk}_gan'

        # 各层 -> 主体域集合
        layer_domains: Dict[str, Set[str]] = {}
        layer_domains['干支象'] = _domains_of_ganzhi(gan, zhi)
        layer_domains['宫位象'] = set(_GONGWEI_DOMAIN.get(pname, []))
        ss = _compute_shishen(day_gan, gan)
        if ss and ss in _SHISHEN_DOMAIN:
            layer_domains['十神象'] = {_SHISHEN_DOMAIN[ss]}
        else:
            layer_domains['十神象'] = set()
        shen_domains = {
            _SHENSHA_DOMAIN.get(n, '') for n in shen_by_p.get(pk, [])
        }
        shen_domains.discard('')
        layer_domains['神煞象'] = shen_domains

        # 干支性情象（滴天髓）：该柱天干命中的性情规则所述五行之主体域
        layer_domains['性情象'] = _ganqing_layer_domains(gan, day_gan, gans, zhis)

        # 主体域 -> 命中层列表
        domain_layers: Dict[str, List[str]] = {}
        for layer, doms in layer_domains.items():
            for dom in doms:
                domain_layers.setdefault(dom, []).append(layer)

        for dom, layers in domain_layers.items():
            if len(set(layers)) >= 2:
                uniq_layers = list(dict.fromkeys(layers))
                findings.append({
                    'principle': '共象',
                    'subject': dom,
                    'domain': dom,
                    'layers': uniq_layers,
                    'pillar': PILLAR_NAMES_CN[i],
                    'pos': pos_gan,
                    'evidence': [f'{l}指向{dom}' for l in uniq_layers],
                    'locked': True,
                    'desc': f'{PILLAR_NAMES_CN[i]}柱{dom}象被{len(uniq_layers)}层象（{"、".join(uniq_layers)}）共同指向，共象锁定',
                })
    return findings


# ───────────────────── 2. 合象 ─────────────────────

def hexiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
) -> List[Dict]:
    """合象原则：天干合/地支合产生新象。

    天干五合 -> 合化气之象 + 合双方十神组合之象（日干合财=合财象、合官=合官象）；
    地支六合 -> 合化/闭气之新象；三合局 -> 成势之象。

    Returns:
        合象记录列表。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    day_wx = GAN_WX.get(day_gan, '')

    for a in wa:
        t = a.get('type', '')
        if t == '天干合':
            he_type = rel.get('day_he_type') or ''
            from_pos, to_pos = a.get('from_pos', ''), a.get('to_pos', '')
            # 合化气
            pair = (gans[PILLAR_KEYS.index(_pos_pillar(from_pos))] if _pos_pillar(from_pos) in PILLAR_KEYS else '',
                    gans[PILLAR_KEYS.index(_pos_pillar(to_pos))] if _pos_pillar(to_pos) in PILLAR_KEYS else '')
            hua_wx = HUA_YONG_MAP.get(pair) or HUA_YONG_MAP.get((pair[1], pair[0]), '')
            subject = ''
            if he_type == '合财':
                subject = '合财（得财/姻缘）'
            elif he_type == '合官':
                subject = '合官（就职/姻缘·女命）'
            else:
                subject = f'合（化{hua_wx}）' if hua_wx else '合'
            findings.append({
                'principle': '合象',
                'subject': subject,
                'domain': _wx_to_shishen_cat(day_gan, hua_wx) if hua_wx else '',
                'pillar': PILLAR_NAMES_CN[PILLAR_KEYS.index(_pos_pillar(to_pos))] if _pos_pillar(to_pos) in PILLAR_KEYS else '',
                'pos': to_pos,
                'evidence': [a.get('desc', ''), f'合化气={hua_wx}' if hua_wx else '合未化'],
                'locked': True,
                'desc': f'{a.get("desc", "")}，产生{subject}之合象',
            })
        elif t in ('地支合', '暗合', '半合'):
            findings.append({
                'principle': '合象',
                'subject': '地支合（合绊/合制）',
                'domain': '',
                'pillar': '',
                'pos': a.get('to_pos', ''),
                'evidence': [a.get('desc', '')],
                'locked': True,
                'desc': f'{a.get("desc", "")}，地支合产生合绊/合制新象',
            })
        elif t == '三合局':
            findings.append({
                'principle': '合象',
                'subject': '三合成势',
                'domain': '',
                'pillar': '',
                'pos': a.get('to_pos', ''),
                'evidence': [a.get('desc', '')],
                'locked': True,
                'desc': f'{a.get("desc", "")}，三合成势产生成局之象',
            })
    return findings


# ───────────────────── 3. 化象 ─────────────────────

def huaxiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
) -> List[Dict]:
    """化象原则：合化成功后的新象。

    天干合化（type='合化'）-> 化气五行之象（如甲己化土=中央/信用/地产之象）；
    杀印相生（type='杀印相生'）-> 化杀为印、化印为身之化象（印权）。

    Returns:
        化象记录列表。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    for a in wa:
        t = a.get('type', '')
        if t == '合化':
            desc = a.get('desc', '')
            # 解析化气五行（desc 含「合化X」）
            hua_wx = ''
            for wx in ('木', '火', '土', '金', '水'):
                if f'化{wx}' in desc:
                    hua_wx = wx
                    break
            cat = _wx_to_shishen_cat(day_gan, hua_wx) if hua_wx else ''
            findings.append({
                'principle': '化象',
                'subject': f'合化{hua_wx}（化气之象）' if hua_wx else '合化之象',
                'domain': cat,
                'pillar': PILLAR_NAMES_CN[PILLAR_KEYS.index(_pos_pillar(a.get('to_pos', '')))] if _pos_pillar(a.get('to_pos', '')) in PILLAR_KEYS else '',
                'pos': a.get('to_pos', ''),
                'evidence': [desc],
                'locked': True,
                'desc': f'{desc}，合化成功产生{hua_wx or ""}气新象' + (f'（对日主为{cat}）' if cat else ''),
            })
        elif t == '杀印相生':
            findings.append({
                'principle': '化象',
                'subject': '化杀为印（印权）',
                'domain': '印',
                'pillar': PILLAR_NAMES_CN[PILLAR_KEYS.index(_pos_pillar(a.get('to_pos', '')))] if _pos_pillar(a.get('to_pos', '')) in PILLAR_KEYS else '',
                'pos': a.get('to_pos', ''),
                'evidence': [a.get('desc', '')],
                'locked': True,
                'desc': f'{a.get("desc", "")}，化杀为印、化印为身，产生印权之化象',
            })

    # ④ 五行相生化象（生克化象）：两五行相生，化出行业之复合象。
    # 段氏《高级篇》6.2（三）：化象是两个以上的象通过生/会/合转化成全新之象，
    # 最常见为五行相生之化象。阴木(卯)生火->丝线化为织物->纺织/服装/刺绣/布匹；
    # 阳木(寅)生火->木材化为器物->家具/家私/装潢；金生水(庚壬/辛癸)->金融/法律/
    # 会计/科技；水生木(壬甲/癸乙)->文化/教育/艺术。此化象独立于 primary_work 的
    # type 标签（不耦合 work_types），以原局五行相生之组合为准（解耦象法对做功
    # type 的依赖）。
    _gan_set = {g for g in gans if g}
    _zhi_set = {z for z in zhis if z}
    _has_fire_gan = ('丙' in _gan_set or '丁' in _gan_set)
    # 木生火：阴木(卯)为丝线布匹、阳木(寅)为木材，象分阴阳；卯优先于寅
    if '卯' in _zhi_set and _has_fire_gan:
        findings.append({
            'principle': '化象',
            'subject': '阴木化火（纺织/服装）',
            'domain': '食艺',
            'pillar': '',
            'pos': '',
            'evidence': ['卯(阴木·丝线布匹)生火(丙丁·光彩)，化象为纺织/服装/刺绣/布匹'],
            'locked': False,
            'desc': '阴木(卯)生火，丝线经加工化为织物，化象为纺织/服装/刺绣/布匹',
        })
    elif '寅' in _zhi_set and _has_fire_gan:
        findings.append({
            'principle': '化象',
            'subject': '阳木化火（家具/装潢）',
            'domain': '食艺',
            'pillar': '',
            'pos': '',
            'evidence': ['寅(阳木·木材)生火(丙丁)，化象为家具/家私/装潢'],
            'locked': False,
            'desc': '阳木(寅)生火，木材加工化为器物，化象为家具/家私/装潢',
        })
    # 金生水（庚壬/辛癸）：金融/法律/会计/科技
    if ({'庚', '壬'} <= _gan_set) or ({'辛', '癸'} <= _gan_set):
        findings.append({
            'principle': '化象',
            'subject': '金生水（金融/法律）',
            'domain': '财',
            'pillar': '',
            'pos': '',
            'evidence': ['金(庚壬/辛癸)生水，金水相涵，化象为金融/法律/会计/科技'],
            'locked': False,
            'desc': '金生水，金水相涵，化象为金融/法律/会计/科技',
        })
    # 水生木（壬甲/癸乙）：文化/教育/艺术
    if ({'壬', '甲'} <= _gan_set) or ({'癸', '乙'} <= _gan_set):
        findings.append({
            'principle': '化象',
            'subject': '水生木（文化/教育）',
            'domain': '印文',
            'pillar': '',
            'pos': '',
            'evidence': ['水(壬甲/癸乙)生木，水木相生，化象为文化/教育/艺术'],
            'locked': False,
            'desc': '水生木，水木相生，化象为文化/教育/艺术',
        })
    return findings


# ───────────────────── 4. 墓象 ─────────────────────

def muxiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    muku_result: Optional[Dict] = None,
) -> List[Dict]:
    """墓象原则：入墓/开库之物象变化。

    墓库五行对日主为某十神（财/官/印/食伤），其开闭/入墓改变物象：
      开库 -> 墓中之物复出（开财库=发财、开官库=掌权/出狱、开印库=得印文）；
      闭库/墓库 -> 墓中之物被收藏/封存（财入库=守财储蓄、官入库=封存/狱象）。
    入墓（tomb_relations）-> 某五行/十神入墓=被收藏/管理/困住之象。

    Returns:
        墓象记录列表。
    """
    findings: List[Dict] = []
    if not (day_gan and len(zhis) == 4):
        return findings
    mu = _ensure_muku(gans or [], zhis, muku_result)
    day_wx = GAN_WX.get(day_gan, '')

    # 墓库开闭
    for tomb in mu.get('tombs', []) or []:
        z = tomb.get('zhi', '')
        status = tomb.get('status', '')
        # 墓库所收五行 -> 对日主十神大类
        cats = []
        for wx in TOMB_MAP.get(z, []):
            c = _wx_to_shishen_cat(day_gan, wx)
            if c and c not in cats:
                cats.append(c)
        cat_str = '、'.join(cats)
        pillar = tomb.get('pillar', '')
        if status == '开库':
            subject = f'开{cat_str}库' if cat_str else '开库'
            desc = f'{pillar}{z}开库，墓中{cat_str or "之物"}复出'
            if '财' in cats:
                desc += '（发财之象）'
            elif '官杀' in cats:
                desc += '（掌权/出狱之象）'
            elif '印' in cats:
                desc += '（得印文之象）'
        elif status == '闭库':
            subject = f'闭{cat_str}库' if cat_str else '闭库'
            desc = f'{pillar}{z}闭库，墓中{cat_str or "之物"}被困'
        else:  # 墓库（未开未闭）
            subject = f'{cat_str}入库' if cat_str else '入库'
            desc = f'{pillar}{z}墓库收藏{cat_str or "之物"}'
            if '财' in cats:
                desc += '（守财储蓄之象）'
            elif '官杀' in cats:
                desc += '（封存/狱象）'
        findings.append({
            'principle': '墓象',
            'subject': subject,
            'domain': cats[0] if cats else '',
            'pillar': pillar,
            'pos': '',
            'evidence': [tomb.get('desc', '')],
            'locked': True,
            'desc': desc,
        })

    # 入墓关系
    for rel in mu.get('tomb_relations', []) or []:
        # muku 的 tomb_relations from/to 可能为 {zhi, pillar} 字典，须取 zhi
        def _zhi_of(v):
            if isinstance(v, dict):
                return v.get('zhi', '')
            return v or ''
        tombed = rel.get('tombed_zhi', '') or _zhi_of(rel.get('from', ''))
        tomb_z = rel.get('tomb_zhi', '') or _zhi_of(rel.get('to', ''))
        if not tombed or not tomb_z:
            continue
        tombed_wx = ZHI_WX.get(tombed, '')
        cat = _wx_to_shishen_cat(day_gan, tombed_wx) if tombed_wx else ''
        subject = f'{cat}入墓' if cat else '入墓'
        desc = f'{tombed}({cat or "之物"})入{tomb_z}墓'
        if cat == '财':
            desc += '（财被收藏/守财之象）'
        elif cat == '官杀':
            desc += '（官被收/封存之象）'
        findings.append({
            'principle': '墓象',
            'subject': subject,
            'domain': cat,
            'pillar': '',
            'pos': '',
            'evidence': [rel.get('desc', f'{tombed}入{tomb_z}墓')],
            'locked': True,
            'desc': desc,
        })
    return findings


# ───────────────────── 5. 制象 ─────────────────────

def zhixiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
) -> List[Dict]:
    """制象原则：制住了才有象（制官得官、制财得财）。

    制用动作（冲/克/穿/刑/破/合制）成立 -> 制方制被制方，得被制方之象。
    主位(日时)制宾位(年月) = 自己制外物 = 得（制财得财、制官得官）；
    宾位制主位 = 外物制自己 = 失/被制（破财、被管）。

    Returns:
        制象记录列表，含 direction(主制宾/宾制主)与所得 subject。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    seen: Set[Tuple[str, str, str]] = set()  # (to_pos, cat, direction) 去重

    for a in wa:
        t = a.get('type', '')
        if t not in _ZHI_CONTROL and t not in _HE_CONTROL:
            continue
        from_pos, to_pos = a.get('from_pos', ''), a.get('to_pos', '')
        if not from_pos or not to_pos:
            continue
        from_zhu = _is_zhu(from_pos)
        to_zhu = _is_zhu(to_pos)
        # 被制方 = to（受方）；其十神为所得/所失之物
        controlled_cats = list({
            _shishen_cat(ss) for ss in _shishen_list_of_pos(to_pos, day_gan, gans, zhis)
            if ss
        })
        if not controlled_cats:
            continue
        # 方向：主制宾=得，宾制主=失。同侧（主制主/宾制宾）=内部做功，中性得。
        if from_zhu and not to_zhu:
            direction = '主制宾'
            verb = '得'
        elif to_zhu and not from_zhu:
            direction = '宾制主'
            verb = '失/被制'
        else:
            direction = '同侧制'
            verb = '得（内部做功）'

        for cat in controlled_cats:
            if (to_pos, cat, direction) in seen:
                continue  # 同一对（被制位+十神+方向）多关系类型只记一次
            seen.add((to_pos, cat, direction))
            subject_map = {
                '财': '财', '官杀': '官', '印': '印文', '食伤': '才艺', '比劫': '比劫',
            }
            subj = subject_map.get(cat, cat)
            findings.append({
                'principle': '制象',
                'subject': f'{verb}{subj}',
                'domain': cat,
                'pillar': PILLAR_NAMES_CN[PILLAR_KEYS.index(_pos_pillar(to_pos))] if _pos_pillar(to_pos) in PILLAR_KEYS else '',
                'pos': to_pos,
                'direction': direction,
                'evidence': [a.get('desc', '')],
                'locked': True,
                'desc': f'{a.get("desc", "")}，{direction}，制{cat}{verb}{subj}之象',
            })
    return findings


# ───────────────────── 6. 带象（带帽）─────────────────────

def daixiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
) -> List[Dict]:
    """带象原则（带帽）：天干（帽）+地支藏干（身）十神组合产生复合象。

    逐柱取帽=天干十神大类、身=地支各藏干十神大类（本气/中气/余气皆查，本气在先），
    查 _DAIMAO_COMBO 表（命名「身带帽帽」，身=地支藏干在前、帽=天干在后）：
      印带官帽（官杀帽+印身）-> 职权；官带财帽（财帽+官杀身）-> 财权；
      官带印帽、财带食伤帽、财带官帽、财坏印、官带比劫帽 等。
    一柱可能多藏干各成带帽（如丑藏己辛癸，官杀帽遇辛印身=印带官帽、遇己财身=财坏印），
    本气命中列前。

    Returns:
        带象记录列表。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings

    qi_label = {0: '本气', 1: '中气', 2: '余气'}
    for i, pk in enumerate(PILLAR_KEYS):
        gan, zhi = gans[i], zhis[i]
        if not gan or not zhi:
            continue
        mao_ss = _compute_shishen(day_gan, gan)
        mao_cat = _shishen_cat(mao_ss)
        if not mao_cat:
            continue
        for order, (cg, qi) in enumerate(get_canggan_mangpai(zhi)):
            shen_ss = _compute_shishen(day_gan, cg)
            shen_cat = _shishen_cat(shen_ss)
            if not shen_cat or shen_cat == mao_cat:
                continue
            combo = _DAIMAO_COMBO.get((mao_cat, shen_cat))
            if not combo:
                continue
            findings.append({
                'principle': '带象',
                'subject': combo['subject'],
                'domain': mao_cat,
                'pillar': PILLAR_NAMES_CN[i],
                'pos': f'{pk}_gan',
                'mao': mao_ss,            # 帽（天干十神）
                'shen': shen_ss,          # 身（命中藏干十神）
                'shen_qi': qi_label.get(order, qi),  # 身气位（本/中/余气）
                'combo': combo['name'],
                'evidence': [f'帽={mao_ss}({mao_cat})坐身={shen_ss}({shen_cat}·{qi_label.get(order, qi)})'],
                'locked': True,
                'desc': f'{PILLAR_NAMES_CN[i]}柱{combo["name"]}（身{qi_label.get(order, qi)}{shen_ss}）：{combo["desc"]}',
            })
    return findings


# ───────────────────── 7. 借象 ─────────────────────

def jiexiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
) -> List[Dict]:
    """借象原则：借邻柱/六合/通禄之象。

    三种借象：
      ① 借邻柱：某柱缺某十神大类，相邻柱有之 -> 借邻柱之象补足；
      ② 借六合：六合之支互借对方之象（如子丑合，互借水/库象）；
      ③ 借通禄：天干借其禄位地支之象（禄为原身，天干通禄取象，LU 表）。

    Returns:
        借象记录列表。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings

    # ① 借邻柱：逐柱取本柱天干十神大类集合，与前/后邻柱比对，借所缺大类
    pillar_cats: List[Set[str]] = []
    for i, pk in enumerate(PILLAR_KEYS):
        cats: Set[str] = set()
        ss = _compute_shishen(day_gan, gans[i])
        c = _shishen_cat(ss)
        if c:
            cats.add(c)
        # 含藏干十神大类
        for cg, _ in get_canggan_mangpai(zhis[i]):
            c2 = _shishen_cat(_compute_shishen(day_gan, cg))
            if c2:
                cats.add(c2)
        pillar_cats.append(cats)

    neighbor_pairs = [(0, 1), (1, 2), (2, 3)]  # 年-月、月-日、日-时
    for a_i, b_i in neighbor_pairs:
        a_only = pillar_cats[b_i] - pillar_cats[a_i]  # a 缺而 b 有
        b_only = pillar_cats[a_i] - pillar_cats[b_i]  # b 缺而 a 有
        for cat in a_only:
            if cat in ('比劫',):
                continue  # 比劫为同我，不构成借象
            findings.append({
                'principle': '借象',
                'subject': f'借{cat}象',
                'domain': cat,
                'pillar': PILLAR_NAMES_CN[a_i],
                'pos': f'{PILLAR_KEYS[a_i]}_gan',
                'borrow_from': PILLAR_NAMES_CN[b_i],
                'kind': '借邻柱',
                'evidence': [f'{PILLAR_NAMES_CN[a_i]}柱缺{cat}，借邻柱{PILLAR_NAMES_CN[b_i]}之{cat}象'],
                'locked': False,
                'desc': f'{PILLAR_NAMES_CN[a_i]}柱借邻柱{PILLAR_NAMES_CN[b_i]}之{cat}象',
            })
        for cat in b_only:
            if cat in ('比劫',):
                continue
            findings.append({
                'principle': '借象',
                'subject': f'借{cat}象',
                'domain': cat,
                'pillar': PILLAR_NAMES_CN[b_i],
                'pos': f'{PILLAR_KEYS[b_i]}_gan',
                'borrow_from': PILLAR_NAMES_CN[a_i],
                'kind': '借邻柱',
                'evidence': [f'{PILLAR_NAMES_CN[b_i]}柱缺{cat}，借邻柱{PILLAR_NAMES_CN[a_i]}之{cat}象'],
                'locked': False,
                'desc': f'{PILLAR_NAMES_CN[b_i]}柱借邻柱{PILLAR_NAMES_CN[a_i]}之{cat}象',
            })

    # ② 借六合：六合之支互借象
    for i in range(4):
        for j in range(i + 1, 4):
            z1, z2 = zhis[i], zhis[j]
            if not z1 or not z2:
                continue
            if (z1, z2) in LIU_HE or (z2, z1) in LIU_HE:
                for src, tgt, si, ti in [(z1, z2, i, j), (z2, z1, j, i)]:
                    src_wx = ZHI_WX.get(src, '')
                    cat = _wx_to_shishen_cat(day_gan, src_wx) if src_wx else ''
                    if not cat or cat == '比劫':
                        continue
                    findings.append({
                        'principle': '借象',
                        'subject': f'借{cat}象',
                        'domain': cat,
                        'pillar': PILLAR_NAMES_CN[ti],
                        'pos': f'{PILLAR_KEYS[ti]}_zhi',
                        'borrow_from': f'{PILLAR_NAMES_CN[si]}支{src}',
                        'kind': '借六合',
                        'evidence': [f'{src}{tgt}六合，{PILLAR_NAMES_CN[ti]}支{tgt}借{src}之{cat}象'],
                        'locked': False,
                        'desc': f'{PILLAR_NAMES_CN[ti]}支{tgt}借六合{src}之{cat}象',
                    })

    # ③ 借通禄：天干借其禄位地支之象（禄为原身）
    for i, pk in enumerate(PILLAR_KEYS):
        gan = gans[i]
        if not gan:
            continue
        lu_zhi = LU.get(gan, '')
        if not lu_zhi:
            continue  # 四库无禄，无通禄
        # 禄位是否在他柱地支
        for j, z in enumerate(zhis):
            if j == i or z != lu_zhi:
                continue
            lu_wx = ZHI_WX.get(lu_zhi, '')
            cat = _wx_to_shishen_cat(day_gan, lu_wx)
            findings.append({
                'principle': '借象',
                'subject': f'通禄借{cat or "比劫"}象',
                'domain': cat or '比劫',
                'pillar': PILLAR_NAMES_CN[i],
                'pos': f'{pk}_gan',
                'borrow_from': f'{PILLAR_NAMES_CN[j]}支{lu_zhi}（{gan}之禄）',
                'kind': '借通禄',
                'evidence': [f'{PILLAR_NAMES_CN[i]}干{gan}通禄于{PILLAR_NAMES_CN[j]}支{lu_zhi}，借禄之原身象'],
                'locked': False,
                'desc': f'{PILLAR_NAMES_CN[i]}干{gan}通禄{lu_zhi}（在{PILLAR_NAMES_CN[j]}柱），借禄之原身象',
            })

    # ④ 借同五行（副宫借象）：同五行阴阳字（寅卯/巳午/申酉/亥子）互为副宫，
    # 一方在宫位、另一方在他柱，可借同气之象。段氏《高级篇》6.5（二）：同五行
    # 而阴阳不同者（如寅与卯、巳与午）犹如兄弟姊妹，气息相通；夫妻宫/子女宫
    # 之字其同五行阴阳字现于他柱，即为该宫"副宫"，象可互借。此关系独立于禄原
    # 互通（③）与六合（②），补足借象之同气维度。
    _tong_wx_pairs = [('寅', '卯'), ('巳', '午'), ('申', '酉'), ('亥', '子')]
    for _a, _b in _tong_wx_pairs:
        _a_pos = [i for i, z in enumerate(zhis) if z == _a]
        _b_pos = [i for i, z in enumerate(zhis) if z == _b]
        if not _a_pos or not _b_pos:
            continue
        _wx = ZHI_WX.get(_a, '')
        _cat = _wx_to_shishen_cat(day_gan, _wx) if _wx else ''
        for _ai in _a_pos:
            for _bi in _b_pos:
                if _ai == _bi:
                    continue
                findings.append({
                    'principle': '借象',
                    'subject': f'同五行借{_cat or "比劫"}象',
                    'domain': _cat or '比劫',
                    'pillar': PILLAR_NAMES_CN[_ai],
                    'pos': f'{PILLAR_KEYS[_ai]}_zhi',
                    'borrow_from': f'{PILLAR_NAMES_CN[_bi]}支{_b}',
                    'kind': '借同五行',
                    'evidence': [f'{_a}{_b}同五行(副宫)，{PILLAR_NAMES_CN[_ai]}支{_a}借{PILLAR_NAMES_CN[_bi]}支{_b}之同气象'],
                    'locked': False,
                    'desc': f'{PILLAR_NAMES_CN[_ai]}支{_a}借同五行{_b}（{PILLAR_NAMES_CN[_bi]}柱）之副宫象',
                })
    return findings


# ───────────────────── 8. 换象（制尽则换，主从易位）─────────────────────

def huanxiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
    zb_result: Optional[Dict] = None,
) -> List[Dict]:
    """换象原则（高级篇 6.3）：制尽则换，主从易位。

    当制方以绝对优势将被制方彻底制伏（制尽），被制方便失去独立本性，其象意、
    身份、价值转换归属于制方——「制方换得被制方之象」。如比劫制财（制尽），
    财便为比劫之财，主大富；制官杀（制尽），制方换得官象，主大贵。
    （源文 8481-8806：「制尽方能把象换，胜者为主败者贱；制方换得败者象，
      败者化为胜者钱」。）

    门槛=制尽：制方成党成势、被制方孤立无援被完全控制。复用
    zeishen_bushen.detect_zeishen_bushen 的 jing_zhi='净'（用神与其原神俱制、
    无残存=制之干净=制尽）为判据，并兼采 detect_bao_zhi（包制围猎=制尽之一种）
    与 _party_strength/_CHENG_DANG 党势。本函数为象意层：只产出换象之象意，
    不做功量加分（功量层见 gongliang）。

    制伏三档（源文 8506-8513）：制尽→可换象；制伤（部分制）→不可换象，
    仅主得失；制动（对抗）→不可换象，主争斗消耗。故仅 jing_zhi='净'方换象。

    Returns:
        换象记录列表，含 subject/domain/direction/evidence/desc。
        direction ∈ {'主制宾(我得)','宾制主(失)','围制(命局掌控)'}。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []

    # 制尽判据：贼神捕神净制（用神+原神俱制、无残存）。
    # 修批A②（R5 block-3）：净制口径单源化——优先消费调用方（engine）已算的
    # zeishen_bushen 结果；缺省自算须以 zuogong_confirm 标记后的 work_actions
    # 为准（auxiliary 过滤在 detect_zeishen_bushen 内生效）。裸 detect_relations
    # wa 未标 auxiliary，会把宾位互制塞入制局目标集 → 原神同制误净（假「净」，
    # 蒋介石书锚「制之不净达不到四层功」，zeishen_bushen.py:606-608）。
    bao = detect_bao_zhi(gans, zhis, day_gan)
    if zb_result is not None:
        zb = zb_result.get('zeishen_bushen') or {}
        bao = zb_result.get('bao_zhi') or bao
    else:
        from mangpai.subjective.zuogong_confirm import analyze_zuogong
        zg = analyze_zuogong(day_gan, zhis[2], gans[0], zhis[0],
                             gans[1], zhis[1], gans[3], zhis[3])
        clian = detect_chong_lian(zhis, gans)
        zb = detect_zeishen_bushen(
            day_gan, gans, zhis,
            work_actions=zg.get('work_actions') or [],
            bao_zhi=bao, chong_lian=clian,
        )
    jing_zhi = zb.get('jing_zhi', '')
    zeishen_wx = zb.get('zeishen_wx', '')
    bushen_wx = zb.get('bushen_wx', '')
    if jing_zhi != '净' or not zeishen_wx:
        return findings  # 未制尽（制伤/制动/无制）→不换象

    # 被制方（贼神）五行 → 对日主十神大类 → 制方换得此象
    zeishen_cat = _wx_to_shishen_cat(day_gan, zeishen_wx)
    if not zeishen_cat:
        return findings
    subject_map = {
        '财': ('换财象', '财', '大富（制方换得财象，败者化为胜者钱）'),
        '官杀': ('换官象', '官权', '大贵（制方换得官杀象，掌权）'),
        '印': ('换印象', '印文', '制方换得印象（权管文书/单位）'),
        '食伤': ('换食伤象', '食艺', '制方换得食伤象（权管技艺）'),
        '比劫': ('换比劫象', '比劫', '制方换得比劫象（聚党）'),
    }
    subj, domain, hint = subject_map.get(zeishen_cat, (f'换{zeishen_cat}象', zeishen_cat, '制方换得被制方之象'))

    # 方向：于 work_actions 中找一条 捕神五行→贼神五行 的制用动作，定主宾
    direction = '围制(命局掌控)'  # 包制/无明确单柱方向时默认命局掌控
    if bao and bao.get('detected'):
        direction = '围制(命局掌控)'
    else:
        for a in wa:
            if a.get('type') not in (_ZHI_CONTROL | _HE_CONTROL):
                continue
            fpos, tpos = a.get('from_pos', ''), a.get('to_pos', '')
            f_elem = _elem_of_pos(fpos, gans, zhis)
            t_elem = _elem_of_pos(tpos, gans, zhis)
            if (_wx_of(f_elem) == bushen_wx) and (_wx_of(t_elem) == zeishen_wx):
                if _is_zhu(fpos) and not _is_zhu(tpos):
                    direction = '主制宾(我得)'
                elif _is_zhu(tpos) and not _is_zhu(fpos):
                    direction = '宾制主(失)'
                else:
                    direction = '同侧制(内部)'
                break

    findings.append({
        'principle': '换象',
        'subject': subj,
        'domain': domain,
        'pillar': '',
        'pos': '',
        'bushen_wx': bushen_wx,
        'zeishen_wx': zeishen_wx,
        'direction': direction,
        'evidence': [
            f'制尽：捕神「{bushen_wx}」党势成势、贼神「{zeishen_wx}」孤立无援被净制',
            zb.get('reason', ''),
        ],
        'locked': True,
        'desc': f'制尽则换：制方（{bushen_wx}）制尽被制方（{zeishen_wx}={zeishen_cat}），'
                f'主从易位，制方换得{zeishen_cat}象，{direction}，{hint}',
    })
    return findings


# ───────────────────── 9. 局象（全局氛围象）─────────────────────

def juxiang(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
) -> List[Dict]:
    """局象原则（高级篇 6.6 + 2.6）：全局干支组合形成的宏观氛围象。

    五类局象（源文 9509-9526）：
      1. 包局之象——某五行/十神/干支出现≥2次，包围/拱卫/困锁日主或核心宫位；
      2. 夹局之象——核心位置被年时或月时两柱相同/相生干支夹在中间（消费
         zuogong_detect.detect_jia_ju 的纯结构检测）；
      3. 全阴全阳之象——八字干支皆阴或皆阳；
      4. 一方专旺之象——某五行极其强旺成专旺格（稼穑/曲直/炎上/从革/润下）；
      5. 寒暖燥湿之象——金水过重为寒湿、木火过重为暖燥。

    本函数为象意层（源文 9562-9568「局象定层次，做功定成败」）：只产出全局
    氛围象意，不做功量加分（功量层包局+1 见 gongliang，与本层并行不悖）。

    Returns:
        局象记录列表，含 type/qi_xiang(氛围定性)/domain/evidence/desc。
    """
    findings: List[Dict] = []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return findings

    day_wx = GAN_WX.get(day_gan, '')

    # ── 五行计数（天干+地支主气）──
    wx_count: Dict[str, int] = {wx: 0 for wx in ('木', '火', '土', '金', '水')}
    for g in gans:
        w = GAN_WX.get(g, '')
        if w:
            wx_count[w] += 1
    for z in zhis:
        w = ZHI_WX.get(z, '')
        if w:
            wx_count[w] += 1
    total = sum(wx_count.values())

    # ── 1. 包局之象 ──
    # 干支包：同地支出现在年+时（外层包内层）；或同地支≥3柱。
    # 五行包：同五行在年+时（外夹内）；或同五行≥3柱。
    # 十神包：同十神大类≥3柱（透干+本气）。
    zhi_at = {pk: zhis[i] for i, pk in enumerate(PILLAR_KEYS)}
    # 干支包（年时同支 / 三柱同支）
    for z in set(z for z in zhis if z):
        pillars_with = [PILLAR_KEYS[i] for i, zz in enumerate(zhis) if zz == z]
        if len(pillars_with) >= 3 or (set(pillars_with) >= {'year', 'hour'} and len(pillars_with) >= 2):
            findings.append({
                'principle': '局象', 'type': '包局',
                'qi_xiang': '干支包局',
                'domain': _domains_of_ganzhi('', z).pop() if _domains_of_ganzhi('', z) else '',
                'evidence': [f'地支{z}现于{"、".join(pillars_with)}柱，形成包围之势'],
                'desc': f'地支{z}多柱重复，形成干支包局之象（包围/拱卫/困锁）',
            })
    # 五行包（年时同五行外夹 / 三柱同五行）
    zhi_wx_at = {pk: ZHI_WX.get(zhis[i], '') for i, pk in enumerate(PILLAR_KEYS)}
    for w, c in wx_count.items():
        pillars_w = [pk for pk, ww in zhi_wx_at.items() if ww == w]
        if c >= 3 or (set(pillars_w) >= {'year', 'hour'} and len(pillars_w) >= 2):
            findings.append({
                'principle': '局象', 'type': '包局',
                'qi_xiang': '五行包局',
                'domain': _wx_to_shishen_cat(day_gan, w),
                'evidence': [f'{w}五行现{c}字（{ "、".join(pillars_w) }柱），包围日主'],
                'desc': f'{w}五行多字成包局之象',
            })
    # 十神包（同十神大类≥3柱）
    pillar_cats: List[Set[str]] = []
    for i, pk in enumerate(PILLAR_KEYS):
        cats: Set[str] = set()
        ss = _compute_shishen(day_gan, gans[i])
        c = _shishen_cat(ss)
        if c:
            cats.add(c)
        for cg, _ in get_canggan_mangpai(zhis[i]):
            c2 = _shishen_cat(_compute_shishen(day_gan, cg))
            if c2:
                cats.add(c2)
        pillar_cats.append(cats)
    for cat in ('官杀', '财', '印', '食伤', '比劫'):
        pillars_cat = [PILLAR_KEYS[i] for i, cs in enumerate(pillar_cats) if cat in cs]
        if len(pillars_cat) >= 3:
            findings.append({
                'principle': '局象', 'type': '包局',
                'qi_xiang': '十神包局',
                'domain': cat,
                'evidence': [f'{cat}现于{"、".join(pillars_cat)}柱（≥3），十神包局'],
                'desc': f'{cat}十神多柱成包局之象',
            })

    # ── 2. 夹局之象（消费 detect_jia_ju 纯结构检测）──
    try:
        jj = detect_jia_ju(
            day_gan, zhis[PILLAR_KEYS.index('day')],
            gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3],
        )
    except Exception:
        jj = {'jia_ju': []}
    for j in jj.get('jia_ju', []):
        subtype = j.get('subtype', '夹局')
        findings.append({
            'principle': '局象', 'type': '夹局',
            'qi_xiang': subtype,
            'domain': '',
            'wrap_pillars': j.get('wrap_pillars', []),
            'wrapped_pillars': j.get('wrapped_pillars', []),
            'evidence': [j.get('desc', '')],
            'desc': f'夹局之象：{j.get("desc","")}（左右同气夹中间，机遇/压力并存）',
        })

    # ── 3. 全阴全阳之象 ──
    all_chars = list(gans) + list(zhis)
    all_yang = all(c in _YANG_GANS or c in _YANG_ZHIS for c in all_chars) and all_chars
    all_yin = all((c not in _YANG_GANS and c not in _YANG_ZHIS) for c in all_chars) and all_chars
    if all_yang:
        findings.append({
            'principle': '局象', 'type': '全阳',
            'qi_xiang': '纯阳之局',
            'domain': '',
            'evidence': ['八字干支皆阳'],
            'desc': '全阳之象：纯阳之局，主性格刚烈、六亲有损、运势极端',
        })
    elif all_yin:
        findings.append({
            'principle': '局象', 'type': '全阴',
            'qi_xiang': '纯阴之局',
            'domain': '',
            'evidence': ['八字干支皆阴'],
            'desc': '全阴之象：纯阴之局，主性格阴柔、多虑、运势偏沉',
        })

    # ── 4. 一方专旺之象 ──
    zhuan_wang_name = {'土': '稼穑', '木': '曲直', '火': '炎上', '金': '从革', '水': '润下'}
    for w, c in wx_count.items():
        if c >= 6 and total:  # ≥6/8 字同五行→专旺
            findings.append({
                'principle': '局象', 'type': '专旺',
                'qi_xiang': f'{zhuan_wang_name.get(w, w)}格',
                'domain': _wx_to_shishen_cat(day_gan, w),
                'evidence': [f'{w}五行现{c}/{total}字，一方专旺'],
                'desc': f'一方专旺之象：{w}极旺成{zhuan_wang_name.get(w, "专旺")}格',
            })

    # ── 5. 寒暖燥湿之象 ──
    han_wx = wx_count.get('金', 0) + wx_count.get('水', 0)
    nuan_wx = wx_count.get('木', 0) + wx_count.get('火', 0)
    if han_wx >= 5:
        findings.append({
            'principle': '局象', 'type': '寒湿',
            'qi_xiang': '金水寒湿',
            'domain': '',
            'evidence': [f'金水合{han_wx}/{total}字，寒湿偏重'],
            'desc': '寒暖燥湿之象：金水过重为寒湿，主性情冷峻、健康偏寒、需火调候',
        })
    elif nuan_wx >= 5:
        findings.append({
            'principle': '局象', 'type': '暖燥',
            'qi_xiang': '木火暖燥',
            'domain': '',
            'evidence': [f'木火合{nuan_wx}/{total}字，暖燥偏重'],
            'desc': '寒暖燥湿之象：木火过重为暖燥，主性情急躁、健康偏热、需水调候',
        })

    return findings


# ───────────────────── 聚合 ─────────────────────

def analyze_xiangfa_ops(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    muku_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    zeishen_result: Optional[Dict] = None,
) -> Dict:
    """象法九原则操作层聚合（中级七原则 + 高级换象/局象）。

    支持两种签名：旧位置参数（day_gan/gans/zhis），或首个参数为 Pillars 对象。
    analyze_xiangfa_ops(pillars) 等价展开四柱。

    Args:
        day_gan: 日干（或 Pillars 对象）
        gans: 四柱天干 [year, month, day, hour]
        zhis: 四柱地支 [year, month, day, hour]
        relations: detect_relations 输出（缺省自调）
        muku_result: analyze_muku 输出（缺省自调）
        shensha_result: compute_shensha_ext 输出（缺省自调）
        zeishen_result: analyze_zeishen_bushen 输出（缺省时 huanxiang 以
            zuogong_confirm 标记后的 work_actions 自算；修批A② 净制口径单源化）

    Returns:
        {
          'gongxiang': [...],  # 共象锁定
          'hexiang': [...],    # 合象
          'huaxiang': [...],   # 化象
          'muxiang': [...],    # 墓象
          'zhixiang': [...],   # 制象
          'daixiang': [...],   # 带象（带帽）
          'jiexiang': [...],   # 借象
          'huanxiang': [...],  # 换象（高级·制尽则换）
          'juxiang': [...],    # 局象（高级·全局氛围）
          'all_findings': [...],  # 全部象（按原则序拼接）
          'locked_subjects': [str],  # 锁定的事物集合（locked=True）
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        if not day_gan:
            day_gan = p.day_gan
        else:
            day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []

    # 缺省自调客观检测（共象需神煞，合/化/制需 relations，墓象需 muku）
    if shensha_result is None and day_gan and len(zhis) == 4:
        try:
            shensha_result = compute_shensha_ext(day_gan, zhis)
        except Exception:
            shensha_result = None

    gong = gongxiang(day_gan, gans, zhis, shensha_result)
    he = hexiang(day_gan, gans, zhis, relations)
    hua = huaxiang(day_gan, gans, zhis, relations)
    mu = muxiang(day_gan, gans, zhis, muku_result)
    zhi = zhixiang(day_gan, gans, zhis, relations)
    dai = daixiang(day_gan, gans, zhis)
    jie = jiexiang(day_gan, gans, zhis)
    huan = huanxiang(day_gan, gans, zhis, relations, zb_result=zeishen_result)
    ju = juxiang(day_gan, gans, zhis, relations)

    all_findings = gong + he + hua + mu + zhi + dai + jie + huan + ju
    locked_subjects: List[str] = []
    for f in all_findings:
        if f.get('locked') and f.get('subject'):
            s = f['subject']
            if s not in locked_subjects:
                locked_subjects.append(s)

    return {
        'gongxiang': gong,
        'hexiang': he,
        'huaxiang': hua,
        'muxiang': mu,
        'zhixiang': zhi,
        'daixiang': dai,
        'jiexiang': jie,
        'huanxiang': huan,
        'juxiang': ju,
        'xiangfa_fallback': xiangfa_fallback(day_gan, gans, zhis, relations),
        'all_findings': all_findings,
        'locked_subjects': locked_subjects,
    }


# ──────────────────────────────────────────────────────────────────────
# 象法回退分支（K4）
# ──────────────────────────────────────────────────────────────────────
# 理论来源：
#   《段氏理象学》7960-8000：做功不成立时切象法——
#     例一 庚己甲己/子卯辰巳：杀星虚透并无做功，应用带象原理，
#       「庚子年柱之象谓印带杀帽，其印星子水这里表示权力，子通于辰墓，
#         说明辰是权力之库，甲坐在辰地，所以他拥有权力」；
#     例二 丁戊戊戊/酉申申午（张之洞）：金重难制效率不高，归于「伤官诀」——
#       「土金伤官成局，又非常纯粹，配印午火，故得重权」；
#     例三 壬壬癸甲/午寅卯寅：看不出任何做功，「然有水木伤官成局，局象也纯，
#       并非发财之命，而是一位高官」。
#   《段氏理象学》7409 + 《初级命理学》干支互通（2174-2190）：
#     连体（连根之体不可制，制之伤身体及寿命）；丙戊一家/丁己一家（同禄于巳午，
#     半通禄为一家看）；半禄关系（丁未、癸丑；乙见辰、丁见戌）。
#   《高级内容篇》层功法则5案例（辛丑壬辰辛未戊戌：丑未冲+辰戌冲，开两库）：
#     连墓做功（两墓库相互作用开库）。

# 连体日柱（连根之体，书列 + 干支同气/支本气生干规则并集）
_LIANTI_PILLARS = {
    '丁巳', '丙午', '丁未', '丙戌',  # 火（连根/得强根，书：不能被坏）
    '乙亥', '乙卯', '甲寅', '甲辰', '乙未',  # 连根木
    '庚申', '辛酉', '辛丑',  # 连根金
}
# 半禄关系（同柱）：丁未、癸丑；交叉：乙见辰、丁见戌
_BANLU_PILLARS = {'丁未', '癸丑'}
_BANLU_CROSS = {('乙', '辰'), ('丁', '戌')}
# 一家（同禄）：丙戊同禄于巳、丁己同禄于午 → 半通禄为一家看
_YIJIA_PAIRS = [('丙', '戊', '巳'), ('丁', '己', '午')]


def _pillar_gan_cat(day_wx: str, gan: str) -> str:
    w = GAN_WX.get(gan, '')
    if not day_wx or not w:
        return ''
    if w == day_wx:
        return '比劫'
    if WX_SHENG.get(w) == day_wx:
        return '印'
    if WX_SHENG.get(day_wx) == w:
        return '食伤'
    if WX_KE.get(day_wx) == w:
        return '财'
    if WX_KE.get(w) == day_wx:
        return '官杀'
    return ''


def xiangfa_fallback(
    day_gan: str,
    gans: List[str],
    zhis: List[str],
    relations: Optional[Dict] = None,
    zuogong_result: Optional[Dict] = None,
) -> Dict:
    """象法回退分支（K4）：做功不成立时切象法。

    回退激活（fallback_active）：zuogong 无功（work_types 空或 work_level==0）。
    三分支：印带杀帽 / 伤官诀 / 局象纯；三结构检测（与回退并列录入）：
    连体 / 连墓做功 / 丙戊一家半禄。

    Returns:
        {
          'fallback_active': bool,       # 做功不成立，象法回退激活
          'yin_dai_sha_mao': [...],      # 印带杀帽（权力象）
          'shangguan_jue': {...},        # 伤官诀（成局+纯粹+配印->贵）
          'juxiang_chun': {...},         # 局象纯（主导两行覆盖率）
          'lianti': {...},               # 连体（连根之体+被制警示）
          'lianmu_zuogong': [...],       # 连墓做功（两墓库刑冲开库）
          'yijia_banlu': [...],          # 丙戊一家/丁己一家/半禄
          'desc': str,
        }
    """
    gans = gans or []
    zhis = zhis or []
    out: Dict = {
        'fallback_active': False,
        'yin_dai_sha_mao': [],
        'shangguan_jue': {},
        'juxiang_chun': {},
        'lianti': {},
        'lianmu_zuogong': [],
        'yijia_banlu': [],
        'desc': '',
    }
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        out['desc'] = '四柱不全'
        return out
    day_wx = GAN_WX.get(day_gan, '')
    if not day_wx:
        out['desc'] = '日干五行不明'
        return out

    # ── 回退激活：做功不成立（zuogong 无功/无功量），缺省自调 ──
    zg = zuogong_result
    if zg is None:
        try:
            from mangpai.subjective.zuogong_confirm import analyze_zuogong
            zg = analyze_zuogong(
                day_gan, zhis[2], gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3])
        except Exception:
            zg = {}
    work_types = (zg or {}).get('work_types') or []
    work_level = (zg or {}).get('work_level') or 0
    out['fallback_active'] = (not work_types) or work_level == 0

    # ── 1. 印带杀帽：天干七杀坐地支本气印之柱（印=权力，杀帽=权柄之象）──
    yin_wx = ''
    for _w, _gen in WX_SHENG.items():
        if _gen == day_wx:
            yin_wx = _w
            break
    for i in range(4):
        g, z = gans[i], zhis[i]
        if not g or not z:
            continue
        if _pillar_gan_cat(day_wx, g) == '官杀' and ZHI_WX.get(z) == yin_wx:
            item = {
                'pillar': PILLAR_KEYS[i],
                'gz': f'{g}{z}',
                'desc': f'{g}{z}印带杀帽（{z}印{g}杀同柱），印=权力，杀帽=权柄之象',
            }
            # 印支通墓库 -> 权力之库（例一 子水印通辰墓：辰为权力之库）
            power_tombs = [tz for tz in zhis if tz and tz != z and yin_wx in TOMB_MAP.get(tz, [])]
            if power_tombs:
                item['power_tomb'] = power_tombs[0]
                item['desc'] += f'；{z}印通{power_tombs[0]}墓，{power_tombs[0]}为权力之库'
            out['yin_dai_sha_mao'].append(item)

    # ── 2/3. 伤官诀 + 局象纯（同源性，一并算）──
    # 全局主气五行统计（干 + 支本气，共 8 字）
    wx_counts: Dict[str, int] = {}
    for g in gans:
        w = GAN_WX.get(g, '')
        if w:
            wx_counts[w] = wx_counts.get(w, 0) + 1
    for z in zhis:
        w = ZHI_WX.get(z, '')
        if w:
            wx_counts[w] = wx_counts.get(w, 0) + 1
    # 局象纯：主导相生两行覆盖率 ≥6/8（例三 水木 7/8）
    best_pair, best_cnt = None, 0
    for a, b in WX_SHENG.items():
        c = wx_counts.get(a, 0) + wx_counts.get(b, 0)
        if c > best_cnt:
            best_pair, best_cnt = (a, b), c
    chun = bool(best_pair) and best_cnt >= 6
    out['juxiang_chun'] = {
        'pure': chun,
        'pair': f'{best_pair[0]}{best_pair[1]}' if best_pair else '',
        'count': best_cnt,
        'desc': (f'局象纯：{best_pair[0]}{best_pair[1]}二行{best_cnt}/8字，气势纯一'
                 if chun else f'局象杂（主导二行{best_cnt}/8字，未达6字）'),
    }
    # 伤官诀：食伤同一五行干支主气 ≥3（成局）+ 局象纯 + 配印（印明现）
    shi_wx = WX_SHENG.get(day_wx, '')
    sg_cnt = sum(1 for g in gans if GAN_WX.get(g) == shi_wx) + \
        sum(1 for z in zhis if ZHI_WX.get(z) == shi_wx)
    sg_chengju = sg_cnt >= 3
    yin_mingxian = bool(yin_wx) and (
        any(GAN_WX.get(g) == yin_wx for g in gans)
        or any(ZHI_WX.get(z) == yin_wx for z in zhis))
    sg_ok = sg_chengju and chun and yin_mingxian
    out['shangguan_jue'] = {
        'detected': sg_ok,
        'chengju': sg_chengju,
        'sg_wx': shi_wx,
        'sg_count': sg_cnt,
        'pure': chun,
        'pei_yin': yin_mingxian,
        'desc': (f'伤官诀：{day_wx}{shi_wx}伤官成局（{sg_cnt}字）又纯粹，配印，'
                 f'主贵（重权/高官），非做功财命' if sg_ok
                 else f'伤官诀不成立（成局={sg_chengju} 纯={chun} 配印={yin_mingxian}）'),
    }

    # ── 4. 连体（连根之体）──
    day_gz = f'{day_gan}{zhis[2]}'
    day_zhi_wx = ZHI_WX.get(zhis[2], '')
    lianti = (day_gz in _LIANTI_PILLARS
              or day_zhi_wx == day_wx                  # 干支同气
              or WX_SHENG.get(day_zhi_wx) == day_wx)   # 支本气生干（连根）
    lianti_hit = {'is_lianti': bool(lianti), 'gz': day_gz, 'attacked': [], 'warning': ''}
    if lianti:
        # 连体之字不可制服：日柱为被制方（to_pos=day_*）之冲/克/穿/刑（非辅助）
        rel = relations or {}
        for a in (rel.get('work_actions') or []):
            if a.get('auxiliary'):
                continue
            if a.get('type') not in ('冲', '克', '穿', '刑'):
                continue
            tp = a.get('to_pos', '')
            if tp.startswith('day_'):
                lianti_hit['attacked'].append(a.get('desc', ''))
        if lianti_hit['attacked']:
            lianti_hit['warning'] = (
                f'连体之字不可制服：{day_gz}连根之体被制'
                f'（{"、".join(lianti_hit["attacked"][:2])}），制之防伤身体及寿命')
    out['lianti'] = lianti_hit

    # ── 5. 连墓做功：≥2 墓库在局且两墓库相刑冲（开库互制）──
    tomb_zhis = [z for z in zhis if z and z in TOMB_MAP]
    if len(tomb_zhis) >= 2:
        rel = relations or {}
        for a in (rel.get('work_actions') or []):
            if a.get('type') not in ('冲', '刑'):
                continue
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            fk, tk = fp.split('_')[0], tp.split('_')[0]
            if fk in PILLAR_KEYS and tk in PILLAR_KEYS:
                fz = zhis[PILLAR_KEYS.index(fk)] if fp.endswith('_zhi') else ''
                tz = zhis[PILLAR_KEYS.index(tk)] if tp.endswith('_zhi') else ''
                if fz in TOMB_MAP and tz in TOMB_MAP:
                    out['lianmu_zuogong'].append({
                        'pair': f'{fz}{tz}',
                        'type': a.get('type'),
                        'auxiliary': bool(a.get('auxiliary')),
                        'desc': f'连墓做功：{fz}{tz}相{a.get("type")}，两库互开（{a.get("desc","")}）',
                    })
        if not out['lianmu_zuogong']:
            out['lianmu_zuogong'].append({
                'pair': ''.join(tomb_zhis), 'type': '并立', 'auxiliary': True,
                'desc': f'连墓并立：{"".join(tomb_zhis)}两墓库在局，无刑冲互开（待运岁引动）',
            })

    # ── 6. 丙戊一家/丁己一家 + 半禄 ──
    for g1, g2, lu_zhi in _YIJIA_PAIRS:
        if g1 in gans and g2 in gans:
            out['yijia_banlu'].append({
                'kind': '一家', 'pair': f'{g1}{g2}',
                'desc': f'{g1}{g2}一家（同禄于{lu_zhi}，半通禄为一家看，用{g2}如用{g1}）',
            })
    for i in range(4):
        gz = f'{gans[i]}{zhis[i]}'
        if gz in _BANLU_PILLARS:
            out['yijia_banlu'].append({
                'kind': '半禄', 'pillar': PILLAR_KEYS[i], 'gz': gz,
                'desc': f'{gz}为半禄关系（{PILLAR_NAMES_CN[i]}柱）',
            })
        elif (gans[i], zhis[i]) in _BANLU_CROSS:
            out['yijia_banlu'].append({
                'kind': '半禄', 'pillar': PILLAR_KEYS[i], 'gz': gz,
                'desc': f'{gans[i]}见{zhis[i]}为半禄（{PILLAR_NAMES_CN[i]}柱）',
            })

    # ── 汇总 ──
    parts: List[str] = []
    if out['fallback_active']:
        parts.append('做功不成立，象法回退激活')
    if out['yin_dai_sha_mao']:
        parts.append(out['yin_dai_sha_mao'][0]['desc'])
    if out['shangguan_jue'].get('detected'):
        parts.append(out['shangguan_jue']['desc'])
    if out['juxiang_chun'].get('pure'):
        parts.append(out['juxiang_chun']['desc'])
    if out['lianti'].get('warning'):
        parts.append(out['lianti']['warning'])
    for lm in out['lianmu_zuogong'][:1]:
        if not lm.get('auxiliary'):
            parts.append(lm['desc'])
    for yj in out['yijia_banlu'][:2]:
        parts.append(yj['desc'])
    out['desc'] = '；'.join(parts) if parts else '无象法回退信号'
    return out


__all__ = [
    'gongxiang', 'hexiang', 'huaxiang', 'muxiang',
    'zhixiang', 'daixiang', 'jiexiang',
    'huanxiang', 'juxiang',
    'xiangfa_fallback',
    'analyze_xiangfa_ops',
]
