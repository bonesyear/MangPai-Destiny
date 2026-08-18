"""llm_channel 三层校验器自检（离线，不调 LLM）。

覆盖：L0 schema / L1 basis 路径解析 / L2 枚举回对（财档越级、官命矛盾、
死亡红线）+ N1 数字校验接线。引擎路径零触网。
"""
from mangpai.subjective.llm_channel import (
    validate_reading, _l0_schema, _l1_basis, _l2_enum, _tier_rank,
)

_FEATURES = {
    'caiming': {'tier_static': '小康', 'tier': '富'},
    'guanming': {'is_guanming': False, 'summary': '无官'},
    'zuogong': {'work_types': ['化用'], 'work_level': 2},
}
_ENGINE = {'caiming': {'tier_static': '小康', 'tier': '富'},
           'guanming': {'is_guanming': False}}


def _good():
    return {d: {'conclusion': '一段断语', 'basis': ['zuogong.work_level'],
                'confidence': '中'} for d in ('性格', '事业', '财运', '婚姻', '应期')}


def test_l0_happy():
    assert _l0_schema(_good()) == []


def test_l0_missing_dim_and_bad_confidence():
    data = _good()
    del data['婚姻']
    data['财运']['confidence'] = '很高'
    v = _l0_schema(data)
    assert any('婚姻' in x['detail'] for x in v)
    assert any('confidence' in x['detail'] for x in v)


def test_l1_bad_path_and_empty_value():
    data = _good()
    data['事业']['basis'] = ['caiming.tier_static', 'nonexistent.key', 'guanming.nope']
    v = _l1_basis(data, _FEATURES)
    assert len(v) == 2
    assert any('nonexistent.key' in x['detail'] for x in v)


def test_l1_empty_basis_for_gap_is_ok():
    data = _good()
    data['应期'] = {'conclusion': '数据不足', 'basis': [], 'confidence': '低'}
    assert _l1_basis(data, _FEATURES) == []


def test_tier_rank():
    assert _tier_rank('巨富之家') == 4
    assert _tier_rank('富命') == 3
    assert _tier_rank('平常人家') == 1
    assert _tier_rank('没有档位词') == -1


def test_l2_tier_overclaim():
    data = _good()
    data['财运']['conclusion'] = '你是巨富之命'
    v = _l2_enum(data, _ENGINE)
    assert any('越引擎上限' in x['detail'] for x in v)
    # 引擎上限=富（全量轨），叙述「富」合法
    data['财运']['conclusion'] = '富命'
    assert not any('越引擎上限' in x['detail'] for x in _l2_enum(data, _ENGINE))


def test_l2_guanming_contradiction():
    data = _good()
    data['事业']['conclusion'] = '这是官命，能当官'
    v = _l2_enum(data, _ENGINE)
    assert any('官命=否' in x['detail'] for x in v)
    data['事业']['conclusion'] = '不是官命，仕途无缘'
    assert not any('官命=否' in x['detail'] for x in _l2_enum(data, _ENGINE))


def test_l2_death_redline():
    data = _good()
    data['应期']['conclusion'] = '六十八岁寿终'
    v = _l2_enum(data, _ENGINE)
    assert any('死亡红线' in x['detail'] for x in v)


def test_validate_reading_n1_wired():
    data = _good()
    data['财运']['conclusion'] = '1997年发大财'
    rep = validate_reading(data, _FEATURES, _ENGINE)
    assert not rep['ok']
    assert any(x['layer'] == 'N1' for x in rep['violations'])
