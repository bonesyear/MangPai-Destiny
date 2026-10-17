# -*- coding: utf-8 -*-
"""批D 哨兵：xiangfa_ops 干支性情象层 ganqing 接线（tougian/states 传入）。

书证：乙赋「虚湿之地，骑马亦忧」，任氏曰「生于亥子月，四柱无丙丁，又无戌未
燥土，即使年支有午，亦难发生也」。修复前 _ganqing_layer_domains 调
match_ganqing 不传 tougian/states——依赖 tougian_any/state 之约 15 条规则
永不命中，且 no_tougian 空集恒真致柱有丙仍命中「虚湿之地」（反向误命中）。
本哨兵锁定：tougian=四柱天干、states=derive_states 推导态传入后的行为。
"""
from mangpai.subjective.xiangfa_ops import _ganqing_layer_domains


def test_bing_present_no_xushi_domains():
    """乙生子月柱有丙：不再报「虚湿之地」——其 rationale 所述戌未燥土（土五行，
    甲日=财）之主体域不进性情象层；冬月「宜火」正例（火=食伤→食艺）仍在。"""
    gans = ['丙', '乙', '甲', '戊']
    zhis = ['寅', '子', '卯', '辰']
    doms = _ganqing_layer_domains('乙', '甲', gans, zhis)
    assert '财' not in doms      # 虚湿之地误命中时会经「燥土→土→财」带入
    assert '食艺' in doms        # 乙木虽柔·冬宜火（解冻）正常命中


def test_truly_no_bingding_xushi_hits():
    """正例对照：子月确无丙丁透干且无戌未 → 虚湿之地正常命中（土→财域出现）。"""
    gans = ['庚', '乙', '甲', '戊']
    zhis = ['寅', '子', '卯', '辰']
    doms = _ganqing_layer_domains('乙', '甲', gans, zhis)
    assert '财' in doms


def test_tougian_wiring_revives_huochi_rule():
    """tougian 接线复活 tougian_any 规则：甲寅午戌局透丙 → 「火炽乘龙」命中
    （rationale 含火/水/土/木，火=食伤→食艺域）；修复前该规则永不命中。"""
    gans = ['丙', '甲', '甲', '戊']
    zhis = ['午', '寅', '戌', '子']
    doms = _ganqing_layer_domains('甲', '甲', gans, zhis)
    assert '食艺' in doms
