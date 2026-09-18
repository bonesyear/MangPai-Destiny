# Kimi 任务：narrative.py 遗留通道处置路线分析（判断类，只分析不改码）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + `mangpai/subjective/narrative.py` 模块 docstring（S1 标注）
2. **只分析不改码**——本批产出=路线评估报告 + 推荐，用户在等决策
3. 报告写 `/root/.claude/projects/-root-metaphysics/memory/kimi-narrative-legacy-routing-20260918.md`；stdout 400 字内摘要

## 背景（主会话已核实的证据链，可信；请抽查关键项，勿重复全量诊断）

**问题**：仓库内存在第二家 provider 硬绑——`narrative._call_llm`（`anthropic.Anthropic()` + 默认 `claude-sonnet-5`）。用户问「为什么绑 Anthropic」，已查明：

| 事实 | 证据 |
|---|---|
| **原住民非后加** | git blame 行首 `^878f3ce` = 仓库**初始提交**（2026-07-15，「盲派引擎 v2026-07-13」）；当时 `narrative.py` 438 行 + `hao_style_fewshot.py`，初始提交说明写「Narrative 层: 郝金阳风格推演」——**那时它是唯一 LLM 通道** |
| **后续被替代** | 正式通道演进为 `llm_channel`（七维结构化三层校验）+ `llm_backend`（`MANGPAI_LLM_*` 体系，任意 OpenAI 兼容）；DeepSeek 成默认 |
| **anthropic 全仓位置** | 仅 `mangpai/subjective/narrative.py` 一个文件 |
| **`_call_llm` 调用点** | 仅 `narrative.py:586`（`render_hao_narrative(call_llm=True)` 分支）；**生产零调用**，只在测试 monkeypatch 里出现 |
| **测试依赖** | `test_narrative.py:249/256/262/268`（monkeypatch `_call_llm`）+ `test_s1_llm_config.py:254`（断言 docstring 含「遗留通道」） |
| **工具函数仍服役** | `summarize_engine_result` / `validate_narrative_numbers` / `_bazi_line` 被 `llm_channel.py` 复用（非死代码） |
| **降级契约** | 无 anthropic SDK/key → 不抛错，返回组装好的 prompt 文本（可手工喂任意 LLM） |

**三候选路线**（用户要你评估走哪条）：
- **A 保留现状**（已标注遗留 + 无生产调用点 + 软依赖降级）
- **B 删 `_call_llm` 段**（摘 Anthropic 实调，保留 `render_hao_narrative(call_llm=False)` 的 prompt 组装）
- **C 改造 `_call_llm` 走 `MANGPAI_LLM_*`**（能力保留 + 通道统一）

## 分析要求（逐项给结论，别只做综述）

1. **影响面量化**：每条路的具体改动点（文件:行号）、测试改动数、是否触碰降级契约/对外行为
2. **对外使用者视角**（判事基准=「任何人自由选 LLM 且不影响本机」）：三条路各自让使用者看到什么？**B 删掉后仓库是否真的零 provider 硬绑**（全仓扫一遍 anthropic/openai/厂商 SDK 引用，别只看 narrative）？C 是否引入"两套配置入口"的新困惑？
3. **隐式依赖排查**：`call_llm` 参数是否被 `feishu`/`engine`/`llm_channel` 以其它形式使用？`render_hao_narrative` 是否有调用方传 `call_llm=True`（grep 全仓含 `output/`、`scripts/`）？删除是否破坏 `test_narrative` 的既有覆盖意图（那些测试测的是"数字校验/降级"，还是"Anthropic 调用"本身）？
4. **是否有第四选项**（如：保留但改为"可选插件式"、`_call_llm` 降级为不调 SDK 只返回 prompt、文档化而非删除）——你独立判断，可以推翻选项集
5. **性价比**：这三条路值不值得动？如果推荐"不动"，也要给出未来触发条件（什么情况下必须动）
6. **推荐**：明确选一条 + 理由 + 若实施的最小改动清单（**本批不实施**，只出清单供用户拍板）

## 红线
- **只分析不改码**（`git status` 必须保持干净——除非你写报告到 memory/ 目录）
- 不调外部 API
- 引用代码位置给行号，结论要有 grep/读码依据
- 汇报 400 字内（推荐路线 + 核心理由 + 改动清单要点）
