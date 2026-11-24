from types import SimpleNamespace

from scripts import check_doc_links


def test_repo_has_no_dead_doc_links():
    assert check_doc_links.find_dead_links() == []


def test_dead_link_detector_and_history_exclusion(tmp_path, monkeypatch):
    (tmp_path / 'target.md').write_text('target', encoding='utf-8')
    (tmp_path / 'good.md').write_text(
        '[ok](target.md)\n[old](missing.md)\n', encoding='utf-8')
    (tmp_path / 'history.md').write_text(
        '<!-- doc-links:ignore -->\n历史路径未公开：missing-history.md\n', encoding='utf-8')
    monkeypatch.setattr(check_doc_links.subprocess, 'run', lambda *args, **kwargs:
                        SimpleNamespace(stdout='good.md\nhistory.md\n'))
    assert check_doc_links.find_dead_links(tmp_path) == [('good.md', 2, 'missing.md')]
