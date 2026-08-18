# Kimi 任务：LLM 通路 · prompt 迭代 2（键清单附注 + per-case 财档锚定 + 复测）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/llm-batch-report-20260818.md` + 迭代 1 结果（L1 23.88% 超标剩 83 条全「键不存在」近-miss：caiming.wealth_grade×17 真键 gongliang/xiangfa.all_findings+juxiang×19 真键 xiangfa_ops/guanming.authority×4/hunyin.is_duohun×4 真键 duohun；L2 财档越限 44 条小康→富 22/贫→富 14）
2. 本批 = **迭代 2**（Kimi 上批自定的两个方向）+ 294 例复测；引擎零改动
3. 汇报 300 字内

## 任务（两个方向）
1. **user prompt 附特征 JSON 实际键清单**：把特征 JSON 的顶层键+子键清单直接写进 user prompt（不是让 LLM 猜键名）——近-miss 编造可压大半
   - 实现：llm_prompt.py 动态生成键清单（从 build_payload 输出提取实际键结构）或静态维护一份精确清单
   - 注意：清单必须与 build_payload 实际输出**逐字一致**（防止又引入新的键名偏差）
2. **财档 per-case 锚定**：user prompt 直接写入本案 `caiming.tier_static/tier` 的上限档原值（如「本案财命档上限=小康」）——治小康→富/贫→富越限

## 复测
- 294 例全量复测（validate=mark）
- 达标判定：L0≈0 / N1<2% / **L1<5%** / L2 参考
- 不达标 → 剩余违规分布 + 迭代 3 方向（或判定收档）

## 红线
- 引擎零改动（只动 llm_prompt.py/llm_channel.py）
- 只吃 trainset；LLM 输出不落 compute_all dict

## 验证
1. pytest 全绿
2. 复测达标判定表
3. 成本实测

## 汇报（300 字内）
两方向落地要点 + 复测达标判定（L0/N1/L1/L2 实测率）+ 剩余违规分布 + 成本 + **是否可进正式通道**
