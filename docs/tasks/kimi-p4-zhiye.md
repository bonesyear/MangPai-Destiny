# Kimi 任务：P4 · 职业军警新面批（军警墓库做功）——P 系列收官批

## ⚠️ 执行指引
1. **先读**：`/root/.claude/projects/-root-metaphysics/memory/kimi-engine-precision-plan-20260918.md`（**P4 节**）+ `docs/knowledge-base.md`（§6.1 职业残留、§4.x 军警/gongmen 相关）+ P1/P2/P3 预注册先例 + `docs/remaining-tasks-20260918.md`（基线=`snapshots/20260918_p3.json`）
2. 本批 = **P4（职业军警新面——P 系列收官）**
3. 汇报 500 字内

## 对象（依方案）
- **objective muku 域**：「库制库」做功检测（`gaoji` 8.2 墓库章）
- **zhiye military 消费扩展**

## 书锚依据（回书逐字核行号）
- `gaoji` 8.2 墓库章（gongmen_wuzhi/F15 相关——注意：gongmen_wuzhi 已弃用不接 zhiye，F15 已在 zhiye._score_military 按书重写 8.2 六组）
- 军官例二 / 纪检例九（既有 military ✅ 锚）

## 修法纪律
1. **窄检测面 + 窄消费桶**（方案定为中低风险）——保持范围克制
2. **预注册**（同前三批）：受影响书例 + 双端锚 + 行号
3. ⚠️ **墓库检测改动须过 F2 muku 消费方全量回归先例**：muku 是 10 模块（caiming/guanming/gongliang 等）的共享依赖——**改动前先审计全部消费方**，改动后全量回归
4. 既有 military ✅ 锚 **margin 检验**（军官例二/纪检例九）
5. **yx-科级 collateral 类不复现**（方案验收④——历史 collateral 案例，须确认不重演）

## 验证（DoD）
- [ ] **heldout 职 24✅ 不下滑**（零回退硬红线）
- [ ] **军警探针 3/10 → 目标 ≥4/10**（方案定量验收）
- [ ] 既有 military ✅ 锚（军官例二/纪检例九）margin 检验
- [ ] yx-科级 collateral 类不复现
- [ ] **非目标维零翻转**（官/财：heldout 48/47 保 + trainset 102/61 保）
- [ ] M2 分组门禁（职业分组无失衡）
- [ ] 预警指标：trainset 职 **+2~4**（40→42~44）
- [ ] 哨兵先红后绿 + 六件套全绿 + 双 seed 一致 + calib 常驻 2 条零新增
- [ ] 全量 blind diff 逐条归因
- [ ] muku 消费方全量回归（10 模块）
- [ ] 分层两件套 + 3.11/3.14 冒烟

## 分诊纪律
- 红线破 → 停下报告
- 收档项写 backlog 附理由

## 产出
- 检测面 + 消费扩展 + 预注册 + 逐条归因
- 新基线（若改善）+ backlog「P4」节 + 收工记录（**P 系列收官终态**）
- 汇报 500 字内：实现项 / 探针结果 / 指标变化 / 锚与 collateral 检验 / muku 回归 / 归因 / 六件套

## 红线
- heldout 只评估不反推
- 判定改动须有书锚
- 不调外部 API
