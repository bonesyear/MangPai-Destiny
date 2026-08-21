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
                'confidence': '中'}
            for d in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}


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


def test_l1_zhiye_primary_empty_allowed():
    # 迭代 5：zhiye.primary 空串=「无明确职业倾向」的判定本体，引此为出处合法
    feats = dict(_FEATURES, zhiye={'primary': '', 'primary_label': '未分类',
                                   'scores': {'teacher': 5}})
    data = _good()
    data['事业']['basis'] = ['zhiye.primary']
    assert _l1_basis(data, feats) == []
    # 白名单外的空引用仍违规
    data['事业']['basis'] = ['zhiye.primary', 'guanming.summary']
    feats['guanming'] = {'is_guanming': False, 'summary': ''}
    assert len(_l1_basis(data, feats)) == 1


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
    # 迭代 7：否定窗 ±2→±5 对齐财档（E6 官命矛盾 4 例全为误判：否定词出窗）
    for s in ('你不是当官的命，官杀不见，官命一票否决',
              '比劫夺财太凶，官命又被否决，求财多波折',
              '虽非正统官命但能掌实权，宜走武职',
              '无明确职业倾向，官命被反局否决'):
        data['事业']['conclusion'] = s
        assert not any('官命=否' in x['detail'] for x in _l2_enum(data, _ENGINE)), s
    # 窗口外仍拦真矛盾：无任何否定语境的正向断言
    data['事业']['conclusion'] = '此人是官命，能当官，仕途顺遂'
    assert any('官命=否' in x['detail'] for x in _l2_enum(data, _ENGINE))


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
    # 迭代 6：能力承诺/条件假设句中的档位词同样受上限约束
    assert '能力承诺句' in a and '条件假设句' in a
    assert _tier_anchor({'caiming': {}}) == ''


def test_zhiye_anchor_primary_and_candidates():
    # 迭代 5：主荐桶锚定——primary 非空时明令主荐桶 + 达阈候选桶
    from mangpai.subjective.llm_prompt import _zhiye_anchor
    feats = {'zhiye': {'primary': 'merchant', 'primary_label': '商人/经营',
                       'min_score_threshold': 6,
                       'scores': {'merchant': 11, 'teacher': 6, 'lawyer': 3}}}
    a = _zhiye_anchor(feats)
    assert '主荐桶=商人/经营' in a and '不得换成其他职业类别' in a
    assert '候选桶=教师/教育6分' in a and 'lawyer' not in a  # 低于阈值不入候选


def test_zhiye_anchor_no_tendency():
    # 迭代 5：primary 为空=引擎无倾向，必须如实说无倾向，禁止断言具体职业
    from mangpai.subjective.llm_prompt import _zhiye_anchor
    feats = {'zhiye': {'primary': '', 'primary_label': '未分类',
                       'min_score_threshold': 6,
                       'scores': {'accountant': 3, 'doctor': 2, 'lawyer': 0}}}
    a = _zhiye_anchor(feats)
    assert '无明确职业倾向' in a and '禁止断言任何具体职业' in a
    assert '会计/财务3分' in a  # 相对高分桶只作倾向性参考
    # 零分盘：不得给出任何职业方向
    feats['zhiye']['scores'] = {'merchant': 0}
    assert '不得给出任何职业方向' in _zhiye_anchor(feats)
    assert _zhiye_anchor({}) == '' and _zhiye_anchor({'zhiye': {}}) == ''


def test_yingqi_anchor_dayun_and_liunian():
    # 迭代 5：应期锚定——逐运 overall+正负信号、逐年 overall + 套话禁令
    from mangpai.subjective.llm_prompt import _yingqi_anchor
    feats = {
        'dayun_analysis': {'dayun': [
            {'gz': '庚申', 'order': 1, 'overall': '吉',
             'positive_signals': ['到禄位'], 'negative_signals': []},
            {'gz': '辛酉', 'order': 2, 'start_age': 11, 'end_age': 20,
             'overall': '吉凶参半', 'positive_signals': ['临官'],
             'negative_signals': ['穿命局']},
        ]},
        'liunian_analysis': {'liunian': [
            {'gz': '丙午', 'overall': '凶'}, {'gz': '丁未', 'overall': '平'}]},
    }
    a = _yingqi_anchor(feats)
    assert '庚申运[第1步]=吉' in a
    assert '辛酉运[11-20岁]=吉凶参半（吉:临官；凶:穿命局）' in a
    assert '丙午=凶；丁未=平' in a
    assert '禁止脱离此表' in a and '晚景渐佳' in a
    assert _yingqi_anchor({}) == ''
    assert _yingqi_anchor({'dayun_analysis': {}}) == ''


def test_user_prompt_includes_iter5_anchors():
    from mangpai.subjective.llm_prompt import build_user_prompt
    feats = {'caiming': {'tier_static': '小康', 'tier': '小康'},
             'zhiye': {'primary': '', 'primary_label': '未分类',
                       'scores': {'teacher': 5}},
             'dayun_analysis': {'dayun': [{'gz': '甲子', 'order': 1,
                                           'overall': '吉'}]}}
    p = build_user_prompt('{}', '甲子 乙丑 丙寅 丁卯', features=feats)
    assert '【本案职业锚定】' in p and '无明确职业倾向' in p
    assert '【本案应期锚定】' in p and '甲子运' in p


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


def test_tier_rank_iter6_exemptions():
    # 迭代 6（U3 假阳 9 例口径修）：
    # ②泛指动词「致富」不计
    assert _tier_rank('主经营致富，档次小康') == 2
    # ④修饰档归位：「小富」=小康级
    assert _tier_rank('可小富但难大富') == 2
    # ④「小康偏下」降半档归位（仍高于贫，边界例不豁免）
    assert _tier_rank('难成巨富，只能小康偏下') == 1
    # ⑤愿望条件句「想…得靠…」不计
    assert _tier_rank('求稳则小康可期，想大富得靠大运流年引动') == 2
    # ①让步+封顶：封顶标记前的档位词不计
    assert _tier_rank('虽功量有中富中贵之说，但财命封顶贫') == 0
    assert _tier_rank('虽做功层次高有大富之象，但财星反局被封顶') == -1
    assert _tier_rank('财命小康，主过河拆桥富格……财命上限小康') == 2
    # ①封顶后的越限仍拦
    assert _tier_rank('封顶小康，若运程配合能成巨富') == 4
    # ⑥富格/富档=引擎术语复合词，不计（E6 复测新发同族假阳）
    assert _tier_rank('功量富档虽高，但财命只小康') == 2
    assert _tier_rank('看似过河拆桥的富格，财命定格为贫') == 0
    # ①定档/定格同为封顶标记
    assert _tier_rank('虽功量可至大富，然财命定档小康') == 2
    # 能力承诺式仍拦（E6 新发真越限同型）
    assert _tier_rank('财命小康，踏实经营可达中富') == 3
    # ⑦（迭代 7，E7 复测新发让步同族假阳）：「虽」让步窗 + 归位语标记
    assert _tier_rank('财命属贫，虽有小富之象，但功神比劫制财反主破财') == 0
    assert _tier_rank('小康之命，虽有大富之量级但被下浮，不可贪求暴富') == 2
    assert _tier_rank('功量层级中富中贵，但财命档就是小康，别指望暴富') == 2
    # ⑦后真越限仍拦（无让步无归位的能力承诺）
    assert _tier_rank('财命富，财统官杀制杀得财，能积巨富') == 4


def test_tier_rank_iter6_quote_exemption():
    # ③引擎原文引用豁免：命中处落在引擎 caiming 原文子串内不计
    corpus = '"details": ["宾官被制尽（净制），过河拆桥富格——制官得财"]'
    assert _tier_rank('你财命小康，主过河拆桥富格，经营取财', corpus) == 2
    # 巨富档不适用引用豁免（防引擎旁注掩护真越限）
    corpus2 = '"details": ["制尽则能成巨富"]'
    assert _tier_rank('经营得法能成巨富', corpus2) == 4
    # ⑥后「富格」恒豁免（引擎术语复合词），无需 corpus
    assert _tier_rank('主过河拆桥富格') == -1
    assert _tier_rank('账面富贵、过手之财') == -1  # 富贵=泛指
    assert _tier_rank('不可奢求大富') == -1       # 否定窗 5（不字距 5）


def test_l2_tier_overclaim_iter6_kept():
    # 迭代 6：真越限 5 例句式仍拦（能力承诺/假设外壳/条件能力）
    eng_poor = {'caiming': {'tier_static': '贫', 'tier': '贫'}}
    eng_rich = {'caiming': {'tier_static': '富', 'tier': '富'}}
    data = _good()
    data['财运']['conclusion'] = '禄神当财，财命属贫，但勤劳可小康，大财难求'
    assert any('越引擎上限' in x['detail'] for x in _l2_enum(data, eng_poor))
    data['财运']['conclusion'] = '一旦库开，富可敌国——大运戌冲开辰库，便是大发之机'
    eng_xk = {'caiming': {'tier_static': '小康', 'tier': '小康'}}
    assert any('越引擎上限' in x['detail'] for x in _l2_enum(data, eng_xk))
    data['财运']['conclusion'] = '你属富命，宜谨慎经营，可成巨富'
    assert any('越引擎上限' in x['detail'] for x in _l2_enum(data, eng_rich))


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


# ── N1 七维批：迁移/相貌进叙述 ─────────────────────────────


def test_l0_requires_seven_dims():
    data = _good()
    del data['迁移']
    del data['相貌']
    v = _l0_schema(data)
    assert any('迁移' in x['detail'] for x in v)
    assert any('相貌' in x['detail'] for x in v)


def test_l2_qianyi_redline():
    # 迁移维绝对禁「出国/移民/海外/国外/外国」（对齐引擎措辞上限「迁移/远行」）
    data = _good()
    for s in ('你命中有出国之象', '宜移民海外发展', '中年定居国外',
              '配偶是外国人', '远行海外方吉'):
        data['迁移']['conclusion'] = s
        v = _l2_enum(data, _ENGINE)
        assert any('迁移' in x['detail'] for x in v), s
    # 措辞上限内放行；且只约束迁移维（其他维不拦——如婚姻维提及迁居地）
    data['迁移']['conclusion'] = '命局多迁移，中年后有远行应期'
    assert not any('迁移' in x['detail'] for x in _l2_enum(data, _ENGINE))


def test_l2_xiangmao_redline():
    # 相貌维禁「漂亮/美/丑/帅」结论词（marker 层无档位）
    data = _good()
    for s in ('面容漂亮', '五官俊美', '相貌丑陋', '人长得很帅'):
        data['相貌']['conclusion'] = s
        v = _l2_enum(data, _ENGINE)
        assert any('相貌' in x['detail'] for x in v), s
    # 排除窗放行：美元（货币）/丑时（时辰）/干支（丁丑）非相貌结论词
    for s in ('忌佩戴美元饰品', '丑时生人眼象清', '丁丑年眼象有损'):
        data['相貌']['conclusion'] = s
        v = _l2_enum(data, _ENGINE)
        assert not any('相貌' in x['detail'] for x in v), s


def test_qianyi_anchor():
    # N1：有信号盘列 marker+应期窗+禁令；无信号盘明令不得断言迁移
    from mangpai.subjective.llm_prompt import _qianyi_anchor
    feats = {'qianyi': {
        'qianyi_yuanju': {'beijing_lixiang': True, 'anju': False,
                          'ma_lin_nianshi': {'hit': True, 'positions': ['时']},
                          'markers': ['月日冲：背井离乡之象'], 'desc': 'x'},
        'qianyi_yingqi': {'move_windows': [
            {'dayun': '戊午', 'liunian': '甲午', 'mechanism': '马逢冲',
             'pillar': '时', 'confidence': '中', 'basis': 'b', 'note': ''}],
            'stay_windows': [], 'desc': ''},
        'summary': 's'}}
    a = _qianyi_anchor(feats)
    assert '【本案迁移锚定】' in a and '月日冲：背井离乡之象' in a
    assert '马逢冲' in a and '出境' in a  # 禁令提示（N2 r3 起锚定改类别级措辞，枚举在 SCHEMA）
    assert 'confidence 锁「低」' in a     # 应期窗或然 → 锁低
    empty = {'qianyi': {
        'qianyi_yuanju': {'beijing_lixiang': False, 'anju': True,
                          'ma_lin_nianshi': {'hit': False, 'positions': []},
                          'markers': [], 'desc': ''},
        'qianyi_yingqi': {'move_windows': [], 'stay_windows': [], 'desc': ''},
        'summary': ''}}
    a2 = _qianyi_anchor(empty)
    assert '无迁移信号' in a2 and '不得断言迁移' in a2
    assert _qianyi_anchor({}) == ''


def test_xiangmao_anchor():
    # N1：命中线列 marker 描述+禁词令；未命中明令不得给相貌评价
    from mangpai.subjective.llm_prompt import _xiangmao_anchor
    feats = {'xiangmao': {
        'xiuqi': {'hit': True, 'tou_gan': ['丁'], 'desc': '秀气透干（丁透），秀气主文章才华'},
        'jinshui': {'hit': False, 'blocked_by': ['非辛日主'], 'desc': ''},
        'muhuo': {'hit': False, 'fire': [], 'desc': ''},
        'yanxiang': {'bing': True, 'ding': False, 'gui': False,
                     'eye_full': False, 'desc': '丙=眼框/大眼之象'},
        'meili': {'hit': False, 'jiyi_only': False, 'desc': ''},
        'shencai': {'hit': False, 'markers': [], 'desc': ''},
        'summary': 's'}}
    a = _xiangmao_anchor(feats)
    assert '【本案相貌锚定】' in a and '秀气透干' in a and '眼框' in a
    assert '漂亮' in a  # 禁词提示
    empty = {'xiangmao': {
        'xiuqi': {'hit': False, 'tou_gan': [], 'desc': ''},
        'jinshui': {'hit': False, 'blocked_by': [], 'desc': ''},
        'muhuo': {'hit': False, 'fire': [], 'desc': ''},
        'yanxiang': {'bing': False, 'ding': False, 'gui': False,
                     'eye_full': False, 'desc': ''},
        'meili': {'hit': False, 'jiyi_only': False, 'desc': ''},
        'shencai': {'hit': False, 'markers': [], 'desc': ''},
        'summary': ''}}
    a2 = _xiangmao_anchor(empty)
    assert '无显著相貌特征' in a2 and '不得给' in a2
    assert _xiangmao_anchor({}) == ''


def test_zhiye_anchor_unemployed_must_state():
    # F-V3-1 搭车（zhenbao-23a 族）：unemployed/laborer 是引擎判定非无倾向，
    # 必须如实直述，不得改述为「无明确职业倾向」或另给安稳就业建议
    from mangpai.subjective.llm_prompt import _zhiye_anchor
    feats = {'zhiye': {'primary': 'unemployed', 'primary_label': '无业',
                       'min_score_threshold': 6,
                       'scores': {'unemployed': 9, 'laborer': 2}}}
    a = _zhiye_anchor(feats)
    assert '主荐桶=无业' in a and '如实直述' in a
    assert '无明确职业倾向' in a  # 禁令语境中出现（不得改述为…）
    # 普通桶不加该行
    feats['zhiye']['primary'] = 'merchant'
    feats['zhiye']['primary_label'] = '商人/经营'
    assert '如实直述' not in _zhiye_anchor(feats)


def test_user_prompt_includes_n1_anchors():
    from mangpai.subjective.llm_prompt import build_user_prompt
    feats = {'qianyi': {'qianyi_yuanju': {'markers': ['月日冲'], 'desc': ''},
                        'qianyi_yingqi': {'move_windows': [], 'stay_windows': []},
                        'summary': ''},
             'xiangmao': {'xiuqi': {'hit': False, 'desc': ''}, 'summary': ''}}
    p = build_user_prompt('{}', '甲子 乙丑 丙寅 丁卯', features=feats)
    assert '【本案迁移锚定】' in p and '【本案相貌锚定】' in p
    assert '输出七维 JSON' in p


def test_tier_rank_n2_guwei_yufu():
    # N2 迭代修（r1 yx-酒店假阳）：归位语「小康之富」=档词+之富，尾字富按前缀档计
    assert _tier_rank('你是小康之命，行运得当能积小康之富，莫想一夜暴富') == 2
    assert _tier_rank('财命贫，辛苦求财，也就平之富') == 1
    # 只降不升：前缀档仍高于引擎时照拦
    assert _tier_rank('财命贫，实际小康之富') == 2
    # 无档词前缀的「之富」不归位（真越限仍拦）
    assert _tier_rank('可积巨富之资') == 4


def test_xiangmao_anchor_n2_sanitize():
    # N2 迭代修（r1 相貌维 38 例违规主根因）：引擎秀气线原文含「漂亮」
    # （xiangmao.py:111 性别分流语，引擎侧本批冻结），锚定行注入前改写到红线内
    from mangpai.subjective.llm_prompt import _xiangmao_anchor
    feats = {'xiangmao': {
        'xiuqi': {'hit': True, 'tou_gan': ['甲'],
                  'desc': '秀气透干（甲透），女看秀气漂亮倾向、男看文章才华'},
        'jinshui': {'hit': False, 'blocked_by': [], 'desc': ''},
        'muhuo': {'hit': False, 'fire': [], 'desc': ''},
        'yanxiang': {'bing': False, 'ding': False, 'gui': False,
                     'eye_full': False, 'desc': ''},
        'meili': {'hit': False, 'jiyi_only': False, 'desc': ''},
        'shencai': {'hit': False, 'markers': [], 'desc': ''},
        'summary': 's'}}
    a = _xiangmao_anchor(feats)
    assert '女看秀气倾向' in a and '秀气漂亮' not in a
    # 禁令不再含可照抄的「不评美丑」口号式表述（r1 次根因：模型复述禁令）
    assert '只述象不评美丑' not in a


def test_qianyi_anchor_n2_empty_basis():
    # N2 迭代修（r1 迁移维 L1 6 例：无信号例引空数组键）：锚定明令 basis 留空
    from mangpai.subjective.llm_prompt import _qianyi_anchor
    empty = {'qianyi': {
        'qianyi_yuanju': {'markers': [], 'desc': ''},
        'qianyi_yingqi': {'move_windows': [], 'stay_windows': [], 'desc': ''},
        'summary': ''}}
    a = _qianyi_anchor(empty)
    assert 'basis 必须给空数组' in a and '禁止引用' in a


def test_tier_rank_n2_dafudagui():
    # N2 r2 迭代修（b67-初中假阳）：「大富大贵」成语泛指同富贵族，不计
    assert _tier_rank('财命小康，稳扎稳打，大富大贵需靠运势添翼') == 2
    assert _tier_rank('小康之命，莫指望大富大贵') == 2
    # 拆开单用仍拦
    assert _tier_rank('踏实经营可达大富') == 3


def test_anchors_n2_r3_meta_ban():
    # N2 r3 迭代修（r2 残留 4 例=元复述族：模型把禁令写进正文）：
    # 锚定行明令「不要声明或解释你在遵守禁令」；无 marker 盘只许写一句
    from mangpai.subjective.llm_prompt import _qianyi_anchor, _xiangmao_anchor
    qy_empty = {'qianyi': {
        'qianyi_yuanju': {'markers': [], 'desc': ''},
        'qianyi_yingqi': {'move_windows': [], 'stay_windows': [], 'desc': ''},
        'summary': ''}}
    assert '不要声明你在遵守禁令' in _qianyi_anchor(qy_empty)
    xm_empty = {'xiangmao': {
        'xiuqi': {'hit': False, 'desc': ''}, 'jinshui': {'hit': False, 'desc': ''},
        'muhuo': {'hit': False, 'desc': ''},
        'yanxiang': {'bing': False, 'ding': False, 'gui': False,
                     'eye_full': False, 'desc': ''},
        'meili': {'hit': False, 'desc': ''}, 'shencai': {'hit': False, 'desc': ''},
        'summary': ''}}
    a = _xiangmao_anchor(xm_empty)
    assert '只写「无显著相貌特征」一句' in a and '不声明禁令' in a


def test_tier_rank_n2_r3_exemptions():
    # N2 r3 复测假阳族（⑥⑦⑧同族变体）：
    # ⑧c「富足」泛指形容词
    assert _tier_rank('勤劳可至小康富足，不可奢望巨富') == 2
    assert _tier_rank('命定小康，安稳富足') == 2
    # ⑧d 告诫式暴富专属宽窗（别/莫距命中 6 字，一般 ±5 窗差一字）
    assert _tier_rank('撑死温饱有余，别想着投机暴富，踏实做工薪') == -1
    assert _tier_rank('财命看贫，别指望一夜暴富，守好本分') == 0
    assert _tier_rank('财命小康，别指望大富暴富') == 2
    # ⑧d 无否定语境的暴富仍拦
    assert _tier_rank('运气好就能暴富') == 3
    # ⑧e「平平」叠词口语非档位断言
    assert _tier_rank('财命平平，属贫命，量级有限') == 0
    # 单个「平」作档位词仍计
    assert _tier_rank('财命平，小康无望') == 1


def test_l2_guan_daoshi_exemption():
    # N2 r3 yx-富钢材生意发财假阳：「倒是官带财帽」让步/术语族放行
    from mangpai.subjective.llm_channel import _l2_enum
    eng = {'guanming': {'is_guanming': False},
           'caiming': {'tier_static': '富', 'tier': '富'}}
    data = {d: {'conclusion': '', 'basis': [], 'confidence': '中'}
            for d in ('性格', '财运', '婚姻', '应期', '迁移', '相貌')}
    data['事业'] = {'conclusion': '虽是富格，但制官不尽，非官命，倒是官带财帽，宜管钱管账',
                    'basis': [], 'confidence': '中'}
    assert _l2_enum(data, eng) == []
    # 无让步的真正向断言仍拦
    data['事业']['conclusion'] = '你是官命，能掌大权'
    v = _l2_enum(data, eng)
    assert any('官命' in x['detail'] for x in v)
