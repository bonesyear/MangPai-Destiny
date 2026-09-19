# MangPai · Chinese Bazi Analysis Engine

基于段建业/郝金阳盲派理论的八字命理推演引擎。59 模块四层架构，1149 验证用例全绿（+1 xfail）。

> 🔒 **隐私优先**：引擎本地运算，零外发、零落盘、不建用户档案；命理计算始终在你自己机器上完成。详见 [隐私说明](docs/privacy-policy.md)。

## 什么是盲派 (MangPai / Blind-Pai)

盲派是段建业、郝金阳一脉的八字命理流派。与传统的子平格局派不同，盲派不看重日主旺衰和用神喜忌，而是聚焦于**八字在做什么**——谁在做功、怎么做功、做了多少。核心方法论：宾主体用、做功类型、墓库、象法。

## 架构

```
八字输入 → Foundation（公共基础）→ Objective（确定性检测）→ Subjective（解释性判断）→ Narrative（叙事层）
```

| 层 | 名称 | 模块数 | 职责 |
|------|------|:--:|------|
| **Foundation** | 基础层 | 2 | 干支性情赋（滴天髓 65 条规则）+ 六十甲子纳音表（跨流派共享） |
| **Objective** | 客观层 | 27 | 排盘、节气、藏干、长生、十神（shishen 单一权威）、空亡、冲合刑害穿破检测、做功识别、墓库、神煞、大运流年、应期、身体部位 |
| **Subjective** | 主观层 | 30 | 层功量化、象法九原则、财命官命、婚姻学历牢狱、职业取象、应期推断、岁运反局、方向判断、六亲、子女、迁移、相貌、灾祸、诀法 |
| **Narrative** | 叙事层 | - | 引擎结论 → 郝金阳风格推演（5 模板 Few-shot + 生成后校验器） |

> H-fix 系列（2026-09）新增公共模块：objective `shishen.py`（十神单一权威）/ `_relation_utils.py`（关系对工具）、subjective `utils.py`（`_ensure_*` 公共 helper）——重复逻辑下沉产物，防多份实现漂移；分层单向依赖不变（`scripts/check_layering.py` 守护）。

## 推演流程

1. **八字输入** — 出生年月日时、性别、地点
2. **排盘** — 四柱八字、大运、流年（内嵌 1900-2100 节气表，经天文历 468 组交叉验证）
3. **客观检测** — 做什么功？类型/层次/效率。神煞、墓库、虚实
4. **主观判断** — 富贵层级、财命官命、婚姻职业、应期
5. **叙事输出** — 结构化结论 + 郝金阳风格自然语言推演

## 核心概念

| 概念 | 说明 |
|------|------|
| **做功** | 盲派核心：制用（克制）、化用（杀印相生）、合用（天干合）、墓用（墓库）、生用（食伤泄秀）、复合——六种做功类型 |
| **宾主体用** | 区分"我的"（日柱为体）和"外面的"（年月时为宾）。做功方向决定吉凶：体制宾=吉，宾克体=凶 |
| **象法九原则** | 共象（多象聚焦）、合象（合化生新象）、换象（制尽主从易位）、局象（全局氛围）等九条操作规则 |
| **层功四档** | L1 小富小贵 → L4 极富极贵。段氏定性判断，引擎用加法规则+边界标注实现 |
| **方向判断** | 区分该制与不该制——制忌神=吉，制用神=凶。比劫夺财、反局否决等 |

## 验证

| 验证 | 用例 | 状态 |
|------|------|:--:|
| verify_mangpai（V7 合并版） | 432 | ✅ |
| verify_dayun / verify_layer1 / verify_layer3_checkpoint | 70 / 64 / 20 | ✅ |
| pytest（含属性化测试 + 契约测试 + 错误注入测试 + mock 哨兵） | 1149 passed + 1 xfailed | ✅ |
| blind_eval（heldout 215 + trainset 294 三维盲测） | 快照零翻转（基线 `snapshots/LATEST`） | ✅ |

## 入仓前的脱敏闸门

仓库入库守护脚本三件套：`scripts/check_layering.py`（分层单向）、`scripts/check_typing_imports.py`（typing/import 面）、`scripts/check_credentials.py`（脱敏脱密闸门）。

`check_credentials.py` 在 commit 前自动扫描**暂存区新增行**（存量不干扰）：

- **P0 真凭证**（阻止）：ark-/sk-/GitHub/AWS/Slack token、私钥块、Bearer、邻近 key/secret/token 的高熵串
- **P1 隐私**（阻止）：手机号、身份证、非 example 域名邮箱
- **P2 本机路径**（默认仅警告，`--strict` 可升级为阻止）
- 输出一律打码（前 4 + 后 2），白名单占位符（`your-`/`<REDACTED>`/`sk-fake*` 等）放行

```bash
bash scripts/install_git_hooks.sh   # 安装 pre-commit hook（.git/hooks/ 不入库，克隆后需执行一次）
python3 scripts/check_credentials.py          # 手动扫暂存区（默认 --staged）
python3 scripts/check_credentials.py --all    # 全量审计（存量 P2 路径命中属预期）
```

## 三层审计

| 层 | 内容 | 通过率 |
|:--:|------|:--:|
| 第一层 | 基础数据（纳音/节气/藏干/长生/干支性情）vs 经典原著 | 100% |
| 第二层 | 模块算法 67 例 vs 段建业原著 | 72%✅ 28%⚠️ 0%❌ |
| 第三层 | 端到端 10 例 vs 郝金阳断语 | 47%✅ 75%✅+⚠️ |

## 快速开始

```python
from mangpai.engine import calc_mangpai_full
result = calc_mangpai_full(1992, 10, 9, 13, 58, 'male', 114.09)
print(result['summary'])
```

## 安装

Python 3.10+（3.11.15 / 3.14.4 双版本全量实测通过；3.10 语法面兼容、未单独实测）。

**引擎核心零依赖（纯标准库）**，排盘数据全部内嵌，clone 即可用。其余组件按需安装：

```bash
pip install pyyaml       # 跑 demo / 测试 / 评估工具需要（llm_channel CLI、blind_eval 等读 cases.yaml）
pip install sxtwl        # 可选：交运精确时刻（缺省优雅降级为缺省值，主流程不受影响）
pip install anthropic    # 可选：仅遗留叙事通道 narrative.py 需要（正式通道 llm_channel 不需要）
```

> 说明：README 旧版"纯标准库"表述仅对**引擎核心**成立；LLM demo/测试/评估链路需要 `pyyaml`。

## 配置你自己的 LLM（可选）

LLM 叙事层是**可选组件**：不配置即纯引擎模式，零外发。配置后可指向 **DeepSeek（默认）/ OpenAI / 本地 Ollama / vLLM / 任意 OpenAI 兼容服务**。全部配置为环境变量，模板见 [`.env.example`](.env.example)，总表：

| 变量 | 缺省 | 说明 |
|------|------|------|
| `MANGPAI_LLM_API_KEY` | 无（必填） | API Key（回退链：→ `DEEPSEEK_API_KEY` → env 文件） |
| `MANGPAI_LLM_BASE_URL` | DeepSeek 官方端点 | 任意 OpenAI 兼容端点 |
| `MANGPAI_LLM_MODEL` | `deepseek-flash` | 模型名（回退链：→ `DEEPSEEK_MODEL`） |
| `MANGPAI_LLM_THINKING` | `1` | `0`=请求体剔除 `thinking`/`reasoning_effort` 两字段——**接 OpenAI/Ollama/vLLM 等严格兼容服务时设 0**（否则可能 HTTP 400 unknown field） |
| `MANGPAI_LLM_REASONING_EFFORT` | `low` | 仅 thinking 开启时发出 |
| `MANGPAI_LLM_TIMEOUT` / `MANGPAI_LLM_RETRIES` | `120` / `2` | 本地模型首载慢可调大超时 |
| `MANGPAI_LLM_ENV_FILE` | 项目根 `.env`；可选 | env 文件回退路径（缺省链：项目根 `.env` → `~/.env`） |
| `MANGPAI_USE_LLM` | `1` | `0`=关闭 LLM 叙述，纯引擎直出（旧名 `FEISHU_USE_LLM` 仍兼容） |

最省事的配法：`cp .env.example .env`（放项目根）后按需填写即可——项目根 `.env` 会被自动读取（回退链：`MANGPAI_LLM_ENV_FILE` 指定 → 项目根 `.env` → `~/.env`）。

provider 示例：

```bash
# DeepSeek（默认，无需改端点；峰谷价计价仅对 DeepSeek 有效）
export MANGPAI_LLM_API_KEY=sk-your-key

# OpenAI
export MANGPAI_LLM_BASE_URL=https://api.openai.com/v1/chat/completions
export MANGPAI_LLM_API_KEY=sk-your-key
export MANGPAI_LLM_MODEL=gpt-4o-mini
export MANGPAI_LLM_THINKING=0

# 本地 Ollama（key 任意非空即可；首载慢，超时调大）
export MANGPAI_LLM_BASE_URL=http://localhost:11434/v1/chat/completions
export MANGPAI_LLM_API_KEY=ollama
export MANGPAI_LLM_MODEL=qwen2.5:14b
export MANGPAI_LLM_THINKING=0
export MANGPAI_LLM_TIMEOUT=300

# vLLM / 其他 OpenAI 兼容服务：同上，设 BASE_URL+MODEL+THINKING=0 即可

# 关闭 LLM（纯引擎模式，零外发）
export MANGPAI_USE_LLM=0   # 或干脆不配 API Key
```

其他 provider 的成本显示「未计价」（计价表仅对 DeepSeek 定价有效）。通道细节见 [docs/llm-channel-20260818.md](docs/llm-channel-20260818.md)。

## 完整流程示例（排盘 → 判定 → LLM 叙述）

```python
from mangpai.engine import calc_mangpai_full
from mangpai.subjective.llm_channel import render_structured_reading

# 1) 引擎层：本地确定性计算，零外发
result = calc_mangpai_full(1992, 10, 9, 13, 58, 'male', 114.09)
print(result['summary'])

# 2) LLM 叙事层：按上面配置走你自选的 LLM；未配 key 时自动降级返回 prompt 文本（不抛错）
text = render_structured_reading(result, user_question='此造财运如何？')
print(text)
```

命令行 demo（吃 trainset 内置案例，需 `pip install pyyaml`；案例路径已锚定 `__file__`，**可在任意目录运行**）：

```bash
python3 -m mangpai.subjective.llm_channel b67-李嘉诚 "财运"
```

飞书机器人仅为**可选接入层**（见 [mangpai/feishu/README.md](mangpai/feishu/README.md)），核心流程完全可脱离飞书运行。

## 知识库 & 审计

- `docs/remaining-tasks-20260717.md` — 待修复项清单（含人机交互依赖标注）
- `docs/layer2-9gap-analysis-20260713.md` — 第二层 67 例架构分析
- `docs/layer3-haojin-yang-audit-20260713.md` — 第三层郝金阳案例审计
- `docs/k3-shouke-jiaocheng-audit-20260717.md` — 授课教程逐章审计

## 理论来源

基于段建业盲派方法论，核心理论参照《段氏理象学》《盲派命理研究》《盲派初级/中级/高级命理学》《命理授课教程》及《命理珍宝 50 期》。基础语法层参照《渊海子平》《子平真诠》《滴天髓阐微》等子平经典。

## 依赖

Python 3.10+；**引擎核心纯标准库**，零外部日历依赖，排盘数据全部内嵌。demo/测试/评估工具链需 `pyyaml`，交运精确时刻可选 `sxtwl`——安装命令见上文「安装」节。

## 隐私

本系统按 **privacy-by-design** 构建，三条核心原则：

- **本地优先**：命理推演（排盘/做功/十神/大运流年/应期等）为确定性逻辑运算，**完全在本地完成**，不联网、不落盘、不遥测。
- **默认零外发**：引擎本身零网络行为。唯一可能的外发是**可选的 LLM 叙事层**（将八字/性别/出生地经度提交 LLM API 生成自然语言解读）——该组件可关闭（`MANGPAI_USE_LLM=0`，飞书接入层旧名 `FEISHU_USE_LLM` 仍兼容）、可替换为任意 OpenAI 兼容服务（本地模型 / 私有部署，配置见上文「配置你自己的 LLM」节）、源码完全可审计。
- **无状态**：不建用户档案、不写数据库、不记录使用历史——处理完即弃；生辰数据不用于任何模型训练。

**数据主权归部署者**：本系统为开源/自托管项目，数据始终在使用者自己的控制范围内。仓库本身**不含任何使用者隐私数据**——`tests/` 下的验证用例取自段建业/郝金阳公开出版的著作断例（含原文出处行号），非真实用户数据；凭据一律通过环境变量注入，永不入库。

📄 **完整说明见 [docs/privacy-policy.md](docs/privacy-policy.md)**（数据处理分层、第三方边界、使用者控制权、日志策略、内容免责）。

## 免责

命理分析仅供参考，不构成人生决策依据。引擎输出为确定性推演结果；开启叙事层后的大模型解读可能存在表述偏差，两者性质不同。系统不提供死亡预测、疾病诊断等敏感内容（内置安全过滤）。

## 许可

MIT
