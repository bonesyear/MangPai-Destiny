# -*- coding: utf-8 -*-
"""批次28B：回测与验证脚本可信度。"""
import json
import os
import subprocess
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKTEST = os.path.join(_HERE, 'backtest')
_HELDOUT = os.path.join(_HERE, 'heldout')
for _path in (_BACKTEST, _HELDOUT):
    if _path not in sys.path:
        sys.path.insert(0, _path)


def test_verify_all_shows_failure_and_continues_all_suites(tmp_path):
    fake_python = tmp_path / 'fake-python'
    fake_python.write_text(
        '#!/bin/bash\n'
        'if [[ "$1" == *verify_mangpai.py ]]; then\n'
        '  echo "验证结果: injected verify failure"\n'
        '  exit 1\n'
        'fi\n'
        'echo "called:$1 $2" >> "' + str(tmp_path / 'calls') + '"\n'
        'if [[ "$1" == "-m" && "$2" == "pytest" ]]; then echo "1939 passed"; exit 0; fi\n'
        'case "$1" in\n'
        '  *verify_*.py) echo "验证结果: 1 passed, 0 failed" ;;\n'
        '  *regression67.py|*regression_famous.py|*calib_assertions.py) echo "TOTAL: ✅1 ⚠️0 ❌0" ;;\n'
        '  *blind_eval.py) echo "文本抖动合计: 0" ;;\n'
        'esac\n'
        'exit 0\n', encoding='utf-8')
    fake_python.chmod(0o755)
    env = dict(os.environ, PYTHON=str(fake_python), PYTHONIOENCODING='utf-8')
    result = subprocess.run(
        ['bash', os.path.join(_HERE, 'backtest', 'verify_all.sh')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, timeout=30)
    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert 'injected verify failure' in output
    assert '=== 509 regression gate ===' in output
    calls = (tmp_path / 'calls').read_text(encoding='utf-8')
    assert 'regression_famous.py' in calls
    assert 'calib_assertions.py' in calls


@pytest.mark.parametrize('module_name', ['regression67', 'regression_famous'])
def test_regression_case_set_mismatch_fails(module_name, tmp_path, monkeypatch, capsys):
    module = __import__(module_name)
    monkeypatch.setattr(module, 'compute', lambda: (
        {'current': ('✅', 'detail')}, []) if module_name == 'regression67'
        else {'current': ('✅', 'detail')})
    baseline = tmp_path / 'baseline.json'
    baseline.write_text(json.dumps({
        'current': {'verdict': '✅'}, 'deleted': {'verdict': '✅'},
    }), encoding='utf-8')
    monkeypatch.setattr(sys, 'argv', [module_name + '.py', str(baseline)])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code != 0
    assert 'deleted' in capsys.readouterr().out


@pytest.mark.parametrize('module_name', ['regression67', 'regression_famous'])
def test_regression_write_baseline_rejected(module_name, tmp_path, monkeypatch):
    module = __import__(module_name)
    monkeypatch.setattr(module, 'compute', lambda: (
        {'current': ('❌', 'detail')}, []) if module_name == 'regression67'
        else {'current': ('❌', 'detail')})
    baseline = tmp_path / 'baseline.json'
    original = json.dumps({'current': {'verdict': '✅'}})
    baseline.write_text(original, encoding='utf-8')
    monkeypatch.setattr(module, 'DEFAULT_BASELINE', str(baseline))
    monkeypatch.setattr(sys, 'argv', [module_name + '.py', str(baseline), '--write-baseline'])
    with pytest.raises(SystemExit) as exc:
        module.main()
    assert exc.value.code != 0
    assert baseline.read_text(encoding='utf-8') == original


def test_calib_write_baseline_accepts_explicit_case_dimension(tmp_path, monkeypatch):
    import calib_assertions

    path = tmp_path / 'calib.yaml'
    path.write_text('''meta: {baseline_counts: {✅: 0, ⚠️: 0, ❌: 0}}
cases:
  - id: case
    items:
      - {dim: 财命, gold: {}, baseline: ✅}
''', encoding='utf-8')
    current = {('case', '财命'): ('❌', 'detail')}
    written = []
    monkeypatch.setattr(calib_assertions, 'YAML_PATH', str(path))
    monkeypatch.setattr(calib_assertions, 'compute', lambda doc: current)
    monkeypatch.setattr(calib_assertions, '_write_baseline',
                        lambda cur, cnt: written.append(cur))
    monkeypatch.setattr(sys, 'argv', [
        'calib_assertions.py', '--write-baseline', '--accept=case/财命',
    ])
    with pytest.raises(SystemExit) as exc:
        calib_assertions.main()
    assert exc.value.code == 1
    assert written == [current]


def test_cat4_guanming_uses_engine_veto_chain(monkeypatch):
    import regression67

    monkeypatch.setattr(regression67, 'run', lambda gans, zhis: {
        'guanming': {'is_guanming': False},
        'caiming': {'primary_view': '禄神当财'},
    })
    results = regression67.judge_cat4()
    dai_mao = next(row for row in results if row[0] == 'guan:带帽')
    assert dai_mao[2] is False


def test_public_zhiye_matches_engine_for_coal_worker():
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective.zhiye import analyze_zhiye
    import blind_eval
    import calib_assertions

    case = {
        'id': 'gj-煤矿工人',
        'bazi': {'year': '乙酉', 'month': '乙酉', 'day': '戊寅', 'hour': '乙卯'},
        'gender': '乾',
    }
    direct = analyze_zhiye('戊', ['乙', '乙', '戊', '乙'], ['酉', '酉', '寅', '卯'])
    engine = MangpaiEngine(blind_eval._bazi_data(case)).compute_all()
    assert direct['primary'] == engine['zhiye']['primary'] == 'laborer'

    calib_case = {
        'gans': ['乙', '乙', '戊', '乙'], 'zhis': ['酉', '酉', '寅', '卯'],
        'gender': '乾', 'year': 1960,
    }
    out = calib_assertions.run_case(calib_case)
    assert out['zy']['primary'] == out['res']['zhiye']['primary'] == 'laborer'


def test_public_zhiye_matches_engine_for_all_trainset_cases():
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective.zhiye import analyze_zhiye
    import blind_eval

    cases = blind_eval.yaml.safe_load(
        open(os.path.join(_HERE, 'trainset', 'cases.yaml'), encoding='utf-8'))
    mismatches = []
    for case in cases:
        bazi = case['bazi']
        gans = [bazi[p][0] for p in ('year', 'month', 'day', 'hour')]
        zhis = [bazi[p][1] for p in ('year', 'month', 'day', 'hour')]
        direct = analyze_zhiye(gans[2], gans, zhis)
        engine = MangpaiEngine(blind_eval._bazi_data(case)).compute_all()
        if direct['primary'] != engine['zhiye']['primary']:
            mismatches.append((case['id'], direct['primary'], engine['zhiye']['primary']))
    assert mismatches == []
