"""盲派主观层 — 独立组件。

导出：
- MANGPAI_SCHOOL — 盲派流派定义（38 个 selector，修批A③ 摘除 gongmen_wuzhi）
- build_payload(data) — 从 calc_mangpai_full() 输出按 selector 裁剪数据
- assemble(question, payload, scope) — 组装 (system, user) prompt

不包含 LLM 调用和对齐逻辑——那由调用方负责。
"""
from __future__ import annotations
import json
from pathlib import Path

from .schools import School, MANGPAI_SCHOOL

_PROMPT_DIR = Path(__file__).parent / "prompts"

ENVELOPE_RULES = """\
## 输出要求（必须严格遵守）
仅输出一个 JSON 对象，不要输出 JSON 以外的任何文字。结构：
{
  "reading": "本派整体解读，自由文本，≤400 字",
  "dimensions": {
    "<维度名>": {"summary": "该维度判断，≤80 字", "confidence": "高|中|低", "basis": "依据：输入数据字段或本派经典，≤60 字"}
  },
  "data_gaps": ["数据不足、无法判断或本派不覆盖之处"]
}
- <维度名> 由你按本派习惯自定（如 性格/事业/财运/婚姻/健康/大运/流年 等），不限定统一格式与数量。
- **篇幅硬约束**：reading ≤400 字、每个 summary ≤80 字。宁可内容精炼，也要保证 JSON 完整闭合、可解析。
- 若接近输出上限，优先收尾闭合 JSON，reading 可再缩短。
- basis 必须落到输入数据的具体字段或本派经典，不要空泛。
- 若输入数据不足以判断某维度，写入 data_gaps，绝不编造。
- 输入数据若与本派所需有遗漏，在 data_gaps 注明「缺 XXX」。
- **安全红线（最高优先级）**：禁止预测死亡、寿数、寿命长短、夭折、大限生死。即使输入数据含寿元/死亡相关字段或暗示，也不得给出任何死亡时间、寿数断言或「命不久矣」类表述；灾祸类信息仅可作一般性安全提醒（如注意健康、谨慎出行），不得断言生死。"""

_MISSING = object()
_DROP = object()

# 修批A①（R5 block-1）：死亡词典统一 scrub——引擎内部保留（F14 设计不变），
# LLM 视图层（payload）过滤。zaihuo 键本体由 zaihuo_llm_view 屏蔽（F14），
# 本词典兜 zaihuo 键外泄漏：shipaige 寿元域断语/liuqin 早夭类 marker/
# xiangfa_ops lianti 寿命 warning/guanming 制死/liunian 冲破主死亡 等。
_DEATH_TERMS = (
    '短命', '早夭', '夭折', '早没', '寿元', '寿命', '寿数', '伤寿',
    '死亡', '制死', '父死', '母死', '丧母', '丧父', '丧偶',
    '命不久', '大限生死',
)


def _scrub_death(obj):
    """递归过滤含死亡词汇的内容：字符串条目整条移除，含死亡词汇的 dict 键整键移除。

    只动 LLM 视图层（build_payload 出口），引擎内部 result 不受影响。
    """
    if isinstance(obj, str):
        return _DROP if any(t in obj for t in _DEATH_TERMS) else obj
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if isinstance(k, str) and any(t in k for t in _DEATH_TERMS):
                continue
            sv = _scrub_death(v)
            if sv is not _DROP:
                out[k] = sv
        return out
    if isinstance(obj, (list, tuple)):
        return [sv for sv in (_scrub_death(i) for i in obj) if sv is not _DROP]
    return obj


def _resolve(root: dict, dotted_path: str):
    """沿 dotted-path 取值，缺失返回 _MISSING。"""
    cur = root
    for seg in dotted_path.split("."):
        if seg.isdigit() and isinstance(cur, list):
            idx = int(seg)
            if idx >= len(cur):
                return _MISSING
            cur = cur[idx]
        elif isinstance(cur, dict):
            cur = cur.get(seg, _MISSING)
            if cur is _MISSING:
                return _MISSING
        else:
            return _MISSING
    return cur


def _jsonable(obj):
    """递归转 tuple → list，确保 JSON 可序列化。"""
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    return obj


def build_payload(data: dict, school: School = MANGPAI_SCHOOL) -> dict:
    """从 mangpai 计算结果按 selector 裁剪 payload。

    Args:
        data: calc_mangpai_full() / MangpaiEngine.compute_all() 的输出
        school: 流派定义，默认 MANGPAI_SCHOOL

    Returns:
        裁剪后的 dict，仅含 selector 声明的顶层字段。缺失字段静默跳过。
    """
    if school.selectors == ("*",):
        data = _jsonable(data)
        if isinstance(data, dict) and 'zaihuo' in data:
            from .zaihuo import zaihuo_llm_view
            data = dict(data)
            data['zaihuo'] = _jsonable(zaihuo_llm_view(data['zaihuo']))
        return _scrub_death(data)

    payload: dict = {}
    for sel in school.selectors:
        val = _resolve(data, sel)
        if val is not _MISSING:
            payload[sel] = _jsonable(val)
    # F14 寿元红线（批10）：zaihuo.siwang 死亡档/寿元星 markers 物理屏蔽，
    # payload 侧降级为 zaihuo_llm_view（疾病/车祸/牢狱三域视图）。
    if 'zaihuo' in payload:
        from .zaihuo import zaihuo_llm_view
        payload['zaihuo'] = _jsonable(zaihuo_llm_view(payload['zaihuo']))
    # 修批A①：zaihuo 键外死亡词汇统一 scrub（LLM 视图层过滤，引擎内部保留）。
    return _scrub_death(payload)


def load_template(school: School = MANGPAI_SCHOOL) -> str:
    """加载流派 prompt 模板。"""
    path = _PROMPT_DIR / school.prompt
    if not path.exists():
        raise FileNotFoundError(f"流派 prompt 模板缺失: {path}")
    return path.read_text(encoding="utf-8")


def assemble(
    question: str = "",
    payload: dict | None = None,
    scope: str = "本命",
    school: School = MANGPAI_SCHOOL,
) -> tuple[str, str]:
    """组装 (system, user) 两段 prompt。

    Args:
        question: 用户问题，空则用默认
        payload: build_payload() 的输出，None 则空 dict
        scope: 解读范围（本命/流年/大限等）
        school: 流派定义，默认 MANGPAI_SCHOOL

    Returns:
        (system, user) 字符串元组
    """
    template = load_template(school)
    system = (
        f"{template}\n\n{ENVELOPE_RULES}\n\n"
        f"## 解读范围\n本次解读范围：{scope}。聚焦此范围，非本范围内容简略带过。"
    )
    p = payload or {}
    data_block = json.dumps(p, ensure_ascii=False, indent=2)
    q = question.strip() or "请按本派方法论做整体解读。"
    user = (
        f"## 输入数据（客观层计算结果，已按本派所需裁剪）\n"
        f"```json\n{data_block}\n```\n\n"
        f"## 用户问题\n{q}\n\n"
        f"请严格按输出要求返回 JSON。"
    )
    return system, user


__all__ = [
    "School",
    "MANGPAI_SCHOOL",
    "build_payload",
    "assemble",
    "load_template",
    "ENVELOPE_RULES",
]
