# Kimi 任务：修复批 D5 · 工具/备案批（收尾）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + T4 规划（D5 定位：rescore glob 顺序修复；G6 scrub/as_of_year/子夜带备案入 KB）+ D4 汇报（已顺手修 rescore glob 覆盖隐患——**先确认现状，已修的跳过不重复**）
2. 本批 = **D5 工具/备案批**（小收尾，零引擎判定改动）
3. 汇报 200 字内

## 任务
1. **rescore glob 状态确认**：D4 说"顺手修 rescore glob 覆盖隐患"——核实 `_llm_batch_rescore.py` 是否已用 sorted glob 合并（12 例挽回记录不再被覆盖）；已修→确认+测试，未修→补
2. **G6 scrub 备案入 KB**：G6（死亡词典 scrub）当前状态/位置记录进 KB §4.11 或合适节（含测试覆盖点）
3. **as_of_year 备案入 KB**：R5 遗留的 now() 锚（跨年翻档 T0 已证判定域零翻档）——as_of_year 可注入方案记录入 KB（维护项）
4. **子夜带备案入 KB**：T0 发现的子夜 ±1 分钟日柱敏感带（历法固有边界两派自洽）——备案入 KB
5. KB §9 残留总账同步（D1-D4 已修的条目清理 + D5 记录）

## 红线
- 引擎零改动（纯工具/文档）
- 备案内容必须与实测一致（不估）

## 验证
1. pytest 全绿（确认无意外）
2. grep 抽查 KB 新备案条目存在

## 汇报（200 字内）
rescore 确认/修复 + 三备案落位 + KB §9 同步 + pytest
