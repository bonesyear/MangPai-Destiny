# 收工记录 · 2026-08-19（终态，下次开工必读）

> 上一份收工记录（remaining-tasks-20260818.md）保留作历史对照，内容以本文件为准。
> 本文件是 08-19 D1→E7 全链终态 + 08-20 缺口批1-3（qianyi/xiangmao 立、世应/风水化解/时空测事收档）收官。所有里程碑 commit 均在 GitHub。

## 〇、08-19 批次链（commit 序）

| 批 | commit | 内容 | 验证 |
|----|--------|------|------|
| D1 数据批 | `7eb7ca5` | gold 修正 5 条+锚 15 处+raw_quote 剔除+zhenbao-10 dayun 误录删除，纯数据 | calib 常驻 4→2；trainset 财 51.33→52.21；基线 d1 |
| D2 入口批 | `d55d90d` | 性别必填报错/年份 1900-2100 guard/lon 校验，引擎判定零改动 | test_entry_guards 33 测先红 19 后绿；基线 d2 |
| D3 供给批 | `5b49b66` | dayun_analysis 死 selector 修复（build_payload 层合成，engine 零改动） | test_d3 5 测；selectors 断言顺手修 39→38；基线 d3 |
| D4 prompt 迭代 5 | `fc5accb` | 职业桶+应期逐年锚定入 llm_prompt | S1 复验翻转 9/30→0/30 三线全达标 |
| D5 工具/备案批 | `94b519e` | rescore glob 确认已修+三备案（G6 scrub/as_of_year/子夜带）落 KB §4.11 | pytest 727+1xf+19xp |
| D6a 设计批 | `5bece72` | 子女断法设计：勘误 T2（F17 已立 zixi 三节，真缺口=应期+借腹），四书 60+ 锚，立 4 收档 8 | 纯设计零实现 |
| D6b 实现批 | `2b70811` | zinv 新模块 4 项（得子 3 机制/损子 5 机制/借腹/时柱喜用腿落 liuqin），selectors 38→39 | test_d6b_zinv 12 测先红后绿；blind vs d3 零翻转；基线 d6b |
| 飞书集成 | `bb4decf` | mangpai/feishu 新包 6 文件 528 行，mock 全链三例跑通 | test_feishu 23 测；零引擎文件无快照 |
| U1-U4 审查 | `2193454..b97cbb5` | 新引擎侧+飞书包+财档定性+收官闸，P0=0 全程 | 六件套全绿，漂移清单全文档级 |
| E1 飞书必修 | `188e3ca` | token 99991663/99991661 重试/reply 兜底/EncryptKey 红线/VT 强制 | test_feishu 28 全绿（+5）；飞书上线闸通过 |
| E2 文档清零 | 本批 | KB K1-K7+CHANGELOG C1-C4+本收工，纯文档零代码 | grep 抽查+pytest 767 复跑 |
| E3 数据/锚注批 | `0d9d00e` | raw_quote 恢复（QQ卜文确系书据）+锚修 4 处+calib 回填 5 条+U3 备案 3 注 | 六件套全绿；基线 e3 |
| E4 引擎裁定批 | `cdb3a25` | 穿引动裁定 a·改注（纯注释零行为）+损子「冲」收档（孤锚不立） | pytest 767+1xf+19xp；blind vs e3 零翻转 |
| E5 飞书加固 | `ba1fbc6` | 重放窗口滚动/token 刷新锁/静默错解三例（123:45/秒位/四柱抢占）/500 脱敏/HTTPServer 上限 | test_feishu 28→34；pytest 773 |
| E6 财档迭代 6 | `09c476f` | llm_channel 校验器口径修 6 条+prompt 锚定行，引擎零改动 | L2 财档越限 16→2（0.68%）；pytest 776；$2.98 谷段 |
| E7 迭代 7+文档同步 | 本批 | 官命维否定窗 ±2→±5（4 例全误判）+prompt 锚定补「可达/可至」+校验器⑦让步/归位同族清零 | L2 财档 2→1（0.34%）、官命 4→0；pytest 776；$3.01 谷段 |
| 缺口批1 qianyi | `854bbf2` | 迁移/远行新模块（原局三 marker+应期窗，措辞上限「迁移/远行」），selectors 39→40 | test_qianyi 11 测先红后绿；pytest 787；blind vs e3 零翻转零抖动；基线 gap1 |
| 缺口批2 xiangmao | `261de9d` | 相貌 marker 层（4 主线+2 弱线，纯 marker 无判定），selectors 40→41 | test_xiangmao 7 测先红后绿；pytest 794；blind vs gap1 零翻转零抖动；基线 gap2 |
| 缺口批3 收档同步 | 本批 | 世应/风水化解/时空测事收档口径入 KB §6.6 + KB/收工全量同步，纯文档零代码 | grep 抽查+pytest 794 复跑 |

## 一、引擎终态（2026-08-19，U4 全量实测+E2 复跑）

**留出集（215 例）**：财命 **47✅ 68.12%** / 官命 **48✅ 72.73%** / 职业 **24✅ 46.15%**
**训练集（294 例）**：财命 59✅ 52.21% / 官命 96✅ 83.48% / 职业 40✅ 47.06%
**工程**：pytest **814 collected（794 passed+1 xfailed+19 xpassed）** / verify 432+70+64+20 全绿 / 双 seed 逐字节一致 / 快照链至 `20260820_gap2`（…→d1→d2→d3→d6b→e3→gap1→gap2，跨档零翻转零抖动）/ regression67+famous 无变化 / calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财=存量）

## 二、LLM 通道终态（E7 迭代 7 后，294 例谷段复测）

- **四指标**：L0 0% / L1 1.36% / N1 0% / L2 0.34%（D4 旧记 L0 0.36/L1 0.00/N1 0.36/L2 4.98 作废）
- **S1 语义层**：翻转 0/30、放大 8.1%、一致率 89.3%——三线全达标（D4）
- **残留**：财档 L2 真越限 1 例（gj-合财小康「能积巨富」，单例采样抖动，mark 留人工=设计语义）；官命矛盾 0；**零已知系统性残留**（详见 docs/kimi-e7-caifu-iter7-20260819.md）

## 三、go/no-go（U4 收官闸 + E1/E7 后）

| 维度 | 判定 | 依据 |
|------|------|------|
| 引擎 | **GO** | P0=0；六件套全绿；776 测全过；快照零翻转；双 seed 一致；calib 残留=存量备案 |
| LLM 通道 | **GO** | D4 S1 三线达标；E7 复测 L2 0.34%（财档 1 例真越限 mark 留人工）、官命矛盾 0，零已知系统性残留 |
| 飞书包 | **GO**（E1+E5 后） | U4 原「条件 GO」三 P1（token 重试/reply 兜底/EncryptKey 红线）+P2-4（VT 强制）E1 全清；U2 P2 余项（重放窗口/token 锁/静默错解/500 脱敏/HTTPServer 上限）E5 全清 |
| 缺口序列（批1-3，08-20） | **GO**（收官） | 引擎 GO 三维维持：gap1/gap2 盲测各对上一基线零翻转零抖动、heldout 闸门 48✅/47✅/24✅ 保；新模块 qianyi/xiangmao 书例哨兵全绿；T2 五项缺口全处置=立 2（qianyi/xiangmao）收档 3（世应/风水化解/时空测事，KB §6.6） |

## 四、剩余（修批 E3-E7 已全清，按 U4 §5）

E3（数据/锚注）/E4（引擎裁定+损子收档）/E5（飞书 U2 P2 余项）/E6（财档迭代 6）/E7（迭代 7+官命口径）均已完成，见 §〇 批次链。仅余：

| 批 | 内容 | 性质 |
|----|------|------|
| 可选散项 | EncryptKey 解密支持 / 去重外部存储（量级上来再做） | 可选 |
| 长期 | 单命调用体验打磨/跨流派/十排歌完整版/三维残留（KB §6 已收档不追） | 暂缓 |

## 五、关键环境与教训（防再踩）

- **Kimi CLI**：任务开头必带 `docs/knowledge-base.md`（记忆替代机制）；kimi 配额=5h 账单周期非整点重置
- **push 通道**：GitHub 直连超时 → 临时 URL（gh-proxy+token）push，`ls-remote` 验证；origin 保持干净 URL
- **DeepSeek 峰谷**：北京 09-12/14-18 = peak，其余半价；大批量跑谷段
- **验证六件套**：verify_mangpai 432 / verify_dayun 70 / layer1 64 / layer3 20 / pytest / blind_eval（基线快照链，当前 gap2）
- **铁律**：heldout 是闸门（财 47✅/官 48✅/职 24✅ 不回退）；书锚铁律（规则改动带书明文行号）；LLM 输出永不入 compute_all dict；prompt 调优只吃 trainset；prompts/schools 受保护（zinv selectors 追加=D6b 设计 §3.4 授权备案）
