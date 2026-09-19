"""文档数字闸门 check_doc_numbers.py 哨兵测试（先红后绿）。

红阶段 = 篡改数字 / 错误口径用例（本文件 test_tamper_*、test_parse_* 历史口径用例），
绿阶段 = 真实文档自洽 + 当前仓库端到端全绿。
"""
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_doc_numbers.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("check_doc_numbers", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def mod():
    return _load_mod()


@pytest.fixture(scope="module")
def docs_and_actuals(mod):
    """从真实文档解析声明值，构造自洽 actuals（不跑 collect，不依赖硬编码数字）。"""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    kb = (REPO_ROOT / "docs" / "knowledge-base.md").read_text(encoding="utf-8")
    modules, cases = mod.parse_readme_headline(readme)
    kb_collected, kb_passed = mod.parse_kb_pytest_line(
        mod.find_line(kb, "验证口径", "collected"))
    actuals = {
        "collected": kb_collected,
        "xfail": kb_collected - cases,
        "passed": cases,
        "foundation": mod.parse_readme_layer_row(readme, "Foundation"),
        "objective": mod.parse_readme_layer_row(readme, "Objective"),
        "subjective": mod.parse_readme_layer_row(readme, "Subjective"),
        "modules_total": modules,
    }
    assert kb_passed == cases and kb_collected > cases
    return readme, kb, actuals


# ---------- 绿：正确数字 → 全过 + 退出码 0 ----------

def test_correct_numbers_all_green(mod, docs_and_actuals):
    readme, kb, actuals = docs_and_actuals
    results = mod.check_docs(readme, kb, actuals)
    assert len(results) == 10
    assert all(r.ok for r in results), [r for r in results if not r.ok]
    assert mod.exit_code(results) == 0


# ---------- 红：篡改任一数字 → 报不一致 + 退出码 1 ----------

def test_tamper_readme_headline_cases(mod, docs_and_actuals):
    readme, kb, actuals = docs_and_actuals
    bad = mod._RE_HEADLINE.sub(
        lambda m: m.group(0).replace(m.group(2), str(int(m.group(2)) + 1)), readme, count=1)
    assert bad != readme
    results = mod.check_docs(bad, kb, actuals)
    failed = [r for r in results if not r.ok]
    assert len(failed) == 1 and failed[0].item == "验证用例(passed)"
    assert mod.exit_code(results) == 1


def test_tamper_readme_layer_count(mod, docs_and_actuals):
    readme, kb, actuals = docs_and_actuals
    line = mod.find_line(readme, "**Subjective**")
    n = mod.parse_readme_layer_row(readme, "Subjective")
    bad = readme.replace(line, line.replace(f"| {n} |", f"| {n + 1} |"), 1)
    assert bad != readme
    results = mod.check_docs(bad, kb, actuals)
    failed = [r for r in results if not r.ok]
    assert len(failed) == 1 and "Subjective" in failed[0].item
    assert mod.exit_code(results) == 1


def test_tamper_kb_tools_row_collected(mod, docs_and_actuals):
    readme, kb, actuals = docs_and_actuals
    line = mod.find_line(kb, "python3 -m pytest mangpai/tests/", "collected")
    collected, _ = mod.parse_kb_pytest_line(line)
    bad_line = line.replace(f"{collected} collected", f"{collected + 1} collected", 1)
    assert bad_line != line
    results = mod.check_docs(readme, kb.replace(line, bad_line, 1), actuals)
    failed = [r for r in results if not r.ok]
    assert len(failed) == 1 and failed[0].location.endswith("§8 工具表")
    assert mod.exit_code(results) == 1


# ---------- 模块数口径：subjective 只算顶层，子目录不计入 ----------

def test_count_modules_top_level_only(mod, tmp_path):
    (tmp_path / "foundation").mkdir()
    (tmp_path / "foundation" / "a.py").write_text("", encoding="utf-8")
    (tmp_path / "foundation" / "b.py").write_text("", encoding="utf-8")
    (tmp_path / "foundation" / "__init__.py").write_text("", encoding="utf-8")
    obj = tmp_path / "mangpai" / "objective"
    obj.mkdir(parents=True)
    (obj / "x.py").write_text("", encoding="utf-8")
    (obj / "sub").mkdir()
    (obj / "sub" / "y.py").write_text("", encoding="utf-8")  # objective 递归计入
    subj = tmp_path / "mangpai" / "subjective"
    subj.mkdir(parents=True)
    (subj / "s1.py").write_text("", encoding="utf-8")
    (subj / "s2.py").write_text("", encoding="utf-8")
    (subj / "__init__.py").write_text("", encoding="utf-8")
    (subj / "prompts").mkdir()
    (subj / "prompts" / "p1.py").write_text("", encoding="utf-8")  # 子目录不计入
    (subj / "prompts" / "p2.py").write_text("", encoding="utf-8")

    counts = mod.count_modules(tmp_path)
    assert counts == {"foundation": 2, "objective": 2, "subjective": 2}


# ---------- 解析函数单测（含历史口径不得当作声明） ----------

def test_parse_readme_anchors(mod):
    text = "…引擎。59 模块四层架构，1149 验证用例全绿（+1 xfail）。\n"
    assert mod.parse_readme_headline(text) == (59, 1149)
    row = "| pytest（含属性化测试） | 1149 passed + 1 xfailed | ✅ |"
    assert mod.parse_readme_pytest_row(row) == 1149
    table = "| **Foundation** | 基础层 | 2 | 干支性情赋 |"
    assert mod.parse_readme_layer_row(table, "Foundation") == 2
    assert mod.parse_readme_layer_row(table, "Objective") is None


def test_parse_kb_line_authoritative_vs_stale(mod):
    line = "- **验证口径**：… `pytest mangpai/tests/` 1150 collected（**1149 passed+1 xfailed，脱敏闸门批实测**；脱敏闸门批 +20 测后 1149、审查修复批 1129+1xf、L1 1066+1xf、旧记 G2 838+1xf+19xp、批10 499 均作废）"
    assert mod.parse_kb_pytest_line(line) == (1150, 1149)  # 取首个权威声明，历史口径不顶位

    stale = "旧记 794 collected（794 passed+1 xfailed）均作废"
    assert mod.parse_kb_pytest_line(stale) is None  # 「旧记…作废」不得当作声明

    stale2 = "（旧记 1129 collected（1129 passed+1 xfailed），均已作废）"
    assert mod.parse_kb_pytest_line(stale2) is None


def test_parse_missing_returns_none(mod):
    assert mod.parse_readme_headline("没有任何数字") is None
    assert mod.parse_readme_pytest_row("| 其他 | 行 |") is None
    assert mod.parse_kb_pytest_line("") is None


# ---------- 端到端：当前仓库实跑脚本 → 全绿（退出码 0） ----------

def test_repo_end_to_end_green():
    r = subprocess.run([sys.executable, str(SCRIPT), "--quiet"],
                       capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
