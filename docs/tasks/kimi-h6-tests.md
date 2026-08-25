# Kimi 任务：代码卫生审查 H6 · 测试基建批（51 测试文件——结构/质量/死测试）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（七维）+ H1-H5 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×91——本批**重点查同型残留**：裸 except/死代码/局部 import）+ 收工终态
2. 本批 = **代码卫生 H6 · 测试基建批**（只审不改；纯本地零 API；51 文件——按组走）
3. 汇报 300 字内

## 审查对象（mangpai/tests/ 51 文件，按组）
**组 A（15 文件）**：test_llm_channel（757 行）/ test_feishu（375）/ test_juefa（368）/ test_p0_blindgap（358）/ test_zeishen_bushen（343）/ calib_assertions（332）/ test_g9_zihe_g5_g1（320）+ test_f11~f19 系列（各批哨兵）
**组 B（~36 文件）**：其余全部（test_anhe/test_body_parts/test_dayun_objective/test_entry_guards 等 + heldout/ 子目录 + snapshots 基建）

## 审查维度（测试特有的）
1. **死测试/冗余测试**：从未失败的测试（恒真断言）、重复覆盖（同一断言多文件）、跳过未完成的测试（skip/xfail 滥用）
2. **断言质量**：弱断言（只 assert not None/不验证值）、无断言测试（只跑不查）
3. **测试与实现脱节**：测试名与断言不符、断言与书锚不符（哨兵纪律——书例哨兵是否真锁书锚）
4. **fixture/基建**：snapshot 路径硬编码、临时文件泄漏、测试间状态污染（共享可变全局）
5. **异常处理一致性**：测试里裸 except（吞失败——测试静默通过的危险）
6. **复杂度/重复**：测试函数过长、重复 setup、复制粘贴断言块
7. **import 卫生**：未使用导入、测试依赖顺序

## 重点（测试层特有的）
- **"绿但没验证"风险**：测试跑过但断言没锁住行为（恒真/弱断言）——这是测试基建最大的坑
- **哨兵纪律核查**：各批次哨兵（test_f1_gate/test_qianyi/test_xiangmao/test_d6b 等）是否真"先红后绿"可验证（红态能被测试复现吗）
- **快照基建**：snapshots/ 的读写/基线对比逻辑健康度

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H6 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API
- 本批是"测试审查"——**不实际改任何测试**

## 汇报（300 字内）
51 文件审查结果（按组）+ P0/P1/P2 统计 + "绿但没验证"风险清单 + 哨兵纪律核查 + 快照基建
