# Kimi 任务：H-fix-2b · 异常处理策略-subjective 层

## ⚠️ 执行指引
1. **先读**：`docs/tasks/h-fix-workplan-v2-20260917.md` + `docs/tasks/codehygiene-fix-backlog.md` 的 **H2 节**（subjective 核心批：67 处裸 except 分布）+ **H3 节** + **H-fix-2a 节**（框架与分流模式，本批复用）
2. 本批 = **H-fix-2b（🔴 异常策略第二层：subjective 判断层）**
3. 汇报 400 字内

## 阶段 0：重新计数定边界（v2 计划要求）
- 实测命令：`grep -rn "except Exception" mangpai/subjective/*.py | wc -l` → 当前 **91 处**（计划口径 67，已漂移）
- 逐文件计数并按类型分类（`except Exception:` / `except Exception as e:` / `except:`），**以实测数字为本批工作量基准**，写入汇报

## 阶段 1：subjective 层异常策略改造
复用 H-fix-2a 的分类模式（传导 / 安全降级 / 白名单），但**注意 subjective 层的特殊性**：

1. **判定模块是"纯函数"倾向**——多数模块的异常应在**模块内部处理**（返回明确的"无法判定"结构），而非上抛：
   - **安全降级**：判定失败 → 返回明确的"未判定"结果（如 `{'is_xxx': None, 'reason': 'compute_error'}`）而非静默 `{}`
   - **应传导**：仅真正的契约违反（如输入结构非法）才上抛 `EngineComputeError`
   - **白名单**：已知可忽略的特定异常收窄类型
2. **重点文件**（按实测处数）：`caiming.py`(11) / `zhiye.py`(10) / `yongshen.py`(9) / `liuqin.py`(9) / `zaihuo.py`(7) / `xiangfa_ops.py`(7) / `gongmen_wuzhi.py`(7) / `zuogong_confirm.py`(5) / `hunyin.py`(5) / `guanming.py`(4) / `gongliang.py`(4) / `yunfan.py`(3) + 其余
3. **回写契约一致性**：subjective 层的失败返回结构必须与 `engine.py` 的 `_MODULE_DEFAULTS` 对齐（2a 已建成——本批需确保两边一致，发现不一致以 engine 侧为准）

## 阶段 2：错误注入覆盖扩展
- 复用 `test_inject_faults.py` 框架，**扩展主观层注入用例**：
  - 各主要模块（caiming/zhiye/yongshen/liuqin/hunyin/guanming/gongliang/xiangfa_ops）注入非法输入 → 断言"返回明确未判定结构"或"抛明确异常"
- **哨兵纪律**：新用例先对未修复代码证明静默失败（红）→ 修复后绿

## 验证（DoD）
- [ ] 错误注入扩展用例全绿
- [ ] 六件套全量：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260917_hfix2a.json` 零翻转零抖动**
- [ ] **引擎判定零改动**：正常输入下 `compute_all` 输出**逐字节不变**（subjective 层的异常路径改造不得影响正常判定结果）
- [ ] 裸 except 计数对比（改前 91 → 改后？）
- [ ] 与 `_MODULE_DEFAULTS` 的结构一致性确认

## 分诊纪律
- 吞改抛若暴露真实既有 bug → 记 backlog「H-fix-2b 暴露」+ fix-forward（小修当场，大修延后）
- **不带红前进**；正常路径字节变更一律延后（同 2a 的 zaihuo 处理先例）

## 产出
- 阶段 0 计数表 + 改造 + 注入扩展
- backlog 追加「H-fix-2b」节
- 汇报 400 字内：计数（改前/改后）+ 分类统计 + 重点文件处理 + 注入用例数 + 六件套结果 + 暴露的既有 bug

## 红线
- **正常路径输出逐字节不变**
- 不改判定逻辑与书锚口径（只改异常路径行为）
- 不调外部 API
