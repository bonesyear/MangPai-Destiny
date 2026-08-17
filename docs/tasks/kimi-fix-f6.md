# Kimi 任务：修复批 F6 · gongliang（阎锡山解锁 checkpoint + 奥纳西斯制库门）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F6 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批3（gongliang P0-1 奥纳西斯书断 4 层引擎 L2 三重漏计：制库+2 以 san_he_formed 为门书 6037 无三合条件且两书例均非三合/杀库作功无路径/方局包制检不出；P0-2 阎锡山书断「三层强一点」引擎 L4 自我撤销校准：:799 降 +2、:853-862 又化用高层+1 加回，三重背离书义 + **verify_layer3_checkpoint.py:99 以 L4 反锁**）
3. **Kimi 规划 F6 风险点**：gongliang level → guanming grade 传导（阎锡山 grade_map 与 F12 联动）；checkpoint 反锁教训（阎锡山 L4 被工程资产固化）
4. 汇报 300 字内

## 任务（两件）
1. **阎锡山校准去锁**（理象学 7182-7188 纯制局读法 + 授课 38 期「旺忌神弱制」非从杀）：
   - gongliang.py:799 降 +2 校准保留（本身是对的），**:853-862 化用高层+1 收窄**（杀党≥5 触发条件加书锚约束）——去此 +1 阎锡山 3.5→L3 合书
   - **verify_layer3_checkpoint.py:99 反锁 L4 → 改 L3**（checkpoint 与书锚正面冲突，以书为准）
   - 检查是否有其它盘被该「化用高层+1」错误加层（全量扫描）
2. **奥纳西斯制库门**（书 6470-6474「制库两层功，杀库作功一层功，加包制一层功，有四层功量」）：
   - 制墓库+2 的 san_he_formed 门 → 去三合条件（书 6037 无三合条件；两书例奥纳西斯丑未冲/克林顿戌刑丑均非三合）
   - 「杀库作功」补规则路径（7f 墓库属性 yuanshen_hit is None 门修复）
   - 方局包制（巳午未）检出补足
   - 奥纳西斯 L2 → L4 预期；**注意 caiming 制库得财 floor 兜底与其关系（CHANGELOG:238「L2 无损靠 caiming 兜底」）**

## 书例哨兵（先红后绿）
- 阎锡山（L4→L3 预期）
- 奥纳西斯（L2→L4 预期）
- 乾隆（L4 金字塔——不得误伤）
- 李嘉诚（L4 净制——不得误伤）
- 蒋介石（不净封 3——F5 后已正，不得回退）

## 红线
- **heldout 财命 46✅ 不回退**（66.67%）、官/职不退化
- **巨富三锚（李嘉诚/保尔森/奥纳西斯）不得降**（奥纳西斯应升）
- 书锚铁律：每处改动带书明文行号
- 阎锡山解锁后 67 例/famous 里若有其它盘受影响——逐案例审查

## 验证（全部通过后回报，300 字内）
1. 书例哨兵：先红后绿记录
2. `python3 mangpai/verify_mangpai.py` — 432 全绿
3. `python3 -m pytest mangpai/tests/ -q` — 全绿
4. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260817_f5.json` — heldout 翻转明细（每个列原因）
5. 67 例 + famous + calib — 0 回归（阎锡山相关若有变化逐案例审查）
6. 双 seed 一致

## 汇报（300 字内）
两件改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细（奥纳西斯/阎锡山确认）
