"""LLM 结构化推演通道（方案 C 混合·升级 narrative 层）。

链路：引擎 dict → build_payload 特征抽取（selectors 41 键 + zaihuo_llm_view
+ 死亡词典 scrub，全复用）→ DeepSeek JSON mode 七维叙述 → 三层校验 → 展示。

**红线：本模块输出永不回写 compute_all() dict**；无 API key/调用失败时
降级返回组装好的 prompt 文本（同 narrative.render_hao_narrative 契约）。

三层校验（validate_reading）：
- L0 schema：七维键齐、conclusion/basis/confidence 结构合法；
- L1 出处：basis 每条路径回解析特征 JSON，不存在/为空/带数组下标 → 违规；
  意图唯一的近-miss（缺 _ops 前缀/层级拍平/多包一层/叶键别名）自动 remap 转正；
- L2 枚举：财命档位/官命是非回对引擎枚举值 + 死亡词黑名单兜底
  + 迁移维禁「出国/移民/海外/国外/外国」+ 相貌维禁「漂亮/美/丑/帅」（N1 七维批）；
- N1 数字校验复用 narrative.validate_narrative_numbers（对白名单外数字留痕）。

单命示例：python3 -m mangpai.subjective.llm_channel
"""
from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional

from mangpai.subjective import build_payload, _resolve, _MISSING
from mangpai.subjective.llm_prompt import build_system_prompt, build_user_prompt
from mangpai.subjective.narrative import (
    _bazi_line,
    summarize_engine_result,
    validate_narrative_numbers,
)

DIMENSIONS = ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')
_CONFIDENCE = ('高', '中', '低')

# L2 财命档位序（index 大=高）。引擎双轨：tier_static 原局轨 + tier 全量轨，
# 措辞上限取两轨较高者（运中层级断语合法，v6 口径）。
_TIER_ORDER = ('贫', '平', '小康', '富', '巨富')

# L2 死亡词黑名单（兜底双保险之二；payload 已 scrub，此乃对 LLM 输出端）。
_DEATH_WORDS = ('死亡', '寿终', '享年', '夭折', '早夭', '短命',
                '命不久', '寿数', '寿命', '寿元', '大限生死')

# L2 死亡词误报窗（V4 P2-2/2-3）：模型合规拒答句会复述死亡词（如「寿数」）
# 并外露「红线」字样——死亡词所在句（。！？换行分隔）内出现拒答标记则该处不计。
# ponytail: 拒答识别是同句关键词启发式，语义级拒答变体漏判由 mark/reject 输出人工兜底
_DEATH_REFUSAL = ('不测', '不予', '拒绝', '红线', '不预测', '不涉')
_SENT_END = '。！？!?\n'

# L2 官命正向断言关键词（仅在引擎 is_guanming=False 时拦截）。
# ponytail: 关键词回对是启发式，否定语境按「前 5 字符+后 5 字符」窗口排除
# （迭代 7：±2→±5 对齐财档 _TIER_NEG 窗，盖「官命一票否决/官命又被否决/
# 官命被反局否决/非正统官命」四类否定出窗误判），仍覆盖不了全部中文
# 否定句式——语义级残留由 L1+人工兜底，见归档 §2.1。
_GUAN_POSITIVE = ('官命', '当官', '走仕途', '是官', '贵格', '掌大权')
_NEG_PREFIX = ('不', '非', '无', '难', '未', '莫', '否')

# N1 七维批·L2 按维红线：
# 迁移维绝对禁出境词（对齐引擎措辞上限「迁移/远行」，qianyi 模块不出硬断语）。
_QIANYI_FORBID = ('出国', '移民', '海外', '国外', '外国')
# 相貌维禁结论词（marker 层无判定无档位，只许引用 marker 描述）。
_XIANGMAO_FORBID = ('漂亮', '美', '丑', '帅')
# 相貌排除窗（E7 窗口机制同族，但按相邻字判定更准——±5 窗会放跑真结论词）：
# 「美元」货币、「丑时」时辰、「X丑」干支 非相貌结论词，放行。
_STEMS = '甲乙丙丁戊己庚辛壬癸'


def _xiangmao_exempt(text: str, w: str, j: int) -> bool:
    """相貌禁词命中处的排除窗：美元/丑时/干支（X丑）不计。"""
    if w == '美' and text[j + 1:j + 2] == '元':
        return True
    if w == '丑' and (text[j + 1:j + 2] == '时' or text[j - 1:j] in _STEMS):
        return True
    return False


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


# L1 数组下标访问（"juxiang[7]"、"juxiang.7"）一律违规：数组只许引数组名本身。
_ARRAY_INDEX = re.compile(r'\[\d+\]|(?:^|\.)\d+(?:\.|$)')

# L1 近-miss remap 规则表（v5 迭代 4 残余 10 条归纳）。只对意图唯一可展开者
# remap，多候选=歧义仍记违规（宁缺毋滥）。各规则依据：
#  A 缺 _ops 前缀：juxiang/all_findings 等只存在于 xiangfa_ops（顶层 xiangfa* 仅此两节点）；
#  B 层级拍平：所引键在已解析前缀节点的子树中恰有一处（gong_attacked 唯在 hunyin.quality，
#    caixing_path 唯在 caiming.caifu_view）；
#  C 多包一层：恰有一种中间段删法可解析（hunyin.quality.summary → hunyin.summary）；
#  D 叶键别名：hunyin 系子模块原因列表统一键名为 factors（duohun/dushen/laoyue 等），
#    LLM 套用了 jiehun_yingqi.signals 的键名。
_LEAF_ALIAS = {'signals': 'factors'}


def _remap_basis(features: dict, path: str):
    """近-miss 路径的唯一展开。返回 (真键, 值)；无唯一展开返回 (None, _MISSING)。"""
    segs = path.split('.')
    cands = set()
    # 规则 A：xiangfa.X → xiangfa_ops.X
    if segs[0] == 'xiangfa' and len(segs) > 1:
        cands.add('xiangfa_ops.' + '.'.join(segs[1:]))
    # 规则 B：已解析前缀节点的直接子 dict 中，恰一个可接续剩余路径
    node, i = features, 0
    while i < len(segs) and isinstance(node, dict) and segs[i] in node:
        node = node[segs[i]]
        i += 1
    if i < len(segs) and isinstance(node, dict):
        rest = '.'.join(segs[i:])
        hits = [k for k, ch in node.items()
                if isinstance(ch, dict) and _resolve(ch, rest) is not _MISSING]
        if len(hits) == 1:
            cands.add('.'.join(segs[:i] + [hits[0]] + segs[i:]))
    # 规则 C：删除一个中间段
    for j in range(1, len(segs) - 1):
        cands.add('.'.join(segs[:j] + segs[j + 1:]))
    # 规则 D：叶键别名
    if len(segs) > 1 and segs[-1] in _LEAF_ALIAS:
        cands.add('.'.join(segs[:-1] + [_LEAF_ALIAS[segs[-1]]]))
    vals = {}
    for cand in cands:
        val = _resolve(features, cand)
        if val is not _MISSING:
            vals[cand] = val
    uniq = {id(v): (k, v) for k, v in vals.items()}  # 多候选解析到同一对象=同一意图
    if len(uniq) == 1:
        return next(iter(uniq.values()))
    return None, _MISSING


# L1 空值引用白名单（迭代 5）：zhiye.primary 空串本身即判定（空=无明确职业倾向），
# 职业锚定要求叙述无倾向时引此为出处，不适用「(空)=无出处」规则。
_L1_EMPTY_OK = {'zhiye.primary'}


def _l1_basis(data: dict, features: dict, remapped: list | None = None) -> list:
    """L1 依据路径解析：basis 每项须在特征 JSON 中可解析且非空，且不得带数组下标。
    可唯一展开的近-miss 自动 remap 转正（映射记入 remapped，不算违规）。"""
    v = []
    for dim in DIMENSIONS:
        node = data.get(dim)
        if not isinstance(node, dict):
            continue  # 非对象维度已由 L0 记违规，L1 跳过防崩
        for path in node.get('basis') or []:
            if not isinstance(path, str):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 含非字符串项: {path!r}'})
                continue
            if _ARRAY_INDEX.search(path):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 数组路径禁止带下标: {path}'})
                continue
            val = _resolve(features, path)
            real = None
            if val is _MISSING:
                real, val = _remap_basis(features, path)
            if val is _MISSING or (val in (None, {}, [], '') and path not in _L1_EMPTY_OK):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 路径无出处或为空: {path}'})
            elif real is not None and remapped is not None:
                remapped.append({'layer': 'L1',
                                 'detail': f'{dim}.basis remap: {path} → {real}'})
    return v


# 档位词否定窗（迭代 2 复测发现：锚定生效后 LLM 多用「难大富/非巨富/大富难求」
# 等否定式合规表述，裸 substring 全误判越限）。命中词前 5 字符内现否定字、
# 或后随「（填1字）难求/不足/不起/不了/无望」则该处不计。「财富」之富为泛指，亦不计。
# （迭代 6：窗 4→5，盖「不可奢求大富」类不字距 5 的合规否定。）
_TIER_NEG = '不非难无莫勿未别'
_TIER_NEG_AFTER = re.compile(r'^[一-鿿]?(?:难求|不足|不起|不了|无望)')

# 迭代 6 口径修（U3：16 例越限中 9 例假阳=校验器误判，聚四类缺口）：
# ①让步封顶：「…之说/之象，但财命封顶X」「上限X」前的档位词是让步引用，不计；
# ②泛指动词：「致富」同「财富」不计；
# ③引擎原文引用：命中词落在引擎 caiming 原文子串内（≥3 字）不计——
#   但巨富档不适用（防引擎旁注文字掩护真越限）；
# ④修饰档归位：「小富」按小康级、「X偏下」降半档归位；
# ⑤愿望条件句：「想大富得靠…」式（命中词前 4 字符内有「想」）不计。
#   「若/一旦」不入豁免——U3 #10「一旦库开富可敌国」双实例裁真越限。
# ⑥「富格/富档」=引擎格局/档位术语（同「财富」类复合词），不计。
# ⑦（迭代 7，E6 复测新发同族）让步句「虽」字窗（前 5 字内有「虽」不计，
#   盖「虽有大富之量级但被下浮」「虽有小富之象」）+归位语标记「档就是/档为」
#   同①（「功量层级中富中贵，但财命档就是小康」词前归位，词不计）。
# ⑧（N2 迭代修，r1 yx-酒店）归位语「小康之富」：档词+之富=该档归位表述，
#   尾字「富」按前缀档计（同④「小富」族）；只降不升，不掩护真越限。
# ⑧b/c/d/e（N2 r3 复测假阳族）：「大富大贵」成语泛指同富贵；「富足」泛指形容词；
#   「暴富」专属宽窗（±8，盖「别想着投机暴富/别指望一夜暴富」告诫句——一般窗
#   ±5 差一字漏放，仅暴富复合词加宽，防泛窗掩护真越限）；「平平」叠词口语
#   （普通/平常）非档位断言。
_TIER_CAP_MARKERS = ('封顶', '上限', '定档', '定格', '档就是', '档为')


def _quoted(text: str, j: int, length: int, corpus: str) -> bool:
    """命中处的 ±2 字窗（≥3 字）是否为引擎原文子串。"""
    for a in range(3):
        for b in range(3):
            s = text[max(0, j - a):j + length + b]
            if len(s) >= 3 and s in corpus:
                return True
    return False


def _tier_rank(text: str, corpus: str = '') -> int:
    """文本中未被否定/豁免的最高财命档位（无则 -1）。巨富先于富匹配。"""
    cap = min((text.find(m) for m in _TIER_CAP_MARKERS if m in text), default=-1)
    best = -1
    for i, t in enumerate(_TIER_ORDER):
        start = 0
        while True:
            j = text.find(t, start)
            if j == -1:
                break
            start = j + 1
            if 0 <= cap and j < cap:
                continue  # ①让步+封顶：封顶标记前的档位词为被压住的让步引用
            r = i
            if t == '富':
                prev = text[j - 1:j]
                if prev in ('巨', '财', '致'):
                    continue  # 巨富单独判；财富/致富=泛指非档位（②）
                if text[j + 1:j + 2] in ('格', '档', '贵'):
                    continue  # ⑥富格/富档=引擎格局/档位术语；富贵=泛指
                if text[j + 1:j + 2] == '足':
                    continue  # ⑧c「富足」泛指形容词，同富贵族
                if text[j - 1:j + 3] == '大富大贵':
                    continue  # ⑧b「大富大贵」成语泛指，同富贵族
                if prev == '暴' and any(c in _TIER_NEG
                                        for c in text[max(0, j - 8):j]):
                    continue  # ⑧d 告诫式「别/莫…暴富」专属宽窗 ±8
                if prev == '小':
                    r = 2  # ④「小富」=小康级修饰档，归位
                elif prev == '之':
                    if text[j - 3:j - 1] == '小康':
                        r = 2  # ⑧「小康之富」归位语，按小康计
                    elif text[j - 2:j - 1] in ('贫', '平'):
                        r = _TIER_ORDER.index(text[j - 2:j - 1])  # ⑧「贫/平之富」同理
            if any(c in _TIER_NEG for c in text[max(0, j - 5):j]):
                continue
            if t == '平' and (text[j - 1:j] == '平' or text[j + 1:j + 2] == '平'):
                continue  # ⑧e「平平」叠词口语（普通/平常），非档位断言
            if '想' in text[max(0, j - 4):j]:
                continue  # ⑤愿望条件句「想大富得靠…」
            if '虽' in text[max(0, j - 5):j]:
                continue  # ⑦让步句「虽有大富之量级但被下浮」（虽…但…后段归位）
            if _TIER_NEG_AFTER.match(text[j + len(t):]):
                continue
            if text[j + len(t):j + len(t) + 2] == '偏下':
                r -= 1  # ④「小康偏下」降半档
                if r < 0:
                    continue
            if t != '巨富' and corpus and _quoted(text, j, len(t), corpus):
                continue  # ③引擎原文引用豁免（巨富档除外）
            best = max(best, r)
            break
    return best


def _l2_enum(data: dict, engine_result: dict) -> list:
    """L2 枚举回对：财命档位不越引擎双轨上限；官命是非不反引擎；死亡词黑名单。"""
    v = []
    texts = {dim: str(((data.get(dim) or {}) if isinstance(data.get(dim), dict) else {}).get('conclusion') or '')
             for dim in DIMENSIONS}

    # 死亡红线（所有维度；拒答句误报窗豁免——合规拒答复述死亡词不计）
    for dim, t in texts.items():
        for w in _DEATH_WORDS:
            start = 0
            while True:
                j = t.find(w, start)
                if j == -1:
                    break
                start = j + 1
                l = max((t.rfind(p, 0, j) for p in _SENT_END), default=-1)
                r = min((c for p in _SENT_END
                         if (c := t.find(p, j + len(w))) != -1), default=len(t))
                seg = t[l + 1:r]  # 同句窗：拒答标记与死亡词同句 = 合规拒答复述
                if any(m in seg for m in _DEATH_REFUSAL):
                    continue
                v.append({'layer': 'L2', 'detail': f'{dim} 触死亡红线词「{w}」'})
                break

    # 财命档位（corpus=引擎 caiming 原文，供③引用豁免）
    cm = engine_result.get('caiming') or {}
    ceiling = max((_tier_rank(str(cm.get(k) or ''))
                   for k in ('tier_static', 'tier')), default=-1)
    corpus = json.dumps(cm, ensure_ascii=False)
    got = _tier_rank(texts['财运'], corpus)
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
                if w == '是官' and t[i - 1:i] == '倒':
                    i = t.find(w, i + 1)
                    continue  # 「倒是官带财帽」让步/术语族（N2 r3 yx-富钢材生意发财假阳）
                # 前后各 5 字符内出现否定词（不是…/…否决/无缘/难成…）视为否定语境放行
                seg = t[max(0, i - 5):i + len(w) + 5]
                if not any(ch in _NEG_PREFIX for ch in seg):
                    v.append({'layer': 'L2',
                              'detail': f'事业 与引擎官命=否矛盾：「{w}」'})
                    break
                i = t.find(w, i + 1)

    # 迁移维措辞上限（引擎「迁移/远行」，绝对禁出境词）
    t = texts['迁移']
    for w in _QIANYI_FORBID:
        if w in t:
            v.append({'layer': 'L2', 'detail': f'迁移 越措辞上限词「{w}」'})
            break

    # 相貌维禁结论词（marker 层无档位；美元/丑时/干支排除窗放行）
    t = texts['相貌']
    for w in _XIANGMAO_FORBID:
        start = 0
        while True:
            j = t.find(w, start)
            if j == -1:
                break
            start = j + 1
            if _xiangmao_exempt(t, w, j):
                continue
            v.append({'layer': 'L2', 'detail': f'相貌 触禁结论词「{w}」'})
            break
    return v


def validate_reading(data: Any, features: dict, engine_result: dict) -> dict:
    """三层校验 + N1 数字校验，返回 {'ok', 'violations', 'n1'}。"""
    violations = _l0_schema(data)
    remapped: list = []
    if isinstance(data, dict):
        violations += _l1_basis(data, features, remapped)
        violations += _l2_enum(data, engine_result)
    blob = json.dumps(data, ensure_ascii=False) if isinstance(data, dict) else str(data)
    n1 = validate_narrative_numbers(blob, engine_result)
    violations += [{'layer': 'N1',
                    'detail': f"「{x['text']}」({x['kind']}): {x['detail']}"}
                   for x in n1['violations']]
    return {'ok': not violations, 'violations': violations, 'n1': n1,
            'remapped': remapped}


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
                     f"cost≈¥{backend.get('cost_usd', 0):.4f}]")
    # 免责声明（V4 P0-1）：LLM 叙述路径尾部固定一行
    lines.append('命理分析仅供参考，不构成人生决策依据。')
    return '\n'.join(lines)


def render_structured_reading(
    engine_result: Dict[str, Any],
    user_question: Optional[str] = None,
    *,
    call_llm: bool = True,
    model: str | None = None,
    validate: str = 'mark',
) -> str:
    """引擎 dict → DeepSeek 七维 JSON 叙述 → 三层校验 → 展示文本。

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
                             user_question or '', features=features)
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
    # 死亡红线命中 = reject 级（V4 P1-1）：mark 模式也不展示、不附注，
    # 整段拒出（前缀 '[断语被' 触发 service 层降级引擎直出）。scrub 守输入端
    # （payload 死亡词典物理屏蔽），reject 守输出端，拒答误报窗已在 _l2_enum 豁免。
    if validate != 'off' and any('死亡红线' in x['detail'] for x in report['violations']):
        return '[断语被死亡红线校验拦截，不予展示]'
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
