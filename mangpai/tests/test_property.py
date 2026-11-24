"""属性化测试（V7）：随机八字不崩溃 + 引擎输出不变量。

两类随机输入：
  - 合法四柱：60 甲子随机抽 4 柱（干支阴阳相配，贴近真实排盘）；
  - 应力四柱：天干/地支各自随机（阴阳可错配，压测容错路径）。

不变量：
  1. MangpaiEngine.compute_all() 不抛异常；
  2. gongliang.level ∈ [0, 4]（G1：做功层次唯一事实源；zuogong 不再评层）；
  3. 十神值全部合法（十神集合 + 日主）；
  4. 空亡为 2 个合法地支；
  5. summary 为字符串；
  6. 同一输入两次计算关键结果确定（level/summary 一致）。
"""
import logging
import random
import sys
import os

import pytest


from mangpai import MangpaiEngine
from mangpai.engine import _MODULE_DEFAULTS
from mangpai.objective.bazi_calc import GAN
from mangpai.objective.constants import DI_ZHI

TIAN_GAN = list(GAN)  # GAN 为字符串 '甲乙丙丁戊己庚辛壬癸'

# 60 甲子（阳干配阳支、阴干配阴支）
JIAZI = [TIAN_GAN[i % 10] + DI_ZHI[i % 12] for i in range(60)]

LEGAL_SHISHEN = {
    '比肩', '劫财', '食神', '伤官', '正财', '偏财',
    '正官', '七杀', '正印', '偏印', '日主',
}

_N = 50  # 每类随机样本数（种子固定，结果可复现；控制全套 pytest 时长）
_AS_OF = '2026-07-01T12:00:00'


def _mk_bazi_data(y_gz, m_gz, d_gz, h_gz):
    return {
        'input': {'year': 1990, 'gender': '男'},
        'bazi': {'year': y_gz, 'month': m_gz, 'day': d_gz, 'hour': h_gz},
        'di_zhi_relations': {},
    }


def _assert_invariants(bd, caplog):
    """单命例全量不变量断言。返回 result 供确定性比对。"""
    caplog.clear()
    with caplog.at_level(logging.WARNING, logger='mangpai.engine'):
        engine = MangpaiEngine(bd, as_of=_AS_OF)
        r = engine.compute_all()
    assert isinstance(r, dict)
    assert '计算失败' not in caplog.text, f'引擎发生模块降级: {caplog.text}'

    for k, v in engine.shishen.items():
        assert v in LEGAL_SHISHEN, f'{k}={v} 非法十神'

    kw = r['kong_wang'].get('zhi', [])
    assert len(kw) == 2 and all(z in DI_ZHI for z in kw)
    for key in ('hunyin', 'liuqin', 'zinv', 'qianyi', 'xiangmao'):
        assert r.get(key) != _MODULE_DEFAULTS[key], f'{key} 返回降级默认值'

    # 层功 level ∈ [0,4]（G1：做功层次唯一事实源，0=无功）
    gl = r.get('gongliang')
    if isinstance(gl, dict) and gl.get('level') is not None:
        assert 0 <= gl['level'] <= 4, f"gongliang.level={gl['level']} 越界"

    # summary 为字符串
    assert isinstance(r.get('summary'), str)
    return r


def _random_jiazi_charts(n, seed):
    rng = random.Random(seed)
    return [(rng.choice(JIAZI), rng.choice(JIAZI),
             rng.choice(JIAZI), rng.choice(JIAZI)) for _ in range(n)]


def _random_stress_charts(n, seed):
    rng = random.Random(seed)
    return [(rng.choice(TIAN_GAN) + rng.choice(DI_ZHI),
             rng.choice(TIAN_GAN) + rng.choice(DI_ZHI),
             rng.choice(TIAN_GAN) + rng.choice(DI_ZHI),
             rng.choice(TIAN_GAN) + rng.choice(DI_ZHI)) for _ in range(n)]


def test_random_jiazi_no_crash_and_invariants(caplog):
    """60 甲子随机四柱：不崩溃 + 全量不变量。"""
    for y, m, d, h in _random_jiazi_charts(_N, seed=20260717):
        _assert_invariants(_mk_bazi_data(y, m, d, h), caplog)


def test_random_stress_no_crash_and_invariants(caplog):
    """干支错配应力四柱：不崩溃 + 全量不变量。"""
    for y, m, d, h in _random_stress_charts(_N, seed=20260717):
        _assert_invariants(_mk_bazi_data(y, m, d, h), caplog)


def test_edge_charts_no_crash(caplog):
    """极端结构命例：全伏吟/四库全/全阳/全阴/十天干日主轮转。"""
    edge = [
        ('甲子', '甲子', '甲子', '甲子'),   # 全伏吟
        ('戊辰', '戊戌', '己丑', '己未'),   # 四库全
        ('甲寅', '丙午', '戊申', '庚戌'),   # 全阳
        ('乙卯', '丁巳', '己未', '辛酉'),   # 全阴
        ('壬子', '壬子', '壬子', '壬子'),   # 天元一气+地支一气
    ]
    # 十天干各做一次日主
    for i, g in enumerate(TIAN_GAN):
        z = DI_ZHI[(i * 2) % 12]
        edge.append((JIAZI[(i * 6) % 60], JIAZI[(i * 6 + 13) % 60],
                     g + z, JIAZI[(i * 6 + 29) % 60]))
    for y, m, d, h in edge:
        _assert_invariants(_mk_bazi_data(y, m, d, h), caplog)


def test_deterministic_repeat(caplog):
    """同一输入两次计算：固定 as_of 后完整输出一致。"""
    for y, m, d, h in _random_jiazi_charts(10, seed=42):
        bd = _mk_bazi_data(y, m, d, h)
        r1 = _assert_invariants(bd, caplog)
        r2 = _assert_invariants(bd, caplog)
        assert r1 == r2


@pytest.mark.parametrize('gz', JIAZI)
def test_every_jiazi_as_day_pillar(gz, caplog):
    """60 甲子逐一作日柱（穷尽日主×日支组合）：不崩溃。"""
    bd = _mk_bazi_data('甲子', '丙寅', gz, '庚午')
    _assert_invariants(bd, caplog)


def test_invariants_detect_degraded_module(monkeypatch, caplog):
    import mangpai.engine as engine_mod

    def boom(*args, **kwargs):
        raise RuntimeError('injected property failure')

    monkeypatch.setattr(engine_mod, 'analyze_hunyin', boom)
    bd = _mk_bazi_data('甲子', '丙寅', '戊辰', '庚午')
    with pytest.raises(AssertionError, match='引擎发生模块降级'):
        _assert_invariants(bd, caplog)
