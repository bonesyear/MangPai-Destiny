"""盲派主观层 — 独立组件。

导出：
- MANGPAI_SCHOOL — 盲派流派定义（39 个 selector，D6b 追加 zinv）
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

# D3 补供（2026-08-19，任务书 docs/tasks/kimi-d3-dayun-batch-20260819.md）：
# dayun_analysis 死 selector 修复。断裂点=LLM 批跑/评估路径的 bazi_data 仅带
# bazi+gender+year（无 da_yun 键）→ engine.py `if dy_list:` 不成立 →
# compute_all 不产出该键 → selector 声明静默落空（T3 §A.1：281/281 缺失，
# LLM 全程零大运表）。此处按年干阴阳+性别+月柱合成大运干支序列（方向/序列
# 为确定性计算，不需节气），过 analyze_dayun_mangpai 补进 payload。
# 仅 LLM 视图层补供，engine compute_all 输出不变（判定零影响、盲测零翻转）。

# 每运保留字段（LLM 引用形状：干支/起止/十神/吉凶信号/事件锚），与
# prompts/mangpai.md 的 dayun_analysis.* 引用对齐；剥掉的
# gan_relations/tiyong_import/has_* 布尔/desc 为检测中间件或信号复述。
_DAYUN_KEEP = ('gz', 'order', 'start_age', 'end_age', 'gan_shishen',
               'zhi_relations', 'work_types', 'tomb_effect',
               'fei_shen_activated', 'lu_blade', 'changsheng',
               'qishi_change', 'is_kong_wang',
               'positive_signals', 'negative_signals', 'overall')

_MALE = ('男', 'male', '乾')
_FEMALE = ('女', 'female', '坤')


def _trim_dayun(analysis):
    """dayun_analysis → 按 _DAYUN_KEEP 投影（真实/合成两路径统一形状）。"""
    if not isinstance(analysis, dict):
        return analysis
    out = {k: v for k, v in analysis.items() if k != 'dayun'}
    out['dayun'] = [{k: d[k] for k in _DAYUN_KEEP if k in d}
                    for d in analysis.get('dayun') or []]
    return out


def _synthesize_dayun(data: dict):
    """bazi-only 输入（engine 未产出 dayun_analysis）时补供；无法判向返回 None。

    起运岁数需精确出生月日时刻（compute_da_yun 对节气），bazi-only 输入不可得，
    故合成结果的每运无 start_age/end_age，以 order（第 N 步）为锚并附 age_note。
    """
    bazi = data.get('bazi') or {}
    try:
        gans = [bazi[k][0] for k in ('year', 'month', 'day', 'hour')]
        zhis = [bazi[k][1] for k in ('year', 'month', 'day', 'hour')]
    except (KeyError, IndexError, TypeError):
        return None
    gender = (data.get('input') or {}).get('gender') or ''
    if gender not in _MALE + _FEMALE:
        return None

    from mangpai.objective.dayun import dayun_gz_sequence
    from .dayun import analyze_dayun_mangpai

    seq = dayun_gz_sequence(gans[0], bazi['month'], gender in _MALE)
    analysis = analyze_dayun_mangpai(
        seq['dayun'], gans, zhis, gans[2],
        natal_fei_shen=(data.get('zuogong') or {}).get('fei_shen'),
        kong_wang=data.get('kong_wang'),
    )
    dy = _trim_dayun(analysis)['dayun']
    for d in dy:  # 合成序列无起运岁（缺精确出生时刻），剥缺省 0 防误锚
        d.pop('start_age', None)
        d.pop('end_age', None)
    best = next((d for d in dy if d['overall'] == '吉'), None)
    worst = next((d for d in dy if d['overall'] == '凶'), None)
    parts = [f"共{len(dy)}步大运（{seq['direction']}排）"]
    if analysis['ji_count']:
        parts.append(f"吉运{analysis['ji_count']}步")
    if analysis['xiong_count']:
        parts.append(f"凶运{analysis['xiong_count']}步")
    if analysis['banfeng_count']:
        parts.append(f"吉凶参半{analysis['banfeng_count']}步")
    if best:
        parts.append(f"最吉：{best['gz']}(第{best['order']}步)")
    if worst:
        parts.append(f"最凶：{worst['gz']}(第{worst['order']}步)")
    return {
        'direction': seq['direction'],
        'age_note': '起运岁数需精确出生月日时刻，本表仅干支序列（order=第N步），无年龄锚',
        'dayun': dy,
        'ji_count': analysis['ji_count'],
        'xiong_count': analysis['xiong_count'],
        'banfeng_count': analysis['banfeng_count'],
        'summary': '；'.join(parts),
    }

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
    # D3 补供：dayun_analysis——真实产出统一投影形状；engine 未产出时合成补供。
    if 'dayun_analysis' in school.selectors:
        if 'dayun_analysis' in payload:
            payload['dayun_analysis'] = _trim_dayun(payload['dayun_analysis'])
        else:
            syn = _synthesize_dayun(data)
            if syn is not None:
                payload['dayun_analysis'] = syn
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
