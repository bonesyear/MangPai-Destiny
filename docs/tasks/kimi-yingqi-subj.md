# Kimi 任务：寿元域样本挖掘（yingqi_subj 模块验证）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md`（§4 yingqi_subj 相关、§5 书锚、§6 备案）
2. **读归档** `/root/.claude/projects/-root-metaphysics/memory/kimi-yingqi-mining-2026-08-14.md`（§5：~20 条死亡应期走穿/破禄/寿元星机制，超 liunian 九语义，归 yingqi_subj 域）
3. 汇报 300 字内；分析写归档（追加 §7）

## 背景
矿存 80 条里 ~20 条死亡应期样本（穿/破禄/寿元星机制）——上一批只评估了 liunian 九语义直用部分，这批是「超九语义」域：穿倒食神损寿元/破禄/禄到位。需评估 yingqi_subj（寿元/应期主观层）模块能否承接。

## 任务
1. **定位样本**：从归档 §5 + `/tmp/g3_dropped.json`（矿存 80 条）提取全部死亡/寿元类样本（~20 条：八字+书明文断语+运岁锚+行号）
2. **机制分类**：逐条标注机制——穿（穿倒食神损寿元）/破禄（禄星被破）/禄到位（寿元尽时禄至）/寿元星（食伤为寿元星被坏）等，读 raw quote 逐条确认
3. **对照引擎**：检查 yingqi_subj 模块（或相关寿元逻辑）现状——这些机制是否已建模？差距在哪？
   - 已建模 → 用样本建断言验证（仿 test_liunian_yingqi.py 风格）
   - 未建模 → 评估书锚是否够（≥2 条/机制）：够→修；不够→备案收档
4. **产出**（写归档）：样本清单（按机制分组）+ 引擎现状对照 + 每机制书锚数 + 建断言 or 收档结论

## 红线
- 他模块零改动（除非书锚够且修的是 yingqi_subj 自身）
- 不碰 heldout；死亡/寿元断语是敏感话题——**只做推演验证，不做预测断言**
- 无书锚不修

## 验证（若建了断言/改了代码）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 全绿
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_e.json` — heldout 零翻转

## 汇报（300 字内）
样本数/机制分组 + 引擎现状对照（已建模 or 缺口）+ 书锚数 + 建断言 or 收档结论 + 验证数字
