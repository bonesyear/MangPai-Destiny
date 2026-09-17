# -*- coding: utf-8 -*-
"""原子写工具（H-fix-3）：统一「写 .tmp + fsync + os.replace」模式。

覆盖 H6/H7/H9/H10 标记的写回点（基线/快照/索引/管线产物/诊断 dump）：
中断或写入异常时目标文件不被破坏（至多残留 .tmp），杜绝半写基线。
基线类写回用 backup=True 留存旧版 .bak，并配 validate 回调做写入前校验
（反解析 + 关键字段非空），不通过则拒绝写入。
"""
import json
import os
import shutil


def atomic_write(path, content, *, encoding='utf-8', backup=False):
    """原子写文本；backup=True 且目标已存在时先把旧文件复制为 path+'.bak'。"""
    path = os.fspath(path)
    if backup and os.path.exists(path):
        shutil.copy2(path, path + '.bak')
    tmp = path + '.tmp'
    with open(tmp, 'w', encoding=encoding) as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def atomic_write_json(path, obj, *, validate=None, backup=False,
                      ensure_ascii=False, indent=1, encoding='utf-8'):
    """JSON 原子写 + 写入前校验：内容可反解析；validate(parsed) 抛错则拒绝写入。"""
    content = json.dumps(obj, ensure_ascii=ensure_ascii, indent=indent)
    parsed = json.loads(content)
    if validate is not None:
        validate(parsed)
    atomic_write(path, content, encoding=encoding, backup=backup)
