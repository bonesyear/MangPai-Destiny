"""
hunyin - 盲派婚姻专辑·主观层（subjective）

理论来源：段建业《盲派中级命理学》第十章「婚姻专辑」（源文 4270-5393 行）
核心思想：男命以财星为妻、女命以官杀为夫，日支为婚姻宫。婚姻吉凶看妻/夫星
          与婚姻宫的喜忌、刑冲合害；多婚/独身/水中捞月看星宫结构与神煞；
          结离婚应期看大运流年引动妻/夫星与婚姻宫。

五项判定（F16 按书重写前四项机制，锚 zhongji 婚姻章 4271-5393/gaoji 9.2-9.3）：
  1. 婚姻好坏：宫为主星为辅——宫安静/宫制去夫妻星忌神（制得住）/宫为忌被
     星制去/星合入宫/宫坐库喜刑冲 -> 好；宫有用被刑冲破穿/合他星/制不住
     反坏/杂透多现/比劫争夫争妻 -> 差。冲穿刑非一律凶（:4294/4300/4493/4504）。
  2. 多婚：男财星多(正偏财混杂)/女官杀多(正官七杀混杂)、婚姻宫被冲合多次、
     比劫克财(男)/伤官克官(女) -> 多婚（离婚再婚之象）。
  3. 独身四格：宫占比劫禄印星难入/宫星互害反成克/星入墓库不开/水中捞月
     偏星扰（gaoji:13068-13070/zhongji:4924-4928）。
  4. 水中捞月三要素：正星坐宫+日主与日支自合+天干偏星干扰
     （zhongji:5081-5083）-> 理想过高、求而不得。
  5. 结离婚应期：
     结婚--大运流年到妻/夫星、合妻/夫星、婚姻宫被合冲引动；
     离婚--男比劫到运年克财、女伤官到运年克官、妻/夫星被冲合走、婚姻宫被冲；
     女命关财门--运岁比劫夺财（财是官之原神），gaoji:12963-12967。

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
from mangpai.subjective.yongshen import assess_direction_signals, direction_brief
from mangpai.subjective.zhengfan import _compute_qishi

_YANG_GANS = set('甲丙戊庚壬')

# 势党（书第一章口径，复用 zhengfan._compute_qishi）：金水湿土党/火土燥土党。
# 婚姻喜忌由此定：宫方成势则星为忌、星方成势则宫为忌（zhongji:4294/4300/4340）。
_SHI_ZHIS = frozenset('申酉亥子丑辰')
_ZAO_ZHIS = frozenset('巳午未戌')
_KU_ZHIS = frozenset('辰戌丑未')


def _zhi_party(z: str) -> str:
    if z in _SHI_ZHIS:
        return 'shi'
    if z in _ZAO_ZHIS:
        return 'zao'
    return ''


def _qishi_dang(gans: List[str], zhis: List[str]) -> Dict:
    """成势之党与对方党计数（{'dang': 'shi'/'zao'/'', 'opp': int}）。

    婚姻喜忌由此定：宫方成势则星为忌、星方成势则宫为忌（zhongji:4294/4300/4340）；
    对方党 ≥2 为「制不住」（书「原局水火之力量相当…制不住夫星」:4303-4308）。
    仅采书明文势党（复用 zhengfan._compute_qishi），单向/两神不定喜忌。
    """
    try:
        q = _compute_qishi(gans, zhis)
    except Exception:
        q = None
    if not (q and q.get('kind') == '势党'):
        return {'dang': '', 'opp': 0}
    dang = 'shi' if q.get('pair') == ['金', '水'] else 'zao'
    counts = {wx: 0 for wx in ('金', '水', '火')}
    for g in (gans or []):
        if GAN_WX.get(g) in counts:
            counts[GAN_WX[g]] += 1
    for z in (zhis or []):
        if ZHI_WX.get(z) in counts:
            counts[ZHI_WX[z]] += 1
    shi = counts['金'] + counts['水'] + sum(1 for z in (zhis or []) if z in ('丑', '辰'))
    zao = counts['火'] + sum(1 for z in (zhis or []) if z in ('未', '戌'))
    return {'dang': dang, 'opp': zao if dang == 'shi' else shi}


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


def _is_star_zhi(day_gan: str, z: str, gender: str) -> bool:
    """支是否为配偶星之支（本气或藏干含配偶星五行，含余气——戴安娜丑中辛锚）。"""
    swx = _spouse_wx(day_gan, gender)
    if not swx or not z:
        return False
    if ZHI_WX.get(z) == swx:
        return True
    return any(GAN_WX.get(cg) == swx for cg, _q in get_canggan_mangpai(z))


def _zhi_main_cat(day_gan: str, z: str) -> str:
    """支本气十神大类（合宫对象判印/禄用，zhongji:4351）。"""
    cg = get_canggan_mangpai(z)
    return _cat(_compute_shishen(day_gan, cg[0][0])) if cg else ''


def _gong_actions(wa: List[Dict], zhis: List[str]) -> tuple:
    """日支(婚姻宫)涉入的作用拆两类：冲穿刑(攻制) / 合(地支合·半合·暗合)。

    每项 (type, other_zhi, action)；自刑（同支）非攻击，排除
    （zhenbao-05 锚：自刑/伏吟非反制）。
    """
    day_zhi = zhis[PILLAR_KEYS.index('day')]
    adv: List = []
    he: List = []
    for a in wa:
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        if 'day_zhi' not in (fp, tp):
            continue
        other = tp if fp == 'day_zhi' else fp
        k = other.split('_')[0]
        if k not in PILLAR_KEYS or not other.endswith('_zhi'):
            continue
        oz = zhis[PILLAR_KEYS.index(k)]
        t = a.get('type', '')
        if t in ('冲', '穿', '刑'):
            if oz == day_zhi:
                continue  # 自刑
            adv.append((t, oz, a))
        elif t in ('地支合', '半合', '暗合'):
            he.append((oz, a))
    return adv, he


# ───────────────────── 1. 婚姻好坏 ─────────────────────

# 宫/星加权（M3）：源文《盲派中级命理学》第十章第一节「看婚姻的好坏，应以
# 配偶宫为主，配偶星为辅」——宫为主（权重×2）、星为辅（权重×1）。
# 破坏程度分档（源文「能否离婚，却要看夫妻宫破坏到什么程度」）：
#   穿=2.0（穿倒最重，盲派"穿坏即灾"）；冲=1.5（正面对抗）；
#   合=1.5（六合/暗合他星，合走配偶）；刑=1.0、破=1.0（较轻）。
_GONG_ATTACK_W = {'穿': 2.0, '冲': 1.5, '合': 1.5, '刑': 1.0, '破': 1.0}
_GONG_SAFE_W = 2.0        # 宫位安静（宫为主，安稳为婚姻好之基）
_STAR_MINGXIAN_W = 1.0    # 配偶星明现（星为辅）
_STAR_IN_GONG_W = 1.0     # 配偶星居婚姻宫（得位）
_STAR_ABSENT_W = -1.0     # 配偶星不明现
_ZHENG_HE_W = -1.0        # 争合（比劫争夫/争妻，第三者之象）
_STAR_MIXED_W = -1.0      # 星杂透多现（正偏混杂）
# 阈值：好须宫星俱善（≥2.0）；差为净负分（<0，宫坏为主即落差）；其间为平。
_QUALITY_GOOD_MIN = 2.0


def classify_hunyin_quality(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """婚姻好坏判断（M3：星/宫/破坏程度加权，替代等权一票制）。

    男命看财星(妻星)、女命看官杀(夫星)，日支为婚姻宫。
    加权口径（源文：宫为主、星为辅；破坏程度定吉凶深浅）：
      宫：安稳 +2.0；被穿 -2.0 / 冲 -1.5 / 合(他星) -1.5 / 刑 -1.0 / 破 -1.0；
      星：明现 +1.0、居宫得位 +1.0、不明现 -1.0、争合 -1.0、杂透多现 -1.0。

    Returns:
        {'quality': '好'|'差'|'平', 'score': float, 'signals': [str],
         'star_count': int, 'gong_attacked': [str]}
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
    score = 0.0

    # 星明现（星为辅 ±1.0）
    if star_count >= 1:
        signals.append(f'配偶星明现（{star_count}位）')
        score += _STAR_MINGXIAN_W
    else:
        signals.append('配偶星不明现')
        score += _STAR_ABSENT_W
    # 星在日支(婚姻宫)得位（+1.0）
    day_idx = PILLAR_KEYS.index('day')
    day_zhi_wx = ZHI_WX.get(zhis[day_idx], '')
    swx = _spouse_wx(day_gan, gender)
    if day_zhi_wx == swx:
        signals.append('配偶星居婚姻宫（日支），星宫得位')
        score += _STAR_IN_GONG_W
    # ── 婚姻宫（宫为主）：冲穿刑非一律凶，按书喜忌定吉凶（F16 重写）──
    # 书口径（zhongji:4286-4351）：宫安静=好；宫制去夫妻星忌神（制得住）=好；
    # 宫为忌被夫妻星制去=较好；宫有用被刑冲破穿/合他星=差；宫坐库喜刑冲（开库）；
    # 合正偏印与禄不论坏（:4351）；制不住反为坏婚姻（:4290，戴安娜:4516-4518）。
    adv, he_acts = _gong_actions(wa, zhis)
    day_zhi = zhis[day_idx]
    qs = _qishi_dang(gans, zhis)
    dang, opp = qs['dang'], qs['opp']
    gong_attacked = sorted({t for t, _oz, _a in adv} | ({'合'} if he_acts else set()))

    # 宫坐四库：非星支之冲/刑/穿=开库为喜（库喜刑冲，zhongji:4493/4500；
    # 「无刑冲克破者也易独身」:4927），免罚；星支攻制仍入宫星互制（戴安娜
    # 未被戌刑坏=制不住 :4516-4518，不开库）
    ku_open = False
    if day_zhi in _KU_ZHIS and adv:
        kept = []
        for t, oz, a in adv:
            if not _is_star_zhi(day_gan, oz, gender):
                ku_open = True
            else:
                kept.append((t, oz, a))
        adv = kept
    if ku_open:
        signals.append(f'婚姻宫坐库（{day_zhi}），刑冲开库为喜（库喜刑冲）')
        score += 1.0

    star_adv = [(t, oz, a) for t, oz, a in adv if _is_star_zhi(day_gan, oz, gender)]
    nonstar_adv = [(t, oz, a) for t, oz, a in adv
                   if not _is_star_zhi(day_gan, oz, gender)]
    gong_good = False
    if star_adv and dang:
        gong_dang = _zhi_party(day_zhi)
        star_dangs = {_zhi_party(oz) for _t, oz, _a in star_adv}
        if gong_dang == dang and dang not in star_dangs \
                and len(star_adv) == 1 and not nonstar_adv and opp < 2:
            # 宫制去夫妻星忌神且制得住→好婚姻（zhongji:4289-4294/4300）
            signals.append('婚姻宫制去夫妻星忌神（宫方成势，制之得住），好婚姻')
            score += 2.0
            gong_good = True
        elif dang in star_dangs and gong_dang != dang:
            # 配偶宫为忌神被夫妻星制去（去之为吉），婚姻较好（zhongji:4291/4340/4504）
            signals.append('配偶宫为忌神，被夫妻星制去（去之为吉），婚姻较好')
            score += 2.0
            gong_good = True

    # 合宫三分（zhongji:4351/4318）：星合入宫=吉；合印/禄=不论坏；合他星=差
    he_bad: List[str] = []
    for oz, a in he_acts:
        if _is_star_zhi(day_gan, oz, gender):
            signals.append(f'配偶星({oz})合入婚姻宫，星宫相合为吉')
            score += 1.0
        elif _zhi_main_cat(day_gan, oz) not in ('印', '比劫'):
            he_bad.append(oz)

    if gong_good:
        loss = len(he_bad) * _GONG_ATTACK_W['合']
        if loss:
            signals.append(f'婚姻宫(日支)合他星{"、".join(he_bad)}（破坏度-{loss:g}）')
            score -= loss
    elif adv or he_bad:
        loss = sum(_GONG_ATTACK_W.get(t, 1.0) for t, _oz, _a in adv)
        loss += len(he_bad) * _GONG_ATTACK_W['合']
        kinds = [t for t, _oz, _a in adv] + (['合'] if he_bad else [])
        signals.append(f'婚姻宫(日支)被{"、".join(kinds)}（破坏度-{loss:g}）')
        score -= loss
    else:
        signals.append('婚姻宫(日支)安稳无冲合穿刑')
        score += _GONG_SAFE_W
    # 争合（日干被两干以上合）
    if rel.get('zheng_he'):
        signals.append('日干争合，配偶星易被争')
        score += _ZHENG_HE_W
    # 男财多/女官杀混杂
    if gender == '男' and star_count >= 3:
        signals.append('男命财星多现（正偏财混杂），婚姻易不稳')
        score += _STAR_MIXED_W
    if gender == '女' and star_count >= 3:
        signals.append('女命官杀多现（官杀混杂），婚姻易不稳')
        score += _STAR_MIXED_W

    quality = '好' if score >= _QUALITY_GOOD_MIN else ('差' if score < 0 else '平')
    return {
        'quality': quality,
        'score': round(score, 2),
        'signals': signals,
        'star_count': star_count,
        'gong_attacked': gong_attacked,
    }


# ───────────────────── 2. 多婚 ─────────────────────

def classify_duohun(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """多婚命理判定（M3 补三检测）。

    男财星多(正偏财混杂)/女官杀多(正官七杀混杂)、婚姻宫被冲合多次、
    比劫克财(男)/伤官克官(女) -> 多婚（离婚再婚之象）。
    M3 补（源文第二节规则1 + 高级篇盖头）：配偶星被穿/破/冲、
    劫财(男)/伤官(女)盖头配偶星、配偶星入墓。

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
            # 日主克财=「我克者财」（正常得财），非比劫夺财/伤官克官，
            # 与 yongshen.detect_bijiao_duocai 的 day_gan 排除同口径。
            if fp == 'day_gan':
                continue
            if fp and tp:
                f_idx = PILLAR_KEYS.index(fp.split('_')[0]) if fp.split('_')[0] in PILLAR_KEYS else -1
                t_idx = PILLAR_KEYS.index(tp.split('_')[0]) if tp.split('_')[0] in PILLAR_KEYS else -1
                if f_idx >= 0 and t_idx >= 0:
                    f_main = _main_cat(day_gan, gans, zhis, f_idx, fp)
                    t_main = _main_cat(day_gan, gans, zhis, t_idx, tp)
                    if f_main == killer and t_main == cat:
                        factors.append(f'{killer}克{cat}（{a.get("desc","")}），配偶星受克')
                        break

    # ── M3 补三检测（源文第二节多婚规则 + 高级篇盖头）──
    swx = _spouse_wx(day_gan, gender)
    # 本气配偶星支（被穿/破/冲仅认本气：中气藏星过弱，免误检——如 zb04 未中乙财
    # 被丑未冲误中，书断"妻好无事"）
    star_zhis_main: Set[str] = {z for z in zhis if z and ZHI_WX.get(z) == swx}
    # 本/中气配偶星支（盖头用：克星干坐于藏星之支上同柱相克）
    star_zhis_all: Set[str] = set(star_zhis_main)
    for i in range(4):
        z = zhis[i]
        if not z or z in star_zhis_all:
            continue
        for idx, (cg, _) in enumerate(get_canggan_mangpai(z)):
            if idx <= 1 and GAN_WX.get(cg) == swx:  # 本/中气藏配偶星
                star_zhis_all.add(z)
                break
    # 1. 配偶星被穿/破/冲（源文规则1：「夫妻宫穿了夫妻星的那个字，必离婚（可以冲）」，
    #    推及配偶星所在支被穿/破/冲即为多婚标志）
    for a in wa:
        t = a.get('type', '')
        if t not in ('穿', '破', '冲'):
            continue
        hit_zhi, via_gong = None, False
        for pk in (a.get('from_pos', ''), a.get('to_pos', '')):
            k = pk.split('_')[0]
            if pk.endswith('_zhi') and k in PILLAR_KEYS:
                zv = zhis[PILLAR_KEYS.index(k)]
                if zv in star_zhis_main:
                    hit_zhi = zv
                    if (a.get('from_pos') == 'day_zhi' or a.get('to_pos') == 'day_zhi'):
                        via_gong = True
        if hit_zhi:
            gong_note = '，夫妻宫{0}夫妻星（源文：必离婚）'.format(t) if via_gong else ''
            factors.append(f'配偶星({hit_zhi})被{t}{gong_note}，多婚标志')
            break
    # 2. 盖头劫财(男)/盖头伤官(女)（高级篇：「酉金财星被丁火劫财盖头」、
    #    「酉金正官为夫星，但被丁火盖头」——克星干坐配偶星支上，同柱相克）
    for i in range(4):
        if i == PILLAR_KEYS.index('day'):
            continue
        g, z = gans[i], zhis[i]
        if not g or not z or z not in star_zhis_all:
            continue
        if _cat(_compute_shishen(day_gan, g)) == killer and WX_KE.get(GAN_WX.get(g, '')) == swx:
            factors.append(f'{killer}({g})盖头配偶星({z})，同柱相克，婚不稳')
            break
    # 3. 配偶星入墓（星入墓库，婚缘受损，多婚/婚变标志之一）。
    #    须配偶星明现于天干或地支本气方论入墓——仅中气藏星且该星即藏于墓库
    #    自身者（如未中乙）为"星藏于库"，非星被收墓，不计（免 zb04 误中）。
    tombs = _star_in_tomb(day_gan, gans, zhis, gender)
    if tombs:
        star_mingxian = bool(star_zhis_main) or any(
            g and GAN_WX.get(g) == swx for g in gans)
        if star_mingxian:
            factors.append(f'配偶星入{"".join(sorted(set(tombs)))}墓，婚缘受损')

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
    """独身命理判定（F16：书独身=四格，委托 classify_dushen_sige）。

    书诀 gaoji:13068-13070/zhongji:4924-4928：宫占比劫禄印/宫星互害反成克/
    星入墓库不开/水中捞月偏星扰。旧「无星宫坏/纯阳纯阴/华盖孤辰寡宿」条款
    无书锚（「华盖」四书 grep 0 命中），已废。

    Returns:
        {'is_dushen': bool, 'factors': [str]}
    """
    sige = classify_dushen_sige(day_gan, gans, zhis, gender, relations,
                                shensha_result=shensha_result)
    return {'is_dushen': sige.get('is_dushen', False),
            'factors': sige.get('grids', [])}


# ───────────────────── 4. 水中捞月 ─────────────────────

# 正星之偏（偏星干扰用，zhongji:5081-5083；扩大型含自合对象之偏:5099-5105）
_PIAN_OF = {'正财': '偏财', '正官': '七杀', '正印': '偏印',
            '食神': '伤官', '比肩': '劫财', '偏财': '正财', '七杀': '正官'}


def detect_shuizhong_laoyue(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
) -> Dict:
    """水中捞月：婚姻虚象、求而不得（F16 按书三要素重写）。

    书三要素（zhongji:5081-5083 闲注明文；gaoji:12904-12910 同）：
      1. 夫妻星的正星坐夫妻宫（男=正财、女=正官，日支本/中气藏）；
      2. 日主与日支自合（日干合日支所藏之干，自合柱戊子/壬午/己亥/丁亥/
         辛巳/癸巳，zhongji:5098）；
      3. 天干出现偏星干扰（正星之偏：正财→偏财、正官→七杀；扩大型含
         自合对象之偏，zhongji:5099-5105 壬午造丙火偏财例）。
    机制：正星自合=内心理想配偶形象，偏星透干=现实所遇皆偏缘，过分挑剔
    而独身。旧实现（星与他干合/争合/宫被冲）与书义全错已废。

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

    day_idx = PILLAR_KEYS.index('day')
    cg_list = get_canggan_mangpai(zhis[day_idx])
    zheng = '正财' if gender == '男' else '正官'

    # 要素1：正星坐宫（日支本/中气藏正星）
    gong_star = next((cg for idx, (cg, _q) in enumerate(cg_list)
                      if idx <= 1 and _compute_shishen(day_gan, cg) == zheng), '')
    # 要素2：日主与日支自合（日干之合干藏于日支）
    he_target = TIAN_GAN_HE.get(day_gan, '')
    zihe_gan = next((cg for cg, _q in cg_list if cg == he_target), '')
    # 要素3：偏星透干（正星之偏，或自合对象十神之偏——扩大型）
    pians = {_PIAN_OF.get(zheng, '')}
    if zihe_gan:
        pians.add(_PIAN_OF.get(_compute_shishen(day_gan, zihe_gan), ''))
    pians.discard('')
    pian_gans = [g for i, g in enumerate(gans)
                 if i != day_idx and g and _compute_shishen(day_gan, g) in pians]

    factors: List[str] = []
    if gong_star:
        factors.append(f'正星({gong_star}{zheng})坐夫妻宫')
    if zihe_gan:
        factors.append(f'日主与日支自合（{day_gan}{zihe_gan}合），心存理想配偶')
    if pian_gans:
        factors.append(f'偏星({"".join(pian_gans)})透干干扰，所遇皆偏缘')
    is_laoyue = bool(gong_star) and bool(zihe_gan) and bool(pian_gans)
    if is_laoyue:
        factors.append('三要素齐备：水中捞月，理想过高求而不得')
    return {'is_laoyue': is_laoyue, 'factors': factors}


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
    dayun_gan: str = '', dayun_zhi: str = '',
    liunian_gan: str = '', liunian_zhi: str = '',
) -> Dict:
    """关财门（F16 按书重写）：女命专属，运岁比劫夺财→离婚应期。

    书口径（gaoji:12963-12967「女命关财门最验」；zhongji:3578 同）：
    女命以官杀为夫，财星是官杀之原神（财生官）。原局财星在，行运流年
    遇比劫将财星克夺，称为「关财门」——财门一关，官星无生，必被伤官
    克倒，婚姻破裂。轻重：伤官旺者财被穿倒→必离；伤官轻者财受冲→
    闹离（gaoji:12979-12980，案例十二卯运冲酉=闹离）。
    旧实现（男女对称、原局星入墓/合锁冠名「关财门」）名同实异已废——
    书「入墓不开」实属独身格三（zhongji:4927），移至 classify_dushen_sige。

    Returns:
        {'is_guanmen': bool, 'severity': '必离'|'闹离'|'', 'factors': [str]}
    """
    if is_pillars(day_gan):
        p = day_gan
        gans = [p.year_gan, p.month_gan, p.day_gan, p.hour_gan]
        zhis = [p.year_zhi, p.month_zhi, p.day_zhi, p.hour_zhi]
        day_gan = p.day_gan
    gans = gans or []
    zhis = zhis or []
    if not (day_gan and len(gans) == 4 and len(zhis) == 4):
        return {'is_guanmen': False, 'severity': '', 'factors': ['四柱不全']}
    if gender != '女':
        return {'is_guanmen': False, 'severity': '',
                'factors': ['关财门为女命专属（财是官之原神），男命不论']}

    day_wx = GAN_WX.get(day_gan, '')
    cai_wx = WX_KE.get(day_wx, '')
    # 原局财星明现（干或支本气）——财是官之原神，无财则无门可关
    cai_zhis = [z for z in zhis if z and ZHI_WX.get(z) == cai_wx]
    cai_ming = bool(cai_zhis) or any(g and GAN_WX.get(g) == cai_wx for g in gans)
    if not (cai_wx and cai_ming):
        return {'is_guanmen': False, 'severity': '', 'factors': ['原局无财星，无关财门']}

    # 运岁比劫夺财：运岁干为比劫（同我），或运岁支冲/穿原局财支
    hits: List[str] = []
    cai_chuan = False
    for label, dg, dz in (('大运', dayun_gan, dayun_zhi), ('流年', liunian_gan, liunian_zhi)):
        if not dg and not dz:
            continue
        if dg and GAN_WX.get(dg) == day_wx:
            hits.append(f'{label}干{dg}为比劫，克夺财星（财是官之原神），关财门')
        if dz:
            for cz in cai_zhis:
                if (dz, cz) in LIU_CHONG or (cz, dz) in LIU_CHONG:
                    hits.append(f'{label}支{dz}冲财星{cz}，财受劫官无源，关财门')
                elif (dz, cz) in LIU_HAI or (cz, dz) in LIU_HAI:
                    hits.append(f'{label}支{dz}穿倒财星{cz}，财被穿倒，关财门')
                    cai_chuan = True
    if not hits:
        return {'is_guanmen': False, 'severity': '', 'factors': []}

    # 轻重（gaoji:12979-12980）：伤官旺+财被穿倒=必离；伤官轻+财受冲=闹离
    shangguan = sum(1 for i, g in enumerate(gans)
                    if i != PILLAR_KEYS.index('day') and g
                    and _compute_shishen(day_gan, g) == '伤官')
    shangguan += sum(1 for z in zhis if z and
                     _compute_shishen(day_gan, get_canggan_mangpai(z)[0][0]) == '伤官')
    severity = '必离' if (cai_chuan and shangguan >= 2) else '闹离'
    factors = hits + [f'伤官{"旺" if shangguan >= 2 else "轻"}（{shangguan}位），'
                      f'财被{"穿倒" if cai_chuan else "冲克"}→{severity}']
    return {'is_guanmen': True, 'severity': severity, 'factors': factors}


def detect_lu_ban_taohua(
    day_gan: str, gans: List[str], zhis: List[str],
    gender: str = '男', relations: Optional[Dict] = None,
    shensha_result: Optional[Dict] = None,
) -> Dict:
    """禄绊桃花（书桃花口径）：日干之禄与他支六合/半合，所合之支藏干
    十神属财/官/杀/伤/食 → 禄被桃花绊（zhongji:1517「合到伤官、官杀、
    财为禄绊桃花，禄逢三合也是桃花；合到夫妻宫不为桃花」、:4349
    「禄合印不是，是禄印相随」；gaoji:13259-13310 口诀+案例八/九）。

    禄=日主身体临官位，桃花=情欲。男女同论。
    ⚠️F13 重建：旧实现以咸池地支煞为桃花（五书无「咸池」明文），
    现改消费 shensha 桃花['lu_ban']（detect_lu_ban_taohua_zhi 供给）。

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
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    hits = (((shen.get('桃花') or {}).get('lu_ban') or {}).get('hits')) or []
    factors = [f'禄{h["lu"]}合{h["partner"]}（{"/".join(h["cats"])}），'
               f'禄被桃花绊（{h["pillar"]}柱），主情欲重、为情所累'
               for h in hits]
    return {'is_lu_ban': bool(hits), 'factors': factors}


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

    # 法四·桃花合宫/居宫（F13：取日支起算口径——day_ref 子键恒在，
    # engine 默认 reference='day' 时主键即日支口径，gaoji:7912）
    try:
        shen = resolve_shensha(day_gan, zhis, shensha_result)
    except Exception:
        shen = {}
    _tao = shen.get('桃花') or {}
    th = (_tao.get('day_ref') or _tao).get('zhi', '')
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
    """独身四格（F16 按书诀重写，gaoji:13068-13070/zhongji:4924-4928）。

    书诀：「宫占比劫星难家/宫星互害反成克/星入墓库不开花/水中捞月偏星扰」。
      格一·宫占比劫禄印，夫妻星不易进入（日支本气为比劫/印 + 星全无或
        星支被冲穿刑克，gaoji 案例六/七、zhongji:4946 教授例）；
      格二·宫坐制星之星，制之不成星反坏宫（宫五行克星五行 + 星支冲穿刑宫
        + 星有援：透干或得合，gaoji 案例八；力量相当无援不论，:4303 反锚）；
      格三·星入墓库不开（宫占星之墓 或 星透干入墓，无冲刑开库，gaoji 案例九；
        书「入墓不开」正位在此，非关财门）；
      格四·水中捞月偏星扰（=detect_shuizhong_laoyue，zhongji:4939-4940）。
    旧格「纯阳纯阴/华盖重见」系自造（「华盖」四书 grep 0 命中），已废。

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
    day_idx = PILLAR_KEYS.index('day')
    day_zhi = zhis[day_idx]
    swx = _spouse_wx(day_gan, gender)
    star_count = _star_mingxian_count(day_gan, gans, zhis, gender)
    adv, _he = _gong_actions(wa, zhis)
    star_adv = [(t, oz) for t, oz, _a in adv if _is_star_zhi(day_gan, oz, gender)]

    # 星被夫妻宫所拒（宫与星支间冲/穿/刑/克，书「妻星无法进入妻宫」）
    def _other_zhi_of_day(a: Dict) -> str:
        fp, tp = a.get('from_pos', ''), a.get('to_pos', '')
        other = tp if fp == 'day_zhi' else (fp if tp == 'day_zhi' else '')
        k = other.split('_')[0]
        if other.endswith('_zhi') and k in PILLAR_KEYS:
            return zhis[PILLAR_KEYS.index(k)]
        return ''

    gong_rejects_star = any(
        a.get('type') in ('冲', '穿', '刑', '克')
        # 克须宫为施事方（宫克星=拒星；星克宫=宫被坏，非拒）
        and (a.get('type') != '克' or a.get('from_pos') == 'day_zhi')
        and (oz := _other_zhi_of_day(a))
        and ZHI_WX.get(oz, '') == swx  # 本气星支方论（案例十二丑余气官不算）
        for a in wa)

    # 格一·宫占比劫禄印，星不得入（gaoji 案例六/七、zhongji:4946 教授例）
    # 三型居一：星全无 / 宫拒星（案例六·教授）/ 宫占印+时柱占禄刃（案例七）
    gong_main = _zhi_main_cat(day_gan, day_zhi)
    hour_main = _zhi_main_cat(day_gan, zhis[PILLAR_KEYS.index('hour')])
    if gong_main in ('比劫', '印') and (
            star_count == 0 or gong_rejects_star
            or (gong_main == '印' and hour_main == '比劫')):
        grids.append('宫占比劫禄印格')

    # 格二·宫星互害反成克（宫坐制星之星，制之不成星反坏宫）
    if swx and WX_KE.get(ZHI_WX.get(day_zhi, '')) == swx and star_adv:
        star_tou = any(g and GAN_WX.get(g) == swx for g in gans)
        star_tombs = {z for z in zhis if z and swx in TOMB_MAP.get(z, [])}
        star_he = False
        for a in wa:
            if a.get('type') not in ('地支合', '半合'):
                continue
            pair = [zhis[PILLAR_KEYS.index(pk.split('_')[0])]
                    for pk in (a.get('from_pos', ''), a.get('to_pos', ''))
                    if pk.endswith('_zhi') and pk.split('_')[0] in PILLAR_KEYS]
            for oz in pair:
                if ZHI_WX.get(oz, '') == swx:  # 本气星支（辰余气癸不算）
                    partner = next((z for z in pair if z != oz), '')
                    # 合入己墓=星被收（教授例子入辰墓），非得援
                    if partner not in star_tombs:
                        star_he = True
        if star_tou or star_he:
            grids.append('宫星互害反成克格')

    # 格三·星入墓库不开（宫占星之墓 或 星透干入墓，无冲刑开库）
    tombs = _star_in_tomb(day_gan, gans, zhis, gender)
    gong_is_tomb = bool(swx) and swx in TOMB_MAP.get(day_zhi, [])
    star_tou_ru_mu = bool(tombs) and any(g and GAN_WX.get(g) == swx for g in gans)
    if tombs and (gong_is_tomb or star_tou_ru_mu):
        opened = any(
            a.get('type') in ('冲', '刑') and any(
                pk.endswith('_zhi') and pk.split('_')[0] in PILLAR_KEYS
                and zhis[PILLAR_KEYS.index(pk.split('_')[0])] in tombs
                for pk in (a.get('from_pos', ''), a.get('to_pos', '')))
            for a in wa)
        if not opened:
            grids.append('星入墓不开格')

    # 格四·水中捞月偏星扰
    if detect_shuizhong_laoyue(day_gan, gans, zhis, gender, relations).get('is_laoyue'):
        grids.append('水中捞月偏星扰格')

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
    direction_result: Optional[Dict] = None,
) -> Dict:
    """婚姻综合：好坏 + 多婚 + 独身 + 水中捞月 + 关财门 + 禄绊桃花
    + 结婚四法 + 独身四格 + 结离婚应期。

    支持两种签名：旧位置参数，或首个参数为 Pillars 对象。
    A3：接入 yongshen 方向总线（direction_result 缺省自调），
    direction_signals 切片录入输出（只读信号，不改婚姻判定）。

    Returns:
        {
          'quality': {...}, 'duohun': {...}, 'dushen': {...}, 'laoyue': {...},
          'guan_caimen': {...}, 'lu_ban_taohua': {...},
          'jiehun_sifa': {...}, 'dushen_sige': {...},
          'jiehun_yingqi': {...}, 'lihun_yingqi': {...},
          'direction_signals': {...}, 'summary': str,
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
    guanmen = detect_guan_caimen(day_gan, gans or [], zhis or [], gender, relations,
                                 dayun_gan=dayun_gan, dayun_zhi=dayun_zhi,
                                 liunian_gan=liunian_gan, liunian_zhi=liunian_zhi)
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

    # A3：方向总线信号（缺省自调）
    if direction_result is None:
        try:
            direction_result = assess_direction_signals(
                day_gan, gans or [], zhis or [], relations=relations)
        except Exception:
            direction_result = {}

    parts = [f'婚姻{quality.get("quality","平")}']
    if duohun.get('is_duohun'):
        parts.append('多婚之象')
    if dushen.get('is_dushen') or dushen_ge.get('is_dushen'):
        grids = dushen_ge.get('grids', [])
        parts.append('独身之象' + (f'（{",".join(grids)}）' if grids else ''))
    if laoyue.get('is_laoyue'):
        parts.append('水中捞月(婚虚)')
    if guanmen.get('is_guanmen'):
        parts.append(f'关财门(离婚应期·{guanmen.get("severity","")})')
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
        'direction_signals': direction_brief(direction_result),
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
