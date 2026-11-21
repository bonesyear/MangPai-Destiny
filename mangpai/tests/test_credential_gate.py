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


class TestBirthData:
    _DATE = '2000-01-' + '01'

    def test_datetime_gender_city_hits_p1(self, gate, tmp_path):
        line = f'阳历 {self._DATE} 12:00 男 北京'
        findings = gate.scan_lines([line], fname='t.md')
        assert any(f.level == 'P1' and f.kind == 'birth-data' for f in findings)
        f = tmp_path / 'birth.txt'
        f.write_text(line + '\n', encoding='utf-8')
        rc, out = gate.scan_paths([f])
        assert rc == 0 and 'birth-data' in out

    def test_adjacent_lines_hit_p1(self, gate):
        findings = gate.scan_lines(
            [f'阳历 {self._DATE} 12:00', '男 北京'], fname='t.md')
        assert any(f.level == 'P1' and f.kind == 'birth-data' for f in findings)

    def test_synthetic_marker_passes(self, gate):
        findings = gate.scan_lines(
            ['阳历 2000-01-01 12:00 男 北京  # synthetic'], fname='t.md')
        assert not any(f.kind == 'birth-data' for f in findings)


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
        assert "[P2] abs-path-root" in out

    def test_p2_strict_exit_1(self, gate, tmp_path):
        f = tmp_path / "b.py"
        f.write_text("p = '/Users/somebody/project'\n", encoding="utf-8")
        rc, out = gate.scan_paths([f], strict=True)
        assert rc == 1
        assert "[P2] abs-path-macos-user" in out

    def test_home_of_real_user_is_p2(self, gate, tmp_path):
        import getpass
        f = tmp_path / "c.sh"
        f.write_text(f"cd /home/{getpass.getuser()}/work\n", encoding="utf-8")
        findings = gate.scan_paths([f], strict=False)[1]
        assert "[P2] abs-path-home-user" in findings


class TestStagedMode:
    """用临时 git 仓库验证暂存区拦截行为（存量不干扰）。"""

    def _repo(self, tmp_path):
        subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        return tmp_path

    def _run_gate(self, repo, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--staged", *args],
            cwd=repo, capture_output=True, text=True,
            encoding="utf-8", errors="replace")  # Windows 管道里混入 UTF-8 字节时 locale 解码会炸

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


class TestExtendedPatterns:
    @pytest.mark.parametrize('line', [
        f'FEISHU_APP_SECRET={FAKE_ARK[4:]}',
        f'OPENAI_API_KEY=sk-proj-{FAKE_ARK[4:]}',
        f'ANTHROPIC_API_KEY=sk-ant-api03-{FAKE_ARK[4:]}',
        f'GITHUB_TOKEN=ghs_{FAKE_ARK[4:]}',
        f'app_secret="{FAKE_ARK[4:]}"',
    ])
    def test_new_secret_shapes_hit(self, gate, line):
        assert any(f.level == 'P0' for f in gate.scan_lines([line], fname='t.env'))

    @pytest.mark.parametrize('suffix', ['# your-key', '# TODO xxx', '# ***'])
    def test_nearby_placeholder_does_not_exempt(self, gate, suffix):
        line = f'key = "{FAKE_SK}" {suffix}'
        assert any(f.level == 'P0' for f in gate.scan_lines([line], fname='t.py'))
        line = f'phone={FAKE_PHONE} {suffix}'
        assert any(f.level == 'P1' for f in gate.scan_lines([line], fname='t.py'))

    @pytest.mark.parametrize('word', ['spark-submit', 'dark-themes'])
    def test_ark_requires_word_boundary(self, gate, word):
        assert not any(f.kind == 'volcengine-ark-key'
                       for f in gate.scan_lines([word], fname='t.md'))


class TestPrivacyFormats:
    @pytest.mark.parametrize('line', [
        '联系邮箱zhangsan@real-domain.cn',  # credscan: allow-email
        '请发至lisi@real-domain.cn获取',  # credscan: allow-email
        'dev@latest.io',  # credscan: allow-email
        '联系人 yourong@real-domain.cn',  # credscan: allow-email
    ])
    def test_email_boundaries_and_exemptions(self, gate, line):
        assert any(f.kind == 'email' for f in gate.scan_lines([line], fname='t.md'))

    @pytest.mark.parametrize('line', [
        f'tel:+86{FAKE_PHONE}',
        f'tel:{FAKE_PHONE[:3]}-{FAKE_PHONE[3:7]}-{FAKE_PHONE[7:]}',
        f'tel:{FAKE_PHONE[:3]} {FAKE_PHONE[3:7]} {FAKE_PHONE[7:]}',
    ])
    def test_mobile_formats(self, gate, line):
        assert any(f.kind == 'cn-mobile' for f in gate.scan_lines([line], fname='t.md'))


class TestRobustInputs:
    @pytest.mark.parametrize('encoding', ['utf-16', 'gb18030'])
    def test_encoded_files_are_not_skipped(self, gate, tmp_path, encoding):
        f = tmp_path / f'{encoding}.txt'
        f.write_text(f'中文注释\napi_key={FAKE_SK}\n', encoding=encoding)
        rc, out = gate.scan_paths([f])
        assert rc == 1 and 'P0' in out

    def test_getuser_failure_does_not_break_import(self, monkeypatch):
        import getpass
        monkeypatch.setattr(getpass, 'getuser', lambda: (_ for _ in ()).throw(OSError()))
        gate = _load_mod()
        assert gate.scan_lines([f'key={FAKE_SK}'], fname='t.py')

    def test_all_from_subdirectory_and_unicode_name(self, tmp_path):
        repo = TestStagedMode()._repo(tmp_path)
        (repo / 'sub').mkdir()
        (repo / '笔记.md').write_text(f'tel={FAKE_PHONE}\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
        r = subprocess.run([sys.executable, str(SCRIPT), '--all'], cwd=repo / 'sub',
                           capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert r.returncode == 1 and 'P1=1' in r.stdout

    @pytest.mark.parametrize('kind', ['nodiff', 'external', 'u2028'])
    def test_staged_bypasses_closed(self, tmp_path, kind):
        repo = TestStagedMode()._repo(tmp_path)
        name = 'config.yaml' if kind == 'nodiff' else 'notes.txt'
        text = f'note: see below\u2028api_key={FAKE_SK}' if kind == 'u2028' else f'api_key={FAKE_SK}'
        (repo / name).write_text(text, encoding='utf-8')
        if kind == 'nodiff':
            (repo / '.gitattributes').write_text('*.yaml -diff\n', encoding='utf-8')
            subprocess.run(['git', 'add', '.gitattributes'], cwd=repo, check=True)
        if kind == 'external':
            subprocess.run(['git', 'config', 'diff.external', 'echo'], cwd=repo, check=True)
        subprocess.run(['git', 'add', name], cwd=repo, check=True)
        r = TestStagedMode()._run_gate(repo)
        assert r.returncode == 1 and 'P0' in r.stdout


class TestHookChain:
    def _install(self, repo):
        import shutil
        (repo / 'scripts').mkdir()
        for name in ('check_credentials.py', 'install_git_hooks.sh'):
            shutil.copy2(REPO_ROOT / 'scripts' / name, repo / 'scripts' / name)
        bash = shutil.which('bash')
        if not bash:
            pytest.skip('bash unavailable')
        env = dict(os.environ, MANGPAI_PYTHON=sys.executable)
        return subprocess.run([bash, 'scripts/install_git_hooks.sh'], cwd=repo,
                              env=env, capture_output=True, text=True), env

    def test_existing_hook_is_not_overwritten(self, tmp_path):
        repo = TestStagedMode()._repo(tmp_path)
        (repo / '.git' / 'hooks' / 'pre-commit').write_text('# custom\n', encoding='utf-8')
        r, _env = self._install(repo)
        assert r.returncode == 1
        assert (repo / '.git' / 'hooks' / 'pre-commit').read_text() == '# custom\n'

    def test_pre_push_scans_incoming_commit_range(self, tmp_path):
        repo = TestStagedMode()._repo(tmp_path)
        r, env = self._install(repo)
        assert r.returncode == 0, r.stdout + r.stderr
        subprocess.run(['git', 'config', 'user.email', 't@example.com'], cwd=repo, check=True)
        subprocess.run(['git', 'config', 'user.name', 't'], cwd=repo, check=True)
        (repo / 'ok.txt').write_text('ok\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
        subprocess.run(['git', 'commit', '-qm', 'init'], cwd=repo, env=env, check=True)
        old = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        (repo / 'bad.txt').write_text(f'key={FAKE_SK}\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.'], cwd=repo, check=True)
        subprocess.run(['git', 'commit', '--no-verify', '-qm', 'incoming'], cwd=repo, check=True)
        new = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=repo, text=True).strip()
        import shutil
        pushed = subprocess.run(
            [shutil.which('bash'), str(repo / '.git' / 'hooks' / 'pre-push')],
            cwd=repo, env=env, input=f'refs/heads/main {new} refs/heads/main {old}\n',
            capture_output=True, text=True, encoding='utf-8', errors='replace')
        assert pushed.returncode == 1, pushed.stdout + pushed.stderr
        assert 'P0' in pushed.stdout + pushed.stderr


class TestStagedSpecialContent:
    def test_utf16_staged_blob(self, tmp_path):
        repo = TestStagedMode()._repo(tmp_path)
        (repo / 'utf16.txt').write_text(f'api_key={FAKE_SK}\n', encoding='utf-16')
        subprocess.run(['git', 'add', 'utf16.txt'], cwd=repo, check=True)
        r = TestStagedMode()._run_gate(repo)
        assert r.returncode == 1 and 'P0' in r.stdout

    def test_lfs_smudged_blob(self, tmp_path):
        import shutil
        if not shutil.which('git-lfs'):
            pytest.skip('git-lfs unavailable')
        repo = TestStagedMode()._repo(tmp_path)
        subprocess.run(['git', 'lfs', 'install', '--local'], cwd=repo, check=True,
                       capture_output=True)
        (repo / '.gitattributes').write_text('*.env filter=lfs diff=lfs merge=lfs -text\n',
                                             encoding='utf-8')
        (repo / 'secret.env').write_text(f'api_key={FAKE_SK}\n', encoding='utf-8')
        subprocess.run(['git', 'add', '.gitattributes', 'secret.env'], cwd=repo, check=True)
        r = TestStagedMode()._run_gate(repo)
        assert r.returncode == 1 and 'P0' in r.stdout
