# 盲派客观层 变更记录

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
