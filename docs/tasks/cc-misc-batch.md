# K3 任务：杂项清理批（知识库提炼 + M3 CI + 收尾）

## ⚠️ 执行指引
1. 背景：294 例三维攻坚已收官（财 52.21/官 83.48/职 50.59，trainset）。本批是工程收尾 + 知识固化。
2. **先改代码，后统一验证**；汇报 300 字内
3. 铁律：留出集只评估不反推

## 任务 1：知识库提炼（最重要——为切换 Kimi CLI 做准备）
- 把你 `~/.claude/projects/-root-metaphysics/memory/` 下 24+ 个分析归档的关键结论提炼成 **`docs/knowledge-base.md`**：
  - **书锚清单**：各批次用到的核心书锚（段氏著作章节/原文），按模块分类（做功/体用/财命/官命/职业/神煞/从格/墓库等）
  - **已修簇与规则**：已固化的规则要点（每个模块的判定逻辑一句话）
  - **备案清单**：C 类备案（结构性盲区：军警墓库/中医 3/lawyer 盲区等）+ 已知存量（罗斯切尔德已修、zhenbao-01 官命等）
  - **铁律与测量纪律**：留出集只评估、heldout 闸门、双 seed 确定性、rubric 版本历史
- 目标：这份文件成为未来任何 CLI（含 Kimi code）跑任务时的**上下文替代品**——新会话读它即可获得全部历史知识
- 格式：结构化 markdown，长度不限但信息密度高（这是知识库不是流水账）

## 任务 2：M3 Wilson CI 报告（P3 测量卫生最后一项）
- blind_eval 汇总行输出 **Wilson 95% CI**（acc ± half，公式 scipy.stats 或手工实现）
- `--diff` 仅当 |Δacc| > 两 CI 半宽之和 才判显著改善/退化，其余记「噪声带内」
- 验收门槛以 CI 下界计（如「财命 CI 下界 ≥ X%」）
- ⚠️ 只增不改现有输出格式（像 M2 分组表一样附加）

## 任务 3：收尾决策
- `mangpai/tests/heldout/_p2_diag.py`：留删决策（诊断脚本是否还有用——若已无引用价值则删除，保留有价值的改名为正式工具）
- gongshen 年时身段颠倒备案：确认现状（修 or 永久备案，给结论）
- 快照管理：确认 snapshots/ 各基线文件的 meta 完整性

## 红线
- **引擎规则零改动**（本批纯文档 + 测量脚本附加）
- verify 432/pytest 473 全绿
- heldout 零翻转（blind_eval 现有输出不变，CI 是附加列）

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py` — 数字与 20260814_c 一致 + CI 列正常输出
4. 知识库 `docs/knowledge-base.md` 已生成（报告里给章节概览）

## 汇报（300 字内）
knowledge-base.md 章节概览 + M3 CI 实现说明 + 收尾决策（_p2_diag/gongshen）+ 验证数字
