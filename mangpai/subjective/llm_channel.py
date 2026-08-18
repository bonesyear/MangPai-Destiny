"""LLM 结构化推演通道（方案 C 混合·升级 narrative 层）。

链路：引擎 dict → build_payload 特征抽取（selectors 38 键 + zaihuo_llm_view
+ 死亡词典 scrub，全复用）→ DeepSeek JSON mode 五维叙述 → 三层校验 → 展示。

**红线：本模块输出永不回写 compute_all() dict**；无 API key/调用失败时
降级返回组装好的 prompt 文本（同 narrative.render_hao_narrative 契约）。

三层校验（validate_reading）：
- L0 schema：五维键齐、conclusion/basis/confidence 结构合法；
- L1 出处：basis 每条路径回解析特征 JSON，不存在或为空 → 违规；
- L2 枚举：财命档位/官命是非回对引擎枚举值 + 死亡词黑名单兜底；
- N1 数字校验复用 narrative.validate_narrative_numbers（对白名单外数字留痕）。

单命示例：python3 -m mangpai.subjective.llm_channel
"""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from mangpai.subjective import build_payload, _resolve, _MISSING
from mangpai.subjective.llm_prompt import build_system_prompt, build_user_prompt
from mangpai.subjective.narrative import (
    _bazi_line,
    summarize_engine_result,
    validate_narrative_numbers,
)

DIMENSIONS = ('性格', '事业', '财运', '婚姻', '应期')
_CONFIDENCE = ('高', '中', '低')

# L2 财命档位序（index 大=高）。引擎双轨：tier_static 原局轨 + tier 全量轨，
# 措辞上限取两轨较高者（运中层级断语合法，v6 口径）。
_TIER_ORDER = ('贫', '平', '小康', '富', '巨富')

# L2 死亡词黑名单（兜底双保险之二；payload 已 scrub，此乃对 LLM 输出端）。
_DEATH_WORDS = ('死亡', '寿终', '享年', '夭折', '早夭', '短命',
                '命不久', '寿数', '寿命', '寿元', '大限生死')

# L2 官命正向断言关键词（仅在引擎 is_guanming=False 时拦截）。
# ponytail: 关键词回对是启发式，否定语境（「不是官命」）按前两字符窗口排除，
# 覆盖不了全部中文否定句式——语义级残留由 L1+人工兜底，见归档 §2.1。
_GUAN_POSITIVE = ('官命', '当官', '走仕途', '是官', '贵格', '掌大权')
_NEG_PREFIX = ('不', '非', '无', '难', '未', '莫')


def _l0_schema(data: Any) -> list:
    """L0 schema 校验，返回违规列表。"""
    v = []
    if not isinstance(data, dict):
        return [{'layer': 'L0', 'detail': '输出不是 JSON 对象'}]
    for dim in DIMENSIONS:
        node = data.get(dim)
        if not isinstance(node, dict):
            v.append({'layer': 'L0', 'detail': f'缺维度「{dim}」或非对象'})
            continue
        if not isinstance(node.get('conclusion'), str) or not node['conclusion'].strip():
            v.append({'layer': 'L0', 'detail': f'{dim}.conclusion 缺失或非字符串'})
        if not isinstance(node.get('basis'), list):
            v.append({'layer': 'L0', 'detail': f'{dim}.basis 缺失或非数组'})
        if node.get('confidence') not in _CONFIDENCE:
            v.append({'layer': 'L0', 'detail': f'{dim}.confidence 非法值: {node.get("confidence")!r}'})
    return v


def _l1_basis(data: dict, features: dict) -> list:
    """L1 依据路径解析：basis 每项须在特征 JSON 中可解析且非空。"""
    v = []
    for dim in DIMENSIONS:
        node = data.get(dim) or {}
        for path in node.get('basis') or []:
            if not isinstance(path, str):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 含非字符串项: {path!r}'})
                continue
            val = _resolve(features, path)
            if val is _MISSING or val is None or val == {} or val == [] or val == '':
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 路径无出处或为空: {path}'})
    return v


def _tier_rank(text: str) -> int:
    """文本中出现的最高财命档位（无则 -1）。巨富先于富匹配。"""
    for i in range(len(_TIER_ORDER) - 1, -1, -1):
        t = _TIER_ORDER[i]
        if t == '富':
            if '巨富' in text:
                continue  # 巨富已在上一轮命中
        if t in text:
            return i
    return -1


def _l2_enum(data: dict, engine_result: dict) -> list:
    """L2 枚举回对：财命档位不越引擎双轨上限；官命是非不反引擎；死亡词黑名单。"""
    v = []
    texts = {dim: str((data.get(dim) or {}).get('conclusion') or '')
             for dim in DIMENSIONS}

    # 死亡红线（所有维度）
    for dim, t in texts.items():
        for w in _DEATH_WORDS:
            if w in t:
                v.append({'layer': 'L2', 'detail': f'{dim} 触死亡红线词「{w}」'})

    # 财命档位
    cm = engine_result.get('caiming') or {}
    ceiling = max((_tier_rank(str(cm.get(k) or ''))
                   for k in ('tier_static', 'tier')), default=-1)
    got = _tier_rank(texts['财运'])
    if ceiling >= 0 and got > ceiling:
        v.append({'layer': 'L2',
                  'detail': f'财运档位越引擎上限：引擎={_TIER_ORDER[ceiling]}，叙述={_TIER_ORDER[got]}'})

    # 官命是非（引擎否 → 叙述不得正向断言）
    gm = engine_result.get('guanming') or {}
    if gm.get('is_guanming') is False:
        t = texts['事业']
        for w in _GUAN_POSITIVE:
            i = t.find(w)
            while i != -1:
                # 前两字符内出现否定词（不是/非/无缘…）则视为否定语境放行
                if not any(ch in _NEG_PREFIX for ch in t[max(0, i - 2):i]):
                    v.append({'layer': 'L2',
                              'detail': f'事业 与引擎官命=否矛盾：「{w}」'})
                    break
                i = t.find(w, i + 1)
    return v


def validate_reading(data: Any, features: dict, engine_result: dict) -> dict:
    """三层校验 + N1 数字校验，返回 {'ok', 'violations', 'n1'}。"""
    violations = _l0_schema(data)
    if isinstance(data, dict):
        violations += _l1_basis(data, features)
        violations += _l2_enum(data, engine_result)
    blob = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else str(data)
    n1 = validate_narrative_numbers(blob, engine_result)
    violations += [{'layer': 'N1',
                    'detail': f"「{x['text']}」({x['kind']}): {x['detail']}"}
                   for x in n1['violations']]
    return {'ok': not violations, 'violations': violations, 'n1': n1}


def format_reading(reading: dict, validation: dict, backend: dict) -> str:
    """成品展示文本。"""
    lines = []
    for dim in DIMENSIONS:
        node = (reading or {}).get(dim) or {}
        lines.append(f"【{dim}】({node.get('confidence', '?')}) {node.get('conclusion', '')}")
        if node.get('basis'):
            lines.append(f"  依据: {', '.join(str(b) for b in node['basis'])}")
    if validation and not validation['ok']:
        lines.append('')
        lines.append('【引擎校验】以下要点未通过三层校验（请人工复核，勿直采信）：')
        for x in validation['violations']:
            lines.append(f"  - [{x['layer']}] {x['detail']}")
    if backend:
        u = backend.get('usage') or {}
        lines.append('')
        lines.append(f"[model={backend.get('model')} "
                     f"in={u.get('prompt_tokens', '?')} out={u.get('completion_tokens', '?')} "
                     f"elapsed={backend.get('elapsed_s', 0):.1f}s "
                     f"cost≈${backend.get('cost_usd', 0):.4f}（≈¥{backend.get('cost_usd', 0) * 7.2:.3f}）]")
    return '\n'.join(lines)


def render_structured_reading(
    engine_result: Dict[str, Any],
    user_question: Optional[str] = None,
    *,
    call_llm: bool = True,
    model: str | None = None,
    validate: str = 'mark',
) -> str:
    """引擎 dict → DeepSeek 五维 JSON 叙述 → 三层校验 → 展示文本。

    validate: 'mark'(默认)=违规附注于成品后；'reject'=L0 不过则拦截；
    'off'=不校验。LLM 不可用时降级返回 prompt 文本（不抛错）。
    """
    from mangpai.subjective.prompts.hao_style_fewshot import (
        FEWSHOT_EXAMPLES, format_fewshot_block,
    )
    features = build_payload(engine_result)
    features_json = json.dumps(features, ensure_ascii=False, separators=(',', ':'))
    system = build_system_prompt(format_fewshot_block(FEWSHOT_EXAMPLES))
    user = build_user_prompt(features_json, _bazi_line(engine_result),
                             user_question or '')
    if not call_llm:
        return f"===== SYSTEM =====\n{system}\n\n===== USER =====\n{user}"

    from mangpai.subjective.llm_backend import call_deepseek, LLMBackendError
    try:
        resp = call_deepseek(system, user, model=model)
    except LLMBackendError as e:
        return (f"[LLM 不可用，降级返回 prompt 文本 | 原因: {e}]\n\n"
                f"===== SYSTEM =====\n{system}\n\n===== USER =====\n{user}")

    raw = resp['text']
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return f"[LLM 输出非合法 JSON，不予展示 | {e}]\n原始输出:\n{raw}"

    report = validate_reading(data, features, engine_result) if validate != 'off' \
        else {'ok': True, 'violations': []}
    if validate == 'reject' and any(x['layer'] == 'L0' for x in report['violations']):
        return ('[断语被 L0 schema 校验拦截，不予输出]\n'
                + '\n'.join(f"  - {x['detail']}" for x in report['violations']))
    return format_reading(data, report, resp)


def demo(case_id: str = 'b67-李嘉诚', question: str = ''):
    """单命示例：trainset 案例 → 引擎特征 → LLM 叙述 → 三层校验 → 展示。"""
    import yaml
    from mangpai.engine import MangpaiEngine
    cases_path = 'mangpai/tests/trainset/cases.yaml'
    with open(cases_path, encoding='utf-8') as f:
        cases = {c['id']: c for c in yaml.safe_load(f)}
    c = cases[case_id]
    bazi_data = {
        'bazi': dict(c['bazi']), 'shishen': {}, 'kong_wang': {},
        'di_zhi_relations': {},
        'input': {'gender': c.get('gender', '男'), 'year': c.get('year', 1960)},
    }
    res = MangpaiEngine(bazi_data).compute_all()
    print(f"===== 案例 {case_id} =====")
    print(f"引擎结论: {summarize_engine_result(res)}")
    print()
    out = render_structured_reading(res, question or None)
    print(out)


if __name__ == '__main__':
    import sys
    demo(*(sys.argv[1:] or []))
