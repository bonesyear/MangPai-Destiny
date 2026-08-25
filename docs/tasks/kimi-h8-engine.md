# Kimi 任务：代码卫生审查 H8 · 剩余模块收尾批（objective 边角 + subjective 边角 + engine 编排）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划 + H1-H7 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×102——本批**重点查同型残留**：裸 except/写回原子性/假 green/死 shim）+ 收工终态
2. 本批 = **代码卫生 H8 · 引擎编排 + 边角批**（只审不改；纯本地零 API）
3. 汇报 300 字内

## 审查对象
**引擎编排（核心）**：engine.py（顶层编排——H1 没覆盖的顶层入口）
**objective 边角**：__init__.py / 顶层 verify_mangpai.py（若 H7 已审则跳过）
**subjective 边角**：__init__.py / schools.py 的 selectors 机制（H4 已审实现质量——本批补查 selectors 注册/保护链机制本身的健康度）
**foundation 层**：foundation/（学派中性基础——分层铁律最底层，从未审过实现质量）

## 审查维度（同前七维）
1. 重复逻辑（engine 与 subjective 的接线重复？foundation 与 objective 的工具重复？）
2. 复杂度（engine.py 主流程 compute_all 长度/分支）
3. 命名
4. 异常处理一致性（**engine 编排层的异常面**：_safe_compute 模式——每个模块调用是否安全兜底/吞异常）
5. 死代码（engine result 键无消费者？foundation 死工具？）
6. 隐藏边界假设（engine 对模块返回结构的隐含依赖——模块改键 engine 会不会崩）
7. import 卫生（engine 全量导入面/循环导入）

## 重点（本批特有）
- **engine._safe_compute 审计**：每个模块的 _safe_compute 包裹——哪些模块的异常被吞（静默降级）、哪些正确传导——**编排层吞异常 = 最危险的静默失败**（模块错了 engine 不知道）
- **result 键消费者核查**：engine 产出的全部键 → build_payload selectors → narrative/formatter 的消费链完整性（死键/无读者键）
- **foundation 层**：从未审过的层——分层铁律最底层的实现质量

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H8 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API
- engine 是编排层——审查只评实现质量不评判定（Spec 轴不重复）

## 汇报（300 字内）
engine 编排面（_safe_compute 吞异常审计/result 键消费者）+ foundation 首审 + P0/P1/P2 统计 + 同型残留
