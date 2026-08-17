# Kimi 任务：修复批 F13 · shensha（桃花/马星/双刃/配置断路）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F13 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批7（岳飞 performer=year-ref 桃花驱动）、批8（shensha P0×3：默认 year 起算颠倒书「日支为主」gaoji:7912/劫煞灾煞无日支双查/**咸池桃花整套无书锚**（书桃花=禄合财官杀伤食 zhongji:1517）/**桃花 day_ref 全库无读者=死数据**/马星 count 恒真死判据/戊双刃四处单值漏检/shensha_reference 配置断路 0 处传 'day'）
3. 汇报 300 字内

## 任务
1. **桃花重建**：按书（zhongji:1517 桃花=禄合财官杀伤食）重定义 + **day-ref 接线**（day_ref 全库无读者→接入 zhiye/hunyin 消费；岳飞 performer 8分→1分的根因修复）
2. **起算主支**：默认 year→day（gaoji:7912 日支为主）；劫煞/灾煞日支双查
3. **马星 count 恒真**：死判据修复（随机 2000 盘 min=3 问题）
4. **戊双刃漏检**：四处单值漏检补全
5. **shensha_reference 配置**：断路修复（0 处传 'day'）

## 书例哨兵（先红后绿）
- 岳飞（performer 8分→1分预期）/ 桃花书例 / 驿马书例

## 红线
- **heldout 职业 23✅ 不回退**（44.23%）、财/官不退化
- 神煞供给侧改动影响 zhiye/hunyin/zaihuo——**下游批必须紧随其后**（F15/F16/F14 会接）
- 书锚铁律

## 验证
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline 20260817_f7.json 翻转明细 5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
五项改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + 岳飞 performer 确认
