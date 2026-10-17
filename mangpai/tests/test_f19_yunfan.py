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


# ── 批E：岁运三特殊法则（gaoji 岁运特殊关系总诀 :18890-18892「并临力倍分
#    喜忌，征岁犯上灾突发，晦岁侵阳福寿差」）marker 级哨兵（中性措辞，
#    不入凶链，输出于 suiyun_teshu 键）──

def _teshu(gans, zhis, day_gan, dy_gz, ln_gz):
    r = analyze_yunfan(gans, zhis, day_gan,
                       dayun_list=[{'gz': dy_gz, 'start_age': 30, 'end_age': 40}],
                       liunian_list=[{'gz': ln_gz, 'year': 2020}],
                       current_dayun={'gz': dy_gz})
    return [t for d in r.get('suiyun_teshu', []) for t in d['teshu']]


def test_e_suiyun_binglin_ji():
    """岁运并临·吉向（gaoji:18894-18898「吉神并临福禄至」）：甲日从弱
    （喜水木），壬子大运+壬子流年干支全同，并临喜神。"""
    ts = _teshu(['庚', '辛', '甲', '丙'], ['申', '酉', '寅', '午'], '甲',
                '壬子', '壬子')
    assert any(t['teshu_type'] == '岁运并临' and t['direction'] == '吉向'
               for t in ts)


def test_e_suiyun_binglin_xiong():
    """岁运并临·凶向（「凶神并临祸灾殃」）：同盘戊申并临（土金=忌）。"""
    ts = _teshu(['庚', '辛', '甲', '丙'], ['申', '酉', '寅', '午'], '甲',
                '戊申', '戊申')
    assert any(t['teshu_type'] == '岁运并临' and t['direction'] == '凶向'
               for t in ts)


def test_e_zheng_taishui_directional():
    """征太岁（gaoji:18882/18995「大运主动冲克流年…以下犯上」，方向特定=
    运克岁）：庚申运克甲寅岁（庚克甲+申冲寅）命中；丙午运于甲寅岁
    （丙不克甲、午寅不冲克）不出。"""
    ts = _teshu(['庚', '辛', '甲', '丙'], ['申', '酉', '寅', '午'], '甲',
                '庚申', '甲寅')
    assert any(t['teshu_type'] == '征太岁' for t in ts)
    ts2 = _teshu(['庚', '辛', '甲', '丙'], ['申', '酉', '寅', '午'], '甲',
                 '丙午', '甲寅')
    assert not any(t['teshu_type'] == '征太岁' for t in ts2)


def test_e_hui_taishui():
    """晦太岁（gaoji:19077-19086「湿土寒水蔽日光…火岁逢辰丑亥子」）：
    身弱甲日（忌土），原局辰湿土忌神在局，丙午火岁 → 晦太岁；
    壬子水岁（非火非木之阳气/生机岁）不出。"""
    ts = _teshu(['壬', '辛', '甲', '丙'], ['辰', '酉', '寅', '午'], '甲',
                '庚子', '丙午')
    assert any(t['teshu_type'] == '晦太岁' for t in ts)
    ts2 = _teshu(['壬', '辛', '甲', '丙'], ['辰', '酉', '寅', '午'], '甲',
                 '庚子', '壬子')
    assert not any(t['teshu_type'] == '晦太岁' for t in ts2)
