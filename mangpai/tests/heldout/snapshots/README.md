# 快照链（heldout blind_eval 基线档案）

> M5 快照机制：每批引擎/规则改动后跑 `blind_eval.py --out snapshots/<批>.json --baseline <上一批>`，
> 快照带 `_meta`（git_sha / rubric_version / note）。**零翻转零抖动**是每批门禁。
> 本文件是快照链的总账：哪个是当前基线、哪些是历史、各批对应的 commit。

## 当前基线指针

- **`LATEST`**（纯文本单行）= 当前基线快照文件名，现指向 **`20260918_p4.json`**。
- `blind_eval.py --baseline latest`（或 `--diff latest <快照>`）自动解指针（H-fix-8 起）。
- 推进基线 = 人工改写 `LATEST` 一行——**刻意不随 `--out` 自动更新**，防误推基线。

## H-fix 序列快照链（2026-09-17~18，rubric v8-20260808 全程不变）

| 快照 | 批次 | git_sha | 对照基线 | 结果 |
|---|---|---|---|---|
| `20260917_prehfix.json` | H-fix 序列动工前基线锚 | 0c48a84 | —（对照锚） | — |
| `20260917_hfix1.json` | H-fix-1 import/typing 崩溃面 | d21937a | prehfix | 零翻转零抖动 |
| `20260917_hfix2a.json` | H-fix-2a 异常策略·引擎层 | 55fff7f | hfix1 | 零翻转零抖动 |
| `20260918_hfix2b.json` | H-fix-2b 异常策略·subjective 层 | ade2090 | hfix2a | 零翻转零抖动 |
| `20260918_hfix2c.json` | H-fix-2c 异常策略·脚本层（收官） | cbbf6ba | hfix2b | 零翻转零抖动 |
| `20260918_hfix3.json` | H-fix-3 原子写 19 处 + 免责提级 | 5acbb89 | hfix2c | 零翻转零抖动 |
| `20260918_hfix4a.json` | H-fix-4a 死代码清理（删 advanced/chuangong） | 57cb5c9 | hfix3 | 零翻转零抖动 |
| `20260918_hfix4b.json` | H-fix-4b 重复逻辑下沉统一 | c5c4e00 | hfix4a | 零翻转零抖动 |
| `20260918_hfix4c.json` | H-fix-4c 局部 import/循环依赖整理 | 19662e9 | hfix4b | 零翻转零抖动 |
| `20260918_hfix6.json` | H-fix-6 selectors/engine-keys 契约测试 | 471890c | hfix4c | 零翻转零抖动 |
| `20260918_hfix5.json` | H-fix-5 大函数拆分（在 6 之后落地，见 v2 计划顺序调整） | 29524b6 | hfix6 | 零翻转零抖动 |
| `20260918_hfix7.json` | H-fix-7 评测框架统一 | 9129c6b | hfix5 | 零翻转零抖动 |
| `20260918_l1.json` | L1 遗留清理批（B1 xiangfa_ops 排序化 4 处+frozenset join 2 处、C1 zaihuo 官杀 label、B2/B3/B4/C2/C3 零输出项） | 见 _meta | hfix7 | 评分字段零翻转零抖动；文本抖动归因五域全部设计内 |
| `20260918_p1.json` | P1 官命检测簇批（A8 支杀化印新 type+A19 食合官支 G9 扩展+A11 贼捕制印新消费边 zeishen→guanming） | 见 _meta | l1 | heldout 三维零翻转零抖动；trainset 官 +4（96→100✅）全预注册、财/职零翻转；文本抖动 1 条（zj-平常八字 veto_reasons，A8 门槛机制设计内） |
| `20260918_p2.json` | P2 官命 fp 窄修簇批（A12 女命夫宫域分流 gender 透传+A17 旺杀入墓墓不开无做功不立官；收档 A13/A14/A15/A16/A18） | 见 _meta | p1 | heldout 三维零翻转；trainset 官 +2（100→102✅）全预注册、财/职零翻转；文本抖动 2 条（cj-妓女/shouke-qi23 veto_reasons，A12 夫宫分流后 veto 链剥除连锁，设计内） |
| `20260918_p3.json` | P3 财命残簇批（A13 制库基阶落位两条款：独力上浮封顶富「库同藏官杀」豁免+明财阻断落富不落小康 sticky floor；收档 A4 土金伤官/N1 已承担、A12 体坏/N5 已接入） | 见 _meta | p2 | heldout 三维零翻转；trainset 财 +2（59→61✅）全预注册、官/职零翻转；文本抖动 7 条全归因（条款一×5 caiming_adjust+条款二×1 li240+入狱一年 tier_static 巨富→富） |
| `20260918_p4.json` | P4 职业军警新面批·P 系列收官（objective muku 新检测 `detect_ku_zhi_ku` 库制库·阳制阴，纯增量既有函数零改动；zhiye military 消费条款+6：阳库收/刑阴库+阴库成双多见，贵气门外格局级通道）（**当前基线**） | 见 _meta | p3 | heldout 三维零翻转零抖动；trainset 职 +1（40→41✅，gj-警察墓库）全预注册、官/财零翻转；军警探针 3/10→4/10（军官例四归位）；文本抖动 0 |

注：hfix6→hfix5 顺序非笔误——v2 计划把契约测试（6）前置于大函数拆分（5），快照按实际落地顺序编号。

## 主链（2026-07 三维攻坚 ~ 2026-08 发布态）

`20260801/02 早期批`（部分已归档）→ `20260808_q`（官命批）→ `q_rescore`→`r`（职批1，rubric v8 rescore）→ `20260814_a/b/c`（职批2-4）→ `20260817_f2`~`f19`（修复批 F2-F19，f8/f9/f14/f15 已归档）→ `20260818_fa/fb`（修批A/B）→ `20260819_d1→d2→d3→d6b→e3`（D/E 批）→ `20260820_gap1→gap2`（缺口批1/2）→ `20260821_n3`（N3 收档）→ `20260822_g1→g2→g3`（发布闸 G1-G3，G2/G3 为 LLM 层改动引擎零触）→ **`20260917_prehfix` → H-fix 链（见上表）**。

各批要点与翻转明细见 `docs/knowledge-base.md` §9 与 `mangpai/CHANGELOG.md`。

## 归档（`archive/`，保留历史不删——快照链是审计证据）

14 份无代码/文档引用的早期/中间快照（H9 P1，2026-09-18 H-fix-8 归档）：
`20260801_f` / `20260801_f_rescore` / `20260801_p2` / `20260802_c` / `20260802_l` / `20260807_m` / `20260808_n` / `20260808_o` / `20260808_q_rescore` / `20260814_c` / `20260817_f8` / `20260817_f9` / `20260817_f14` / `20260817_f15`。
其中 f8/f9/f14/f15 属 F 序列中间态（链上前后批次快照仍在根目录），归档仅因无任何活引用。

## 卫生规则

- 快照一律入 git（`.gitignore` 例外 `!mangpai/tests/**/snapshots/*.json`）。
- `_meta` 三字段（git_sha/rubric_version/note）缺失=拒绝写入（H-fix-3 写入前校验）。
- `--out` 走原子写（`.tmp` + fsync + `os.replace`，H-fix-3）。
- rubric 口径改动须 `--rescore` 重评 + 重设基线 + 改 `RUBRIC_VERSION` changelog（blind_eval 文件头）。
