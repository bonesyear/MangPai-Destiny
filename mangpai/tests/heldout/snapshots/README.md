# 快照链（heldout blind_eval 基线档案）

> M5 快照机制：每批引擎/规则改动后跑 `blind_eval.py --out snapshots/<批>.json --baseline <上一批>`，
> 快照带 `_meta`（git_sha / rubric_version / note）。**零翻转零抖动**是每批门禁。
> 本文件是快照链的总账：哪个是当前基线、哪些是历史、各批对应的 commit。

## 当前基线指针

- **`LATEST`**（纯文本单行）= 当前基线快照文件名，现指向 **`20261027_r5.json`**。
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
| `20260918_p4.json` | P4 职业军警新面批·P 系列收官（objective muku 新检测 `detect_ku_zhi_ku` 库制库·阳制阴，纯增量既有函数零改动；zhiye military 消费条款+6：阳库收/刑阴库+阴库成双多见，贵气门外格局级通道） | 见 _meta | p3 | heldout 三维零翻转零抖动；trainset 职 +1（40→41✅，gj-警察墓库）全预注册、官/财零翻转；军警探针 3/10→4/10（军官例四归位）；文本抖动 0 |
| `20260918_t1.json` | T-教授 财命窄条款微批（caiming 消费侧单点：日支穿月令财→封顶小康，月令本气口径，chuji:2379/3678、zhongji:2322 双锚；objective/总线零改动） | 见 _meta | p4 | heldout 三维零翻转零抖动（官 48✅/财 47✅/职 24✅ 保）；trainset 财 +2（61→63✅：cj-教授 ❌→✅、zj-邢铭芬 ⚠️→✅、yx-贫穷命贫困线上 ❌→⚠️）全预注册、官 102✅/职 41✅ 零翻转；文本抖动 1 条（yx-书法家-2 caiming_adjust，条款文本设计内）；马云/李嘉诚/保尔森/奥纳西斯/煤矿锚全保 |
| `20260918_r1fix.json` | 审查修复批·P2（主会话代码审查发现的 P2 项：output 8 处 cwd 相对路径锚定 + KB book-index 路径与 pytest 计数校准 + privacy-policy 路径前缀 + output/README 白名单精确化；代码本体审查 P0=0） | 见 _meta | t1 | heldout/trainset 零翻转零抖动（官 48✅/财 47✅/职 24✅ 保）；引擎判定零改动（仅 LLM 通道/工具脚本/文档） |
| `20261025_t1.json` | 财命专批（收官）：zhenbao-14a 通关豁免——书机制「未戌刑开库·辛官出库·丙辛暗合」（mingli-zhenbao-50qi.txt:485-486/494-496）四腿判据（财支为财墓/库藏官杀/刑冲开库/藏官与本柱天干五合且为日主食伤）作 R2 财坏印 severe 的化解判据（yongshen.detect_cangguan_tongguan，R2 检出本身不变）；caiming 封顶链仅「唯一凶向=R2 财坏印」且有通关时豁免（反局/破财/原局三式/R3 在档照旧）。**calib REGRESSION 1→0 清零**；反锚 519 盘扫面全保（地矿局长/财党杀攻身/岳飞等） | 见 _meta | 20261025_s3 | heldout 零翻转零抖动；trainset 1 改善（14a 小康→富 ❌→✅，财 55.8%→56.6%）+1 抖动（gj-刘晓庆同构非计分）；pytest 1450+1xf |
| `20261026_r0.json` | R0 验证地基：CLI 编码/失败传播/名人基线；引擎零改动；仅作对照锚，**不推进 LATEST** | 见 _meta | 20261025_t1 | heldout/trainset 零翻转零抖动；509 例对拍仅用于验证后续变化 |
| `20261026_r1.json` | R1 公开输入与时间轴：性别归一/真太阳时/晚子时/节气边界/虚岁与交运/大运分看/综合应期 | 见 _meta | 20261025_t1 | heldout/trainset 零翻转零抖动；时间轴公开入口新增独立哨兵，calib 无新增回归 |
| `20261026_r4.json` | R4 关系语义纠偏：段氏破/核心刑/只合不化/拱局/入墓优先与直接消费方；zhenbao-01 主功为食伤生财时次要财制印不独立立官 | 见 _meta | 20261026_r1 | 对 R1 共 9 翻转、35 文本差异全归因；新基线自比对零翻转零抖动；pytest 1490+1xf；calib 零回归；双 seed 一致 |
| `20261027_r5.json` | R5 方向、宾主与做功资格：定向/主位/泄用及直接消费方；R7 用忌分域、R8 功量权重与专项仍未决；**当前基线** | 见 _meta | 20261026_r4 | 对 R4 共 56 翻转、138 文本差异逐例归因；新基线自比对零翻转零抖动；pytest 1510+8xf；calib 32✅/10⚠️/4❌、无回归；双 seed 一致。不拿严格 xfail 或未决回归冒充已修书例 |
| `20261025_s3.json` | 官命专批（批S2 修法草图执行）：zhenbao-01 官命假阳修复——四条独立路径收窄：①藏杀被制须≥2 不同来方非辅助制或单方来方五行成势（yanjiu:7792-7796 匪制成势锚；岳飞/蒋介石/慈禧/黄兴等 19 锚盘全保、combo 逐字节不变）②印制伤食与伤食制印「互战护官」排除（被制支藏官杀+反向互战；岳飞/周恩来零伤）④财制印「宾制主+财支藏官杀」排除（50qi:16；首版误伤 yx-3290 哨兵抓获收窄）。calib REGRESSION 2→1（余 14a 备案）；trainset 官 88.7%→89.6%（zhenbao-01 ❌→✅ 归位） | 见 _meta | 20261024_r1 | heldout 零翻转零打分变化；trainset 1 改善+heldout 4 条未计分翻转的下游字段抖动全归因；pytest 1443+1xf |
| `20261024_r1.json` | 批R LLM 加固二期（引擎判定零改动）：L0 拒 schema 七维外维度（堵 L2 盲区）、user_question 「」包裹+隔离声明（注入隔离）、应期/婚姻回对否定语境排除（复用批F _neg_in_pre，「婚姻不美满」类不误拦）、词表扩（迁移补赴外/南洋/赴美；死词补「大限将至/已到」组合形态，大限术语放行）；juefa B 组复评维持不接（判定集 n<10 不达批L 接入线，纪律性拒绝） | 见 _meta | 20261020_l1 | 零翻转零抖动（校验器/prompt 不触引擎）；pytest 1428+1xf（+4 哨兵） |
| `20261020_l1.json` | 批Q 长尾人生事项（Q1 hunyin/liuqin/zinv 十项+Q2 zaihuo/xueli/qianyi/xiangmao 十一项，明细见台账批Q 节；全 marker 级措辞不进凶链）：含 xueli 中断机制按书替换（财坏印→伤官太旺无印 zhongji:5557-5558+例14 合杀豁免，21 例探针 9→15/21）、伤官特殊应期锚实测 gaoji:13238-13258、过房/过继两域分工（zinv 子女过继 vs liuqin 命主被弃养） | 见 _meta | 20261020_k1 | 三维零翻转零抖动；calib 无新增回归（余 zhenbao-01/14a 存量备案）；pytest 1424+1xf（+39 哨兵） |
| `20261020_k1.json` | 批S2 14b 溯源：层功规则3（批G2 慈禧规则）收窄加第三要件「三合所化五行≠月令印本气」（慈禧亥印化入亥卯未杀局=做功之力保 L4；14b 寅午戌火局所化=印本行只是自旺不做功，回 2 归位；理象学:10600-10611+8284-8302 双锚）；财档线证伪批N3 假设②（贫→小康系 gl 抬级传导非同源 caiming 下浮变化，收窄后随源归位贫）；zhenbao-01/14a 存量回归归因（批13 藏杀被制腿/F2 TOMB_MAP 加戌，修法草图入台账留官命/财命专批） | 见 _meta | 20261020_j1 | heldout 零翻转；trainset 1 换档（14b 小康→贫 ✅→✅ 预期传导）；calib 回归 4→2（余 01/14a 保真可见）；pytest 1385+1xf |
| `20261020_j1.json` | 批P+23b：P1=caiming 五规则（禄当财并联条件 zhongji:2603-2607/禄神制财 :2637/官杀带财象 :2819-2820/阳日主七杀当财 gaoji:10021-10022/财虚透合财不主富 理象学:6682-6684+生用三式 :6553-6559）；P2=合象定义组合库五组（zhongji:2204-2212+gaoji:8193-8225）+三合局归正化象（zhongji:2276-2278）+公门文官/医生/教师 marker（gaoji:11601-11605/10806/10872，计分被 blind_eval 否决改纯 marker）+guanming 规则五（zhongji:3693-3695）+「官杀须有根」硬门槛**被数据否决**（25 翻转全变差零收益，书例自身普遍虚透立官+「大运落实时也易当官」:3696——撤为 marker，正面回答批1 审计：书口径无法机械化硬条件）；23b=星众坏规则（妻星被≥2 非本党支众坏=星坏非制去，zhenbao:767-770；宫星交互/本党相攻/单攻不伤四吉例） | 见 _meta | 20261020_i1 | 三维零翻转；文本抖动 3 条全归因 P1 措辞；pytest 1381+1xf；calib 23b 归位✅ |
| `20261020_i1.json` | 批O 应期体系补全（批3 审计遗漏最大整块）：①冲起/冲去/冲开喜忌分流（liunian classify_chong_semantic 增 xiji/alias 键，chong_type 判定向零改动）②干支互应（yingqi_subj.detect_ganzhi_huying，zhongji:820-826 次序：本气禄位>墓>余气）③大限×大运交脱诀四态（detect_daxian_dayun_jiaotuo，zhongji:649-657）④寿元空亡 marker（detect_shouyuan_jixie 可选 kong_wang 参数，不进 engine 链红线保持，chuji:1849+gaoji:7651-7654）⑤合冲互应总则泛化（liunian.detect_hechong_yingqi，zhenbao:690+zhongji:934） | 见 _meta | 20261020_h1 | 三维零翻转零抖动（marker 级新增预期内）；pytest 1341+1xf（+28 哨兵） |
| `20261020_h1.json` | 批N2 从格判定修复（批N1 只读测量驱动：金标 56 例准确率 51.8%→**87.5%**、509 判出率 41.1%→37.3%、负例特异度 7/18→16/18 零误伤）：①粗闸从弱侧先过日主救应根（zhenbao:714 逆命题+li004/li131/li139/li263/li208 五锚）②粗闸从强侧异党两库依托闸（ans29「水得两库而不能从」）③从强化势计数+得令成势三径+两停从禄（洪秀全/qi35/走私/制例三归位）④坏根口径双向（li128 坐强根不判坏/巳申刑合以合论/主位邻支单冲坏/土冲变虚限土日主丑未冲）⑤所从财线优先（ans06/qi27/li211）⑥乞丐造注释勘误+破从夺财 severe 闭环 ⑦李敖/qi50 书内冲突备案依例7 | 见 _meta | 20261019_g1 | heldout 财 -1.4%/trainset 财 **+1.8%**（均噪声带内，官/职零变化）：改善 4（li111 官/li128 财/yx 两财）、变差 3 全归因（qi37-曹锟官硬退化 1 例备案=劫财中气根救应与从势读法书内两读不可机械分离）；ans37b 取舍备案（宁缺勿滥保 4 书锚案例）；pytest 1313+1xf |
| `20261019_g1.json` | 批L：juefa C 组豁免修复（批J 评估驱动）——D2b 财多不富加从财/比劫担财双豁免（gaoji:20067-20070 真读 direction.cong_target）；财库族 4 条断向改应期提示（理象学:8857-8858、chuji:2259，静态原局不坐实发财）；D5a 伤官见官加伤官去官格/身弱官忌双豁免（gaoji:1135-1136、shouke:2146 朱元璋锚）。复测 509 例：六条均不达接入线（D5a 80% 但判定集 5、D2b 60%、财库族中性化判定集 0），duanyu_a 维持 A 组 5 条零变更 | 见 _meta | 20261017_f1 | 三维零翻转零抖动；pytest 1286+1xf |
| `20261017_f1.json` | 批K：juefa 断语 A 组 5 条选择性接入生产（批J 509 例评估驱动：D12 争合 94%/J 配偶星多 93%/D6 枭神 79%/D13 女命婚难 77%/D1 两头钳 76%；D1 门槛收紧年时各≥2 吉神）——engine 48→49 键（juefa 全参数接入）、selectors 41→42（首个 dotted-path `juefa.duanyu_a`，marker 级措辞不进 22 项全文）、契约测试同步；yongshen.py:882 内部直调零改动 | 见 _meta | 20261017_e1 | 三维零翻转零抖动；pytest 1278+1xf |
| `20261017_e1.json` | 批H/I：①hunyin 悬案闭案——星居宫得位+1.0 以「安静无伤」为前提（gaoji:12368-12369、zhongji:4462-4463），癸丑/辛酉/戊午/丁巳 女命（星=宫=午被丑穿）由平回差，合 zhongji:4459「宫逢穿必离」+ gaoji:12947-12950 同构断语「丑午一穿宫星坏」，regression67 归位 ②gongliang 体用口径注释对齐（零行为） ③L2 校验器补应期维吉凶回对（引运 overall 凶配吉词拦）+婚姻维质量回对（差配美满拦） ④「大富大贵」成语豁免收窄（前 3 字现断言主语不豁免） | 见 _meta | 20261017_d1 | 三维零翻转零抖动；pytest 1271+1xf |
| `20261017_d1.json` | G2 三条书证功量规则（预注册 docs/kimi-g2-sanli-prereg-20261017.md）：①三种功≠三层功通则扩展（副总 甲癸丁庚/寅酉丑子 L3→L1 合书，理象学:6912；日主克链剔边+同族合并计层）②天干坏之否决（差例三 甲乙己辛/午亥巳未 L3→L0 合书，:6354-6358；官杀并透混杂+日主无印化+制不净方成立，乾隆制净豁免）③月令见印整层（慈禧 乙丁乙己/未亥丑卯 L3→L4 合书，:10607；限印入三合成势，gaoji 法则7 +0.5 让位） | 见 _meta | 20261017_c1 | heldout 零翻转；trainset 5 翻转全归因（reg67-伤食当财/yx-记者-2 变差=书内张力备案不硬推、yx-富富有百万改善归位、2 换档）+17 抖动全归因（含差例三本尊 L0 自证、朱元璋 L3→L4 帝王归位）；16 钉例零变差；pytest 1266+1xf |
| `20261017_c1.json` | G1 层次体系收编（设计稿 docs/design-gongliang-merge-20261017.md、预注册 docs/kimi-g1-gongliang-merge-prereg-20261017.md）：废 zuogong_confirm L0-L5 类型计数（理象学:6912「三种功只有一层」/6018「最多四层」明文否定）+「连珠成势」（七书零命中）；gongliang 为做功层次唯一事实源，补 0=无功态（:6022-6024）；删双轨对账；消费方过渡 narrative/engine/xiangfa_ops/__init__/prompts；verify 432→420（删失效 16+新锚 4：总理例/慈禧/差例三/副总）；公共 API 删 assess_work_level | 见 _meta | 20261017_b1 | 三维零翻转零抖动（设计论证：快照字段不含层次键、领域层早已只读 gongliang）；3 例不合书备案（慈禧 L3vs4=月令见印层级缺口、副总 L3vs1=「三种功≠三层」通则消费缺口、差例三 L3vs0=天干坏之否决缺口，候选后续批）；baseline67 hunyin:离婚 standing ❌ 立案待查（台账） |
| `20261017_b1.json` | 批D/E/F（台账 docs/audit-vs-originals-20261017.md）：D=ganqing 消费方接线（tougian/states 透传+None 保守）+体用双口径对齐（伤官归用）+制法效率分级（理象学:7462-7489）+六破表删 5 对伪书据+羊刃逢冲逢合（gaoji:16223/16548/16562）+ganqing 锚失真 4 条+narrative DeprecationWarning；E=支象行业（中级:3685-3687）+伤官合杀落地（gaoji:11661，F15 复计教训入闸注）+岁运并临/征太岁/晦太岁（gaoji:18894/18882/19077）+合财坐支得旺口径（理象学:6672-6684）+hunyin 应期三前提+冲突消解（中级:5283/5143/5217、chuji:6096）+qianyi 门户伏吟（shouke:704）；F=LLM 否定窗收窄（未移出+双字词表+伪否定剔除）+cap-marker 加转折连词门+幽灵档「平」对齐四档+SCHEMA 错路径+N1 中文数字/干支纪年+gender 归一 | 见 _meta | 20261017_a1 | heldout 零翻转零抖动；trainset 1 换档（zj-护士长 merchant→lawyer，伤官合杀落地，None→None 无打分损益）+2 抖动（yx-律师-3 caiming_adjust 书口径预期、zj-护士长 zhiye 字段）；pytest 1264+1xf |
| `20261017_a1.json` | 原著对照修复批（批6·审计台账 docs/audit-vs-originals-20261017.md）：注释锚修正 10 项（changsheng 归属任铁樵、天乙版本注、ganqing 65→75 条等）+ 方向性 bug 14 项（xiangfa_ops 财带印帽判反、ganqing 3 条件语义、yunfan 流年冲墓豁免、liunian 虚岁 -1、dayun 气势反局、zeishen 虚贼不成、liuqin 财克印恒真、hunyin 配偶星替代+正偏星之制、xueli 财克印方向+死代码、laoyu 墓开官非、shipaige 丁见丙寅、caiming 过河拆桥去冒称+制不尽封顶富、yongshen R3 六合化气豁免删除）+ LLM 校验器 6 域（非 JSON 回显封死、L2 出境/美丑全维、死词表双侧同步补词+冒号断句、缺数据最严口径、narrative 免责+scrub、backend 429/URL 兜底） | 见 _meta | t1 | heldout 财命 -7.2%/trainset 财 -2.7%（均噪声带内、官/职零翻转）：翻转 9 条归因=R3 豁免删除 4（书禁六合化气读法，理象学:2311/shouke:2574）+流年冲墓豁免 2（li141 错误信号碰巧得分）+过河拆桥 2（qi05/普例3 巨富过冲经封顶门收至富、✅→⚠️）+qi02 ⚠️；文本抖动 21 条全归因修复文案 |

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
