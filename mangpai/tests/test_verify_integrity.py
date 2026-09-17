# -*- coding: utf-8 -*-
"""H-fix-2c 验证脚本可信度哨兵：注入引擎异常 → 验证脚本必须显式失败（防假 green）。

覆盖 H7/H9 标记的验证基建吞异常点：
  - blind_eval.py eval_cases：引擎异常 → 记 error + main() 退出码非 0
  - verify_layer3_checkpoint.py B 环节：analyze_guanming 异常 → 退出码非 0
    （旧版静默置 {}，未被下游断言覆盖的案例（如第1期）失败也可假绿）
  - calib_zhenbao.py 顶层循环：案例失败 → 打印后 re-raise（H12 P1）
  - verify_heldout.py：排盘异常 → 计失败、退出码 1（既已合规，本测试锁回归）
"""
import os
import runpy
import sys

import pytest
import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_HERE, 'heldout'))

import blind_eval  # noqa: E402
from mangpai.engine import MangpaiEngine  # noqa: E402

_LAYER3 = os.path.join(_REPO, 'mangpai', 'verify_layer3_checkpoint.py')
_CALIB = os.path.join(_REPO, 'mangpai', 'calib_zhenbao.py')
_VERIFY_HELDOUT = os.path.join(_HERE, 'heldout', 'verify_heldout.py')


def _boom(self):
    raise RuntimeError('injected engine failure')


def test_blind_eval_engine_error_recorded(tmp_path, monkeypatch):
    """eval_cases：引擎异常记入快照 error 字段（不静默丢弃）。"""
    monkeypatch.setattr(MangpaiEngine, 'compute_all', _boom)
    p = tmp_path / 'cases.yaml'
    p.write_text(yaml.dump([{
        'id': 'inj-1',
        'bazi': {'year': '甲子', 'month': '乙丑', 'day': '丙寅', 'hour': '丁卯'},
        'gender': '男', 'year': 1960,
    }], allow_unicode=True), encoding='utf-8')
    out = blind_eval.eval_cases(str(p))
    assert 'error' in out['inj-1']
    assert 'injected engine failure' in out['inj-1']['error']


def test_blind_eval_engine_error_exit_nonzero(monkeypatch):
    """blind_eval main：任一案例引擎异常 → 退出码 1（CI 不得误绿）。"""
    monkeypatch.setattr(MangpaiEngine, 'compute_all', _boom)
    monkeypatch.setattr(sys, 'argv', ['blind_eval.py', '--trainset-only'])
    with pytest.raises(SystemExit) as exc:
        blind_eval.main()
    assert exc.value.code == 1


def test_verify_layer3_compute_error_exit_nonzero(monkeypatch):
    """verify_layer3_checkpoint A 环节：compute_all 异常 → 退出码非 0。"""
    monkeypatch.setattr(MangpaiEngine, 'compute_all', _boom)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(_LAYER3, run_name='__main__')
    assert exc.value.code != 0


def test_verify_layer3_guanming_error_exit_nonzero(monkeypatch):
    """verify_layer3_checkpoint B 环节：analyze_guanming 对未被下游断言覆盖的
    案例（第1期）异常 → 旧版静默置 {} 假绿（exit 0），新版必须 exit != 0。"""
    import mangpai.subjective.guanming as gm_mod
    real = gm_mod.analyze_guanming

    def selective(day_gan, gans, zhis, **kw):
        if list(gans) == ['戊', '己', '乙', '丁']:  # 第1期·生孩子/官司/职业
            raise RuntimeError('injected guanming failure')
        return real(day_gan, gans, zhis, **kw)

    monkeypatch.setattr(gm_mod, 'analyze_guanming', selective)
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(_LAYER3, run_name='__main__')
    assert exc.value.code != 0


def test_calib_zhenbao_case_failure_raises(monkeypatch):
    """calib_zhenbao：案例引擎异常 → 打印 case id 后 re-raise（不再静默继续）。"""
    monkeypatch.setattr(MangpaiEngine, 'compute_all', _boom)
    with pytest.raises(RuntimeError, match='injected engine failure'):
        runpy.run_path(_CALIB, run_name='__main__')


def test_verify_heldout_compute_error_exit_nonzero(monkeypatch):
    """verify_heldout：排盘异常 → 计失败、退出码 1（既已合规，锁回归）。"""
    monkeypatch.setattr(MangpaiEngine, 'compute_all', _boom)
    monkeypatch.setattr(sys, 'argv', ['verify_heldout.py', '--trainset'])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path(_VERIFY_HELDOUT, run_name='__main__')
    assert exc.value.code == 1
