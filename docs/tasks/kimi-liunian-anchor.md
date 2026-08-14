# Kimi 任务：4 个 liunian xfail 缺口 · 书锚搜索与修复评估

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md`（§4 liunian 九语义、§5 书锚清单、§7 关键坑——尤其「规则改动须 ≥2 书锚」门槛）
2. **读归档** `/root/.claude/projects/-root-metaphysics/memory/kimi-yingqi-mining-2026-08-14.md`（§5 追加：16 条断言 + 4 xfail 明细）
3. 汇报 300 字内；分析写归档（追加到 kimi-yingqi-mining-2026-08-14.md §6）

## 背景：4 个 xfail 引擎缺口
| xfail | 缺口 | 现有锚 |
|-------|------|--------|
| 合去 | 流年字被合去（离异等反向语义）未建模 | 1 条 |
| 合绊 | 运-局合绊不入流年分类器 | 方向对但书证不足 |
| 冲去 | 流年冲去定向不触发（ch13） | 1 条 |
| 冲破夫宫 | 辰戌冲坏夫宫 | 1 条 |

## 任务
1. **搜索书锚**：在 `mangpai/docs/duan-books/` 全部 txt（理象学/研究版/初级/中级/高级/中高级/授课教程）搜这 4 种语义的书明文断语：
   - 合去类：「合走」「合去」「被合」「合绊」「绊住」「合住」（配偶星/财/官被合）
   - 冲去类：「冲去」「冲走」「冲散」
   - 冲破类：「冲破」「冲坏」「冲崩」+ 夫宫/婚姻上下文
   - 用 grep 系搜索 + 读上下文确认是断语案例（非理论阐述）
2. **逐缺口评估**：每个缺口收集 ≥2 条书明文（原文 + 文件 + 行号 + 盘例）
   - 书锚够（≥2 条语义明确的断语案例）→ 修 liunian.py（书锚驱动，仿第三十六批三规则风格）
   - 不够 → 确认收档（记录缺口无书证，保持 xfail）
3. **修复评估**（若书锚够）：修法须与现有 classify_chong_semantic/he_semantic 架构一致（gender 参数模式），不得破坏 12 条已 pass 断言

## 红线
- 他模块零改动；heldout 零翻转（liunian 独立）
- 12 条已 pass 断言不得回归
- 无书锚不修（宁可收档）

## 验证（若修了代码）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 全绿（xfail 数应减少或保持）
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_d.json` — heldout 零翻转

## 汇报（300 字内）
四缺口各搜到几条书锚（原文+出处）+ 修了几个（哪些 xfail→pass）+ 收档几个 + 验证数字
