# Kimi 任务：H-fix-4a · 死代码/死数据清理批（纯删除类，低风险）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的相关节：**H1**（advanced.py 6 个死 shim、detect_relations 死分支）+ **H3**（shipaige SHIPAI_DOMAINS/METHODOLOGY 死数据、chuangong engine 零消费、gongmen_wuzhi 弃用模块）+ **H7**（8 个历史模拟脚本归档清单）+ **H10**（foundation `__all__` 遗漏、NAYIN_WUXING 与 constants 重复）+ **H-fix-2b 节**（死调用 2 条：gongmen muku 未用、xiangfa_ops if/else 同支）+ **H2/H4**（`cost_usd`→`cost_cny` 改名）
2. 本批 = **H-fix-4a（🟡 死代码/死数据清理——纯删除类）**
3. 汇报 350 字内

## 重要前提：删除前必须验证"真死"
每一项删除前**必须**：
1. **全仓引用搜索**（`grep -rn "符号名"` 覆盖 mangpai/ + foundation/ + scripts/ + tests/ + output/）
2. **确认无隐式消费**：检查 `build_payload` selectors / `formatter` / `narrative` / prompt 模板是否读取（**prompt-only 字段风险**——v2 计划红线）
3. **记录证据**（引用搜索结果行数=0 或仅自引用）——写入汇报

## 清理清单（按 backlog 逐项复核后执行）

### A. 死 shim / 死导出
- `advanced.py` 的 6 个 eager re-export（H1 报零调用方）+ `__getattr__` lazy import 的循环依赖隐患
- `foundation/objective/__init__.py` 的 `__all__` 遗漏 `get_nayin_wuxing`（H10）——补齐而非删除
- `NAYIN_WUXING` 与 constants 重复（H10）——择一保留，另一个改为引用

### B. 死数据 / 弃用模块
- `shipaige.py` 的 `SHIPAI_DOMAINS` / `METHODOLOGY`（H3：F18 已整体重写，旧碎片表留档）——**注意**：H3 记载"留作碎片原文档案"，删除前确认 KB/审计文档是否引用
- `chuangong.py`（engine 零消费）
- `gongmen_wuzhi.py`（已声明弃用，F18 决议）
- 其余 backlog 标注的死键/死字段

### C. 死调用 / 死分支
- `gongmen` muku 未用调用（H-fix-2b 暴露）
- `xiangfa_ops` if/else 同支（H-fix-2b 暴露）
- H1 报的 `detect_relations` 内死分支（若属重复逻辑则留 H-fix-4b；纯死分支本批删）

### D. 改名（统计口径修正）
- `cost_usd` → `cost_cny`（H4 P1 + H10 P1：字段实际存人民币却按美元换算的遗留）——**全仓统一改名** + 检查所有消费方（output 脚本的换算逻辑）

### E. 脚本归档
- H7 的 8 个历史模拟脚本（`_a1_exp.py`、`_zy2_sim2/3`、`_zy3/4_sim`、`_zy55_feat/sim`、`_zy_margin` 等）→ 移到 `mangpai/tests/heldout/archive/`（或删除——按 H7 建议归档；若仓库已有 archive 约定则遵循）

## 验证（DoD）
- [ ] 每项删除/改名都有"引用搜索=0 或仅自引用"证据
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix3.json` 零翻转零抖动**
- [ ] **引擎判定零改动**：正常路径输出**逐字节不变**（删除死代码不应改任何输出）
- [ ] `cost_cny` 改名后成本计算仍正确（抽查一次估价函数）
- [ ] payload 探针：确认无 prompt-only 字段被误删（跑一次 payload 构建，键数与 hfix3 一致）
- [ ] 3.11 + 3.14 import 冒烟（删除可能影响 import 面）

## 分诊纪律
- 任何"不确定是否死"的项 → **不删**，记入 backlog 待议（宁留勿误删）
- 不带红前进

## 产出
- 清理执行 + 证据记录
- backlog 追加「H-fix-4a」节（含"不确定未删"清单）
- 汇报 350 字内：各类删除数量 + 证据概况 + 改名影响面 + 六件套结果 + 未删待议项

## 红线
- **引擎正常路径输出逐字节不变**
- 不确定的宁留勿删
- 不调外部 API
