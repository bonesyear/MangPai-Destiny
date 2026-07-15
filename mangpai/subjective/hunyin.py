"""
hunyin - 盲派婚姻专辑·主观层（subjective）

理论来源：段建业《盲派中级命理学》第十章「婚姻专辑」（源文 4270-5393 行）
核心思想：男命以财星为妻、女命以官杀为夫，日支为婚姻宫。婚姻吉凶看妻/夫星
          与婚姻宫的喜忌、刑冲合害；多婚/独身/水中捞月看星宫结构与神煞；
          结离婚应期看大运流年引动妻/夫星与婚姻宫。

五项判定：
  1. 婚姻好坏：妻/夫星明现不被克破、婚姻宫(日支)为喜用不被冲合穿刑 -> 好；
     星被克破/争合/入墓、婚姻宫被冲合穿刑、男财多身弱/女官杀混杂伤官见官 -> 差。
  2. 多婚：男财星多(正偏财混杂)/女官杀多(正官七杀混杂)、婚姻宫被冲合多次、
     比劫克财(男)/伤官克官(女) -> 多婚（离婚再婚之象）。
  3. 独身：无妻星/夫星且婚姻宫坏、星入墓、纯阳/纯阴、华盖孤辰寡宿重 -> 独身（僧道/清居）。
  4. 水中捞月：妻/夫星与他人争合、或与日主合而被冲开 -> 婚姻虚象、求而不得。
  5. 结离婚应期：
     结婚--大运流年到妻/夫星、合妻/夫星、婚姻宫被合冲引动；
     离婚--男比劫到运年克财、女伤官到运年克官、妻/夫星被冲合走、婚姻宫被冲。

消费关系：
  - objective.zuogong_detect.detect_relations（日支冲合穿刑、星被克合）
  - objective.shensha.compute_shensha_ext（孤辰/寡宿/华盖/桃花/羊刃）
  - objective.binzhu.analyze_binzhu（主宾，星宫位置）
  - objective.constants（五行生克/藏干）

分层位置：subjective/，单向依赖 objective。本模块不反向依赖 engine。
已知争议：多婚/独身阈值为段氏主流口径启发式（星宫结构+神煞综合，非计数定量）；
          结离婚应期需大运流年输入，本模块给信号不给断言。
置信度：中
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, WX_KE, WX_SHENG, WX_KE_ME,
    TIAN_GAN_HE, LU, TOMB_MAP, LIU_CHONG, LIU_HE, LIU_HAI, XING_PAIRS,
    CANG_GAN_MANGPAI, PILLAR_KEYS, PILLAR_NAMES_CN, is_pillars,
)
from mangpai.objective.canggan import get_canggan_mangpai
from mangpai.objective.shensha import compute_shensha_ext, resolve_shensha
from mangpai.objective.zuogong_detect import detect_relations

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


def _spouse_star_cat(gender: str) -> str:
    """配偶星十神大类：男命=财，女命=官杀。"""
    return '财' if gender == '男' else '官杀'


def _spouse_wx(day_gan: str, gender: str) -> str:
    """配偶星五行：男=我克(财)，女=克我(官杀)。"""
    day_wx = GAN_WX.get(day_gan, '')
    if gender == '男':
        return WX_KE.get(day_wx, '')
    return WX_KE_ME.get(day_wx, '')


def _is_zhu(pos: str) -> bool:
    return pos.split('_')[0] in ('day', 'hour')


def _star_positions(day_gan: str, gans: List[str], zhis: List[str], gender: str) -> List[int]:
    """配偶星所在柱索引（天干或地支本/中气含配偶星五行）。"""
    swx = _spouse_wx(day_gan, gender)
    if not swx:
        return []
    out: List[int] = []
    for i in range(4):
        if GAN_WX.get(gans[i]) == swx:
            out.append(i)
            continue
        z = zhis[i]
        if ZHI_WX.get(z) == swx:
            out.append(i)
            continue
        # 中气藏干含配偶星
        for idx, (cg, _) in enumerate(get_canggan_mangpai(z)):
            if idx == 0:
                continue  # 本气已由主气五行覆盖
            if GAN_WX.get(cg) == swx:
                out.append(i)
                break
    return out


def _star_mingxian_count(day_gan: str, gans: List[str], zhis: List[str], gender: str) -> int:
    """配偶星明现柱数（天干+地支本/中气，余气不计）。"""
    swx = _spouse_wx(day_gan, gender)
    if not swx:
        return 0
    cnt = 0
    for i in range(4):
        hit = GAN_WX.get(gans[i]) == swx
        if not hit:
            z = zhis[i]
            if ZHI_WX.get(z) == swx:
                hit = True
            else:
                for idx, (cg, _) in enumerate(get_canggan_mangpai(z)):
                    if idx <= 1 and GAN_WX.get(cg) == swx:  # 本气/中气
                        hit = True
                        break
        if hit:
            cnt += 1
    return cnt


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


def _dayzhi_attacked(wa: List[Dict]) -> List[str]:
    """日支(婚姻宫)被冲/合/穿/刑的动作类型列表。"""
    kinds: List[str] = []
    for a in wa:
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if fp == 'day_zhi' or tp == 'day_zhi':
            t = a.get('type', '')
            if t in ('冲', '克', '穿', '刑', '破'):
                if '冲' not in kinds and t == '冲':
                    kinds.append('冲')
                if '穿' not in kinds and t == '穿':
                    kinds.append('穿')
                if '刑' not in kinds and t == '刑':
                    kinds.append('刑')
            elif t in ('地支合', '半合'):
                if '合' not in kinds:
                    kinds.append('合')
    return kinds


# ───────────────────── 1. 婚姻好坏 ─────────────────────

def classify_hunyin_quality(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """婚姻好坏判断。

    男命看财星(妻星)、女命看官杀(夫星)，日支为婚姻宫。
    好：配偶星明现不被克破、婚姻宫不被冲合穿刑、星宫得位（星在日支/主位）；
    差：星被克破/争合/入墓、婚姻宫被冲合穿刑、男财多身弱/女官杀混杂伤官见官。

    Returns:
        {'quality': '好'|'差'|'平', 'signals': [str], 'star_count': int, 'gong_attacked': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'quality': '平', 'signals': ['四柱不全'], 'star_count': 0, 'gong_attacked': []}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    star_count = _star_mingxian_count(day_gan, gans, zhis, gender)
    gong_attacked = _dayzhi_attacked(wa)

    signals: List[str] = []
    good = 0
    bad = 0

    # 星明现
    if star_count >= 1:
        signals.append(f'配偶星明现（{star_count}位）')
        good += 1
    else:
        signals.append('配偶星不明现')
        bad += 1
    # 星在日支(婚姻宫)得位
    day_idx = PILLAR_KEYS.index('day')
    day_zhi_wx = ZHI_WX.get(zhis[day_idx], '')
    swx = _spouse_wx(day_gan, gender)
    if day_zhi_wx == swx:
        signals.append('配偶星居婚姻宫（日支），星宫得位')
        good += 1
    # 婚姻宫被冲合穿刑
    if gong_attacked:
        signals.append(f'婚姻宫(日支)被{"、".join(gong_attacked)}')
        bad += len(gong_attacked)
    else:
        signals.append('婚姻宫(日支)安稳无冲合穿刑')
        good += 1
    # 争合（日干被两干以上合）
    if rel.get('zheng_he'):
        signals.append('日干争合，配偶星易被争')
        bad += 1
    # 男财多/女官杀混杂
    if gender == '男' and star_count >= 3:
        signals.append('男命财星多现（正偏财混杂），婚姻易不稳')
        bad += 1
    if gender == '女' and star_count >= 3:
        signals.append('女命官杀多现（官杀混杂），婚姻易不稳')
        bad += 1

    quality = '好' if good > bad else ('差' if bad > good else '平')
    return {
        'quality': quality,
        'signals': signals,
        'star_count': star_count,
        'gong_attacked': gong_attacked,
    }


# ───────────────────── 2. 多婚 ─────────────────────

def classify_duohun(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """多婚命理判定。

    男财星多(正偏财混杂)/女官杀多(正官七杀混杂)、婚姻宫被冲合多次、
    比劫克财(男)/伤官克官(女) -> 多婚（离婚再婚之象）。

    Returns:
        {'is_duohun': bool, 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_duohun': False, 'factors': ['四柱不全']}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    factors: List[str] = []
    star_count = _star_mingxian_count(day_gan, gans, zhis, gender)

    if star_count >= 3:
        factors.append(f'配偶星多现（{star_count}位，{"财星" if gender=="男" else "官杀"}混杂）')
    # 婚姻宫被冲+合（多次引动）
    gong_attacked = _dayzhi_attacked(wa)
    if '冲' in gong_attacked:
        factors.append('婚姻宫被冲，夫妻宫动')
    # 比劫克财(男)/伤官克官(女)
    cat = _spouse_star_cat(gender)
    killer = '比劫' if gender == '男' else '食伤'
    for a in wa:
        if a.get('type') in ('冲', '克', '穿', '刑'):
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            if fp and tp:
                f_idx = PILLAR_KEYS.index(fp.split('_')[0]) if fp.split('_')[0] in PILLAR_KEYS else -1
                t_idx = PILLAR_KEYS.index(tp.split('_')[0]) if tp.split('_')[0] in PILLAR_KEYS else -1
                if f_idx >= 0 and t_idx >= 0:
                    f_main = _main_cat(day_gan, gans, zhis, f_idx, fp)
                    t_main = _main_cat(day_gan, gans, zhis, t_idx, tp)
                    if f_main == killer and t_main == cat:
                        factors.append(f'{killer}克{cat}（{a.get("desc","")}），配偶星受克')
                        break

    return {'is_duohun': len(factors) >= 2 or star_count >= 3, 'factors': factors}


def _main_cat(day_gan, gans, zhis, idx, pos) -> str:
    """柱 idx 的主气十神大类（gan 取干，zhi 取本气藏干）。"""
    if pos.endswith('_gan'):
        g = gans[idx]
        c = _compute_shishen(day_gan, g)
        return _cat(c)
    canggan = get_canggan_mangpai(zhis[idx])
    return _cat(_compute_shishen(day_gan, canggan[0][0])) if canggan else ''


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


# ───────────────────── 3. 独身 ─────────────────────

def classify_dushen(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """独身命理判定。

    无配偶星且婚姻宫坏、星入墓、纯阳/纯阴、华盖孤辰寡宿重 -> 独身（僧道/清居）。

    Returns:
        {'is_dushen': bool, 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_dushen': False, 'factors': ['四柱不全']}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    factors: List[str] = []
    star_count = _star_mingxian_count(day_gan, gans, zhis, gender)

    if star_count == 0:
        factors.append('配偶星全无（无妻星/夫星）')
    gong_attacked = _dayzhi_attacked(wa)
    if gong_attacked:
        factors.append(f'婚姻宫被{"、".join(gong_attacked)}坏')

    # 纯阳/纯阴
    all_gans = [g for g in gans if g]
    all_yang = all(g in _YANG_GANS for g in all_gans)
    all_yin = all(g not in _YANG_GANS for g in all_gans)
    if all_gans and (all_yang or all_yin):
        factors.append('四柱天干纯' + ('阳' if all_yang else '阴') + '，性偏孤')

    # 神煞：华盖/孤辰/寡宿
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    lonely = [n for n in ('华盖', '孤辰', '寡宿') if shen.get(n, {}).get('in_pillars')]
    if lonely:
        factors.append('神煞孤（' + '、'.join(lonely) + '）')

    # 独身：无星+宫坏，或纯阳阴+孤神煞，或无星+孤神煞
    is_dushen = (star_count == 0 and bool(gong_attacked)) or \
                (all_gans and (all_yang or all_yin) and bool(lonely)) or \
                (star_count == 0 and bool(lonely))
    return {'is_dushen': is_dushen, 'factors': factors}


# ───────────────────── 4. 水中捞月 ─────────────────────

def detect_shuizhong_laoyue(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """水中捞月：婚姻虚象、求而不得。

    配偶星与他人争合（非日主）、或与日主合而被冲开 -> 水中捞月。
    星明现却被合走/合住不得、或星与他柱合 -> 求而不得。

    Returns:
        {'is_laoyue': bool, 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_laoyue': False, 'factors': ['四柱不全']}

    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    factors: List[str] = []
    swx = _spouse_wx(day_gan, gender)
    star_idxs = _star_positions(day_gan, gans, zhis, gender)

    # 配偶星(天干)与他人合（非日干合）
    for a in wa:
        if a.get('type') == '天干合':
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            # 日干合配偶星=正合（非捞月）；非日干之间合配偶星=争合
            if 'day_gan' in (fp, tp):
                continue
            for pk in (fp, tp):
                if pk.endswith('_gan'):
                    idx = PILLAR_KEYS.index(pk.split('_')[0])
                    if idx < len(gans) and GAN_WX.get(gans[idx]) == swx:
                        factors.append(f'配偶星({gans[idx]})与他干合（{a.get("desc","")}），婚象被他合走')
                        break
    # 争合（日干被两干以上合）
    if rel.get('zheng_he') and star_idxs:
        factors.append('日干争合，配偶星被争（求而不得）')

    # 婚姻宫被冲（合而被冲开之象）
    gong_attacked = _dayzhi_attacked(wa)
    if '冲' in gong_attacked and star_idxs:
        factors.append('婚姻宫被冲，婚象冲散（水中捞月）')

    return {'is_laoyue': bool(factors), 'factors': factors}


# ───────────────────── 5/6. 结离婚应期 ─────────────────────

def infer_jiehun_yingqi(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男',
    dayun_gan: str = '', dayun_zhi: str = '',
    liunian_gan: str = '', liunian_zhi: str = '',
) -> Dict:
    """结婚应期：大运流年引动配偶星/婚姻宫。

    信号：大运流年干为配偶星(到星)、大运流年支合/冲婚姻宫(日支)、
          大运流年与日干合(合星)。多信号齐备为结婚应期。

    Returns:
        {'is_jiehun_signal': bool, 'signals': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    swx = _spouse_wx(day_gan, gender)
    day_zhi = zhis[PILLAR_KEYS.index('day')] if len(zhis) == 4 else ''
    signals: List[str] = []

    for label, dgan, dzhi in (('大运', dayun_gan, dayun_zhi), ('流年', liunian_gan, liunian_zhi)):
        if not dgan and not dzhi:
            continue
        if dgan and GAN_WX.get(dgan) == swx:
            signals.append(f'{label}干{dgan}为配偶星（到星），结婚应期信号')
        if dzhi and day_zhi:
            if (dzhi, day_zhi) in LIU_HE or (day_zhi, dzhi) in LIU_HE:
                signals.append(f'{label}支{dzhi}合婚姻宫{day_zhi}，引动夫妻宫')
            if (dzhi, day_zhi) in LIU_CHONG or (day_zhi, dzhi) in LIU_CHONG:
                signals.append(f'{label}支{dzhi}冲婚姻宫{day_zhi}，宫动婚成')
        if dgan and TIAN_GAN_HE.get(day_gan) == dgan:
            signals.append(f'{label}干{dgan}合日干（合星），婚配应期')

    return {'is_jiehun_signal': len(signals) >= 1, 'signals': signals}


def infer_lihun_yingqi(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男',
    dayun_gan: str = '', dayun_zhi: str = '',
    liunian_gan: str = '', liunian_zhi: str = '',
) -> Dict:
    """离婚应期：大运流年克配偶星/冲婚姻宫。

    男命比劫到运年克财、女命伤官到运年克官；配偶星被冲合走；婚姻宫被冲 -> 离婚信号。

    Returns:
        {'is_lihun_signal': bool, 'signals': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    day_wx = GAN_WX.get(day_gan, '')
    swx = _spouse_wx(day_gan, gender)
    # 克配偶星之物：男财被比劫(同我)克、女官被食伤(我生)克
    killer_wx = day_wx if gender == '男' else WX_SHENG.get(day_wx, '')
    day_zhi = zhis[PILLAR_KEYS.index('day')] if len(zhis) == 4 else ''
    signals: List[str] = []

    for label, dgan, dzhi in (('大运', dayun_gan, dayun_zhi), ('流年', liunian_gan, liunian_zhi)):
        if not dgan and not dzhi:
            continue
        if dgan and killer_wx and GAN_WX.get(dgan) == killer_wx:
            star = '财(妻)' if gender == '男' else '官(夫)'
            killer = '比劫' if gender == '男' else '伤官'
            signals.append(f'{label}干{dgan}为{killer}，克{star}星，离婚信号')
        if dzhi and day_zhi and ((dzhi, day_zhi) in LIU_CHONG or (day_zhi, dzhi) in LIU_CHONG):
            signals.append(f'{label}支{dzhi}冲婚姻宫{day_zhi}，夫妻宫动散')
        if dzhi and swx and ZHI_WX.get(dzhi) == swx:
            # 运年支为配偶星(到星)亦可能引动婚变（星到而宫坏）
            pass

    return {'is_lihun_signal': len(signals) >= 1, 'signals': signals}


# ───────────────────── 7. 关财门 / 禄绊桃花（高级篇 ch9 扩展） ─────────────────────

def _star_in_tomb(day_gan: str, gans: List[str], zhis: List[str], gender: str) -> List[str]:
    """配偶星是否入墓：配偶星五行被局中墓库支收（TOMB_MAP）。

    返回收星之墓支列表（如配偶星五行=木，局有未→未收木入墓）。
    """
    swx = _spouse_wx(day_gan, gender)
    if not swx:
        return []
    tombs: List[str] = []
    for z in zhis:
        if not z:
            continue
        if swx in TOMB_MAP.get(z, []):
            tombs.append(z)
    return tombs


def detect_guan_caimen(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """关财门（高级篇 ch9）：配偶星入墓或被合锁，婚姻门关。

    男命财门=财星，女命官门=官杀。配偶星入墓（墓库收星五行）或被地支合锁住
    无冲开 -> 财门/官门关，婚姻难成或丧偶之象。与「水中捞月」区别：关财门是
    星被锁死（入墓/合住），捞月是星被合走（求而不得）。

    Returns:
        {'is_guanmen': bool, 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_guanmen': False, 'factors': ['四柱不全']}
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    factors: List[str] = []
    door = '财门' if gender == '男' else '官门'

    # 入墓
    tombs = _star_in_tomb(day_gan, gans, zhis, gender)
    if tombs:
        # 入墓且墓不开（无冲刑开库）方为关门
        opened = any(a.get('type') in ('冲', '刑') for a in wa
                     if (a.get('from_pos', '').split('_')[0] in PILLAR_KEYS and
                         zhis[PILLAR_KEYS.index(a.get('from_pos', '').split('_')[0])] in tombs) or
                     (a.get('to_pos', '').split('_')[0] in PILLAR_KEYS and
                      zhis[PILLAR_KEYS.index(a.get('to_pos', '').split('_')[0])] in tombs))
        if not opened:
            factors.append(f'配偶星入墓{"".join(set(tombs))}且墓不开，{door}关')

    # 配偶星支被合锁（地支合/半合锁住配偶星所在支，无冲开）
    star_idxs = _star_positions(day_gan, gans, zhis, gender)
    star_zhis = {zhis[i] for i in star_idxs if i < len(zhis) and zhis[i]}
    locked: Set[str] = set()
    for a in wa:
        if a.get('type') not in ('地支合', '半合'):
            continue
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        for pk in (fp, tp):
            k = pk.split('_')[0]
            if pk.endswith('_zhi') and k in PILLAR_KEYS:
                zv = zhis[PILLAR_KEYS.index(k)]
                if zv in star_zhis:
                    locked.add(zv)
    if locked:
        factors.append(f'配偶星支{"".join(locked)}被合锁，{door}闭')

    return {'is_guanmen': bool(factors), 'factors': factors}


def detect_lu_ban_taohua(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """禄绊桃花（高级篇 ch9）：日干之禄与桃花同柱或相合，禄被桃花绊。

    禄=日主身体临官位，桃花=情欲。禄与桃花同支、或桃花合禄支（地支合/半合），
    -> 禄被桃花绊住，主情欲重、为情所累（禄受桃花之累）。男女同论。

    Returns:
        {'is_lu_ban': bool, 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_lu_ban': False, 'factors': ['四柱不全']}
    day_lu = LU.get(day_gan, '')
    if not day_lu or day_lu not in zhis:
        return {'is_lu_ban': False, 'factors': []}
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    th = (shen.get('桃花') or {}).get('zhi', '')
    if not th:
        return {'is_lu_ban': False, 'factors': []}
    factors: List[str] = []
    if th == day_lu:
        factors.append(f'禄({day_lu})与桃花同支，禄桃花同柱，禄受情欲之累')
    else:
        rel = _ensure_relations(day_gan, gans, zhis, relations)
        wa: List[Dict] = rel.get('work_actions') or []
        for a in wa:
            if a.get('type') not in ('地支合', '半合'):
                continue
            fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
            pair = set()
            for pk in (fp, tp):
                k = pk.split('_')[0]
                if pk.endswith('_zhi') and k in PILLAR_KEYS:
                    pair.add(zhis[PILLAR_KEYS.index(k)])
            if {th, day_lu} <= pair:
                factors.append(f'桃花{th}合禄{day_lu}（{a.get("desc","")}），禄被桃花绊')
                break
    return {'is_lu_ban': bool(factors), 'factors': factors}


# ───────────────────── 8. 结婚四法 / 独身四格 ─────────────────────

def classify_jiehun_sifa(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """结婚四法（高级篇 ch9）：命局倾向的四种成婚方式（原局结构层面）。

      法一·星来合身：配偶星天干合日干（星主动来合日主）；
      法二·合动夫妻宫：日支（婚姻宫）被地支合/半合引动；
      法三·星居主位：配偶星在日/时柱（主位），星到主位易成婚；
      法四·桃花合宫：桃花支合日支或桃花居日支，桃花引动婚姻宫。
    与 infer_jiehun_yingqi 区别：yingqi 看大运流年引动（时间触发），本函数看
    原局结构倾向（成婚方式配置）。

    Returns:
        {'methods': [str], 'primary': str}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'methods': [], 'primary': ''}
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    swx = _spouse_wx(day_gan, gender)
    methods: List[str] = []
    day_idx = PILLAR_KEYS.index('day')
    day_zhi = zhis[day_idx]

    # 法一·星来合身：配偶星干合日干
    he_gan = TIAN_GAN_HE.get(day_gan, '')
    if he_gan and GAN_WX.get(he_gan) == swx:
        methods.append('星来合身（配偶星干合日干）')

    # 法二·合动夫妻宫：日支被地支合/半合
    gong_he = any(a.get('type') in ('地支合', '半合') and
                  (a.get('from_pos') == 'day_zhi' or a.get('to_pos') == 'day_zhi')
                  for a in wa)
    if gong_he:
        methods.append('合动夫妻宫（日支被合引动）')

    # 法三·星居主位：配偶星在日/时柱
    star_idxs = _star_positions(day_gan, gans, zhis, gender)
    if any(i in (day_idx, PILLAR_KEYS.index('hour')) for i in star_idxs):
        methods.append('星居主位（配偶星在日/时柱）')

    # 法四·桃花合宫/居宫
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    th = (shen.get('桃花') or {}).get('zhi', '')
    if th:
        if th == day_zhi:
            methods.append('桃花居夫妻宫')
        else:
            th_he_gong = any(a.get('type') in ('地支合', '半合') for a in wa
                             if th in {zhis[PILLAR_KEYS.index(a.get('from_pos', '').split('_')[0])]
                                       if a.get('from_pos', '').split('_')[0] in PILLAR_KEYS else '',
                                       zhis[PILLAR_KEYS.index(a.get('to_pos', '').split('_')[0])]
                                       if a.get('to_pos', '').split('_')[0] in PILLAR_KEYS else ''})
            if th_he_gong:
                methods.append('桃花合夫妻宫')

    primary = methods[0] if methods else '无明显成婚结构'
    return {'methods': methods, 'primary': primary}


def classify_dushen_sige(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """独身四格（高级篇 ch9）：独身命的四种格局细分。

      格一·无星宫坏：配偶星全无且婚姻宫被冲合穿刑；
      格二·星入墓：配偶星入墓且墓不开（关财门/官门）；
      格三·纯阳纯阴孤神：四柱天干纯阳或纯阴+孤辰寡宿/华盖；
      格四·华盖重见/僧道：华盖≥2位或孤辰寡宿并现，性孤向道。
    为 classify_dushen 的格局细分（不替代其综合判定）。

    Returns:
        {'grids': [str], 'is_dushen': bool}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'grids': [], 'is_dushen': False}
    rel = _ensure_relations(day_gan, gans, zhis, relations)
    wa: List[Dict] = rel.get('work_actions') or []
    grids: List[str] = []
    star_count = _star_mingxian_count(day_gan, gans, zhis, gender)
    gong_attacked = _dayzhi_attacked(wa)

    # 格一·无星宫坏
    if star_count == 0 and gong_attacked:
        grids.append('无星宫坏格')
    # 格二·星入墓（关财门）
    guanmen = detect_guan_caimen(day_gan, gans, zhis, gender, relations)
    if guanmen.get('is_guanmen') and any('入墓' in f for f in guanmen.get('factors', [])):
        grids.append('星入墓格')
    # 格三·纯阳纯阴孤神
    all_gans = [g for g in gans if g]
    all_yang = bool(all_gans) and all(g in _YANG_GANS for g in all_gans)
    all_yin = bool(all_gans) and all(g not in _YANG_GANS for g in all_gans)
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    lonely = [n for n in ('孤辰', '寡宿') if shen.get(n, {}).get('in_pillars')]
    if (all_yang or all_yin) and lonely:
        grids.append('纯阳纯阴孤神格')
    # 格四·华盖重见/僧道
    huagai_pillars = shen.get('华盖', {}).get('in_pillars', [])
    if len(huagai_pillars) >= 2 or len(lonely) >= 2:
        grids.append('华盖重见僧道格')

    return {'grids': grids, 'is_dushen': len(grids) >= 1}


# ───────────────────── 聚合 ─────────────────────

def analyze_hunyin(
    day_gan: str = '',
    gans: Optional[List[str]] = None,
    zhis: Optional[List[str]] = None,
    gender: str = '男',
    *,
    dayun_gan: str = '', dayun_zhi: str = '',
    liunian_gan: str = '', liunian_zhi: str = '',
    relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """婚姻综合：好坏 + 多婚 + 独身 + 水中捞月 + 关财门 + 禄绊桃花
    + 结婚四法 + 独身四格 + 结离婚应期。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。

    Returns:
        {
          'quality': {...}, 'duohun': {...}, 'dushen': {...}, 'laoyue': {...},
          'guan_caimen': {...}, 'lu_ban_taohua': {...},
          'jiehun_sifa': {...}, 'dushen_sige': {...},
          'jiehun_yingqi': {...}, 'lihun_yingqi': {...},
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

    # 神煞：优先用 engine 透传值，缺省才就地重算（孤辰/寡宿/华盖/桃花/羊刃）
    ss = resolve_shensha(day_gan, zhis or [], shensha_result)

    quality = classify_hunyin_quality(day_gan, gans or [], zhis or [], gender, relations)
    duohun = classify_duohun(day_gan, gans or [], zhis or [], gender, relations)
    dushen = classify_dushen(day_gan, gans or [], zhis or [], gender, relations,
                             shensha_result=ss)
    laoyue = detect_shuizhong_laoyue(day_gan, gans or [], zhis or [], gender, relations)
    guanmen = detect_guan_caimen(day_gan, gans or [], zhis or [], gender, relations)
    luban = detect_lu_ban_taohua(day_gan, gans or [], zhis or [], gender, relations,
                                 shensha_result=ss)
    jiehun_fa = classify_jiehun_sifa(day_gan, gans or [], zhis or [], gender, relations,
                                     shensha_result=ss)
    dushen_ge = classify_dushen_sige(day_gan, gans or [], zhis or [], gender, relations,
                                    shensha_result=ss)
    jiehun = infer_jiehun_yingqi(day_gan, gans or [], zhis or [], gender,
                                 dayun_gan, dayun_zhi, liunian_gan, liunian_zhi)
    lihun = infer_lihun_yingqi(day_gan, gans or [], zhis or [], gender,
                               dayun_gan, dayun_zhi, liunian_gan, liunian_zhi)

    parts = [f'婚姻{quality.get("quality","平")}']
    if duohun.get('is_duohun'):
        parts.append('多婚之象')
    if dushen.get('is_dushen') or dushen_ge.get('is_dushen'):
        grids = dushen_ge.get('grids', [])
        parts.append('独身之象' + (f'（{",".join(grids)}）' if grids else ''))
    if laoyue.get('is_laoyue'):
        parts.append('水中捞月(婚虚)')
    if guanmen.get('is_guanmen'):
        parts.append('关财门(星被锁)')
    if luban.get('is_lu_ban'):
        parts.append('禄绊桃花')
    if jiehun_fa.get('methods'):
        parts.append('成婚法：' + jiehun_fa['methods'][0])
    if jiehun.get('is_jiehun_signal'):
        parts.append('有结婚应期信号')
    if lihun.get('is_lihun_signal'):
        parts.append('有离婚应期信号')

    return {
        'quality': quality,
        'duohun': duohun,
        'dushen': dushen,
        'laoyue': laoyue,
        'guan_caimen': guanmen,
        'lu_ban_taohua': luban,
        'jiehun_sifa': jiehun_fa,
        'dushen_sige': dushen_ge,
        'jiehun_yingqi': jiehun,
        'lihun_yingqi': lihun,
        'summary': '；'.join(parts),
    }


__all__ = [
    'classify_hunyin_quality',
    'classify_duohun',
    'classify_dushen',
    'detect_shuizhong_laoyue',
    'detect_guan_caimen',
    'detect_lu_ban_taohua',
    'classify_jiehun_sifa',
    'classify_dushen_sige',
    'infer_jiehun_yingqi',
    'infer_lihun_yingqi',
    'analyze_hunyin',
]
