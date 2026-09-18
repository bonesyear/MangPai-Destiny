# Kimi 任务：分享可用性评估（他人配置自家 LLM 跑通完整流程，纯评估）

## ⚠️ 执行指引
- 纯评估：报告写 `/root/.claude/projects/-root-metaphysics/memory/kimi-shareability-assessment-20260918.md`，stdout 500 字内摘要
- **只评估不改动**
- **先读**：`README.md`（对外门面）+ `docs/privacy-policy.md`（隐私声明承诺）+ `docs/final-state-20260918.md`（系统终态）+ `mangpai/subjective/llm_backend.py`、`llm_channel.py`、`llm_prompt.py`（叙事层实现）+ `mangpai/feishu/README.md`（接入层说明）

## 核心背景（评估基准，务必以此为准）
**本仓库 share 到 GitHub 的目的**：让其他人**各自配置自己手头上的 LLM**（可能是 OpenAI / 本地 Ollama / vLLM / 其他兼容服务 / 其他厂商），也能**正常完整地跑通命理推演流程**。

→ 请以此为唯一标准评估：**一个外部使用者 clone 仓库后，能否用自己的 LLM 跑通完整流程（排盘 → 判定 → LLM 叙述）？**

## 已初步发现（请核实准确性 + 补充遗漏）
主会话已核实 LLM 通道的硬编码点：
1. `_API_URL = 'https://api.deepseek.com/chat/completions'`（端点硬编码）
2. `DEEPSEEK_API_KEY`（密钥变量名硬编码）
3. `_DEFAULT_MODEL = 'deepseek-flash'`（默认模型硬编码）
4. 请求体含 **provider 特有参数**：`'thinking': {'type': 'enabled'|'disabled'}` + `'reasoning_effort'`——**其他 OpenAI 兼容服务可能 400 报错**
5. env 回退路径硬编码 `/root/.hermes/.env`（部署者私有路径）
6. README/privacy-policy 承诺"可替换为本地模型 / 私有部署"——**与实现不符**

## 评估要求

### 1. 核实上述 6 点（准确/不准确/有补充）
逐点核实代码位置与影响，指出任何更正。

### 2. 全面扫"外部使用者视角"的全部阻碍（不止 LLM 配置）
请系统检查（每项给"阻碍/不阻碍 + 证据"）：
- **LLM 层**：provider 可配置性（端点/密钥/模型/特有参数/超时/重试）；不同 provider 的兼容性（哪些参数会导致 400）；成本估算表（`_PRICE`）在其他 provider 下会怎样（是否误导）
- **硬编码路径**：`/root/.hermes/.env`、`/tmp`、其他绝对路径（全仓扫）
- **依赖**：`sxtwl`（节气）/`yaml`/`anthropic`（软依赖）——安装说明是否清晰？缺失时行为？
- **入口**：有无 CLI（现状：仅库函数 `calc_mangpai_full` + 飞书 webhook）；外部使用者跑"完整流程（含 LLM 叙述）"的调用方式是什么？文档说清了吗？
- **平台假设**：Linux 专属？Python 版本要求（3.10+? 实测 3.11/3.14）？文件路径分隔符？
- **凭证管理**：有无 `.env` 模板（如 `.env.example`）？文档是否说明怎么配？
- **飞书组件**：是否清晰标注为"可选接入层"（不影响核心流程）？
- **文档缺口**：README 快速开始是否覆盖"含 LLM 叙述的完整流程"？有无安装步骤？

### 3. 重新评估两个隐患（分享视角）
- **③ 服务依赖**：拆分为 ③-a LLM provider 硬绑（阻碍分享）/ ③-b Hermes/飞书依赖（与使用者无关）——请判断这个拆分是否正确，并给出 ③-a 的严重级
- **④ Kimi 模型漂移**：判断是否与仓库使用者完全无关（仅内部开发工具事项）——给出定性

### 4. 修批方案（若需修）
给出让"任意 LLM + 完整流程"成立的**修批设计**：
- 配置项设计（变量名/默认值/向后兼容策略）
- provider 兼容处理（特有参数开关/自动降级/文档化）
- 文档补充（README 章节结构：配置 LLM / 示例 provider / 完整流程示例）
- 是否需要 CLI 入口（评估价值 vs 成本）
- 批次划分 + 每批工作量 + 验收标准（**红线：不得改变引擎判定与现有 DeepSeek 路径行为**；六件套）

## 产出
- 6 点核实结论 + 全阻碍清单（按严重级）+ ③④重新定性 + 修批方案
- stdout 500 字内摘要

## 红线
- 只评估不执行
- 不调外部 API
