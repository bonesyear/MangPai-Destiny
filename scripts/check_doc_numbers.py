#!/usr/bin/env python3
"""文档数字闸门：README / knowledge-base 权威声明位 vs 实测值，防数字漂移。

只校验「权威声明位置」（README 首行 / 验证表 pytest 行 / 架构分层表、
KB 验证口径行 / KB §8 工具表 pytest 行），不做全量 grep——KB 含大量
「旧记 X 均作废」历史口径，全量扫会误报。

实测来源（脚本内自算，不信任声明）：
- pytest：`python3 -m pytest --collect-only -q`（~0.5s，不真跑全量）；
  xfail 数 = `-m xfail --collect-only` 计数；passed = collected - xfail。
- 模块数：foundation（仓库根，递归）/ mangpai/objective（递归）/
  mangpai/subjective（只算顶层，prompts/ 子目录不计入，README 既有口径）。

verify 四件套（432/70/64/20）为低频项：各 verify 脚本总数由运行期动态累计，
静态解析不可靠，本闸门跳过；需核对时实际运行对应 verify 脚本。

用法：
    python3 scripts/check_doc_numbers.py          # 全量报告；退出码 0=全一致 / 1=任一漂移
    python3 scripts/check_doc_numbers.py --quiet  # 只报不一致项
    python3 scripts/check_doc_numbers.py --json   # JSON 输出
建议：改了测试数量（新增/删除用例）或模块数后跑一次。非 pre-commit 默认项。
"""
import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
README_PATH = REPO_ROOT / "README.md"
KB_PATH = REPO_ROOT / "docs" / "knowledge-base.md"

_RE_HEADLINE = re.compile(r"(\d+)\s*模块[^。\n]*?(\d+)\s*验证用例")
_RE_README_PYTEST_ROW = re.compile(r"\|\s*pytest[^|\n]*?\|\s*\**(\d+)\s*passed")
_RE_KB_PYTEST = re.compile(r"(\d+)\s*collected（[^\d（）]*?(\d+)\s*passed\s*\+\s*1\s*xfailed")
_RE_STALE_CTX = re.compile(r"旧记|作废")
_RE_COLLECTED = re.compile(r"(?:(\d+)/)?(\d+) tests? collected")

LOW_FREQ_NOTE = (
    "verify 四件套（verify_mangpai/verify_dayun/verify_layer1/verify_layer3_checkpoint）"
    "= 低频项跳过：总数由运行期动态累计，静态解析不可靠；需核对时请实际运行对应脚本。"
)


@dataclass
class Result:
    location: str
    item: str
    declared: object  # int；None = 声明位未解析到（视为不一致）
    actual: int
    ok: bool


# ---------- 解析（纯函数，哨兵可单测） ----------

def parse_readme_headline(text):
    """README 首行「…N 模块四层架构，M 验证用例全绿…」→ (模块数, 用例数)。"""
    m = _RE_HEADLINE.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def parse_readme_pytest_row(text):
    """README 验证表 pytest 行「| pytest（…） | N passed + 1 xfailed |」→ passed 数。"""
    m = _RE_README_PYTEST_ROW.search(text)
    return int(m.group(1)) if m else None


def parse_readme_layer_row(text, layer):
    """README 架构表「| **Layer** | … | N |」→ 该层模块数。"""
    m = re.search(r"\|\s*\*\*" + re.escape(layer) + r"\*\*\s*\|[^|\n]*\|\s*(\d+)\s*\|", text)
    return int(m.group(1)) if m else None


def parse_kb_pytest_line(line):
    """KB pytest 声明行 → (collected, passed)；「旧记/作废」历史口径跳过。"""
    for m in _RE_KB_PYTEST.finditer(line):
        ctx = line[max(0, m.start() - 12):m.start()]
        if _RE_STALE_CTX.search(ctx):
            continue
        return int(m.group(1)), int(m.group(2))
    return None


def find_line(text, *needles):
    for line in text.splitlines():
        if all(n in line for n in needles):
            return line
    return None


# ---------- 实测 ----------

def _py_files(dirpath, recursive):
    if not dirpath.is_dir():
        return []
    it = dirpath.rglob("*.py") if recursive else dirpath.glob("*.py")
    return [p for p in it if p.name != "__init__.py" and "__pycache__" not in p.parts]


def count_modules(root):
    """分层口径：foundation/objective 递归；subjective 只算顶层（prompts/ 不计入）。"""
    root = Path(root)
    return {
        "foundation": len(_py_files(root / "foundation", True)),
        "objective": len(_py_files(root / "mangpai" / "objective", True)),
        "subjective": len(_py_files(root / "mangpai" / "subjective", False)),
    }


def _pytest_interpreter():
    for cand in (sys.executable, "python3", "/usr/bin/python3"):
        try:
            r = subprocess.run([cand, "-m", "pytest", "--version"],
                               capture_output=True, text=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            continue
        if r.returncode == 0:
            return cand
    return None


def _collect_count(interp, root, extra=()):
    """→ (选中数, 总数)。普通 collect: N tests collected；-m xfail: X/N tests collected。"""
    r = subprocess.run([interp, "-m", "pytest", "--collect-only", "-q", *extra],
                       capture_output=True, text=True, cwd=str(root), timeout=300)
    out = r.stdout + r.stderr
    matches = _RE_COLLECTED.findall(out)
    if not matches:
        raise RuntimeError("pytest collect 输出无法解析：\n" + out[-800:])
    selected, total = matches[-1]
    return (int(selected) if selected else int(total)), int(total)


def gather_actuals(root=REPO_ROOT):
    interp = _pytest_interpreter()
    if interp is None:
        raise RuntimeError("找不到可用的 pytest 解释器（试过 sys.executable / python3 / /usr/bin/python3）")
    collected, _ = _collect_count(interp, root)
    xfail, _ = _collect_count(interp, root, ("-m", "xfail"))
    mods = count_modules(root)
    return {
        "collected": collected,
        "xfail": xfail,
        "passed": collected - xfail,
        **mods,
        "modules_total": sum(mods.values()),
    }


# ---------- 校验 ----------

def _res(location, item, declared, actual):
    return Result(location, item, declared, actual, declared == actual)


def check_docs(readme_text, kb_text, actuals):
    """对全部权威声明位出结果列表；declared=None 表示声明位缺失/未解析（不一致）。"""
    results = []

    headline = parse_readme_headline(readme_text)
    results.append(_res("README.md 首行", "模块总数",
                        headline[0] if headline else None, actuals["modules_total"]))
    results.append(_res("README.md 首行", "验证用例(passed)",
                        headline[1] if headline else None, actuals["passed"]))

    row = parse_readme_pytest_row(readme_text)
    results.append(_res("README.md 验证表", "pytest passed", row, actuals["passed"]))

    for layer, key in (("Foundation", "foundation"), ("Objective", "objective"),
                       ("Subjective", "subjective")):
        results.append(_res("README.md 架构表", f"{layer} 模块数",
                            parse_readme_layer_row(readme_text, layer), actuals[key]))

    for label, needles in (
        ("docs/knowledge-base.md 验证口径行", ("验证口径", "collected")),
        ("docs/knowledge-base.md §8 工具表", ("python3 -m pytest mangpai/tests/", "collected")),
    ):
        line = find_line(kb_text, *needles)
        parsed = parse_kb_pytest_line(line) if line else None
        results.append(_res(label, "pytest collected",
                            parsed[0] if parsed else None, actuals["collected"]))
        results.append(_res(label, "pytest passed",
                            parsed[1] if parsed else None, actuals["passed"]))

    return results


def exit_code(results):
    return 0 if all(r.ok for r in results) else 1


# ---------- CLI ----------

def _fmt(r):
    declared = str(r.declared) if r.declared is not None else "未解析"
    mark = "✅" if r.ok else "❌"
    return f"{mark} {r.location} | {r.item} | 声明 {declared} | 实测 {r.actual}"


def main(argv=None):
    ap = argparse.ArgumentParser(description="文档数字闸门：README/KB 权威声明位 vs 实测")
    ap.add_argument("--quiet", action="store_true", help="只输出不一致项")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    args = ap.parse_args(argv)

    actuals = gather_actuals()
    results = check_docs(README_PATH.read_text(encoding="utf-8"),
                         KB_PATH.read_text(encoding="utf-8"), actuals)
    rc = exit_code(results)

    if args.json:
        print(json.dumps({"ok": rc == 0, "actuals": actuals, "low_freq_skipped": LOW_FREQ_NOTE,
                          "results": [asdict(r) for r in results]}, ensure_ascii=False, indent=2))
        return rc

    shown = results if not args.quiet else [r for r in results if not r.ok]
    for r in shown:
        print(_fmt(r))
    print(f"· 低频项：{LOW_FREQ_NOTE}")
    if not args.quiet or rc == 0:
        print(f"实测基准：{actuals['modules_total']} 模块（foundation {actuals['foundation']} / "
              f"objective {actuals['objective']} / subjective {actuals['subjective']} 顶层）；"
              f"pytest {actuals['collected']} collected = {actuals['passed']} passed + "
              f"{actuals['xfail']} xfailed")
    print("闸门结论：" + ("全部一致 ✅" if rc == 0 else "存在漂移 ❌——请同步上述文档数字"))
    return rc


if __name__ == "__main__":
    sys.exit(main())
