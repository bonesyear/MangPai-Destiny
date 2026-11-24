# -*- coding: utf-8 -*-
"""批次26：岁运喜忌、冲合语义、总评与分段边界。"""
from mangpai.subjective.liunian import analyze_liunian_mangpai
from mangpai.subjective.yingqi_subj import detect_daxian_dayun_jiaotuo
from mangpai.subjective.yunfan import analyze_yunfan


CONG_QIANG_GANS = ['壬', '癸', '壬', '丙']
CONG_QIANG_ZHIS = ['子', '卯', '子', '午']


def test_h27_cong_qiang_uses_yin_bijian_not_cai_guan():
    result = analyze_liunian_mangpai(
        [{'gz': '丙子'}], CONG_QIANG_GANS, CONG_QIANG_ZHIS, '壬',
        current_dayun={'gz': '丙午'},
    )['liunian'][0]
    assert any('冲去忌神反吉' in s for s in result['positive_signals'])
    assert not any('冲去喜神反凶' in s for s in result['negative_signals'])

    jiaotuo = detect_daxian_dayun_jiaotuo(
        '壬', CONG_QIANG_GANS, CONG_QIANG_ZHIS, age=40,
        dayun_gan='丙', dayun_zhi='午')
    assert jiaotuo['dayun_jx'] == '凶'

    yunfan = analyze_yunfan(
        CONG_QIANG_GANS, CONG_QIANG_ZHIS, '壬',
        current_dayun={'gz': '丙午'}, liunian_list=[{'gz': '丙午'}],
        natal_work_actions=[], natal_gong_shen=[], natal_fei_shen=[])
    binglin = [m for row in yunfan['suiyun_teshu'] for m in row['teshu']
               if m['teshu_type'] == '岁运并临']
    assert binglin and binglin[0]['direction'] == '凶向'


def test_h27_cong_ruo_uses_cai_guan_not_yin_bijian():
    gans = ['庚', '庚', '甲', '辛']
    zhis = ['申', '午', '寅', '酉']
    result = detect_daxian_dayun_jiaotuo(
        '甲', gans, zhis, age=10, dayun_gan='戊', dayun_zhi='午')
    assert result['dayun_jx'] == '吉'


def _spouse_palace_chong(year_gan, year_zhi):
    result = analyze_liunian_mangpai(
        [{'gz': '甲辰'}], [year_gan, '己', '甲', '辛'],
        [year_zhi, '巳', '戌', '未'], '甲', gender='男',
    )['liunian'][0]
    return next(r['chong_semantic'] for r in result['zhi_relations']
                if r['type'] == '冲' and r['target'] == '戌')


def test_h28_gongju_is_not_half_he_but_true_half_he_is_kept():
    gongju = _spouse_palace_chong('甲', '寅')
    assert gongju['chong_type'] == '冲开'
    assert '婚姻发动' not in gongju['desc']

    half_he = _spouse_palace_chong('戊', '午')
    assert half_he['chong_type'] == '冲动'
    assert '婚姻发动' in half_he['desc']


def test_f58_overall_uses_all_final_signals():
    cases = [
        ({'gz': '丙寅'}, None),
        ({'gz': '甲子'}, {'gz': '乙丑'}),
    ]
    for liunian, dayun in cases:
        result = analyze_liunian_mangpai(
            [liunian], ['辛', '戊', '甲', '戊'], ['辰', '午', '子', '戌'], '甲',
            current_dayun=dayun,
        )['liunian'][0]
        assert result['positive_signals'] and result['negative_signals'], result
        assert result['overall'] == '吉凶参半', result
        assert result['desc'].endswith('综合：吉凶参半'), result['desc']


def test_f60_stem_activation_belongs_to_first_five_years():
    from mangpai.subjective.dayun import analyze_dayun_mangpai

    for gz in ('甲子', '甲午', '甲戌'):
        result = analyze_dayun_mangpai(
            [{'gz': gz, 'start_age': 5, 'end_age': 15}],
            ['己', '丙', '庚', '壬'], ['寅', '子', '午', '辰'], '庚',
            natal_fei_shen=['year_gan'],
        )['dayun'][0]
        gan, zhi = result['segments']
        assert any('激活1个废神' in s for s in gan['positive_signals']), (gz, gan)
        assert not any('激活' in s for s in zhi['positive_signals']), (gz, zhi)


def test_f61_tied_natal_dominant_does_not_invent_fanju():
    from mangpai.subjective.dayun import analyze_dayun_mangpai

    results = {}
    for gz in ('庚申', '甲寅'):
        row = analyze_dayun_mangpai(
            [{'gz': gz, 'start_age': 5, 'end_age': 15}],
            ['甲', '庚', '乙', '辛'], ['寅', '申', '子', '午'], '乙',
        )['dayun'][0]
        assert not any('反局' in s for s in row['negative_signals']), row
        results[gz] = row
    assert results['庚申']['qishi_change']['natal_dominant'] == '不明'
    assert results['甲寅']['qishi_change'] is None


def test_f59_out_of_dayun_year_does_not_trigger_phase():
    from mangpai.subjective.liunian import determine_dayun_phase

    phase = determine_dayun_phase(
        '丁', '亥', [{'gz': '乙巳', 'year': 2025}],
        birth_year=1990, dayun_start_age=37)
    assert phase['phase'] == '统看'
    assert '乙巳' not in phase['reason']
    assert '辛亥' in phase['reason']


def test_f60_branch_activation_belongs_to_second_five_years():
    from mangpai.subjective.dayun import analyze_dayun_mangpai

    row = analyze_dayun_mangpai(
        [{'gz': '甲午', 'start_age': 5, 'end_age': 15}],
        ['己', '丙', '庚', '壬'], ['寅', '子', '午', '辰'], '庚',
        natal_fei_shen=['month_zhi'],
    )['dayun'][0]
    gan, zhi = row['segments']
    assert not any('激活' in s for s in gan['positive_signals'])
    assert any('激活1个废神' in s for s in zhi['positive_signals'])
