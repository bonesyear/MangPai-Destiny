"""LLM 结构化推演通道（方案 C 混合·升级 narrative 层）。

链路：引擎 dict → build_payload 特征抽取（selectors 42 键 + zaihuo_llm_view
+ 死亡词典 scrub，全复用）→ DeepSeek JSON mode 七维叙述 → 三层校验 → 展示。

**红线：本模块输出永不回写 compute_all() dict**；无 API key/调用失败时
降级返回组装好的 prompt 文本（同 narrative.render_hao_narrative 契约）。

三层校验（validate_reading）：
- L0 schema：七维键齐、无额外维度（批R①）、conclusion/basis/confidence 结构合法；
- L1 出处：basis 每条路径回解析特征 JSON，不存在/为空/带数组下标 → 违规；
  意图唯一的近-miss（缺 _ops 前缀/层级拍平/多包一层/叶键别名）自动 remap 转正；
- L2 枚举：财命档位/官命是非回对引擎枚举值 + 死亡词黑名单兜底
  + 出境词/相貌结论词全维度禁（红2：与死词表同口径，跨维逃逸亦拦；N1 七维批起）
  + 应期运岁吉凶/婚姻质量回对引擎 overall/quality（2026-10-17 零校验补齐）；
- N1 数字校验复用 narrative.validate_narrative_numbers（对白名单外数字留痕）。

单命示例：python3 -m mangpai.subjective.llm_channel
"""
from __future__ import annotations

from pathlib import Path

import json
import logging
import re
from typing import Any, Dict, Optional

from mangpai.subjective import (
    build_payload, _resolve, _MISSING, DEATH_WORDS, normalize_safety_text,
)
from mangpai.subjective.llm_backend import call_deepseek, LLMBackendError
from mangpai.subjective.llm_prompt import build_system_prompt, build_user_prompt
from mangpai.subjective.prompts.hao_style_fewshot import (
    FEWSHOT_EXAMPLES, format_fewshot_block,
)
from mangpai.subjective.narrative import (
    _bazi_line,
    summarize_engine_result,
    validate_narrative_numbers,
)

DIMENSIONS = ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')
_CONFIDENCE = ('高', '中', '低')

_logger = logging.getLogger(__name__)

# 免责声明（V4 P0-1）：成功/降级/拦截三路径成品均自带（G2 F6-4：
# 降级文本不再单点依赖 service 前缀白名单兜底）
_DISCLAIMER_LINE = '命理分析仅供参考，不构成人生决策依据。'

# 修批F⑥：gender → 乾/坤造标记归一表（对齐 bazi_calc 入口合法集 男/女/male/female/乾/坤）
_GENDER_ZAO = {'男': '乾造', '乾': '乾造', 'male': '乾造',
               '女': '坤造', '坤': '坤造', 'female': '坤造'}

# L2 财命档位序（index 大=高）。引擎双轨：tier_static 原局轨 + tier 全量轨，
# 措辞上限取两轨较高者（运中层级断语合法，v6 口径）。
# 修批F③：对齐引擎四档真值（caiming.tier_map={1:贫,2:小康,3:富,4:巨富}）——
# 幽灵档「平」移出；LLM 输出「平档」按引擎不存在的档位词处理：不归档、不计 rank。
_TIER_ORDER = ('贫', '小康', '富', '巨富')

# L2 死亡词黑名单（兜底双保险之二；payload 已 scrub，此乃对 LLM 输出端）。
# G1（F6-2）：补近义词 离世/去世/归西/病逝 + 同类 过世/身故/辞世（W1 合成例 9）。
# 红3：再补 早逝/病故/亡故/终年/卒于/活不过/往生/百年之后（对抗用例实测逃逸族；
# 输入侧 subjective._DEATH_TERMS 同步补同一批，两侧口径对齐）。
_DEATH_WORDS = DEATH_WORDS

# L2 死亡词误报窗（V4 P2-2/2-3）：模型合规拒答句会复述死亡词（如「寿数」）
# 并外露「红线」字样——死亡词所在句内出现拒答标记则该处不计。
# G1（F6-2）：句界符补「，；」——逗号/分号不断句曾致「死断+拒答标记同逗号句」
# 误豁免（W1 合成例 6/10）。
# ponytail: 拒答识别是同句关键词启发式，语义级拒答变体漏判由 mark/reject 输出人工兜底
_DEATH_REFUSAL = ('不予预测', '不予断言', '不涉生死', '不测生死', '不测寿',
                  '不做生死断言', '寿数属红线', '生死属红线', '不预测寿')
_SENT_END = '。！？!?\n，；：:,;.、…— \t'
_DISEASE_WORDS = ('糖尿', '白血', '血病', '血液病', '尿毒', '癌', '肿瘤',
                  '精神病', '心梗', '脑溢血', '中风', '瘫痪')
_CHILD_GENDER_WORDS = ('生男', '生女', '得子', '得女', '男胎', '女胎',
                       '头胎男', '头胎女', '次胎男', '次胎女')
_ENGLISH_DEATH_WORDS = ('lifespan', 'life expectancy', 'pass away', 'death',
                        'die', 'dying')

# L2 官命正向断言关键词（仅在引擎 is_guanming=False 时拦截）。
# ponytail: 关键词回对是启发式，否定语境按「前 5 字符+后 5 字符」窗口排除
# （迭代 7：±2→±5 对齐财档否定窗，盖「官命一票否决/官命又被否决/
# 官命被反局否决/非正统官命」四类否定出窗误判），仍覆盖不了全部中文
# 否定句式——语义级残留由 L1+人工兜底，见归档 §2.1。
# 修批F①：否定判定改走 _neg_in_pre/_neg_in_post（与财档同窗同口径——同子句、
# 双字词、剔除双重否定「不是没官命」与反语肯定「官命不小」），_NEG_PREFIX
# 仅留作 output/ 扫描脚本兼容引用，校验逻辑不再使用。
_GUAN_POSITIVE = ('官命', '当官', '走仕途', '是官', '贵格', '掌大权')
_NEG_PREFIX = ('不', '非', '无', '难', '未', '莫', '否')  # 已弃用，见上注

# N1 七维批·L2 红线词表（红2 起全维度扫描，与死词表口径一致——
# 跨维逃逸曾致出境词/美丑词落在迁移/相貌维之外而放行）：
# 出境词绝对禁（对齐引擎措辞上限「迁移/远行」，qianyi 模块不出硬断语）。
# 红2 补词：出境/移居/异国/留洋（对抗用例实测逃逸族）。
# 批R④a 补词：赴外/南洋/赴美（批5 对抗实跑逃逸词；词级匹配无单字误报）。
_QIANYI_FORBID = ('出国', '移民', '海外', '国外', '外国',
                  '出境', '移居', '异国', '留洋',
                  '赴外', '南洋', '赴美')
# 相貌结论词禁（marker 层无判定无档位，只许引用 marker 描述）。
# N2b 裁定（书锚为准）：含「美」复合评价词（优美/柔美/秀美/俊美等）书内零锚
# → 一律入禁，单字「美」扫描已全覆盖（r3 残留 2 例均被抓），不加词表不加
# 后缀放行（美丽/美妙等仍是评价词——「美丽」lixiangxue 有 3 处用例
# （9928/12583/12632），禁之属保守不违书但非零锚，W3-P2#2 注释口径改准）；
# 真正缺口在生成侧，由 llm_prompt SCHEMA/锚定禁令显式点名复合词族收敛。
# G1（W2 P1 复合词真漏网）：标致/水灵/清秀/端庄 书内零锚但不含美丑帅字——
# 词级匹配补入（无单字误报，无需排除窗）；prompt 轨同步点名五词（含甜美）。
# 红2 补词：英俊/好看/靓丽/俊俏/颜值高/姿色（对抗用例实测逃逸族，词级匹配
# 无单字误报——「好看」书锚 zhongji:3981-3982 系身材描述非结论档位词，入禁
# 属保守不违书，与「美丽」同口径）。
_XIANGMAO_FORBID = ('漂亮', '美', '丑', '帅', '标致', '水灵', '清秀', '端庄',
                    '英俊', '好看', '靓丽', '俊俏', '颜值高', '姿色')
# 相貌排除窗（E7 窗口机制同族，但按相邻字判定更准——±5 窗会放跑真结论词）：
# 「美元」货币、「丑时」时辰、「X丑」及独立「丑」地支搭配，非相貌结论词，放行。
_STEMS = '甲乙丙丁戊己庚辛壬癸'
_BRANCHES = '子丑寅卯辰巳午未申酉戌亥'


def _xiangmao_exempt(text: str, w: str, j: int) -> bool:
    """相貌禁词排除窗：美元/丑时/干支及独立丑地支搭配不计。"""
    if w == '美' and text[j + 1:j + 2] == '元':
        return True
    if w == '丑' and (
            text[j + 1:j + 2] == '时'
            or (j > 0 and text[j - 1] in _STEMS + _BRANCHES)
            or text[j + 1:j + 2] in _BRANCHES + '土库墓月年日运未戌合冲刑穿破害马本空临'
            or (text[j + 1:j + 2] == '、' and text[j + 2:j + 3] in _BRANCHES)
            or text[j + 1:j + 3] in ('又合', '是财')
            or text[j + 1:j + 6] == '为家乡之马'):
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
            v.append({'layer': 'L0', 'detail': f'{dim}.confidence 非法值'})
    # 批R①：七维之外的额外维度记违规——自造第 8 维（如「健康」）静默通过则
    # 其内容不受 L2 检查（L2 只扫 DIMENSIONS 内维度文本）
    for key in data:
        if key not in DIMENSIONS:
            v.append({'layer': 'L0', 'detail': '额外维度不在 schema 七维内'})
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
    cands = []
    # 规则 A：xiangfa.X → xiangfa_ops.X
    if segs[0] == 'xiangfa' and len(segs) > 1:
        cands.append('xiangfa_ops.' + '.'.join(segs[1:]))
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
            cands.append('.'.join(segs[:i] + [hits[0]] + segs[i:]))
    # 规则 C：删除一个中间段
    for j in range(1, len(segs) - 1):
        cands.append('.'.join(segs[:j] + segs[j + 1:]))
    # 规则 D：叶键别名
    if len(segs) > 1 and segs[-1] in _LEAF_ALIAS:
        cands.append('.'.join(segs[:-1] + [_LEAF_ALIAS[segs[-1]]]))
    vals = {}
    for cand in cands:
        val = _resolve(features, cand)
        if val is not _MISSING:
            vals[cand] = val
    uniq = {}
    for k, v in vals.items():
        uniq.setdefault(json.dumps(v, ensure_ascii=False, sort_keys=True, default=str), (k, v))
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
        basis = node.get('basis') or []
        if not isinstance(basis, list):
            continue
        if len(basis) > 20:
            v.append({'layer': 'L1', 'detail': f'{dim}.basis 超过20条'})
            basis = basis[:20]
        for path in basis:
            if not isinstance(path, str):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 含非字符串项'})
                continue
            if len(path) > 120 or path.count('.') >= 8:
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 路径超长或层级过深'})
                continue
            if _ARRAY_INDEX.search(path):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 数组路径禁止带下标'})
                continue
            val = features.get(path, _MISSING)
            if val is _MISSING:
                val = _resolve(features, path)
            real = None
            if val is _MISSING:
                real, val = _remap_basis(features, path)
            if val is _MISSING or (val in (None, {}, [], '') and path not in _L1_EMPTY_OK):
                v.append({'layer': 'L1', 'detail': f'{dim}.basis 路径无出处或为空'})
            elif real is not None and remapped is not None:
                remapped.append({'layer': 'L1',
                                 'detail': f'{dim}.basis remap: {path} → {real}'})
    return v


# 档位词否定窗（迭代 2 复测发现：锚定生效后 LLM 多用「难大富/非巨富/大富难求」
# 等否定式合规表述，裸 substring 全误判越限）。命中词前 5 字符内现否定字、
# 或后随「（填1字）难求/不足/不起/不了/无望」则该处不计。「财富」之富为泛指，亦不计。
# （迭代 6：窗 4→5，盖「不可奢求大富」类不字距 5 的合规否定。）
# 修批F①否定窗击穿收口：
# - 「未」移出单字表——干支「癸未/乙未」高频撞窗（「癸未运开库，巨富可期」逃逸）；
# - 「难/无」单字改双字词（未能/没有/并无/难成/难发/无官/无财族）或紧贴档位词
#   （难大富/无富）才计——单字在「无数/难道」类非否定语境误豁免真越限；
# - 否定单位与档位词须同子句（中间无句读标点）——「莫急，你是巨富命」跨子句豁免逃逸；
# - 伪否定语境剔除：双重否定（不是没/并非不…）、非常/非凡（「你非常富有」逃逸）、
#   反语肯定（不小/不弱/不低/不微，「你官命不小」逃逸）。
_TIER_NEG = '不非莫勿别'
_TIER_NEG_PHRASES = ('未能', '没有', '并无', '毫无', '难成', '难发', '难达', '难有',
                     '无官', '无财', '无富', '无贵', '无缘', '无份', '否决')
_TIER_NEG_AFTER = re.compile(r'^[一-鿿]?(?:难求|不足|不起|不了|无望)')
_NEG_CLAUSE_BREAK = '，。！？；：、;:!?…—'
_NEG_FALSE_PATTERNS = ('不是没', '并非没', '并非不', '不是不', '未必不', '未尝不',
                       '非常', '非凡', '不小', '不弱', '不低', '不微',
                       '特别', '级别', '个别', '区别', '分别', '不仅', '不但',
                       '不断', '不久', '不愁', '莫大')
_NEG_UNIT_RE = re.compile('|'.join(list(_TIER_NEG_PHRASES)
                                   + ['[' + _TIER_NEG + ']']))


def _neg_in_pre(text: str, j: int, width: int = 5) -> bool:
    """命中词前 width 字窗内有有效否定（同子句、剔除伪否定）则 True。"""
    seg = text[max(0, j - width):j]
    for p in _NEG_FALSE_PATTERNS:
        seg = seg.replace(p, '×' * len(p))
    for m in _NEG_UNIT_RE.finditer(seg):
        if not any(c in _NEG_CLAUSE_BREAK for c in seg[m.end():]):
            return True
    return False


def _neg_in_post(text: str, end: int, width: int = 5) -> bool:
    """命中词后 width 字窗内有有效否定（同子句、剔除伪否定）则 True。"""
    seg = text[end:end + width]
    for p in _NEG_FALSE_PATTERNS:
        seg = seg.replace(p, '×' * len(p))
    for m in _NEG_UNIT_RE.finditer(seg):
        if not any(c in _NEG_CLAUSE_BREAK for c in seg[:m.start()]):
            return True
    return False

# 迭代 6 口径修（U3：16 例越限中 9 例假阳=校验器误判，聚四类缺口）：
# ①让步封顶：「…之说/之象，但财命封顶X」「上限X」前、与标记同句且有转折连词
#   （但/然/却）的档位词是让步引用，不计（修批F②收窄——无转折连词的独立
#   断言不豁免：「原局本是巨富格，可惜岁运反局压制，财命档就是小康」逃逸）；
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

# ⑧b 收窄（2026-10-17）：「大富大贵」泛指豁免仅适用非断言语境——前 3 字内现
#   断言主语（你/命中/此造/命主/一生）即断言语境，不豁免（「你命中大富大贵，
#   只是财库未开」在 ceiling=小康 时曾借此漏网）。
_DAFUDAGUI_SUBJ = ('你', '命中', '此造', '命主', '一生')


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
            if 0 <= cap and j < cap \
                    and any(c in '但然却' for c in text[j + len(t):cap]):
                continue  # ①让步+封顶：档词与封顶标记同句且有转折连词（但/然/却）
                # =被压住的让步引用。修批F②收窄：无转折连词的独立断言不豁免
                # （「原局本是巨富格，可惜岁运反局压制，财命档就是小康」逃逸）。
            r = i
            if t == '富':
                prev = text[j - 1:j]
                if prev in ('巨', '财', '致'):
                    continue  # 巨富单独判；财富/致富=泛指非档位（②）
                if text[j + 1:j + 2] in ('格', '档', '贵'):
                    continue  # ⑥富格/富档=引擎格局/档位术语；富贵=泛指
                if text[j + 1:j + 2] == '足':
                    continue  # ⑧c「富足」泛指形容词，同富贵族
                if text[j - 1:j + 3] == '大富大贵' \
                        and not any(s in text[max(0, j - 4):j - 1]
                                    for s in _DAFUDAGUI_SUBJ):
                    continue  # ⑧b「大富大贵」成语泛指，同富贵族；
                    # 前 3 字现断言主语（你/命中/此造/命主/一生）=断言语境，不豁免
                if prev == '暴' and any(c in _TIER_NEG
                                        for c in text[max(0, j - 8):j]):
                    continue  # ⑧d 告诫式「别/莫…暴富」专属宽窗 ±8
                if prev == '小':
                    r = 1  # ④「小富」=小康级修饰档，归位（修批F③四档序：小康=1）
                elif prev == '之':
                    if text[j - 3:j - 1] == '小康':
                        r = 1  # ⑧「小康之富」归位语，按小康计
                    elif text[j - 2:j - 1] == '贫':
                        r = 0  # ⑧「贫之富」同理
                    elif text[j - 2:j - 1] == '平':
                        continue  # 修批F③：幽灵档「平」不归档（引擎无此档）
            if _neg_in_pre(text, j) or text[j - 1:j] in ('难', '无') \
                    or (t == '富' and text[j - 2:j] in ('难大', '无大')):
                continue  # 否定窗（修批F①：同子句否定单位/难无紧贴前缀，
                # 「难大富/无大富」的难无隔「大」字亦计——距 2 的唯一合法形态）
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
    return best


# L2 应期维吉凶回对词表（2026-10-17 零校验补齐，小词表起步）：
# 应期 conclusion 引用某运/年干支，该条目 overall=凶 而叙述含吉词、
# overall=吉 而叙述含凶词 → 矛盾记违规；吉凶参半/平不查，缺数据不查。
# 批R③：命中词剔除否定语境（复用批F _neg_in_pre 同口径——同子句±5 窗、
# 剔除双重否定/反语肯定，「婚姻不美满」「运势不算顺利」不误拦）；
# ponytail: 分运分句不细辨（词与干支不绑同句），语义级残留由人工兜底
_YINGQI_POS_WORDS = ('大吉', '顺利', '亨通', '好运')
_YINGQI_NEG_WORDS = ('大凶', '凶险', '灾祸')

# L2 婚姻维质量回对词表（同批，小词表起步）：引擎 hunyin.quality.quality=差
# 而叙述含褒词、=好 而叙述含贬词 → 矛盾记违规；=平或缺 hunyin 数据不查。
# 批R③：同应期口径剔除否定语境。
_HUNYIN_POS_WORDS = ('美满', '幸福', '恩爱', '和睦')
_HUNYIN_NEG_WORDS = ('婚变', '离异', '不幸')


def _unnegated_hit(text: str, words) -> Optional[str]:
    """词表中首个无否定语境的命中词；全部命中处均被否定则 None（批R③）。"""
    for w in words:
        start = 0
        while True:
            j = text.find(w, start)
            if j == -1:
                break
            start = j + 1
            if not _neg_in_pre(text, j):
                return w
    return None


def _l2_enum(data: dict, engine_result: dict) -> list:
    """L2 枚举回对：财命档位不越引擎双轨上限；官命是非不反引擎；死亡词黑名单；
    应期运岁吉凶/婚姻质量回对引擎 overall/quality。"""
    v = []
    texts = {dim: str(((data.get(dim) or {}) if isinstance(data.get(dim), dict) else {}).get('conclusion') or '')
             for dim in DIMENSIONS}

    # 安全红线扫描整份模型输出，覆盖 conclusion/basis/confidence/额外键名。
    safety_blob = normalize_safety_text(json.dumps(data, ensure_ascii=False))
    for w in _DEATH_WORDS:
        start = 0
        while True:
            j = safety_blob.find(w, start)
            if j == -1:
                break
            start = j + 1
            l = max((safety_blob.rfind(p, 0, j) for p in _SENT_END), default=-1)
            r = min((c for p in _SENT_END
                     if (c := safety_blob.find(p, j + len(w))) != -1), default=len(safety_blob))
            seg = safety_blob[l + 1:r]
            if any(m in seg for m in _DEATH_REFUSAL) \
                    and not re.search(r'\d|岁|年|旬', seg):
                continue
            v.append({'layer': 'L2', 'detail': f'输出 触死亡红线词「{w}」',
                      'reject': True})
            break
    for words, label in ((_DISEASE_WORDS, '疾病诊断'), (_CHILD_GENDER_WORDS, '子女性别')):
        hit = next((w for w in words if w in safety_blob), '')
        if hit:
            v.append({'layer': 'L2', 'detail': f'输出 触{label}红线词「{hit}」',
                      'reject': True})
    hit = next((w for w in _ENGLISH_DEATH_WORDS if w in safety_blob.lower()), '')
    if hit:
        v.append({'layer': 'L2', 'detail': f'输出 触英文死亡红线词「{hit}」',
                  'reject': True})

    # 财命档位（corpus=引擎 caiming 原文，供③引用豁免）
    cm = engine_result.get('caiming') or {}
    ceiling = max((_tier_rank(str(cm.get(k) or ''))
                   for k in ('tier_static', 'tier')), default=-1)
    corpus = json.dumps(cm, ensure_ascii=False)
    got = _tier_rank(texts['财运'], corpus)
    # 红4：ceiling=-1（引擎降级/缺 caiming 数据）不再整体跳过——按最严口径，
    # 任何未被否定/豁免的档位断言（rank>=0）一律记违规（此前巨富放行）
    if got > ceiling:
        cap = _TIER_ORDER[ceiling] if ceiling >= 0 else '未知(缺数据)'
        v.append({'layer': 'L2',
                  'detail': f'财运档位越引擎上限：引擎={cap}，叙述={_TIER_ORDER[got]}'})

    # 官命是非（引擎否 → 叙述不得正向断言）
    # 红4：is_guanming 缺数据（None，引擎降级空 dict）按否口径同查——
    # 缺数据时正向官命断言同样拦（此前 `is False` 不成立导致整体跳过）
    gm = engine_result.get('guanming') or {}
    if gm.get('is_guanming') is not True:
        t = texts['事业']
        for w in _GUAN_POSITIVE:
            i = t.find(w)
            while i != -1:
                if w == '是官' and t[i - 1:i] == '倒':
                    i = t.find(w, i + 1)
                    continue  # 「倒是官带财帽」让步/术语族（N2 r3 yx-富钢材生意发财假阳）
                # 前后各 5 字符内有有效否定（不是…/…否决/无缘/难成…）视为否定语境放行；
                # 另识别明确否定谓语，不扩大窗口，避免误放「官命格成立」；
                # 修批F①：同财档口径——否定单位须同子句，双重否定/反语肯定不免
                if not (_neg_in_pre(t, i) or _neg_in_post(t, i + len(w))
                        or t[i + len(w):].startswith(
                            ('为否', '判否', '一栏是否', '是否定的',
                             '这一块是凶向否决', '断的是「否」', '一途被否',
                             '：否', '是被否掉的', '断否', '又被凶向否决',
                             '判为否', '判定为否', '这一条被凶向直接否决'))
                        or t[i - 1:i] in ('难', '无')):
                    v.append({'layer': 'L2',
                              'detail': f'事业 与引擎官命=否矛盾：「{w}」'})
                    break
                i = t.find(w, i + 1)

    # 应期维吉凶回对（零校验补齐）：conclusion 引用的运/年干支，引擎 overall
    # 与叙述褒贬矛盾记违规（overall ∈ 吉/凶/吉凶参半/平——参半/平不查；
    # 缺 dayun/liunian 数据不查）。
    t_yq = texts['应期']
    if t_yq:
        _yl = (((engine_result.get('dayun_analysis') or {}).get('dayun') or [])
               + ((engine_result.get('liunian_analysis') or {}).get('liunian') or []))
        for e in _yl:
            gz, ov = e.get('gz', ''), e.get('overall', '')
            if not gz or gz not in t_yq:
                continue
            if ov == '凶':
                w = _unnegated_hit(t_yq, _YINGQI_POS_WORDS)
            elif ov == '吉':
                w = _unnegated_hit(t_yq, _YINGQI_NEG_WORDS)
            else:
                continue
            if w:
                v.append({'layer': 'L2',
                          'detail': f'应期 与引擎「{gz}」overall={ov}矛盾：叙述含「{w}」'})

    # 婚姻维质量回对（零校验补齐）：引擎 hunyin.quality.quality=差 而叙述褒词、
    # =好 而叙述贬词记违规；=平或缺 hunyin 数据不查。批R③：否定语境命中不计。
    _hq = ((engine_result.get('hunyin') or {}).get('quality') or {}).get('quality')
    if _hq in ('好', '差'):
        _hw = _HUNYIN_NEG_WORDS if _hq == '好' else _HUNYIN_POS_WORDS
        w = _unnegated_hit(texts['婚姻'], _hw)
        if w:
            v.append({'layer': 'L2',
                      'detail': f'婚姻 与引擎婚姻质量={_hq}矛盾：叙述含「{w}」'})

    # 出境/相貌扫描全部维的 conclusion，并记录实际所在维度；
    # 财档/官命仍按维，相貌排除窗（美元/丑时/干支）按词法放行。
    normalized_texts = {dim: normalize_safety_text(text) for dim, text in texts.items()}
    for w in _QIANYI_FORBID:
        matched = [dim for dim, text in normalized_texts.items() if w in text]
        if matched:
            for dim in matched:
                v.append({'layer': 'L2', 'detail': f'输出 越措辞上限词「{w}」（{dim}）',
                          'reject': True, 'kind': 'qianyi_redline', 'dim': dim})
            break
    for w in _XIANGMAO_FORBID:
        matched = []
        for dim, text in normalized_texts.items():
            start = 0
            while True:
                j = text.find(w, start)
                if j == -1:
                    break
                start = j + 1
                if not _xiangmao_exempt(text, w, j):
                    matched.append(dim)
                    break
        if matched:
            for dim in matched:
                v.append({'layer': 'L2', 'detail': f'输出 触禁结论词「{w}」（{dim}）',
                          'reject': True, 'kind': 'xiangmao_redline', 'dim': dim})
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


def _larkmd_sanitize(text: str) -> str:
    """禁用 LLM 文本中的卡片链接、at/font 标签及三类排版符。"""
    out = []
    for ln in str(text).split('\n'):
        s = ln.lstrip()
        if s.startswith(('- ', '> ')):
            ln = ln[:len(ln) - len(s)] + '· ' + s[2:]
        out.append(ln.replace('---', '——'))
    return '\n'.join(out).translate(str.maketrans({
        '[': '［', ']': '］', '(': '（', ')': '）', '<': '＜', '>': '＞'}))


def format_reading(reading: dict, validation: dict, backend: dict,
                   show_telemetry: bool = True) -> str:
    """成品展示文本。"""
    lines = []
    bad_l1 = {x['detail'].split('.')[0] for x in validation.get('violations', [])
              if x.get('layer') == 'L1'} if validation else set()
    for dim in DIMENSIONS:
        node = (reading or {}).get(dim) or {} if isinstance(reading, dict) else {}
        if not isinstance(node, dict):
            node = {}
        confidence = node.get('confidence') if node.get('confidence') in _CONFIDENCE else '?'
        lines.append(f"【{dim}】({confidence}) "
                     f"{_larkmd_sanitize(node.get('conclusion', ''))}")
        if node.get('basis') and dim not in bad_l1:
            lines.append(f"  依据: {_larkmd_sanitize(', '.join(str(b) for b in node['basis']))}")
    if validation and not validation['ok']:
        lines.append('')
        lines.append('【引擎校验】以下要点未通过三层校验（请人工复核，勿直采信）：')
        for x in validation['violations']:
            lines.append(f"  · [{x['layer']}] {_larkmd_sanitize(x['detail'])}")
    if backend and show_telemetry:
        u = backend.get('usage') or {}
        # S1：定价表仅 DeepSeek 有效，其他 provider cost_cny=None → 显式「未计价」
        cost = backend.get('cost_cny')
        cost_txt = f'¥{cost:.4f}' if cost is not None else '未计价'
        lines.append('')
        lines.append(f"[model={backend.get('model')} "
                     f"in={u.get('prompt_tokens', '?')} out={u.get('completion_tokens', '?')} "
                     f"elapsed={backend.get('elapsed_s', 0):.1f}s "
                     f"cost≈{cost_txt}]")
    # 免责声明（V4 P0-1）：LLM 叙述路径尾部固定一行
    lines.append(_DISCLAIMER_LINE)
    return '\n'.join(lines)


def build_prompts(
    engine_result: Dict[str, Any], user_question: Optional[str] = None,
) -> tuple[str, str]:
    """生产和批跑共用的 system/user prompt，保证八字性别标记一致。"""
    features = build_payload(engine_result)
    features_json = json.dumps(features, ensure_ascii=False, separators=(',', ':'))
    system = build_system_prompt(format_fewshot_block(FEWSHOT_EXAMPLES))
    bazi_line = _bazi_line(engine_result)
    gender = str((engine_result.get('input') or {}).get('gender') or '').strip()
    gender = _GENDER_ZAO.get(gender) or _GENDER_ZAO.get(gender.lower())
    if gender:
        bazi_line += f'（{gender}）'
    user = build_user_prompt(features_json, bazi_line,
                             user_question or '', features=features)
    return system, user


def _loads_reading_json(raw: str):
    """仅剥离模型偶尔回显的 response_format 前缀，其他多余文本仍拒绝。"""
    prefix = '{"type":"json_object"}'
    if raw.startswith(prefix):
        raw = raw[len(prefix):].lstrip()
    return json.loads(raw)


def render_structured_reading(
    engine_result: Dict[str, Any],
    user_question: Optional[str] = None,
    *,
    call_llm: bool = True,
    model: str | None = None,
    validate: str = 'mark',
    timeout: float | None = None,
    retries: int | None = None,
    show_telemetry: bool = True,
) -> str:
    """引擎 dict → DeepSeek 七维 JSON 叙述 → 三层校验 → 展示文本。

    validate: 'mark'(默认)=普通违规附注于成品后；'reject'=L0 不过也拦截；
    两种模式遇结构化 reject 红线均整段拒出；'off'=不校验。
    LLM 不可用时降级返回 prompt 文本（不抛错）。
    """
    system, user = build_prompts(engine_result, user_question)
    features = build_payload(engine_result)
    if not call_llm:
        return f"===== SYSTEM =====\n{system}\n\n===== USER =====\n{user}"

    try:
        resp = call_deepseek(system, user, model=model, timeout=timeout, retries=retries)
    except LLMBackendError as e:
        _logger.warning('LLM 不可用，已降级: %s', e)
        return (f"[LLM 不可用，降级返回 prompt 文本 | 原因: {e}]\n\n"
                f"===== SYSTEM =====\n{system}\n\n===== USER =====\n{user}"
                f"\n\n{_DISCLAIMER_LINE}")

    raw = resp.get('text') if isinstance(resp, dict) else None
    if not isinstance(raw, str) or len(raw) > 16_000:
        _logger.warning('LLM 输出类型非法或超长，不予展示')
        return f"[LLM 输出非合法 JSON，不予展示 | 类型非法或超过16000字符]\n{_DISCLAIMER_LINE}"
    try:
        data = _loads_reading_json(raw)
    except ValueError as e:
        _logger.warning('LLM 输出非合法 JSON，不予展示（%s）', type(e).__name__)
        return f"[LLM 输出非合法 JSON，不予展示 | {type(e).__name__}]\n{_DISCLAIMER_LINE}"
    if not isinstance(data, dict) or validate != 'reject' \
            and any(not isinstance(data.get(d), dict) for d in DIMENSIONS):
        _logger.warning('LLM 输出 schema 结构异常，不予展示')
        return f"[LLM 输出非合法 JSON，不予展示 | 七维结构异常]\n{_DISCLAIMER_LINE}"

    report = validate_reading(data, features, engine_result) if validate != 'off' \
        else {'ok': True, 'violations': []}
    # 结构化 reject 红线在 mark 模式也不展示、不附注，
    # 整段拒出（前缀 '[断语被' 触发 service 层降级引擎直出）。scrub 守输入端
    # （payload 死亡词典物理屏蔽），reject 守输出端，拒答误报窗已在 _l2_enum 豁免。
    # G2（F6-3）：闸改结构化 reject 字段（不再按 detail 子串「死亡红线」匹配）。
    if validate != 'off' and any(x.get('reject') for x in report['violations']):
        return f'[断语被安全红线校验拦截，不予展示]\n{_DISCLAIMER_LINE}'
    if validate == 'reject' and any(x['layer'] == 'L0' for x in report['violations']):
        return ('[断语被 L0 schema 校验拦截，不予输出]\n'
                + '\n'.join(f"  - {x['detail']}" for x in report['violations'])
                + f'\n{_DISCLAIMER_LINE}')
    return format_reading(data, report, resp, show_telemetry=show_telemetry)


def _demo_cases_path() -> Path:
    """demo 用 trainset 案例路径——锚定 __file__，与调用方 cwd 无关。"""
    return Path(__file__).resolve().parents[1] / 'tests' / 'trainset' / 'cases.yaml'


def demo(case_id: str = 'b67-李嘉诚', question: str = ''):
    """单命示例：trainset 案例 → 引擎特征 → LLM 叙述 → 三层校验 → 展示。"""
    # CLI 入口专用局部导入（H-fix-4c 保留）：demo/main 仅命令行调试调用，
    # 延迟加载 engine 避免库调用方（feishu service 等）重复承担编排层导入。
    import yaml
    from mangpai.engine import MangpaiEngine
    with open(_demo_cases_path(), encoding='utf-8') as f:
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
