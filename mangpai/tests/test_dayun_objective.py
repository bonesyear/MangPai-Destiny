# -*- coding: utf-8 -*-
"""objective.dayun 检测层测试（M2 四项口径修复）。

锁定四项修复口径：
  a. 运干合/克日干（日主自身）跳过——原 L81-82 死 pass 从未生效；
  b. 戊刃取段氏全刃表（午、未双刃），shensha/dayun/yunfan 单一事实源；
  c. 墓库冲/刑+透干引拔才开库（与 objective.muku 同口径），无透干闭而不开；
  d. 天干五合只合不化，不再附化气字段（初级:2663）。

口径备案（F19）：11 测全为自建盘、锁 M2 修复自洽口径，零书例锚（批5 测试
缺口记录）。a-d 四口径本身各有上游书锚（见 objective/dayun.py docstring），
本文件盘例为工程构造非书例原造；书例锚（冲开财库吉运 gaoji:17400-17414、
到禄/到刃书例）未入断言——备案 KB §6.5，不硬补。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.dayun import _analyze_pillar_interaction
from mangpai.objective.shensha import compute_shensha_ext, _YANG_REN_FULL


# ── a. 日干跳过 ──

def test_dy_gan_vs_day_gan_skipped():
    """大运丁 vs 壬日主：丁壬合日主不入 gan_relations（日主关系由 tiyong 专管）。"""
    r = _analyze_pillar_interaction('丁', '亥', ['甲', '丙', '壬', '戊'],
                                    ['寅', '子', '午', '辰'], '壬')
    assert not any(x['type'] == '天干合' for x in r['gan_relations'])
    assert not any(x['target_pos'] == 'day_gan' for x in r['gan_relations'])


def test_dy_gan_vs_same_char_other_pillar_kept():
    """运干合他柱同字比肩星（非日主）仍保留：壬运合年干丁，跳过仅日干位。"""
    r = _analyze_pillar_interaction('壬', '戌', ['丁', '丙', '丁', '戊'],
                                    ['卯', '子', '酉', '辰'], '丁')
    assert any(x['type'] == '天干合' and x['target_pos'] == 'year_gan'
               for x in r['gan_relations'])
    assert not any(x['target_pos'] == 'day_gan' for x in r['gan_relations'])


# ── b. 戊刃双刃（段氏「戊刃在午、未」）──

def test_wu_blade_wei_dayun():
    """戊日主，大运未 → 羊刃位（段氏双刃之二）。"""
    r = _analyze_pillar_interaction('戊', '未', ['甲', '丙', '戊', '庚'],
                                    ['寅', '子', '午', '辰'], '戊')
    assert r['lu_blade'] and r['lu_blade']['type'] == '羊刃'
    assert '未' in r['lu_blade']['desc']


def test_wu_blade_wu_dayun():
    """戊日主，大运午 → 羊刃位（主刃）。"""
    r = _analyze_pillar_interaction('戊', '午', ['甲', '丙', '戊', '庚'],
                                    ['寅', '子', '丑', '辰'], '戊')
    assert r['lu_blade'] and r['lu_blade']['type'] == '羊刃'


def test_shensha_wu_blade_full_table():
    """shensha 羊刃：zhi 主刃位单值（旧契约），zhi_all 双刃，in_pillars 任一落柱。"""
    ss = compute_shensha_ext('戊', ['寅', '子', '未', '辰'])
    yr = ss['羊刃']
    assert yr['zhi'] == '午'
    assert yr['zhi_all'] == ['午', '未']
    assert yr['in_pillars']  # 未在日支 → 命中
    assert _YANG_REN_FULL['戊'] == ['午', '未']


# ── c. 墓库冲/刑+透干才开 ──

def test_tomb_chong_with_tougan_opens():
    """戌冲辰（水库）+ 壬透干 → 开库，tou_gan 含水。"""
    r = _analyze_pillar_interaction('戊', '戌', ['甲', '丙', '庚', '壬'],
                                    ['寅', '子', '午', '辰'], '庚')
    opens = r['tomb_effect']['opens']
    assert opens and '水' in opens[0]['tou_gan']
    assert '透干引拔而开' in opens[0]['desc']


def test_tomb_chong_without_tougan_closed():
    """戌冲辰无透干 → 闭而不开（旧版「冲即开库」口径已废）。"""
    r = _analyze_pillar_interaction('戊', '戌', ['甲', '丙', '庚', '辛'],
                                    ['寅', '子', '午', '辰'], '庚')
    assert not r['tomb_effect']['opens']
    assert any('闭而不开' in c['desc'] for c in r['tomb_effect']['closes'])


def test_tomb_xing_with_tougan_opens():
    """未刑戌（火库）+ 丙透干 → 刑开库（与 muku 冲/刑皆开同口径）。"""
    r = _analyze_pillar_interaction('己', '未', ['丙', '庚', '壬', '甲'],
                                    ['戌', '申', '子', '寅'], '壬')
    opens = r['tomb_effect']['opens']
    assert opens and opens[0].get('open_kind') == '刑'
    assert '火' in opens[0]['tou_gan']


def test_tomb_he_closes_unchanged():
    """酉合辰 → 合闭墓库（既有行为不变）。"""
    r = _analyze_pillar_interaction('丁', '酉', ['甲', '丙', '庚', '壬'],
                                    ['寅', '子', '午', '辰'], '庚')
    assert any('合闭' in c['desc'] for c in r['tomb_effect']['closes'])


# ── d. 天干只合不化 / 拱局 ──

def test_gan_he_has_no_hua_annotation():
    """初级:2663 只讲合不讲化：辰月也不附加合化字段或文案。"""
    r = _analyze_pillar_interaction('己', '丑', ['甲', '丙', '庚', '壬'],
                                    ['寅', '辰', '午', '子'], '庚')
    he = [x for x in r['gan_relations'] if x['type'] == '天干合']
    assert he and 'hua' not in he[0]
    assert '化' not in he[0]['desc']


def test_gan_he_without_month_still_has_no_hua():
    r = _analyze_pillar_interaction('己', '丑', ['甲', '丙', '庚', '壬'],
                                    ['寅', '子', '午', '辰'], '庚')
    he = [x for x in r['gan_relations'] if x['type'] == '天干合']
    assert he and 'hua' not in he[0]
    assert '化' not in he[0]['desc']


def test_sheng_mu_pair_is_gongju_not_banhe():
    """理象学:2498 亥未拱木，不把生墓两端误报为半合。"""
    r = _analyze_pillar_interaction('己', '未', ['甲', '丙', '庚', '壬'],
                                    ['亥', '子', '午', '辰'], '庚')
    gong = [x for x in r['zhi_relations'] if x['type'] == '拱局']
    assert len(gong) == 1 and gong[0]['target'] == '亥'
    assert '拱木局' in gong[0]['desc']
    assert not any(x['type'] == '半合' and x.get('target') == '亥'
                   for x in r['zhi_relations'])


def test_po_and_noncore_xing_do_not_create_work_type():
    r = _analyze_pillar_interaction('辛', '卯', ['壬', '壬', '庚', '壬'],
                                    ['子', '亥', '寅', '卯'], '庚')
    po = [x for x in r['zhi_relations'] if x['type'] == '破']
    xing = [x for x in r['zhi_relations'] if x['type'] == '刑']
    assert po and all(x.get('relation_only') for x in po + xing)
    assert '制用' not in r['work_types']
