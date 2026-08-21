# Kimi 任务：动工批 N1 · 七维叙述代码批（qianyi/xiangmao 进五维，L2 两红线 + schema + 锚定行）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 七维计划（`docs/tasks/kimi-narrative5d-plan.md`：五维→七维，迁移/相貌独立成维；复用 conclusion/basis/confidence schema；L2 两条按维黑名单——迁移禁出国/移民/海外/国外/外国，相貌禁漂亮/美/丑/帅+排除窗复用 E7 ±5 窗口；prompt SCHEMA_SPEC +2 条款 + _qianyi_anchor/_xiangmao_anchor 两锚定行；few-shot 不动）+ 统一动工方案（N1 纯 LLM 层改动，叠 F1+F3 终态：_l2_enum 已含误报窗/max_tokens 8192 已落地）+ V1 报告（维度口径：或然窗/弱线→confidence 锁低）
2. 本批 = **N1 七维代码批**（llm_channel/llm_prompt 层；引擎零改动；纯本地零 API）
3. 汇报 300 字内

## 任务
1. **DIMENSIONS 五→七**：加「迁移」「相貌」两维（复用 conclusion/basis/confidence schema——L0/L1 自动覆盖）
2. **L2 两条按维红线**（llm_channel `_l2_enum` 扩展）：
   - 迁移维：绝对禁「出国/移民/海外/国外/外国」（对齐引擎措辞上限）
   - 相貌维：禁「漂亮/美/丑/帅」结论词 + 排除窗（美元/丑时放行——复用 E7 ±5 窗口机制）
3. **prompt 扩展**（llm_prompt）：
   - SCHEMA_SPEC + 两条款（迁移/相貌维度定义 + 措辞约束）
   - `_qianyi_anchor`/`_xiangmao_anchor` 两条 per-case 锚定行（从引擎特征注入：qianyi markers/应期、xiangmao markers）
   - few-shot 不动
4. **哨兵先红后绿**：test 新增——迁移维说「出国」→ 违规；相貌维说「漂亮」→ 违规；排除窗（「美元/丑时」）→ 放行；无迁移信号盘叙述不得断言迁移（锚定行约束）
5. **F-V3-1 搭车**：prompt `_zhiye_anchor` 补 unemployed 桶一行（zhenbao-23a 族——N2 漏斗里加 zhenbao-23a 强制集验证）

## 红线
- 引擎零改动（compute_all 不动）；L0/L1/N1 校验不回归
- 只吃 trainset；LLM 输出不落 compute_all dict
- 措辞约束：迁移上限「迁移/远行」、相貌禁结论词

## 验证
1. 哨兵红绿（新增测试）
2. pytest 全绿（807+新增）
3. blind 不需要（引擎零触）
4. payload 探针（qianyi/xiangmao 特征已在 selectors 41——确认 prompt 锚定行能取到）

## 汇报（300 字内）
七维 schema + L2 两红线 + 锚定行 + unemployed 搭车 + 哨兵 + pytest
