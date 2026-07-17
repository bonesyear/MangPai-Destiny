"""属性化测试（V7）：随机八字不崩溃 + 引擎输出不变量。

两类随机输入：
  - 合法四柱：60 甲子随机抽 4 柱（干支阴阳相配，贴近真实排盘）；
  - 应力四柱：天干/地支各自随机（阴阳可错配，压测容错路径）。

不变量：
  1. MangpaiEngine.compute_all() 不抛异常；
  2. gongliang.level ∈ [0, 5]、zuogong.work_level ∈ [0, 5]（存在时）；
  3. 十神值全部合法（十神集合 + 日主）；
  4. 空亡为 2 个合法地支；
  5. summary 为字符串；
  6. 同一输入两次计算关键结果确定（level/summary 一致）。
"""
import random
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai import MangpaiEngine
from mangpai.objective.bazi_calc import compute_shishen, get_kong_wang, GAN
from mangpai.objective.constants import DI_ZHI

TIAN_GAN = list(GAN)  # GAN 为字符串 '甲乙丙丁戊己庚辛壬癸'

# 60 甲子（阳干配阳支、阴干配阴支）
JIAZI = [TIAN_GAN[i % 10] + DI_ZHI[i % 12] for i in range(60)]

LEGAL_SHISHEN = {
    '比肩', '劫财', '食神', '伤官', '正财', '偏财',
    '正官', '七杀', '正印', '偏印', '日主',
}

_N = 50  # 每类随机样本数（种子固定，结果可复现；控制全套 pytest 时长）


def _mk_bazi_data(y_gz, m_gz, d_gz, h_gz):
    return {
        'input': {'year': 1990},
        'bazi': {'year': y_gz, 'month': m_gz, 'day': d_gz, 'hour': h_gz},
        'shishen': compute_shishen(d_gz[0], y_gz, m_gz, d_gz, h_gz),
        'kong_wang': get_kong_wang(d_gz[0], d_gz[1]),
        'di_zhi_relations': {},
    }


def _assert_invariants(bd):
    """单命例全量不变量断言。返回 result 供确定性比对。"""
    r = MangpaiEngine(bd).compute_all()
    assert isinstance(r, dict)

    # 十神合法（输入侧断言：构造的 shishen 本身须在合法集内）
    for k, v in bd['shishen'].items():
        assert v in LEGAL_SHISHEN, f'{k}={v} 非法十神'

    # 空亡：2 个合法地支
    kw = bd['kong_wang'].get('zhi', [])
    assert len(kw) == 2 and all(z in DI_ZHI for z in kw)

    # 层功 level ∈ [0,5]
    gl = r.get('gongliang')
    if isinstance(gl, dict) and gl.get('level') is not None:
        assert 0 <= gl['level'] <= 5, f"gongliang.level={gl['level']} 越界"

    # 做功 work_level ∈ [0,5]
    zg = r.get('zuogong')
    if isinstance(zg, dict) and zg.get('work_level') is not None:
        assert 0 <= zg['work_level'] <= 5, f"work_level={zg['work_level']} 越界"

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


def test_random_jiazi_no_crash_and_invariants():
    """60 甲子随机四柱：不崩溃 + 全量不变量。"""
    for y, m, d, h in _random_jiazi_charts(_N, seed=20260717):
        _assert_invariants(_mk_bazi_data(y, m, d, h))


def test_random_stress_no_crash_and_invariants():
    """干支错配应力四柱：不崩溃 + 全量不变量。"""
    for y, m, d, h in _random_stress_charts(_N, seed=20260717):
        _assert_invariants(_mk_bazi_data(y, m, d, h))


def test_edge_charts_no_crash():
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
        _assert_invariants(_mk_bazi_data(y, m, d, h))


def test_deterministic_repeat():
    """同一输入两次计算：level 与 summary 完全一致。"""
    for y, m, d, h in _random_jiazi_charts(10, seed=42):
        bd = _mk_bazi_data(y, m, d, h)
        r1 = _assert_invariants(bd)
        r2 = _assert_invariants(bd)
        assert r1.get('gongliang', {}).get('level') == r2.get('gongliang', {}).get('level')
        assert r1.get('zuogong', {}).get('work_level') == r2.get('zuogong', {}).get('work_level')
        assert r1.get('summary') == r2.get('summary')


@pytest.mark.parametrize('gz', JIAZI)
def test_every_jiazi_as_day_pillar(gz):
    """60 甲子逐一作日柱（穷尽日主×日支组合）：不崩溃。"""
    bd = _mk_bazi_data('甲子', '丙寅', gz, '庚午')
    r = MangpaiEngine(bd).compute_all()
    assert isinstance(r, dict)
    gl = r.get('gongliang')
    if isinstance(gl, dict) and gl.get('level') is not None:
        assert 0 <= gl['level'] <= 5
