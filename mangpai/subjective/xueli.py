"""
xueli - 盲派学历专辑·主观层（subjective）

理论来源：段建业《盲派中级命理学》第十一章「学历专辑」（源文 5394-5577 行）
核心思想：学历看「学历之神」与「破坏之神」的较量。段氏明言「以官杀、印星
          与食神当学历之神；以财星、伤官、比劫当破坏学历之神」（zhongji:5397）。
          学历之神为用且不被坏 -> 高学历；财/伤官/比劫坏印食 -> 低学历/学业中断。

三项判定：
  1. 学历之神 vs 破坏之神：
       学历之神=官杀+印+食神（官杀主科名纪律、印主学问、食神主科甲才华）；
       破坏之神=财+伤官+比劫（zhongji:5397；财坏印、伤官不守规矩、比劫好动不思学习）。
  2. 学历高低：印食旺且不被坏 -> 高学历；财/伤官/比劫坏之 -> 低学历；印食受克中断 -> 中断；
       杀制伤官/合杀（杀配伤官/合杀为用）-> 高学历（官杀亦学历之神）。
  3. 文理行业：文科=印/食神/木火旺（主文）；理科=伤官/七杀/金水旺（主理）。

消费关系：
  - objective.zuogong_detect.detect_relations（财坏印、枭夺食、印食受克关系）
  - objective.constants（五行生克/藏干）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：学历高低的旺衰/破坏阈值为段氏主流口径启发式（非计数定量）；
          文理行业映射为段氏取象归纳。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.yongshen import assess_direction_signals, direction_brief

_YANG_GANS = set('甲丙戊庚壬')


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


def _pillar_cats(day_gan: str, gans: List[str], zhis: List[str]) -> List[Set[str]]:
    """逐柱十神大类集合（天干 + 藏干）。"""
    out: List[Set[str]] = []
    for i in range(4):
        cats: Set[str] = set()
        if i < len(gans) and gans[i]:
            c = _cat(_compute_shishen(day_gan, gans[i]))
            if c:
                cats.add(c)
        if i < len(zhis) and zhis[i]:
            for cg, _ in get_canggan_mangpai(zhis[i]):
                c = _cat(_compute_shishen(day_gan, cg))
                if c:
                    cats.add(c)
        out.append(cats)
    return out


def _mingxian_cats(day_gan: str, gans: List[str], zhis: List[str]) -> List[Set[str]]:
    """逐柱明现十神大类集合（天干+本/中气，余气不计）。"""
    out: List[Set[str]] = []
    for i in range(4):
        cats: Set[str] = set()
        if i < len(gans) and gans[i]:
            c = _cat(_compute_shishen(day_gan, gans[i]))
            if c:
                cats.add(c)
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break  # 仅本气/中气
                c = _cat(_compute_shishen(day_gan, cg))
                if c:
                    cats.add(c)
        out.append(cats)
    return out


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


# 合用动作类型（对称关系，from/to 无方向语义）
_HE_CONTROL: Set[str] = {'天干合', '地支合', '暗合', '半合'}


def _pos_pillar(pos: str) -> str:
    return pos.split('_')[0] if pos else ''


def _pillar_mingxian_shishen(day_gan: str, gans: List[str], zhis: List[str]) -> List[Set[str]]:
    """逐柱明现十神集合（天干+本/中气，余气不计），具体十神（七杀/伤官等，非大类）。

    用于杀制伤官/合杀判定：须定位七杀与伤官的明现柱位。
    """
    out: List[Set[str]] = []
    for i in range(4):
        ss_set: Set[str] = set()
        if i < len(gans) and gans[i]:
            ss = _compute_shishen(day_gan, gans[i])
            if ss:
                ss_set.add(ss)
        if i < len(zhis) and zhis[i]:
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break  # 仅本气/中气
                ss = _compute_shishen(day_gan, cg)
                if ss:
                    ss_set.add(ss)
        out.append(ss_set)
    return out


def _pos_mingxian_shishen(day_gan: str, gans: List[str], zhis: List[str], pos: str) -> Set[str]:
    """pos 的明现十神集合（取 pos 实际字，非整柱）：'X_gan' 取天干，'X_zhi' 取地支本/中气藏干。

    合杀判定须取合动作两端实际相合之字（天干合取干、地支合/暗合/半合取支藏本中气），
    避免柱含杀伤而他字相合的误判（如壬丁合财，柱虽含杀伤，相合者乃比肩与财）。
    """
    pk = _pos_pillar(pos)
    if pk not in PILLAR_KEYS:
        return set()
    idx = PILLAR_KEYS.index(pk)
    out: Set[str] = set()
    if pos.endswith('_gan'):
        if idx < len(gans) and gans[idx]:
            ss = _compute_shishen(day_gan, gans[idx])
            if ss:
                out.add(ss)
    else:  # _zhi
        if idx < len(zhis) and zhis[idx]:
            for i, (cg, _) in enumerate(get_canggan_mangpai(zhis[idx])):
                if i > 1:
                    break  # 仅本气/中气
                ss = _compute_shishen(day_gan, cg)
                if ss:
                    out.add(ss)
    return out


# ───────────────────── 1. 学历之神 vs 破坏之神 ─────────────────────

def classify_xueli_shen(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """学历之神(官杀+印+食神) vs 破坏之神(财+伤官+比劫，zhongji:5397)。

    段氏明言「以官杀、印星与食神当学历之神；以财星、伤官、比劫当破坏学历之神」。
    学历之神：官杀(主科名纪律) + 印(正印/偏印，主学问学历) + 食神(主科甲才华)；
    破坏之神：财(坏印) + 伤官(不守规矩不爱学习教课书) + 比劫(好动争斗不思学习)。
    （枭夺食书锚在牢狱章 zhongji:5589-5590，非学历章破坏之神——F17 X1 修正）

    Returns:
        {
          'xueli_shen': [str],     # 学历之神命中（官杀/印/食神）
          '破坏_shen': [str],      # 破坏之神命中（财/伤官/比劫）
          'yin_count': int, 'shi_count': int,
          'cai_count': int, 'guan_count': int, 'xiao_count': int,
          'shang_count': int, 'bijie_tou': int, 'bijie_gen': int,
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
        return {'xueli_shen': [], '破坏_shen': [], 'yin_count': 0, 'shi_count': 0,
                'cai_count': 0, 'guan_count': 0, 'xiao_count': 0,
                'shang_count': 0, 'bijie_tou': 0, 'bijie_tou_ym': 0, 'bijie_gen': 0,
                'details': ['四柱不全']}

    prom = _mingxian_cats(day_gan, gans, zhis)
    yin_count = sum(1 for c in prom if '印' in c)
    shi_count = sum(1 for c in prom if '食伤' in c)  # 食伤含食神
    cai_count = sum(1 for c in prom if '财' in c)
    guan_count = sum(1 for c in prom if '官杀' in c)  # 官杀亦学历之神

    # 枭(偏印)夺食计数保留（牢狱章口径，不再作学历破坏之神——F17 X1）
    has_pianyin = False
    has_shishen = False
    # 伤官/比劫明现计数（破坏之神，zhongji:5397）；日主自身不算比劫
    shang_count = 0
    bijie_tou = 0
    bijie_tou_ym = 0  # 年月透干比劫（年月=学业期宫位，zhongji:5484）
    bijie_gen = 0
    for i in range(4):
        if i < len(gans) and gans[i]:
            ss = _compute_shishen(day_gan, gans[i])
            if ss == '偏印':
                has_pianyin = True
            if ss == '食神':
                has_shishen = True
            if i != 2:  # 日主不算比劫/伤官破坏方
                if ss == '伤官':
                    shang_count += 1
                if ss in ('比肩', '劫财'):
                    bijie_tou += 1
                    if i in (0, 1):
                        bijie_tou_ym += 1
        if i < len(zhis) and zhis[i]:
            zhi_shang = False
            zhi_bijie = False
            for idx, (cg, _) in enumerate(get_canggan_mangpai(zhis[i])):
                if idx > 1:
                    break
                ss = _compute_shishen(day_gan, cg)
                if ss == '偏印':
                    has_pianyin = True
                if ss == '食神':
                    has_shishen = True
                if ss == '伤官':
                    zhi_shang = True
                if ss in ('比肩', '劫财'):
                    zhi_bijie = True
            if zhi_shang:
                shang_count += 1
            if zhi_bijie:
                bijie_gen += 1
    xiao_count = 1 if (has_pianyin and has_shishen) else 0

    xueli_shen: List[str] = []
    po_shen: List[str] = []
    if yin_count > 0:
        xueli_shen.append('印')
    if has_shishen:
        xueli_shen.append('食神')
    if guan_count > 0:
        xueli_shen.append('官杀')  # 段氏：官杀亦学历之神（主科名纪律）
    # 破坏之神=财/伤官/比劫（zhongji:5397，枭非学历章破坏之神）
    if cai_count > 0:
        po_shen.append('财')
    if shang_count > 0:
        po_shen.append('伤官')
    if bijie_tou + bijie_gen > 0:
        po_shen.append('比劫')

    details: List[str] = []
    if xueli_shen:
        details.append(f'学历之神：{"、".join(xueli_shen)}（印{yin_count}位、食神{"有" if has_shishen else "无"}、官杀{guan_count}位）')
    if po_shen:
        details.append(f'破坏之神：{"、".join(po_shen)}（财{cai_count}位、伤官{shang_count}位、比劫透{bijie_tou}根{bijie_gen}）')

    return {
        'xueli_shen': xueli_shen,
        '破坏_shen': po_shen,
        'yin_count': yin_count,
        'shi_count': 1 if has_shishen else 0,
        'cai_count': cai_count,
        'guan_count': guan_count,
        'xiao_count': xiao_count,
        'shang_count': shang_count,
        'bijie_tou': bijie_tou,
        'bijie_tou_ym': bijie_tou_ym,
        'bijie_gen': bijie_gen,
        'details': details,
    }


# ───────────────────── 2. 学历高低 ─────────────────────

def classify_xueli_level(
    day_gan: str, gans: List[str], zhis: List[str],
    relations: Optional[Dict] = None,
) -> Dict:
    """学历高低：印食旺且不被坏 -> 高；财/伤官/比劫坏之 -> 低；印食受克中断 -> 中断；
    杀制伤官/合杀（杀配伤官/合杀为用，官杀亦学历之神）-> 高。

    Returns:
        {'level': '高'|'中'|'低'|'中断', 'signals': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'level': '中', 'signals': ['四柱不全']}

    shen = classify_xueli_shen(day_gan, gans, zhis, relations)
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    cats = _pillar_cats(day_gan, gans, zhis)

    yin = shen.get('yin_count', 0)
    shi = shen.get('shi_count', 0)
    cai = shen.get('cai_count', 0)
    guan = shen.get('guan_count', 0)
    shang = shen.get('shang_count', 0)
    bijie_tou = shen.get('bijie_tou', 0)
    bijie_tou_ym = shen.get('bijie_tou_ym', 0)
    bijie_gen = shen.get('bijie_gen', 0)

    signals: List[str] = []
    # 财坏印：需财五行明现且财克印（元素级）。印五行=生我者。
    day_wx = GAN_WX.get(day_gan, '')
    yin_wx = ''
    for w, gen in WX_SHENG.items():
        if gen == day_wx:
            yin_wx = w
            break
    cai_wx = WX_KE.get(day_wx, '')  # 财五行=我克
    cai_huai_yin = bool(
        yin_wx and cai_wx and WX_KE.get(cai_wx) == yin_wx and cai >= 1
    )

    score = 0
    if yin >= 1:
        score += 2
        signals.append(f'印星明现（{yin}位），利学历')
    if shi:
        score += 1
        signals.append('食神明现，主科甲才华')
    if guan >= 1:
        score += 1
        signals.append(f'官杀明现（{guan}位），官杀亦学历之神，利科名')
    # 财坏印按力量对比加权：财多印少才算实坏
    if cai_huai_yin:
        if yin == 0:
            score -= 1
            signals.append('财旺无印，学历之神本弱')
        elif cai >= yin:
            score -= 2
            signals.append('财坏印（财多印少），学历受损')
        else:
            score -= 1
            signals.append('财轻印重，印未全坏')
    elif yin == 0 and cai >= 2:
        score -= 1
        signals.append('财多无印，学历之神不显')
    # 伤官为破坏之神；配印/配官杀做功则学有所成，不扣（zhongji:5405-5407）
    shang_deduct = shang >= 1 and yin == 0 and guan == 0
    if shang_deduct:
        score -= 1
        signals.append('伤官明现无印杀相配，不守规矩不爱学习教课书')
    # 比劫结伙成群主不思学习（zhongji:5408-5409）。年月=学业期宫位，年月比劫成群
    # 方为重破坏（zhongji:5484「年月比劫是不爱学习的标志」）；年时分布之比劫多主
    # 帮身泄印（zhongji:5540 例17 闲注「泄的越多学问越高」），按透干有根群轻扣；
    # 单透无根群不扣（zhongji:5575 例21 甲泄印反锚）。
    bijie_deduct = bijie_tou_ym >= 2 or (bijie_tou >= 1 and bijie_gen >= 2)
    if bijie_tou_ym >= 2:
        score -= 2
        signals.append('年月比劫成群，好动争斗不思学习')
    elif bijie_tou >= 1 and bijie_gen >= 2:
        score -= 1
        signals.append('比劫透干有根群，主不思学习')

    # 杀制伤官/合杀 -> 高学历（段氏：官杀亦学历之神，杀配伤官/合杀为用主科甲高学历）
    # - 合杀：七杀明现 + 伤官明现 + 合动作连接杀位与伤官位（伤官合杀，合杀为用）；
    # - 杀制伤官：七杀明现 + 伤官明现 + 杀五行克伤官五行（杀制伤官，杀配伤官）。
    per_ss = _pillar_mingxian_shishen(day_gan, gans, zhis)
    sha_pillars = {i for i, s in enumerate(per_ss) if '七杀' in s}
    shang_pillars = {i for i, s in enumerate(per_ss) if '伤官' in s}
    he_sha = False
    sha_zhi_shang = False
    if sha_pillars and shang_pillars:
        # 合杀（伤官合杀）：合动作两端须分别为七杀与伤官--取 pos 实际相合之字
        # （天干合取干、地支合/暗合/半合取支藏本中气），非整柱，避免柱含杀伤而
        # 他字相合的误判（如壬丁合财误作伤官合杀）。
        wa = rel.get('work_actions') or []
        for a in wa:
            if a.get('type') not in _HE_CONTROL:
                continue
            fss = _pos_mingxian_shishen(day_gan, gans, zhis, a.get('from_pos', ''))
            tss = _pos_mingxian_shishen(day_gan, gans, zhis, a.get('to_pos', ''))
            if ('七杀' in fss and '伤官' in tss) or ('伤官' in fss and '七杀' in tss):
                he_sha = True
                break
        # 杀制伤官：七杀五行克伤官五行（杀_wx 克 伤官_wx）
        sha_wx = WX_KE_ME.get(day_wx, '')    # 官杀五行=克我
        shang_wx = WX_SHENG.get(day_wx, '')  # 食伤五行=我生
        if sha_wx and shang_wx and WX_KE.get(sha_wx) == shang_wx:
            sha_zhi_shang = True
    if he_sha:
        signals.append('伤官合杀（合杀为用），杀配伤官主高学历')
    if sha_zhi_shang:
        signals.append('杀制伤官，杀配伤官主高学历')

    if he_sha or sha_zhi_shang:
        level = '高'
    elif score >= 3:
        level = '高'
    elif score <= 0 and (cai_huai_yin or shang_deduct or bijie_deduct or (yin == 0 and cai >= 2)):
        level = '低'
    elif cai_huai_yin and cai >= 2 and yin >= 1 and cai >= yin:
        level = '中断'
    else:
        level = '中'
    return {'level': level, 'signals': signals, 'score': score}


# ───────────────────── 3. 文理行业 ─────────────────────

def classify_wenli(
    day_gan: str, gans: List[str], zhis: List[str],
) -> Dict:
    """文理行业：文科=印/食神/木火旺；理科=伤官/七杀/金水旺。

    Returns:
        {'direction': '文'|'理'|'文理兼', 'signals': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'direction': '文理兼', 'signals': ['四柱不全']}

    prom = _mingxian_cats(day_gan, gans, zhis)
    # 木火(文) vs 金水(理) 计数
    wen_wx = {'木', '火'}
    li_wx = {'金', '水'}
    wen_count = 0
    li_count = 0
    for i in range(4):
        if i < len(gans) and gans[i]:
            w = GAN_WX.get(gans[i], '')
            if w in wen_wx:
                wen_count += 1
            elif w in li_wx:
                li_count += 1
        if i < len(zhis) and zhis[i]:
            w = ZHI_WX.get(zhis[i], '')
            if w in wen_wx:
                wen_count += 1
            elif w in li_wx:
                li_count += 1
    # 印/食神主文，伤官/七杀主理
    has_yin_shi = any('印' in c or '食伤' in c for c in prom)
    # 伤官/七杀主理（更细：伤官偏理、七杀偏理）
    has_shang_sha = False
    for i in range(4):
        if i < len(gans) and gans[i]:
            ss = _compute_shishen(day_gan, gans[i])
            if ss in ('伤官', '七杀'):
                has_shang_sha = True

    signals: List[str] = []
    if has_yin_shi:
        signals.append('印/食神现，偏文科')
    if has_shang_sha:
        signals.append('伤官/七杀现，偏理科')
    signals.append(f'木火(文){wen_count}位、金水(理){li_count}位')

    if wen_count > li_count and (has_yin_shi or not has_shang_sha):
        direction = '文'
    elif li_count > wen_count and (has_shang_sha or not has_yin_shi):
        direction = '理'
    elif wen_count == li_count:
        direction = '文理兼'
    else:
        direction = '文' if has_yin_shi else '理'
    return {'direction': direction, 'signals': signals}


# ───────────────────── 聚合 ─────────────────────

def analyze_xueli(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    *,
    relations: Optional[Dict] = None,
    direction_result: Optional[Dict] = None,
) -> Dict:
    """学历综合：学历之神/破坏之神 + 学历高低 + 文理。
    A3：接入 yongshen 方向总线（direction_result 缺省自调，只读信号不改判定）。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'shen': {...}, 'level': {...}, 'wenli': {...},
          'level_str': str, 'direction': str, 'summary': str,
        }
    """
    if is_pillars(day_gan):
        p = day_gan
        if not gans:
            gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        if not zhis:
            zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan

    shen = classify_xueli_shen(day_gan, gans or [], zhis or [], relations)
    level = classify_xueli_level(day_gan, gans or [], zhis or [], relations)
    wenli = classify_wenli(day_gan, gans or [], zhis or [])

    # A3：方向总线信号（缺省自调）
    if direction_result is None:
        try:
            direction_result = assess_direction_signals(
                day_gan, gans or [], zhis or [], relations=relations)
        except Exception:
            direction_result = {}

    summary = f'学历{level.get("level","中")}；{wenli.get("direction","文理兼")}'
    po = shen.get('破坏_shen', [])
    if po:
        summary += f'；破坏之神({"、".join(po)})坏印食'

    return {
        'shen': shen,
        'level': level,
        'wenli': wenli,
        'level_str': level.get('level', '中'),
        'direction': wenli.get('direction', '文理兼'),
        'direction_signals': direction_brief(direction_result),
        'summary': summary,
    }


__all__ = [
    'classify_xueli_shen',
    'classify_xueli_level',
    'classify_wenli',
    'analyze_xueli',
]
