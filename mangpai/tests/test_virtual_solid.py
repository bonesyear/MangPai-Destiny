"""virtual_solid 虚实书例哨兵（F4 批：批9 P0×2 锁定）

书锚：
- 《段氏理象学》:5647-5649 「盲派讲的虚实只就一柱干支而言，与周围的生克关系没有联系」
- 《段氏理象学》:5659 「天干无根无生者虚，天干有根有生者实」
- 《段氏理象学》:5663-5665 / :5706-5714 虚实表（甲子列实，甲坐午/庚戌/辛未列虚）
- 《盲派初级命理学》:2461 「得强根、坐禄、坐印都是实」
- 《段氏理象学》:3120-3122 燥土（未戌）不生金反脆金（庚戌/辛未列虚的机制）
"""
from mangpai.objective.virtual_solid import analyze_virtual_solid


def _entry(result, pillar):
    for r in result['virtual_solid']:
        if r['pillar'] == pillar:
            return r
    raise AssertionError(f'{pillar} 未分析')


def test_root_search_limited_to_own_pillar():
    # 甲坐午书定虚（:5665）；他柱见寅不得使甲坐实（只就一柱，:5647-5649）
    r = analyze_virtual_solid('丙', '寅', '甲', '午', '庚', '申', '辛', '酉')
    jia = _entry(r, '年柱')
    assert jia['is_solid'] is False
    assert jia['base_type'] == '虚透'


def test_zuo_yin_is_solid():
    # 坐印皆实（初级:2461；甲子列实表 :5663-5665）——不再判虚透怕克
    r = analyze_virtual_solid('丙', '戌', '甲', '子', '庚', '申', '辛', '酉')
    jia = _entry(r, '年柱')
    assert jia['is_solid'] is True
    assert jia['vulnerable_to_ke']['vulnerable'] is False
    assert jia['vulnerable_to_ke']['level'] == '无'


def test_book_table_spot_checks():
    # 实表：庚辰（本气印）/辛丑（本气印）/甲辰（藏干根）；虚表：庚戌/辛未（燥土脆金）
    cases = [
        ('庚', '辰', True), ('辛', '丑', True), ('甲', '辰', True),
        ('庚', '戌', False), ('辛', '未', False),
    ]
    for gan, zhi, solid in cases:
        r = analyze_virtual_solid('丙', '寅', gan, zhi, '壬', '午', '癸', '亥')
        e = _entry(r, '年柱')
        assert e['is_solid'] is solid, f'{gan}{zhi} 应{"实" if solid else "虚"}'
