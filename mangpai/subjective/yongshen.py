# -*- coding: utf-8 -*-
"""用神/忌神方向判定（扶抑框架）+ 凶向信号聚合。

段氏功量层（gongliang）能检测「做了什么功」，但不知「该不该做」。
本模块补吉凶方向判定：

1. **比劫夺财（R1）**——段氏「制财得财」成立的前提是功神非比劫；
   功神=比劫制财（尤以身强财为用神、财弱孤）为「比劫夺财」=破财凶，
   与「印/食伤/官制财=得财吉」对立。典型：第9期 子(比劫)冲午(财) =>
   清家荡产；区别于蒋介石 巳(印)冲亥(财)=得财贵（功神=印非比劫）。

2. **凶向信号聚合**——反局(fan)/坐牢(laoyu)/比劫夺财/过河拆桥破财
   任一命中即「凶向」，供 caiming/guanming/zhiye 反哺降档/否决。

设计约束（见 memory: mangpai-objective-subjective-refactor）：
  - 本模块属 subjective 判断层，单向消费 objective 检测 + 同层 zuogong/zhengfan/laoyu；
  - 缺省自调（_ensure_*），engine 透传或 calib 直调均可用；
  - 不改 gongliang 功量点累加，仅在其后施加方向性封顶/标记。
"""

from typing import Dict, List, Optional, Set

from mangpai.objective.constants import GAN_WX, ZHI_WX, WX_KE, WX_SHENG

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


def classify_strength(day_gan: str, gans: List[str], zhis: List[str]) -> str:
    """扶抑身强弱粗分（势-based，非精细得令透干）。

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
    if abs(selfc - conc) <= 1:
        return '中和'
    return '身强' if selfc > conc else '身弱'


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


def detect_bijiao_duocai(
    day_gan: str, gans: List[str], zhis: List[str],
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """比劫夺财检测（R1）。

    判定：身强（财为扶抑用神）+ 存在 冲/克/穿/破/刑 非辅助做功
    其功神(from_pos 主气)=比劫、被制(to_pos 主气)=财，且财弱（明现≤1柱）。
    严重度：比劫≥2柱 或 财被≥2处比劫制 -> severe（清家荡产/贫）。

    段氏「制财得财」以功神非比劫为前提；功神=比劫即「夺财」破财，与
    蒋介石（印制财=得财）、LIU8（印制财=七杀当财）相区别。

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
        fc = _wx_cat(dw, _pos_main_wx(fp, gans, zhis))
        tc = _wx_cat(dw, _pos_main_wx(tp, gans, zhis))
        if fc == '比劫' and tc == '财':
            duocai_hits += 1
            hit_descs.append(f'{t} {fp}(比劫)→{tp}(财)')

    detected = bool(hit_descs) and strength in ('身强', '从弱')
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


def assess_direction_signals(
    day_gan: str, gans: List[str], zhis: List[str],
    *,
    relations: Optional[Dict] = None,
    gongliang_result: Optional[Dict] = None,
    zhengfan_result: Optional[Dict] = None,
    laoyu_result: Optional[Dict] = None,
    work_actions: Optional[List[Dict]] = None,
) -> Dict:
    """聚合「凶向」信号，供 caiming/guanming/zhiye 反哺降档/否决。

    凶向 = 反局(fan) OR 坐牢(risk≥中) OR 比劫夺财(R1) OR 过河拆桥破财。

    Returns:
        {'direction': '吉'|'凶'|'中性',
         'fanju': bool, 'laoyu_risk': str,
         'bijiao_duocai': {...}, 'pocai': bool, 'pocai_severe': bool,
         'guohe_pocai': bool, 'reasons': [str]}
    """
    if not (day_gan and gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return {'direction': '中性', 'fanju': False, 'laoyu_risk': '无',
                'bijiao_duocai': {}, 'pocai': False, 'pocai_severe': False,
                'guohe_pocai': False, 'reasons': []}

    gl = gongliang_result or {}
    # R1：优先读 gongliang 已算得的 pocai_signal；缺省自算
    bijiao = {}
    if gl.get('pocai_signal'):
        bijiao = {'detected': True, 'severity': gl.get('pocai_severity') or 'normal',
                  'reason': gl.get('pocai_reason', '')}
    else:
        bijiao = detect_bijiao_duocai(day_gan, gans, zhis, work_actions)

    zf = zhengfan_result or _ensure_zhengfan(day_gan, gans, zhis, relations)
    ly = laoyu_result or _ensure_laoyu(day_gan, gans, zhis, relations)

    fanju = bool(zf and zf.get('type') == 'fan')
    laoyu_risk = ly.get('risk', '无') if ly else '无'
    # 注：laoyu(牢狱)检测在富贵局上系统性过火（如李嘉诚/克林顿/例八皆判 risk=高
    # 而实非牢狱），故仅作信息保留，不计入凶向否决/降档触发，避免误伤正当富贵。
    laoyu_hit = False

    # 过河拆桥破财（gongliang_result 未带时留 False；caiming 自算 guohe 透传）
    guohe_pocai = bool(gl.get('guohe_pocai'))

    pocai = bool(bijiao.get('detected')) or guohe_pocai
    pocai_severe = (bijiao.get('severity') == 'severe')

    reasons: List[str] = []
    if fanju:
        reasons.append(f"反局（{zf.get('configuration', '')}）")
    if bijiao.get('detected'):
        reasons.append(bijiao.get('reason', '比劫夺财破财'))
    if guohe_pocai:
        reasons.append('过河拆桥破财')

    direction = '凶' if (fanju or pocai) else '中性'
    return {
        'direction': direction,
        'fanju': fanju,
        'laoyu_risk': laoyu_risk,
        'laoyu_hit': laoyu_hit,
        'bijiao_duocai': bijiao,
        'pocai': pocai,
        'pocai_severe': pocai_severe,
        'guohe_pocai': guohe_pocai,
        'reasons': reasons,
    }
