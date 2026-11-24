import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize('script', [
    'check_layering.py', 'check_typing_imports.py', 'check_doc_links.py',
])
def test_repo_static_gates(script):
    result = subprocess.run(
        [sys.executable, str(ROOT / 'scripts' / script)],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', timeout=120)
    assert result.returncode == 0, result.stdout + result.stderr
