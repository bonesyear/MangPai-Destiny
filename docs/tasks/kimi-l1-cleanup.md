# Kimi 任务：L1 · 遗留项清理批（引擎精度批紧前批，批内两阶段）

## ⚠️ 执行指引
1. **先读**：`/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-fix-plan-20260918.md`（本批方案——阶段划分与修法裁定）+ 同目录评估报告（`kimi-leftover-assessment-20260918.md`）+ `docs/remaining-tasks-20260917.md`（待办节）+ `docs/tasks/codehygiene-fix-backlog.md`（L0 节转出待办）
2. 本批 = **L1（引擎精度批紧前批——先换基线）**
3. 汇报 400 字内

## 阶段甲：零输出项（逐字节不动）
按方案逐项执行，**每项完成后立即验证**（输出逐字节不变）：

1. **B2 入口守卫**：`engine.py:577-578`（漂移后行号，请重新定位）——`liunian_data` truthy 非 dict → `.get` AttributeError；加类型守卫
2. **B3 初始化**：`engine.__init__` 补 `_auto_liunian_injected` 初始化（当前 getattr 兜底——状态泄漏潜伏项）
3. **B4 冗余删除**：`_scan_shengyong` 嵌套冗余 `if day_wx:` + `_prepare_inputs` 死代码块（实在 `subjective/gongliang.py:431-433`，非 engine.py——行号已更正）
4. **C2 DISCLAIMER 统一**：`formatter.DISCLAIMER` 与 `llm_channel._DISCLAIMER_LINE` 文本重复 → 单一来源（注意：改文案会动输出 → **确认文本内容完全一致再做统一**，若一致则纯代码统一、输出不变）
5. **C3 快照卫生测试**：新建 `test_snapshot_hygiene.py`——快照 meta 链自动校验（rubric_version/git_sha/split 字段完整性 + LATEST 指针有效性）

**阶段甲验收**：六件套 + **输出逐字节不变**（blind vs `LATEST`；若 C2 文本确一致则零抖动）

## 阶段乙：输出项（一次换基线）
1. **B1 排序化**：`xiangfa_ops` 4 处 `.pop()`（:336/:677/:811/:1090+:1096——漂移后请重新定位）——**取"消费方排序"修法**（方案裁定），消除 `PYTHONHASHSEED` 旋转导致的批跑输出不可复现
   - 验证：随机 seed 下 t3_dump 类输出应**稳定**（H-fix-7 曾实测 287 例序差）
2. **C1 zaihuo label**：`zaihuo.py:319-322`（漂移后）正官误标「七杀」→ 修正 label 文本（计数有书锚不动，仅 label）
   - 影响面：限 zaihuo desc 一域；score/判定不动

**阶段乙验收**：
- 抖动**逐条归因**（每条抖动必须能解释为 B1 或 C1 的预期效果）
- **一次换基线**（新快照 + LATEST 指针更新）
- 非目标维零翻转（官/财/职判定不进抖动）

## 全局 DoD
- [ ] 阶段甲：输出逐字节不变；阶段乙：抖动逐条归因 + 一次换基线
- [ ] 六件套全量（pytest / verify 全项 / blind / 双 seed / 67+famous / calib 零新增）
- [ ] **双 seed 复现验证**（B1 的核心价值——`PYTHONHASHSEED` 0/7/42 下 xiangfa_ops 输出一致）
- [ ] `check_layering.py` + `check_typing_imports.py` 通过
- [ ] 3.11 + 3.14 import 冒烟

## 产出
- 阶段甲 5 项 + 阶段乙 2 项 + 新基线
- backlog 追加「L1」节 + 收工记录更新（L1 转已办）
- 汇报 400 字内：各项落地情况 + 双 seed 复现验证结果 + 抖动归因 + 新基线 + 六件套

## 红线
- 阶段甲严格零输出；阶段乙抖动全归因
- 判定逻辑（score/层级）零改动
- 不调外部 API
