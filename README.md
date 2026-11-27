# MangPai · Chinese Bazi Analysis Engine

基于段建业/郝金阳盲派理论的八字命理推演引擎。59 模块四层架构，2026 验证用例通过，无 strict xfail。

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
| **Narrative** | 叙事层 | 4（已计入 Subjective 30） | 引擎结论 → 郝金阳风格推演（5 模板 Few-shot + 生成后校验器） |

> H-fix 系列（2026-09）新增公共模块：objective `shishen.py`（十神单一权威）/ `_relation_utils.py`（关系对工具）、subjective `utils.py`（`_ensure_*` 公共 helper）——重复逻辑下沉产物，防多份实现漂移；分层单向依赖不变（`scripts/check_layering.py` 守护）。

## 推演流程

1. **八字输入** — 出生年月日时、性别、地点
2. **排盘** — 四柱八字、大运、流年（内嵌 1900-2100 节气表，4824 项与 sxtwl 交叉验证（分钟级））
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
| verify_mangpai（V7 合并版） | 375 passed（375 项） | ✅ |
| verify_dayun / verify_layer1 / verify_layer3_checkpoint | 72 / 68 / 20 | ✅ |
| pytest（含属性化测试 + 契约测试 + 错误注入测试 + mock 哨兵） | 2026 passed + 0 xfailed | ✅ |
| blind_eval（heldout 214 + trainset 295 三维开发评估） | `LATEST=20261125_batch32.json`（rubric v10）；批次32仅制例二/过河拆桥 ❌→✅，零退化、零文本抖动，双 seed 一致 | ✅ 新基线零差异 |
| 真实 LLM 冒烟 | Coding Plan ACP + DeepSeek 单例生产 prompt；七维/Schema/validate_reading 均通过，0违规、0 reject；DeepSeek 45,483 tokens，offpeak 估算 ¥0.0775605 | ✅ 单例通过（全量S1未做） |
| 真实 S1 试点 | 30例冻结样本，14/27有效校验通过；2空内容、1解析失败、4例触发结构化 reject（7条）；总成本 ¥2.1691605 | ⚠️ 试点完成，非全量GO |
| S1问题定向修复 | 2个空内容+1个解析案例真实复测通过；7条地支「丑」误报离线全消，27例通过14→16；新增费用 ¥0.224349 | ✅ 定向修复（非全量重跑） |
| N1/L2误报专项 | 4例明确官命否定不再误报，27例通过16→17；时长N1、额外维度和其他L1保留 | ✅ 定向修复（无新增调用） |
| L1 remap与L0边界 | 同值展开按值去重并优先精确嵌套路径，真实L1清零；总通过仍17（N1仍在），额外维度保留 | ✅ 定向修复（无新增调用） |
| N1年份与时长 | 运岁`gz`白名单消除8条干支误判和3条代词误判，N1从13降至2、总通过17→24；「那五年」时长与额外维度保留 | ✅ 定向修复（无新增调用） |
| L0额外维度 | 非保护生产prompt明禁拼接维度名、占位键和后缀复制键；两例真实复测额外维度2→0，27例定向合并通过24→25；`cj-1209`保留1条独立L2，费用¥0.142332 | ✅ 定向修复（非全量重跑） |
| 单例残余与分段时长 | 官命`为否`误报消除；运干/运支时长仅按对应segments豁免，普通那五年与错误时长仍拦截；27例定向合并25→27，县长复测全过，费用¥0.075213 | ✅ 定向修复（非全量重跑） |
| 30例同样本复跑 | 30/30完成，原始口径14/27→16/29；当前校验器下旧27份25/27、同27 IDs新15通过/11违规/1解析失败；5例schema错误，空内容2→0，费用¥2.15121 | ⚠️ 不扩量，非全量GO |
| 复跑误报专项 | 6条官命判否、3条地支「丑」及3条N1误报消除，复跑29份有效输出16→23；22条L0、2条L1和1例解析失败保留，无新增调用 | ✅ 定向修复（不扩量） |
| schema生成稳定性 | 维度名/附属键/嵌套/单JSON约束；6例真实复测全过，费用¥0.457155；30例定向合并29/30，仅剩2条真实无出处L1 | ✅ 定向修复（非同prompt全量） |
| 县长L1单例 | `shishen={}`且键清单为空，两条`.verdict`属臆造；当前prompt复测全过，费用¥0.0750945；定向合并30/30，无代码改动 | ✅ 单例闭合（非同prompt全量） |
| 当前prompt全30例复跑 | 30/30可解析，21/30通过；L0 22→4、L1 2→0、reject 3→0、解析失败1→0，费用¥2.173278；4例仍自造键，1例运干支/数字错误 | ⚠️ 改善但未稳定，不扩量 |
| 批次47复跑误报 | 补3类官命判否及有据运段表达变体，当前30例21→25；L2 4→0、N1 5→1，4条L0和真实「一岁运」保留，无新增调用 | ✅ 定向修复（不扩量） |
| 自造键与运岁防护 | 最终prompt核对+大运干支回对，五例结构问题均消除；后续误报离线修复，定向合并30/30，费用¥0.702195 | ✅ 定向修复（非同prompt全量） |
| G15书证专项 | 反例A与书例在引擎量上同构；原著txt缺失，制财条件无法证为通则，保持未决，不改代码或金标 | 研究结项（无通用判据） |
| H44书证专项 | 排除day_gan被三个书例证伪；日支主动做功条件仅为待验假设，原著缺失，保持未决，不改代码或金标 | 研究结项（无兼容判据） |
| H96书证专项 | 盘A与ans17的伤官诀均为真，放宽会误翻非官命金标；时支/日支分流仅待验假设，保持未决，不改代码或金标 | 研究结项（无兼容判据） |
| 真实飞书验收 | 用户决定永久结项，不再调用或安排验收；现有离线测试保留 | 已结项 |

## 入仓前的脱敏闸门

仓库常驻闸门六件套：分层单向（`scripts/check_layering.py`）、typing/import 面（`scripts/check_typing_imports.py`）、键契约（`mangpai/tests/test_key_contract.py`）、防假-green（`mangpai/tests/test_verify_integrity.py`）、脱敏脱密（`scripts/check_credentials.py`）、**文档数字**（`scripts/check_doc_numbers.py`，2026-09-19 入库）。`test_repo_gates.py` 与提交钩子执行分层/typing/死链检查；CI 在 Python 3.10/3.11/3.14 矩阵运行完整 pytest 和静态闸门。

文档数字闸门校验本 README 与 `docs/knowledge-base.md` 权威声明位（首行/验证表/架构表/验证口径行/§8 工具表）的模块数与 pytest 数字是否等于实测（`pytest --collect-only` ~0.5s + 分层口径计数，不真跑全量、不跑 verify），漂移即退出码 1。**不算 pre-commit 默认项**——改了测试数量（新增/删除用例）或模块数后手动跑一次即可：

```bash
python3 scripts/check_doc_numbers.py          # 全量报告；--quiet 只报不一致；退出码 0=全一致
python3 scripts/check_doc_numbers.py --github  # 追加核对 GitHub 仓库 description 数字声明（联网 opt-in）
```

`--github` 为 **opt-in 联网项**（默认关闭，不带它时行为与纯离线版完全一致）：拉取仓库 GitHub `description` 里的 `N modules` / `N test cases` 声明与实测比对。**需自备网络**；public 仓库匿名即可读，`GITHUB_TOKEN` 可选（有 token 提高限速），`MANGPAI_GITHUB_REPO` 可换目标仓库。网络失败 / 非 200 / 提取不到数字同样退 1 并报明原因——显式开启却无法完成校验绝不报绿。

`check_credentials.py` 在 commit 前自动扫描**暂存区新增行**（存量不干扰）：

- **P0 真凭证**（阻止）：ark-/sk-/GitHub/AWS/Slack token、私钥块、Bearer、邻近 key/secret/token 的高熵串
- **P1 隐私**（阻止）：手机号、身份证、非 example 域名邮箱
- **P1 出生信息**（首批仅警告）：按日期、时刻、性别、地点组合检测同行/相邻行；标注 `synthetic` 或「虚构示例」的合成值豁免
- **P2 本机路径**（默认仅警告，`--strict` 可升级为阻止）
- 输出一律打码（前 4 + 后 2），白名单占位符（`your-`/`<REDACTED>`/`sk-fake*` 等）放行

```bash
bash scripts/install_git_hooks.sh   # 安装 pre-commit / pre-merge-commit / pre-push（不入库，克隆后需执行）
MANGPAI_PYTHON=python bash scripts/install_git_hooks.sh  # Windows 无 python3 时可显式指定
python3 scripts/check_credentials.py          # 手动扫暂存区（默认 --staged）
python3 scripts/check_credentials.py --all    # 全量审计（存量出生信息告警/P2 路径命中属预期）
```

本地钩子覆盖提交、自动合并和推送；`.github/workflows/credentials.yml` 对 PR/push 再跑全量扫描。已有非本脚本钩子不会被覆盖，可用 `MANGPAI_PYTHON` 指定 Python 3.10+。

## 三层审计

| 层 | 内容 | 通过率 |
|:--:|------|:--:|
| 第一层 | 基础数据（纳音/节气/藏干/长生/干支性情）vs 经典原著 | 100% |
| 第二层 | 模块算法 68 项 vs 段建业原著 | 67✅ 1⚠️ 0❌（现行基线） |
| 第三层 | 端到端 10 例 vs 郝金阳断语（45 项） | 35✅ 10⚠️ 0❌（77.78%✅，100%✅+⚠️） |

## 快速开始

```python
from mangpai.engine import calc_mangpai_full
result = calc_mangpai_full(2000, 1, 1, 12, 0, 'male', 116.41)  # synthetic
print(result['summary'])
```

时间输入默认是 UTC+8 标准时。中国大陆 1986–1991 年历史夏令时出生的钟表时间须显式传 `is_dst=True`，引擎减一小时后再排盘和起运；切换日不存在或不在夏令时区间的输入会报错。其他地区/年份不自动推断。

## 安装

Python 3.10+（3.11.15 / 3.14.4 双版本全量实测通过；3.10 语法面兼容、未单独实测）。Windows 实测通过（3.14.7）；Windows 控制台中文输出乱码属 GBK 终端问题，命令行用法前设 `PYTHONIOENCODING=utf-8` 即可（引擎本身不受影响）。

```bash
git clone https://github.com/bonesyear/MangPai-Destiny.git
cd MangPai-Destiny  # 后续模块命令默认在仓库根运行；其他目录需先设 PYTHONPATH=<仓库根>
```

**引擎核心零依赖（纯标准库）**，排盘数据全部内嵌，clone 即可用。其余组件按需安装：

```bash
pip install pyyaml       # 跑 demo / 测试 / 评估工具需要（llm_channel CLI、blind_eval 等读 cases.yaml）
pip install sxtwl        # 可选：交运精确时刻（缺省优雅降级为缺省值，主流程不受影响）
pip install anthropic    # 可选：仅遗留叙事通道 narrative.py 需要（正式通道 llm_channel 不需要）
```

> 说明：README 旧版"纯标准库"表述仅对**引擎核心**成立；LLM demo/测试/评估链路需要 `pyyaml`。

## 配置你自己的 LLM（可选）

LLM 叙事层是**可选组件**：默认关闭，零外发；须显式设置 `MANGPAI_USE_LLM=1` 并配置有效 key。开启后可指向 **DeepSeek（默认）/ OpenAI / 本地 Ollama / vLLM / 任意 OpenAI 兼容服务**。配置可由环境变量或 env 文件提供，模板见 [`.env.example`](.env.example)，总表：

| 变量 | 缺省 | 说明 |
|------|------|------|
| `MANGPAI_LLM_API_KEY` | 无（启用时必填） | API Key；仅官方默认端点可回退 `DEEPSEEK_API_KEY`，自定义端点必须显式设置新名 |
| `MANGPAI_LLM_BASE_URL` | DeepSeek 官方端点 | 任意 OpenAI 兼容端点 |
| `MANGPAI_LLM_MODEL` | `deepseek-flash` | 模型名（回退链：→ `DEEPSEEK_MODEL`） |
| `MANGPAI_LLM_THINKING` | `1` | `0`=请求体剔除 `thinking`/`reasoning_effort` 两字段——**接 OpenAI/Ollama/vLLM 等严格兼容服务时设 0**（否则可能 HTTP 400 unknown field） |
| `MANGPAI_LLM_REASONING_EFFORT` | `low` | 仅 thinking 开启时发出 |
| `MANGPAI_LLM_TIMEOUT` / `MANGPAI_LLM_RETRIES` | `120` / `2` | 单次超时秒数（0<t≤600）/重试次数（0..5）；非法值回退缺省。总预算约束重试/退避，不能中断任意滴流式响应 |
| `MANGPAI_LLM_MAX_TOKENS` / `MANGPAI_LLM_CONTEXT` | `8192` / 不预检 | 输出上限 / 模型上下文窗口；设置后者后按字符保守估算，不足则不外发 |
| `MANGPAI_LLM_ENV_FILE` | 项目根 `.env`；可选 | env 文件路径；缺省只读项目根 `.env`，不读取 `~/.env` |
| `MANGPAI_USE_LLM` | `0` | `1/true/on/yes`=显式开启；其余或缺省=纯引擎零外发（旧名 `FEISHU_USE_LLM` 仍兼容） |

最省事的配法：`cp .env.example .env`（放项目根）后按需填写即可——项目根 `.env` 会被自动读取（`MANGPAI_LLM_ENV_FILE` 指定时只读该文件）。复制模板本身不会开启外发。

provider 示例：

```bash
# 以下示例都须显式开启；未开启时不发请求
export MANGPAI_USE_LLM=1

# DeepSeek（默认，无需改端点；峰谷价计价仅对 DeepSeek 有效）
export MANGPAI_LLM_API_KEY=sk-your-key

# OpenAI
export MANGPAI_LLM_BASE_URL=https://api.openai.com/v1/chat/completions
export MANGPAI_LLM_API_KEY=sk-your-key
export MANGPAI_LLM_MODEL=gpt-4o-mini
export MANGPAI_LLM_THINKING=0

# 本地 Ollama（key 任意非空即可；首载慢，超时调大）
# 服务端须用 OLLAMA_CONTEXT_LENGTH=65536 启动，或 Modelfile: PARAMETER num_ctx 65536
export MANGPAI_LLM_BASE_URL=http://localhost:11434/v1/chat/completions
export MANGPAI_LLM_API_KEY=ollama
export MANGPAI_LLM_MODEL=qwen2.5:14b
export MANGPAI_LLM_THINKING=0
export MANGPAI_LLM_TIMEOUT=300
export MANGPAI_LLM_CONTEXT=65536

# vLLM：同上并单独设 MANGPAI_LLM_API_KEY；服务端加 --max-model-len 65536
# 本地、私网 IP 和 .local 端点自动绕过环境代理，不继承 DEEPSEEK_API_KEY

# 关闭 LLM（纯引擎模式，零外发）
export MANGPAI_USE_LLM=0   # 或干脆不配 API Key
```

其他 provider 的成本显示「未计价」（计价表仅对 DeepSeek 定价有效）。通道细节见 [docs/llm-channel-20260818.md](docs/llm-channel-20260818.md)。

## 完整流程示例（排盘 → 判定 → LLM 叙述）

```python
from mangpai.engine import calc_mangpai_full
from mangpai.subjective.llm_channel import render_structured_reading

# 1) 引擎层：本地确定性计算，零外发
result = calc_mangpai_full(2000, 1, 1, 12, 0, 'male', 116.41)  # synthetic
print(result['summary'])

# 2) LLM 叙事层：须按上面显式开启并配置；未开启或未配有效 key 时降级返回 prompt 文本
text = render_structured_reading(result, user_question='此造财运如何？')
print(text)
```

命令行 demo（吃 trainset 内置案例，需 `pip install pyyaml`；需在仓库根目录运行，或先设置 `PYTHONPATH=<仓库根>`）：

```bash
python3 -m mangpai.subjective.llm_channel b67-李嘉诚 "财运"
```

飞书机器人仅为**可选接入层**（见 [mangpai/feishu/README.md](mangpai/feishu/README.md)），核心流程完全可脱离飞书运行。

## 知识库 & 审计

- [知识库](docs/knowledge-base.md) — 模块、规则与验证口径
- [原著对照审计](docs/audit-vs-originals-20261017.md) — 当前规则、历史差异与 R0–R10 修整记录
- `docs/layer3-haojin-yang-audit-20260713.md` — 第三层郝金阳案例审计

## 理论来源

基于段建业盲派方法论，核心理论参照《段氏理象学》《盲派命理研究》《盲派初级/中级/高级命理学》《命理授课教程》及《命理珍宝 50 期》。基础语法层参照《渊海子平》《子平真诠》《滴天髓阐微》等子平经典。

## 依赖

Python 3.10+；**引擎核心纯标准库**，零外部日历依赖，排盘数据全部内嵌。demo/测试/评估工具链需 `pyyaml`，交运精确时刻可选 `sxtwl`——安装命令见上文「安装」节。

## 隐私

本系统按 **privacy-by-design** 构建，三条核心原则：

- **本地优先**：命理推演（排盘/做功/十神/大运流年/应期等）为确定性逻辑运算，**完全在本地完成**，不联网、不落盘、不遥测。
- **默认零外发**：引擎本身零网络行为。唯一可能的外发是**可选的 LLM 叙事层**（提交引擎特征 JSON、性别、流年公历年份、大运起运岁/分看位次及用户提问原文；出生地经度仅本地排盘，不进入 payload）——该组件可关闭（`MANGPAI_USE_LLM=0`，飞书接入层旧名 `FEISHU_USE_LLM` 仍兼容）、可替换为任意 OpenAI 兼容服务（本地模型 / 私有部署，配置见上文「配置你自己的 LLM」节）、源码完全可审计。请勿在提问中填写姓名、证件号等身份信息。
- **无状态**：不建用户档案、不写数据库、不记录使用历史——处理完即弃；生辰数据不用于任何模型训练。

**数据主权归部署者**：本系统为开源/自托管项目，数据始终在使用者自己的控制范围内。仓库本身**不含任何使用者隐私数据**——`tests/` 下的验证用例取自段建业/郝金阳公开出版的著作断例（含原文出处行号），非真实用户数据；凭据一律通过环境变量注入，永不入库。

📄 **完整说明见 [docs/privacy-policy.md](docs/privacy-policy.md)**（数据处理分层、第三方边界、使用者控制权、日志策略、内容免责）。

## 免责

命理分析仅供参考，不构成人生决策依据。引擎输出为确定性推演结果；开启叙事层后的大模型解读可能存在表述偏差，两者性质不同。系统不提供死亡预测、疾病诊断等敏感内容（内置安全过滤）。

## 许可

项目代码采用 [MIT](LICENSE)。公开出版物的案例断语、出处与第三方资料不属于本项目 MIT 授权范围；相关权利归原作者/权利人，当前树只保留评估所需断语、出处与去标识数据。
