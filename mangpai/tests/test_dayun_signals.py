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
    """换运年按虚岁定位：2000 生、2010 年虚岁 11，应进入第二步大运。"""
    from mangpai.engine import MangpaiEngine

    class FakeDateTime:
        @classmethod
        def now(cls):
            return type('Now', (), {'year': 2010})()

    monkeypatch.setattr('mangpai.engine.datetime', FakeDateTime)
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
    result = MangpaiEngine(data).compute_all()
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
