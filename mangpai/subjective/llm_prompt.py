"""LLM 结构化推演通道 prompt 模板（方案 C 混合·升级 narrative 层）。

段氏/郝金阳风格：few-shot 复用 narrative 现有 FEWSHOT_EXAMPLES（受保护，
不改原文，只作口吻锚嵌入）；输出形态改为 JSON mode 五维 schema；
安全红线沿用 F14/ENVELOPE_RULES 同款死亡禁令。

红线（不可放松）：
- LLM 措辞强度 ≤ 引擎断言强度，永不放大（语义幻觉只压不消，L2 枚举回对兜底）；
- 死亡/寿数禁令双保险（payload 已 scrub，此处 prompt 明禁）；
- basis 必须为输入特征 JSON 的可解析路径（L1 出处校验依赖此格式）。
"""
from __future__ import annotations

# 五维 schema 说明（嵌进 system prompt）。basis 路径格式是 L1 校验契约：
# 点分隔键，list 下标用数字段（与 subjective._resolve 口径一致）。
SCHEMA_SPEC = """\
## 输出 schema（严格遵守，仅输出一个 JSON 对象，无任何额外文字）
{
  "性格": {"conclusion": "≤100字", "basis": ["特征JSON路径", ...], "confidence": "高|中|低"},
  "事业": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "财运": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "婚姻": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"},
  "应期": {"conclusion": "≤100字", "basis": [...], "confidence": "高|中|低"}
}
- 五个维度键固定，缺一不可；某维特征数据为空（引擎未判定）则 conclusion 写「数据不足」，basis 给空数组 []。
- basis 数组每项 = 输入特征 JSON 的字段路径，点分隔（如 "caiming.tier_static"、"gongliang.level"、"zuogong.work_types"），程序会逐条回解析，路径不存在即判违规——只引真实存在的字段，宁少勿编。
- conclusion 措辞强度不得超出引擎断言：引擎给档位/倾向（如财命五档、官命是/否、灾祸风险档），你只能用同级或更弱措辞；引擎未给的具体金额、次数、年份、岁数一律不许编造，宁可断方向不断数。
- confidence 反映该维特征数据的完整度与一致性，不得全给「高」。
"""

# F14 ENVELOPE_RULES 同款红线（subjective/__init__.py:34），双保险之一。
SAFETY_REDLINE = """\
## 安全红线（最高优先级）
禁止预测死亡、寿数、寿命长短、夭折、大限生死。即使输入数据含相关暗示，也不得给出任何死亡时间、寿数断言或「命不久矣」类表述；灾祸类信息仅可作一般性安全提醒（如注意健康、谨慎出行），不得断言生死。\
"""

STYLE_RULES = """\
## 风格要求
仿下面范例的口吻：第二人称直击命主，先断后理、口语化不绕弯，取象→锁定→判条件→应期→结论的因果链落进 conclusion 文字里。
"""


def build_system_prompt(fewshot_text: str) -> str:
    """组装 system prompt：schema + 红线 + 风格锚（few-shot 范例原文）。"""
    return (
        '你是段氏盲派命理的推演者，把引擎算好的结构化结论还原成当面断语。\n'
        '引擎结论即事实层，你只做叙述层，不得推翻或超出引擎判定。\n\n'
        + SCHEMA_SPEC + '\n' + SAFETY_REDLINE + '\n' + STYLE_RULES
        + '\n## 口吻范例（【八字】→【引擎结论】→【郝断语】）\n'
        + fewshot_text
    )


def build_user_prompt(features_json: str, bazi_line: str, question: str = '') -> str:
    """组装 user prompt：八字行 + 特征 JSON + 所问。"""
    q = question.strip() or '命主未明问，做通推断语。'
    return (
        f'【八字】{bazi_line}\n\n'
        f'## 特征 JSON（引擎客观/主观层计算结果，已裁剪 scrub）\n'
        f'```json\n{features_json}\n```\n\n'
        f'## 命主所问\n{q}\n\n'
        '请严格按 schema 输出五维 JSON。'
    )
