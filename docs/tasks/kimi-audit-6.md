# Kimi 任务：全模块复审 · 批6 判定层A（财命/官命/用神/诀法）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + 对照纪律：原著优先/挑战知识库/备案不豁免/每条 P0/P1 带原著行号）+ `/root/metaphysics/docs/knowledge-base.md`
2. **参考前批归档**（风格 + 传导线索）：`kimi-audit-2-zuogong`（P0 蒋介石 zeishen 未滤 auxiliary）、`kimi-audit-3-gongliang`（P0 奥纳西斯 L2 vs 书 4 层、阎锡山）、`kimi-audit-4-zhengfan`（zhengfan 7 书例仅 2 命中）、`kimi-audit-5-suiyun`（断言集行号漂移、知识库勘误节格式）
3. 本批对象：`mangpai/subjective/` 的 caiming/guanming/yongshen/juefa
4. 对照源：**原著优先**——`mangpai/docs/duan-books/*.txt`（财命章/官命章/用神/诀法），知识库§3/§5 仅定位索引
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：caiming（财命判定）/ guanming（官命判定）/ yongshen（用神/身强身弱）/ juefa（诀法断语）
2. **对照原著原文**（行号引用），逐函数检查：
   - 财命档位（巨富/富/小康/平/贫/破财/凶）判定与书例是否一致（重点锚：李嘉诚净制巨富/保尔森/奥纳西斯制库/li002/li200 封顶富/ans12 必损/森田健否决）
   - 官命判定（G0-G7 收口 + veto 链）与书例是否一致（重点锚：famous 官命 10/10、克林顿/乾隆/朱元璋/慈禧/希特勒）
   - 用神/身强弱（从格/扶抑/化势）与书是否一致（重点：R1-R3 误判史、22期从格行运）
   - 诀法断语与十排歌/书诀是否一致
   - **传导验证**：批2/3 的 P0（zeishen auxiliary、奥纳西斯 L2）在财命/官命最终档位上的实际影响面
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "caiming or guanming or yongshen or juefa"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘 + 知识库勘误节
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-6-caiming-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条（含传导影响面）
