# K3 任务：294 例训练集修复 · 职业批2（剩余 43❌）

## ⚠️ 执行指引
1. 分析归档：`/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-zhiye-2026-08-08.md`（55 例逐例总表 + 簇）+ 你批 1 的实测（_zy55_* 脚本可复用）
2. 基线：trainset 294 例 职业 32.94%（28✅/14⚠️/43❌，批1 后）；heldout 职业 40.38%（21✅）
3. **先改代码，后统一验证**；汇报 300 字内
4. 铁律：留出集只评估不反推；回归检测反馈用书锚修

## 任务：剩余 43❌（按归档 + 批1 后现状）
1. 先重扫批 1 后 43❌ 的现状（哪些被批 1 改动影响、哪些仍是原簇）
2. 按归档逐簇修（优先收益高的）：
   - 已知残留簇：**中医 3 簇**（doctor 桶）、yx-2658、图书管理员（teacher？）、邢铭芬 tie 簇
   - teacher/accountant/doctor 桶缺口（批 1 未充分动的桶）
   - 其它归档里的簇（按逐例总表）
3. 每簇书锚驱动，窄条件（参考批 1 的教训：**改完先自查 heldout 对应桶无损**再全量验证）

## 红线
- **heldout 职业 21✅ 不回退**（40.38% 底线，批1 的 merchant 3 例 + 其它 ✅ 全保）
- trainset 职业 28✅ 不回退，**❌ 应减少**（预期 43❌ → ~35-38❌）
- 财命/官命不退化；与既往批锚不冲突

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260808_r.json` — **heldout 职业 ≥40.38%（21✅ 不回退）**，财命/官命零翻转
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 职业 ≥32.94% 且 ❌ 减少
5. 67 例回测：0 回归
6. famous + calib：0 回归

## 汇报（300 字内）
改动/行号/diff 摘要 + 验证 6 项 + trainset 职业翻转（按桶分列）+ heldout 无损确认
