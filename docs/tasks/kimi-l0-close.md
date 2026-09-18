# Kimi 任务：L0 · 遗留项关闭标记批（docs-only）

## ⚠️ 执行指引
1. **先读**：`/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-assessment-20260918.md`（你的评估报告——6 项关闭的裁定与理由）+ `/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-fix-plan-20260918.md`（维修方案——L0 的定位）+ `docs/remaining-tasks-20260917.md`（收工记录）+ `docs/tasks/codehygiene-fix-backlog.md`（相关节）
2. 本批 = **L0（docs-only 关闭标记——零代码改动）**
3. 汇报 300 字内

## 任务：6 项"明示关闭"落档
按评估报告的裁定，将以下 6 项**从"待议"转为"已关闭（附理由）"**：

| # | 项 | 关闭理由（依评估报告） |
|---|-----|----------------------|
| A1 | SHIPAI_DOMAINS/METHODOLOGY | 修批C 明议留档优先（**非待删项**——此前误列为遗留） |
| A2 | gongmen_wuzhi 整模块 | 修批A③/F18 锁定决策 + 三层防护（**非待删项**——此前误列） |
| A4 | jiaoyun `if not span` | 公开 API 边缘语义，非死码 |
| B5 | gongliang 4 处自调吞异常 / 13 书例无命中 | 2b 已实质处置（异常策略批覆盖）/纯备案非问题 |
| B6 | detect_relations 返回含 set | 内部键不进 payload，**过度防御**；实测无泄漏面 |
| C4 | magic numbers ~45 处 | v2 计划 ⏸️ 维持（可接受后置） |

## 落档位置（三处同步）
1. **`docs/remaining-tasks-20260917.md`**：§二「剩余待议项」重构为两节——
   - 「已关闭（附理由）」：上述 6 项
   - 「待办」：L1 项（B1/B2/B3/C1/B4/C2/C3）+ D（上线 checklist）+ B1 时机条件
2. **`docs/tasks/codehygiene-fix-backlog.md`**：相关节加关闭标记（避免以后重复立项）
3. **KB**（若相关条目需同步）

## 同时记录（方案里确认的待办）
- **L1 批**（单批两阶段：甲零输出项 B2/B3/B4/C2/C3 → 乙输出项 B1/C1）+ 时机条件（引擎批前置位 / 或 LLM 批跑有需求时独立先做）
- **行号更正**：`_prepare_inputs` 死块实在 `gongliang.py:431-433`（非 engine.py）——更正 backlog/收工记录中的误记
- **D**：真实凭证冒烟 = 上线 checklist #3 执行项（前置：飞书 APP_ID/SECRET/chat_id）

## 验证（DoD）
- [ ] 三处落档一致（收工记录 / backlog / KB）
- [ ] 6 项关闭理由明确（可直接引用评估报告）
- [ ] **零代码改动**（纯 docs）
- [ ] 六件套不必跑（无代码变动），但**建议快速 `git status` 确认只动 docs**

## 产出
- 三处文档同步
- 汇报 300 字内：关闭项落档位置 + 待办清单更新 + 行号更正

## 红线
- 纯文档（不改任何代码/测试）
- 不调外部 API
