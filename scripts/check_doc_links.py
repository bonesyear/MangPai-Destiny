#!/usr/bin/env python3
"""检查已跟踪 Markdown 中的仓库相对文档/快照链接。"""
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH_RE = re.compile(r'(?:docs|mangpai|output|scripts|snapshots)/[^\s`\'"<>()\[\]，。；：、+「」;]*\.(?:md|json|py|sh|yaml|txt)')
LINK_RE = re.compile(r'\[[^\]]*\]\(([^)]+)\)')
SUFFIX_RE = re.compile(r'(?:#[^\s]*|:\d+(?:-\d+)?)$')


def _candidate(line):
    for match in LINK_RE.finditer(line):
        target = match.group(1).split()[0]
        if PATH_RE.fullmatch(target) or re.fullmatch(r'[^\s/]+\.md', target):
            yield target
    for match in PATH_RE.finditer(line):
        yield match.group(0)


def _exists(source, target, root):
    target = SUFFIX_RE.sub('', urllib.parse.unquote(target))
    if not target or target.startswith(('/', '~', '<')):
        return True
    direct = (source.parent / target).resolve()
    rooted = (root / target).resolve()
    if direct.exists() or rooted.exists():
        return True
    if target.startswith('snapshots/'):
        return (root / 'mangpai/tests/heldout' / target).exists()
    return False


def find_dead_links(root=ROOT):
    root = Path(root).resolve()
    listed = subprocess.run(
        ['git', 'ls-files', '*.md'], cwd=root, capture_output=True,
        text=True, encoding='utf-8', check=True)
    dead = []
    for name in listed.stdout.splitlines():
        source = root / name
        text = source.read_text(encoding='utf-8')
        if '<!-- doc-links:ignore -->' in text.splitlines()[:6]:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if '未公开' in line or '仅本地' in line:
                continue
            for target in _candidate(line):
                if target.startswith(('http://', 'https://', 'mailto:')):
                    continue
                if any(mark in target for mark in ('*', '{', 'YYYY', '上一批')):
                    continue
                if not _exists(source, target, root):
                    dead.append((name, lineno, target))
    return dead


def main():
    dead = find_dead_links()
    for name, lineno, target in dead:
        print(f'{name}:{lineno}: 失效路径 {target}')
    print(f'文档死链: {len(dead)}')
    return 1 if dead else 0


if __name__ == '__main__':
    sys.exit(main())
