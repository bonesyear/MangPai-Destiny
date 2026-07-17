"""身体部位表 (body_parts) 测试 - 锁定高级篇 ch11.2/ch4 干支身体映射数据层。

覆盖：主表完整性（10干/12支/四柱）、古传口诀抽查、干主外支主内分层、
宫位身段主表（年腿足/时头面）、ch11 变体、十神归并查表、穿/破/刑主病表、
数据自检（_self_check 零问题）。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.body_parts import (
    GAN_BODY, ZHI_BODY, GAN_BODY_EXT, ZHI_BODY_EXT,
    PILLAR_BODY, PILLAR_BODY_CH11, SHISHEN_BODY,
    YINYANG_BINGJI, WX_BINGJI, HAI_DISEASE, PO_DISEASE, XING_DISEASE,
    get_gan_body, get_zhi_body, get_pillar_body, get_shishen_body,
    get_disease_by_hai, get_disease_by_po, get_disease_by_xing,
    _self_check,
)
from mangpai.objective.constants import DI_ZHI, GAN_WX, PILLAR_KEYS


# ── 完整性与自检 ──

def test_self_check_clean():
    assert _self_check() == []


def test_main_tables_cover_all():
    assert set(GAN_BODY) == set(GAN_WX)
    assert set(ZHI_BODY) == set(DI_ZHI)
    assert set(GAN_BODY_EXT) == set(GAN_WX)
    assert set(ZHI_BODY_EXT) == set(DI_ZHI)
    assert set(PILLAR_BODY) == set(PILLAR_KEYS)
    assert set(PILLAR_BODY_CH11) == set(PILLAR_KEYS)
    for t in (GAN_BODY, ZHI_BODY, GAN_BODY_EXT, ZHI_BODY_EXT):
        assert all(len(v) >= 2 for v in t.values())


# ── 古传口诀抽查（主表与口诀一致）──

def test_verse_spot_checks_gan():
    # 甲头乙项（颈）丙肩、丁心戊胃己脾、庚脐辛股壬胫癸足
    assert '头' in GAN_BODY['甲']
    assert '颈' in GAN_BODY['乙']
    assert '肩' in GAN_BODY['丙']
    assert '心' in GAN_BODY['丁']
    assert '胃' in GAN_BODY['戊']
    assert '脾' in GAN_BODY['己']
    assert '脐' in GAN_BODY['庚']
    assert '股' in GAN_BODY['辛']
    assert '胫' in GAN_BODY['壬']
    assert '足' in GAN_BODY['癸']


def test_verse_spot_checks_zhi():
    # 子膀胱、丑胞肚脾、寅胆、卯肝十指、辰皮肩胸、巳面齿、
    # 午眼目、未胃脊梁、申大肠肺、酉精血小肠→（主表取肺鼻精血耳）、
    # 戌命门腿足、亥头肾
    assert '膀胱' in ZHI_BODY['子']
    assert '脾' in ZHI_BODY['丑']
    assert '胆' in ZHI_BODY['寅']
    assert '肝' in ZHI_BODY['卯'] and '十指' in ZHI_BODY['卯']
    assert '皮肤' in ZHI_BODY['辰'] and '肩胸' in ZHI_BODY['辰']
    assert '面' in ZHI_BODY['巳'] and '齿' in ZHI_BODY['巳']
    assert '眼' in ZHI_BODY['午']
    assert '胃' in ZHI_BODY['未'] and '脊梁' in ZHI_BODY['未']
    assert '大肠' in ZHI_BODY['申'] and '肺' in ZHI_BODY['申']
    assert '精血' in ZHI_BODY['酉']
    assert '命门' in ZHI_BODY['戌'] and '腿足' in ZHI_BODY['戌']
    assert '头' in ZHI_BODY['亥'] and '肾' in ZHI_BODY['亥']


# ── 宫位身段主表（书主版本：年腿足、时头面门户）──

def test_pillar_body_main_version():
    assert '腿' in PILLAR_BODY['year'] and '足' in PILLAR_BODY['year']
    assert '脊' in PILLAR_BODY['month'] and '肩' in PILLAR_BODY['month']
    assert '五脏' in PILLAR_BODY['day'] and '六腑' in PILLAR_BODY['day']
    assert '头' in PILLAR_BODY['hour'] and '面' in PILLAR_BODY['hour']
    assert '生殖器' in PILLAR_BODY['hour']


def test_pillar_body_ch11_variant_kept():
    # ch11 变体单独存查（年含头面），不污染主表
    assert '头面' in PILLAR_BODY_CH11['year']
    assert '头面' not in PILLAR_BODY['year']


# ── 查表函数 ──

def test_getters():
    assert get_gan_body('甲') == ['头', '胆']
    assert '头面' in get_gan_body('甲', ext=True)     # 扩展层
    assert get_gan_body('X') == []                    # 非法干容错
    assert get_zhi_body('子')[0] == '膀胱'
    assert '喉咙' in get_zhi_body('子', ext=True)
    assert get_zhi_body('X') == []
    assert get_pillar_body('year') == PILLAR_BODY['year']
    assert get_pillar_body('year', variant='ch11') == PILLAR_BODY_CH11['year']
    assert get_pillar_body('x') == []
    # 返回副本，改返回值不污染表
    v = get_gan_body('甲')
    v.append('ZZ')
    assert get_gan_body('甲') == ['头', '胆']


def test_shishen_group_mapping():
    # 正印/偏印→印、正官/七杀→官杀、食神/伤官→食伤…
    assert get_shishen_body('正印') == SHISHEN_BODY['印']
    assert get_shishen_body('偏印') == SHISHEN_BODY['印']
    assert get_shishen_body('七杀') == SHISHEN_BODY['官杀']
    assert get_shishen_body('伤官') == SHISHEN_BODY['食伤']
    assert get_shishen_body('劫财') == SHISHEN_BODY['比劫']
    assert get_shishen_body('偏财') == SHISHEN_BODY['财']
    assert '身体' in get_shishen_body('禄')
    assert '四肢' in get_shishen_body('羊刃')
    assert get_shishen_body('日主') == []
    assert get_shishen_body('不存在') == []


# ── 病机数据层 ──

def test_wx_bingji_seven_named():
    # 七具名组合齐全
    assert set(WX_BINGJI) == {'寅亥合', '丑辰合金', '火克金', '木多火塞',
                              '土多金埋', '水多木漂', '金多水浊'}
    for v in WX_BINGJI.values():
        assert v.get('condition') and v.get('organs') and v.get('diseases')
    # 火克金注记金水相连才主肺
    assert '金水相连' in WX_BINGJI['火克金']['note']


def test_yinyang_three_states():
    assert set(YINYANG_BINGJI) == {'阴阳离决', '阳亢阴弱', '阴盛阳衰'}
    assert '高血压' in YINYANG_BINGJI['阳亢阴弱']['diseases']


def test_disease_tables():
    # 六穿 6 组、破仅书明文 2 组、三刑 3 组
    assert len(HAI_DISEASE) == 6
    assert len(PO_DISEASE) == 2
    assert len(XING_DISEASE) == 3
    # 无序查表
    assert get_disease_by_hai('午', '丑') == get_disease_by_hai('丑', '午')
    assert '心脏' in get_disease_by_hai('丑', '午')
    assert get_disease_by_hai('子', '丑') == []
    assert '肾气虚' in get_disease_by_po('子', '卯')
    assert get_disease_by_po('子', '酉') == []   # 书无明文不收
    assert '顽疾难愈' in get_disease_by_xing(['丑', '未', '戌'])
    assert get_disease_by_xing(['子', '卯'])     # 子卯刑（亦作破）
    assert get_disease_by_xing(['寅', '巳']) == []  # 寅巳仅两支不成申局不收
