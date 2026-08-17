# -*- coding: utf-8 -*-
"""F17 哨兵：xueli 破坏之神书口径 + liuqin 星宫同坏总门/子息原神/三节补齐。

书锚：
- zhongji:5397「以官杀、印星与食神当学历之神；以财星、伤官、比劫当破坏学历之神」
- zhongji:5405-5409 伤官配印/配官杀做功则学有所成；比劫结伙成群主不思学习
- gaoji:13649「父母星与父母宫同时被破坏，且破坏之力甚剧」（星宫同坏总门）
- gaoji:14116-14118「官杀之原神为财，食伤之原神为比劫」（财星统看则原神=食伤）
- gaoji:14412 排行诀 / 14651 情谊诀 / 14230 子女优劣诀
"""
from mangpai.subjective.xueli import classify_xueli_shen, classify_xueli_level
from mangpai.subjective.liuqin import (
    detect_parent_zaoshi,
    detect_zixi_youwu,
    detect_zixi_youlie,
    classify_xiongdi_paihang,
    classify_xiongdi_qingyi,
    analyze_liuqin,
)


def _xueli_level(g4, z4):
    return classify_xueli_level(g4[2], list(g4), list(z4)).get('level', '')


# ── 中级 ch11 学历 21 书例探针（zhongji:5414-5577）──
XUELI_21 = [
    ('丁壬甲己', '未子戌巳', '高'),   # 例1 食神库制印做功，考入重点大学
    ('庚癸甲己', '戌未寅巳', '高'),   # 例2 印杀看学历，庚午年考取重点大学
    ('壬壬丙丁', '子子戌酉', '高'),   # 例3 丁壬合杀有功，考大本
    ('甲甲辛甲', '寅戌亥午', '高'),   # 例4 杀星成局合制伤官，博士（reg67 锚）
    ('癸癸庚丁', '丑亥午亥', '高'),   # 例5 金水伤官见官，文科博士
    ('丙乙甲丁', '子未寅卯', '低'),   # 例6 比劫旺无文化，小学未毕业
    ('壬丙壬丁', '子午辰未', '低'),   # 例7 杀不配印，初中（reg67 锚）
    ('壬丙壬己', '子午辰酉', '高'),   # 例8 杀配印，硕士
    ('丁丁丙癸', '卯未戌巳', '低'),   # 例9 年月比劫不爱学习，没考上大学
    ('乙癸壬丁', '丑未申未', '低'),   # 例10 印不做功，学历不高（护校）
    ('癸甲丙戊', '亥子申子', '高'),   # 例11 官杀有制化，壬午年考中大学
    ('辛壬乙丁', '亥辰酉亥', '高'),   # 例12 印制食神+杀合辰，数学博士
    ('壬辛庚丁', '午亥辰亥', '高'),   # 例13 食神合官+食神入辰墓，数学教授
    ('庚乙甲丁', '午酉午卯', '高'),   # 例14 乙庚合杀有功，学习优等
    ('丁丙庚壬', '未午戌午', '高'),   # 例15 火燥土成势制尽食神，数学硕士
    ('乙戊丁甲', '卯寅酉辰', '高'),   # 例16 伤官配印，博士
    ('癸丁丁丙', '卯巳巳午', '高'),   # 例17 杀印尽泄于丁，博士
    ('丁丁甲辛', '巳未午未', '中断'), # 例18 伤官太旺无印制服，中途中断
    ('庚己戊甲', '戌丑午寅', '高'),   # 例19 杀星配印，本科
    ('辛庚甲癸', '未子子酉', '高'),   # 例20 官杀配印，学习特别好
    ('甲癸甲癸', '子酉子酉', '高'),   # 例21 正官配印，保送重点大学
]

# 修复后实测命中数（先红后绿锁定，勿无书锚上调）
XUELI_21_MIN_HITS = 9


def test_xueli_21_shuli_probe():
    misses = []
    hits = 0
    for g4, z4, want in XUELI_21:
        got = _xueli_level(list(g4), list(z4))
        if got == want:
            hits += 1
        else:
            misses.append(f'{g4}/{z4} 书={want} 引擎={got}')
    assert hits >= XUELI_21_MIN_HITS, f'命中 {hits}/21 < {XUELI_21_MIN_HITS}\n' + '\n'.join(misses)


def test_pohuai_shen_book_koujing():
    """破坏之神=财/伤官/比劫（zhongji:5397），非枭。"""
    # 例9（丁丁丙癸/卯未戌巳）：年月比劫双透，无枭——破坏之神须含比劫
    shen = classify_xueli_shen('丙', list('丁丁丙癸'), list('卯未戌巳'))
    assert '比劫' in shen['破坏_shen']
    assert '枭' not in shen['破坏_shen']
    # 伤官明现亦为破坏之神（例6 丙乙甲丁/子未寅卯 丁伤官透）
    shen2 = classify_xueli_shen('甲', list('丙乙甲丁'), list('子未寅卯'))
    assert '伤官' in shen2['破坏_shen']


def test_xueli_li9_bijie_direction():
    """例9 方向反转修复：年月比劫成群，不再判高（书断没考上大学，zhongji:5484-5486）。
    判「低」须 X2 印做功要件（规划项，本批 X1 范围外），先锁不再判高+中。"""
    lv = _xueli_level(list('丁丁丙癸'), list('卯未戌巳'))
    assert lv in ('低', '中')


def test_xueli_li6_bijie_wang():
    """例6：比劫旺表示无文化 → 低（zhongji:5462-5463）。"""
    assert _xueli_level(list('丙乙甲丁'), list('子未寅卯')) == '低'


def test_xueli_li21_bijie_xiebu_kou():
    """例21 反锚：单透比劫无根群（甲坐子泄印做功）不扣 → 高（zhongji:5573-5576）。"""
    assert _xueli_level(list('甲癸甲癸'), list('子酉子酉')) == '高'


# ── liuqin：星宫同坏总门（gaoji:13649）──

def test_zaoshi_gong_huai_only_not_enough():
    """仅年月宫受冲、父母星无伤 → 不断早逝（总门：星宫同坏方断）。"""
    # 甲日：年丙子（印食）月丁午（伤财?己=财）——四柱无财临库/患父患母
    r = detect_parent_zaoshi('甲', list('丙丁甲戊'), list('子午寅申'))
    assert r['is_zaoshi'] is False


def test_zaoshi_xing_gong_tong_huai():
    """父星财坐墓（戊戌）+ 年月辰戌冲 → 星宫同坏断早逝（口诀二 财临库地父当死）。"""
    r = detect_parent_zaoshi('甲', list('戊甲甲丙'), list('戌辰寅寅'))
    assert r['is_zaoshi'] is True


# ── liuqin：子息原神取反（gaoji:14116-14118）──

def test_zixi_yuanshen_cai_shi_shishang():
    """女命财星统看子息时，原神=食伤（生财者）；比劫克财是忌神，误报须消。"""
    # 甲日女：火（食伤）全无明现 → cat=财（辰中戊）；比劫乙卯被子卯破
    r = detect_zixi_youwu('甲', list('甲乙甲庚'), list('子卯辰申'), gender='女')
    assert r['child_star_cat'] == '财'
    assert not any('比劫' in m and '原神' in m for m in r['markers'])


def test_zixi_yuanshen_guan_sha_shi_cai():
    """男命官杀为子息，原神=财不变（书锚原句）。"""
    # 丁日男：癸水七杀为子，财金居申受寅申冲 → 原神（财）被冲
    r = detect_zixi_youwu('丁', list('戊庚丁壬'), list('寅申巳寅'), gender='男')
    assert any('原神（财）' in m for m in r['markers'])


# ── liuqin：排行诀（gaoji:14412）──

def test_paihang_yang_gan_yang_sheng():
    """案例四：戊子甲寅甲子丙寅——甲木日主生寅月（建禄），阳干阳生必为大。"""
    r = classify_xiongdi_paihang('甲', list('戊甲甲丙'), list('子寅子寅'))
    assert r['is_eldest'] is True


def test_paihang_yin_gan_yin_sheng():
    """阴干阴生大定准：乙木日主生亥月（盲派阴阳同生同死，乙长生亥）。"""
    r = classify_xiongdi_paihang('乙', list('丁甲乙丙'), list('卯亥酉午'))
    assert r['is_eldest'] is True


def test_paihang_not_eldest():
    """甲日子月（沐浴非生旺）→ 非老大判定。"""
    r = classify_xiongdi_paihang('甲', list('丙甲甲丁'), list('午子寅卯'))
    assert r['is_eldest'] is not True


def test_paihang_ri_zuo_chong_sheng():
    """日坐冲生定无兄：甲日亥月（长生）日支巳冲亥。"""
    r = classify_xiongdi_paihang('甲', list('壬甲甲丙'), list('戌亥巳寅'))
    assert r['is_eldest'] is True


# ── liuqin：情谊诀（gaoji:14651）──

def test_qingyi_zhengcai():
    """案例十：甲申戊辰甲子丙寅——双甲争戊财，兄弟争产（gaoji:14720）。"""
    r = classify_xiongdi_qingyi('甲', list('甲戊甲丙'), list('申辰子寅'))
    assert any('争' in m for m in r['markers'])
    assert r['verdict'] in ('争夺', '薄')


def test_qingyi_gong_sheng_rizhu():
    """兄弟宫（月支亥水）生日主甲木 → 情谊厚。"""
    r = classify_xiongdi_qingyi('甲', list('戊壬甲丙'), list('戌亥午申'))
    assert r['verdict'] == '厚'


def test_qingyi_gong_chong_rizhu():
    """兄弟宫与日柱相冲（月申冲日寅）→ 缘薄。"""
    r = classify_xiongdi_qingyi('甲', list('戊甲申丙'), list('戌申寅午'))
    assert r['verdict'] in ('薄', '争夺')


# ── liuqin：子女优劣（gaoji:14230）──

def test_youlie_an8_you():
    """案例八：壬辰癸卯丙辰戊子（女）——食神透时干得位、杀印相生 → 优。"""
    r = detect_zixi_youlie('丙', list('壬癸丙戊'), list('辰卯辰子'), gender='女')
    assert r['verdict'] == '优'


def test_youlie_an9_lie():
    """案例九：丙子戊戌丁丑丁未（女）——食伤满盘犯丑未戌三刑 → 劣。"""
    r = detect_zixi_youlie('丁', list('丙戊丁丁'), list('子戌丑未'), gender='女')
    assert r['verdict'] == '劣'


def test_analyze_liuqin_has_three_new_sections():
    r = analyze_liuqin('甲', list('戊甲甲丙'), list('子寅子寅'), gender='男')
    assert 'xiongdi_paihang' in r
    assert 'xiongdi_qingyi' in r
    assert 'zixi_youlie' in r
