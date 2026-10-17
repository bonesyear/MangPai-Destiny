# -*- coding: utf-8 -*-
"""哨兵：ganqing（滴天髓干支性情）三条条件语义修复（2026-10-17 修复批）。

书证（docs/ditianchansui/ditianchansui.txt）：
  (a) :392「生于申酉月，或乙酉日」——申酉月与乙酉日为 OR，非 AND；
  (b) :443「辛为丙之臣也，合丙化水…」——「能扶社稷能救生灵」主语为合丙化水，
      须丙在局，无丙（仅甲/戊）不命中；
  (c) :423-424「又生四季月者……如柱见木火，或行运遇之，则破矣」——
      「见木火则破」以生四季月（辰戌丑未）为前提。
"""
from foundation.objective.ganqing import (
    GAN_QING_RULES, GAN_YUANZHU, derive_states, match_ganqing,
)


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


# ── 批D：no_tougian/no_branches 上下文缺失保守不命中 ──
# 书证：乙赋「虚湿之地，骑马亦忧」任氏曰「生于亥子月，四柱无丙丁，又无戌未燥土」
# ——「无丙丁」为排除条件，tougian 上下文未提供时旧实现空集恒真，柱有丙仍命中
# （反向误命中）。修复：tougian/branches 为 None（未提供）时含 no_tougian/
# no_branches 之规则保守不命中；显式传入则正常判定。
class TestYiXuShiZhiDiGuard:
    def test_bing_tougian_present_no_match(self):
        # 柱有丙透干 → 不命中（修复前反向误命中点）
        cs = _clauses('乙', month_zhi='子', tougian=['乙', '丙'],
                      stems=['乙', '丙'], branches=['寅', '子', '卯', '辰'])
        assert '虚湿之地，骑马亦忧' not in cs

    def test_tougian_missing_conservative(self):
        # tougian 未提供（None）→ 含 no_tougian 之规则保守不命中
        cs = _clauses('乙', month_zhi='子',
                      stems=['乙', '庚'], branches=['寅', '子', '卯', '辰'])
        assert '虚湿之地，骑马亦忧' not in cs

    def test_branches_missing_conservative(self):
        # branches 未提供（None）→ 含 no_branches 之规则保守不命中
        cs = _clauses('乙', month_zhi='子', tougian=['乙', '庚'],
                      stems=['乙', '庚'])
        assert '虚湿之地，骑马亦忧' not in cs

    def test_truly_no_bingding_still_matches(self):
        # 正例对照：亥子月确无丙丁透干、无戌未燥土 → 书之正例仍命中
        cs = _clauses('乙', month_zhi='子', tougian=['乙', '庚'],
                      stems=['乙', '庚'], branches=['寅', '子', '卯', '辰'])
        assert '虚湿之地，骑马亦忧' in cs


# ── 批D：戊「生于秋冬」2 条 fu_clause 归类修正 ──
# ditianchansui:421-422「生于秋冬，水多宜火暖之，则万物化成，湿则物病」
# 实出自任氏曰非赋文——fu_clause 归准为所发挥之赋文原句「水润物生，火燥物病」，
# 任氏曰文句留 renshi 字段（source='任氏发挥' 不变）。
class TestWuQiuDongAnchor:
    def test_wuhuan_fu_clause(self):
        rs = [r for r in GAN_QING_RULES['戊'] if r.behavior == '宜火暖（物化）']
        assert len(rs) == 1
        assert rs[0].fu_clause == '水润物生，火燥物病'
        assert rs[0].source == '任氏发挥'
        assert '生于秋冬，水多宜火暖之' in rs[0].renshi

    def test_shibing_fu_clause(self):
        rs = [r for r in GAN_QING_RULES['戊'] if r.behavior == '湿则物病']
        assert len(rs) == 1
        assert rs[0].fu_clause == '水润物生，火燥物病'
        assert rs[0].source == '任氏发挥'


# ── 批D：辛冬月 2 条 fu_clause 自造缩写 → 真实原文句 ──
# ditianchansui:445 辛原注末句「故辛金生于冬月，见丙火则男命不贵，虽贵亦不忠；
# 女命克夫，不克亦不和。见丁男女皆贵且顺」——fu_clause 取真实原文句，
# 该句补入 GAN_YUANZHU['辛']。match_ganqing 无 gender 上下文，男女分断合判。
class TestXinDongYueAnchor:
    def test_bing_fu_clause_verbatim(self):
        rs = [r for r in GAN_QING_RULES['辛']
              if r.condition.get('season') == '冬'
              and '丙' in (r.condition.get('stems') or [])]
        assert len(rs) == 1
        assert rs[0].fu_clause == '见丙火则男命不贵，虽贵亦不忠；女命克夫，不克亦不和'
        assert rs[0].source == '原注'

    def test_ding_fu_clause_verbatim(self):
        rs = [r for r in GAN_QING_RULES['辛']
              if r.condition.get('season') == '冬'
              and '丁' in (r.condition.get('stems') or [])]
        assert len(rs) == 1
        assert rs[0].fu_clause == '见丁男女皆贵且顺'
        assert rs[0].source == '原注'

    def test_yuanzhu_xin_completed(self):
        assert '见丙火则男命不贵' in GAN_YUANZHU['辛']
        assert '见丁男女皆贵且顺' in GAN_YUANZHU['辛']


# ── 批D：derive_states 可得状态推导（xiangfa_ops 接线用）──
class TestDeriveStates:
    def test_fire_duo_and_water_present(self):
        st = derive_states(['丙', '丙', '丙', '丁'], ['午', '午', '巳', '子'])
        assert '火旺' in st and '火多' in st      # 火 6/8 字
        assert '有水不争克' in st                  # 子水在局
        assert '无金水' not in st

    def test_no_jinshui_and_mu_sheng(self):
        st = derive_states(['甲', '乙', '丙', '丁'], ['寅', '卯', '巳', '午'])
        assert '无金水' in st                        # 金 0 且水 0
        assert '木盛' in st                          # 木 4/8 字

    def test_huotu_bingwang_and_zao(self):
        st = derive_states(['丙', '丁', '戊', '己'], ['巳', '午', '辰', '戌'])
        assert '火土并旺' in st and '火土多' in st   # 火 4 + 土 4 >= 5
        assert '土多' in st                          # 土 4/8 字
        assert '燥' in st                            # 戌燥土在支
        assert '湿' in st                            # 辰湿土在支

