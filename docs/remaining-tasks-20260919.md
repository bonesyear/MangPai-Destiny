# 收工记录 · 2026-09-19（审查修复批 · LLM 通道去私有路径 B 方案 · 凭证安全整改 · 规则固化）

> 系统处发布态。本周期无开放待办；唯一未闭环的安全项随用户确认「key 早失效」而**风险归零**。

## 一、本会话落地终态（按时间序）

| # | 批 | commit | 内容 | 引擎 |
|---|----|--------|------|------|
| 1 | **审查修复批·P2** | `2393c87` | 主会话代码审查发现的 P2：output 8 处 cwd 相对路径→`ROOT` 锚定、KB book-index 路径与 pytest 计数校准、privacy-policy 路径前缀、output/README 白名单精确化（顶层 vs 子目录陷阱） | 零改动 |
| 2 | **LLM 通道去私有路径（B 方案）** | `4a3b785` | 删 `llm_backend._ENV_FILE='/root/.hermes/.env'` → `_PROJECT_ENV_FILE`（项目根 `.env`）；回退链 = `MANGPAI_LLM_ENV_FILE` → 项目根 `.env` → `~/.env`；报错文本中性化；`.gitignore` 补 `.env.local`/`.env.*.local`；README/`.env.example` 指引同步 | 零改动 |
| 3 | 快照链总账补登 | `a2a8457` | `20260918_r1fix.json` 登记（审查修复批·P2，零翻转非基线） | — |
| 4 | narrative 遗留通道分析 | `90b4b99` | Kimi 独立分析 A/B/C 三选 → **推荐 A（保留，零改动）**；理由：S1 批已裁定（backlog + 哨兵锁定）+ B 收益观感而代价是真实对外契约静默变化 + C 与单通道收敛逆行 | — |
| 5 | **凭证安全整改（两批）** | `7e8811f` + `3d76d0c` | `docs/cc-volcengine-config-backup.md`（真实火山 ARK key，**自初始提交 `878f3ce` 起在公开仓库 2 个月**）删除 + 全仓凭证复扫 + 报告打码；随后补齐残留的 key 前缀打码 | 零改动 |
| 6 | **脱敏脱密自动闸门** | `589b0f4` | 新建 `scripts/check_credentials.py`（P0 凭证/P1 隐私→阻止，P2 本机路径→警告；默认扫暂存区**新增行**，`--all` 全量审计；输出打码+内置断言）+ `install_git_hooks.sh`（pre-commit 已装，**实测拦假凭证**）+ 哨兵 20 测 + `calib_zhenbao.py` 硬编码路径修复（代码文件本机路径**清零**）+ README 小节 | 零改动 |
| 7 | **Hermes 环境维护** | —（本机配置，不入库） | `hermes doctor` 全绿后处理 2 项：**config v44→v45 迁移**（diff 仅版本号一行，5 gateway 无影响）+ **GITHUB_TOKEN 入 profile `.env`**（Skills Hub 转认证模式） | 零改动 |
| 8 | 收工记录补记 | `c13ac20` | `_kang_*` 保留本地勿删 / 存量路径保留 | — |
| 9 | **文档数字闸门** | `257b717` | 新建 `scripts/check_doc_numbers.py`（校验 10 处**权威声明位**：README 首行/验证表/架构表 + KB §1/§8；实测自算 `--collect-only` ~0.5s；历史口径「旧记…作废」前置窗跳过不误报；全一致退 0、任一漂移退 1）+ 哨兵 9 测 + 常驻闸门升**六件套** + README/KB 数字同步 1158/1159 | 零改动 |
| 10 | **README/KB 数字对齐核查** | `0e3f1f7` | 用户问「README 是否检查过/版本号对齐」→ 实测发现用例数**第三次漂移**（1129→1149）；模块数 59 复核无误（foundation 2 在仓库根 + objective 27 + subjective 30 顶层）；项目无 `__version__`（无数值版本号） | 零改动 |

### 关键实证（本轮最有价值的三条）

1. **双环境兼顾已达成**（判事基准「任何人自由选 LLM + 不影响本机」）：
   - 读取优先级 = 环境变量 → env 文件（`MANGPAI_LLM_ENV_FILE` → 项目根 `.env` → `~/.env`），**本机设置永远优先于仓库默认值**
   - 本机 key 的真实来源 = **Hermes `env_loader`（dotenv）注入 os.environ** → 子进程继承（实测：把 `_ENV_FILE` 指向不存在路径后**真实 API 调用照常成功**）
   - ⚠️ **探针教训**：`/proc/<pid>/environ` 只反映 execve 时刻环境，看不到运行时 dotenv 注入 → 曾据此误判「兜底正在承重」；正确探针 = 查自己进程 `os.environ` + monkeypatch 后跑真实调用
2. **对外使用者真缺口已修**：README 指向仓库根 `.env.example`，旧链只读 `~/.env` → `cp .env.example .env`（常人做法）读不到；现项目根 `.env` 在链内
3. **凭证泄漏的完整暴露面**：main 最新版已清；但仍存在于 **git 历史（247 提交）+ 27 个 tag + 2 个 fork**（`pyqq4bs4xy-sys` / `kekewolf`）——**用户确认该 key 早已失效 → 风险归零**，故**不做历史重写**（代价：247 SHA 全变 + 27 tag 重建 + 59 份快照 `_meta.git_sha` 溯源断 + fork 无论如何清不掉）

## 二、闸门（收工实测，2026-09-19）

```
pytest 1158 passed + 1 xfailed ✅          ← 文档数字闸门批 +9 测
verify  432 / 70 / 64 / 20 全绿 ✅
分层检查 66 文件无反向依赖 ✅   typing/import 183 文件 0 处 ✅
常驻闸门 **6 件套**：分层 / typing / 键契约 / 防假-green / 脱敏 / **文档数字（新增）** ✅
双版本 import 冒烟：3.14.4 / 3.11.15 ✅
LATEST = 20260918_t1.json（有效）✅
git 工作区干净 · 本地 = 远程 = 257b717 ✅
凭证终扫 + `check_credentials --all`：P0=0 / P1=0 ✅（P2=287 存量仅警告）
blind 独立复跑：零翻转（逐字段核对 True）✅
`check_doc_numbers`：全一致退 0；**篡改 README 数字实测退 1 并精确报差异** ✅
Hermes doctor：配置 v45 / Skills Hub 认证 / 5 gateway 健康 / 日志无 ERROR ✅
```

## 三、新固化的规则（技能 `mangpai-workflow` + 记忆）

| 位置 | 规则 |
|------|------|
| **§7b** | **所有 code 工作交 Kimi**——Hermes 只做规划/派发/验收/push/文档；发现代码问题写进任务书，不自己动手。依据：`parents[2]` 路径层级错、output 批量替换留语法错误（均自测未发现） |
| **§14b** | 双环境兼顾三层分离（读取优先级/零写入/测试零外发/凭证防线）+ 「新增任何外部服务集成一律走同一模式」硬约定 |
| **§14c** | 凭证泄漏处置流程：扫描（含未跟踪+output/）→ 判暴露区间 → **优先级 轮换 > 删除 > 历史重写** → 打码三规则（任务书不得复述原文 / 打码字符类别假设格式 / **输出前断言敏感模式命中数=0**） |
| 记忆 | 「code 工作一律交 Kimi」+ 仓库卫生约定补凭证事件 |

## 四、剩余事项（收工时点）

| 项 | 状态 |
|----|------|
| **火山 ARK key** | ✅ **风险归零**（用户确认早已失效）；仓库历史/27 tag/2 fork 里的失效 key 保留不动（用户决策：不清历史） |
| narrative 遗留通道 | ✅ **维持 A**；触发条件：散文通道回生产 → 做 C（须前置补校验/红线/免责）；政策要求零厂商字样或 anthropic 供应链事故 → 做 B |
| 引擎层残留 ❌ | 55 例全例有终判（收档带理由），零悬置 |
| 长期方向（用户规划） | **web 页面入口**（替代 CLI 方案）· webhook 独立部署 · 跨流派扩展 —— 均暂缓 |
| 上线 checklist | 7/7 闭环（群聊 #4 与冒烟 #3 均随用户决策关闭） |
| `output/_kang_*`（康老师案例本地数据 3 文件） | ✅ **保留本地**（用户决策 2026-09-19：「不用清…没传仓库就行了」）——**勿删**，随时可复看康老师盘；已确认从未入库（当前树 + 全历史 `--diff-filter=A` 均零命中） |
| 文档存量本机路径（P2=287 处） | ✅ 保留（历史事实记录；闸门只对新增生效，`--strict` 可升级） |

## 五、下一棒接续指引

- **基线**：`snapshots/LATEST` → `20260918_t1.json`；本会话所有改动**引擎零触**，heldout 三维（官 48✅/财 47✅/职 24✅）与 trainset（官 102✅/财 63✅/职 41✅）未动
- **闸门六件套**：pytest **1158**+1xf / verify 432+70+64+20 / blind 零翻转 / 双 seed / **常驻 6 件套（分层·typing·键契约·防假-green·脱敏·文档数字）** / 双版本 import
- **文档数字闸门（新增）**：`python3 scripts/check_doc_numbers.py`——**改了测试数/模块数后跑一次**（校验 README 首行/验证表/架构表 + KB §1/§8 共 10 处），不一致退 1；此前该数字**漂移过三次**（794→1066→1129→1149），故机制化
- **脱敏闸门（重要，新增）**：`.git/hooks/pre-commit` 已装（**不入库**）——换机器/clone 后须跑一次 `scripts/install_git_hooks.sh`；全量审计 = `python3 scripts/check_credentials.py --all`；P2 本机路径存量仅警告（`--strict` 可升级为阻止）
- **Hermes 侧**：config 已 v45；`GITHUB_TOKEN` 已入 profile `.env`（Skills Hub 认证模式）；本机配置回滚锚 = `config.yaml.bak-20260919-083851`
- **纪律**：code 工作交 Kimi（§7b）；一批一发等通知；验收不采信自报（自己 `git grep` / 自己跑闸门）；push 走 gh-proxy + **`git fetch` 后查 `FETCH_HEAD`** 验证远程真实状态
- **凭证纪律**：新增文件前扫明文；报告/任务书一律用位置描述而非字符复述
