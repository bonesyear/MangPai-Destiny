# Kimi 任务：通盘审查 R1 · 接口契约（最重批）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（R1 定位：7 条已知接缝）+ `/root/metaphysics/docs/knowledge-base.md`
2. 本批=**接口契约审查**（只核不修，发现问题记录 P0/P1/P2 + 修复建议）
3. 汇报 300 字内

## 任务：7 条已知接缝逐条核验
1. **zeishen 滤 auxiliary 三消费方**（F5 改动）：gongliang 三通道（无制采纳/bao 门/不净覆写）+ xiangfa_ops + caiming 两处豁免——F5 后消费方是否与新的 zb 语义一致（还有没有依赖旧「净」语义的死角）
2. **shensha day 键**（F13 改动）：zhiye/hunyin/zaihoo 消费 shensha 输出时是否全部按 day-ref 语义（有没有残留 year-ref 消费点）；day_ref 子键读者确认
3. **grade_map 收书**（F12 改动）：guanming grade 输出与下游（narrative 官阶叙述/payload）是否一致；_RANK_GRADE 与 grade_map 口径差（F6 备案项）现状
4. **起运岁截断**（F3 改动）：liunian/jiaoyun int() 截断联动是否已完全一致（有没有残留实岁小数消费点）
5. **engine 传 age**（F10 改动）：infer_comprehensive_yingqi 的 age 参数全链路（engine→yingqi_subj）一致
6. **zaihuo A1 切片**（F14 改动）：engine:592 全量 yunfan→A1 切片后，zaihuo 消费的 yunfan 数据是否完整（A1 切片含哪些字段）
7. **gongmen 弃用残留**（F18 改动）：narrative _gongmen_wuzhi_line 通道切断后，还有没有其它模块消费 gongmen_wuzhi 输出（engine 键因 selectors 保护链保留——确认无泄漏）

## 方法
- 每条第：读消费方源码（grep 引用点）→ 读生产方源码（F 批改动处）→ 实跑探针（diag_case 或直接函数调用）→ 判定一致/漂移
- 漂移的：记录 P0（进 payload）/P1（模块间）/P2（记录） + 修复建议

## 产出
1. 7 条接缝核验表（每条：生产方语义/消费方语义/探针结果/判定）
2. 问题清单（P0/P1/P2 + 修复建议）
3. 汇报 300 字内
