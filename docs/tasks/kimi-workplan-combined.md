# Kimi 任务：统一动工方案（第五轮修批 F1-F3 + 七维叙述 N1-N3 结合）

## ⚠️ 执行指引
- 纯规划：方案写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-workplan-2026-08-21.md`，stdout 300 字摘要
- **只出方案不动工**
- **先读**：V5 报告（`docs/kimi-review5-v5-final-20260821.md` 的修批排期 F1/F2/F3 + 备案项 + F-V3-1）+ 待修清单（`docs/tasks/review5-fix-backlog.md` 已升级排期）+ 七维计划（`docs/tasks/kimi-narrative5d-plan.md` 的 N1/N2/N3）

## 两块工作（结合成一个统一动工方案）
### A. 统一修批（第五轮发现，V5 已排 F1-F3）
- **F1 发布闸**：P0 免责声明 + P1×5（Tuple import/lark_md 三符/丁眼锚注/死亡词 mark 升级 reject/外发告知）——小 diff 一次六件套
- **F2 文档清零**：xiangmao 丁锚注（或归 F1？）+ 4179 行号 + 同构措辞 + docstring 41 + KB/CHANGELOG/收工 五轮入档——纯文档零行为
- **F3 健壮性 P2 可选**：bot isinstance + 裸 repr + max_tokens 8192 + _self_check 人民币口径 + L2 误报窗——可并 F1 或单列
- 备案不排期：client.send/断网双发/非文本忽略/compute 线程上限/judge prompt/@bot 前缀
- F-V3-1：unemployed 锚定（可选，需 S1 复测）

### B. 七维叙述新增（qianyi/xiangmao 进五维，N1-N3 已规划）
- N1 代码批：L2 两红线（迁移禁出国/相貌禁美丑）+ 七维 schema + 锚定行 + 哨兵（含 V1 遗留 P1/P2 注释清零）
- N2 复测：294 例谷段两轮（新维加严：红线违规 0/翻转 0，≤$12）
- N3 收档：heldout 215 评估 + KB/CHANGELOG

## 请设计（结合方案）
1. **批次合并/编排**：F1-F3 与 N1-N3 怎么排（依赖/并行/合并）——例如：N1 的"V1 遗留注释清零"与 F2 重叠？F3 的 max_tokens 与 N2 复测相关？
2. **依赖拓扑**：完整动工顺序（谁先谁后、哪些可并行、哪些必须串行）
3. **每批内容/工作量/验证**（统一格式）
4. **发布闸位置**：P0/P1 清零后发布判定在哪一步（F1 后？N 系列前/后？——七维新增是否在发布前做？）
5. **配额/成本预估**（Kimi + DeepSeek 谷段）
6. **回退预案**（七维打不下→相貌降回特征层的触发条件）

## 输出（写归档，300 字摘要）
统一批次编排 + 依赖拓扑 + 发布闸位置 + 配额 + 回退预案
