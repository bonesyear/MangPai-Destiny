# Kimi 任务：修复批 D3 · dayun 补供（死 selector 修复，选 B 补供方案）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + T3 报告（`docs/kimi-review3-t3-e2e-20260818.md` §A.1：dayun_analysis 死 selector 281/281 缺失，LLM 全程零大运表）+ T4 规划（D3 供给批）+ T2 报告（「大运为路」三书应期骨架）
2. **方案已定（用户拍板）**：选 B **补供**——把 engine 已算的大运分析补进 payload（数据现成、大运是应期骨架、D4 前置、摘除伤核心能力）
3. **独立判断纪律**：旧归档仅参考
4. 本批 = **D3 供给批**（纯引擎/selector 层，零 DeepSeek API）
5. 汇报 300 字内

## 任务
1. **定位断裂点**：selectors 里 dayun_analysis 为什么死（引用了不存在的键？还是 build_payload 没产出？还是 llm_prompt 引用但 payload 无此键？）——T3 说「死 selector 281/281 缺失」
2. **补供实现**：
   - 确认 engine 侧 dayun 分析数据在哪（subjective/dayun.py 输出 → compute_all 的哪个键）
   - selectors 加键 → payload 产出 dayun_analysis（每运：干支/起止/吉凶信号/事件锚——形状适合 LLM 引用）
   - **数据形状要求**：带书锚、结构化（LLM 可逐运引用）、与三层校验器兼容（L1 出处可溯）
3. **payload 体积评估**：补供后每命 +多少 token（8-10 运 × 每运字段）——报数字
4. **D4 联动预留**：补供的字段命名/结构要方便迭代 5 的应期锚定 prompt 引用（写清楚结构即可，prompt 改动留 D4）

## 红线
- 引擎判定零变化（payload 加键不影响 compute_all 判定——盲测零翻转）
- heldout 财 47✅/官 48✅/职 24✅ 不回退
- LLM 输出不落 compute_all dict（维持）

## 验证（六件套）
1. 哨兵红绿（payload 含 dayun_analysis 断言 + 结构测试）
2. verify 432
3. pytest 全绿
4. blind --baseline snapshots/20260819_d2.json 零翻转
5. 67/famous/calib 0 回归
6. 双 seed 一致 + payload 探针（构造盘确认 dayun_analysis 产出 + token 估算）

## 汇报（300 字内）
断裂点定位 + 补供实现/字段结构 + token 体积评估 + 哨兵 + 验证 6 项 + 零翻转确认
