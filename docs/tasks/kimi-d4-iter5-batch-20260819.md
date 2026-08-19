# Kimi 任务：修复批 D4 · prompt 迭代 5（职业桶锚定 + 应期逐年吉凶锚定 → S1 复验）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + T3 S1 报告（`docs/kimi-review3-t3-e2e-20260818.md`：翻转 9/30——职业维 8（无倾向被断言 5 + 主荐桶不一致 3）+ 应期维；放大 10.1% 达标）+ D3 补供（dayun_analysis 14 字段已进 payload，L1 可溯，**本批直接可用**）
2. **前置已完成**：D3 已补供大运表（每运 14 字段）；职业桶数据本就在 payload
3. **v4-pro 协议**（用户拍板）：复验评审/judge 用 v4-pro 双实例隔离，谷段跑
4. 本批 = **D4 prompt 迭代 5**（llm_prompt.py/llm_channel.py 可改，引擎零改动）+ **S1 复验**
5. 汇报 300 字内

## 任务
1. **职业桶锚定**（治 S1 职业维翻转 8 格）：
   - prompt 明令：职业叙述必须引用 `zhiye.primary` 及候选桶枚举；「无倾向」必须如实说无倾向，禁止断言具体职业
   - 主荐桶与候选桶的引用规则（LLM 只能展开引擎给的主荐桶，候选桶可提及但标注候选）
2. **应期逐年吉凶锚定**（治应期维翻转/套话）：
   - prompt 引用 D3 补供的 `dayun_analysis.dayun[]`（14 字段：overall/positive/negative_signals 等）
   - 应期叙述必须逐运锚定（某运吉/凶/平按 overall+信号），禁止脱离大运表自由发挥
   - 流年叙述锚 `liunian_analysis`（如有）
3. **S1 复验**（同 T3 协议三层漏斗）：
   - 规则锚零 API 扫 281 例 → v4-pro 评审 30 例（同抽样设计）→ v4-pro judge 281 例（双实例隔离）→ 一致率校准
   - 达标线不变：翻转 ≤1/30 且 L2 高危零翻转；放大 ≤20%
4. 产出：S1 复验报告（对比 T3 基线：翻转 9/30→?）

## 红线
- 引擎零改动（只动 llm_prompt.py/llm_channel.py）
- 只吃 trainset；LLM 输出不落 compute_all dict
- 谷段跑 judge/评审（成本控制）；预算 ~¥30-75

## 验证
1. pytest 全绿（test_llm_channel 适配）
2. S1 复验达标判定（翻转/放大/一致率）
3. 成本实测

## 汇报（300 字内）
职业桶/应期锚定落地要点 + S1 复验结果（vs T3 基线 9/30）+ 达标判定 + 成本 + 飞书 go/no-go 更新
