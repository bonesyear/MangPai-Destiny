# Kimi 任务：H-fix-4c · 局部 import / 循环依赖整理批

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H2 节**（56 处局部 import + `gongliang↔caiming` 双向依赖 + `yongshen` 星型中心）+ **H3 节**（gongmen_wuzhi.py:516 局部回导 gongliang）+ **H10 节**（output 脚本 sys.path.insert 手动改路径）+ **H12 节**（局部 import ~70 处遗漏项→本批）
2. 本批 = **H-fix-4c（🟡 局部 import / 循环依赖整理）**
3. 汇报 400 字内

## 分层铁律（不可破坏）
`foundation/`（学派中性）← `mangpai/objective/`（纯检测）← `mangpai/subjective/`（解释判断）← `mangpai/engine.py`（编排）
**单向依赖**——本批整理不得引入任何反向依赖。

## 阶段 0：清点与分类（先做）
1. **实测计数**：全仓函数内 `import` 语句（局部导入）——`grep -rn "^\s\+import \|^\s\+from " mangpai/ foundation/ scripts/` 复核 H2 的 56 处口径
2. **逐处分类**：
   | 类 | 特征 | 处置 |
   |----|------|------|
   | **A 纯冗余** | 顶层已导入，函数内重复 | 删除（低风险） |
   | **B 循环依赖规避** | 为解决循环依赖而局部导入 | 见阶段 1 处理 |
   | **C 重型依赖延迟** | 如 `anthropic` 软依赖、大模块 | **保留**（有意设计），加注释说明 |
   | **D 测试/工具** | 测试内导入 | 保留 |

## 阶段 1：循环依赖破除（本批核心）
已知：
- **`gongliang ↔ caiming` 双向依赖**（subjective 层内）
- **`yongshen` 星型中心**（多模块依赖它，也可能反向）
- **`gongmen_wuzhi.py:516` 局部回导 `gongliang`**（H3）

处置原则：
1. **能不破不破**：若局部导入是稳定的、有注释的循环规避手段 → 保留 + 补注释说明（改造成本 vs 收益）
2. **该破则破**：
   - 抽公共逻辑到下层模块（objective 或 subjective 内的基础 utils——已验证有 `subjective/utils.py` 可承载）
   - 或引入 **协议/数据结构** 中间层（如共享的 dataclass 常量表）
3. **依赖方向梳理**：画一份 subjective 层内部依赖图（模块 → 依赖），标注双向边——写入 backlog 供 H-fix-5 拆分参考

## 阶段 2：清理与规范
- A 类冗余局部导入删除
- `sys.path.insert` 手动改路径（output 脚本）→ **评估**：是否可改为相对导入/包安装（若工程成本高则保留 + 注释——output 脚本是批跑工具，非生产代码）
- 统一的导入风格（顶层导入优先）

## 验证（DoD）
- [ ] 局部 import 计数（改前/改后）+ 分类统计（A/B/C/D 各多少）
- [ ] 循环依赖图（subjective 层内部）——写入 backlog
- [ ] **分层铁律验证**：写一个检查脚本（AST 分析 import 关系），断言无反向依赖（`foundation` 不 import `objective`/`subjective`；`objective` 不 import `subjective`）+ 入库 `scripts/check_layering.py`
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_hfix4b.json` 零翻转零抖动**
- [ ] **正常路径输出逐字节不变**
- [ ] 3.11 + 3.14 import 冒烟

## 分诊纪律
- 循环依赖"能不破不破"——保留 + 注释优先于重构（本批不追求消灭所有循环，追求**显式化 + 方向正确**）
- 不带红前进

## 产出
- 分类清点表 + 循环破除/显式化 + 分层检查脚本
- backlog 追加「H-fix-4c」节（含依赖图）
- 汇报 400 字内：计数 + 分类 + 循环处理（破除/保留各多少）+ 分层检查结果 + 六件套

## 红线
- **分层铁律不可破**（单向依赖）
- 正常路径输出逐字节不变
- 不调外部 API
