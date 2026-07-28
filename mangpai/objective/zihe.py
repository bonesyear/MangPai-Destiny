# -*- coding: utf-8 -*-
"""zihe — 天地合/自合柱检测（objective 层）

理论来源：《段建业命理授课教程》第四十八期「天地合的重要性」
（shouke-jiaocheng.txt:2160-2194）。

九柱自合（天干与坐支藏干五合）：
  恒常自合：丁亥（丁壬合）、甲午（甲己合）、戊子（戊癸合）、己亥（己合亥中甲）、
            辛巳（丙辛合）、壬午（丁壬合）、癸巳（戊癸合）；
  条件自合：丙戌（丙辛合）、壬戌（丁壬合）——戌逢刑冲时激活。

段氏：「天地合能使天干之意向发生改变，如日主因合而从支，或日主因合而被支制」。
  - 日主自合：日主从支/被支制（例2 己坐亥自合，不受丁火之生，从官）；
  - 非日柱自合：柱上之干被坐支藏干合绊而失用（例1 康熙 年干甲被年支午中己
    合绊=制官得官；合绊所藏十神=制）。

注：yunfan 的「天地合」为岁运干合+支合联动（同名异物），本模块只检原局四柱
自合柱。本模块仅检测不判断，供 subjective 层（yongshen 从格/R1b、caiming、
guanming）消费。自合**不**并入 zuogong 通用合做功源——过河拆桥等通用合源
消费者不得取本表（守门：48期自合是柱内干支合，非柱间做功）。
"""
from typing import Dict, List, Optional, Set

from mangpai.objective.constants import (
    GAN_WX, ZHI_WX, TIAN_GAN_HE, LIU_CHONG, XING_PAIRS, PILLAR_KEYS,
)
from mangpai.objective.canggan import get_canggan_mangpai

_PK4_CN = ['年', '月', '日', '时']

# 九柱自合表：gz -> (支中合神藏干, 是否恒常激活)
# 恒常=True：丁亥/甲午/戊子/己亥/辛巳/壬午/癸巳；False：丙戌/壬戌（戌逢刑冲激活）
_ZIHE_TABLE: Dict[str, tuple] = {
    '丁亥': ('壬', True),
    '甲午': ('己', True),
    '戊子': ('癸', True),
    '己亥': ('甲', True),
    '辛巳': ('丙', True),
    '壬午': ('丁', True),
    '癸巳': ('戊', True),
    '丙戌': ('辛', False),
    '壬戌': ('丁', False),
}

# 戌之刑冲激活源：辰（冲）、丑/未（刑）
_XU_ACTIVATORS: Set[str] = set()
for _a, _b in LIU_CHONG:
    if '戌' in (_a, _b):
        _XU_ACTIVATORS.add(_b if _a == '戌' else _a)
for _pair in XING_PAIRS:
    _pa = _pair if isinstance(_pair, tuple) else tuple(_pair)
    if '戌' in _pa:
        _XU_ACTIVATORS.update(x for x in _pa if x != '戌')


def _xu_activated(idx: int, zhis: List[str]) -> bool:
    """丙戌/壬戌柱之戌是否被原局他支刑冲激活（「戌逢刑冲时」）。"""
    for j, z in enumerate(zhis):
        if j == idx or not z:
            continue
        if z in _XU_ACTIVATORS:
            return True
    return False


def detect_zihe(gans: List[str], zhis: List[str]) -> Dict:
    """自合柱检测：扫原局四柱，逐柱判 干 vs 坐支藏干 五合。

    Returns:
        {
          'pillars': [{idx, key, key_cn, gz, gan, zhi, he_shen, always,
                       activated, is_day, desc}...],   # 命中自合的柱
          'day_zihe': {...}|None,      # 日柱自合（日主自合，从格/合财合官用）
          'ban_gan_positions': [str],  # 失用干位（'year_gan' 等，激活自合柱之干，
                                       # 非日柱——R1b/财合绊消费口径）
          'has_zihe': bool,
        }
    """
    out: Dict = {'pillars': [], 'day_zihe': None, 'ban_gan_positions': [],
                 'has_zihe': False}
    if not (gans and zhis and len(gans) == 4 and len(zhis) == 4):
        return out
    for i in range(4):
        g, z = gans[i], zhis[i]
        if not g or not z:
            continue
        ent = _ZIHE_TABLE.get(g + z)
        if not ent:
            continue
        he_shen, always = ent
        # 表内一致性校验：合神确在支藏干中且与干五合（数据自检，防表笔误）
        cangs = [cg for cg, _q in get_canggan_mangpai(z)]
        if he_shen not in cangs or TIAN_GAN_HE.get(g) != he_shen:
            continue
        activated = always or _xu_activated(i, zhis)
        rec = {
            'idx': i,
            'key': PILLAR_KEYS[i],
            'key_cn': _PK4_CN[i],
            'gz': g + z,
            'gan': g,
            'zhi': z,
            'he_shen': he_shen,          # 支中合神（被合藏干）
            'always': always,            # 恒常自合 or 条件自合
            'activated': activated,      # 条件自合须戌逢刑冲方激活
            'is_day': i == 2,
            'desc': (f'{_PK4_CN[i]}柱{g}{z}自合（{g}{he_shen}合）'
                     + ('' if always else ('，戌逢刑冲激活' if activated else '，戌未逢刑冲未激活'))),
        }
        out['pillars'].append(rec)
        if i == 2:
            out['day_zihe'] = rec
        elif activated:
            # 非日柱之干被坐支藏干合绊失用（康熙型；与 R1b 受害方口径统一）
            out['ban_gan_positions'].append(f'{PILLAR_KEYS[i]}_gan')
    out['has_zihe'] = bool(out['pillars'])
    return out


__all__ = ['detect_zihe']
