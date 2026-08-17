# Kimi 任务：全模块复审 · 批10 主观层（叙事/流派/编排/payload）——收官批

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-audit-plan.md`（总纲 + 对照纪律）+ `/root/metaphysics/docs/knowledge-base.md`（§0 分层铁律/§8 工具链）
2. **参考前批归档**（失效模式全集）：批7（docstring 冠名≠实现）、批8（死数据/配置断路：桃花 day_ref 全库无读者、shensha_reference 0 处传 day）、批9（chuangong 伪标置信度高/测试锁自造 spec/全字段零消费）
3. 本批对象：`mangpai/subjective/` 的 narrative/schools + `mangpai/engine.py` 编排 + payload 组装
4. 对照源：**原著优先**——段氏断语风格（duan-books/*.txt 口语断例）+ SOUL.md 输出流程 + 知识库§0/§8
5. 只审计不改码；问题全列不筛选；测试只跑不修

## 任务
1. 逐文件读源码：narrative（叙述层）/ schools（流派选择器）/ engine.py（编排）/ payload 组装（主观层 payload 裁剪/组装）
2. **对照检查**：
   - narrative 的断语模板与段氏口语风格是否一致（是否有背离书义的固定句式）
   - schools selectors 的流派选择逻辑是否正确（35 键特征抽取）
   - engine.py 编排：各模块调用链是否正确（**重点：批8 发现 zaihuo 是全引擎唯一收全量 yunfan 的模块 engine.py:588；批8 gongmen_wuzhi 实现未接入 zhiye**；批9 死数据模块是否被编排误用）
   - payload 组装：传给 narrative/LLM 的特征是否完整、是否泄漏敏感字段（shouyuan 红线）
   - **死数据/未接入/伪标模块审计**：把前 9 批发现的「死字段/零消费/伪标」汇总成一个清单（哪些模块的字段实际无人消费）
3. 跑相关测试：`python3 -m pytest mangpai/tests/ -q -k "narrative or school or engine or payload or subjective"` 记录现状
4. 输出问题清单（全列不筛选）：P0 算法偏离书义（带原著行号）/ P1 缺书锚或口径疑点 / P2 注释或边缘 + 知识库勘误节 + **死数据总清单**
5. 写归档 `/root/.claude/projects/-root-metaphysics/memory/kimi-audit-10-subjective-2026-08.md` + 300 字摘要

## 汇报（300 字内）
逐文件检查结论 + 问题数（P0/P1/P2）+ 测试现状 + 死数据总清单概览 + 审计收官结论
