# 盲派客观层 变更记录

## 2026-08-22 第六轮审查 W1-W5 收官（只审不改、纯本地零 API；引擎/生产代码零改动，基线仍 `snapshots/20260821_n3`）

| 项目 | 内容 |
|------|------|
| W1 F1+F3 十一项走查 | 免责/Tuple/外发告知/丁眼锚注/isinstance/max_tokens/_self_check 人民币 7 项✅；P1×2=F6-1 降级丢迁移/相貌两维+提示语误导、F6-2 误报窗逗号/分号漏杀+死词表缺近义词（离世/去世/归西/病逝）；P2×3=F6-3 reject 子串匹配/F6-4 render 层无免责行/F6-5 lark_md LLM 路径漏网；18 合成例实测 15/18 符合预期。报告 `docs/kimi-review6-w1-f1f3-code-20260822.md` |
| W2 N 系列代码 | 七维 schema 扩展干净（生产代码零五维漏改，唯一实质漏改=test_f1_gate 五维 mock P2）；P1×2=复合词真漏网（标致/水灵/清秀/端庄书内零锚该禁，校验器+prompt 双侧抓不到，双轨补禁）、相貌引用率统计口径（独癸 16 例 desc 空，对齐后 251/251=100%，修 `_n2_analyze.py`）；P2×6。报告 `docs/kimi-review6-w2-report-20260821.md` |
| W3 书锚复核 | 锚定行 17 条回书 A×16+B×1、C 级违书=0、模块键零幻影、校验器新规则回书全 A；P2×2=「大眼」泛化/「美丽」注释口径。报告 `docs/kimi-review6-w3-report-20260821.md` |
| W4 体验样张 | 10 例红线全保零、confidence 锁/或然标注全守、basis 零幻影；F6-6（P2 新）弱线程度词放大族。报告 `docs/kimi-review6-w4-report-20260822.md` |
| W5 跨层+收官 | 10 例三层对照（`output/_w5_crosscheck.py`）：锚定行忠实 10/10、L1→L2 零断链，断链全在 LLM 加料层；294 例全量坐实：评价词添加（有神采 32/明亮 31/灵动 20/灵秀 9）+程度词（明显 17）并入 F6-6 扩展族、F6-7 臆造断语「宜动不宜静」3 例（P2 新）、F6-8 性别分流语未落地 11 例（P2 新）、「数据不足」8 例存量再犯。报告 `docs/kimi-review6-w5-report-20260822.md` |
| 发布判定 | **七维正式发布 NO-GO**——阻塞=P1 三项（F6-1/F6-2/复合词真漏网），统计口径裁定可后置，P2 全不阻塞；修批 G=G1 发布闸四项一次六件套验收→转 GO、G2 样式批紧随；统一待修清单 `docs/tasks/review6-fix-backlog.md`（review5 清单 F1/F2/F3 全落地收官） |
| 收档 | KB（header/§6.8 第六轮发现摘要/§9 总账）+CHANGELOG（本条）+五份报告；六件套引用 N3 当日全绿不重复跑 |

## 2026-08-21 动工批 N2b+N3 · 相貌维小修续打 + 七维收档收官（用户选 a 续打；引擎零改动）

| 项目 | 内容 |
|------|------|
| N2b 复合词裁定 | r3 残留 2 例（cj-1395「曲线优美」/yx-种地「体态柔美」）以书锚为准：书内相貌结论词仅 漂亮/美貌/秀气/好看/曲线好（且均被 marker 层红线改写），「优美/柔美」等含美复合评价词零锚 → **一律入禁**；校验器单字「美」扫描已全覆盖（r3 两例均被抓），码不动、不加词表不加后缀放行（`llm_channel.py` 注释记裁定）；真缺口在生成侧 → `llm_prompt.py` SCHEMA 相貌条款+`_xiangmao_anchor` 禁令显式点名「含美/丑复合评价词（曲线优美/体态柔美/秀美/俊美）同禁」 |
| 哨兵 | `test_llm_channel.py`：`test_xiangmao_redline_n2b_compound` 先红后绿（禁令点名复合词族）；`test_l2_xiangmao_redline` 补 优美/柔美/秀美 三例锁定覆盖 |
| r4 复测（294 例谷段） | **相貌维红线 2→0（加严线达成）**、迁移维红线 0 保；L0=0、L1=1.36%（4 例杂键旧族抖动，压 E7 线）、N1=1 例（reg67-合例六两妻「一次婚」计数白名单外=单例采样抖动，r1 同族）、L2 既有=1 例 0.34% 压线（gj-低保伤官「守成则平」告诫式疑似假阳族，mark 留人工，同 E7 gj-合财小康/N2 cj-县长-4 处置）；成本 ¥21.08（谷段，预算内）；数据 `output/llm_batch_20260821_n2_r4/` |
| N3 heldout 复跑 | 引擎零改动确认：blind vs gap2 heldout/trainset **零翻转零抖动**，官 48✅/财 47✅/职 24✅ 保；快照 `snapshots/20260821_n3.json`；双 seed 逐字节一致；verify 432+70+64+20 全绿；67/famous 无变化；calib 常驻 2 条存量零新增；pytest 822+1xf+19xp |
| 收档 | KB（header/§0/§8/§9 补 N1/N2/N2b+N3）+CHANGELOG（本条）+收工记录 `docs/remaining-tasks-20260821.md`（**发布 GO**：F1+F2 落地+六件套全绿；**七维 GO**：新维加严线达成）+统一动工方案归档标记完成；报告 `docs/kimi-n2b-n3-final-report-20260821.md` |

## 2026-08-21 动工批 N2 · 七维复测（294 例三轮收敛 + S1 加严漏斗；引擎零改动）

| 项目 | 内容 |
|------|------|
| 三轮批跑 | r1 L2 相貌 38（12.93%：引擎秀气线「漂亮」注入+禁令口号被复述 双根因）→ r2 剩 3（锚定 sanitize+禁令改「正文不得出现四字」；迁移锚定明令 basis 空数组治 L1 6 例）→ r3 剩 2（元复述族：正向处方代替禁令复述）；r3 离线终扫（零 API）：校验器⑧c-e 财档假阳 5 例清零（「富足」泛指/告诫式「暴富」±8 宽窗/「平平」叠词/「倒是官带财帽」让步） |
| r3 终态线 | L0=0、L1=1.36%、N1=0、L2 既有=0.34%（cj-县长-4 真越限抖动 mark 留人工）、L2 迁移=**0**、L2 相貌=2（「优美/柔美」复合词族，加严线未达 → N2b 续打） |
| S1 加严漏斗 | v4-pro 评审 30 例：新维红线 2（与校验器互洽真违规）、新维原始翻转 2（眼象同向 embellish，操作员裁决降 1=放大）→ **裁决后新维翻转 0/30**、既有五维翻转 0/30、放大 6.3%；judge 一致率 91.2% 但翻转召回 0/2 → 降级筛子；F-V3-1（zhenbao-23a 失业直述）修复确认 |
| 成本 | 合计 ¥67.2（三轮批跑 ¥63.6+评审/judge ¥3.6，谷段 ≤$12 预算内）；成本口径更正：`_PRICE` 为人民币口径，V3「v4-pro 涨价 7×」系 $→¥ 单位伪影非真涨 |
| 发现 | F-N2-1（引擎侧冻结）：`xiangmao.py:111` 秀气线 desc 含「漂亮」违模块自述红线，本批 prompt sanitize 兜底，留后续引擎批；F-N2-2 judge 新维翻转召回弱；F-N2-3 评审 API 空 content 偶发重跑即过。报告 `docs/kimi-n2-retest-report-20260821.md` |

## 2026-08-21 动工批 N1 · 七维叙述代码批（迁移/相貌独立成维；引擎零改动）

| 项目 | 内容 |
|------|------|
| llm_channel | `DIMENSIONS` 五维→七维（+迁移+相貌）；L2 按维红线两条：迁移维绝对禁「出国/移民/海外/国外/外国」（对齐引擎措辞上限）、相貌维禁「漂亮/美/丑/帅」结论词（排除窗=美元/丑时/X丑干支） |
| llm_prompt | SCHEMA_SPEC 补迁移/相貌两条款；`_qianyi_anchor`/`_xiangmao_anchor` per-case 锚定行（有信号列 marker/应期窗+禁令，无信号明令如实说无+basis 空数组） |
| 哨兵 | test_llm_channel 补迁移/相貌红线+锚定行合成违规测（先红后绿）；294 例探针全通；pytest 821+1xf+19xp |
| 前置 | F1+F3 代码一揽子（免责语/Tuple/lark_md/死亡词 mark→reject/外发告知/丁眼锚注+isinstance/max_tokens 8192 等 11 项）已随 f3d3e5e 落地（并行 F1 哨兵 test_f1_gate 计入） |

## 2026-08-21 第五轮审查 V1-V6（只审不改）+ 修批 F2 文档清零（纯注释/文档零行为）

| 项目 | 内容 |
|------|------|
| V1 新维度书锚终审 | qianyi/xiangmao 27 锚回书全过、无自造 spec、P0=0；P1-1 xiangmao 丁眼锚注缺（书内明文存在）+P2-1 zhongji:4179 行号偏 1（实 4180）+P2-2「结构同构」措辞失准（一合一冲不同构，措辞上限立论成立）；维度交付口径裁定=保持特征层不进五维叙述。报告 `docs/kimi-review5-v1-qianyi-xiangmao-20260820.md` |
| V2 端到端真实路径 | mock 飞书+mock LLM 走真实 engine 14 场景，无阻塞静默失败；P1-1 `zuogong_detect.py:997` Tuple 未导入（≤3.13 import 即崩）+P1-2 lark_md 三符字面残留+P2×3。报告 `docs/kimi-review5-v2-e2e-20260821.md` |
| V3 S1 复抽 | E7 终态 30 例三层漏斗：裁决后真翻转 1/30 压线达标（zhenbao-23a unemployed 桶同族）、L2 高危零翻转、放大 10.1% 达标；judge 召回 1/2 未过→降级筛子；v4-pro 成本 ~7× 涨（$3.23 超预算）。报告 `docs/kimi-review5-v3-s1-20260821.md` |
| V4 性能+注入+合规 | 注入 6 向量零穿透（死亡红线三层防线守住）；LLM 段均值 20.4s/P95 26.3s、¥0.0728/命谷段、6 并发全成功；**P0=免责声明两路径全缺（发布阻塞）**+P1×2+P2×4；21 次调用 ¥1.51。报告 `docs/kimi-review5-v4-perf-injection-compliance-20260821.md` |
| V6 回归复审 | 死数据零复生（D3 无双轨/41 键无死键/E5 无死分支）；fuzz 800 例零崩溃零慢；E3/E4 锚回书 6/6 全 A；快照链七件连续；P2×4（docstring 40→41 等）。报告 `docs/kimi-review5-v6-regression-20260821.md` |
| V5 收官 | 六件套全量复跑全绿（794+1xf+19xp、blind vs gap2 双零、双 seed 一致、calib 常驻 2 条零新增）；已知项全原位；新漂移 D-V5-1 五轮未入档（F2 清）+D-V5-2 清单漏项补录；**发布判定 NO-GO**（P0 免责+P1×5 未清）→F1+F2 落地+六件套复跑后转 GO；待修清单升级排期 F1/F2/F3（`docs/tasks/review5-fix-backlog.md`）。报告 `docs/kimi-review5-v5-final-20260821.md` |
| F2 文档清零（本批） | 锚注清零：qianyi zhongji:4179→4180（模块 5 处+test_qianyi 注/函数名）、「结构同构」措辞改准（一合一冲不同构、立论成立）、subjective/__init__ docstring 40→41+test_subjective 函数名同步；五轮入档：KB（header/新 §6.7/§9 总账）+CHANGELOG（本条）+收工（go/no-go+批次链）；待修清单标认领（F1 #1-6 含丁眼锚注/F3 #11-15）。纯注释/文档零行为 |
| 验证 | grep 抽查（V1-V6/免责声明/4180/41 等键全中）+pytest 快跑 794+1xf+19xp 无意外+git status 纯文档/注释零行为 |

## 2026-08-20 缺口批3 · 三项收档文档 + KB/收工全量同步（纯文档零代码，收官批）

| 项目 | 内容 |
|------|------|
| 世应收档 | 单一技法（shouke:2084-2114 定义+4 例共 8 锚）+作者自己并入宾主框架弃用（shouke:3630/5130）；应用域=过继已被 liuqin.detect_parent_qiyang 覆盖；唯一增量「要他人之子」3 例依赖临场换象样本不足不立码——收档口径入 KB §6.6 |
| 风水化解弃用 | 书明言弃用（lixiangxue:8220-8278「从未见逆转」+10633-10643+shouke:372 否定五行补+shouke:1800 自承不知是否有效）——弃用口径入 KB §6.6 防误立 |
| 时空测事收档 | 中级 3 案例花絮无体系（zhongji:2166-2173/2175-2189/2794-2811）+需新输入「问事时间」+断语开放取象——长期可选备案入 KB §6.6 |
| KB/收工同步 | KB §1.1 模块地图 29→31（+qianyi+xiangmao）/新增 §4.14/§4.15/selectors 41（§10.2 #42 记录）/pytest 794+1xf+19xp/快照链 e3→gap1→gap2/§9 总账补批1-3；remaining-tasks-20260819 补批1-3+go/no-go |
| 验证 | grep 抽查（qianyi/xiangmao/世应收档/风水弃用/时空测事/794/41 全中）+pytest 快跑复跑无意外+git status 纯文档零代码 |

## 2026-08-20 缺口批2 · xiangmao 相貌 marker 层（轻量，单批实现）

| 项目 | 内容 |
|------|------|
| 新模块 | `subjective/xiangmao.py`（~190 行）：4 主线 marker（秀气透干 zhongji:3914+反条件 lixiangxue:6655 / 金水伤官限辛 zhongji:1484+shouke:5394+反条件 shouke:474 / 活木见火 zhongji:4513+chuji:4371+lixiangxue:6628 消费 wood_type / 眼象丙丁癸 zhongji:1482-1483+lixiangxue:11124）+ 2 弱线（伤官合官杀魅力 gaoji:5618-5623+shouke:634-638 对照 / 身材曲线 zhongji:3981+1484）；十神复用 liuqin._compute_shishen 零重造 |
| 红线 | 纯 marker 无判定无档位，全输出不出「美/丑/帅」结论词；回核修正：gaoji:4035 慈禧造系反例不作秀气正锚；收档不立=贵相口诀/难看反推(zhongji:5064 孤例)/五行形体表(lixiangxue:1353-1484)/配偶相貌/身高定量 |
| 接线 | engine `result['xiangmao']`（_safe_compute 同款，只加键不改旧逻辑，wood_type 复用 result 已有键）；selectors 40→41 追加进特征 JSON（LLM 五维不扩，同 D6b 口径） |
| 哨兵 | test_xiangmao.py 7 测先红后绿（梦露/刘晓庆/阮玲玉 vs 美容师对照造+理象学6655 反例 guard+schema 红线+engine/payload 通道）；test_subjective/test_a_llm_redline/verify_dayun 计数断言同步 40→41；test_subjective payload fixture 补 xiangmao 键 |
| 验证 | verify 432+70+64+20 全绿；pytest 794+1xf+19xp；blind vs gap1 零翻转零抖动（官 48✅/财 47✅/职 24✅ 保）；67/famous 无变化；calib 常驻 2 条=存量零新增；双 seed 逐字节一致+payload 探针确认 |
| 快照 | `snapshots/20260820_gap2.json`（基线链 …→e3→gap1→gap2） |

## 2026-08-20 缺口批1 · qianyi 迁移/远行模块（设计+实现合一拍）

| 项目 | 内容 |
|------|------|
| 新模块 | `subjective/qianyi.py`（~230 行）：原局三 marker（月日冲=背井离乡 gaoji:5857 / 日时合=安居 gaoji:5858 / 马临年时=多动 gaoji:6735）+ 应期窗（马逢冲 shouke:3602+gaoji:6757、合到门户 zhongji:4179+lixiangxue:6571 双锚、马星伏吟 shouke:6692 或然、冲出年时 shouke:72 或然；马逢合=停留窗 zhongji:1567）；马星查法复用 shensha._YI_MA 零重造 |
| 红线 | 措辞上限「迁移/远行/离乡」，全输出不出「出国/移民」硬断语（书无级别判据）；伏吟/冲出带「或然」标签（gaoji:15803 书自承马多动频） |
| 接线 | engine `result['qianyi']`（_safe_compute 同款，只加键不改旧逻辑）；selectors 39→40 追加进特征 JSON（LLM 五维不扩，同 D6b 口径） |
| 哨兵 | test_qianyi.py 11 测先红后绿（书例 7 造+反例 guard 2+schema 红线+engine/payload 通道）；test_subjective/test_a_llm_redline/verify_dayun 计数断言同步 39→40 |
| 验证 | verify 432+70+64+20 全绿；pytest 787+1xf+19xp；blind vs e3 零翻转零抖动（官 48✅/财 47✅/职 24✅）；67/famous 无变化；calib 常驻 2 条=存量零新增；qianyi 键双 seed 一致+payload 探针确认（compute_all 全量双 seed 差异=xiangfa_ops 排序存量，干净树复现，非本批引入） |
| 快照 | `snapshots/20260820_gap1.json`（基线链 …→d6b→e3→gap1） |

## 2026-08-19 修批 E7 · 迭代 7 + 文档同步（官命矛盾 4 例定性 + 零残留收官）

| 项目 | 内容 |
|------|------|
| 4 例定性 | 全校验器误判无一真矛盾（叙述均与引擎 is_guanming=False 一致，否定词出旧 ±2 窗）；修复=官命维否定窗 ±2→±5 对齐财档 + prompt 锚定补「可达/可至」 |
| 复测 | 294 例谷段 validate=mark：官命矛盾 4→0、财档 2→1（0.34%）；L0/N1=0、L1 1.36%；唯一残留=真越限采样抖动 mark 留人工 |
| 验证 | pytest 776+1xf+19xp 全绿（官命/财档新断言含 4 例原文）；引擎零改动；成本 $3.01（谷段） |
| 文档 | KB 补 E5/E6/E7 + pytest 统一；收工记录补 E3-E7 批次链 go/no-go 三维 GO；零残留收官确认 |

## 2026-08-19 修批 E4 · 引擎裁定（zinv 穿引动改注 + 损子冲收档）

| 项目 | 内容 |
|------|------|
| 穿引动裁定 (a) 改注 | 回书重核 F6（gaoji:14295-14312）=原局有穿+运岁引动，其岁运己丑辛巳不构成六穿，现实现确不触发；(b) 补书据否决=无第二独立锚；(c) 改实现否决=书未给「引动」具体口径，具体化即工程自造 |
| 损子冲收档 | 仅 gaoji:14122 一处直锚 + 案例五（21038-21052）形态非同构，未达双锚不立 |
| 改动 | 纯注释零行为（zinv docstring+两处行注 + test 头注 + KB §4.13/§9 同步） |
| 验证 | pytest 767 全绿；blind vs e3 零翻转零抖动（官 48✅/财 47✅/职 24✅）；基线仍 e3 |

## 2026-08-19 修批 E3 · 数据锚注批（raw_quote 恢复 + 锚修 4 处 + calib 回填 + U3 备案）

| 项目 | 内容 |
|------|------|
| raw_quote 恢复 | 回书核实 chuji:1300-1306 QQ 追问即本案（癸丑己未丙辰甲午），卜文确系书据，D1 剔除理由不成立，恢复+补 source |
| 锚修 4 处 | 县长-3 补锚 chuji:3702 / 刑警 3851→3852 / zinv 14374→14372-3 / test_d6b 乾→坤（书 gaoji:14242 坤造） |
| calib 回填 | IMPROVE 5 条（修双码点 regex）；常驻 2 条保真不回写；baseline {✅31 ⚠️11 ❌4} |
| U3 备案 3 注 | yx-房地产-2 / yx-富数百万 / zj-邢铭芬（引擎/gold 背离，YAML 口径注入） |
| 验证 | verify 全绿、pytest 767、blind vs d6b 零翻转（官 48✅/财 47✅/职 24✅）、新快照 20260819_e3.json |

## 2026-08-19 修批 E2 · 文档清零（KB K1-K7 + CHANGELOG 补 5 条 + 收工 20260819 终态）

| 项目 | 内容 |
|------|------|
| KB | pytest 787collected 统一 / 模块地图 25→29（+zinv+llm 三件套）+feishu / 新增 §4.13 zinv 条 / §9 总账基线 d3→d6b / M5 快照链 47 份 / selectors 39；顺手修两处自相矛盾（§2.3 财 51.33→52.21、§7.13 calib 4→2） |
| CHANGELOG | 补 5 条：E1/飞书集成/D5/D4/D1（表格+验证行） |
| 收工 | remaining-tasks-20260819.md 新建（批次链 + go/no-go 全 GO + 剩余 E3 必做 E4 可选）；0818 版加取代标注 |
| 验证 | grep 五键全中 + pytest 767 复跑无意外 + git status 纯文档零代码 |

## 2026-08-19 修批 E6 · 财档迭代 6（校验器口径修 + prompt 一行锚定，引擎零改动）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| 假阳 9 例四类缺口 | ①让步封顶（封顶/上限/定档/定格标记前档位词不计）②泛指动词「致富」豁免 ③引擎原文引用豁免（±2 字窗≥3 字落 caiming 原文不计，巨富档除外防掩护真越限）④修饰档归位（小富→小康级、偏下降半档）⑤愿望条件句「想…得靠…」豁免（若/一旦不入，保 8721） | U3 报告 §2 | subjective/llm_channel.py |
| E6 复测新发同族补漏 | ⑥「富格/富档/富贵」恒豁免（引擎术语/泛指复合词）；否定窗 4→5（盖「不可奢求大富」） | E6 复测 | subjective/llm_channel.py |
| 真越限 5 例同机制 | _tier_anchor 追加一行：能力承诺句（能成/可成/勤劳可）与条件假设句（一旦/若…便）档位词同样不得超上限 | U3 §3 | subjective/llm_prompt.py |
| 哨兵 | test_llm_channel +3 测（豁免五类/引用豁免巨富除外/真越限句式仍拦/锚定行内容） | — | tests/test_llm_channel.py |

验证：pytest 776+1xf+19xp 全绿；谷段复测 294 例（$2.98）L2 财档越限 **16(5.44%)→2(0.68%)**——假阳清零、真越限 5→1（变体「可达中富」）、边界 1（小康偏富留人工）；U3 16 例新叙述全合规。报告 `docs/kimi-e6-caifu-iter6-20260819.md`。判定：**收敛收尾**；迭代 7 候选（非阻塞）=「可达/至」能力变体锚定 + 新发 3 例官命矛盾口径复核。

## 2026-08-19 修批 E5 · 飞书加固（U2 P2 余项五项清零，纯 feishu 包内引擎零触）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| 重放窗口超 2000 全清重开（U2 P2-1，已复现） | `_seen_mids` set→dict 滚动窗口：超上限逐条滚出最老，窗口内近期消息仍去重 | U2 审查 | feishu/bot.py |
| token 刷新无锁并发重复刷新（U2 P2-2，实测 8 线程刷 8 次） | `threading.Lock` 锁内双检，等锁线程复用新 token，并发只刷 1 次 | U2 审查 | feishu/client.py |
| 静默错解三例（U2 P2-3） | ①时间正则加前导边界 `(?<![\d:：.])`，`123:45` 不再截断成 23:45 报 ParseError；②时刻后紧跟 `:秒` 明确报错不静默丢弃；③「四柱」触发词让位阳历：文本含完整阳历日期走阳历路径 | U2 审查 | feishu/router.py |
| 500 回显内部错误（U2 P2-5） | 异常响应改通用 `{"error":"internal error"}`，详情 `log.exception` 记日志 | U2 审查 | feishu/bot.py |
| 单线程 server 慢连接阻塞（U2 P2-6） | 换 `ThreadingHTTPServer`+并发上限 32（信号量排队）+body 上限 1MB(413)+读超时 15s，README 参数表注明 | U2 审查 | feishu/bot.py、feishu/README.md |
| 哨兵 | test_feishu +6→34 测：窗口滚动双向钉死（近期去重/最老滚出）/8 线程 1 次刷新/123:45 报错/秒位报错/四柱让位阳历/500 不回显 | — | tests/test_feishu.py |

验证：test_feishu 34 全绿、pytest 773 passed+1 xfailed+19 xpassed（767+6）、mock 冒烟（并发 token 刷新 8 线程→1 次、重放窗口滚动）随哨兵覆盖。skipped：Encrypt Key 解密支持（控制台勿配，README 红线已有）、外部去重存储——量级上来再做。

## 2026-08-19 修批 E1 · 飞书上线必修（U4 条件 GO 三 P1+P2-4 清零，纯 feishu 包内引擎零触）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| token 服务端作废无刷新重试（U2 P1-1：99991663/99991661 缓存期内全断） | `_api` 捕获两错误码→清缓存重取 token 重试一次，再败抛错；正常路径零影响 | U2 审查 | feishu/client.py |
| reply 发送失败用户零反馈（U2 P1-2） | bot reply 包 try+纯文本兜底重发一次，再败仅日志，线程不静默死 | U2 审查 | feishu/bot.py |
| README 未警示 Encrypt Key（U2 P1-3：控制台误配即全断） | bot 检测 encrypt 字段告警丢弃+README 红线段「勿配 Encrypt Key」 | U2 审查 | feishu/bot.py、feishu/README.md |
| VT 未配=零校验（U2 P2-4，上线 checklist 强制） | main() 启动查 FEISHU_VERIFICATION_TOKEN 未配 RuntimeError+README 必填说明 | U4 处置 | feishu/bot.py、feishu/README.md |
| 哨兵 | test_feishu +5→28 测：99991663 重试成功/reply 首败兜底/VT 缺失报错/encrypt 告警（旧 3 failed 含 VT 挂起全修） | — | tests/test_feishu.py |

验证：test_feishu 28 全绿、pytest 767 passed+1 xfailed+19 xpassed（762+5）、mock 冒烟四条全过。飞书上线闸通过（U4 go/no-go：条件 GO→GO）。skipped：token 并发锁（P2-2）/EncryptKey 解密支持——量级上来再做。

## 2026-08-19 飞书集成工程批 · mangpai/feishu 新包（LLM 通道接日常推演，引擎零触）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| 飞书机器人全链 | 新包 6 文件 528 行：client（TenantAccessToken 缓存+API 封装）/router（事件路由+重放去重）/service（命盘推演编排）/formatter（结果卡片模板）/bot（webhook HTTPServer 入口）+README | 任务书；LLM 通道四指标已达标为前提 | mangpai/feishu/（新增） |
| 哨兵 | test_feishu 23 测：mock 全链三例跑通（不触真实飞书 API） | — | tests/test_feishu.py |

验证：test_feishu 23 绿、pytest 762 passed+1 xfailed+19 xpassed（739+23）、U2 审查 P0=0（token 刷新/重放/降级三判据全过、并发降级 8/8、fuzz 232 例零崩溃）、`git show --stat` 实证零引擎文件（无快照合理）。残留 P1×3+P2 簇→E1 批修（见上条）。

## 2026-08-19 修批 D6b · 子女断法实现（zinv 岁运应期+借腹+时柱喜用腿）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| zinv 新模块（子息岁运应期+借腹） | `analyze_zinv(day_gan/gans/zhis/gender, *, relations/liuqin_result/dayun_list/liunian_list)`，分层单向依赖 objective+subjective.liuqin（只读其 child_star_cat，不重造星宫定位）。得子窗三机制：合动（岁运合子息星，shouke:18-20 丁壬合）/开墓（子息星·妻星墓逢冲开，shouke:18-20 辰冲戌+gaoji:14008-14009/14374 口诀）/制枭（枭夺食潜势盘岁运合制偏印，gaoji:14087-14107 庚辰运乙庚合）；损子窗五机制：克到位（运干克星到位且不合星，gaoji:14108-14128）/合去（克运中流年合走子息星，gaoji:14108-14128 戊合癸）/穿引动（岁运支穿子息星所临支，gaoji:14295-14312+17465-17484 降权）/枭夺食运（shouke:428）/合神被克（shouke:18-20 戊克壬）；借腹 marker=日支受穿+子息星/妻星入时墓（gaoji:14317-14334+zhongji:1911-1914/4165-4170 两书同构）。损子措辞中性（子息星受创/子女宫引动），字面无死/夭/丧，LLM 侧由既有 _scrub_death 兜底 | 设计 docs/kimi-d6a-zinv-design-20260819.md §3（R1/R2/R3 立） | subjective/zinv.py（新增） |
| liuqin 优劣增补腿（R4） | detect_zixi_youlie 增「时柱为喜用→优/为忌神→劣」腿，用忌取扶抑总线 classify_strength/_yongshen_cats（direction_result 只读消费，缺省自调）；喜忌混杂不立腿防过火；analyze_liuqin 方向总线计算前置于 zx_yl 透传 | D1 gaoji:14226-14240+D2 gaoji:5972-5973/6341-6342+D3 理象学研究版:4283-4285（跨两书三处明文） | subjective/liuqin.py |
| engine 接线+特征 JSON 通道 | `result['zinv']=_safe_compute('zinv', analyze_zinv, ...)` 置于 liuqin 之后（消费其结果）；schools.py selectors 追加 'zinv' 一条（38→39，镜像 liuqin 同通道进特征 JSON 纯数据，LLM 五维不扩不进 prompt——设计 §3.4 授权，KB 保护文件特此备案）；selectors 计数断言三处同步（test_subjective/test_a_llm_redline/verify_dayun） | — | engine.py、subjective/schools.py、subjective/__init__.py docstring、verify_dayun.py、tests/test_subjective.py、tests/test_a_llm_redline.py |
| 明确不做 | 数量（E1-E4 书自证不准）/送终（G1-G3 孤口诀）/性情（D7 孤条）/有无增补腿 R5（动 M3 共振须重验，候选）/运定性别 R6（候选） | 设计 §4 收档/候选 | — |
| 哨兵（先红后绿） | 新建 test_d6b_zinv.py 12 测（先红：模块不存在 collection error → zinv 实现后 liuqin 两腿红 1 failed → 全绿）：F1 制枭（己卯运不在窗/庚辰运在窗+己卯枭夺食运）、F2 一造三机制（壬戌运+丁卯年合动/戊辰年开墓/戊辰年合神被克入损子窗、壬戌运不误判克到位）、F4 克到位+合去、H2/H3 双借腹、案例八反例 guard（平和岁运零损子窗+非借腹）、schema+死亡词典字面红线、summary 只述应期借腹、R4 喜用腿（案例八）/忌神腿、engine 接线+payload 通道 | 见各测注释行号 | tests/test_d6b_zinv.py |

验证：哨兵先红后绿 12/12、verify_mangpai 432 全绿、verify_dayun 70/70、pytest 739 passed+1 xfailed+19 xpassed（727+12 新测）、blind 对照 20260819_d3——heldout 官 48✅/财 47✅/职 24✅ 三维 0 翻转 0 文本抖动、trainset 0 翻转、67/famous 0 回归（无变化）、calib REGRESSION 2 条（zhenbao-01 官/zhenbao-14a 财）与 HEAD worktree 复跑逐条一致=存量零新增、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260819_d6b.json`。

## 2026-08-19 修批 D5 · 工具/备案批（收尾，引擎零改动）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| rescore glob 合并隐患复核 | 确认 D4 已修（sorted glob 合并）；冒烟验证 retry 覆盖生效——原记录无 reading 被 retry 覆盖后重评分例数=1 | T3 §A.2 | output/_llm_batch_rescore.py |
| 三备案落 KB | G6 scrub 代价（官命 veto 理由 12/281 被 scrub）/as_of_year 可注入方案（四处 now() 锚，T0 跨年对拍判定域零翻档）/子夜 ±1min 日柱敏感带（历法固有边界不修）——落 KB §4.11+§9 同步 | 修批A/T0 复核 | docs/knowledge-base.md |

验证：pytest 727 passed+1 xfailed+19 xpassed 全绿；引擎零改动无快照。

## 2026-08-19 修批 D4 · prompt 迭代 5（职业桶/应期逐年锚定，引擎零改动）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| L1 职业锚定 | llm_prompt 增 `_zhiye_anchor`（主荐桶锚定/无倾向禁断言）；llm_channel `_l1_basis` 空值白名单 `{'zhiye.primary'}`（空=无倾向判定本体，L1 3.40%→0.68%） | T3 评审翻转簇 | subjective/llm_prompt.py、subjective/llm_channel.py |
| L2 应期逐年锚定 | llm_prompt 增 `_yingqi_anchor`（dayun_analysis 逐运+liunian 逐年 overall 锚定，禁套话）；D3 补供的 dayun_analysis 直接可用 | T3 评审翻转簇 | subjective/llm_prompt.py |
| 评测脚本 | glob 合并 sorted（修 T3 §A.2 retry 覆盖隐患）+_t3_eval 材料补 dayun 锚表 | T3 §A.2 | output/ 评测脚本 |

验证：S1 复验（同 T3 三层漏斗、同 sample30、v4-pro 双实例谷段）评审翻转 **9/30→0/30**（L2 高危 2→0），放大 10.1%→8.1%，一致率 85.2%→89.3%——**三线全达标，S1 语义层 NO-GO→GO，飞书集成三阻塞全解除**；rescore L0 0/L1 0.68%/L2 5.44%（财档越限 16 例留迭代 6）/N1 0；pytest 727+1xf+19xp。成本 $5.23（全谷段）。报告 `docs/kimi-d4-prompt-iter5-20260819.md`。

## 2026-08-19 修批 D3 · 供给批（dayun_analysis 死 selector 修复，选 B 补供方案）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| dayun_analysis 死 selector（T3 §A.1 P1：281/281 缺失，LLM 全程零大运表） | 断裂点定位：selector 声明（schools.py，受保护不动）与 build_payload 转发均正常；LLM 批跑/评估路径 bazi_data 仅 bazi+gender+year（无 da_yun 键）→ engine.py `if dy_list:` 不成立 → compute_all 不产出该键 → 声明静默落空。修复=build_payload 层补供：`dayun_gz_sequence`（年干阴阳+性别+月柱 → 方向+8 步干支序列，确定性计算不需节气）+ 复用 analyze_dayun_mangpai 出吉凶信号，engine compute_all 零改动（判定零影响） | 「大运为路，流年为应」（高级:18598-18855；授课:936-976、7144）；方向口径同 compute_da_yun（理象学:3854+） | objective/dayun.py、subjective/__init__.py |
| 数据形状（D4 应期锚定预留） | 每运保留 gz/order/gan_shishen/zhi_relations/work_types/tomb_effect/fei_shen_activated/lu_blade/changsheng/qishi_change/is_kong_wang/positive_signals/negative_signals/overall（与 prompts/mangpai.md 的 dayun_analysis.* 引用对齐，L1 校验按 dayun_analysis.dayun 整组引用可溯）；剥 gan_relations/tiyong_import/has_* 布尔/desc 检测中间件控体积；真实 da_yun 路径同投影统一形状。合成路径起运岁不可得（需精确出生月日时刻对节气）→ 诚实缺省 start_age/end_age，以 order 为锚+age_note 声明 | 起运岁书口径 理象学:3846-3877 | 同上 |
| verify_dayun selectors 总数断言 39→38（D1 存量备案①顺手修） | 修批A③ 摘 gongmen_wuzhi 后断言未同步，更正后 verify_dayun 70/70 | KB §10.1 #42 | verify_dayun.py |
| 哨兵（先红后绿） | 新建 test_d3_dayun_payload.py 5 测（先红 3）：engine 无 da_yun 不产出（红线锁）/合成方向+序列正确/结构+缺岁诚实/真实 da_yun 投影后起止岁保留/性别缺失不合成不编造方向 | — | tests/test_d3_dayun_payload.py |

验证：哨兵先红 3 后绿 5/5、verify 432 全绿、verify_dayun 70/70（69→70）、pytest 722 passed+1 xfailed+19 xpassed、blind 对照 20260819_d2 三维零翻转零抖动（heldout 官 48✅72.73/财 47✅68.12/职 24✅46.15，trainset 官 96✅/财 59✅/职 40✅ 全同）、67/famous 0 回归、calib 常驻 2 条无新增、双 seed payload 探针逐字节一致（sha256 相同）。引擎基线=`snapshots/20260819_d3.json`。token 体积：补供后每命 payload +约 7180 字符（≈4500 token，10 例均值，payload 50.4k→57.6k 字符 +14%），峰段成本 +约 $0.002/命。

## 2026-08-19 修批 D2 · 入口批（性别必填 + 界外年份 guard + lon 校验，T0 边角三项）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| 性别缺失/未知静默按阴逆排（T0 P1） | 定策略（a）报错：calc_bazi_full 入口校验，None/''/'未知' 等一律 ValueError 带「大运方向依赖性别」说明；合法集=男/女/male/female/乾/坤（compute_da_yun is_male 补 '乾'，旧口径 乾 被静默当阴=同型陷阱）；飞书交互侧性别设必填 | 阳男阴女顺排/阴男阳女逆排（理象学:3854+）——方向 50% 硬依赖性别，任何缺省都是静默错排；与入口既有风格一致（月13/时25 本就 ValueError） | objective/bazi_calc.py |
| 界外年份裸 KeyError（T0 P2） | 入口 guard：<1900 或 >2100 → ValueError 带「节气表覆盖 1900-2100」说明（原 SOLAR_TERMS[year] 裸 KeyError） | T0 报告 §2/§4 | objective/bazi_calc.py |
| city_lon 无校验（T0 P2） | 入口校验：非数值/None/bool/nan/inf/越 [-180,180] → ValueError（原 None 裸 TypeError、999 静默跑通） | T0 报告 §2/§4 | objective/bazi_calc.py |
| 子夜 ±1min 日柱敏感带（T0 P2 备案） | 确认现状合理不修：均时差秒级残差致 BT 00:00 压回前日 23:59:58，真太阳时两派各自自洽，属历法固有边界 | T0 报告 §2 | （备案，零改动） |
| 哨兵（先红后绿） | 新建 test_entry_guards.py 33 测（先红 19）：性别缺失/未知×5、合法性别×6、乾坤=男女同向、界外年份×5、边界年 1900/2100、非法 lon×8、合法 lon×6 | — | tests/test_entry_guards.py |

验证：哨兵先红 19 后绿 33/33、verify 432 全绿、pytest 717 passed+1 xfailed+19 xpassed（LLM 打磨批实测 684 passed 基线 + 本批 33；KB 旧记 682 collected 系修批C 口径已过期）、blind 对照 20260819_d1 零翻转（引擎判定零改动：guard 仅挡非法输入，blind_eval/llm_channel 合成 bazi_data 路径不过 calc_bazi_full）、67/famous 0 回归、calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财）无新增、双 seed 逐字节一致。引擎基线=`snapshots/20260819_d2.json`。

## 2026-08-19 修批 D1 · 数据批（gold 修正 5 条+锚 15 处，纯数据引擎零改动）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| calib gold 标注错 3 条 | zhenbao-05 官命 lv4→3（厅级反标 L4）/层功 [3,4]→[2,3]（无书据）；zhenbao-23a 层功 max1→2 | 50qi:157/yanjiu:6103-6104 | tests/calib_assertions.yaml |
| trainset gold 标注错 2 条 | cj-处级-5 财 富→小康、cj-足球 财 小康→富（书两处「收入很高」chuji:5797-5805） | 书原文复核 | tests/trainset/cases.yaml |
| source 锚漂移 15 处+raw_quote 张冠剔除 | 锚按书行号更正；cj-贫穷命 raw_quote 剔除张冠；cj-老总口径注；calib zhenbao-10 dayun 误录删除（戊寅=1998 流年非大运，50qi:313-315，采方案 b 删字段） | 逐条书核 | heldout/trainset/calib yaml |

验证（Hermes 复核）：calib 常驻回归 4→2（余 zhenbao-01 官命/zhenbao-14a 财命=引擎错存量）；trainset 财 51.33→52.21%（59✅/44⚠️/10❌，翻转 2 条皆改善）；heldout vs fb 零翻转零抖动（官 72.73/财 68.12/职 46.15）；verify 432 全绿；pytest 704+1xf+19xp。基线=`snapshots/20260819_d1.json`。

## 2026-08-18 打磨批 · LLM 通道（峰谷价计价 + 正式通道文档，引擎零改动）

| 项 | 处理方式 | 依据 | 文件 |
|----|----------|------|------|
| _PRICING 旧平价 $0.14/$0.28 过期（2026-08-16 官方改峰谷价） | 改 peak/off-peak 双档表（官方 2026-08-18 复核：v4-flash 峰 $0.44/$1.32、谷半价 $0.22/$0.66；v4-pro 峰 $1.32/$3.96、谷 $0.66/$1.98，cache miss 口径）；峰段=UTC 01:00-04:00/06:00-10:00=北京 09:00-12:00、14:00-18:00 | api-docs.deepseek.com/quick_start/pricing | subjective/llm_backend.py |
| `_estimate_cost` 不按时段选档 | 增 `_price_tier(at)`（按请求发出的北京时间选峰/谷），`call_deepseek` 以请求 wall time 计价，返回 dict 增 `price_tier` 标注；历史批次成本不回算（文档标注口径） | 任务书 | 同上 |
| 正式通道交付文档 | 新建 `docs/llm-channel-20260818.md`：§1 接口（render_structured_reading 单命入口/validate 三模式 mark/reject/off）§2 验证记录（四指标达标线+五轮迭代轨迹 40.21%→23.88%→12.76%→9.62%→3.41%→remap 0.00%+remap 规则表）§3 使用指南（成本实测+峰谷价+批跑一键命令+谷段建议）§4 安全红线 §5 维护项；KB §8 补 llm 通道条目 | 数字全部以批跑/重评分实测为准 | docs/llm-channel-20260818.md、docs/knowledge-base.md |
| 哨兵 | 新建 test_llm_backend.py 3 测（峰段边界 7 探针/flash 峰谷计价+谷=半价/pro 谷档+未知模型放行）；llm_backend `_self_check` 同步双档 | — | tests/test_llm_backend.py |

验证：计价测试 3 绿、test_llm_channel 19 绿、pytest 全量 **684 passed + 1 xfailed + 19 xpassed，0 failed**（修批C 682 collected + remap 批既有新增 + 本批 3）；计价探针峰/谷两时间点档位实测正确（峰 10:00 $0.0110/谷 20:00 $0.0055 样例 usage，谷恰半价）。v5  remap 离线重评分复核（n=281）：L0 0.36% / L1 0.00% / N1 0.36% / L2 4.98% 与任务书口径一致。引擎零改动，compute_all 链未碰。

## 2026-08-18 修批B · 引擎 P1（神煞 year_ref×3 + calib 传 age，R1/R2 P1 清单）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| zaihuo 双查合并漏 year_ref（R2 同型新发现：:394-398/:584-592 读主键+day_ref，day_ref 实为死代码——主键即日支侧，year-only 劫煞/亡神/灾煞静默丢失） | 车祸 xiong_shen 与死亡 xiong_sha 两处并入 year_ref 子键 in_pillars；实证盘（年支申→劫煞巳落时柱、日支午→劫煞亥不在局）修前未入 xiong_shen 可翻转 risk 档 | gaoji:7912「先以日支为主…年支亦需同查」 | subjective/zaihuo.py |
| laoyu 就地重算 shensha 不读子键（R2：:640-648 裸 compute_shensha_ext+只读顶层，配置断路+顶层语义 F13 后静默翻转） | detect_jiesha_wangshen 改走 resolve_shensha + 并入 year_ref/day_ref（zhi 取实际落柱一侧）；analyze_laoyu/engine 链路补透传 shensha_result | gaoji:7912 | subjective/laoyu.py、engine.py |
| calib 不传 age（R1 P1：calib_assertions.py:76 has_daxian 恒 False，应期断言评旧口径） | run_case 传 age=流年公历年−出生年（锚定事件年，与断语时段同口径；无流年缺省不变）；应期 6 断言传 age 后 6/6✅ 口径一致 | 与 engine F10 传 age 同族 | tests/calib_assertions.py |
| 同型扫描 | xiangfa_ops `_shensha_by_pillar`（R1/R2 P2 存量）一并修复：共象映射并入 year_ref/day_ref 子键落柱；**备案**：liuqin:872/gongmen_wuzhi×3 就地重算仅消费羊刃（day_gan 起算，非 reference 敏感，无双查子键问题）；hunyin:892/zhiye:955 为带注释的显式 day_ref/year_ref 健康读者（灾煞 year_ref=阎锡山锚） | — | subjective/xiangfa_ops.py |
| 哨兵（先红后绿） | 新建 test_fb_shensha_yearref.py 5 测（先红 5）：实证盘劫煞/灾煞 year-only→zaihuo 车祸+死亡、laoyu has_jiesha、xiangfa 落柱、calib daxian 定位 | 见上 | tests/test_fb_shensha_yearref.py |

验证：哨兵先红 5 后绿 5/5、verify 432 全绿、pytest 662 passed（+5）、blind 对照 20260818_fa——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动、trainset 0 翻转**；67 例 0 回归（5 IMPROVE）、famous 0 回归（9 IMPROVE）、calib 4 REGRESSION stash 实证=存量（与修批A 同清单，0 新增）、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260818_fb.json`。

## 2026-08-18 修批A · LLM 红线三项（R5 block×3：siwang scrub → zeishen 单源化 → gongmen 摘除）

| 项 | 处理方式 | 书锚/依据 | 文件 |
|----|----------|------|------|
| A① siwang 键外泄漏（R5 block-1：shipaige「寿元：食伤被制短命」「父死母再嫁」/liuqin「手足早夭」/xiangfa_ops lianti warning「寿命」/guanming「制死」/liunian「冲破主死亡」） | build_payload 装配层统一死亡词典 scrub（`_scrub_death` 递归过滤：含死亡词字符串条目整条移除、含死亡词 dict 键整键移除），非逐键补丁；只动 LLM 视图层，引擎内部 siwang 保留（F14 设计不变） | F14 寿元红线延续；prompt 禁令之外的物理屏蔽 | subjective/__init__.py |
| A② 换象假「净」（R5 block-3：huanxiang 用裸 detect_relations wa 缺 zuogong_confirm auxiliary 标记 → 11/509 矛盾例=9 train+2 heldout，payload 换象断语与同帧 zeishen_bushen.jing_zhi 自相矛盾） | 净制口径单源化：huanxiang 改消费引擎已算 zb_res（engine 透传 `zeishen_result`）；缺省 fallback 以 analyze_zuogong 标记后 work_actions 自算（zhiye 内部调用路径同口径）；caiming `_zeishen_jingzhi` 补传 zg（旧 wa=空与引擎口径分叉，27 例 jingzhi False→True 但已评分 heldout 4 例 tier 均不变） | 蒋介石「制之不净达不到四层功」（zeishen_bushen.py:606-608 同源） | subjective/xiangfa_ops.py、subjective/caiming.py、engine.py |
| A③ gongmen_wuzhi 98.8% 恒真进 payload（R5 block-4） | selectors 摘除（39→38 键），F18 弃用决策落 payload 通道；engine result 键保留（内部存档/测试消费） | F18 正式弃用决策延续 | subjective/schools.py、engine.py 注释 |
| 预注册（本批铁律） | heldout 例=shouke-qi15-房地产千万（戊子辛酉戊戌乙卯）：预期**不翻转**——merchant 7→6 与 lawyer 6 平，tie_pri(merchant>lawyer) 保 primary；财命⚠️不经净制豁免路径。实测确认 0 翻转 ✓（另一 heldout shouke-li048 仅应期 verdict，unscorable） | — | 本表+汇报 |
| 哨兵（先红后绿） | 新建 test_a_llm_redline.py 9 测（先红：ImportError+行为红——zhenbao-09 不净仍换财象/死亡盘 payload 命中 5 词/selectors 39）：scrub 单元+两死亡盘零命中+引擎内部 siwang 保留/矛盾例不换象+fallback 同口径+李嘉诚净制锚保留+caiming 与引擎同口径/selectors 38+payload 无 gongmen | 见上 | tests/test_a_llm_redline.py |

验证：哨兵先红后绿 9/9、verify 432 全绿、pytest 657 passed（+9，test_subjective 39→38 同步）、blind 对照 20260817_f19——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转**（预注册 qi15 确认不翻转）、trainset 0 翻转；文本抖动 3 条（heldout qi05+trainset yx-处级/yx-科级）逐条审=意图内（caiming_adjust 文案「制不尽量级不足，封顶富」→「贼神捕神净制，量级同制尽」，tier 由后续凶向封顶决定不变，rubric outcome 全不变）；67 例 0 回归（5 IMPROVE）、famous 0 回归（6 IMPROVE）、calib 4 REGRESSION stash 实证=存量（与 F6-F19 同清单，0 新增）、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260818_fa.json`。509 例语料复跑：换象矛盾 11→0、is_wuzhi 出 payload。

## 2026-08-17 F19 批 · P1/P2 扫尾（收尾批：yunfan 两 P1 修 + 全遗留条目清账）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 大运侧合变冲无参与字限制（批4 P1-3，F8 skip） | 运冲须冲原局合做功参与字（与冲变合 A14 收窄对称）——包工头盘己酉运酉冲卯（卯与寅亥合局无关）假阳消除 | 案例四子合丑同族机制；包工头 chuji:3296「壬卯/丁巳运发财」 | subjective/yunfan.py `_detect_dayun_fan` |
| 大运侧禄刃倒戈漏挂（批4 P1-4）+禄/刃字须在局守卫（批4 P2-1） | `_detect_lu_ren_fangg` 补挂大运侧；natal_zhis 形参生效（字不在局冲无所冲，流年侧同受益收窄） | 案例七 gaoji:3761-3764 辛卯丙申辛未丁酉行丁卯运「酉金禄神被冲…因罪被枪毙」 | subjective/yunfan.py |
| dayun 测试口径（批5 测试缺口） | 备案标注：11 测自建盘锁 M2 自洽口径零书例，docstring 注明不硬补（四口径上游书锚见 objective/dayun.py） | — | tests/test_dayun_objective.py |
| 遗留条目全扫（批1-10 归档+F0-F18 汇报「留后续」） | 收档备案 15 项全录 KB §6.5：laoyu 岁运维度（机制归 yunfan 域，「官出现之年」单条不足立法）/孙立人出干（单例+机制含混）/穿变合（无失败锚）/T2 多而墓/案例二袁世凯/yingqi_subj 两条/liunian 统看缺并+七杀冲禄分工（皆书内张力）/dayun 十神定吉凶簇/soil_type 六细化/biqi 收口/payload 补键（与 F14 红线反向）/docstring 卫生；F17/F15/F11/F4/F1/F18 残留复核维持收档 | 逐项理由见 KB §6.5 | docs/knowledge-base.md |
| 哨兵（先红后绿） | 新建 test_f19_yunfan.py 4 测（先红 3）：包工头合变冲消除/构造正例保触发/案例七禄刃倒戈/禄刃在局守卫 | 见上 | tests/test_f19_yunfan.py |

验证：哨兵先红 3 后绿 4/4、verify 432 全绿、verify_dayun 70/layer1 64/layer3 20 全绿、pytest 648 passed（+4）、blind 对照 20260817_f18——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 红线回退**；trainset 0 翻转；文本抖动 17 条（heldout 8+trainset 9）逐条审=意图内（caiming_adjust/veto_reasons 文案随合变冲抑制/禄刃倒戈重分类，rubric outcome 全不变）；67 例 0 回归（54✅13⚠️0❌）、famous 0 回归、calib 4 REGRESSION 经 stash 实证=存量（与 F6-F18 同清单，0 新增）、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260817_f19.json`。F0-F19 修复批系至此收官，残留全入 KB §6 备案簇可追溯。

## 2026-08-17 F18 批 · shipaige + gongmen_wuzhi（殿后批：批8 P0×3 断语层重写 + 弃用决策落地 + 阳制阴口径）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| shipaige 断语层与郑氏碎片 39 条零对应+两冠名冲突+自相矛盾（批8 P0×3/P1） | 六域断语层整体重写：逐条=碎片原文+行号，仅收录可机械检测者（父母3/婚姻4/子女4/事业8/牢狱4/寿元5），未实现条目（性别/空亡/神煞/运岁/年龄段未接入本模块）入 todos；「官杀为子」冠名废→碎片:81 身旺财为子身弱印作儿（身强弱=比劫印 vs 财官食伤数量简化代理，本模块不接 yongshen）；「劫财抗杀入牢狱」冠名冲突废→碎片:90 劫财七杀两相连从军（相邻柱一柱劫财一柱七杀）归事业域；「食神生旺子女聪慧」与自身数量诀「二食贪吃/三食愚钝」矛盾→废，子女域按碎片重建；方法论层重写为碎片§四 8 条 | 碎片:61-115（mangpai/docs/zhengminsheng-shipaige-fragments.md） | subjective/shipaige.py |
| gongmen_wuzhi 接入决策（F1 标记弃用，决策留 F18） | **正式弃用：不接 zhiye**（F15 已在 zhiye._score_military 按书重写 8.2 六组组合，本模块仅存档）；隔离=narrative `_gongmen_wuzhi_line` 结论行通道切断（is_wuzhi 近恒真、零信息量行不再进 LLM 结论），engine result 键因 schools selectors 保护链保留；docstring 改正式弃用 | 批8 审计 11 P0 + F15 决策 | subjective/gongmen_wuzhi.py、subjective/narrative.py |
| 阳制阴口径与书相反（批8 P0-5） | 旧=标准阳支集纯地支「克」（子算阳）→ 书口径：阳气=丙丁巳午戊戌 制 阴气=辛酉癸子丑，**含天干**（按 _gan/_zhi 位置后缀取字）、**子归阴**、制类（克/冲/穿/刑）须阳为制方；与 F15 zhiye.py:1042-1050 同口径 | gaoji:11787-11788 | subjective/gongmen_wuzhi.py |
| 哨兵（先红后绿） | 新建 test_f18_shipaige_gongmen.py 18 测（先红 17）：三 P0 修复探针+碎片断语 11 例+阳制阴正反两例（丁克辛含天干/子克巳反向不计）+正式弃用标注+narrative 隔离 | 见上 | tests/test_f18_shipaige_gongmen.py |

验证：哨兵先红 17 后绿 18/18、verify 432 全绿、pytest 644 passed（+18）、blind 对照 20260817_f17——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动**（shipaige/gongmen 不进 blind rubric 与快照字段）；67 例 0 回归、famous 0 新增回归、calib 4 REGRESSION stash 实证=存量（0 新增）、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260817_f18.json`。残留封存：shipaige 未实现碎片条目（性别/空亡/神煞/运岁接入）入 todos；gongmen_wuzhi 其余 10 条 P0 随正式弃用封存不修。

## 2026-08-17 F17 批 · xueli + liuqin（批7 P0：xueli X1 破坏之神 + liuqin L2/L4 + 三节补齐）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| xueli 破坏之神与书明文不符（批7 P0-1） | 破坏之神 财+枭 → **财/伤官/比劫**（zhongji:5397 逐字）。`classify_xueli_shen` 增 shang_count/bijie_tou/bijie_tou_ym/bijie_gen（日主不算比劫）；`classify_xueli_level` 扣分重写：伤官明现无印杀相配 -1（配印/配官杀做功不扣，zhongji:5405-5407）；**年月**比劫成群 -2（年月=学业期宫位，zhongji:5484「年月比劫是不爱学习的标志」）、透干有根群 -1、单透无根群不扣（zhongji:5540 例17 泄印反锚、:5575 例21 反锚）；枭夺食移出学历章（书锚在牢狱章 :5589-5590），xiao_count 键保留兼容 | zhongji:5397/5405-5409/5484/5540/5575 | subjective/xueli.py |
| liuqin 早逝失星宫同坏总门（批7 P0-2） | `detect_parent_zaoshi`：is_zaoshi=len(markers)>=1 → **星坏∧宫坏**双门（星坏=财临库地/患父患母；宫坏=年月宫刑/冲/穿/破）；单标志只录 marker 不即断 | gaoji:13649「父母星与父母宫同时被破坏」 | subjective/liuqin.py |
| liuqin 子息原神取反（批7 P0-4） | cat=财（财星统看）时原神 比劫→**食伤**（比劫克财是忌神）；官杀=财/食伤=比劫原口径不动 | gaoji:14116-14118 | 同上 :572 |
| liuqin 三节整缺（批7 P1） | 新增 `classify_xiongdi_paihang`（阳干阳生/阴干阴生/日坐冲生定无兄，顺逆数书无定量不杜撰返 None）/`classify_xiongdi_qingyi`（比劫争财·兄弟宫生合=厚/刑冲=薄）/`detect_zixi_youlie`（优=得位+原神生扶；劣=原神被坏/星宫犯三刑/宫受冲穿/枭夺食——刑限三刑、破不取：案例八子卯刑破仍判优 vs 案例九丑未戌三刑判劣）；analyze_liuqin 输出+summary 接入，__all__ 导出 | gaoji:14412/14651/14230；案例四 :14520、案例八 :14236、案例九 :14260、案例十 :14720 | 同上 |
| 哨兵（先红后绿） | 新建 test_f17_xueli_liuqin.py 19 测（先红：导入错误+基线 5/21）：xueli 21 书例探针 5→**9**（例6/11/12/15 新命中，原 5 命中全保；例9 高→中方向反转修复）；liuqin 星宫同坏双探针/子息原神三探针/排行四测/情谊三测/优劣案例八·九 | 见上 | tests/test_f17_xueli_liuqin.py |

验证：哨兵先红后绿 19/19、verify 432 全绿、pytest 626 passed（+19）、blind 对照 20260817_f16——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动**（xueli/liuqin 不进 blind rubric 与快照字段）；67 例 0 回归、famous 0 新增回归、calib 0❌、双 seed 剥 _meta 逐字节一致。引擎基线=`snapshots/20260817_f17.json`。残留备案：xueli X2 须做功要件/X3-X7（杀制伤官死分支/合杀羊刃劫财/财坏印退化/枭夺食错置/中断判据）未修——21 书例 12 例未达标主因（例1/2/5/9/10/13/14/16/18/19/20 须 X2/X5/X7）；liuqin L1 印当父门控恒真/L3 弃养日支辰墓/L5 物极必反阈值留后续批。

## 2026-08-17 F16 批 · hunyin（批7 P0-1/2/4/5：四冠名条款机制与原著全错 + 冲穿刑四吉例）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 好婚姻「宫制/冲去夫妻星」未实现且反向扣分（批7 P0-1） | `classify_hunyin_quality` 宫判定重写：宫星互制（冲/穿/刑）按势党定喜忌——宫方成势且制得住（单一星制动作+对方党<2）=宫制去忌神**好婚姻**+2；星方成势=宫忌被制去**较好**+2；无势/制不住（星多方攻宫）回落扣分。合宫三分：星合入宫+1/合印·禄不论坏/合他星-1.5。宫坐四库：非星支冲刑穿=**开库为喜**（库喜刑冲）免罚+1，星支攻制不入开库（戴安娜未被戌刑坏=制不住）。复用 zhengfan._compute_qishi 势党（subjective→subjective 已有 yongshen 先例），自刑排除 | zhongji:4286-4351（rule2/3+:4351 合印禄）；四吉例 :4294/4300/4493/4504；制不住 :4290/4303-4308、戴安娜 :4516-4518 | subjective/hunyin.py |
| 水中捞月机制全错（批7 P0-2） | 按书三要素重写：①正星（男正财/女正官）坐夫妻宫（日支本/中气）②日主与日支自合（日干合日支所藏之干）③偏星透干（正星之偏；扩大型含自合对象之偏——壬午造丙火偏财）。旧「星与他干合/争合/宫被冲」废 | zhongji:5081-5083 闲注三条件、:5098 自合柱、:5099-5105 扩大型；gaoji:12904-12910 案例十/十一 | 同上 `detect_shuizhong_laoyue` |
| 关财门名同实异（批7 P0-4） | 重写为**女命专属·运岁应期**：原局财星明现（财=官之原神）+运岁比劫透干或运岁支冲/穿财支→关财门（离婚信号）；轻重=伤官旺+财被穿倒→必离/余→闹离。旧「男女对称·原局星入墓/合锁」废——书「入墓不开」正位=独身格三 | gaoji:12963-12967「女命关财门最验」、:12979-12980 轻重、案例十二（卯运冲酉=闹离）；zhongji:3578 | 同上 `detect_guan_caimen`（签名增 dayun/liunian 四参，engine 本已透传） |
| 独身四格与书诀不符（批7 P0-5） | 按书诀重写：格一宫占比劫禄印星难入（宫本气比劫/印 + 星全无/宫拒星（冲穿刑克本气星支，克须宫为施事方）/宫占印+时柱占禄刃——案例六/七·教授三型）；格二宫星互害反成克（宫五行克星五行+星支攻宫+星有援=透干或得合，合入己墓=被收非援——教授例纯格一）；格三星入墓不开（宫占星之墓或星透干入墓，无冲刑开）；格四=水中捞月。旧「纯阳纯阴/华盖重见」两格自造（「华盖」四书 grep 0 命中）废；`classify_dushen` 改委托四格 | gaoji:13068-13070 口诀+案例六~十一；zhongji:4924-4940 | 同上 `classify_dushen_sige`/`classify_dushen` |
| 禄绊桃花（批7 P0-3） | F13 已重建（shensha lu_ban=禄合财官杀伤食），本批仅补书例哨兵锁定（案例八辰酉合禄/案例九卯戌合禄） | zhongji:1517；gaoji:13259-13310 | tests/test_f16_hunyin.py |
| 哨兵（先红后绿） | 新建 test_f16_hunyin.py 21 测（先红 12）：好婚姻四吉例/制不住三反锚/捞月三书例+无自合反例/独身四格书例+好婚反例/关财门书例+男命+无运岁/禄绊桃花两书例 | 见上 | tests/test_f16_hunyin.py |

验证：哨兵先红 12 后绿 21/21、verify 432 全绿、pytest 607 passed（+21）、blind 对照 20260817_f15——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 三维 0 翻转 0 文本抖动**（hunyin 不进 blind rubric 与快照字段，财 47≥46 红线守住）；67 例 0 回归、famous 0 新增回归（戴安娜 hunyin=差守住）、calib 4 REGRESSION 经 stash 实证=存量（0 新增，婚姻 ✅2⚠️2❌1 逐条不动）、双 seed 剥 _meta 逐字节一致。

## 2026-08-17 F15 批 · zhiye（批7 P0-3/P0-4/P0-6 + 批8 接入决策）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 军警 8.2 明文组合未实现（批7 P0-3，军警书例 4 中 1） | `_score_military` 落地 6 组：①戌武库做功+3（须做功，存在不计）②火金相战+2（字级一火一金有制/合动作）③金水成势见火+2 ⑤申酉丑寅≥3字交织+2 ⑦丑戌刑/阳制阴+2（书口径含天干、子归阴；制类须阳为制方）⑧戌武库刑冲开官杀库+2；**贵气门**=官杀主气≥2 柱且透干（gaoji:11964「先观格局有无贵气，再查组合」——羊刃/官杀库腿经锚检验误伤面大已撤）+组合封顶 +6。**接入决策：不接 gongmen_wuzhi**（11 条 P0 偏差+is_wuzhi 近恒真，F1 已弃用），本模块按书重写窄条款。④比劫库/羊刃库制印不落地（政委例十 未穿子=军权 vs 复例四 辰穿卯=经商，双锚同构不可分，铁律16） | gaoji:11620/11648/11654/11658/11785-11788/11964；口诀二+案例四 :11745 | subjective/zhiye.py `_score_military` |
| 内食神格丢书限定（批7 P0-4 之三） | 补「地支食神做功，或食神生财」闸：做功=HE/ZHI 动作当事人（被日主泄秀之生用不算），或食伤生财信号已立；旧版存在即 +2（教师例六/校长例七文职书例皆被喂分） | gaoji:11020/7.2 案例一「巳火食神被制」 | 同上 `_score_merchant` |
| merchant 收窄试案（批7 P0-4 之一/二）→ **撤回备案** | 食伤生财主气化+冲财/合财去重曾落地，blind 实证误伤 heldout merchant 既有✅ ans33（8→6 被 accountant 抢）/li131（6→4）/li133（7→5）——旧「双计/柱级」口径恰是三例过阈来源，红线「既有✅不得误伤」优先，整体回退。**勿重试**（KB §7.15） | 红线 vs gaoji:11020 书内张力 | 同上（已还原） |
| lawyer ⑥伤官合杀/食神制杀 → **撤回备案** | 与既有「伤官制官」同动作复计，误伤 li154 摇滚歌星（performer 6 被 lawyer 7 抢）/董竹君庚申门户锚/trainset 杰克逊，书例端零增益（例九纪检不依赖此条），撤 | 铁律16 | 同上（已还原） |
| C4 硬绑定审查（批7 P0-6 传导：宾馆服务员 caiming 巨富→merchant 12） | zhiye 消费侧「身弱+财官主气≥4+日支无比劫」扩展 gating 试案：真阳锚宾馆 vs 假阳锚 7.2 案例一（庚子辛巳甲辰癸酉，书断内食神格董事长）同构（两造皆身弱+财官主气 4 字），双锚不可分撤回。**根因定在上游**：caiming 财统官(b)腿（caiming.py:779-785 财生官相连+少方仅一位）不验身弱——zhongji:2853 巨富例与 :3478 富屋贫人例同构异断（书内张力），gongliang 同判 L3；修复留 caiming 后续批。zhiye 侧旧富屋贫人 gating 不动 | zhongji:3477-3478 vs 2853-2859 | （审查结论备案，无代码改动） |
| 哨兵（先红后绿） | 新建 test_f15_zhiye.py 10 测：军官例一保持/例二（先红：未分类）/纪检例九（先红：merchant 10 吸走）归位 military、例四贵气门挡、律师例八/商人例十二保持、贵气门构造反例、罗斯切尔德/乔布斯/岳飞保护锚 | 见上 | tests/test_f15_zhiye.py |

验证：哨兵先红 2（例二/例九）后绿 10/10、verify 432 全绿、pytest 586 passed、blind 对照 20260817_f14——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 46.15% 三维全不动**（唯一翻转 li263-三陪女=unscorable 换档不入准确率）；trainset collateral 备案 1 条：yx-科级（会计/审计书例，申子辰水局锚）会计 6→军警 9（金水成势见火+火金相战过门，8.2 字级组合固有声纳）；67 例 0 回归、famous 0 新增回归、calib 4 REGRESSION 与 F14 存量清单逐条一致（0 新增）、双 seed 逐字节一致。军警书例探针 1/10→3/10（军官例二/纪检例九归位）；7.3 职业章持平 2/12（fn 侧 teacher/accountant 通道缺口留后续批）。

## 2026-08-17 F14 批 · zaihuo + LLM 红线（批7 P0×2/P1×2 + 批10 寿元红线；prompts 决策点3已解锁）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 马星死判据（批7 P0-1） | F13 已修（ma_count 改消费 in_pillars），本批补书例哨兵锁定：死例一（丙午癸巳辛酉癸巳）全局无马 ma_count=0 | excerpts:149「以年支日支为主」 | tests/test_f14_zaihuo_llm.py |
| 死亡「高」双向偏离（批7 P0-2） | 旧「墓绝空亡任二项即高」收窄为书诀「墓/绝/空亡三类齐见方判高」——绝+空无墓假阳（构造盘甲申辛未壬子壬寅）高→中；书真死例一/九/十（单一类）维持中 | gaoji:16323「墓绝空亡齐相见，神仙难救必归西」 | subjective/zaihuo.py `detect_siwang` |
| 禄落空亡未实现（批7 P1） | 补条款：禄支落空亡入 mu_jue_kong——死例九（庚辰戊寅甲辰戊辰，寅禄甲辰旬空）出「禄神（寅）落空亡」marker | gaoji:16434-16436「禄神空亡，根基虚浮」 | 同上 |
| 牢狱漏接（批7 P1） | analyze_zaihuo 新增 laoyu_result 入参：laoyu.risk 入 max_risk 与 summary（牢狱 11.1 为灾祸之首）；engine 接线 result['laoyu'] | gaoji ch11 章序 | 同上 `analyze_zaihuo`、engine.py |
| A1 破口（批7/批10） | engine zaihuo 调用 yunfan_result 全量→yunfan_slice（与 caiming/guanming/zhiye/direction 同口径，自动流年窗口不再污染 siwang 急性触发） | 批10 A1 口径 | engine.py:592-602 |
| LLM 寿元红线（批10 护栏只堵一半） | ①prompt 禁令：mangpai.md 增「安全红线」节 + ENVELOPE_RULES 增禁令条——禁死亡/寿数/夭折/大限生死断言，灾祸仅作一般安全提醒；②物理屏蔽：zaihuo 新增 `zaihuo_llm_view`（剔除 siwang，max_risk/summary 重算为疾病/车祸/牢狱三域），build_payload 对 zaihuo 选择器（含 "*" 通配）强制走该视图，narrative `_zaihuo_line` 同源——siwang 死亡档/寿元星 markers 不再进 payload/digest 双通道，引擎内部 result['zaihuo']['siwang'] 保留 | 批10 红线只堵 detect_shouyuan_jixie 一半 | subjective/prompts/mangpai.md、subjective/__init__.py、subjective/narrative.py、subjective/zaihuo.py |
| 哨兵（先红后绿） | 新建 test_f14_zaihuo_llm.py 11 测（先红 6）：马星书例/墓绝空亡齐见高/绝+空无墓收窄/死例一·九·十三书例/牢狱入 max_risk 有无两向/payload 屏蔽/narrative 屏蔽/prompt 禁令 | 见上 | tests/test_f14_zaihuo_llm.py |

验证：哨兵先红 6 后绿 11/11、verify 432 全绿、pytest 576 passed（+11）、blind 对照 20260817_f13——**heldout 官 48✅/财 47✅ 68.12%/职 24✅ 全不动，0 翻转 0 文本抖动**（f7→f14 累计翻转 42 条全为 F8-F13 已备案项，财 47≥46 红线守住）；67 例 0 新增回归、famous 0 新增回归、calib 4 REGRESSION 经 stash 实证=存量（与 F6-F13 同清单，0 新增）、双 seed 逐字节一致。

## 2026-08-17 F13 批 · shensha（批7/8：桃花重建/day-ref 接线/日支起算/马星死判据/戊双刃/reference 断路）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 桃花重建（批8 P0-3+传导 P0-2） | 咸池整套五书无「咸池」明文，书桃花=「禄合财官杀伤食」十神合绊象。shensha 新增 `detect_lu_ban_taohua_zhi`（禄支与他支六合/半合+所合支藏干十神属财/官/杀/伤/食+合日支不论），挂 桃花['lu_ban']；hunyin `detect_lu_ban_taohua` 改消费 lu_ban（旧以咸池为桃花，伪锚）；zhiye performer 桃花信号书口径化=咸池日支起（`_tao_day` 接 day_ref）∨丙火食伤透∨日主坐禄+禄做功+食伤透；「居日柱」补日主坐沐浴修饰（仅 has_tao 已立时）。岳飞 performer 8→1 根因修复（旧 year-ref 咸池子落日柱驱动） | zhongji:1517/4349/4471、gaoji:13259-13313 口诀+案例八/九、zhenbao14期「丙火主艺术演技」、chuji:5871/5877 吕丽萍/梦露「禄神与食神做功应是艺人」、gaoji:1610 刘晓庆 | objective/shensha.py、subjective/hunyin.py、subjective/zhiye.py `_score_performer` |
| 起算主支 year→day + 双查（批8 P0-1/2） | 默认 reference 'day'（compute_shensha_ext/resolve_shensha/engine×2/bazi_calc 签名对齐）；亡神/劫煞/灾煞/桃花/驿马恒年日双查——year_ref/day_ref 子键年日异支且异值时恒在，不再随 reference 翻转丢次柱值（旧配置断路：全库 0 处传 'day' 且真切会丢亡神次柱） | gaoji:7912「先以日支（为主）查空亡、亡神、劫煞。年支亦需同查」、:7789「以年支或日支查」 | objective/shensha.py `_dual_ref`、engine.py、bazi_calc.py |
| 马星 count 死判据（批7/8 P0） | zaihuo 车祸 ma_count 改消费在局马数 in_pillars（旧 count=并集马支数恒≥3，随机 2000 盘 min=3，`ma_count>=1` 恒真白送 1 分）；供给层 count 字段保留但注释警示 | 批8 供给侧实锤 | subjective/zaihuo.py `detect_chehuo` |
| 戊双刃四处单值漏检（批8 传导 P0-3） | zaihuo 凶神汇聚/gongmen_wuzhi 组合1+武职类象/liuqin 羊刃逢冲 四处 `zhi in zhis` 单值改全刃表（zhi_all/in_pillars）——戊日刃在未（无午）盘不再漏检 | 理象学:2086「戊刃在午、未」（:4977/zhongji:1520「未或巳」分歧标注） | subjective/zaihuo.py、gongmen_wuzhi.py、liuqin.py |
| 灾煞条款口径固定（传导护卫） | zhiye military 灾煞条款（灾煞三书无载，象法自造）固定读 year_ref 保持旧校准口径——日支起算切换下阎锡山（年支未→灾煞酉在局）军警锚不失、复例四merchant 锚不翻 | 批8 P1 灾煞无锚；阎锡山 calib 锚 | subjective/zhiye.py `_score_military` |
| 哨兵（先红后绿） | 新建 test_f13_shensha.py 9 测（先红 7）：岳飞 performer=1/禄绊桃花两书例+两反例（合印不论/合夫妻宫不论）/驿马 gaoji 案例九双查/默认 day+劫煞灾煞双查/戊双刃供给+两消费/马星 count=0 同局盘；test_laoyu 阳制阴盘午移月支（日支起算后旧盘午日→劫煞亥在局多中一法属书口径正确，调合成盘保「单法命中」前提） | 见上 | tests/test_f13_shensha.py、tests/test_laoyu.py |

验证：哨兵先红 7 后绿 9/9、verify 432 全绿、verify_dayun 70/layer1 64/layer3 20 全绿、pytest 585 collected 565 passed（+9）、blind 对照 20260817_f12——**heldout 官 48✅/财 47✅ 68.12% 不动、职 23→24✅（44.23%→46.15%，ans10-梦露 ⚠️→✅，红线守住）**；trainset 职 42→41✅——collateral 备案 3 条：生例二经理 ✅→❌、带帽银行副处/yx-14300 ⚠️→❌（皆日支起算后咸池日在局之象法固有声纳，卯日→子在月/申日→酉在月/巳日→午在时均为咸池日支查法正检，非检测错误）；帕瓦罗蒂 ❌→✅ 改善。famous 0 降级（帕瓦罗蒂/李嘉诚/乔布斯 ❌→✅ 等 6 改善）、67 例 0 回归（5 改善）、calib 4 REGRESSION 经 stash 实证=存量（与 F6-F12 同清单，0 新增）、双 seed 逐字节一致。文本抖动=zhiye_primary/label 换档同名条目，逐条对应翻转明细=意图内。

## 2026-08-17 F12 批 · guanming + juefa（批6 七 P0：官禄格定义/制用三反向/主位字门槛/grade 映射/G5 误杀/断语7 方向）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 官禄格定义与书相反（批6 P0-4） | 废「官星天干坐其禄位」旧口径，改书明文「印生禄的，禄在主位，禄当权力，为官禄格」——日主之禄居日支/时支（主位）且印星明现（印生日主即生禄）。慈禧（乙未丁亥乙丑己卯，时上见禄）哨兵锁定；阎锡山辛坐酉误贴消除（其 calib 盘乙禄在卯+亥印，按新定义成立属口径内） | zhongji:3969、shouke:6392、慈禧例 zhongji:3970-3973 | subjective/guanming.py `classify_guanming_combo` |
| 制用四类缺三反向（批6 P0-1） | `_CONTROL_PATTERNS` 补 官杀制伤食/印制财/伤食制印 三反向（书明言四类皆双向）——布莱尔（癸巳丁巳丁巳戊申，戊癸合=合制·官杀制伤食，「制去官之原神…当了大官」）恢复 | zhongji:3700/3842/3868、理象学:7277、布莱尔 zhongji:3833-3836 | 同上 |
| 印配比禄整体缺失（批6 P0-2） | 新检「印配比禄·比劫制印库」：禄/刃支制印五行之墓库=制印得权、印主权力（印库主气非印，主气粒度配不到）。三收窄：比劫限日主禄/刃支、禄刃须居时支、印不透干 | zhongji:3678-3679 章首列目、总编 zhongji:4105-4108、朱镕基 zhongji:3850-3854；反锚 robber（泛比劫）/ans17 骗子（壬印透干，shouke:776-790） | 同上 |
| G5 误杀羊刃合杀锚（批6 P0-3） | G5「杀刃类另须官杀有制化」废除——刃制杀本身就是制，额外要印制化无书据；庭长（壬子丙午壬辰丙午，羊刃合杀当官）恢复。孪生丁未造由反局否决承担区分：`_has_positive_guanming` 收窄——身弱官杀为忌，其「官杀有根」「官带财帽」非正向（丁未造身弱+反局「见辰有牢狱」，反局 veto 生效）；新增 N3GUAN：藏杀被制 combo 在场=统杀/制杀得权，官杀入墓不否决（希特勒丑入辰墓锚恢复） | 庭长 zhongji:3808-3813、丁未造 zhongji:3814-3822/shouke:3462、希特勒/曾国藩/慈禧墓杀锚 | 同上 + veto 链 |
| 主位字门槛未实现（批6 P0-5） | 制用 combo 纯宾位（年月互制，两端无主位字）不立官命；藏杀被制须被制支居主位或制它的动作另一端在主位（希特勒年支丑：日支寅克/时支酉合，主位参与保留）。印类 combo（财制印/印制伤食/伤食制印）豁免——书例 ans46 银行行长「未财制子印…沾岳父的光」即纯宾位财制印得官，规则三与该书例存书内张力备案 | zhongji:3683-3684、ans46 shouke:2112 | 同上 |
| grade 映射系统性降 1-2 档（批6 P0-6） | grade_map 收书：4→总理-元首级/3→厅级-省部级/2→处级-厅级/1→科级-处级（与 gongliang._RANK_GRADE 同口径，F6 备案口径差收口） | 理象学:6103-6104「一层科级到处级…四层总理或元首级」 | 同上 `assess_guanming_level` |
| 布莱尔 比劫夺财 veto 误报（批6 P1-1，联动必修） | 新增 R1GUAN3：官杀透干且官杀/食伤互制 combo 在场者，比劫制财=制去官之原神得权，比劫夺财不否决官命（无食伤之局 zhenbao-23a 真凶锚不命中） | 布莱尔 zhongji:3835、处级「制去官与官的原神是当大官的」 | 同上 veto 链 |
| juefa 断语7 干克方向接反（批6 P0） | `WX_KE_ME[g]==year_wx`（检出年克他）改 `WX_KE[month]==year_wx`——书「提纲（月）克年，亦主父母不全」 | gaoji:20230 | subjective/juefa.py 断语7 |
| 哨兵（先红后绿） | 新建 test_f12_guanming_juefa.py 13 测（先红 12）：布莱尔/庭长/总编三锚恢复 + 丁未孪生造反局否决 + 慈禧官禄格 + 旧口径废除 + 纯宾位构造盘 + grade 四档 + juefa 断语7 双向；test_guanming_g 丁未造改 analyze 级反局断言（G5 废除同步） | 见上 | tests/test_f12_guanming_juefa.py、tests/test_guanming_g.py |

验证：哨兵先红 12 后绿 13/13、verify 432 全绿、pytest 556 passed（+13）、blind 对照 20260817_f11——**heldout 官命 50→48✅（75.76%→72.73%，Δ=-3.0% 噪声带内，红线未全守，2 条 collateral 备案见下）、财 47✅ 68.12%/职 23✅ 不动、trainset 官 96✅ 83.48% 持平**。翻转明细：heldout 2 条皆官命 ✅→❌——li002-去印得权（书机制=「印弱为病，用财去印得权」shouke:2216，印不现未建模，旧 ✅ 靠寅丑暗合歪打正着，规则三下现形）、li207-副市长秘书（书机制=「癸印化酉官」印化官杀 shouke:6648，A8 支杀化印检测层残留§6.2 备案簇，旧 ✅ 靠 G1 例外歪打正着）；trainset 0 翻转（希特勒经 N3GUAN 恢复）。famous gm 三改善：慈禧/希特勒/李昌镐 ❌→✅（0 降级）；67 例 0 回归（54✅13⚠️0❌）；calib 4 REGRESSION 经 stash 实证=存量（与 F6-F11 同清单，0 新增）；双 seed 逐字节一致。文本抖动 7 条皆 veto_reasons 语义变化（positive 身弱收窄/R2GUAN 印类家族扩/R3GUAN·YUNFAN-G 随 raw 翻转），逐条审过=意图内。

## 2026-08-17 F11 批 · yongshen + caiming（批6 四 P0：22期例6/例7 从格 + 财统官前置 + 过河拆桥相连）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 22期例6 从官格漏判（批6 P0-1） | 根被坏三式补第四式「晦」：邻支湿土（丑/辰）晦巳/午火根失其性；成势闸根坏宽口径——日主根俱被坏者同用合局化势计数（例6 水势主气仅 2，申子半合化水则实 3 成势），两停且根未被坏者维持主气计数。附 F0 勘误落地：旧注释锚干支「酉丑子申」更正为「巳丑子申」 | zhenbao:739-743「被丑土晦尽…看八字气势在官，以从官格看」；例3「辰土晦火之故」；生例一富婆两停不从反锚 | subjective/yongshen.py `_broken`/`classify_strength` |
| 22期例7 未从误判从弱（批6 P0-2） | conc>=6 粗闸收窄：印有根且印根不被坏者不能从、落 22期细则判身弱——印须透干明现方有扶身之力（藏干印不作救，否则粗闸无一得行）；段氏明文反对衰旺计数取用 | zhenbao:744-747「乙木印星根在亥，印星有根，故不能从…以身弱看」；shouke:454 | subjective/yongshen.py `classify_strength` |
| 财统官前置补全（批6 P0-1 caiming） | 书外硬前置「主位制宾官」独腿致书例漏检——前置改两腿居一：(a) 主位制宾官（旧口径保留，巨富锚群 load-bearing）；(b) 财生官相连且少方仅一位（书注「少指只有一个」防财2官3两可误统，PUTONG3 一章锚）。zhongji:2853 巨富书例（乙己壬辛/巳丑辰丑）views 补出财统官 | zhongji:2817-2822 注「财官必须相连了，即财生官了…只论原局」、:2853-2859「官多而财星少，财可统官…巨富」 | subjective/caiming.py `classify_caifu_view` |
| 过河拆桥验财生官相连（批6 P0-2 caiming） | 旧码仅全局验五行（WX_SHENG[财]==官）不验该财确生该宾官；新增 `_pos_connected`：同柱相互作用/支支五行流通不限柱位/干干须紧贴/异柱干支无直接生系。ans12 桥=壬（月干）巳中庚支藏财不生异柱天干→假富格撤销 | zhongji:2977「主位的酉生了宾位的亥官」；shouke-ans12:2560 书断小康不贵不富；真阳锚 qi05/qi20/qi02 不动 | subjective/caiming.py `_detect_guohe_chaiqiao`/`_pos_connected` |
| 哨兵（先红后绿） | 新建 test_f11_yongshen_caiming.py 7 测：例6 从官/例7 身弱/例1-2-4-5-8 回归锚/2853 财统官/ans12 假富格撤销/qi05+qi20 破财富格双锚/qi02+qi20歌厅 隔柱支支相连锚；test_p0_blindgap N3 测试盘时支酉→亥（旧盘被「晦」改判从弱，调盘保身弱前提） | 见上各行号 | tests/test_f11_yongshen_caiming.py、tests/test_p0_blindgap.py |

验证：哨兵先红 4 后绿 7/7、verify 432 全绿、pytest 543 passed（+7）、blind 对照 20260817_f10——**heldout 财命 46→47✅（66.67%→68.12%，红线守住）、官 50✅、职 23✅ 不动**；**ans12 ⚠️→✅ 翻转确认**（富→小康，假富格根因修复）。翻转明细：heldout 3 条（ans12 改善；li191 ❌→❌换档；li202-乞丐 ⚠️→❌ 备案——根坏宽口径下酉丑半合金势实，书断「身弱不胜财」与例6「印无根不救」存书内张力）；trainset 1 条（zj-工薪无官 官 ✅→❌ 备案——从弱触发 G3 从格豁免，消费侧域级过滤留后续批）。67 例 0 回归（54✅13⚠️0❌）、famous 0 降级、calib 4 REGRESSION 经 stash 实证=存量（与 F6-F10 相同清单，0 新增）、双 seed 逐字节一致。

## 2026-08-17 F10 批 · yingqi_subj 寿元域（批4 四缺口：印级寿元星+克/绝坏关系+engine 传 age+高级两书例）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 寿元星定位补印级（批4 P0-1） | 定位诀三级落地：天干食伤 → 支/藏干食伤亦为寿 → 无食或食伤受伤无用（透干虚浮无根或坐绝）则透干印补位；日干旧已覆盖第三级 | gaoji:16148「食神为寿第一尊，无食看印印为根」、:16157「无食神或食神受伤无用，则看印星」、:4600/7651 支上食伤为寿 | subjective/yingqi_subj.py `detect_shouyuan_jixie` |
| 坏关系补「克」「绝」（批4 P0-2） | 新增 `_is_zhengke`（五行正克）**仅限「到位被坏」语境**（原局静克是做功常态不计带病）；「绝」=透干寿元星虚浮无根坐绝地→带病（寿元星被坏）。附带按书收窄破集：盲派破仅子卯/卯午互破（子卯已由刑覆盖，补卯午），标准六破其余各对（寅亥等）无段氏书锚移出 `_HUAI_PAIRS`——不收窄则藏干寿元星壬禄亥被寅亥假破误带病、吉反锚（cj1:697 状元造）翻 risk | gaoji:16148「穿害克绝命难长」、:16547「最忌寿星遭刑克」、yx2:7486「申金到位被局中官星火正克」、cj1:1846「水绝于巳」、理象学:2934-2955 | subjective/yingqi_subj.py `_HUAI_PAIRS`/`_is_zhengke` |
| 寿元星根被坏检出 | 寿元星藏干根支（禄以外）被原局坏=带病、被运岁支坏=引动 | gaoji:16206-16216 案例二「癸水印星之根辰土被穿坏…流年甲戌冲辰，辰中癸水印根被冲散，印根被拔寿星倒」 | 同上 |
| engine 传 age（批4 P0 传导） | 新增 `_current_age()`（当前年−出生年，与 `_current_dayun` 同口径并复用），`infer_comprehensive_yingqi` 调用传 `age=`——has_daxian 不再恒 False，大限∩大运∩流年 commit 名副其实；无出生年回退空转不变 | 批4 审计：engine.py 旧 :594-598 三要素名不副实 | engine.py |
| 哨兵（先红后绿） | test_yingqi_shouyuan.py +4：高级寿元章案例一（丙午癸巳辛酉癸巳，丁酉运乙酉年——食神坐绝+酉到位被午正克，先红 risk=False 后绿）/案例二（癸卯丙辰甲辰乙丑，庚申运甲戌年——印级补位+印根辰被戌冲，先红路径错后绿）；engine 传/不传 age 各一 | gaoji:16164-16216 | tests/test_yingqi_shouyuan.py |

验证：哨兵先红 3 后绿 14/14、verify 432 全绿、pytest 536 passed（+4）、blind 对照 20260817_f9——**heldout/trainset 0 翻转 0 文本抖动**（官 50✅ 75.76%/财 46✅ 66.67%/职 23✅ 44.23% 全守住）、67 例 0 回归、famous 0 降级、calib 4 REGRESSION 与 F9 存量清单逐条相同（0 新增）、双 seed 逐字节一致。红线维持：只做「带病逢引动」推演，`detect_shouyuan_jixie` 不进 engine 消费链。残留备案：刃/墓/空亡机制族（批4 P1-6）、运岁逢绝、他干破禄不区分命主/六亲（批4 P1-5）。

## 2026-08-17 F8 批 · yunfan 岁运反局（三 P0：三刑补全闸 + T3 伏吟干收窄 + T1 冲开库豁免）

| 项目 | 内容 |
|------|------|
| 联动三刑补全闸 | 原局已齐三刑不再任意流年必出极重（案例九 gaoji:3799 锚） |
| T3 伏吟干收窄 | 须「所透之墓为主位功神墓库」前提（中级 903/2853 锚）；理象学 7720 酉运亿万巨富豁免 |
| T1 冲开库豁免 | 运冲墓库功神支不入破坏功神（zj 中级 903/2853 戌运冲开辰库发 5 亿） |
| 验证 | verify 432；pytest 522（+5 哨兵）；blind 对照 f7 heldout/trainset 0 翻转（财 46✅/官 50✅/职 44.23%）；67 例 0 回归（+5 IMPROVE）；famous/calib 0 回归；双 seed 一致；KB §5.5 发财锚群 10/11→11/11 |

## 2026-08-17 F9 批 · laoyu 牢狱（批5 四 P0：死条款复活+方向/死码/过宽）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 法五「反局+辰丑」复活（批5 P0-1） | `detect_fanju_chen_chou` 旧调 `analyze_zhengfan(day_gan, gans, zhis, relations=rel)` 签名错配实抛 TypeError 被 except 吞，条款上线即死 3 年；改与 `yongshen._ensure_zhengfan` 同径：`analyze_zuogong` 取 work_actions → `analyze_zhengfan(wa, None, gans, zhis)` | 中级:5592「凡出现反局的情况，有辰、丑等字在局中，多数应牢狱」；书例:5652-5659 冲合反局+丑 | subjective/laoyu.py |
| 七杀夹克方向修正（批5 P0-2） | 旧判据要求日柱本身带杀（方向反），书锚两例日柱均无杀漏检；改判=月、时两柱皆明现七杀夹日主；:498 等价重复死分支删除 | 中级:5825-5829 上海庄家「双杀夹克身，是有官灾之象」（月时双己未）、:445-447「七杀夹克日主…已被枪毙」（月时双丁） | subjective/laoyu.py |
| 阳制阴减凶兑现（批5 P0-3） | risk 聚合 hit_count==1 分支旧码 `'低' if yang_zhi_yin else '低'` 两分支同值；改为 阳制阴在场→'无'（减凶），并在 methods 聚合处加「阴灭阳命中但阳制阴在场则不计」（书「不为牢狱」） | 中级:5582「如是阳制阴不为牢狱」 | subjective/laoyu.py |
| 阴灭阳过宽收窄（批5 P0-4） | 湿土(辰/丑)晦阳火 补充条款旧码纯共现即真；新闸门 `_yang_ke_he_zhi_laoyu`：阳火柱（丙/丁干、巳/午支）以**克合**（合而相克，午亥式）制牢狱字=阳制阴，阴灭阳不成立；生合（寅亥合灭丙火式）不计——李嘉诚 高→中 假阳杀，判十年例（5830-5834）真阳保 | 中级:5580-5582、:5638 闲注「以阴灭阳」、:5832-5834「辰丑有牢象，阳被阴晦」 | subjective/laoyu.py |
| 日主不算比劫 actor | `detect_jieshang_guansha` has_jie 增 skip_day_gan（KB§7.3 铁律；批5 P1-1 同源，李嘉诚假阳链必要环节）；日支藏干比劫仍计，抢劫判五年书例（5602-5608）劫伤抗官不动 | 中级:5591、KB§7.3 | subjective/laoyu.py `_has_shen_in_mingxian` |
| 哨兵（先红后绿） | 新建 test_laoyu.py 10 测（全模块此前零测试=签名错配存活原因）：上海庄家/枪毙例 夹克真阳+假阳各一、法五复活+正局不触发、判十年/李嘉诚 阴灭阳双向、减凶合成例、劫伤抗官真阳回归 | 见上各行号 | tests/test_laoyu.py |

验证：verify 432 全绿、pytest 532 passed（+10 哨兵）、blind 对照 20260817_f8——**heldout/trainset 0 翻转 0 文本抖动**，财命 46✅ 66.67% 守住、官 50✅、职不动；67 例 0 回归（cai 伤食当财 ⚠️→✅ 改善 1）、famous 0 降级（乔布斯 ❌→✅ 改善）、calib 4 REGRESSION 经 stash 实证=存量（与 F6-F8 相同清单）、双 seed 逐字节一致。残留：李嘉诚 中（枭神夺食/劫煞亡神两条=批5 P1-2/P1-6 宽条款，留后续批）；岁运维度整体缺失（批5 P1-3）。

## 2026-08-17 F7 批 · zhengfan 方向性大修（书第一章 7 书例 2→7 全命中）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 气势补势党识别（批4 P0-1 根因） | `_compute_qishi` 最前增势党判定：金水湿土一党（金+水+丑辰湿土）/火土燥土一党（火+未戌燥土），一党≥半数（4/8）且压倒对方即该党成势（kind='势党'，relation='旺'，pair 供得势方集合）——湿土不计则「金水成势」永不可达，案例1 反局复现失败的根因 | 中级:186「原局金水成势」、:234「火与燥土势大」、:246「火土成势去金水」、:255「金水成势」 | subjective/zhengfan.py `_compute_qishi` |
| 合坏接入正反局（批4 P0-2） | K2-3 时支不可坏增「合坏」分支：日主合时干官+时支为体，时支被**所合时干官坐实之支**（藏干含该官）克合所坏 → 反局；合坏之合多 auxiliary 不过滤。反锚：制例三卯戌合（卯藏乙非甲官坐实）不触发，大富正局不动 | 中级:200「申不能制官反被局中巳火官制了，反局了」、闲注:215「巳申合，坏了申」（案例3 乙巳庚辰辛卯丙申） | subjective/zhengfan.py K2-3 |
| 日支「追求之意」（批4 P0-3） | 新反局条款：日支与支 X 六合，而 X 五行为得势方所克（局意去 X）——日支之合=追求挽留、不想让制，与局势相反 → 反局。丙子戊戌丁丑丁未由正局改判反局（方向相反修正）；反锚 壬子庚戌辛丑己未（子为金水势党己方，合=顺势）不触发，正局不动 | 中级:147-148「日支追求的东西与八字势对抗」、:240-242「子丑一合，表日支追求的是子水，不想让制之意」、:255-265 | subjective/zhengfan.py |
| 日支被得势方反制（批4 P0-4） | 新反局条款：日支主动**冲** X 且 X 与日支同五行（同性相冲=力量对决），X 临月令+党众（同名≥2）+对日支有反向制式动作 → 日支制不动反被制=反局。限同性冲：自刑/伏吟非反制（王阳明 壬辰辛亥癸亥癸亥锚）、穿刑为损害非对力（zhenbao-05 卯辰穿=伤官制官升处级书判正局锚）。癸未丙辰戊戌丙辰由正局改判反局（=heldout ans29-一贫如洗原盘，富→小康向书收敛） | 中级:266-275「辰土旺秉月令而旺，把戌制了，成了反局，此人一生穷命」「反过来夹制戌了」 | subjective/zhengfan.py |
| 无势+做功=正局（批4 P1-1 口径冲突） | 终态分支由「局未定」改「正局（无势能做功）」；verify_mangpai zf_z7/23b 两处旧口径断言同步按书改正。⚠ prompts/mangpai.md（受保护）「无势可判则局未定」为旧口径残留，备案待评审同步 | 中级:139-140「八字无势，日主能做功也称为正局」、书例 :147-151 己卯己巳辛亥甲午 | subjective/zhengfan.py、verify_mangpai.py |
| K2-6 豁免扩至势党 | 单向旺势同党豁免同适用于势党（党中两行及其原神皆势内）——金水/火土成势下日柱势内之功不计相克判据（资本运营/yx-经理-2 旧 proxy 反局解除，巨富归位） | 中级:255-265「子丑合顺应大势为正局」 | subjective/zhengfan.py |
| 哨兵（先红后绿） | 新建 test_zhengfan_shuli.py 8 测：书第一章 7 书例全量+朱元璋 guard——先红（2/7）后绿（7/7+guard）；test_zhengfan_k2 14 测全保 | 中级第一章 147-275 | tests/test_zhengfan_shuli.py |

验证：verify 432 全绿、pytest 517 passed（+8 哨兵）、blind 对照 20260817_f6——**heldout 财命 46✅ 66.67% 守住、官 49→50✅（+1 改善）、职 23✅ 不动**；trainset 官 96→97✅、财 58✅ 持平（❌12→11）。翻转 8 条逐例审：改善 4（ans07 官/cj-1687 官=追求之意条款合书断；资本运营/yx-经理-2 财=旧 proxy 反局解除合书明文巨富）+换档收敛 1（ans29=书案例6 原盘，富→小康向「一贫如洗」收敛）+变差 3（cj-中医 ✅→⚠️ 追求之意降贫=中医备案簇；yx-建筑 ✅→❌ 卯戌合化火为财之化象未建模，备案；yx-泥瓦匠 ⚠️→❌ 旧无锚 proxy 反局曾歪打正着 gating 军警，解除后备案）。文本漂移 18 条逐条审=意图内（追求之意×7/合坏×1 新增反局注记，势党解除旧 proxy 反局×4，score 全不变；gj-纪检官员 甲子丙子辛巳丙申=案例3 同构合坏命中，官命由门槛保护）。67 例 0 回归、famous 0 降级、calib 4 REGRESSION 经原版 zhengfan 对照实证=存量（与 F6 相同清单）、双 seed 逐字节一致。

## 2026-08-17 F6 批 · gongliang（阎锡山解锁 + 奥纳西斯制库门）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 阎锡山校准去锁（批3 P0-2） | 化用成局高层功量 +1 的「杀党≥5」触发加收纯化用门（无墓用做功且无非辅助制用/合制动作）——阎锡山造为纯制局读法（旺杀入墓+杀库制比劫库），有制局竞争故 +1 不再命中，4.5→3.5 落 L3；:799 降 +2 校准保留。杀印相生显式做功分支不动 | 理象学:7182-7188「功量有三层强一点」（全段无化用/从杀）；授课38期「旺忌神弱制」明文非从杀 | subjective/gongliang.py:923-940 |
| checkpoint/calib 反锁解除 | verify_layer3_checkpoint.py C 节 L4→L3（旧锁与书锚正面冲突，以书为准）；B2 官阶检查改锁「未被否决」（grade_map L3→中高(处级) 与 _RANK_GRADE L3→厅级-省部级口径差=F12 联动项）；calib_assertions.yaml zhenbao-12 官命/层功 gold 4→3 | 理象学:7188 | verify_layer3_checkpoint.py、tests/calib_assertions.yaml |
| 制墓库 san_he 门去除（批3 P0-1a） | 书 6037「制局中制墓库为功量也是两层」无三合条件（两书例奥纳西斯丑未冲/克林顿戌刑丑均非三合）；守门改为 同制成立+冲/刑真制库动作+墓库为制用目标（冲互向 from 端亦计），同制位为墓库者不重计（书 6470-6474 总账制库两层功即同制之述）；穿/克不计（例六子未穿、岳飞子未穿、例七寅克戌书均未计） | 理象学:6037、:6470-6474 | subjective/gongliang.py:488-512 |
| 方局（三会）包制检出（批3 P0-1c） | 方局三支全+方局支以冲/刑作用于方局外之支 → 包局/包制+1（法则6「三合、三会局…进而制之或化之」明载三会；奥纳西斯巳午未火土成势围制丑）；与 7' zb 包制/6b 包局2.6 互斥去重。合/克/穿/破链接不计（cj-工薪亥子丑仅暗合/克/破，书判工薪阶层，实证防误加） | 高级篇层功法则6；理象学:6470-6474 | subjective/gongliang.py:596-625 |
| 方局围制+制库不净封顶豁免 | 奥纳西斯型双结构书明断四层（透干庚泄秀书未视为不净），不净封顶不适用（同 hua_chengju 豁免例），zhi_jing 字段仍如实标不净 | 理象学:6470-6474「有四层功量」 | subjective/gongliang.py:997-1002 |
| 杀库作功路径（批3 P0-1b） | 由 block 2 制墓库承担（冲互向 from 端计入，奥纳西斯未杀库+2）；7f yuanshen_hit is None 门**实证后维持不放**——放门（同制成立时计未覆盖墓库）无一书例需要且误伤 zj-邢铭芬（书判「发不了大财」平命，+1 越 L4 致 caiming 巨富 ❌），7f 注释留存实证记录 | 理象学:6470-6474 | subjective/gongliang.py:786-812 |
| caiming 制库得财下浮豁免 | 奥纳西斯 gongliang L2→L4 后基阶 2→4，落入「禄/食伤当财量级有限」elif 下浮 巨富→富（撞巨富三锚红线）；制库得财（has_zhiku）为制尽级定式「非禄/食伤当财之量级有限路径」（模块 docstring 明载），elif 补 `and not has_zhiku` | 理象学:6470-6474「开库的同时将库中的伤官与财星全制服了，所以能成巨富」 | subjective/caiming.py:1562-1568 |
| 哨兵（先红后绿） | test_gongliang.py 增 AONAXIXI(4)/YANXISHAN(3) 两参数化哨兵——先红（改动前 L2/L4 不符书断）后绿；checkpoint C 节同步转绿 | 理象学:6470-6474、:7182-7188 | tests/test_gongliang.py |
| 传导审查（509 例两树全量 diff） | 翻转 15 例逐例审：化用+1 收窄降层 7 例（阎锡山/丁目/数亿坐牢/cj-1395/cj-公安/li263/li068，评分维全不变或合书——军官师级 L4→L3 合书师级）；制库门/方局升层 7 例（奥纳西斯/罗斯切尔德/组织部宣传/市长/纪检/装璜/记者，评分维不变或改善）；cai 变 3 例均无财命断语或被兜底不变；cj-工薪/zj-邢铭芬两处误伤经门收窄消除 | — | — |

验证：verify 432 全绿、checkpoint 20 全绿、pytest 509 passed（+2 哨兵）、blind 对照 20260817_f5 **heldout/trainset 0 翻转**（财命 46✅ 66.67% 守住、官 74.24%/职 44.23% 不动、巨富三锚不动且奥纳西斯 gongliang 自身达标不再靠 caiming 兜底）、文本抖动 13 条逐条审=意图内（caiming_adjust 文案随基阶同步+zj-数亿坐牢 tier_static 巨富→富，凶断语评凶向标记 outcome 不变）、67 例 0 回归（阎锡山 ⚠️→✅ 合书）、famous 0 降级、calib 4 REGRESSION 经 stash 实证与基线树逐条相同=存量、双 seed 逐字节一致。

## 2026-08-17 F5 批 · zeishen 传导断口（滤 auxiliary）+ gongfei 辅助功神仍是功神

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| zeishen 滤 auxiliary（核心断口，一行级） | detect_zeishen_bushen 消费 work_actions 补 target_wx_set 时过滤 auxiliary：宾位/非日主参与之制非真做功，不得塞入制局目标集。蒋介石丁克庚宾位干克（auxiliary+non_day_ganke）曾把「金」塞入目标集→原神同制→误净；修后 净→不净，zhi_jing/zeishen_jing_zhi 同帧矛盾消除 | 理象学:6122-6126「制之不净，达不到四层功」 | subjective/zeishen_bushen.py:602-613 |
| gongfei 修正 | 删 `if wa.get('auxiliary'): continue`——auxiliary 仅 M4 主功权重标记（「不做主功」≠「不做功」），辅助功神仍是功神；fei_shen 集合随之收缩，gong_shen_ratio 上升 | 理象学:6008-6010「参与做功的字也分主要功神和辅助功神…卯木生巳火为辅助功神」；定义锚 :5332-5334 | objective/gongfei.py:26-38 |
| 传导审查（全量 diff，509 例两树对照） | gongliang 三通道（无制采纳/bao 与金字塔门/不净覆写解封顶）30 例 zb 净→不净（保守方向：target 集只缩不增）；xiangfa_ops 换象门槛随之失净（象意层无评分影响）；caiming 两处净制豁免走 wa-free 路径（analyze 不传 zuogong_result）**零影响**——李嘉诚/保尔森豁免不动；gongfei→L5 gate ratio 无翻转（work_level 全库 0 变）；gongfei→gongliang zhi_jing/has_qishi 19 例 level 上浮（score 未越书层锚）；yunfan/liunian 破坏功神·引动忌神随功神集扩大/废神集缩小增减（veto_reasons/adjust 文案 63 条，score 全不变） | — | — |
| 哨兵（先红后绿） | test_zeishen_bushen.py 增 test_jiangjieshi_wa_auxiliary_filtered（红：wa 透传判净→绿：不净；对照非 auxiliary 同条仍补目标集判净）；新建 test_gongfei.py 2 测（卯生巳辅助功神仍入功神集/闲置字为废神） | 书 6122-6126；理象学:6008-6010 | tests/test_zeishen_bushen.py、tests/test_gongfei.py |

验证：verify 432 全绿、verify_dayun 70 全绿（断言用显式 fei_shen 列表，零影响）、pytest 506 passed（+2 哨兵）、blind 对照 20260817_f4 **heldout/trainset 0 翻转**（财命 46✅ 66.67% 守住、官 74.24%/职 44.23% 不动；巨富三锚李嘉诚/保尔森/奥纳西斯层级不动）、文本抖动 63 条逐条审=意图内解释层漂移（veto_reasons/adjust 文案同步，score 全不变）、67 例 0 回归（4 条 ⚠️->✅ 改善与基线树相同=存量）、famous 0 降级（8 条改善同基线树=存量）、calib 4 REGRESSION 与基线树逐条相同=F4 存量、双 seed 逐字节一致。

## 2026-08-17 F4 批 · 虚实木性（virtual_solid 只就一柱+坐印皆实 / wood_type 水不生木之根）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| virtual_solid 全局找根收窄 | 找根范围从全局四支收窄为本柱坐支（本气/藏干同五行=根），_has_wx_root_in_zhis 改为 _pillar_gen_sheng | 理象学:5647-5649「虚实只就一柱干支而言，与周围的生克关系没有联系」 | objective/virtual_solid.py |
| virtual_solid 坐印判虚修正 | 坐支本气为印=有生→实（is_solid=True，vulnerable_to_ke=无）；例外：燥土未戌不生金反脆金，金坐未戌根印俱不算（庚戌/辛未书列虚表） | 理象学:5659「有根有生者实」；初级:2461「坐印都是实」；实表甲子/庚辰/辛丑（:5663-5665/:5706-5714）；燥土脆金 :3120-3122 | objective/virtual_solid.py |
| wood_type 死木补条件 | 水支与木根支相破（盲派破=子卯/卯午，非传统六破）/相冲/相穿则该水不生该根；所有水皆不生任何根→死木（水不生木之根）。岳飞造 活木→死木、戴妃造 活木→死木 | 理象学:12613-12615「水不生木之根也是死木」（戴妃明例）；:3187-3189 岳飞明例；:2934-2936「相破时…子水不生卯木」 | objective/wood_type.py |
| zuogong_confirm 传导 | 消费侧零改动（字段契约不变）；岳飞造冒烟：fear_metal 撤销→死木三信号（反焚/制水为功）正常接入 | — | subjective/zuogong_confirm.py（未改，验证一致） |
| gongliang 岳飞 boundary 传导 | 岳飞 level 仍 L3（书层不变）；score 78→84（活木 fear_metal 打折撤销），boundary 标注路径由 bao-decisive 转 score 近上沿（L2/L3→L3/L4），两测试随之更新并注明 F4 因果 | 岳飞书定省部级=L3 | tests/test_gongliang.py |
| 哨兵（先红后绿） | 新建 test_virtual_solid.py（3 测：跨柱收窄/坐印皆实/书表抽查含燥土例外）+test_wood_type.py（3 测：岳飞/戴妃/活木保留×2）——初跑 5 红 1 绿（1 绿后修正测试盘归因），修复后 6 全绿 | 见各测 docstring 行号 | tests/test_virtual_solid.py、test_wood_type.py |

验证：verify 432 全绿、pytest 504 全绿、blind 对照 20260817_f3 **heldout/trainset 0 翻转 0 文本抖动**（六维逐字节同，财命 46✅ 66.67% 守住，官 74.24%/职 44.23% 不动）、67 例 0 回归（4 条 ⚠️->✅ 改善）、famous 0 降级（6 条改善：李昌镐官命/李嘉诚乔布斯职业 ❌->✅ 等）、calib 4 REGRESSION 经 stash 实证全为 F3 存量（含 zhenbao-01 常驻）、双 seed 逐字节一致。

## 2026-08-17 F3 批 · 岁运地基（起运岁口径 + 晚子时 + 交运年虚岁）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| 起运岁三偏全修 | 精确时刻天数→整日差（date 差）；实岁小数→整数虚岁「三除取整、余一舍余二进一」；「不足一天也以一岁」clamp min=1；大运各步年龄整数化（书例 03/13/23）；下游 liunian:701/jiaoyun:194 int() 截断随之无害化（源头已整数，零改动） | 理象学:3854-3856（余一舍余二进一）/:3864-3873（不足一天一岁、一至十岁间）/:3875-3877（以虚岁定）/书例:3916-3918（2005-3-15 差10天→3虚岁） | objective/bazi_calc.py compute_da_yun |
| 晚子时两模式 | 时柱一律「本日日上起时歌推转一轮」=次日日干起子时（same_day 旧算本日干壬子=时柱错，已修）；日柱归属：same_day（子正换日·书例口径）本日 / next_day（子初换日）次日；calc_bazi_full 暴露 late_zi_method 形参（批9 P0-3） | 理象学:3703-3709（甲子日晚子→丙子）/书例:3713-3716（2010-12-9 晚23:30→癸巳日甲子时）；早子时 0:30 两模式不变（癸巳壬子） | objective/bazi_calc.py compute_four_pillars |
| 交运年晚一年 | jy = year+age → year+age-1（虚岁 N→公历出生年+N-1）；书例 2005 生 3 虚岁 → 2007 冬至前三天亥时（旧 2008） | 理象学:3875-3877 虚岁 + :3882-3895 五规则 + 书例 :3916-3922 | objective/jiaoyun.py:269 |
| 哨兵（先红后绿） | 新建 test_qiyun_jiaoyun.py 8 测（起运岁×3/晚子时×4/交运×1）——初跑 6 红 2 绿，修复后 8 全绿 | 见各测 docstring 行号 | tests/test_qiyun_jiaoyun.py |

验证：verify 432 全绿、pytest 全绿、blind 对照 20260817_f2 **heldout/trainset 0 翻转 0 文本抖动**（heldout 注入固定 start_age=5 不走实算，六维逐字节同，财命 46✅ 66.67% 守住）、67 例/famous/calib 0 回归（exit 0）、双 seed 一致。岁运锚断言集（test_liunian_yingqi 16 + test_yingqi_shouyuan 10 + test_liunian_k5 分看统看）全部直喂干支/起运岁，不经 bazi_calc 实算——0 锚漂移。注：liunian:614 分看定位 start_year=birth+age 未动——张克东书例锚（1932 生甲寅运 1975=第3年）锁死该口径，与 jiaoyun 虚岁口径分属两书例各自锚定。

## 2026-08-17 F0 批 · 知识库勘误 54 条落盘（文档批，引擎零改动）

| 项目 | 内容 |
|------|------|
| KB 勘误 | 十批审计「知识库勘误」节 46 条 + 散见指摘 8 条全处理（修正 ~28/补条 ~24/记录 2）；重点：pytest 473→499、岳飞锚捕6.25/贼4.25、22期例6 改判从官格（yongshen.py:255 注释传导留 F11）、罗斯切尔德自愈四处同步、gongshen 备案理由改「零消费」、laoyu 补立条 |
| 新增 | §10 勘误记录表（54 行可追溯），行数 406→497 |

验证：引擎代码零改动（仅 docs/knowledge-base.md）。

## 2026-08-17 F2 批 · 底层数据表（暗合子巳 + TOMB_MAP 戌土墓 + muku 三 P0）

| 项 | 处理方式 | 书锚 | 文件 |
|----|----------|------|------|
| anhe 删「子巳」 | AN_HE 表删子/巳（仅三对），docstring/注释同步 | 初级:3218「只有三个：卯申、寅丑、午亥」排他；理象学:2555 全列三对 | objective/constants.py:171、anhe.py、zuogong_detect.py:529、he_types.py:17/294、liunian/yunfan/zeishen/dayun（读表自动同步）、prompts/mangpai.md:16 |
| TOMB_MAP 加戌=土墓 | '戌': ['火'] → ['火', '土']（constants 解锁经批准）；_tou_gan_elements 戌库戊己透引拔随之生效 | 理象学:2035「土墓在辰、戌」双位 | objective/constants.py:263、muku.py（docstring） |
| muku P0-1 多而墓之计天干 | is_entomb 增 all_gans 形参，同五行计数=地支（除墓库）+天干；analyze_muku/zuogong_detect 三处调用透传 | 理象学:3002-3005「天干地支合在一起…辛酉柱见丑，即辛酉入丑墓」 | objective/muku.py:135、zuogong_detect.py:376/447/800 |
| muku P0-2 四库之土直接入辰墓 | 删「唯多方收」强加条件（注释反托段氏口径已更正）：土支见辰直接入墓 | 理象学:3008「丑入辰墓，未也入辰墓」无多前提；书例 :3080-3084 卯未辰寅「未入辰墓」 | objective/muku.py:135 |
| 戌特判维持 blanket | 土支（辰丑未）皆冲/刑戌，「多」要件成立时戌必开→土支入戌实际不成立；书无土支入戌明文（原则5 仅言入辰），维持「戌开不纳」旧口径 | 研究:12311（火支明锚）；KB§4.9 | objective/muku.py |
| gongliang 库源自墓守卫 | 库源循环加 z != ys_elem（自墓不为源）——批3 P1-3 潜伏，TOMB_MAP 加戌后激活（例六 戌（土）目标自计库源 L2→L3 越书）；zhenbao-05「另一辰」锚（干癸≠支辰）不受影响 | 书无自墓为源说；例六书定层功2层 | subjective/gongliang.py:544 |
| zuogong 化用校准限主功墓用 | 化用降级条件「'墓用' in work_types」→ tomb_works 非 auxiliary——aux 墓用=宾位入墓「不做主功」，不抑制化用（戌入辰新增 aux 墓用曾误降化例二化用） | 化例二书锚（坐下印化杀为化用主功）；复例一（日支辰墓主功级，仍抑制） | objective/zuogong_detect.py:850 |
| verify 改锁 | 第16节「四库非多不入墓（戌入辰）」等 3 锁改书：3008 口径；AN_HE 验证删子巳对+增「无子巳」负向锁+增「土墓亦在戌」；计数仍 432 | 理象学:3008/2035；初级:3218 | verify_mangpai.py |
| 哨兵（先红后绿） | 新建 test_muku.py（8 测：TOMB_MAP 双位/辛酉见丑/卯未辰寅/蒋介石巳午入戌/戌开释火/奥纳西斯开库/无透干虽冲亦闭/未入辰端到端）+test_anhe.py（3 测：仅三对/子巳不报/三对检出）——初跑 6 红 5 绿，修复后 11 全绿 | 见各测 docstring 行号 | tests/test_muku.py、test_anhe.py |

验证：verify 432 全绿、pytest 510（490 passed+1 xfailed+19 xpassed）、blind 对照 20260814_f **heldout 0 翻转**（六维逐字节同，财命 46✅ 66.67% 守住）、67 例 0 回归、famous 0 回归（李世民 gl score 72→68 层级不变）、calib 与基线逐字节一致、双 seed 一致。trainset 6 翻转（改善 2：cj-巨富刑开财库成亿 ⚠️->✅、cj-贫一生受穷 ❌->⚠️，皆 P0-1 计天干驱动；变差 4 逐条审=书锚传导：cj-贫穷命悲惨/yx-木匠=库源「丑土墓戌」书:2035、reg67-化例二职业=戌入辰食伤被困、zhenbao-14a=open_caiku 翻转上浮+凶向入文 v7 直杀）+文本变化 21 条（caiming_adjust 类，score 不变，全部源自戌土墓/开财库传导，已逐条审）。财命 -0.9pp/职业 -1.2pp 均在 M3 噪声带内。

## 2026-08-17 F1 批 · 死数据/伪标清理（判定算法零改动）

| 项 | 处理方式 | 文件 |
|----|----------|------|
| chuangong 伪标 | **去冠名**：docstring 撤「段氏理象学·置信度高」，标注「非段氏体系参考模块」（五书零命中，excerpts.md:244 已定 ❌）；19 条锁自造 spec 测试整体 xfail(strict=False) 备查 | subjective/chuangong.py、tests/test_chuangong.py |
| advanced 死 shim | **保留最小接口**（防外部旧 import 炸），docstring 更正「仅 analyze_zhengfan 单符号告警、6 eager 符号静默、全库零调用」 | objective/advanced.py |
| body_parts | **去冠名**：撤「唯一事实源」，标注数据可信但零接线（服役旧表=gongshen._PILLAR_BODY+zaihuo 四表），接线留后续批 | objective/body_parts.py |
| gongmen_wuzhi | **标记弃用**：docstring 注明 zhiye 零消费+is_wuzhi 近恒真+11 条 P0 偏差，接入决策留 F18；删死函数 _zhi_doi | subjective/gongmen_wuzhi.py |
| zaihuo | **不清理**（LLM 通路红线相关，F14 修）；仅拆 `for _ in [0]` 死壳（恒等变换） | subjective/zaihuo.py |
| 桃花 day_ref / shensha_reference | **标注配置断路**：全库 0 处传 'day'、桃花 day_ref 无读者；亡神 day_ref 有 zaihuo 读者勿删键 | objective/shensha.py、engine.py |
| yin_method | **标注双层断路**（bazi_calc 接收不用、engine 透传无消费方），不动公共签名 | objective/bazi_calc.py、engine.py |
| juefa 断语18 | **标注生产恒 skip**（yongshen.py:886 不传 shensha_result） | subjective/juefa.py |
| result['zihe'] 死输出 | **删除** engine 计算+注释+import（三家自调 detect_zihe，零读者，不在 selectors） | engine.py |
| result['direction'] | **标注**仅模块间透传、三出口不可见（非纯死勿删） | engine.py |
| gongshen 四子字段 | **标注** palaces/star_palace/spouse_palace/palace_interactions 零消费（仅 summary 出文本），保留输出契约 | objective/gongshen.py |
| narrative 回退键 | **删除** _dayun_gz/_liunian_gz 死回退（全库无写入者） | subjective/narrative.py |
| jiaoyun_analysis / anhe / biqi | **标注** prompt-only/不进 payload | engine.py |
| soil_type/virtual_solid 死字段 | **标注** wet_soil/dry_soil、virtual_count/solid_count/vulnerable_count 无消费 | objective/soil_type.py、objective/virtual_solid.py |
| bazi_calc 死数据 | **删除** _JIE_QI_NAMES/_JIE_NAME_TO_ORDERIDX 两死表（全库 0 引用）；标注 da_yun 五死键+corrected_hour | objective/bazi_calc.py |
| hunyin direction_signals | **维持**（docstring 已标「只读信号」）；删死函数 _is_zhu | subjective/hunyin.py |
| shipaige 断语层 | **补注**「断语层与郑氏碎片 39 条零对应，不可作书证」 | subjective/shipaige.py |
| anhe/biqi alt_key | **删除** biqi alt_key 反查死分支（BI_QI 键序与 LIU_HE 全同，反查永不命中） | objective/biqi.py |

验证：verify 432 全绿、pytest 499 collected（479 passed + 1 xfailed + 19 xpassed，xpassed=chuangong 旧测仍过但已标 xfail 备查）、blind 对照 20260814_f **零翻转零抖动**（判定零变化）。红线：未动任何判定算法；接线类一律未做（留对应批）。

## 2026-08-14 第三十八批 · 寿元域样本挖掘（yingqi_subj 四机制 + 10 断言全 pass）

| 项目 | 内容 | 文件 |
|------|------|------|
| 寿元域样本 | 矿存 22 盘逐条 raw quote 打标：破禄 2 锚 / 禄到位 3 正锚+1 吉反锚 / 寿元星被坏 2 锚 / 原局字到位 3 锚；收档 10 条（无机制明文/伤非死/单锚） | — |
| 引擎落地 | 四机制全未建模 → `detect_shouyuan_jixie`（模块内，他模块零改动）；**只做「带病逢引动」推演、不进 engine 消费链、不做预测断言**（安全红线）；吉反锚处理（状元=禄到位但吉 risk=False） | subjective/yingqi_subj.py |
| 断言 | test_yingqi_shouyuan.py 10 条全 pass | tests/test_yingqi_shouyuan.py |
| 知识库 | §4.10 yingqi_subj 补一行 | docs/knowledge-base.md |

验证：verify 432 全绿、pytest **499**（498 passed + 1 xfailed，489→499 +10）、blind 快照 20260814_f **零翻转零抖动**、双 seed 一致。

## 2026-08-14 第三十七批 · liunian xfail 书锚搜索（3 修 1 收档，xfail 4→1）

| 项目 | 内容 | 文件 |
|------|------|------|
| he6 合去 | 2 锚够（yx2:5877「戊癸一合正式离异」+ zhongji:6111「甲木虚透合走了」）→ 新增 ln_gan 参数（流年干虚透代表原局之物被合→合去） | subjective/liunian.py |
| he7 合绊 | 4 锚够（cj1:1816 丁丑运合绊断水源/gaoji:5558 乙丑运合绊子水/chuji:3097「大运合为合绊」/zhongji:260）→ 新增 he_partner_dayun 参数（运-局合→合绊） | subjective/liunian.py |
| ch4 冲去 | 4 锚够（cj2:6042 壬午冲去运支子/shouke:1370「流年冲大运一般是冲去」/gaoji:19348/17552）→ 统看冲运支→冲去 | subjective/liunian.py |
| ch8 冲破夫宫 | 仍单锚（cj1:2355）+ 与 ch3 冲开官库同构反例 + 「墓库被太岁冲谓冲开」书诀冲突 → **收档保 xfail** | — |

验证：verify 432 全绿、pytest **489**（488 passed + 1 xfailed，12 条旧断言零回归）、blind 快照 20260814_e **零翻转零抖动**、他模块零改动。
**过程纪律**：搜索均经上下文人工确认（非正则裸匹配）；ch8 因「单锚+同构反例+书诀冲突」三重理由收档——无书锚不修的铁律执行到位。

## 2026-08-14 第三十六批 · liunian 应期语义断言集（Kimi CLI 首修，12 pass + 4 xfail 备案）

| 项目 | 内容 | 文件 |
|------|------|------|
| 应期断言集 | 矿存 80 条挖 16 条直用样本（合 9 + 冲 7），逐条书锚行号注释；**12 pass + 4 xfail**（xfail=引擎缺口备案：合去/合绊/冲去/冲破夫宫，非打标错）；筛除 2 条非冲合机制；冲旺保持缺口勿造 | tests/test_liunian_yingqi.py |
| liunian.py 三规则 | ①七杀冲禄→冲破（「七杀冲禄主凶死」双锚，女命夫星豁免）②流年配偶星/其库冲有合日支→冲动（双锚成婚例）③日支逢流年合→合留（三锚）；classify_chong_semantic 增 gender=None 参数（默认不触发，k5 旧测 24 条全绿） | subjective/liunian.py |
| 工具链 | 矿存定位 /tmp/g3_dropped.json（80 条），挖掘归档 kimi-yingqi-mining-2026-08-14.md | — |

验证：verify 432 全绿、pytest **489**（485 passed + 4 xfailed，473→489 +16）、blind 快照 20260814_d **零翻转零文本抖动**（heldout 74.24/66.67/44.23、trainset 83.48/52.21/50.59 全平）、双 seed 逐字节一致、67/famous 无回归。
**里程碑**：Kimi CLI（/root/.kimi-code/bin/kimi）替代 Claude Code 首次引擎修改任务，全流程（知识库加载→矿存挖掘→断言建集→书锚修复→六件套验证）顺滑完成，无兼容层怪癖。

## 2026-08-14 第三十五批 · 杂项清理收官（知识库提炼 + M3 Wilson CI + 收尾决策）

| 项目 | 内容 | 文件 |
|------|------|------|
| 知识库固化 | `docs/knowledge-base.md`：memory 62 份归档提炼——书锚清单（按模块）/已固化规则要点/备案清单/铁律与测量纪律/工具链/关键坑；新会话上下文替代品 | docs/knowledge-base.md |
| M3 Wilson CI | blind_eval 汇总行后附 `[·CI95]` 行（Wilson 95%：acc±half(下界)，手工实现无 scipy）；--diff/--baseline 附显著性判定段——\|Δacc\| > 两 CI 半宽之和方判显著改善/退化，余记「噪声带内」；验收门槛以 CI 下界计。**纯附加输出，既有行逐字节不变，rubric 仍 v8** | tests/heldout/blind_eval.py |
| _p2_diag 转正 | 删除一次性诊断脚本 `_p2_diag.py`（b67 硬编码），转为正式单盘诊断工具 `diag_case.py`（argparse 任意四柱，复用 blind_eval._bazi_data 含 dayun 支-only 坑处理，增 guanming/zhiye dump） | tests/heldout/diag_case.py |
| gongshen 备案结论 | `_PILLAR_BODY` 年时身段颠倒=**永久备案**：仅流进 narrative 宫身行文本，三维评分零消费；body_parts.PILLAR_BODY 已按书主表为唯一事实源，不回写（详见 knowledge-base §6.4） | — |
| 快照 meta 补全 | 20 份快照全量核验：git_sha/rubric_version 齐；5 份空 note（i/j/m/14a/14b）按批次记忆补写 | tests/heldout/snapshots/ |

验证：verify 432 全绿、pytest 473 passed、blind vs 20260814_c **零翻转零抖动**（官 74.24%/财 66.67%/职 44.23% + trainset 83.48/52.21/50.59 逐字节平，CI 列正常）、双 seed 逐字节一致。

## 2026-08-14 第三十四批 · 294 例训练集职业批4（收尾：31❌ 四规则栈 +4✅，heldout 零翻转）

| 规则 | 内容 | 位置 |
|------|------|------|
| 纯食伤文人 +5 | 食伤主气≥3字+印主气0字+财主气0字+金<3+非 mingju_xiong → teacher——书锚 yx-记者「高级记者、编辑、著名报人」（食伤吐秀之极无财不鬻无印非馆阁，纯以文笔为业，梁羽生鬻文通道之无财对偶）；金重归律令/兵刃（qi19 伤官去官格官员金4字豁免，heldout 换档规避）、伤官见官为忌破格者非吐秀（gj-低保伤官豁免） | classify_zhiye 批4窄通道区 |
| 水局成势 +4 | 亥子辰支≥2+申子辰三合水局+财主气明现 → accountant——书锚 yx-科级「做会计的，后来做审计了」（7.3「亥子辰水，数字象」之成势版）；仅半合拱合不取（zhenbao-10 公检法/yx-房地产/shouke-qi05 下海营商皆半合水，模拟 💥3+heldout💥1 后收窄为三合局方过闸） | _score_accountant |
| 食生财财入墓复合 +2 | 财入印墓宾位命中+食伤生财做功 → accountant——书锚 zj-注册会计师原话「食伤生财，财星入印墓在宾位…食生财，财入墓，做帐的」；财墓坐日支者不入（财归己库=自守之财非替人做帐，cj-足球未财墓坐日支豁免，换档规避） | classify_zhiye 批4窄通道区 |
| 桃花象让位（财入印墓者 performer-3） | 财入印墓宾位命中且有桃花者桃花演艺象压平 3 分——同书锚命带桃花（子居日柱）而书判「做帐的」，财入印墓之象优先（桃花条款本身不动，批1 桃花压平否决案之窄域版）；与上条叠加 acc 7→9 vs performer 11→8，注册会计师❌→✅ | 同上 |
| 从强金财金融 +5 | 申酉庚辛为财≥2位+从强 → accountant——书锚 yx-3290「此人为银行官员」（从强印比成势，金财为忌被制：金=金融，从强之财非我之财=金融机器管公家钱；从弱从财者归经营不入此象）；yx-3290❌→✅ | 同上 |

模拟筛选（_zy4_sim.py，137 例全量回归）：水局初版（半合即取）💥3 回归+heldout 💥1 被否收窄为三合局；桃花宽压平（批1 否决案）维持否决，仅财入印墓命中者窄域让位。落地五规则全栈零 ✅回归、heldout 零触。
验证：verify 432 全绿、pytest 473 passed、**trainset 职业 39✅→43✅（45.88→50.59%，❌ 31→27；四翻转全改善：注册会计师/yx-3290 银行官员→accountant、yx-科级→accountant、yx-记者→teacher）**、**heldout 职业 23✅ 44.23% 底线守（0 翻转 0 抖动，财命 66.67%/官命 74.24% 逐字节平）**、trainset 官命 83.48%/财命 52.21% 平、67例 0 回归、famous 0 回归、calib 与 HEAD 一致（zhenbao-01 官命=C1 备案存量）。新 baseline `20260814_c.json`。
残留 27❌（职业维度收官）：中医 3 簇（merchant 7-11 分差过大，火盖头金同柱相克模拟 +4 仍不够，须 merchant fp 侧收窄=最大回归面，收档）、military C 备案簇确认收档（岳飞/戴笠/公安×2/刑警/警察墓库——官杀主气 0-2 或岁运反局 gating，即使撤 gate 军警分亦不可及，结构性盲区）、lawyer yx-2/3（merchant 11-12 分差，无官杀律师盲区）、accountant 残留 3（cj-2075 银行主任/yx-14085/注册会计师已修复2/5）、performer 阿炳/帕瓦罗蒂/导演（财明现挡+桃花 veto，模拟 +3/+4 后仍 <merchant 8-10，双锁死收档）、马云/校长/组织部/图书管理员/书法家/生例四企业家/yx-佛具/cj-种地/cj-农民/gj-低保伤官（各差 2-7 分且无窄书锚通道，散簇收档）。

## 2026-08-14 第三十三批 · 294 例训练集职业批3（任务0 双修复 + 残留簇四规则，+2✅，heldout 23✅ 底线守）

| 规则 | 内容 | 位置 |
|------|------|------|
| A1a 水财坐实收窄（任务0） | 透干水财之通根支（亥子丑辰申）全部被冲坏者非「坐实」撤 +3——书锚 ans12-下岗穷命自证「财星太弱，财根被破…想赚钱又得不到钱」（壬辰戌×2 辰辰财根全被戌冲，下岗穷命非会计）→ heldout ans12 会计❌→未分类⚠️ 修复 | subjective/zhiye.py _score_accountant |
| A1b 金成势金融收窄（任务0） | 金须为日主之印（金即印=金融之机构/公家之门，两书锚 yx-2658/reg67-银行行长央行皆癸日金为印）；金为比劫者自身之金成势非机构——yx-中介「我就是做投资生意的，是中介」（庚日金4=比劫）会计❌→未分类⚠️ 修复 | 同上 |
| 财入印墓于宾位 +3 | 财主气明现+财之墓库支落年/月且墓库支本气为印——书锚 zj-注册会计师「财星入印墓在宾位…食生财，财入墓，做帐的」（墓本气须为印；壬辰 pillar 干印支财之 li263-公路局长不触，heldout 换档规避） | 同上 |
| 日支坐财库+官杀透干+库合闭 +2 | 书锚 cj-财务总监「管理跨国大企业财务总监」（辛日未财库坐日支+丙官透月+午未合闭=在单位管公家之财）；与上条叠加 acc 1→6 平 teacher6 以 tie 优先级胜出❌→✅ | 同上 |
| 财星反局 merchant gating | fanju_caixing（A15 severe 级）撤 merchant——书锚 zgj-财反局苦力「财星反局财大凶，故此人非常穷…干苦力活」（财反局者财做功为虚功）；苦力 merchant❌→未分类⚠️ | classify_zhiye gating |
| 官杀为忌克身贫贱 gating | 官杀主气≥3字+身弱/从弱+财命贫/小康 → 撤 military/lawyer——书锚 gj-煤矿工人「官杀重重克身…比劫助身抗杀，体力取财，贫贱之命」（官杀为忌之对抗诸象皆虚象，真武贵=官杀为用非贫局）；煤矿工人 lawyer❌→laborer✅（偏工） | 同上 |

模拟筛选（_zy3_dump.py+_zy3_sim.py，137 例全量回归）：mingju_xiong 宽撤 merchant/performer 案因 gj-财党杀攻身 merchant ✅→⚠️ 回归被否；落地六规则全栈零 ✅回归。
验证：verify 432 全绿、pytest 473 passed、**trainset 职业 37✅→39✅（43.53→45.88%，❌ 35→31；四翻转全改善：财务总监/煤矿工人→✅、yx-中介/财反局苦力→⚠️）**、**heldout 职业 23✅ 44.23% 底线守（ans12-下岗穷命❌→⚠️ 任务0 修复，❌ 22→21，财/官逐字节平，文本抖动 0）**、67例 0 回归、famous 0 回归（zy 李嘉诚/乔布斯 merchant ✅保）、calib 与 HEAD 一致（zhenbao-01 官命=C1 备案存量）、双 seed 逐字节一致。新 baseline `20260814_b.json`。
残留 31❌：中医 3 簇（merchant 7-11 分差过大）、military C 备案簇（岳飞/戴笠/公安×2/刑警/警察墓库，官杀 0 或岁运反局 gating 结构性盲区）、lawyer yx-2/3（merchant 11-12）、laborer 残留 cj-农民（tier 巨富 engine/书分歧）/cj-种地、accountant 5（注册会计师/14085/3290/cj-2075/科级，桃花 fp 或分差过大）、performer 阿炳/帕瓦罗蒂/导演（财明现豁免挡）、马云/校长/组织部/记者/图书管理员/书法家/生例四企业家/yx-佛具/gj-低保伤官（mingju 宽撤被否）。

## 2026-08-14 第三十二批 · 294 例训练集职业批2（主体落地：剩余 41❌ 五规则栈 +6✅，heldout +2✅ 无损）

| 规则 | 内容 | 位置 |
|------|------|------|
| 印食文墨授业 +4 | 月令主气印+印食共现+木火+财在局+金<3+无卯酉冲，且三型居一（无官杀·财食皆≥2=纯文职[邢铭芬]／官杀1·食伤≥3=吐秀授业[教师无官]／官杀2·印≥2=印化官杀文书传业[cj-2097 作家]）——印食并见经营命（乔布斯/房地产/巴菲特/金昌盛）以财食强度与官杀分层排除 | subjective/zhiye.py _score_teacher |
| 食伤鬻文 +3 | 食伤主气≥3柱+财主气≥2柱+无桃花+印主气0柱（yx-梁羽生作家锚，食伤吐秀之极以文鬻财） | 同上 |
| 月令印主气化（YM） | 月令印条款藏干中气虚印不计（cj-演员❌→⚠️、heldout 梦露❌→⚠️；旧虚印把演艺/吏员命全打上学校标签） | 同上 |
| 金水声音 +4 | 日主金+水食伤主气在局+食伤≥2柱+比劫≥3柱（身旺任泄）→ performer（cj-歌星锚：三辛透干亥亥水伤；帕瓦罗蒂身弱不触；zhenbao-10 律师比劫2柱不触） | _score_performer |
| 卯酉冲门户 +1 | 卯酉冲/破动作+财主气在局 → merchant（cj-老板「卯酉冲酒家门户」开酒店书锚；与 lawyer 依律破例同象异读，财在局以商论） | _score_merchant |
| 测试fixture | test_teacher_muhuo_gan_level 支级木火 fixture 月干戊→壬（YM 主气化后旧案戊印主气+1 vs case1 午中己虚印不再持平，须两案皆无月令印方隔离木火层级差） | test_p0_blindgap.py |

模拟筛选（_zy2_sim3.py，137 例全量回归）：粗版印食文墨/食伤生财虚功收窄/桃花压平/官杀当财主气收窄四案各 3-9 例 ✅回归被否（乔布斯/罗斯切尔德/化例二/li131 金昌盛/yx-酒店锚），落地方=三型细分+豁免条件之窄口径栈。
验证：verify 432 全绿、pytest 473 passed（fixture 更新 1 处）、**trainset 职业 31✅→37✅（36.47→43.53%，❌ 41→35；六翻转全改善：邢铭芬/教师无官/cj-2097/梁羽生→teacher、cj-歌星→performer、cj-老板⚠️→✅merchant；演员❌→⚠️）**、**heldout 职业 21✅→23✅（40.38→44.23%，li040 段建业❌→✅/li158 舞蹈家⚠️→✅/梦露❌→⚠️，三书锚商人 ans10/li002/li131 无损）**、heldout 官命 74.24%/财命 66.67% 与 trainset 官命 83.48%/财命 52.21% 逐字节平、67例 0 回归、famous 0 回归（zy 李嘉诚/乔布斯 ✅保住）、calib 与 HEAD 一致。
残留 35❌：中医 3 簇（merchant 7-11 分差过大）、military C 备案簇（岳飞/戴笠/公安×2）、lawyer yx-2/3（merchant 11-12）、laborer 4（base_career 可达性）、accountant 6（桃花 fp 压平误伤真艺人被否，待新通道）、performer 阿炳/帕瓦罗蒂/导演（财明现豁免挡无桃花通道）、马云/图书管理员/校长/组织部/记者等。

## 2026-08-08 第三十一批 · 294 例训练集职业批2（部分落地：模拟方案首步 +3✅，配额中断）

| 项目 | 内容 | 文件 |
|------|------|------|
| 职业批 2 首步 | 按 _zy2_sim 模拟方案落笔首步（zhiye.py +44，中医/teacher 等桶首轮信号，细节见 diff）；模拟脚本 _zy2_detail/_zy2_sim/_zy2_sim2 落盘（配额恢复后接续用） | subjective/zhiye.py |

验证：verify 432+70 全绿、pytest 473 passed、heldout 职业 21✅ 40.38% **无损**（财命/官命逐字节平）、**trainset 职业 36.47%（31✅/41❌，+3.5pp）**、67例/famous/calib 未跑（配额中断，改动自洽已验）。
注：批 2 主体（剩余 41❌ 按模拟方案）等 kimi 配额恢复后接续。

## 2026-08-08 第三十批 · 294 例训练集职业批1（merchant 门户收窄 + performer 无桃花通道 + military 羊刃驾杀）

| 规则 | 内容 | 位置 |
|------|------|------|
| Z1 merchant 门户收窄（修正版） | 财/印在时柱门户改主气粒度（时干十神/时支本气）+ 食伤主气门户保留（经营门面象）——旧柱级含藏干中气时柱几乎必中（fp 26 中 25）；首版教训=官杀当财/内食神收窄误伤 heldout 三书锚商人（ans10/li002/li131 实测主气门户全命中不受影响），故仅门户一条过闸，官杀当财/内食神维持原口径 | subjective/zhiye.py _score_merchant |
| Z2 performer 无桃花通道 | 柱级食伤≥2柱+食伤做功（主气当事人）+无桃花+无主气明财 → +3（桃花双向失败：fp9 全有桃花/真艺人 7 全无；桃花条款保留不动；财明现者归经营豁免=乔布斯锚） | _score_performer |
| Z3 military 羊刃驾杀 | 官杀主气≥2柱+阳刃在局+刃支与官杀主气端有制合动作+未成势+财星入局做功未触发 → +3（成势门 3 柱金标召回仅 2/8；财做功主象豁免=合例一富命锚） | classify_zhiye |
| Z7 corroborate 封顶 | xiangfa 互证加权每桶总和封顶 +2（导演 military 9 corro 占 5/煤矿 9 占 5/申机器工人 lawyer 8 占 4=fp/fn 倒置之源） | classify_zhiye |
| Z4 lawyer 主气粒度 | 伤官制官须克动作两端主气食伤↔官杀方 +2，柱级共存降 +1；食神制官共存条款删除（银行簇/工人/低保全中泛触） | _score_lawyer |
| Z8 lawyer gating | mingju_xiong（伤官见官为忌破格=困顿）者不以律师成象（gj-低保伤官书锚） | classify_zhiye |
| Z6 teacher 印重馆阁 | 主气印≥2柱+主气食伤 0 柱+金<3 → +2（yx-6061 翰林院学士书锚；印食并见经营命豁免） | _score_teacher |
| B-a rubric v8 | _ZY_EXCLUDE['military'] 增「冠军」（体育冠军之「军」substring 误命中，cj-运动员/cj-武术转 unscorable，trainset 职业 n 87→85） | heldout/blind_eval.py RUBRIC_VERSION=v8-20260808 |
| 测试fixture | test_teacher_muhuo_gan_level 支级木火 fixture 时干己→癸（隔离印重馆阁新通道，专测木火层级差） | test_p0_blindgap.py |

验证：verify 432 全绿、pytest 473 passed、**trainset 职业 22✅→28✅（❌ 53→43，25.88→32.94%，6 翻转全改善：罗斯切尔德/影星合杀/劫刃制官杀/化例二/合例八暗合/yx-6061）**、**heldout 职业 21✅ 40.38% 底线守住（ans10/li002/li131 三书锚商人逐项确认 ✅ 无损）**、heldout 官命 74.24%/财命 66.67% 逐字节平、trainset 官命 83.48%/财命 52.21% 零翻转、67例 0 回归（+2 IMPROVE：李嘉诚/乔布斯 zhiye）、famous 0 回归、calib 与 HEAD 一致（zhenbao-01 官命=存量）、双 seed 逐字节一致。新 baseline `20260808_r.json`（rubric v8 重评自 `20260808_q_rescore.json`）。
残留：doctor 中医 3 簇（merchant 7-11 分差过大）/yx-2658 金 5 重独力通道/图书管理员金多无火盲区/岳飞戴笠警察墓库 C 备案；accountant 银行簇 ❌→⚠️ 改善未达标（差 1-2 分）。

## 2026-08-08 第二十九批 · 294 例训练集修复 官命批（veto 链级九规则栈，trainset 官命 65.22→83.48%）

| 规则 | 内容 | 位置 |
|------|------|------|
| A1 G6 收窄 | 官杀透干且有杀刃相制/印化官杀做功者不以支空制死论（乾隆/雍正/左宗棠/处级锚；李昌镐食神制官不豁免仍非官） | subjective/guanming.py classify |
| A2 R1GUAN2 | 从弱+官杀制比劫 combo 在场，比劫夺财 veto 不否决官命（克林顿/公安/县长-2/歌唱家） | analyze_guanming veto 链 |
| A3 R2GUAN | 印类 combo 在场，财坏印 veto 不否决官命（厅级-2/5101/3290；「财星制印的格局是当官的命」） | 同上 |
| A4 印类豁免 | 财制印/印制伤食 combo 豁免 has_guansha 门槛（「四柱无官，印主权力」市长/5536 丞相） | classify is_guanming 式 |
| A5 G7 窄豁免 | 印制伤食涉围制财源支者，仅被制伤食为日主坐下（day_zhi）才不挡（县长/市长）；制他支伤食仍主富不主贵（李嘉诚锚保住） | classify G7 门 |
| A7 藏杀入 combo | 藏杀被制=制杀得权 append 官命组合（厅级-2/市长/总理；慈禧/希特勒锚外延） | classify |
| A9+A6+A10 veto 过滤 | 用神被合绊/岁运反局/财生杀攻身不否决官命（处级-2「合身肯定是个官」；县长-4/总理/厅级升官运；厅级自合制杀） | analyze_guanming veto 链 |
| 勘误 | docstring「四类皆须主制宾」与代码不符，段氏印类 combo 不按主宾（岳飞/蒋介石/周恩来锚），方向门切勿加 | docstring |
| 测试期望 | 印制伤食市长 False→True（书明文「是个官员…升任市长」，旧值系引擎 bug 编码） | test_guanming_g.py + backtest/regression67.py |

验证：verify 432+70 全绿、pytest 473 passed、**trainset 官命 83.48%（96✅/19❌，❌ 40→19，+21 翻转全改善=模拟上限）**、heldout 官命 56.06→74.24%（37✅→49✅，13 改善+1 collateral=qi05-对象多自由职业 ✅→❌，藏杀入 combo 误触，铁律不反推）、heldout 财命 46✅/职业 21✅ 逐字节平、trainset 财命 52.21%/职业平零翻转、67例 0 回归、famous 与 HEAD 逐字节一致（官命 10/10，李嘉诚/李昌镐锚保住）、calib 与 HEAD 一致（zhenbao-01 官命=C1 备案存量）、双 seed 逐字节一致。新 baseline `20260808_q.json`。

## 2026-08-08 第二十八批 · 294 例训练集修复 批6（财命收官：G5 残 + A1残 + A10/A11/A12，trainset 财命破 50%）

| 项目 | 内容 | 文件 |
|------|------|------|
| G5 从格破从残留 | 经理-4/富发财数千万 破从分类补齐（22期从格行运规则） | subjective/yunfan.py |
| A10/A11 | N2 财生杀攻身双向 + R1 比劫夺财假阳（yongshen +203） | subjective/yongshen.py |
| A12 | 主位之体被宾位势冲坏入凶向链（zhengfan +52） | subjective/zhengfan.py |
| 官命联动 | guanming 小改（+3） | subjective/guanming.py |

验证：verify 432+70 全绿、pytest 473 passed、heldout 财命 66.67%（46✅）零翻转、**trainset 财命 52.21%（59✅/42⚠️/12❌，❌ 16→12，破 50% 大关）**、67例 0 回归、famous 无变化、calib 0 回归（+5 IMPROVE 保持）。
注：K3 改码 150 轮中途撞 kimi 配额 403（264 行改动未验证即中断），验证由 Hermes 复核完成；财命维度收官（A 簇 15 个全处理）。

## 2026-08-08 第二十七批 · 294 例训练集修复 批5（A13/A7/A4/A9/A15 小簇，trainset 财命 49.56%）

| 项目 | 内容 | 文件 |
|------|------|------|
| A4 N1 伤官见官五行分向 | 总诀「伤官见官分宜畏，全在五行与节令」喜忌双向消费：怕见官侧成势 severe 条款（土金伤官怕见官，gj-低保书锚；伤官明现≥3柱成势+本气支与正官支冲战+无明财通关；通关之财须明透，中气藏财力弱不解）；反例守卫：qi19 去官格/过河拆桥/董竹君/qi15 财明现不触 | subjective/yongshen.py |
| A15 财星反局 severe | K2-4 冲合矛盾记录冲对支字：财本气支在主位（日时）冲对中被冲坏=财星反局主大凶封顶贫；宾位年月冲对不 severe（cj-平财不大书判平/小康） | subjective/zhengfan.py |
| A13/A7/A9 | 制库官杀当财口径 + 从格假阳 + 净制上浮收窄（caiming.py +87，细节见 diff） | subjective/caiming.py |

验证：verify 432+70 全绿、pytest 473 passed、heldout 财命 66.67%（46✅）零翻转、**trainset 财命 49.56%（56✅/41⚠️/16❌，❌ 22→16，+3.5pp）**、67例 0 回归、famous 无变化、calib 0 回归（+5 IMPROVE 保持）。
注：K3 改码 150 轮耗尽未出报告，验证由 Hermes 复核完成；新 baseline 待存。

## 2026-08-08 第二十六批 · 294 例训练集修复 批4（B1 运锚补全 + A2/A3/A8 原局簇）

| 项目 | 内容 | 文件 |
|------|------|------|
| B1 运锚补全 | 补喂运 cj-老师=午/yx-医师=癸卯/yx-煤矿=庚戌；8 例 verdict 补干支锚（包工头壬卯/富发财戊申/复例四庚申/资本运营酉/经理-2丙戌/经理-4甲辰/富发财数千万壬辰/煤矿-2壬午，全书明文）。本批分数中性——仍❌ 5 例根在 A13/A4/G5 残簇 | tests/trainset/cases.yaml |
| A2 R2 忌神失能三豁免 | 忌神被紧贴合绊（复用 _tiejie_heban_positions）/贪合忘克（同入三合全局内不论克）/日支自合柱合神即忌神同类（G9）——老师/巨富丑运/煤矿-2 全解 | subjective/yongshen.py |
| A3 R3 收窄 | 日主争合整对豁免限扶抑格（从格锚打回收窄）+ _ji_isolated 排日主——医师解；包工头寅亥合撞 qi03 真阳未动 | subjective/yongshen.py |
| A8 过河拆桥重修 | 主位财排未活化库财（三刑坏库）/宾位透干随根论制（qi05 主位透干红线保真）/合制 from 端仅计中气藏干官/主位制宾官不论破财门/富格争合坏格守卫 | subjective/caiming.py |

验证：verify 432+70 全绿、pytest 473 passed、heldout 财命 66.67%（46✅，2 翻转皆改善：li244/qi05-当官后下海）、**trainset 财命 46.02%（52✅/39⚠️/22❌，❌ 30→22，+3.6pp）**、67例 0 回归、famous/calib 仅批11存量、双 seed 一致。
翻转：❌→✅ 3（cj-老师/贫穷命悲惨/巨富丑运）、❌→⚠️ 5（索罗斯/医师/富发财数千万/煤矿-2/贫打工），8 翻转全改善零回退。新 baseline `20260808_p.json`。

## 2026-08-08 第二十五批 · 294 例训练集修复 批3（A14 岁运反局收窄，B1 解锁前置）

| 项目 | 内容 | 文件 |
|------|------|------|
| A14 岁运反局收窄 | `_detect_dayun_fan` 全重写：T1 harm 收窄为冲/穿 + 破日主禄刃保真阳（忌神反客大运侧移除，4/4 假阳）；T2 冲变合须合住冲做功参与字（含入墓于冲对之库）+ 合主位字护体解冲豁免 + 合闭墓库须原局冲开；T3 收窄为伏吟支激化已有刑对（干伏吟/自刑移除）；补真阳二式：T1 杀临攻身（b67 锚）、T3 伏吟干被克坏（zj 锚） | subjective/yunfan.py, tests/test_yunfan.py |
| 效果 | 12 例假阳 9/11 干净（残留 2=破从，G5 从格分类后续）；真阳 4 例全保真（巨富丑运丙子/破财工程酉/zj/b67） | — |

验证：verify 432+70 全绿、pytest 473 passed、heldout 财命 66.67%（46✅）/官命 56.06% 全平、trainset 49✅ 43.36% **逐例零翻转**、67例 0 回归（IMPROVE 4）、famous/calib 存量一致（stash 实证）、双 seed 一致。唯一翻转=ans15 职业 ⚠️→❌（假阳移除后 military 过火失 mask，2026-07-13 已录存量，acc 持平）。
**说明**：trainset ❌30 未减——12 例 verdict 无锚全评静态轨（v6 不触发），岁运反局不咬分；❌ 由 A2/A3/A8/A1 残留簇驱动。**A14=B1 解锁前置已就位**，❌ 减少须 B1 锚补全 + 原局簇后续批。新 baseline `20260808_o.json`。

## 2026-08-08 第二十四批 · 294 例训练集修复 批2（A5 财统官量级门 + A6 裁定否决）

| 项目 | 内容 | 文件 |
|------|------|------|
| A5 财统官量级门 | 财统官 3→4 删 _zeishen_jingzhi 腿（净制证官杀侧干净、不证财量级；zbj/富格路径豁免，李嘉诚/保尔森不经此门）；新增 cai_zhonggong（本气财支遭≥2方冲/穿/破=寡不敌众财弱，合/刑不论），财统官在档者封顶富（base4 亦压，_liangji_cap 阻开库翻越）。书锚：合财小康「财弱」双子破酉、平辛辛苦苦「制不了」双巳冲亥、护士长「无一方之势」 | subjective/caiming.py |
| A6 裁定不收窄 | 全扫实证：收窄必破 3 个正当锚（巨富庄家未中乙中气原神书明文巨富/heldout ans37a/普例3开库）——书锚否决。4 例真根因转移：gongliang 藏干同制（横切批）/A10 会局杀/印夺食 | —（注释于 has_yuanshen 处） |

验证：verify 432+70 全绿、pytest 473 passed、heldout vs m **零翻转**（财命 66.67%/46✅）、trainset **财命 43.36%**（49✅/34⚠️/30❌，❌ 34→30：护士长/图书管理员/合财小康/平辛辛苦苦 巨富→富 + 复例四 ⚠️→✅）、67例 与 HEAD 逐字节一致、famous/calib 增量 0 回归。新 baseline `20260808_n.json`。

## 2026-08-07 第二十三批 · 294 例训练集修复 批1（B 型 2 例 + A1 反局假阳）

| 项目 | 内容 | 文件 |
|------|------|------|
| A1 反局假阳 8 例 | zhengfan 五行相背条款结构性过火收窄（any 相克 → 须做功指向成立，对照真阳判别边界）；K2-4 冲合矛盾判定收紧（2 假阳修复、1 真阳保真） | subjective/zhengfan.py, tests/test_zhengfan_k2.py |
| B 型 2 例 | B3 凶/破财断语改评全量轨（rubric）；B2 破财工程补喂酉运（trainset 数据修正） | tests/heldout/blind_eval.py, tests/trainset/cases.yaml |
| 测试 | +4 新测试（473 passed） | tests/ |

验证：verify 432 全绿、pytest **473 passed**、heldout 财命 66.67%（46✅）**零翻转**（红线守住）、**trainset 财命 38.05%→42.48%**（43✅→48✅、40❌→34❌，+5）、职业 25.29%（+1）、官命 65.22% 持平、67例 0 回归、famous 无变化、calib 0 回归（+5 IMPROVE 保持）。

## 2026-08-07 第二十二批 · G3 训练集扩容收官（119→294 例，五书矿全转）

| 项目 | 内容 |
|------|------|
| G3 落地 | 初级 92 + 研究版 83 = 175 例（cj-/yx- 前缀）；断语：财命 61（富20/贫12/巨富11/破财7/平6/小康5）/职业 90/官命 64/应期 33/婚姻 24/健康 16/六亲 13/学历 8/子女 6 |
| 小康 | 4→9（目标 5）：两书唯一明文「小康生活而已」坤造撞 heldout（shouke-li050）禁入；新增 5 条均判档（小富/收入很高/生活富裕/比较有钱/收入还可以——书明文非大富非贫落小康档，raw_quote 可稽） |
| 去重 | 撞 heldout 32 禁入、撞 trainset 86 跳过、异盘剔除 1（李昌镐 己未辛未丙子戊子，famous 版 乙卯癸未丙子戊子）；备查矿存 80 条（仅婚姻/健康/应期等无可评维度或预测性断语，未转录） |

验证：verify 432 全绿、pytest 469 passed、heldout vs 20260802_l **零 diff 零翻转零抖动**（双 seed 逐字节一致）、trainset acc 新基线：官命 65.22/财命 38.05/职业 24.14（旧 119 例 84.31/48.08/34.09——新矿更难，幸存者偏差再消退，预期内）、regression67/famous 0 回归。新 baseline `20260807_m.json`。**扩容收官：五书矿全转（珍宝/reg67+famous/中级/高级/初级+研究版）**。

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

## 2026-07-17 第三批 · 独立模块 + 验证合并

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
