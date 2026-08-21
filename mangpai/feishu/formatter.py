"""compute_all dict → Markdown 结构化报告。

模板：八字 → 做功 → 层功 → 三维（财/官/职业）→ 婚姻 → 应期 → 一句话总结。
字段知识全部复用 narrative 的行函数（同一结论源，引擎零改动、不重抄字段）。
"""
from __future__ import annotations

from typing import Any, Dict

from mangpai.subjective.narrative import (
    _bazi_line, _caiming_line, _gongliang_line, _guanming_line, _hunyin_line,
    _yingqi_line, _zhiye_line, _zuogong_line,
)

# 免责声明（V4 P0-1）：引擎直出/LLM 叙述两路径尾部各带一行
DISCLAIMER = '\n命理分析仅供参考，不构成人生决策依据。'


def one_liner(r: Dict[str, Any]) -> str:
    """一句话总结：层功档 + 财档 + 官命档。"""
    gl, cm, gm = r.get('gongliang') or {}, r.get('caiming') or {}, r.get('guanming') or {}
    lvl = gm.get('level')
    grade = lvl.get('grade') if isinstance(lvl, dict) else lvl
    segs = [s for s in (
        gl.get('tier_name') or '',
        f"财{cm.get('tier')}" if cm.get('tier') else '',
        f"官{grade}" if gm.get('is_guanming') and grade else '',
    ) if s]
    return '，'.join(segs) or '普通格局'


def format_report(r: Dict[str, Any], meta: str = '') -> str:
    """引擎 dict → Markdown 报告。缺失维度静默跳过（引擎 _safe_compute 语义）。"""
    yq = r.get('yingqi') or r.get('yingqi_subj') or {}
    da = r.get('dayun_analysis') or {}
    la = r.get('liunian_analysis') or {}

    lines = [f"**八字** {_bazi_line(r)}" + (f"（{meta}）" if meta else '')]
    sections = [
        ('做功', [_zuogong_line(r.get('zuogong') or {})]),
        ('层功', [_gongliang_line(r.get('gongliang') or {})]),
        ('三维', [_caiming_line(r.get('caiming') or {}),
                  _guanming_line(r.get('guanming') or {}),
                  _zhiye_line(r.get('zhiye') or {})]),
        ('婚姻', [_hunyin_line(r.get('hunyin') or {})]),
        ('应期', [_yingqi_line(yq, da, la)]),
    ]
    for title, rows in sections:
        rows = [x for x in rows if x]
        if rows:
            lines.append(f"\n**{title}**")
            lines.extend(f'· {x}' for x in rows)
    lines.append(f"\n**一句话**：{one_liner(r)}")
    lines.append(DISCLAIMER)
    return '\n'.join(lines)
