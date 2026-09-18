# Kimi 任务：S2 · 文档批（外部使用者视角：安装 / 配 LLM / 完整流程）

## ⚠️ 执行指引
1. **先读**：你的评估报告（`/root/.claude/projects/-root-metaphysics/memory/kimi-shareability-assessment-20260918.md`——**S2 方案节 + 文档待修清单**）+ S1 落地的配置项（backlog S1 节 / `mangpai/subjective/llm_backend.py` 的 `MANGPAI_LLM_*` 八项）+ `README.md` + `docs/privacy-policy.md` + `mangpai/feishu/README.md` + `docs/llm-channel-20260818.md`
2. 本批 = **S2（对外文档批——分享目标的"看得懂"部分）**
3. 汇报 400 字内

## 背景
S1 已让 LLM 通道**技术可配**；S2 让外部使用者**知道怎么配、怎么跑通完整流程**（当前 README 快速开始只有引擎示例，**完全不提 LLM 配置**；隐私声明承诺"可替换本地模型"但用户找不到方法）。

## 任务清单（依 S1 报告待修清单 6 项）

### 1. `.env.example`（新建，仓库根）
- 列出全部配置项（含新 `MANGPAI_LLM_*` 八项 + 旧 `DEEPSEEK_*` 兼容说明 + `FEISHU_*` 可选接入层）
- 每项带注释：用途 / 默认值 / 是否必填
- **绝不填真实值**（占位符如 `your-api-key-here`）
- ⚠️ 隐私红线：不得含任何真实凭证

### 2. README 补充三节（核心）
按评估建议的结构：
- **「安装」**：Python 版本要求（实测 3.11/3.14；3.10+ 声明核实）、依赖（`pyyaml` 必备 / `sxtwl` 节气 / `anthropic` 软依赖——**修正"纯标准库"的误导表述**）、安装命令
- **「配置你自己的 LLM」**：`MANGPAI_LLM_*` 用法 + **多 provider 示例**（DeepSeek 默认 / OpenAI / 本地 Ollama / vLLM / 任意 OpenAI 兼容服务）+ `THINKING=0` 的适用场景（不支持该参数的服务）+ 关闭 LLM（纯引擎模式）
- **「完整流程示例」**：从排盘 → 判定 → LLM 叙述的端到端代码示例（不只是引擎 `calc_mangpai_full`）

### 3. 修正文档失实点
- `README.md:89`：`FEISHU_USE_LLM` 开关名 → 更新为通用别名 `MANGPAI_USE_LLM`（保兼容说明）
- `docs/privacy-policy.md:78/79/123`：措辞与实际能力同步（现在**真的**可替换任意 provider/本地模型——S1 已实现）
- `mangpai/feishu/README.md`：变量表补 `MANGPAI_USE_LLM` + 说明"飞书为可选接入层，核心流程可脱离"
- `docs/llm-channel-20260818.md`：补配置项链接 + 明确「**计价表仅对 DeepSeek 有效**」（未知 provider 显示"未计价"）

### 4. 记录 S3 关联项
- `llm_channel.py:480` cwd 相对路径（CLI demo 限制）→ 标注/记录给 S3

## 验证（DoD）
- [ ] `.env.example` 完整且无真实值
- [ ] README 三节齐备（安装/配 LLM/完整流程）+ 失实点修正
- [ ] privacy-policy/feishu README/llm-channel 同步
- [ ] **可复现性自检**：按你写的 README 步骤，从零（干净 venv）能跑通"引擎 → LLM 配置 → 完整流程"（可用 mock/本地无 key 检查到配置解析层）
- [ ] 零代码改动（纯文档 + .env.example）；`git status` 确认
- [ ] 六件套不必跑（无代码变动）

## 产出
- `.env.example` + README 三节 + 四处文档修正
- backlog「S2」节 + 收工更新
- 汇报 400 字内：三节结构 / `.env.example` 项数 / 失实点修正清单 / 可复现性自检结果 / S3 关联项

## 红线
- 纯文档（不改代码/测试）
- `.env.example` 零真实凭证
- 不调外部 API
