# 做功层次体系重写设计稿（只读，未改任何文件）

> 对应审计台账 `docs/audit-vs-originals-20261017.md` 遗留项③「结构深水区：zuogong_confirm 层次体系重写——需专项设计」。所有书证行号已亲自逐行 sed 验证；代码行号对当前工作树实测。（本稿由审计代理产出，主代理存档；实施另立批次）

---

## 0. 结论（TL;DR）

- **收编进 `gongliang`，废除 `zuogong_confirm` 的 L0-L5 类型计数体系**。gongliang 的加法功量模型就是书口径（理象学:6026-6045），且已被 test_gongliang.py 钉在 16 个书例上全绿；zuogong_confirm 的体系被书明文否定（:6912、:6018），「连珠成势」七书零命中（全库复扫确认）。
- **实证错位**：现有钉扎值中，乾隆 work_level=1、克林顿=2、蒋介石=2、岳飞=2、例八=1（书分别为 4/4/3/3/3 层），而普例二 work_level=3（书判「功不算大」）——方向性错误双向都有。
- **迁移破坏面比预想小**：领域层（caiming/guanming/gongmen_wuzhi/yongshen）早已只消费 gongliang，无人消费 work_level 做判定；heldout 快照 engine 字段不含 zuogong.work_level（blind_eval.py:239-261），预期**三维零翻转零抖动**，换基线走 F6 先例流程即可。

## 1. 现状梳理

### 1.1 zuogong_confirm 体系（L0-L5，类型计数 + 主被动加减）

- `assess_work_level()`（:73-215）：san_he_formed+占比>70%+成势为主功 → L5「连珠成势」（:150-152）；hua_success+type_count>=3 → L4（:153-155）；type_count>=3 → L3（:156-158）；type_count>=2 and active>=3 → L3；type_count>=2 → L2；主被动/折扣 ±1（:186-201）
- `analyze_zuogong()` 返回键：`work_level`(0-5)、`work_tier`、`work_level_desc`、`has_severe_harm`、`has_active_harm` 等

### 1.2 gongliang 体系（L1-L4，书加法功量）

- 14 条计分规则：原神用神同制+2 / 制墓库+2 / 七杀当财+1 / 入墓为功+1 / 库源连墓+1 / 包局包制+1 / 克链+1 / zb 翻转 / 金字塔冲链 / 包局2.6 / 带象+1 / 统+1 / 月令+0.5 / 墓库属性+1 / 开库+1 / 化用成局+2
- 映射封顶（:1166-1179）：points≥4→L4、≥3→L3、≥2→L2；制不净封顶 L3；相生之功封顶 L1；相克之制封顶 L2
- 空数据早退（:291-297）：level=1 + penalty='无功'（书 :6022-6024 的「无功/半层」目前无独立 0 态——目标态要补）

### 1.3 消费方全表（grep 全库穷举）

| 消费方 | 位置 | 读什么 | 性质 |
|---|---|---|---|
| narrative._zuogong_line | narrative.py:62-65 | work_level/work_tier/work_efficiency | LLM 摘要行 |
| narrative._gongliang_line | narrative.py:69-78 | level/tier_name/zhi_jing/boundary | 层功行（已就位） |
| narrative 数字白名单 | narrative.py:465 | regex work_level/level/score | LLM 数字回对 |
| engine._build_summary | engine.py:887 | work_tier+work_level | summary 文本行 |
| xiangfa_ops | xiangfa_ops.py:1404-1405 | work_level==0 → fallback_active | 冗余：⟺ not work_types |
| gongliang 双轨对账 | gongliang.py:1371-1390 | work_level_duizhang | 标注级，diff≥2 写 reasons |
| caiming / guanming / gongmen_wuzhi / yongshen | 各处 | gl.level/wealth_grade 等 | **只读 gongliang** |
| calib_zhenbao / harness | 调试脚本 | 双套打印 | — |
| regression67 | :51-62 cat1 cap、:64-87 cat2 | work_level cap + gl.level 判分 | 67 例回归闸 |
| verify_mangpai | :599-660、749-757、917-936 | **单测 assess_work_level 十余处** | verify 432 闸 |
| test_property / test_gongliang / test_hfix5_gongliang / test_narrative / test_llm_channel / test_subjective | 各 mock fixture | work_level 钉值/假数据 | pytest |
| prompts/mangpai.md | :11、:34、:42、:67 | L0-L5 阶梯写进 prompt | LLM 提示词 |
| `__init__.py` | :31-32、:54 | 导出 assess_work_level | 公共 API |
| 文档 | PACKAGE.md:31/83、objective/README.md:25/90-91 | work_level.py 引用——**已腐** | 文档债 |
| blind_eval | :239-261 | 快照字段不含 work_level/gl.level | 仅经领域层间接传导 |

## 2. 书口径目标态（每条附亲验行号）

**权重纪律**：理象学正文 > 理象学附录（博客文粹） > gaoji（今人重编本）。gaoji 条目一律在 reasons/注释中标注「高级篇法则 N」。

| # | 规则 | 书证（亲验） |
|---|---|---|
| G0 | 上限四层；存在半层功与无功 | :6018「最多也只有四层功罢了」；:6022-6024「有的命只有半层功或根本无功」（yanjiu:6101 互证） |
| G1 | **通则：功的种数 ≠ 层数** | :6912「虽然看起来有三种不同的功，但论功量只有一层，不是三层功」（:6898-6910 丑三合=三种功语境） |
| G2 | 原神用神同制 = 两层 | :6026-6030 |
| G3 | 制墓库 = 两层 | :6037 |
| G4 | 七杀当财 比财高一层 | :6038-6041 |
| G5 | 入墓为功 = 一层 | :6041 |
| G6 | 年时包局/包制 +一层 | :6041-6043 |
| G7 | 层层相制逐级一层（金字塔） | :6081-6085 乾隆例 |
| G8 | 制净调节：制之不净达不到四层 | :6120-6126 蒋介石例 |
| G9 | 普通四柱三情形降档 | :6203-6213 |
| G10 | 量级-层数对照表 | :6014-6022 |
| gaoji-1~7 | 制去用神两层（814-823）/制去库两层（825-835）/带象一层（838-844）/统一层（845-852）/墓库属性+1、开库功上加功（853-859）/包局+1（860-865）/月令+半层（866-870） | gaoji:814-870，权重注明 |

**书内张力备案**：附录博客文粹 :12309-12315「四层或五层功」与正文 :6018「最多四层」冲突。裁定：正文优先，锁四层上限；五层说不实现。

**目标判定算法 = 现行 gongliang 算法本体不动**，只补零态：

- `level ∈ {0,1,2,3,4}`；0=无功（早退分支 level=1 改 level=0，tier_name='无功'，score=0）
- 半层不立独立档：gong_points 小数+boundary 已能表达「三层强一点」
- work_types 种数从此与层次无关（G1 落地）

## 3. 20 个书锚案例对照表

「钉」=现有测试钉扎值；「回填」=迁移时用 diag_case.py 实测后补全，不得凭推算填写。

| # | 命例 | 书断语（行号） | 书层 | 现行 work_level | 现行 gongliang | 目标 |
|---|---|---|---|---|---|---|
| 1 | 李嘉诚 戊己庚丁/辰未午亥 | 「共有四层功，千亿级别」:6051-6063 | 4 | 4（钉）✓ | 4 ✓ | 4 |
| 2 | 乾隆 辛丁庚丙/卯酉午子 | 「一层功…又一层功…帝王」:6081-6085 | 4 | **1（钉）✗** | 4 ✓ | 4 |
| 3 | 克林顿 丙丙乙戊/戌申丑寅 | 「包制一层+申入丑墓一层+戌刑丑制墓」:6100-6106 | 4 | **2（钉）✗** | 4 ✓ | 4 |
| 4 | 蒋介石 丁庚己庚/亥戌巳午 | 「两层功…墓加一层…制之不净达不到四层」:6120-6124 | 3 | **2（钉）✗** | 3 ✓ | 3 |
| 5 | 岳飞 癸乙甲己/未卯子巳 | 「两层…包局再加一层，共三层，省部级」:6134-6138 | 3 | **2（钉）✗** | 3 ✓ | 3 |
| 6 | 例六 乙丙甲甲/未戌子戌 | 「比岳飞少一层。两层，厅级」:6150 | 2 | 回填 | 2 ✓ | 2 |
| 7 | 例七 丙戊戊甲/申戌寅寅 | 「申金及申中之水被制，两层，厅级」:6173 | 2 | 回填 | 2 ✓ | 2 |
| 8 | 例八 壬戊丙壬/寅申申辰 | 「制寅两层…杀星当财…三层，数十亿」:6181-6183 | 3 | **1（钉）✗** | 3 ✓ | 3 |
| 9 | 例九 壬戊癸庚/寅申巳申 | 「再加两层，共三层…数十亿」:6197 | 3 | 回填 | 3 ✓ | 3 |
| 10 | 普例一 丙戊辛癸/戌戌巳巳 | 「巳入戌墓之功…只是普通人」:6232-6236 | ~1 | 回填 | 1 ✓ | 1 |
| 11 | 普例二 壬己乙丁/子酉丑丑 | 「相生之功，功不算大，小职权」:6244-6249 | ≤1 | **3（钉）✗反向虚高** | 1 ✓ | 1 |
| 12 | 普例三 庚庚癸丁/戌辰未巳 | 「相生效率低，普通人」:6257-6263 | ≤1 | 回填 | 1 ✓ | 1 |
| 13 | 普例四 壬甲庚辛/子辰午巳 | 「两层功量，行至水运富有千万」:6271-6274 | 2 | 回填 | 2 ✓ | 2 |
| 14 | 普例五 壬甲庚己/子辰寅卯 | 「虽有两层功…高工资」:6293-6297 | 2 | 回填 | 2 ✓ | 2 |
| 15 | 奥纳西斯 乙己己庚/巳丑未午 | 「制库两层+杀库一层+包制一层，四层」:6470-6474 | 4 | **3（钉，双证）✗** | 4 ✓ | 4 |
| 16 | 三种合副总 甲癸丁庚/寅酉丑子 | 「三种功…只有一层，不是三层功」:6900-6912 | **1（通则锚）** | **2（钉）✗** | 回填（未钉） | 1 |
| 17 | 总理例 戊壬乙己/辰戌未卯 | 「墓库做功功量很大…近四层功…总理」:7332-7336 | 近4 | 回填 | 未钉（新增锚） | L3/L4 边界 |
| 18 | 阎锡山 癸辛乙丁/未酉酉丑 | 「功量有三层强一点」:7182-7188 | 3.5→3 | **2（钉）✗** | 3 ✓ | 3 |
| 19 | 慈禧 乙丁乙己/未亥丑卯 | 「双层…又加一层…共四层」:10595-10611 | 4 | 回填 | 未钉（新增锚，落地验证，不达则预注册备案） | 4 |
| 20 | 差例三 甲乙己辛/午亥巳未 | 「似乎功量很大…全被天干坏了。一生没有富贵」:6354-6358 | 无功 | 回填 | 未钉（新增锚） | 0/1 |

**对照结论**：已钉 11 例次中，现行 work_level 仅李嘉诚 1 例合书；现行 gongliang 16/16 合书。目标体系=书 20/20。

## 4. 迁移方案

### 4.1 路线裁定：统一收编进 gongliang（单一事实源）

理由：书只有一个功量体系；gongliang 已是其工程化实现且 16 锚全绿；双轨对账的存在本身就是「两套并存」的创可贴。

**不选**「改 zuogong_confirm 保留 work_level 键、改算法」：engine 编排 zuogong 先于 gongliang，zuogong 无法自算书口径层数；standalone 调用拿到无层次版，键行为不一致是新坑。

### 4.2 改动点清单（函数级）

**A. gongliang.py（小改）**
1. :291-297 空数据早退：`_build_result(level=0, score=0, penalty='无功', tier_name='无功')`；`_TIER_NAMES` 增 `0: '无功'`；`_SCORE_BAND` 增 0 分支
2. 删双轨对账段（:1371-1390）与输出键 `work_level_duizhang`
3. docstring「两套体系并行」段改写为「本模块为做功层次唯一事实源」

**B. zuogong_confirm.py（删层次，保 harm 信号）**
1. 删 `_TIER_MAP` 与 `assess_work_level()` 整函数
2. analyze_zuogong：删层次计算段与返回 dict 的 `work_level`/`work_tier`/`work_level_desc` 三键
3. **保留** `has_severe_harm`/`has_active_harm`（gongliang:414、xiangfa 等有消费）——:128-139 的两个 any() 内联到 analyze_zuogong 尾部或抽 `_harm_signals()`，行为逐字等价
4. docstring 同步改写

**C. 消费方逐一过渡**

| 消费方 | 改法 |
|---|---|
| narrative.py:62-66 `_zuogong_line` | 删 `L{lv} {tier}` 段，行改「做功：类型+效率」；层功由 `_gongliang_line` 承担 |
| narrative.py:465 数字白名单 | regex 删 work_level，补 gong_points（小数 `(\d+(?:\.\d+)?)`）——否则「0.5 层」被幻影数字误杀 |
| engine.py:887 `_build_summary` | 改读 gongliang：`功量层次：{tier_name}（{level} 层功）` |
| xiangfa_ops.py:1404-1405 | 删 work_level==0 支路（not work_types 已等价） |
| calib_zhenbao/harness 打印行 | 删或改读 gl |
| prompts/mangpai.md | :11 阶梯改四层功量级表（G10）；:34 删「连珠成势」；:42 改「层功几层？依据哪几条功量规则」；:67 basis 示例改 gongliang.level |
| `__init__.py` | 删 assess_work_level 导出（公共 API 变更，CHANGELOG 注明） |
| regression67.py | cat1 删 cap（书无「类型数→层次」映射）；**复例二副总补进 CAT2**（gl 判 1 预期，实测不符则预注册）；baseline67 走 --write-baseline 重钉 |

### 4.3 会红的测试与处置（逐一）

| 测试 | 红因 | 处置 |
|---|---|---|
| verify_mangpai :599-660、749-757、917-936（十余处） | assess_work_level 消失 | 整段删除，替换为 4 个新增锚例（总理例/慈禧/差例三/副总）经 analyze_gongliang 的层数断言；verify 总数变化写 CHANGELOG |
| test_gongliang `test_empty_input_is_level1` | 无功态 1→0 | 改断言 level==0，注释引 :6022-6024 |
| test_hfix5_gongliang | 钉值含 work_level_duizhang | 按文件头部既定流程重钉（exec 捕获实况），禁手改数字；层数/score 钉值预期不动 |
| test_property :68-71、:129 | work_level 键消失 | 改钉 gongliang.level ∈ [0,4] |
| test_narrative/test_llm_channel/test_subjective mock fixture | 含旧键/旧行格式 | fixture 同步删键；_zuogong_line 文本断言按新格式改 |
| regression67 baseline67.json | detail 串含 lv= | --write-baseline 重钉（修批C 先例） |
| test_snapshot_hygiene / test_key_contract / test_hfix5_compute_all | — | **不红** |

### 4.4 blind_eval 基线更换（照 F6/P 系列先例）

1. rubric 只读领域层字段（领域层本就读 gongliang）——口径不变，不需 --rescore，RUBRIC_VERSION 不动
2. 流程：预注册文档（仿 docs/kimi-p1-~t1-prereg-*.md）→ 哨兵先红后绿 → 六件套 → `blind_eval.py --out snapshots/<批>.json --baseline 20261017_a1.json` → 预期**三维零翻转零抖动**（若有翻转必是意外传导，逐条归因）→ 人工改 LATEST 一行 → _meta 三字段齐全（test_snapshot_hygiene 闸）
3. CHANGELOG 批次条目 + KB §4.2「比 zuogong.work_level 准」句改写为收编终态 + 审计台账 ③ 关闭 + PACKAGE.md/objective/README.md 腐引用顺手修正

## 5. 风险与不做清单

**风险**
- R1（中）：standalone analyze_zuogong 调用方失去层次键——4.2C 表已穷举仓内调用点；仓外属公共 API 变更，CHANGELOG 明示
- R2（低）：慈禧新锚可能落 L3 而非书 4（:10607 月令见印当整层 vs gaoji 法则7 +0.5 张力）——预案：落地验证，不达则按「附录口径让位法则7」预注册备案
- R3（低）：LLM 数字白名单漏 gong_points 小数 → 幻影数字误报，4.2C 已列改法
- R4（低）：hfix5 钉值重钉须按文件头部原流程（exec 捕获），禁手改数字

**不做清单**
- 不动 gongliang 分值带工程化（_SCORE_BAND/_compute_score/_compute_boundary 全保留）
- 不动 14 条计分规则的阈值与守门（F6 批校准成果）
- 不动 caiming/guanming/gongmen_wuzhi/yongshen 消费侧条款
- 不立「五层功」（:12313 附录孤证）
- 不复活「连珠」词、不引入任何形式的新类型计数
- 不动 work_efficiency 高/中/低三档（书的「效率」与「功量层数」是两件事，保留）
- 不顺手做台账其他遗留项

### 附：核实记录

- 书证 21 段全部亲验：理象学 :6014-6045、:6051-6297、:6305-6313、:6350-6358、:6470-6474、:6894-6912、:7178-7188、:7326-7336、:10121、:10534-10611、:12309-12346、:12487-12521；gaoji:814-870；yanjiu:6101 互证
- 「连珠」docs/duan-books/ 全库 grep 零命中（复扫确认）
- 现行 work_level 钉扎值出处：test_hfix5_gongliang.py:44-134 ph5 钉值 9 例 + baseline67.json 18 例 lv= 记录
- 未钉扎的 10 例标「回填」，迁移时实测补全，不得凭推算填写

---

## 6. 实施结果（G1 批落地后回填，2026-10-17）

全部改动按 §4.2/§4.3 表执行完毕。**blind vs LATEST（20261017_b1）三维零翻转零抖动**（heldout/trainset 各 0 翻转、文本抖动各 0，六维 Δ 全 +0.0%）——§0 结构论证成立。预注册=`docs/kimi-g1-gongliang-merge-prereg-20261017.md`。

### 6.1 回填实测（11 例，diag_case.py 真实引擎，改动前捕获）

合预期 8 例：例六 L2 / 例七 L2 / 例九 L3 / 普例一 L1（相生降档）/ 普例三 L1 / 普例四 L2 / 普例五 L2 / 总理例 L4（points 6.5，书「近四层」吻合，verify 新锚钉 4）。偏差 3 例（全部预注册备案，不为单例改权重，verify/regression67 钉实测层数注明书层）：

- **慈禧 L3**（书 4）：R2 预案触发——points 7.5 raw4 经「制不净（食伤透干）」封顶 3；附录口径让位法则7。
- **副总 L3**（书 1）：§4.2C「实测不符则预注册」——加法功量 4.5 点（同制+2/七杀当财+1/克链+1/月令+0.5）raw4 封顶 3；regression67 CAT2 standing ❌ 备案锚。
- **差例三 L3**（书「无功」）：设计未单列预案，按同纪律备案——引擎无「天干坏之」否决规则，记为已知模型缺口（候选后续批：天干坏局否决规则，须另立设计与书证）。

### 6.2 与设计的偏差（逐条）

1. **§4.3 预判 test_hfix5_compute_all「不红」偏差**：该文件钉 `_build_summary` 全文，engine.py:887 层次行改读 gongliang 后 PIN_LI/PIN_QL_SUMMARY 两颗钉翻转（4 测红）——按同一 exec 实况捕获重钉复绿；乾隆盘旧钉「单层做功（Level 1）」正系 §0 实证错位例，新钉归书「极富极贵（4 层功）」。
2. **TestParallelToAssessWorkLevel**（test_gongliang）§4.3 未列但必红（import assess_work_level 即失败）→ 整类删除（pytest −1 测）。
3. verify 总数 432→**420**（§11 删 9 + §14d-2 删 2 + §18 删 5 + 新锚 4）；pytest 1264→**1263**；README/KB 验证口径行/§8 工具表/快捷命令行、PACKAGE.md ×2 已同步，check_doc_numbers 过。
4. regression67 --write-baseline 重钉时一并吸收 `hunyin:离婚` ✅→❌ 既存回归（**干净树 f5c50f6 复现**=批D/E/F 基线陈旧，非本批引入）——预注册 §五-4 备案，建议另批核查 hunyin 模块。
5. 空数据早退 reason 文案微调（「功量微弱（半层/无功）」→「无功（理象学:6022-6024）」）——与 0 态语义对齐，全库无测试钉该串。
6. 顺手修正（任务授权）：KB:50 模块签名、KB:111/495 概念性 432→420、PACKAGE.md work_level.py 腐行 ×2 删、objective/README.md work_level.py 腐行+输出结构示例三键改注。

### 6.3 不做清单守护（§5 全守住）

14 条计分规则阈值与守门未动（hfix5 重钉安全断言实证 ph1-ph4 逐字节不变、13 盘 level/score 不变）；_SCORE_BAND/_compute_score/_compute_boundary 全保留（仅 _SCORE_BAND 增 0 分支）；caiming/guanming/gongmen_wuzhi/yongshen 消费侧条款未动；五层功未立；「连珠」词与任何形式类型计数未复活（全库 grep 零残留）；work_efficiency 三档保留；台账其他遗留项未顺手做。基线未写新快照、git 未提交——主代理复核后统一换基线（F6 先例：人工改 LATEST 一行 + _meta 三字段齐全，test_snapshot_hygiene 闸）。

---

## 6.4 G2 批实施结果（三条书证规则，2026-10-17）

§6.1 三个偏差备案案例（慈禧/副总/差例三「引擎缺三条规则」）本批补规则闭合，预注册=`docs/kimi-g2-sanli-prereg-20261017.md`。**三案例全部落书判值：副总 L3→L1（书 1，:6898-6912）、差例三 L3→L0 无功（书「一生没有富贵」，:6354-6358）、慈禧 L3→L4（书 4，:10595-10611）**。

| 规则 | 机制（书怎么说就怎么实现） | 落点 |
|---|---|---|
| G2-1 三种功≠三层功（:6898-6912） | 日主无功弃之不看（日主所出/所受之克剔出克链，书「日主丁火没有功，弃之不看」）；日支合中心（涉≥3合，同 `_apply_he_center_skip` 口径）为同制位时同制族并计一层（书「论功量只有一层，不是三层功」） | 副总 4.5→1.5 点 L1 |
| G2-2「天干坏之」否决（:6354-6358） | 结构候选=制局目标支藏官杀透出+官杀并透混杂（正官七杀同透，书「并透」）+日主无印透干化杀；制净闸确认（制不净方成立——乾隆官杀并透而帝王，制净根尽透干为虚闸回）→ 同制族整族撤销、层功判 0（无功） | 差例三 4.5→1.5 点 L0 |
| G2-3 月令见印整层（:10595-10611 vs gaoji:866-870） | 月令本气为日主之印且入三合局成势（「强有力的印」）计 +1 整层（书于此计整层）；其余月令做功维持 +0.5（gaoji 法则7 权重低）；三合成势围制+制库书判制之彻底（「全部制死…共四层功」），不净封顶不适用（同奥纳西斯豁免例） | 慈禧 7.5→8.0 点 L4 |

**红线守护**：16 已钉书例 level/score 一个不变差（test_gongliang 42 测全绿；hfix5 exec 重钉安全断言=ph1/ph2 逐字节不变、13 盘 level/raw_level/score/gong_points 不变——变化精确落在预期 5 盘 chain_length 1→0 与 ph3/ph4 新键）。pytest 1263→1266（+3 哨兵先红后绿）；verify 420 总数不变（三锚就地改书判值）。

**blind vs LATEST（20261017_c1）**：heldout **0 翻转**；trainset 5 翻转 + 文本抖动 17 条**逐案归因全闭合**——2 例变差（⚠️→❌）=书内张力备案（reg67-伤食当财：书读戊己官杀为成势之党一员（:7280-7285）与否决谓词张力，豁免须党势五行判定另立批；yx-记者-2：通则 L1 vs 断语富一档张力）、1 改善（yx-富富有百万巨富→富归位）、2 换档（✅→✅）；抖动含副总/差例三两本尊自证合书、朱元璋 sanhe 豁免 L4 帝王归位。六维 Δ 噪声带内（trainset 财 +0.9%）。**未写基线**（LATEST 推进留主代理，F6 先例）。附带补缺：`_SCORE_BASE` 补 0 分支（G1 仅补 _SCORE_BAND，本批否决为首个中管道 0 态）。
