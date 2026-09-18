"""脱敏闸门 check_credentials.py 哨兵测试（先红后绿）。

红线：本文件只使用合成假值，绝不含真实凭证。
"""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_credentials.py"


def _load_mod():
    spec = importlib.util.spec_from_file_location("check_credentials", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# 合成假值（非真实凭证，仅形态同构）
FAKE_ARK = "ark-" + "Ab1Cd2Ef3Gh4Ij5Kl6Mn7Op8Qr9St0Uv"  # 32 位假串
FAKE_SK = "sk-" + "Zx9Yw8Vu7Ts6Rq5Po4Nm3Lk2Jh1Gf0Ed"  # 32 位假串
FAKE_PHONE = "138" + "00138000"  # 经典测试号段（拼接写法避免闸门误伤本文件）
FAKE_BEARER = "Bearer " + "Qq1Ww2Ee3Rr4Tt5Yy6Uu7Ii8"


@pytest.fixture()
def gate():
    return _load_mod()


class TestP0Block:
    def test_fake_ark_hits_p0(self, gate):
        findings = gate.scan_lines([f'key = "{FAKE_ARK}"'], fname="t.py")
        assert any(f.level == "P0" for f in findings)

    def test_fake_sk_hits_p0(self, gate):
        findings = gate.scan_lines([f'token="{FAKE_SK}"'], fname="t.py")
        assert any(f.level == "P0" for f in findings)

    def test_bearer_hits_p0(self, gate):
        findings = gate.scan_lines([f"auth = '{FAKE_BEARER}'"], fname="t.py")
        assert any(f.level == "P0" for f in findings)

    def test_p0_exit_code_1(self, gate, tmp_path):
        f = tmp_path / "a.txt"
        f.write_text(f"api_key={FAKE_ARK}\n", encoding="utf-8")
        rc, out = gate.scan_paths([f], strict=False)
        assert rc == 1
        assert "P0" in out


class TestWhitelist:
    @pytest.mark.parametrize("line", [
        "api_key = 'your-api-key-here'",
        "key='sk-xxx'",
        "token = 'sk-fake0000000000000000000000'",
        "example: ark-[A-Za-z0-9]{6,} 是扫描模式描述",
        "邮箱 test@example.com 或 admin@example.org",
        "host = '127.0.0.1' or 'localhost' or '192.168.1.1' or '10.0.0.8'",
        "old_key = '<REDACTED>'",
    ])
    def test_placeholders_pass(self, gate, line):
        findings = [f for f in gate.scan_lines([line], fname="t.md")
                    if f.level in ("P0", "P1")]
        assert findings == [], f"误报: {findings}"


class TestMasking:
    def test_mask_never_contains_full(self, gate):
        for secret in (FAKE_ARK, FAKE_SK, FAKE_BEARER, FAKE_PHONE):
            masked = gate.mask(secret)
            assert secret not in masked, f"打码失败泄漏原文: {masked}"

    def test_mask_shape(self, gate):
        masked = gate.mask(FAKE_ARK)
        assert masked.startswith(FAKE_ARK[:4])
        assert masked.endswith(FAKE_ARK[-2:])
        assert len(masked) < len(FAKE_ARK)

    def test_short_value_fully_redacted(self, gate):
        assert gate.mask("abc") == "<REDACTED>"


class TestLocalPathP2:
    def test_p2_warn_exit_0(self, gate, tmp_path):
        f = tmp_path / "b.py"
        f.write_text("sys.path.insert(0, '/root/somewhere/x')\n", encoding="utf-8")
        rc, out = gate.scan_paths([f], strict=False)
        assert rc == 0
        assert "P2" in out

    def test_p2_strict_exit_1(self, gate, tmp_path):
        f = tmp_path / "b.py"
        f.write_text("p = '/Users/somebody/project'\n", encoding="utf-8")
        rc, out = gate.scan_paths([f], strict=True)
        assert rc == 1

    def test_home_of_real_user_is_p2(self, gate, tmp_path):
        import getpass
        f = tmp_path / "c.sh"
        f.write_text(f"cd /home/{getpass.getuser()}/work\n", encoding="utf-8")
        findings = gate.scan_paths([f], strict=False)[1]
        assert "P2" in findings


class TestStagedMode:
    """用临时 git 仓库验证暂存区拦截行为（存量不干扰）。"""

    def _repo(self, tmp_path):
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        return tmp_path

    def _run_gate(self, repo, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--staged", *args],
            cwd=repo, capture_output=True, text=True)

    def test_staged_clean_passes(self, tmp_path):
        repo = self._repo(tmp_path)
        (repo / "ok.py").write_text("x = 'your-key-here'\n", encoding="utf-8")
        subprocess.run(["git", "add", "ok.py"], cwd=repo, check=True)
        r = self._run_gate(repo)
        assert r.returncode == 0, r.stdout + r.stderr

    def test_staged_secret_blocked(self, tmp_path):
        repo = self._repo(tmp_path)
        (repo / "bad.py").write_text(f"key = '{FAKE_ARK}'\n", encoding="utf-8")
        subprocess.run(["git", "add", "bad.py"], cwd=repo, check=True)
        r = self._run_gate(repo)
        assert r.returncode == 1
        assert FAKE_ARK not in r.stdout + r.stderr, "输出泄漏完整敏感串"

    def test_staged_existing_secret_unstaged_ignored(self, tmp_path):
        """存量（已提交）的敏感串不干扰；只看新增行。"""
        repo = self._repo(tmp_path)
        f = repo / "old.py"
        f.write_text(f"key = '{FAKE_ARK}'\n", encoding="utf-8")
        subprocess.run(["git", "add", "old.py"], cwd=repo, check=True)
        subprocess.run(["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
                        "commit", "-qm", "init"], cwd=repo, check=True)
        # 追加一行干净内容并暂存：存量敏感行不应触发拦截
        with open(f, "a", encoding="utf-8") as fh:
            fh.write("clean = 1\n")
        subprocess.run(["git", "add", "old.py"], cwd=repo, check=True)
        r = self._run_gate(repo)
        assert r.returncode == 0, r.stdout + r.stderr
