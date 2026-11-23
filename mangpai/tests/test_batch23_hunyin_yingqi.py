# -*- coding: utf-8 -*-
"""批次23：婚姻应期的入墓、拱局、禄刃与冲宫分向。"""
from mangpai.subjective.hunyin import (
    _star_in_tomb, classify_duohun, classify_dushen_sige,
    infer_jiehun_yingqi, infer_lihun_yingqi,
)


def test_h21_single_zheng_branch_does_not_enter_tomb():
    result = infer_jiehun_yingqi(
        '丙', ['甲', '丁', '丙', '庚'], ['辰', '卯', '子', '寅'], '男',
        liunian_gan='戊', liunian_zhi='戌')
    assert not any('刑冲开辰墓' in signal for signal in result['signals'])
    result = infer_jiehun_yingqi(
        '丙', ['壬', '丁', '丙', '庚'], ['辰', '卯', '子', '寅'], '男',
        liunian_gan='戊', liunian_zhi='戌')
    assert any('刑冲开辰墓' in signal for signal in result['signals'])


def test_h22_arch_is_not_half_he_and_li_hun_wins():
    married = infer_jiehun_yingqi(
        '壬', ['甲', '丁', '壬', '甲'], ['戌', '卯', '寅', '辰'], '男',
        liunian_gan='戊', liunian_zhi='申')
    assert not any('合处逢冲' in signal for signal in married['signals'])
    divorced = infer_lihun_yingqi(
        '壬', ['甲', '丁', '壬', '甲'], ['戌', '卯', '寅', '辰'], '男',
        liunian_gan='戊', liunian_zhi='申')
    assert any('夫妻宫动散' in signal for signal in divorced['signals'])


def test_h23_tomb_itself_is_not_a_spouse_star():
    for day_gan, zhis, gender in [
        ('甲', ['午', '寅', '辰', '寅'], '男'),
        ('甲', ['午', '寅', '戌', '寅'], '男'),
        ('壬', ['午', '寅', '辰', '寅'], '女'),
    ]:
        gans = [day_gan, '午', day_gan, day_gan]
        assert _star_in_tomb(day_gan, gans, zhis, gender) == []
        assert classify_dushen_sige(day_gan, gans, zhis, gender)['is_dushen'] is False
        assert classify_duohun(day_gan, gans, zhis, gender)['is_duohun'] is False


def test_h97_hour_luren_uses_actual_lu_ren_table():
    assert classify_dushen_sige(
        '乙', ['庚', '己', '乙', '戊'], ['午', '卯', '亥', '寅'], '男')['is_dushen'] is False
    result = classify_dushen_sige(
        '己', ['甲', '壬', '己', '庚'], ['子', '申', '巳', '午'], '男')
    assert '宫占比劫禄印格' in result['grids']


def test_h98_same_chong_cannot_signal_marriage_and_divorce():
    married = infer_jiehun_yingqi(
        '丙', ['辛', '辛', '丙', '甲'], ['卯', '丑', '辰', '午'], '女',
        liunian_gan='甲', liunian_zhi='戌')
    divorced = infer_lihun_yingqi(
        '丙', ['辛', '辛', '丙', '甲'], ['卯', '丑', '辰', '午'], '女',
        liunian_gan='甲', liunian_zhi='戌')
    assert not any('刑冲开辰墓' in signal for signal in married['signals'])
    assert any('夫妻宫动散' in signal for signal in divorced['signals'])
