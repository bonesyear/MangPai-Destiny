# 盲派命理引擎知识库（knowledge-base）

> **用途**：新会话（任何 CLI，含 Kimi code）读本文件即获得 2026-07 ~ 2026-08 全部攻坚历史的关键结论，
> 替代逐次会话上下文。来源 = `~/.claude/projects/-root-metaphysics/memory/` 62 份归档的提炼。
> 最后更新：2026-08-14（杂项清理批）。引擎当前 HEAD 基线 = `snapshots/20260814_c.json`。

---

## 0. 速览（TL;DR）

- **项目**：段建业盲派命理引擎（Python3，无重型依赖；`yaml` 必备，`sxtwl` 用于节气，`anthropic` 软依赖仅叙事层）。
- **分层铁律**：`foundation/`（学派中性）← `mangpai/objective/`（纯检测）← `mangpai/subjective/`（解释判断）← `mangpai/engine.py`（编排），**单向依赖不可破坏**。
- **受保护勿改**：`subjective/schools.py`、`subjective/prompts/`、`objective/constants.py` 的数据表。
- **同音陷阱**：`gongfei.py`（功神/废神，`classify_gongshen`）与 `gongshen.py`（宫身，`analyze_gongshen`）同音异义**刻意共存**，勿合并勿改名。
- **数据**：heldout 215 例（`mangpai/tests/heldout/cases.yaml`，⚠️ 只评估不反推）/ trainset 294 例（`mangpai/tests/trainset/cases.yaml`）。
- **当前成绩**（blind_eval rubric v8）：

| 维度 | trainset 294 | heldout 215 |
|---|---|---|
| 官命 | 96✅/19❌ = **83.48%** (n=115) | 49✅ = **74.24%** (n=66) |
| 财命 | 59✅ = **52.21%** (n=113) | 46✅/15⚠️/8❌ = **66.67%** (n=69) |
| 职业 | 43✅/15⚠️/27❌ = **50.59%** (n=85) | 23✅ = **44.23%** (n=52) |

- **验证口径**：`verify_mangpai.py` 432 项 + `pytest mangpai/tests/` 473 + blind_eval 快照零翻转 + 双 seed 逐字节一致（旧 853 口径 2026-07-17 起作废）。
- **三维攻坚已收官**（2026-08-14 职业批4）。残留❌全数收档备案（见 §6），后续批次须先读本文件 §5/§6 防重复踩坑。

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
  subjective/ 25 模块：zuogong_confirm(analyze_zuogong+assess_work_level)/zhengfan/
    gongliang(1-4层功量)/zeishen_bushen/yongshen(方向层R1-R3+N1-N3+classify_strength)/
    caiming/guanming/zhiye/hunyin/xueli/laoyu/liuqin/zaihuo/gongmen_wuzhi/xiangfa_ops
    (换象/局象/化象/借象操作层)/yunfan(岁运反局)/dayun/liunian/shipaige/juefa/
    chuangong/yingqi_subj/narrative/schools(保护)/prompts(保护)
  tests/
    heldout/   cases.yaml(215) blind_eval.py snapshots/ diag_case.py _*_diag/_*_sim(诊断考古)
    trainset/  cases.yaml(294)
    backtest/  regression67.py famous_cases.py famous_baseline.json regression_famous.py
    calib_assertions.py/.yaml  test_*.py(473 测)
  docs/        duan-books/(段氏五书+珍宝50期+授课教程原文txt) 各分析文档
  CHANGELOG.md           批次变更记录（第七批起有书写惯例）
docs/                    任务书(tasks/)、remaining-tasks 系列、本知识库
```

### 1.2 关键调用链

- `MangpaiEngine.compute_all()` → 各 subjective `analyze_*`；`result['gongshen']` 已接入但**不进** `_build_summary`（verify_dayun 文案断言约束）。
- 官命判定链：`classify_guanming_combo`（制用四类+生用化用，G0-G7/G9 门）→ `is_guanming_raw` → `analyze_guanming` veto 链（反局/岁运反局/牢狱/比劫夺财/过河拆桥/R2/R3/N1/N2/官杀入墓/主位体坏），门槛保护 `_has_positive_guanming`（**从强一律非正向**——贪财坐牢例锚；须有官杀有根/印化官杀/官禄格/印带官帽/官带财帽）。
- 财命双轨（P0-a）：`tier_static/summary_static/level_static`（原局轨，yunfan 不入链）+ `tier/summary`（含 yunsui_delta 全量轨）。**「凶向在档」强制标注仅写全量轨**——静态轨结构性不可见凶向，rubric 对破财/凶断语一律评全量轨（v7）。
- 职业：`classify_zhiye` 七桶打分（military/lawyer/teacher/doctor/accountant/merchant/performer + laborer/unemployed base_career），`_MIN_SCORE_THRESHOLD=6` 以下为「无明确职业倾向」fallback；同分按 tie_pri 序；base_career 以 caiming `tier_static` 贫/小康为闸（财命-职业硬绑定，已知缺陷 C4）。

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
- **M5 快照**：`heldout/snapshots/*.json` 入 git（.gitignore 例外），带 `_meta`（git_sha/rubric_version/note，加载剥离）。基线链：`…→20260808_q(官命批)→r(职批1,rubric v8 rescore)→20260814_a(职批2)→b(职批3)→c(职批4,当前)`。全 20 份快照 meta 完整（2026-08-14 核验，5 份空 note 已补）。
- **用法**：`python3 mangpai/tests/heldout/blind_eval.py --out snapshots/<批>.json --note "<验证状态>" --baseline snapshots/<上一批>.json`

### 2.3 评估纪律要点

- **trainset/heldout acc gap = 过拟合度量**；扩容后 trainset acc 必降（幸存者偏差消退），**不可与旧小样本基线比**（23→91→119→294 每次重设基线）。
- 当前 heldout 职业 44.23% < trainset 50.59%、heldout 财命 66.67% > trainset 52.21%——构成不同，只看集内趋势。
- 小样本噪声：n≈50-115 时 Wilson 半宽 ±9-13pp，个位数 ✅ 变动多在噪声带内——结论以 CI 下界+显著性判定为准。
- 模拟器（_zy*_sim/_gm_sim）只含 gold 可评例，**unscorable 例换档对 sim 失明**——落地后必须 blind_eval 全量 diff 兜底（职批4两处换档均靠此抓回归险）。
- famous/calib 出现 REGRESSION 先 stash 实证是否存量（罗斯切尔德 zy=批11 存量、zhenbao-01 官命=批13-15 存量，两条长期挂在回归清单上，**非新回归**）。
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

- 加分：原神用神同制+2（**须冲/克/穿实制佐证**，合族单独不支撑——PUTONG2 书锚；多候选偏好财/官杀为用神）；制墓库+2（须 san_he）；七杀当财+1（透干+与制局目标同根）；入墓+1；库源+1（须同制成立；**库源×入墓同源去重**——引出与收藏同一墓对相反读法不重计）；包局+1（须 san_he）；层层相制+1（克链≥2，冲链不计）；月令+0.5；连墓加层（月令入墓于已计源头之库+1，李嘉诚第4点）；金字塔门（zb 链长≥3+冲边≥2+zb 净 → 乾隆 L4）。
- 克链入墓惰性：已入墓元素出边不入链。
- 封顶：制不净→3 层（化用成局路径除外）；相生之功→封顶 1 层（**日干无功弃之不看**——日主自克非制）；相克之制→封顶 2 层。
- 7d 化用成局/从杀格：纯化用路径（yuanshen_hit is None）+杀印相生/杀≥5+日主从弱 → +3/+1 可达 L4（阎锡山）；不净封顶对化用成局路径豁免。
- 包制 distrust 有条件翻转：bao_zhi 检出+zb 净+非三合成局 → 采信围制+1（克林顿 L4/岳飞 L3）；净 override；`_bao_suppress_pocai`（围制下比劫=制财非夺财）。
- 带象+1/统+1 以「同制不成立方计」为门（跨书去重）；富贵贫贱四档定性 wealth_grade。
- `boundary` 字段（score 距层沿≤5 或 bao 翻转 decisive → 'Ln/Ln+1边界'），只标注不改 level。
- **判别器易错**：sha_wx 用 `WX_KE_ME`（克我=官杀）非 `WX_KE`（我克=财）。

### 4.3 贼神捕神 zeishen_bushen（objective 检测，subjective 聚合）

- 党势权重=透干2/本气2/中气1/余气0.5/原神0.5；party≥4 成势、≥6 太旺；净制=被制方孤立+制方成党成势；不成=捕≥6+贼孤立+捕/贼≥3 overkill。
- 五易错点：①合制仅取克合（生合不计——李嘉诚午未生合排除）；②主位做功优先（日柱为 doer）；③日主不算贼神原神；④包制内柱本气皆入制局目标集（原神同制→净）；⑤冲边优先于克边（冲为链骨）。
- `_zeishen_jingzhi` 是 caiming 三处净制豁免的共用判据（李嘉诚/保尔森巨富锚保命符）。

### 4.4 正反局 zhengfan + yunfan（岁运反局）

- 原局反局：K2-4 冲合矛盾/K2-5 合官位置（合年月官+官五行克日主不计日柱指向=反局豁免方向）、五行相背条款、K2-6 单向旺势豁免（li101 红线）。时支不可坏特判（己甲戌/辛丙申）。
- yunfan 大运三类型（批3 重写后口径）：T1 破坏功神 harm 仅{冲,穿}+例外运破日主禄/刃=破护体（阴阳逆转）；T2 冲变合须原局冲做功参与字，合主位字=护体解冲豁免；合闭墓库须原局有冲开该库之冲；T3 伏吟/三刑须伏吟支激化原局已有刑对（合解刑豁免、刑开库豁免），单字伏吟/自刑不即反局；新增 T1 杀临攻身（身弱非从+运支官杀五行+透干=虚杀逢根）、T3 伏吟干被克坏（非日主干伏吟+原局有干克之）。**忌神反客大运侧已移除**（判别集 4/4 假阳，流年侧引动忌神保留）。
- 大运/流年反局已并入 yunfan.py（fanju.py/suiyun_fanju.py 拆分未做，整合版即现行）。

### 4.5 方向层 yongshen（吉凶方向=准确率最大杠杆）

- `classify_strength`：身强/身弱/中和/从强/从弱；从格四规则=根被坏三式（双夹冲/邻支刑穿/合会化入异党——印生身不坏）+一方成势闸（异党单五行主气≥3；化势宽口径 selfc<conc 可用合局计数，两停仍主气）+从旺从禄三道闸；印根计本/中气、日主根计余气两套并存（22期例1/2 vs 例5）。
- R1 比劫夺财：功神=比劫制财且身强/从弱 → 凶；**day_gan 不作比劫 actor**（日主克财=我克者财）；severe=比劫≥2柱或 hits≥2。豁免族：R1a 财旺夺不动（财≥2）；R1b 功神合绊失能只取受害方（_LIUHE_VICTIMS：子丑两伤/卯戌戌/巳申申/辰酉辰/寅亥寅/午未未——辰酉合化反助不豁免教训）；R1c 从弱虚根/从化（功神干无本气根/支入财向三半合局）。
- R2 忌神制用神：身弱/从强→财坏印、身强/从弱→印夺食；忌神失能三豁免（紧贴合绊/贪合忘克三字全三合/日支自合柱合神为忌同类）；从格忌孤用众按主气计（中气藏干不计）。
- R3 用神被合绊：紧贴六合受害方+年月干五合互绊；忌神受绊不触发；冲/穿做功参与抑制；合化出喜用豁免（化气∈喜用且≠受害方本行）；**日主自合财（日支主气=财+合神为财，戊子/壬午型）不论绊**（G9 配套）；日主争合整对豁免限扶抑格（从格不论争合）。
- N1 伤官见官为忌：扶抑官为用+伤官明现+正官明现+非辅助实伤；豁免=伤官去官格（官为忌）/伤官诀五类/伤官配印（第三方纯印位）/财星通关。
- N2 财生杀攻身：仅身弱+财明现≥2+七杀贴身（**非年柱**——年杀不论）+杀无制+印化无力，severity=normal（severe 曾误触留出集富命被否）。
- N3 官杀入墓限身弱（身强官用入墓属官运域）；杀忌入主位墓=制忌自消，宾位墓方论被关押。
- 聚合 `mingju_xiong`/`mingju_xiong_severe`；消费：caiming 封顶、guanming 否决（受正向结构门槛保护）、zhiye military gating。
- ⚠️ 扶抑用忌 vs 做功口径根本冲突（岳飞印制伤食仍中 R2 印夺食）——veto 修复一律走**消费侧域级过滤**（如官命 veto 链），不动检测器。

### 4.6 财命 caiming

- 财富看法：财星当财/禄神当财（八字无财时口径）/伤食当财/官杀当财两式（财统官/官统财，须 cai≥1 零财无可统）/制不尽当财/过河拆桥（富格 vs 破财分两键——ch14 与 caiming 同名相反两诀并存）；取财五法（经营/风险/智力/体力/工薪）。
- 基阶校准：校准一=有功 L1 基阶小康；校准二=财星当财+原神+主位财+经营法 基阶≥3 不落下富（两校准俱 `not ds_xiong` 门）。
- 上浮链收敛（层层设卡）：zhibujin 独力封顶富（净制豁免）；富格独力上浮封顶富+净制豁免；封顶 sticky `_liangji_cap`（开库不得翻越）；开财库+1 须财有原神；zbj 零财 guard；财源上浮 tier_idx<3（投资财至富，巨富须制级锚）；制库得财 opener 排自刑（辰辰伏吟非开库）；财统官 3→4 须原神 AND 主位财（净制腿已移除——净制证官杀干净不证财量级）；财众攻封顶富（本气财支被≥2 不同柱支冲/穿/破=寡不敌众，合/刑不论）。
- 过河拆桥判据五件：主位财排未活化库财（余气仍计）；`_is_zhi_jin` 宾位透干随根论制（主位透干仍计残存——qi05 红线）；合制 from 端仅计中气藏干官（he_both_ends 开关仅 _is_zhi_jin 用，zhibujin 用旧口径）；主位制宾官门（制不尽时主位制宾官=官杀当财做功不论破财）；富格两守卫（丑戌未三刑全=刑坏非开库；日主被≥2 同五行透干争合坏富格）。
- 官统财/财统官在 views 时跳过过河拆桥（防假破财）；primary 序=官统财/财统官 → 过河拆桥 → 财星/禄/伤食当财；「伴过河拆桥破财信号」仅破财型挂。
- G9 自合柱：非日柱激活自合柱干为财且合神与日主同五行 → 财来就我不论绊+视同合财做功；财源上浮与 G9 同源一事不二升 `_g9_up`。
- 从财格顺势档：财成局/有原神转化→基阶不落下富；伏吟单一（同名财支≥3）无转化→从财亦贫；从儿无财门控=明财限干透/支本气（中气不算）。
- 富屋贫人 gating：身弱+财≥2+无印 → merchant 压制。
- 中气藏干**算**原神（裁定不收窄——庄家未中乙/ans37a 寅中丙/普例3 三书锚）。

### 4.7 官命 guanming

- 组合：制用四类+生用化用+印化官杀+官禄格+印带官帽/官带财帽；G0 aux 不计；G1 劫刃制财归财命域（例外：比劫孤≤1+官≥2）；G2 杀刃须相当（1v1 即相当）；G3 官弱（<2）为用神被制不为官（伤官去官格食伤≥3 豁免=朱元璋锚）；G4 象法单独不立官；G5 杀刃类须杀有制化；从格豁免 G2/G3/G5。
- G6 官被制空亡硬否（日/年旬并参），**官杀透干+杀刃相制/印化官杀做功者豁免**（乾隆/雍正/左宗棠/处级——支上官被制空干上犹存）；官有墓在局=被收非制死（曾国藩豁免）。
- G7 围制财源支涉 combo 降出（主富不主贵——李嘉诚/保尔森锚）；印制伤食仅 to_pos==day_zhi（日主坐下伤食被印制=护官）窄豁免（归档全豁免案误伤李嘉诚被 famous 核验抓回）。
- G9 官合身=得官（「合身肯定是官」）；食合官支型未覆盖（A19 残留）。
- 批29 九规则栈（全在官命域消费侧，检测器零动）：A1 G6 透干豁免/A2 R1GUAN2（从弱+官杀制比劫在场免夺财 veto）/A3 R2GUAN（印类 combo 在场免财坏印 veto）/A4 印类 combo 豁免 has_guansha（「四柱无官印主权力」）/A5 G7 窄豁免/A7 藏杀被制 append combo（慈禧/希特勒外延）/A9+A6+A10 合绊/岁运反局/财生杀 veto 官命域移除。
- **方向门禁令**：印类 combo（财制印/印制伤食）不按主宾方向（岳飞/蒋介石/周恩来等 10 锚否决）——切勿加「主制宾」过滤，代码现状是对的。
- 杀印相生须过滤 auxiliary（G0 洞）；藏杀被制=制杀得权入 combo。

### 4.8 职业 zhiye（批1-4 规则栈，全窄条件）

- merchant：真实做功信号（财入局/主位合制财/食伤生财+2、财印门户/官杀当财被制/冲财+1，上限9）；时柱门户按**主气**粒度（食伤主气门户保留）；卯酉冲/破+财主气+1（酒家门户）；夺财动作不计经营；财反局 gating（fanju_caixing→merchant=0）。
- performer：桃花栈（食伤+桃花+财俱现+4/桃花居日柱+2 等）**一律不动**（刘晓庆/li154 靠其过阈）；无桃花通道=柱级食伤≥2+食伤做功+无桃花+无主气明财+3（乔布斯豁免闸）；金水声音+4（金日主+水食伤主气+食≥2柱+比劫≥3）；桃花让位-3（仅财入印墓宾位命中者）。
- military：官杀主气≥2+阳刃+刃支与官杀动作+未成势+财做功未触发+3（驾杀）；corro 每桶封顶+2；mingju_xiong gating；官杀为忌克身贫贱 gating（官杀主气≥3+身弱/从弱+tier 贫/小康 → 撤 military/lawyer）。
- lawyer：伤官制官须主气克动作+2/柱级共存+1；食神制官条款删；mingju_xiong lawyer gating（伤官见官为忌=困顿非律师）。
- teacher：木火通明（天干甲乙见丙丁+2/仅地支+1）；印重馆阁+2（主气印≥2+食伤0+金<3）；印食文墨授业+4（月令主气印+印食共现+木火+财主气≥1+金<3+无卯酉冲，三型居一：纯文职/吐秀授业/印化文书）；食伤鬻文+3（食主气≥3+财主气≥2+无桃花+印0）；纯食伤文人+5（食≥3+印0+财0+金<3+非 mingju_xiong）；月令印主气化（藏干中气虚印不计）。
- accountant：金成势金融须金为日主之印（+收窄庚日金4=比劫者）；财入印墓于宾位+3（**墓支本气为印**，干携带不算）；日支财库+官杀透干+库合闭+2；食生财财入墓复合+2（**财墓坐日支排除**——财归己库非替人做帐）；水局成势+4（亥子辰≥2+**申子辰三合局**+财主气——半合版被 sim 否决）；从强金财+5（金财≥2 位+从强）。
- 方法论铁律：**纯收窄≈0✅**（❌→⚠️ 不提 acc），收益主要来自 fn 侧窄条件 boost；每条收窄先过同桶 ✅ 集 margin 检验（margin≤1 经不起任何降分）；粗 uniform boost collateral 大（换错桶），落地须逐桶窄条件+全量回归 sim。

### 4.9 墓库 muku

- 刑与冲皆可开库（「不冲不刑是墓」），透干引拔对刑同适用（无透干虽刑亦闭）。
- 戌特判细化：**戌已开（辰戌冲/刑开）则火支不入戌墓；未开则走通用入墓**（四生入墓/多而入墓——蒋介石巳午入戌墓书锚）。勿删特判（反转戌入辰多而入墓测试），勿一刀切（两书矛盾）。
- 入墓=得到/控制/占有（做功语义）；开库=释放。changsheng 己墓戌 vs muku 己墓辰=中性层与盲派层未分离的已知分歧。

### 4.10 神煞 shensha / 象法 / 其他

- 神煞三层收口：核心5（禄/羊刃/墓库/驿马/空亡）+灾祸三煞（空亡/亡神/劫煞）+传统6 降级 traditional_shensha（5 vs 10 矛盾的最终答案，schools.py 开关待做）。亡神表与驿马**不同位**。
- 驿马=段氏三支皆马：每支映射所属局对冲三支（申子辰马在寅午戌…），首位=传统单点向后兼容；zaihuo 车祸 ma_count≥1 阈值因此近恒真（已知行为）。
- xiangfa_ops：换象（门槛=制尽，主从易位）/局象（包局/夹局/全阴全阳/专旺/寒暖燥湿，只做象意不加点）/化象补五行相生/借象借同五行副宫；muxiang tomb_relations dict 须 `_zhi_of` 解包（曾致 analyze_xiangfa_ops 整体崩被 try 吞掉）。
- juefa：伤官诀五类（金水喜见官/土金喜佩印怕见官/水木喜财官/木火喜见印/火土看组合）+断语22项；断语15/17/19 须传 yongshen_result 否则跳过（防过杀）。
- liunian：冲九语义（冲动/冲开/冲去/冲破/冲旺）+合四分（留/动/去/绊）；分看统看唯一机械触发=流年刑冲合运。
- yingqi_subj：大限∩大运∩流年三要素命中其二即 commit；`_classify_lu` 分日干/他干/外神（任何见禄都算 trigger，标签区分）。
- 宫位年龄=大限套（1-18/18-35/35-55/55+）已统一，GONG_WEI_XIANG 旧 1-15 套作废。
- body_parts=身体部位唯一事实源（干主外/支主内；宫位身段主表年腿足/时头面 + ch11 变体分键）。
- narrative 叙事层：郝金阳 5 模板 few-shot 三段式，软依赖 anthropic，失败降级返 prompt 文本；LLM temperature 与「敢下数字」无生成后校验（已知幻觉风险备案）。

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
| 岳飞 | 净（4.5/4.4 势均非不成）；无官杀之将（职业 C 备案） |
| 奥纳西斯（b67 制例一） | 制库得财（丑未冲 opener）巨富；gongliang 基阶锚 |
| 森田健（b67） | 同制须戌克亥实制佐证（亥卯半合生扶不担责）；身弱+透财得根+有原神+非成势 cap **否决锚** |
| PUTONG2 | 酉丑相拱+子丑合=相生之功非同制；「日干无功弃之不看」 |
| 源文14例 | gongliang 14/14 达书层（PUTONG2/乾隆 xfail 已解锁） |

### 5.2 财命

| 锚 | 要点 |
|---|---|
| qi14（辛戊甲甲/巳戌寅戌） | 身弱+财3 但「通根于寅成火土气势」→异党单五行≥3 成势豁免身弱 cap |
| b67 森田健 | 与 qi14 双锚夹击：任何身弱财旺 cap 不可落地 → ans12 永久必损 |
| ans12-下岗财会 | 局部最优实证：gongliang 任何降层反而更糟（真锁=caiming 富格 floor+开财库链）→永久必损 |
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
| 22期例4/5/6 | 从格根被坏三式；例6 破从（日主得根）；「比肩再多也无用」（qi22） |
| li191 | 「巳顺从酉势」从化；li141「没有转化缺乏连贯性」从财伏吟贫 |
| yx 双胞胎（戊申壬戌戊午 乙卯/甲寅时） | 书判贫/富，引擎曾完全倒置（A1+A9 对照组）；「戊喜见甲为财富」 |

### 5.3 官命

| 锚 | 要点 |
|---|---|
| 岳飞/蒋介石/周恩来/曾国藩/例6副省级/银行行长×2 等10例 | 非主制宾印类 combo 立官——**方向门否决锚群** |
| 李昌镐 | G6 正锚：「食神制官…官星被制空亡故不入仕途」（年柱旬空）；技艺立命 |
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
| cj-老板 | 卯酉冲=酒家门户 merchant+1 锚 |
| cj-歌星 | 金水声音（三辛+亥亥，身旺任泄） |
| yx-记者 | 纯食伤文人（食≥3 印0 财0）「高级记者、编辑、著名报人」 |
| 梁羽生 | 食伤鬻文（食≥3 财≥2 无桃花印0） |
| yx-6061 | 翰林院学士=印重馆阁锚（贫而贵，tier 贫→laborer 硬绑定缺陷 C4） |
| gj-煤矿工人 | 「官杀重重克身…体力取财，贫贱」=官杀克身 gating 锚 |
| zgj-财反局苦力 | 「财反局财大凶…干苦力活」=财反局 merchant gating 锚 |
| gj-低保伤官 | 「土金伤官怕见官…格局破败…低保」=mingju_xiong lawyer gating 锚 |
| 段氏体育冠军 | 冠军=比劫做功（非军）；歌厅小姐/歌女=食伤桃花无工作贱命（非演艺） |
| yx-酒店丁未/董竹君庚申 | 食伤主气门户保留锚（merchant 门户收窄时勿伤） |
| 乔布斯 | 印食并见经营命（teacher 通道豁免闸）；无主气明财（performer 无桃花通道闸） |
| zhenbao-10/qi15/ans07 | accountant/lawyer 收窄时的 ✅ 挡路锚（申酉金让位须更细条件） |

### 5.5 岁运/墓库/从格/神煞

- yunfan 五书锚（test_yunfan 锁定）：案例一（忌神反客不可复现已移除断言）/案例三（卯合申、申入丑墓）/案例四（丑未冲开库+子合丑闭）/案例五（乙伏吟被辛克坏=坏辰墓，zj 数亿坐牢乙酉运）/案例八/九。
- 真阳锚：yx-巨富丑运丙子运入狱（破刃+伏吟激刑）；yx-破财工程酉运（冲卯，书明文工程被强拆）；yx-煤矿戌运刑开丑库发财十几亿（刑开库豁免）；b67 复例二丙子运杀临攻身破财。
- 发财运非反局锚群（11 例）：复例四庚申/资本运营酉/包工头壬卯/富发财戊申/经理-2丙戌/经理-4甲辰/富发财数千万壬辰/煤矿-2壬午/老师午/医师卯/煤矿戌——**yunfan 三类型收紧后 9 干净，残留 2=破从（G5 分类）**。
- 驿马三支：`docs/duan-shi-lixiangxue-excerpts.md:149`。
- 阴阳同生同死沿用+火土同宫+弱长生（金长生巳=相克之长生）；盲派不站队阴阳干争议。
- 升官运被误杀锚（官命域已豁免）：县长-4 乙巳运/总理戊辰运/厅级戊戌运。

---

## 6. 备案清单（C 类结构性盲区 + 已知存量——**勿再立项重攻**）

### 6.1 职业残留 27❌（批4 收官收档）

- **中医 3 簇**（cj-中医/李阳波/yx-中医）：merchant 7-11 分差过大，火盖头金同柱相克模拟+4 仍不够；须 merchant fp 侧收窄=最大回归面（批1 警示 22✅ 中 merchant 占15）→收档。
- **军警 C 备案簇**：岳飞（官杀0）/戴笠（无官杀特务）/警察墓库（墓用库制库未实现）/公安×2/刑警——结构性盲区；岁运反局 gate 撤后军警分亦不可及。
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
- 缓行：A20 R1 身强侧豁免（真凶锚冲突）。

### 6.3 财命残留与必损

- **永久必损**：ans12-下岗财会（双锚夹击+局部最优）/li244（寿元章附述零财）/张克东/qi31。
- C 备案：yx-破财那几年（事件断语无干支锚）/cj-足球（书无层级明文）/cj-种地（语录体半C）/zgj-财反局苦力边界（A15 力度）。
- 弃修：ans32 vs zhenbao-14b 零和互拉；qi07 自刑开库（无排除书锚）；qi15 根治须 zuogong 层寅亥合绊优先级+caiming 财统官「财被合绊无统摄力」双改联动。
- 残留❌8（heldout）/22→（trainset 批4 后）主簇：A13 制库基阶/A4 伤官见官（土金伤官条款）/G5 破从残/A1 反局残/A12 体坏未入凶向链（独眼乞食）。

### 6.4 数据/工程备案

- **罗斯切尔德 zhiye**（merchant→teacher）：批11 merchant 召回存量换位，stash 实证与后续批无关——长期挂 famous REGRESSION 清单。
- **zhenbao-01 官命**：批13-15 存量，calib REGRESSION 清单常驻。
- **few-shot 交叉污染**：叙事模板第19期（qi19）/第25期（ans25）身在 heldout——prompts 受保护，备案不动。
- **gongshen 年时身段颠倒**：`gongshen._PILLAR_BODY` 年=头颈/时=腿足，与书三处主表（年腿足/时头面）颠倒。**2026-08-14 收尾结论=永久备案**：该字段仅流进 narrative 宫身行文本，三维评分零消费；`body_parts.PILLAR_BODY` 主表已按书收录为唯一事实源，gongshen 不回写（改它动核心判定链无收益）。未来若做健康/身体维度再按 body_parts 口径修。
- 宫位年龄两套已统一大限套；神煞 5 vs 10 已三层收口；过河拆桥同名两诀已分键并存——三大书内矛盾均已收口，勿再当缺口报。
- 阎锡山 L3（书）vs L4（郝金阳）双标准冲突——引擎取 L4，67例 baseline 已同步。
- 双胞胎盘（yx 贫富姐妹）引擎与书完全倒置=A1+A9 调试对照组，备案。
- dropped 59 例不回收（无断语/六合彩/时辰存疑）；备查矿 80 条（仅婚姻/健康/应期等断语）未转录，pipeline 在 /tmp 易失。
- 书源码共模偏差：断语=段氏自评，trainset/heldout 同源同偏见（评估一致性↑真理性存疑），知情即可。

---

## 7. 关键坑与工程教训（血泪清单）

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
13. **存量回归识别**：famous/calib 回归先 stash 实证（罗斯切尔德/zhenbao-01 两条常驻勿惊）。
14. **Edit 工具**：长块 old_string 易因全角标点/em-dash/箭头失配，拆小改+ASCII 锚点。
15. **被否决修法勿重试**：方向门（10 书锚）/mingju 宽撤 merchant/桃花压平/桃花宽让位/GZ 主气收窄/SSK fallback 收窄/纯强度 MAX 聚合/不成 capL2/克链≥3 提阈/库源自墓排除/身弱财旺 cap/中气原神收窄/mingju_xiong 宽撤——全部有书锚或 sim 否决记录（见各批记忆）。
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
| `python3 -m pytest mangpai/tests/ -q` | 473 测（含 test_property 64 属性化测试） |
| `mangpai/tests/heldout/blind_eval.py` | 三维盲测评估器：`--out 快照 --note 备注 --baseline 基线` 一条龙；`--diff A B` 对比；`--rescore` rubric 重评；输出含 M2 分组/M3 CI/显著性/文本抖动 |
| `mangpai/tests/heldout/diag_case.py` | 单盘诊断（原 _p2_diag 转正）：`python3 diag_case.py 乙己己庚 巳丑未午 [--gender 女 --dayun X --liunian Y]`，dump gongliang/caiming/guanming/zhiye 内部状态 |
| `mangpai/tests/heldout/_zy55_dump/_zy55_sim/_zy55_feat/_zy_all_dump/_zy_margin/_zy_master/_zy2_*/_zy3_*/_zy4_sim` | 职业批诊断考古（dump+条款网格模拟器，特征预计算模式可复用） |
| `_gm40_diag/_gm_all_dump/_gm_sim` | 官命批诊断考古（veto 翻转模拟） |
| `_a14_diag/_a1_*/_b5_diag` | 财命批诊断考古 |
| `mangpai/tests/backtest/regression67.py` / `regression_famous.py` | 67 书例回测 / 23 名人回测（famous_baseline.json 已 git add -f） |
| `mangpai/calib_zhenbao.py` + `tests/calib_assertions.*` | 郝金阳 10 例校准（zhenbao 系） |
| `mangpai/tests/heldout/{extract_cases,curate,build_yaml,verify_heldout}.py` | 案例管线（扩容批次复用模式；G3 提取 pipeline 在 /tmp 易失） |
| 记忆目录 `~/.claude/projects/-root-metaphysics/memory/` | 62 份批次归档（本文件=其提炼；细节回查原件） |

**标准验证六件套**（每批落地前必跑）：
```bash
python3 mangpai/verify_mangpai.py                 # 432 全绿
python3 -m pytest mangpai/tests/ -q               # 473 passed
python3 mangpai/tests/heldout/blind_eval.py --out snapshots/<批>.json --note "<验证状态>" --baseline snapshots/<上一批>.json
PYTHONHASHSEED=0 python3 mangpai/tests/heldout/blind_eval.py --out /tmp/seed0.json  # 与默认 seed 逐字节一致
python3 mangpai/tests/backtest/regression67.py    # 0 回归
python3 mangpai/tests/backtest/regression_famous.py  # 仅存量回归（罗斯切尔德）
```

---

## 9. 当前基线与残留总账（2026-08-14 收官态）

- baseline=`snapshots/20260814_c.json`（rubric v8-20260808，git 866baa9）。
- trainset 294：官 83.48%（19❌=§6.2）/ 财 52.21%（❌22=§6.3）/ 职 50.59%（27❌=§6.1）。
- heldout 215：官 74.24% / 财 66.67% / 职 44.23%（全部零翻转守护中）。
- 三维攻坚正式收官；后续方向（若重启）：官命 fp 窄修簇 A12-A18（各1例窄修）+检测簇 A8/A11/A19、财命 A13/A4/G5 残簇、职业中医/军警/lawyer 盲区（均须新突破面，旧窄通道已尽）。
- 汇报惯例：批次号+改动清单+翻转明细+六件套数字+300 字内。
