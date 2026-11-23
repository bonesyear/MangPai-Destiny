# -*- coding: utf-8 -*-
"""批次25：牢狱方向、墓库与魁罡边界。"""
from mangpai.subjective.laoyu import (
    analyze_laoyu, detect_guansha_rumu, detect_kuigang, detect_laoyu_zi,
)


def test_f53_open_tomb_counts_risk_not_less_than_closed():
    opened = analyze_laoyu('甲', ['辛', '乙', '甲', '丙'], ['丑', '未', '寅', '寅'])
    closed = analyze_laoyu('甲', ['辛', '庚', '甲', '丙'], ['丑', '寅', '寅', '寅'])
    assert opened['hit_count'] >= closed['hit_count']
    assert opened['risk'] == closed['risk']
    assert '官杀墓动' in opened['methods']
    assert '官杀入墓' in closed['methods']


def test_h24_only_actor_can_destroy_yang_not_be_controlled():
    result = detect_laoyu_zi('甲', ['丙', '己', '甲', '丙'], ['戌', '亥', '子', '寅'])
    assert result['yin_mie_yang'] is False
    assert result['yang_zhi_yin'] is True
    full = analyze_laoyu('甲', ['丙', '己', '甲', '丙'], ['戌', '亥', '子', '寅'])
    assert full['methods'] == ['枭神夺食']
    assert full['risk'] == '无'


def test_h25_muku_status_is_single_source_for_tomb_open():
    for gans, zhis in [
        (['辛', '壬', '甲', '辛'], ['丑', '辰', '子', '未']),
        (['庚', '庚', '丙', '庚'], ['辰', '辰', '寅', '寅']),
        (['癸', '己', '甲', '丙'], ['丑', '未', '寅', '寅']),
    ]:
        result = detect_guansha_rumu(gans[2], gans, zhis)
        assert result['tomb_open'] is False
        assert result['laoyu_signal'] is True


def test_h26_kuigang_day_itself_is_not_zhihua():
    for gans, zhis in [
        (['丙', '庚', '庚', '乙'], ['酉', '酉', '辰', '酉']),
        (['丙', '庚', '庚', '乙'], ['酉', '酉', '戌', '酉']),
        (['甲', '戊', '戊', '乙'], ['子', '子', '戌', '亥']),
    ]:
        result = detect_kuigang(gans[2], gans, zhis)
        assert result['wu_zhi'] is True
        assert result['with_guansha'] is True
        assert result['laoyu_signal'] is True
