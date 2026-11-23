# -*- coding: utf-8 -*-
"""批次22：婚姻星宫的正配星、合冲刑破与墓库边界。"""
from mangpai.subjective.hunyin import (
    _gong_actions, analyze_hunyin, classify_duohun, classify_dushen_sige,
    classify_hunyin_quality, classify_jiehun_sifa, detect_shuizhong_laoyue,
    infer_jiehun_yingqi, infer_lihun_yingqi,
)


def test_f46_substitute_star_does_not_create_mixed_or_multiple_marriage():
    quality = classify_hunyin_quality(
        '甲', ['丙', '丁', '甲', '丙'], ['子', '卯', '子', '子'], '男')
    assert not any('财星多现' in signal for signal in quality['signals'])
    assert classify_duohun(
        '甲', ['丙', '丁', '甲', '丙'], ['子', '卯', '子', '子'], '男')['is_duohun'] is False
    for gans, zhis in [
        (['壬', '癸', '甲', '丙'], ['子', '亥', '子', '寅']),
        (['丙', '乙', '甲', '丙'], ['寅', '亥', '子', '寅']),
    ]:
        assert classify_dushen_sige('甲', gans, zhis, '女')['is_dushen'] is False
    result = infer_jiehun_yingqi(
        '甲', ['壬', '癸', '甲', '丙'], ['子', '亥', '子', '寅'], '女',
        liunian_gan='丙', liunian_zhi='午')
    assert not any('官杀多杂' in signal for signal in result['signals'])


def test_f50_fuyin_is_not_natal_he():
    result = infer_jiehun_yingqi(
        '甲', ['甲', '丙', '甲', '丙'], ['子', '寅', '子', '寅'], '男',
        liunian_gan='丙', liunian_zhi='午')
    assert not any('合处逢冲' in signal for signal in result['signals'])
    result = infer_lihun_yingqi(
        '甲', ['甲', '丙', '甲', '丙'], ['子', '寅', '子', '寅'], '男',
        liunian_gan='丙', liunian_zhi='午')
    assert any('夫妻宫动散' in signal for signal in result['signals'])
    positive = infer_jiehun_yingqi(
        '甲', ['庚', '丁', '壬', '甲'], ['申', '亥', '子', '辰'], '男',
        liunian_gan='丙', liunian_zhi='午')
    assert any('合处逢冲' in signal for signal in positive['signals'])


def test_f51_po_counts_as_palace_damage():
    result = classify_hunyin_quality(
        '庚', ['辛', '癸', '庚', '己'], ['卯', '巳', '午', '卯'], '男')
    assert '破' in result['gong_attacked']
    assert result['quality'] != '好'
    assert not any('安稳无冲合穿刑' in signal for signal in result['signals'])


def test_h101_day_branch_can_join_star_zhonghuai_not_bonus():
    result = classify_hunyin_quality(
        '壬', ['壬', '癸', '壬', '戊'], ['子', '卯', '子', '申'], '男')
    assert result['quality'] != '好'
    assert any('众坏' in signal for signal in result['signals'])
    result = classify_hunyin_quality(
        '壬', ['壬', '癸', '壬', '甲'], ['子', '卯', '子', '辰'], '男')
    assert any('众坏' in signal and signal.count('子') >= 2
               for signal in result['signals'])


def test_h13_h20_self_xing_does_not_open_tomb():
    result = classify_dushen_sige(
        '戊', ['癸', '丙', '戊', '戊'], ['巳', '辰', '辰', '午'], '男')
    assert '星入墓不开格' in result['grids']
    result = classify_dushen_sige(
        '丙', ['辛', '辛', '丙', '壬'], ['卯', '丑', '辰', '辰'], '女')
    assert '星入墓不开格' in result['grids']
    from mangpai.subjective.xiangfa_ops import xiangfa_fallback
    fallback = xiangfa_fallback('戊', ['癸', '丙', '戊', '戊'], ['巳', '辰', '辰', '午'])
    assert not any('两库互开' in item['desc'] for item in fallback['lianmu_zuogong'])


def test_h14_only_book_listed_zihe_pillars_count():
    result = detect_shuizhong_laoyue(
        '乙', ['己', '丙', '乙', '戊'], ['卯', '子', '巳', '寅'], '男')
    assert result['is_laoyue'] is False
    assert classify_dushen_sige(
        '乙', ['己', '丙', '乙', '戊'], ['卯', '子', '巳', '寅'], '男')['is_dushen'] is False


def test_h15_full_sanhe_and_half_he_share_gong_he_semantics():
    full = classify_hunyin_quality(
        '壬', ['庚', '丁', '壬', '甲'], ['申', '亥', '子', '辰'], '男')
    half = classify_hunyin_quality(
        '壬', ['庚', '丁', '壬', '甲'], ['寅', '亥', '子', '辰'], '男')
    assert full['score'] == half['score']
    assert full['gong_attacked'] == half['gong_attacked']
    for zhis in (['申', '亥', '子', '辰'], ['寅', '亥', '子', '辰']):
        result = classify_jiehun_sifa('壬', ['庚', '丁', '壬', '甲'], zhis, '男')
        assert any('合动夫妻宫' in method for method in result['methods'])


def test_h16_relation_only_xing_does_not_duplicate_attack():
    result = classify_hunyin_quality(
        '庚', ['癸', '辛', '庚', '戊'], ['丑', '酉', '申', '寅'], '男')
    assert result['quality'] == '好'
    for day_zhi, hour_zhi, attack in [
        ('申', '寅', '冲'), ('丑', '未', '冲'), ('巳', '寅', '穿'),
    ]:
        actions = [
            {'type': attack, 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi'},
            {'type': '刑', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi',
             'auxiliary': True, 'relation_only': True},
        ]
        adv, _ = _gong_actions(actions, ['癸', '丑', day_zhi, hour_zhi])
        assert [(kind, other) for kind, other, _ in adv] == [(attack, hour_zhi)]


def test_h17_star_attacking_palace_is_not_palace_rejecting_star():
    assert classify_dushen_sige(
        '甲', ['乙', '丙', '甲', '甲'], ['未', '戌', '子', '戌'], '男')['is_dushen'] is False
    result = classify_dushen_sige(
        '己', ['甲', '丙', '己', '戊'], ['辰', '子', '未', '辰'], '男')
    assert '宫占比劫禄印格' in result['grids']


def test_h18_chuan_does_not_open_tomb_or_add_safe_score():
    result = classify_hunyin_quality(
        '丙', ['辛', '辛', '丙', '甲'], ['卯', '丑', '辰', '午'], '女')
    assert result['quality'] == '差'
    assert not any('安稳无冲合穿刑' in signal for signal in result['signals'])
    summary = analyze_hunyin(
        '丙', ['辛', '辛', '丙', '甲'], ['卯', '丑', '辰', '午'], '女')['summary']
    assert not ('婚姻好' in summary and '独身之象' in summary)


def test_h19_relation_only_xing_does_not_reject_star():
    assert classify_dushen_sige(
        '庚', ['辛', '乙', '庚', '辛'], ['丑', '未', '申', '巳'], '女')['is_dushen'] is False
    result = classify_dushen_sige(
        '庚', ['辛', '乙', '庚', '辛'], ['寅', '未', '申', '巳'], '女')
    assert '宫占比劫禄印格' in result['grids']
