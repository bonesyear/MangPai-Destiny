"""D3 补供哨兵（2026-08-19）：dayun_analysis 死 selector 修复。

断裂点：LLM 批跑/评估路径 bazi_data 仅 bazi+gender+year（无 da_yun 键），
engine 不产出 dayun_analysis → selector 声明静默落空（T3 §A.1：281/281 缺失，
LLM 全程零大运表）。修复=build_payload 层合成补供，engine compute_all 零改动。

红线锁定：compute_all 对无 da_yun 输入仍不产出 dayun_analysis（判定零变化）。
"""
from mangpai.engine import MangpaiEngine
from mangpai.subjective import build_payload, _resolve, _MISSING

# 阎锡山造（calib zhenbao-12）：癸未 辛酉 乙酉 丁丑，男。
# 癸=阴干，阴男逆排，月柱辛酉 → 首运庚申。
_BAZI_DATA = {
    'bazi': {'year': '癸未', 'month': '辛酉', 'day': '乙酉', 'hour': '丁丑'},
    'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
    'input': {'gender': '男', 'year': 1943},
}


def _res():
    return MangpaiEngine(dict(_BAZI_DATA, bazi=dict(_BAZI_DATA['bazi']),
                              input=dict(_BAZI_DATA['input']))).compute_all()


def test_engine_still_omits_dayun_without_input():
    """红线：compute_all 对无 da_yun 输入不产出 dayun_analysis（零变化）。"""
    assert 'dayun_analysis' not in _res()


def test_payload_synthesizes_dayun():
    payload = build_payload(_res())
    da = payload['dayun_analysis']
    assert da['direction'] == '逆'  # 阴男逆排
    assert len(da['dayun']) == 8
    assert da['dayun'][0]['gz'] == '庚申'
    assert da['dayun'][1]['gz'] == '己未'
    assert da['age_note']


def test_synthesized_shape_llm_referenceable():
    """每运：干支/十神/吉凶信号/事件锚；无年龄锚；L1 按整组引用可溯。"""
    da = build_payload(_res())['dayun_analysis']
    for d in da['dayun']:
        assert set(d) >= {'gz', 'order', 'gan_shishen', 'overall',
                          'positive_signals', 'negative_signals'}
        assert d['overall'] in ('吉', '凶', '吉凶参半', '平')
        assert 'start_age' not in d and 'end_age' not in d  # 缺精确时刻，诚实缺省
    val = _resolve({'dayun_analysis': da}, 'dayun_analysis.dayun')
    assert val is not _MISSING and val  # L1 校验路径可解析非空


def test_real_dayun_trimmed_but_ages_kept():
    """有 da_yun 输入时走 engine 真实产出：统一天投影形状，起止岁保留。"""
    bazi_data = dict(_BAZI_DATA, bazi=dict(_BAZI_DATA['bazi']),
                     input=dict(_BAZI_DATA['input']))
    bazi_data['da_yun'] = {'start_age': 3, 'dayun': [
        {'gz': '庚申', 'start_age': 3, 'end_age': 13},
        {'gz': '己未', 'start_age': 13, 'end_age': 23},
    ]}
    res = MangpaiEngine(bazi_data).compute_all()
    da = build_payload(res)['dayun_analysis']
    assert da['dayun'][0]['start_age'] == 3
    assert 'tiyong_import' not in da['dayun'][0]  # 检测中间件已剥
    assert 'gan_relations' not in da['dayun'][0]


def test_no_gender_no_synthesis():
    """性别缺失无法判向 → 不合成（不编造方向）。"""
    bazi_data = dict(_BAZI_DATA, bazi=dict(_BAZI_DATA['bazi']),
                     input={'year': 1943})
    payload = build_payload(MangpaiEngine(bazi_data).compute_all())
    assert 'dayun_analysis' not in payload
