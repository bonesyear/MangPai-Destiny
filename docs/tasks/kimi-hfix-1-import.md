# Kimi 任务：H-fix-1 · import/typing 崩溃面修复（+ 轻量抽查）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md`（v2 计划）+ `docs/tasks/codehygiene-fix-backlog.md` 的 H8 节（P0×3 具体发现）
2. 本批 = **H-fix-1（🔴 阻塞批第一发）**
3. 汇报 350 字内

## 任务 A：崩溃面修复（核心）
1. **`mangpai/subjective/guanming.py`**：补 `Any` 导入（第 39 行 `from typing import Dict, List, Optional, Set` 缺 `Any`，但第 139 行用了 `kong_wang: Any = None`）
2. **`mangpai/engine.py`**：补 `Optional` 导入（第 15 行 `from typing import Dict, Any, List`）
3. **全仓 typing 卫生扫描**：找出所有"注解里用了但未导入"的符号（`Any`/`Optional`/`Tuple`/`List`/`Dict`/`Set`/`Union` 等）——H8 只报了这两处，需全量扫（`zuogong_detect.py:997` 的 Tuple 已修过，确认无同类残留）
   - 方法建议：写一个静态检查脚本（AST 解析：函数签名的注解名 vs 模块导入集合），跑全仓 `mangpai/` + `foundation/` + `scripts/`

## 任务 B：多版本 import 冒烟（修复验证）
- **3.14**（系统 python3，PEP 649 惰性注解）：`/usr/bin/python3 -c "import mangpai"`
- **3.11**（venv，非惰性）：`/usr/local/lib/hermes-agent/venv/bin/python3 -c "import mangpai"`
- 两版都要通过（修复前 3.11 崩、3.14 通过——修复后双绿）
- 修复前先复现 3.11 的 NameError（红），修复后再跑（绿）——**哨兵纪律**

## 任务 C：轻量抽查（v2 计划并入项，零成本）
用你对旧代码的熟悉过程顺带完成：
1. 通读 `docs/tasks/codehygiene-fix-backlog.md` 的 **H11 施工图**（`_safe_compute` 37 模块对照 + 三大函数拆分方案）
2. 快速扫 5 个关键模块，标注是否有 H1-H13 **未发现**的新问题（只记录不改）：
   - `mangpai/engine.py`（编排层）
   - `mangpai/subjective/guanming.py`
   - `mangpai/objective/zuogong_detect.py`
   - `mangpai/subjective/gongliang.py`
   - `mangpai/subjective/zaihuo.py`

## 验证（DoD）
- [ ] 3.11 + 3.14 双版本 `import mangpai` 全绿
- [ ] typing 静态扫描脚本全仓零残留（脚本本身可入库 `scripts/check_typing_imports.py`）
- [ ] 六件套全量：`/usr/bin/python3 -m pytest`（预期 860 全绿）+ verify 全项 + **blind vs `snapshots/20260917_prehfix.json` 零翻转零抖动**
- [ ] 引擎判定零改动（本批只补 import，不应改任何逻辑）
- [ ] 批前 tag（如 `git tag h-fix-1-pre`）——**注意：git 操作由主会话负责，你只报告需要 tag 的时点**

## 产出
- 修复 + 静态检查脚本 + 抽查记录
- 汇报 350 字内：修了什么/双版本 import 结果/扫描残留数/抽查新发现/六件套结果

## 红线
- 只修 import 与 typing 注解卫生——**不改任何逻辑/判定/输出**
- 不调外部 API
