#!/usr/bin/env python3
"""脱敏脱密闸门（check_credentials）——入仓前自动扫描凭证/隐私/本机路径。

用法：
    python3 scripts/check_credentials.py            # 默认 --staged：只扫暂存区新增行
    python3 scripts/check_credentials.py --staged   # 供 pre-commit hook 调用
    python3 scripts/check_credentials.py --all      # 全量审计（存量出生信息告警/P2 命中属预期）
    python3 scripts/check_credentials.py --strict   # P2 本机路径也升级为退出码 1

退出码：P0/P1 命中 → 1（阻止 commit；birth-data 首批只告警）；仅 P2 → 0 + 警告（--strict 时 1）；无命中 → 0。

红线：输出一律打码（前 4 + 后 2），绝不打印完整敏感串；脚本自身只含扫描模式，
不含任何真实凭证。零依赖（纯标准库）。
"""
import argparse
import difflib
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

SELF = Path(__file__).resolve()

# ---------------------------------------------------------------- 扫描模式（分类分级）
# P0 真凭证：命中即阻止
P0_PATTERNS = [
    ("volcengine-ark-key", re.compile(r"\bark-[A-Za-z0-9]{6,}")),
    ("sk-style-key", re.compile(r"\bsk-(?:[a-z0-9]+-)*[A-Za-z0-9_-]{16,}")),
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}")),
    ("aws-access-key", re.compile(r"\bAKIA[A-Z0-9]{16}\b")),
    ("slack-token", re.compile(r"\bxox[bp]-[A-Za-z0-9-]{10,}")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
    ("bearer-token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}")),
]
# 高熵串：须邻近出现 key/secret/token 等字样 + 同时含大写/小写/数字（误报控制：
# 纯 snake_case 标识符、小写连字符文件名、纯 hex 摘要等不计）
HIGH_ENTROPY = re.compile(r"[A-Za-z0-9_-]{32,}")
ENTROPY_CONTEXT = re.compile(
    r"(?i)(?:api[_-]?key|secret|token|passw(?:or)?d|credentials?|auth)(?![a-z])")
ENV_ASSIGN_RE = re.compile(
    r"\b[A-Z][A-Z0-9_]*(?:KEY|SECRET|TOKEN|PASSWORD)\s*=\s*[\"']?"
    r"([A-Za-z0-9_./+\-=]{16,})")


def _is_mixed_secret_shape(value: str) -> bool:
    return all(re.search(c, value) for c in (r"[a-z]", r"[A-Z]", r"[0-9]"))

# P1 隐私：默认阻止；birth-data 首批只告警，见 _verdict。
P1_PATTERNS = [
    ("cn-mobile", re.compile(
        r"(?<!\d)(?:\+?86[-\s]?)?1[3-9]\d[-\s]?\d{4}[-\s]?\d{4}(?!\d)")),
    ("cn-id-card", re.compile(r"(?<![\dXx])\d{17}[\dXx](?!\d)")),
]
EMAIL_RE = re.compile(
    r"(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@"
    r"([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)(?![A-Za-z0-9-])")
EMAIL_EXEMPT = ("example.com", "example.org", "example.net", ".example", ".test", ".invalid")
BIRTH_DATE_RE = re.compile(
    r"(?<!\d)(?:(?:19|20)\d{2}\s*[-/.年]\s*\d{1,2}\s*[-/.月]\s*\d{1,2}\s*日?"
    r"|(?:19|20)\d{2}\s*,\s*\d{1,2}\s*,\s*\d{1,2})")
BIRTH_TIME_RE = re.compile(
    r"(?<![\d:：])(?:[01]?\d|2[0-3])\s*[:：]\s*[0-5]\d(?!\d)"
    r"|(?<!\d)(?:[01]?\d|2[0-3])\s*,\s*[0-5]\d(?!\d)")
BIRTH_GENDER_RE = re.compile(r"男|女|\bmale\b|\bfemale\b", re.IGNORECASE)
BIRTH_PLACE_RE = re.compile(r"[\u4e00-\u9fff]{2,12}|\d{2,3}\.\d{1,4}")
BIRTH_DATA_RE = re.compile(
    r"(?:" + BIRTH_DATE_RE.pattern + r")[^\n]{0,40}?(?:"
    + BIRTH_TIME_RE.pattern + r")[^\n]{0,20}?(?:"
    + BIRTH_GENDER_RE.pattern + r")\s*[,，]?\s*(?:"
    + BIRTH_PLACE_RE.pattern + r")")
BIRTH_EXEMPT = ("# synthetic", "虚构示例")

# P2 本机路径：默认仅警告
P2_PATTERNS = [
    ("abs-path-root", re.compile(r"/root/")),
    ("abs-path-macos-user", re.compile(r"/Users/")),
    ("abs-path-win-user", re.compile(r"[A-Za-z]:\\Users\\")),
    ("abs-path-home-user", re.compile(r"/home/[^/]+/")),
]

# ---------------------------------------------------------------- 白名单/豁免
FAKE_PREFIXES = ("sk-fake", "sk-file")
HASH_FIELD_RE = re.compile(
    r'^\s*"(?:engine_sha256|tree_hash)"\s*:\s*"[0-9a-f]{64}"\s*,?$')


def _is_placeholder(value: str, line: str, start: int, end: int) -> bool:
    """只按命中值本身豁免，邻近注释不得连带放行真实凭证。"""
    v = value.lower()
    return (v.startswith(FAKE_PREFIXES) or v.startswith("your-") or "-fake-" in v
            or v == "<redacted>" or re.fullmatch(r"(?:sk-)?x{3,}|\*+", v) is not None)


def _allowed(line: str, kind: str) -> bool:
    return re.search(rf"credscan:\s*allow-(?:{re.escape(kind)}|all)\b", line) is not None


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
                if _is_placeholder(m.group(0), line, m.start(), m.end()) or _allowed(line, kind):
                    continue
                findings.append(Finding("P0", kind, fname, lineno, mask(m.group(0))))
        for m in HIGH_ENTROPY.finditer(line):
            value = m.group(0)
            if len(set(value)) < 6 or not _is_mixed_secret_shape(value):
                continue
            ctx = line[max(0, m.start() - 48):m.end() + 48]
            if not ENTROPY_CONTEXT.search(ctx):
                continue
            if _is_placeholder(value, line, m.start(), m.end()) or _allowed(line, "high-entropy-near-key"):
                continue
            findings.append(Finding("P0", "high-entropy-near-key", fname, lineno, mask(value)))
        for m in ENV_ASSIGN_RE.finditer(line):
            value = m.group(1)
            if _allowed(line, "sensitive-env-assignment"):
                continue
            if not _is_placeholder(value, line, m.start(1), m.end(1)):
                findings.append(Finding("P0", "sensitive-env-assignment", fname, lineno, mask(value)))
        if HASH_FIELD_RE.fullmatch(line):
            continue
        for kind, pat in P1_PATTERNS:
            for m in pat.finditer(line):
                if _is_placeholder(m.group(0), line, m.start(), m.end()) or _allowed(line, kind):
                    continue
                findings.append(Finding("P1", kind, fname, lineno, mask(m.group(0))))
        for m in EMAIL_RE.finditer(line):
            domain = m.group(1).lower()
            local = m.group(0).split("@", 1)[0].lower()
            exempt = domain == "localhost" or any(
                domain == token or domain.endswith(token if token.startswith(".") else "." + token)
                for token in EMAIL_EXEMPT)
            if exempt or local in ("test", "your", "your-email"):
                continue
            if _allowed(line, "email"):
                continue
            findings.append(Finding("P1", "email", fname, lineno, mask(m.group(0))))
        birth_windows = [line]
        if lineno > 1 and any(p.search(line) for p in (
                BIRTH_DATE_RE, BIRTH_TIME_RE, BIRTH_GENDER_RE, BIRTH_PLACE_RE)):
            birth_windows.append(lines[lineno - 2] + " " + line)
        for window in birth_windows:
            if any(tok in window.lower() for tok in BIRTH_EXEMPT):
                continue
            if BIRTH_DATA_RE.search(window):
                findings.append(Finding("P1", "birth-data", fname, lineno, "<REDACTED>"))
                break
        for kind, pat in P2_PATTERNS:
            for m in pat.finditer(line):
                findings.append(Finding("P2", kind, fname, lineno, mask(m.group(0))))
    return findings


def _decode_text(data: bytes) -> str:
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16")
    for encoding in ("utf-8-sig", "gb18030"):
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            pass
    return data.decode("latin-1")


def scan_paths(paths, strict: bool = False):
    """扫描文件列表，返回 (退出码, 报告文本)。不可读文件失败关闭。"""
    findings = []
    unscanned = []
    for p in paths:
        p = Path(p)
        try:
            text = _decode_text(p.read_bytes())
        except OSError:
            unscanned.append(str(p))
            continue
        findings.extend(scan_lines(text.split('\n'), fname=str(p)))
    return _verdict(findings, strict, unscanned)


def _verdict(findings, strict: bool, unscanned=None):
    unscanned = unscanned or []
    lines = [f.render() for f in findings]
    lines.extend(f"{p}: [ERROR] unscanned" for p in unscanned)
    n0 = sum(1 for f in findings if f.level == "P0")
    n1 = sum(1 for f in findings if f.level == "P1")
    n2 = sum(1 for f in findings if f.level == "P2")
    lines.append(f"汇总: P0={n0} P1={n1} P2={n2}"
                 + ("（--strict 生效）" if strict else ""))
    blocking_p1 = sum(
        f.level == "P1" and f.kind != "birth-data" for f in findings)
    if unscanned:
        rc = 2
    elif n0 or blocking_p1:
        rc = 1
    elif n2 and strict:
        rc = 1
    else:
        rc = 0
    # 红线总断言：报告内不得残留任何命中原文（逐条已由 mask 断言兜底）
    return rc, "\n".join(lines) + "\n"


def _repo_root() -> str:
    proc = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("git rev-parse 失败: " + proc.stderr.decode("utf-8", "replace").strip())
    return proc.stdout.strip().decode("utf-8", "surrogateescape")


def _git_blob(root: str, spec: str, missing_ok: bool = False) -> str:
    proc = subprocess.run(["git", "cat-file", "--filters", spec],
                          cwd=root, capture_output=True)
    if proc.returncode != 0:
        if missing_ok:
            return ""
        raise RuntimeError("读取 Git 内容失败: " + spec)
    return _decode_text(proc.stdout)


def _changed_lines(range_spec: str = None):
    root = _repo_root()
    if range_spec:
        old_ref, new_ref = range_spec.split("..", 1)
        args = ["diff", "--name-only", "-z", "--diff-filter=ACMRT", old_ref, new_ref]
    else:
        old_ref, new_ref = "HEAD", None
        args = ["diff", "--cached", "--name-only", "-z", "--diff-filter=ACMRT"]
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError("git diff 失败: " + proc.stderr.decode("utf-8", "replace").strip())
    per_file = {}
    for raw_path in proc.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = raw_path.decode("utf-8", "surrogateescape")
        old_text = _git_blob(root, f"{old_ref}:{path}", missing_ok=True)
        new_spec = f"{new_ref}:{path}" if new_ref else f":{path}"
        new_text = _git_blob(root, new_spec)
        old_lines, new_lines = old_text.split('\n'), new_text.split('\n')
        added = []
        matcher = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
        for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
            if tag in ("insert", "replace"):
                added.extend(new_lines[j1:j2])
        per_file[path] = added
    return per_file


def _all_files():
    root = _repo_root()
    lists = []
    for args in (["ls-files", "-z"], ["ls-files", "-z", "--others", "--exclude-standard"]):
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError("git ls-files 失败: " + proc.stderr.decode("utf-8", "replace").strip())
        lists.append(proc.stdout)
    return [os.path.join(root, raw.decode("utf-8", "surrogateescape"))
            for output in lists for raw in output.split(b"\0") if raw]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="脱敏脱密闸门：扫描凭证(P0)/隐私(P1)/本机路径(P2)，输出一律打码。")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true",
                      help="只扫暂存区新增行（默认，供 pre-commit hook 用）")
    mode.add_argument("--all", action="store_true",
                      help="全量审计：扫描全部已跟踪+未忽略文件")
    mode.add_argument("--range", metavar="OLD..NEW",
                      help="扫描提交范围的新增行（pre-push 用）")
    ap.add_argument("--strict", action="store_true",
                    help="P2 本机路径命中也返回退出码 1")
    ap.add_argument("paths", nargs="*", help="直接指定文件扫描（调试用途）")
    args = ap.parse_args(argv)

    try:
        if args.paths:
            rc, report = scan_paths(args.paths, strict=args.strict)
        elif args.all:
            rc, report = scan_paths(_all_files(), strict=args.strict)
        else:  # 默认 --staged；--range 走同一 Git 对象比较逻辑
            findings = []
            for fname, lines in _changed_lines(args.range).items():
                findings.extend(scan_lines(lines, fname=fname))
            rc, report = _verdict(findings, args.strict)
    except (RuntimeError, OSError, UnicodeError) as e:
        print(f"check_credentials: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"check_credentials: 闸门自身异常: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if rc == 1:
        report += ("修复指引：移除敏感串（改用环境变量/占位符），或确认其为测试假值后"
                   "按白名单形态（your-/sk-fake*/<REDACTED> 等）改写；"
                   "P2 本机路径改为相对路径或 __file__ 锚定。\n")
    elif rc == 2:
        report += "闸门自身异常或存在未扫描文件；请修复环境后重试，未执行内容扫描。\n"
    sys.stdout.write(report)
    return rc


if __name__ == "__main__":
    sys.exit(main())
