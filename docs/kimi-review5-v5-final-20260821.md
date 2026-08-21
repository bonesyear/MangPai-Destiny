# 第五轮审查 V5 · 卫生抽查 + 六件套全量复跑 + 发布 go/no-go（收官批，2026-08-21）

> 只审不改（代码零改动；本报告 + 待修清单排期升级为产出）。全程本地零 API。
> 运行环境 = 项目口径 `/usr/bin/python3`（3.14.4）；shell `python3`=venv 3.11（V2 P1-1 实锤机，本批不用）。

## 0. 一句话结论

**六件套全量复跑全绿、零翻转零抖动、双 seed 一致、快照链完整；卫生抽查确认全部已知项仍在原位、新漂移 1 条（V1-V4 未入 KB/CHANGELOG/收工）；发布判定 = NO-GO——P0 免责声明 + 5 项 P1 未清，修批 F1+F2 落地后转 GO。**

## 1. 六件套实测表（全量，非增量）

| 件 | 实测 | 预期 | 判定 |
|----|------|------|------|
| verify_mangpai | 432 passed / 0 failed | 432 | ✅ |
| verify_dayun | 70 / 0 | 70 | ✅ |
| verify_layer1 | 64 / 0 | 64 | ✅ |
| verify_layer3 | 20 / 0 | 20 | ✅ |
| pytest 全量 | **794 passed + 1 xfailed + 19 xpassed**（65s） | 814 collected 同口径 | ✅ |
| blind_eval vs `snapshots/20260820_gap2.json` | heldout **0 翻转 0 抖动**（官 48✅/财 47✅/职 24✅ 闸门保）；trainset **0 翻转 0 抖动**（官 96✅/财 59✅/职 40✅）；M3 全噪声带内 | 零翻转含 trainset | ✅ |
| regression67 / famous | 均「无变化」 | 0 回归 | ✅ |
| calib（calib_assertions vs YAML 基线） | REGRESSION 仅 zhenbao-01 官命 + zhenbao-14a 财命 = 常驻 2 条存量，零新增；TOTAL ✅30/⚠️10/❌6（n=46） | 常驻 2 条 | ✅ |
| 双 seed | `PYTHONHASHSEED=0` 与默认 seed 输出 cases 部分逐字节一致（仅 _meta.note 异）；git_sha 均 86e0dd3 | 逐字节一致 | ✅ |
| 快照链 | d1→d2→d3→d6b→e3→gap1→gap2 七件齐全；rubric 全 v8-20260808；_meta.git_sha 链式吻合（V6 已验，本批复核一致）；V3/V4 审查批引擎零改动无快照 = 合理 | 连续 | ✅ |

复跑快照落 `/tmp/v5_blind.json`、`/tmp/v5_seed0.json`（审查批不污染 snapshots/ 链）。

## 2. 卫生漂移清单

### 2.1 已知项复确认（全部仍在原位 = 待修清单有效，无自愈无恶化）

| 项 | 复确认 |
|----|--------|
| V6 P2-2/V2 P1-1 `zuogong_detect.py:997` Tuple 未导入 | ✅ 仍在（:13 仅导 Dict/List/Optional/Set）；**全仓扫描 Tuple 用法，缺导入仅此一处** |
| V6 P2-1 `subjective/__init__.py:4` docstring 「40 个 selector」 | ✅ 仍陈旧（实 41，漏 xiangmao） |
| V6 P2-3 bot 非 dict body | ✅ 仍在（bot.py:67 `'encrypt' in body` 无 isinstance guard） |
| V6 P2-4 client.send 生产零调用 | ✅ 仍在（仅 test_feishu.py 3 处） |
| V1 P2-1 zhongji:4179 行号偏 1 | ✅ qianyi.py 5 处（:12/:20/:35/:177/:183）未改 |
| V1 P2-2 「结构同构」措辞 | ✅ qianyi.py:20-21 仍在 |
| V1 P1-1 xiangmao 丁眼锚注 | ✅ xiangmao.py:154 仍无锚（:149 丙癸有锚、丁独缺） |
| V2 P1-2 lark_md 三符 | ✅ formatter.py:49 `- `、:50 `> `、service.py:74 `---` 全在 |
| V2 P2-2 @bot `<at>` 前缀 | ✅ bot.py:84 原文直取无 strip |
| V4 P0-1 免责声明 | ✅ 全仓 grep「仅供参考/免责声明/不构成…依据」= **0 命中**，两路径仍全缺 |
| V4 P1-2 外发告知 | ✅ router.py HELP 无第三方/大模型/DeepSeek 字样 |
| V4 P2-1 max_tokens=4096 | ✅ llm_backend.py:93 仍 4096 |
| V4 P2-4 _self_check 美元口径 | ✅ llm_backend.py:170 仍 0.44/1.32（b190c8f 改了 _PRICE 未改自检） |

### 2.2 新漂移（V5 本批新发）

- **D-V5-1（文档）**：V1-V4 四份审查报告已 commit 入 `docs/`，但 KB / CHANGELOG / 收工记录零第五轮条目（KB 止于 08-20 缺口批3；CHANGELOG 末条同）——五轮审查结论未入档，记入待修清单随修批 F2 清零。
- **D-V5-2（清单漏项）**：V2 P2-1（S7 裸 `str(e)` 回显，bot.py:54）与 V2 P2-3（compute 后台线程无上限）未入既有待修清单——本批补录。
- 无代码/行为层新漂移：KB §9 口径（794+1xf+19xp / 41 selectors / 快照链 / 常驻 2 条）与实测逐条吻合。

## 3. 发布 go/no-go（五轮完整汇总）

| 级 | 项 | 来源 | 判定 |
|----|----|------|------|
| **P0** | 免责声明两路径全缺 | V4 | **发布阻塞，未修** |
| **P1** | Tuple ≤3.13 环境 import 即崩 | V2/V3/V6 三源实锤 | 必清 |
| **P1** | lark_md 三符字面残留 | V2 | 必清 |
| **P1** | xiangmao 丁眼锚注缺 | V1 | 必清 |
| **P1** | mark 模式死亡词仍展示仅附注 | V4 | 必清 |
| **P1** | 出生信息外发 DeepSeek 无告知 | V4 | 必清 |
| P2 | 14 项（见待修清单排期 F2/F3/备案） | V1/V2/V3/V4/V6 | 清单化 |

**判定：NO-GO。** 修批 F1（P0+P1 代码六项）+ F2（锚注+文档入档）落地并复跑六件套全绿后转 GO；P2 不阻塞发布。

## 4. 统一修批规划（待修清单已升级：`docs/tasks/review5-fix-backlog.md`）

- **F1 发布闸修批（代码）**：免责语三处 / Tuple 一行 / formatter 去三符 / 死亡词 mark→reject / 外发告知。小 diff，一次六件套。
- **F2 文档清零批（零行为）**：丁眼锚注 / 4179→4180 / 同构措辞 / docstring 41 / KB+CHANGELOG+收工五轮入档。
- **F3 健壮性批（P2，可与 F1 并）**：bot isinstance + S7 裸 repr 统一 / max_tokens 8192 / _self_check 人民币口径 / L2 拒答误报窗。
- **备案不修**：client.send / 断网双发 / 非文本忽略 / compute 线程上限 / judge prompt 同步（下轮评审前）/ @bot 前缀（真实群验证后）/ unemployed 桶锚定（下轮 prompt 迭代 + S1 复测）。
