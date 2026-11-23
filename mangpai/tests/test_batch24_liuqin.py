# -*- coding: utf-8 -*-
"""批次24：六亲判定与 LLM 输出边界。"""
import json

from mangpai.engine import calc_mangpai_full
from mangpai.subjective import build_payload
from mangpai.subjective.liuqin import (
    classify_parent_star, classify_xiongdi_qingyi, classify_xiongdi_shuliang,
    detect_parent_duohun, detect_parent_qiyang, detect_parent_zaoshi,
    detect_zixi_xingbie, detect_zixi_youwu,
)
from mangpai.subjective.narrative import _liuqin_line


def test_f48_tomb_requires_open_or_missing_origin_and_payload_scrubs_death():
    result = detect_parent_zaoshi(
        '甲', ['戊', '丙', '甲', '己'], ['辰', '寅', '子', '巳'])
    assert result['is_zaoshi'] is False
    assert not any('三刑夹刑' in marker for marker in result['markers'])
    payload = build_payload({'liuqin': {
        'parent_zaoshi': {'is_zaoshi': True, 'markers': ['父星戊坐辰墓库']},
        'xiongdi_keshun': {'has_keshun': True, 'markers': ['兄弟有损']},
    }})
    assert 'is_zaoshi' not in json.dumps(payload, ensure_ascii=False)
    assert 'has_keshun' not in json.dumps(payload, ensure_ascii=False)


def test_g24_payload_and_narrative_do_not_expose_child_gender():
    result = calc_mangpai_full(1990, 5, 10, 8, 0, 'male', 116.4)  # synthetic
    blob = json.dumps(build_payload(result), ensure_ascii=False)
    assert 'final_gender' not in blob
    assert 'base_gender' not in blob
    assert '头胎男' not in blob and '头胎女' not in blob
    assert '生女' not in blob and '生儿' not in blob and '双女' not in blob
    payload = build_payload({'liuqin': {
        'summary': '六亲论断；头胎男；兄弟和睦',
        'zixi_xingbie': {'final_gender': '男', 'desc': '头胎男'},
    }})
    assert 'final_gender' not in json.dumps(payload, ensure_ascii=False)
    assert payload['liuqin']['summary'] == '六亲论断；兄弟和睦'
    assert '头胎' not in _liuqin_line({'summary': '六亲论断；头胎男；兄弟和睦'})


def test_h121_year_pian_cai_requires_actual_benqi():
    assert detect_parent_qiyang(
        '壬', ['丙', '壬', '壬', '乙'], ['午', '辰', '申', '巳'])['is_qiyang'] is False
    result = detect_parent_qiyang(
        '壬', ['丙', '壬', '壬', '乙'], ['巳', '辰', '申', '巳'])
    assert any('干支皆偏财' in marker for marker in result['markers'])


def test_h122_sanhe_participants_count_for_qiyang_and_qingyi():
    full = detect_parent_qiyang('己', ['乙', '乙', '己', '丁'], ['巳', '酉', '丑', '卯'])
    half = detect_parent_qiyang('己', ['乙', '乙', '己', '丁'], ['卯', '酉', '丑', '卯'])
    assert full['is_qiyang'] is True and half['is_qiyang'] is True
    assert any('被合绊' in marker for marker in full['markers'])
    assert classify_xiongdi_qingyi(
        '己', ['乙', '乙', '己', '丁'], ['巳', '酉', '丑', '卯'])['verdict'] == '厚'


def test_h124_day_master_he_does_not_flip_child_gender():
    result = detect_zixi_xingbie(
        '甲', ['甲', '己', '甲', '戊'], ['辰', '巳', '午', '辰'], '女')
    assert result['huanxiang'] is False
    assert result['final_gender'] == '男'
    positive = detect_zixi_xingbie(
        '甲', ['辛', '己', '甲', '丙'], ['辰', '巳', '午', '辰'], '女')
    assert positive['huanxiang'] is True
    assert positive['final_gender'] == '男'


def test_h30_unopened_tomb_and_controlled_tomb_count():
    result = detect_zixi_youwu(
        '丙', ['乙', '己', '丙', '壬'], ['亥', '卯', '午', '辰'], '男')
    assert result['has_zixi'] is False
    assert any('入辰墓不开' in marker for marker in result['markers'])
    result = detect_zixi_youwu(
        '癸', ['壬', '乙', '癸', '庚'], ['丑', '巳', '丑', '戌'], '男')
    assert result['has_zixi'] is False
    assert any('入戌墓不开' in marker for marker in result['markers'])


def test_h32_shishang_tomb_must_match_element():
    result = detect_parent_qiyang(
        '甲', ['丁', '癸', '甲', '壬'], ['丑', '卯', '寅', '申'])
    assert not any('入丑墓' in marker for marker in result['markers'])
    result = detect_parent_qiyang(
        '甲', ['丙', '癸', '甲', '壬'], ['戌', '卯', '寅', '申'])
    assert any('入戌墓' in marker for marker in result['markers'])


def test_h33_parent_star_fuyin_includes_branches():
    result = detect_parent_duohun(
        '乙', ['己', '丁', '乙', '丁'], ['巳', '丑', '亥', '亥'])
    assert result['is_duohun'] is True
    assert any('母星亥伏吟' in marker for marker in result['markers'])


def test_h34_month_gan_bijie_is_not_counted_twice():
    result = classify_xiongdi_shuliang(
        '甲', ['戊', '乙', '甲', '癸'], ['辰', '丑', '申', '酉'])
    assert result['estimate'] == 5
    assert not any('月令比劫旺地' in factor for factor in result['factors'])
    other = classify_xiongdi_shuliang(
        '甲', ['乙', '己', '甲', '癸'], ['辰', '丑', '申', '酉'])
    assert other['estimate'] == result['estimate']


def test_h35_kongwang_and_attack_are_one_palace_marker():
    relations = {
        'kong_wang_zhis': ['亥'],
        'work_actions': [{'type': '穿', 'from_pos': 'month_zhi', 'to_pos': 'hour_zhi'}],
    }
    result = detect_zixi_youwu(
        '甲', ['己', '壬', '甲', '乙'], ['酉', '申', '子', '亥'], '男', relations)
    assert result['has_zixi'] is True
    assert result['markers_count'] == 1
    assert '子息有阻（单标志' in result['desc']


def test_h36_generic_ke_is_not_actual_cai_ke_yin():
    for gans, zhis in [
        (['戊', '戊', '丙', '丁'], ['寅', '午', '午', '酉']),
        (['甲', '庚', '丙', '戊'], ['子', '午', '寅', '戌']),
    ]:
        assert classify_parent_star(gans[2], gans, zhis)['father_variant'] == ''
