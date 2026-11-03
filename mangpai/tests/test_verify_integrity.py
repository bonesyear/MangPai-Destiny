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


@pytest.mark.parametrize('relative,args', [
    ('mangpai/tests/calib_assertions.py', []),
    ('mangpai/tests/heldout/blind_eval.py', ['--diff', 'latest', 'latest']),
    ('mangpai/tests/backtest/regression67.py', []),
    ('mangpai/tests/backtest/regression_famous.py', []),
])
def test_cli_utf8_default_console(relative, args):
    import subprocess

    env = os.environ.copy()
    env.pop('PYTHONIOENCODING', None)
    env['PYTHONUTF8'] = '0'
    r = subprocess.run([sys.executable, os.path.join(_REPO, relative), *args],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env=env, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr


def test_verify_mangpai_reports_only_known_xfail():
    import subprocess

    env = os.environ.copy()
    env.pop('PYTHONIOENCODING', None)
    env['PYTHONUTF8'] = '0'
    r = subprocess.run([sys.executable, os.path.join(_REPO, 'mangpai', 'verify_mangpai.py')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       env=env, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert '验证结果: 404 passed, 0 failed, 0 xfailed, total 404' in r.stdout


def test_famous_r7_regressions_closed():
    import subprocess

    r = subprocess.run([sys.executable,
                        os.path.join(_REPO, 'mangpai/tests/backtest/regression_famous.py')],
                       capture_output=True, text=True, encoding='utf-8', errors='replace',
                       timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert '预期未决（R7' not in r.stdout
    assert 'REGRESSION (' not in r.stdout


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


@pytest.mark.parametrize('script', ['regression67.py', 'regression_famous.py'])
def test_regression_missing_baseline_exit_nonzero(script, tmp_path):
    """回归 runner：指定基线不存在时必须失败，不能仅打印当前判定后假绿。"""
    import subprocess

    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(
        [sys.executable, os.path.join(_HERE, 'backtest', script),
         str(tmp_path / 'missing-baseline.json')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, timeout=60,
    )
    assert r.returncode != 0
    assert 'baseline 不存在' in r.stdout + r.stderr


def test_verify_all_propagates_pytest_failure(tmp_path):
    """verify_all：任一 pytest 失败必须传到总退出码，不能被后续成功命令掩盖。"""
    import shutil
    import subprocess

    if shutil.which('bash') is None:
        pytest.skip('verify_all.sh 需要 bash')
    fake_python = tmp_path / 'fake-python'
    fake_python.write_text(
        '#!/bin/bash\n'
        'if [[ "$1" == "-m" && "$2" == "pytest" ]]; then\n'
        '  echo "injected pytest failure"\n'
        '  exit 1\n'
        'fi\n'
        'case "$1" in\n'
        '  *verify_*.py) echo "验证结果: 420 passed, 0 failed" ;;\n'
        '  *regression67.py|*regression_famous.py|*calib_assertions.py)\n'
        '    echo "TOTAL: ✅0 ⚠️0 ❌0" ;;\n'
        'esac\n'
        'exit 0\n',
        encoding='utf-8',
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    env['PYTHON'] = str(fake_python)
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(
        ['bash', os.path.join(_HERE, 'backtest', 'verify_all.sh')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, timeout=30,
    )
    assert r.returncode != 0
    assert 'injected pytest failure' in r.stdout + r.stderr


def test_verify_all_propagates_verify_failure(tmp_path):
    """verify_all：命令替换中的 verify 失败也必须传到总退出码。"""
    import shutil
    import subprocess

    if shutil.which('bash') is None:
        pytest.skip('verify_all.sh 需要 bash')
    fake_python = tmp_path / 'fake-python'
    fake_python.write_text(
        '#!/bin/bash\n'
        'if [[ "$1" == *verify_mangpai.py ]]; then\n'
        '  echo "验证结果: injected verify failure"\n'
        '  exit 1\n'
        'fi\n'
        'if [[ "$1" == "-m" && "$2" == "pytest" ]]; then\n'
        '  echo "1453 passed"\n'
        '  exit 0\n'
        'fi\n'
        'case "$1" in\n'
        '  *verify_*.py) echo "验证结果: 420 passed, 0 failed" ;;\n'
        '  *regression67.py|*regression_famous.py|*calib_assertions.py)\n'
        '    echo "TOTAL: ✅0 ⚠️0 ❌0" ;;\n'
        'esac\n'
        'exit 0\n',
        encoding='utf-8',
    )
    fake_python.chmod(0o755)
    env = os.environ.copy()
    env['PYTHON'] = str(fake_python)
    env['PYTHONIOENCODING'] = 'utf-8'
    r = subprocess.run(
        ['bash', os.path.join(_HERE, 'backtest', 'verify_all.sh')],
        capture_output=True, text=True, encoding='utf-8', errors='replace',
        env=env, timeout=30,
    )
    assert r.returncode != 0


def test_cat3_specific_gold_requires_actual_book_conclusion(monkeypatch):
    sys.path.insert(0, os.path.join(_HERE, 'backtest'))
    import regression67

    args = ('局象', '戊丙乙戊', '申辰丑寅', '⚠️', ('合成缺口词',))
    assert regression67.judge_cat3(*args)[0] == '❌'
    monkeypatch.setattr(regression67, 'run', lambda gans, zhis: {
        'xiangfa_ops': {'juxiang': [{'desc': '合成缺口词'}]}
    })
    assert regression67.judge_cat3(*args)[0] == '✅'


def test_gongxiang_ding_eye_and_shen_machine():
    from mangpai.subjective.xiangfa_ops import gongxiang
    eyes = gongxiang('乙', list('丁辛乙丁'), list('酉亥酉亥'))
    assert any(f['subject'] == '眼睛' for f in eyes)
    machines = gongxiang('辛', list('辛丙辛丙'), list('卯申巳申'))
    assert any(f['subject'] == '机器' for f in machines)
    no_machine = gongxiang('甲', list('辛丙辛丙'), list('卯申巳申'))
    assert not any(f['subject'] == '机器' for f in no_machine)


def test_hexiang_building_design_and_financial_officer():
    from mangpai.subjective.xiangfa_ops import hexiang
    building = hexiang('丙', list('壬癸丙戊'), list('子丑寅戌'))
    assert any(f['subject'] == '建筑设计' for f in building)
    no_building = hexiang('丙', list('壬癸丙戊'), list('子丑寅午'))
    assert not any(f['subject'] == '建筑设计' for f in no_building)
    finance = hexiang('癸', list('庚乙癸庚'), list('辰酉卯申'))
    assert any(f['subject'] == '金融官员' for f in finance)
    no_finance = hexiang('癸', list('庚乙癸庚'), list('辰酉卯午'))
    assert not any(f['subject'] == '金融官员' for f in no_finance)


def test_zhixiang_yuefei_captured_power_and_reverse_wealth():
    from mangpai.subjective.xiangfa_ops import zhixiang
    yuefei = zhixiang('甲', list('癸乙甲己'), list('未卯子巳'))
    assert any('得兵权' in f['subject'] for f in yuefei)
    assert not any(f['subject'] == '失/被制印文' for f in yuefei)
    capital = zhixiang('丙', list('丁癸丙壬'), list('未丑子辰'))
    assert any(f['direction'] == '反向做功' for f in capital)
    no_reverse = zhixiang('庚', list('丁癸丙壬'), list('未丑子辰'))
    assert not any(f['direction'] == '反向做功' for f in no_reverse)


def test_juxiang_yang_cover_yin_with_yin_gongmen():
    from mangpai.subjective.xiangfa_ops import juxiang
    police = juxiang('乙', list('戊丙乙戊'), list('申辰丑寅'))
    assert any(f.get('qi_xiang') == '阳包阴' and '公门' in f['desc']
               for f in police)
    no_gongmen = juxiang('乙', list('戊丙乙戊'), list('申辰丑卯'))
    assert not any('公门' in f['desc'] for f in no_gongmen)


def test_calib_not_applicable_dimension_is_skipped(monkeypatch, tmp_path):
    from collections import Counter
    import calib_assertions as ca
    monkeypatch.setattr(ca, 'run_case', lambda case: (_ for _ in ()).throw(
        AssertionError('不适用维度不应调用引擎')))
    doc = {'cases': [{'id': 'official', 'items': [
        {'dim': '职业', 'gold': {'not_applicable': True}}
    ]}]}
    assert ca.compute(doc) == {}
    path = tmp_path / 'calib.yaml'
    path.write_text('''meta: {baseline_counts: {✅: 0, ⚠️: 0, ❌: 0}}
cases:
  - id: official
    items:
      - {dim: 职业, gold: {not_applicable: true}, baseline: ❌}
''', encoding='utf-8')
    monkeypatch.setattr(ca, 'YAML_PATH', str(path))
    ca._write_baseline({}, Counter())
    assert 'not_applicable: true' in path.read_text(encoding='utf-8')
