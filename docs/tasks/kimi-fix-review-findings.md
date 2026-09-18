# Kimi 任务：修复你自己的审查发现（P2 项 + 复核主会话 P1 修复）

## ⚠️ 执行指引
1. **先读**：你的审查报告（`/root/.claude/projects/-root-metaphysics/memory/kimi-hermes-code-review-20260918.md`——**P1×3 + P2×8 清单**）+ 主会话刚提交的修复（commit `6c37463`）
2. 本批 = **修审查发现（P2 项）** + **复核主会话的 P1 修复**
3. 汇报 400 字内

## 背景
你的审查结论：P0=0，P1×3（对外文档失实），P2×8。主会话已修 P1×3 + 部分 P2，**但 output/ 脚本的批量替换不可靠（留下语法错误）已全量回滚**——这部分交你统一修。

## 任务 A：复核主会话已修项（commit 6c37463）
逐项确认修复是否正确、彻底：
1. `README.md`：pytest 数（1066→1129 两处）+ cwd 陈述（:140 改"可在任意目录运行"）
2. `docs/llm-channel-20260818.md:30`：cwd 陈述同步
3. `mangpai/subjective/llm_channel.py`：`_demo_cases_path` 的 Path 导入提到顶部（原局部 import）
4. `docs/privacy-policy.md`：§五 duan-books 表述（改准为"原著 txt 未进入公开仓库，仅章节索引"）+ 版本号 v1.2

**复核要点**：是否有残留同类失实（如其他文档仍称 cwd 限制/其他数字失实）；改法是否彻底（不是打补丁）

## 任务 B：修 P2 项（依你审查报告）

### B1. output/ 脚本 cwd 相对路径（7 个文件）——**重点**
- 报告指出：`_llm_batch_analyze/rescore/retry/trainset.py`、`_n2_analyze.py`、`_t3_dump.py`、`_w4_sample.py`、`_w5_crosscheck.py` 等仍用 `'mangpai/tests/trainset/cases.yaml'` 类 cwd 相对路径
- ⚠️ **主会话尝试批量替换失败**（脚本头部有 `sys.path.insert` 惯用法，插入位置易错）——请你**逐个文件按各自结构正确处理**（保持 `# noqa: E402` 风格与现有头部结构一致）
- 修法建议：`Path(__file__).resolve().parents[1] / ...` 锚定（output/ 的上一级=仓库根）
- **验证**：每文件 `py_compile` 通过 + 从非仓库目录运行时的路径解析正确性（可用 `-c` 小测，**不要真跑批跑**——会调 LLM API）

### B2. `_demo_cases_path` 复核（主会话已改）
确认 import 提升后无副作用（库调用方导入 `llm_channel` 时不再有函数内 import 延迟收益问题——Path 是标准库，应无影响）

### B3. 其他 P2（依报告逐项）
- `pro` 无新名别名（docstring 已标注待官网复核——**保留现状**，或按你判断）
- privacy-policy 其他小项（你报告里列的：路径 shorthand 等）
- output 子目录白名单注释（若需要）
- 其余你报告里的 P2 项

### B4. 你判断为"不需修"的 P2 → 明确写下理由（收档标记）

## 验证（DoD）
- [ ] output 全部脚本 `py_compile` 通过 + 路径锚定正确（非仓库 cwd 验证）
- [ ] 主会话 P1 修复复核结论（通过/有问题）
- [ ] P2 项逐项处置（修 / 收档附理由）
- [ ] 六件套：pytest 全绿 + verify 全项 + **blind vs `snapshots/20260918_t1.json` 零翻转**（引擎零触）
- [ ] 分层两件套通过
- [ ] 汇报 400 字内

## 红线
- 不改引擎判定
- 不真跑批跑脚本（会调 LLM API）——用 `py_compile` + 路径解析小测
- 不调外部 API
