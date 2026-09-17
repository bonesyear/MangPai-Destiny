# -*- coding: utf-8 -*-
"""H-fix-3 原子写批哨兵（先红后绿）。

- 原子写：写入中途失败（fsync/replace 抛异常）→ 目标文件完好、.tmp 残留
- 基线写回校验：非法 YAML/JSON、结构异常（条数不符/verdict 越域）→ 拒绝写入
- calib --write-baseline：端到端改写 + 旧版 .bak 留存 + 校验失败不破坏原文件
"""
import json
import os
import sys
from collections import Counter

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from _atomic_io import atomic_write, atomic_write_json  # noqa: E402
import calib_assertions  # noqa: E402


# ---------------------------------------------------------------- 原子写本体

def test_atomic_write_success(tmp_path):
    p = tmp_path / 'a.json'
    atomic_write(p, '{"x": 1}')
    assert p.read_text(encoding='utf-8') == '{"x": 1}'
    assert not (tmp_path / 'a.json.tmp').exists()  # 正常路径无 .tmp 残留


def test_atomic_write_failure_preserves_target(tmp_path, monkeypatch):
    """写入中途失败（fsync 抛 OSError）：原文件完好，.tmp 残留供排查。"""
    p = tmp_path / 'base.json'
    p.write_text('OLD', encoding='utf-8')
    monkeypatch.setattr(os, 'fsync',
                        lambda fd: (_ for _ in ()).throw(OSError('disk boom')))
    with pytest.raises(OSError):
        atomic_write(p, 'NEW')
    assert p.read_text(encoding='utf-8') == 'OLD'   # 目标未被破坏
    assert (tmp_path / 'base.json.tmp').exists()     # .tmp 残留
    # 恢复后仍可正常写
    monkeypatch.undo()
    atomic_write(p, 'NEW')
    assert p.read_text(encoding='utf-8') == 'NEW'


def test_atomic_write_replace_failure_preserves_target(tmp_path, monkeypatch):
    """replace 失败：原文件完好。"""
    p = tmp_path / 'base.json'
    p.write_text('OLD', encoding='utf-8')
    monkeypatch.setattr(os, 'replace',
                        lambda *a: (_ for _ in ()).throw(OSError('replace boom')))
    with pytest.raises(OSError):
        atomic_write(p, 'NEW')
    assert p.read_text(encoding='utf-8') == 'OLD'


def test_atomic_write_backup(tmp_path):
    """backup=True 覆盖已存在文件时留存 .bak。"""
    p = tmp_path / 'baseline.json'
    p.write_text('V1', encoding='utf-8')
    atomic_write(p, 'V2', backup=True)
    assert p.read_text(encoding='utf-8') == 'V2'
    assert (tmp_path / 'baseline.json.bak').read_text(encoding='utf-8') == 'V1'
    atomic_write(p, 'V3')  # 无 backup 不更新 .bak
    assert (tmp_path / 'baseline.json.bak').read_text(encoding='utf-8') == 'V1'


# ---------------------------------------------------------------- 写入前校验

def test_atomic_write_json_validate_rejects(tmp_path):
    """validate 回调抛错 → 拒绝写入，目标不产生/不破坏。"""
    p = tmp_path / 'b.json'
    with pytest.raises(ValueError, match='为空'):
        atomic_write_json(p, {}, validate=lambda d: (_ for _ in ()).throw(
            ValueError('baseline 为空，拒绝写入')) if not d else None)
    assert not p.exists()
    p.write_text('OLD', encoding='utf-8')
    with pytest.raises(ValueError):
        atomic_write_json(p, {'verdict': '可疑'}, validate=_strict_verdict)
    assert p.read_text(encoding='utf-8') == 'OLD'
    atomic_write_json(p, {'verdict': '✅'}, validate=_strict_verdict)
    assert json.loads(p.read_text(encoding='utf-8')) == {'verdict': '✅'}


def _strict_verdict(d):
    if d.get('verdict') not in ('✅', '⚠️', '❌'):
        raise ValueError('verdict 非法')


# ---------------------------------------------------------------- calib YAML 基线写回

_CALIB_MINI = """meta:
  baseline_counts: {✅: 0, ⚠️: 0, ❌: 1}
cases:
  - id: c1
    items:
      - {dim: 财命, gold: {direction: 破财, note: x}, baseline: ❌}
"""


def test_calib_validate_rejects_bad_yaml():
    """注入非法 YAML / 结构异常 → 拒绝写入（SystemExit）。"""
    with pytest.raises(SystemExit, match='反解析失败'):
        calib_assertions._validate_baseline_yaml('cases: [unclosed', 1)
    with pytest.raises(SystemExit, match='结构异常'):
        calib_assertions._validate_baseline_yaml('meta: {}\ncases: []', 1)
    with pytest.raises(SystemExit, match='结构异常'):
        calib_assertions._validate_baseline_yaml(_CALIB_MINI, 2)  # 条数不符
    calib_assertions._validate_baseline_yaml(_CALIB_MINI, 1)       # 合法通过


def test_calib_write_baseline_atomic(tmp_path, monkeypatch):
    """端到端：改写 baseline 行 + counts 同步 + 原子写 + .bak 留存。"""
    p = tmp_path / 'calib.yaml'
    p.write_text(_CALIB_MINI, encoding='utf-8')
    monkeypatch.setattr(calib_assertions, 'YAML_PATH', str(p))
    calib_assertions._write_baseline({('c1', '财命'): ('✅', 'ok')}, Counter({'✅': 1}))
    txt = p.read_text(encoding='utf-8')
    assert 'baseline: ✅}' in txt and 'baseline_counts: {✅: 1' in txt
    assert (tmp_path / 'calib.yaml.bak').read_text(encoding='utf-8') == _CALIB_MINI
    assert not (tmp_path / 'calib.yaml.tmp').exists()


def test_calib_write_baseline_refuses_broken_source(tmp_path, monkeypatch):
    """源 YAML 结构异常（正则匹配行数 != 计算项数）→ 拒绝写入，原文件不动。"""
    broken = _CALIB_MINI.replace('baseline: ❌}', 'baseline:❌}')  # 缺空格不匹配正则
    p = tmp_path / 'calib.yaml'
    p.write_text(broken, encoding='utf-8')
    monkeypatch.setattr(calib_assertions, 'YAML_PATH', str(p))
    with pytest.raises(SystemExit, match='YAML 结构异常'):
        calib_assertions._write_baseline({('c1', '财命'): ('✅', 'ok')}, Counter())
    assert p.read_text(encoding='utf-8') == broken  # 原文件未被破坏
