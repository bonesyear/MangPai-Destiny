# 第三轮审查 T3 · 端到端交付物报告（2026-08-18）

> 范围：A. payload 语义保真（零 API，v5 数据复用）+ B. S1 语义忠实度（§五 v4-pro 协议三层漏斗）。
> 红线遵守：只测不改（引擎/测试零改动）；评审/judge 均 deepseek-v4-pro 谷段、双实例隔离
> （不同 system prompt/不同 schema/不同信息面，judge 永不接触评审输出）；
> 被评对象 = v4-flash v5 生产叙述（281 例，rescore 口径）；不碰 heldout。
> 脚本：`output/_t3_dump.py` / `_t3_anchor_scan.py` / `_t3_eval.py` / `_t3_calibrate.py`；
> 数据：`output/t3_s1/{dump,payload_fidelity,anchor_candidates,sample30,calibration}.json` +
> `review30.jsonl` / `judge281.jsonl` / `violations.md`。

## 0. 一句话结论

**payload 保真 GO（37/38 键零扭曲，1 死键 P1）；S1 按协议不达标（评审样本翻转 9/30 ≥3 一票否决，集中在职业维+应期维；财命/官命/婚姻三维零真翻转）——飞书集成在「职业/应期叙述语义」维度 NO-GO，须 prompt 迭代 5 后复验。**

---

## A. payload 语义保真（零 API，281 例全量）

方法：逐例重跑引擎（确定性），`build_payload` 输出 vs 无 scrub 对照 payload 递归 diff（字符串列表用
SequenceMatcher 定位真实删除条目——尾部归因曾张冠李戴，已修正）；另抽样 50 例验证 user prompt
内嵌 features JSON 逐字一致（50/50 ✅）。

### A.1 保真检查表（38 selector 键 × 281 例）

| 键 | 传递状态 | 扭曲记录 |
|---|---|---|
| bazi / shensha / nayin / nayin_work / canggan / chang_sheng / kong_wang / di_zhi_relations / binzhu / tiyong / zuogong / gongliang / muku / anhe / biqi / soil / he_types / virtual_solid / zhengfan / xiangfa / shenshu / caiming / hunyin / xueli / laoyu / yingqi_subj / yunfan / zhiye / zeishen_bushen / narrative（30 键） | **逐字节保真**（`_jsonable` tuple→list 外零变换） | 无 |
| **dayun_analysis** | **281/281 全缺失（死 selector）** | engine result 45 键中**无此键**（`dayun`/`dayun_gz` 亦无），selector 声明静默落空；`summarize_engine_result` digest 同源缺失 → **LLM 全程零大运表数据**（仅 yunfan/liunian_analysis 岁运切片）。payload 层最大结构缺口 |
| zaihuo | 281/281 变更 | F14 红线（设计内）：`zaihuo_llm_view` 整键丢弃 siwang（281）+ direction_signals（281）；summary 246 例删「死亡X」段；max_risk 1 例 中→低 |
| shipaige | 281/281 变更 | 死亡 scrub（设计内）：todos 尾部 562 条（含「父死母再嫁」等碎片原文）、domains.寿元 193 例 |
| xiangfa_ops | 117/281 变更 | xiangfa_fallback.lianti warning/desc（连体被制「防伤身体及寿命」）117 例 scrub |
| liuqin | 29/281 变更 | xiongdi_keshun markers/desc（「手足早夭」）29 例 scrub |
| liunian_analysis | 27/281 变更 | 逐年条目 30 条「冲破主终结/死亡」scrub |
| wood_type | 15/281 变更 | rules「怕见旺火（燃烧焚尽，伤寿）」15 例 scrub |
| guanming | 12/281 变更 | combo.details「官被制空制死，不立官命」12 例 scrub——**注意：这是官命否决理由，LLM 看不到该条论据**（红线代价，记录） |

### A.2 判定

- **键值传递零扭曲**：37/38 键原值直达 LLM（全部变更=死亡红线 scrub/zaihuo 视图，设计内逐条可对账）；prompt 内嵌 JSON 逐字一致；键清单/财档锚定行均由 features 派生，无二手改写。
- **结构缺口 1 个（P1）**：`dayun_analysis` 死 selector——应期维 LLM 只有流年切片无大运表。修批 A③ 摘 gongmen_wuzhi 时未同步发现；schools.py 受保护，处置（摘死键 or 引擎补供 dayun 数据）须用户决策。
- **红线代价（P2 记录）**：guanming G6 否决理由被 scrub，官命维 LLM 缺一条论据；zaihuo summary 删死亡段后三域视图保留，可接受。
- **工具隐患（P2）**：`_llm_batch_rescore.py` 的 glob 合并顺序使 retry 挽回的 12 例 reading 被主批旧记录覆盖（「281 例」口径由来）；v5 实际存在 293 例 reading，12 例未参与本批评估。

---

## B. S1 语义忠实度（三层漏斗）

### B.1 第一层：规则式语义锚（零 API，281 例全量筛子）

词表：富↔贫/官↔非官/婚好↔婚差/吉↔凶 + blind_eval `_ZY_RULES`/`_XIONG_MARKERS` 复用，否定窗抑制假阳；
数据源=引擎 features 全键（duohun/dushen 纳入后婚姻维假阳收敛：cand2 6→1、cand1 112→47）。

| 维 | cand1（放大/缩水嫌疑） | cand2（翻转嫌疑） |
|---|---|---|
| 财命 | 10 | 3 |
| 官命 | 14 | 3 |
| 职业 | 33 | 4 |
| 婚姻 | 47 | 1 |
| 应期 | 0 | 0 |

合计 101 例命中（cand2 仅 11 例）。定位=筛子不作判据；应期维词表覆盖不到逐年吉凶对位（该维问题由评审/judge 层揭露，见 B.6-F2）。

### B.2 抽样（n=30）

- 强制 24 例 = L2 违规 14 例 ∪ 规则锚 cand2 16 例（重叠 6；抽样后词表 duohun 修正使 cand2 收敛至 11，样本不再重抽——多收 5 例作高危覆盖保留）；
- 分层补足 6 例：财 verdict 分组（巨富/富/小康/平/贫/破财/凶）× 官命（是/否）空格优先（seed=20260818）；
- 名单：`output/t3_s1/sample30.json`。

### B.3 第二层：v4-pro 评审 30 例（实例 A，单盲）

材料四轮补全史（评审质量自身教训，r1-r3 留存 `review30.round*.jsonl` 备查）：r1 max_tokens 不足 →
r2 补 yingqi_subj 全键+liunian_analysis → r3 补 hunyin duohun/dushen → r4 补 liunian 逐年 `overall` 吉凶总判。
**r4 为采信版本**——每轮补料都消除一类评审自身误判（如 cj-1209 婚姻/应期曾被误判翻转，补料后纠正）。

r4 评审分布（5 维 × 30 例 = 149 有效格）：

| 维 | 0 忠实 | 1 放大/缩水 | 2 翻转 |
|---|---|---|---|
| 财命 | 25 | 5 | **0** |
| 官命 | 25 | 5 | **0** |
| 职业 | 18 | 3 | **8** |
| 婚姻 | 29 | 1 | **0** |
| 应期 | 28 | 1 | **1** |

- 翻转 9 格 / 9 例（30%）；放大缩水 15 格 = **10.1%**（线 ≤20% ✅）。
- L2 高危 14 例中翻转 2 例（cj-1209、yx-贫打工不赚钱无，均职业维）。
- 翻转 8/9 集中**职业维**：①引擎「无明确倾向」（scores 全 <6 阈值）被断言具体职业 5 格；②叙述主荐桶 ≠ 引擎 primary 桶 3 格（zj-图书管理员 merchant→军警、cj-贫一生受穷 merchant→文职、yx-贫打工不赚钱无 merchant→执法司法）。

### B.4 第三层：v4-pro judge 281 例（实例 B，隔离）

judge 全量分布（1405 格）：

| 维 | 0 | 1 | 2 |
|---|---|---|---|
| 财命 | 255 | 23 | 3 |
| 官命 | 276 | 4 | **0** |
| 职业 | 190 | 29 | **62** |
| 婚姻 | 260 | 20 | 1 |
| 应期 | 227 | 40 | 14 |

### B.5 一致率校准（30 例重叠，逐格）

- **总一致率 127/149 = 85.2%**（线 ≥85% 踩线过）；分维：财 23/30、官 26/30、职 22/29、婚 27/30、应 29/30。
- **翻转召回 6/9 = 66.7% < 100%** → 协议硬性不满足。
- **采信判定：以评审样本为准，judge 降级为筛子**（judge 全量数只作排查线索，不作正式指标）。
- 分歧模式：judge 在「附加警示类叙述」上系统性偏严（操作员抽审：judge 财命 3 格+婚姻 1 格全为假阳——方向忠实仅附加「防破财/闹离」类警示，引擎 summary 本身含对应信号）；评审在职业维偏严但方向可查。

### B.6 达标判定

| 指标 | 达标线 | 实测（评审样本，采信） | 判定 |
|---|---|---|---|
| 语义翻转 | ≤1/30 且 L2 高危零翻转；≥3 例一票否决 | **9/30（30%），L2 高危 2 例** | ❌ **一票否决触发** |
| 放大/缩水 | ≤20% | 10.1% | ✅ |
| judge 校准 | 一致率 ≥85% 且翻转召回 100% | 85.2% / 66.7% | ❌ judge 降级筛子 |

操作员裁决注记（不改变协议判定，供量刑）：9 翻转格中 5 格为职业「无倾向→断言」类——叙述方向与引擎
scores 顶桶/guanming 主行业**同向**（弱信号断言，量表字面=2，非反方向）；真反方向翻转 3 格全在职业维
（merchant 被叙述成军警/文职/执法）；应期 1 格为淡化非纯颠倒。**财命/官命/婚姻三维经评审+judge 双重验证零真翻转**。

### B.7 系统性发现（S1 层面）

- **F1 职业维无锚（主因）**：财命有 `_tier_anchor`、官命有二元锚，职业维 prompt 无任何锚定机制——引擎 abstain（scores<6）时叙述自由发挥（judge 标记 62/281≈22%），或拿 guanming 行业/scores 次桶当主荐。62 例职业翻转格清单见 violations.md 第二部分。
- **F2 应期维吉凶套话**：叙述不逐年对位引擎 `overall`+反局表，泛化为「近年多反局，皆有是非」或「晚景渐佳」——judge 标记 14 翻转格+40 软格；评审样本内 1 翻转+1 软。规则锚层对此维失明（词表覆盖不到逐年对位）。
- **F3 婚姻维残留**：材料补全后评审 0 翻转 1 软，judge 20 软格多为「引擎好+附加独身/闹离信号」（引擎 summary 自带同向信号，忠实度边界），危害低。

---

## C. 产出清单

- **S1 评估报告**：本文件。
- **payload 保真检查表**：§A.1（机读：`output/t3_s1/payload_fidelity.json`）。
- **语义违规清单**：`output/t3_s1/violations.md`（评审 24 格全证据 + judge 80 翻转格筛子清单 + 操作员裁决注记；机读：`calibration.json`）。

## D. 对飞书集成的 go/no-go 建议（T3 维度）

| 维度 | 判定 | 依据 |
|---|---|---|
| payload 结构层 | **GO**（带 1 项 P1） | 37/38 键零扭曲；dayun_analysis 死键=P1 信息缺口（不阻塞集成，但应期维 LLM 无大运数据——修复决策须用户拍板：摘死键 or 引擎补供） |
| S1 语义层 | **NO-GO** | 协议一票否决已触发（评审样本翻转 9/30≥3，L2 高危 2 例非零） |

**综合建议：飞书集成暂缓至 prompt 迭代 5 复验后。** 迭代 5 候选条款（只吃 trainset）：
1. 职业维锚定（同 `_tier_anchor` 机制）：primary 非空 → user prompt 注入「主荐桶=X，叙述主荐不得离桶」；primary 空 → 「引擎未定职业倾向，只许说'倾向不明'，禁止断言具体职业」；
2. 应期维锚定：liunian 逐年 `overall`+yunfan 反局年份表注入 user prompt，禁止「近年皆有是非/晚景渐佳」式无对位套话；
3. 复验 = 重跑批（谷段 v4-flash）+ 本协议三层漏斗重测，达标线不变。

不阻塞项（随集成批顺手带）：dayun_analysis 死键处置、rescore glob 顺序隐患、guanming G6 论据 scrub 备案。

## E. 成本实测（全谷段，price_tier=offpeak 核验）

| 项 | 成本 |
|---|---|
| 评审 30 例 ×4 轮（r1-r3 材料迭代作废 + r4 采信） | $1.072 ≈ ¥7.72 |
| judge 281 例 ×1（含 16 例重试） | $1.880 ≈ ¥13.54 |
| **合计** | **$2.95 ≈ ¥21.3**（授权额度 ¥30-75 内；另 r1 首轮失败调用 ~$0.03 未入档） |

注：评审 4 轮中 3 轮为材料盲区迭代（每轮都抓到评审自身误判类），若一轮到位成本可压至 ¥16 内；
该经验已固化进 `_t3_eval.py` 材料组装（yingqi 全键/duohun/overall 三件套）。
