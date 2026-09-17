# Kimi 任务：H-fix-2a · 异常处理策略-引擎层（含错误注入框架前置）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md`（v2 计划）+ `docs/tasks/codehygiene-fix-backlog.md` 的 **H8 节**（engine._safe_compute P0）+ **H11 节**（37 模块施工图）+ **H-fix-1 节**（新发现 13 条，本批需处理其中 2 条 P1）
2. 本批 = **H-fix-2a（🔴 异常策略第一层：引擎层 + 入口校验）**
3. 汇报 400 字内

## 阶段 1：错误注入测试框架（前置，必须先做）
新建 `mangpai/tests/test_inject_faults.py`（或 `scripts/fault_inject.py` + 测试包装）：
- **参数化故障注入**：
  1. **非法干支**（如 `'甲甲'`、`'XX'`、空串）→ 输入到 `dayun_gz_sequence` / `_advance_gz` / `calc_bazi_full`
  2. **空 actions**（`compute_all` 的 work_actions 为空）
  3. **越界索引**（`_cand_hua[0]` 空列表场景）
  4. **畸形输入**（None / 非 dict / 缺键的 bazi_data）
- 每个注入点断言：**要么抛明确业务异常（如新增 `EngineInputError`），要么安全降级返回**——禁止静默吞掉（`except: pass`）
- 跑 calib 10 例作冒烟（`mangpai/tests/calib_assertions.py` 或 heldout 的用法）
- **哨兵纪律**：框架先跑 → 对未修复代码应**证明现有静默失败面**（红），修复后转绿

## 阶段 2：引擎层异常策略改造（37 模块施工图）
按 H11 施工图逐模块处理 `engine.py` 的 `_safe_compute`：
1. **分类裁定**（每个模块归一类）：
   - **应传导**（关键路径失败必须让上游知道）→ 不吞，抛明确异常
   - **应安全降级**（可选模块失败不影响主链）→ 记录 warning + 返回明确默认值（不用裸 `or {}`）
   - **应白名单化**（已知可忽略的特定异常）→ 只抓特定类型
2. **engine 回写契约统一**（H8 P1，本批并入）：统一 `or {}` / `is not None` / 缺键三态处理——建议统一为显式 `is not None` 判断 + 缺键时返回明确结构
3. **入口校验 3 项 P0 显式纳入**：
   - `dayun.py` `dayun_gz_sequence()` 非法干支裸 `index()` → 抛明确业务异常
   - `_advance_gz` 同类
   - `_cand_hua[0]` 越界
4. **`JSONDecodeError` 包装**（llm_backend，H4 P0）：HTTP 200 但非 JSON 时 → 明确异常而非穿透

## 阶段 3：H-fix-1 抽查发现的 2 条 P1（本批顺带）
- `engine.py:179` `end_age=None` 会炸 `compute_all` → 加守卫
- `zaihuo.py:388` 正官误标"七杀" → 按书锚核对修正（若涉及判定逻辑，**先确认书锚再改**，并在汇报中说明）

## 验证（DoD）
- [ ] 错误注入框架全绿（每个注入点行为符合预期）
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260917_hfix1.json` 零翻转零抖动**
- [ ] **引擎判定零改动确认**：`compute_all` 正常输入下的输出**逐字节不变**（异常路径改造不得影响正常路径）——建议写一个"正常路径输出快照对比"验证
- [ ] 计数核查：裸 `except Exception:` 在引擎层的数量变化（改前/改后）
- [ ] 批前 tag（主会话负责，你报告时点）

## 分诊纪律（v2 计划要求）
吞改抛若暴露**真实的既有 bug**（非本批引入）：
- 记录到 backlog（新节「H-fix-2a 暴露」）
- 按 fix-forward 原则：小修当场修（带哨兵），大修记入后续批
- **不带红前进**：若六件套任一红且无法当场修，停下报告

## 产出
- 错误注入框架 + 37 模块分类处理 + 入口校验 + 契约统一
- backlog 追加「H-fix-2a」节（含暴露的既有 bug）
- 汇报 400 字内：分类统计（传导/降级/白名单各多少）/入口3项/JSONDecodeError/2条P1/六件套结果/暴露的既有bug

## 红线
- **引擎正常路径输出逐字节不变**（本批只改异常路径行为）
- 不调外部 API
