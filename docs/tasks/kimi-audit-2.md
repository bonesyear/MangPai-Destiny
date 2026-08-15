# Kimi 任务：全模块复审 · 批2 做功层

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲）+ `/root/metaphysics/docs/knowledge-base.md`（§4.1 做功/贼捕/功量书锚、§5.1）
2. **参考批1归档**：`/root/.claude/projects/-root-metaphysics/memory/kimi-audit-1-foundation-2026-08.md`（问题分级风格）
3. 本批对象：**做功层**——`mangpai/objective/` 的 zuogong_detect/zuogong_confirm/tiyong/binzhu/zeishen_bushen
4. 对照源：`mangpai/docs/duan-books/duan-shi-lixiangxue.txt`（理象学）+ `duan-mangpai-zhonggaoji.txt`（中高级）+ 知识库§4.1/§5.1（李嘉诚/保尔森/乾隆/克林顿/蒋介石/岳飞等书锚）
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：
   - zuogong_detect（做功检测：制/化/合/墓/冲等功象识别）
   - zuogong_confirm（做功确认：主宾体用、功的成立条件）
   - tiyong（体用：日主为体、他神为用）
   - binzhu（宾主：主位日时/宾位年月）
   - zeishen_bushen（贼神捕神：制贼之神、捕贼）
2. 对照理象学/中高级 + 知识库书锚，逐函数检查：
   - 做功类型的分类与段氏「制/化/合/墓」体系是否一致
   - 体用判定（日主/他神）是否符合段氏体用论
   - 宾主位划分（主位日时/宾位年月）是否符合
   - 贼神捕神的定义与判定是否符合（贼神=做功之神/捕神=制贼之神）
   - 关键书锚例（李嘉诚同制四点/乾隆金字塔/蒋介石入墓包局）能否解释
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "zuogong or tiyong or binzhu or zeishen"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义 / P1 缺书锚或口径疑点 / P2 注释或边缘
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-2-zuogong-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条
