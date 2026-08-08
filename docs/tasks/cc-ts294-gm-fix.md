# K3 任务：294 例训练集修复 · 官命批（veto 链级放宽，九规则栈）

## ⚠️ 执行指引
1. 分析归档：`/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-guanming-2026-08-08.md`（40 例逐例总表 + 模拟验证：九规则组合栈 +21 翻正 0 误伤，官命 65.22%→83.5% 上限）
2. 基线：trainset 294 例 官命 65.22%（75✅/40❌）；heldout 官命 56.06%（37✅）
3. **先改代码，后统一验证**；汇报 300 字内
4. 铁律：留出集只评估不反推；规则改动必须有书锚或训练集锚

## 任务：官命 veto 链级修复（九规则组合栈，按归档模拟清单执行）
- 主矛盾：fn 漏判 28 : fp 误判 12——**veto 链过严误杀真官**（G6 官被制空亡过火 4fn、R1 从弱比劫夺财 veto 误杀 4fn、veto 链共误杀 12fn）
- 修复原则：**在官命 veto 链级修（guanming.py veto_reasons 消费侧），不动底层检测器**——财命 52.21% 零风险
- 九规则栈：G6 官被制空亡收窄（官杀透干不得按支空制死论）、R1 比劫自身被官制者不 veto、R2/R3/N2/岁运反局 各收窄（按归档模拟验证的判别边界）

## ⚠️ 否决项（归档明确，切勿实施）
- **方向门（主制宾才计）不可加**——误伤岳飞/蒋介石/周恩来等 10 个 ✅ 锚，段氏印类 combo 不按主宾

## 红线
- **heldout 官命 37✅ 不回退**（56.06% 底线）、财命/职业不退化
- trainset 官命 75✅ 不回退，**❌ 应明显减少**（预期 40❌ → ~20-25❌）
- fp 侧不得恶化（李昌镐/李嘉诚等 famous fp 锚核验安全）
- 与既往批锚不冲突（批13 famous 4 例、G0-G7 收口体系）

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 473 passed
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline snapshots/20260808_p.json` — heldout 零翻转（或只增不减）
4. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only` — trainset 官命 ≥65.22% 且 ❌ 减少（新旧对比）
5. 67 例回测：0 回归
6. famous + calib：0 回归（famous 官命 10/10 必须保住）

## 汇报（300 字内）
改动/行号/diff 摘要（九规则逐条）+ 验证 6 项数字 + trainset 官命翻转明细（fn 修复列表）+ fp 无损确认
