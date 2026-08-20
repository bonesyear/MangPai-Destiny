# Kimi 任务：缺口批1 · qianyi 迁移/出国模块（设计+实现合一拍）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 缺口方案归档（`/root/.claude/projects/-root-metaphysics/memory/kimi-gaps-plan-2026-08-20.md` §一 qianyi：~24 条独立规则四书皆载、骨架清晰（驿马动静×宫位空间）、「合到门户→出国/移民」两书同构达立法门槛、零新输入（shensha 马星/岁运冲合现成）、红线=措辞上限「迁移/远行」不出「出国」硬断语）
2. **独立判断纪律**：书锚为准（每条规则带行号）；方案归档的书锚已收，回书核对关键锚
3. 本批 = **qianyi 迁移模块**（新模块 + engine 接线 + 特征 JSON；引擎已有判定零改动；纯本地零 DeepSeek）
4. 汇报 300 字内

## 任务
1. **模块设计落地**（按归档 §一）：
   - 原局三 marker（驿马动静×宫位空间/门户冲合等——按归档定稿）
   - 应期三机制（合到门户/马星动/岁运冲合引动）
   - 每条规则书锚行号随行注释
2. **subjective/qianyi 实现**（~250 行）：输入=现有引擎字段（shensha 马星/岁运/宫位），输出结构化 marker + 应期信号
3. **engine 接线**：result['qianyi'] 键（_safe_compute 同款）+ schools.py 追加进特征 JSON（LLM 可消费，prompt 五维暂不扩）
4. **哨兵先红后绿**：test_qianyi.py 8-10 测——书例对照造（四书里迁移案例）+ 反例 guard（无迁移信号盘）
5. **红线**：措辞上限「迁移/远行」，**不出「出国」硬断语**（书无级别判据）；引擎已有判定零回归

## 红线
- 引擎已有判定零改动（新模块增量，只加 result 键不改旧逻辑）
- heldout 财 47✅/官 48✅/职 24✅ 不回退（盲测零翻转）
- 书锚铁律

## 验证（六件套）
1. 哨兵红绿（新增测试）
2. verify 432
3. pytest 全绿（776+新增）
4. blind --baseline snapshots/20260819_e3.json 零翻转（新模块不触发旧判定）
5. 67/famous/calib 0 回归
6. 双 seed 一致 + payload 探针（qianyi 特征进 payload 确认）

## 汇报（300 字内）
设计定稿要点（marker/应期机制）+ 实现/行号 + 哨兵红绿 + 验证 6 项 + 零翻转确认 + 新快照
