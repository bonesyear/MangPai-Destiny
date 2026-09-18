# -*- coding: utf-8 -*-
"""L1 C3 快照卫生校验（哨兵纪律：含反向构造用例）。

快照链是审计证据（H-fix-8 建 LATEST 指针/`--baseline latest` 机制）。
指针误推、meta 腐化、rubric_version 漂移此前无自动闸，本测试常驻防护：

1. LATEST 指针可解且指向存在的在链快照；
2. 在链快照（snapshots/ 根目录，archive/ 归档无引用不入链口径）全部
   `_meta` 完整（git_sha / rubric_version / note 非空）；
3. LATEST 指向的基线快照 rubric_version == blind_eval.RUBRIC_VERSION
   （历史快照保留各自 rubric 版本不强制）；
4. 命名规范 `YYYYMMDD_<批>.json`。

反向用例（test_hygiene_catches_bad_dir）在 tmp 目录构造坏 meta/坏指针/
坏命名，证明校验器能抓红。
"""
import json
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_HELDOUT = os.path.join(_HERE, 'heldout')
for p in (_HERE, _HELDOUT):
    if p not in sys.path:
        sys.path.insert(0, p)

import blind_eval  # noqa: E402

SNAP_DIR = os.path.join(_HELDOUT, 'snapshots')
_NAME_RE = re.compile(r'^\d{8}_[a-z0-9]+\.json$')
_META_KEYS = ('git_sha', 'rubric_version', 'note')


def _check_dir(snap_dir):
    """对单个快照目录跑全部校验，返回问题列表（空=绿）。"""
    problems = []
    ptr = os.path.join(snap_dir, 'LATEST')
    latest_name = None
    if not os.path.isfile(ptr):
        problems.append('LATEST 指针不存在')
    else:
        with open(ptr, encoding='utf-8') as f:
            latest_name = f.read().strip()
        if not latest_name:
            problems.append('LATEST 指针为空')
        elif not os.path.isfile(os.path.join(snap_dir, latest_name)):
            problems.append(f'LATEST 指向不存在的快照：{latest_name}')

    snap_names = [n for n in os.listdir(snap_dir) if n.endswith('.json')]
    if not snap_names:
        problems.append('无在链快照')
    for name in sorted(snap_names):
        if not _NAME_RE.match(name):
            problems.append(f'命名不规范：{name}')
        with open(os.path.join(snap_dir, name), encoding='utf-8') as f:
            data = json.load(f)
        meta = data.get('_meta')
        if not isinstance(meta, dict):
            problems.append(f'{name} 缺 _meta')
            continue
        for k in _META_KEYS:
            if not meta.get(k):
                problems.append(f'{name} _meta.{k} 缺失或为空')

    if latest_name and latest_name in snap_names:
        with open(os.path.join(snap_dir, latest_name), encoding='utf-8') as f:
            latest_meta = json.load(f).get('_meta') or {}
        if latest_meta.get('rubric_version') != blind_eval.RUBRIC_VERSION:
            problems.append(
                f'基线 {latest_name} rubric={latest_meta.get("rubric_version")} '
                f'!= 当前 {blind_eval.RUBRIC_VERSION}')
    return problems


def test_snapshot_chain_hygiene():
    problems = _check_dir(SNAP_DIR)
    assert problems == [], '快照链卫生问题：' + '; '.join(problems)


def test_hygiene_catches_bad_dir(tmp_path):
    """反向哨兵：坏 meta/坏指针/坏命名/坏 rubric 必须被抓到。"""
    d = tmp_path / 'snapshots'
    d.mkdir()
    (d / 'LATEST').write_text('nonexistent.json\n', encoding='utf-8')
    (d / '20260918_bad.json').write_text(json.dumps({'_meta': {
        'git_sha': '', 'rubric_version': 'v8-20260808', 'note': 'x'}}),
        encoding='utf-8')
    (d / 'badname.json').write_text(json.dumps({'_meta': {
        'git_sha': 'abc', 'rubric_version': 'v8-20260808', 'note': 'x'}}),
        encoding='utf-8')
    problems = _check_dir(str(d))
    blob = '; '.join(problems)
    assert 'LATEST 指向不存在的快照' in blob
    assert 'git_sha 缺失或为空' in blob
    assert '命名不规范：badname.json' in blob

    # 坏 rubric：LATEST 指向真实存在但版本漂移的快照
    (d / 'LATEST').write_text('20260918_bad.json\n', encoding='utf-8')
    (d / '20260918_bad.json').write_text(json.dumps({'_meta': {
        'git_sha': 'abc', 'rubric_version': 'v0-old', 'note': 'x'}}),
        encoding='utf-8')
    problems = _check_dir(str(d))
    assert any('rubric=v0-old' in p for p in problems), problems
