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


def test_l1_array_index_forbidden():
    data = _good()
    # 下标两种写法（方括号/数字段）一律违规，即使数字段在界内可解析
    data['性格']['basis'] = ['xiangfa_ops.juxiang[7]', 'zuogong.work_types.0']
    v = _l1_basis(data, _FEATURES)
    assert len(v) == 2
    assert all('禁止带下标' in x['detail'] for x in v)


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
    # 后置否定窗（扩到后 2 字符）：「官命否决/无缘」不误报
    data['事业']['conclusion'] = '官命否决，贵格难成'
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


def test_n1_daxian_boundary_whitelisted():
    # 大限宫位边界 18/35/55 入年龄白名单（特征 JSON 内含，非编造）
    data = _good()
    data['应期']['conclusion'] = '55岁前后是一道坎'
    rep = validate_reading(data, _FEATURES, _ENGINE)
    assert not any(x['layer'] == 'N1' for x in rep['violations'])
    # 白名单外年龄仍拦截
    data['应期']['conclusion'] = '42岁有一劫'
    rep = validate_reading(data, _FEATURES, _ENGINE)
    assert any(x['layer'] == 'N1' for x in rep['violations'])


def test_key_manifest_verbatim():
    # 迭代 2：键清单与特征 JSON 实际结构逐字一致；数组标 []
    # 迭代 3：数组行内标「禁下标」，空值键行内标「(空)」
    # 迭代 4：改完整点路径格式（每行一条可引路径，治拍平/归属错位）
    from mangpai.subjective.llm_prompt import _key_manifest
    feats = {'caiming': {'tier_static': '小康', 'caifu_view': {'primary': '财星当财'}},
             'xiangfa_ops': {'juxiang': [{'label': '寒湿'}], 'huanxiang': []},
             'nayin': ['路旁土'], 'zhiye': {'primary': '', 'summary': None}}
    m = _key_manifest(feats)
    lines = m.split('\n')
    assert 'caiming.tier_static' in lines
    assert 'caiming.caifu_view' in lines and 'caiming.caifu_view.primary' in lines
    assert 'xiangfa_ops.juxiang[]禁下标' in lines
    assert 'xiangfa_ops.huanxiang[](空,禁引用)' in lines
    assert 'nayin[]禁下标' in lines
    assert 'zhiye.primary(空)' in lines and 'zhiye.summary(空)' in lines
    # 每行路径的首段必须是真实顶层键；子键逐字来自特征 JSON
    for line in lines:
        top = line.split('.', 1)[0].split('[]')[0].split('(')[0]
        assert top in feats


def test_tier_anchor_ceiling():
    # 迭代 2：锚定行取两轨较高档；无档位信息时不生成
    from mangpai.subjective.llm_prompt import _tier_anchor
    a = _tier_anchor({'caiming': {'tier_static': '贫', 'tier': '小康'}})
    assert '不得超过「小康」' in a and 'tier_static=贫' in a
    assert _tier_anchor({'caiming': {}}) == ''


def test_user_prompt_includes_manifest_and_anchor():
    from mangpai.subjective.llm_prompt import build_user_prompt
    p = build_user_prompt('{"caiming":{}}', '甲子 乙丑 丙寅 丁卯',
                          features={'caiming': {'tier_static': '小康', 'tier': '小康'}})
    assert '特征 JSON 键清单' in p and 'caiming.tier_static' in p
    assert '不得超过「小康」' in p
    # 不给 features 时保持旧形态（无清单段）
    p2 = build_user_prompt('{}', '甲子 乙丑 丙寅 丁卯')
    assert '特征 JSON 键清单' not in p2


def test_tier_rank_negation_window():
    # 迭代 2 复测：否定式档位词（锚定生效后的合规表述）不计越限
    assert _tier_rank('难大富，注意防破财') == -1
    assert _tier_rank('封顶富，非巨富') == 3
    assert _tier_rank('财命档止于小康，不主巨富') == 2
    assert _tier_rank('大富难求') == -1
    assert _tier_rank('财富量级有限') == -1  # 财富=泛指
    assert _tier_rank('能成巨富之资') == 4   # 真越限仍拦
    assert _tier_rank('经营取财可积富') == 3


# remap 测试用特征结构（仿 v5 残余 10 条的真实 payload 形态）
_REMAP_FEATURES = {
    'xiangfa': {'gan_xiang': {'甲': '木'}},
    'xiangfa_ops': {'juxiang': [{'label': '寒湿'}], 'all_findings': ['专旺']},
    'hunyin': {'quality': {'quality': '差', 'gong_attacked': ['冲']},
               'duohun': {'is_duohun': True, 'factors': ['婚姻宫被冲']},
               'summary': '婚姻差'},
    'caiming': {'caifu_view': {'caixing_path': {'has_yuanshen': True}}},
    'zuogong': {'work_level': 2},
}


def _remapped_ok(path):
    data = _good()
    data['性格']['basis'] = [path]
    remapped = []
    v = _l1_basis(data, _REMAP_FEATURES, remapped)
    return v, remapped


def test_l1_remap_unique_expansion():
    # 规则 A 缺 _ops 前缀
    v, r = _remapped_ok('xiangfa.juxiang')
    assert v == [] and r[0]['detail'].endswith('→ xiangfa_ops.juxiang')
    v, r = _remapped_ok('xiangfa.all_findings')
    assert v == [] and r[0]['detail'].endswith('→ xiangfa_ops.all_findings')
    # 规则 B 层级拍平（唯一子节点）
    v, r = _remapped_ok('hunyin.gong_attacked')
    assert v == [] and r[0]['detail'].endswith('→ hunyin.quality.gong_attacked')
    v, r = _remapped_ok('caiming.caixing_path.has_yuanshen')
    assert v == [] and r[0]['detail'].endswith('→ caiming.caifu_view.caixing_path.has_yuanshen')
    # 规则 C 多包一层
    v, r = _remapped_ok('hunyin.quality.summary')
    assert v == [] and r[0]['detail'].endswith('→ hunyin.summary')
    # 规则 D 叶键别名 signals→factors
    v, r = _remapped_ok('hunyin.duohun.signals')
    assert v == [] and r[0]['detail'].endswith('→ hunyin.duohun.factors')


def test_l1_remap_ambiguous_stays_violation():
    # 歧义不 remap：hunyin.signals 可展开到 quality/duohun 多处 → 仍违规
    feats = {'hunyin': {'a': {'signals': ['x']}, 'b': {'signals': ['y']}},
             'zuogong': {'work_level': 2}}
    data = _good()
    data['性格']['basis'] = ['hunyin.signals', 'hunyin.nope']
    remapped = []
    v = _l1_basis(data, feats, remapped)
    assert len(v) == 2 and remapped == []


def test_l1_remap_empty_target_stays_violation():
    # remap 只治键名写错；映射到的真键为空仍记违规
    feats = {'xiangfa_ops': {'juxiang': []}, 'zuogong': {'work_level': 2}}
    data = _good()
    data['性格']['basis'] = ['xiangfa.juxiang']
    remapped = []
    v = _l1_basis(data, feats, remapped)
    assert len(v) == 1 and remapped == []


def test_validate_reading_reports_remapped():
    data = _good()
    data['性格']['basis'] = ['xiangfa.juxiang']
    rep = validate_reading(data, _REMAP_FEATURES, _ENGINE)
    assert rep['ok']  # remap 转正，不计违规
    assert rep['remapped'][0]['detail'].endswith('→ xiangfa_ops.juxiang')
