# Kimi 任务：缺口批2 · xiangmao 相貌模块（轻量 marker 层）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 缺口方案归档（`/root/.claude/projects/-root-metaphysics/memory/kimi-gaps-plan-2026-08-20.md` §二 xiangmao：39 锚收敛 4 主线（秀气透干/金水伤官限辛/活木见火/丙丁癸眼象）+2 弱线，全用现有字段；轻量 marker 层无判定无档位供叙事消费，仿 ganqing 定位；贵相口诀/难看反推/五行形体表如实标不可计算收档；哨兵对照造=梦露/刘晓庆/阮玲玉）
2. **独立判断纪律**：书锚为准（每条规则带行号）；39 锚回书核对关键锚
3. 本批 = **xiangmao 轻量 marker 层**（新模块 + engine 接线 + 特征 JSON；引擎已有判定零改动；纯本地零 DeepSeek）
4. 汇报 300 字内

## 任务
1. **设计落地**（按归档 §二）：
   - 4 主线 marker（秀气透干/金水伤官限辛/活木见火/丙丁癸眼象）+ 2 弱线
   - 每条书锚行号随行注释
   - **定位：无判定无档位**（不判美丑等级），输出 marker 供叙事层消费（仿 ganqing）
   - 不可计算项（贵相口诀/难看反推/五行形体表）如实标注收档
2. **subjective/xiangmao 实现**（~150 行）：输入=现有字段（十神/五行/干支结构），输出 marker 列表
3. **engine 接线**：result['xiangmao'] 键（_safe_compute 同款）+ schools.py 追加进特征 JSON（LLM 可消费，prompt 五维暂不扩）
4. **哨兵先红后绿**：test_xiangmao.py 5-6 测——对照造（梦露/刘晓庆/阮玲玉——按归档选）+ 反例 guard
5. **红线**：只出 marker 不出判定（不写「美/丑/帅」结论词——无档位设计）

## 红线
- 引擎已有判定零改动（新模块增量）
- heldout 财 47✅/官 48✅/职 24✅ 不回退（盲测零翻转）
- 书锚铁律

## 验证（六件套）
1. 哨兵红绿（新增测试）
2. verify 432
3. pytest 全绿（787+新增）
4. blind --baseline snapshots/20260820_gap1.json 零翻转
5. 67/famous/calib 0 回归
6. 双 seed 一致 + payload 探针（xiangmao 特征进 payload 确认）

## 汇报（300 字内）
设计落地（主线 marker + 收档项）+ 实现/行号 + 哨兵红绿 + 验证 6 项 + 零翻转确认 + 新快照
