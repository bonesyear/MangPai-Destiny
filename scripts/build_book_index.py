#!/usr/bin/env python3
"""原著分章索引生成器（零 LLM，纯机械正则）

扫描 docs 下全部 txt 原著，提取章节标题 + 行号，生成索引文件。
用法: python3 scripts/build_book_index.py（需本地全部原著；任一缺失即退出且不写文件）
"""
import re
import os
import sys
from pathlib import Path

_TESTS = Path(__file__).resolve().parent.parent / "mangpai" / "tests"
if str(_TESTS) not in sys.path:
    sys.path.insert(0, str(_TESTS))
from _atomic_io import atomic_write

DOCS = Path(__file__).resolve().parent.parent / "mangpai" / "docs"

# (文件名, 显示名)
BOOKS = [
    ("duan-books/duan-shi-lixiangxue.txt", "理象学（duan-shi-lixiangxue）"),
    ("duan-books/duan-shi-lixiangxue-yanjiu.txt", "理象学研究（yanjiu 版）"),
    ("duan-books/mangpai-chuji-minglixue.txt", "初级命理学"),
    ("duan-books/mangpai-gaoji-ocr.txt", "高级（gaoji-ocr）"),
    ("duan-books/mangpai-zhongji.txt", "中级（zhongji）"),
    ("duan-books/shouke-jiaocheng.txt", "授课教程"),
    ("yuanhaiziping/yuanhai-mobi.txt", "渊海子平"),
    ("ziping-zhenquan-pdf.txt", "子平真诠（pdf 版）"),
    ("ziping-zhenquan-pingzhu.txt", "子平真诠评注"),
    ("ditianchansui/ditianchansui.txt", "滴天髓阐微（pdf 转 txt）"),
]

# 章节标题模式（中文书常见结构）
PATTERNS = [
    r'^\s*第[一二三四五六七八九十百千0-9]+[章篇部卷节讲]',
]

# 噪音过滤：纯数字/过短/页码类
def is_noise(s):
    if re.fullmatch(r'[\d\s\W]+', s) or len(s) < 3:
        return True
    if re.fullmatch(r'[0-9]{1,4}', s):  # 纯页码
        return True
    if re.search(r'^\d{4}[-/年]', s):  # 日期开头
        return True
    if re.search(r'[。；，]|眉批|yibooks', s):  # 正文句/眉批/水印不收
        return True
    return False

def scan(path: Path):
    hits = []
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or len(s) > 40 or is_noise(s):
            continue
        for p in PATTERNS:
            if re.match(p, s):
                hits.append((i, s[:40]))
                break
    return len(lines), hits

def main():
    missing = [rel for rel, _name in BOOKS if not (DOCS / rel).is_file()]
    if missing:
        print('原著缺失，未修改索引：')
        for rel in missing:
            print(f'  文件缺失: {rel}')
        sys.exit(1)
    out_dir = DOCS / "book-index"
    out_dir.mkdir(exist_ok=True)
    total_entries = 0
    for rel, name in BOOKS:
        path = DOCS / rel
        if not path.exists():
            print(f"  文件缺失: {rel}")
            continue
        total, hits = scan(path)
        # gaoji-ocr 命中爆炸（OCR 噪音）：只留 篇/章/节/讲 级
        if "gaoji-ocr" in rel:
            hits = [h for h in hits if re.search(r'第[一二三四五六七八九十百千0-9]+[篇章节讲]|篇[一二三四五六七八九十]{1,2}[:：]', h[1])]
        stem = rel.split("/")[-1].replace(".txt", "")
        per = out_dir / f"index-{stem}.md"
        lines = [f"# {name} 分章索引（机械生成）", f"文件: {rel} | 总行数: {total} | 命中: {len(hits)}", ""]
        if not hits:
            lines.append("（未识别到章节标题——标题格式特殊，需人工补充）")
        for lineno, title in hits:
            lines.append(f"{lineno:>7} | {title}")
        atomic_write(per, "\n".join(lines))
        total_entries += len(hits)
        print(f"  {per.name}: {len(hits)} 命中 / {total} 行")
    # 总索引（每书一行，指向分文件）
    idx = DOCS / "book-index.md"
    idx_lines = ["# 原著分章索引总表（机械生成，零 LLM）", ""]
    for rel, name in BOOKS:
        path = DOCS / rel
        if not path.exists():
            idx_lines.append(f"- {name}: 文件缺失")
            continue
        stem = rel.split("/")[-1].replace(".txt", "")
        idx_lines.append(f"- [{name}](book-index/index-{stem}.md)")
    atomic_write(idx, "\n".join(idx_lines))
    print(f"\n总索引: {idx} | 分文件目录: {out_dir} | 共 {total_entries} 命中")

if __name__ == "__main__":
    main()
