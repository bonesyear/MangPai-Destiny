# -*- coding: utf-8 -*-
"""哨兵：ganqing（滴天髓干支性情）三条条件语义修复（2026-10-17 修复批）。

书证（docs/ditianchansui/ditianchansui.txt）：
  (a) :392「生于申酉月，或乙酉日」——申酉月与乙酉日为 OR，非 AND；
  (b) :443「辛为丙之臣也，合丙化水…」——「能扶社稷能救生灵」主语为合丙化水，
      须丙在局，无丙（仅甲/戊）不命中；
  (c) :423-424「又生四季月者……如柱见木火，或行运遇之，则破矣」——
      「见木火则破」以生四季月（辰戌丑未）为前提。
"""
from foundation.objective.ganqing import match_ganqing


def _clauses(gan, **ctx):
    return [r.fu_clause for r in match_ganqing(gan, **ctx)]


class TestYiHuaiDingBaoBing:
    def test_shenyou_month_alone_matches(self):
        # 申酉月（无乙酉日）即命中
        cs = _clauses('乙', month_zhi='酉', tougian=['丙'], states=['有水不争克'])
        assert '怀丁抱丙，跨凤乘猴' in cs

    def test_yiyou_day_alone_matches(self):
        # 乙酉日（非申酉月）亦命中——OR 语义
        cs = _clauses('乙', month_zhi='寅', day_gz='乙酉',
                      tougian=['丁'], states=['有水不争克'])
        assert '怀丁抱丙，跨凤乘猴' in cs

    def test_neither_no_match(self):
        cs = _clauses('乙', month_zhi='寅', tougian=['丙'], states=['有水不争克'])
        assert '怀丁抱丙，跨凤乘猴' not in cs


class TestXinHeBing:
    def test_bing_present_matches(self):
        cs = _clauses('辛', stems=['辛', '丙', '甲'])
        assert '能扶社稷，能救生灵' in cs

    def test_no_bing_no_match(self):
        # 仅甲/戊无丙：主语「合丙化水」不成立，不命中
        cs = _clauses('辛', stems=['辛', '甲', '戊'])
        assert '能扶社稷，能救生灵' not in cs


class TestWuJianMuHuo:
    def test_siji_month_matches(self):
        cs = _clauses('戊', month_zhi='辰', stems=['戊', '甲'])
        assert '静翕动辟，万物司命' in cs
        rs = match_ganqing('戊', month_zhi='辰', stems=['戊', '甲'])
        assert any(r.behavior == '见木火则破' for r in rs)

    def test_non_siji_month_no_match(self):
        # 非四季月（午月）见木火不论破
        rs = match_ganqing('戊', month_zhi='午', stems=['戊', '甲'])
        assert not any(r.behavior == '见木火则破' for r in rs)
