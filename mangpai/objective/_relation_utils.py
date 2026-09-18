# -*- coding: utf-8 -*-
"""_relation_utils - objective 层关系判定公共小工具（H-fix-4b 下沉统一）。

原 `_check_pair` 在 objective 层 zuogong_detect/dayun/gongshen 三处复制、
muku 以 _is_chong/_is_he/_is_xing 特化复制、subjective/liunian 两处函数内
局部复制——六处逐字等价（差异分析见 docs/tasks/codehygiene-fix-backlog.md
H-fix-4b 节），统一为 pair_in 单一实现。
"""


def pair_in(a: str, b: str, pairs) -> bool:
    """双向判定 (a,b) 是否属于 pairs。"""
    return (a, b) in pairs or (b, a) in pairs
