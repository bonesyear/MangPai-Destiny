# Kimi 任务：修批 G3 · 引擎侧收尾（大眼锚注 + F-N2-1 秀气线 + 删 sanitize 兜底 + judge 判据）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 统一待修清单（`docs/tasks/review6-fix-backlog.md` G3/备案区：#15 大眼锚注随引擎批 / F-N2-1 秀气线 desc 含「漂亮」→引擎侧修+删 `_xm_sanitize` 兜底 / judge 判据更新）+ W2 报告（_xm_sanitize 语义安全域：引擎侧修复后应连函数一起删）
2. 本批 = **G3 引擎侧收尾**（⚠️ 本次允许引擎模块小改——xiangmao.py 仅锚注与 desc 措辞，判定逻辑不变）
3. 汇报 300 字内

## 任务
1. **#15 大眼锚注**（W3 P2）：`xiangmao.py:152` 眼象线「大眼」补 inline 锚——回书找「大眼」表述的书锚（丙为眼框 zhongji:1483 附近、黛安娜大眼睛 lixiangxue:12632——核实哪条支持「大眼」表述）；有锚则补注，无锚则措辞收敛（如「眼象突出」）
2. **F-N2-1 秀气线 desc 修**（引擎侧根治）：
   - `xiangmao.py` 秀气线 desc 含「漂亮」的表述——按书理改为准确表述（秀气≠漂亮，zhongji:3914 性别分流——原文是「女看秀气」？核实书原文表述改准）
   - 修后 `_xm_sanitize`（llm_channel 的「漂亮→秀气」兜底替换）可删——确认无其他依赖后删除该函数及其调用
3. **judge 判据更新**（下轮评审前）：`_t3_eval.py`/评审判据——第七轮起 judge 用七维口径（迁移/相貌维加严判据）+ F6-6 程度词禁入判据
4. **回归确认**：xiangmao 输出键结构不变（desc 措辞变不影响消费方）；锚定行/LLM 叙述引用不受影响

## 红线
- ⚠️ 本次为引擎模块小改（xiangmao.py）——**判定逻辑/输出键零变**，仅锚注与 desc 措辞；其余模块不动
- 六件套全量（引擎侧改动后必须 blind 验证）

## 验证（六件套）
1. 哨兵红绿（test_xiangmao 适配新 desc 措辞 + sanitize 删除后测试更新）
2. verify 432
3. pytest 全绿（838+新增-删减）
4. blind --baseline snapshots/20260822_g2.json 零翻转（引擎改动后关键）
5. 67/famous/calib 0 回归
6. 双 seed 一致 + payload 探针（xiangmao desc 新措辞正常）

## 汇报（300 字内）
大眼锚注裁决 + 秀气线措辞修正 + sanitize 删除确认 + judge 判据 + 六件套（blind 零翻转关键）+ 全量收官确认
