"""wood_type 木性死活书例哨兵（F4 批：批9 P0 锁定）

书锚：
- 《段氏理象学》:12613-12615 「有水有根，水不生木之根也是死木」（戴妃造明例）
- 《段氏理象学》:3187-3189 岳飞造「子水并不生卯木，也不生甲木…所以算死木」
- 《段氏理象学》:2934-2936 「相破时就不一样了，子水不生卯木」
- 《段氏理象学》:3201-3205 乙亥活木明例（亥为木长生，亥未拱木）
"""
from mangpai.objective.wood_type import analyze_wood_type


def test_yuefei_is_dead_wood():
    # 岳飞：癸未乙卯甲子己巳——子水破卯根、穿未根，水不生木之根 → 死木
    r = analyze_wood_type('甲', '未', '卯', '子', '巳')
    assert r['wood_type'].startswith('死木'), r['wood_type']
    assert r['fire_xiuxiu'] is False
    assert r['control_water'] is True


def test_daifei_is_dead_wood():
    # 戴妃：辛丑甲午乙未丙戌——丑中癸水冲未中乙根，水不生木之根 → 死木
    r = analyze_wood_type('乙', '丑', '午', '未', '戌')
    assert r['wood_type'].startswith('死木'), r['wood_type']


def test_living_wood_preserved():
    # 乙亥活木例（:3201-3205）：亥水与未根无破冲穿 → 活木
    r = analyze_wood_type('乙', '戌', '未', '巳', '亥')
    assert r['wood_type'] == '活木', r['wood_type']
    assert r['fire_xiuxiu'] is True
    # 普通有根有水（子与寅卯无破冲穿）仍活木
    r2 = analyze_wood_type('甲', '亥', '寅', '子', '申')
    assert r2['wood_type'] == '活木', r2['wood_type']
