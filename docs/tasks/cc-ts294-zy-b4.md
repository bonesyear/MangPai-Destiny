# K3 任务：294 例训练集修复 · 职业批4（剩余 31❌ 收尾）

## ⚠️ 执行指引
1. 分析归档：`/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-zhiye-2026-08-08.md` + 批3 后残留清单（CHANGELOG 第三十三批）
2. 基线：trainset 294 例 职业 45.88%（39✅/15⚠️/31❌，批3 后）；heldout 职业 44.23%（23✅/8⚠️/21❌）
3. **先改代码，后统一验证**；汇报 300 字内
4. 铁律：留出集只评估不反推；回归检测反馈用书锚修；改完先自查 heldout 对应桶无损

## 任务：剩余 31❌ 按残留清单逐簇修
已知残留簇（批3 后）：
- **中医 3 簇**（merchant 分差 7-11——医生判商人，分差大）
- **军警 C 备案簇**（岳飞/戴笠/公安×2——墓库无官杀军警，C 类备案可能无解，评估后确认）
- **lawyer 盲区**（yx-2/3）
- **accountant 5**（桃花 fp 压平误伤真艺人被否，待新通道——会计与 performer 的判别）
- **performer 财明现挡**（阿炳/帕瓦罗蒂/导演——无桃花通道被财明现豁免挡住）
- **马云/图书管理员/校长/组织部/记者等散簇**

每簇书锚驱动，窄条件。**预期：31❌ → ~25-28❌（职业 ~47-48%）**——收益递减期，不强求全修，C 类备案可确认收档。

## 红线
- **heldout 职业 23✅ 不回退**（44.23% 底线）
- trainset 职业 39✅ 不回退，❌ 应减少
- 财命/官命不退化；与既往批锚不冲突（merchant ✅ 15+、无桃花通道、军警羊刃驾杀）

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_b.json` — **heldout 职业 ≥44.23%（23✅ 不回退）**，财命/官命零翻转
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 职业 ≥45.88% 且 ❌ 减少
5. 67 例回测：0 回归
6. famous + calib：0 回归

## 汇报（300 字内）
各簇改动/行号/diff 摘要 + 验证 6 项 + trainset 翻转（按桶分列）+ heldout 无损确认 + 职业维度收官结论（C 类备案是否收档）
