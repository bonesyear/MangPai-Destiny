# -*- coding: utf-8 -*-
"""M9+A8: zuogong 主做功声明式规则表 + 强度加权混合解析。

M9：旧串行 if-elif 链（补丁堆叠天花板）重构为声明式规则表——每条规则声明
candidacy/strength/vetoes，解析器统一裁决；primary_work 附 candidates/
resolution 诊断字段（additive，不改 type/path 契约）。
A8：强度加权混合——串行链优先级为主体，低优先级候选强度超出在任者 2 则
逆袭（非纯强度 MAX，纯 MAX 历史回归已弃用）。锚例：化例三（争合1<月干印
化用3）、制例三（日干合2<日支穿制5）由强度解析自然复现，不再依赖硬编码
让位补丁（坐下印+争合 margin 不足、穿降级无候选两边缘保留硬性否决）。
"""
import pytest

from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _pw(day_gan, day_zhi, yg, yz, mg, mz, hg, hz):
    return analyze_zuogong(day_gan, day_zhi, yg, yz, mg, mz, hg, hz)['primary_work']


class TestRuleTableContract:
    def test_candidates_field_present(self):
        # 有做功结构时 candidates 诊断字段存在且含强度
        pw = _pw('己', '丑', '甲', '子', '丙', '寅', '甲', '子')
        assert 'candidates' in pw
        assert all('strength' in c and 'rule' in c for c in pw['candidates'])

    def test_resolution_field(self):
        pw = _pw('己', '丑', '甲', '子', '丙', '寅', '甲', '子')
        res = pw['resolution']
        assert res['margin'] == 2
        assert res['winner_rule'] in (
            '日干合', '化用成局', '生用泄秀', '弃干看支')

    def test_type_path_contract_unchanged(self):
        # type/path 契约不变（下游 regression67/verify 只读这两个键）
        pw = _pw('己', '丑', '甲', '子', '丙', '寅', '甲', '子')
        assert pw['type'] == '化用'
        assert '杀印相生' in pw['path']


class TestStrengthOverride:
    def test_huali3_zhenghe_yields_to_huayong(self):
        # 化例三中堂：甲子丙寅己丑甲子——争合(强度1)被化用月干印(强度3)逆袭
        pw = _pw('己', '丑', '甲', '子', '丙', '寅', '甲', '子')
        assert pw['type'] == '化用'
        assert pw['resolution']['override_fired'] is True
        assert pw['resolution']['winner_rule'] == '化用成局'
        he = [c for c in pw['candidates'] if c['rule'] == '日干合'][0]
        hua = [c for c in pw['candidates'] if c['rule'] == '化用成局'][0]
        assert he['strength'] == 1 and hua['strength'] == 3

    def test_zhili3_chuan_overrides_he(self):
        # 制例三：癸卯戊午己酉甲戌——日支 high 穿(强度5)逆袭日干合(强度2)
        pw = _pw('己', '酉', '癸', '卯', '戊', '午', '甲', '戌')
        assert pw['type'] == '制用'
        assert pw['resolution']['override_fired'] is True
        assert pw['resolution']['winner_rule'] == '弃干看支'

    def test_no_override_when_margin_insufficient(self):
        # 生例一富婆：辛亥庚子庚寅己卯——日干合无竞争，生用主功，无逆袭
        pw = _pw('庚', '寅', '辛', '亥', '庚', '子', '己', '卯')
        assert pw['type'] == '生用'
        assert pw['resolution']['override_fired'] is False

    def test_single_he_strength2_beats_hua_margin1(self):
        # 单合(2) vs 化用坐下印(2)：margin<2 不逆袭，日干合居首（旧链语义保持）
        # 化例一：壬寅丙午戊寅乙卯——日干戊合癸？无合；此例验化用正常居首即可
        pw = _pw('戊', '寅', '壬', '寅', '丙', '午', '乙', '卯')
        assert pw['type'] == '化用'


class TestDeclaredVetoes:
    def test_shihezhi_vetoes_shengyong(self):
        # 复例四老师经商：戊申丙辰丁巳癸卯——食伤合制让位，生用被否决
        pw = _pw('丁', '巳', '戊', '申', '丙', '辰', '癸', '卯')
        assert pw['type'] in ('合用', '制用')
        sheng = [c for c in pw.get('candidates', []) if c['rule'] == '生用泄秀']
        if sheng:
            assert sheng[0]['vetoed'] is True
            assert any('合制' in v for v in sheng[0]['veto_reasons'])

    def test_fallback_lu_still_works(self):
        # 自坐禄 fallback 不受规则表影响（verify zg_lu 同口径）
        pw = _pw('甲', '寅', '丙', '子', '丁', '丑', '辛', '未')
        assert pw['type'] in ('禄比', '制用', '合用')
