# ⚠️ V3 留出集 · 严禁用于修引擎 ⚠️

`cases.yaml`（215 例）是郝金阳/段建业断例的**留出集（held-out）**：
只用于评估引擎，**任何引擎修改（规则、阈值、权重、模板）都不得参考本文件中的断语**。
训练侧已校准案例在 `../trainset/cases.yaml`（23 例），那里才是修引擎可以看的。

## 构成

| 集 | 例数 | 内容 |
|---|---|---|
| heldout/cases.yaml | 215 | 两书全部未校准断例（授课教程 + 50期资料） |
| trainset/cases.yaml | 23 | calib10（zhenbao-01/04/05/09/10/12/14a/14b/23a/23b）+ b67 书例 13 例 |

污染路由规则：凡出现在 `calib_assertions.yaml`（10 例）或 `backtest/regression67.py`
（67 例）的同盘案例一律入 trainset，不入 heldout（性别无关匹配，零泄漏已验证）。

## 维度覆盖（heldout 215 例，共 476 条维度断语）

官命 66 · 职业 94 · 应期 124 · 健康 40 · 婚姻 65 · 财命 70 · 子息 17

verdicts 只标注原文明文断语的维度；raw_quote 为原文逐字摘录（OCR 原样）。
2026-07-27 金标准验证（462→476 条：删误标 10、修偏差 16、补漏标 51、学风非凡整例移 dropped），
逐条清单见 `verification_report.md`。

## 管线（可复跑）

```
extract_cases.py   # 两书扫描 乾造/坤造 标记 → 375 候选（叠排/inline/双造/无标记块，OCR纠错+六十甲子校验）
curate.py          # 跨文件去重 → 293；标记 calib10/b67 污染 → review.txt
annotations_*.py   # 人工逐例读原文审定（全量 293 例读完）：KEPT/DROP/PHANTOM/CALIB10/B67
build_yaml.py      # 路由 + 校验（未路由/孤儿即中止）→ cases.yaml × 2 + dropped.txt
verify_heldout.py  # 每例过 MangpaiEngine.compute_all() 不炸 + 干支合法性/echo 校验
```

当前状态：`verify_heldout.py` → heldout 215/215 ✅、trainset 23/23 ✅。

## 已知边界

- 梁启超两版并存（li181 月干丙 / qi37 月干甲，原书两处异文），id 已标 A/B。
- `subjective/xiangfa_ops.py:1361-1364` 注释引用过两例书例原则（庚己甲己/子卯辰巳、
  张之洞丁戊戊戊/酉申申午）——仅为原理引注非拟合目标，仍留 heldout。
- OCR 别字按原文保留（己/已/巳、戍/戌等在干支位已位置感知纠错；正文不动）。
- 8 例无断语维度太薄、六合彩 4 例、时辰存疑 2 例等共 59 例弃用，理由见 `dropped.txt`。
