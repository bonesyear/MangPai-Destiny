# Kimi 任务：全模块复审 · 批7 判定层B（职业/婚姻/灾祸/学历/六亲）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + 对照纪律）+ `/root/metaphysics/docs/knowledge-base.md`
2. **参考前批归档**：`kimi-audit-6-caiming-2026-08.md`（P0 风格：ans12 必损真根因=过河拆桥不验财生官相连；guanming 制用双向缺反向；yongshen 例6/7；知识库勘误 8 条格式）
3. 本批对象：`mangpai/subjective/` 的 zhiye/hunyin/zaihuo/xueli/liuqin
4. 对照源：**原著优先**——`mangpai/docs/duan-books/*.txt`（职业章/婚姻章/灾祸章/学历/六亲），知识库§3/§4 仅定位索引
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐模块读源码：zhiye（职业桶判定）/ hunyin（婚姻）/ zaihuo（灾祸）/ xueli（学历）/ liuqin（六亲）
2. **对照原著原文**（行号引用），逐函数检查：
   - 职业桶（merchant/teacher/lawyer/doctor/military/performer/accountant/laborer 等）判定与书例是否一致（重点锚：merchant 15+ ✅、罗斯切尔德、乔布斯、无桃花通道、军警 C 备案簇）
   - 婚姻（差/好/平 + 配偶星宫）与书是否一致（重点：桃花条件、配偶星、婚期断言）
   - 灾祸（凶向/破财/牢狱衔接）与书是否一致（注意批5 laoyu 死条款与 zaihuo 的衔接）
   - 学历（学历断语）与书是否一致
   - 六亲（父母/兄弟/子女）与书是否一致
   - **传导验证**：批4/5 的 P0（zhengfan 方向、laoyu 死条款）在婚姻/灾祸上的影响面
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "zhiye or hunyin or zaihuo or xueli or liuqin"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘 + 知识库勘误节
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-7-zhiye-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐模块检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 代表性发现 2-3 条（含传导影响面）
