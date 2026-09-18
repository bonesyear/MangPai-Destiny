#!/usr/bin/env python3
"""脱敏脱密闸门（check_credentials）——入仓前自动扫描凭证/隐私/本机路径。

用法：
    python3 scripts/check_credentials.py            # 默认 --staged：只扫暂存区新增行
    python3 scripts/check_credentials.py --staged   # 供 pre-commit hook 调用
    python3 scripts/check_credentials.py --all      # 全量审计模式（存量会大量命中 P2，属预期）
    python3 scripts/check_credentials.py --strict   # P2 本机路径也升级为退出码 1

退出码：P0/P1 命中 → 1（阻止 commit）；仅 P2 → 0 + 警告（--strict 时 1）；无命中 → 0。

红线：输出一律打码（前 4 + 后 2），绝不打印完整敏感串；脚本自身只含扫描模式，
不含任何真实凭证。零依赖（纯标准库）。
"""
import argparse
import getpass
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SELF = Path(__file__).resolve()

# ---------------------------------------------------------------- 扫描模式（分类分级）
# P0 真凭证：命中即阻止
P0_PATTERNS = [
    ("volcengine-ark-key", re.compile(r"ark-[A-Za-z0-9]{6,}")),
    ("sk-style-key", re.compile(r"\bsk-[A-Za-z0-9]{16,}")),
    ("github-token", re.compile(r"\b(?:ghp|gho)_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("aws-access-key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    ("slack-token", re.compile(r"\bxox[bp]-[A-Za-z0-9-]{10,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
]
# 高熵串：须邻近出现 key/secret/token 等字样 + 同时含大写/小写/数字（误报控制：
# 纯 snake_case 标识符、小写连字符文件名、纯 hex 摘要等不计）
HIGH_ENTROPY = re.compile(r"[A-Za-z0-9_-]{32,}")
ENTROPY_CONTEXT = re.compile(
    r"(?i)\b(?:api[_-]?key|secret|token|password|passwd|credentials?|auth(?:orization)?)\b")


def _is_mixed_secret_shape(value: str) -> bool:
    return all(re.search(c, value) for c in (r"[a-z]", r"[A-Z]", r"[0-9]"))

# P1 隐私：默认阻止
P1_PATTERNS = [
    ("cn-mobile", re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")),
    ("cn-id-card", re.compile(r"(?<![\dXx])\d{17}[\dXx](?!\d)")),
]
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)\b")
EMAIL_EXEMPT = ("example.", "test.", "localhost")

# P2 本机路径：默认仅警告
P2_PATTERNS = [
    ("abs-path-root", re.compile(r"/root/")),
    ("abs-path-macos-user", re.compile(r"/Users/")),
    ("abs-path-win-user", re.compile(r"[A-Za-z]:\\Users\\")),
    ("abs-path-home-user", re.compile(r"/home/" + re.escape(getpass.getuser()) + r"/")),
]

# ---------------------------------------------------------------- 白名单/豁免
PLACEHOLDER_TOKENS = ("your-", "<REDACTED>", "***", "xxx")
FAKE_PREFIXES = ("sk-fake", "sk-file")


def _is_placeholder(value: str, line: str, start: int, end: int) -> bool:
    """占位符/测试假值豁免：看命中值本身与邻近上下文。"""
    v = value.lower()
    if v.startswith(FAKE_PREFIXES) or v.startswith("your-"):
        return True
    ctx = line[max(0, start - 24):end + 24].lower()
    return any(tok.lower() in ctx for tok in PLACEHOLDER_TOKENS)


def mask(value: str) -> str:
    """打码：前 4 + 后 2；过短则整体 <REDACTED>。断言打码结果不含完整原串。"""
    if len(value) <= 6:
        masked = "<REDACTED>"
    else:
        masked = value[:4] + "***" + value[-2:]
    assert value not in masked, "打码失败：结果包含完整敏感串"
    return masked


@dataclass
class Finding:
    level: str
    kind: str
    fname: str
    lineno: int
    masked: str

    def render(self) -> str:
        return f"{self.fname}:{self.lineno}: [{self.level}] {self.kind}: {self.masked}"


def scan_lines(lines, fname: str):
    """扫描若干行文本，返回 Finding 列表。"""
    findings = []
    # 模式定义自身豁免（本脚本/同类守护脚本内的正则字面量）
    try:
        is_self = fname != "<stdin>" and Path(fname).resolve() == SELF
    except OSError:
        is_self = False
    if is_self:
        return findings

    for lineno, line in enumerate(lines, 1):
        for kind, pat in P0_PATTERNS:
            for m in pat.finditer(line):
                if _is_placeholder(m.group(0), line, m.start(), m.end()):
                    continue
                findings.append(Finding("P0", kind, fname, lineno, mask(m.group(0))))
        for m in HIGH_ENTROPY.finditer(line):
            value = m.group(0)
            if len(set(value)) < 6 or not _is_mixed_secret_shape(value):
                continue
            ctx = line[max(0, m.start() - 48):m.end() + 48]
            if not ENTROPY_CONTEXT.search(ctx):
                continue
            if _is_placeholder(value, line, m.start(), m.end()):
                continue
            findings.append(Finding("P0", "high-entropy-near-key", fname, lineno, mask(value)))
        for kind, pat in P1_PATTERNS:
            for m in pat.finditer(line):
                if _is_placeholder(m.group(0), line, m.start(), m.end()):
                    continue
                findings.append(Finding("P1", kind, fname, lineno, mask(m.group(0))))
        for m in EMAIL_RE.finditer(line):
            domain = m.group(1).lower()
            local = m.group(0).split("@", 1)[0].lower()
            if any(t in domain for t in EMAIL_EXEMPT) or local.startswith(("test", "your")):
                continue
            findings.append(Finding("P1", "email", fname, lineno, mask(m.group(0))))
        for kind, pat in P2_PATTERNS:
            for m in pat.finditer(line):
                findings.append(Finding("P2", kind, fname, lineno, mask(m.group(0))))
    return findings


def scan_paths(paths, strict: bool = False):
    """扫描文件列表，返回 (退出码, 报告文本)。报告只含打码片段。"""
    findings = []
    for p in paths:
        p = Path(p)
        try:
            text = p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue  # 二进制/不可读文件跳过
        findings.extend(scan_lines(text.splitlines(), fname=str(p)))
    return _verdict(findings, strict)


def _verdict(findings, strict: bool):
    lines = [f.render() for f in findings]
    n0 = sum(1 for f in findings if f.level == "P0")
    n1 = sum(1 for f in findings if f.level == "P1")
    n2 = sum(1 for f in findings if f.level == "P2")
    lines.append(f"汇总: P0={n0} P1={n1} P2={n2}"
                 + ("（--strict 生效）" if strict else ""))
    if n0 or n1:
        rc = 1
    elif n2 and strict:
        rc = 1
    else:
        rc = 0
    # 红线总断言：报告内不得残留任何命中原文（逐条已由 mask 断言兜底）
    return rc, "\n".join(lines) + "\n"


def _staged_lines():
    """解析 git diff --cached --unified=0，产出 (文件名, 新增行) 列表。"""
    proc = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color", "--diff-filter=ACMR"],
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("git diff --cached 失败: " + proc.stderr.strip())
    per_file = {}
    fname = None
    for raw in proc.stdout.splitlines():
        if raw.startswith("+++ "):
            path = raw[4:]
            fname = None if path == "/dev/null" else (path[2:] if path.startswith("b/") else path)
        elif raw.startswith("+++") or raw.startswith("@@"):
            continue
        elif raw.startswith("+") and fname is not None:
            per_file.setdefault(fname, []).append(raw[1:])
    return per_file


def _all_files():
    proc = subprocess.run(
        ["git", "ls-files", "-z"] ,
        capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError("git ls-files 失败: " + proc.stderr.strip())
    tracked = proc.stdout.split("\0")
    proc2 = subprocess.run(
        ["git", "ls-files", "-z", "--others", "--exclude-standard"],
        capture_output=True, text=True)
    others = proc2.stdout.split("\0") if proc2.returncode == 0 else []
    return [p for p in tracked + others if p]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="脱敏脱密闸门：扫描凭证(P0)/隐私(P1)/本机路径(P2)，输出一律打码。")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true",
                      help="只扫暂存区新增行（默认，供 pre-commit hook 用）")
    mode.add_argument("--all", action="store_true",
                      help="全量审计：扫描全部已跟踪+未忽略文件")
    ap.add_argument("--strict", action="store_true",
                    help="P2 本机路径命中也返回退出码 1")
    ap.add_argument("paths", nargs="*", help="直接指定文件扫描（调试用途）")
    args = ap.parse_args(argv)

    try:
        if args.paths:
            rc, report = scan_paths(args.paths, strict=args.strict)
        elif args.all:
            rc, report = scan_paths(_all_files(), strict=args.strict)
        else:  # 默认 --staged
            findings = []
            for fname, lines in _staged_lines().items():
                findings.extend(scan_lines(lines, fname=fname))
            rc, report = _verdict(findings, args.strict)
    except RuntimeError as e:
        print(f"check_credentials: {e}", file=sys.stderr)
        return 2

    if rc != 0:
        report += ("修复指引：移除敏感串（改用环境变量/占位符），或确认其为测试假值后"
                   "按白名单形态（your-/sk-fake*/<REDACTED> 等）改写；"
                   "P2 本机路径改为相对路径或 __file__ 锚定。\n")
    sys.stdout.write(report)
    return rc


if __name__ == "__main__":
    sys.exit(main())
