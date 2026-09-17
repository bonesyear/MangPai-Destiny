# H-fix 工作计划 v2（2026-09-17 修订）

> 来源：v1 计划（`h-fix-workplan-20260825.md`）+ Kimi 检视报告（`~/.claude/projects/-root-metaphysics/memory/kimi-h-fix-plan-review-20260828.md`）
> **状态**：Kimi 配额已恢复（2026-09-17 实测任务跑通）；模型已切 k3（运行时自报 `kimi-code/k3`）
> **问题池**：`docs/tasks/codehygiene-fix-backlog.md`（498 处 → 去重 ~45 核心项）

---

## 〇、动工前实测核查（已复现）

| 核查项 | 结果 | 处置 |
|--------|------|------|
| `import mangpai`（3.11） | ❌ **仍崩**（`guanming.py:39` 缺 `Any`；`engine.py:15` 缺 `Optional`） | H-fix-1 前提成立 |
| 裸 `except Exception:` 计数 | 计划 115 → **实测 103 处**（漂移 ~12） | H-fix-2 动工前**重新计数定边界** |
| 模型版本 | 运行时自报 `kimi-code/k3` | ✅ k3 已生效 |

---

## 一、H-fix 批次表（v2，含检视调整）

### 🔴 阻塞批（先行）

| 批 | 内容 | 调整点 | 验证 |
|----|------|--------|------|
| **H-fix-1** | import/typing 崩溃面：`guanming.py` 补 `Any`、`engine.py` 补 `Optional`、Tuple 类全仓扫 | **+ 轻量抽查并入**：k3 通读 H11 施工图 + 扫 5 关键模块（engine/guanming/zuogong_detect/gongliang/zaihuo） | 多版本 import 冒烟（3.11/3.14 双跑）+ 六件套 |
| **H-fix-2a** | 异常处理策略 - **引擎层**：`_safe_compute` 37 模块改造（施工图）+ engine 回写契约统一（`or {}`/`is not None`/缺键三态）；**+ 入口校验/索引越界 3 项 P0**（`dayun_gz_sequence`/`_advance_gz`/`_cand_hua[0]`）；**+ `JSONDecodeError` 包装**（llm_backend） | **前置两件**：①**错误注入测试框架**（参数化：非法干支/空 actions/越界索引，跑 calib 10 例）②**pre-hfix 盲测基线快照**（零翻转比对的对照锚） | 错误注入全绿 + 盲测 vs pre-hfix 零翻转 |
| **H-fix-2b** | 异常处理策略 - **subjective 层**（67 处） | 同上框架复用 | 同 2a |
| **H-fix-2c** | 异常处理策略 - **诊断/验证脚本**（~20 处） | 同上 | 同 2a |
| **H-fix-3** | 原子写 12 处（`--write-baseline` 等）+ **llm_channel `validate='reject'` 降级缺免责声明**（H4 P1 提级——红线一致性） | **提级项并入** | 写回后校验 + 六件套 |

### 🟡 第二波

| 批 | 内容 | 调整点 |
|----|------|--------|
| **H-fix-4** | 死代码/重复清理：`_check_pair` 四文件下沉（含 **局部 import/循环依赖 ~70 处**）+ 十神十余处统一 + shipaige 死数据 + 8 诊断脚本归档 + `cost_cny` 改名 | **顺序前移**（先于 H-fix-5，减少同文件冲突面）；**局部 import 归此批** |
| **H-fix-6** | selectors 契约（engine-keys 自动契约测试） | **顺序前移**：先于 H-fix-5 的 compute_all 拆分落地（拆分前先有防键漂移哨兵） |
| **H-fix-5** | 大函数拆分（gongliang 957 行 / detect_relations 850 行 / compute_all 490 行——按 H11 方案） | 依赖 H-fix-4（下沉后）+ H-fix-6（契约先立） |

### 🟢 后置

| 批 | 内容 |
|----|------|
| **H-fix-7** | 评测框架统一（_n2/_t3/_v3/_w4/_w5 合并——防口径漂移，可选） |
| **H-fix-8** | 文档/基线同步（README 用例数/MANUAL 4 例/快照 LATEST 指针） |

### ⏸️ 明示"暂不修"（不缺席）

| 项 | 理由 |
|----|------|
| feishu 并发两 P1（后台线程无界 / `_seen_mids` 非原子） | 单聊场景影响低；群聊上线前再修——**显式记录** |
| magic numbers（~45 处 P2） | 可接受后置，明示不修 |

---

## 二、遗漏项处置表（检视发现，8 项）

| # | 遗漏项 | 处置 |
|---|--------|------|
| 1 | 局部 import/循环依赖 ~70 处 | → **H-fix-4** |
| 2 | 入口校验/索引越界 P0（3 项） | → **H-fix-2a** 显式纳入 |
| 3 | engine 回写模式不一致 | → **H-fix-2a** 统一契约 |
| 4 | `cost_usd`→`cost_cny` 改名 | → **H-fix-4**（顺带 H-fix-8 文档） |
| 5 | feishu 并发 P1 | → **明示暂不修**（群聊上线前） |
| 6 | llm_channel 降级缺免责 | → **H-fix-3**（提级） |
| 7 | JSONDecodeError 未包装 | → **H-fix-2a** |
| 8 | magic numbers P2 | → **明示不修** |

---

## 三、风险预案（补全检视指出的 4 项缺口）

1. **前置基线锚**：H-fix-2 动工前先跑 blind_eval 存 `pre-hfix` 快照——"零翻转"才有对照
2. **新崩溃面分诊**：吞改抛暴露真崩溃时，预定义 fix-forward vs 临时白名单（如 `EngineComputeError` 显式降级）判定标准
3. **回滚方案**：每批独立 git 分支 + 批前 tag；**六件套任一红即整批 revert**，不带红前进
4. **计数漂移**：`grep` 计数脚本纳入批 DoD（103 vs 115 已实证需重核）

---

## 四、每批 DoD（完成定义）

- [ ] 哨兵先红后绿（新测试先证明失败）
- [ ] 六件套全绿（verify 全项 + pytest + blind 零翻转 + 67/famous + calib + 双 seed）
- [ ] 计数类核查（若批涉及）
- [ ] 回滚点已打（批前 tag）
- [ ] 文档同步（KB/CHANGELOG/收工记录）
- [ ] 引擎判定零改动确认（compute_all 输出结构不变）

---

## 五、动工顺序（v2 最终）

```
① H-fix-1（import 崩溃面 + 轻量抽查）
② 前置：错误注入框架 + pre-hfix 基线快照
③ H-fix-2a → 2b → 2c（异常策略分三层）
④ H-fix-3（原子写 + 免责提级项）
⑤ H-fix-4（死代码/重复/局部 import）
⑥ H-fix-6（selectors 契约）→ H-fix-5（大函数拆分）
⑦ H-fix-7 / H-fix-8（后置）
```

**每批一发一等通知**（用户节奏），发现先记待修清单。

---

## 六、模型切换说明（K2.7 → k3）

- 六件套 + 盲测硬门禁兜底，**无需专门"旧代码熟悉"批**
- 轻量抽查**零成本并入 H-fix-1**（k3 通读施工图 + 扫 5 关键模块）
- **H-fix-1 本身即 k3 生效验证场**：若一行级 import 修复都出漂移，说明模型/配置仍未切对
