# 第四轮审查 U4 · 收官闸报告（2026-08-19）

> 任务书：`docs/tasks/kimi-review4-u4.md`。只审不改（本报告为唯一落盘产出）。
> 综合 U1（P0=0 / P1×2 / P2×6）+ U2（P0=0 / P1×3 / P2×6）+ 全量实测 → go/no-go + 修批 E 规划。

## 1. 六件套实测表（2026-08-19 全量实跑，值落盘）

| 项 | 实测 | 判定 |
|---|---|---|
| verify_mangpai | 432 passed / 0 failed | ✅ |
| verify_dayun | 70 passed / 0 failed | ✅ |
| verify_layer1 | 64 passed / 0 failed | ✅ |
| verify_layer3_checkpoint | 20 passed / 0 failed | ✅ |
| pytest 全量 | **762 passed + 1 xfailed + 19 xpassed**（782 collected，55s） | ✅ 与任务预期 762 一致 |
| blind_eval vs `snapshots/20260819_d6b.json` | heldout/trainset **0 翻转、0 文本抖动**；成绩 heldout 官 72.73/财 68.12/职 46.15、trainset 官 83.48/财 52.21/职 47.06（与 KB §0 逐字一致） | ✅ |
| 双 seed | 默认 vs PYTHONHASHSEED=0 两快照**逐字节一致** | ✅ |
| regression67 | vs baseline67 **无变化** | ✅ |
| regression_famous | vs famous_baseline **无变化** | ✅ |
| calib | REGRESSION 2 条=zhenbao-01 官命/zhenbao-14a 财命（=KB §6.4 常驻存量，D1 起 4→2，无新增）；IMPROVE 5 条悬挂未回填 | ✅ 存量 |

实测中间件：`/tmp/u4_default.json`、`/tmp/u4_seed0.json`（未入库，只审不改）。
注：D6b（zinv 引擎接线）后首轮全量闸——零翻转坐实 D6b/feishu/审查全程引擎判定零改动。

## 2. 漂移清单（全项 + 处置建议）

### KB（knowledge-base.md）
| # | 位置 | 漂移 | 处置 |
|---|---|---|---|
| K1 | §0 验证口径 + §8 六件套注释 | pytest 记 747 collected（727+1xf+19xp，D5 实测）→ **实测 762+1xf+19xp**（D6b +12、feishu +23，精确吻合 727+12+23） | 更新为 762 实测口径 |
| K2 | §0 头部「最后更新」 | 止 D5，缺 D6a/D6b（zinv）与飞书集成两棒 | 补 D6b 棒+feishu 棒摘要 |
| K3 | §1.1 模块地图 | subjective 25 模块缺 **zinv**（现 26）；LLM 三件套（llm_channel/llm_prompt/llm_backend）地图未列（§8 有载）；**mangpai/feishu/ 整包缺失**（6 文件 754 行+test_feishu 23 测）；tests 行「682 测」过期 | 补 zinv/feishu/llm 三件套+测数 |
| K4 | §4 规则层 | zinv 新模块 4 项立法（得子 3 机制/损子 5 机制/借腹/时柱喜用腿）无 §4.x 条目 | 补 §4.13 zinv 条（锚见 U1 §1 回书表） |
| K5 | §9 基线与总账 | 当前基线记 `20260819_d3.json` → 实为 **`20260819_d6b.json`**（D6b 引擎改动，本批实测零翻转确认）；§9 头止 D5 | 基线改 d6b，补 D6b/feishu 总账 |
| K6 | §2.2 M5 快照链 | 链叙述止于 fb（「全 22 份 meta 完整」）→ 实测链 d1→d2→d3→d6b（49 份，抽检 4 份 meta 完整、rubric v8 一致） | 链叙述补 d1-d6b 段 |
| K7 | §10.1 #42 | selectors 38 键 → D6b 已 **39**（verify_dayun:405 断言=39，实测过） | 注 38→39 |
| K8 | §0 成绩表 / §6.4 残留 | 与实测**逐字一致**；calib 常驻 2 条一致 | 无漂移 ✅ |

### 收工记录（remaining-tasks-20260818.md）
| # | 漂移 | 处置 |
|---|---|---|
| S1 | 缺 **D2 入口批**快报（KB §9 有载，收工记录漏） | 补 |
| S2 | 缺 **D5/D6a/D6b** 快报 | 补 |
| S3 | §四「飞书集成 未做」→ **已交付**（bb4decf，754 行+23 测） | 更新为已交付+残留 P1×3 |
| S4 | §一 pytest 701 / 快照链止 fb → 实 762 / d6b | 更新 |
| S5 | D1 hash 引用错误 → 已由 524faa3 修正 | 无漂移 ✅ |

### CHANGELOG（mangpai/CHANGELOG.md）
| # | 漂移 | 处置 |
|---|---|---|
| C1 | 缺 **D1 数据批**条目（gold 修正 5 条+锚 15 处，含验证数字与基线重设） | 补条目 |
| C2 | 缺 **D4 prompt 迭代 5** 条目（llm_prompt 两锚定+S1 复验 9/30→0/30） | 补条目 |
| C3 | 缺 **D5 工具/备案批**条目 | 补条目 |
| C4 | 缺**飞书集成**条目（新包 754 行） | 补条目 |
| — | D2/D3/D6b 在档；D6a 纯设计已由 D6b 条目引用覆盖 | ✅ |

### 快照链 / 模块地图
- 快照链：**连续无断** ✅（d1→d2→d3→d6b，meta 完整；d4/d5 引擎零改动无快照合理；feishu commit 经 `git show --stat` 实证零引擎文件，无快照合理）。d3→d6b 跨档本批实测零翻转。
- 模块地图：见 K3（缺 zinv/feishu）。

## 3. U3 处置

财档 L2 越限 16 例（D4 rescore L2 5.44%，原定迭代 6）：**按既有倾向跳过，记录为已知残留**。不阻塞上线（LLM 通道四指标已达标，越限为财档单维放大，输出附人工复核注）。若重启：谷段 v4-pro，参照 D4 S1 复验成本约 $5。

## 4. go/no-go 矩阵（正式上线服务判定）

| 维度 | 判定 | 依据 | 阻塞项 |
|---|---|---|---|
| 引擎 | **GO** | P0=0（U1/U2/U4）；六件套全绿；762 测全过；快照零翻转零抖动；双 seed 一致；calib 残留=存量备案 | 无 |
| LLM 通道 | **GO** | D4 S1 三线达标（翻转 0/30）；L0/L1/N1/L2 四指标达标；U1 确认 D3 字段零错位零编造 | 无（财档 16 例=已知残留，迭代 6 可选） |
| 飞书包 | **条件 GO** | P0=0（三判据全过）；并发降级 8/8；fuzz 232 例零崩溃 | **P1×3 上线前必修**：①token 服务端作废（99991663/99991661）无刷新重试，缓存期内全断；②bot.py:50 reply 无兜底，发送失败用户零反馈；③README 未警示 Encrypt Key，控制台误配即全断。另 P2-4（VT 未配=零校验）建议列入上线 checklist 强制 |

新增发现：本批无新 P0/P1；漂移清单全为文档级（不阻塞服务，但 KB/收工/CHANGELOG 是下一棒的事实源，建议与 E1 同批清零）。

## 5. 修批 E 规划（分批；执行另批）

| 批 | 内容 | 依赖 | 性质 |
|---|---|---|---|
| **E1 飞书上线必修** | U2 P1-1（`_api` 捕获 99991663/99991661 清缓存重试一次）+ P1-2（reply 包 try 留日志）+ P1-3（README 红线「勿配 Encrypt Key」）+ P2-4（VT 上线强制+hmac.compare_digest）；test_feishu 补 2-3 哨兵 | 无 | **必做**（飞书通道上线闸）；纯 feishu 包内，引擎零触 |
| **E2 文档漂移清零** | 本报告 §2 全项：KB K1-K7、CHANGELOG C1-C4、收工记录 S1-S4（新建 remaining-tasks-20260819 终态） | 无（可与 E1 并行） | **必做**（事实源修复，防下一棒踩旧数） |
| **E3 数据/锚注修正** | U1 P1-2（cj-贫穷命 raw_quote 恢复 chuji:1306）+ P2-1/2/3/6（test_d6b 注释 乾→坤、zinv 锚 14374→14372-3、县长-3 补锚 chuji:3702、刑警区间 3851→3852、calib baseline 5 条 IMPROVE 回填、哨兵脆弱对齐注释） | 含 gold 数据改动，须配六件套复验 | **必做**（U1 两条 P1 之一在此）；低成本 |
| **E4 候选/缓** | U1 P1-1（zinv 穿引动锚-实现错位：改注或补书据，须设计裁定）+ 损子窗「冲」机制增补（F4 次子亡，须双锚）+ U2 P2-1/2/3/5/6（去重外部存储、token 刷新锁、router 静默错解、500 回显、HTTPServer 上限）+ U3 迭代 6（谷段 ~$5） | E4 引擎项须新批任务书+六件套闸 | 可选 |

执行序建议：E1+E2 并行 → E3 → E4 按需。E1/E2/E3 全部落地后飞书通道即达上线状态。
