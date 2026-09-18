# Kimi 任务：H-fix-6 · selectors/engine-keys 契约测试批

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H4 节**（`zinv` selector 无生产消费者，仅 engine 写入 + payload 透传）+ **H8 节**（selectors 与 engine 产出键无同步保护）+ **H11 节**（selectors 为静态元组，新增键漏登记会静默丢失数据，缺 engine-key 自动契约测试）+ **H-fix-4c 节**（依赖图与拆分顺序建议）
2. 本批 = **H-fix-6（🟡 契约测试——必须前置于 H-fix-5 的 compute_all 拆分）**
3. 汇报 350 字内

## 背景与目标
**问题**：`subjective/schools.py` 的 selectors 是**静态元组**（手工维护）——engine 新增模块键时若忘记登记：
- 该键进不了 payload → LLM/叙述层看不到 → **静默丢功能**
- 反之，selectors 里若留了 engine 不再产出的键 → **死键**

**目标**：建立**自动契约**——engine 产出键 ↔ selectors 登记键 ↔ payload 键互为校验，任何漂移在测试里暴露。

## 阶段 0：现状清点
1. 实测：engine `compute_all` 产出的全部键（跑一个样本盘 dump 键集合，预期 48）
2. 实测：`schools.py` selectors 登记键（预期 41）
3. 实测：`build_payload` 输出键（预期 41）
4. **三方对照表**：engine 有而 selectors 无（漏登记？）/ selectors 有而 engine 无（死键？）/ payload 键 → 消费方（narrative/llm_prompt/formatter 是否有读者）

## 阶段 1：契约测试实现
新建 `mangpai/tests/test_key_contract.py`，包含三类断言：

1. **engine → selectors 完整性**（防漏登记）
   ```
   断言：engine 产出的每个顶层键，或在 selectors 中登记，或在显式白名单（如内部键 input/bazi）中
   ```
   - 为什么需要：未来新增模块（如七维扩展）忘登记 → 今天起测试就红
2. **selectors → engine 存在性**（防死键）
   ```
   断言：selectors 登记的每个键，engine 实际产出（或显式标注"预留/兼容"）
   ```
3. **payload → 消费方**（防死键，比 H4 的 zinv 问题更进一步）
   ```
   断言：payload 的每个键，至少有一个消费者（llm_prompt basis 白名单 / formatter / narrative）
   ```
   - 对无消费者的键（如 H4 报的 zinv selector 只有透传）→ **显式标注为"预留（供未来扩展）"而非静默存在**

## 阶段 2：登记机制改进（可选但推荐）
若阶段 0/1 发现手工维护易错：
- 评估是否引入**自动派生**（如 selectors 从 engine 的模块注册表推导）
- 若引入需保证：不影响现有 41 键行为（payload 键数不变）
- **不与阶段 1 的契约测试冲突**（测试是哨兵，改进是机制）

## 验证（DoD）
- [ ] 契约测试三类断言全绿（且**对当前代码不是"恒真"**——用故意破坏验证：临时删一个 selectors 键 → 测试应变红 → 恢复）
- [ ] 三方对照表（engine 48 / selectors 41 / payload 41）差异项全部有显式处置（登记/白名单/标注预留）
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix4c.json` 零翻转零抖动**
- [ ] payload 键数不变（41）；正常路径输出逐字节不变
- [ ] 分层检查脚本仍通过（`scripts/check_layering.py`）

## 产出
- 契约测试 + 三方对照表 + 差异处置
- backlog 追加「H-fix-6」节（含"预留键"清单——供 H-fix-5 拆分时参照）
- 汇报 350 字内：三方键数 + 差异项处置 + 契约测试（含红验证）+ 六件套

## 红线
- **引擎判定与 payload 结构零改动**（本批只加测试与标注，除非阶段 2 的机制改进经评估安全）
- 不调外部 API
