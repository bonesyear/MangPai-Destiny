# -*- coding: utf-8 -*-
"""哨兵：subjective.dayun 气势变化不一律标吉（2026-10-17 修复批）。

书证：mangpai-zhongji.txt:314-316「最怕行反局大运，即行运正好与原局表达的
意思相反，或行运与原局势力对抗而无法被原局制之，主此大运凶」——气势变化
非必吉：新主导五行克原局主导五行（势力对抗）判反局入 negative_signals；
其余变化为中性，不进 positive_signals，desc 标「须辨正反」。输出键结构不变。
"""
from mangpai.subjective.dayun import judge_pillar_signals


def _mk_qishi(natal_wx, new_wx):
    return {'changed': True, 'natal_dominant': natal_wx, 'new_dominant': new_wx,
            'desc': f'大运加入后{new_wx}旺成势（原{natal_wx}为主）'}


def test_qishi_fanju_goes_negative():
    """原木为主、运后金旺成势（金克木=势力对抗）-> 反局入负面信号。"""
    r = judge_pillar_signals({'qishi_change': _mk_qishi('木', '金')})
    assert any('反局' in s for s in r['negative_signals'])
    assert not any('成势' in s for s in r['positive_signals'])
    assert '反局' in r['desc']


def test_qishi_neutral_not_positive():
    """原火为主、运后土旺成势（火生土，非对抗）-> 中性：不进正/负信号。"""
    r = judge_pillar_signals({'qishi_change': _mk_qishi('火', '土')})
    assert not any('成势' in s for s in r['positive_signals'])
    assert not any('成势' in s for s in r['negative_signals'])
    assert '须辨正反' in r['desc']
    assert set(r.keys()) >= {'positive_signals', 'negative_signals', 'overall', 'desc'}


def test_current_dayun_uses_virtual_age(monkeypatch):
    """精确交运不可用时按立春虚岁回退：2010 虚岁 11 进入第二步运。"""
    from mangpai.engine import MangpaiEngine

    monkeypatch.setattr('mangpai.engine.safe_compute_jiaoyun',
                        lambda *a, **k: {'timeline': []})

    data = {
        'bazi': {'year': '庚辰', 'month': '戊子', 'day': '甲午', 'hour': '甲子'},
        'input': {'year': 2000, 'gender': '男'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'da_yun': {'start_age': 1, 'dayun': [
            {'gz': '甲子', 'start_age': 1, 'end_age': 11},
            {'gz': '乙丑', 'start_age': 11, 'end_age': 21},
        ]},
        'liunian': [{'gz': '戊申', 'year': 2010}],
    }
    result = MangpaiEngine(data, as_of='2010-06-01').compute_all()
    phase = result['liunian_analysis']['dayun_phase']['per_year'][2010]
    assert phase['position'] == 1, phase
    assert phase['active'] == '干', phase


def test_dayun_segments_split_stem_and_branch():
    """分看：甲木正官为吉、寅支冲命局为凶；整运混合但干/支不得混判。"""
    from mangpai.subjective.dayun import analyze_dayun_mangpai

    result = analyze_dayun_mangpai(
        [{'gz': '甲寅', 'start_age': 1, 'end_age': 11}],
        ['丁', '癸', '己', '庚'], ['酉', '丑', '卯', '申'], '己')
    segments = result['dayun'][0]['segments']
    assert len(segments) == 2, segments
    gan, zhi = segments
    assert (gan['part'], gan['start_age'], gan['end_age']) == ('干', 1, 6), gan
    assert (zhi['part'], zhi['start_age'], zhi['end_age']) == ('支', 6, 11), zhi
    assert gan['overall'] == '吉', gan
    assert zhi['overall'] == '凶', zhi


def test_yingqi_anchor_uses_segments_and_phase():
    """应期锚定使用干/支分段及分统信息，无年龄锚时仍用第 N 步。"""
    from mangpai.subjective.llm_prompt import _yingqi_anchor

    features = {
        'dayun_analysis': {'dayun': [{
            'gz': '甲寅', 'start_age': 1, 'end_age': 11,
            'overall': '吉凶参半',
            'segments': [
                {'part': '干', 'start_age': 1, 'end_age': 6, 'overall': '吉'},
                {'part': '支', 'start_age': 6, 'end_age': 11, 'overall': '凶'},
            ],
        }]},
        'liunian_analysis': {'dayun_phase': {
            'phase': '分看', 'reason': '流年未与大运刑冲合',
        }},
    }
    text = _yingqi_anchor(features)
    assert '甲寅运[干1-6岁]=吉' in text, text
    assert '甲寅运[支6-11岁]=凶' in text, text
    assert '大运分统：分看（流年未与大运刑冲合）' in text, text


def test_yingqi_anchor_tongkan_uses_overall_not_segments():
    """统看只引整运，分看才拆干支；逐年 overall 不被十年总评覆盖。"""
    from mangpai.subjective.llm_prompt import _yingqi_anchor

    features = {
        'dayun_analysis': {'dayun': [{
            'gz': '甲寅', 'start_age': 1, 'end_age': 11,
            'overall': '吉凶参半',
            'segments': [
                {'part': '干', 'start_age': 1, 'end_age': 6, 'overall': '吉'},
                {'part': '支', 'start_age': 6, 'end_age': 11, 'overall': '凶'},
            ],
        }]},
        'liunian_analysis': {
            'dayun_phase': {'phase': '统看', 'reason': '己未年甲己合', 'gz': '甲寅'},
            'liunian': [{'gz': '己未', 'overall': '吉', 'dayun_phase_active': '干支'}],
        },
    }
    text = _yingqi_anchor(features)
    assert '甲寅运[1-11岁]=吉凶参半' in text, text
    assert '甲寅运[干' not in text, text
    assert '己未=吉' in text, text


def test_dayun_phase_includes_current_gz():
    from mangpai.subjective.liunian import determine_dayun_phase

    phase = determine_dayun_phase('甲', '寅', [{'gz': '己未', 'year': 1979}])
    assert phase['gz'] == '甲寅'


def test_liunian_relation_types_are_triggers():
    """冲合刑穿墓任一关系都算流年触发，不要求必须透干或到禄。"""
    from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi

    for kind in ('冲', '六合', '刑', '穿', '墓'):
        result = infer_comprehensive_yingqi(
            '甲', ['甲', '壬', '丙', '丁'], ['子', '午', '寅', '卯'],
            dayun_gan='庚', dayun_zhi='子', liunian_gan='庚', liunian_zhi='辰',
            age=20, liunian_interaction=[{'type': kind, 'target': '午'}])
        assert result['liunian_trigger'] is True, (kind, result)
        assert any('关系' in s for s in result['liunian_yingqi']['signals']), (kind, result)
    for kind in ('克', '生'):
        result = infer_comprehensive_yingqi(
            '甲', ['甲', '壬', '丙', '丁'], ['子', '午', '寅', '卯'],
            dayun_gan='庚', dayun_zhi='子', liunian_gan='庚', liunian_zhi='辰',
            age=20, liunian_interaction=[{'type': kind, 'target': '午'}])
        assert result['liunian_trigger'] is False, (kind, result)


def test_engine_passes_liunian_relations_to_yingqi():
    """引擎必须把 liunian_analysis 的关系结果传入综合应期，而非丢弃。"""
    from mangpai.engine import MangpaiEngine

    data = {
        'bazi': {'year': '甲子', 'month': '壬午', 'day': '丙寅', 'hour': '丁卯'},
        'input': {'year': 2000, 'gender': '男'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'liunian': [{'gz': '庚辰', 'year': 2026}],
    }
    result = MangpaiEngine(data).compute_all()
    assert result['yingqi_subj']['liunian_trigger'] is True, result['yingqi_subj']


def test_liunian_uses_the_dayun_of_its_own_year():
    """2025 属丙戌而非运行日所在的丁亥；未起运年不配对、不报负数运年。"""
    from mangpai.engine import MangpaiEngine

    data = {
        'bazi': {'year': '庚午', 'month': '戊子', 'day': '甲午', 'hour': '甲子'},
        'input': {'year': 1990, 'gender': '男'},
        'da_yun': {'start_age': 17, 'dayun': [
            {'gz': '甲申', 'start_age': 17, 'end_age': 27},
            {'gz': '丙戌', 'start_age': 27, 'end_age': 37},
            {'gz': '丁亥', 'start_age': 37, 'end_age': 47},
        ]},
        'liunian': [{'gz': '乙巳', 'year': 2025}, {'gz': '乙酉', 'year': 2005}],
    }
    result = MangpaiEngine(data, as_of='2026-06-01T00:00').compute_all()
    rows = {r['year']: r for r in result['liunian_analysis']['liunian']}
    assert any(i['type'] == '生' for i in rows[2025]['dayun_interaction'])
    assert not any(i['type'] == '冲' for i in rows[2025]['dayun_interaction'])
    assert not rows[2005].get('dayun_interaction')
    assert 2005 not in result['liunian_analysis']['dayun_phase']['per_year']


def test_as_of_uses_lichun_and_exact_jiaoyun():
    import pytest
    pytest.importorskip('sxtwl')
    from datetime import datetime
    from mangpai.engine import calc_mangpai_full
    from mangpai.objective.bazi_calc import year_gz

    as_of = '2027-01-15T12:00'
    result = calc_mangpai_full(
        1990, 8, 15, 12, 0, '男', 116.4, as_of=as_of)
    assert result['liunian_analysis']['liunian'][0]['gz'] == year_gz(
        2027, 1, 15, 12, 0)
    assert result['liunian_analysis']['liunian'][0]['year'] == 2026
    assert result['input']['as_of'] == as_of
    timeline = result['jiaoyun_analysis']['timeline']
    current = [t for t in timeline
               if t.get('jiaoyun_dt') and t['jiaoyun_dt'] <= datetime(2027, 1, 15, 12, 0)]
    assert current
    assert result['liunian_analysis']['dayun_phase']['gz'] == current[-1]['gz']
    assert not result['yingqi_subj']['conclusion'].startswith('真应期成立')
    assert not result['yingqi_subj']['conclusion'].startswith('应期成立')


def test_yingqi_needs_real_liunian_trigger_and_natal_lu():
    from mangpai.subjective.yingqi_subj import infer_comprehensive_yingqi
    from mangpai.objective.yingqi import detect_lu_yuanshen

    lu = detect_lu_yuanshen(list('庚癸戊甲'), list('戌未午寅'), '戊')
    wu_lu = [x for x in lu['lu_pillars'] if x['zhi'] == '午']
    assert wu_lu and all(not x['natal'] for x in wu_lu)
    assert all(x not in lu['yuanshen_via_lu'] for x in ('丁', '己'))
    result = infer_comprehensive_yingqi(
        '戊', list('庚癸戊甲'), list('戌未午寅'),
        dayun_gan='丁', dayun_zhi='亥', liunian_gan='壬', liunian_zhi='辰', age=40)
    assert result['daxian_yingqi']['pillar_lu_seen'] is False
    assert result['intersection'] is False
    assert not result['conclusion'].startswith('应期成立')

    no_liunian = infer_comprehensive_yingqi(
        '戊', list('庚癸戊甲'), list('戌未午寅'),
        dayun_gan='丁', dayun_zhi='亥', age=40)
    assert '待应期' in no_liunian['conclusion']
