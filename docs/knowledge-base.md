# 盲派命理引擎知识库（knowledge-base）

> **用途**：新会话（任何 CLI，含 Kimi code）读本文件即获得 2026-07 ~ 2026-08 全部攻坚历史的关键结论，
> 替代逐次会话上下文。来源 = `~/.claude/projects/-root-metaphysics/memory/` 62 份归档 + 十批审计归档（kimi-audit-1~10）的提炼。
> 最后更新：2026-08-22（**修批 G3 引擎侧收尾收官·review6 清单全清**：#15 大眼锚注——回书裁决有明锚 zhongji:4531「丙主眼睛大」（+1478 丙食造「女命眼睛大」、lixiangxue:12632 黛安娜大眼睛旁证），xiangmao.py 眼象线补 inline 锚注（zhongji:1483/4531；lixiangxue:12632）；F-N2-1 秀气线 desc 去「漂亮」改「女看秀气倾向」（书原文 zhongji:3914-3915「女命秀气主漂亮」，措辞红线不进结论词），`_xm_sanitize` 连函数+调用删除（llm_prompt 锚定行/formatter 两路直传）；F-N2-2 judge 判据更新=_n2_eval.py 眼象线命中示例（独癸 desc 空不算命中）+F6-6 程度词/评价词/引申句入 lv=1+相貌 red 补复合词，_t3_eval.py 标注五维存档。哨兵+2（test_xiangmao G3 措辞/锚注）+2 测改名适配；六件套全绿（verify 432+70+64+20、pytest 860=840+1xf+19xp、blind vs g2 零翻转零抖动快照 `snapshots/20260822_g3.json`、双 seed 除 note 逐字节一致、67/famous 无变化、calib 由 pytest 覆盖）。引擎 compute_all 判定零改动、xiangmao 输出键结构零变。前一棒=**修批 G2 样式批落地→G1/G2 收官·系统发布态**：F6-7 臆造断语禁（迁移锚定「只述象与应期，不得输出引擎特征之外的结论式建议」，两分支同禁）+F6-8 性别分流（相貌锚定「按本造性别只写对应分支」+render 八字行补乾/坤造标记）+「数据不足」模板语明令（迁移/相貌无信号分支禁写）；统计口径后置项清零（`_n2_analyze` 改 hit 且 desc 非空，独癸 16 例误计修正，对齐后 251/251=100%）；存量 P2 归并=F6-3 reject 结构化字段（`reject: true`，闸不再按 detail 子串匹配）/F6-4 降级三返回自带免责行（`_DISCLAIMER_LINE`，不再单点依赖 service 前缀）/F6-5 lark_md LLM 路径 sanitize（`_larkmd_sanitize` 行首三符+附注 bullets 改 `· `）/test_f1_gate 七维 mock/schools 注释/「美丽」注释口径改准。哨兵 8 测先红后绿；六件套全绿（verify 432+70+64+20、pytest 838+1xf+19xp、blind vs g1 零翻转零抖动快照 `snapshots/20260822_g2.json`、双 seed 一致、67/famous 无变化、calib 常驻 2 条零新增）。上线 checklist 6/8 闭环（#3 真实凭证冒烟/#4 群聊 @bot 后置随首次上线冒烟）；review6 清单 G2 项全清，#15 大眼锚注随下个引擎批；收工 `docs/remaining-tasks-20260822.md`。引擎 compute_all 判定零改动。前一棒=**修批 G1 发布闸四项落地→七维正式发布 GO**：F6-1 降级提示语区分（死词拒出=「触发安全过滤」/一般失败=「暂不可用」）+formatter 直出补迁移/相貌两段（秀气线「漂亮」sanitize 入红线）；F6-2 句界符补「，；」+死词表 11→18（离世/去世/归西/病逝+过世/身故/辞世）；复合词双轨（`_XIANGMAO_FORBID` 扩标致/水灵/清秀/端庄+SCHEMA/锚定点名五词含甜美）；F6-6 顺手并入（锚定禁程度词/评价词/气质引申句）。哨兵 9 测先红后绿；六件套全绿（verify 432+70+64+20、pytest 831+1xf+19xp、blind vs n3 零翻转零抖动快照 `snapshots/20260822_g1.json`、双 seed 一致、67/famous 无变化）；r4 离线重扫迁移/死亡红线保 0（新词表抓「清秀」47 例存量，prompt 轨复跑收敛）。统计口径（_n2_analyze）裁定后置 G2。引擎 compute_all 判定零改动。前一棒=第六轮审查 W1-W5 收官（只审不改、纯本地零 API，六件套引用 N3 当日全绿不重复）：W1 F1+F3 十一项走查（F6-1 降级丢两维 P1/F6-2 误报窗逗号漏杀+死词近义词缺口 P1/F6-3~5 P2，18 合成例实测）；W2 N 系列代码（复合词真漏网 标致/水灵/清秀/端庄 P1 双轨补禁、相貌引用率统计口径 P1 对齐后 251/251=100%，P2×6）；W3 书锚复核（C 级违书=0，P2×2=「大眼」B 级泛化/「美丽」注释口径）；W4 体验样张 10 例（F6-6 程度词放大族 P2）；W5 跨层对照 10 例三层+294 例全量坐实（锚定忠实 10/10、断链全在 LLM 加料层：评价词添加 有神采32/明亮31/灵动20 并入 F6-6 族、F6-7 臆造断语「宜动不宜静」3 例 P2、F6-8 性别分流语未落地 11 例 P2、「数据不足」8 例存量再犯）。**发布判定：七维正式发布 NO-GO**——阻塞=P1 三项（F6-1/F6-2/复合词真漏网），统计口径裁定可后置，P2 全不阻塞；修批 G 规划=G1 发布闸四项一次六件套验收→转 GO、G2 样式批紧随；全量发现入 `docs/tasks/review6-fix-backlog.md`（接替 review5 已收官清单），报告五份 `docs/kimi-review6-w{1..5}*-2026082*.md`。前一棒 2026-08-21（动工批 N2b+N3 · 相貌维小修续打+七维收档收官（用户选 a 续打，引擎零改动）：「优美/柔美」复合词族以书锚为准入禁（书内零锚；校验器单字「美」已覆盖码不动，llm_prompt SCHEMA+相貌锚定禁令显式点名复合词族）；r4 复测 294 例谷段**相貌维红线 2→0 加严线达成**、迁移红线 0 保、L0=0/L1=1.36%/N1=1 例抖动/L2 既有=0.34% 压线（gj-低保伤官告诫式 mark 留人工），成本 ¥21.08；N3 heldout 复跑 blind vs gap2 零翻转零抖动（官 48✅/财 47✅/职 24✅ 保），快照=`snapshots/20260821_n3.json`；六件套全绿 pytest 822+1xf+19xp；发布 **GO**（F1+F2 落地+六件套复跑全绿）+七维 **GO**；收档=KB/CHANGELOG/收工 remaining-tasks-20260821/动工方案归档标完成，报告 docs/kimi-n2b-n3-final-report-20260821.md。前一棒 动工批 N2 · 七维复测（三轮收敛 L2 相貌 38→2/迁移维全绿/S1 裁决后新维翻转 0/30/F-V3-1 修复确认，¥67.2，详见 docs/kimi-n2-retest-report-20260821.md）。前一棒 动工批 N1 · 七维叙述代码批：DIMENSIONS+迁移/相貌、L2 两按维红线（迁移禁出境词/相貌禁美丑结论词带排除窗）、两锚定行，F1+F3 11 项随 f3d3e5e 并行落地，pytest 821+1xf+19xp。前一棒 2026-08-21（修批 F2 · 文档清零（纯注释+文档零行为）：第五轮审查 V1-V6 入档（新 §6.7 发现摘要+§9 总账+CHANGELOG+收工 go/no-go）；锚注清零=qianyi zhongji:4179→4180（模块 5 处+test_qianyi 注/函数名）、「结构同构」措辞改准（一合一冲机制不同构，措辞上限立论成立）、subjective/__init__ docstring 40→41+test_subjective 函数名同步；待修清单标认领（F1 #1-6 含丁眼锚注/F3 #11-15）。pytest 复跑 794+1xf+19xp 无意外；引擎零改动，基线仍=`snapshots/20260820_gap2.json`。前一棒 2026-08-20（缺口批3 · 三项收档+KB/收工全量同步（纯文档零代码）：世应/风水化解/时空测事收档口径入 §6.6；补同步缺口批1 qianyi/批2 xiangmao（§1.1 模块 29→31、§4.14/§4.15 新条、selectors 41、pytest 794+1xf+19xp、快照链 e3→gap1→gap2、§9 总账）；T2 五项缺口全处置=立 2 收档 3，缺口序列收官。前一棒 缺口批2 · xiangmao 相貌 marker 层：新模块 ~190 行（4 主线：秀气透干/金水伤官限辛/活木见火/眼象丙丁癸 +2 弱线：伤官合官杀魅力/身材曲线，纯 marker 无判定无档位），selectors 40→41，哨兵 test_xiangmao 7 测先红后绿，pytest 794+1xf+19xp，blind vs gap1 零翻转零抖动，基线=`snapshots/20260820_gap2.json`。前一棒 缺口批1 · qianyi 迁移/远行：新模块 ~230 行（原局三 marker 月日冲/日时合/马临年时 + 应期窗 马逢冲/合到门户/伏吟/冲出年时，措辞上限「迁移/远行」不出「出国」硬断语），selectors 39→40，哨兵 test_qianyi 11 测先红后绿，pytest 787+1xf+19xp，blind vs e3 零翻转零抖动，基线=`snapshots/20260820_gap1.json`。前一棒 2026-08-19 修批 E7 · 迭代 7+文档同步：官命矛盾 4 例定性全为校验器误判（叙述与引擎 is_guanming=False 一致，否定词出旧 ±2 窗）→ llm_channel 官命维否定窗 ±2→±5 对齐财档；llm_prompt 锚定补「可达/可至」治「可达中富」变体；E7 复测新发财档 3 假阳（让步同族）→ 校验器⑦补「虽」让步窗+归位语标记「档就是/档为」清零。294 例谷段复测：L2 财档 2→1（0.34%，唯一残留 gj-合财小康=真越限采样抖动 mark 留人工）、官命矛盾 4→0、L0/N1=0、L1 1.36%；pytest 实测 776+1xf+19xp 全绿；成本 $3.01（谷段）。详见 docs/kimi-e7-caifu-iter7-20260819.md。前一棒 修批 E6 · 财档迭代 6：llm_channel 校验器口径修 6 条（①让步封顶标记②泛指致富③引擎原文引用豁免（巨富除外）④小富=小康/偏下降半档⑤愿望条件句⑥富格/富档/富贵豁免+否定窗 4→5）+prompt 能力承诺/条件假设句锚定一行，L2 财档越限 16→2（0.68%）假阳 9 清零真越限 5→1，成本 $2.98 谷段，详见 docs/kimi-e6-caifu-iter6-20260819.md。前一棒 修批 E5 · 飞书加固（纯 feishu 包引擎零触）：重放窗口滚动清理（超 2000 不全清）+token 刷新线程锁+静默错解三例（123:45 非法报错/秒位/「四柱」触发词优先级）+500 脱敏（通用错误+日志详情）+HTTPServer 上限；哨兵 test_feishu 28→34，pytest 773。前一棒 修批 E4 · 引擎裁定批——纯注释零行为：U1 P1-1 穿引动裁定 a·改注（zinv docstring+两处行注口径更正备案，直锚 gaoji:17465-17484 降权、F6 实系「原局有穿+岁运引动」不触发本实现，补书据/改实现双否决，依据见 §4.13）+损子「冲」增补候选收档（孤锚 gaoji:14122，未达双锚）；哨兵 test_d6b_zinv 补备案注释不动行为，pytest 实测 767+1xf+19xp 全绿，blind vs e3 零翻转零抖动。前一棒 修批 E2 · 文档清零批——纯文档零代码：KB K1-K7+CHANGELOG C1-C4+收工 20260819 终态按 U4 漂移清单（docs/kimi-review4-u4-gate-20260819.md §2）清零，pytest 实测 767+1xf+19xp。前一棒 修批 E1 · 飞书上线必修（纯 feishu 包内，引擎零触）：client 捕获 token 99991663/99991661 清缓存重取重试一次+bot reply try 兜底（纯文本重发一次再败仅日志）+EncryptKey 检测告警丢弃+README 红线「勿配 Encrypt Key」+VT 启动强制（FEISHU_VERIFICATION_TOKEN 未配 RuntimeError）；哨兵 test_feishu +5→28 全绿，U4 飞书条件 GO 三 P1 清零=飞书上线闸通过。前一棒 飞书集成工程批：mangpai/feishu 新包 6 文件（client/router/service/formatter/bot+README，528 行），mock 全链三例跑通，引擎零触。前一棒 修批 D6b · 子女断法实现：zinv 新模块立 4 项（得子 3 机制/损子 5 机制/借腹 marker/时柱喜用腿——喜用腿落 liuqin，详见 §4.13），selectors 38→39，哨兵 test_d6b_zinv.py 12 测先红后绿，blind vs d3 零翻转零抖动，基线=`snapshots/20260819_d6b.json`；D6a=纯设计批（勘误 T2：F17 已立 zixi 三节，真缺口=应期+借腹，四书 60+ 锚）。前一棒 D5 工具/备案批——rescore glob 已修确认+G6 scrub/as_of_year/子夜带三备案入 §4.11+§9 同步，引擎零改动。前一棒 D1 数据批 · gold 修正 5 条+source 锚 15 处+raw_quote 1 处+calib zhenbao-10 dayun 误录删除，引擎零改动，详见 §9。前一棒 2026-08-18 修批C · 文档批（R4 数字过期×7+R3 行号微瑕+R1/R2 P2 散项，引擎判定零改动）：§0 成绩表/§2.3/§9 同步修批B 实测（heldout 官 48✅72.73/财 47✅68.12/职 24✅46.15，trainset 官 96✅83.48/财 58✅51.33/职 40✅47.06）；§6.1 职业残留 27→33❌、§6.3 财命残留 8/22→9/11；calib 常驻回归 1→4 条（zb-01官/05官/05层功/14a财）§2.3/§6.4/§7.13/§8 同步；§8 pytest 499→682 实测（任务书所引 668/648 系修批A/B 加 14 测前口径，以实测 682 为准）；R3 行号微瑕——test_yunfan+KB§5.5 理象学：7720→7586-7594、test_f12 6103-6104 标注研究版（＝理象学版：6022）、test_qiyun 「研究版」标签更正为理象学版、test_f15 gaoji:11964→11956/11053→11040、test_f14 :16455→16455-16457、test_f16 案例八补 :12862、test_gongliang 双锚行号更正（6470-6474→6467-6474、7182-7188→7181-7188）+KELINTUN 陈旧「偏低」注清（test_gongfei ±1 复核引用属实不动）；R1/R2 P2——engine.py:230 注释按 R2 口径重写（默认 day/透传名单更正/真重算者=liuqin）、xiangfa_ops `_shensha_by_pillar` 修批B 已修确认、shensha year_ref 子键簇死数据标注（仅灾煞 year_ref 活 zhiye:955）、format_shipaige_report 死函数删除（全库零引用；SHIPAI_DOMAINS 六域表留作碎片原文档案）、_auto_liunian_injected 标注不初始化（P3 无风险路径）；R4 P2 baseline67/famous_baseline 已 --write-baseline 刷新（IMPROVE 5+9 悬挂清零、0 回归）。早前：修批B · 引擎 P1（R1/R2 清单）：神煞 year_ref 并入×3——zaihuo 车祸/死亡两处双查合并补 year_ref 子键（旧「主键+day_ref」day_ref 实为死代码，year-only 劫煞/亡神/灾煞静默丢失，gaoji:7912 年支同查）；laoyu detect_jiesha_wangshen 裸 compute_shensha_ext 改走 resolve_shensha+并入双查子键、engine 链路补透传 shensha_result（配置断路修复）；xiangfa_ops `_shensha_by_pillar` 共象映射并入子键落柱；calib_assertions run_case 传 age=流年公历年−出生年（has_daxian 恒 False 旧口径修复，应期 6 断言 6/6✅）；同型备案=liuqin:872/gongmen_wuzhi×3 仅消费羊刃（非 reference 敏感）。哨兵=test_fb_shensha_yearref.py 5 测先红后绿；引擎基线=`snapshots/20260818_fb.json`，heldout 官 48✅/财 47✅ 68.12%/职 24✅ 0 翻转 0 文本抖动、trainset 0 翻转，67/famous 0 回归、calib 4 REGRESSION stash 实证=存量。早前：修批A · LLM 红线三项（R5 block×3）：A① siwang 死亡词典 scrub——zaihuo 键外泄漏（shipaige 寿元断语/liuqin 早夭/xiangfa_ops lianti 寿命 warning/guanming 制死/liunian 冲破主死亡）经 build_payload 统一 `_scrub_death` 过滤，引擎内部 siwang 保留（F14 不变）；A② zeishen 单源化——huanxiang 改消费引擎已算 zb_res（缺省 fallback 以 zuogong_confirm 标记后 wa 自算，裸 detect_relations wa 缺 auxiliary 标记曾致假「净」，11/509 矛盾例=9 train+2 heldout 口径统一），caiming `_zeishen_jingzhi` 补传 zg（27 例 jingzhi False→True 但已评分 heldout 4 例 tier 均不变）；A③ gongmen_wuzhi 从 selectors 摘除（is_wuzhi 98.8% 恒真，39→38 键，engine result 键保留）；预注册 heldout 例=shouke-qi15-房地产千万，预期不翻转（merchant 7→6 与 lawyer 平靠 tie_pri 保 primary）实测确认；哨兵=test_a_llm_redline.py 9 测先红后绿；引擎基线=`snapshots/20260818_fa.json`，heldout 官 48✅/财 47✅ 68.12%/职 24✅ 0 翻转，67/famous 0 回归（11 项 IMPROVE）、calib 4 REGRESSION stash 实证=存量。早前：F19 yunfan 两P1+扫尾备案。早前：F18 shipaige+gongmen_wuzhi 殿后批：shipaige 断语层按郑氏碎片整体重写（批8 P0×3——「官杀为子」冠名废→碎片:81 身旺财为子身弱印作儿（身强弱=比劫印 vs 财官食伤数量简化代理）；「劫财抗杀入牢狱」冠名冲突→碎片:90 劫财七杀两相连从军归事业域；「食神生旺」与数量诀「二食贪吃/三食愚钝」矛盾废），六域断语逐条=碎片原文+行号、未实现条目（性别/空亡/神煞/运岁/年龄段未接入）入 todos，方法论层重写为碎片§四；gongmen_wuzhi 决策落地=**正式弃用不接 zhiye**（F15 已在 zhiye._score_military 按书重写 8.2 六组），narrative 结论行通道切断（is_wuzhi 近恒真零信息量），engine result 键因 schools selectors 保护链保留；阳制阴口径按书修正（gaoji:11787-11788 阳气丙丁巳午戊戌制阴气辛酉癸子丑，含天干、子归阴、制类须阳为制方，与 F15 zhiye 同口径）；哨兵=test_f18_shipaige_gongmen.py 18 测先红 17 后绿；引擎基线=`snapshots/20260817_f18.json`，heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动（shipaige/gongmen 不进 blind rubric 与快照字段），67/famous 0 回归、calib 4 REGRESSION stash 实证=存量。早前：F17 xueli+liuqin：xueli 破坏之神改书口径财/伤官/比劫（zhongji:5397，枭移出学历章）——21 书例 5→9（test_f17 探针），年月比劫成群重扣（:5484）、配印/配杀伤官不扣（:5405-5407）；liuqin 星宫同坏总门补回（is_zaoshi=星坏∧宫坏，gaoji:13649）+子息原神取反修正（财星统看原神=食伤非比劫，:14116-14118）+三节补齐（排行诀/情谊诀/子女优劣，:14412/:14651/:14230）；哨兵=test_f17_xueli_liuqin.py 19 测先红后绿；引擎基线=`snapshots/20260817_f17.json`，heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动（xueli/liuqin 不进 blind rubric），67/famous/calib 0 回归。早前：F16 hunyin 四格机制重写：好婚姻宫星互制按势党定喜忌（冲穿刑非一律凶，四吉例 zhongji:4294/4300/4493/4504 差→好，制不住反锚戴安娜/4303 守差）+水中捞月三要素（正星坐宫+日主日支自合+偏星透干，zhongji:5081-5083）+关财门改女命专属运岁比劫夺财（gaoji:12963-12967）+独身四格按书诀（宫占比劫禄印/宫星互害反成克/星入墓不开/水中捞月，gaoji:13068-13070，纯阳纯阴/华盖自造格废）；哨兵=test_f16_hunyin.py 21 测先红 12 后绿；引擎基线=`snapshots/20260817_f16.json`，heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动（hunyin 不进 blind rubric），67/famous/calib 0 新增回归。早前：F13 shensha 五改：桃花书口径重建（lu_ban=禄合财官杀伤食 zhongji:1517，岳飞 performer 8→1 根因修复；performer 桃花信号=咸池日支起∨丙食伤透∨坐禄从艺 chuji:5871，居日柱补沐浴修饰 gaoji:13311）+起算主支默认 day（gaoji:7912，亡神/劫煞/灾煞/桃花/驿马恒年日双查、year_ref/day_ref 子键恒在不翻转）+zaihuo 马星 count 死判据改 in_pillars+戊双刃四处全刃表+reference 配置断路修复；哨兵=test_f13_shensha.py 9 测先红 7 后绿；引擎基线=`snapshots/20260817_f13.json`，heldout 官 48✅/财 47✅ 68.12% 不动、职 23→**24✅**（46.15%，梦露 ⚠️→✅），trainset collateral 备案 3 条（生例二经理 ✅→❌/带帽银行副处/yx-14300 ⚠️→❌——日支起算后咸池正检，非检测错误），帕瓦罗蒂 ❌→✅。早前：F12 guanming+juefa 七 P0：官禄格按书改「印生禄禄在主位」（zhongji:3969，慈禧书例哨兵）/制用四类补三反向（zhongji:3700/3842/3868，布莱尔戊癸合杀恢复）+印配比禄新检（总编羊刃制印库，三收窄：禄刃支/时支/印不透干——robber/ans17 反锚）/主位字门槛（zhongji:3683，印类豁免——ans46 沾岳父光书例存书内张力）/grade 映射收书（理象学:6103-6104，F6 口径差收口）/G5 杀刃制化条款废除（庭长羊刃合杀恢复，丁未孪生改由反局否决+positive 身弱收窄承担）/juefa 断语7 月克年方向（gaoji:20230）；联动 R1GUAN3（制去官之原神不否决）+N3GUAN（藏杀被制=统杀得权不否决，希特勒恢复）；哨兵=test_f12_guanming_juefa.py 13 测先红 12 后绿；引擎基线=`snapshots/20260817_f12.json`，heldout 官 50→**48✅**（72.73%，Δ-3.0% 噪声带内，collateral 备案 2 条 li002/li207 见 §6.2）、财 47✅ 68.12%/职 23✅ 守住，famous gm 三改善（慈禧/希特勒/李昌镐 ❌→✅）。早前：F11 yongshen+caiming 四 P0：22期例6 从官格修复（根被坏补第四式「晦」湿土晦火+成势闸根坏宽口径）/例7 未从修复（conc≥6 粗闸加「透干印有根不被坏」例外落细则判身弱）/财统官前置补「财生官相连且少方仅一位」腿（zhongji:2853 巨富书例补出）/过河拆桥验财生官位置相连（ans12 假富格撤销——⚠️→✅ 翻转确认，§6.3 必损移出坐实）；哨兵=test_f11_yongshen_caiming.py 7 测先红后绿；引擎基线 = `snapshots/20260817_f11.json`，heldout 财命 46→**47✅**（68.12%）、官 50✅/职 23✅ 守住，collateral 备案 2 条（li202/zj-工薪无官，见 §6.3）。早前：F10 yingqi_subj 寿元域四缺口：寿元星定位补印级+支/藏干食伤、坏关系补克/绝（正克限到位语境、盲派破按书收窄子卯/卯午）、寿元星藏干根被坏检出、engine 传 age 三要素 commit 名副其实——高级寿元章两书例哨兵先红后绿；引擎基线 = `snapshots/20260817_f10.json`，heldout/trainset 0 翻转 0 文本抖动，官 50✅/财 46✅ 66.67%/职 23✅ 守住，红线维持不进 engine 消费链，见 §4.10）。早前：F7 zhengfan 方向性大修：气势补势党识别（金水湿土党/火土燥土党，中级:186/234/246/255）+合坏接入 K2-3（:200/215 官坐实之支克合坏体）+日支「追求之意」（:147-148/240-242）+日支被得势方反制（同性冲+临月令党众，:266-275）+无势做功=正局（:139-140，旧「局未定」废，prompts 残留备案）——书第一章 7 书例 2→7 全命中，丙子戊戌/癸未丙辰两方向相反修正，见 §4.4；引擎基线 = `snapshots/20260817_f7.json`，heldout 财命 46✅ 66.67% 守住、官 49→50✅、职不动，trainset 财 58✅ 持平。早前：F6 gongliang 批（阎锡山解锁 L4→L3 合书「三层强一点」（化用高层+1 杀党≥5 加收纯化用门；checkpoint/calib 反锁以书为准改 L3）+奥纳西斯制库门 L2→L4（制墓库去 san_he 门改 同制+冲/刑 门、方局三会包制检出、方局围制+制库不净豁免、caiming 制库得财免禄/伤食下浮），见 §4.2；引擎基线 = `snapshots/20260817_f6.json`，heldout/trainset 0 翻转、财命 46✅ 66.67% 守住、巨富三锚不动）。早前：F5 zeishen 传导断口批（zeishen 消费 work_actions 滤 auxiliary——蒋介石 zb 误净→不净（书 6122-6126）；gongfei 删 auxiliary 排除——辅助功神仍是功神（理象学 6008-6010）；引擎基线 = `snapshots/20260817_f5.json`，heldout/trainset 0 翻转、财命 46✅ 66.67% 守住、巨富三锚不动）。早前：F4 虚实木性批（virtual_solid 只就一柱+坐印皆实、wood_type 水不生木之根=死木（岳飞/戴妃死木化），见 §4.12；引擎基线 = `snapshots/20260817_f4.json`，heldout/trainset 0 翻转 0 抖动、财命 46✅ 66.67% 守住）。早前：F3 岁运地基批（起运岁整数虚岁+整日差/晚子时推转一轮/交运年虚岁-1，见 §4.11；基线 `snapshots/20260817_f3.json`）；F2 数据表层批（anhe 删子巳+TOMB_MAP 加戌=土墓+muku 三 P0+传导两守卫，见 §4.9/§4.11）；F0 知识库勘误批（十批审计 46 条勘误+批1-4 散见 8 条落盘，见 §10）。

---

## 0. 速览（TL;DR）

- **项目**：段建业盲派命理引擎（Python3，无重型依赖；`yaml` 必备，`sxtwl` 用于节气，`anthropic` 软依赖仅叙事层）。
- **分层铁律**：`foundation/`（学派中性）← `mangpai/objective/`（纯检测）← `mangpai/subjective/`（解释判断）← `mangpai/engine.py`（编排），**单向依赖不可破坏**。
- **原著索引**（2026-08-25 建，机械生成零 LLM）：`docs/book-index.md` 总表 + `docs/book-index/index-*.md` 分文件（十书：理象学×2/初级/高级/中级/授课/渊海子平/子平真诠×2/滴天髓——章节标题+行号，导航用粗定位，精确核对仍以读原文行号为准）。探索型找锚（不知行号只知主题）先查索引再跳原文。
- **受保护勿改**：`subjective/schools.py`、`subjective/prompts/`、`objective/constants.py` 的数据表。
- **同音陷阱**：`gongfei.py`（功神/废神，`classify_gongshen`）与 `gongshen.py`（宫身，`analyze_gongshen`）同音异义**刻意共存**，勿合并勿改名；第三条（批8 增补）：`gongmen_wuzhi.py`=**公门武职**（gaoji 8.2），非「宫门五物」（五书 grep 零命中，批8 任务书曾误写）。
- **数据**：heldout 215 例（`mangpai/tests/heldout/cases.yaml`，⚠️ 只评估不反推）/ trainset 294 例（`mangpai/tests/trainset/cases.yaml`）。
- **当前成绩**（blind_eval rubric v8）：

| 维度 | trainset 294 | heldout 215 |
|---|---|---|
| 官命 | 96✅/19❌ = **83.48%** (n=115) | 48✅ = **72.73%** (n=66) |
| 财命 | 59✅/44⚠️/10❌ = **52.21%** (n=113) | 47✅/13⚠️/9❌ = **68.12%** (n=69) |
| 职业 | 40✅/12⚠️/33❌ = **47.06%** (n=85) | 24✅ = **46.15%** (n=52) |

- **验证口径**：`verify_mangpai.py` 432 项 + `pytest mangpai/tests/` 858 collected（838 passed+1 xfailed+19 xpassed，G2 实测；G1 记 831 passed、N2b+N3 记 822 passed、N1 记 821 passed、缺口批2 记 794 passed、批1 记 787 passed、修批E6/E7 记 776 passed、E5 记 773 passed（feishu 28→34）、修批E1 记 767、U4 记 762 passed（D6b+12/feishu+23）、D5 记 747 collected/727 passed、D4 记 727 同口径；修批B/C 记 682、修批A 记 677、F19 记 668/648、F18 记 664、F17 记 646、F15 记 606、F13 记 585、F12 记 576、F11 记 543、F10 记 536、F9 记 532、F7 记 517、F6 记 529、批10 旧记 499 均作废）+ blind_eval 快照零翻转 + 双 seed 逐字节一致（旧 853 口径 2026-07-17 起作废）。
- **三维攻坚已收官**（2026-08-14 职业批4）。残留❌全数收档备案（见 §6），后续批次须先读本文件 §5/§6 防重复踩坑。
- **十批全模块审计已收官**（2026-08-17）：P0=96/P1=245/P2=259，修复批次 F0-F19 已批准（见 `docs/audit-progress-20260816.md`）；审计勘误本文件记录见 §10。

---

## 1. 架构与模块地图

### 1.1 目录

```
foundation/objective/    ganqing.py(滴天髓干支性情65+5条,条件->行为映射) nayin.py(纯计算)
mangpai/
  engine.py              MangpaiEngine.compute_all() 编排器
  __init__.py            公共 API re-export 枢纽（from mangpai import X 对一切可用）
  calib_zhenbao.py       郝金阳10例校准脚本（zhenbao-01~23b）
  verify_mangpai.py      432 项自洽检查（唯一版本，objective 副本已删）
  verify_dayun.py        70 项大运检查；verify_layer1.py 64 项基础层
  verify_layer3_checkpoint.py  20 项方向层检查点
  objective/  26 模块：bazi_calc/canggan/changsheng/constants/nayin/shensha/shenshu/
    xiangfa(静态四层象数据)/binzhu/tiyong/gongfei/gongshen/muku/anhe/zihe/he_types/
    zuogong_detect(纯检测)/virtual_solid/wood_type/soil_type/jiaoyun/dayun(纯检测)/
    yingqi/biqi/body_parts/advanced(deprecated shim,lazy-import zhengfan)
  subjective/ 31 模块：zuogong_confirm(analyze_zuogong+assess_work_level)/zhengfan/
    gongliang(1-4层功量)/zeishen_bushen/yongshen(方向层R1-R3+N1-N3+classify_strength)/
    caiming/guanming/zhiye/hunyin/xueli/laoyu/liuqin/zinv(子女岁运应期+借腹,D6b 新模块,§4.13)/
    qianyi(迁移marker+应期窗,缺口批1,§4.14)/xiangmao(相貌marker层,缺口批2,§4.15)/
    zaihuo/gongmen_wuzhi/xiangfa_ops
    (换象/局象/化象/借象操作层)/yunfan(岁运反局)/dayun/liunian/shipaige/juefa/
    chuangong/yingqi_subj/narrative/schools(保护)/prompts(保护)/
    llm_channel/llm_prompt/llm_backend(LLM 三件套,§8 有载)
  feishu/      飞书集成包(飞书批+E1 上线必修)：client/router/service/formatter/bot+README(528 行)
  tests/
    heldout/   cases.yaml(215) blind_eval.py snapshots/ diag_case.py _*_diag/_*_sim(诊断考古)
    trainset/  cases.yaml(294)
    backtest/  regression67.py famous_cases.py famous_baseline.json regression_famous.py
    calib_assertions.py/.yaml  test_*.py(794 测,含 test_feishu 34/test_d6b_zinv 12/test_llm_channel 27/test_qianyi 11/test_xiangmao 7)
  docs/        duan-books/(段氏五书+珍宝50期+授课教程原文txt) 各分析文档
  CHANGELOG.md           批次变更记录（第七批起有书写惯例）
docs/                    任务书(tasks/)、remaining-tasks 系列、本知识库
```

### 1.2 关键调用链

- `MangpaiEngine.compute_all()` → 各 subjective `analyze_*`；`result['gongshen']` 已接入但**不进** `_build_summary`（verify_dayun 文案断言约束）。
- 官命判定链：`classify_guanming_combo`（制用四类**皆双向**（F12 补全）+印配比禄+生用化用，G0-G4/G6-G7/G9 门——G5 杀刃制化条款 F12 废除）→ `is_guanming_raw` → `analyze_guanming` veto 链（反局/岁运反局/牢狱/比劫夺财/过河拆桥/R2/R3/N1/N2/官杀入墓/主位体坏），门槛保护 `_has_positive_guanming`（**从强一律非正向**——贪财坐牢例锚；**F12 起身弱同收窄**：官杀有根/官带财帽于身弱者非正向——丁未孪生造反局牢狱锚；须有官杀有根/印化官杀/官禄格/印带官帽/官带财帽）。
- 财命双轨（P0-a）：`tier_static/summary_static/level_static`（原局轨，yunfan 不入链）+ `tier/summary`（含 yunsui_delta 全量轨）。**「凶向在档」强制标注仅写全量轨**——静态轨结构性不可见凶向，rubric 对破财/凶断语一律评全量轨（v7）。
- 职业：`classify_zhiye` 七桶打分（military/lawyer/teacher/doctor/accountant/merchant/performer + laborer/unemployed base_career），`_MIN_SCORE_THRESHOLD=6` 以下为「无明确职业倾向」fallback；同分按 tie_pri 序；base_career 以 caiming `tier`（**全量轨**，zhiye.py:1074——⚠️批7 勘误：非 tier_static，岁运 delta 可改变 laborer/unemployed 判定；tier_static 仅用于官杀为忌 gating :1372）贫/小康为闸（财命-职业硬绑定，已知缺陷 C4——**F15 审查**：根因=caiming 财统官（b）腿不验身弱（caiming.py:779-785），zhiye 消费侧扩展 gating 与 7.2 案例一董事长双锚同构不可分已撤回，修复留 caiming 后续批）。

---

## 2. 铁律与测量纪律（P3 测量卫生 M1-M5 + M3）

### 2.1 铁律（违者成果作废）

1. **留出集只评估不反推**：heldout 215 例严禁用于修引擎；任何「因 heldout 某例失败而改规则」= 污染。误用后该例须迁 trainset（单向不可逆，heldout 优先）。
2. **扩容去重硬顺序**：新例 8 字（性别无关）撞 heldout → 禁入；撞 trainset → 并 source；同盘异时辰 → A/B 标注并存；理象学两版只扫研究版；时辰推定例可入但注明 confidence、不作拟合孤锚。
3. **断语只录书明文**：verdict 禁从引擎输出反推；无明文不录该维；raw_quote 逐字+source=书:行号。财命层级 label **勿带干支锚**（防误触 v6 delta 轨），事件断语（破财/凶）**须带锚**。
4. **引擎改动须 ≥2 例同构+书锚**，禁逐例调参。
5. **每批门禁**：heldout 快照零翻转 + trainset 分组门禁 + 双 seed 一致 + 67例/famous/calib 零新增回归。扩容批 heldout 必须**逐字节不动**（引擎未改），动了=确定性或泄漏事故。

### 2.2 测量卫生机制（blind_eval.py）

- **M1 确定性**：`PYTHONHASHSEED=0` 与默认 seed 各跑一次输出须逐字节一致。subjective 11 处 set 迭代已排序化（gongliang 5/yunfan/zeishen/hunyin/zaihuo/zuogong_confirm/detect_bao_zhi）。--diff 报告末尾「文本抖动」段 >0 即卫生失败（score 不变但 engine 字段变；单边缺失案例不计）。
- **M2 分组门禁**：财命按 verdict 首词分组（巨富/富/小康/平/贫/破财/凶）各报 n/✅/⚠️/❌/acc，防汇总掩盖分组失衡。
- **M3 显著性（2026-08-14 新增）**：汇总行后附 `[·CI95]` 行（Wilson 95%：acc±half(下界)）；--diff 附显著性判定——**|Δacc| > 两 CI 半宽之和** 方判显著改善/退化，余记「噪声带内」（同案例配对设计下此约定偏保守）；**验收门槛以 CI 下界计**。
- **M4 rubric 版本**：口径改动须 `--rescore` 重评+重设基线+写 RUBRIC_VERSION changelog（blind_eval 文件头）。版本史：
  - v2 层级断语差0不再因 summary 凶向词直杀（Group X 过杀修复）；
  - v3 `_XIONG_MARKERS` 增「凶向」（配凶向在档强制标注）；
  - v4 military 桶删 武/兵/保安/保卫（泛文/履历/行政岗假阳）；
  - v5 `_ZY_EXCLUDE` 语境排除：performer 桶 色情业/歌厅/舞厅/歌女 作废，military 桶 参军 作废（转 unscorable 不入准确率）；
  - v6 运锚层级断语判轨：断语干支锚=所喂运岁且原局轨差≥2 → 评 delta 轨（**差≥2 门槛是关键**，裸锚匹配会误杀 li001/li131/qi22 乙亥发财）；
  - v7 破财/凶断语一律评全量轨（凶向在档仅全量轨可见）；
  - v8 `_ZY_EXCLUDE['military']` 增「冠军」（体育冠军=比劫做功，substring 误命中）。
- **M5 快照**：`heldout/snapshots/*.json` 入 git（.gitignore 例外），带 `_meta`（git_sha/rubric_version/note，加载剥离）。基线链：`…→20260808_q(官命批)→r(职批1,rubric v8 rescore)→20260814_a(职批2)→b(职批3)→c(职批4)→20260817_f2~f7(F2-F7 修复批)→f8(yunfan 三P0)→f9(laoyu 四P0)→f10(yingqi_subj 寿元域四缺口)→f11(yongshen+caiming 四P0)→f12(guanming 六P0+juefa 断语7)→f13(shensha 五改)→f14(zaihuo+LLM 红线)→f15(zhiye 8.2 军警组合)→f16(hunyin 四格重写)→f17(xueli 破坏之神+liuqin 总门/原神/三节)→f18(shipaige 重写+gongmen 弃用)→f19(yunfan 两P1+扫尾备案)→fa(修批A LLM红线)→fb(修批B 神煞year_ref+calib age)→20260819_d1(D1 gold修正)→d2(D2 入口guard)→d3(D3 dayun补供)→d6b(D6b zinv)→e3(E3 数据锚注)→20260820_gap1(缺口批1 qianyi)→gap2(缺口批2 xiangmao)→20260821_n3(N3 收档 heldout 复跑,当前)`（D4 prompt迭代/D5 工具备案/E1 飞书必修引擎零改动、feishu commit 零引擎文件，均无快照合理；d3→d6b 跨档 U4 实测零翻转）。全 49 份快照 meta 完整（U4 抽检 4 份，rubric v8 一致）。
- **用法**：`python3 mangpai/tests/heldout/blind_eval.py --out snapshots/<批>.json --note "<验证状态>" --baseline snapshots/<上一批>.json`

### 2.3 评估纪律要点

- **trainset/heldout acc gap = 过拟合度量**；扩容后 trainset acc 必降（幸存者偏差消退），**不可与旧小样本基线比**（23→91→119→294 每次重设基线）。
- 当前 heldout 职业 46.15% < trainset 47.06%、heldout 财命 68.12% > trainset 52.21%——构成不同，只看集内趋势。
- 小样本噪声：n≈50-115 时 Wilson 半宽 ±9-13pp，个位数 ✅ 变动多在噪声带内——结论以 CI 下界+显著性判定为准。
- 模拟器（_zy*_sim/_gm_sim）只含 gold 可评例，**unscorable 例换档对 sim 失明**——落地后必须 blind_eval 全量 diff 兜底（职批4两处换档均靠此抓回归险）。
- famous/calib 出现 REGRESSION 先 stash 实证是否存量——⚠️批7 勘误：罗斯切尔德 zy「批11 存量」**已自愈**（famous_baseline.json 该条即 ✅merchant，重跑仍 ✅，同分 6:6 靠 tie_pri margin=0 仍脆；乔布斯 baseline ❌→当前 ✅merchant），calib 常驻回归 2 条=zhenbao-01 官命/zhenbao-14a 财命（批13-15 存量起，修批B stash 实证=存量，R4 复核；原 zhenbao-05 官命/层功两条系 gold 标注错非引擎错，D1 数据批按书修正消化）。
- 853/432 是自洽检查非命例回归——**绿≠无回归**，回归判定以 67例/famous/calib/blind 为准。

---

## 3. 三维评分口径（rubric v8 现行）

- **官命**：verdict 是/否 ↔ is_guanming 二元，符✅不符❌。
- **财命**：层级断语（巨富/富/小康/平/贫，平按小康计）评**原局轨** tier_static，差0✅差1⚠️差≥2❌；差≥1 且 summary 含凶向词（破财/比劫夺财/坐牢/牢狱/官非/下浮封顶/凶向）直杀❌。破财/凶断语一律评**全量轨**（v7）；运锚层级断语按 v6 例外。破财=凶向标记或 tier 贫✅小康⚠️余❌；凶=凶向标记✅贫⚠️余❌。
- **职业**：verdict 关键词→桶集合（_ZY_RULES 粗口径+_ZY_EXCLUDE 语境排除），primary 命中✅/空⚠️/余❌；无法映射的 verdict（官员/农民单标/色情业/司机等）记 **unscorable 不入准确率**。
- 财命判轨核心：**层级断语=原局层级**（段氏「八字为车，大运为路…过路财神」——断语只称运中层级者不评原局轨）。

---

## 4. 已固化规则要点（按模块，一句话/条）

### 4.1 做功层 zuogong（detect=objective，confirm=subjective）

- 主功优先级链：日干合 →（日干合+日支 high 穿则让位 `_chuan_yields`）→ 生用 →（食伤合制则让位 `_has_shi_hezhi`；伤官入墓 `gan_entombed` 让位）→ 化用成局（须月干印/坐下印非合中心）→ 弃干看支 → 禄/比。M9：串行链已改声明式规则表（candidacy/strength/vetoes+统一解析器），A8=margin 2 强度逆袭（化例三/制例三复现）。
- 入墓之物不做功（食伤地支入墓 skip 生用）；日支≥3 合中心之食伤不泄秀（he_center_skip）；时支本气食伤+坐支藏财+天干无明财=内食神格生用（企业家）。
- L5 连珠成势须三合局本身为主功（`chengshi_primary` gate）；纯强度 MAX 聚合已证回归弃用，保守混合（串行链+3 决策点强度 override）。
- 化用 detect 含坐下印；前置校准：涉日支制两端有一为印=化用路径内象不抑制；化用两 type（合化/杀印相生）共享 action='化用'，测试过滤按 type='合化'。
- 穿=害等价；寅巳既穿又刑沿「刑去重穿」约定。

### 4.2 功量层 gongliang（1-4 层，比 zuogong.work_level 准，engine 已接）

- 加分：原神用神同制+2（**须冲/克/穿实制佐证**，合族单独不支撑——PUTONG2 书锚；多候选偏好财/官杀为用神）；制墓库+2（F6 去 san_he 门——书 6037 无三合条件，两书例丑未冲/戌刑丑皆非三合；新门=同制成立+冲/刑真制库动作+墓库为制用目标（冲互向 from 端亦计），同制位为墓库不重计，穿/克不计——例六/岳飞子未穿、例七寅克戌书均未计）；七杀当财+1（透干+与制局目标同根）；入墓+1；库源+1（须同制成立；**库源×入墓同源去重**——引出与收藏同一墓对相反读法不重计）；包局+1（san_he 或 **方局三会**——法则6 明载三会，奥纳西斯巳午未书例；方局支须以冲/刑作用于方局外之支，合/克/穿/破不计——cj-工薪实证）；层层相制+1（克链≥2，冲链不计）；月令+0.5；连墓加层（月令入墓于已计源头之库+1，李嘉诚第4点）；金字塔门（zb 链长≥3+冲边≥2+zb 净 → 乾隆 L4）。
- 克链入墓惰性：已入墓元素出边不入链。
- 封顶：制不净→3 层（化用成局路径除外）；相生之功→封顶 1 层（**日干无功弃之不看**——日主自克非制）；相克之制→封顶 2 层。
- 7d 化用成局/从杀格：纯化用路径（yuanshen_hit is None）+杀印相生/杀≥5+日主从弱 → +2/+1 可达 L4；不净封顶对化用成局路径豁免。**F6**：+1 的杀党≥5 触发加收纯化用门（无墓用+无非辅助制用/合制动作）——阎锡山造为纯制局读法（理象学 7182-7188「三层强一点」、授课38期「旺忌神弱制」非从杀），+1 撤销后 L4→L3 合书，checkpoint/calib 旧锁 L4 已改 L3（以书为准）。另 F6：**方局围制+制库双结构不净封顶豁免**（奥纳西斯书明断四层，理象学 6470-6474）。7f 杀库作功放门实证误伤 zj-邢铭芬（平命越 L4❌）维持不放，杀库路径由制墓库 block 承担。
- 包制 distrust 有条件翻转：bao_zhi 检出+zb 净+非三合成局 → 采信围制+1（克林顿 L4/岳飞 L3）；净 override；`_bao_suppress_pocai`（围制下比劫=制财非夺财）。
- 带象+1/统+1 以「同制不成立方计」为门（跨书去重）；富贵贫贱四档定性 wealth_grade。
- `boundary` 字段（score 距层沿≤5 或 bao 翻转 decisive → 'Ln/Ln+1边界'），只标注不改 level。
- **判别器易错**：sha_wx 用 `WX_KE_ME`（克我=官杀）非 `WX_KE`（我克=财）。

### 4.3 贼神捕神 zeishen_bushen（objective 检测，subjective 聚合）

- 党势权重=透干2/本气2/中气1/余气0.5/原神0.5；party≥**4.25** 成势（`_CHENG_DANG=4.25`——⚠️批2 勘误：旧记「≥4」与码漂移 0.25，以码为准；包制/太旺/overkill 4.25/6.0/3.0 皆启发式阈值无书定量）、≥6 太旺；净制=被制方孤立+制方成党成势；不成=捕≥6+贼孤立+捕/贼≥3 overkill。
- 五易错点：①合制仅取克合（生合不计——李嘉诚午未生合排除）；②主位做功优先（日柱为 doer）；③日主不算贼神原神；④包制内柱本气皆入制局目标集（原神同制→净）；⑤冲边优先于克边（冲为链骨）。
- `_zeishen_jingzhi` 是 caiming **两处**净制豁免的共用判据（caiming.py:1532/1545——⚠️批6 勘误：旧记「三处」有误）（李嘉诚/保尔森巨富锚保命符）。

### 4.4 正反局 zhengfan + yunfan（岁运反局）

- 原局反局：K2-3 时支不可坏（含 F7 **合坏**分支：官坐实之支克合坏体，中级:200/215）/K2-4 冲合矛盾/K2-5 合官位置（合年月官+官五行克日主不计日柱指向=反局豁免方向）、五行相背条款、K2-6 单向旺势/**势党**同党豁免（li101 红线）、F7 **日支追求之意**（日支六合 X 而 X 为得势方所克=反局，中级:240-242；反锚壬子庚戌辛丑己未）与**日支被得势方反制**（同性冲+X 临月令党众≥2+反向制式=反局，中级:266-275；自刑/伏吟非反制=王阳明锚、穿刑非对力=zhenbao-05 锚）。时支不可坏特判（己甲戌/辛丙申）。
- **F7 气势势党**（_compute_qishi 最前）：金水湿土一党（金+水+丑辰）/火土燥土一党（火+未戌），≥半数且压倒对方即成势（中级:186/234/246/255——湿土不计则书「金水成势」不可达）；无势+日柱做功=正局（:139-140，旧「局未定」口径按书改正，prompts/mangpai.md 受保护残留备案）。书第一章 7 书例哨兵=test_zhengfan_shuli.py 8 测（F7 先红 2/7 后绿 7/7+朱元璋 guard）。已知备案：卯戌合化火为财之化象未建模（yx-建筑 trainset 财 ✅→❌ 备案）；旧五行相背 proxy 曾歪打正着 gating 军警（yx-泥瓦匠 ⚠️→❌ 备案）。
- yunfan 大运三类型（批3 重写后口径）：T1 破坏功神 harm 仅{冲,穿}+例外运破日主禄/刃=破护体（阴阳逆转）；T2 冲变合须原局冲做功参与字，合主位字=护体解冲豁免；合闭墓库须原局有冲开该库之冲；T3 伏吟/三刑须伏吟支激化原局已有刑对（合解刑豁免、刑开库豁免），单字伏吟/自刑不即反局；新增 T1 杀临攻身（身弱非从+运支官杀五行+透干=虚杀逢根）、T3 伏吟干被克坏（非日主干伏吟+原局有干克之）。**忌神反客大运侧已移除**（判别集 4/4 假阳，流年侧引动忌神保留）。**F19 补两条**：大运侧合变冲须冲原局合做功参与字（包工头己酉运假阳消除，与冲变合 A14 收窄对称）；大运侧补挂禄刃倒戈（案例七丁卯运锚 gaoji:3761-3764）+禄/刃字须在局守卫（批4 P2-1 根治）。
- 大运/流年反局已并入 yunfan.py（fanju.py/suiyun_fanju.py 拆分未做，整合版即现行）。

### 4.5 方向层 yongshen（吉凶方向=准确率最大杠杆）

- `classify_strength`：身强/身弱/中和/从强/从弱；从格四规则=根被坏**四式**（双夹冲/邻支刑穿/合会化入异党——印生身不坏；**F11 补第四式「晦」**：邻支湿土丑/辰晦巳/午火根失其性，zhenbao:739-743 例6 丑晦巳/例3 辰晦火）+一方成势闸（异党单五行主气≥3——⚠️批6 勘误：书无此数值阈值，系自造后验归纳，应知；化势宽口径 selfc<conc **或日主根俱被坏（F11，例6 申子半合化水实3成势）** 可用合局计数，两停且根未坏仍主气）+从旺从禄三道闸；印根计本/中气、日主根计余气两套并存（22期例1/2 vs 例5，批6 独立复核属实）。**F11：conc≥6 粗闸收窄**——透干印有根且印根不被坏者不能从、落 22期细则判身弱（例7「乙木印星根在亥…不能从以身弱看」zhenbao:744-747；段氏明文反对衰旺计数 shouke:454；藏干印不作救否则粗闸无一得行）。
- R1 比劫夺财：功神=比劫制财且身强/从弱 → 凶；**day_gan 不作比劫 actor**（日主克财=我克者财）；severe=比劫≥2柱或 hits≥2。豁免族：R1a 财旺夺不动（财≥2）；R1b 功神合绊失能只取受害方（_LIUHE_VICTIMS：子丑两伤/卯戌戌/巳申申/辰酉辰/寅亥寅/午未未——辰酉合化反助不豁免教训）；R1c 从弱虚根/从化（功神干无本气根/支入财向三半合局）。
- R2 忌神制用神：身弱/从强→财坏印、身强/从弱→印夺食；忌神失能三豁免（紧贴合绊/贪合忘克三字全三合/日支自合柱合神为忌同类）；从格忌孤用众按主气计（中气藏干不计）。
- R3 用神被合绊：紧贴六合受害方+年月干五合互绊；忌神受绊不触发；冲/穿做功参与抑制；合化出喜用豁免（化气∈喜用且≠受害方本行）；**日主自合财（日支主气=财+合神为财，戊子/壬午型）不论绊**（G9 配套）；日主争合整对豁免限扶抑格（从格不论争合）。
- N1 伤官见官为忌：扶抑官为用+伤官明现+正官明现+非辅助实伤；豁免=伤官去官格（官为忌）/伤官诀五类/伤官配印（第三方纯印位）/财星通关。
- N2 财生杀攻身：仅身弱+财明现≥2+七杀贴身（**非年柱**——年杀不论）+杀无制+印化无力，severity=normal（severe 曾误触留出集富命被否）。
- N3 官杀入墓限身弱（身强官用入墓属官运域）；杀忌入主位墓=制忌自消，宾位墓方论被关押。
- 聚合 `mingju_xiong`/`mingju_xiong_severe`；消费：caiming 封顶、guanming 否决（受正向结构门槛保护）、zhiye military gating。
- ⚠️ 扶抑用忌 vs 做功口径根本冲突（岳飞印制伤食仍中 R2 印夺食）——veto 修复一律走**消费侧域级过滤**（如官命 veto 链），不动检测器。

### 4.6 财命 caiming

- 财富看法：财星当财/禄神当财（八字无财时口径）/伤食当财/官杀当财两式（财统官/官统财，须 cai≥1 零财无可统；**F11 前置两腿居一**：(a) 主位制宾官旧口径 + (b) 财生官相连且少方仅一位——书注「少指只有一个，且财官必须相连了，即财生官了」zhongji:2821，补出 zhongji:2853 巨富书例；官统财「官仅一位」书例因 guan≥2 外闸仍漏=批6 P1-2 留后续）/制不尽当财/过河拆桥（富格 vs 破财分两键——⚠️批6 勘误：「ch14 与 caiming 同名相反两诀并存」**不成立**，ch14 gaoji:19772-19815 与中级 2976-2978 皆只有发财义，「制不尽=破财」分键系引擎自造非书诀，§6.4「已收口」定性同步修正）/取财五法（经营/风险/智力/体力/工薪）。
- 基阶校准：校准一=有功 L1 基阶小康；校准二=财星当财+原神+主位财+经营法 基阶≥3 不落下富（两校准俱 `not ds_xiong` 门）。
- 上浮链收敛（层层设卡）：zhibujin 独力封顶富（净制豁免）；富格独力上浮封顶富+净制豁免；封顶 sticky `_liangji_cap`（开库不得翻越）；开财库+1 须财有原神；zbj 零财 guard；财源上浮 tier_idx<3（投资财至富，巨富须制级锚）；制库得财 opener 排自刑（辰辰伏吟非开库）；财统官 3→4 须原神 AND 主位财（净制腿已移除——净制证官杀干净不证财量级）；财众攻封顶富（本气财支被≥2 不同柱支冲/穿/破=寡不敌众，合/刑不论）。
- 过河拆桥判据六件：**F11 财生官位置相连（`_pos_connected`：同柱相互作用/支支五行流通不限柱位/干干须紧贴/异柱干支无直接生系——ans12 巳中庚支藏财不生异柱壬官=无生系，假富格撤销）**；主位财排未活化库财（余气仍计）；`_is_zhi_jin` 宾位透干随根论制（主位透干仍计残存——qi05 红线）；合制 from 端仅计中气藏干官（he_both_ends 开关仅 _is_zhi_jin 用，zhibujin 用旧口径）；主位制宾官门（制不尽时主位制宾官=官杀当财做功不论破财）；富格两守卫（丑戌未三刑全=刑坏非开库；日主被≥2 同五行透干争合坏富格）。
- 官统财/财统官在 views 时跳过过河拆桥（防假破财）；primary 序=官统财/财统官 → 过河拆桥 → 财星/禄/伤食当财；「伴过河拆桥破财信号」仅破财型挂。
- G9 自合柱：非日柱激活自合柱干为财且合神与日主同五行 → 财来就我不论绊+视同合财做功；财源上浮与 G9 同源一事不二升 `_g9_up`。
- 从财格顺势档：财成局/有原神转化→基阶不落下富；伏吟单一（同名财支≥3）无转化→从财亦贫；从儿无财门控=明财限干透/支本气（中气不算）。
- 富屋贫人 gating：身弱+财≥2+无印 → merchant 压制。
- 中气藏干**算**原神（裁定不收窄——庄家未中乙/ans37a 寅中丙/普例3 三书锚）。

### 4.7 官命 guanming

- 组合：制用四类（**F12 起四类皆双向**：伤食制官杀/官杀制伤食、劫刃制官杀/官杀制比劫、财制印/印制财、印制伤食/伤食制印）+印配比禄（比劫制印库，F12 新检）+生用化用+印化官杀+官禄格（**F12 改书口径=印生禄禄在主位**）+印带官帽/官带财帽；G0 aux 不计；G1 劫刃制财归财命域（例外：比劫孤≤1+官≥2）；G2 杀刃须相当（1v1 即相当）；G3 官弱（<2）为用神被制不为官（伤官去官格食伤≥3 豁免=朱元璋锚）；G4 象法单独不立官；~~G5 杀刃类须杀有制化~~（**F12 废除**：刃制杀本身就是制，庭长锚；孪生丁未造由反局否决承担）；从格豁免 G2/G3。**主位字门槛（F12）**：纯宾位互制不立官（印类豁免，见下）。
- ⚠️批6 补记（**F12 已修**）：官禄格定义口径书=印生禄禄在主位（zhongji:3969）——旧码「官星坐禄」与书相反已废，慈禧书例哨兵锁定；阎锡山 calib 盘（乙禄卯时+亥印）按新定义成立属口径内。李昌镐书内两造并存（lixiangxue:11202 vs 3576-3584），备案。
- **F12 主位字门槛（zhongji:3683-3684）**：制用 combo 纯宾位（年月互制）不立官命；藏杀被制须被制支居主位或制它动作另一端在主位。**印类 combo 豁免**（财制印/印制伤食/伤食制印）——书例 ans46 银行行长「未财制子印…沾岳父的光」（shouke:2112）即纯宾位财制印得官，规则三与该书例存书内张力，沿方向门先例不按主宾/主位。
- **F12 veto 链增补**：R1GUAN3（官杀透干+官杀/食伤互制 combo 在场，比劫制财=制去官之原神得权，比劫夺财不否决——布莱尔/处级锚）；N3GUAN（藏杀被制 combo 在场=统杀/制杀得权，官杀入墓不否决——希特勒/曾国藩/慈禧墓杀锚）。G5 废除后庭长造恢复，孪生丁未造由反局否决区分（身弱官杀有根/官带财帽非正向）。
- **F12 grade 收书**（理象学研究版：6103-6104＝理象学版：6022，修批C 标注，R3）：grade_map 4→总理-元首级/3→厅级-省部级/2→处级-厅级/1→科级-处级，与 gongliang._RANK_GRADE 同口径（F6 备案口径差收口）。
- G6 官被制空亡硬否（日/年旬并参），**官杀透干+杀刃相制/印化官杀做功者豁免**（乾隆/雍正/左宗棠/处级——支上官被制空干上犹存）；官有墓在局=被收非制死（曾国藩豁免）。
- G7 围制财源支涉 combo 降出（主富不主贵——李嘉诚/保尔森锚）；印制伤食仅 to_pos==day_zhi（日主坐下伤食被印制=护官）窄豁免（归档全豁免案误伤李嘉诚被 famous 核验抓回）。
- G9 官合身=得官（「合身肯定是官」）；食合官支型未覆盖（A19 残留）。
- 批29 九规则栈（全在官命域消费侧，检测器零动）：A1 G6 透干豁免/A2 R1GUAN2（从弱+官杀制比劫在场免夺财 veto）/A3 R2GUAN（印类 combo 在场免财坏印 veto）/A4 印类 combo 豁免 has_guansha（「四柱无官印主权力」）/A5 G7 窄豁免/A7 藏杀被制 append combo（慈禧/希特勒外延）/A9+A6+A10 合绊/岁运反局/财生杀 veto 官命域移除。
- **方向门禁令**：印类 combo（财制印/印制伤食）不按主宾方向（岳飞/蒋介石/周恩来等 10 锚否决）——切勿加「主制宾」过滤，代码现状是对的。
- 杀印相生须过滤 auxiliary（G0 洞）；藏杀被制=制杀得权入 combo。

### 4.8 职业 zhiye（批1-4 规则栈，全窄条件）

- merchant：真实做功信号（财入局/主位合制财/食伤生财+2、财印门户/官杀当财被制/冲财+1，上限**15**——⚠️批7 勘误：旧记「上限9」不实，批2-4 新增条款后律师例九 merchant=11 实证；且 merchant 桶系统性过宽，7.3 职业章 12 书例探针仅中 1，内食神格丢书「地支食神做功或生财」限定存在即+2、冲财与财入局双计）；时柱门户按**主气**粒度（食伤主气门户保留）；卯酉冲/破+财主气+1（酒家门户）；夺财动作不计经营；财反局 gating（fanju_caixing→merchant=0）。
- performer：桃花栈（食伤+桃花+财俱现+4/桃花居日柱+2 等）**一律不动**（刘晓庆/li154 靠其过阈——⚠️批7 勘误：「靠其过阈」是拟合事实非书证，刘晓庆书锚=食神泄秀木火 gaoji:1610 非桃花，桃花栈本身无书锚）；**F13 已重建**：桃花信号=咸池日支起（_tao_day）∨丙食伤透（zhenbao14「丙火主艺术演技」/gaoji:1610/shouke:6170 三锚）∨日主坐禄+禄做功+食伤透（chuji:5871/5877 吕丽萍/梦露），居日柱补沐浴修饰（gaoji:13311 不可一见便断→仅 has_tao 已立时）；无桃花通道=柱级食伤≥2+食伤做功+无桃花+无主气明财+3（乔布斯豁免闸）；金水声音+4（金日主+水食伤主气+食≥2柱+比劫≥3）；桃花让位-3（仅财入印墓宾位命中者）。
- military：官杀主气≥2+阳刃+刃支与官杀动作+未成势+财做功未触发+3（驾杀）；corro 每桶封顶+2；mingju_xiong gating；官杀为忌克身贫贱 gating（官杀主气≥3+身弱/从弱+tier 贫/小康 → 撤 military/lawyer）。**F15 落地 8.2 组合**（gaoji:11620-11964）：戌武库做功+3/火金相战+2/金水成势见火+2/申酉丑寅≥3字交织+2/丑戌刑·阳制阴+2（制类须阳为制方）/戌武库刑冲开官杀库+2，贵气门=官杀主气≥2柱且透干+组合封顶+6；④比劫库制印不落地（政委例十 vs 复例四双锚同构）；接入决策=不接 gongmen_wuzhi（F1 弃用，11 P0；**F18 正式弃用落地**：narrative 结论行通道切断、阳制阴口径按 gaoji:11787-11788 修正存档），本模块重写；军警书例探针 1/10→3/10（军官例二/纪检例九归位）。
- lawyer：伤官制官须主气克动作+2/柱级共存+1；食神制官条款删；mingju_xiong lawyer gating（伤官见官为忌=困顿非律师）。
- teacher：木火通明（天干甲乙见丙丁+2/仅地支+1）；印重馆阁+2（主气印≥2+食伤0+金<3）；印食文墨授业+4（月令主气印+印食共现+木火+财主气≥1+金<3+无卯酉冲，三型居一：纯文职/吐秀授业/印化文书）；食伤鬻文+3（食主气≥3+财主气≥2+无桃花+印0）；纯食伤文人+5（食≥3+印0+财0+金<3+非 mingju_xiong）；月令印主气化（藏干中气虚印不计）。
- accountant：金成势金融须金为日主之印（+收窄庚日金4=比劫者）；财入印墓于宾位+3（**墓支本气为印**，干携带不算）；日支财库+官杀透干+库合闭+2；食生财财入墓复合+2（**财墓坐日支排除**——财归己库非替人做帐）；水局成势+4（亥子辰≥2+**申子辰三合局**+财主气——半合版被 sim 否决）；从强金财+5（金财≥2 位+从强）。
- 方法论铁律：**纯收窄≈0✅**（❌→⚠️ 不提 acc），收益主要来自 fn 侧窄条件 boost；每条收窄先过同桶 ✅ 集 margin 检验（margin≤1 经不起任何降分）；粗 uniform boost collateral 大（换错桶），落地须逐桶窄条件+全量回归 sim。

### 4.9 墓库 muku

- 刑与冲皆可开库（「不冲不刑是墓」），透干引拔对刑同适用（无透干虽刑亦闭）。
- 戌特判细化：**戌已开（辰戌冲/刑开）则火支不入戌墓；未开则走通用入墓**（四生入墓/多而入墓——蒋介石巳午入戌墓书锚）。勿删特判（反转戌入辰多而入墓测试），勿一刀切（两书矛盾）。⚠️F2 补：土支（辰丑未）皆冲/刑戌，「多」要件成立时戌必开→**土支入戌实际不成立**（书亦无土支入戌明文，原则5 仅言入辰），特判维持 blanket 不窄化。
- 入墓=得到/控制/占有（做功语义）；开库=释放。changsheng 己墓戌 vs muku 己墓辰=中性层与盲派层未分离的已知分歧。**F2 已修三方不一致之 TOMB_MAP 缺「戌=土墓」**：理象学:2035「土墓在辰、戌」双位已入表（'戌':['火','土']），消费方 caiming/guanming/gongliang/laoyu/hunyin/juefa/zhengfan/zhiye/xiangfa_ops/dayun 全量回归过（F2 批）。
- **F2 已修 muku 三 P0**：①多而墓之计天干（理象学:3002-3005「天干地支合在一起…辛酉柱见丑即入丑墓」，is_entomb 增 all_gans 形参）；②四库之土直接入辰墓去「多」条件（:3008「丑入辰墓，未也入辰墓」无多前提+书例 :3080-3084 未入辰；旧注释「唯多方收」反托段氏已更正）；③TOMB_MAP 戌传导（见上）。哨兵=test_muku.py 8 测（先红后绿）。
- **F2 传导两守卫**：gongliang 库源加「自墓不为源」（z!=ys_elem——批3 P1-3 潜伏，戌成己墓后激活，例六 L2→L3 越书；zhenbao-05「另一辰」干癸≠支辰不受影响）+连墓加层改走 is_entomb 统一口径（裸 wx 匹配会把刑开之库误计入墓）；zuogong 化用校准「墓用双计去重」限主功级（非 auxiliary）墓用——aux 墓用=宾位入墓不做主功不抑制化用（化例二锚，复例一日支辰墓仍抑制）。

### 4.10 神煞 shensha / 象法 / 其他

- 神煞三层收口：核心5（禄/羊刃/墓库/驿马/空亡）+灾祸三煞（空亡/亡神/劫煞）+传统6 降级 traditional_shensha（5 vs 10 矛盾的最终答案，schools.py 开关待做）。亡神表与驿马**不同位**。⚠️批7/8 勘误补记：①代码侧脱节——zaihuo siwang 实消费亡神/劫煞/灾煞，shensha.py:10 四项称「三煞」与书（空亡/亡神/劫煞 gaoji:7907-7908）不符，**灾煞三书全文零命中无锚**（gaoji 灾祸章 14818-16567 无「灾煞」）；②起算口径颠倒——生产全链路默认 year（engine.py:70，0 处传 'day'），违 gaoji:7912「先以日支为主…年支亦需同查」，且劫煞/灾煞无 other_ref 双查（亡神/桃花/驿马有，供给侧不对称）；③羊刃消费两口径并存——zhi_all 全刃表（zhiye/juefa/yunfan/dayun）vs zhi 单值（zaihuo/gongmen_wuzhi×2/liuqin），戊日刃在未盘后者四处漏检；④戊刃书内两口径——理象学:2086「戊刃在午、未」vs 理象学:4977/zhongji:1520「戊刃在未或巳」，代码取前者未标注分歧。**F13 已修②③**：默认 reference 改 'day'（compute/resolve/engine/bazi_calc 全链路），亡神/劫煞/灾煞/桃花/驿马恒年日双查且 year_ref/day_ref 子键恒在不随 reference 翻转（配置断路修复）；劫煞/灾煞双查补齐（gaoji:7789）；zaihuo/gongmen_wuzhi×2/liuqin 四处羊刃改全刃表。桃花书口径重建（lu_ban=禄合财官杀伤食，zhongji:1517）+zhiye/hunyin day-ref 接线，岳飞 performer 8→1（见 CHANGELOG F13）。
- 驿马=段氏三支皆马：每支映射所属局对冲三支（申子辰马在寅午戌…），首位=传统单点向后兼容；⚠️批7/8 勘误：zaihuo 车祸 `ma_count≥1` 非「近恒真」是**恒真**（任意盘 count≥3，随机 2000 盘 min=3），且 count 语义=映射对冲支并集数非在局马数（应消费 in_pillars）——「死判据+语义错」，原「已知行为」备案低估；另书锚「以年支日支为主」与实现「四柱皆起取并集」相左未记。**F13 已修死判据**：zaihuo 车祸 ma_count 改消费 in_pillars 在局马数（供给层 count 保留并注释警示）。
- xiangfa_ops：换象（门槛=制尽，主从易位）/局象（包局/夹局/全阴全阳/专旺/寒暖燥湿，只做象意不加点——⚠️批3 勘误：与 zhiye.py:1282-1319 把换象/局象转职业候选数值权重存在边界争议，gongliang/caiming 不加点评核 ✓）/化象补五行相生/借象借同五行副宫；muxiang tomb_relations dict 须 `_zhi_of` 解包（曾致 analyze_xiangfa_ops 整体崩被 try 吞掉）。⚠️批3 补记：专旺≥6/8、寒暖燥湿≥5/8、局象纯≥6/8、伤官诀≥3 字均为无书定量的工程阈值（自定义）。
- juefa：伤官诀五类（金水喜见官/土金喜佩印怕见官/水木喜财官/木火喜见印/火土看组合）+断语22项；断语15/17/19 须传 yongshen_result 否则跳过（防过杀——⚠️批6 勘误：仅「None→skip」一半属实，19 提供后不读内容、17 以身强/从弱代理「财为用神」）。
- liunian：冲合九语义=**冲5**（冲动/冲开/冲去/冲破/冲旺）+**合4**（留/动/去/绊）——⚠️批4 勘误：旧文「冲九语义」措辞歧义，九=冲5+合4 非冲有九种；分看统看机械触发=流年与大运刑、冲、合、**并**——⚠️批4/5 勘误：旧条文漏「并」（伏吟）字，shouke:1368「刑冲合并则统看」，引擎 determine_dayun_phase（liunian.py:599-610）同漏（批4 P1-6）。
- yingqi_subj：大限∩大运∩流年三要素命中其二即 commit；`_classify_lu` 分日干/他干/外神（⚠️批4 勘误：旧文「任何见禄都算 trigger」与函数自述「外神不计触发」冲突——commit 路径却用含外神的 ln_lu_all，外神之禄算触发无书锚，且 `trigger` 字段全仓无消费=死字段）。**F10 已修**：engine 调 `infer_comprehensive_yingqi` 现传 `age=self._current_age()`（engine.py:608 一带，has_daxian 不再恒 False，三要素 commit 名副其实）；寿元星定位补印级（「无食看印印为根/食伤受伤无用则看印」gaoji:16148/16157，受伤=透干虚浮无根或坐绝；支/藏干食伤亦为寿 gaoji:4600/7651）；坏关系补「绝」（透干寿元星虚浮无根坐绝地=带病，gaoji:16172 案例一）与「正克」（限到位被坏语境，yx2:7486/gaoji:16547）；破从盲派书口径仅子卯/卯午互破（理象学:2934-2955，标准六破其余各对无段氏书锚移出 _HUAI_PAIRS）；寿元星藏干根被坏/被运岁冲散检出（gaoji:16206-16216 案例二印根辰）。高级寿元章两书例（gaoji:16164 案例一/16190 案例二）哨兵=test_yingqi_shouyuan.py TestGaojiShouyuanShuli（先红后绿）。`detect_shouyuan_jixie` 寿元机制推演（破禄/禄到位/寿元星被坏/原局字到位，risk=带病逢引动）——只推演验证，**不进 engine 消费链**（红线维持）。
- 宫位年龄=大限套（1-18/18-35/35-55/55+）已统一，GONG_WEI_XIANG 旧 1-15 套作废。
- body_parts=身体部位数据可信但**未接线**（⚠️批9 勘误：旧文「唯一事实源」名不副实——全模块零生产消费（engine/subjective 零引用），服役旧表=gongshen._PILLAR_BODY 颠倒备案表+zaihuo 自带四表；干主外/支主内；宫位身段主表年腿足/时头面 + ch11 变体分键本身与书逐项吻合）。
- narrative 叙事层：郝金阳 5 模板 few-shot 三段式，软依赖 anthropic，失败降级返 prompt 文本；数字生成后校验已建（N1，narrative.py:446——⚠️批10 勘误：旧备案「无生成后校验」已过时）。⚠️批10 真缺口=**寿元红线只堵一半**：detect_shouyuan_jixie 物理隔离 ✓，但 zaihuo 死亡档/寿元星 markers 经 selector+narrative 双通道直进 LLM 且 prompt 全文无死亡禁令（F14 修）；few-shot「引擎段实跑生成」名不副实（子女/岁运行系人工增补混合体），第14期把已证伪的咸池桃花→演艺伪因果固化成风格锚（prompts 受保护，备案升级为伪因果风格锚）；payload 裁剪意图被绕——selector 排除 gongshen/direction/jiaoyun_analysis，narrative digest 行间接带入 gongshen summary 与灾祸文本。

### 4.11 岁运 laoyu/jiaoyun/排盘（批5/批9 补条——原 KB 零条目）

- **laoyu（牢狱）**：书五法实现四法有伤（批5 重灾区，P0×4，全模块零测试）——①「反局+辰丑→牢狱」条款签名错配上线即死（laoyu.py:425，TypeError 被 try/except 吞 3 年）；②七杀夹克方向反（上海庄家双杀夹克书锚漏检=假阴）；③阳制阴减凶两分支同值（:498/:820 死代码）；④阴灭阳共现条款过宽（李嘉诚 risk=高 假阳）；唯一完好=水多金沉（无书锚量化）。
- **jiaoyun/起运（批9 升级 P0，F3 已修）**：交运年=出生年+起运岁把虚岁当实岁（书例 2005 生 3 虚岁起运，书口径 2007 引擎 2008，系统性晚一年）→ **已修为 year+age-1**（jiaoyun.py:269，理象学:3875-3877+书例:3916-3922）；起运岁三处叠加偏离书明文（理象学:3854-3856/3864-3877）→ **已修**：整日差/整数虚岁「余一舍余二进一」/「不足一天一岁」clamp min=1（bazi_calc.py compute_da_yun）；下游 liunian:701/jiaoyun:194 int() 截断随源头整数化无害化。哨兵=test_qiyun_jiaoyun.py 8 测。
- **晚子时（批9 新 P0，F3 已修）**：bazi_calc 两种 late_zi_method 均与理象学:3703-3716 书例不符（书=日柱本日+时柱推转一轮纳次日干）→ **已修**：时柱一律次日干起子时（same_day 旧算本日干=时柱错已纠正），日柱 same_day 本日/next_day 次日；`calc_bazi_full` 已暴露 late_zi_method 形参；凌晨早子时全对保持不变。
- **anhe 子巳（批1 P1→批9 升级 P0，F2 已修）**：暗合表「子巳」已删（初级:3218「只有三个」排他），五处+prompt 已同步：constants AN_HE/zuogong_detect:529/liunian:115/yunfan:101/zeishen:374（读表自动）/prompts/mangpai.md:16；哨兵=test_anhe.py 3 测。
- **hunyin/zaihuo/xueli/liuqin 四模块 KB 零规则条零书锚**（批7 覆盖缺口，非勘误但记录）；⚠️两 docstring 不可采信（批7）：liuqin「性别口诀统一口径」不属实（口诀 gaoji:14133 自带「阴阳日干要端详」）；xueli「枭夺食」口径误引 5397（书=财/伤官/比劫）。zaihuo._PO_DISEASE 伪引（批9）：注释「源文15468-15471」列 6 组破其中 4 组书外杜撰且漏书明文子卯破；_XING_DISEASE 行号笔误 15221→15521。
- **LLM 视图死亡 scrub 与 G6 代价备案**（修批A① + T3 payload 对拍实测，D5 落盘）：`_scrub_death`（subjective/__init__.py:122-218）在 build_payload 统一过滤死亡词典，引擎内部 siwang 保留（F14 不变）；T3 对拍 281 例键变更全=设计内 scrub 逐条可对账（shipaige 281/xiangfa_ops 117/liuqin 29/liunian 27/wood_type 15 例）；**guanming G6 否决理由「官被制空制死，不立官命」12/281 例被 scrub——官命维 LLM 缺该条论据，红线代价记录接受**。哨兵=test_a_llm_redline.py（scrub 泄漏串单测）。
- **as_of_year 可注入方案备案**（R5 遗留 now() 锚，T0 跨年对拍已证）：`datetime.now()` 锚四处=engine.py:122（_auto_liunian_list 当年±1 流年）/engine.py:138（_current_age 虚岁）/jiaoyun.py:332（next_jiaoyun 过滤）/narrative.py:423（N1 数字校验年龄白名单）；T0 mock now() 2026-06-15 vs 2027-06-15 对拍 509 例：**判定域（caiming tier/tier_static/yunsui_delta/summary）跨年零翻档**，漂移 100% 限「当下锚」岁运窗口域（payload 流年/应期/婚姻应期键跨年不同，设计内）。如需完全可复现交付：注入 as_of_year 形参（engine 构造透传至上述锚点）即收口——维护项，非阻塞。
- **子夜 ±1 分钟日柱敏感带备案**（T0 边界矩阵，D2 复核同结论）：均时差 −2s 级残差使真太阳时 BT 00:00 被压回前一日 23:59:58，same_day 口径下日柱与 00:01 差一天；子初/子正换日两派各自自洽，属历法固有边界，备案不修。

### 4.12 辅助层补条（批8/批9——原 KB 未记）

- **chuangong=伪标模块**：docstring 署「段氏理象学·置信度高」与项目自家 excerpts.md:244「❌ 非段氏体系」直接冲突，五书 grep 零命中；20 条绿测试锁自造 spec；spec 集成要求未执行=全字段零消费。任务书「十二神串宫压运」与本模块同名不同物（两者五书均无出处）。
- **advanced=死 shim**：弃用告警仅 zhengfan 单符号触发（6 eager 符号静默），全库零调用方。
- **virtual_solid 两原则偏离（批9，F4 已修）**：「虚实只就一柱干支而言」（理象学:5647-5649）曾被改成全局四支找根→**已收窄为本柱坐支**（本气/藏干算根）；「坐印都是实」（初级:2461，甲子列实表）曾被判虚透怕克→**已修：坐支本气为印=实**，例外燥土未戌脆金（庚戌/辛未书列虚表，:3120-3122）。is_solid 传导 zuogong_confirm「虚透被克损害加重」消费侧契约不变已核对。同型 **F4 已修**：wood_type 补「水不生木之根也是死木」甄别（理象学:12613-12615；机制=水支与木根支相破（盲派破子卯/卯午，:2934-2936）/冲/穿则不生）——岳飞造（:3187-3189）/戴妃造（:12615）均已从活木改死木。传导：岳飞 gongliang score 78→84（活木 fear_metal 打折撤销），level 仍 L3 书层不变，boundary 标注路径转为 score 近沿（test_gongliang 两测已同步）。残留 P1 未修：长生微调/他柱印扫描/「有气偏虚」中间态无书锚（批9 P1，留后续批）。
- **engine↔模块双轨死输出四例**（批9+批10）：soil/virtual/wood（engine 计算结果进 result+prompt，但 zuogong_confirm.py:864-962 自算不读 engine 结果——当前行为一致，参数演进后会分叉）+zihe（result['zihe'] 零消费不进 payload，guanming/yongshen/caiming 全部自调 detect_zihe）。
- **shenshu/shipaige 对照源仅郑民生公开碎片**（批8）：段氏五书 grep「一财是财/十排歌」零命中；shenshu 数量诀 70 句与碎片逐字吻合（干净）；shipaige 断语层 39 条碎片几乎零实现+两处冠名冲突（官杀为子/劫财抗杀），docstring「置信度：低」自承属实——**shipaige 断语层不可作书证**。**F18 已重写**：断语层逐条=碎片原文+行号（六域 28 条可机械检测者），三 P0（官杀为子/劫财抗杀/食神生旺）全修，未实现条目入 todos；「断语层不可作书证」标注维持。
- **gongfei 消费面**（批8）：classify_gongshen 输出经 zuogong_confirm.py:1051 三路扩散（L5 gate ratio / dayun 废神激活+verify_dayun 断言 / yunfan·liunian·gongliang 叙事）——auxiliary 语义错位（P0）有实质传导，非孤立模块。
- **任务书误称备案**（批8/9）：biqi=闭气非「比气」（五书零命中）；gongmen_wuzhi=公门武职非「宫门五物」（见 §0 同音陷阱）；chuangong≠十二神串宫。

### 4.13 子女 zinv（D6b 新模块，2026-08-19）

- **定位**：子息岁运应期+借腹 marker。星宫定位/有无/性别/优劣在 liuqin（F17 已立 zixi_youwu/xingbie/youlie 三节），zinv 只读其 child_star_cat 不重造星宫定位；分层=subjective，单向依赖 objective+subjective.liuqin。设计书 `docs/kimi-d6a-zinv-design-20260819.md`。
- **得子窗三机制**：合动（岁运合子息星，shouke:18-20 丁壬合）/开墓（子息星·妻星墓逢岁运冲开，shouke:18-20 辰冲戌+gaoji:14008-14009/14374 口诀）/制枭（枭夺食潜势盘岁运合制偏印，gaoji:14087-14107 庚辰运乙庚合）。
- **损子窗五机制**：克到位（运干克星到位且不合星，gaoji:14108-14128）/合去（克运中流年合走子息星，gaoji:14108-14128 戊合癸）/穿引动（岁运支穿子息星所临支；**修批 E4 裁定 a·改注**：直锚=gaoji:17465-17484「运逢己巳巳火到位穿寅木」逐字同构但书自承疑点降权；gaoji:14295-14312 实系「原局有穿+运岁引动穿害力」，其岁运己丑/辛巳不构成六穿不触发本实现——配对偏松备案；(b) 补书据否决，四书无第二独立锚，17783-17810 系同案例重出；(c) 改实现否决，书未给「引动」具体口径。行为不变）/枭夺食运（shouke:428）/合神被克（shouke:18-20 戊克壬）。**「冲」增补候选收档**（E4：孤锚 gaoji:14122 巳运冲亥次子亡；gaoji:21038-21052 案例五以冲引动凶象为主、形态非同构，未达双锚不立）。**措辞中性**（子息星受创/子女宫引动，字面无死/夭/丧），LLM 侧由既有 `_scrub_death` 兜底（zinv 不自建过滤）。
- **借腹 marker**：日支（妻宫）受穿+子息星/妻星入时墓（gaoji:14317-14334 案例十二+zhongji:1911-1914/4165-4170 两书同构）。
- **时柱喜用腿（R4，落 liuqin.detect_zixi_youlie 增补非 zinv）**：时柱为喜用→优/为忌神→劣（gaoji:14226-14240+5972-5973/6341-6342+理象学研究版:4283-4285 跨两书三处明文）；喜忌混杂不立腿防过火；用忌取扶抑总线 classify_strength/_yongshen_cats。
- **明确不做**：数量（E1-E4 书自证不准）/送终（G1-G3 孤口诀孤例）/性情（D7 孤条）；候选=R5 有无增补腿（动 M3 共振须重验哨兵）/R6 运定性别。
- 哨兵=test_d6b_zinv.py 12 测（先红后绿：F1 制枭/F2 一造三机制/F4 克到位+合去/H2+H3 双借腹/案例八反例 guard/schema+死亡词典红线）；engine 接线 `result['zinv']` 置于 liuqin 后；schools.py selectors 追加 'zinv'（38→39，镜像 liuqin 进特征 JSON 纯数据，LLM 五维不扩不进 prompt——schools/prompts 受保护特此备案）；基线=`snapshots/20260819_d6b.json`（blind vs d3 零翻转零抖动）。
- **已知残留（E4 候选）**：穿引动锚-实现错位（U1 P1-1，改注或补书据须设计裁定）；损子窗「冲」机制未收（F4 次子亡=巳亥冲，须双锚方可增补）。

### 4.14 迁移 qianyi（缺口批1 新模块，2026-08-20）

- **定位**：迁移/远行 marker+迁移应期窗（T2 缺口 9）。马星查法复用 objective/shensha._YI_MA（F13 年日双查+in_pillars）零重造；岁运扫描仿 zinv 消费 dayun/liunian 序列。设计=规划归档（`~/.claude/projects/-root-metaphysics/memory/kimi-gaps-plan-2026-08-20.md`）§一。
- **原局三 marker**：月日支冲=背井离乡（gaoji:5857）/日时支合=安居（gaoji:5858 同锚反向）/在局马临年时=多动倾向（gaoji:6735）。
- **应期窗**：马逢冲=离（shouke:3602「马冲在哪儿，离开哪儿」+gaoji:6757 口诀）/合到门户（岁运合且合端落时/年柱，zhongji:4179+lixiangxue:6571 双锚同构=立法门槛）/马星伏吟（shouke:6692，或然）/冲出年时（shouke:72，或然，书自承「未必所有人都会出门」）；马逢合=停留窗（zhongji:1567）。
- **红线**：措辞上限「迁移/远行/离乡」，全输出不出「出国/移民」硬断语（书无出国 vs 国内级别判据——zhongji:4179 与 gaoji:17390 结构同构而结论一为出国一为调动）；伏吟/冲出带「或然」置信标签（gaoji:15803 书自承马星更多动象更频，误报率天然偏高）。
- **收档不立**：出国级别判定/方位推断（仅 2 例无条文）/出行吉凶（依赖未形式化「用神旺地」）/六亲迁移（gaoji:17422-17433 单案例）/海外职业象（归 zhiye 域）。
- 哨兵=test_qianyi.py 11 测（先红后绿：书例 7 造+反例 guard 2+schema 红线+engine/payload 通道）；engine 接线 `result['qianyi']`（_safe_compute 同款）；schools.py selectors 追加（39→40，同 D6b 口径进特征 JSON 纯数据，LLM 五维不扩不进 prompt）；基线=`snapshots/20260820_gap1.json`（blind vs e3 零翻转零抖动，官 48✅/财 47✅/职 24✅ 保）。

### 4.15 相貌 xiangmao（缺口批2 新模块，2026-08-20）

- **定位**：纯 marker 层无判定无档位（T2 缺口 10；仿 foundation/ganqing 定位：ganqing 管性情、xiangmao 管外形），供 LLM 叙事层消费；**不进 heldout 闸门体系**（无金标可考），验证全靠书例哨兵。十神复用 liuqin._compute_shishen 零重造。设计=规划归档 §二。
- **4 主线**：秀气透干→漂亮倾向（zhongji:3914+反条件 lixiangxue:6655 不透干则相貌平平）/金水伤官限辛（zhongji:1484 庚金不算+shouke:5394+反条件 shouke:474 金多不秀/土埋不秀）/活木见火（zhongji:4513+chuji:4371+lixiangxue:6628，消费 wood_type 木死活）/眼象丙丁癸（zhongji:1482-1483+lixiangxue:11124「火土焦干癸水，双目无瞳」）。
- **2 弱线**：伤官合官杀→性感魅力（gaoji:5618-5623+shouke:634-638 阮玲玉 vs 美容师对照，须官杀在场否则仅技艺）/乙卯禄·己土→身材曲线（zhongji:3981+1484，单案例证据薄）。
- **红线**：全输出不出「美/丑/帅」结论词；gaoji:4035 慈禧造系反例不作秀气正锚（书自承个案可反）；三处条件从句（辛金限定/秀气须透干/伤官须见官杀）=作者自己当充分性倾向非定律。
- **收档不立**：贵相口诀（眼细而长=贵相，书未给干支触发条件）/难看反推（zhongji:5064 孤例机制不明）/五行盛衰形体表（lixiangxue:1353-1484，传统《滴天髓》系通论非盲派特色）/配偶相貌（过散，叙事层素材）/身高定量。
- 哨兵=test_xiangmao.py 7 测（先红后绿：梦露/刘晓庆/阮玲玉 vs 美容师对照+lixiangxue:6655 反例 guard+schema 红线+engine/payload 通道）；engine 接线 `result['xiangmao']`（wood_type 复用 result 已有键）；selectors 40→41（test_subjective/test_a_llm_redline/verify_dayun 计数断言同步）；基线=`snapshots/20260820_gap2.json`（blind vs gap1 零翻转零抖动）。

---

## 5. 书锚清单（按模块；修规则前必查双侧锚=真阳锚+假阳锚）

### 5.1 做功/贼捕/功量

| 锚 | 要点 |
|---|---|
| 李嘉诚（戊辰己未庚午丁亥） | 同制四点：亥从辰墓引出/午亥克合（午未生合不计）/主位做功优先/连墓加层（月令未入墓于辰）；净制巨富；G7 围制财源主富不主贵 |
| 保尔森 | 「财与财的原神同时被制」净制巨富 |
| 乾隆（辛卯丁酉庚午丙子） | 金字塔冲链 子→午→酉→卯 链长3冲边2+zb 净=L4；「冲为层层相制之骨」 |
| 克林顿（丙戌丙申乙丑戊寅） | 寅戌火翼包申=包制；包制内柱本气入制局目标集（原神同制→净） |
| 蒋介石 | 入墓+包局不净封三层；巳午入戌墓（戌未开时）=墓加一层功 |
| 岳飞 | 净（捕 6.25/贼 4.25 实测——⚠️批2 勘误：旧记 4.5/4.2 数字漂移，结论同）；无官杀之将（职业备案——批7/8 定性修正见 §6.1） |
| 奥纳西斯（b67 制例一） | 制库得财（丑未冲 opener）巨富；F6 起 gongliang L4 达标（制墓库+方局+不净豁免，书 6470-6474），不再单靠 caiming 兜底 |
| 森田健（b67） | 同制须戌克亥实制佐证（亥卯半合生扶不担责）；身弱+透财得根+有原神+非成势 cap **否决锚** |
| PUTONG2 | 酉丑相拱+子丑合=相生之功非同制；「日干无功弃之不看」 |
| 源文14例 | gongliang 14/14 达书层（PUTONG2/乾隆 xfail 已解锁） |

### 5.2 财命

| 锚 | 要点 |
|---|---|
| qi14（辛戊甲甲/巳戌寅戌） | 身弱+财3 但「通根于寅成火土气势」→异党单五行≥3 成势豁免身弱 cap |
| b67 森田健 | 与 qi14 双锚夹击：任何身弱财旺 cap 不可落地 → ans12 永久必损 |
| ans12-下岗财会 | ⚠️批6 勘误：根因=过河拆桥不验财生官相连，非必损；**F11 已按根因修复**（桥=壬月干、巳中庚支藏财不生异柱天干→假富格撤销），⚠️→✅ 翻转确认（富→小康，v6 运锚评 delta 轨） |
| li244 | 亿万富翁 verdict 出寿元章附述（零财局）→永久必损（松零财 guard 违反批15 锚） |
| 张克东/qi31 | 必损清单（财统官 3→4 要件收紧的代价） |
| li002/li200 | zbj 封顶富锚（不净）；与李嘉诚/保尔森 gl 逐点撞车靠净制豁免分流 |
| li001/li131/qi22 | 乙亥发财：裸锚匹配误杀锚（v6 差≥2 门槛保命） |
| zj-图书管理员 | 「为何不是大富贵…不能大富」净制腿移除书锚 |
| gj-合财小康 | 「财弱故不发大财」双子破酉=财众攻锚 |
| 《中级》己酉戊辰壬申癸卯 | 「零财之局官杀当财不成立…以伤官当财」=zbj/财统官零财 guard 锚 |
| ans29（30期） | 「水弱被制无原神所以会穷」=开库须原神锚 |
| 48期/例134 | 自合柱财来就我（癸巳合戊）；「子丑合，丑土不克水」R3 自合豁免 |
| 索罗斯 | 「制七杀申金制之干净」=宾透干随根论制锚 |
| 22期例4/5/6 | 从格根被坏四式（批6 复核无误，F11 补「晦」式）；⚠️批6 勘误：**例6 书判从官格（论从）非「破从」**——「未从」是例7，旧记与书相反；传导 yongshen.py 注释（锚干支「酉丑子申」误记）**F11 已修正**（例6/例7 双双归位，哨兵 test_f11）；「比肩再多也无用」（qi22） |
| li191 | 「巳顺从酉势」从化；li141「没有转化缺乏连贯性」从财伏吟贫 |
| yx 双胞胎（戊申壬戌戊午 乙卯/甲寅时） | 书判贫/富，引擎曾完全倒置（A1+A9 对照组）；「戊喜见甲为财富」 |

### 5.3 官命

| 锚 | 要点 |
|---|---|
| 岳飞/蒋介石/周恩来/曾国藩/例6副省级/银行行长×2 等10例 | 非主制宾印类 combo 立官——**方向门否决锚群** |
| 李昌镐 | G6 正锚：「食神制官…官星被制空亡故不入仕途」（年柱旬空）；技艺立命（⚠️批6：书内两造并存 lixiangxue:11202 vs 3576-3584，见 §4.7） |
| 曾国藩 | 「功在墓杀」；官有墓在局=被收非制死 |
| 慈禧/希特勒 | 藏杀被制（丑中辛/丑辰中癸）=制杀得权；「最大的功是丑入辰墓」 |
| 朱元璋 | G3 伤官去官格得官锚 |
| 单田芳（cj-演员） | 去官**不能**当官——与朱元璋书内矛盾备案，G3 不动 |
| 乾隆/雍正/左宗棠/cj-处级 | G6 透干豁免四帝王大官锚；「制去官与官的原神是当大官的」 |
| reg67-印制伤食市长 | 「四柱无官，印主权力，所以此造是个官员」=A4 锚 |
| cj-处级-5 | 「财星制印的格局，是当官的命…管财的官」 |
| cj-县长（戊戌壬戌辛亥甲午） | 印制伤护官（两戌制日支亥）=G7 窄豁免锚 |
| cj-厅级-2/yx-5101/yx-3290 | 从强财制印=掌兵权/管财的官（R2 财坏印扶抑口径误杀锚） |
| b67-克林顿/reg67-公安/cj-县长-2/cj-歌唱家 | 从弱比劫被官制不夺财（R1GUAN2 四锚） |
| 贪财坐牢例 | 从强一律非正向门槛锚（_has_positive_guanming 穿透保护） |
| zhenbao-23a | 身强比劫夺财真凶反锚（R1GUAN2 窄化「从弱」保护之） |
| cj-正处级化杀 | 「这种结构就是当官的。化杀得权」——支杀化印（A8 检测层残留） |
| cj-书记/cj-主席 | 贼捕制印得官/食合官支得官（A11/A19 检测层残留） |
| cj-2206 | 女命夫宫做功=夫荣非己官（A12 fp 窄修残留） |
| 书内矛盾备案 | 体制内管理=官（生例四董事长是 vs 老总/包工头否）；运中官来非原局（县长-3） |

### 5.4 职业

| 锚 | 要点 |
|---|---|
| yx-2658 | 「金有金融之意」（金5重 accountant 独力通道锚，acc 0 仍未达） |
| 《高级》案例七 | 「财库包局，银行工作」 |
| zj-注册会计师 | 「财入印墓…做帐的」=财入印墓宾位+食生财复合锚 |
| cj-老板 | 卯酉冲=酒家门户 merchant+1 锚（⚠️批7 勘误：代码注释引「《中级》象法卯酉为出入之门」系伪引文 txt 中不存在，真锚=lixiangxue:2647-2649/chuji:2221-2224；「用神被坏下岗」锚错标第50期，实 shouke:2236） |
| cj-歌星 | 金水声音（三辛+亥亥，身旺任泄）——⚠️批7 勘误：书声音锚=火克金主声音（zhongji:3543/lixiangxue:4837/13754），森进一机制=比肩生伤官+伤官合杀+杀虚透（3549-3553），条款机制与书文有偏差 |
| yx-记者 | 纯食伤文人（食≥3 印0 财0）「高级记者、编辑、著名报人」 |
| 梁羽生 | 食伤鬻文（食≥3 财≥2 无桃花印0） |
| yx-6061 | 翰林院学士=印重馆阁锚（贫而贵，tier 贫→laborer 硬绑定缺陷 C4） |
| gj-煤矿工人 | 「官杀重重克身…体力取财，贫贱」=官杀克身 gating 锚 |
| zgj-财反局苦力 | 「财反局财大凶…干苦力活」=财反局 merchant gating 锚 |
| gj-低保伤官 | 「土金伤官怕见官…格局破败…低保」=mingju_xiong lawyer gating 锚 |
| 段氏体育冠军 | 冠军=比劫做功（非军）；歌厅小姐/歌女=食伤桃花无工作贱命（非演艺） |
| yx-酒店丁未/董竹君庚申 | 食伤主气门户保留锚（merchant 门户收窄时勿伤） |
| 乔布斯 | 印食并见经营命（teacher 通道豁免闸）；无主气明财（performer 无桃花通道闸）（⚠️批7：baseline ❌→当前 ✅merchant，见 §6.4） |
| zhenbao-10/qi15/ans07 | accountant/lawyer 收窄时的 ✅ 挡路锚（申酉金让位须更细条件） |

### 5.5 岁运/墓库/从格/神煞

- yunfan 五书锚（test_yunfan 锁定——⚠️批4 勘误：案例五实际无 pytest 断言，「锁定」名不副实；A14 新增规则零 pytest 锁定是最大裸面）：案例一（忌神反客不可复现已移除断言）/案例三（卯合申、申入丑墓）/案例四（丑未冲开库+子合丑闭）/案例五（乙伏吟被辛克坏=坏辰墓，zj 数亿坐牢乙酉运）/案例八/九。
- 真阳锚：yx-巨富丑运丙子运入狱（破刃+伏吟激刑）；yx-破财工程酉运（冲卯，书明文工程被强拆）；yx-煤矿戌运刑开丑库发财十几亿（刑开库豁免）；b67 复例二丙子运杀临攻身破财。
- 发财运非反局锚群（11 例）：复例四庚申/资本运营酉/包工头壬卯/富发财戊申/经理-2丙戌/经理-4甲辰/富发财数千万壬辰/煤矿-2壬午/老师午/医师卯/煤矿戌——**F8 后 11/11 干净**：资本运营酉运（T3 伏吟干收窄加「主位墓透为功神」前提，理象学:7586-7594——修批C 更正行号，旧记 :7720 偏 126 行，R3）与 zj 丙戌运（T1 冲开墓库豁免，中级903/2853，群外锚）两假阳已修，哨兵=test_yunfan.py F8 五测。
- 驿马三支：`docs/duan-shi-lixiangxue-excerpts.md:149`（⚠️批7：同锚「以年支日支为主」与实现「四柱皆起取并集」相左，见 §4.10）。
- 阴阳同生同死沿用+火土同宫+弱长生（金长生巳=相克之长生）；盲派不站队阴阳干争议。
- 升官运被误杀锚（官命域已豁免）：县长-4 乙巳运/总理戊辰运/厅级戊戌运。

---

## 6. 备案清单（C 类结构性盲区 + 已知存量——**勿再立项重攻**）

### 6.1 职业残留 33❌（批4 收官收档；修批C 实测 27→33，R4）

- **中医 3 簇**（cj-中医/李阳波/yx-中医）：merchant 7-11 分差过大，火盖头金同柱相克模拟+4 仍不够；须 merchant fp 侧收窄=最大回归面（批1 警示 22✅ 中 merchant 占15，批7 复核成立）→收档。
- **军警备案簇**：岳飞（官杀0）/戴笠（无官杀特务）/警察墓库（墓用库制库未实现）/公安×2/刑警——⚠️批7/8 勘误定性修正：非「结构性无解」，gaoji 8.2 七组明文组合（火金相战/金水见火/申酉丑寅/丑戌刑/阳制阴/比劫库制印/戌武库）**已在 gongmen_wuzhi.py 实现**但有 11 条 P0 级偏差，真问题=**zhiye 不消费该模块**（engine 并行独立计算）+is_wuzhi 近恒真致输出无信息量——盲区=「已实现未接入且实现偏差大」；岁运反局 gate 撤后军警分亦不可及。另批7/8 补记：岳飞实际输出=performer「演艺/色情求财」8 分（比未分类更糟）——year-ref 桃花子落日柱驱动（切 day 仅 1 分），无书锚桃花栈所致，根因闭环。**F13 已修**：performer 8→1（test_f13 哨兵锁定），primary 落 merchant（军警盲区备案不动）。**F15**：zhiye 本模块落地 8.2 六组组合（贵气门=官杀主气≥2 柱且透干，不接 gongmen_wuzhi），军警书例探针 1/10→3/10（军官例二/纪检例九归位）；残留备案=例三/例五（凶向 gating）、例四（贵气门所挡，无官杀主气）、例六（lawyer 桶抢）、例七/例八（公检法/武职桶界张力，performer tie/羊刃合杀落 military）、例十（无官杀不过门）、yx-科级 trainset collateral（会计→军警，金水成势见火固有声纳）。
- **lawyer yx-2/3**：无官杀律师盲区+merchant 11-12 分差。
- **performer 阿炳/帕瓦罗蒂/导演**：财明现挡无桃花通道+桃花 veto 双锁。
- **accountant 残留**：cj-2075（银行主任官/商/会计三可，C6）/yx-14085；yx-2658 金5重需+6 不现实。
- **散簇**：马云/校长/组织部/图书管理员（金多无火盲区）/书法家/生例四企业家/yx-佛具/cj-种地/cj-农民（engine tier 巨富 vs 书农民=书分歧备案）/gj-低保伤官（mingju 宽撤被否：财党杀攻身 merchant✅ 会回归）。
- tie 序 Z9（tie_pri performer>military>merchant>accountant>doctor>teacher>lawyer）：22✅ 依赖未知，备案不动。

### 6.2 官命残留 19❌

- fp 窄修簇 A12 女命夫宫/A13 争合官无力/A14 合绊无功/A15 制不尽/A16 禄上坐官/A17 墓不开/A18 制财尽（各1例书明文强锚，窄修须保 cj-2097/yx-部长/朱元璋/公安锚）。
- 检测簇 A8 支杀化印/A11 贼捕入官/A19 食合官支（objective 层，须全量回归+化用虚高锚复验）。
- C 备案 8：zhenbao-01（与岳飞同构无法区分）/cj-演员单田芳（书内矛盾）/cj-平财不大/cj-1687/cj-包工头（管理≠官）/生例四（体制内口径）/县长-3（运引非原局）/戴笠（制财=军权与 G1 冲突）。
- collateral 备案：shouke-qi05（A7 藏杀入 combo 误触，书「不喜欢当官」软断语，铁律不反推）。
- **F12 collateral 备案 2 条**（heldout 官 ✅→❌，主位字门槛副作用，书机制均未建模）：li002-去印得权（书机制=「印弱为病，同样用财…去印得权」shouke:2216——印不现于局，「印弱为病去印得权」模式未建模，旧 ✅ 靠寅丑暗合官杀制比劫歪打正着）；li207-副市长秘书（书机制=「癸印化酉官…申杀占主的位置」shouke:6648=A8 支杀化印检测簇残留，旧 ✅ 靠 G1 例外劫刃制财歪打正着）。规则三（zhongji:3683）落地后两假结构现形，非规则错误。
- 缓行：A20 R1 身强侧豁免（真凶锚冲突）。

### 6.3 财命残留与必损

- **永久必损**：li244（寿元章附述零财）/张克东/qi31。⚠️批6 勘误：ans12-下岗财会**移出**——mismatch 属实但根因=过河拆桥不验财生官相连，按根因修复并非必损（双锚夹击+局部最优记录保留 §5.2 参考）；**F11 修复落地，⚠️→✅ 坐实移出**。
- **F11 collateral 备案 2 条**：li202-乞丐 ⚠️→❌（庚辰乙酉丁丑乙巳：巳根被丑晦+合会化金、根坏宽口径下酉丑半合金势实 3 判从弱→凶向词直杀；书断「身弱不胜财」与例6「印无根不救」存书内张力）；zj-工薪无官 官 ✅→❌（trainset，壬子丁未癸亥乙卯：子未穿+亥卯未化木根俱坏→从弱→G3 从格豁免→官命 True；书「制官只表示有工作」消费侧域级过滤留后续批）。
- C 备案：yx-破财那几年（事件断语无干支锚）/cj-种地（语录体半C）/zgj-财反局苦力边界（A15 力度）。cj-足球 原记「书无层级明文」D1 作废——书两处「收入很高」（chuji:5797-5805），v4-pro 裁 gold 小康→富，现 ⚠️（引擎巨富差1）。
- 弃修：ans32 vs zhenbao-14b 零和互拉；qi07 自刑开库（无排除书锚）；qi15 根治须 zuogong 层寅亥合绊优先级+caiming 财统官「财被合绊无统摄力」双改联动。
- 残留❌9（heldout）/10（trainset——D1 数据批 gold 修正后实测；修批C 记 11，旧记 8/22 系批4 收官口径，R4）主簇：A13 制库基阶/A4 伤官见官（土金伤官条款）/G5 破从残/A1 反局残/A12 体坏未入凶向链（独眼乞食）。

### 6.4 数据/工程备案

- **罗斯切尔德 zhiye**：⚠️批7 勘误——旧记「批11 merchant 召回存量换位、长期挂 famous REGRESSION 清单」**已自愈过期**：famous_baseline.json 该条即 ✅merchant，重跑仍 ✅（同分 6:6 靠 tie_pri，margin=0 仍脆）；乔布斯 baseline ❌→当前 ✅merchant。「常驻回归勿惊」提示失效，famous 侧无存量回归；calib 侧常驻 2 条（见下条，R4 复核+D1 更新）。
- **calib 常驻回归 2 条**（D1 起）：zhenbao-01 官命（批13-15 存量）/zhenbao-14a 财命，REGRESSION 清单常驻（修批B stash 实证=存量，R4 复核，勿惊勿立项）；原 zhenbao-05 官命/层功两条=gold 标注错（厅级反标 L4、层功 [3,4] 无书据），D1 按书修正（50qi:157/yanjiu:6103-6104）消化。
- **few-shot 交叉污染**：叙事模板第19期（qi19）/第25期（ans25）身在 heldout——prompts 受保护，备案不动。
- **gongshen 年时身段颠倒**：`gongshen._PILLAR_BODY` 年=头颈/时=腿足，与书主表（年腿足/时头面）颠倒——⚠️批8 勘误：书证实为 **≥6 处**非「三处」（理象学4163-4167+3993表、zhongji1669-1672+1716-1722、gaoji OCR5906-5907+15751+6066、chuji3995）。**永久备案结论维持，备案理由修正**（批8）：原理由「该字段仅流进 narrative 宫身行文本」**不实**——narrative 只取 summary（gongshen.py:287-293 不含 pillar_body），palaces/star_palace/spouse_palace/palace_interactions 全字段**零消费**；不回写的真实理由=零消费无收益（改它动核心判定链）。body_parts.PILLAR_BODY 主表已按书收录（但本身亦未接线，见 §4.10）。未来若做健康/身体维度再按 body_parts 口径修。
- 宫位年龄两套已统一大限套；神煞 5 vs 10 已三层收口——两大书内矛盾已收口。⚠️批6 勘误：过河拆桥「同名两诀已分键并存、已收口」**不成立**——ch14 与中级皆只有发财义，「制不尽=破财」是引擎自造分键非书诀（见 §4.6），勿再当缺口报但定性改为自造。
- 阎锡山 L3（书）vs L4（郝金阳）双标准冲突——**F6 已裁：以书（理象学 7188「三层强一点」）为准取 L3**，checkpoint/calib gold 同步改 3；guanming grade_map L3→中高（处级） 与 _RANK_GRADE L3→厅级-省部级口径差——**F12 已收口**（grade_map 全档收书 理象学研究版：6103-6104（＝理象学版：6022，修批C 标注，R3），与 _RANK_GRADE 同口径）。
- 双胞胎盘（yx 贫富姐妹）引擎与书完全倒置=A1+A9 调试对照组，备案。
- dropped 59 例不回收（无断语/六合彩/时辰存疑）；备查矿 80 条（仅婚姻/健康/应期等断语）未转录，pipeline 在 /tmp 易失。
- 书源码共模偏差：断语=段氏自评，trainset/heldout 同源同偏见（评估一致性↑真理性存疑），知情即可。

### 6.5 F19 扫尾决策簇（2026-08-17，P1/P2 全清账）

> 原则=书锚充分才修；每条记处理方式+理由。**修 2 / 备案标注 1 / 收档备案 15**。

**修（2 项，哨兵 test_f19_yunfan.py 先红 3 后绿 4）**

- **yunfan 大运侧合变冲参与字收窄**（批4 P1-3，F8 skip）：运冲须冲原局合做功参与字（与冲变合 A14 收窄对称，案例四子合丑同族机制）——包工头盘己酉运酉冲卯（卯与寅亥合局无关，chuji:3296）假阳消除；构造正例（运冲合参与字）锁定不回归。
- **yunfan 大运侧禄刃倒戈补挂**（批4 P1-4）：`_detect_lu_ren_fangg` 原仅流年侧挂接，大运段 0 命中——案例七锚（辛卯丙申辛未丁酉行丁卯运卯冲酉禄，「因罪被枪毙」gaoji:3761-3764）；同修 natal 在局守卫（禄/刃字不在局则冲无所冲，批4 P2-1 形参陪绑根治，流年侧同受益收窄）。

**备案标注（1 项）**

- **dayun 测试口径**（批5 测试缺口）：test_dayun_objective 11 测全自建盘锁 M2 自洽口径零书例——不硬补书例锚（冲开财库吉运 gaoji:17400-17414 等与 M2 四口径不同族），已在测试 docstring 标注备案；四口径上游书锚见 objective/dayun.py。

**收档备案（15 项，勿再立项重攻）**

- **laoyu 岁运维度**（批5 P1-3/4，F9 留本批）：书例机制（亥运杀合寅/丙辰合申穿卯/甲辰官合身收丑，中级:5610-5622/5850-5859）皆 **yunfan 域岁运反局**（冲变合/破坏功神已覆盖或属该域），非 laoyu 独立检测定式；「必须是官出现之年」（中级:5594-5596）为应期 gate 单条，不足立法岁运 API；接线将改 zaihuo max_risk 全局面，风险>收益。
- **laoyu 李嘉诚「中」残留**（批5 P1-2/P1-6，F9 留）：枭神夺食缺「克夺动作」书定量（5589 一句无细则）；魁罡/劫煞亡神两条 gaoji 定位不到明文（无 ch11 行号锚）——宽条款不动。
- **孙立人忌神出干克用**（批4 P1-5，F8 skip）：单例孤锚（gaoji:3502-3504），书述「癸水克戊土」实戊癸合绊、机制表述含混；立法=单例泛化（批4 P1-7 杀临攻身同诫），且须新引 yongshen 用神依赖。
- **穿变合规则**（批4 P1-1，F8 skip）：案例六/十一两书锚现经旁路命中（无失败锚），新增规则只有泛触风险无可验证目标。
- **T2 入墓「多而墓」条件**（批4 P1-2）：影响面=案例十一理由链文案纯净度；收紧恐失案例三/十一既有命中，判定不变文案级，不动。
- **案例二袁世凯庚辰运假阴**（批4 P1-6）：忌神反客移除代价，§4.4 已备案，确认永久漏检。
- **yingqi_subj 他干破禄不区分命主/六亲**（批4 P1-5）：书无区分定式，desc 标注级问题。
- **yingqi_subj 刃/墓/空亡机制族+运岁逢绝**（批4 P1-6，F10 留）：「合可坏刃」（gaoji:16548）入 _HUAI_PAIRS 将翻 cj1:697 状元反锚（F10 收窄破集的同型约束）；寿元红线域，只推演不消费现状维持。
- **liunian 统看缺「并」**（批4 P1-6/批5）：shouke:1368 条文与 test_liunian_k5 书例反例锚（丙午同气不自动统看，批次36/37 已裁定）张力，维持现状。
- **liunian 七杀冲禄不分年月/日时**（批5 liunian P1）：chuji:1401 分工明文 vs 现行「主凶死」双锚（cj2:5278 急病死/cj1:652 入院）——书内张力，两向皆锚，不动。
- **subjective/dayun 十神机械定吉凶等 P1 簇**（批5 dayun P1-3/4/5/6）：全书无机械口诀（真机制=对做功/正反局影响，yunfan 域已覆盖）；该层信号仅进文案，删改无书定式且动 prompt 面。
- **soil_type 6 条「书有码无」细化**（批9 P2：戌克亥分工/湿土不克水例外/晦火分工/燥土制金/帮土力差/克水偏强半档，理象学:3103-3126 皆锚真）：soil_type 输出大面积死字段（F1 标注 wet/dry 无消费），细化无判定传导，低收益封存。
- **biqi/he_types 闭气双实现收口**：工程去重，无行为锚，维持双实现（各自口径已合书）。
- **payload 补 direction/jiaoyun_analysis 键**（规划 F19③）：selector 排除系批10 A1 刻意防护，补键扩 LLM 面与 F14 寿元红线反向——维持排除。
- **残余 docstring/注释卫生**（各批 P2 未尽项）：无行为影响，不逐一修；新改动处注释已随批同步。

**既录残留维持收档（本批复核不再重攻）**：F17 xueli X2/X3-X7+liuqin L1/L3/L5（要件书无定量）/ F15 teacher·accountant fn 缺口（§7.10 纯收窄≈0✅）/ F15 C4 财统官不验身弱（书内张力 zhongji:2853 vs 3478，§7.15 被否决修法）/ F11 zj-工薪无官 G3 消费侧过滤（软断语，风险>收益）/ F4 virtual_solid 长生微调·他柱印扫描·有气偏虚（批9 P1 无书锚）/ F1 body_parts 接线（零消费）/ F18 shipaige 未实现碎片条目（已入 todos 封存）。

### 6.6 缺口批3 收档簇（2026-08-20，规划归档 §三/§四/§五——勿再立项重攻）

> 来源 = T2 五项缺口调研规划（`~/.claude/projects/-root-metaphysics/memory/kimi-gaps-plan-2026-08-20.md`）：迁移/相貌已立（§4.14/§4.15），以下三项收档，口径以归档为准。

- **世应引入八字（收档）**：本体仅授课第四十六期一节（shouke:2084-2114 定义+4 例）+宾主两处呼应+初级一句渊源，共 8 锚，**单一技法不成体系**；**作者自己弃用**——shouke:3630/5130 把世应并入宾主框架，后续四书再无用此术语。应用域（过继/弃养，gaoji 10.1 专节两口诀+5 案例）用的是宾主/伏吟/合化语言，引擎 liuqin.detect_parent_qiyang 已完整覆盖（自身被送养方向，F 批已立）。唯一增量=「要他人之子/女」反向（shouke:2090-2100、7370-7374 共 3 例），依赖作者临场换象（男命正法官杀为子，案例却用财/食伤当子），规则化必高误报；且 S4（年杀冲日禄断「被抢奸」）断语内容不可计算、OCR 残句边界不明。**不建模块**；增量 3 例仅以「子星衰绝+原神在宾位→子息或非亲生（低置信）」一句备案，不立码。
- **风水化解（弃用口径，防误立标注）**：真正「化解方法论」全书仅授课 2 处——纳音转运回避法（shouke:5844-5854，唯一成小节）+住宅五行化解单案例（shouke:1800，**作者自承「也不知是否有效果」**）；其余命中主体是否定性论述：**lixiangxue:8220-8278「从未见过行差运的人通过改好风水局逆转」**+lixiangxue:10633-10643「不信奉可以改变一切的说法」+**shouke:372 明言「八字缺什么补什么……都是错误的认识」**（直接抽掉五行补理据）。书的态度=**明确弃用为主、有限承认为辅**（限度内作用仅「不投资减损/指导方向」，即预测的应用非调理术）。**不建模块、不留候选**；纳音转运法标注「民俗法、字段缺输入（节气表/他人生肖）、非盲派核心」一并入档。
- **时空测事（收档·长期可选备案）**：全部家当=中级一书 3 案例花絮（zhongji:2166-2173 洗桑拿/2175-2189 官司/2794-2811 失物，合计约 30 行，无专节无标题体系），其余四书+残片零命中；起局需**新输入**「问事时间」（+求测人本命），方法句「问事以起八字时间为准」仅见闲注旁批；三例核心断语（桑拿/五百元/红色钱包）全是开放式干支取象+类数，无收敛规则，只能当 LLM 叙事素材。**不随本周期立项**；备案一句：若未来做问事入口产品形态，失物占（财库逢冲=失、伏神透合回主位=得）相对最可落成布尔+窗口，留长期可选。

### 6.7 第五轮审查发现摘要（V1-V6，2026-08-20~21，只审不改；待修排期=`docs/tasks/review5-fix-backlog.md`）

> 六报告：V1 新维度书锚终审 / V2 端到端真实路径 / V3 E7 终态 S1 复抽 / V4 性能+注入+合规 / V5 收官卫生+六件套复跑+go/no-go / V6 回归复审（锚回书/死数据/fuzz），均入 `docs/kimi-review5-v{1..6}-*-2026082*.md`。
> 发布判定（V5）= **NO-GO**：P0 免责声明 + P1×5 未清；F1（P0+P1 代码六项）+ F2（文档清零，08-21 已落地）并复跑六件套全绿后转 GO；P2 不阻塞。**N2b+N3 核销：F1+F3 代码 11 项随 f3d3e5e 并行落地+F2 落地+N3 六件套复跑全绿 → 转 GO（2026-08-21）**。

- **V1（qianyi/xiangmao 终审）**：27 锚回书全过、无自造 spec、P0=0。P1-1 xiangmao「丁=眼之象」marker 无锚注（书内明文 zhongji:2122-2147/gaoji:15337/lixiangxue:1777 存在，F1 补）；P2-1 zhongji:4179 行号偏 1（实 4180，F2 已清）；P2-2「结构同构」措辞失准（一合一冲机制不同构，措辞上限立论成立，F2 已清）。维度交付口径裁定：zinv/qianyi/xiangmao 保持特征层不进五维叙述（若进，前置=LLM 红线校验+S1 复测）。
- **V2（端到端）**：14 场景无阻塞静默失败（S9 断网双发/S10 非文本=基础设施/输入类型层）。P1-1 `zuogong_detect.py:997` Tuple 未导入（≤3.13 import 即 NameError，3.14 PEP 649 掩盖，V2/V3/V6 三源实锤，F1 一行修）；P1-2 lark_md 不支持 `- `/`> `/`---` 字面残留（F1 去三符）；P2-1 S7 裸 str(e) 回显 / P2-2 @bot `<at>` 前缀 / P2-3 compute 线程无上限。
- **V3（S1 复抽）**：裁决后真翻转 1/30 压线达标（zhenbao-23a 职业 unemployed 桶被叙述成「无倾向+宜安稳」，D4 zhenbao-09 同族，F-V3-1=迭代 5 锚定覆盖缺口，下轮 prompt 迭代补 `_zhiye_anchor`）；L2 高危零翻转、放大 10.1% 达标；judge 召回 1/2 未过→降级筛子（F-V3-2 judge prompt 未同步迭代 5「倾向性参考」许可）；v4-pro 成本较 D4 ~7× 涨（评审+judge $3.23 超 ¥6 预算；v4-flash 叙述侧未涨，V4 实测 ¥0.073/命）。
- **V4（性能/注入/合规）**：注入 6 向量零穿透（payload 死亡 scrub+prompt 红线+L2 黑名单三层防线守住、system prompt 零泄漏）；LLM 段均值 20.4s/P95 26.3s、¥0.0728/命谷段（千命 ≈¥73 谷/¥146 峰）、6 并发全成功。**P0-1 免责声明两路径全缺（发布阻塞，F1 修）**；P1-1 mark 模式死亡词命中仍展示仅附注（F1 升 reject）；P1-2 出生信息外发 DeepSeek 无告知（F1 HELP 告知）；P2-1 max_tokens=4096 可截断（F3→8192）/ P2-2 L2 死亡词 substring 误报合规拒答句（F3）/ P2-4 _self_check 美元口径旧（F3 人民币口径）。
- **V6（回归）**：死数据零复生（D3 合成层无双轨、41 键无死键、E5 五项全活路径）；fuzz 800 例零崩溃零慢零静默失败（D2 guard 34/34、E5 HTTP 面 17 项全兜住、qianyi/xiangmao marker 盘 7/7）；E3/E4 锚回书 6/6 全 A；快照链 d1→d2→d3→d6b→e3→gap1→gap2 七件连续 git_sha 链式吻合。P2-1 docstring 40→41（F2 已清）/ P2-3 bot 非 dict body 裸 TypeError（F3 isinstance guard）/ P2-4 client.send 生产零调用（备案不删）。
- **V5（收官）**：六件套全量复跑全绿（verify 432+70+64+20、pytest 794+1xf+19xp、blind vs gap2 heldout/trainset 双零翻转零抖动、双 seed 逐字节一致、calib 常驻 2 条零新增、快照链连续）；已知项全部原位无自愈无恶化。新漂移 D-V5-1=五轮结论未入档（F2 本批清）/ D-V5-2=清单漏项补录（S7 裸 str(e)、compute 线程上限）。
- **修批排期（V5 定）**：F1 发布闸（免责语三处/Tuple 一行/formatter 去三符/死亡词 mark→reject/外发告知/丁眼锚注）→ F2 文档清零（4179→4180/同构措辞/docstring 41/五轮入档，08-21 落地）→ 六件套复跑 → **GO**；F3 健壮性 P2（isinstance guard/S7 统一/max_tokens 8192/_self_check 人民币/L2 拒答误报窗）可并行不阻塞；备案不修=client.send/断网双发/非文本忽略/compute 线程上限/judge prompt 同步（下轮评审前）/@bot 前缀（真实群验证后）/unemployed 桶锚定（下轮 prompt 迭代+S1 复测）。

### 6.8 第六轮审查发现摘要（W1-W5，2026-08-21~22，只审不改；待修排期=`docs/tasks/review6-fix-backlog.md`）

> 五报告：W1 F1+F3 十一项代码审查 / W2 N 系列代码质量 / W3 新代码书锚复核 / W4 七维体验样张 / W5 跨层一致性+发布阻塞汇总收官，均入 `docs/kimi-review6-w{1..5}*-2026082*.md`。
> 发布判定（W5）= **七维正式发布 NO-GO**：P1 三项阻塞（F6-1/F6-2/复合词真漏网），G1 落地+六件套复跑全绿后转 GO；P2 不阻塞。第五轮清单（review5-fix-backlog）F1/F2/F3 全落地收官，本清单接替为统一待修清单。

- **W1（F1+F3 十一项）**：免责/Tuple/外发告知/丁眼锚注/isinstance/max_tokens/_self_check 人民币 7 项✅；lark_md 引擎直出干净但 LLM 路径两处漏网（F6-5 P2）；死亡词 mark→reject 行为正确但 reject 闸按 detail 子串「死亡红线」匹配（F6-3 P2）、降级三返回文本无免责行靠 service 前缀单点兜底（F6-4 P2）。**P1×2**：F6-1 reject/失败降级走引擎直出仅五段丢迁移/相貌+死词拒出场景提示语误写「暂不可用」（W5 裁定=提示语区分+明示简版即清，补两维后置）；F6-2 L2 误报窗句界符不含逗号/分号致「死断+拒答同逗号句」漏杀（合成例 6/10 实测）+死词表缺 离世/去世/归西/病逝（例 9）。18 合成例 15/18 符合预期，3 偏差全入 F6-2。
- **W2（N 系列代码）**：七维 schema 扩展干净（L0/L1/L2/format 全走 DIMENSIONS 循环，生产代码零五维漏改；唯一实质漏改=test_f1_gate 五维 mock P2）。迁移五禁词全有书内断语锚=安全收紧；相貌 ±1 相邻字排除窗设计正确（残留 美金/小丑/丑月 低频假阳族 P2）。**P1×2**：复合词真漏网——标致/水灵/清秀/端庄书内零锚该禁但不含美/丑/帅字，校验器+prompt 双侧抓不到（双轨补禁）；相貌引用率 251/267 实为统计口径 bug（独癸 16 例 gui=True 但 desc 空，锚定按无 marker 输出、LLM 漏引 0，对齐后 251/251=100%，修 `_n2_analyze.py`）。`_xm_sanitize` 当前安全但属静默语义改写，F-N2-1 落地后连函数删（P2）。F-V3-1 失业直述锚改动正确。
- **W3（书锚复核）**：锚定行 17 条回书 A 级 16+B 级 1（丙=「大眼」泛化无 inline 锚 P2）、C 级违书=0；模块键零幻影；校验器新规则回书全 A（「美丽」注释口径过强 P2，禁令本身合规）；基准锚抽验 5 条零漂移。P0=0 P1=0。
- **W4（体验样张 10 例）**：迁移/相貌维红线 10/10 保零、confidence 锁与或然标注全守、basis 零幻影（3 疑似键回验真实）；**F6-6（P2 新）** 弱线程度词放大族「曲线明显/表现力强」+引申气质句；存量确认=「数据不足」2/2 再犯、「大眼」透传。
- **W5（跨层+收官）**：10 例三层对照（脚本 `output/_w5_crosscheck.py`）——锚定行忠实 10/10、L1→L2 零断链，断链全在 L2→L3/L3 LLM 加料层；294 例全量离线坐实：评价词添加（有神采 32/明亮 31/灵动 20/灵秀 9）+程度词（明显 17）并入 F6-6 扩展族；**F6-7（P2 新）** 迁移维臆造建议断语「宜动不宜静」3 例（修后复扫仍现升 P1）；**F6-8（P2 新）** 秀气性别分流语未按本造落地 11 例；「数据不足」8 例再犯。结构观察不立项：应期窗 note/pillar/basis 不入锚（宫位语义 L1→L2 丢失=设计性收窄）。
- **修批排期（W5 定）**：G1 发布闸 P1×4（F6-1 提示语/F6-2 句界符+词表/复合词双轨/统计口径）→ 六件套+294 离线重扫 → **GO**；G2 样式批 P2×12 紧随（#5-#8 同一次 prompt 锚定增补，r5 复测一轮）；G3/备案=F-N2-1 引擎侧+删 _xm_sanitize、judge 判据（下轮评审前）。

---

1. **tuple 解包**：`analyze_zuogong` 签名=(day_gan, day_zhi, year_gan, year_zhi, month_gan, month_zhi, hour_gan, hour_zhi)；测试 tuple=(yg,mg,dg,tg,yz,mz,dz,tz) 4干后4支，勿交错。
2. **WX_KE vs WX_KE_ME**：我克=财、克我=官杀；juefa 财五行=WX_KE[day_wx]。搞反曾致「官杀『土』」凑数触发。
3. **day_gan 身份**：不算比劫 actor（R1）、不算贼神原神、日主自克非制（相生之功判据）；日支比劫仍计（配偶宫）。
4. **set 迭代序=确定性杀手**：11 处已排序化；li002 抖动根因=同制候选 sort 平局定 yuanshen_pos→下游库源/连墓触发分叉（打分不变纯文本）。
5. **凶向标注只写全量轨**：误入静态轨会把 qi02 等 ⚠️→❌（P0-a 假阳陷阱）；静态轨对破财/凶断语结构性失明，rubric 一律评全量轨。
6. **v6 差≥2 门槛**：层级断语运锚改判只在原局轨差≥2 时（本必❌，改判只改善不回退）；裸锚匹配误杀真✅。
7. **财命 label 卫生**：层级 label 勿带干支锚；事件断语（破财/凶）必须带锚+案例喂运。
8. **案例转录**：跨书同盘合并须 merge verdicts（初版丢过财政部长官命）；官命 verdict 防「老公当官」归属错；企业副总≠官员；性别不明弃（影响大运方向）；预测性职业断语剔。
9. **收窄先验 margin**：同桶 ✅ 集 margin≤1 者经不起任何降分；fp/真标两侧条款命中常同形（门户 25/26fp vs 14/15 真），clause 级收窄常零区分度。
10. **纯收窄≈0✅**：职业/财命修复必须 fn 侧 boost 为主+fp 收窄前置配合；粗 uniform boost 换错桶 collateral 大。
11. **模拟器失明面**：_zy/_gm dump 只含 gold 可评例，unscorable 换档须 blind_eval 全量 diff 兜底；sim 先做基线自洽校验（mismatch=[]）再信翻转数。
12. **绿≠无回归**：432 自洽检查与方向/veto 场景正交；principled judge cat4 曾绕 veto 失明（已改 engine 路径）。
13. **存量回归识别**：famous/calib 回归先 stash 实证——⚠️批7 勘误：罗斯切尔德已自愈移出（见 §6.4），calib 常驻 2 条（见 §6.4，D1 起 4→2）。
14. **Edit 工具**：长块 old_string 易因全角标点/em-dash/箭头失配，拆小改+ASCII 锚点。
15. **被否决修法勿重试**：方向门（10 书锚）/mingju 宽撤 merchant/桃花压平/桃花宽让位/GZ 主气收窄/SSK fallback 收窄/纯强度 MAX 聚合/不成 capL2/克链≥3 提阈/库源自墓排除/身弱财旺 cap/中气原神收窄/mingju_xiong 宽撤——全部有书锚或 sim 否决记录（见各批记忆）。**F15 增补三条**：①merchant 收窄（食伤生财主气化/冲财合财去重——误伤 heldout 既有✅ ans33/li131/li133，旧双计口径恰是过阈来源）；②lawyer 伤官合杀/食神制杀条款（与伤官制官同动作复计，误伤 li154/董竹君门户锚）；③C4 富屋贫人扩展 gating（身弱+财官主气≥4——与 7.2 案例一董事长同构不可分）。
16. **锚双侧卡**：每条新规则须真阳锚（保）+假阳锚（杀）双端验证；单端规则必翻船。
17. **heldout>trainset 不反常**：训练集更难（新矿）；acc 跨集不可比。
18. **gongshen/gongfei 同音**：勿「修正」命名一致性（见 §0）。
19. **戌特判方向**：选 tomb 非 tombed（verify 刻意编码戌入辰多而入墓）；细化=开则不入，勿删。
20. **解释层漂移可接受**：文本抖动（score 不变文案变）在意图内时放行，但须逐条审。

---

## 8. 工具链速查

| 工具 | 用途 |
|---|---|
| `mangpai/verify_mangpai.py` | 432 项自洽检查（唯一版） |
| `mangpai/verify_dayun.py` / `verify_layer1.py` / `verify_layer3_checkpoint.py` | 70 大运 / 64 基础 / 20 方向检查点 |
| `python3 -m pytest mangpai/tests/ -q` | 842 collected（822 passed+1 xfailed+19 xpassed，N2b+N3 实测；N1 记 821、缺口批2 记 794 passed、批1 记 787 passed、修批E6/E7 记 776 passed、E5 记 773 passed、E1 记 767、U4 记 762 passed、D5 记 747/727、修批B/C 记 682、F19 记 668/648、批10 记 499、旧记 473 均作废） |
| `mangpai/tests/heldout/blind_eval.py` | 三维盲测评估器：`--out 快照 --note 备注 --baseline 基线` 一条龙；`--diff A B` 对比；`--rescore` rubric 重评；输出含 M2 分组/M3 CI/显著性/文本抖动 |
| `mangpai/tests/heldout/diag_case.py` | 单盘诊断（原 _p2_diag 转正）：`python3 diag_case.py 乙己己庚 巳丑未午 [--gender 女 --dayun X --liunian Y]`，dump gongliang/caiming/guanming/zhiye 内部状态 |
| `mangpai/tests/heldout/_zy55_dump/_zy55_sim/_zy55_feat/_zy_all_dump/_zy_margin/_zy_master/_zy2_*/_zy3_*/_zy4_sim` | 职业批诊断考古（dump+条款网格模拟器，特征预计算模式可复用） |
| `_gm40_diag/_gm_all_dump/_gm_sim` | 官命批诊断考古（veto 翻转模拟） |
| `_a14_diag/_a1_*/_b5_diag` | 财命批诊断考古 |
| `mangpai/tests/backtest/regression67.py` / `regression_famous.py` | 67 书例回测 / 23 名人回测（famous_baseline.json 已 git add -f） |
| `mangpai/calib_zhenbao.py` + `tests/calib_assertions.*` | 郝金阳 10 例校准（zhenbao 系） |
| `mangpai/tests/heldout/{extract_cases,curate,build_yaml,verify_heldout}.py` | 案例管线（扩容批次复用模式；G3 提取 pipeline 在 /tmp 易失） |
| `mangpai/subjective/llm_channel.py`（+llm_prompt/llm_backend） | LLM 结构化推演通道（正式通道，交付文档 `docs/llm-channel-20260818.md`）：单命 `python3 -m mangpai.subjective.llm_channel [case_id]`；批跑 `output/_llm_batch_trainset.py` + `_llm_batch_analyze.py` 汇总 + `_llm_batch_rescore.py` 离线重评分（零 API）；**七维终态（N2b r4，294 例谷段）L0 0 / L1 1.36 / N1 1 例抖动 / L2 0.34**（财档 1 例告诫式 mark 留人工；迁移维红线 0 / 相貌维红线 0=加严线达成；E7 五维旧记 L2 0.34、D4 旧记 L2 4.98 作废）；计价按北京时间峰谷双档（峰 09-12/14-18，谷半价），批量评估排谷段 |
| 记忆目录 `~/.claude/projects/-root-metaphysics/memory/` | 62 份批次归档+10 份审计归档（本文件=其提炼；细节回查原件） |

**标准验证六件套**（每批落地前必跑）：
```bash
python3 mangpai/verify_mangpai.py                 # 432 全绿
python3 -m pytest mangpai/tests/ -q               # 842 collected（822 passed+1 xfailed+19 xpassed）
python3 mangpai/tests/heldout/blind_eval.py --out snapshots/<批>.json --note "<验证状态>" --baseline snapshots/<上一批>.json
PYTHONHASHSEED=0 python3 mangpai/tests/heldout/blind_eval.py --out /tmp/seed0.json  # 与默认 seed 逐字节一致
python3 mangpai/tests/backtest/regression67.py    # 0 回归
python3 mangpai/tests/backtest/regression_famous.py  # 0 回归（罗斯切尔德批7 已自愈；calib 侧常驻 2 条见 §6.4；两 baseline 修批C 已刷新，IMPROVE 悬挂清零）
```

---

## 9. 当前基线与残留总账（2026-08-22 **修批 G2 样式批落地 → G1/G2 收官·系统发布态**：F6-7/F6-8/模板语三令+统计口径清零+F6-3/4/5 结构性残留清零+注释/mock 归并，六件套全绿，基线推进=`snapshots/20260822_g2.json`；上线 checklist 6/8 闭环（真实凭证冒烟/群聊 @bot 后置）；收工 `docs/remaining-tasks-20260822.md`。前一态=**修批 G1 落地 → 七维正式发布 GO**：F6-1/F6-2/复合词真漏网三阻塞项全清+F6-6 顺手并入，六件套全绿，基线推进=`snapshots/20260822_g1.json`；统计口径项裁定后置 G2。前一态=第六轮审查 W1-W5 收官（只审不改零 API，引擎/生产代码零改动，基线=`snapshots/20260821_n3.json`）：六轮全量=P0×0、P1×4（F6-1 降级丢两维/F6-2 误报窗逗号漏杀+死词近义词缺口/复合词真漏网 标致水灵清秀端庄/统计口径——前三项阻塞、统计口径裁定可后置）、P2 若干（F6-3~F6-8 等，全不阻塞）；**七维正式发布 NO-GO**，修批 G1（发布闸四项，一次六件套验收）落地后转 GO；统一待修清单=`docs/tasks/review6-fix-backlog.md`（review5 清单 F1/F2/F3 全落地收官）；发现摘要见 §6.8。前一棒 2026-08-21 动工批 N2b+N3 · 相貌维小修续打+七维收档收官（用户选 a 续打，引擎零改动）：r3 残留「优美/柔美」复合词族以书锚为准**入禁**（书内相貌结论词仅 漂亮/美貌/秀气/好看/曲线好，复合评价词零锚；校验器单字「美」扫描已全覆盖码不动，llm_prompt SCHEMA 相貌条款+`_xiangmao_anchor` 禁令显式点名「曲线优美/体态柔美/秀美/俊美」同禁；哨兵 test_xiangmao_redline_n2b_compound 先红后绿）。r4 复测 294 例谷段：**相貌维红线 2→0 加严线达成、迁移维红线 0 保**；L0=0、L1=1.36%（4 例杂键旧族压 E7 线）、N1=1 例（reg67-合例六两妻「一次婚」计数=单例采样抖动，r1 同族）、L2 既有=1 例 0.34% 压线（gj-低保伤官「守成则平」告诫式疑似假阳族 mark 留人工，同 E7/N2 处置）；成本 ¥21.08 预算内。N3：blind vs gap2 heldout/trainset 零翻转零抖动（官 48✅/财 47✅/职 24✅ 保）+双 seed 一致+verify×4 全绿+67/famous 无变化+calib 常驻 2 条零新增+pytest 822+1xf+19xp，基线=`snapshots/20260821_n3.json`。**七维叙述终态指标：迁移维红线 0/294、相貌维红线 0/294、新维翻转 0/30（S1 裁决后）、既有五维 L0 0 / L1 1.36% / N1≈0 / L2 0.34% 全压 E7 线内**；发布 **GO**（F1+F2 落地+六件套复跑全绿）+七维 **GO**（新维加严线达成）→ 统一动工方案 F+N 全链收官。收档=CHANGELOG N1/N2/N2b 条目+收工 remaining-tasks-20260821+方案归档标完成；报告 docs/kimi-n2b-n3-final-report-20260821.md。前一棒 动工批 N2 · 七维复测（三轮收敛：L2 相貌 38→3→2，迁移维全绿 红线 0/翻转 0/锚定引用 264/264；S1 评审 30 例裁决后新维翻转 0/既有五维翻转 0/放大 6.3%；judge 一致率 91.2% 召回 0/2 降级筛子；F-V3-1 zhenbao-23a 失业直述修复确认；成本 ¥67.2≤$12；F-N2-1 引擎侧 xiangmao.py:111「漂亮」冻结留后续引擎批；报告 docs/kimi-n2-retest-report-20260821.md）。前一棒 动工批 N1 · 七维叙述代码批：DIMENSIONS 五→七（+迁移+相貌）+L2 两按维红线（迁移绝对禁出境词/相貌禁美丑结论词带美元/丑时/X丑排除窗）+`_qianyi_anchor`/`_xiangmao_anchor` 锚定行+哨兵先红后绿；F1+F3 代码 11 项随 f3d3e5e 并行落地（免责语/Tuple/lark_md/死亡词 mark→reject/外发告知/丁眼锚注/isinstance/max_tokens 8192 等）；294 例探针全通；pytest 821+1xf+19xp；引擎零触快照链不动。前一棒 2026-08-21 修批 F2 · 文档清零（纯注释+文档零行为）：第五轮审查 V1-V6 入档（§6.7 发现摘要+CHANGELOG+收工 go/no-go=NO-GO 待 F1+F2 落地转 GO）；锚注清零=qianyi zhongji:4179→4180（5 处+测试注/函数名）、「结构同构」措辞改准（一合一冲不同构、立论成立）、subjective/__init__ docstring 40→41；待修清单标认领（F1 #1-6/F3 #11-15）。pytest 复跑 794+1xf+19xp 无意外；引擎零改动，基线仍=`snapshots/20260820_gap2.json`。前一棒 2026-08-20 缺口批3 · 三项收档+KB/收工全量同步（纯文档零代码）：世应/风水化解/时空测事收档口径入 §6.6；KB 补同步批1/批2——§1.1 模块 29→31、§4.14 qianyi/§4.15 xiangmao 新条、selectors 41、pytest 794+1xf+19xp、快照链 e3→gap1→gap2；引擎零改动，基线仍=`snapshots/20260820_gap2.json`。前一棒 缺口批2 · xiangmao 相貌 marker 层：4 主线（秀气透干 zhongji:3914+lixiangxue:6655 反条件/金水伤官限辛 zhongji:1484+shouke:5394/活木见火 zhongji:4513+chuji:4371+lixiangxue:6628/眼象丙丁癸 zhongji:1482-1483）+2 弱线（伤官合官杀魅力 gaoji:5618-5623+shouke:634-638/身材曲线 zhongji:3981+1484），纯 marker 无判定，selectors 40→41，哨兵 test_xiangmao 7 测先红后绿，pytest 794+1xf+19xp，blind vs gap1 零翻转零抖动，基线=`snapshots/20260820_gap2.json`。前一棒 缺口批1 · qianyi 迁移/远行：原局三 marker（月日冲 gaoji:5857/日时合 gaoji:5858/马临年时 gaoji:6735）+应期窗（马逢冲 shouke:3602/合到门户 zhongji:4179+lixiangxue:6571 双锚/伏吟冲出或然），措辞上限「迁移/远行」不出「出国」，selectors 39→40，哨兵 test_qianyi 11 测先红后绿，pytest 787+1xf+19xp，blind vs e3 零翻转零抖动，基线=`snapshots/20260820_gap1.json`。前一棒 2026-08-19 修批 E7 · 迭代 7+文档同步：官命矛盾 4 例全误判（否定出窗）→官命维窗 ±2→±5；prompt 锚定补「可达/可至」；校验器⑦补「虽」让步窗+「档就是/档为」归位标记治 E7 新发 3 假阳；294 例谷段复测 L2 财档 2→1（0.34%，残留=单例真越限抖动 mark 留人工）、官命 4→0；pytest 776+1xf+19xp 全绿；引擎零改动，基线仍=`snapshots/20260819_e3.json`。前一棒 修批 E6 · 财档迭代 6：校验器口径修 6 条+prompt 锚定，L2 财档 16→2（0.68%），$2.98 谷段。前一棒 修批 E5 · 飞书加固（引擎零触）：重放窗口滚动/token 锁/静默错解三例/500 脱敏/HTTPServer 上限，test_feishu 28→34，pytest 773。前一棒 修批 E4 · 引擎裁定批：穿引动裁定 a·改注（纯注释零行为，口径备案见 §4.13）+损子「冲」收档（孤锚不立）；pytest 767+1xf+19xp 全绿，blind vs e3 零翻转零抖动，基线仍=`snapshots/20260819_e3.json`。前一棒 修批 E2 · 文档清零批：KB/CHANGELOG/收工文档按 U4 漂移清单清零，引擎零触。前一棒 修批 E1 · 飞书上线必修（纯 feishu 包内引擎零触）：client.py 捕获 token 99991663/99991661 清缓存重取重试一次（正常路径零影响）+bot.py reply 包 try 纯文本兜底重发一次+EncryptKey 检测告警丢弃+README 红线「勿配 Encrypt Key」+main() 启动 VT 强制（FEISHU_VERIFICATION_TOKEN 未配 RuntimeError+上线 checklist）；哨兵 test_feishu +5→28 全绿，mock 冒烟四条全过，U4 飞书条件 GO 三 P1 清零。前一棒 飞书集成工程批（bb4decf）：mangpai/feishu 新包 6 文件 528 行（client 带 TenantAccessToken 缓存/router/service/formatter/bot+README）+test_feishu 23 测，mock 全链三例跑通，U2 审查 P0=0（token 刷新/重放/降级三判据全过，fuzz 232 例零崩溃），引擎零触。前一棒 修批 D6b · 子女断法实现：zinv 新模块立 4 项（得子 3 机制/损子 5 机制/借腹 marker/时柱喜用腿落 liuqin，详见 §4.13），selectors 38→39（verify_dayun:405 断言同步），哨兵 test_d6b_zinv.py 12 测先红后绿，pytest 739+1xf+19xp，blind vs d3 零翻转零抖动，基线=`snapshots/20260819_d6b.json`；D6a=纯设计批零实现。前一棒 修批 D5 · 工具/备案批（收尾，引擎零改动）：`_llm_batch_rescore.py` sorted glob 合并确认 D4 已修+冒烟验证 retry 覆盖生效（原记录无 reading 被 retry 覆盖后重评分例数=1）；G6 scrub/as_of_year/子夜带三备案落 §4.11；pytest 727+1xf+19xp 全绿。前一棒 修批 D4 · prompt 迭代 5：职业桶/应期逐年锚定入 llm_prompt，引擎零改动；S1 复验翻转 9/30→0/30 三线全达标，飞书集成 GO，详见 docs/kimi-d4-prompt-iter5-20260819.md。pytest 727+1xf+19xp。前一棒 D3 供给批更新：dayun_analysis 死 selector 修复——选 B 补供，build_payload 层合成大运表（dayun_gz_sequence 方向+8 步干支序列 + analyze_dayun_mangpai 信号），engine compute_all 零改动；合成路径起运岁诚实缺省（缺精确出生时刻），每运投影 14 字段与 prompts/mangpai.md 引用对齐，D4 应期锚定直接可用；payload +约 7180 字符≈4500 token/命；顺手修 verify_dayun selectors 断言 39→38（70/70）。前一棒 D2 入口批：性别必填+界外年份 guard+lon 校验，引擎判定零改动；再前 D1 数据批 gold 修正 5 条+source 锚 15 处+raw_quote 1 处+calib zhenbao-10 dayun 误录删除）

- baseline=`snapshots/20260822_g1.json`（rubric v8-20260808，G1 发布闸批；G1=LLM/feishu 层改动引擎零触，g1 对 n3 heldout/trainset 零翻转零抖动、双 seed 逐字节一致；快照链 …→20260819_d1→d2→d3→d6b→e3→20260820_gap1→gap2→20260821_n3→20260822_g1，n3 对 gap2 heldout/trainset 零翻转零抖动、双 seed 逐字节一致；N1/N2/N2b 为 LLM 层（llm_channel/llm_prompt）改动引擎零触，D4/D5/E1/飞书引擎零改动无快照合理）。
- D2 备案：性别策略定（a）报错——calc_bazi_full 入口校验（合法集 男/女/male/female/乾/坤，is_male 补 '乾' 修同型静默），None/''/'未知'→ValueError；年份 <1900/>2100→ValueError（原裸 KeyError）；city_lon 非数值/越 [-180,180]→ValueError（原 None 裸 TypeError）。子夜 ±1min 敏感带复核=历法固有边界，维持备案不修。哨兵=test_entry_guards.py 33 测（先红 19 后绿）。blind_eval/llm_channel 合成 bazi_data 路径不过 calc_bazi_full，评估链零影响。pytest 实测 717 passed+1 xfailed+19 xpassed（§0/§8 旧记 682 系修批C 口径，LLM 打磨批后实为 704 collected）。
- trainset 294：官 83.48%（19❌=§6.2）/ 财 52.21%（❌10=§6.3）/ 职 47.06%（33❌=§6.1）。
- heldout 215：官 72.73% / 财 68.12% / 职 46.15%（D1 全量 diff 零翻转零抖动）。
- D1 备案：calib 常驻回归 4→2（zhenbao-05 官命 lv4→3、层功 [3,4]→[2,3] 按书修正 gold 消化，余 zhenbao-01 官命/zhenbao-14a 财命=引擎错存量）；trainset 财命翻转 2 条皆改善（cj-处级-5 ⚠️→✅、cj-足球 ❌→⚠️，gold 标注错修正）；D4 zhenbao-10 `dayun:[戊,寅]` 系误录——书（50qi:313-315）明「戊寅年寅刑巳动火而调动」，戊寅=1998 流年非大运，书中未给真实大运，采方案（b) 删 dayun 字段（脚本对缺省容错），删后各维不恶化（婚姻 ❌→⚠️ 改善）。
- 三维攻坚正式收官；后续方向（若重启）：官命 fp 窄修簇 A12-A18（各1例窄修）+检测簇 A8/A11/A19、财命 A13/A4/G5 残簇、职业中医/军警/lawyer 盲区（均须新突破面，旧窄通道已尽）。
- 汇报惯例：批次号+改动清单+翻转明细+六件套数字+300 字内。

---

## 10. 勘误记录（F0 批 · 2026-08-17 落盘）

> 来源 = 十批审计归档「知识库勘误」节+散见 KB 指摘（`~/.claude/projects/-root-metaphysics/memory/kimi-audit-{1..10}-*.md`）。
> 本批只改本文档，**引擎代码零改动**（yongshen.py:255 注释传导留 F11 修）。处置：修正=改正文，补条=新增条目，记录=仅本节备案。

### 10.1 审计「知识库勘误」节 46 条（批5-批10）

| # | 位置 | 旧值/旧记述 | 新值/处置 | 来源 |
|---|------|------------|----------|------|
| 1 | §4.10 liunian | 「机械触发=流年刑冲合运」漏字 | 修正：补「并」（伏吟），shouke:1368 | 批5勘误1（批4 P1-6 同源） |
| 2 | §4.11 | laoyu 全模块零条目 | 补条：五法四伤+签名错配+零测试全录 | 批5勘误2 |
| 3 | §4.3 | 「caiming 三处净制豁免」 | 修正：两处（caiming.py:1532/1545） | 批6勘误1 |
| 4 | §4.6/§6.4 | 过河拆桥「同名相反两诀并存、已收口」 | 修正：不成立——两书皆发财义，破财分键系引擎自造 | 批6勘误2 |
| 5 | §5.2/§6.3 ans12 | 「永久必损」 | 修正：移出必损清单，根因=过河拆桥不验财生官相连 | 批6勘误3 |
| 6 | §5.2 22期例6 | 「例6 破从（日主得根）」 | 修正：例6 书判**从官格**（论从），未从=例7；传导 yongshen.py 注释（锚干支误记）**F11 已修** | 批6勘误4 |
| 7 | §4.5 | 成势闸「主气≥3」如书口径 | 修正：标注自造（后验归纳，书无数值阈值） | 批6勘误5 |
| 8 | §4.7 | 官禄格口径/李昌镐两造未记 | 补条：书=印生禄 vs 代码=官星坐禄；两造备案 | 批6勘误6 |
| 9 | §4.10 juefa | 「断语15/17/19 须传 yongshen_result」 | 修正：仅 None→skip 半属实；19 不读内容、17 身强/从弱代理 | 批6勘误7 |
| 10 | §4.5 | 22期例4/5/6 三式+双套根口径 | 记录：独立复核**属实无误**，不改 | 批6勘误8 |
| 11 | §2.3/§6.4/§7.13/§8 | 罗斯切尔德「批11 存量、常驻回归勿惊」 | 修正：已自愈（baseline ✅merchant，margin=0 靠 tie_pri 仍脆）；乔布斯 ❌→✅ | 批7勘误1 |
| 12 | §1.2 | base_career 闸=tier_static | 修正：实为 tier 全量轨（zhiye.py:1074） | 批7勘误2 |
| 13 | §4.8 | merchant「上限9」 | 修正：实际 15（律师例九=11 实证）；桶过宽补记 | 批7勘误3 |
| 14 | §5.4 cj-歌星 | 金水声音未记机制偏差 | 补条：书=火克金主声音；森进一机制三件套 | 批7勘误4 |
| 15 | §6.1 | 军警「结构性盲区」 | 修正：书明文组合未实现（批8 再更正为「已实现未接入且偏差大」）；岳飞输出 performer 8 分补记 | 批7勘误5 |
| 16 | §4.8 performer | 「刘晓庆靠桃花栈过阈」 | 修正：拟合事实非书证；刘晓庆书锚=食神泄秀木火 | 批7勘误6 |
| 17 | §4.10 驿马 | ma_count「近恒真（已知行为）」 | 修正：**恒真**（2000 盘 min=3）+count 语义错（应消费 in_pillars） | 批7勘误7 |
| 18 | §4.10 神煞 | 「灾祸三煞」未记代码脱节 | 补条：siwang 实消费亡神/劫煞/灾煞；四项称三煞 | 批7勘误8 |
| 19 | §5.5 驿马 | 未记口径相左 | 补条：书「年日支为主」vs 实现「四柱并集」 | 批7勘误9 |
| 20 | §4.11 | hunyin/zaihuo/xueli/liuqin 零条目 | 补条：覆盖缺口记录+liuqin/xueli 两 docstring 不可采信 | 批7勘误10 |
| 21 | §5.4 cj-老板 | 卯酉门户引文未核 | 补条：伪引文（《中级》txt 不存在），真锚 lixiangxue:2647/chuji:2221；下岗锚错标 50 期实 shouke:2236 | 批7勘误11 |
| 22 | §6.4 gongshen | 备案理由「仅流进 narrative 宫身行文本」 | 修正：理由不实→**零消费**；书证≥6 处非三处；备案结论维持 | 批8勘误1 |
| 23 | §6.1 | 军警定性（批7勘误5 续） | 修正：8.2 条款已在 gongmen_wuzhi 实现（11 条 P0 偏差），真问题=zhiye 不消费+is_wuzhi 近恒真 | 批8勘误2 |
| 24 | §0 | 同音陷阱仅两条 | 补条：gongmen_wuzhi=公门武职（非「宫门五物」） | 批8勘误3 |
| 25 | §4.10 神煞 | 未记起算口径颠倒 | 补条：默认 year 违「日支为主」；劫煞/灾煞无双查；马星恒真实锤 | 批8勘误4 |
| 26 | §4.10 | 未记羊刃消费两口径 | 补条：zhi_all vs zhi 单值，戊刃在未盘四处漏检 | 批8勘误5 |
| 27 | §4.10 神煞 | 三层收口未记灾煞无锚 | 补条：灾煞三书零命中，入灾祸层无据 | 批8勘误6 |
| 28 | §4.12 | shenshu/shipaige 对照源未记 | 补条：仅郑民生碎片；shipaige 断语层不可作书证 | 批8勘误7 |
| 29 | §4.10 | 未记戊刃书内两口径 | 补条：2086「午、未」vs 4977「未或巳」，代码取前者 | 批8勘误8 |
| 30 | §4.12 | gongfei 消费面未记 | 补条：三路扩散，auxiliary 错位有实质传导 | 批8勘误9 |
| 31 | §4.11 | 晚子时口径未记 | 补条：两模式均不符书例（理象学:3703-3716），新 P0 | 批9勘误1 |
| 32 | §4.11 | 起运岁仅 P1 疑点 | 修正：升级 P0——三处叠加偏离+「不足一天一岁」未实现 | 批9勘误2 |
| 33 | §4.11 | anhe 子巳仅批1 P1 | 修正：升级 P0（初级:3218），传播五处须同步 | 批9勘误3 |
| 34 | §4.10 body_parts | 「身体部位唯一事实源」 | 修正：名不副实——数据可信未接线，服役旧表=gongshen 颠倒表+zaihuo 四表 | 批9勘误4 |
| 35 | §4.11 | zaihuo 破病表未核 | 补条：_PO_DISEASE 伪引（4 组杜撰漏子卯破）+行号笔误 | 批9勘误5 |
| 36 | §4.12 | chuangong 全貌未记 | 补条：伪标「段氏冠名」实非段氏；测试锁自造 spec；零消费 | 批9勘误6 |
| 37 | §4.12 | 任务书误称未记 | 补条：biqi=闭气非「比气」；chuangong≠十二神串宫 | 批9勘误7 |
| 38 | §4.12 | engine↔zuogong 双轨未记 | 补条：soil/virtual/wood 双轨，参数演进后会分叉 | 批9勘误8 |
| 39 | §4.12 | advanced shim 现状未记 | 补条：告警仅单符号触发，全库零调用=死模块 | 批9勘误9 |
| 40 | §4.12 | virtual_solid 原则偏离未记 | 补条：全局找根/坐印判虚两条与书相反 | 批9勘误10 |
| 41 | §0/§8 | pytest 473 | 修正：499（批10 collect 实测；F0 复核 499 collected） | 批10勘误1 |
| 42 | （外部归档） | selectors「35 键」 | 记录：实际 39 键；compute_all 输出 49 键（KB 未载旧值，备查）。**修批A③（2026-08-18）起 38 键——gongmen_wuzhi 摘除（is_wuzhi 98.8% 恒真零信息量，payload 通道切断），engine result 键保留**；**D6b（2026-08-19）起 39 键——zinv 追加（镜像 liuqin 通道进特征 JSON 纯数据），verify_dayun:405 断言=39 实测过**；**缺口批1/批2（2026-08-20）起 41 键——qianyi/xiangmao 追加（同口径进特征 JSON 纯数据，LLM 五维不扩），test_subjective/test_a_llm_redline/verify_dayun 计数断言同步** | 批10勘误2 |
| 43 | §4.10 narrative | 「无生成后校验（幻觉风险备案）」 | 修正：N1 校验已建（narrative.py:446）；真缺口=zaihuo 死亡档/寿元星直进 LLM 无禁令（F14） | 批10勘误3 |
| 44 | §4.12 | zihe 死输出未记 | 补条：双轨第四例（三家自调 detect_zihe） | 批10勘误4 |
| 45 | （外部文档） | SOUL.md 验证数字 409/69/27、「objective 25 模块」 | 记录：全面过期——现行 432/70/499、detect/confirm 拆分结构；SOUL.md 本体不在本仓，待其维护方更新 | 批10勘误5 |
| 46 | §4.10 narrative | few-shot「实跑生成」未记/ payload 裁剪被绕未记 | 补条：人工增补混合体+伪因果风格锚备案升级；selector 排除项经 digest 行间接带入 | 批10勘误6/7 |

### 10.2 批1-4 散见 KB 指摘 8 条（无独立勘误节，F0 一并落盘）

| # | 位置 | 旧值/旧记述 | 新值/处置 | 来源 |
|---|------|------------|----------|------|
| 47 | §5.1 岳飞 | 「捕4.5/贼4.2（4.5/4.4）」 | 修正：实测捕 6.25/贼 4.25，结论同 | 批2 P2-13 |
| 48 | §4.3 | 「party≥4 成势」 | 修正：_CHENG_DANG=4.25，以码为准 | 批2 P2-3 |
| 49 | §4.9 | 己墓分歧备案仅两方 | 补条：TOMB_MAP 缺戌=土墓，三方不一致（F2 修） | 批1 P1-1 |
| 50 | §4.10 xiangfa_ops | 「只做象意不加点」 | 补条：与 zhiye:1282-1319 边界争议+四组工程阈值自定义 | 批3 P1-8/P2-10 |
| 51 | §4.10 liunian | 「冲九语义」 | 修正：冲合九语义=冲5+合4（措辞歧义） | 批4 前提纠正3/P2-2 |
| 52 | §5.5 | 「五书锚 test_yunfan 锁定」 | 修正：案例五无 pytest 断言，名不副实 | 批4 P1-10 |
| 53 | §5.5 | 发财锚群「9 干净残留 2=破从」 | 修正：现状 10/11——资本运营酉+zj 丙戌两假阳（A14 零测试面） | 批4 yunfan P0-1/2 |
| 54 | §4.10 yingqi_subj | 「任何见禄都算 trigger」 | 修正：与函数自述冲突+trigger 死字段+engine 不传 age | 批4 yingqi_subj P1-4 |
