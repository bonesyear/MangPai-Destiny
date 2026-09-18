# Kimi 任务：审查主会话（Hermes）的代码改动（独立代码审查）

## ⚠️ 执行指引
- 审查报告写 `/root/.claude/projects/-root-metaphysics/memory/kimi-hermes-code-review-20260918.md`，stdout 400 字内摘要
- **只审不改**（发现的问题列清单，不修）
- 汇报 400 字内

## 背景
本仓库的绝大多数代码由你（Kimi CLI）在 F/L/H/P/S 系列批中编写并自审。但**主会话（Hermes）也直接改过若干代码**——这些改动**从未经过独立审查**（主会话自己写的、自己验证的）。本批 = 对这些改动做独立审查。

## 审查对象（主会话改动的代码文件）

### 1. `mangpai/subjective/llm_backend.py`（改动最多）
主会话改动：
- 定价表 `_PRICING` → `_PRICE`（美元口径 → **人民币口径**）
- 新增 `'deepseek-flash'` 键 + 保留 `'deepseek-v4-flash'` 旧名别名
- `_DEFAULT_MODEL`：`deepseek-v4-flash` → `deepseek-flash`
- `_estimate_cost` docstring：USD → 人民币
- `_self_check` 断言更新 + 新增别名等价性断言
- docstring 定价说明更新（数据来源/日期/V4.1 标注）

**审查重点**：
- 价格数值是否正确（人民币口径：flash 峰 ¥3.0/¥9.0、谷 ¥1.5/¥4.5；pro 峰 ¥9.0/¥27.0、谷 ¥4.5/¥13.5）
- 单位/量纲一致性（¥/1M tokens）
- 别名机制是否完整（读/写、批跑脚本、历史数据兼容）
- 是否有遗漏的旧名引用（全仓 grep 验证）
- S1 之后（`MANGPAI_LLM_*`）与本改动的交互是否正确（`_PRICE` 键与 `_DEFAULT_MODEL` 的配合）

### 2. `mangpai/subjective/llm_channel.py`（`_demo_cases_path` 新增）
主会话改动：demo 的 `cases.yaml` 相对路径 → `_demo_cases_path()`（`Path(__file__)` 锚定）
**历史**:主会话第一次写成 `parents[2]`（错误，指向仓库根而非 mangpai/），手工验证抓到后改 `parents[1]`
**审查重点**：路径层级是否正确（可多 cwd 验证）、函数放置/命名/注解风格是否合规、有无其他类似相对路径残留

### 3. `mangpai/feishu/router.py`（HELP 文本）
主会话改动：HELP 隐私提示去厂商名（`第三方大模型（DeepSeek）` → `第三方大模型`）
**审查重点**：与 F1 批次加的隐私告知的意图是否一致、是否有其他地方仍硬编码厂商名

### 4. `mangpai/tests/test_llm_backend.py` / `test_f1_gate.py` / `test_llm_channel.py`
主会话改动：断言同步（模型名/厂商名/新增 cwd 哨兵）
**审查重点**：断言是否仍有意义（不是为过而改）、覆盖是否充分

### 5. `scripts/build_book_index.py`（主会话新建）
主会话新建的索引生成脚本
**审查重点**：正则模式健壮性、噪音过滤正确性、输出路径/原子写（H-fix-3 已给 `_atomic_io` 但本脚本未用？）、编码处理

### 6. `.gitignore` + `output/README.md`（主会话改/新建）
**审查重点**：白名单语法正确性（`output/*` + `!output/*.py` 形式）、隐私排除是否严密（`_kang*`/数据文件）、有无绕过风险（如 `git add -f` 提示是否明确）

### 7. `README.md` / `docs/privacy-policy.md`（主会话改）
**审查重点**：数字准确性（模块数/用例数）、与实现一致性、有无遗留失实表述

## 产出
1. **问题清单**：`文件:行号 | 类型（正确性/一致性/卫生/安全）| 严重级（P0/P1/P2）| 问题 | 修法建议`
2. **每项改动给结论**：通过 / 有问题（列问题）/ 需补充
3. **特别核查**：主会话是否犯了与 `parents[2]` 同类的"未验证假设"错误（其他改动里有没有）
4. 汇报 400 字内

## 红线
- 只审不改
- 不调外部 API
- 独立判断（不因主会话已自测就放松——目标就是找漏）
