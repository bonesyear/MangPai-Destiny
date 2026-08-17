# Kimi 任务：全模块复审 · 批9 辅助层（基础计算/干支象/身体/串宫/暗合等）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + 对照纪律）+ `/root/metaphysics/docs/knowledge-base.md`
2. **参考前批归档**：`kimi-audit-8-zashen-2026-08.md`（失效模式：docstring 冠名≠实现/死数据/配置断路；shensha_reference 配置 0 处传 'day'）
3. 本批对象：`mangpai/objective/` 的 bazi_calc/advanced/biqi/body_parts/chuangong/soil_type/virtual_solid/wood_type/anhe
4. 对照源：**原著优先**——`mangpai/docs/duan-books/*.txt` + `mangpai/docs/yuanhaiziping/yuanhai-mobi.txt`（基础层），知识库§1 仅定位索引
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：
   - bazi_calc（八字计算：大运起法/起运岁——批5 发现交运晚一年与此相关，重点复核）
   - advanced（进阶计算）
   - biqi（比气）
   - body_parts（身体部位）
   - chuangong（串宫）
   - soil_type/virtual_solid/wood_type（土型/虚实/木型）
   - anhe（暗合——批1 发现暗合表多「子巳」P1，复核）
2. **对照原著原文**（行号引用），逐函数检查：
   - 大运起法/起运岁（实岁小数 vs 书整数虚岁——批5 交运晚一年的上游）与书是否一致
   - 暗合定义与书是否一致（批1 线索：段氏仅寅丑/午亥/卯申三对）
   - 干支象/身体部位/土型木型与书是否一致
   - 串宫（十二神串宫压运）与书是否一致
   - 各模块在引擎消费链中的角色（死数据/未接入检测——批8 发现桃花 day_ref 死数据同型）
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "bazi or advanced or biqi or body or chuangong or soil or virtual or wood or anhe"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘 + 知识库勘误节
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-9-fuzhu-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条（含死数据/未接入检测）
