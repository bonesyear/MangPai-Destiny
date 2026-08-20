# LLM 结构化推演通道 · 正式交付文档（2026-08-18）

> 通道：`mangpai/subjective/llm_channel.py`（+ `llm_prompt.py` / `llm_backend.py`）。
> 定位：narrative 层的结构化升级旁路——引擎 dict → 特征 JSON → DeepSeek 五维 JSON 断语 → 三层校验 → 展示。
> 验证：trainset 294 例五轮批跑（`output/llm_batch_20260818{,_v2.._v5}/`）+ remap 离线重评分。
> 本批（打磨收尾）：峰谷价计价落地 + 本文档；**引擎零改动**。

## §1 接口

### 单命入口

```python
from mangpai.subjective.llm_channel import render_structured_reading

text = render_structured_reading(
    engine_result,            # MangpaiEngine.compute_all() 的返回 dict
    user_question=None,       # 命主所问，缺省做通推断语
    call_llm=True,            # False=只返回组装好的 prompt 文本
    model=None,               # 缺省 deepseek-v4-flash（env DEEPSEEK_MODEL 可覆盖）
    validate='mark',          # 校验模式，见下
)
```

返回 = 展示文本（五维 conclusion+basis+confidence，附校验附注与 cost 行）。
LLM 不可用（无 key/网络失败）时降级返回 prompt 文本，不抛错；输出非合法 JSON 不予展示。

命令行单命示例：`python3 -m mangpai.subjective.llm_channel [case_id] [question]`（吃 trainset 案例）。

### validate 三模式

| 模式 | 语义 |
|---|---|
| `mark`（默认） | 违规不拦截，逐条附注于成品后（「请人工复核，勿直采信」） |
| `reject` | L0 schema 不过则整体拦截，不予输出 |
| `off` | 不校验（仅调试用） |

### 校验器返回结构

`validate_reading(data, features, engine_result)` →
`{'ok': bool, 'violations': [{'layer','detail'}...], 'n1': {...}, 'remapped': [...]}`。
层级：L0 schema / L1 basis 出处（含近-miss remap）/ L2 枚举回对（财档上限、官命是非、死亡词）/ N1 数字白名单（复用 `narrative.validate_narrative_numbers`）。

### 后端

`llm_backend.call_deepseek(system, user, ...)` →
`{'text','usage','cost_usd','price_tier','elapsed_s','model'}`；失败抛 `LLMBackendError` 由调用方降级。
`cost_usd` 按请求发出的实际时段（北京时间）自动选峰/谷档，`price_tier` 标注所中档（见 §3）。

## §2 验证记录

### 四指标达标线（终态 = E6/E7 后迭代 6/7，n=294 含 reading 例；L2 财档 0.34% / 官命 0）

| 指标 | 达标线 | 实测（最新） | 判定 |
|---|---|---|---|
| L0 schema 违规率 | ≈0 | 0/294 = **0.00%**（E7 实测） | ✅ |
| L1 basis 无出处率 | <5% | 4/294 = **1.36%**（E7 实测；remap 后迭代 4 曾 0.00%） | ✅ |
| N1 数字违规率 | <2% | 0/294 = **0.00%**（E7 实测） | ✅ |
| L2 枚举回对违规率 | 参考（无硬线） | 1/294 = **0.34%**（E7 实测：财档越限 1，官命矛盾 0；E6 校验器口径修后由 16→2→1） | ✅ 收敛 |
| S1 语义忠实度（离线） | 翻转 ≤1/30 | 0/30（D4 迭代 5 后评审实测） | ✅ |

> ⚠️ 2026-08-20 更新：L2 财档越限自交付时点 4.98% 经 E6（校验器口径修 6 条）→16→2、E7（官命否定窗 ±5 + 可达变体）→1（0.34%）；L1 因 E7 新断言口径 1.36%（迭代 4 remap 后 0.00% 系旧口径）。数字以 KB §9/CHANGELOG E6-E7 为准。

### 迭代轨迹（trainset 294 例全量批跑，各轮实测）

| 轮次 | 数据目录 | 有效校验 | L0 | L1 | L2 | N1 | 成本（旧平价口径） |
|---|---|---|---|---|---|---|---|
| 基线批 | `llm_batch_20260818` | 291 | 0.00% | 40.21%（219 条） | 21.99% | 26.80%（原始） | $1.0504 ≈ ¥7.56 |
| 迭代 1（basis 契约/财档锚定/大限白名单） | `_v2` | 289 | 0.35% | 23.88%（83 条） | 15.57% | 0.35% | $1.0806 ≈ ¥7.78 |
| 迭代 2（键清单入 user/否定窗） | `_v3` | 290 | 0.34% | 12.76%（44 条） | 15.17% | 0.34% | $1.1844 ≈ ¥8.53 |
| 迭代 3（键清单升 system 硬约束） | `_v4` | 291 | 0.69% | 9.62%（31 条） | 6.19% | 0.34% | $1.2480 ≈ ¥8.99 |
| 迭代 4（完整点路径清单/整行照抄） | `_v5` | 293 | 0.34% | 3.41%（10 条）✅ | 4.78% | 0.34% | $1.5134 ≈ ¥10.90 |
| remap 重评分（零 API，v5 数据重算） | `_v5` | 281 | **0.36%** | **0.00%** ✅ | **4.98%** | **0.36%** | — |

N1 基线批 26.80% 系白名单缺口假阳（大限边界 18/35/55 未入年龄白名单，76/80 条），迭代 1 补白名单后即达标，非 LLM 编造。

### L1 remap 规则表（`llm_channel._remap_basis`，只对意图唯一展开者转正，歧义仍记违规）

| 规则 | 模式 | 唯一展开依据 | 例 |
|---|---|---|---|
| A | 缺 `_ops` 前缀 | juxiang/all_findings 只存在于 xiangfa_ops | `xiangfa.juxiang` → `xiangfa_ops.juxiang` |
| B | 层级拍平 | 所引键在已解析前缀子树中恰有一处 | `hunyin.gong_attacked` → `hunyin.quality.gong_attacked` |
| C | 多包一层 | 恰有一种中间段删法可解析 | `hunyin.quality.summary` → `hunyin.summary` |
| D | 叶键别名 | hunyin 系原因列表统一键名 factors | `hunyin.duohun.signals` → `hunyin.duohun.factors` |

v5 残余 10 条（hunyin 6 / xiangfa 3 / caiming 1）全部唯一展开转正，**remap 后 L1=0**；歧义/臆造键不 remap（宁缺毋滥）。

## §3 使用指南

### 成本实测

- 单命（v5 均值）：in 32.5k / out 2.1k tokens，19.2s（max 37.5s）；8 并发全量 294 例 ~35 min。
- 批跑记录成本均为 2026-08-16 前旧平价（$0.14/$0.28）口径，**历史数据不回算**。
- 按现行峰谷价折算同 tokens（cache miss 口径，¥按 7.2）：

| 时段 | v4-flash 单命 | 294 例批（v5 量级） |
|---|---|---|
| 谷（半价） | ≈$0.0086 ≈ ¥0.06 | ≈$2.52 ≈ ¥18.1 |
| 峰 | ≈$0.017 ≈ ¥0.12 | ≈$5.03 ≈ ¥36.2 |

### 峰谷价（api-docs.deepseek.com 2026-08-18 复核）

- 峰段：UTC 01:00-04:00 / 06:00-10:00 = **北京时间 09:00-12:00、14:00-18:00**；其余时段半价。
- v4-flash：peak $0.44/$1.32，off-peak $0.22/$0.66（input/output，$/1M tokens）。
- v4-pro：peak $1.32/$3.96，off-peak $0.66/$1.98。
- 计价实现：`llm_backend._PRICING` 双档表 + `_price_tier(at)`（按请求发出的北京时间选档），成本随 `cost_usd`/`price_tier` 出账。

### 批次脚本一键命令

```bash
# 批跑（8 并发，分段可并行；LLM_BATCH_DIR 指定输出目录）
LLM_BATCH_DIR=output/llm_batch_<日期> python3 output/_llm_batch_trainset.py 0 294
# 汇总达标判定 + 成本
python3 output/_llm_batch_analyze.py output/llm_batch_<日期>
# 校验器改动后离线重评分（零 API 成本）
python3 output/_llm_batch_rescore.py output/llm_batch_<日期>
```

### 低峰期建议

批量复测/评估一律排**谷段**（北京 12:00-14:00、18:00-次日 09:00），成本减半；峰段只跑单例冒烟（单命 ¥0.12 内，无痛）。注意 2026-08-16 峰谷价相对旧平价实为**涨价**（谷 input $0.22 > 旧 $0.14），评估批次宜少而精。

## §4 安全红线（不可放松）

1. **死亡 scrub 双保险**：①供给侧 `build_payload` 统一 `_scrub_death` 递归过滤（死亡词典命中条目/键整条移除，修批A）；②输出侧 prompt 明禁（`llm_prompt.SAFETY_REDLINE`，F14 ENVELOPE_RULES 同款）+ L2 死亡词黑名单兜底（五轮批跑触发 0 次）。
2. **LLM 不落 compute_all**：本通道输出永不回写引擎 dict；引擎内部 siwang/寿元机制保留（F14 不变），detect_shouyuan_jixie 只推演不进消费链。
3. **只吃 trainset**：批跑/调优只用 trainset 294 例；heldout 215 例只评估不反推（few-shot 交叉污染 qi19/ans25 已备案，prompts 受保护不动）。
4. **措辞不放大**：LLM 措辞强度 ≤ 引擎断言（prompt 契约 + L2 枚举回对兜底），语义幻觉只压不消，违规附注由人工兜底。

## §5 维护项

- **峰谷价机制**：定价表在 `llm_backend._PRICING`（peak/offpeak 双档，cache miss 口径）；官方调价时改表 + 复核 `test_llm_backend.py` 三测。`_estimate_cost(model, usage, at=None)` 的 `at` 缺省=调用时刻，探针可传任意 epoch 秒复算历史档位。
- **历史成本口径**：2026-08-18 五轮批跑 jsonl 内 `cost_usd` 为旧平价口径（已标注，不回算）；此后新批次自动按峰谷档出账。
- **未来迭代记录位**：prompt/校验器迭代历史见 `docs/tasks/kimi-llm-{mvp,iter,iter2,iter3,iter4,remap,polish}.md`；新迭代在同目录续档 + 本文件 §2 轨迹表追加一行。L2 财档越限 11 条（小康→富为主）与官命矛盾 3 条为下批候选面。
- **与 narrative.py 的关系**：llm_channel = narrative 的结构化升级旁路，复用其 `_bazi_line` / `summarize_engine_result` / `validate_narrative_numbers` 与 few-shot 范例（`prompts/hao_style_fewshot`，受保护只读）；`render_hao_narrative` 旧散文通道保留并存，两通道互不回写引擎。
- **测试**：`mangpai/tests/test_llm_channel.py`（校验器 19 测）+ `test_llm_backend.py`（峰谷计价 3 测），全离线不触网。
