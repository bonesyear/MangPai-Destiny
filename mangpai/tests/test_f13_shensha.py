# -*- coding: utf-8 -*-
"""F13 shensha 批哨兵测试（先红后绿）。

五项改动锚点：
1. 桃花重建——书桃花=「禄合财官杀伤食」（zhongji:1517/2792/4349，
   gaoji:13259-13310 口诀「日主之禄与他合，便是情缘起动关」+案例八/九）；
   咸池整套五书无「咸池」明文，降为传统层；day_ref 接入 zhiye/hunyin 消费。
   岳飞（癸未乙卯甲子己巳）year-ref 咸池子落日柱曾驱动 performer=8 分，
   日支起算后桃花=酉不在局，performer 应落 1 分（批7/批8 审计实锤）。
2. 起算主支——默认 year→day（gaoji:7912「先以日支为主查空亡、亡神、劫煞，
   年支亦需同查」）；劫煞/灾煞补年日双查（gaoji:7789「以年支或日支查」）。
3. 马星 count 死判据——zaihuo 车祸改消费在局马数（in_pillars），
   旧 count=并集马支数恒≥3（随机 2000 盘 min=3，批8 实锤）。
4. 戊双刃漏检——zaihuo/gongmen_wuzhi×2/liuqin 四处 zhi 单值改全刃表
   （理象学:2086「戊刃在午、未」）。
5. shensha_reference 配置断路——默认 'day'，且 year_ref/day_ref 子键恒在
   （不再随 reference 翻转丢失）。

书例哨兵：岳飞 performer / 禄绊桃花两书例 / 驿马 gaoji 案例九。
"""
from mangpai.objective.shensha import compute_shensha_ext
from mangpai.subjective.zhiye import classify_zhiye
from mangpai.subjective.hunyin import detect_lu_ban_taohua
from mangpai.subjective.zaihuo import detect_chehuo
from mangpai.subjective.liuqin import detect_xiongdi_keshun


def test_yuefei_performer_day_ref():
    """岳飞：日支起算后咸池=酉不在局，performer 8分→1分（批8 传导实锤）。"""
    r = classify_zhiye('甲', ['癸', '乙', '甲', '己'], ['未', '卯', '子', '巳'])
    assert r['scores'].get('performer', 0) == 1


def test_taohua_shuli_genii():
    """gaoji 案例八 歌女（乙卯辛巳辛酉壬辰）：辛禄酉，辰酉合，
    辰藏癸=食神 → 禄绊桃花（外合）。"""
    r = detect_lu_ban_taohua('辛', ['乙', '辛', '辛', '壬'],
                             ['卯', '巳', '酉', '辰'], gender='女')
    assert r['is_lu_ban']


def test_taohua_shuli_anli9():
    """gaoji 案例九（戊午壬戌乙卯丁亥）：乙禄卯，卯戌合，
    戌藏戊辛丁=财/杀/食 → 禄绊桃花（内合）。"""
    r = detect_lu_ban_taohua('乙', ['戊', '壬', '乙', '丁'],
                             ['午', '戌', '卯', '亥'], gender='女')
    assert r['is_lu_ban']


def test_taohua_lu_he_yin_not_taohua():
    """zhongji:1517/4349「禄合印不为桃花」：甲禄寅，寅亥合，
    亥藏壬甲=枭/比（无财官杀伤食）→ 非桃花。"""
    r = detect_lu_ban_taohua('甲', ['甲', '丙', '甲', '丁'],
                             ['寅', '辰', '卯', '亥'])
    assert not r['is_lu_ban']


def test_taohua_he_fuqi_gong_not_taohua():
    """zhongji:1517「合到夫妻宫不为桃花」：丙禄巳，巳申合而申=日支 → 非桃花；
    对照：申在年（宾位）→ 桃花（申藏庚壬戊=财/杀/食）。"""
    r = detect_lu_ban_taohua('丙', ['庚', '乙', '丙', '甲'],
                             ['午', '辰', '申', '巳'])
    assert not r['is_lu_ban']
    r2 = detect_lu_ban_taohua('丙', ['庚', '乙', '丙', '甲'],
                              ['申', '辰', '午', '巳'])
    assert r2['is_lu_ban']


def test_yima_shuli():
    """gaoji 案例九 驿马（丁未辛亥乙巳丁丑）：日支巳→马亥卯未（未在年），
    年支未→马巳酉丑（巳在日、丑在时）——「马星在年时，主远行」双查并见。"""
    ss = compute_shensha_ext('乙', ['未', '亥', '巳', '丑'])
    ym = ss['驿马']
    assert ym['zhi'] == '亥' and ym['reference'] == 'day_zhi'
    assert 'year' in ym['in_pillars']
    assert ym['year_ref']['zhi'] == '巳'
    assert 'day' in ym['year_ref']['in_pillars']
    assert 'hour' in ym['year_ref']['in_pillars']


def test_reference_default_day():
    """起算主支 day + 劫煞/灾煞年日双查 + year_ref/day_ref 子键恒在。"""
    ss = compute_shensha_ext('甲', ['寅', '午', '子', '戌'])
    assert ss['桃花']['zhi'] == '酉'              # 日支子起（旧默认 year 得卯）
    assert ss['桃花']['year_ref']['zhi'] == '卯'  # 年支兼看
    assert ss['劫煞']['zhi'] == '巳'              # 日支子→巳
    assert ss['劫煞']['year_ref']['zhi'] == '亥'  # 年支寅→亥（双查补齐）
    assert ss['灾煞']['year_ref']['zhi'] == '子'  # 年支寅→子
    assert ss['亡神']['zhi'] == '亥'              # 日支子→亥
    assert ss['亡神']['year_ref']['zhi'] == '巳'  # 年支寅→巳


def test_wu_shuang_ren():
    """戊双刃（理象学:2086 午、未）：刃在未（无午）盘供给层 in_pillars 命中，
    消费层 zaihuo 凶神/liuqin 羊刃逢冲不再漏检。"""
    ss = compute_shensha_ext('戊', ['寅', '子', '未', '辰'])
    assert ss['羊刃']['zhi'] == '午'              # 主刃位单值契约保留
    assert ss['羊刃']['in_pillars'] == ['day']    # 全刃表检出未
    r = detect_chehuo('戊', ['己', '癸', '戊', '壬'], ['丑', '子', '未', '辰'])
    assert '羊刃' in r['xiong_shen']
    r2 = detect_xiongdi_keshun('戊', ['己', '癸', '戊', '壬'],
                               ['丑', '子', '未', '辰'])
    assert any('羊刃逢冲' in m for m in r2['markers'])  # 丑未冲冲动刃位


def test_chehuo_ma_count_in_pillars():
    """马星死判据：同局盘[寅午戌寅]马支=申子辰全不在局，
    旧 count=并集数=3 恒真白送 1 分；改消费在局马数后应为 0。"""
    r = detect_chehuo('甲', ['甲', '丙', '甲', '甲'], ['寅', '午', '戌', '寅'])
    assert r['ma_count'] == 0
