# -*- coding: utf-8 -*-
"""_relation_utils - objective 层关系判定公共小工具（H-fix-4b 下沉统一）。

原 `_check_pair` 在 objective 层 zuogong_detect/dayun/gongshen 三处复制、
muku 以 _is_chong/_is_he/_is_xing 特化复制、subjective/liunian 两处函数内
局部复制——六处逐字等价（差异分析见 docs/tasks/codehygiene-fix-backlog.md
H-fix-4b 节），统一为 pair_in 单一实现。
"""
from typing import Dict, List, Optional, Tuple

from mangpai.objective.constants import (
    CANG_GAN_MANGPAI, GAN_WX, LIU_CHONG, LIU_HE, LIU_HAI, LIU_PO,
    PILLAR_KEYS, WX_KE, WX_SHENG, ZHI_WX,
)

XING_PAIRS = [
    ('寅', '巳'), ('巳', '申'), ('申', '寅'),
    ('丑', '戌'), ('戌', '未'), ('未', '丑'),
    ('子', '卯'), ('卯', '子'),
]
XING_GROUPS = [('寅', '巳', '申'), ('丑', '戌', '未')]
SAN_HE = [('申', '子', '辰'), ('巳', '酉', '丑'),
          ('寅', '午', '戌'), ('亥', '卯', '未')]
GONG_JU = {g[0] + g[2]: ZHI_WX[g[1]] for g in SAN_HE}
ZI_XING = ['辰', '午', '酉', '亥']
SAN_HUI = [('寅', '卯', '辰'), ('巳', '午', '未'),
           ('申', '酉', '戌'), ('亥', '子', '丑')]


def pair_in(a: str, b: str, pairs) -> bool:
    """双向判定 (a,b) 是否属于 pairs。"""
    return (a, b) in pairs or (b, a) in pairs


def is_work_xing(a: str, b: str, all_zhis) -> bool:
    """理象学核心做功刑；子卯、自刑、丑未只保留领域关系标记。"""
    if pair_in(a, b, [('丑', '戌'), ('未', '戌')]):
        return True
    return (pair_in(a, b, XING_PAIRS[:3])
            and all(z in all_zhis for z in XING_GROUPS[0]))


_W_GAN_TG = 2.0
_W_BEN_QI = 2.0
_W_ZHONG_QI = 1.0
_W_YU_QI = 0.5
_W_YUAN = 0.5


def _yuan_wx(wx: str) -> str:
    return next((w for w, born in WX_SHENG.items() if born == wx), '')


def _wx_in_elem(wx: str, elem: str, is_gan: bool) -> float:
    if not elem:
        return 0.0
    if is_gan:
        return _W_GAN_TG if GAN_WX.get(elem) == wx else 0.0
    weight = 0.0
    for gan, qi in CANG_GAN_MANGPAI.get(elem, []):
        if GAN_WX.get(gan) != wx:
            continue
        weight += {'本气': _W_BEN_QI, '中气': _W_ZHONG_QI}.get(qi, _W_YU_QI)
    return weight


def _party_strength(wx: str, gans: List[str], zhis: List[str],
                    include_yuan: bool = True) -> float:
    """既有工程权重：同党全计、原神折半；只用于结构强弱，不判吉凶。"""
    strength = sum(_wx_in_elem(wx, g, True) for g in gans)
    strength += sum(_wx_in_elem(wx, z, False) for z in zhis)
    if include_yuan:
        yuan = _yuan_wx(wx)
        strength += _W_YUAN * sum(_wx_in_elem(yuan, g, True) for g in gans)
        strength += _W_YUAN * sum(_wx_in_elem(yuan, z, False) for z in zhis)
    return strength


def _single_zhi_party(wx: str, zhi: str, zhis: List[str],
                      gans: Optional[List[str]] = None) -> float:
    """土冲局部党势：燥土支及木火对湿土支及金水，等权则不定向。"""
    if wx != '土' or zhi not in {'辰', '戌', '丑', '未'}:
        return _wx_in_elem(wx, zhi, False)
    dry = zhi in {'未', '戌'}
    own_soil = {'未', '戌'} if dry else {'辰', '丑'}
    support = ('木', '火') if dry else ('金', '水')
    strength = 0.0
    for i, branch in enumerate(zhis):
        gan = gans[i] if gans and i < len(gans) else ''
        if branch in own_soil:
            strength += _wx_in_elem('土', gan, True)
            strength += _wx_in_elem('土', branch, False)
        for element in support:
            strength += _W_GAN_TG if GAN_WX.get(gan) == element else 0.0
            strength += _W_BEN_QI if ZHI_WX.get(branch) == element else 0.0
    return strength


def _main_qi_count(wx: str, gans: List[str], zhis: List[str],
                   zhi: str = '', camp: bool = True) -> float:
    """主气阵营数：金水湿土与木火燥土按 4/8 判党；camp=False 仅同五行。"""
    if not camp:
        return sum(GAN_WX.get(g) == wx for g in gans) + sum(
            ZHI_WX.get(z) == wx for z in zhis)
    if wx == '土' and ZHI_WX.get(zhi) in ('木', '火'):
        return sum(GAN_WX.get(g) in ('木', '火', '土') for g in gans) + sum(
            ZHI_WX.get(z) in ('木', '火') or z in ('未', '戌') for z in zhis)
    if wx == '土' and ZHI_WX.get(zhi) in ('金', '水'):
        return sum(GAN_WX.get(g) in ('金', '水', '土') for g in gans) + sum(
            ZHI_WX.get(z) in ('金', '水') or z in ('丑', '辰') for z in zhis)
    if wx == '土' and zhi:
        return _single_zhi_party(wx, zhi, zhis, gans)
    if wx in ('金', '水'):
        return sum(GAN_WX.get(g) in ('金', '水') for g in gans) + sum(
            ZHI_WX.get(z) in ('金', '水') or z in ('丑', '辰') for z in zhis)
    if wx in ('木', '火'):
        fire = sum(GAN_WX.get(g) == '火' for g in gans) + sum(
            ZHI_WX.get(z) == '火' for z in zhis)
        wood = sum(GAN_WX.get(g) == '木' for g in gans) + sum(
            ZHI_WX.get(z) == '木' for z in zhis)
        dry = sum(z in ('未', '戌') for z in zhis)
        if wx == '木':
            return wood + fire if wood + fire >= 4 else wood
        if fire + dry >= 4:
            return wood + fire + dry
        return fire if wood + fire >= 4 else fire + dry
    return sum(GAN_WX.get(g) == wx for g in gans) + sum(
        ZHI_WX.get(z) == wx for z in zhis)


def _directed_control_edges(zhis: List[str], gans: Optional[List[str]] = None
                            ) -> List[Tuple[str, str, str]]:
    """冲/克有向边；先分是否成党，未形成党势时保留自然克向。"""
    edge_type: Dict[Tuple[str, str], str] = {}
    nz = [z for z in zhis if z]
    gs = gans or []

    def _add(a: str, b: str, relation_type: str) -> None:
        current = edge_type.get((a, b))
        if current is None or (current == '克' and relation_type == '冲'):
            edge_type[(a, b)] = relation_type

    for a in nz:
        for b in nz:
            if a != b and WX_KE.get(ZHI_WX.get(a, '')) == ZHI_WX.get(b, ''):
                _add(a, b, '克')

    chong_map = {a: b for a, b in LIU_CHONG}
    chong_map.update({b: a for a, b in LIU_CHONG})
    for a in nz:
        b = chong_map.get(a, '')
        if not b or b not in nz:
            continue
        wa, wb = ZHI_WX.get(a, ''), ZHI_WX.get(b, '')
        if {wa, wb} == {'水', '火'}:
            ca, cb = _main_qi_count(wa, gs, zhis), _main_qi_count(wb, gs, zhis)
            if ca >= 4 and cb < 4:
                sa, sb = 1.0, 0.0
            elif cb >= 4 and ca < 4:
                sa, sb = 0.0, 1.0
            elif ca >= 4 and cb >= 4:
                sa = _party_strength(wa, gs, zhis)
                sb = _party_strength(wb, gs, zhis)
            else:
                # 乾隆原文「命局没有形成一方之势」：无权以微差反冲，取自然克向。
                if WX_KE.get(wa) == wb:
                    sa, sb = 1.0, 0.0
                else:
                    sa, sb = 0.0, 1.0
        elif wa == wb and wa == '土':
            sa = _single_zhi_party(wa, a, zhis, gans)
            sb = _single_zhi_party(wb, b, zhis, gans)
        elif WX_KE.get(wa) == wb:
            sa, sb = 1.0, 0.0
        elif WX_KE.get(wb) == wa:
            sa, sb = 0.0, 1.0
        else:
            continue
        if sa > sb:
            _add(a, b, '冲')
        elif sb > sa:
            _add(b, a, '冲')
    return [(a, b, t) for (a, b), t in edge_type.items()]


def resolve_relation_direction(a: str, b: str, relation_type: str,
                               zhis: List[str], gans: Optional[List[str]] = None
                               ) -> Tuple[str, str, str]:
    """返回实际施受端点；互克/双向为 mutual，证据不足为 unknown。"""
    if relation_type in ('地支合', '暗合', '半合', '三合局'):
        return a, b, 'mutual'
    if relation_type == '冲':
        for source, target, link_type in _directed_control_edges(zhis, gans):
            if link_type == '冲' and {source, target} == {a, b}:
                return source, target, 'directed'
        if {ZHI_WX.get(a), ZHI_WX.get(b)} == {'水', '火'}:
            wa, wb = ZHI_WX[a], ZHI_WX[b]
            if (_main_qi_count(wa, gans or [], zhis) >= 4
                    and _main_qi_count(wb, gans or [], zhis) >= 4
                    and _party_strength(wa, gans or [], zhis)
                    == _party_strength(wb, gans or [], zhis)):
                return a, b, 'mutual'
    elif relation_type in ('刑', '穿', '破'):
        sa = _main_qi_count(ZHI_WX.get(a, ''), gans or [], zhis, a)
        sb = _main_qi_count(ZHI_WX.get(b, ''), gans or [], zhis, b)
        if sa > sb:
            return a, b, 'directed'
        if sb > sa:
            return b, a, 'directed'
        if WX_KE.get(ZHI_WX.get(a, '')) == ZHI_WX.get(b, ''):
            return a, b, 'directed'
        if WX_KE.get(ZHI_WX.get(b, '')) == ZHI_WX.get(a, ''):
            return b, a, 'directed'
        return a, b, 'mutual'
    return a, b, 'unknown'


def he_control_target(a: str, b: str, day_marker: str,
                      gans: List[str], zhis: List[str]) -> str:
    """克合的受方；主位优先，其余按党势，生合或势均不判单向合制。"""
    wa, wb = GAN_WX.get(a, '') or ZHI_WX.get(a, ''), GAN_WX.get(b, '') or ZHI_WX.get(b, '')
    if not wa or not wb or wa == wb:
        return ''
    if a == day_marker:
        doer, target = a, b
    elif b == day_marker:
        doer, target = b, a
    else:
        sa = _party_strength(wa, gans, zhis)
        sb = _party_strength(wb, gans, zhis)
        if sa == sb:
            return ''
        doer, target = (a, b) if sa > sb else (b, a)
    dw, tw = GAN_WX.get(doer, '') or ZHI_WX.get(doer, ''), GAN_WX.get(target, '') or ZHI_WX.get(target, '')
    if WX_KE.get(dw) != tw and WX_KE.get(tw) != dw:
        return ''
    return target
