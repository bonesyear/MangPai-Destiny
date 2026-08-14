# K3 任务：294 例训练集修复 · 职业批3（剩余 35❌，收工记录指引）

## ⚠️ 执行指引
1. 收工记录：`/root/metaphysics/docs/remaining-tasks-20260808.md`（批 3 指引在「三、下一步」第 1 条）+ 你的分析归档 `k3-trainset294-zhiye-2026-08-08.md` + 模拟脚本 `_zy2_sim.py/_zy2_sim2.py/_zy2_sim3.py` 复用
2. 基线：trainset 294 例 职业 43.53%（37✅/13⚠️/35❌，批2 后）；heldout 职业 44.23%（23✅/7⚠️/22❌）
3. **先改代码，后统一验证**；汇报 300 字内
4. 铁律：留出集只评估不反推；回归检测反馈用书锚修

## 任务 0（先修，变差点名）
**A1 水财算帐通道误伤**：
- heldout **ans12 下岗穷命 ⚠️→❌**（未分类→会计）
- trainset **yx-中介 ⚠️→❌**（投资中介→会计）
- 书锚驱动修正：水财算帐通道条件收窄（下海/中介类非会计误伤）

## 任务 1：剩余 35❌ 按收工记录残留簇逐簇修
- 中医 3 簇（merchant 7-11 分差过大）
- military C 备案簇（岳飞/戴笠/公安×2）
- lawyer yx-2/3
- laborer 4（base_career 可达性）
- accountant 6（桃花 fp 压平误伤真艺人被否，待新通道）
- performer 阿炳/帕瓦罗蒂/导演（财明现豁免挡无桃花通道）
- 马云/图书管理员/校长/组织部/记者等散簇

每簇书锚驱动，窄条件；**改完先自查 heldout 对应桶无损**再全量验证（批1 教训）。

## 红线
- **heldout 职业 23✅ 不回退**（44.23% 底线，批1 merchant 3 例 + 批2 新增全保）
- trainset 职业 37✅ 不回退，**❌ 应减少**（预期 35❌ → ~28-32❌，职业 ~46%）
- ans12/yx-中介 变差先修复（任务 0）
- 财命/官命不退化；与既往批锚不冲突

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_a.json` — **heldout 职业 ≥44.23%（23✅ 不回退）**，财命/官命零翻转
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 职业 ≥43.53% 且 ❌ 减少
5. 67 例回测：0 回归
6. famous + calib：0 回归

## 汇报（300 字内）
任务 0 修复确认 + 各簇改动/行号/diff 摘要 + 验证 6 项 + trainset 职业翻转（按桶分列）+ heldout 无损确认
