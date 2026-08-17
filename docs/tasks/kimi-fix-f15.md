# Kimi 任务：修复批 F15 · zhiye（依赖 F11/F13）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F15 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批7（zhiye P0×6：**7.3 职业章 12 书例探针仅中 1**/merchant 桶过宽吸走律师/教师/会计/公安书例/**军警 8.2 七组明文组合全未实现**/传导：caiming 错档经 C4 硬绑定放大（宾馆服务员书断贫命→merchant 12））、批8（gongmen_wuzhi 实现未接入——is_wuzhi 近恒真）
3. **前置**：F11（caiming 档位）F13（shensha 桃花 day-ref）已修——本批在其上修
4. 汇报 300 字内

## 任务
1. **merchant 收窄**：12 书例仅中 1——merchant 过宽吸走他桶书例（书锚逐例）
2. **军警 8.2 七组明文组合**：实现（或接入 gongmen_wuzhi——**决策**：F1 标记弃用的 gongmen_wuzhi 是接入还是在本模块重写）
3. **C4 硬绑定审查**：caiming 错档经 C4 放大问题（宾馆服务员）
4. **12 书例全量回归**：从 1/12 提升

## 书例哨兵（先红后绿）
- 职业章 12 书例（全量）/ 宾馆服务员（C4 修正）/ 罗斯切尔德/乔布斯（merchant ✅ 不得回退）

## 红线
- **heldout 职业 23✅ 不回退**（44.23%）、财/官不退化
- merchant 既有 ✅（罗斯切尔德/乔布斯等）不得误伤
- 书锚铁律

## 验证
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline 20260817_f7.json 翻转明细 5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
改动/行号/书锚 + 哨兵红绿（12 书例命中数）+ 验证 6 项 + heldout 职业翻转明细
