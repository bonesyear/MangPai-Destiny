# Kimi 任务：H-fix-8 · 文档/基线同步批（H-fix 序列收尾）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H9 节**（README 23 例过期 / MANUAL 4 例未入 merged+candidates / 14 份快照无引用 + 缺 LATEST 基线指针）+ **H10 节**（output 脚本 sys.path.insert 备案留 H-fix-8）+ **H-fix-4a/4c/5/7 节**（本批需同步的数字与新状态）
2. 本批 = **H-fix-8（🟢 文档/基线同步——H-fix 序列最后一批）**
3. 汇报 350 字内

## 任务 A：README/文档数字同步（现存过期项）
实测后同步：
1. **验证用例数**：README 写 860 → 实测当前（预期 1059+1xf）
2. **模块数**：README 写 58 → 实测（H-fix-4a 删了 advanced/chuangong 两模块，预期 56；按各层重新数）
3. **各层模块数**（架构表）：Objective / Subjective / Foundation 的数字
4. **架构描述**：H-fix 期间新增模块（`objective/shishen.py`、`objective/_relation_utils.py`、`subjective/utils.py`）是否需要写入架构说明
5. **README 23 例过期**（H9 P1）：README 里写 trainset 23 例 → 实测 294 例
6. **MANUAL 4 例未入 merged/candidates**（H9 P1）：补入数据文件或标注说明

## 任务 B：快照基线机制（H9 P1）
1. **LATEST 基线指针**：`snapshots/` 缺一个"当前基线"指针文件（如 `snapshots/LATEST` 或 `_baseline.json`）——加一个显式指针（指向最新基线快照），并让脚本可读（`blind_eval --baseline` 支持）
2. **14 份无引用快照**：归档到 `snapshots/archive/`（保留历史，不删——快照链是审计证据）
3. **快照链文档**：在 KB 或 `snapshots/README.md` 里记录快照链（哪个是基线、哪些是历史、各批对应的 commit/tag）——**H-fix 全序列快照需补录**（hfix1~hfix7 + prehfix）

## 任务 C：收尾同步
1. **sys.path.insert 备案**（H10）：output 脚本的手动路径改评估结论——若安装化成本高，**写明备案理由**（output 非包、批跑工具）
2. **KB 同步**：H-fix 全序列（1~8）的终态——包括：裸 except 残留数、模块数变化、新增工具脚本（check_typing_imports/check_layering）、契约测试、原子写机制
3. **CHANGELOG**：H-fix-1~8 各条（若前面批次已写则核对补漏）
4. **收工记录**：`docs/remaining-tasks-20260917.md`（新建）——H-fix 序列终态 + 剩余待议项清单（backlog 里的"未删待议"/"待议问题"汇总）

## 验证（DoD）
- [ ] README/文档数字与实测一致（逐项核对）
- [ ] 快照 LATEST 指针生效（`blind_eval --baseline` 可读取）
- [ ] 快照链文档完整（H-fix 全序列可见）
- [ ] KB/CHANGELOG/收工记录三件套同步
- [ ] 六件套全量：pytest 全绿 + verify 全项 + blind 零翻转（vs `snapshots/20260918_hfix7.json`）
- [ ] `scripts/check_layering.py` + `scripts/check_typing_imports.py` 仍通过

## 产出
- 文档同步 + 快照指针 + 收尾三件套
- 汇报 350 字内：数字同步项 + 快照机制 + 三件套 + 六件套结果

## 红线
- 纯文档/基建改动（不动引擎/主观层逻辑）
- 不调外部 API
