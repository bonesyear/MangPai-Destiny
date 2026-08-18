"""岁运反局 (yunfan) 测试 - 验证高级篇 3.3 岁运反局命例。

覆盖《盲派高级命理学》3.3 五个核心命例的反局类型检出：
  案例一(丙辰运穿卯晦巳→破坏功神)、案例三(辛卯运合申→冲变合)、
  案例四(壬子运合丑→冲变合/闭库)、案例八(甲申流年己巳运→天地合岁运联动)、
  案例九(癸未流年→丑未戌三刑搅局)。
判据为结构启发式（见模块 docstring），本测试锁定类型检出而非精确应事。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.yunfan import analyze_yunfan


def _dy_fan_types(r):
    return [f['fan_type'] for d in r['dayun_fan'] for f in d['fans']]

def _ln_fan_types(r):
    return [f['fan_type'] for l in r['liunian_fan'] for f in l['fans']]

def _liandong_types(r):
    return [x['fan_type'] for s in r['sui_yun_liandong'] for x in s['liandong']]


def test_dayun_case1_break_gongshen():
    """案例一：戊申甲寅辛卯癸巳，丙辰运——辰穿卯晦巳，破坏功神。

    （A14：忌神反客大运侧已移除——书锚机制辰生申要求 zuogong 判申为废神，
    本引擎判申为功神不可复现，原断言实靠丙干生戊偶合；判别集 4 例全假阳。
    流年侧引动忌神保留。）"""
    r = analyze_yunfan(['戊', '甲', '辛', '癸'], ['申', '寅', '卯', '巳'], '辛',
                       dayun_list=[{'gz': '丙辰'}])
    assert any('破坏功神' in t for t in _dy_fan_types(r))


def test_dayun_case3_chong_bian_he():
    """案例三：庚申己丑丙申乙未，辛卯运——卯合申，冲变合。"""
    r = analyze_yunfan(['庚', '己', '丙', '乙'], ['申', '丑', '申', '未'], '丙',
                       dayun_list=[{'gz': '辛卯'}])
    assert any('冲变合' in t for t in _dy_fan_types(r))


def test_dayun_case4_bi_ku():
    """案例四：癸卯乙丑辛未己丑，壬子运——子合丑，冲变合+合闭墓库。"""
    r = analyze_yunfan(['癸', '乙', '辛', '己'], ['卯', '丑', '未', '丑'], '辛',
                       dayun_list=[{'gz': '壬子'}])
    types = _dy_fan_types(r)
    assert any('冲变合' in t for t in types)
    assert any('合闭墓库' in t for t in types)


def test_dayun_sanxing_excludes_natal_complete():
    """原局自带寅巳申三刑时，运支不补全不应误报三刑（案例一原局寅巳申）。"""
    r = analyze_yunfan(['戊', '甲', '辛', '癸'], ['申', '寅', '卯', '巳'], '辛',
                       dayun_list=[{'gz': '丙辰'}])
    assert not any('伏吟三刑' in t for t in _dy_fan_types(r))


def test_liunian_case8_tiandi_he():
    """案例八：癸卯乙丑辛未己丑，己巳运甲申流年——天地合岁运联动(最凶)。"""
    r = analyze_yunfan(['癸', '乙', '辛', '己'], ['卯', '丑', '未', '丑'], '辛',
                       current_dayun={'gz': '己巳'},
                       liunian_list=[{'gz': '甲申'}])
    assert '岁运联动·天地合' in _liandong_types(r)
    # 天地合为极重
    for s in r['sui_yun_liandong']:
        for x in s['liandong']:
            if x['fan_type'] == '岁运联动·天地合':
                assert x['severity'] == '极重'


def test_liunian_case9_sanxing():
    """案例九：丙午辛丑戊戌戊午，癸未流年——丑未戌三刑搅局。"""
    r = analyze_yunfan(['丙', '辛', '戊', '戊'], ['午', '丑', '戌', '午'], '戊',
                       liunian_list=[{'gz': '癸未'}])
    assert any('伏吟三刑' in t for t in _ln_fan_types(r))


def test_yunfan_returns_structure():
    """输出契约：四键齐备 + 原局正反局基线。"""
    r = analyze_yunfan(['庚', '己', '丙', '乙'], ['申', '丑', '申', '未'], '丙',
                       dayun_list=[{'gz': '辛卯'}])
    for k in ('natal_zhengfan', 'dayun_fan', 'liunian_fan', 'sui_yun_liandong', 'summary'):
        assert k in r
    assert 'configuration' in r['natal_zhengfan']
    assert 'type' in r['natal_zhengfan']


def test_no_fan_when_peaceful():
    """平和运岁不误报反局：甲子运与庚申己丑丙申乙未无明显冲合功神。"""
    r = analyze_yunfan(['庚', '己', '丙', '乙'], ['申', '丑', '申', '未'], '丙',
                       dayun_list=[{'gz': '甲子'}])
    # 甲子运非源文反局运；不强制为空，但不应误报天地合/三刑联动
    assert r['sui_yun_liandong'] == []


# ---------------------------------------------------------------------------
# F8 书例哨兵：批4 yunfan 三 P0（先红后绿）
# ---------------------------------------------------------------------------

def test_f8_case5_fuyin_gan_kehuai_true():
    """案例五（乙己壬辛/巳丑辰丑）乙酉运：乙伏吟被辛克坏=坏辰墓——真阳不动。

    书锚 中级903/2853：「乙这里可以代表辰，乙透被原局中辛金克坏，等于坏了
    辰，所以此运大凶…坐牢。没收所有的财产。」（乙为主位辰墓之透，前提成立）"""
    r = analyze_yunfan(['乙', '己', '壬', '辛'], ['巳', '丑', '辰', '丑'], '壬',
                       dayun_list=[{'gz': '乙酉'}])
    assert any('伏吟三刑' in t for t in _dy_fan_types(r))


def test_f8_case5_bingxu_chong_kai_ku_exempt():
    """案例五同盘丙戌运：戌冲辰=冲开财库应期，豁免 T1——假阳修复。

    书锚 中级903/2853：「行戌运，冲开辰墓，发财数亿…发5年财，有5亿资产」。"""
    r = analyze_yunfan(['乙', '己', '壬', '辛'], ['巳', '丑', '辰', '丑'], '壬',
                       dayun_list=[{'gz': '丙戌'}])
    assert not any('破坏功神' in t for t in _dy_fan_types(r))


def test_f8_reg67_dingyou_no_fuyin_gan_fan():
    """reg67 资本运营（丁未癸丑丙子壬辰）丁酉运：丁伏吟被癸克，但丁所透之
    未墓在宾位（年支）非主位功神——不判 T3。假阳修复。

    书锚 理象学:7586-7594：「行酉运，亿万巨富」（修批C 更正，旧记 :7720 偏 126 行，R3）。"""
    r = analyze_yunfan(['丁', '癸', '丙', '壬'], ['未', '丑', '子', '辰'], '丙',
                       dayun_list=[{'gz': '丁酉'}])
    assert not any('伏吟三刑' in t for t in _dy_fan_types(r))


def test_f8_liandong_sanxing_requires_completion():
    """岁运联动·三刑补全闸：原局寅巳申已齐者，岁运不补全不触发（假阳修复）；
    原局缺一支岁运补全者仍触发（案例九真阳不动，gaoji:3799 癸未年入狱）。"""
    # 医师盘（壬寅丁未壬申乙巳）原局寅巳申已齐：癸亥年癸卯运不误报（审计假阳例）
    r = analyze_yunfan(['壬', '丁', '壬', '乙'], ['寅', '未', '申', '巳'], '壬',
                       liunian_list=[{'gz': '癸亥', 'year': 1983}],
                       current_dayun={'gz': '癸卯'})
    assert '岁运联动·三刑' not in _liandong_types(r)
    # 案例九（丙午辛丑戊戌戊午）癸未年未补全丑戌：仍触发
    r = analyze_yunfan(['丙', '辛', '戊', '戊'], ['午', '丑', '戌', '午'], '戊',
                       liunian_list=[{'gz': '癸未', 'year': 2003}],
                       current_dayun={'gz': '甲午'})
    assert '岁运联动·三刑' in _liandong_types(r)


def test_f8_true_yang_guards():
    """四个真阳锚不得误伤：
    巨富丑运丙子运入狱（yanjiu:5962，破刃+伏吟激刑）、
    破财工程酉运强拆反赔（yanjiu:2763，酉冲卯功神）、
    b67 复例二丙子运破财（shouke-ans34:2872，杀临攻身）、
    医师卯运年入百万（yanjiu:7048，吉运无反局）。"""
    r = analyze_yunfan(['庚', '己', '庚', '乙'], ['戌', '卯', '子', '酉'], '庚',
                       dayun_list=[{'gz': '丙子'}])
    assert any('破坏功神' in t or '伏吟三刑' in t for t in _dy_fan_types(r))
    r = analyze_yunfan(['辛', '癸', '丁', '癸'], ['亥', '巳', '未', '卯'], '丁',
                       dayun_list=[{'gz': '己酉'}])
    assert any('破坏功神' in t for t in _dy_fan_types(r))
    r = analyze_yunfan(['甲', '癸', '丁', '庚'], ['寅', '酉', '丑', '子'], '丁',
                       dayun_list=[{'gz': '丙子'}])
    assert any('杀临攻身' in t for t in _dy_fan_types(r))
    r = analyze_yunfan(['壬', '丁', '壬', '乙'], ['寅', '未', '申', '巳'], '壬',
                       dayun_list=[{'gz': '癸卯'}])
    assert r['dayun_fan'] == []


# ---------------------------------------------------------------------------
# A1：岁运反局切片入方向否决链（caiming 封顶 / guanming 否决+门槛 / zhiye gating）
# ---------------------------------------------------------------------------
from mangpai.subjective.yunfan import current_fan_slice
from mangpai.subjective.yongshen import assess_direction_signals
from mangpai.subjective.caiming import analyze_caiming
from mangpai.subjective.guanming import analyze_guanming


def _zhenbao1_yunfan():
    """第1期（戊戌己未乙巳丁亥，壬戌运戊辰年）yunfan 全量。"""
    return analyze_yunfan(['戊', '己', '乙', '丁'], ['戌', '未', '巳', '亥'], '乙',
                          dayun_list=[{'gz': '壬戌', 'start_age': 5}],
                          liunian_list=[{'gz': '戊辰', 'year': 1988}],
                          current_dayun={'gz': '壬戌'})


def test_current_fan_slice_filters_current_dayun():
    """切片只保留当前大运柱；include 开关控制运/岁两段。

    夹具用案例一（丙辰运辰穿卯=类型一破坏功神，书锚真阳）；原第1期壬戌运
    夹具于 A14 收窄后大运段不再命中（其反局在戊辰年流年/双冲联动侧，非
    大运三类型），不足以作大运切片夹具。"""
    yf = analyze_yunfan(['戊', '甲', '辛', '癸'], ['申', '寅', '卯', '巳'], '辛',
                        dayun_list=[{'gz': '丙辰', 'start_age': 5}],
                        liunian_list=[{'gz': '戊辰', 'year': 1988}],
                        current_dayun={'gz': '丙辰'})
    s = current_fan_slice(yf, '丙辰')
    assert s['dayun_fan'] and all(d['gz'] == '丙辰' for d in s['dayun_fan'])
    assert s['liunian_fan']
    # 不含大运段
    s2 = current_fan_slice(yf, '丙辰', include_dayun=False)
    assert s2['dayun_fan'] == [] and s2['liunian_fan']
    # 不含流年段（自动流年展示锚点不入否决链）
    s3 = current_fan_slice(yf, '丙辰', include_liunian=False)
    assert s3['liunian_fan'] == [] and s3['sui_yun_liandong'] == []
    # 全量 dayun_fan 中无匹配 gz → 空
    s4 = current_fan_slice(yf, '甲子')
    assert s4['dayun_fan'] == []


def test_direction_signals_suiyun_fanju():
    """岁运反局切片使 fanju=True 并带岁运理由；无切片时行为不变。"""
    gans, zhis = ['戊', '己', '乙', '丁'], ['戌', '未', '巳', '亥']
    base = assess_direction_signals('乙', gans, zhis)
    assert not base['suiyun_fanju']
    slice_ = current_fan_slice(_zhenbao1_yunfan(), '壬戌')
    ds = assess_direction_signals('乙', gans, zhis, yunfan_result=slice_)
    assert ds['suiyun_fanju'] and ds['fanju']
    assert any(r.startswith('岁运') for r in ds['reasons'])
    assert ds['direction'] == '凶'


def test_caiming_capped_by_suiyun_fanju():
    """第1期：原局富档（L3大富大贵），岁运反局（壬戌运戊辰年双冲）→ 财命封顶小康下。"""
    gans, zhis = ['戊', '己', '乙', '丁'], ['戌', '未', '巳', '亥']
    slice_ = current_fan_slice(_zhenbao1_yunfan(), '壬戌')
    cm = analyze_caiming('乙', gans, zhis, yunfan_result=slice_)
    assert cm['tier'] in ('贫', '小康')
    assert '下浮封顶' in cm['summary']
    # 富档抹除：不再标亿级（避免破财岁仍标富档的口径跳跃）
    assert '亿' not in str(cm['level'].get('wealth_grade', ''))


def test_guanming_veto_threshold_protects_positive_structure():
    """第5期（乙巳庚辰辛卯壬辰，官杀有根=正向官命结构）：岁运反局不误否决官命。"""
    gans, zhis = ['乙', '庚', '辛', '壬'], ['巳', '辰', '卯', '辰']
    yf = analyze_yunfan(gans, zhis, '辛',
                        dayun_list=[{'gz': '丙子', 'start_age': 5}],
                        liunian_list=[{'gz': '壬午', 'year': 2002}],
                        current_dayun={'gz': '丙子'})
    slice_ = current_fan_slice(yf, '丙子')
    assert slice_['liunian_fan']  # 壬午年确有反局/联动
    gm = analyze_guanming('辛', gans, zhis, yunfan_result=slice_)
    assert gm['is_guanming']  # 门槛保护：岁运反局理由被剥离，不否决
