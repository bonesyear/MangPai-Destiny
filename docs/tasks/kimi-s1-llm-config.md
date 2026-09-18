# Kimi 任务：S1 · LLM 通道配置化（分享目标前提，叙事旁路层）

## ⚠️ 执行指引
1. **先读**：你的评估报告（`/root/.claude/projects/-root-metaphysics/memory/kimi-shareability-assessment-20260918.md`——**S1 方案节**）+ `mangpai/subjective/llm_backend.py` + `llm_channel.py` + `narrative.py` + `README.md:89` + `docs/privacy-policy.md:79/123`
2. 本批 = **S1（LLM 通道配置化——让外部使用者能配自家 LLM）**
3. 汇报 450 字内

## 背景（本批目的）
仓库分享目标 = 让其他人**配置自己手头上的 LLM**（OpenAI / Ollama / vLLM / 其他兼容服务）跑通完整流程。当前 LLM 叙事层硬绑 DeepSeek（+ narrative 硬绑 Anthropic）→ **目标级阻塞**。

## 任务 A：llm_backend 配置化（核心）
按评估报告 S1 方案实施：

### 配置项（回退链设计，保现状逐字不动）
| 新变量 | 回退 | 语义 |
|--------|------|------|
| `MANGPAI_LLM_BASE_URL` | → 无 → `https://api.deepseek.com/chat/completions`（现状默认） | 端点 |
| `MANGPAI_LLM_API_KEY` | → `DEEPSEEK_API_KEY`（现状） | 密钥 |
| `MANGPAI_LLM_MODEL` | → `DEEPSEEK_MODEL` → `deepseek-flash`（现状） | 模型 |
| `MANGPAI_LLM_THINKING` | → 默认 enabled（现状） | provider 特有参数开关 |
| `MANGPAI_LLM_TIMEOUT` / `MANGPAI_LLM_RETRIES` | → 现状默认值 | 超时/重试 |

**关键要求**：
1. **回退链完整**：未设新变量时，行为与当前**逐字节一致**（DeepSeek 路径零变化）
2. **provider 特有参数可关**：`thinking` / `reasoning_effort` 在其他 provider 会 400 → 提供关闭方式（如 `MANGPAI_LLM_THINKING=0` 时不发 `thinking` 字段；`reasoning_effort` 同理可配/可省）
3. **清私有路径**：`_load_api_key` 的 `/root/.hermes/.env` 硬编码回退 → 改为通用（如 `~/.env` / 环境变量优先 / 可选自定义路径 `MANGPAI_LLM_ENV_FILE`）
4. **成本估算降级**：`_PRICE` 表对其他 provider 会静默显示 ¥0（P2 项）→ 至少**明确标注**（未知 provider 显式返回 None/标注"未计价"而非误导性 ¥0）
5. **命名评估**：`FEISHU_USE_LLM` 开关（命名绑定飞书）→ 评估是否加通用别名 `MANGPAI_USE_LLM`（保兼容，飞书组件仍可用原名）

## 任务 B：narrative.py 的 Anthropic 硬绑处置（第二家）
- 现状：`narrative.py:370` 默认 `claude-sonnet-5`（Anthropic）——**仓库第二家硬绑 provider**
- 处置（评估后择一，说明理由）：
  a. 一并配置化（同 MANGPAI_LLM_* 体系，或独立 `MANGPAI_NARRATIVE_*`）
  b. 标注为**遗留通道**（若 llm_channel 已是主通道，narrative 旧路径可标废弃/明确"需自配 Anthropic 才能用"）
- 评估：当前系统实际走哪条通道？（llm_channel 为主？narrative 是否还有生产调用点）

## 验证（DoD）
- [ ] **DeepSeek 现状路径逐字节不变**（未设新变量时行为与改前一致——用 mock/对比验证）
- [ ] **新配置项生效**：mock server 测试各类配置（自定义端点/模型/关闭 thinking/自定义密钥变量）
- [ ] **narrative Anthropic 处置完成**（配置化或明确标注）
- [ ] 成本估算对未知 provider 不再误导（显式标注）
- [ ] 哨兵测试（mock 服务器，不调真实 API）
- [ ] 六件套：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_t1.json` 零翻转**（引擎零触）
- [ ] 自主复查：README/privacy-policy 的实现不符点，**本批不修文档**（留 S2），但需列出"文档待修清单"给 S2

## 分诊纪律
- 红线：**引擎判定零改动**、**DeepSeek 生产路径行为零变化**（本批只加配置通道，不改默认行为）
- 不带红前进

## 产出
- 配置化实现 + 哨兵 + narrative 处置 + 文档待修清单
- backlog「S1」节 + 收工更新
- 汇报 450 字内：配置项落地 / 回退链验证 / thinking 开关 / narrative 处置 / 成本估算处理 / 六件套结果 / 文档待修清单

## 红线
- 引擎零触 + DeepSeek 路径零变化
- 不调外部 API（用 mock）
