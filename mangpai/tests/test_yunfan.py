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
