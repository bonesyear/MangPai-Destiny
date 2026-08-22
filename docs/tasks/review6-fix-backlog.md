# 第六轮审查统一待修清单 + 修批 G 排期（2026-08-22，W5 收官批立；G1/G2 当日落地收官）

> 前身 = `docs/tasks/review5-fix-backlog.md`（第五轮 F1/F2/F3 **全部落地收官**，本文件接替为统一待修清单）。
> 来源 = 第六轮 W1-W5 五报告全量发现（W1 F6-1~F6-5 / W2 P1×2+P2×6 / W3 P2×2 / W4 F6-6 / W5 F6-7~F6-8+F6-6 扩展）。
> 发布判定：**G1 发布闸（P1×3 阻塞项）+ G2 样式批（P2 归并）均已落地，六件套全绿**（2026-08-22）；清单项全清，剩 G3/备案随对应批。

## G1 发布闸修批（代码，P1，一次六件套验收）——**✅ 已落地（2026-08-22）**

| # | 级 | 项 | 位置 | 修法 | 状态 |
|---|----|----|------|------|------|
| 1 | **P1** | F6-1 reject/失败降级丢迁移/相貌两维+死词拒出场景提示语误写「暂不可用」（W1 风险#2；W5 裁定：静默丢维不可接受，补文案即可，补两维后置 G2） | feishu/service.py 降级前缀白名单（:22）/ llm_channel.py 降级返回（:412/:419/:425/:433） | 提示语按场景区分，明示「本报告为引擎简版（五维）」 | ✅ 落地：提示语区分（死词拒出=「触发安全过滤不予展示」/一般失败=「暂不可用」）；裁定升级为 formatter 直出补迁移/相貌两段（原 G2 #12 提前并入） |
| 2 | **P1** | F6-2 误报窗结构性漏杀：逗号/分号不断句致「死断+拒答标记同逗号句」误豁免；死词表缺近义词 离世/去世/归西/病逝（W1 合成例 6/9/10 实测） | llm_channel.py:44-48（句界符 `。！？!?\n`）/:289-294（死词表） | 句界符补「，；」（或限定拒答标记须在死词前）；词表增补四词 | ✅ 落地：句界符补「，；」；词表 11→18（四词+同类 过世/身故/辞世） |
| 3 | **P1** | 复合词真漏网：标致/水灵/清秀/端庄 书内零锚该禁，但不含美/丑/帅字——校验器抓不到+prompt 未点名（W2 §4 书锚回查裁定） | llm_prompt.py SCHEMA+`_xiangmao_anchor` 禁令；llm_channel.py `_XIANGMAO_FORBID`(:62-65) | 双轨：prompt 点名五词（含甜美）+ `_XIANGMAO_FORBID` 扩四词（词级匹配无单字误报，无需排除窗） | ✅ 落地：双轨齐备；r4 离线重扫新词表抓「清秀」47 例存量（prompt 轨已点名，复跑批次收敛） |
| 4 | **P1** | 相貌引用率统计口径：`_has_xiangmao_marker` 只看 hit 不看 desc，独癸 16 例误计「有 marker」（W2 §3；对齐后 251/251=100%） | output/_n2_analyze.py:53-58 | 改「hit 且 desc 非空」（或补 eye_full 同口径） | ✅ G2 落地（裁定后置项清零） |
| 4b | P2 并入 | F6-6 程度词放大族（W4/W5） | llm_prompt.py `_xiangmao_anchor` | 锚定补「禁程度词/禁评价词/禁引申气质总结句」 | ✅ 顺手并入 G1 落地 |

**验收（已全过）**：哨兵 9 测先红后绿（逗号窗+死词近义词+复合词双轨+程度词+降级提示语+直出两维）→ pytest 831+1xf+19xp 全绿 → 294 例离线重扫（迁移/死亡红线保 0）→ verify 432+70+64+20 全绿、blind vs n3 零翻转、双 seed 一致、67/famous 无变化 → **转 GO**。

## G2 样式批（P2，紧随 G1 或并批）——**✅ 已落地（2026-08-22）**

| # | 项 | 位置 | 状态 |
|---|----|------|------|
| 5 | F6-6 扩展族（W4 立+W5 全量坐实 ~60+ 例次）：prompt 相貌锚定补「只写象描述本身——禁程度词（明显/很/强）、禁评价词（有神采/明亮/灵动/灵秀）、禁引申气质总结句（艺术气息/灵动之感）」**✅ G1 已并入落地；G2 剩 r5 复跑确认收敛** | llm_prompt.py `_xiangmao_anchor` | ✅ G1 落地；r5 复跑归口 LLM 复测批 |
| 6 | F6-7 迁移维臆造建议断语「宜动不宜静」3/294（W5 新；修后复扫仍现升 P1）：迁移锚定补「只述象与应期，不得给宜动/宜静等建议断语」 | llm_prompt.py `_qianyi_anchor` | ✅ 落地：ban 补「不得输出引擎特征之外的结论式建议（如「宜动不宜静」类宜忌断语，引擎无此输出=臆造）」，有/无信号两分支同禁；哨兵 `test_qianyi_anchor_g2_no_fabricated_advice` |
| 7 | F6-8 性别分流语未落地 11/294（W5 新）：相貌锚定补「秀气分流语按本造性别只写对应分支」 | llm_prompt.py `_xiangmao_anchor` | ✅ 落地：锚定补「按本造性别只写对应分支，另一支不得复述」+八字行补乾/坤造标记（llm_channel render，LLM 方知本造性别）；哨兵 `test_xiangmao_anchor_g2_gender_branch`/`test_render_bazi_line_carries_gender` |
| 8 | 「数据不足」非模板语 8/294 再犯（W2-P2#4/W4/W5 三批确认）：迁移无信号锚定补「禁写数据不足，必须用『无迁移信号』」 | llm_prompt.py `_qianyi_anchor` | ✅ 落地：迁移/相貌两无信号分支均明令模板语+禁写「数据不足」；哨兵 `test_g2_no_signal_template_words` |
| 4 | 相貌引用率统计口径（W2 P1 后置）：`_has_xiangmao_marker` 只看 hit 不看 desc，独癸 16 例误计（对齐后 251/251=100%） | output/_n2_analyze.py:46-58 | ✅ 落地：改「hit 且 desc 非空」（yanxiang 同口径），对齐锚定判据 |
| 9 | F6-3 reject 闸按 detail 子串「死亡红线」匹配 → violation 加结构化 `reject: true` 字段 | llm_channel.py:295/:429-433 | ✅ 落地：死亡红线违规带 `'reject': True`，闸改 `x.get('reject')`；哨兵 `test_death_violation_structured_reject_flag` |
| 10 | F6-4 render 层三条降级返回文本自带免责行（当前单点依赖 service 前缀白名单） | llm_channel.py:412/:419/:425/:433 | ✅ 落地：`_DISCLAIMER_LINE` 常量，LLM 不可用/非合法 JSON/死亡拦截三返回均自带；哨兵 `test_degrade_returns_carry_disclaimer` |
| 11 | F6-5 lark_md LLM 路径漏网：附注 bullets `- ` + LLM conclusion 原文未三符 sanitize | llm_channel.py:377/:436 + format_reading | ✅ 落地：`_larkmd_sanitize`（行首 - /> 改 ·、--- 改 ——）+附注 bullets 改 `· `；哨兵 `test_format_reading_larkmd_sanitized` |
| 12 | F6-1 后置腿：formatter 引擎直出补迁移/相貌两段（若裁定为补维而非改提示语则提前） | feishu/formatter.py | ✅ G1 已提前并入落地 |
| 13 | test_f1_gate `_five_dims()` 改从 DIMENSIONS 生成七维 mock（W2-P2#1） | mangpai/tests/test_f1_gate.py:26-28 | ✅ 落地：`_dims()` 从 DIMENSIONS 生成 |
| 14 | schools.py:38 注释「五维」字样同步七维口径（W2-P2#5） | subjective/schools.py:38 | ✅ 落地 |
| 15 | W3-P2#1 眼象线「大眼」泛化：改「丙=眼框/眼睛之象」或补锚注（引擎批） | subjective/xiangmao.py:152 | ⏸ 随下个引擎批（本批红线=引擎零改动） |
| 16 | W3-P2#2 「美丽」注释口径过强改准（lixiangxue:9928/12583/12632 有 3 处用例；禁令本身合规不动） | llm_channel.py:64 注释 | ✅ 落地：注释改准（3 处用例，禁之属保守不违书但非零锚） |

**验收（已全过）**：哨兵 8 测先红后绿（臆造断语禁/性别分流+乾坤造标记/模板语×2/reject 结构化/降级免责/lark_md sanitize）→ pytest 838+1xf+19xp 全绿 → verify 432+70+64+20 全绿 → blind vs g1 零翻转零抖动（快照 `snapshots/20260822_g2.json`）→ 双 seed 逐字节一致 → 67/famous 无变化、calib 常驻 2 条零新增。

## G3 / 备案（不阻塞，随对应批）

- F-N2-1（引擎侧冻结项）：`xiangmao.py:111` 秀气线 desc「漂亮」改「女看秀气倾向」；**落地后连 `_xm_sanitize` 函数一起删**（W2-P2#2：静默语义改写，留函数即成掩盖点）——随下个引擎批。
- F-N2-2 judge 新维翻转召回弱（0/2）：下轮评审/judge 前判据补眼象线命中示例 + 同步迭代 5「倾向性参考」许可（V3 F-V3-2 并项）。
- F-N2-3 评审 API 偶发空 content 重跑即过：已知环境。
- 可选：迁移禁词补 出境/离境（书内零锚实测零违规，W2-P2#6 优先级最低）；相貌排除窗残留假阳族 美金/小丑/丑月（出现再补，W2-P2#3）；英文死词不覆盖（中文输出面，观察）。
- 观察项不立项（W5）：应期窗 note/pillar/basis 不入锚（宫位语义 L1→L2 丢失=设计性收窄，需求驱动再扩）；安居窗/或然窗省略（遗漏非臆造）；「未来流年…乙巳」时态瑕疵。

## 执行序

G1（P1 四项）→ 六件套+294 离线重扫 → **七维正式发布 GO** ✅；G2 样式批（#4-#16 归并，哨兵 8 测先红后绿+六件套全绿）✅ 2026-08-22 落地收官；G3/备案随对应批不排期（#15 大眼锚注随下个引擎批）。
