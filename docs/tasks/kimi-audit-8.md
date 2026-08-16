# Kimi 任务：全模块复审 · 批8 杂项层（神煞/十排歌/宫身/功废/宫门五物）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + 对照纪律）+ `/root/metaphysics/docs/knowledge-base.md`
2. **参考前批归档**：`kimi-audit-7-zhiye-2026-08.md`（失效模式：docstring 冠名引用≠实现合书义；知识库勘误 11 条格式；测试覆盖裸面——29 P0 无一哨兵）
3. 本批对象：`mangpai/objective/` 的 shensha/shenshu/shipaige/gongshen/gongfei/gongmen_wuzhi
4. 对照源：**原著优先**——`mangpai/docs/duan-books/*.txt`（神煞章/十排歌/宫身/功神废神/宫门五物）+ `mangpai/docs/zhengminsheng-shipaige-fragments.md`（十排歌碎片），知识库§4 仅定位索引
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：shensha（神煞）/ shenshu（十排歌数量诀）/ shipaige（十排歌断语）/ gongshen（宫身）/ gongfei（功神废神）/ gongmen_wuzhi（宫门五物）
2. **对照原著原文**（行号引用），逐函数检查：
   - 神煞定义（天乙/桃花/驿马/羊刃/空亡等）与书是否一致（重点：桃花条件——批7 发现岳飞被桃花栈驱动成 performer）
   - 十排歌数量诀（一财是财/二财是妾…）与郑民生碎片/书是否一致
   - 宫身（十二宫/宫位）与书是否一致
   - 功神废神（classify_gongshen——注意与 gongshen.py 同音异义刻意共存，勿混）与书是否一致
   - 宫门五物与书是否一致
   - 传导验证：神煞（桃花/驿马）在 zhiye/hunyin 的消费正确性
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "shensha or shenshu or shipaige or gongshen or gongfei or gongmen"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘 + 知识库勘误节
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-8-zashen-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条（含桃花/驿马消费传导）
