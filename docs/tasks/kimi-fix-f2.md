# Kimi 任务：修复批 F2 · 数据表层（anhe 子巳 + TOMB_MAP 戌 + muku 三 P0）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F2 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读审计归档**：批1（TOMB_MAP 缺戌 P1-1、暗合表子巳 P1-2）、批3（muku P0-1 多而墓之未计天干/P0-2 四库入辰强加多/P0-3 TOMB_MAP 传导）、批9（anhe 子巳升级 P0 传播五处）
3. 本批**已解锁 constants 保护**（用户批准）——可改 `objective/constants.py` 的 TOMB_MAP
4. 汇报 300 字内

## 任务（三件，含传导同步）
1. **anhe 子巳**：删「子巳」暗合对（初级 3218「只有三个」显式排除）——**五处同步**（anhe 定义 + zuogong/liunian/yunfan/zeishen 消费 + prompt 若有），漏一则链路口径分裂
2. **TOMB_MAP 加戌=土墓**（段氏「土墓在辰、戌」双位）：constants TOMB_MAP['戌'] 加土；**消费方全量回归**（caiming/guanming/gongliang/laoyu/muku 的 is_entomb/_tou_gan_elements 等——批3 P0-3 列的三处消费 + 传导面）；注意与批3 muku P0-2（四库入辰不加多条件）联动改
3. **muku 三 P0**：
   - P0-1 多而墓之**计天干**（书 3002「天干地支合在一起…辛酉柱见丑即入丑墓」）
   - P0-2 四库之土入辰墓**去「多」条件**（书 3008「丑入辰墓，未也入辰墓」无多前提；注释反托段氏口径需更正）
   - P0-3 TOMB_MAP 戌传导修复（随 2 一起）

## 书例哨兵（先红后绿）
先写书例断言（红）：奥纳西斯（丑未冲开库）/蒋介石（巳午入戌）/卯未辰寅（未入辰墓书例 3080-3084）/辛酉柱见丑（多而墓之书例 3002-3005）——跑红 → 修复 → 转绿

## 红线
- **heldout 财命 46✅ 不回退**（66.67%）、官/职不退化——墓库改动面大，**全量 diff 审查**（Kimi 规划 F2 风险点：改表后 caiming/guanming/gongliang/laoyu 全量回归）
- 书锚铁律：每处改动带书明文行号
- 与 F5（zeishen 滤 auxiliary）不冲突——本批只动数据表层

## 验证（全部通过后回报，300 字内）
1. 书例哨兵：先红后绿记录
2. `python3 mangpai/verify_mangpai.py` — 432 全绿
3. `python3 -m pytest mangpai/tests/ -q` — 全绿
4. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_f.json` — heldout 翻转明细（**允许改善，不容许回退**；每个翻转列原因）
5. 67 例 + famous + calib — 0 回归
6. 双 seed 一致

## 汇报（300 字内）
三件改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细（若有）
