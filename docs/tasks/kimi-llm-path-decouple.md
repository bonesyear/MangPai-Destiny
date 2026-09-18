# Kimi 任务：LLM 通道去私有路径（B 方案）+ 项目根 .env 支持

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 主会话实测报告（见下「背景实证」）
2. 本批 = 代码改动 + 文档同步，**逐项验证必须实跑**（见 DoD）
3. 汇报 400 字内

## 背景实证（主会话已跑完，直接采信，勿重复诊断）

用户决策：**清掉仓库代码里的本机私有路径**，同时保证「任何人自由选 LLM」+「不影响本机部署」。

实测结论（`/root/metaphysics` 上跑出）：
1. `llm_backend._ENV_FILE = '/root/.hermes/.env'`（:46）是**本机部署路径硬编码**，须清
2. **本机通道不依赖它**：Hermes 用 `hermes_cli/env_loader.py`（dotenv）把 `/root/.hermes/.env` 加载进 os.environ，子进程继承 → 实测 `DEEPSEEK_API_KEY: 已设置 (len=35)`；将 `_ENV_FILE` 指向不存在路径后**仍能取到 key 并发出 API 请求**（HTTP 400 系 prompt 格式问题，非 key 问题）
3. **对外使用者的真缺口**：README:85 指向仓库根 `.env.example`，但 `_env_files()` 只读 `~/.env` + 私有 legacy——`cp .env.example .env`（项目根，常规做法）**读不到**
4. 全无 key 时已优雅报错（`LLMBackendError`），但**报错文本会列出私有路径**，须中性化

## 任务 A：去私有路径 + 回退链重设计

`mangpai/subjective/llm_backend.py`：
1. 删除 `_ENV_FILE = '/root/.hermes/.env'`（:46）及其 docstring 引用（:11、:45 的私有路径说明同步中性化）
2. `_env_files()` 回退链改为（保序）：
   - `MANGPAI_LLM_ENV_FILE` 显式指定 → 只用它
   - 否则：**项目根 `.env`**（`Path(__file__).resolve().parents[2] / '.env'`，即 `/root/metaphysics/.env`）→ `~/.env`
   - **理由**：README 教 `cp .env.example .env`，项目根是使用者预期位置；`~/.env` 保留家目录习惯
3. `_load_api_key` 报错文本随之中性化（不得再出现 `/root/.hermes/...`；只出现「项目根 .env / ~/.env」这类通用表述）
4. **保持零依赖**：沿用现有手工解析（`startswith(name + '=')`），**不要引入 python-dotenv**

## 任务 B：gitignore 补漏

`.gitignore`：补 `.env.local` 与 `.env.*.local`（测试用 `git check-ignore -v` 验证命中；确认现有 `.env` 规则未被破坏，`.env.example` 仍不被忽略）

## 任务 C：文档同步

1. `README.md`：`MANGPAI_LLM_ENV_FILE` 行（:95）默认值描述更新为「项目根 `.env`；可选」；「配置你自己的 LLM」节补一句 `cp .env.example .env`（放项目根）即可被自动读取
2. `.env.example`：顶部注释说明放置位置（项目根，或 `MANGPAI_LLM_ENV_FILE` 指定）
3. `docs/llm-channel-20260818.md`：env 链描述同步（如提及旧私有路径则改准）

## DoD（逐项实跑，勿只读代码）

- [ ] **A1** 清路径：全仓 `grep -rn "/root/.hermes" mangpai/ README.md docs/*.md`（当前对外文档/包内）零命中；历史报告文档不改（如实记录）
- [ ] **A2** 环境变量在 + 无 legacy → 真实 API 调用成功（用 `json_mode=False` 或 prompt 含 json 避免 400 混淆；单次调用即可，成本极小）
- [ ] **A3** 全无 key → `LLMBackendError` 报错文本**不含任何私有路径**（打印全文核对）
- [ ] **A4** 项目根 `.env` 生效：临时创建 `/root/metaphysics/.env`（**占位假 key，勿用真 key**）→ 验证 `_load_api_key()` 能读到 → **测试后立即删除**
- [ ] **A5** `~/.env` 仍在链内（顺序：MANGPAI_LLM_ENV_FILE → 项目根 → ~/.env）
- [ ] **B** `git check-ignore -v .env .env.local .env.example` 三例行为符合预期（前两者忽略、后者不忽略）
- [ ] **C** 文档三处同步，`grep` 复核无残留旧描述
- [ ] **六件套**：pytest 全绿 + verify 432/70/64/20 + **blind vs `snapshots/20260918_t1.json` 零翻转** + 双 seed 逐字节一致 + 67/famous 无变化 + 分层两件套通过
- [ ] **汇报** 400 字内（改动清单 + 五项验证实测结果 + 六件套数字）

## 红线

- **引擎判定零改动**（本批只动 LLM 通道配置读取 + 文档）
- 不引入新依赖（保持零依赖）
- 不改历史报告文档（如实记录原则）
- 不真跑批跑脚本（会调 LLM API）；A2 的单次调用除外（成本 ~¥0.001）
- 提交前跑 `git status --short` 核对改动范围，`.env` 类临时文件不得入库
