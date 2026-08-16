# Kimi 任务：全模块复审 · 批4 命局正反层

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲）+ `/root/metaphysics/docs/knowledge-base.md`（§4 正反局/岁运/应期、§5 书锚）
2. **参考前批归档**（问题分级风格 + 传导线索）：`kimi-audit-2-zuogong-2026-08.md`（P0 蒋介石：zeishen 未滤 auxiliary）+ `kimi-audit-3-gongliang-2026-08.md`（P0×6：阎锡山自我撤销校准/批2传导/zhi_jing 同帧矛盾）
3. 本批对象：`mangpai/objective/` 的 zhengfan/yunfan/yingqi/yingqi_subj
4. 对照源：`mangpai/docs/duan-books/`（正反局章/岁运章）+ `mangpai/docs/duan-mangpai-zhonggao-zhengfan-ch1.md`（正反局专项）+ 知识库§4
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：
   - zhengfan（正反局：五行相背/气势判定/局定）
   - yunfan（岁运反局：运反触发/冲穿刑/伏吟/杀临攻身）
   - yingqi + yingqi_subj（应期：冲/合/刑/墓应期 + 寿元四机制）
2. 对照书，逐函数检查：
   - 正反局判定（五行相背条款/成势/局定）与段氏正反局体系是否一致（重点：**批2 的 P0 曾误伤过反局判定——K2-4 冲合矛盾**）
   - 岁运反局触发条件（运支冲/穿/伏吟）与书是否一致
   - 应期语义（liunian 冲五种/合四种）与书诀是否一致（**近期刚建断言集，注意 25 条断言的书锚**）
   - 寿元四机制（破禄/禄到位/寿元星被坏/原局字到位）与书锚是否一致
   - 关键锚：yx-巨富丑运丙子（书明文入狱反局）、破财工程酉、医师卯运、b67 杀临攻身、zj 伏吟干被克坏
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "zhengfan or yunfan or yingqi"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义 / P1 缺书锚或口径疑点 / P2 注释或边缘
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-4-zhengfan-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条
