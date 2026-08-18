# -*- coding: utf-8 -*-
"""修批B（fb）哨兵测试（先红后绿）——神煞 year_ref 并入 + calib 传 age。

R1/R2 审查 P1：F13 后 shensha 主键=reference 所定柱（默认日支），年支侧
命中在 year_ref 子键；消费方只读主键+day_ref → year-only 劫煞/亡神/灾煞
静默丢失（gaoji:7912「年支亦需同查」）。

实证盘：辛酉/辛丑/辛午/辛巳（zhis=[申,丑,午,巳] 型，下用 ['申','丑','午','巳']）——
  日支午→劫煞亥（不在局）；年支申→劫煞巳（落时柱）= year-only 劫煞；
  日支午→灾煞子（不在局）；年支申→灾煞午（落月柱）= year-only 灾煞。
  修前 zaihuo xiong_shen/xiong_sha 与 laoyu has_jiesha 全漏检（红）；
  修后并入 year_ref（绿）。
"""
import os
import sys

import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))

from mangpai.objective.shensha import compute_shensha_ext
from mangpai.subjective.zaihuo import detect_chehuo, detect_siwang
from mangpai.subjective.laoyu import detect_jiesha_wangshen
from mangpai.subjective.xiangfa_ops import _shensha_by_pillar

_GANS = ['辛', '辛', '辛', '辛']
_ZHIS = ['申', '丑', '午', '巳']  # 年支申→劫煞巳(时)/灾煞午(月)，日支午→劫煞亥/灾煞子(均不在局)


def test_zaihuo_chehuo_year_ref_jiesha():
    """zaihuo 车祸：year-only 劫煞（年支申→巳落时柱）须入 xiong_shen。"""
    r = detect_chehuo('辛', _GANS, _ZHIS)
    assert '劫煞' in r['xiong_shen']


def test_zaihuo_siwang_year_ref_sansha():
    """zaihuo 死亡：year-only 劫煞/灾煞须入 xiong_sha（凶性三煞）。"""
    r = detect_siwang('辛', _GANS, _ZHIS)
    assert '劫煞' in r['xiong_sha']
    assert '灾煞' in r['xiong_sha']


def test_laoyu_year_ref_jiesha():
    """laoyu 劫煞亡神：year-only 劫煞须检出 has_jiesha（gaoji:7912 年支同查）。"""
    r = detect_jiesha_wangshen('辛', _GANS, _ZHIS)
    assert r['has_jiesha']
    assert r['jiesha_zhi'] == '巳'


def test_xiangfa_shensha_by_pillar_subkeys():
    """xiangfa_ops 共象：_shensha_by_pillar 须并入 year_ref/day_ref 子键落柱。"""
    by_p = _shensha_by_pillar(compute_shensha_ext('辛', _ZHIS))
    assert '劫煞' in by_p['hour']  # year_ref 劫煞巳
    assert '灾煞' in by_p['day']  # year_ref 灾煞午（午=日支）


def test_calib_yingqi_age_daxian():
    """calib 应期：run_case 须传 age——daxian 定位柱不再恒空（has_daxian 恒
    False 旧口径，R1 P1）。取 calib 首例（1958 生，戊辰 1988 流年→age=30，
    大限落月柱）。"""
    sys.path.insert(0, _HERE)
    import calib_assertions as ca
    with open(ca.YAML_PATH, encoding='utf-8') as f:
        cases = yaml.safe_load(f)['cases']
    case = next(c for c in cases if c.get('liunian'))
    out = ca.run_case(case)
    assert out['yq']['daxian_yingqi']['active'] is not None
