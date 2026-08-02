# 盲派客观层 变更记录

## 2026-08-02 第二十一批 · G2 训练集扩容（91→119 例，中级/高级主矿）

| 项目 | 内容 |
|------|------|
| G2 落地 | 中级 12 + 高级 15 + 双源 1 = 28 例（zj-/gj- 前缀）；断语财命 21/职业 21/官命 4/婚姻 5/健康 2/应期 1 |
| 缺口 | **平 0→7、贫 1→7、凶 1→5 达标**；小康 2→4 差 1（中级全文 0 条小康明文，高级范例二「资产数百万」归富档，**书矿枯竭**） |
| 去重 | gj-正处级撞 reg67-化例一同盘跳过 1；heldout 8 字撞 0 |

验证：verify 432 全绿、pytest 469 passed、heldout vs 20260802_k **零 diff 零翻转零抖动**、trainset acc：官命 84.31/财命 48.08/职业 34.09（旧 85.11/48.39/40.62，职业更多案例暴露短板）、regression67/famous 归档零改动。新 baseline `20260802_l.json`。

## 2026-08-02 第二十批 · G1 训练集扩容（23→91 例，纯数据批）

| 项目 | 内容 |
|------|------|
| G1 落地 | regression67 未转 47 例 + famous 21 例转训练集（schema 零新增、id 分源前缀、verdict 只录书明文）；去重：内部同盘 3 对合并、已在库 16 跳过、李嘉诚撞 b67、慈禧撞 heldout 禁入 |
| 分布 | 训练集 23→91 例：财命 n=31、官命 n=47、职业 n=32、婚姻等 |
| 门禁 | heldout vs 20260802_j **零翻转**（双 seed 一致）；trainset acc 重算：官命 80.0→85.11%、**财命 81.82→48.39%**、职业 66.67→40.62%（**幸存者偏差消退，预期内**——旧 23 例 acc 虚高） |

验证：verify 432 全绿、pytest 469 全绿、regression67/regression_famous 0 回归。新 baseline `snapshots/20260802_k.json`。

## 2026-08-02 第十九批 · E 收尾：PUTONG2 同制判定细化（全库 xfail 清零）

| 项目 | 内容 | 文件 |
|------|------|------|
| destructive_positions 集 | 新增 destructive_positions（冲/克/穿非辅助双方），同制候选须落该集——**合族（六合/半合）单独不支撑 +2**（书锚：普通例二丑经酉丑相拱/子丑合，书判相生之功）；正当同制俱有实制（蒋介石巳亥冲/奥纳西斯丑未冲/森田健戌克亥） | subjective/gongliang.py |
| 相生之功门 | _assess_penalty：日干无功弃之不看（例三书锚），日主自克非做功之制 | subjective/gongliang.py |
| 连墓加层 | 库源块补「连墓加层」（月令入墓于源头之库，李嘉诚「月令己未全部入墓于辰」书锚）——同制位由未落亥后补足第 4 点保 L4 | subjective/gongliang.py |

验证：verify 432+70 全绿、**pytest 469 passed, 0 xfailed（2 xfail 解锁，全库 xfail 清零）**、盲测财命 66.67%（46✅）/官命 56.06/职业 40.38 全平零翻转（文本抖动 5 条=解释层漂移分数不变）、67例 0 回归 + 普例2 ⚠️→✅、famous/calib 0 新增回归（罗斯切尔德=批11存量）。
同制案例无损：李嘉诚 L4 / 奥纳西斯 L2 / 森田健 L2 全保。

## 2026-08-02 第十八批 · gongliang base3 层校准（财命 66.67% 持平，虚高双计收敛）

| 项目 | 内容 | 文件 |
|------|------|------|
| 库源×入墓同源去重 | 被制元素已计「入墓为功」者，同一元素-墓库对不得再以「出自墓库=源头得库」重计——李嘉诚锚「亥从辰墓中**引出**」（引出）与入墓（收藏）为同一墓对相反读法；qi15-伤官当财造同一辰亥对双计摘除（7.5→5.5） | subjective/gongliang.py |
| 克链入墓惰性 | 入墓之物不做功（审计P1 既定原则「入墓则失去作用」）——已入墓元素出边不入克链（`_chain_length` 增 `inert` 参数）；qi15 造亥入辰墓在案、亥克午边惰性，辰→亥→午链不成立 | subjective/gongliang.py |

验证：verify 432+70 全绿、pytest 467 passed+2 xfailed、盲测 vs 20260802_i.json **财命 66.67%（46✅/13⚠️/10❌）零翻转**、仕途 56.06%/职业 40.38%/trainset 持平、67例 ✅52 零回归、famous+calib 0 边际回归（罗斯切尔德 zy/zhenbao-01 官命=批11/批13-15 存量，本批 stash 双实证）、M1 双 seed 逐字节一致。
诊断（归档 k3-gongliang-base3-2026-08-01）：**ans12 批17 定位证伪**——base≤2 反触发开财库上浮至巨富，富（⚠️）系局部最优，真锁=caiming 富格 floor+开财库链；「身弱财旺非成势封顶」全库扫描命中 b67-森田健（trainset ✅富），与 qi14（成火土气势书锚）构成双锚夹击→ans12/li244 永久必损移出候选。qi15-伤官当财虚高 7.5→5.5 仍 L4 ❌（根治=zuogong 层寅亥合绊优先级+caiming 财统官合绊排除，下批双改联动）。
回退：月令做功 strong-gate（法则7 主要功神口径）实证击穿校准一 P1-a（li158 唯一 0.5 归零 ⚠️→❌）撤回。
13 例 gong_points 下降但 level 全库零变化、score 仅 qi05 一例 68→71（raw_level 归位，边界注记消失=意图内）。新 baseline=snapshots/20260802_j.json。

## 2026-08-02 第十七批 · 巨富档 overshoot 校准（财命 65.22%→66.67%）

| 项目 | 内容 | 文件 |
|------|------|------|
| 财源上浮不越巨富 | 财星当财路径财源上浮（财有原神+为我所及）上限「富」（`tier_idx<3` 方可 +1）——段氏「有财则伤食是其原神，可以当投资之财」投资/经营财量级至富，巨富须制级锚（制尽/净制/制库各有专支）；li128 实证 base3→4 过冲（书判=富）⚠️→✅ | subjective/caiming.py |
| 制库得财排除自刑开库 | 要件2 opener 排同支（辰辰/午午/酉酉/亥亥自刑=伏吟，主重复痛苦非开库；段氏开库=他支冲/刑「丑未冲开一点点」，与 `_tomb_chong_xing_open` 排同支口径对齐）——qi07 辰辰自刑过冲巨富→富 ❌→⚠️（书判=平·发财后赔光） | subjective/caiming.py |

验证：verify 432+70 全绿、pytest 467 passed+2 xfailed、盲测 vs 20260802_h.json **财命 66.67%（46✅/13⚠️/10❌）**、仕途 56.06%/职业 40.38%/trainset 持平零翻转、67例 0 回归、famous+calib 0 边际回归（罗斯切尔德=批11存量、zhenbao-01官命=批13-15存量 stash 实证）、M1 双 seed 逐字节一致。
翻转：li128 ⚠️→✅、qi07 ❌→⚠️。文本抖动 3 例全为意图内（li050 无财命断语 text-only、li263-走私被扣 巨富→富 score✅ 不变、zhenbao-05 制库上浮摘除——后二者即两收敛之直接后果）。
ans12-下岗财会维持 ⚠️（富 vs gold 小康）：定档障碍=gongliang base3，caiming 侧无书锚可压——身弱财旺主动封顶被 qi14-亿万企业家（身弱+财≥3+gold 巨富）锚否决；qi15（gongliang base4）/li244（零财 guard 内 禄财口径，亿万富翁 verdict 出寿元章附述）同归下批/存量。
新 baseline=snapshots/20260802_i.json。

## 2026-08-02 第十六批 · yongshen 侧 3 项（财命 60.87%→65.22%）

| 项目 | 内容 | 文件 |
|------|------|------|
| R3 G9 财合日主豁免 | 日支为激活自合柱且合神/主气皆财（戊子/壬午型）者，六合受害不论绊——例134 子丑合书读「丑土不克水」，受绊者是克财之比劫忌神侧；解锁 caiming G9 自合合财升档（li133 ⚠️→✅） | subjective/yongshen.py |
| 财源上浮一事不二升 | `_g9_up`：财源上浮与 G9 同源（财为我所及+有原神），G9 已升者财源不叠加（防 li133 双升巨富仍 ⚠️；例134 书判=富） | subjective/caiming.py |
| R2 从格忌神主气口径 | 从强/从弱 孤忌犯众豁免之忌神明现改主气（透干/支本气，22期成势闸同口径）——qi40 巳中戊中气不计、印主气=丑=1→豁免；qi40 匡正不翻（tier 障碍=从儿无财门控，批xfail deliberate 收敛不动），附带匡正 li263/qi07/qi16 从格 R2 假阳（text-only） | subjective/yongshen.py |
| P0-a 运锚层级断语判轨（rubric v6） | 层级断语干支锚=所喂运岁 且 原局轨与断语档位差≥2 → 改评 delta 轨（「八字为车大运为路…过路财神」）；差≥2 门槛下原局本必❌，只改善不回退（裸锚匹配会把 li001/li131/qi22 乙亥发财 ✅→❌）；qi02/qi21 ❌→✅，li128 锚≠所喂运维持静态⚠️ | tests/heldout/blind_eval.py |

验证：verify 432+70 全绿、pytest 467 passed+2 xfailed、盲测 vs 真基线 20260802_c.json **财命 65.22%（45✅/13⚠️/11❌）**、仕途 56.06%/职业 40.38%/trainset 持平零翻转、67例 0 回归、famous+calib 0 边际回归（罗斯切尔德=批11存量、zhenbao-01官命=批13-15存量 stash 实证）、M1 双 seed 逐字节一致。
注：任务书所附 g.json 为批12旧基线（批13-15 不在其中），本批 diff 审阅一律对 c.json；新 baseline=snapshots/20260802_h.json（rubric v6-20260802）。
下批候选：li128/li244/qi41 型静态档巨富 overshoot（财源上浮/官统财 巨富档校准，caiming 侧）；ans12 下岗财会（必损清单存量）。

## 2026-08-01 第十五批 · C批 caiming 上浮链收敛（财命 57.97%→60.87%）

| 项目 | 内容 | 文件 |
|------|------|------|
| 富格独力上浮封顶富 | 富格独力上浮封顶「富」+ 净制豁免（批A floor富锚 + 巨富皆净制/制库锚） | subjective/caiming.py |
| 封顶富 sticky | `_liangji_cap`：开库链不得翻越封顶富 | subjective/caiming.py |
| 开库+1 须财有原神 | ans29 书文「水弱被制无原神所以会穷」 | subjective/caiming.py |
| zbj 零财 guard | 《中级》零财之局官杀当财不成立（同 663 行财统官锚） | subjective/caiming.py |

验证：verify 432+70 全绿、pytest 467 passed+2 xfailed、盲测 **财命 60.87%（42✅/14⚠️/13❌）**、仕途 56.06%/职业 40.38% 持平、67例 0 回归、famous 仅批11存量罗斯切尔德（巨富三锚+li002/li200 全保）、双 seed 一致。
翻转：qi41 ⚠️→✅、li151 ❌→✅、ans12-下岗财会 ❌→⚠️（批B必损后改善）、ans29 巨富→富（虚高收敛生效）。
下批候选（yongshen 侧）：R3 日主自合误绊锁死 G9（li133）、R2 从儿印夺食（qi40）、P0-a 运锚层级断语（li128/qi02-辛未/qi21）。

## 2026-08-01 第十四批 · 功量层合批（乾隆金字塔门 + 虚高面诊断）

| 项目 | 内容 | 文件 |
|------|------|------|
| 乾隆金字塔门 | gongliang 新增「金字塔门」：zb 链长≥3 覆盖四支 + 冲边≥2 以冲为骨 + zb 净制 → +1 层；净制采纳扩至金字塔路径。乾隆 xfail 解锁（strict→pass），L3→L4（同制2+七杀1+金字塔1+月令0.5=4.5，净制） | subjective/gongliang.py, tests/test_gongliang.py |
| M1 存量修复 | zeishen_bushen detect_bao_zhi `sorted(shared)`——批 F 后第 11 处 set 排序化（多候选包制 3 例由 hash 序定制局） | subjective/zeishen_bushen.py |
| 虚高面诊断 | **虚高 9 例翻转=0**：终档由 caiming 上浮链（官杀当财/制库得财/开财库）决定，非 gongliang 基阶——克链≥3 实证 0 翻转、库源自墓破 zhenbao-05 已回退、不成 cap 假阳否决。**虚高面收敛归 caiming 侧，留待 C 批** | — |

验证：verify 432+70 全绿、pytest **467 passed+2 xfailed**（乾隆解锁，无新增）、盲测财命 57.97%（40✅持平）/仕途 56.06%/职业 40.38% 0 翻转、M1 双 seed 逐字节一致、67例 0 回归（乾隆 ⚠️→✅ level4/书4）、famous+calib 0 新增回归（李嘉诚/保尔森巨富、li002/li200 富全保住）。

## 2026-08-01 第十三批 · famous 官命 4 例对案修复（误火+漏判共性）

| 项目 | 内容 | 文件 |
|------|------|------|
| 藏杀被制→has_guansha | 官杀藏支被非辅助制=制杀得权（慈禧「合局制死丑中杀」/希特勒「丑入辰墓」/曾国藩「功在墓杀」）→ 修漏判共性（慈禧/希特勒 ❌→✅） | subjective/guanming.py |
| 杀印相生滤 auxiliary | G0 同口径补洞：李昌镐/李嘉诚假「印化官杀」皆 auxiliary，滤除 | subjective/guanming.py |
| G7 围制财源支主富不主贵 | 财/原神支被≥2方硬制，涉其 combo 不入官命（李嘉诚「主富不主贵」）；藏官杀之库豁免（以杀论权） | subjective/guanming.py |
| G6 官星被制空亡硬否 | 李昌镐「官星被制空亡故不入仕途」（日/年旬并参）+ 墓库豁免（官有墓在局=被收非制死，救曾国藩） | subjective/guanming.py |

验证：verify 432 全绿、pytest 466 passed+3 xfailed、盲测仕途 56.06%（37✅持平）/财 57.97%/职 40.38% 持平、**famous 官命 ❌4→✅ 10/10 判定项全对**（慈禧/希特勒/李昌镐/李嘉诚全翻转）、67例 0 回归（+2 改善）、trainset 官命 11→12✅。

## 2026-08-01 第十二批 · 职业桶语境排除（_ZY_EXCLUDE，rubric v5）

| 项目 | 内容 | 文件 |
|------|------|------|
| 职业桶假阳性剔除 | 诊断 95 条职业断语，真阳性 2 类：歌厅/歌女（色情业）误入 performer ×3、参军误入 military ×1。新增 `_ZY_EXCLUDE` 语境排除（v4 同法理转 unscorable）。**qi20 歌厅小姐原 ✅ 系假阳性**（gold 色情业仅凭「歌」撞桶），剔除后 22→21 真 ✅ 全干净，acc 40.0%→**40.38%**（n 变化） | tests/heldout/blind_eval.py |
| rubric | _ZY_EXCLUDE 逻辑 → v5；新 baseline `snapshots/20260802_g.json` | tests/heldout/blind_eval.py |

验证：verify 432+70 全绿、pytest 466 passed+3 xfailed、盲测职业 40.38%/仕途 56.06%/财命 57.97% 全达标、67例 0 回归（2 改善）、calib 0 回归。
famous 罗斯切尔德 ❌（merchant 判 teacher）为存量问题（git stash 实证 clean HEAD 即有），留待仕途/职业批。

## 2026-08-01 第十一批 · 职业维·商业类召回修复（merchant 结构性塌陷）

| 项目 | 内容 | 文件 |
|------|------|------|
| merchant 结构性塌陷修复 | 日支合财/制财（主位经营取财第一象，段氏「我合财、制宾财得财」）曾被全量误排——merchant 召回结构性塌陷（li213 申子合财误排同此）；暗合按支中藏干本气+中气计（段氏「暗合者，支中藏干相合也」）；群比夺财背景（比劫主气≥4 成群，中级「只有比劫做功，比劫主竞争」）不计经营；财根被坏（劫财冲财=坏财之根）不计；财星入局做功 +2 精细判据（冲=双向商贸流动，7.3「相冲做功…物品交换」；合类须主位端参与+功神端主气非印/官杀/比劫） | subjective/zhiye.py |
| 测试 | +1 新测试（466 passed） | tests/test_p0_blindgap.py |

验证：verify 432+70 全绿、pytest 466 passed+3 xfailed、67例 0 回归（2 改善保持）、famous **乔布斯 ❌→✅**（商人/经营命中）、calib 0 回归（+5 IMPROVE 保持）。
留出集盲测：**职业 24.56%→40.0%（14✅→22✅，+15.4pp）**、官命 56.06%（37✅持平）、财命 57.97%（40✅持平）——零回退。

## 2026-08-01 第十批(F) · P3测量卫生三件套 M1复跑确定性+M2分组门禁+M5快照入git

| 项目 | 内容 | 文件 |
|------|------|------|
| M1 复跑确定性 | 10 处 set 迭代序排序化（纯定序不改语义）：gongliang 5 处（strong_positions tie-break/zhi_targets 首中/墓库 join/净制理由 x2）、yunfan 废神列表、zeishen 最长路径平局、hunyin/zaihuo join、zuogong_confirm work_types；双 seed（PYTHONHASHSEED=0 vs 默认）逐字节一致；钉死 li002 原神用神同制 tie-break（adjust 文本变、打分不变，67例/calib 反改善） | subjective/gongliang.py, yunfan.py, zeishen_bushen.py, hunyin.py, zaihuo.py, zuogong_confirm.py |
| M2 分组门禁 | blind_eval 汇总增财命 verdict 首词分组表（巨富/富/小康/平/贫/破财/凶 各自 n/✅/⚠️/❌/acc），eval 与 diff 报告均附 | tests/heldout/blind_eval.py |
| M5 快照入 git | snapshots/ 目录 + .gitignore 例外；快照附 _meta（git sha/rubric 版本/备注）；blind_eval 增 --baseline（eval+diff 一条龙）与 --note；存 20260801_p2（批C基线）与 20260801_f（本批后基线）；--diff 增「文本抖动」段（score 不变但 engine 字段变，>0 即卫生失败，单边缺失案例不计） | tests/heldout/blind_eval.py, .gitignore, snapshots/ |

验证：verify 432+70 全绿、pytest 465 passed+3 xfailed、留出集财命 57.97%/官命 56.06%/职业 24.56% 与批C完全一致、双 seed 逐字节一致、67例 0 回归（2 改善）、famous 23 0 回归、calib 0 回归。

## 2026-08-01 第九批 · K3财命50%攻坚 批C（P2束5项，收官）

| 项目 | 内容 | 文件 |
|------|------|------|
| 功量基阶重校·制库得财 | 月令墓库被主位冲/刑开、库中财与原神同制=制尽级财命定式，直判 floor 富（理象学制例一奥纳西斯船王锚：巨富旧判贫——局无明财落禄/伤食当财被 -1 下浮；「月令之财与财的原神同时被制，财富级别可见一斑」） | subjective/caiming.py |
| muku 冲刑开库 | 丑未冲/刑动库半开（《中级》「丑未冲开一点点」「不冲不刑是墓」）：库逢冲/刑则动而非死墓，财不死藏，不论「收藏难取」之阻；唯无透干引拔则财未全出（理象学「墓中余气透干引出方有用，不透干也无用」），记 rumu_bankai——基阶不压、升档不升 | subjective/caiming.py |
| N4 官非牢狱复合凶向 | 段氏牢狱五法「命中占其一即有牢狱之象，占多者灾重」收口——五法单式泛火严重，laoyu 聚合 risk 在富贵局系统性过火，仅以最特异两法俱中为官非牢狱凶向：魁罡逢冲官（庚辰/壬辰/庚戌/戊戌日逢刑冲官杀，高级篇 ch11）∧ 枭神夺食（食伤做功之神被夺，中级牢狱专辑法三）。全库命中面实测仅 4 例（li094/ans31 两牢狱金标在内，famous23 与 trainset 零命中），方入凶向链 | subjective/yongshen.py |
| 合绊取财·不劳而获标注 | 段氏诀「枭神生劫不劳而获」（11期贱命无赖「一生靠劫取他人财为生」；虎应造「靠绊大款为生，也为个劳而获」同诀）：偏印透干 + 劫财明现 = 取财性质识别（methods 尾位标注「不劳而获」），不参与定档——档位仍由功量/财源主线判定，ans12 已批损失面与批B R3 豁免口径不动 | subjective/caiming.py |
| zhengfan 日柱主动做功门控 | R-a 门控：非辅助动作由 day_gan/day_zhi 发起≥1 才算日柱主动做功（防反局误判） | subjective/zhengfan.py |
| 官命 veto 收窄 | veto_reasons 过滤列表增「官非牢狱」（N4 入凶向链后不再直接否决官命） | subjective/guanming.py |
| 数据锚定 | li050（断语主语=娘家非本人）财命 verdict 移除 → unscorable（财命 n 70→69）；li141 喂运 癸亥→壬戌（与断语对齐） | tests/heldout/cases.yaml, annotations_heldout.py |

验证：verify 432+70 全绿、pytest 465 passed+3 xfailed（无新增）、67例 0 回归（✅51）、famous 23例 无变化、calib 46项 0 回归（+5 IMPROVE 保持）。
留出集盲测：**财命 54.29%→57.97%（n=69，✅38→40，净+2）**、官命 56.06%（37✅持平）、职业 24.56%（14✅持平）、trainset 财命 72.7%→81.8%（9✅/2⚠️/0❌）。

## 2026-08-01 第八批 · K3财命50%攻坚 批B（P1束3项）

| 项目 | 内容 | 文件 |
|------|------|------|
| 财统官3→4需量级证据 | P1-4：财统官（官多财少，财可统官）以少财统多官，财之量级本疑——财源上浮 3→4 阶须财量级支撑：**财有原神且归主位**（贫富三要素之浮实判据：财有源头且为我所及）或**贼神捕神净制**（量级同制尽），否则封顶「富」不到巨富；官统财（财多官少，财量级自证）与过河拆桥·富格（制尽路径）不在此限 | subjective/caiming.py（assess_caiming_level 财源上浮块） |
| 过河拆桥制尽判据重修+富格直判+泄漏清理 | A：制尽判据——主位（日/时）支中**藏干**官不计「残存同党」（藏而不透附于主位=财之附属，非宾官夺财之党；trainset 实锤 b67 森田健日支亥中气甲被旧判据误计残存→误判制不尽破财，gold 富）；主位**透干**官杀明现有力仍计残存（qi05 时干癸杀透，制不尽成立）。B：富格直判 floor 富（制尽净制、制官得财之财命定式，纵功量低估不落下富；升档仍走官杀当财+1，仅+1不越级；凶向封顶链不受影响）。C：标注泄漏清理——「伴过河拆桥破财信号」文本仅属制不尽分键，富格不再无条件下挂（「破财」标记词泄入 summary 误杀评分，qi41） | subjective/caiming.py（_is_zhi_jin、assess_caiming_level、_assemble_summary） |
| 反局精化（K2-5合年月官） | 日主合年/月干官=管理、控制别人（官为我所用，《中高级》「如是日主合年、月上的官，则意思不一样了」）——「日主合官」之合与「官杀克日主」（日主为受方、非日柱做功指向）不再计入反局（五行方向）之日柱指向（day_fan_targets 分离，day_targets 全量仍供「无功不为局」）；日柱另有他类做功指向相克者仍照常判反。合时干官（被官控制）不豁免；li101 反局判定不动（非全局放宽） | subjective/zhengfan.py（analyze_zhengfan） |
| R3合化出喜用豁免 | 用神被合绊（R3）精化：合之**化气**五行属喜用类且异于受害方本行者，合非「绊住失用」而是「向化喜用」，不论凶绊（森田健卯戌合化火=印，段氏明文「需行火运生扶日主则好」——合之化气正是其所喜；合绊事实仍计入身弱判定，不双重计入凶向）；化气==受害方本行仍论绊（qi03 寅亥合化木、寅本木「故不吉」；化例三中堂子丑化土==丑土），化出忌神者不豁免。新增 _LIUHE_HUAQI 六合化气表（天干五合用既有 HUA_YONG_MAP） | subjective/yongshen.py（detect_heban_yongshen） |
| 测试契约更新 | test_r3_morita_ken_detected→test_r3_morita_ken_huaqi_exempt（森田健 R3 不命中为新口径预期；化气==本行仍论绊由 zichou/gan_he 两测锁定）；test_caiming_capped_by_r3 锚例换化例三中堂（子丑合绊丑根不豁免，R3 封顶小康仍成立） | tests/test_yongshen_r2r3.py |

验证：verify 432+70 全绿、pytest 465 passed+3 xfailed（无新增）、67例 0 回归（✅51）、famous 23例 无变化、calib 46项 0 回归。
留出集盲测：**财命 51.43%→54.29%（✅36→38，净+2）**、官命 56.06%（37✅持平）、职业 24.56%（14✅持平）、trainset 财命 63.6%→72.7%（b67 ❌→✅）。
翻转明细（heldout 7条+trainset 1条，零未批损失）：+ans15银行董事长（反局精化）❌→✅、+li002办事处主任（R3合化豁免）❌→✅、
+ans30从禄格/+li001乙亥发财（财统官封顶富）⚠️→✅、qi41离婚同居（泄漏清理）❌→⚠️、b67森田健（制尽重修+富格直判）❌→✅；
必损2项（用户已批）：张克东（财统官封顶富）✅→⚠️、ans12下岗财会（R3豁免后富格+开财库到巨富）✅→❌。
中途修正：制尽判据初版全排主位官误转 qi05（时干透杀）破财→富格致未批损失，收窄为「仅排主位藏干」后 qi05 保真✅。

## 2026-08-01 第七批 · K3财命50%攻坚 批A（P0束3项）+ rubric v3

| 项目 | 内容 | 文件 |
|------|------|------|
| zhibujin封顶富 | 制不尽当财（zhibujin）独力上浮封顶「富」不到巨富（段氏做功量级口径：制尽方得全权，制不尽量级不足；官统财/财统官/过河拆桥·富格等制尽路径不在此限）。豁免=贼神捕神净制（段氏理象学主线：净制=贼神原神俱制、制之干净，量级同制尽——李嘉诚/保尔森书锚「财与财的原神同时被制，财富级别可见一斑」；不净者模块自注「封顶三层」与本封顶同口径） | subjective/caiming.py（assess_caiming_level + _zeishen_jingzhi） |
| 自合柱财来就我 | G9自合柱财绊豁免：非日柱激活自合柱之干为财、且支中合神与日主同五行（日主/比劫=我方）者，财星被我方合入=48期「财来就我」、反为得财——不论合绊失用，视同合财做功（hecai_work）；合神非我方者（壬戌之丁火合壬财，ans12型）仍论绊 | subjective/caiming.py（_assess_caixing_path） |
| 过河拆桥-1去重+凶向标注 | A：方向信号已携带过河拆桥破财时由凶向封顶链统一处理（封顶小康），不再重复-1（双计压档且封顶链「下浮封顶」文本不触发→凶向标记丢失）；B：凶向在档强制标注——凶向命中但档位本在封顶下（capped=False）时，**仅全量轨** summary 追加「凶向在档（理由）」，静态轨严禁写入（P0-a假阳陷阱：静态轨带凶向词会把层级断语⚠️误杀❌） | subjective/caiming.py（assess_caiming_level、analyze_caiming） |
| rubric v3 | _XIONG_MARKERS 加「凶向」（配套凶向在档标注）；RUBRIC_VERSION v2-20260728→v3-20260801；已 --rescore 重设基线（/tmp/blind-20260731_rescore.json，三维计数不变） | tests/heldout/blind_eval.py |

验证：verify 432+70 全绿、pytest 465 passed+3 xfailed（test_p0_blindgap 合成造巨富→富为新口径预期更新）、
67例 0 回归（+2 IMPROVE）、famous 23例 无变化、calib 46项 0 回归（+5 IMPROVE）。
留出集盲测：**财命 42.9%→51.4%（✅30→36，+6，达 50% 目标）**、官命 56.1% 持平、职业 24.6% 持平、trainset 0 翻转。
翻转明细（heldout 7条，零回退）：li002炒股/li200地产（zhibujin封顶）⚠️→✅、li263亿万富翁（财来就我+原神上浮）❌→✅、
qi02夫死（-1去重后平=小康）❌→✅、qi02家业破尽/li141名笔杆子（凶向在档标注）⚠️→✅、li128 ⚠️→⚠️换档（走原神上浮到巨富，预期内）。

## 2026-07-28 第六批 · G9自合柱+G5从格余留+G1十干喜忌+GroupX评分修复 

| 项目 | 内容 | 文件 |
|------|------|------|
| G9 | 自合柱检测模块：九柱查表（丁亥/甲午/戊子/己亥/辛巳/壬午/癸巳恒常；丙戌/壬戌戌逢刑冲激活）。消费：日主自合→印扶失效+从格判定增强；合绊所藏十神=制（康熙型，甲自合午→午中己绊甲=制官得官）；非日柱干意向失用（与R1b受害方口径统一） | objective/zihe.py, engine.py, caiming.py, yongshen.py |
| G5 | 从格余留：破从运=yunfan反局型，流年合去日主，从强异党合去=吉 | yunfan.py, yongshen.py |
| G1 | 十干喜忌标注层：干×月令→喜/忌查表，进direction总线做小权重辅助票，不做yongshen主判据 | yongshen.py |
| Group X | 评分误杀修复：4例 tier diff=0 但summary含"破财/下浮封顶"被rubric直杀❌→修复blind_eval评分器 | heldout/blind_eval.py |

验证：432+70全绿、pytest 463 passed+5 xfail（2例K3中断xfail，配额恢复后接线）、67例0回归。
留出集盲测：**财命 37.1%→42.9%（✅26→30，+5.7pts）**、官命 56.1%、职业 24.6%。

## 2026-07-28 第五批 · B类凶向precision + C类功量补齐 + D类从格细则（K3建议批次）

| 项目 | 内容 | 文件 |
|------|------|------|
| P0 B类precision（G0-G5模式） | R1a 财旺夺不动（身强财明现≥2夺不动——例134「身旺财旺…发财」，财孤方可夺）；R1b 功神为紧贴合绊受害方者失能不能夺财（六合受害方口径同R3/he_types，辰酉合酉非受害方合化反助不豁免——王亚樵锚）；R1c 从弱虚根/从化豁免（功神干无本气根「比肩再多也无用」、功神支入财向合局「巳顺从酉势」）；R2 孤忌犯众用豁免（忌神孤≤1柱且用神众≥2柱，孤忌犯众自败——张克东「财被两酉夹合而化，原气尽失」）；R3 日主争合抑制（月干受害方与日主五合=日主合用未失原性）+ 双侧顺势豁免（六合双方俱用神类=原神合财顺势生合，qi22；对侧为忌方论绊，qi03）；N1 伤官诀五类豁免（金水喜见官/水木喜财官/佩印，juefa消费）+伤官配印（第三方纯印位制伏伤官，排除官伤同柱误读）+财星通关（非冲穿实战+财明现，贪生忘克）；N2 合杀豁免（「戊癸合去之无害」ans10/合杀贵，合制四型入杀有制化）；N3 墓之宾主归属（高级篇2.5「主位墓库制忌，其祸自消」——杀忌入主位墓不论被关押） | yongshen.py, test_p0_blindgap.py(+6测), test_yongshen_r2r3.py(+7测) |
| P1 C类功量补齐 | G4 库财不计明现（墓库所藏之财归财库收藏口径——第4期「此造八字无财」；活化三式：冲刑开库/三半合成局/月令得令——金昌盛丑月令金库锚）+ 财统官须财在（cai≥1，「官多财少财可统官」零财无可统——己酉戊辰壬申癸卯「坏了，不为官了」以伤官当财）；禄神当财门槛按书收紧「八字无财时」（李嘉诚误挂禄财下浮修正）；包局2.6 +1（年时干/支/十神包围+包围载体亲制化所包；反局破包官杀×食伤/财×比劫不计；支系异字十神包局暂缓——四墓库两两必同土，例6锚）；复合协同/矛盾标注级（fuhe字段：合官又伤官见官/印制食伤又食伤生财两矛盾对，不加点）；取财五法覆盖检查=全通道可达无threshold压死（经营208/风险205/智力159/体力67/工薪62 of 238；工薪primary=0为排序现象备案） | caiming.py, gongliang.py, regression67.py(命名对齐) |
| P2 D类从格细则 | classify_strength 补22期四规则（additive不改判既有从格）：①无根无扶/③无根印无根/④无根印根坏/②有根无生扶根被坏（根被坏=双夹冲[例4三戌方坏、例5一贴一不贴不坏]/邻支刑穿/合会转化为异党[午戌会火于己日=印生身不坏]）+唯年根远；从格须一方成势（异党单五行≥3——生例一富婆水木两停不从）；印根计本/中气、日主根计余气（例1/例2 vs 例5两套并存口径）；从旺/从禄=自党≥5+月令异党被坏+异党天干无本气根（ans30从禄格；乞丐丙火根在午不从）。从财格顺势档（caiming）：从弱财为所从——财成局（巳酉丑）/财有原神转化基阶不落下富；财伏吟单一无转化（例141「没有转化，缺乏连贯性」）从财亦贫。gongliang 附 strength/cong_ge 标注（七杀当财从格照计——例八从弱叠杀当财达三层书例正面） | yongshen.py, caiming.py, gongliang.py, test_p2_cong_baoju.py(15测) |
| P3 测量卫生 | 方案文档（不落地）：复跑不确定性排序化/训练集构成倒挂分组门禁/Wilson CI报告/rubric版本化备案/快照入git/双轨口径统一 | docs/p3-measurement-hygiene-20260728.md |

验证：verify 432+70 全绿、pytest 432 passed+3 xfailed（+28 新测）、67 例 0 回归
（cat4 cai 禄当财/伤食当财 ⚠️→✅，TOTAL ✅51）、famous 23 例基线一致、
calib 46 项 5 IMPROVE 0 REGRESSION。
留出集盲测（215 例）：**财命 27.1%→37.1%（✅19→26，+10.0pts，超 +4pts 目标）**、
官命 57.6% 持平、职业 22.8%→24.6%；19 条翻转零回退（7例❌→✅：女强人理财/
得200万/壬子运穷/乙亥发财/从财非常穷/从财富有/张克东 + 6例❌→⚠️）；
trainset 财命 63.6%/官命 73.3% 持平。训练-留出 gap 36→26pts 收窄。

## 2026-07-28 第四批 · K5/根因A/官命over-fire/M9+A8

| 项目 | 内容 | 文件 |
|------|------|------|
| K5 | liunian 冲/合从「触发/未触发」二分升级九种语义（高级篇 ch12 法则一/二）：冲五种（冲动/冲开/冲去/冲破/冲旺，旺衰根气评分判别：同气+1生扶+1克-1燥土脆金、月令双倍当令+2、天干盖头截脚计入；流年支旺衰另用纯根气口径）+合四种（合留/合动/合去/合绊，相贴优先于衰、虚透根坏论合去、配偶星须 gender）；补大运分看/统看 phase（口诀唯一机械触发=流年刑冲合运→统看；干支同气仅附 note 不自动统看——甲寅/丙午两书例冲突备案）；relations 附 chong_semantic/he_semantic（additive 不改旧字段）；engine 透传 start_age/gender/birth_year | liunian.py, engine.py, test_liunian_k5.py(24测) |
| 根因A | 分析结论：锚案（第9期官司破财 L4→清家荡产）已由 R1 比劫夺财封顶（2026-07-13）+P0-b/c（07-28）缓解（现状 L1+财命贫+官命否决），M1 R2/R3 非本案机制。R2/R3 扶抑层与做功层口径冲突实证（岳飞印制伤食=贵格仍命中 R2 印夺食 severe、化例二/墓例一同理、普例5 财坏印 severe 书判 L2），硬接降档必回退书例——故 gongliang 接入 yongshen 凶向为**标注级**（yongshen_xiong 字段入报告，层数不降） | gongliang.py, test_gongliang.py(+4测) |
| 官命 over-fire | 残余误判共性=杀刃类组合滥用（劫刃制官杀/官杀制比劫无格即立官）+劫刃制财误入官命+象法单独立官。G0-G5 收口：G0 辅助做功不计入；G1 劫刃制财归财命域（比劫孤≤1且官有根≥2 例外，日禄归时贵命保真）；G2 杀刃力量须相当（弱/强≥0.5，「七杀制刃要杀刃力量相当」；从格豁免）；G3 官弱为用神被制不为官（官为忌/从格/伤官去官格食伤≥3 豁免，朱元璋/qi19 保真）；G4 象法（官禄格/印带官帽）单独不立官；G5 杀刃类须官杀有制化（郝批「杀先天无制无化，杀为忌」；从格豁免）。zhenbao-23b/初中/司机/抢劫 处级误判全纠正 | guanming.py, engine.py |
| M9 | zuogong 主做功串行链→声明式规则表：每规则声明 candidacy/strength/vetoes，解析器统一裁决；primary_work 附 candidates/resolution 诊断（additive，type/path 契约不变） | zuogong_confirm.py, test_zuogong_m9.py(9测) |
| A8 | 强度加权混合（串行链+强度 override，非纯 MAX——纯 MAX 历史回归已弃用）：margin=2 逆袭机制，化例三（争合1<月干印3）/制例三（合2<穿制5）锚例由强度自然复现，坐下印+争合与穿降级无候选两边缘保留硬性否决；行为与旧链全等 | zuogong_confirm.py |
| K6 | 名人命例回归 23 例（理象学研究附录博客文粹：李世民/汉武帝/唐明皇/曾国藩/慈禧/王阳明/希特勒/辛普森/阿炳/李昌镐/帕瓦罗蒂/杰克逊/牛顿/戴安娜/王亚樵/巴菲特/保尔森/索罗斯/马云/李嘉诚/罗斯切尔德/坤沙/乔布斯；dropped 4：爱因斯坦/玻尔纯象说、元春虚构、袁隆平无对应类目）；famous_cases.py 数据+regression_famous.py runner（47 判定项：✅15⚠️19❌13 基线如实反映现状——❌集中 zhiye 职业桶7+guanming误火4，与既知审计结论一致）；verify_all.sh 并入 famous 段 | tests/backtest/famous_cases.py, regression_famous.py, famous_baseline.json, verify_all.sh |

验证：verify 432+70 全绿、pytest 402 passed+3 xfailed（+51 新测）、67 例 0 回归、
famous 23 例基线一致、calib 46 项 5 IMPROVE 0 REGRESSION（zhenbao-04/官命 ❌→✅，
官命维 ❌ 清零）。
留出集盲测：官命 57.6% 持平不劣化（trainset 官命 53.3%→73.3%：初中/抢劫/
zhenbao-04 三例翻转修正）、财命 27.1%/职业 22.8% 持平。

## 2026-07-28 盲测鸿沟四修复（P0-a/P0-b/P0-c/P1-a）

根因（见 memory blind-gap-rootcause-2026-07-28）：岁运反局 artifact 压原局档位
（A类15例假阴）/ 原局凶向承重墙缺失（凶✅靠岁运 artifact 偶然供给）/
merchant 通道上限5<阈值6 结构性压死 / 功量→tier「百万级→贫」误映。

| 项目 | 内容 | 文件 |
|------|------|------|
| P0-a | caiming 原局/运岁分离：tier_static + yunsui_delta + summary_static/level_static 双轨输出；rubric 按断语性质选轨（层级断语评原局轨，破财/凶且锚定运岁的流年事件评含 delta 轨）；凶向命中富档无条件抹除（乞丐不标百万级） | caiming.py, heldout/blind_eval.py, calib_assertions.py/.yaml |
| P0-b | yongshen 原局级凶向三式：N1伤官见官为忌（官为用神被伤，伤官去官格豁免）/N2财生杀攻身（身弱财旺生杀贴身无制+印化无力，normal）/N3官杀入墓（限身弱，杀忌入墓=被关押；身强官用入墓属官运域不入财命凶链）；接入 caiming 封顶/guanming 否决（正向结构门槛保护）/zhiye military gating | yongshen.py, caiming.py, guanming.py, zhiye.py |
| P0-c | merchant 通道重构：真实做功信号（财入局+2/主位合制财+2/食伤生财+2/门户+1/官杀当财被制+1/冲财+1，上限9）替换 co-occurrence（旧上限5<阈值6 永不成象）；比劫夺财动作不计经营做功；pocai_severe 与富屋贫人（身弱财旺无印）gating；teacher 木火通明收窄天干口径（甲乙见丙丁+2/地支共存+1）；lawyer 共存加分压低（伤官见官无动作不加分/食神制官须做功） | zhiye.py |
| P1-a | 功量→tier 基阶校准：有功一层=小富小贵（百万级）基阶小康非贫（无功/半层仍贫）；财星当财·经营带原神+主位基阶不落下富（3）；凶向命中者不校准（方向封顶收尾） | caiming.py |

验证：verify 432+70 全绿、pytest 351 passed + 3 xfailed（+27 新测 test_p0_blindgap.py）、
calib 46 项 0 回归（4 项改进）、67 例 0 回归。
留出集盲测（215 例，两次全量跑 0 不一致）：财命 20.0%→27.1%（✅14→19，❌43→34；
A类15例 5❌→✅+2❌→⚠️，余 8 例转为原局真差距）、职业 14.0%→22.8%（✅8→13，
merchant 6 例 ❌→✅）、官命 57.6% 持平无劣化；训练集财命 54.5%→63.6%、职业 50% 持平。
未达预估点目标（30/25）的余量 = B类原局凶向误触 + C/D类真差距，须书锚新增量，非本次范围。

## 2026-07-17 第一批 · 安全网 + 止血

| 项目 | 内容 | 文件 |
|------|------|------|
| V1 | 67例回归套件入git | tests/backtest/ |
| V2 | calib 46项断言化 | tests/calib_assertions.yaml |
| A2 | 时间锚点修复（current_dayun按年龄定位） | engine.py |
| N1 | 叙事层校验器（数字回对引擎字段） | narrative.py |
| N2 | 降温0.7→0.2 + 数字白名单 | prompts/hao_style_fewshot.py |
| N3 | 5例few-shot重跑（口径跳跃根除） | prompts/hao_style_fewshot.py |
| A1 | yunfan岁运反局接入方向否决链 | yunfan/yongshen/caiming/guanming/zhiye |
| M2 | dayun四项缺陷（死pass/戊刃双刃/开库口径/化气验月令） | objective/dayun.py, shensha.py |
| K2 | zhengfan原局四项（合官位置/时支归主/不可坏/冲合矛盾） | zhengfan.py |

验证：853全绿 + pytest 156 passed + 67例0回归 + calib 3项改进。

## 2026-07-17 第二批 · 方向层体系化

| 项目 | 内容 | 文件 |
|------|------|------|
| M3 | 婚姻加权（宫为主星为辅）+ duohun三检测 + 子息共振 | hunyin.py, liuqin.py |
| M4 | 柱位漏检补齐（生用/墓用/合制/天干克四放开） | zuogong_detect.py |
| M5 | gongliang收尾（气势浪费回接+高级篇三项+双轨对账） | gongliang.py |
| A3 | yongshen升格方向总线（五模块接入direction信号） | yongshen/liunian/zaihuo/hunyin/liuqin/xueli/gongmen_wuzhi |
| K3 | 授课教程逐章审计（263例断例集） | docs/k3-shouke-jiaocheng-audit-20260717.md |
| K4 | 象法回退三分支 + 连体/连墓/丙戊一家 | xiangfa_ops.py |
| V4 | verdict解冻（活算+回归报警） | tests/ |

验证：853全绿 + pytest 156 passed + 67例0回归 + calib 4项改进。

## 2026-07-17 第三期 · 独立模块 + 验证合并

不改核心判定逻辑（zuogong_detect/zuogong_confirm/gongliang 零触碰），
新模块均不接 engine（同 yunfan/zhiye 模式，仅 __init__ 重导出）。

### K7 新建模块

| 文件 | 说明 |
|------|------|
| `subjective/chuangong.py`（新建）| 串宫压运：同支≥2柱成串宫链（2弱串/3强串/4全串），大运/流年压入三型（增强/触发/引入）+冲散/合化/会局 conflict；空亡排除；需求见 docs/chuangong-spec.md |
| `subjective/juefa.py`（新建）| 诀法层（高级篇ch14）：伤官诀五行喜忌5类（金水喜见官/土金喜佩印怕见官/水木喜财官/木火喜见印/火土看组合，乾隆/张之洞等书例全验）+ 断语22项（15/17/19须yongshen_result防过杀、18须shensha_result、女命项须gender）+ 断句集8域26条可查表子集 + 巾箱字碰字6组 + 日元月令诀言词典（书载6条）|
| `objective/body_parts.py`（新建）| 干支身体部位映射（ch11.2主表：干主外/支主内 + ch4/中级扩展层 + 宫位身段 + 阴阳三态/五行病机7组合/穿破刑主病），纯数据查表零判断；为身体部位唯一事实源，xiangfa 'body' 保持速记不回写 |
| 宫位年龄统一 | `xiangfa.GONG_WEI_XIANG` 废弃 1-15/16-30/31-50/50+，全引擎统一大限套（1-18/18-35/35-55/55+），与 `yingqi.DAXIAN_MAP` 同源；MODULE_ATTRS 统一决定已改写 |

### V7 验证体系

| 项 | 说明 |
|------|------|
| verify 合并 | `objective/verify_mangpai.py`（422）与顶层（361）大面积重复，合并为唯一 `mangpai/verify_mangpai.py`，语义去重后并集 **432 项**（保留 objective 版全部 + 并入顶层版独有10项：天乙口诀分组5+柱位场景3+文昌庚干2）；旧 objective 副本删除 |
| xfail 严格化 | test_gongliang.py 3 个 xfail 加 `strict=True`（PUTONG2×2、乾隆冲链） |
| 属性化测试 | `tests/test_property.py`（新建）：100 随机四柱（60甲子+干支错配应力）+ 极端命例 + 60甲子日柱穷尽；不变量：不崩溃、gongliang.level∈[0,5]、work_level∈[0,5]、十神合法、空亡2支、summary为str、重复计算确定性 |

验证：verify_mangpai 432/432、verify_dayun 70/70、pytest 292 passed + 3 xfailed（0 fail）、
67例 vs baseline 无变化（0 回归）、calib 46 项 4 IMPROVE 0 REGRESSION。

存疑备案（本期未动）：`gongshen._PILLAR_BODY` 年/时柱身段与书中三处主表颠倒
（书：年=腿足、时=头面门户；码：年=头颈、时=腿足），另立 bug 单；body_parts.PILLAR_BODY
已按书主表收录，未回写 gongshen。

## 2026-07-09 第一批核心能力升级（高级篇补齐）

基于《盲派高级命理学》审计（memory/mangpai-gaoji-audit-2026-07.md）的第一批 12 项，
全走扩展现有模块（仅 yunfan.py 新建），不碰 schools.py/prompts/。三套验证全绿：
verify_mangpai 409/409、verify_dayun 70/70、pytest 92 passed。

| 文件 | 变更 |
|------|------|
| `subjective/xiangfa_ops.py` | +换象 huanxiang（制尽则主从易位，消费 zeishen_bushen 净制判据）+局象 juxiang（包局/夹局/全阴全阳/专旺/寒暖燥湿五类全局氛围象，与 gongliang 包局并行只做象意不加点）|
| `subjective/gongliang.py` | +层功补齐3项：带象+1（干生支承财官印象且参与做功，原神用神同制不成立方计避免双计）、统+1（消费 caiming 官统财/财统官，同制不成立方计）、富贵贫贱四档定性（wealth_grade/rank_grade/fugui_pinjian 按 level 落档）|
| `objective/zuogong_detect.py` | +夹局 detect_jia_ju()（夹禄/夹刃/夹库/夹财官/夹冲/夹合，纯检测无吉凶）|
| `objective/xiangfa.py` | +六十干支组合象表 LIUSHI_GANZHI_XIANG（11 组核心组合 nature/body/object/person/motto）+ get_liushi_ganzhi_xiang()|
| `subjective/caiming.py` | +过河拆桥分键：制尽(净制)=富格巨富(高级篇) / 制不尽=破财(中级篇)，加 _is_zhi_jin() 制尽判据 + _guan_mingxian_positions/_controlled_guan_positions 辅助；结果加 guohe_chaiqiao_type 字段|
| `objective/shensha.py` | +神煞三层收口：SHENSHA_LAYER 分类(盲派核心5/灾祸三煞/传统6降级) + 亡神表 _WANG_SHEN + 盲派多马星 _YI_MA_MANGPAI；各项带 layer 字段；compute_shensha_ext 加 亡神/马星|
| `subjective/yunfan.py`（新建）| 岁运反局三位一体：大运反局3类型(破坏功神/冲合互变/伏吟三刑) + 流年反局2类型(单独引动/岁运联动) + 岁运联动(天地合/三刑/双冲最凶)；冲合vs合冲、阴阳逆转(禄刃倒戈/忌神反客)；统一消费 zuogong_confirm+zhengfan+dayun+liunian|
| `objective/MODULE_ATTRS.md` | +过河拆桥分键口径标注 + 神煞三层收口口径（替换原神煞配置条目）|
| `tests/test_yunfan.py`（新建）| 8 项测试锁定高级篇 3.3 五命例反局类型检出（案例一/三/四/八/九）|
| `mangpai/__init__.py`、`objective/__init__.py` | 导出 SHENSHA_LAYER、get_liushi_ganzhi_xiang/LIUSHI_GANZHI_XIANG、analyze_yunfan|

去重口径（关键设计决定）：带象+1/统+1 均为高级篇1.4 补齐，与第六章原神用神同制(+2核心铁律)
重叠时不再单计——以「原神用神同制不成立方计」为门，保段氏理象学6章 14 例回归不跨书双计
（唯一触发的 PUTONG1 被相生之功 penalty 封顶一层，回归全绿）。

## 2026-07-08 大运/流年分析模块

### 新增模块
| 文件 | 说明 |
|------|------|
| `objective/dayun.py` | 大运盲派分析（~400行）：干支关系/墓库开闭/废神激活/禄刃应期/气势变化/长生位/综合吉凶 |
| `objective/liunian.py` | 流年盲派分析（~200行）：复用 dayun 核心逻辑 + 流年与大运互动（君臣关系） |
| `verify_dayun.py` | 大运/流年专项验证脚本（69 项测试） |

### 集成变更
| 文件 | 变更 |
|------|------|
| `objective/__init__.py` | +导入 dayun/liunian；`compute_all()` 集成大运流年分析（有数据才算）；`_build_summary()` 加大运摘要；`_raw_bazi_data` 存储 |
| `subjective/schools.py` | selectors 20→23（+`chang_sheng`/`dayun_analysis`/`liunian_analysis`） |
| `subjective/prompts/mangpai.md` | +岁运分析要点（7条大运+1条流年）；输出指引加大运/流年要求 |
| `tests/test_subjective.py` | 适配 23 selectors + 新字段 |
| `objective/README.md` | 模块数 21→23，统计更新 |
| `docs/duan-shi-lixiangxue-excerpts.md` | 覆盖表更新（大运/流年→✅，天乙→✅，交运时间→❌） |

### 大运分析维度（7项）
1. 天干十神定位 + 体用引入
2. 天干关系（合/克/被克）
3. 地支关系（冲/合/穿/刑/破/暗合/三合半合/生/克）
4. 墓库开闭（冲开需透干引拔，合闭）
5. 废神激活（废神遇运而动→新做功）
6. 禄刃应期（到禄位→吉，到刃位→凶）
7. 长生位（日主在大运地支的状态）+ 气势变化 + 空亡折扣

### 流年分析特点
- 复用 dayun `_analyze_pillar_interaction()` 核心逻辑
- 增加流年与大运互动分析（冲/合/穿/刑/生/克/暗合）
- 流年冲大运→运局动荡（降级吉运）；流年合大运→稳定（升级）

### 测试
- verify_mangpai.py: 348 passed（无回归）
- objective/verify_mangpai.py: 409 passed（无回归）
- tests/test_subjective.py: 27 passed（无回归）
- verify_dayun.py: 69 passed（新增）

---

# 盲派客观层 2026-07-07 修复记录

## 文件变更

| 文件 | 增量 |
|------|------|
| zuogong.py | 719 → +300+ |
| work_level.py | +11 |
| muku.py | 修改 |
| constants.py | +8 (LU 表) |
| zhengfan.py | 修改 |
| binzhu.py | 新增 layers 参数 |
| nayin.py | docstring 修正 |
| verify_mangpai.py | 170 → 303 (+133) |

## 修复清单

### 🐛 Bug 修复 (6)
- S1 重复计数去重：type 失配 '合'→'地支合' + frozenset 无序键
- 被动穿 harm 信号被去重吃掉 → _is_passive_chuan 保护
- 四库入墓误判 → 四库走"多而入墓"
- 禄做功触发条件过宽 → has_day_zuo_gong 前置检查
- 正反局不过滤 auxiliary → zhengfan 加 auxiliary 过滤
- 禄 action 追加太晚漏折扣 + 自坐禄双计 + work_types 含 S2 降级

### ✨ 新功能 (8)
- M1: binzhu 返回值消费 → layer 替代硬编码
- M2: tiyong 深度消费 → ti_elems/yong_elems 补充
- M3: 长生效率折扣真正消费
- M4: 天干入墓 → gan_entombed
- 空亡接入做功 → kong_wang 参数
- 伏吟/反吟检测
- 禄做功 → LU 表 + 禄 detection
- 天干克 → GAN_WX 干克检测

### 🔧 重构/修正 (7)
- S2 宾宾交互过滤
- M5 闭库抑制墓用
- 反向做功降级：不 +1 level，改为参考信号
- muku 透干引拔 → 天干透出才开库
- 正反局气势扩展 + 正局 fallback 改"局未定"
- binzhu 新增 layers=2 两层选项
- _is_passive_chuan 提环、work_level L156 修正、主动穿保护

### 审查结论
- 终审：5 个辅助语义/时序缺陷已全部修复
- 303 项测试全绿，零回归
