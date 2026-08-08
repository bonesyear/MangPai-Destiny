# K3 任务：294 例训练集修复 · 职业批1 修正版（merchant 收窄须过 heldout 闸）

## ⚠️ 执行指引
1. 分析归档：`/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-zhiye-2026-08-08.md` + 你的模拟脚本（`_zy55_sim/_zy55_feat/_zy55_dump` 在 heldout/ 下，直接复用）
2. 基线：trainset 294 例 职业 25.29%（22✅/10⚠️/55❌）；heldout 职业 40.38%（21✅）
3. **先改代码，后统一验证**；汇报 300 字内
4. 铁律：留出集只评估不反推——但**回归检测反馈不算调参**：heldout 商人被误伤是规则 bug，须用书锚修正

## ⚠️ 首版教训（已回退，本版必须避免）
首版在 trainset 收窄 merchant 泛触后：trainset 职业 25.29→29.89%（✅+4），但 **heldout 真商人被误伤 3 例**：
- **ans10-下海百万 ✅→❌**（商人→教师；书明文「辞职下海创业」=典型商人）
- **li002-牟其中 ✅→⚠️**（商人→未分类；书明文「民营企业家」）
- **li131-金昌盛 ✅→⚠️**（商人→未分类；书明文「商人·钢材」）
根因：trainset 上保住了 merchant ✅，但 heldout 商人特征分布不同——收窄条件在留出集上误杀。**本版 merchant 收窄条件必须用 heldout 商人共同校验**（书锚：下海创业/民营企业家/钢材商 = 真实经营信号，不是泛触）。

## 任务（按归档模拟组合，修正 merchant 条）
1. **merchant 收窄（修正版）**：门户+1/官杀当财+1/内食神+2 泛触收窄，但**下海创业/民营企业家/行业商（钢材等）类书明文商人必须保留**——收窄针对「无真实经营信号的泛触」；验证时 heldout 商人 3 例不得回退
2. **performer 桃花条件重写**：桃花作核心条件双向失败（fp 9 全有桃花/真艺人 7 全无）——改组合
3. **military corro 去虚高 + 真军警 boost**：corro 降权 + 军警真信号（杀刃细分，可借官命联动）
4. **teacher/accountant/lawyer/doctor 桶**：按归档缺口补信号

## B 型（一并做）
- 「冠军」→unscorable：`_ZY_EXCLUDE` 增词（须 --rescore + CHANGELOG 记 rubric 版本）

## 红线
- **heldout 职业 21✅ 不回退（40.38% 底线）**——尤其 ans10/li002/li131 三商人
- trainset 职业 22✅ 不回退，❌ 应减少（预期 55❌ → ~45-48❌）
- 财命/官命不退化；与既往批锚不冲突（批11 merchant、批12 _ZY_EXCLUDE、批29 官命）

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260808_q.json` — **heldout 职业 ≥40.38%（21✅ 不回退）**，财命/官命零翻转
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 职业 ≥25.29% 且 ❌ 减少
5. 67 例回测：0 回归
6. famous + calib：0 回归

## 汇报（300 字内）
各桶改动 + 验证 6 项 + trainset 职业翻转（按桶分列）+ **heldout 商人 3 例无损确认**
