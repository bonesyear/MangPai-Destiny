# LLM 通路 · trainset 294 例批量校验报告（2026-08-18）

> 任务书：`docs/tasks/kimi-llm-batch.md`。纯评估批：引擎零改动、prompt 零改动；LLM 输出不落 compute_all dict。
> 数据：`output/llm_batch_20260818/batch_*.jsonl`（每例 tokens/耗时/校验结果/reading 原文，可追溯）。
> 脚本：`output/_llm_batch_trainset.py`（批跑，8 并发）+ `output/_llm_batch_analyze.py`（汇总）。

## 1. 达标判定（n=294，有效校验 291）

| 指标 | 达标线 | 实测 | 判定 |
|---|---|---|---|
| L0 schema 违规率 | ≈0 | 0/291 = **0.00%**（另 JSON 解析失败 3/294 = 1.02%：cj-平辛辛苦苦挣钱/cj-足球/yx-经理） | ✅ |
| L1 违规率（basis 无出处） | <5% | 117/291 = **40.21%**（219 条） | ❌ 严重超标 |
| N1 数字违规率 | <2% | 原始 78/291 = 26.80%；剔除系统性「55岁」假阳（76/80 条，见 §3）后 **4/291 = 1.37%** | 原始❌ / 修正口径✅ |
| L2 枚举回对 | （无硬线） | 64/291 = 21.99%（65 条，58 条为财档越上限） | 参考 |

结论：**L1 不达标，本通道暂不可进正式通道**；N1 实为白名单缺口（单点修复即达标）；L0/schema 侧健康。

## 2. 违规分布

- 维度分布（条数）：性格 108 / 财运 49+58(档位越限) / 应期 31 / 事业 21 / 婚姻 17。**性格维独占约一半**。
- L1 两类失败模式：
  - 编造子键 125 条：`shensha.tianyi_gui_ren`/`shensha.hua_gai`（payload 已三层收口无此键）、`hunyin.is_duohun`、`caiming.wealth_grade`、`caiming.details`、`caiming.caifu_view.blockers` 等——LLM 按命理常识臆测字段名。
  - 数组下标越界/当 dict 用 91 条：`xiangfa_ops.juxiang[7].desc`（实长<7）、`xiangfa.all_findings[26]`、`zuogong.work_actions[3]`、`xiangfa_ops.juxiang.寒湿`（juxiang 是 list 被当 map 按键引用）。
- L1 top 前缀：xiangfa_ops 40 / caiming 34 / liunian_analysis 17 / hunyin 16 / zuogong 15 / yunfan 14 / xiangfa 14。
- L2：财档越上限 58（小康→富 最多，另有 富→巨富、贫→平/小康）；官命矛盾 3（含假阳，见 §3）；死亡红线词 0 触发 ✅。
- N1 修正后真实 4 例：gj-入狱一年「50岁」、cj-周恩来「3年」、yx-厅级「2030年」、famous-辛普森「二次婚」。

## 3. 典型案例

1. **b67-复例二副总**（L1 编造键）：性格 basis 引 `shensha.tianyi_gui_ren`/`hua_gai`——特征 JSON 神煞只含核心五+灾祸三煞，天乙/华盖属传统十神煞已被降级剔除，LLM 凭命理常识补出。
2. **zhenbao-12 阎锡山**（L1 下标越界 + L2 越档）：`xiangfa_ops.juxiang[7].desc` 数组实长不足；财运 conclusion 写「巨富…亿至数十亿级」而引擎 tier=富——LLM 把功量金额档（亿级）误升格为财命档。
3. **reg67-劫刃制官杀**（L2 贫→富 + L1 把 list 当 map）：引擎 tier=贫，叙述「功量富档达千万级，能积中产之富」；basis `xiangfa_ops.juxiang.暖燥` 把数组当字典键。
4. **zhenbao-23a**（L2 假阳）：事业 conclusion「官命否决」被官命正向关键词「官命」命中——否定词在后（否决/无缘）超出前两字符否定窗口，启发式局限（代码注释已备案此残留）。
5. **N1 系统性假阳「55岁」×76**：LLM 引大限宫位边界（1-18/18-35/35-55/55+，特征 JSON 内含）作应期表述，N1 年龄白名单只收 dayun start/end_age+当前年龄，不覆盖大限边界——白名单缺口，非 LLM 编造。

## 4. prompt 调优方向（只吃 trainset，落地下一批）

1. **basis 路径契约收紧**（治 L1，最大杠杆）：system prompt 增「basis 只能从特征 JSON 中**逐字照抄**的键路径；数组字段（juxiang/all_findings/work_actions/liunian 等）禁止带下标，直接引数组字段名本身；拿不准的子键宁缺毋编」。可考虑 user prompt 附顶层键清单+一句话语义。
2. **财档枚举锚定**（治 L2 58 条）：user prompt 直接给出「财命档位上限=富（引擎 tier_static/tier 原值），conclusion 档位词只允许贫/平/小康/富/巨富五选且≤上限」；并注明「功量金额档（百万/千万/亿级）≠财命档，不得据金额升格」。
3. **岁数引用禁令或白名单扩容**（治 N1 假阳）：二选一——prompt「禁止给出具体岁数，只可引大运起止年龄」，或校验侧把大限边界 18/35/55 并入年龄白名单。建议两者都做（校验侧一行）。
4. **L2 官命否定窗假阳**：校验侧否定窗口扩到后两字符（否决/无缘/不成），或 prompt 要求 is_guanming=False 时避免单独出现「官命」一词。一行级修复。
5. **应期维**：liunian 子结构指引（`liunian_analysis.liunian[i].overall` 系臆造），同 1 的数组规则可覆盖大半。

## 5. 成本实测

- 总成本 **$1.0504 ≈ ¥7.56**（预估 ~¥8 ✓）；tokens in 6.50M / out 0.50M（含 thinking）。
- 单例均值：in 22.3k / out 1.7k，**18.6s**（max 242.8s）；8 并发全量 ~35 min。
- API 空响应 3 例（thinking 耗尽 max_tokens，重试即恢复，已补跑入 batch_retry.jsonl）。

## 6. 本批改动备案

- **引擎零改动**；prompt 零改动。
- `llm_channel.py` 校验器健壮性修复 2 处（非对象维度节点 L1/L2 跳过防 AttributeError——LLM 返回「性格」为字符串时批跑崩于 batch_101_198；修复后该类输出正常记 L0 违规）。`test_llm_channel.py` 9 测全绿。
- pytest 全量：**671 passed + 1 xfailed + 19 xpassed，0 failed**（修批B 口径 662 passed，差 9 系修批B→本批间既有演进，本批只加 output/ 脚本不改引擎）。
