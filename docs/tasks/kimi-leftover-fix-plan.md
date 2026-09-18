# Kimi 任务：遗留项维修方案（规划合理批次，纯规划不执行）

## ⚠️ 执行指引
- 纯规划：方案写 `/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-fix-plan-20260918.md`，stdout 400 字内摘要
- **只出方案不动手**
- **先读**：你的评估报告（`/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-assessment-20260918.md`——你刚出的判断）+ `docs/remaining-tasks-20260917.md`（收工记录）+ `docs/tasks/codehygiene-fix-backlog.md`（相关节）+ `docs/tasks/h-fix-workplan-v2-20260917.md`（H-fix 序列的批次设计与纪律模板——本方案应沿用同样标准）

## 规划对象（评估确认的"值得动"项）
1. **B1** xiangfa_ops set 排序化（LLM 批跑输出不可复现——M1 模式漏网）
2. **B2** `engine.py:578`（漂移后行号，请重新定位）liunian_data truthy 非 dict 入口守卫
3. **B3** `engine.__init__` 未初始化 `_auto_liunian_injected`（同实例复调状态泄漏）
4. **C1** `zaihuo.py`（约 :322）正官误标「七杀」label
5. **B4** `_scan_shengyong` 嵌套冗余 / `_prepare_inputs` 死代码块删除
6. **C2** `formatter.DISCLAIMER` 与 `llm_channel._DISCLAIMER_LINE` 文本统一
7. **C3** `test_snapshot_hygiene.py`（快照 meta 链自动校验）新建
8. **D** 真实凭证冒烟（上线闸执行项——单独说明归属与前置条件）

## 规划要求
### 1. 批次划分（核心）
- 按**依赖拓扑 + 风险等级 + 成本摊薄**划批（注意你的评估建议：L1 应与下个引擎批捆绑以摊薄六件套+换基线成本——请明确这个建议如何落地）
- 候选方案仅供参考，你可自行判断更优结构（如：L1a 真 bug 三件（B1/B2/B3）→ L1b 文本/清理四件（C1/B4/C2/C3）→ 或合并为一批）
- **每批粒度可控**（≤30 文件、单批会话规模合理）
- 说明**为何这样分批**（依赖关系/风险隔离/成本考虑）

### 2. 每批内容（沿用 H-fix 格式）
- 批次名 / 对象清单（含**重新定位的行号**）/ 具体修法（每项怎么做）/ 关键纪律（红线）/ 验证方式（DoD：哨兵先红后绿、六件套、正常路径逐字节不变等）/ 工作量估计 / 风险

### 3. 特别说明
- **B1 排序化的修法**：是"消费方排序"还是"源侧有序结构"？哪个更彻底？（你的评估提到 detect_relations 返回含 set 是同类问题——一并考虑）
- **B3 状态泄漏的影响面**：同实例复调在什么场景发生（批跑？飞书长驻进程？）——影响面决定优先级
- **C1 label 修正的输出影响**：会改 payload desc 文本 → 需说明"换基线"的必要性与范围
- **D 真实凭证冒烟**：归属（上线 checklist 执行项 vs 修复批）+ 前置条件（需什么凭证）+ 建议时机

### 4. 6 项"明示关闭"的收尾动作
- 建议如何落地（在 backlog/收工记录里标记"已关闭（理由）"）+ 是否需要一个专门的文档批来做

### 5. 与下个引擎批的捆绑建议（若采纳）
- 具体怎么捆绑（前置？同批？）+ 若引擎批短期不启动，L1 是否该独立先做（给条件判断）

## 产出
- 批次规划（每批明细）+ 捆绑方案 + 关闭项收尾 + 优先级与时机建议
- stdout 400 字内摘要

## 红线
- 只规划不执行
- 不调外部 API
