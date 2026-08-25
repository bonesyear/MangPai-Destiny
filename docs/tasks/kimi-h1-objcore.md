# Kimi 任务：代码卫生审查 H1 · objective 核心批（zuogong_detect/bazi_calc/dayun + 其余 objective）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（`/root/.claude/projects/-root-metaphysics/memory/kimi-codereview-plan-2026-08-25.md`：七维审查项——重复逻辑/复杂度/命名/异常处理一致性/死代码/隐藏边界假设/import 卫生；分级 P0 立即修/P1 必修/P2 技术债池）+ 收工终态
2. 本批 = **代码卫生 H1 · objective 核心批**（只审不改；纯本地零 API；≤30 文件）
3. 汇报 300 字内

## 审查对象（objective 核心 + 基础对象，按行数优先）
**核心批**：zuogong_detect.py（1122 行）/ bazi_calc.py（882）/ dayun.py（694）
**基础对象批**（同一批次内按组走）：shensha.py（427）/ jiaoyun.py（393）/ xiangfa.py（382）/ muku.py（324）/ body_parts.py（319）/ gongshen.py（311）+ 其余小模块（constants/advanced/anhe/binzhu/biqi/canggan/changsheng/gongfei/he_types/nayin/shenshu/soil_type/tiyong/virtual_solid/wood_type/yingqi/zihe）

## 审查维度（每模块逐项）
1. **重复逻辑**：跨模块重复（如多个模块各自实现同类判定——可提炼未提炼）/ 模块内重复分支
2. **复杂度**：函数过长（>80 行）/分支过深（嵌套>4）/圈复杂度异常
3. **命名**：误导性命名/与书理术语冲突/缩写不明
4. **异常处理一致性**：裸 except/未捕获 TypeError（Tuple 类——zuogong_detect:997 已修过，检查同类残留）/静默失败路径
5. **死代码**：未引用函数/死参数/死分支/冗余条件（历史遗留——G2 曾删过 shipaige 死函数，检查其他模块）
6. **隐藏边界假设**：硬编码/魔法数字/隐含依赖（如对输入格式的隐含假设）
7. **import 卫生**：未导入引用（延迟绑定风险）/循环导入/多余导入

## 产出（每批格式）
1. 问题表：`文件:行号 | 问题类型 | 严重级（P0/P1/P2）| 问题描述 | 修法建议`
2. P0/P1/P2 统计汇总
3. 汇报 300 字内

## 红线
- 只审不改（问题清单入 `docs/tasks/codehygiene-fix-backlog.md`——本批发现追加该文件）
- 纯本地零 API（不调 DeepSeek）
- 修法建议只写"怎么改"，不实际改

## 汇报（300 字内）
各模块审查结果 + P0/P1/P2 统计 + 高价值发现亮点（Tuple 类/崩溃面/死代码）
