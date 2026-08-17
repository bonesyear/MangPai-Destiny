"""
gongmen_wuzhi - 盲派公门武职专辑·主观层（subjective）

⚠️ F18 批（2026-08-17）**正式弃用**（F1 标记弃用 → 本批决策落地）：
  接入决策=**不接 zhiye**——F15 已在 zhiye._score_military 按书重写 8.2
  六组组合（贵气门+组合封顶），本模块仅存档备查。is_wuzhi 聚合口径近恒真
  （任一武职类象即 True，几乎逢盘必中），输出信息量趋零——narrative LLM
  结论行通道本批已切断（engine result 键因 schools selectors 保护链保留）。
  实现与 gaoji 8.2 的 11 条 P0 级偏差（批8 审计）不再逐条修，唯阳制阴口径
  按书 11787-11788 修正存档。删除/_zhi_doi 等死代码 F1 已清。

理论来源：段建业《盲派命理高级内容篇》8.2「公门武职」（源文 11588-11971 行）
核心思想：公门武职以「干支类象 + 组合做功」定位——寅为公门、戌为火药枪弹
          库、申酉为刀枪律法、丑为阴库（公安刑警）、巳午为枪炮、羊刃七杀为
          暴力权柄。军官四组合 + 公检法三组各有其配置，层次高低看做功效率
          与制化清浊（消费 gongliang 四档定性）。

两组判定（高级篇 8.2）：
  A. 军官四组合（8.2 三）：
     1. 七杀配羊刃/羊刃库——以暴制暴反得兵权（羊刃库未冲刑七杀库丑戌亦同）。
     2. 伤官制杀或杀库——以技取权，技术兵种/参谋。
     3. 官杀配比劫/比劫库——官杀管比劫（兵众），比劫库冲官杀库。
     4. 戌土火库做功——戌为火药库/刀枪库，入兵营掌权。
  B. 公检法三组（8.2 四）：
     - 公安：申酉丑寅组合做功、丑戌相刑（扫黑）、阳制阴。
     - 检察·法院：申酉金做功、伤官合杀（检察纪检）、食神制官（法官）、
       卯酉冲/卯午破（依律断案）。
     - 司法·纪检：伤官重/伤官见官（监督官员）、枭神夺食（查处经济/审计）。

层次（8.2 五 + 8.3）：制得干净/包局/合化=官大权重；制不净=官小基层；
官杀印星虚透天干=名气荣誉非实权，地支见根方落实为管理之职。消费 gongliang
四档定性（level 1-4 / rank_grade）定军官级别，本模块做公门武职口径细化。

消费关系：
  - objective.constants（五行生克/藏干）
  - objective.canggan.get_canggan_mangpai（藏干，十神定位）
  - objective.zuogong_detect.detect_relations（冲刑合克，做功组合）
  - objective.shensha.compute_shensha_ext（羊刃，武职刀枪/暴力）
  - objective.muku.analyze_muku（墓库开闭，戌火库/丑阴库做功）
  - subjective.gongliang.analyze_gongliang（四档定性，军官层次）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：军官四组合/公检法三组为类象+组合启发式（非精确分类器）；层次量化
          依赖 gongliang 功量层，公门武职口径与行政级别对应为段氏主流归纳。
置信度：中
"""
from typing import Dict, List, Optional, Set, Tuple

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext, resolve_shensha
from mangpai.objective.muku import analyze_muku
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.yongshen import assess_direction_signals, direction_brief

_YANG_GANS = set('甲丙戊庚壬')


# ───────────────────── 共用小工具 ─────────────────────

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


def _cat(ss: str) -> str:
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
    return ''


def _wx_cat(day_gan: str, wx: str) -> str:
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


def _pillar_cats(day_gan: str, gan: str, zhi: str) -> Set[str]:
    cats: Set[str] = set()
    c = _cat(_compute_shishen(day_gan, gan))
    if c:
        cats.add(c)
    zw = ZHI_WX.get(zhi, '')
    if zw:
        cats.add(_wx_cat(day_gan, zw))
    for idx, (cg, _) in enumerate(get_canggan_mangpai(zhi)):
        if idx <= 1:
            cats.add(_cat(_compute_shishen(day_gan, cg)))
    cats.discard('')
    return cats


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


def _pos_idx(pos: str) -> int:
    k = pos.split('_')[0]
    return PILLAR_KEYS.index(k) if k in PILLAR_KEYS else -1


def _has_cat(day_gan, gans, zhis, cat) -> bool:
    n = min(len(gans), len(zhis))
    return any(cat in _pillar_cats(day_gan, gans[i], zhis[i]) for i in range(n))


def _action_between_cats(wa, day_gan, gans, zhis, cat_a, cat_b, types) -> List[Dict]:
    out: List[Dict] = []
    for a in wa:
        if a.get('type') not in types:
            continue
        fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
        if fi < 0 or ti < 0:
            continue
        fa = _pillar_cats(day_gan, gans[fi], zhis[fi])
        ta = _pillar_cats(day_gan, gans[ti], zhis[ti])
        if (cat_a in fa and cat_b in ta) or (cat_b in fa and cat_a in ta):
            out.append(a)
    return out

# ───────────────────── A. 军官四组合 ─────────────────────

def classify_junguan(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """军官四组合检测（8.2 三）。

    Returns:
        {
          'combos': [str],  # 命中的组合名（1-4）
          'evidence': [str],
          'is_junguan': bool,
          'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    try:
        ss = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        ss = {}
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}

    combos: List[str] = []
    ev: List[str] = []

    has_qisha = _has_cat(day_gan, gans, zhis, '官杀')
    # F13：全刃表口径（戊刃在午、未双刃，旧 zhi 单值对刃在未盘漏检）
    yr_hits = [z for z in ((ss.get('羊刃') or {}).get('zhi_all')
                           or [(ss.get('羊刃') or {}).get('zhi', '')])
               if z and z in zhis]
    has_yangren = bool(yr_hits)
    # 羊刃库=未（劫财库），七杀库=丑/戌
    has_yangren_ku = '未' in zhis
    open_tombs = {t.get('zhi') for t in (muku.get('open_tombs') or [])}

    # 组合1：七杀配羊刃/羊刃库（杀入羊刃墓）
    if has_qisha and (has_yangren or has_yangren_ku):
        combos.append('七杀配羊刃/羊刃库')
        detail = f'羊刃{yr_hits[0]}' if has_yangren else '羊刃库未'
        ev.append(f'七杀配{detail}（以暴制暴得兵权）')
        if has_yangren_ku and ('丑' in open_tombs or '戌' in open_tombs):
            ev.append('羊刃库未冲刑七杀库（权力入军队）')

    # 组合2：伤官制杀/杀库
    if _action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'克'}):
        combos.append('伤官制杀/杀库')
        ev.append('伤官制杀（以技取权，技术兵种/参谋）')

    # 组合3：官杀配比劫/比劫库（比劫库冲官杀库）
    if has_qisha and _has_cat(day_gan, gans, zhis, '比劫'):
        combos.append('官杀配比劫/比劫库')
        ev.append('官杀管比劫（兵众），调动管理之象')
        if '未' in zhis and ('丑' in open_tombs or '戌' in open_tombs):
            ev.append('比劫库未冲官杀库')

    # 组合4：戌土火库做功
    if '戌' in zhis:
        xu_doi = any(a.get('type') in ('冲', '刑', '地支合', '半合')
                     and (_pos_idx(a.get('from_pos', '')) == zhis.index('戌')
                          or _pos_idx(a.get('to_pos', '')) == zhis.index('戌'))
                     for a in wa)
        if xu_doi or '戌' in open_tombs:
            combos.append('戌土火库做功')
            ev.append('戌火药库/刀枪库做功（入兵营掌权）')

    is_junguan = bool(combos)
    return {
        'combos': combos,
        'evidence': ev,
        'is_junguan': is_junguan,
        'desc': '军官象：' + '；'.join(ev) if ev else '无明显军官组合',
    }


# ───────────────────── B. 公检法三组 ─────────────────────

def classify_gongjianfa(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """公检法三组检测（8.2 四）。

    Returns:
        {
          'groups': [str],  # 命中组（公安/检察法院/司法纪检）
          'evidence': [str],
          'is_gongjianfa': bool,
          'desc': str,
        }
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    try:
        muku = analyze_muku(zhis, gans)
    except Exception:
        muku = {}
    open_tombs = {t.get('zhi') for t in (muku.get('open_tombs') or [])}

    groups: List[str] = []
    ev: List[str] = []
    present = set(z for z in zhis if z)

    # ── 公安：申酉丑寅组合做功为基，丑戌刑/阳制阴为辅 ──
    gong_an_keys = {'申', '酉', '丑', '寅'} & present
    gong_an_base = len(gong_an_keys) >= 2
    gong_an_score = 1 if gong_an_base else 0
    if gong_an_base:
        ev.append(f'申酉丑寅组合{"".join(sorted(gong_an_keys))}（公安象）')
        # 丑戌相刑（扫黑）—— 仅在公安基象成立时计入
        if any(a.get('type') == '刑'
               and {zhis[_pos_idx(a.get('from_pos', ''))],
                    zhis[_pos_idx(a.get('to_pos', ''))]} == {'丑', '戌'} for a in wa):
            gong_an_score += 1
            ev.append('丑戌相刑（扫黑破案）')
        # 阳制阴——仅在公安基象成立时计入
        # F18 按书修正口径（批8 P0-5，gaoji:11787-11788）：阳气=丙丁巳午戊戌、
        # 阴气=辛酉癸子丑——**含天干、子归阴**（旧码=标准阳支集纯地支「克」、
        # 子算阳，与书相反）；制类动作（克/冲/穿/刑）须阳为制方。
        _YANG82 = set('丙丁戊巳午戌')
        _YIN82 = set('辛癸酉子丑')

        def _end_ch(pos: str) -> str:
            i = _pos_idx(pos)
            if i < 0:
                return ''
            return gans[i] if pos.endswith('_gan') else zhis[i]

        yang_ke_yin = any(
            a.get('type') in ('克', '冲', '穿', '刑')
            and _end_ch(a.get('from_pos', '')) in _YANG82
            and _end_ch(a.get('to_pos', '')) in _YIN82
            for a in wa
        )
        if yang_ke_yin:
            gong_an_score += 1
            ev.append('阳制阴（正义制邪恶）')
    if gong_an_score >= 1:
        groups.append('公安')

    # ── 检察·法院：申酉金做功 + 伤官合杀/食神制官 + 卯酉冲卯午破 ──
    jcy_score = 0
    if {'申', '酉'} & present:
        jcy_score += 1
        ev.append('申酉金做功（律法/法院检察）')
    if _action_between_cats(wa, day_gan, gans, zhis, '食伤', '官杀', {'天干合', '地支合', '半合'}):
        jcy_score += 1
        ev.append('伤官合杀（检察/纪检）')
    if any(_compute_shishen(day_gan, g) == '食神' for g in gans if g) and \
       _has_cat(day_gan, gans, zhis, '官杀'):
        jcy_score += 1
        ev.append('食神制官（法官）')
    for a in wa:
        if a.get('type') in ('冲', '破'):
            fi, ti = _pos_idx(a.get('from_pos', '')), _pos_idx(a.get('to_pos', ''))
            if fi >= 0 and ti >= 0:
                pair = frozenset({zhis[fi], zhis[ti]})
                if pair == frozenset({'卯', '酉'}) or pair == frozenset({'卯', '午'}):
                    jcy_score += 1
                    ev.append(f'{"".join(pair)}{a.get("type")}（依律断案）')
                    break
    if jcy_score >= 2:
        groups.append('检察法院')

    # ── 司法·纪检：伤官重/伤官见官 + 枭神夺食 ──
    sf_score = 0
    sg_count = sum(1 for i in range(4) if _has_cat(day_gan, [gans[i]], [zhis[i]], '食伤'))
    if sg_count >= 2 and _has_cat(day_gan, gans, zhis, '官杀'):
        sf_score += 1
        ev.append('伤官重见官（监督官员）')
    # 枭神夺食：印旺克食伤
    yin_count = sum(1 for i in range(4) if '印' in _pillar_cats(day_gan, gans[i], zhis[i]))
    if yin_count >= 2 and yin_count > sg_count and sg_count >= 1:
        sf_score += 1
        ev.append('枭神夺食（查处经济/审计纪检）')
    if sf_score >= 2:
        groups.append('司法纪检')

    is_gjf = bool(groups)
    return {
        'groups': groups,
        'evidence': ev,
        'is_gongjianfa': is_gjf,
        'desc': '公检法象：' + '；'.join(ev) if ev else '无明显公检法组合',
    }


# ───────────────────── 类象 + 层次 ─────────────────────

def detect_gongmen_wuzhi_xiang(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """公门/武职类象检测（8.2 总论）。

    Returns:
        {'gongmen': [str], 'wuzhi': [str], 'desc': str}
    """
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    try:
        ss = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        ss = {}
    gongmen: List[str] = []
    wuzhi: List[str] = []

    # 公门：寅为公门
    if '寅' in zhis:
        gongmen.append('寅（公门官府）')
    # 印配官杀（公家单位）
    if _has_cat(day_gan, gans, zhis, '印') and _has_cat(day_gan, gans, zhis, '官杀'):
        gongmen.append('印配官杀（公家单位职务）')
    # 财库制印库（管公财，财政税务）
    if _action_between_cats(wa, day_gan, gans, zhis, '财', '印', {'克', '穿'}):
        gongmen.append('财制印（管公财之权，财政税务）')

    # 武职：戌火库/申酉刀枪/丑阴库/巳午枪炮/羊刃/七杀
    if '戌' in zhis:
        wuzhi.append('戌（火药枪弹库）')
    if {'申', '酉'} & set(zhis):
        wuzhi.append('申酉（刀枪律法）')
    if '丑' in zhis:
        wuzhi.append('丑（阴库，公安刑警）')
    if {'巳', '午'} & set(zhis):
        wuzhi.append('巳午（枪炮灯光）')
    # F13：全刃表口径（戊双刃午未，旧 zhi 单值漏检刃在未盘）
    yr2 = (ss.get('羊刃') or {})
    yr2_hits = [z for z in (yr2.get('zhi_all') or [yr2.get('zhi', '')])
                if z and z in zhis]
    if yr2_hits:
        wuzhi.append(f'羊刃{"".join(yr2_hits)}（刀枪暴力）')
    if _has_cat(day_gan, gans, zhis, '官杀'):
        wuzhi.append('七杀（权威暴力）')

    return {
        'gongmen': gongmen,
        'wuzhi': wuzhi,
        'desc': '公门：' + '、'.join(gongmen) + '；武职：' + '、'.join(wuzhi)
        if (gongmen or wuzhi) else '无明显公门武职类象',
    }


def assess_wuzhi_level(
    day_gan: str, gans: List[str], zhis: List[str],
    gongliang_result: Optional[Dict] = None,
) -> Dict:
    """公门武职层次（8.2 五 + 8.3）：消费 gongliang 四档定性 + 虚透/落实判据。

    层次映射（段氏主流）：
      gongliang level 4 → 将官/极品；3 → 师级/中高；2 → 团营/中；1 → 基层/小。
    虚透判据：官杀仅透天干无地支根=名气荣誉非实权；地支见根=落实管理之职。

    Returns:
        {
          'level': int, 'grade': str, 'you_gen': bool, 'xutou': bool,
          'desc': str,
        }
    """
    # gongliang level
    gl = gongliang_result or {}
    level = gl.get('level', 0) if gl else 0
    grade_map = {4: '将官/极品', 3: '师级/中高', 2: '团营/中', 1: '基层/小'}
    grade = grade_map.get(level, '未定（缺 gongliang）')

    # 官杀有根判据（地支见根=落实实权）
    day_wx = GAN_WX.get(day_gan, '')
    guan_wx = WX_KE_ME.get(day_wx, '')
    you_gen = False
    if guan_wx:
        for z in zhis:
            if ZHI_WX.get(z) == guan_wx:
                you_gen = True
                break
            for idx, (cg, _) in enumerate(get_canggan_mangpai(z)):
                if idx <= 1 and GAN_WX.get(cg) == guan_wx:
                    you_gen = True
                    break
            if you_gen:
                break
    # 虚透：天干有官杀但无地支根
    has_gan_guan = any(_cat(_compute_shishen(day_gan, g)) == '官杀' for g in gans if g)
    xutou = has_gan_guan and not you_gen

    parts = [f'层次：{grade}']
    if xutou:
        parts.append('官杀虚透天干（名气荣誉，非实权）')
    elif you_gen:
        parts.append('官杀地支有根（落实管理之职）')
    return {
        'level': level,
        'grade': grade,
        'you_gen': you_gen,
        'xutou': xutou,
        'desc': '；'.join(parts),
    }


# ───────────────────── 聚合 ─────────────────────

def analyze_gongmen_wuzhi(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    gongliang_result: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
    direction_result: Optional[Dict] = None,
) -> Dict:
    """公门武职综合：类象 + 军官四组合 + 公检法三组 + 层次。
    A3：接入 yongshen 方向总线（direction_result 缺省自调，只读信号不改判定）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'xiang': {...}, 'junguan': {...}, 'gongjianfa': {...},
          'level': {...}, 'is_wuzhi': bool, 'primary': str, 'summary': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'summary': '四柱不全，无法判定公门武职'}

    # 神煞：优先用 engine 透传值，缺省才就地重算（羊刃，武职刀枪/暴力）
    ss = resolve_shensha(day_gan, zhis, shensha_result)

    # gongliang 缺省自调
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

    xiang = detect_gongmen_wuzhi_xiang(day_gan, gans, zhis, relations,
                                       shensha_result=ss)
    jg = classify_junguan(day_gan, gans, zhis, relations, shensha_result=ss)
    gjf = classify_gongjianfa(day_gan, gans, zhis, relations)
    lv = assess_wuzhi_level(day_gan, gans, zhis, gl)

    # A3：方向总线信号（缺省自调）
    if direction_result is None:
        try:
            direction_result = assess_direction_signals(
                day_gan, gans, zhis, relations=relations, gongliang_result=gl)
        except Exception:
            direction_result = {}

    is_wuzhi = jg.get('is_junguan') or gjf.get('is_gongjianfa') or \
        bool(xiang.get('wuzhi'))
    primary = ''
    if jg.get('is_junguan'):
        primary = '军官'
    elif gjf.get('is_gongjianfa'):
        primary = '、'.join(gjf.get('groups', []))
    elif xiang.get('gongmen'):
        primary = '公门'

    parts = []
    if primary:
        parts.append(f'公门武职：{primary}')
    parts.append(lv.get('desc', ''))
    summary = '；'.join(p for p in parts if p) or '无明显公门武职象'

    return {
        'xiang': xiang,
        'junguan': jg,
        'gongjianfa': gjf,
        'level': lv,
        'is_wuzhi': is_wuzhi,
        'primary': primary,
        'direction_signals': direction_brief(direction_result),
        'summary': summary,
    }


__all__ = [
    'classify_junguan',
    'classify_gongjianfa',
    'detect_gongmen_wuzhi_xiang',
    'assess_wuzhi_level',
    'analyze_gongmen_wuzhi',
]
