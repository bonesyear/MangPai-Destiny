# Kimi 任务：修复批 F5 · zeishen 传导断口（滤 auxiliary）+ gongfei

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F5 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批2（P0：zeishen_bushen.py:602-610 消费 work_actions 补 target_wx_set 时未过滤 auxiliary——丁克庚宾位天干克把「金」塞进制局目标集→原神同制→误净；书 6122-6126「制之不净达不到四层功」）、批3（传导实锤：gongliang 三条消费通道结构性开放 + zhi_jing/zeishen_jing_zhi 同帧矛盾）、批8（gongfei：auxiliary 排除违背书「辅助功神仍是功神」理象学 6008-6010，经 L5 gate/废神激活/应期叙事三路扩散）
3. **Kimi 规划 F5 风险点**：zeishen 修后 gongliang 三通道 + xiangfa_ops + caiming 两处豁免方向反向（保守漏豁免→修后部分案例可能获得净制上浮→heldout 翻转风险，须全量 diff 审查）；gongfei fei_shen 集合变→verify_dayun 断言 + 叙事
4. 汇报 300 字内

## 任务（两件）
1. **zeishen 滤 auxiliary**（核心断口，一行级）：
   - `zeishen_bushen.py:602-610` 补 target_wx_set 时过滤 auxiliary（仅主位/日干参与的真做功）
   - 预期：蒋介石 zb 误净 → 不净（书 6122-6126）；zhi_jing/zeishen_jing_zhi 同帧矛盾消除
   - **全量 diff 审查**：修后 gongliang 三通道（无制采纳/bao 与金字塔门/不净覆写解封顶）+ xiangfa_ops + caiming 两处豁免——哪些案例获得/失去净制上浮，逐案例审查书锚合理性
2. **gongfei 修正**：auxiliary 排除 → 「辅助功神仍是功神」（理象学 6008-6010）；fei_shen 集合变化后 verify_dayun 断言 + dayun/liunian/gongliang 叙事同步

## 书例哨兵（先红后绿）
- 蒋介石（zb 净→不净预期，书 6122-6126）
- 李嘉诚（净制巨富——**不得误伤**！）
- 保尔森（净制——不得误伤）
- gongfei 书例（辅助功神仍是功神）

## 红线
- **heldout 财命 46✅ 不回退**（66.67%）、官/职不退化
- **巨富三锚（李嘉诚/保尔森/奥纳西斯）不得降**——净制上浮修正可能影响，重点审查
- 书锚铁律：每处改动带书明文行号
- 修 A 破 B：gongfei 与 zeishen 是不同模块，分开验证传导

## 验证（全部通过后回报，300 字内）
1. 书例哨兵：先红后绿记录
2. `python3 mangpai/verify_mangpai.py` — 432 全绿
3. `python3 -m pytest mangpai/tests/ -q` — 全绿
4. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260817_f4.json` — heldout 翻转明细（每个列原因，重点：巨富三锚）
5. 67 例 + famous + calib — 0 回归
6. 双 seed 一致

## 汇报（300 字内）
两件改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细（巨富三锚确认）
