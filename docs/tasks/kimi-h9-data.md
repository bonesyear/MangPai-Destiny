# Kimi 任务：代码卫生审查 H9 · 测试基建收尾批（heldout 数据文件 + trainset + calib YAML + 快照机制）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划 + H1-H8 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×105——本批**重点查同型残留**：裸 except/写回原子性/假 green）+ 收工终态
2. 本批 = **代码卫生 H9 · 数据/快照基建批**（只审不改；纯本地零 API）
3. 汇报 300 字内

## 审查对象
**数据文件**：heldout/cases.yaml（215 例）+ heldout/merged.json + heldout/candidates.json + heldout/review.txt + trainset/cases.yaml（294 例）+ calib_assertions.yaml（+ calib 目录结构）
**快照机制**：heldout/snapshots/ 目录（快照链 ~50 份）+ 快照读写逻辑（blind_eval 的 snapshot 部分——H7 已审脚本整体，本批审数据侧）

## 审查维度（数据/快照特有的）
1. **数据一致性**：
   - cases.yaml 与 merged.json/candidates.json 三方一致（同一命例在多个文件是否同步——**数据漂移**：改了一个忘了另一个）
   - calib_assertions.yaml 与 cases.yaml 的引用关系（calib 断言引用的 case 是否都在）
   - heldout/trainset 是否真的互斥（无重叠命例——评估污染红线）
2. **快照链健康度**：
   - snapshots/ 快照的命名/元数据（git_sha/rubric_version/note）一致性
   - 快照与当前代码的匹配（旧快照是否还被引用）
   - baseline 机制（最新基线指针？）
3. **数据卫生**：
   - 重复命例/重复 case id
   - 注释/书锚字段完整性（gold 标注的 source 锚）
   - YAML 语法/结构一致性（calib 正则改写脆弱的背景——H7 已标记）
4. **异常处理一致性**（数据加载路径的裸 except）
5. **死数据**（无人引用的数据文件/字段）

## 重点（本批特有）
- **评估污染检查**：heldout 215 与 trainset 294 是否真互斥（重叠=评估污染——红线）
- **数据漂移**：同一 case 的多文件版本是否一致（gold 修正 D1/E3 后有没有留旧版本）
- **快照引用完整性**：代码里引用的快照文件是否都存在（死引用）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H9 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API

## 汇报（300 字内）
数据一致性（三文件同步/互斥检查）+ 快照链健康 + 评估污染红线确认 + P0/P1/P2 统计
