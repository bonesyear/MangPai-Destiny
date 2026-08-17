"""anhe 暗合书例哨兵（F2 批：批1 P1-2 → 批9 升级 P0，删「子巳」锁定）

书锚：
- 《段氏理象学》:2555 「寅丑暗合，午亥暗合，卯申暗合」（定义章全列三对）
- 《盲派初级命理学》:3218 「暗合在盲派命理中也是做功的一部分。只有三个：
  卯申、寅丑、午亥」（排他表述，显式排除子巳）
"""
from mangpai.objective.constants import AN_HE
from mangpai.objective.anhe import analyze_anhe


def test_anhe_exactly_three_pairs():
    assert AN_HE == {
        '寅': '丑', '丑': '寅',
        '午': '亥', '亥': '午',
        '卯': '申', '申': '卯',
    }
    assert '子' not in AN_HE and '巳' not in AN_HE


def test_zi_si_not_anhe():
    # 子巳同盘不再报暗合（初级:3218 排他）
    assert analyze_anhe('子', '巳', '申', '酉')['anhe'] == []


def test_three_pairs_detected():
    r = analyze_anhe('寅', '丑', '午', '亥')['anhe']
    pairs = {(x['from'], x['to']) for x in r}
    assert len(r) == 2  # 寅丑、午亥各一
    r2 = analyze_anhe('卯', '申', '', '')['anhe']
    assert len(r2) == 1 and '卯申暗合' in r2[0]['desc']
