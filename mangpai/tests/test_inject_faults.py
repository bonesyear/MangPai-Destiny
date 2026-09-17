# -*- coding: utf-8 -*-
"""H-fix-2a 错误注入测试框架（哨兵纪律：先红后绿）。

参数化故障注入，逐注入点断言异常策略契约：
  - 非法输入 → 抛明确业务异常（EngineInputError / ValueError，带定位信息），
    禁止裸 ValueError('not in list')/IndexError/TypeError 穿透；
  - 可降级场景 → 安全降级返回明确默认值，禁止静默吞掉（except: pass）；
  - 关键路径模块异常 → EngineComputeError 传导，不得降级为 {} 隐瞒。

冒烟：calib 10 例全量 compute_all 不抛异常（正常路径回归兜底）。
"""
import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_HERE))
for p in (_HERE, _REPO_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

import yaml  # noqa: E402

from mangpai import MangpaiEngine  # noqa: E402
from mangpai.engine import EngineComputeError, EngineInputError  # noqa: E402
from mangpai.objective.bazi_calc import calc_bazi_full  # noqa: E402
from mangpai.objective.dayun import dayun_gz_sequence  # noqa: E402
from mangpai.objective.jiaoyun import _advance_gz  # noqa: E402
from mangpai.subjective.llm_backend import LLMBackendError, call_deepseek  # noqa: E402


def _valid_bazi_data(**over):
    bd = {
        'bazi': {'year': '戊辰', 'month': '己未', 'day': '庚午', 'hour': '丁亥'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': '男', 'year': 1988},
    }
    bd.update(over)
    return bd


# ---------------------------------------------------------------- 1. 非法干支

@pytest.mark.parametrize('year_gan,month_gz', [
    ('X', '甲子'),      # 非法天干
    ('甲甲', '甲子'),   # 多字天干
    ('', '甲子'),       # 空串
    ('甲', '甲甲'),     # 月柱支非法（甲非地支）
    ('甲', 'XX'),       # 月柱全非法
    ('甲', ''),         # 空月柱
    ('甲', '甲'),       # 月柱缺支
])
def test_dayun_gz_sequence_invalid_ganzhi(year_gan, month_gz):
    """非法干支输入 → 明确 ValueError（'非法'定位），禁止裸 index() 穿透。"""
    with pytest.raises(ValueError, match='非法'):
        dayun_gz_sequence(year_gan, month_gz, True)


def test_dayun_gz_sequence_valid_sanity():
    """合法输入行为不变：阳男顺排，甲子月 → 乙丑起。"""
    seq = dayun_gz_sequence('甲', '甲子', True)
    assert seq['direction'] == '顺'
    assert seq['dayun'][0]['gz'] == '乙丑'
    seq_r = dayun_gz_sequence('乙', '甲子', True)  # 阴男逆排
    assert seq_r['direction'] == '逆'
    assert seq_r['dayun'][0]['gz'] == '癸亥'


@pytest.mark.parametrize('gz', ['XX', '', '甲甲', '甲', '子丑'])
def test_advance_gz_invalid_ganzhi(gz):
    """_advance_gz 非法干支 → 明确 ValueError，禁止裸 index()/IndexError。"""
    with pytest.raises(ValueError, match='非法干支'):
        _advance_gz(gz, 1)


def test_advance_gz_valid_sanity():
    assert _advance_gz('甲子', 1) == '乙丑'
    assert _advance_gz('甲子', -1) == '癸亥'


def test_calc_bazi_full_entry_guards():
    """calc_bazi_full 入口校验（D2 既有守卫回归）：非法性别/界外年/非法经度。"""
    with pytest.raises(ValueError):
        calc_bazi_full(1990, 5, 15, 13, 30, '未知', 114.07)
    with pytest.raises(ValueError):
        calc_bazi_full(1800, 5, 15, 13, 30, '男', 114.07)
    with pytest.raises(ValueError):
        calc_bazi_full(1990, 5, 15, 13, 30, '男', None)


# ---------------------------------------------------------------- 2. 畸形 bazi_data

@pytest.mark.parametrize('bad', [None, 'not-a-dict', [], 42])
def test_engine_rejects_non_dict_bazi_data(bad):
    with pytest.raises(EngineInputError):
        MangpaiEngine(bad)


@pytest.mark.parametrize('bazi', [
    None,                                                   # bazi 非 dict
    {},                                                     # 空 bazi
    {'year': '甲子'},                                       # 缺键（缺月/日/时）
    {'year': 'XX', 'month': '丙寅', 'day': '庚子', 'hour': '午午'},   # 非法干支
    {'year': '甲甲', 'month': '丙寅', 'day': '庚子', 'hour': '壬午'},  # 支位非法干
    {'year': '甲子', 'month': '丙寅', 'day': '庚', 'hour': '壬午'},    # 单字柱
    {'year': 123, 'month': '丙寅', 'day': '庚子', 'hour': '壬午'},     # 非字符串
])
def test_engine_rejects_malformed_bazi(bazi):
    with pytest.raises(EngineInputError):
        MangpaiEngine({'bazi': bazi})


def test_engine_accepts_valid_minimal():
    """合法最小输入不受影响（缺 shishen/kong_wang 等可选键正常跑）。"""
    res = MangpaiEngine({'bazi': {'year': '戊辰', 'month': '己未',
                                  'day': '庚午', 'hour': '丁亥'}}).compute_all()
    assert isinstance(res, dict) and 'summary' in res


# ---------------------------------------------------------------- 3. 空 actions 降级

def test_compute_all_empty_work_actions_degrades(monkeypatch):
    """zuogong 返回空做功（无功盘语义）→ 全链安全降级：不崩、zhengfan 中立。"""
    import mangpai.engine as eng_mod
    monkeypatch.setattr(
        eng_mod, 'analyze_zuogong',
        lambda *a, **k: {'work_actions': [], 'work_types': []})
    res = MangpaiEngine(_valid_bazi_data()).compute_all()
    assert res['zhengfan']['type'] == 'neutral'
    assert 'summary' in res


def test_compute_all_critical_module_raises(monkeypatch):
    """关键路径模块抛异常 → EngineComputeError 传导，不得吞为 {}。"""
    import mangpai.engine as eng_mod

    def _boom(*a, **k):
        raise RuntimeError('injected bug')

    monkeypatch.setattr(eng_mod, 'analyze_zuogong', _boom)
    with pytest.raises(EngineComputeError, match='zuogong'):
        MangpaiEngine(_valid_bazi_data()).compute_all()


def test_compute_all_optional_module_degrades(monkeypatch):
    """可选模块抛异常 → warning + 明确默认值，主链不受影响。"""
    import mangpai.engine as eng_mod

    def _boom(*a, **k):
        raise RuntimeError('injected bug')

    monkeypatch.setattr(eng_mod, 'analyze_xiangmao', _boom)
    res = MangpaiEngine(_valid_bazi_data()).compute_all()
    assert res['xiangmao'] == {}        # 明确默认值，不是缺键也不是裸 or {}
    assert 'summary' in res             # 主链完好


# ---------------------------------------------------------------- 4. 越界/边界索引

def test_cand_hua_empty_list_guard():
    """_cand_hua 化用候选空列表越界（zuogong_confirm，backlog H2 条）。

    当前代码下 _hua_chengju 与 hua_actions 同过滤源、不可达越界；
    修复=同源复用+显式判空守卫（防御纵深）。本断言锁「化用路径正常返回」。
    """
    from mangpai.subjective.zuogong_confirm import analyze_zuogong
    # 化例三型（杀印相生+日干合）：化用成局候选路径必须完整走完
    res = analyze_zuogong('己', '巳', '甲', '子', '丙', '寅', '甲', '戌')
    assert isinstance(res, dict) and 'work_actions' in res


def test_current_dayun_end_age_none():
    """engine.py:179 end_age 显式 None → 旧码 TypeError 击穿 compute_all（P1）。"""
    eng = MangpaiEngine(_valid_bazi_data())
    dy = [{'gz': '甲子', 'start_age': 5, 'end_age': None},
          {'gz': '乙丑', 'start_age': 15, 'end_age': 25}]
    assert eng._current_dayun(dy) is not None


def test_compute_all_dayun_end_age_none():
    """da_yun 条目 end_age=None 注入 → compute_all 完整跑完不崩。"""
    bd = _valid_bazi_data(**{
        'da_yun': {'direction': '顺', 'start_age': 5,
                   'dayun': [{'gz': '庚申', 'start_age': 5, 'end_age': None}]},
    })
    res = MangpaiEngine(bd).compute_all()
    assert 'summary' in res


# ---------------------------------------------------------------- 5. JSONDecodeError 包装

class _FakeResp:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return self._body


def test_llm_backend_http200_non_json_wrapped(monkeypatch):
    """HTTP 200 但返回体非 JSON → LLMBackendError（明确异常），
    禁止裸 JSONDecodeError 穿透（H4 P0）。"""
    import urllib.request
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'fault-inject-key')
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda *a, **k: _FakeResp(b'<html>Bad Gateway</html>'))
    with pytest.raises(LLMBackendError, match='JSON'):
        call_deepseek('s', 'u', retries=0)


def test_llm_backend_http200_bad_utf8_wrapped(monkeypatch):
    """HTTP 200 但返回体非法 UTF-8 → 同样包装为 LLMBackendError。"""
    import urllib.request
    monkeypatch.setenv('DEEPSEEK_API_KEY', 'fault-inject-key')
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda *a, **k: _FakeResp(b'\xff\xfe\x00bad'))
    with pytest.raises(LLMBackendError):
        call_deepseek('s', 'u', retries=0)


# ---------------------------------------------------------------- 6. calib 冒烟

def test_calib_smoke_10_cases_no_crash():
    """calib 10 例全量 compute_all 冒烟：正常路径零异常（异常策略改造回归兜底）。"""
    import calib_assertions as ca
    with open(ca.YAML_PATH, encoding='utf-8') as f:
        doc = yaml.safe_load(f)
    cases = doc['cases']
    assert len(cases) >= 10
    for case in cases:
        out = ca.run_case(case)  # 内部 MangpaiEngine(...).compute_all() 全量
        assert isinstance(out, dict)
