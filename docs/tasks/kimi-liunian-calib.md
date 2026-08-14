# Kimi 任务：liunian 应期语义断言集（16 条 calib 式）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md`（§4 liunian 九种语义、§5 书锚、§6 备案）
2. **读你昨天的归档** `/root/.claude/projects/-root-metaphysics/memory/kimi-yingqi-mining-2026-08-14.md`（含 16 条直用样本全表）
3. 汇报 300 字内；过程结论可追加进归档

## 任务：建 liunian 冲/合语义 calib 断言集
1. 从归档取 16 条样本（合四种 9 + 冲四种 9 = 18 条里筛 16 条直用；冲旺无样本保持缺口）
2. **逐条打标机制**：每条明确语义类型（合留/合去/合绊/合动/冲动/冲开/冲去/冲破），读 raw quote 确认（正则筛会混入非事件句，须逐条人工判——这是你的活）
3. **建断言测试**：新文件 `mangpai/tests/test_liunian_yingqi.py`：
   - 每条：八字 + 运岁锚 + 期望语义（书判）
   - 调 `analyze_liunian_mangpai`（或盲测评估路径），断言输出的 chong_semantic/he_semantic 符合书判
   - 仿 calib_assertions 风格（书锚注释每行）
4. **跑断言**：pytest 看 pass/fail
   - **fail 的逐条分析**：是引擎 bug（liunian 语义判定与书诀不符）还是样本/打标问题——区分报告
   - fail 引擎 bug 类：修 liunian.py（书锚驱动）；样本问题类：修正断言
5. 断言集入测试套件（469 → 新数字）

## 红线
- **引擎其余模块零改动**（只动 liunian.py 若确有 bug）
- heldout/三维零影响（liunian 测试独立；若 liunian 改动，跑 blind 确认 heldout 不退化）
- 冲旺语义无样本——**勿造样本**

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 全绿（含新断言文件）
3. 若 liunian.py 有改动：`python3 mangpai/tests/heldout/blind_eval.py` — heldout 零翻转
4. 报告断言 pass/fail 明细（16 条逐条）

## 汇报（300 字内）
断言集文件/条数 + pass/fail 统计 + fail 分析（引擎 bug vs 样本）+ liunian 改动摘要（若有）
