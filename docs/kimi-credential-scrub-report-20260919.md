# 安全整改批报告：凭证清除 + 全仓复扫（2026-09-19）

> 任务书 = `docs/tasks/kimi-credential-scrub.md`。红线遵守：本报告不含任何 key 明文。

## A. 泄漏文件删除

- `git rm docs/cc-volcengine-config-backup.md` 已执行（工作区+索引同步删除）。
- **引用检查**：全仓 grep `volcengine`/`cc-volcengine`/该文件名，唯一命中 = 本批任务书 `docs/tasks/kimi-credential-scrub.md`（引用形态为任务描述，且 key 已打码 `ark-xxxx<REDACTED>`），**无代码/文档依赖**，零残留。

## B. 全仓凭证复扫（含未跟踪/忽略目录）

扫描范围：git 跟踪文件（git grep）+ 未跟踪文件（`git status --porcelain` 全量=无未跟踪）+ `output/` 全目录递归 + 工作区全量递归（排除 .git）。

| 命中 | 判定 | 打码片段 |
|---|---|---|
| （已删文件）docs/cc-volcengine-config-backup.md:9 | **真凭证（已删除）** | `export ANTHROPIC_API_KEY=ark-xxxx<REDACTED>` |
| .env.example:13/64/65 | 占位符 | `MANGPAI_LLM_API_KEY=your-a<REDACTED>` 等 `your-*` 模板 |
| mangpai/feishu/README.md:40 | 占位符 | `FEISHU_VERIFICATION_TOKEN=xxx`、`your-*` |
| mangpai/tests/test_s1_llm_config.py:182/185 | 测试假值 | `"sk-file"` / `'sk-legacy-name'`（构造 fixture，非真 key） |

模式覆盖：`ark-*`、`sk-{16,}`、`API_KEY/TOKEN/SECRET/PASSWORD=*`、`ghp_`、`gho_`、`AKIA`、`PRIVATE KEY`。历史侧 `git log -S 'ark-'` 复核：真 key 仅经初始提交由该文件引入（bb4decf/0254e22 命中为 `lark-oapi`/任务书打码引用，非凭证）。

**真凭证（现存于工作区/索引）= 0。** 其余命中全为占位符/测试假值，无「需人工确认」项。

## C. 暴露范围评估（只报告，不实施）

1. **暴露区间**：该 key 仅由初始提交 `878f3ce`（2026-07-15）引入，此后 244 提交中**无任何提交修改过该文件**（`git log --all --follow` 单命中），key 明文原样存活于 2026-07-15 → 至今的全部历史，公开 GitHub（bonesyear/MangPai-Destiny）暴露约 2 个月。
2. **非初始提交**：无。该文件从未被修改，只存在于「初始提交引入→本批删除」两个事件点。
3. **历史重写建议**：**结论=轮换后不需要**。前提（用户即将轮换该 key）成立时，历史中的旧 key 轮换后即失效，攻击价值归零，`git filter-repo`/BFG 无实际收益。代价（若做）：全仓 244 提交 SHA 全变 → 所有 fork/clone/本地副本失效须重新克隆；快照 `_meta.git_sha` 链（49 份基线溯源）全部断链；须 force push 且任何已流出的旧历史副本仍含 key（公开仓两个月，无法保证无镜像）。**仅当 key 无法轮换时才值得付此代价**。本批未执行、未 force push。
4. **其他「本机工具环境内容」核查**：docs/ 与根目录无同类备份/配置类文件。现存命中仅为：`.env.example`（标准模板，合规）；`docs/tasks/kimi-s1-llm-config.md`、`docs/tasks/kimi-shareability-assessment.md`（配置设计任务书，含端点 URL 与变量名讨论，无凭证）；各文档中 `~/.claude/...` 路径为归档**引用**（KB 惯例），非环境内容本体。**清单=仅此 1 个文件（已删）**。

## D. 验证（六件套，文档删除批实证零影响）

- `verify_mangpai.py` 432/432 ✅；`verify_dayun.py` 70/70 ✅；`verify_layer1.py` 64/64 ✅（sxtwl 在 3.14 环境，用 /usr/bin/python3 跑）；`verify_layer3_checkpoint.py` 20/20 ✅
- `pytest mangpai/tests/` = **1129 passed + 1 xfailed**（与 KB 口径一致）
- blind_eval vs `snapshots/20260918_t1.json`：**heldout/trainset 0 翻转、文本抖动 0**（快照写 /tmp，未入库）
- `scripts/check_layering.py` 通过（66 文件无反向依赖）+ `scripts/check_typing_imports.py` 通过（181 文件 0 处）

改动范围核对：`git status --short` = 删除 `docs/cc-volcengine-config-backup.md` + 新增本报告。
