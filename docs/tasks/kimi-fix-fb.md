# Kimi 任务：修批 B · 引擎 P1（神煞 year-ref×3 + calib 传 age）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + R1/R2 审查结果（P1 清单）
2. **读 R1/R5 归档**：神煞 year-only 丢失（zaihoo.py:394-398/584-592 双查合并写成「顶层+day_ref」，day_ref 死代码 year_ref 永不并入 → year-only 劫煞/亡神/灾煞静默丢失；laoyu.py:640-648 就地重算 shensha 不读子键顶层语义 F13 后静默翻转）+ calib_assertions.py:76 不传 age（has_daxian 恒 False 评旧口径）
3. 本批基线 = **修批 A 快照** `snapshots/20260818_fa.json`（M5 链）
4. 汇报 300 字内

## 任务（四项）
1. **zaihuo 双查合并修复**：:394-398/584-592 并入 year_ref（year-only 劫煞/亡神/灾煞静默丢失——实证盘：劫煞在时柱未入 xiong_shen 可翻转 risk 档）
2. **laoyu 就地重算修复**：:640-648 改走 resolve_shensha + 并入 year_ref（顶层语义 F13 后静默翻转）
3. **calib 传 age**：calib_assertions.py:76 传 age 或复用 res['yingqi_subj']（应期 6 断言评旧口径问题）
4. **同型扫描**：还有没有其它「不读子键/不并入 year_ref」的 shensha 消费点（R1/R2 已列 xiangfa _shensha_by_pillar——一并处理或备案）

## 书例哨兵（先红后绿）
- 实证盘（劫煞在时柱 → 修前未入 xiong_shen 红 → 修后入 绿）
- laoyu 书例（shensha 语义）
- calib 应期 6 断言（传 age 后口径一致）

## 红线
- **heldout 财 47✅/官 48✅/职 24✅ 不回退**
- 书锚铁律
- 基线 = fa 快照（M5 链）

## 验证（六件套）
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline snapshots/20260818_fa.json 翻转明细 5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
四项改动/行号 + 同型扫描结果 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细
