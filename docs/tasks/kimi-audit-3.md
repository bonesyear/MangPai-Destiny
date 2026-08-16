# Kimi 任务：全模块复审 · 批3 功量象法层

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲）+ `/root/metaphysics/docs/knowledge-base.md`（§4 功量/墓库、§5.1 书锚：李嘉诚同制四点/乾隆金字塔/蒋介石入墓包局/奥纳西斯制库/森田健否决锚）
2. **参考前批归档**：`kimi-audit-1-foundation-2026-08.md`（P1 级墓库口径发现：TOMB_MAP 缺戌=土墓）+ `kimi-audit-2-zuogong-2026-08.md`（P0 蒋介石判反：target_wx_set 未滤 auxiliary；work_level 已被 gongliang 取代备案）
3. 本批对象：`mangpai/objective/` 的 gongliang/muku/xiangfa/xiangfa_ops
4. 对照源：`mangpai/docs/duan-books/`（理象学功量章、中级墓库章、高级）+ 知识库§4/§5.1
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：
   - gongliang（功量：基阶/加层/封顶/金字塔门/净制）
   - muku（墓库：入墓/冲刑开库/闭库/库源）
   - xiangfa + xiangfa_ops（象法：取象/做功象/关系象）
2. 对照书锚，逐函数检查：
   - 功量基阶/加层（原神同制两层/制库两层/入墓+1/包局+1/连墓加层）与书是否一致
   - 金字塔门（乾隆链）是否合理
   - 墓库规则（入墓条件/冲刑则动/库源）与中级章是否一致（**注意批1 的 TOMB_MAP 戌=土墓 P1 与此相关**）
   - 象法取象（干象/支象/合冲象）与理象学是否一致
   - 关键锚：李嘉诚（连墓加层月令入墓于辰）、乾隆（L4 金字塔）、奥纳西斯（制库得财）、森田健（否决锚）能否解释
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "gongliang or muku or xiangfa"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义 / P1 缺书锚或口径疑点 / P2 注释或边缘
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-3-gongliang-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条
