# Kimi 任务：通盘审查 R0 · 基线链核验

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（审查计划 R0 定位）+ `/root/metaphysics/docs/knowledge-base.md`（§2 M5 快照链）
2. 本批=**快照链 + CHANGELOG 声明值核验**（只核不修，发现问题记录 P0/P1/P2）
3. 汇报 300 字内

## 任务
1. **快照链核验**：snapshots/ 下 20260817_f2 ~ f19 快照逐份存在 + _meta 备注与 CHANGELOG 声明一致（F0-F19 各批的基线链）
2. **六件套对 CHANGELOG 声明值**（当前 HEAD = F19 后）：
   - verify_mangpai（432）/ verify_dayun（70）/ layer1（64）/ layer3（20）
   - pytest 全量（CHANGELOG 声明 648 passed + 1 xfailed + 19 xpassed）
   - blind_eval 当前基线（对照 f19 快照）：heldout 官 48✅/财 47✅/职 24✅
   - 67 例 / famous / calib（CHANGELOG 声明 0 回归）
   - 双 seed
3. **基线漂移检查**：当前 HEAD 实跑 blind 与 f19 快照是否一致（理论上应完全一致——修复后无新改动；若有 diff 说明有未记录改动）
4. **CHANGELOG 完整性**：F0-F19 每批在 CHANGELOG 有记录（无缺失）
5. 输出：核验结果表（每项声明 vs 实测）+ 问题清单（P0 断链/P1 漂移/P2 记录）

## 红线
- 只核不修（发现问题记录，修复另排）
- 不碰代码

## 验证/产出
1. 六件套实测数字（与 CHANGELOG 声明逐项对照表）
2. 快照链完整清单
3. 问题清单（若有）
4. 汇报 300 字内
