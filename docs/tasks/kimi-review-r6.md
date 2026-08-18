# Kimi 任务：通盘审查 R6 · 影响面综合 + go/no-go（收官批）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（R6 定位）+ 本会话 R0-R5 结果（基线可信/P0 换象门/P1 神煞×3/3 block 2 go/P0 baseline 指针已修/P1 数字过期）
2. 本批=**综合判断**（把 R0-R5 发现汇总成 go/no-go 结论 + 修复排期建议）
3. 只出不改（R6 是判断批，不碰代码）
4. 汇报 300 字内

## 任务
1. **汇总 R0-R5 问题清单**（去重/分级）：
   - R0：无（F8 CHANGELOG 已补）
   - R1：P0 换象门 raw wa（xiangfa_ops:1030-1070，11/509 locked 断语进 payload）/ P1 zaihoo×2+laoyu 神煞 year-ref 丢失 / P1 calib 不传 age / P2×6
   - R5：block×3（siwang 键外泄漏 shipaige/liuqin/xiangfa_ops、换象 P0、gongmen_wuzhi 98.8% 恒真进 payload）/ go×2（39 键/age 备注）
   - R2：P0 换象（存量）/ P1 caiming zeishen 不传 zg→wa=空 / P2×5 / P3×4
   - R3：无 C 级，P2 行号微瑕（数处 ±1~18）
   - R4：P0 baseline 指针（已修）/ P1×7 数字过期 / P2×2 baseline67/famous 悬挂
2. **修复排期建议**（承接各批修复建议）：
   - 分几批修？每批内容/顺序/依赖
   - 修复主线=zeishen 单源化（R2 建议：一次根治 P0 换象 + P1 caiming wa=空）？还是按模块分？
   - LLM 通路 4 个 block 的解除顺序（siwang 键外泄漏→死亡词典 scrub；换象→单源化；gongmen→selectors 摘除）
   - 文档批（R4 P1×7 数字过期 + R3 P2 行号微瑕 + R2 P2）何时修
3. **go/no-go 结论**：
   - LLM 通路 MVP 在修复后是否可启动（明确：修完哪些 block 才能 go）
   - 引擎本身（不接 LLM）是否已达标可交付
4. 输出：问题总表（去重后 P0/P1/P2 计数）+ 修复批次建议（每批内容/预期/依赖）+ go/no-go 结论

## 产出
1. 去重问题总表
2. 修复批次建议（含 LLM block 解除顺序）
3. go/no-go 结论（MVP 前置条件清单）
4. 汇报 300 字内
