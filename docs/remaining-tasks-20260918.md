# 收工记录 · 2026-09-18（P2 官命 fp 窄修簇批落地）

> 接续 `docs/remaining-tasks-20260917.md`（H-fix 序列收官+L0 关闭+L1 已办，其「下批衔接」已定 P2）。
> 本批 = 引擎精度批 P 系列第二批（判定改动批，objective 零改动）。详账=`docs/tasks/codehygiene-fix-backlog.md` P2 节；预注册=`docs/kimi-p2-guanming-prereg-20260918.md`；快照链=`mangpai/tests/heldout/snapshots/README.md`。

## 一、P2 落地终态

| 项 | 内容 |
|---|---|
| 条款实现 2/7 | A12 女命夫宫域分流（gender 透传 guanming 消费侧，chuji:2206+yanjiu:5646）/A17 旺杀入墓墓不开无做功不立官（功在墓杀豁免，chuji:1405/1409+3161 双锚） |
| 收档 5/7 | A13 争合官无力（孤锚+机制不符+R3GUAN 冲突）/A14 合绊无功（触方向门 10 锚禁令）/A15 合用官被穿破（印化官杀独立立官撤 combo 不足翻判；KB 旧标「制不尽」与书原文不符，以书为准）/A16 禄上坐官（孤例+须动印类）/A18 制财尽（与 G7 豁免锚 cj-县长同构不可分） |
| 指标 | trainset 官 **100→102✅**（+2 全预注册，方案带 +2~5 下沿，CI 下界 79.6%→81.6%）；heldout 三维零翻转（官 48✅/财 47✅/职 24✅ 保）；trainset 财/职零翻转 |
| 文本抖动 2 条 | cj-妓女/shouke-qi23-闹婚不离 veto_reasons 岁运剥除连锁（A12 设计内，官维 unscorable） |
| 六件套 | verify 432+70+64+20 ✔；pytest **1087 passed+1xf** ✔；blind 快照 `20260918_p2.json` vs p1 翻转 2 全归因 ✔；双 seed 同 note 复跑逐字节一致 ✔；67/famous 无变化 ✔；calib 常驻 2 条零新增 ✔；check_layering+check_typing_imports ✔；3.11/3.14 冒烟一致 ✔ |
| 基线 | `snapshots/LATEST` → **`20260918_p2.json`**（README 链总账已补录） |
| 四保护锚 margin | cj-2097/yx-部长/reg67-公安/cj-公安全保 True；朱元璋（heldout 只评估）True；本批无降分条款，margin≤1 禁降分规则不适用；A4 印类方向门 10 锚复验 10/10 True |

## 二、偏差备案

1. 任务书称四保护锚「均在 trainset 可查到」——实测**朱元璋仅在 heldout**（shouke-qi47-朱元璋），以只评估不反推方式核验（不以其设计条款）。
2. KB §6.2 未给 A13-A18 case id，本批以代码+书原文实测定位（预注册 §一）；**A15 KB 标「制不尽」与书原文机制不符**（cj-老总实=合用官被穿破，chuji:3258-3262），以书为准收档。
3. 探针（combo key 并集 positions）预判 reg67-制例二/shouke-li084 翻转，实码按动作逐个判定更窄，两例实际不变（良性偏差）。
4. 散落 1 例=zj-工薪无官（§6.5 F11 软断语收档在先，本批未动）。

## 三、剩余事项

- **官命残留 ❌13**（KB §6.2）：fp 簇余 5（收档，勿再立项）+C 备案 7+散落 1。
- **下批=P3**（财命残簇批：A4 土金伤官 juefa→caiming 新消费边+A12 体坏凶向链+A13 制库基阶，方案 `kimi-engine-precision-plan-20260918.md` P3 节，从 `20260918_p2.json` 起跑）；P4=职业军警墓库做功。
- 代码改动未提交（工作树，用户未要求 commit）。
- 0917 文件所载其余事项（D 真实凭证冒烟待办、A3 条件项、feishu 并发两 P1 等）原样维持，见该文件 §二。
