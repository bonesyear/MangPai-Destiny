# -*- coding: utf-8 -*-
"""H-fix-4b 重复逻辑下沉/统一批哨兵。

锁两类事实：
1. 结构同一性（先红后绿）：各模块十神/_cat/_wx_cat/_check_pair/_ensure_*
   必须就是公共实现的同一函数对象（别名），不再是本地副本。
2. 行为等价（回归锁，改动前后皆绿）：真值表抽查 + detect_relations
   黄金摘要（盘 A/B work_actions sha256，改动前捕获）。
"""
import hashlib
import json

from mangpai.objective import shishen as _shishen
from mangpai.objective import _relation_utils as _rel_utils
from mangpai.subjective import utils as _sub_utils

GANS = list('甲乙丙丁戊己庚辛壬癸')
WXS = ['木', '火', '土', '金', '水']


# ─────────── 1. 结构同一性（先红后绿）───────────

def test_shishen_of_single_source():
    from mangpai.objective import dayun, shenshu
    from mangpai.subjective import (caiming, guanming, hunyin, xiangfa_ops,
                                    gongmen_wuzhi, zhiye, liuqin, laoyu,
                                    yingqi_subj, xueli, zaihuo)
    for m in (dayun, shenshu, caiming, guanming, hunyin, xiangfa_ops,
              gongmen_wuzhi, zhiye, liuqin, laoyu, yingqi_subj, xueli, zaihuo):
        assert m._compute_shishen is _shishen.shishen_of, m.__name__


def test_shishen_cat_single_source():
    from mangpai.subjective import (caiming, guanming, xiangfa_ops, hunyin,
                                    gongmen_wuzhi, zhiye, liuqin, laoyu,
                                    xueli, zaihuo)
    for m in (caiming, guanming, xiangfa_ops):
        assert m._shishen_cat is _shishen.shishen_cat, m.__name__
    for m in (hunyin, gongmen_wuzhi, zhiye, liuqin, laoyu, xueli, zaihuo):
        assert m._cat is _shishen.shishen_cat, m.__name__


def test_wx_cat_single_source():
    from mangpai.subjective import (gongmen_wuzhi, zhiye, liuqin, zaihuo,
                                    xiangfa_ops, yongshen, gongliang)
    for m in (gongmen_wuzhi, zhiye, liuqin, zaihuo):
        assert m._wx_cat is _shishen.gan_wx_cat, m.__name__
    assert xiangfa_ops._wx_to_shishen_cat is _shishen.gan_wx_cat
    assert yongshen._wx_cat is _shishen.wx_cat
    assert gongliang._shishen_cat is _shishen.wx_cat


def test_check_pair_single_source():
    from mangpai.objective import zuogong_detect, dayun, gongshen
    for m in (zuogong_detect, dayun, gongshen):
        assert m._check_pair is _rel_utils.pair_in, m.__name__


def test_ensure_single_source():
    from mangpai.subjective import (caiming, guanming, hunyin, xiangfa_ops,
                                    zhiye, liuqin, laoyu, zaihuo, xueli,
                                    gongmen_wuzhi)
    for m in (caiming, guanming, hunyin, xiangfa_ops, zhiye, liuqin, laoyu,
              zaihuo, xueli, gongmen_wuzhi):
        assert m._ensure_relations is _sub_utils.ensure_relations, m.__name__
    for m in (caiming, xiangfa_ops):
        assert m._ensure_muku is _sub_utils.ensure_muku, m.__name__


def test_xiangmao_marker_single_source():
    from mangpai.subjective import xiangmao
    assert callable(xiangmao.marker_descriptions)


# ─────────── 2. 行为等价（回归锁）───────────

def test_shishen_truth_table():
    """全干×全干真值表抽查（阴阳×五生克十式）。"""
    assert _shishen.shishen_of('甲', '甲') == '比肩'
    assert _shishen.shishen_of('甲', '乙') == '劫财'
    assert _shishen.shishen_of('甲', '丙') == '食神'
    assert _shishen.shishen_of('甲', '丁') == '伤官'
    assert _shishen.shishen_of('甲', '戊') == '偏财'
    assert _shishen.shishen_of('甲', '己') == '正财'
    assert _shishen.shishen_of('甲', '庚') == '七杀'
    assert _shishen.shishen_of('甲', '辛') == '正官'
    assert _shishen.shishen_of('甲', '壬') == '偏印'
    assert _shishen.shishen_of('甲', '癸') == '正印'
    # 边界：空/非法干返回 ''
    assert _shishen.shishen_of('', '甲') == ''
    assert _shishen.shishen_of('甲', '') == ''
    # bazi_calc.ten_god 严格契约：非法干抛 KeyError
    from mangpai.objective import bazi_calc
    assert bazi_calc.ten_god('甲', '庚') == '七杀'
    for bad in ('', 'X'):
        try:
            bazi_calc.ten_god(bad, '甲')
            raise AssertionError('ten_god 应抛 KeyError')
        except KeyError:
            pass


def test_cat_truth_table():
    pairs = {'比肩': '比劫', '劫财': '比劫', '食神': '食伤', '伤官': '食伤',
             '偏财': '财', '正财': '财', '七杀': '官杀', '正官': '官杀',
             '偏印': '印', '正印': '印'}
    for ss, cat in pairs.items():
        assert _shishen.shishen_cat(ss) == cat
    assert _shishen.shishen_cat('') == ''
    assert _shishen.shishen_cat('日主') == ''
    for d in WXS:
        for w in WXS:
            assert _shishen.wx_cat(d, w) in ('比劫', '印', '食伤', '财', '官杀')
    assert _shishen.wx_cat('', '') == ''
    assert _shishen.gan_wx_cat('甲', '金') == '官杀'
    assert _shishen.gan_wx_cat('', '金') == ''


def test_pair_in_truth_table():
    from mangpai.objective.constants import LIU_HE, LIU_CHONG
    assert _rel_utils.pair_in('子', '丑', LIU_HE)
    assert _rel_utils.pair_in('丑', '子', LIU_HE)
    assert not _rel_utils.pair_in('子', '午', LIU_HE)
    assert _rel_utils.pair_in('子', '午', LIU_CHONG)
    from mangpai.objective import muku
    assert muku._is_he('寅', '亥') and not muku._is_he('寅', '申')
    assert muku._is_chong('寅', '申') and muku._is_xing('子', '卯')


def test_ensure_behavior():
    """缺省自调 + 透传 + 守卫三态。"""
    rel = _sub_utils.ensure_relations('甲', ['甲', '丙', '戊', '庚'],
                                      ['子', '午', '卯', '酉'], None)
    assert isinstance(rel, dict) and rel.get('work_actions')
    sentinel = {'x': 1}
    assert _sub_utils.ensure_relations('甲', [], [], sentinel) is sentinel
    assert _sub_utils.ensure_relations('', [], [], None) == {}
    mk = _sub_utils.ensure_muku(['甲', '丙', '戊', '庚'],
                                ['丑', '辰', '未', '戌'], None)
    assert isinstance(mk, dict)
    assert _sub_utils.ensure_muku([], [], sentinel) is sentinel
    assert _sub_utils.ensure_muku([], ['子'], None) == {}


def test_detect_relations_golden():
    """盘 A/B work_actions 黄金摘要（H-fix-4b 注册表化前捕获）。"""
    from mangpai.objective.zuogong_detect import detect_relations
    rA = detect_relations('甲', '卯', '庚', '丑', '丙', '午', '壬', '子')
    sA = json.dumps(rA['work_actions'], ensure_ascii=False)
    assert len(rA['work_actions']) == 15
    assert hashlib.sha256(sA.encode()).hexdigest()[:16] == 'f3f81dbc62d0d639'
    rB = detect_relations('丙', '寅', '甲', '丑', '庚', '申', '戊', '戌')
    sB = json.dumps(rB['work_actions'], ensure_ascii=False)
    assert len(rB['work_actions']) == 12
    assert hashlib.sha256(sB.encode()).hexdigest()[:16] == 'd4d846a1eb8b0227'
