# Kimi 任务：修复批 F11 · yongshen + caiming（先于 zhiye 的档位层）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F11 定位）+ `/root/metaphysics/docs/knowledge-base.md`（§10 勘误：22期例6 从官格已改判）
2. **读审计归档**：批4（yongshen P0×2：22期例6 从官格漏判（缺「晦」机制+成势闸误杀）/例7 未从误判从弱（conc≥6 粗闸抢跑，段氏明文反对衰旺计数 shouke:454））、批6（caiming P0×2：财统官主位制宾官前置漏检 zhongji:2853 巨富书例/过河拆桥不验财生官相连致 **ans12 假富格**——「永久必损」备案根因在此实非必损；yongshen.py:255 注释按 F0 勘误修正）
3. 汇报 300 字内

## 任务
1. **yongshen 22期例6**：从官格漏判修复（缺「晦」机制 + 成势闸收窄）——注意 KB:247 勘误后 yongshen.py:255 注释同步
2. **yongshen 22期例7**：未从误判从弱修复（conc≥6 粗闸收窄，段氏明文反对衰旺计数）
3. **caiming 财统官前置**：主位制宾官前置补全（zhongji:2853 巨富书例）
4. **caiming 过河拆桥**：验财生官相连（ans12 假富格真根因）——ans12 预期翻转（⚠️→✅ 或至少不再假富格）

## 书例哨兵（先红后绿）
- 22期例6（从官格）/ 例7（未从）/ ans12（假富格→正）/ zhongji:2853 巨富书例

## 红线
- **heldout 财命 46✅ 不回退**（66.67%）、官/职不退化
- 与既往批锚不冲突（F6 gongliang 层、F5 zeishen）
- 书锚铁律

## 验证
1. 哨兵红绿 2. verify 432 3. pytest 全绿 4. blind --baseline 20260817_f7.json 翻转明细（ans12 重点关注）5. 67/famous/calib 0 回归 6. 双 seed 一致

## 汇报（300 字内）
四件改动/行号/书锚 + 哨兵红绿 + 验证 6 项 + ans12 翻转确认
