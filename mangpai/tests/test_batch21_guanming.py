# -*- coding: utf-8 -*-
"""批次21：官命判定、否决门槛与行业输出。"""
from mangpai.subjective.guanming import (
    _ensure_relations, analyze_guanming, classify_guanming_combo,
    classify_hangye_xiang,
)


def _combo(gans, zhis, **kwargs):
    return classify_guanming_combo(gans[2], gans, zhis, **kwargs)


def _analyze(gans, zhis):
    return analyze_guanming(gans[2], gans, zhis)


def test_g10_mutual_control_does_not_depend_on_action_order():
    for gans, zhis in [
        (['壬', '庚', '己', '癸'], ['申', '戌', '未', '酉']),
        (['己', '辛', '戊', '庚'], ['巳', '未', '戌', '申']),
    ]:
        rel = _ensure_relations(gans[2], gans, zhis, None)
        reversed_actions = []
        for action in rel['work_actions']:
            other = dict(action)
            if action.get('relation_direction') == 'mutual':
                other['from_pos'], other['to_pos'] = action['to_pos'], action['from_pos']
            reversed_actions.append(other)
        reversed_rel = dict(rel, work_actions=reversed_actions)
        assert (_combo(gans, zhis)['is_guanming']
                == _combo(gans, zhis, relations=reversed_rel)['is_guanming'])


def test_g11_one_attacker_is_not_surrounding():
    result = _combo(['戊', '庚', '己', '戊'], ['辰', '申', '巳', '辰'])
    assert result['is_guanming'] is True
    result = _combo(['壬', '壬', '乙', '壬'], ['寅', '子', '未', '午'])
    assert '印制伤食' in result['zhiyong_combos']
    assert result['is_guanming'] is True


def test_g9_outgoing_action_is_not_an_attacker():
    result = _combo(['丁', '丁', '乙', '戊'], ['亥', '未', '巳', '寅'])
    assert '藏杀被制' not in result['zhiyong_combos']
    assert result['is_guanming'] is False


def test_h12_caixing_fanju_respects_positive_structure():
    for gans, zhis in [
        (['丁', '丙', '庚', '戊'], ['未', '午', '申', '寅']),
        (['丁', '甲', '戊', '甲'], ['酉', '辰', '午', '子']),
    ]:
        result = _analyze(gans, zhis)
        assert result['is_guanming'] is True
        assert result['veto_reasons'] == []


def test_h90_luren_must_match_day_element():
    assert _combo(['庚', '庚', '戊', '戊'], ['戌', '辰', '辰', '午'])[
        'is_guanming'] is False
    assert _combo(['庚', '庚', '戊', '戊'], ['戌', '辰', '辰', '未'])[
        'is_guanming'] is True
    assert _combo(['庚', '庚', '戊', '戊'], ['戌', '辰', '辰', '申'])[
        'is_guanming'] is False


def test_h91_lone_bijie_exception_also_checks_surrounding():
    result = _combo(['甲', '甲', '戊', '甲'], ['子', '戌', '辰', '寅'],
                    kong_wang=['戌', '亥'])
    assert result['zhiyong_combos'] == []
    assert result['is_guanming'] is False
    assert any('围制财源' in detail for detail in result['details'])


def test_h92_same_direction_actions_are_not_mutual_war():
    result = _combo(['己', '戊', '丁', '丙'], ['卯', '辰', '巳', '午'])
    assert '印制伤食' in result['zhiyong_combos']
    assert result['is_guanming'] is True


def test_h94_tomb_cannot_exempt_its_own_controlled_branch():
    result = _combo(['甲', '甲', '癸', '甲'], ['寅', '寅', '卯', '辰'],
                    kong_wang=['辰', '巳'])
    assert result['is_guanming'] is False
    assert any('官星被制空亡' in detail for detail in result['details'])
    exempt = _combo(['甲', '甲', '癸', '甲'], ['寅', '寅', '丑', '辰'],
                    kong_wang=['丑', '辰', '巳'])
    assert exempt['is_guanming'] is True
    for gans, zhis in [
        (['癸', '丁', '壬', '庚'], ['卯', '巳', '申', '戌']),
        (['丙', '辛', '戊', '丁'], ['午', '丑', '寅', '巳']),
        (['庚', '乙', '癸', '庚'], ['辰', '酉', '卯', '申']),
    ]:
        assert _analyze(gans, zhis)['is_guanming'] is True


def test_g12_non_guanming_summary_does_not_claim_office_or_industry():
    for gans, zhis in [
        (['戊', '己', '乙', '丁'], ['戌', '未', '巳', '亥']),
        (['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未']),
    ]:
        result = _analyze(gans, zhis)
        assert result['is_guanming'] is False
        assert result['primary_combo'] == ''
        assert result['primary_hangye'] == '未明'
        assert '管财的官' not in result['summary']
        assert '财政/金融/税务' not in result['summary']


def test_g13_combo_names_are_normalized_and_explicit():
    gans, zhis = ['壬', '丙', '壬', '丙'], ['子', '午', '辰', '午']
    result = classify_hangye_xiang('壬', gans, zhis)
    assert '军警' in result['primary']
    assert '财政/金融/税务' not in result['primary']
    mapped = {
        '伤食制官杀', '劫刃制官杀', '官杀制比劫', '官杀制伤食', '印制伤食',
        '财制印', '印化官杀', '官禄格', '印带官帽',
    }
    unmapped = {
        '藏杀被制', '伤食制印', '印制财', '印配比禄·比劫制印库', '贼捕制印',
        '贼捕制官杀', '合制·自合制官', '合制·食合官支', '伤官诀', '劫刃制财',
    }
    for name in sorted(mapped):
        result = classify_hangye_xiang('壬', gans, zhis, {
            'is_guanming': True, 'zhiyong_combos': [name], 'shengyong_huayong': [],
        })
        assert result['by_combo']
    for name in sorted(unmapped):
        result = classify_hangye_xiang('壬', gans, zhis, {
            'is_guanming': True, 'zhiyong_combos': [name], 'shengyong_huayong': [],
        })
        assert any(name in detail and '无行业映射' in detail
                   for detail in result['details'])
