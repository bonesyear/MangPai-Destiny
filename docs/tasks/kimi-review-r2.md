# Kimi 任务：通盘审查 R2 · 双轨/死数据复生

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（R2 定位）+ `/root/metaphysics/docs/knowledge-base.md`（§4.11/§4.12、F1 死数据清理记录）
2. **读 F1 归档**（19 项死数据清理明细）+ R1/R5 结果（P0 换象/P1 神煞/P2 记录——其中 xiangfa _shensha_by_pillar 不读子键、engine.py:230 注释过期、_auto_liunian_injected 未初始化是 R2 同型）
3. 本批=**双轨/死数据复生检查**（F1 清理后修复期（F2-F19）有没有产生新的）
4. 汇报 300 字内

## 任务
1. **双轨复检**：engine↔模块自算双轨（F1 记录：zihe/soil/virtual/wood/gongshen 各模块自算不读 engine 结果；F1 清理了部分）——F2-F19 修复后：
   - 还有哪些模块自算结果与 engine 结果并存且不一致？
   - 修复是否引入新双轨（如 F11 caiming/yongshen 消费的 zhengfan 是 engine 结果还是自算？）
2. **死数据复生**：F1 清理 19 项后，F2-F19 新增的字段/键有没有无人消费的（grep 写方 vs 读方）：
   - 新增输出键（如 F12 grade_map、F14 zaihuo_llm_view、F13 shensha 子键）——都有读者吗？
   - 修复中保留的旧键有没有变死（如 F5 后 wa 相关键）
3. **R1 P2 同型项深挖**：xiangfa _shensha_by_pillar 不读子键、_auto_liunian_injected 未初始化、engine.py:230 注释过期——确认现状 + 同型扫描（有没有其它"不读子键/未初始化/过期注释"）
4. 输出：双轨清单（模块/engine 值/自算值/差异）+ 死数据清单（键/写方/读方）+ 问题分级（P0/P1/P2）

## 方法
- grep 写方/读方交叉验证 + 实跑探针（构造盘对比 engine 结果 vs 模块自算）
- 只核不修

## 产出
1. 双轨清单 + 死数据清单
2. 问题清单（P0/P1/P2 + 修复建议）
3. 汇报 300 字内
