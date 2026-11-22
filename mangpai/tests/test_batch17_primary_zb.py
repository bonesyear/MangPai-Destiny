# -*- coding: utf-8 -*-
"""批次17：主功确认与贼捕净制的最小反例。"""
from mangpai.objective._relation_utils import _directed_control_edges
from mangpai.subjective.caiming import _zeishen_jingzhi
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.zeishen_bushen import detect_chong_lian, detect_zeishen_bushen
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _zg(day, day_zhi, year, year_zhi, month, month_zhi, hour, hour_zhi):
    return analyze_zuogong(day, day_zhi, year, year_zhi, month, month_zhi,
                           hour, hour_zhi)


def _zb(gans, zhis):
    zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                         gans[1], zhis[1], gans[3], zhis[3])
    return detect_zeishen_bushen(gans[2], gans, zhis,
                                 work_actions=zg['work_actions'])


def test_g4_tomb_covers_reverse_element_control():
    result = _zg('辛', '未', '癸', '酉', '辛', '酉', '庚', '寅')
    covered = [a for a in result['work_actions']
               if a.get('from_pos') == 'hour_zhi' and a.get('to_pos') == 'day_zhi'
               and a.get('type') == '克']
    assert covered and all(a.get('tomb_covered') and a.get('auxiliary') for a in covered)
    assert result['work_efficiency'] == '低'
    assert all('寅木克未土' not in a.get('desc', '') for a in result['passive_control'])


def test_g5_auxiliary_guest_he_does_not_veto_shengyong():
    result = _zg('丁', '酉', '戊', '子', '癸', '亥', '己', '酉')
    assert result['primary_work']['type'] == '生用'
    assert result['primary_work']['resolution']['winner_rule'] == '生用泄秀'


def test_h182_shengyong_precedes_xieyong():
    result = _zg('甲', '午', '甲', '辰', '庚', '午', '甲', '子')
    assert result['primary_work']['type'] == '生用'
    assert result['primary_work']['path'] == '日干生（食伤泄秀）'


def test_h184_chuan_strength_stays_with_selected_action():
    result = _zg('己', '酉', '壬', '辰', '壬', '子', '甲', '戌')
    assert result['primary_work']['type'] == '制用'
    assert result['primary_work']['path'] == '弃干看支（日支刑冲穿做功）'
    assert any(a.get('type') == '穿' and a.get('primary') for a in result['work_actions'])
    control = _zg('己', '酉', '壬', '辰', '壬', '子', '甲', '寅')
    assert control['primary_work']['path'] == '日干合（合财/合官）'


def test_h49_day_gan_tomb_does_not_disqualify_food_output():
    result = _zg('壬', '辰', '丙', '申', '甲', '午', '乙', '巳')
    assert result['primary_work']['type'] == '生用'
    anchor = _zg('戊', '寅', '丙', '午', '辛', '丑', '壬', '戌')
    assert anchor['primary_work']['type'] in ('制用', '合用')
    assert not any(c['rule'] == '生用泄秀' and not c['vetoed']
                   for c in anchor['primary_work']['candidates'])


def test_h50_wealth_food_he_accepts_either_endpoint():
    result = _zg('庚', '寅', '丙', '辰', '己', '亥', '丙', '戌')
    assert result['primary_work']['type'] == '制用'
    assert any(c['rule'] == '化用成局' and c['vetoed']
               and any('财与原神同宫' in reason for reason in c['veto_reasons'])
               for c in result['primary_work']['candidates'])
    anchor = _zg('庚', '午', '戊', '辰', '己', '未', '丁', '亥')
    assert anchor['primary_work']['type'] == '制用'


def test_h51_mutual_chuan_uses_main_side_strength():
    strong = _zg('丁', '巳', '甲', '午', '丙', '寅', '丙', '午')
    assert '制用' in strong['work_types']
    assert any(a.get('type') == '穿' and not a.get('auxiliary')
               for a in strong['work_actions'])
    weak = _zg('丙', '寅', '丙', '午', '癸', '巳', '甲', '午')
    assert any(a.get('type') == '穿' and a.get('weak_faction')
               for a in weak['work_actions'])


def test_g16_guest_guest_edge_does_not_cleanse_yuanshen():
    gans, zhis = ['己', '己', '乙', '丙'], ['酉', '巳', '未', '子']
    result = _zb(gans, zhis)
    assert result['jing_zhi'] == '不净' and not result['yuanshen_yi_zhi']
    assert not _zeishen_jingzhi('乙', gans, zhis)


def test_g17_equal_length_paths_prefer_actual_chong_chain():
    for zhis, gans in ((['申', '酉', '卯', '丑'], ['甲', '癸', '辛', '己']),
                       (['申', '酉', '寅', '辰'], ['甲', '癸', '壬', '甲'])):
        result = detect_chong_lian(zhis, gans)
        assert result and result['has_chong']


def test_h167_and_h43_remove_false_control_directions():
    gans, zhis = ['丙', '甲', '甲', '丁'], ['午', '午', '子', '卯']
    edges = _directed_control_edges(zhis, gans)
    assert ('午', '子', '冲') in edges and ('子', '午', '克') not in edges
    result = _zb(gans, zhis)
    assert (result['bushen_wx'], result['zeishen_wx'], result['jing_zhi']) == ('火', '水', '不成')
    chain = detect_chong_lian(zhis, gans)
    assert not chain or ('克', '子', '午') not in chain['links']

    gans, zhis = ['甲', '庚', '甲', '壬'], ['子', '午', '子', '申']
    result = _zb(gans, zhis)
    assert result['jing_zhi'] == '不净' and not result['yuanshen_yi_zhi']
    assert analyze_gongliang(day_gan='甲', gans=gans, zhis=zhis)['level'] == 3
