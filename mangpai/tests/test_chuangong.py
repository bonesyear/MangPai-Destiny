"""串宫压运 (chuangong) 测试 - 验证 docs/chuangong-spec.md 规定行为。

覆盖：
  串宫分级（2弱/3强/4全）、positions/pillars/theme 结构、空亡排除、
  压运三型（增强/触发/引入）、冲散/合化/会局 conflict、容错与 summary。
判据为结构检测（出现次数+冲合会关系），不做吉凶，见模块 docstring。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.chuangong import analyze_chuangong


# ── 串宫检测与分级 ──

def test_no_chuangong():
    """四支各异 → 无串宫。"""
    r = analyze_chuangong('子', '寅', '午', '酉')
    assert r['chuangong_chains'] == {}
    assert r['chuangong_count'] == 0
    assert r['has_severe_chuangong'] is False
    assert '无串宫' in r['summary']


def test_weak_chuangong_2x():
    """2 次 → 弱串，不计 severe。"""
    r = analyze_chuangong('子', '午', '子', '酉')
    assert set(r['chuangong_chains']) == {'子'}
    c = r['chuangong_chains']['子']
    assert c['count'] == 2
    assert c['level'] == '弱串'
    assert c['positions'] == ['年柱', '日柱']
    assert c['pillars'] == ['year', 'day']
    assert c['theme'] == '水智/暗流'
    assert r['has_severe_chuangong'] is False


def test_strong_chuangong_3x():
    """3 次 → 强串，计 severe（spec 示例：子 年月时）。"""
    r = analyze_chuangong('子', '子', '午', '子')
    c = r['chuangong_chains']['子']
    assert c['count'] == 3
    assert c['level'] == '强串'
    assert c['positions'] == ['年柱', '月柱', '时柱']
    assert c['pillars'] == ['year', 'month', 'hour']
    assert r['has_severe_chuangong'] is True


def test_full_chuangong_4x():
    """4 次 → 全串（一生所有阶段，极强信号）。"""
    r = analyze_chuangong('午', '午', '午', '午')
    c = r['chuangong_chains']['午']
    assert c['count'] == 4
    assert c['level'] == '全串'
    assert c['theme'] == '火明/巅峰'
    assert r['has_severe_chuangong'] is True


def test_multiple_chains():
    """两条独立串宫链可同时成立。"""
    r = analyze_chuangong('子', '午', '子', '午')
    assert set(r['chuangong_chains']) == {'子', '午'}
    assert r['chuangong_count'] == 2


# ── 空亡排除 ──

def test_kong_wang_excluded():
    """空亡地支不参与串宫统计：子×3 但子空亡 → 无串宫。"""
    r = analyze_chuangong('子', '子', '午', '子', kong_wang=['子'])
    assert r['chuangong_chains'] == {}
    assert r['chuangong_count'] == 0


def test_kong_wang_partial_pillars():
    """空亡按地支整体排除（不分柱位），非空亡支不受影响。"""
    r = analyze_chuangong('子', '午', '午', '酉', kong_wang=['戌', '亥'])
    assert set(r['chuangong_chains']) == {'午'}


# ── 压运三型 ──

def test_yayun_enhance():
    """运支命中已有串宫链（命局≥2次）→ 增强。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          dayun_list=[{'gz': '甲子'}])
    assert len(r['yayun_hits']) == 1
    h = r['yayun_hits'][0]
    assert h['dayun_index'] == 0
    assert h['dayun_gz'] == '甲子'
    assert h['zhi'] == '子'
    assert h['type'] == '增强'
    assert '年-月-时' in h['detail']


def test_yayun_trigger():
    """运支在命局仅 1 次 → 触发新串宫。"""
    r = analyze_chuangong('子', '子', '午', '酉',
                          dayun_list=[{'gz': '丙午'}])
    h = r['yayun_hits'][0]
    assert h['type'] == '触发'
    assert h['zhi'] == '午'
    assert '原日位+运位' in h['detail']


def test_yayun_introduce():
    """运支不在命局 → 压运引入新主题。"""
    r = analyze_chuangong('子', '子', '午', '酉',
                          dayun_list=[{'gz': '丙寅'}])
    h = r['yayun_hits'][0]
    assert h['type'] == '引入'
    assert '木生/开创' in h['detail']


# ── 冲合会 conflict ──

def test_yayun_chong_breaks_chain():
    """运支与已有串宫支相冲 → 冲散串宫（子午冲）。"""
    r = analyze_chuangong('子', '子', '辰', '子',
                          dayun_list=[{'gz': '甲午'}])
    h = r['yayun_hits'][0]
    assert h['conflict'] == {'冲': '子'}
    assert '冲散子串宫' in h['detail']


def test_yayun_liuhe():
    """运支与已有串宫支六合 → 合化串宫（子丑合）。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          dayun_list=[{'gz': '己丑'}])
    h = r['yayun_hits'][0]
    assert h['conflict'] == {'合': '子'}
    assert '合化子串宫' in h['detail']


def test_yayun_sanhe_banhe():
    """运支与已有串宫支同三合/半合 → 会局增强（申子半合）。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          dayun_list=[{'gz': '壬申'}])
    h = r['yayun_hits'][0]
    assert h['conflict'] == {'会': '子'}
    assert '会局增强子串宫' in h['detail']


def test_conflict_skips_self_chain():
    """运支增强自身串宫链时，不对自身链记 conflict。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          dayun_list=[{'gz': '丙子'}])
    h = r['yayun_hits'][0]
    assert h['type'] == '增强'
    assert h['conflict'] is None


# ── 流年 ──

def test_liunian_hits():
    """流年序列独立分析，键名为 liunian_index/liunian_gz。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          liunian_list=[{'gz': '戊子'}, {'gz': '庚寅'}])
    assert len(r['yayun_liunian']) == 2
    assert r['yayun_liunian'][0]['liunian_index'] == 0
    assert r['yayun_liunian'][0]['liunian_gz'] == '戊子'
    assert r['yayun_liunian'][0]['type'] == '增强'
    assert r['yayun_liunian'][1]['type'] == '引入'


# ── 容错 ──

def test_none_dayun_liunian():
    """dayun/liunian 为 None → 仅串宫分析，不压运。"""
    r = analyze_chuangong('子', '子', '午', '酉',
                          dayun_list=None, liunian_list=None)
    assert r['yayun_hits'] == []
    assert r['yayun_liunian'] == []


def test_invalid_gz_tolerated():
    """非法干支/空 dict/None 项不崩溃，跳过该步。"""
    r = analyze_chuangong('子', '子', '午', '酉',
                          dayun_list=[{'gz': ''}, {}, None, {'gz': 'X甲'}, {'gz': '甲寅'}])
    assert len(r['yayun_hits']) == 1
    assert r['yayun_hits'][0]['zhi'] == '寅'


def test_invalid_natal_zhi_tolerated():
    """非法命局地支不崩溃。"""
    r = analyze_chuangong('子', 'X', '', '子')
    assert set(r['chuangong_chains']) == {'子'}


# ── summary ──

def test_summary_content():
    """summary 汇总串宫与压运（spec 示例结构）。"""
    r = analyze_chuangong('子', '子', '午', '子',
                          dayun_list=[{'gz': '甲子'}], liunian_list=[{'gz': '丙寅'}])
    s = r['summary']
    assert '命局串宫：子(强串,年/月/时)' in s
    assert '大运甲子增强子支' in s
    assert '流年丙寅引入寅支' in s
