# Kimi 任务：修复批 F17 · xueli + liuqin

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F17 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批7（xueli P0×7：**破坏之神书=财/伤官/比劫被改写为财+枭**/21 书例仅 5 达标；liuqin P0×5：**星宫同坏总门丢失/子息原神取反**/排行/情谊/子女优劣三节整缺）
3. 汇报 300 字内

## 任务
1. **xueli 破坏之神修正**：书=财/伤官/比劫（非财+枭）；21 书例 5→提升
2. **liuqin 星宫同坏总门**：补回
3. **liuqin 子息原神取反**：修正
4. **liuqin 三节补齐**：排行/情谊/子女优劣（书锚）

## 书例哨兵（先红后绿）
- xueli 21 书例 / liuqin 星宫同坏书例 / 子息书例

## 红线
- heldout 零回退；书锚铁律

## 验证
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline 20260817_f7.json 翻转明细 5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
改动/行号/书锚 + 哨兵红绿（xueli 书例命中数）+ 验证 6 项
