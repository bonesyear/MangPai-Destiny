# K3 任务：294 例训练集修复 · 职业批2 接续（剩余 41❌）

## ⚠️ 执行指引
1. 分析归档：`/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-zhiye-2026-08-08.md`（55 例逐例总表 + 簇）
2. **接续状态（不是从头开始）**：批2首步已落地并 commit（`git log --oneline -2` 看 `4cdeb45` 第三十一批）——zhiye.py 已改 44 行（中医/teacher 等首轮信号），**先 `git diff 4cdeb45^ 4cdeb45 -- mangpai/subjective/zhiye.py | head -80` 检测已改内容，在其上继续，不重跑基线**
3. 基线（批2首步后）：trainset 294 例 职业 **36.47%**（31✅/13⚠️/41❌）；heldout 职业 40.38%（21✅）
4. 复用模拟脚本：`mangpai/tests/heldout/_zy2_sim.py`（T1-T4/P1/A1 网格）+ `_zy2_sim2.py`（T4/YM/A1/J9/M2 全量回归），先跑看剩余 41❌ 现状再落笔
5. **先改代码，后统一验证**；汇报 300 字内
6. 铁律：留出集只评估不反推；回归检测反馈用书锚修

## 任务：剩余 41❌（按归档 + 首步后现状）
1. 先重扫首步后 41❌ 的现状（哪些被首步 44 行影响、哪些仍是原簇）
2. 按归档逐簇修（优先收益高的）：
   - 已知残留簇：**中医 3 簇**（doctor 桶）、yx-2658、图书管理员（teacher？）、邢铭芬 tie 簇
   - teacher/accountant/doctor 桶缺口（首步未充分动的桶）
   - 其它归档里的簇（按逐例总表）
3. 每簇书锚驱动，窄条件（参考批1 教训：**改完先自查 heldout 对应桶无损**再全量验证）

## 红线
- **heldout 职业 21✅ 不回退**（40.38% 底线，商人 3 例 ans10/li002/li131 + 其它 ✅ 全保）
- trainset 职业 31✅ 不回退，**❌ 应减少**（预期 41❌ → ~30-33❌，职业 ~42%）
- 财命/官命不退化；与既往批锚不冲突

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260808_r.json` — **heldout 职业 ≥40.38%（21✅ 不回退）**，财命/官命零翻转
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 职业 ≥36.47% 且 ❌ 减少
5. 67 例回测：0 回归
6. famous + calib：0 回归

## 汇报（300 字内）
改动/行号/diff 摘要 + 验证 6 项 + trainset 职业翻转（按桶分列）+ heldout 无损确认
