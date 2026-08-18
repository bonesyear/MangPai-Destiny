# Kimi 任务：LLM 通路 · 校验器近-miss remap（零 API 成本收编残余）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/llm-batch-report-20260818.md` + 迭代 4 结果（L1 3.41% 达标，剩 10 条：hunyin 6/xiangfa 3/caiming 1）
2. **你的评估意见**（采纳）：近-miss 意图唯一可确定性 remap（缺 `_ops` 前缀只有单一合法展开），把 L1 转正——不改 LLM、不松线；只对可唯一展开者 remap，歧义仍记违规
3. 本批 = **校验器侧 remap + 离线重评分**（零 API 成本——对已有 v5 数据重算，不重跑 294 例）
4. 汇报 300 字内

## 任务
1. **分析剩余 10 条模式**（hunyin 6/xiangfa 3/caiming 1 的具体键名 + 唯一展开路径）
2. **remap 规则落地**（llm_channel.py 校验器）：
   - 可唯一展开的近-miss（如缺 `_ops` 前缀/层级拍平）→ 自动映射真键，L1 转正（violations 里标 remapped）
   - 歧义（多候选/臆造）仍记违规
   - 规则表：模式 → 唯一展开（书锚/特征结构依据）
3. **离线重评分**：对 v5 已有 294 例数据重跑校验（零 API 成本）——出 remap 后 L0/N1/L1/L2
4. pytest 全绿（test_llm_channel 增 remap 规则测试）

## 红线
- 引擎零改动；不动 llm_prompt.py（remap 是校验器侧收编，LLM 行为不变）
- 歧义不 remap（宁缺毋滥——只收编意图唯一者）

## 产出
1. remap 规则表（模式/唯一展开/依据）
2. 离线重评分判定表（remap 前后对比）
3. pytest 结果
4. 汇报 300 字内
