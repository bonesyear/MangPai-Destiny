# 任务：优化「仓库日报」cron 的输出格式（只产出设计，不改代码）

## 背景

有一个 Hermes cron job：**`6ba07ff54451`「仓库日报 · MangPai-Destiny（每日18:00）」**，每天 18:00 运行两步：

1. 先跑数据采集脚本 `/root/.hermes/profiles/metaphysics/scripts/repo_daily_report.py` —— 输出纯文本，其 **stdout 会被注入 agent 的提示**；
2. agent（LLM）按 cron 的 **prompt** 把数据写成日报，投递到飞书（本对话）。

用户反馈：**日报的语句不够规范、不够格式化、不够易读** → 本次要优化。

## 现状材料

### A. 当前 cron prompt（全文，待优化对象）

```
你是仓库日报助手，投递目标是飞书，中文、结构化、简短。

数据来源：本任务的 script（repo_daily_report.py）每次运行时会把最新数据注入本次提示的上文（仓库元数据 / issue 与 PR 列表 / 最近 push 时间 / 最近 14 天 clone 流量；clone 段需 token，缺失时会标注不可得）。你还看得到自己**上一次运行**的输出（continuity），用它做对比。

请输出一份日报，四块：
1. **issue / PR**：当前 open 数量（与总数量）；与上次相比有无**新增**（编号 + 标题 + 作者）；若新增了 open issue，附正文摘要并问「需要回复吗？」
2. **最近 push**：取 `last_push`（UTC），**换算成北京时间**（CST = UTC+8）显示
3. **最近 clone**：取 `latest_clone_day` 的日期与当天次数/独立数；必须标注「GitHub 仅提供按天聚合，无单次精确时间」；若流量相比上次异常（明显升高/降低）点一句
4. **星级**：当前 stars，以及与上次相比的变化（如 5 → 6）；无变化就写「无变化（N）」

若某段数据缺失（如无 token 导致 clone 不可得），直接说明，不要编造。

硬边界：
- 只读：不要对 GitHub 做任何写操作（不改仓库、不回复 issue、不建 PR），除非用户在交互会话中明确要求。
- 只为 bonesyear/MangPai-Destiny 巡检；其它仓库一概不碰。
```

### B. 数据脚本的输出样例（实测 stdout，agent 看到的就是这个）

```
repo=bonesyear/MangPai-Destiny
stars=5 forks=2 watchers=0
last_push=2026-09-19T02:00:48Z
last_updated=2026-09-25T10:08:09Z
issues_total=1 open=1 | prs_total=0 open=0
  #1 [issue] open | how to download the skills | by yoneakl | comments=1 | created=2026-09-17
clone_traffic_14d: total=365 uniques=157
  2026-09-10 count=16 uniques=8
  2026-09-11 count=16 uniques=9
  2026-09-12 count=22 uniques=13
  2026-09-13 count=5 uniques=5
  2026-09-14 count=1 uniques=1
  2026-09-15 count=3 uniques=3
  2026-09-16 count=2 uniques=2
  2026-09-17 count=48 uniques=22
  2026-09-18 count=180 uniques=72
  2026-09-19 count=63 uniques=33
  2026-09-20 count=4 uniques=4
  2026-09-21 count=3 uniques=3
  2026-09-22 count=1 uniques=1
  2026-09-23 count=1 uniques=1
latest_clone_day=2026-09-23 (count=1 uniques=1)
```

无 token 时脚本末段会变成一行：`clone_traffic: 不可得（未提供 GITHUB_TOKEN；traffic API 需 push 权限）`。

### C. 现有日报样例

读 `/root/.hermes/profiles/metaphysics/cron/output/6ba07ff54451/` 目录下**最新**的 `.md` 文件（那就是 agent 的实际产出与投递内容；请自己读，不要假定）。历史上只有一份使用**旧 prompt** 的样例（结构是散文式段落，正是"不够规范"的来源）。

### D. 相关文件（可读）

- 数据脚本源码：`/root/.hermes/profiles/metaphysics/scripts/repo_daily_report.py`
- 历史输出目录：`/root/.hermes/profiles/metaphysics/cron/output/6ba07ff54451/`

## 任务

产出一份**可直接替换使用的 cron prompt 全文（v2）**，使日报满足：

1. **结构固定**：每天同一套小节标题与字段顺序（便于扫读、便于逐日对比）
2. **格式规范**：飞书 Markdown（粗体 / 行内代码 / 列表 / 必要时代码块）；关键数字醒目；字段名统一；**单位与时区明确**（UTC vs 北京时间）
3. **语言精炼**：短句、无废话、无重复；术语写法统一（例如统一写 `open issue` 还是「未关闭 issue」，全篇一致）
4. **可读性优先**：一眼看出「有无变化 / 有无待办」；变化项前置或加醒目标记（如 🆕 新增、⚠️ 需处理）
5. **边界不变**（必须原样保留这些硬约束）：只读（不对 GitHub 写任何东西）、只为 `bonesyear/MangPai-Destiny` 巡检、数据缺失时直说不可得而**不得编造**、clone 只有按天聚合（须标注粒度）
6. **自包含**：cron 运行时没有任何对话上下文，prompt 必须自带全部说明
7. **稳定**：不依赖用户输入；每次输出结构一致（同一格式骨架）

## 交付

写入 **`/root/.hermes/profiles/metaphysics/cache/scratch/cron_report_prompt_v2.md`**，包含三部分：

1. **优化后的 prompt 全文** —— 用 ``` 代码块包住，便于整段复制粘贴（**这是最重要的交付物**）
2. **设计说明** —— 每条设计决策对应解决了什么可读性问题（逐条，简短）
3. **效果示例** —— 用材料 B 的真实数据，套用新 prompt 手写一份日报样例，展示最终长什么样

## 硬性约束

- **不改任何代码**（`repo_daily_report.py` 与项目文件一律不动）；本次只产出设计文档，prompt 由 Hermes 应用
- 若你认为**脚本输出**（材料 B）也该调整以配合新格式，请在文档里单独开一节「建议的脚本改动」写清改法（**写建议即可，不要真改**）
- 文档中不得出现任何真实凭证、token、本机私有路径
- 不要建议引入第三方依赖或需要额外安装的东西
- 不要建议新增需要用户输入/确认才能完成的步骤（cron 是自主运行的）

## DoD（逐项报告）

- [ ] v2 prompt 全文可直接粘贴使用（自包含、含全部硬边界）
- [ ] 附「用真实数据套新格式」的日报示例一份
- [ ] 设计说明逐条对应可读性问题
- [ ] 未修改任何代码或仓库文件（可用 `git status` 自证）
- [ ] 交付文件已写入上述指定路径
