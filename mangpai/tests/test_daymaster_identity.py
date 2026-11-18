# -*- coding: utf-8 -*-
"""日主身份边界：日主不是比劫，也不因未做功而沦为废神。"""


def test_guanming_does_not_borrow_daymaster_as_bijie():
    from mangpai.subjective.guanming import classify_guanming_combo

    result = classify_guanming_combo(
        '甲', ['庚', '辛', '甲', '己'], ['戌', '巳', '午', '巳'])
    assert result['is_guanming'] is False
    assert result['zhiyong_combos'] == []


def test_deprecated_junguan_does_not_count_daymaster_as_bijie():
    from mangpai.subjective.gongmen_wuzhi import classify_junguan

    result = classify_junguan('甲', ['辛', '辛', '甲', '癸'], ['丑', '丑', '子', '酉'])
    assert result['is_junguan'] is False
    day_branch = classify_junguan(
        '甲', ['辛', '辛', '甲', '癸'], ['丑', '丑', '寅', '酉'])
    assert '官杀配比劫/比劫库' in day_branch['combos']


def test_liuqin_daymaster_is_not_an_extra_bijie():
    from mangpai.subjective.liuqin import (
        classify_parent_star, classify_xiongdi_shuliang, detect_zixi_youwu,
    )

    siblings = classify_xiongdi_shuliang(
        '甲', ['庚', '戊', '甲', '丙'], ['寅', '寅', '午', '子'])
    assert siblings['wuji_bifan'] is False
    assert siblings['estimate'] == 5
    child = detect_zixi_youwu(
        '甲', ['庚', '戊', '甲', '庚'], ['午', '子', '子', '午'], '女')
    assert child['has_zixi'] is True
    assert child['markers_count'] == 1
    parent = classify_parent_star(
        '丁', ['壬', '壬', '丁', '庚'], ['申', '子', '酉', '子'])
    assert parent['mother_variant'] != '比劫'


def test_qucai_daymaster_control_is_not_risky_bijie():
    from mangpai.subjective.caiming import classify_qucai_method

    result = classify_qucai_method(
        '甲', ['壬', '癸', '甲', '戊'], ['子', '丑', '子', '申'])
    assert result['methods'] == ['经营', '体力']
    assert all('劫刃制财' not in x for x in result['details'])


def test_xiangfa_daymaster_has_no_bijie_hat_or_gongxiang():
    from mangpai.subjective.xiangfa_ops import daixiang, gongxiang

    gans, zhis = ['丙', '庚', '甲', '丙'], ['寅', '寅', '申', '寅']
    assert not any(f['pillar'] == '日柱' and f.get('combo') == '官带比劫帽'
                   for f in daixiang('甲', gans, zhis))
    assert not any(f['pillar'] == '日柱' and f.get('domain') == '比劫'
                   for f in gongxiang('甲', gans, zhis))


def test_day_pillar_daxian_uses_daymaster_not_bijie_vote():
    from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi

    result = infer_comprehensive_yingqi(
        '甲', ['庚', '乙', '甲', '庚'], ['申', '酉', '申', '午'],
        dayun_gan='己', dayun_zhi='丑', age=40)
    assert '比肩' not in result['daxian_yingqi']['content']
    jiaotuo = result['daxian_dayun_jiaotuo']
    assert jiaotuo['daxian_jx'] == '凶'
    assert any(m['jiaotuo_type'] == '限运俱凶' for m in jiaotuo['markers'])


def test_yunshi_daymaster_is_not_fei_shen():
    from mangpai.objective.dayun import _analyze_fei_shen_activation
    from mangpai.subjective.yunfan import analyze_yunfan

    activated = _analyze_fei_shen_activation(
        '辛', '酉', ['day_gan'], ['癸', '癸', '甲', '癸'], ['亥', '亥', '子', '酉'])
    assert activated == []
    result = analyze_yunfan(
        ['壬', '癸', '甲', '壬'], ['辰', '丑', '辰', '申'], '甲',
        liunian_list=[{'gz': '壬子', 'year': 2032}, {'gz': '庚申', 'year': 2040}])
    by_year = {r['year']: r for r in result['liunian_fan']}
    assert all('引动忌神' not in f['fan_type'] for f in by_year.get(2032, {}).get('fans', []))
    assert any('生废神水' in f.get('reason', '')
               for f in by_year.get(2040, {}).get('fans', []))
