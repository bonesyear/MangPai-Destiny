import ast
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import build_book_index, check_doc_numbers, check_layering, check_typing_imports

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_book_index_missing_sources_preserves_existing(tmp_path, monkeypatch):
    docs = tmp_path / 'docs'
    docs.mkdir()
    index = docs / 'book-index.md'
    index.write_text('keep-existing-index', encoding='utf-8')
    monkeypatch.setattr(build_book_index, 'DOCS', docs)
    with pytest.raises(SystemExit) as exc:
        build_book_index.main()
    assert exc.value.code == 1
    assert index.read_text(encoding='utf-8') == 'keep-existing-index'
    assert not (docs / 'book-index').exists()


def test_typing_defaults_to_repo_root(tmp_path):
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / 'scripts' / 'check_typing_imports.py')],
        cwd=tmp_path, capture_output=True, text=True, encoding='utf-8', timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr
    assert '扫描 0 个文件' not in result.stdout


def test_typing_missing_path_fails(tmp_path, capsys):
    assert check_typing_imports.main([str(tmp_path / 'missing')]) == 2
    assert '路径不存在' in capsys.readouterr().err
    empty = tmp_path / 'empty'
    empty.mkdir()
    assert check_typing_imports.main([str(empty)]) == 1
    assert '扫描 0 个文件' in capsys.readouterr().err


def test_doc_numbers_checks_all_matching_declarations():
    readme = (REPO_ROOT / 'README.md').read_text(encoding='utf-8')
    kb = (REPO_ROOT / 'docs' / 'knowledge-base.md').read_text(encoding='utf-8')
    modules, passed = check_doc_numbers.parse_readme_headline(readme)
    collected, kb_passed = check_doc_numbers.parse_kb_pytest_line(
        check_doc_numbers.find_line(kb, '验证口径', 'collected'))
    actuals = {
        'collected': collected, 'passed': passed,
        'foundation': 2, 'objective': 27, 'subjective': 30,
        'modules_total': modules,
    }
    assert kb_passed == passed
    duplicate = ('\npython3 -m pytest mangpai/tests/ -q  '
                 '# 1 collected（1 passed + 0 xfailed）\n')
    results = check_doc_numbers.check_docs(readme, kb + duplicate, actuals)
    assert any(not r.ok and '§8 工具表' in r.location for r in results)


def _module_tree(tmp_path, monkeypatch):
    monkeypatch.setattr(check_layering, 'ROOT', str(tmp_path))
    (tmp_path / 'mangpai').mkdir()
    (tmp_path / 'mangpai' / 'engine.py').write_text('', encoding='utf-8')


def _write_module(root, relative, source):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding='utf-8')
    return path


def test_layering_resolves_root_and_relative_imports(tmp_path, monkeypatch):
    _module_tree(tmp_path, monkeypatch)
    path = _write_module(
        tmp_path, 'mangpai/objective/probe.py',
        'from mangpai import calc_mangpai_full\nfrom .. import engine\n')
    top, _ = check_layering._imports_of(str(path))
    assert 'mangpai' in top
    assert 'mangpai.engine' in top
    assert check_layering._layer_of_module('mangpai') == check_layering.LAYER_ENGINE


def test_layering_scans_dynamic_match_and_async_with_imports(tmp_path, monkeypatch):
    _module_tree(tmp_path, monkeypatch)
    path = _write_module(
        tmp_path, 'mangpai/objective/probe.py',
        '''import importlib
importlib.import_module('mangpai.engine')
__import__('mangpai.subjective.caiming')
async def f():
    async with resource:
        import mangpai.engine
match value:
    case _:
        import mangpai.engine
''')
    top, local = check_layering._imports_of(str(path))
    assert top.count('mangpai.engine') == 2
    assert 'mangpai.subjective.caiming' in top
    assert local == ['mangpai.engine']


@pytest.mark.skipif(not hasattr(ast, 'TryStar'), reason='当前 Python 不支持 except* 语法')
def test_layering_scans_try_star_imports(tmp_path, monkeypatch):
    _module_tree(tmp_path, monkeypatch)
    path = _write_module(
        tmp_path, 'mangpai/objective/probe.py',
        'try:\n    pass\nexcept* Exception:\n    import mangpai.engine\n')
    top, _ = check_layering._imports_of(str(path))
    assert top == ['mangpai.engine']


def test_layering_whitelist_only_allows_local_import(tmp_path, monkeypatch, capsys):
    _module_tree(tmp_path, monkeypatch)
    _write_module(tmp_path, 'mangpai/subjective/llm_channel.py',
                  'import mangpai.engine\n')
    with pytest.raises(SystemExit) as exc:
        check_layering.main()
    assert exc.value.code == 1
    assert '反向导入' in capsys.readouterr().out


def test_layering_detects_package_init_cycle(tmp_path, monkeypatch, capsys):
    _module_tree(tmp_path, monkeypatch)
    _write_module(tmp_path, 'mangpai/subjective/__init__.py', 'from . import foo\n')
    _write_module(tmp_path, 'mangpai/subjective/foo.py',
                  'from mangpai.subjective import foo\n')
    with pytest.raises(SystemExit) as exc:
        check_layering.main()
    assert exc.value.code == 1
    assert '顶层依赖环' in capsys.readouterr().out
