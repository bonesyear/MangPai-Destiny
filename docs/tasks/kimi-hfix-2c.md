# Kimi 任务：H-fix-2c · 异常处理策略-诊断/验证脚本层（异常策略线收官）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H7 节**（验证基建：「假 green」2 处——`blind_eval.py:225` + `verify_layer3_checkpoint.py:51` 裸 except 吞引擎异常，可让 CI 误绿）+ **H6 节** + **H-fix-2a/2b 节**（分类模式）
2. 本批 = **H-fix-2c（🔴 异常策略第三层：脚本层，也是异常策略线收官批）**
3. 汇报 350 字内

## 阶段 0：计数定边界
- `grep -rn "except Exception" output/*.py` → 实测 **3 处**（`_kang_dump.py` 2 / `_llm_batch_trainset.py` 1）
- `grep -rn "except Exception" mangpai/tests/*.py scripts/*.py mangpai/tests/heldout/*.py` → 实测 **12 处**
- 合计 **15 处**（计划口径 ~20，以实测为准）

## 阶段 1：脚本层异常策略改造
**关键区分**（脚本层与引擎层处理原则不同）：

1. **验证脚本（最高优先级）**：`blind_eval.py` / `verify_layer3_checkpoint.py` / `verify_*.py` / `regression*.py` / `calib_assertions.py`
   - **禁止吞引擎异常**——引擎失败必须让验证**显式失败**（否则 CI 误绿 = 假验证！H7 已标 2 处）
   - 改法：`except Exception` → 明确失败（`raise` 或标记 case 为 error 并让退出码非 0）
   - **验证脚本的可信度 > 单例容错**：宁可让批跑中断，也不给假绿

2. **批跑脚本**（`output/_llm_batch_*.py` 等）：单例失败不应中断整批 —— 记录 case id + 错误类型，继续跑并在汇总里报告失败数（**不静默**）

3. **诊断脚本**（`_*_diag.py` 等）：允许降级但必须打日志

## 阶段 2：验证脚本自检（防假 green 回归）
- 为 `blind_eval` / `verify_layer3_checkpoint` 加**哨兵测试**：注入引擎异常 → 断言验证脚本**报错退出**（非静默通过）
- 这类测试进 `test_inject_faults.py` 或 `mangpai/tests/test_verify_integrity.py`

## 验证（DoD）
- [ ] 15 处改造完成（每处标注：传导/降级+日志/白名单）
- [ ] 验证脚本自检哨兵全绿（注入异常 → 验证脚本必失败）
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix2b.json` 零翻转零抖动**
- [ ] **验证结果可信度确认**：改造后 `blind_eval` / `verify_*` 在正常输入下**结果与改造前一致**（脚本行为不变，只改异常路径）
- [ ] 与引擎/主观层契约无冲突

## 分诊纪律
- 同 2a/2b：暴露既有 bug → 记 backlog + fix-forward；不带红前进

## 产出
- 15 处改造 + 验证脚本自检哨兵
- backlog 追加「H-fix-2c」节
- 汇报 350 字内：计数 + 三类脚本处理情况 + 假 green 2 处修法 + 六件套结果

## 红线
- **验证脚本改造后必须仍能正常验证**（结果一致，只改异常路径）
- 不改引擎/主观层判定逻辑
- 不调外部 API
