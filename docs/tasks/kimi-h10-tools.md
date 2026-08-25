# Kimi 任务：代码卫生审查 H10 · 剩余边角批（output 批跑脚本 + scripts + foundation 深审 + docs 脚本类）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划 + H1-H9 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×105——本批**重点查同型残留**：裸 except/原子写/假 green/死脚本）+ 收工终态
2. 本批 = **代码卫生 H10 · 工具脚本收尾批**（只审不改；纯本地零 API）
3. 汇报 300 字内

## 审查对象
**output/ 批跑脚本**（19 个，H7 已梳理在用状态——本批审实现质量）：_llm_batch_trainset.py / _llm_batch_retry.py / _llm_batch_analyze.py / _n2_analyze.py / _n2_calibrate.py / _n2_eval.py / _n2_sample.py / _t3_eval.py / _w4_sample.py / _w5_crosscheck.py / _v3_calibrate.py 等
**scripts/**：build_book_index.py（H7 已审行号正确——补审实现细节）
**foundation/ 深审**：foundation/ 全部（H8 首审发现 __all__ 遗漏 + dataclass 序列化——本批深挖）

## 审查维度（同前七维）
1. 重复逻辑（_n2_* 系列与 _t3_eval 的评审/校准逻辑重复？_llm_batch_* 系列的批跑框架重复？）
2. 复杂度（analyze/calibrate 主流程）
3. 异常处理一致性（**裸 except/静默失败——批跑脚本的容错**：retry 逻辑的异常面）
4. 死代码（H7 归档清单之外的残留；analyze 默认参数问题——迭代 3 的 40.21% 假象教训）
5. 隐藏边界假设（硬编码路径/output 目录名/seed）
6. import 卫生
7. foundation 深审：实现质量（H8 已标记 __all__/dataclass——补查其他）

## 重点（本批特有）
- **批跑脚本的可信度**：分析脚本的统计逻辑（_n2_analyze 统计口径 bug 教训——H9 后复查还有没有同类"统计与事实不符"的隐患）
- **脚本复用/合并评估**：_n2_* 与 _t3_eval 高度相似——是否该合并成统一评测框架（供 H 修复批参考）
- **foundation 完整性**：分层铁律最底层的实现卫生（面向未来跨流派扩展的地基）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H10 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API

## 汇报（300 字内）
批跑脚本可信度（统计口径隐患/复用评估）+ foundation 深审 + P0/P1/P2 统计 + 高价值亮点
