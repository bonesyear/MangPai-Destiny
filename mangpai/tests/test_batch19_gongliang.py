# -*- coding: utf-8 -*-
"""批次19：功量组合证据、纯化用与输入顺序的最小反例。"""
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _gl(gans, zhis):
    return analyze_gongliang(day_gan=gans[2], gans=gans, zhis=zhis)


def test_f23_sanhe_zhiku_does_not_invent_month_seal_point():
    result = _gl(['甲', '庚', '戊', '壬'], ['寅', '午', '辰', '戌'])
    assert not any('月令见印' in reason for reason in result['reasons'])
    assert result['level'] <= 3


def test_h9_shaku_requires_actual_officer_tomb():
    result = _gl(['癸', '戊', '丁', '丁'], ['巳', '午', '丑', '未'])
    assert not any(e.get('id') == 'bundle:shaku' for e in result['evidence'])
    anchor = _gl(['乙', '己', '己', '庚'], ['巳', '丑', '未', '午'])
    assert any(e.get('id') == 'bundle:shaku' for e in anchor['evidence'])


def test_h10_relation_only_self_xing_does_not_form_bundle():
    result = _gl(['壬', '壬', '己', '戊'], ['辰', '子', '亥', '辰'])
    assert result['level'] == 3
    assert not any(e.get('id') == 'bundle:zhiku' and '刑制墓库' in e.get('reason', '')
                   for e in result['evidence'])
    anchor = _gl(['丙', '丙', '乙', '戊'], ['戌', '申', '丑', '寅'])
    assert anchor['level'] == 4


def test_h11_month_as_target_does_not_double_count_lianmu():
    result = _gl(['乙', '辛', '庚', '己'], ['卯', '亥', '辰', '酉'])
    assert result['gong_points'] == 3.5 and result['level'] == 3
    assert not any('连墓加层：月令「亥」' in reason for reason in result['reasons'])
    anchor = _gl(['戊', '己', '庚', '丁'], ['辰', '未', '午', '亥'])
    assert anchor['gong_points'] == 4.5 and anchor['level'] == 4


def test_h79_pure_hua_ignores_officer_against_daymaster():
    result = _gl(['庚', '乙', '甲', '壬'], ['申', '酉', '申', '申'])
    assert any('化用成局/从杀格' in reason for reason in result['reasons'])
    assert result['level'] >= 2
    assert result.get('penalty') not in ('相克之制', '相生之功')


def test_h83_derives_daymaster_before_zeishen_analysis():
    gans, zhis = ['辛', '丁', '庚', '丙'], ['卯', '酉', '午', '子']
    zg = analyze_zuogong('庚', '午', '辛', '卯', '丁', '酉', '丙', '子')
    explicit = analyze_gongliang(zg, day_gan='庚', gans=gans, zhis=zhis)
    omitted = analyze_gongliang(zg, gans=gans, zhis=zhis)
    for key in ('level', 'gong_points', 'zeishen_jing_zhi'):
        assert omitted[key] == explicit[key]
