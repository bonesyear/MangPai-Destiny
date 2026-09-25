"""文档数字闸门 check_doc_numbers.py 哨兵测试（先红后绿）。

红阶段 = 篡改数字 / 错误口径用例（本文件 test_tamper_*、test_parse_* 历史口径用例），
绿阶段 = 真实文档自洽 + 当前仓库端到端全绿。
"""
import importlib.util
import json
import re
import subprocess
import sys
import urllib.error
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


# ---------- --github：GitHub description 核对（全 mock，零真实网络请求） ----------

_GH_ACTUALS = {"modules_total": 10, "passed": 200}  # 合成 actuals，只测比对逻辑


class _FakeResp:
    """最小 urlopen 返回体：context manager + status + read()。"""

    def __init__(self, payload, status=200, raw=None):
        self.status = status
        self._raw = raw if raw is not None else json.dumps(payload).encode("utf-8")

    def read(self):
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _fake_urlopen(payload, status=200, raw=None, captured=None):
    def _open(req, timeout=None):
        if captured is not None:
            captured["req"] = req
            captured["timeout"] = timeout
        return _FakeResp(payload, status=status, raw=raw)
    return _open


def test_github_consistent_green(mod):
    results, errors = mod.check_github_description(
        "An engine — 10 modules, 4-layer architecture, 200 test cases.", _GH_ACTUALS)
    assert errors == []
    assert len(results) == 2 and all(r.ok for r in results)
    assert {r.item for r in results} == {"modules", "test cases"}
    assert all(r.location == "github description" for r in results)


def test_github_mismatch_precise_diff(mod):
    results, errors = mod.check_github_description(
        "An engine — 9 modules, 4-layer architecture, 199 test cases.", _GH_ACTUALS)
    assert errors == []
    failed = [r for r in results if not r.ok]
    assert len(failed) == 2
    line = mod._fmt(failed[0])
    assert line.startswith("❌ github description")
    assert "声明 9 | 实测 10" in line


def test_github_numbers_not_extractable(mod):
    for desc in ("An engine based on Mangpai methodology.", None, ""):
        results, errors = mod.check_github_description(desc, _GH_ACTUALS)
        assert results == []
        assert len(errors) == 1 and "无法从 description 提取数字声明" in errors[0]
        assert repr(desc) in errors[0]  # 当前描述须打印出来


def test_github_fetch_network_failure(mod):
    def _boom(req, timeout=None):
        raise urllib.error.URLError("connection refused")
    with pytest.raises(RuntimeError, match="请求失败"):
        mod.fetch_github_description("o/r", urlopen=_boom)


def test_github_fetch_http_non200(mod):
    def _boom(req, timeout=None):
        raise urllib.error.HTTPError("https://api.github.com/repos/o/r", 404, "Not Found", None, None)
    with pytest.raises(RuntimeError, match="HTTP 404"):
        mod.fetch_github_description("o/r", urlopen=_boom)


def test_github_fetch_bad_json(mod):
    with pytest.raises(RuntimeError, match="JSON 解析失败"):
        mod.fetch_github_description("o/r", urlopen=_fake_urlopen(None, raw=b"<html>not json</html>"))


def test_github_fetch_headers_anonymous_and_token(mod):
    captured = {}
    desc = mod.fetch_github_description("o/r", urlopen=_fake_urlopen({"description": "x"}, captured=captured))
    req = captured["req"]
    assert desc == "x"
    assert req.headers.get("Accept") == "application/vnd.github+json"
    assert req.headers.get("User-agent") == "mangpai-doc-numbers-check"
    assert "Authorization" not in req.headers  # 无 token = 匿名，不带凭证头
    captured2 = {}
    mod.fetch_github_description("o/r", token="your-github-token",
                                 urlopen=_fake_urlopen({"description": "y"}, captured=captured2))
    assert captured2["req"].headers.get("Authorization") == "Bearer your-github-token"


def test_github_run_check_env_and_anonymous(mod, monkeypatch):
    """run_github_check：repo 读 MANGPAI_GITHUB_REPO；无 GITHUB_TOKEN 不报错（匿名成功）。"""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("MANGPAI_GITHUB_REPO", "some/where")
    seen = {}

    def _fake_fetch(repo, token=None, urlopen=None):
        seen["repo"], seen["token"] = repo, token
        return "e — 10 modules, 200 test cases."

    monkeypatch.setattr(mod, "fetch_github_description", _fake_fetch)
    results, errors, repo = mod.run_github_check(_GH_ACTUALS)
    assert repo == "some/where" and seen == {"repo": "some/where", "token": None}
    assert errors == [] and all(r.ok for r in results)


def test_github_run_check_failure_returns_reason(mod, monkeypatch):
    def _boom(repo, token=None, urlopen=None):
        raise RuntimeError("GitHub API 请求失败（URLError: down）")

    monkeypatch.setattr(mod, "fetch_github_description", _boom)
    results, errors, repo = mod.run_github_check(_GH_ACTUALS)
    assert results == [] and len(errors) == 1 and "请求失败" in errors[0]


@pytest.fixture
def cli_env(mod, docs_and_actuals, monkeypatch):
    """main() 全 mock：gather_actuals 替换为自洽值；文档仍读真实文件。"""
    _, _, actuals = docs_and_actuals
    monkeypatch.setattr(mod, "gather_actuals", lambda: actuals)
    return actuals


def test_cli_github_green(mod, cli_env, monkeypatch, capsys):
    desc = f"e — {cli_env['modules_total']} modules, 4-layer, {cli_env['passed']} test cases."
    monkeypatch.setattr(mod, "fetch_github_description",
                        lambda repo, token=None, urlopen=None: desc)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    rc = mod.main(["--github"])
    out = capsys.readouterr().out
    assert rc == 0
    assert "✅ github description | modules |" in out
    assert "✅ github description | test cases |" in out


def test_cli_github_mismatch_exit1(mod, cli_env, monkeypatch, capsys):
    desc = (f"e — {cli_env['modules_total'] + 1} modules, x, "
            f"{cli_env['passed'] + 1} test cases.")
    monkeypatch.setattr(mod, "fetch_github_description",
                        lambda repo, token=None, urlopen=None: desc)
    rc = mod.main(["--github"])
    out = capsys.readouterr().out
    assert rc == 1
    assert (f"❌ github description | modules | 声明 {cli_env['modules_total'] + 1} "
            f"| 实测 {cli_env['modules_total']}") in out


def test_cli_github_network_error_exit1(mod, cli_env, monkeypatch, capsys):
    def _boom(repo, token=None, urlopen=None):
        raise RuntimeError("GitHub API 请求失败（URLError: simulated）")

    monkeypatch.setattr(mod, "fetch_github_description", _boom)
    rc = mod.main(["--github"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "❌ github description | GitHub API 请求失败" in out


def test_cli_github_json_shape(mod, cli_env, monkeypatch, capsys):
    desc = f"e — {cli_env['modules_total']} modules, {cli_env['passed']} test cases."
    monkeypatch.setattr(mod, "fetch_github_description",
                        lambda repo, token=None, urlopen=None: desc)
    rc = mod.main(["--github", "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert payload["github"]["errors"] == []
    assert len(payload["github"]["results"]) == 2
    assert payload["github"]["repo"] == mod.DEFAULT_GITHUB_REPO


def test_cli_default_no_github_unchanged(mod, cli_env, capsys):
    """默认不带 --github：文本/JSON 输出零 github 痕迹（默认行为不变回归）。"""
    rc = mod.main([])
    out = capsys.readouterr().out
    assert rc == 0 and "github" not in out.lower()
    rc = mod.main(["--json"])
    payload = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert set(payload) == {"ok", "actuals", "low_freq_skipped", "results"}
    assert len(payload["results"]) == 10
