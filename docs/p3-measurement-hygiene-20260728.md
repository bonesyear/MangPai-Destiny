# P3 · 测量卫生方案（纯分析，不落地）

- 日期：2026-07-28（第五批：B类precision + C类功量 + D类从格 之配套分析项）
- 性质：只出方案，不改代码。落地须另起批次并过全量验证。
- 上游：`blind-gap-rootcause-2026-07-28`（34%名义差距分解）、`blind-gap-4fix-2026-07-28`（P0-a 双轨）。

## M1 复跑不确定性（evaluator nondeterminism）

**现象**：blind_eval 两次全量跑出现 1 例不一致（shouke-qi20-李连英
caiming_adjust 下浮↔上浮，打分未变）。疑引擎内 set 迭代序
（`for pos in involved_positions` 等）导致同分不同文。

**方案**：
1. 静态排查 subjective/ 与 objective/ 中 `for x in <set>` 且迭代顺序影响
   输出文本/首选候选的点位（gongliang involved_positions、caiming views、
   zhiye evidence、yongshen hits），改 `sorted(...)`（纯排序，不改语义）。
2. 验证器侧加 `--seed` 说明：CI 跑 `PYTHONHASHSEED=0 python3 blind_eval.py`
   作为确定性门禁；现有 `--diff` 增加「文本抖动」段（score 不变但
   engine 字段变者单列），>0 即视为卫生失败。
3. 预期工作量：小（排查~20 处 + 排序），风险：低（排序不改变量，仅稳定序）。

## M2 训练集/留出集构成倒挂（distribution skew）

**现象**：训练集财命中「破财/贫」占 36%，留出集仅 6%；留出集金标 merchant
28%（最大类）而引擎输出 merchant 曾 1/57。「0 回归」门禁只看训练集，
看不见受害类（富/巨富 39% 的留出集主导类）。

**方案**：
1. 训练集扩容（K1 后续）按「领域 × 断语性质（层级/事件/身份）」分层配额，
   每层与留出集边际分布对齐（允许训练集仍偏书例，但每格 ≥5 例）。
2. 回归门禁从「总分 0 回归」升级为「分组 0 回归」：按 verdict 首词
   （巨富/富/小康/平/贫/破财/凶）分组，任一组 acc 下降即判回归——
   本批次 B类修复正是靠此视角发现「R3 对富/巨富组误触」。
3. 每批次的 backtest 报告强制附分组表（一行一格），入 CHANGELOG。

## M3 小样本噪声与置信区间

**现象**：训练集财命 n=11（CI≈[28,79]）、留出集财命 n=70（CI≈[12,31]→
本批次后 [26,49]）。点估计的 1-2 例翻转即可移动 2-5pts，跨批次比较
易被噪声主导。

**方案**：
1. blind_eval 汇总行输出 Wilson 95% CI（acc±half），`--diff` 仅当
   「|Δacc| > 两 CI 半宽之和」才判显著改善/退化，其余记「噪声带内」。
2. 验收门槛以 CI 下界计（如「财命 CI 下界 ≥ 27%」比「点估计 ≥31%」稳健）。
3. 翻转明细按 delta≥2（✅↔❌）与 delta=1（±⚠️）分列，主结论只依赖前者。

## M4 rubric 机械口径的已知偏差（备案，不建议改）

**现象**：
- 「凶向标记一律❌」对贫/平断语过杀（li101 穷命：tier 对、语义对，
  仅因 summary 带「下浮封顶」记 ❌）；本批次 R2/R3 precision pass 后
  该偏差面已大幅收窄，但机制仍在。
- 职业桶关键词粗口径（「武」命中武断语亦命中「武侠」类假阳性风险）。
- 层级断语「平」按小康计、事件断语需 has_yunsui 判轨——两处隐式约定。

**方案**（备案式，冻结 rubric 训练侧口径一致性优先）：
1. rubric 版本化：score_caiming/score_zhiye 顶部注 `RUBRIC_VERSION`；
   任何口径改动必须走 `--rescore` 重设基线并写 CHANGELOG（沿用本批
   「命名对齐」先例）。
2. 报告增列「标记命中但 tier 正确」计数（凶向标记的伪 ❌ 面），作为
   凶向 precision 的长期度量，不参与 acc。
3. 不建议将「贫+凶向」改为 ✅——那会把真漏检（凶命无凶向）洗白，
   当前严口径对方向层是正向压力。

## M5 快照与基线管理

**现象**：前后快照存 /tmp（before.json/after2.json），会话临时、不可复现；
famous_baseline.json 曾需 `git add -f`（.gitignore 有 *.json）。

**方案**：
1. `tests/heldout/snapshots/` 目录：每批次落 `YYYYMMDD_<batch>.json`
   （git add -f），blind_eval 增 `--baseline` 直接读最新快照做 diff。
2. .gitignore 加 `!tests/**/snapshots/*.json` 例外，与 famous_baseline 同款。
3. 快照附 meta 块（git sha、pytest/853 状态、CI），防「拿错基线」。

## M6 报告口径统一（双轨后）

**现象**：P0-a 后存在原局轨/全量轨两套 tier；历史报告（m1 盲测报告等）
为单点口径，直接对比会把「口径差」读成「引擎差」（18pts 训练集通胀
即由此而来）。

**方案**：
1. 一切对外数字按「原局轨 acc（层级断语）/ 事件轨 acc（流年断语）」
   分行呈现；单点混报视为报告缺陷。
2. CHANGELOG 数字一律带口径后缀（如「财命 37.1%（原局轨）」）。
3. trainset/heldout 同表呈现（训练-留出 gap 本身即泛化监控指标，
   本批次 63.6% vs 37.1%，gap 26pts 较上批 36pts 收窄）。

## 优先级

| 项 | 价值 | 工作量 | 建议批次 |
|---|---|---|---|
| M1 复跑确定性 | 高（卫生底线） | 小 | 下批首选 |
| M5 快照入 git | 高（可复现） | 极小 | 下批首选 |
| M2 分组门禁 | 中-高（防受害类） | 中 | 随 K1 扩容 |
| M3 CI 报告 | 中（防过拟合噪声） | 小 | 顺手做 |
| M6 双轨口径 | 中（防误读） | 极小（文档级） | 立即 |
| M4 rubric 备案 | 低-中 | 冻结为主 | 不主动改 |
