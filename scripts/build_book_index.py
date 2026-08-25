#!/usr/bin/env python3
"""原著分章索引生成器（零 LLM，纯机械正则）

扫描 docs 下全部 txt 原著，提取章节标题 + 行号，生成索引文件。
用法: python3 scripts/build_book_index.py
"""
import re
import os
from pathlib import Path

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
    r'^\s*第[一二三四五六七八九十百千0-9]+[章篇部卷节]',  # 第X章/篇/部/卷/节
    r'^\s*[一二三四五六七八九十]+、\S{2,}',  # 一、标题（至少2字）
    r'^\s*[（(][一二三四五六七八九十]+[）)]\s*\S{2,}',  # （一）标题
    r'^\s*【[^】]{2,30}】',  # 【标题】
    r'^\s*\d+[、．.]\s*\S{2,}',  # 1、标题 / 1. 标题
]

# 噪音过滤：纯数字/过短/页码类
def is_noise(s):
    if re.fullmatch(r'[\d\s\W]+', s) or len(s) < 3:
        return True
    if re.fullmatch(r'[0-9]{1,4}', s):  # 纯页码
        return True
    if re.search(r'^\d{4}[-/年]', s):  # 日期开头
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
        per.write_text("\n".join(lines), encoding="utf-8")
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
    idx.write_text("\n".join(idx_lines), encoding="utf-8")
    print(f"\n总索引: {idx} | 分文件目录: {out_dir} | 共 {total_entries} 命中")

if __name__ == "__main__":
    main()
