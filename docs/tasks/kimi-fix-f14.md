# Kimi 任务：修复批 F14 · zaihuo + LLM 红线（护栏同批）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F14 定位 + **决策点 3：prompts 已解锁**）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批7（zaihuo P0×5：马星 count 恒真死判据/死亡「高」双向偏离「墓绝空亡齐见」/漏接牢狱进 max_risk+凶向链/**engine.py:588 唯一收全量 yunfan 的模块（A1 破口）**）、批10（**寿元红线只堵一半：zaihuo.siwang 死亡档+「寿元星遭破」原文直进 LLM 通道，prompt 全文无一字死亡禁令**）
3. **prompts 已解锁**（用户批准）——可以写死亡/寿数禁令进 prompt
4. 汇报 300 字内

## 任务
1. **马星死判据**：count 恒真修复
2. **死亡「高」收窄**：按「墓绝空亡齐见」书诀
3. **牢狱接入**：laoyu（F9 已修活）→ max_risk/凶向链（engine.py:588 全量 yunfan 破口审查——A1 切片 or 收窄）
4. **LLM 红线（护栏）**：prompt 写入死亡/寿数禁令（zaihuo.siwang 不直进 LLM 通道 or 强制屏蔽字段）；payload 侧寿元字段降级

## 书例哨兵（先红后绿）
- 马星书例 / 墓绝空亡齐见书例 / 牢狱衔接书例

## 红线
- **heldout 财命 46✅ 不回退**、官/职不退化
- 安全红线：死亡/寿元不做预测断言，LLM 通道物理屏蔽
- 书锚铁律

## 验证
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline 20260817_f7.json 翻转明细 5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + LLM 红线落地方式
