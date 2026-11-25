# -*- coding: utf-8 -*-
"""批次28A：评测输入、快照与集合完整性。"""
import json
import os
import sys

import pytest
import yaml

_HERE = os.path.dirname(os.path.abspath(__file__))
_HELDOUT = os.path.join(_HERE, 'heldout')
for _p in (_HELDOUT, os.path.join(_HERE, 'backtest')):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import blind_eval
import verify_heldout


def _case(**changes):
    case = {
        'id': 'synthetic',
        'bazi': {'year': '甲子', 'month': '丙寅', 'day': '庚午', 'hour': '丁亥'},
        'gender': '男',
        'verdicts': {},
    }
    case.update(changes)
    return case


def test_f109_single_stem_is_stem_and_missing_year_stays_missing():
    stem = blind_eval._bazi_data(_case(dayun='丙', liunian='辛未'))
    dayun = stem['dayun']['dayun'][0]
    assert dayun['gan'] == '丙'
    assert dayun.get('zhi', '') == ''
    assert 'year' not in stem['input']
    assert 'year' not in stem['liunian'][0]

    branch = blind_eval._bazi_data(_case(dayun='亥'))['dayun']['dayun'][0]
    assert branch['zhi'] == '亥'
    assert branch.get('gan', '') == ''


def test_f109_invalid_dayun_is_rejected_by_shared_input_path():
    with pytest.raises(ValueError, match='大运'):
        blind_eval._bazi_data(_case(dayun='壬卯'))
    assert '大运' in verify_heldout.check_case(_case(dayun='壬卯'))
    assert verify_heldout.check_case(_case(dayun='丙')) == ''


def test_a102_calib_and_trainset_use_same_case_facts():
    calib = {c['id']: c for c in yaml.safe_load(
        open(os.path.join(_HERE, 'calib_assertions.yaml'), encoding='utf-8'))['cases']}
    train = {c['id']: c for c in yaml.safe_load(
        open(os.path.join(_HERE, 'trainset', 'cases.yaml'), encoding='utf-8'))}
    for cid, source in calib.items():
        if cid not in train:
            continue
        target = train[cid]
        assert target['bazi'] == {
            'year': source['gans'][0] + source['zhis'][0],
            'month': source['gans'][1] + source['zhis'][1],
            'day': source['gans'][2] + source['zhis'][2],
            'hour': source['gans'][3] + source['zhis'][3],
        }, cid
        source_dayun = ''.join(source['dayun']) if isinstance(source.get('dayun'), list) else source.get('dayun')
        source_liunian = ''.join(source['liunian'][:2]) if isinstance(source.get('liunian'), list) else source.get('liunian')
        assert target.get('dayun') == source_dayun, cid
        assert target.get('liunian') == source_liunian, cid


def test_a100_significance_is_paired_and_reports_lost_gained(capsys):
    before = {f'c{i}': {'scores': {'财命': '✅'}} for i in range(10)}
    after = {f'c{i}': {'scores': {'财命': '❌' if i < 6 else '✅'}}
             for i in range(10)}
    blind_eval._print_significance({'heldout': before}, {'heldout': after})
    text = capsys.readouterr().out
    assert 'McNemar' in text
    assert 'lost=6' in text and 'gained=0' in text
    assert '显著退化' in text


def test_a103_snapshot_requires_complete_meta_and_rescore_preserves_rubric(
        tmp_path, monkeypatch):
    for meta in ({}, {'git_sha': 'abc', 'rubric_version': 'v0-old', 'note': ''}):
        with pytest.raises(ValueError):
            blind_eval._validate_snapshot({
                'trainset': {'x': {}}, '_meta': meta})

    source = tmp_path / '20261103_old.json'
    source.write_text(json.dumps({
        'trainset': {'driver-case': {
            'verdict_labels': {'职业': '司机·开车运输'},
            'engine': {'zhiye_primary': 'driver'}, 'scores': {},
        }},
        '_meta': {'git_sha': 'abc', 'rubric_version': 'v0-old', 'note': 'old'},
    }), encoding='utf-8')
    output = tmp_path / '20261124_batch28a.json'
    monkeypatch.setattr(sys, 'argv', [
        'blind_eval.py', '--rescore', str(source), '--out', str(output)])
    blind_eval.main()
    data = json.loads(output.read_text(encoding='utf-8'))
    assert data['_meta']['rubric_version'] == 'v0-old'
    assert data['_meta']['zhiye_rubric_version'] == blind_eval.RUBRIC_VERSION
    assert data['_meta']['note']
    assert data['trainset']['driver-case']['scores']['职业'] == '✅'


def test_f110_full_engine_hash_feeds_jitter_and_worktree_meta(monkeypatch):
    left = {'summary': 'same', 'unordered': {'b', 'a'}}
    right = {'summary': 'same', 'unordered': {'a', 'b'}}
    assert blind_eval._engine_hash(left) == blind_eval._engine_hash(right)
    changed = blind_eval._engine_hash({'summary': 'different'})
    assert changed != blind_eval._engine_hash(left)

    before = {'case': {'scores': {}, 'engine': {}, 'engine_sha256': 'old'}}
    after = {'case': {'scores': {}, 'engine': {}, 'engine_sha256': changed}}
    jitter = blind_eval._jitter(before, after)
    assert len(jitter) == 1 and 'engine_sha256' in jitter[0][1]
    import subprocess
    monkeypatch.setattr(subprocess, 'run', lambda *args, **kwargs:
                        subprocess.CompletedProcess(args[0], 0, stdout=' M mangpai/subjective/zhengfan.py\n'))
    meta = blind_eval._worktree_meta()
    assert meta['dirty'] is True
    assert meta['tree_hash']


def test_f106_eval_rejects_unexpected_case_count(tmp_path):
    path = tmp_path / 'heldout' / 'cases.yaml'
    path.parent.mkdir()
    path.write_text(yaml.dump([_case()], allow_unicode=True, sort_keys=False),
                    encoding='utf-8')
    with pytest.raises(ValueError, match='例数'):
        blind_eval.eval_cases(str(path))


def _four_pillars_key(case):
    b = case['bazi']
    return ''.join(b[p][0] for p in ('year', 'month', 'day', 'hour')), \
        ''.join(b[p][1] for p in ('year', 'month', 'day', 'hour'))


def test_f105_contamination_ignores_gender_and_heldout_is_disjoint():
    import curate
    from famous_cases import FAMOUS

    gans = ['乙', '丁', '乙', '己']
    zhis = ['未', '亥', '丑', '卯']
    assert curate.key_of(gans, zhis, '男') == curate.key_of(gans, zhis, '女')
    contaminated = curate.contaminated()
    assert contaminated[curate.key_of(gans, zhis)] == 'famous:慈禧'

    held = yaml.safe_load(open(os.path.join(_HELDOUT, 'cases.yaml'), encoding='utf-8'))
    train = yaml.safe_load(open(os.path.join(_HERE, 'trainset', 'cases.yaml'), encoding='utf-8'))
    held_keys = {_four_pillars_key(c) for c in held}
    assert held_keys.isdisjoint({_four_pillars_key(c) for c in train})
    famous_keys = {(''.join(g), ''.join(z)) for _name, g, z, *_rest in FAMOUS}
    assert held_keys.isdisjoint(famous_keys)
    assert len(held) == 214
    assert len(train) == 295


def _build_fixture(tmp_path, monkeypatch, cid):
    import build_yaml

    root = tmp_path / 'pipeline'
    (root.parent / 'trainset').mkdir(parents=True)
    root.mkdir()
    (root / 'merged.json').write_text('[]', encoding='utf-8')
    case = _case(id=cid, verdicts={'财命': '富·合成案例'})
    (root.parent / 'trainset' / 'cases.yaml').write_text(
        yaml.dump([case], allow_unicode=True, sort_keys=False), encoding='utf-8')
    (root / 'cases.yaml').write_text(
        yaml.dump([case], allow_unicode=True, sort_keys=False), encoding='utf-8')
    monkeypatch.setattr(build_yaml, 'HERE', str(root))
    monkeypatch.setattr(build_yaml, 'KEPT', {})
    monkeypatch.setattr(build_yaml, 'MANUAL', [])
    return root


def test_f106_build_preserves_manual_expansion_and_writes_backup(
        tmp_path, monkeypatch):
    import build_yaml

    root = _build_fixture(tmp_path, monkeypatch, 'cj-manual-expansion')
    build_yaml.main()
    cases = yaml.safe_load((root.parent / 'trainset' / 'cases.yaml').read_text(encoding='utf-8'))
    assert [c['id'] for c in cases] == ['cj-manual-expansion']
    assert (root.parent / 'trainset' / 'cases.yaml.bak').exists()


def test_f106_build_rejects_shrinking_pipeline_cases(tmp_path, monkeypatch):
    import build_yaml

    root = _build_fixture(tmp_path, monkeypatch, 'zhenbao-pipeline-case')
    path = root.parent / 'trainset' / 'cases.yaml'
    before = path.read_text(encoding='utf-8')
    with pytest.raises(SystemExit, match='缩水'):
        build_yaml.main()
    assert path.read_text(encoding='utf-8') == before
