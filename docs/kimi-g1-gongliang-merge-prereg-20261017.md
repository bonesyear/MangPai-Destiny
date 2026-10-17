# G1 做功层次体系收编批 · 预注册清单（批次 G1，2026-10-17）

> 依据：`docs/design-gongliang-merge-20261017.md`（审计台账遗留项③「结构深水区」专项设计，主代理批准照做）。
> 基线（动工前实测）：pytest 1264 passed + 1 xfailed；verify_mangpai total 432；regression67 vs baseline67 仅 1 条既存 hunyin:离婚 回归（干净树复现，见 §五-4）。
> 收编裁定：zuogong_confirm 的 L0-L5「类型计数+主被动加减」体系废除（书明文否定：理象学:6912「三种不同的功…论功量只有一层」、:6018「最多也只有四层功罢了」；「连珠成势」七书零命中），gongliang 加法功量模型为做功层次唯一事实源（0-4 层，补 0=无功态）。gongliang 算法本体（14 条计分规则阈值/守门、_SCORE_BAND/_compute_score/_compute_boundary）不动。

## 一、对象与书锚（设计稿 §2 全带亲验行号）

| 改动 | 书锚 | 落点 |
|---|---|---|
| **G0 无功零态** | 理象学:6018 上限四层；:6022-6024「有的命只有半层功或根本无功」（yanjiu:6101 互证） | gongliang 空数据早退 level=1→0，tier_name='无功'，score=0；`_TIER_NAMES` 增 `0:'无功'`、`_SCORE_BAND` 增 `0:(0,0)` |
| **删双轨对账** | 双轨并存本身即「两套体系」创可贴（设计 §4.1） | gongliang.py 删 M5 对账段与 `work_level_duizhang` 键；docstring 改「本模块为做功层次唯一事实源」 |
| **zuogong_confirm 删层次保 harm** | G1 通则 :6912（功的种数≠层数） | 删 `_TIER_MAP`+`assess_work_level` 整函数；analyze_zuogong 删层次计算段与 work_level/work_tier/work_level_desc 三键；`has_severe_harm`/`has_active_harm` 抽 `_harm_signals()` 逐字等价保留（两个 any() 遍历 non_aux、work_types 空→双 False；gongliang:414、xiangfa 等有消费） |
| **消费方过渡** | — | narrative._zuogong_line 删 L{lv} 段（层功由 _gongliang_line 承担）；数字白名单 regex 删 work_level 补 gong_points 小数（R3）；engine._build_summary 改读 gongliang；xiangfa_ops 删 work_level==0 冗余支路（⟺ not work_types）；`__init__.py` 删 assess_work_level 导出（公共 API 变更，CHANGELOG 明示）；calib_zhenbao/harness 打印行；prompts/mangpai.md 仅授权 :11/:34/:42/:67 四行 |
| **测试处置** | — | verify §11/§14d-2/§18 删换（4 新锚经 analyze_gongliang）；test_gongliang 空输入断言 level==0；test_hfix5 按文件头部既定流程 exec 重钉（禁手改数字）；test_property 钉 gongliang.level∈[0,4]；mock fixtures 删旧键；regression67 cat1 删 cap、复例二副总补 CAT2、baseline67 --write-baseline 重钉 |

## 二、预期翻转清单

### heldout blind_eval（预期三维零翻转零抖动）

设计稿 §0/§1.3 论证：heldout 快照 engine 字段不含 zuogong.work_level（blind_eval.py:239-261），rubric 只读领域层字段，而领域层（caiming/guanming/gongmen_wuzhi/yongshen）早已只消费 gongliang——层次键删除对 scored 三维无传导路径；gongliang 算法本体不动 ⇒ **财/官/职三维零翻转零抖动**。若有翻转必是意外传导（xiangfa fallback/文本行），逐条归因，解决不了停下报回不硬推。RUBRIC_VERSION 不动，不需 --rescore。

### trainset / 回归闸

- regression67：cat1 删 cap 后判定逻辑只剩 primary∈book_set（18 例 verdict 预期不变）；cat2 新增 gl:复例二副总 **预期 standing ❌**（gl 实测 L3 vs 书 1，d=2，备案锚）；baseline67 detail 串 lv= 消失走 --write-baseline 重钉（修批C 先例）。
- verify_mangpai：total 432→420（§11 删 9 + §14d-2 删 2 + §18 删 5 + 新锚 4）。
- pytest：16 已钉书例层数不动（test_gongliang 全绿）；test_hfix5 重钉后 ph1-ph4 逐字节不变、13 盘 level/score 不变（重钉脚本安全断言）。

### 预期文本变化（评分无关，逐条可归因）

- engine._build_summary 文本行「做功层次：…（Level N）」→「功量层次：…（N 层功）」；narrative._zuogong_line 删 L{lv} tier 段——均不进 heldout 快照字段。

## 三、回填锚（设计稿 §3 标「回填/未钉」11 例，diag_case.py 真实引擎逐盘实测）

| # | 命例 | 书层 | 实测 gongliang | 处置 |
|---|---|---|---|---|
| 6 | 例六 乙丙甲甲/未戌子戌 | 2 | L2（points 2.5）✓ | 合书，直接锚 |
| 7 | 例七 丙戊戊甲/申戌寅寅 | 2 | L2（points 2.5）✓ | 合书 |
| 9 | 例九 壬戊癸庚/寅申巳申 | 3 | L3（points 3.5）✓ | 合书 |
| 10 | 普例一 丙戊辛癸/戌戌巳巳 | ~1 | L1（points 4.5，相生之功降档）✓ | 合书 |
| 12 | 普例三 庚庚癸丁/戌辰未巳 | ≤1 | L1（points 1.5）✓ | 合书 |
| 13 | 普例四 壬甲庚辛/子辰午巳 | 2 | L2（points 2.5）✓ | 合书 |
| 14 | 普例五 壬甲庚己/子辰寅卯 | 2 | L2（points 2.5，相克之制）✓ | 合书 |
| 16 | 三种合副总 甲癸丁庚/寅酉丑子 | **1（通则锚 :6900-6912）** | **L3**（points 4.5：同制+2/七杀当财+1/克链+1/月令+0.5，制不净封顶 raw4→3） | **偏差备案 2** |
| 17 | 总理例 戊壬乙己/辰戌未卯 | 近4（:7332-7336） | L4（points 6.5）✓ | 合书，verify 新锚 |
| 19 | 慈禧 乙丁乙己/未亥丑卯 | 4（:10595-10611） | **L3**（points 7.5，制不净封顶 raw4→3） | **偏差备案 1（R2 预案触发）** |
| 20 | 差例三 甲乙己辛/午亥巳未 | 无功（:6354-6358） | **L3**（points 4.5，制不净封顶 raw4→3） | **偏差备案 3** |

已钉 16 例（test_gongliang/test_hfix5）不动：李嘉诚4/乾隆4/克林顿4/蒋介石3/岳飞3/例八3/奥纳西斯4/阎锡山3/普例二1 等全保。

## 四、双端锚

| 对象 | 真阳锚（保） | 假阳锚（杀） |
|---|---|---|
| 无功零态 | test_gongliang.test_empty_input_is_level0（level==0/tier_name=='无功'/score==0，:6022-6024） | test_property gongliang.level∈[0,4] 随机 100 盘 + 60 甲子穷尽日柱不越界 |
| harm 信号等价 | 岳飞 ph1 钉 has_severe_harm=True（test_hfix5 重钉复验）；verify 空 types 盘双 False | 全库 grep 无 assess_work_level/work_level/work_tier 残留消费（__init__/engine/narrative/xiangfa_ops/测试全清） |
| 收编终态 | 16 已钉书例层数不变 + 回填 8 例合书（§三 ✓） | 副总 standing ❌ 备案锚（regression67 CAT2），防「类型计数」任何形式复活（设计 §5 不做清单） |

## 五、落地偏差备案（vs 设计稿预期）

1. **慈禧落 L3 非书 4（设计 R2 预案触发）**：实测 points 7.5（raw 4），「制不净：用神『财』之原神『食伤』透干(month_gan)未被净制」封顶三层。设计 R2 张力：:10607 月令见印当整层 vs gaoji 法则7 +0.5——裁定**附录口径让位法则7**（权重纪律：理象学正文 > 附录 > gaoji 之反向即附录孤证不立新规则），不为单例改权重。verify 锚钉 level==3 并注明书 4。
2. **副总落 L3 非书 1（设计 4.2C 授权「实测不符则预注册」）**：书 :6898-6912 语境=丑三合三种功论功量只一层（G1 通则锚）；引擎按加法功量规则累计 4.5 点（同制+2/七杀当财+1/克链+1/月令+0.5）封顶 L3。G1 落地=「种数不再直接映射层数」，加法规则逐条有书证；该例张力（通则 vs 逐条规则累计）备案，不改阈值。regression67 CAT2 standing ❌ + verify 锚钉 level==3。
3. **差例三落 L3 非书「无功」（设计未单列预案，按同纪律备案）**：书 :6354-6358「似乎功量很大…全被天干坏了。一生没有富贵」——引擎无「天干坏之」否决规则，加法功量 4.5 点封顶 L3。设计 §5 不做清单禁动 14 条规则阈值与守门 ⇒ 不立新规，备案为已知模型缺口（候选后续批次对象：天干坏局否决规则，需另立设计与书证）。verify 锚钉 level==3。
4. **附带发现（非本批引入）**：regression67 `hunyin:离婚` ✅→❌（val=平 vs 预期差，ALARM 打印）在**干净工作树（f5c50f6）上复现**——批D/E/F 引入的 baseline67 陈旧，与 G1 无关。按设计 --write-baseline 重钉时一并吸收；特此备案，建议另立批次核查 hunyin 模块。
5. **TestParallelToAssessWorkLevel 整类删除**（test_gongliang.py）：设计 4.3 表未列，但 assess_work_level 删除后必红（import 即失败），删除为唯一一致处置。
6. **test_hfix5_compute_all 实际会红（设计 4.3 预判「不红」偏差）**：该文件钉 `_build_summary` 全文，engine.py:887 层次行改读 gongliang 后两颗 summary 钉值（PIN_LI/PIN_QL_SUMMARY）翻转——按同一 exec 实况捕获重钉；乾隆盘旧钉「单层做功（Level 1）」正是设计 §0 实证错位例，新钉归书「极富极贵（4 层功）」。

## 六、DoD 核对表（落地后实测回填）

- [x] ① 16 已钉书例层数不动——test_gongliang 全绿；test_hfix5 exec 重钉安全断言（ph1-ph4 逐字节不变、13 盘 level/score 不变）通过
- [x] ② 无功零态锚 + harm 信号等价锚过（空输入 level==0/tier==无功/score==0；岳飞 has_severe_harm=True 与旧钉一致、空 types 盘双 False；全库 grep 无旧键残留消费）
- [x] ③ 六件套全绿：pytest **1263 passed+1xf**（1264→1263，删并行类 1 测）+ verify 四件套（mangpai **420** / dayun 70 / layer1 64 / layer3_checkpoint 20 全绿）+ regression67 无新增回归（G1 自身零回归；hunyin:离婚 既存回归干净树复现，见 §五-4）
- [x] ④ blind_eval --baseline latest（20261017_b1）**三维零翻转零抖动**——heldout 0 翻转 0 文本抖动、trainset 0 翻转 0 文本抖动，六维 Δ 全 +0.0% 噪声带内
- [x] ⑤ 分层/typing/凭证/doc_numbers 四闸门全过；verify 总数 432→420、pytest 1264→1263 已同步 README 首行/验证表、KB 验证口径行/§8 工具表/§8 命令行、PACKAGE.md ×2
- [x] ⑥ CHANGELOG G1 批次条目（公共 API 变更明示）+ KB §4.2 收编终态改写 + 审计台账③关闭 + PACKAGE.md/objective/README.md 腐引用修正 + 设计稿「6. 实施结果」小节（含本表全部偏差明细）
