# -*- coding: utf-8 -*-
"""H-fix-5 compute_all 五阶段拆分哨兵。

锁两件事：
1. 结构（先红后绿）：拆分出的阶段子函数必须存在于 MangpaiEngine
   （_compute_objective_base/_compute_zuogong_and_derivatives/
   _compute_objective_extended/_compute_yunshi/_compute_subjective_domain；
   summary 装配沿用既有 _build_summary）。
2. 行为（改动前后皆绿）：各阶段写回 result 的键集/键序、条件分支
   （dy_list 空不出 dayun_analysis、无出生年不出 jiaoyun_analysis、
   无外部流年时自动流年注入并置 _auto_liunian_injected）、summary 装配，
   以及「手工逐阶段调用 == compute_all()」编排一致性——钉值全部取自
   拆分前 compute_all 实测输出（等价性捕获同批，/tmp/hfix5_ca_pre.json），
   不断言任何新规则。

边界说明（与 backlog H11 对照表的偏差）：H11 的 ① 覆盖 muku..gongshen，
但实际代码中 zuogong/zeishen_bushen/gongliang（H11 ②）位于 tiyong 与
muku 之间（zuogong 是 gongliang/zhengfan/yunfan 全链上游，须先算）。
为保持调用/回写顺序逐字等价，① 拆为 _compute_objective_base（..tiyong）
与 _compute_objective_extended（muku..di_zhi_relations）两段，夹住 ②。
"""
import pytest

from mangpai.engine import MangpaiEngine

_PHASE_FUNCS = (
    '_compute_objective_base',
    '_compute_zuogong_and_derivatives',
    '_compute_objective_extended',
    '_compute_yunshi',
    '_compute_subjective_domain',
)

PAN_LI = {'year': '戊辰', 'month': '己未', 'day': '庚午', 'hour': '丁亥'}
PAN_QL = {'year': '辛卯', 'month': '丁酉', 'day': '庚午', 'hour': '丙子'}
DY = [{'gz': '庚申', 'start_age': 8, 'end_age': 18},
      {'gz': '辛酉', 'start_age': 18, 'end_age': 28}]
LN = [{'gz': '甲子', 'year': 1984}]


def _bazi(pan, **extra):
    bd = {'bazi': dict(pan), 'shishen': {}, 'kong_wang': {},
          'di_zhi_relations': {}}
    bd.update(extra)
    return bd


LI_FULL = _bazi(PAN_LI, input={'year': 1988, 'gender': '男'},
                dayun=list(DY), liunian=list(LN))
LI_DAYUN = _bazi(PAN_LI, input={'year': 1988, 'gender': '男'}, dayun=list(DY))
LI_AUTO = _bazi(PAN_LI, input={'year': 1988, 'gender': '男'})
LI_NOINPUT = _bazi(PAN_LI)
QL_BARE = _bazi(PAN_QL)

# 拆分前实测钉值（/tmp/hfix5_ca_pre.json 同批捕获）
PIN_LI_SUMMARY = (
    '日主：庚午；做功类型：制用、化用、合用；做功层次：化用成局（Level 4）；'
    '做功效率：高；含暗合；正反局：正局（土旺成势，顺势）；'
    '十神歌诀：正官2(混杂)、正印2(混杂)、偏印2(混杂)、食神1(清纯)；'
    '体用：体0用0；劫煞在hour、寡宿在year、驿马在year、天乙贵人在month、'
    '文昌在hour；大运：共2步大运；吉凶参半2步；交运：大寒当日寅时'
)
PIN_QL_SUMMARY = (
    '日主：庚午；做功类型：制用、合用；做功层次：单层做功（Level 1）；'
    '做功效率：高；正反局：正局（金水成势，顺势）；'
    '十神歌诀：正财1(清纯)、正官2(混杂)、七杀1(清纯)、伤官1(清纯)、'
    '劫财2(混杂)；体用：体0用0；羊刃在month、灾煞在hour、桃花在year、'
    '驿马在hour'
)
KEYS_PHASE1 = ['bazi', 'input', 'canggan', 'chang_sheng', 'nayin',
               'nayin_work', 'shensha', 'binzhu', 'tiyong']
KEYS_PHASE2 = ['zuogong', 'gongliang']
KEYS_PHASE3 = ['muku', 'anhe', 'biqi', 'wood_type', 'soil', 'he_types',
               'virtual_solid', 'zhengfan', 'shenshu', 'xiangfa', 'gongshen',
               'kong_wang', 'di_zhi_relations']
KEYS_PHASE5 = ['relations', 'yunfan', 'direction', 'caiming', 'guanming',
               'hunyin', 'xueli', 'laoyu', 'zeishen_bushen', 'xiangfa_ops',
               'zhiye', 'gongmen_wuzhi', 'liuqin', 'zinv', 'qianyi',
               'xiangmao', 'zaihuo', 'yingqi_subj', 'narrative']
KEYS_FULL_48 = (KEYS_PHASE1 + KEYS_PHASE2 + KEYS_PHASE3
                + ['dayun_analysis', 'liunian_analysis', 'jiaoyun_analysis',
                   'shipaige'] + KEYS_PHASE5 + ['summary'])


def run_phases(eng):
    """手工逐阶段调用（与 compute_all 编排平行，供一致性对拍）。"""
    result = {}
    p = eng.pillars
    eng._compute_objective_base(result, p)
    zg_zb = eng._compute_zuogong_and_derivatives(result, p)
    eng._compute_objective_extended(result, p, zg_zb['zg'])
    ctx = eng._compute_yunshi(result, zg_zb['zg'])
    eng._compute_subjective_domain(result, p, zg_zb['zg'], zg_zb['zb_res'],
                                   ctx)
    result['summary'] = eng._build_summary(result)
    return result, zg_zb, ctx


def test_phase_functions_exist():
    for name in _PHASE_FUNCS:
        assert callable(getattr(MangpaiEngine, name, None)), (
            f'阶段子函数 {name} 不存在（拆分未落地？）')


def test_phase1_objective_base_keys_and_pins():
    eng = MangpaiEngine(LI_FULL)
    result = {}
    eng._compute_objective_base(result, eng.pillars)
    assert list(result.keys()) == KEYS_PHASE1
    # 钉值：拆分前实测（参数接线错误即红）
    assert [v['name'] for v in result['nayin']] == [
        '大林木', '天上火', '路旁土', '屋上土']
    assert result['canggan']['未'] == [('己', '本气'), ('乙', '中气'),
                                       ('丁', '余气')]
    assert result['tiyong']['ti_count'] == 0
    assert result['tiyong']['yong_count'] == 0


def test_phase2_zuogong_derivatives_returns_and_pins():
    eng = MangpaiEngine(LI_FULL)
    result = {}
    eng._compute_objective_base(result, eng.pillars)
    ret = eng._compute_zuogong_and_derivatives(result, eng.pillars)
    assert list(result.keys()) == KEYS_PHASE1 + KEYS_PHASE2
    assert set(ret.keys()) == {'zg', 'zb_res'}
    assert ret['zg'] is result['zuogong']  # 回写后重读，同一对象
    assert isinstance(ret['zb_res'], dict)
    assert ret['zg'].get('work_types') == ['制用', '化用', '合用']
    assert result['gongliang'].get('level') == 4


def test_phase3_objective_extended_key_order():
    eng = MangpaiEngine(LI_FULL)
    result = {}
    p = eng.pillars
    eng._compute_objective_base(result, p)
    zg_zb = eng._compute_zuogong_and_derivatives(result, p)
    eng._compute_objective_extended(result, p, zg_zb['zg'])
    assert (list(result.keys())
            == KEYS_PHASE1 + KEYS_PHASE2 + KEYS_PHASE3)
    assert result['zhengfan'].get('type') == 'zheng'


def test_phase4_yunshi_dy_list_conditional():
    # 注入 dayun → dayun_analysis 就位，ctx 透传 dy_list
    eng = MangpaiEngine(LI_DAYUN)
    result = {}
    p = eng.pillars
    eng._compute_objective_base(result, p)
    zg_zb = eng._compute_zuogong_and_derivatives(result, p)
    eng._compute_objective_extended(result, p, zg_zb['zg'])
    ctx = eng._compute_yunshi(result, zg_zb['zg'])
    assert 'dayun_analysis' in result
    assert result['dayun_analysis'].get('summary')
    assert ctx['dy_list'] == DY
    # 无外部流年但有出生年 → 自动流年已注入 → liunian_analysis 就位
    assert list(result.keys()) == (KEYS_PHASE1 + KEYS_PHASE2 + KEYS_PHASE3
                                   + ['dayun_analysis', 'liunian_analysis',
                                      'jiaoyun_analysis', 'shipaige'])
    # 无 dayun → dy_list 空 → 不出 dayun_analysis（条件键）
    eng2 = MangpaiEngine(LI_AUTO)
    result2 = {}
    p2 = eng2.pillars
    eng2._compute_objective_base(result2, p2)
    zg_zb2 = eng2._compute_zuogong_and_derivatives(result2, p2)
    eng2._compute_objective_extended(result2, p2, zg_zb2['zg'])
    ctx2 = eng2._compute_yunshi(result2, zg_zb2['zg'])
    assert 'dayun_analysis' not in result2
    assert ctx2['dy_list'] == []


def test_phase4_yunshi_jiaoyun_conditional():
    # 有出生年 → jiaoyun_analysis；无 input（无年）→ 缺省
    eng = MangpaiEngine(LI_AUTO)
    result = {}
    p = eng.pillars
    eng._compute_objective_base(result, p)
    zg_zb = eng._compute_zuogong_and_derivatives(result, p)
    eng._compute_objective_extended(result, p, zg_zb['zg'])
    eng._compute_yunshi(result, zg_zb['zg'])
    assert 'jiaoyun_analysis' in result

    eng2 = MangpaiEngine(LI_NOINPUT)
    result2 = {}
    p2 = eng2.pillars
    eng2._compute_objective_base(result2, p2)
    zg_zb2 = eng2._compute_zuogong_and_derivatives(result2, p2)
    eng2._compute_objective_extended(result2, p2, zg_zb2['zg'])
    eng2._compute_yunshi(result2, zg_zb2['zg'])
    assert 'jiaoyun_analysis' not in result2
    assert 'liunian_analysis' not in result2  # 无年 → 自动流年也不注入


def test_phase4_yunshi_auto_liunian_injected_flag():
    # 无外部流年 + 有出生年 → 自动构造三岁窗口并置 _auto_liunian_injected
    eng = MangpaiEngine(LI_AUTO)
    assert getattr(eng, '_auto_liunian_injected', False) is False
    result = {}
    p = eng.pillars
    eng._compute_objective_base(result, p)
    zg_zb = eng._compute_zuogong_and_derivatives(result, p)
    eng._compute_objective_extended(result, p, zg_zb['zg'])
    ctx = eng._compute_yunshi(result, zg_zb['zg'])
    assert eng._auto_liunian_injected is True
    assert ctx['liunian_data']  # 自动三岁窗口已注入
    assert 'liunian_analysis' in result
    # 外部流年注入 → 不置 flag（A1：显式运岁方入否决链）
    eng2 = MangpaiEngine(LI_FULL)
    result2 = {}
    p2 = eng2.pillars
    eng2._compute_objective_base(result2, p2)
    zg_zb2 = eng2._compute_zuogong_and_derivatives(result2, p2)
    eng2._compute_objective_extended(result2, p2, zg_zb2['zg'])
    ctx2 = eng2._compute_yunshi(result2, zg_zb2['zg'])
    assert getattr(eng2, '_auto_liunian_injected', False) is False
    assert ctx2['liunian_data'] == LN


def test_phase5_subjective_domain_key_order_and_relations():
    eng = MangpaiEngine(LI_FULL)
    result, _, _ = run_phases(eng)
    n_pre = len(KEYS_PHASE1 + KEYS_PHASE2 + KEYS_PHASE3) + 4  # +yunshi 4 键
    assert list(result.keys())[:n_pre] == (
        KEYS_PHASE1 + KEYS_PHASE2 + KEYS_PHASE3
        + ['dayun_analysis', 'liunian_analysis', 'jiaoyun_analysis',
           'shipaige'])
    assert list(result.keys())[n_pre:-1] == KEYS_PHASE5
    assert list(result.keys())[-1] == 'summary'
    assert set(result['relations'].keys()) == {
        'work_actions', 'tomb_works', 'sheng_yong_actions', 'zheng_he',
        'san_he_formed', 'day_he_type', 'day_changsheng', 'day_weak_zhis',
        'kong_wang_zhis', 'entombed_gan_pillars'}
    # laoyu/zeishen_bushen 在阶段⑤原位置回写（键序锁）
    assert result['zeishen_bushen'] is not None


@pytest.mark.parametrize('bazi_data,key_count,summary', [
    (LI_FULL, 48, PIN_LI_SUMMARY),
    (LI_DAYUN, 48, PIN_LI_SUMMARY),
    (QL_BARE, 45, PIN_QL_SUMMARY),
])
def test_orchestrator_matches_manual_phases(bazi_data, key_count, summary):
    """编排一致性：compute_all() == 手工逐阶段调用（键序 + 全值）。"""
    by_orchestrator = MangpaiEngine(bazi_data).compute_all()
    manual, _, _ = run_phases(MangpaiEngine(bazi_data))
    assert list(by_orchestrator.keys()) == list(manual.keys())
    assert by_orchestrator == manual
    assert len(by_orchestrator) == key_count
    assert by_orchestrator['summary'] == summary


def test_full_key_order_48():
    """全量供给（dayun+liunian 注入）下 48 键顺序锁定（H-fix-6 契约同口径）。"""
    res = MangpaiEngine(LI_FULL).compute_all()
    assert list(res.keys()) == KEYS_FULL_48
    assert len(res) == 48
