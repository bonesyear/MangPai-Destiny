# -*- coding: utf-8 -*-
"""批次27A：诀法共享事实与输出边界。"""
from mangpai.subjective.juefa import analyze_juefa
from mangpai.subjective.yongshen import assess_direction_signals


def _duanyu(r, rid):
    return [h for h in r['duanyu_hits'] if h['id'] == rid]


def test_h107_duanyu17_consumes_actual_duocai_direction():
    gans = ['戊', '甲', '甲', '乙']
    zhis = ['辰', '寅', '辰', '亥']
    not_duocai = analyze_juefa(
        gans, zhis, '甲', yongshen_result={
            'bijiao_duocai': {'detected': False, 'strength': '身强'}},
    )
    assert not _duanyu(not_duocai, 17)

    duocai = analyze_juefa(
        gans, zhis, '甲', yongshen_result={
            'bijiao_duocai': {'detected': True, 'strength': '身强'}},
    )
    assert _duanyu(duocai, 17)


def test_h107_gongliang_short_result_keeps_strength():
    result = assess_direction_signals(
        '甲', ['戊', '甲', '甲', '乙'], ['辰', '寅', '辰', '亥'],
        gongliang_result={'pocai_signal': True, 'pocai_severity': 'normal',
                          'pocai_reason': 'test'},
    )
    assert result['bijiao_duocai']['detected'] is True
    assert result['bijiao_duocai']['strength'] == '身强'


def test_f42_liuhe_closes_tomb_and_siku_is_not_sanhe():
    female = analyze_juefa(
        ['乙', '戊', '甲', '丙'], ['丑', '子', '午', '寅'], '甲', gender='female')
    detail = _duanyu(female, 8)[0]['detail']
    assert '紧闭' in detail and '凶减' not in detail

    siku = analyze_juefa(
        ['丙', '辛', '丁', '丙'], ['辰', '丑', '卯', '午'], '丁')
    assert '会库' not in _duanyu(siku, 3)[0]['detail']

    half_he = analyze_juefa(
        ['壬', '壬', '壬', '丙'], ['戌', '戌', '戌', '午'], '壬')
    assert '半合' in _duanyu(half_he, 3)[0]['detail']


def test_f43_h102_guansha_evidence_is_deterministic_and_hidden_aware():
    result = analyze_juefa(
        ['甲', '己', '甲', '己'], ['子', '巳', '子', '巳'], '甲')
    assert _duanyu(result, 12)[0]['detail'].startswith('两己争合一甲；两甲争合一己')

    hidden = analyze_juefa(
        ['丙', '丁', '甲', '丙'], ['寅', '巳', '午', '寅'], '甲', gender='female')
    assert '官杀全无' not in _duanyu(hidden, 13)[0]['detail']
    assert '仅藏' in _duanyu(hidden, 13)[0]['detail']

    no_guansha = analyze_juefa(
        ['壬', '壬', '甲', '甲'], ['子', '寅', '子', '子'], '甲', gender='female')
    marker = next(h['marker'] for h in no_guansha['duanyu_a'] if h['id'] == 13)
    assert '食伤' not in marker and '夫星偏弱' in marker


def test_h111_shuimu_requires_real_shangguan_and_metal_root():
    for hour in ('丙午', '丙戌'):
        if hour == '丙戌':
            pillars = (['甲', '丙', '壬', '丙'], ['午', '寅', '戌', '午'])
        else:
            pillars = (['甲', '丙', '壬', '丙'], ['午', '寅', '午', '午'])
        result = analyze_juefa(*pillars, '壬')
        assert result['shangguan_jue']['matched'] is False


def _duanju(r, text):
    return [h for h in r['duanju_hits'] if h['text'].startswith(text)]


def test_h103_jiecai_sitting_on_zhengguan_is_reachable():
    result = analyze_juefa(
        ['庚', '乙', '甲', '甲'], ['午', '酉', '子', '子'], '甲')
    hits = _duanju(result, '劫财下面带的官')
    assert len(hits) == 1 and '坐下' in hits[0]['detail']


def test_h106_shishen_chuan_sha_uses_branch_benqi():
    result = analyze_juefa(
        ['己', '癸', '丁', '庚'], ['未', '酉', '卯', '子'], '丁')
    hits = _duanju(result, '食神穿杀')
    assert len(hits) == 1 and '未' in hits[0]['detail'] and '子' in hits[0]['detail']


def test_h104_real_gan_ren_above_tianyi_triggers_duanyu18():
    from mangpai.objective.shensha import compute_shensha_ext

    gans = ['乙', '戊', '甲', '甲']
    zhis = ['丑', '寅', '子', '子']
    shensha = compute_shensha_ext('甲', zhis, gans=gans)
    result = analyze_juefa(gans, zhis, '甲', shensha_result=shensha)
    assert _duanyu(result, 18)
    assert '羊刃' in _duanyu(result, 18)[0]['detail']


def test_h105_competing_partner_uses_actual_ten_god():
    food = analyze_juefa(
        ['丙', '辛', '甲', '丙'], ['寅', '酉', '子', '午'], '甲', gender='female')
    detail = _duanyu(food, 10)[0]['detail']
    assert '食神争合夫星' in detail and '比劫争合' not in detail

    peer = analyze_juefa(
        ['乙', '庚', '乙', '丙'], ['卯', '申', '巳', '午'], '乙', gender='female')
    assert '比劫争合夫星' in _duanyu(peer, 10)[0]['detail']


def test_h108_lu_and_branch_benqi_do_not_count_twice():
    for gans, zhis in [
        (['庚', '戊', '己', '庚'], ['午', '寅', '丑', '午']),
        (['辛', '庚', '戊', '丁'], ['巳', '寅', '子', '巳']),
    ]:
        assert not _duanyu(analyze_juefa(gans, zhis, gans[2]), 1)


def test_h109_spouse_branch_does_not_require_visible_stem():
    female = analyze_juefa(
        ['癸', '乙', '甲', '丙'], ['酉', '卯', '戌', '寅'], '甲', gender='female')
    assert _duanju(female, '夫宫穿夫星')

    male = analyze_juefa(
        ['戊', '庚', '甲', '丙'], ['未', '午', '子', '寅'], '甲', gender='male')
    assert _duanju(male, '夫宫穿夫星')


def test_h110_same_duanju_rule_is_emitted_once():
    result = analyze_juefa(
        ['辛', '辛', '乙', '丙'], ['酉', '丑', '卯', '子'], '乙')
    assert len(_duanju(result, '伤官合官')) == 1
    assert result['hit_count'] == (len(result['duanyu_hits'])
                                 + len(result['duanju_hits'])
                                 + len(result['zipengzi_hits']))


def test_a34_public_analysis_entries_normalize_gender_aliases():
    from mangpai.objective.gongshen import analyze_gongshen
    from mangpai.subjective.hunyin import analyze_hunyin
    from mangpai.subjective.liunian import analyze_liunian_mangpai
    from mangpai.subjective.liuqin import analyze_liuqin
    from mangpai.subjective.zinv import analyze_zinv
    import pytest

    gans = ['庚', '乙', '庚', '辛']
    zhis = ['午', '酉', '子', '巳']
    callers = [
        lambda gender: analyze_juefa(gans, zhis, '庚', gender=gender),
        lambda gender: analyze_liuqin('庚', gans, zhis, gender=gender),
        lambda gender: analyze_hunyin('庚', gans, zhis, gender=gender),
        lambda gender: analyze_gongshen(
            '庚', '午', '辛', '酉', '庚', '午', '乙', '亥', gender=gender),
        lambda gender: analyze_liunian_mangpai(
            [{'gz': '甲子'}], gans, zhis, '庚', gender=gender),
        lambda gender: analyze_zinv('庚', gans, zhis, gender=gender),
    ]
    for call in callers:
        assert call('male') == call('男') == call('乾')
        assert call('female') == call('女') == call('坤')
        for invalid in ('xyz', '', []):
            with pytest.raises(ValueError, match='gender'):
                call(invalid)
