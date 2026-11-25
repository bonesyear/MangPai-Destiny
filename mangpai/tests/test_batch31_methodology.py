import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'heldout'))

import blind_eval

ROOT = Path(__file__).resolve().parents[2]


def test_ordered_regression_is_explicit_and_gated(capsys):
    before = {'case': {'scores': {'财命': '✅'}}}
    after = {'case': {'scores': {'财命': '⚠️'}}}
    assert len(blind_eval._ordered_regressions(before, after)) == 1
    assert blind_eval._diff_gate({'heldout': before}, {'heldout': after})[0] == 1
    blind_eval._print_diff({'heldout': before}, {'heldout': after})
    assert '有序回退 1 条' in capsys.readouterr().out


def test_restored_sources_and_prereg_boundary_exist():
    names = [
        'final-state-20260918.md',
        'tasks/kimi-p1-guanming.md', 'tasks/kimi-p2-guanming-fp.md',
        'tasks/kimi-p3-caiming.md', 'tasks/kimi-p4-zhiye.md',
        'tasks/kimi-t-professor.md', 'tasks/kimi-engine-precision-plan.md',
    ]
    assert all((ROOT / 'docs/archive' / name).is_file() for name in names)
    p1 = (ROOT / 'docs/kimi-p1-guanming-prereg-20260918.md').read_text(encoding='utf-8')
    assert '预注册规则命中 3 条，事后改门命中 1 条' in p1
    assert '捕/贼≈1.47<3' in p1
    assert '同一次提交' in p1


def test_go_is_conditional_and_li141_is_not_zero_regression():
    llm_doc = (ROOT / 'docs/llm-channel-20260818.md').read_text(encoding='utf-8')
    assert '有条件 GO（待复跑）' in llm_doc
    p4 = (ROOT / 'docs/kimi-p4-zhiye-muku-prereg-20260918.md').read_text(encoding='utf-8')
    assert 'li141' in p4 and '有序回退' in p4
    assert 'reg67-财制印刑警：p3/p4 时仍 ❌' in p4


def test_p4_history_matches_snapshots():
    def load(name):
        return json.loads((ROOT / 'mangpai/tests/heldout/snapshots' / f'{name}.json')
                          .read_text(encoding='utf-8'))

    for name in ('20260918_p3', '20260918_p4'):
        doc = load(name)
        assert doc['trainset']['reg67-财制印刑警']['scores']['职业'] == '❌'
        assert doc['heldout']['shouke-li141-名笔杆子']['scores']['职业'] == '⚠️'
    later = load('20261017_a1')
    assert later['heldout']['shouke-li141-名笔杆子']['scores']['职业'] == '❌'
    assert load('20261027_r7')['trainset']['reg67-财制印刑警']['scores']['职业'] == '✅'
