# Kimi 任务：修复批 F4 · 虚实木性（virtual_solid + wood_type）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F4 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批9（virtual_solid P0×3：全局找根违背「只就一柱」/坐印判虚违背「坐印皆实」/传导 zuogong_confirm；wood_type P0×1：漏「水不生木之根也是死木」，**岳飞造误判活木**）
3. 本批**中等影响**：虚实体是五行气力判定辅助模块，影响做功/用神的「虚实」判断
4. 汇报 300 字内

## 任务（四 P0 + 传导）
1. **virtual_solid 全局找根收窄**：违背「只就一柱」——找根范围限本柱（书锚见批9 归档）
2. **virtual_solid 坐印判虚修正**：违背「坐印皆实」——坐下印星不当虚（书锚）
3. **zuogong_confirm 传导同步**：虚实体修正后 confirm 消费侧一致（防修 A 破 B）
4. **wood_type 死木补条件**：漏「水不生木之根也是死木」（书锚）——岳飞造（已知触发点）须从活木改死木

## 书例哨兵（先红后绿）
- 岳飞造（活木→死木预期）
- 批9 归档里 virtual_solid 的书例锚
- 坐印皆实书例

## 红线
- **heldout 财命 46✅ 不回退**（66.67%）、官/职不退化
- 书锚铁律：每处改动带书明文行号
- wood_type 改动可能影响像法/职业木性判定——全量 diff 审查

## 验证（全部通过后回报，300 字内）
1. 书例哨兵：先红后绿记录
2. `python3 mangpai/verify_mangpai.py` — 432 全绿
3. `python3 -m pytest mangpai/tests/ -q` — 全绿
4. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260817_f3.json` — heldout 翻转明细（每个列原因）
5. 67 例 + famous + calib — 0 回归
6. 双 seed 一致

## 汇报（300 字内）
四 P0 改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细（若有）
