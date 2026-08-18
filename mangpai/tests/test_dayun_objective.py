# -*- coding: utf-8 -*-
"""objective.dayun 检测层测试（M2 四项口径修复）。

锁定四项修复口径：
  a. 运干合/克日干（日主自身）跳过——原 L81-82 死 pass 从未生效；
  b. 戊刃取段氏全刃表（午、未双刃），shensha/dayun/yunfan 单一事实源；
  c. 墓库冲/刑+透干引拔才开库（与 objective.muku 同口径），无透干闭而不开；
  d. 天干合化气须验月令（化气五行当令方论化），与 zuogong_detect 合化 gate 同口径。

口径备案（F19）：11 测全为自建盘、锁 M2 修复自洽口径，零书例锚（批5 测试
缺口记录）。a-d 四口径本身各有上游书锚（见 objective/dayun.py docstring），
本文件盘例为工程构造非书例原造；书例锚（冲开财库吉运 gaoji:17400-17414、
到禄/到刃书例）未入断言——备案 KB §6.5，不硬补。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.dayun import _analyze_pillar_interaction, _check_hua
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


# ── d. 化气验月令 ──

def test_hua_requires_month_command():
    """甲己合：辰月（土当令）化土；子月（水）不化；无月令不标化。"""
    assert _check_hua('甲', '己', '辰') == '土'
    assert _check_hua('甲', '己', '子') == ''
    assert _check_hua('甲', '己', '') == ''


def test_hua_in_gan_relations_respects_month():
    """运干合化气经 relations 透出时同样验月令（辰月标化土，子月不标）。"""
    r = _analyze_pillar_interaction('己', '丑', ['甲', '丙', '庚', '壬'],
                                    ['寅', '辰', '午', '子'], '庚')
    he = [x for x in r['gan_relations'] if x['type'] == '天干合']
    assert he and he[0].get('hua') == '土'
    r2 = _analyze_pillar_interaction('己', '丑', ['甲', '丙', '庚', '壬'],
                                     ['寅', '子', '午', '辰'], '庚')
    he2 = [x for x in r2['gan_relations'] if x['type'] == '天干合']
    assert he2 and not he2[0].get('hua')
