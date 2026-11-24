# 开发评估集（历史 heldout，已失去盲测效力）

`cases.yaml`（214 例）是郝金阳/段建业断例的历史留出目录。审查已确认其中案例被用于规则修复、单测钉值和调参，因此从 2026-11-18 起如实称为**开发评估集**：结果只作回归与开发参考，不再宣称盲测或零泄漏。
训练侧案例在 `../trainset/cases.yaml`（295 例）。在新的独立数据来源出现前，不另造“盲测”成绩。

## 构成

| 集 | 例数 | 内容 |
|---|---|---|
| heldout/cases.yaml | 214 | 两书全部未校准断例（授课教程 + 50期资料） |
| trainset/cases.yaml | 295 | calib10（zhenbao-01/04/05/09/10/12/14a/14b/23a/23b）+ b67 书例 + 扩容批次转入的已校准/已参考断例 |

污染路由规则：凡出现在 `calib_assertions.yaml`（10 例）、`backtest/regression67.py`
（67 例）或 `backtest/famous_cases.py`（23 名人例）的同盘案例一律入 trainset，不入 heldout
（性别无关匹配）。历史“零泄漏”声明已被后续审查推翻；本目录只保留回归价值，不再作为无污染证明。

旁路说明（H-fix-8 备案，H9 P1 结案）：`annotations_heldout.py` 的 `MANUAL` 4 例
（qi04-双胞胎弟弟丧妻 / qi04-阮玲玉 / qi14-美容师 / qi04-卜文命学禄当财）系排版未被提取器捕获的
手动补录，由 `build_yaml.py` 直接路由进 heldout/cases.yaml，**不经过** `merged.json`/`candidates.json`
——这是显式旁路而非数据漂移；四例均带 source 行号锚与原文逐字 quote。

## 快照基线

`snapshots/LATEST` 指针 = 当前基线快照（`blind_eval.py --baseline latest` 可解）；
快照链总账与归档说明见 `snapshots/README.md`。

## 维度覆盖（heldout 214 例，共 472 条维度断语）

官命 65 · 职业 94 · 应期 123 · 健康 39 · 婚姻 64 · 财命 70 · 子息 16

verdicts 只标注原文明文断语的维度；raw_quote 为原文逐字摘录（OCR 原样）。
2026-07-27 金标准验证（462→476 条：删误标 10、修偏差 16、补漏标 51、学风非凡整例移 dropped），
逐条清单见 `verification_report.md`。

## 管线与手工扩容

```
extract_cases.py   # 两书扫描 乾造/坤造 标记 → 375 候选（叠排/inline/双造/无标记块，OCR纠错+六十甲子校验）
curate.py          # 跨文件去重 → 293；标记 calib10/b67 污染 → review.txt
annotations_*.py   # 人工逐例读原文审定（全量 293 例读完）：KEPT/DROP/PHANTOM/CALIB10/B67
build_yaml.py      # 路由 + 校验（未路由/孤儿即中止）→ cases.yaml × 2 + dropped.txt
verify_heldout.py  # 每例过 MangpaiEngine.compute_all() 不炸 + 干支合法性/echo 校验
```

当前状态：`verify_heldout.py` → heldout 214/214 ✅、trainset 295/295 ✅。
（上文管线段的 375/293 为 2026-07 初次构建时的历史计数；扩容批次多为手工追加，merged.json/candidates.json 不入库，不宣称全量可复跑。）

## 已知边界

- 梁启超两版并存（li181 月干丙 / qi37 月干甲，原书两处异文），id 已标 A/B。
- `subjective/xiangfa_ops.py:1361-1364` 注释引用过两例书例原则（庚己甲己/子卯辰巳、
  张之洞丁戊戊戊/酉申申午）——仅为原理引注非拟合目标，仍留 heldout。
- OCR 别字按原文保留（己/已/巳、戍/戌等在干支位已位置感知纠错；正文不动）。
- 8 例无断语维度太薄、六合彩 4 例、时辰存疑 2 例等共 59 例弃用，理由见 `dropped.txt`。
