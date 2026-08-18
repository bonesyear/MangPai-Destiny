# Kimi 任务：LLM 通路 · prompt 迭代 4（改码不测，复测等 DeepSeek 低峰期）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/llm-batch-report-20260818.md` + 迭代 3 最终（L1 9.62% 剩 31 条：xiangfa 7/hunyin 7/caiming 6/zhiye 2/guanming 2/shensha 2/xiangfa_fallback 2/zaihuo 1/xuNing_placeholder 1/shishen 1——全键名近-miss 长尾；另有 xuNing_placeholder 臆造键）
2. **用户指令：本批只改码不跑复测**——294 例全量复测等 **DeepSeek 低峰期**（峰谷定价：peak 加倍/off-peak 减半，成本可省一半 ¥9→¥4.5）
3. 汇报 300 字内

## 任务
1. **分析剩余 31 条 L1 违规**（逐条：具体键名/猜对概念猜错归属的模式）
2. **迭代 4 修法落地**（llm_prompt.py/llm_channel.py，引擎零改动）：
   - xiangfa/xiangfa_fallback 7+2 条（键名归属残余——清单或回对强化）
   - hunyin 7 条（含 gong_attacked 空值类残留？）
   - caiming 6 条
   - xuNing_placeholder 臆造键（特殊案例——查这个键为什么会出现）
   - 其它长尾
3. **确认 DeepSeek 峰谷时段**（低峰期几点到几点，官方口径）
4. **备好复测命令**：一键命令（合并 analyze），低峰期跑

## 红线
- **本批不跑 294 例全量复测**（离线验证 pytest 除外）——复测等低峰期（用户到时触发 or 你确认时段后建议）
- 引擎零改动；只吃 trainset；LLM 输出不落 compute_all dict

## 验证（离线）
1. pytest 全绿（test_llm_channel 适配新规则）
2. 单例冒烟（1 例即可，验证 prompt 改动不破坏链路——成本极小；**不做 294 例全量**）

## 汇报（300 字内）
31 条违规逐类分析 + 迭代 4 修法落地要点 + 峰谷时段确认 + 复测命令（低峰期一键跑）+ 单例冒烟结果
