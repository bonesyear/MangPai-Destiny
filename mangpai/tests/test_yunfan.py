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
    """案例一：戊申甲寅辛卯癸巳，丙辰运——辰穿卯晦巳，破坏功神。"""
    r = analyze_yunfan(['戊', '甲', '辛', '癸'], ['申', '寅', '卯', '巳'], '辛',
                       dayun_list=[{'gz': '丙辰'}])
    assert any('破坏功神' in t for t in _dy_fan_types(r))
    assert any('忌神反客' in t for t in _dy_fan_types(r))


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
    """切片只保留当前大运柱；include 开关控制运/岁两段。"""
    yf = _zhenbao1_yunfan()
    s = current_fan_slice(yf, '壬戌')
    assert s['dayun_fan'] and all(d['gz'] == '壬戌' for d in s['dayun_fan'])
    assert s['liunian_fan'] and s['sui_yun_liandong']
    # 不含大运段
    s2 = current_fan_slice(yf, '壬戌', include_dayun=False)
    assert s2['dayun_fan'] == [] and s2['liunian_fan']
    # 不含流年段（自动流年展示锚点不入否决链）
    s3 = current_fan_slice(yf, '壬戌', include_liunian=False)
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
