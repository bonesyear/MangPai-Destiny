# -*- coding: utf-8 -*-
"""批次27C：弃用公门模块的存档输出边界。"""
from mangpai.subjective.gongmen_wuzhi import (
    assess_wuzhi_level, classify_gongjianfa, classify_junguan,
    detect_gongmen_wuzhi_xiang,
)


def test_h84_action_categories_use_actual_endpoints():
    junguan = classify_junguan(
        '甲', ['庚', '戊', '甲', '乙'], ['子', '寅', '午', '亥'])
    assert not any('伤官制杀' in e for e in junguan['evidence'])

    gongjianfa = classify_gongjianfa(
        '甲', ['己', '戊', '甲', '戊'], ['酉', '辰', '午', '辰'])
    assert not any('伤官合杀' in e for e in gongjianfa['evidence'])
    assert '检察法院' not in gongjianfa['groups']


def test_h85_auxiliary_stem_ke_does_not_create_yang_zhi_yin():
    result = classify_gongjianfa(
        '甲', ['丁', '辛', '甲', '壬'], ['丑', '亥', '子', '申'])
    assert not any('阳制阴' in e for e in result['evidence'])

    non_aux = classify_gongjianfa(
        '丁', ['甲', '辛', '丁', '甲'], ['申', '酉', '丑', '亥'])
    assert any('阳制阴' in e for e in non_aux['evidence'])


def test_h87_zhengguan_is_not_qisha():
    gans = ['辛', '乙', '甲', '丙']
    zhis = ['酉', '卯', '卯', '午']
    xiang = detect_gongmen_wuzhi_xiang('甲', gans, zhis)
    assert not any('七杀' in e for e in xiang['wuzhi'])

    junguan = classify_junguan('甲', gans, zhis)
    assert not any('七杀' in e for e in junguan['evidence'])


def test_h88_below_threshold_has_no_group_evidence_or_desc():
    result = classify_gongjianfa(
        '甲', ['壬', '壬', '甲', '甲'], ['申', '子', '戌', '子'])
    assert result['is_gongjianfa'] is False
    assert result['evidence'] == []
    assert result['desc'] == '无明显公检法组合'


def test_f33_level_alone_cannot_create_rank():
    result = assess_wuzhi_level(
        '甲', ['甲', '丙', '甲', '丙'], ['寅', '午', '子', '午'],
        {'level': 4, 'rank_grade': ''})
    assert result['grade'] == '未定（无独立官级证据）'
    assert '将官' not in result['desc']

    ranked = assess_wuzhi_level(
        '戊', ['丙', '丙', '戊', '庚'], ['卯', '酉', '亥', '子'],
        {'level': 0, 'rank_grade': '独立官级'})
    assert ranked['grade'] == '独立官级'


def test_h89_no_work_and_missing_gongliang_are_distinct():
    args = ('戊', ['丙', '丙', '戊', '庚'], ['卯', '酉', '亥', '子'])
    no_work = assess_wuzhi_level(*args, {'level': 0, 'rank_grade': ''})
    missing = assess_wuzhi_level(*args, None)
    assert no_work['grade'] == '无功（无层次）'
    assert missing['grade'] == '未定（缺 gongliang）'
