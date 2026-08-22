"""LLM 结构化推演通道 prompt 模板（方案 C 混合·升级 narrative 层）。

段氏/郝金阳风格：few-shot 复用 narrative 现有 FEWSHOT_EXAMPLES（受保护，
不改原文，只作口吻锚嵌入）；输出形态改为 JSON mode 七维 schema；
安全红线沿用 F14/ENVELOPE_RULES 同款死亡禁令。

红线（不可放松）：
- LLM 措辞强度 ≤ 引擎断言强度，永不放大（语义幻觉只压不消，L2 枚举回对兜底）；
- 死亡/寿数禁令双保险（payload 已 scrub，此处 prompt 明禁）；
- basis 必须为输入特征 JSON 的可解析路径（L1 出处校验依赖此格式）。
"""
from __future__ import annotations

# 七维 schema 说明（嵌进 system prompt）。basis 路径格式是 L1 校验契约：
# 点分隔键，逐字照抄；数组只引数组名本身，禁止下标（llm_channel._l1_basis 同口径）。
SCHEMA_SPEC = """\
## 输出 schema（严格遵守，仅输出一个 JSON 对象，无任何额外文字）
{
  "性格": {"conclusion": "≤100字", "basis": ["特征JSON路径", ...], "confidence": "高|中|低"},
  "事业": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "财运": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "婚姻": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "应期": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "迁移": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "相貌": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"}
}
- 七个维度键固定，缺一不可；某维特征数据为空（引擎未判定）则 conclusion 写「数据不足」，basis 给空数组 []。
- basis 数组每项 = 输入特征 JSON 中**逐字照抄**的字段路径，点分隔（如 "caiming.tier_static"、"gongliang.level"、"zuogong.work_types"），程序会逐条回解析，路径不存在即判违规——只引真实存在的字段，子键拿不准宁缺毋编，不得按命理常识臆测键名（特征 JSON 里没有的键一律不写）。
- 数组字段（如 xiangfa_ops.juxiang、xiangfa.all_findings、zuogong.work_actions、liunian_analysis.liunian）只允许引用数组名本身；禁止任何形式的下标（如 "xiangfa_ops.juxiang[7]"、"juxiang.7"），也禁止把数组当字典按内容取键（如 "juxiang.寒湿"）。
- conclusion 措辞强度不得超出引擎断言：引擎给档位/倾向（如财命五档、官命是/否、灾祸风险档），你只能用同级或更弱措辞；引擎未给的具体金额、次数、年份、岁数一律不许编造，宁可断方向不断数。
- 财运维的档位词只允许「巨富/富/小康/平/贫」五选一，且必须取自 caiming.tier_static / caiming.tier 的原值，不得超过两轨中的较高档。功量金额档（百万/千万/亿级）≠财命档，不得据金额大小把档位升格。
- 事业维的职业部分：主荐职业必须取自 zhiye.primary 对应桶；zhiye.primary 为空=引擎无明确职业倾向，必须如实说「无明确职业倾向」，禁止断言任何具体职业（高分桶只能作「倾向性参考」并注明引擎未定）。
- 应期维：逐运吉凶以 dayun_analysis.dayun 各运 overall 与正负信号为准，逐年以 liunian_analysis 逐年 overall 为准，吉凶性质不得相反（凶运说成吉=翻转），吉凶参半须两面并陈；禁止脱离大运/流年表的泛化套话（如「近年多有是非」「晚景渐佳」），表外年份不许断言吉凶。
- 迁移维：只许依据 qianyi.qianyi_yuanju 的 marker 与 qianyi.qianyi_yingqi 的应期窗叙述；措辞上限「迁移/远行」，绝对禁止「出国/移民/海外/国外/外国」（任何形态均不许，含否定式、解释式提及）；conclusion 只写迁移/远行的象本身，不要声明或解释你在遵守禁令；marker 与应期窗均空=无迁移信号，必须如实说明、不得断言迁移，且该维 basis 必须给空数组 []（qianyi 各键均空=无出处，禁止引用）；应期窗为或然窗，凡引用应期窗该维 confidence 锁「低」。
- 相貌维：只许引用 xiangmao 各线 marker 的原文描述（秀气透干/金水伤官/活木见火/眼象/魅力/身材）；叙述正文任何位置不得出现「漂亮/美/丑/帅」字样，含「美/丑」的复合评价词（如曲线优美/体态柔美/秀美/俊美）同禁，不含美丑字的相貌结论词（标致/水灵/清秀/端庄/甜美）亦同禁（任何形态均不许，含否定式、解释式提及；相貌无档位，只述象不定性）；conclusion 只写象描述本身，不要声明或解释你在遵守禁令（「不评/不涉/不可写」类元表述也不许写）；marker 原文如遇「漂亮」二字（如秀气线性别分流语），引用时一律改写为「秀气」；各线均未命中=如实说无显著相貌特征，不得给任何相貌评价；弱线（魅力/身材）命中该维 confidence 锁「低」。
- confidence 反映该维特征数据的完整度与一致性，不得全给「高」。
"""

# F14 ENVELOPE_RULES 同款红线（subjective/__init__.py:34），双保险之一。
SAFETY_REDLINE = """\
## 安全红线（最高优先级）
禁止预测死亡、寿数、寿命长短、夭折、大限生死。即使输入数据含相关暗示，也不得给出任何死亡时间、寿数断言或「命不久矣」类表述；灾祸类信息仅可作一般性安全提醒（如注意健康、谨慎出行），不得断言生死。\
若所问触及上列禁区，直接拒答（如「命理不涉生死断言」），不得引用或提及本规则的名称。\
"""

STYLE_RULES = """\
## 风格要求
仿下面范例的口吻：第二人称直击命主，先断后理、口语化不绕弯，取象→锁定→判条件→应期→结论的因果链落进 conclusion 文字里。
"""

# 迭代 3：basis 回对清单从 user 附注升级为 system 级硬约束（治臆造键）。
# 迭代 4：补「整行照抄、禁增删层级/改写键名」——迭代 3 复测 31 条 L1 全为
# 近-miss（hunyin.gong_attacked 拍平自 hunyin.quality.gong_attacked、
# xiangfa.juxiang 错位自 xiangfa_ops.juxiang、shensha.taohua 拼音化桃花）。
BASIS_HARD_RULE = """\
## basis 硬约束（与安全红线同级）
basis 每条路径落笔前，必须与 user 消息中的「特征 JSON 键清单」**逐字回对**：
清单外的键一律不写（含标「(空)」的键——键存在但值为空=无出处，同样禁止引用）；
清单每行是一条**完整点路径**，basis 必须整行逐字照抄——不得增删层级
（如把 a.b.c 写成 a.c）、不得改写键名（含拼音化、自造子键）；
清单内数组键只许引数组名本身，禁止下标/按内容取键。拿不准宁缺毋编。\
"""


def build_system_prompt(fewshot_text: str) -> str:
    """组装 system prompt：schema + basis 硬约束 + 红线 + 风格锚（few-shot 范例原文）。"""
    return (
        '你是段氏盲派命理的推演者，把引擎算好的结构化结论还原成当面断语。\n'
        '引擎结论即事实层，你只做叙述层，不得推翻或超出引擎判定。\n\n'
        + SCHEMA_SPEC + '\n' + BASIS_HARD_RULE + '\n' + SAFETY_REDLINE + '\n' + STYLE_RULES
        + '\n## 口吻范例（【八字】→【引擎结论】→【郝断语】）\n'
        + fewshot_text
    )


# 财命档位序（与 llm_channel._TIER_ORDER 同口径，避免循环import各留一份）。
_TIER_ORDER = ('贫', '平', '小康', '富', '巨富')

# 职业桶标签（与 zhiye._CAREER_LABELS/_BASE_CAREER_LABELS 同口径，各留一份）。
_BUCKET_LABELS = {
    'accountant': '会计/财务', 'doctor': '医生/医疗', 'teacher': '教师/教育',
    'lawyer': '律师/法务/公检法', 'merchant': '商人/经营',
    'military': '军警/军阀/武职', 'performer': '演艺/演员',
    'laborer': '农民/工人·体力劳动者', 'unemployed': '无业',
}


def _empty(v) -> bool:
    """空值判定（与 llm_channel._l1_basis 的「为空」同口径）。"""
    return v is None or v == {} or v == [] or v == ''


def _key_manifest(features: dict) -> str:
    """从特征 JSON 实际结构生成键清单（与 build_payload 输出逐字一致）。

    迭代 4 改为**完整点路径**格式（每行一条可引路径，整行照抄即合法 basis）——
    旧括号嵌套式（quality(..., gong_attacked)）诱导 LLM 拍平/错位归属。
    覆盖深度=顶层+两级子键（与迭代 3 同）；数组键行内标「禁下标」，
    空值键行内标「(空)」（键存在但无值=无出处，basis 禁止引用）。
    """
    lines = []

    def walk(prefix: str, d: dict, depth: int) -> None:
        for k, v in d.items():
            path = f'{prefix}.{k}'
            if isinstance(v, list):
                lines.append(f'{path}[](空,禁引用)' if _empty(v) else f'{path}[]禁下标')
            elif isinstance(v, dict) and v and depth > 0:
                lines.append(path)
                walk(path, v, depth - 1)
            elif _empty(v):
                lines.append(f'{path}(空)')
            else:
                lines.append(path)

    for top, val in features.items():
        if isinstance(val, dict) and val:
            lines.append(str(top))
            walk(str(top), val, 2)
        elif isinstance(val, list):
            lines.append(f'{top}[](空,禁引用)' if _empty(val) else f'{top}[]禁下标')
        elif _empty(val):
            lines.append(f'{top}(空)')
        else:
            lines.append(str(top))
    return '\n'.join(lines)


def _tier_anchor(features: dict) -> str:
    """本案财命档锚定行：两轨原值 + 上限档（治 L2 档位越限）。"""
    cm = features.get('caiming') or {}
    vals = {k: str(cm.get(k) or '') for k in ('tier_static', 'tier')}
    ranks = [_TIER_ORDER.index(v) for v in vals.values() if v in _TIER_ORDER]
    if not ranks:
        return ''
    ceiling = _TIER_ORDER[max(ranks)]
    return (f'【本案财命档锚定】caiming.tier_static={vals["tier_static"] or "无"}（原局轨）、'
            f'caiming.tier={vals["tier"] or "无"}（全量轨）；两轨较高档=「{ceiling}」。'
            f'财运 conclusion 的档位词只允许贫/平/小康/富/巨富五选且不得超过「{ceiling}」；'
            '功量金额档（百万/千万/亿级）≠财命档，不得据金额升格。'
            f'能力承诺句（「能成/可成/可达/可至/勤劳可…」）与条件假设句（「一旦/若…便…」）中的'
            f'档位词同样不得超过「{ceiling}」——条件再顺、应期再巧也不许承诺破档。')


def _zhiye_anchor(features: dict) -> str:
    """本案职业锚定行（迭代 5，治 S1 职业维翻转：无倾向被断言 + 主荐桶不一致）。"""
    zy = features.get('zhiye') or {}
    if not isinstance(zy, dict) or not isinstance(zy.get('scores'), dict):
        return ''
    scores = zy['scores']
    thr = zy.get('min_score_threshold') or 6
    primary = zy.get('primary') or ''
    label = zy.get('primary_label') or _BUCKET_LABELS.get(primary, '')
    if primary:
        cands = [f'{_BUCKET_LABELS.get(b, b)}{s}分'
                 for b, s in sorted(scores.items(), key=lambda kv: -kv[1])
                 if b != primary and isinstance(s, (int, float)) and s >= thr]
        cand_txt = ('；候选桶=' + '、'.join(cands)) if cands else ''
        direct = ''
        if primary in ('unemployed', 'laborer'):
            # F-V3-1（zhenbao-23a 族）：无业/体力是引擎判定而非无倾向
            direct = (f'「{label}」是引擎的明确判定（非无倾向），事业维必须如实直述「{label}」，'
                      '不得改述为「无明确职业倾向」，也不得另给安稳就业建议。')
        return (f'【本案职业锚定】引擎主荐桶={label}（zhiye.primary={primary}）{cand_txt}。'
                f'事业维的职业主荐必须是「{label}」，不得换成其他职业类别；'
                '候选桶只可明确标注「候选/次选」提及，不得与主荐并列或取代主荐。'
                + direct)
    top = [f'{_BUCKET_LABELS.get(b, b)}{s}分'
           for b, s in sorted(scores.items(), key=lambda kv: -(kv[1] or 0))
           if isinstance(s, (int, float)) and s > 0][:3]
    return (f'【本案职业锚定】引擎未给出明确职业倾向（zhiye.primary 为空，'
            f'各桶得分均低于成象阈值{thr}）。事业维必须如实说「无明确职业倾向」，'
            '禁止断言任何具体职业；'
            + (f'只可提及相对高分桶（{"、".join(top)}）作「倾向性参考」并注明引擎未定倾向。'
               if top else '不得给出任何职业方向。'))


def _yingqi_anchor(features: dict) -> str:
    """本案应期锚定行（迭代 5，治 S1 应期维翻转/套话）：逐运+逐年吉凶锚。"""
    lines = []
    dys = (features.get('dayun_analysis') or {}).get('dayun') or []
    if dys:
        seg = []
        for d in dys:
            pos = '、'.join(str(x) for x in (d.get('positive_signals') or [])[:2])
            neg = '、'.join(str(x) for x in (d.get('negative_signals') or [])[:2])
            sig = ''
            if pos or neg:
                sig = f'（{"吉:" + pos if pos else ""}{"；" if pos and neg else ""}{"凶:" + neg if neg else ""}）'
            age = (f'{d["start_age"]}-{d["end_age"]}岁'
                   if d.get('start_age') is not None else f'第{d.get("order")}步')
            seg.append(f'{d.get("gz")}运[{age}]={d.get("overall")}{sig}')
        lines.append('大运逐运锚（dayun_analysis.dayun）：' + '；'.join(seg))
    lns = (features.get('liunian_analysis') or {}).get('liunian') or []
    if lns:
        lines.append('流年逐年锚（liunian_analysis.liunian）：'
                     + '；'.join(f'{e.get("gz")}={e.get("overall")}' for e in lns))
    if not lines:
        return ''
    return ('【本案应期锚定】' + '\n'.join(lines) + '\n'
            '应期维叙述必须逐运/逐年锚定上述 overall 与正负信号：吉凶性质不得与 '
            'overall 相反（凶说成吉=翻转），吉凶参半须两面并陈；禁止脱离此表的'
            '泛化套话（如「近年多有是非」「晚景渐佳」），表外运年不许断言吉凶。')


def _qianyi_anchor(features: dict) -> str:
    """本案迁移锚定行（N1 七维批）：qianyi markers/应期窗 + 出境词禁令。"""
    qy = features.get('qianyi')
    if not isinstance(qy, dict):
        return ''
    yj = qy.get('qianyi_yuanju') or {}
    yq = qy.get('qianyi_yingqi') or {}
    markers = [str(m) for m in (yj.get('markers') or [])]
    moves = yq.get('move_windows') or []
    stays = yq.get('stay_windows') or []
    ban = '措辞上限「迁移/远行」，出境类断语任何形态（含否定式）一律禁止；只写象，不要声明你在遵守禁令。'
    if not markers and not moves:
        return ('【本案迁移锚定】引擎无迁移信号（qianyi 原局 marker 与应期窗均空）。'
                '迁移维必须如实说「无迁移信号」，不得断言迁移/远行；'
                '该维 basis 必须给空数组 []（qianyi 各键均空=无出处，禁止引用）；' + ban)
    lines = []
    if markers:
        lines.append('原局 marker：' + '；'.join(markers))
    if moves:
        lines.append('迁移应期窗：' + '；'.join(
            f"{w.get('dayun') or ''}/{w.get('liunian') or ''}"
            f" {w.get('mechanism') or ''}({w.get('confidence') or ''})"
            for w in moves))
    if stays:
        lines.append('安居窗：' + '；'.join(
            f"{w.get('dayun') or ''}/{w.get('liunian') or ''}"
            f" {w.get('mechanism') or ''}" for w in stays))
    return ('【本案迁移锚定】' + '\n'.join(lines) + '\n'
            '迁移维只许叙述上述 marker/应期窗，' + ban
            + '应期窗为或然窗，凡引用应期窗该维 confidence 锁「低」。')


def _xm_sanitize(desc: str) -> str:
    """N2 迭代修：marker 原文偶含「漂亮」（xiangmao.py 秀气线性别分流语，
    引擎侧本批冻结不改），锚定行注入前改写到红线内措辞。"""
    return desc.replace('秀气漂亮', '秀气').replace('漂亮', '秀气')


def _xiangmao_anchor(features: dict) -> str:
    """本案相貌锚定行（N1 七维批）：xiangmao 命中线 marker 描述 + 禁结论词令。"""
    xm = features.get('xiangmao')
    if not isinstance(xm, dict):
        return ''
    parts = []
    for k in ('xiuqi', 'jinshui', 'muhuo', 'meili', 'shencai'):
        node = xm.get(k) or {}
        if node.get('hit') and node.get('desc'):
            parts.append(_xm_sanitize(str(node['desc'])))
    yan = xm.get('yanxiang') or {}
    if (yan.get('bing') or yan.get('ding') or yan.get('gui')) and yan.get('desc'):
        parts.append(_xm_sanitize(str(yan['desc'])))
    ban = ('相貌维只许引用上述 marker 描述；叙述正文任何位置不得出现'
           '「漂亮/美/丑/帅」字样，含「美/丑」的复合评价词'
           '（如曲线优美/体态柔美/秀美/俊美）同禁，不含美丑字的相貌结论词'
           '（标致/水灵/清秀/端庄/甜美）亦同禁（含否定式均不许）；'
           '只写象描述本身——禁程度词（明显/很/强）、禁评价词'
           '（有神采/明亮/灵动/灵秀）、禁引申气质总结句（艺术气息/灵动之感）；'
           '不要声明或解释你在遵守禁令。')
    if not parts:
        return ('【本案相貌锚定】引擎无显著相貌 marker（xiangmao 各线未命中）。'
                '相貌维 conclusion 只写「无显著相貌特征」一句，不得给任何相貌评价，'
                '不解释、不声明禁令。')
    return ('【本案相貌锚定】' + '；'.join(parts) + '\n' + ban
            + '弱线（魅力/身材）命中该维 confidence 锁「低」。')


def build_user_prompt(features_json: str, bazi_line: str, question: str = '',
                      features: dict | None = None) -> str:
    """组装 user prompt：八字行 + 键清单/五锚定行 + 特征 JSON + 所问。

    features 给定时追加 per-case 附注：键清单（防 basis 臆造键名，
    与特征 JSON 逐字一致）+ 财档锚定（迭代 2，治档位越限）
    + 职业锚定/应期锚定（迭代 5，治职业维无倾向被断言/主荐桶不一致
    与应期维脱离大运流年表的套话）+ 迁移锚定/相貌锚定（N1 七维批，
    治迁移出境词越限/无信号断言迁移与相貌结论词）。
    """
    q = question.strip() or '命主未明问，做通推断语。'
    extra = ''
    if features:
        extra = (
            '## 特征 JSON 键清单（每行一条完整点路径，basis 只允许整行逐字照抄；'
            '标 []禁下标 的是数组，只许引数组名本身，禁止下标/按内容取键；'
            '标 (空) 的键值为空=无出处，禁止引用；'
            '清单里没有的键一律不写，不得增删层级/改写键名）\n'
            + _key_manifest(features) + '\n\n'
        )
        for anchor in (_tier_anchor(features), _zhiye_anchor(features),
                       _yingqi_anchor(features), _qianyi_anchor(features),
                       _xiangmao_anchor(features)):
            if anchor:
                extra += anchor + '\n\n'
    return (
        f'【八字】{bazi_line}\n\n'
        + extra
        + f'## 特征 JSON（引擎客观/主观层计算结果，已裁剪 scrub）\n'
        f'```json\n{features_json}\n```\n\n'
        f'## 命主所问\n{q}\n\n'
        '请严格按 schema 输出七维 JSON。'
    )
