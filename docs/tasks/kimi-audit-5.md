# Kimi 任务：全模块复审 · 批5 岁运层

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + **对照纪律批5起强制**：原著优先/挑战知识库/备案不豁免/每条P0P1带原著行号）+ `/root/metaphysics/docs/knowledge-base.md`
2. **参考前批归档**：`kimi-audit-4-zhengfan-2026-08.md`（yunfan 的 P0：资本运营酉运 T3 伏吟干泛化/zj 丙戌运 T1 冲无开库豁免/联动三刑无补全闸；laoyu.py:425 签名错配）
3. 本批对象：`mangpai/objective/` 的 dayun/liunian/jiaoyun/laoyu
4. 对照源：**原著优先**——`mangpai/docs/duan-books/*.txt`（大运/流年/交运/牢狱章），知识库§4 仅定位索引
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：dayun（大运分析）/ liunian（流年分析）/ jiaoyun（交运时间）/ laoyu（牢狱）
2. **对照原著原文**（行号引用），逐函数检查：
   - 大运起法/排法/吉凶判断与书是否一致
   - 流年应期（冲五种/合四种/刑/墓）与书诀是否一致（**近期 25 条断言集的书锚，批4 发现 he4 书目张冠——重点复核**）
   - 交运时间计算（节气/起运）与书是否一致
   - 牢狱条款（laoyu.py:425 签名错配导致上线即死——本批重点验证）
   - 关键锚：巨富丑运丙子（入狱）、破财工程酉、医师卯运、b67 杀临攻身
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "dayun or liunian or jiaoyun or laoyu"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-5-suiyun-2026-08.md` + 300 字摘要（含「知识库勘误」节若有）

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条（含 laoyu 签名错配验证结果）
