# -*- coding: utf-8 -*-
"""F19 批哨兵：yunfan 大运侧两 P1 修复（先红后绿）。

1. 大运侧合变冲参与字收窄（批4 P1-3）：运冲须冲原局合做功参与字——
   与冲变合 A14 收窄对称（案例四子合丑锚）。包工头盘己酉运酉冲卯
   （卯与寅亥合局无关）旧误触发假阳。
2. 大运侧禄刃倒戈补挂（批4 P1-4）：此前 _detect_lu_ren_fangg 仅流年侧
   挂接，大运段 0 命中。案例七锚 gaoji:3761-3764：辛卯丙申辛未丁酉行
   丁卯运，卯冲原局酉禄，书明文「酉金禄神被冲，该年因罪被枪毙」。
3. 禄/刃字须在局方论被冲（批4 P2-1：natal_zhis 形参旧未用）。
"""
from mangpai.subjective.yunfan import analyze_yunfan, _detect_lu_ren_fangg


def _dayun_fan_types(gans, zhis, day_gan, gz):
    r = analyze_yunfan(gans, zhis, day_gan,
                       dayun_list=[{'gz': gz, 'start_age': 30, 'end_age': 40}])
    out = []
    for d in r['dayun_fan']:
        out.extend(f['fan_type'] for f in d['fans'])
    return out


def test_baogongtou_jiyou_hebianchong_suppressed():
    """包工头（壬寅辛亥丁丑癸卯，chuji:3296）己酉运：酉冲卯与寅亥合局
    无关——合变冲假阳消除（书明文壬卯/丁巳运发财）。"""
    types = _dayun_fan_types(['壬', '辛', '丁', '癸'], ['寅', '亥', '丑', '卯'],
                             '丁', '己酉')
    assert '大运反局·类型二(合变冲)' not in types


def test_hebianchong_participating_char_still_fires():
    """构造正例：原局寅亥合，运申冲寅（合参与字）→ 合变冲仍触发。"""
    types = _dayun_fan_types(['甲', '丙', '戊', '庚'], ['寅', '亥', '申', '子'],
                             '戊', '甲申')
    assert '大运反局·类型二(合变冲)' in types


def test_anli7_dingmao_lu_ren_fangg():
    """案例七（辛卯丙申辛未丁酉，gaoji:3761-3764）丁卯运：卯冲原局酉禄
    → 大运反局·禄刃倒戈命中（书明文枪毙）。"""
    types = _dayun_fan_types(['辛', '丙', '辛', '丁'], ['卯', '申', '未', '酉'],
                             '辛', '丁卯')
    assert '大运反局·类型一(禄刃倒戈)' in types


def test_lu_ren_must_be_in_natal():
    """禄/刃字不在局则冲无所冲，不报倒戈（natal_zhis 形参生效）。"""
    # 辛日禄在酉：原局无酉，卯来不报
    assert _detect_lu_ren_fangg('卯', '辛', ['子', '午', '卯', '辰']) is None
    # 原局有酉，卯冲酉 → 报
    assert _detect_lu_ren_fangg('卯', '辛', ['卯', '申', '未', '酉']) is not None
