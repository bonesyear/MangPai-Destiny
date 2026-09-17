# Kimi 任务：H-fix-4b · 重复逻辑下沉/统一批（重构类，等价性优先）

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H1 节**（`_check_pair` 四文件复制粘贴 P1；十神计算 objective 三处独立实现）+ **H2 节**（subjective 8 处 `_compute_shishen` + 12 个 `_ensure_*` 重复）+ **H3 节**（`_cat`/`_wx_cat`/`_ensure_relations` 3 重复族）+ **H10 节**（`_has_xiangmao_marker` 与 `llm_prompt._xiangmao_anchor` 重复）+ **H11 节**（detect_relations 6 组 O(n²) 复制循环 → 注册表统一扫描方案）
2. 本批 = **H-fix-4b（🟡 重复逻辑统一——重构类）**
3. 汇报 400 字内

## ⚠️ 本批最大风险：重构改变行为
**等价性是第一红线**——重复代码块之间可能存在**细微差异**（正是复制粘贴的隐患：改了一处忘了另一处）。统一时必须先判定"哪个版本是正确版本"。

## 执行方法（每项重复的处置流程）
1. **差异分析**（必须先做）：
   - 逐行对比各副本，列出**所有差异点**（哪怕一个符号）
   - 判定差异性质：①真等价（可安全合并）②某一版有 bug（合并时用正确版 + 记录该 bug）③有意的场景差异（**不合并**，加注释说明）
2. **统一实施**：
   - 真等价 → 抽公共函数/模块，各方改为调用（保留原函数名做薄包装，减少调用点改动面）
   - 发现某版有 bug → 修复 + 记 backlog（这属于"重构暴露既有 bug"）
   - 有意差异 → 不合并 + 加注释（说明为何两份不同）
3. **等价性验证**（每项统一后立即验证）：
   - 六件套 + **正常路径输出逐字节不变**
   - 特殊情况：若某项统一涉及判定路径，用 blind 快照逐例比对（heldout+trainset 全部 case 的 engine dict 深比较）

## 统一清单（按优先级）

### A. 工具函数级（低风险，先做）
1. **`_check_pair`**（zuogong_detect / dayun / muku / gongshen 四份）→ 抽到公共模块（建议 `objective/_relation_utils.py` 或 constants 邻近）
2. **`_cat` / `_wx_cat`**（H3 重复族）
3. **`_ensure_relations`**（H3）
4. **12 个 `_ensure_*`**（H2，subjective 层）→ 抽公共 helper
5. **`_has_xiangmao_marker`**（output 脚本）→ 复用 `llm_prompt._xiangmao_anchor` 的判定函数（H10）

### B. 十神计算统一（中风险，工作量较大）
- **objective 三处**（bazi_calc / dayun / shenshu）+ **subjective 8 处**（caiming/zhiye/yongshen/liuqin/zaihuo/xiangfa_ops/gongmen_wuzhi 等）
- 目标：**单一权威实现**（建议放 `foundation/` 或 `objective/canggan.py` 邻近——按依赖方向定，不得反向依赖）
- ⚠️ **重点核查**：各处实现是否**真的等价**（可能有不同的边界处理：如藏干权重/主气中气余气处理/阴阳判定）——**逐处对比后再决定**
- 若发现不等价（不同模块有意不同口径）→ **不强行统一**，改为一处权威 + 各处显式调用带参数变体

### C. detect_relations 6 组循环（H11 方案）
- 6 组 O(n²) 复制循环（六合/暗合/冲/刑/害/破）→ **注册表驱动统一扫描**
- 按 H11 §detect_relations 的拆分方案执行（但**函数拆分主体留 H-fix-5**——本批只做"复制循环 → 注册表"的重复消除，函数长度可自然下降但不强制拆分）

## 验证（DoD）
- [ ] 每项统一有**差异分析记录**（差异点 + 判定 + 处置）
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix4a.json` 零翻转零抖动**
- [ ] **正常路径输出逐字节不变**（deep-compare heldout+trainset 全量 engine dict）
- [ ] 若发现既有 bug → backlog 记录 + fix-forward
- [ ] 3.11 + 3.14 import 冒烟

## 分诊纪律
- 不确定是否等价的 → **不合并**（宁留重复勿改行为）
- 不带红前进

## 产出
- 统一实施 + 差异分析记录
- backlog 追加「H-fix-4b」节（含"判定不等价不合并"清单）
- 汇报 400 字内：各类统一情况（合并/不合并各多少）+ 发现的既有 bug + 代码量变化 + 六件套结果

## 红线
- **引擎正常路径输出逐字节不变**
- 判定逻辑与书锚口径零改动
- 不调外部 API
