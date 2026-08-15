# Kimi 任务：全模块复审 · 批1 基础语法层

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（审计总纲：批次划分/步骤/问题分级 P0/P1/P2）和 `/root/metaphysics/docs/knowledge-base.md`（§1 语法层相关）
2. 本批对象：**基础语法层**——`mangpai/objective/` 的 constants/canggan/changsheng/nayin/zihe/he_types
3. 对照源：`mangpai/docs/yuanhaiziping/yuanhai-mobi.txt`（渊海子平）+ `mangpai/docs/ziping-zhenquan-pingzhu.txt`（真诠）+ 知识库§1
4. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码（constants 数据表/canggan 藏干/changsheng 十二长生/nayin 纳音/zihe 自合/he_types 合类型）
2. 对照子平经典 + 知识库，逐函数/逐表检查：
   - 干支五行/十神定义是否符合经典
   - 藏干规则（本气/中气/余气）是否符合经典
   - 十二长生表（阳生阴死/阴阳顺逆）是否符合经典
   - 纳音六十甲子是否正确
   - 合的类型（六合/三合/半合/暗合/争合/妒合等）分类是否正确
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "canggan or changsheng or nayin or zihe or he_type"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离经典 / P1 缺书锚或口径疑点 / P2 注释或边缘
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-1-foundation-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2 各多少）+ 测试现状 + 代表性发现 2-3 条
