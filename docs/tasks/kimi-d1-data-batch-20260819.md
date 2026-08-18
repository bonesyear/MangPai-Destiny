# D1 数据批 · gold 修正 + 锚卫生（2026-08-19）

> 用户已批准。来源 = 第三轮审查 T1 gold 复核（docs/kimi-review3-t1-gold-20260818.md + output/t1_gold_review/ 原始产物：result_*.json / v4pro_verdicts.json / master_table.md）。
> **本批性质：纯数据批，零引擎代码改动。** 改 cases.yaml / calib_assertions.yaml 的标注与 source 锚，然后验证。

## 任务清单

### A. gold 标注错 5 条（T1 复核定案，含 v4-pro 终审）

**A1. calib_assertions.yaml `zhenbao-05` 官命**（现值 `level: 4`）→ `level: 3`
- 书锚：mingli-zhenbao-50qi.txt:157「官职升到头，居厅级之职」；现行口径 L3=厅级-省部级、L4=总理-元首级（duan-shi-lixiangxue-yanjiu.txt:6103-6104）；同文件阎锡山（省部级）gold=3，厅级反标 4，文件内自相矛盾
- note 相应改为「厅级」口径

**A2. calib_assertions.yaml `zhenbao-05` 层功**（现值 `level_min: 3, level_max: 4`）→ `level_min: 2, level_max: 3`
- 书锚：同案例「伤官与官不紧贴，故官职不大」；L4 无书据

**A3. calib_assertions.yaml `zhenbao-23a` 层功**（现值 `level_max: 1`）→ `level_max: 2`
- v4-pro 终审（v4pro_verdicts.json）：流年破财不能定原局层功为贫；书有家底可破、地委书记贵人相助、郝断后续有转机（mingli-zhenbao-50qi.txt:761-765），至少小康，应 L2 非 L1。engine 实测 level=3

**A4. trainset cases.yaml `cj-处级-5` 财命**（现值 `富·申运发财`）→ `小康·申运发财`
- 书锚：mangpai-chuji-minglixue.txt:5635-5643「开始发财。处级干部。当然财不会是太多吧」——v4-pro 两跑一致裁标注错。engine 实测 tier=小康
- 注意 verdict 字符串格式保持一致（方向·事件）

**A5. trainset cases.yaml `cj-足球` 财命**（现值 `小康·收入很高`）→ `富·收入很高`
- 书锚：mangpai-chuji-minglixue.txt:5797-5805 两处「说明他收入很高」（国家队球员）；v4-pro：小康与「很高」矛盾，巨富无据 → 富。engine 实测 tier=巨富

**A6. trainset cases.yaml `cj-老总` 官命 加注不改值**：gold=否 维持（v4-pro 裁「维持两可」），在 case 的 verdicts 或注释处加口径注「企业高管是否算官」——书原文「企业里的官/管钱的官」与「大企业老总」并存（chuji:3262-3270），未明体制偏否。

### B. source 锚漂移修正 15 处（引文逐字属实，仅锚点偏 30~300 行）

统一修锚：把 source 行号核正到实际位置。修正前用 grep 核证书原文（关键词定位），不要裸改。

| 案例（trainset cases.yaml） | 维度 | source 现值 | 实际位置 |
|---|---|---|---|
| famous-阿炳 | 职业 | yanjiu:11430 | yanjiu:11128-11270 |
| famous-迈克尔杰克逊 | 职业 | yanjiu:12570 | yanjiu:12344 |
| reg67-公安 | 职业 | lixiangxue:9535 | lixiangxue:9376-9378 |
| reg67-伤食当财 | 财命 | lixiangxue:7409 | lixiangxue:7280-7286 |
| reg67-带帽银行副处 | 职业 | zhongji:4077 | zhongji:3985-3993 |
| reg67-普例4千万 | 财命 | lixiangxue:6379 | lixiangxue:6267-6274 |
| reg67-普例5酒店主管 | 财命 | lixiangxue:6400 | lixiangxue:6287-6297 |
| reg67-合例一富命 | 财命 | lixiangxue:6807 | lixiangxue:6692 |
| reg67-财制印刑警 | 职业 | lixiangxue:3931 | lixiangxue:3843-3852 |
| reg67-外贸商 | 财命 | lixiangxue:2683;7484 | lixiangxue:2635/7358 |
| famous-索罗斯 | 财命 | yanjiu:11830 | yanjiu:11693-11743 |
| reg67-合例八暗合 | 职业 | lixiangxue:6909 | lixiangxue:6788 |
| reg67-制例二 | 财命 | lixiangxue:6594 | lixiangxue:6482-6486 |
| reg67-生例二经理 | 职业 | lixiangxue:6692 | lixiangxue:6575-6583 |
| cj-县长-3 | 官命 | chuji:3694 | chuji:5721 + yanjiu:7858（锚选择不佳，官断实出自此两处） |

多锚 source（`a:NNN;b:MMM` 形式）逐段核正。若有顺带发现的小偏移（如 cj-贫穷命一生无作 chuji:1236 实 1244、yanjiu:6477 实 6491）一并核正。

### C. raw_quote 张冠李戴 1 处

**trainset cases.yaml `cj-贫穷命一生无作`**：raw_quote 中「伤合印，伤主技术，表示有偏门的技术。没有功」为 chuji:1306 **下一案例**卜文，删除该段。剩余引文（chuji:1244「个穷命，一生无作为…」+ 理象学/研究版「故是个穷命，一生没有什么作为，无妻无子」yanjiu:6491 / duan-shi-lixiangxue.txt:6414）保留，verdict 本身有据。source 同步核正（见 B 节末）。

### D. calib `zhenbao-10` dayun 疑误录核验

- 现状：calib_assertions.yaml zhenbao-10 `dayun: [戊, 寅]`
- 书原文（mingli-zhenbao-50qi.txt:313-315）：「郝先生给他断到：'你应该是个公检法的干部，９８年有调动之喜。'……因巳火为用神，戊寅年寅刑巳，动火而调动」——**戊寅 = 1998 流年，非大运**；书中未给此人真实大运。
- 修正方案（二选一，用 calib 回归实测决定，gold 忠实优先）：
  - (a) 移 dayun → liunian 增加 [戊, 寅, 1998]（最忠实书，与应期 note「戊寅调动」呼应）
  - (b) 只删 dayun 字段（保守，脚本对 dayun 缺省容错）
- 改后重跑 calib 核验 zhenbao-10 各维度判定不恶化

## BEFORE 基线（Hermes 已实测，勿重跑）

- calib_assertions.py 常驻回归 **4 条**：zhenbao-01/官命、zhenbao-05/官命（is=True lv=2 vs gold lv=4）、zhenbao-05/层功（level=2 vs gold [3,4]）、zhenbao-14a/财命
- trainset blind_eval（n=294）：官命 96✅/0⚠️/19❌ 83.48%、财命 58✅/44⚠️/11❌ 51.33%、职业 40✅/12⚠️/33❌ 47.06%
- heldout 基线：snapshots/20260818_fb.json（或当前最新 heldout 快照）

## 预期 AFTER（T1 复核模拟值，实测为准）

- calib 常驻回归 **4→2**：zhenbao-05/官命 ❌→⚠️（lv=2 vs gold lv=3）、zhenbao-05/层功 ⚠️→✅（level=2 ∈ [2,3]）；余 zhenbao-01/官命、zhenbao-14a/财命维持引擎错
- trainset 财命 **51.33%→52.21%**（59✅/44⚠️/10❌：cj-处级-5 ⚠️→✅、cj-足球 ❌→⚠️）；官命 83.48%、职业 47.06% 不变
- heldout 零翻转零抖动（本批不碰 heldout gold）

## 验证步骤（fast→slow，引擎零改动故全量应秒过）

1. `python3 mangpai/tests/calib_assertions.py` → 回归 4→2 且无新增
2. `python3 mangpai/tests/heldout/blind_eval.py --trainset-only --out snapshots/20260819_d1.json` → 财 52.21%±、官/职不变
3. `python3 mangpai/tests/heldout/blind_eval.py --out /tmp/d1_full.json --baseline <最新heldout快照>` → heldout 零翻转
4. `python3 mangpai/verify_mangpai.py`（432）+ `python3 mangpai/verify_dayun.py`（70）+ `python3 -m pytest mangpai/tests/ -q`（全绿）
5. 更新 `docs/knowledge-base.md`：§0 成绩表 trainset 财命 51.33→52.21（若表格含此数）、§9 baseline 指针 → 20260819_d1.json（查 R4 教训：KB 基线指针曾指旧文件）；D4 处置结论写备案
6. 报告：改动文件清单 + 逐条 gold 修正对照（旧值→新值）+ calib/trainset/heldout 前后数字 + 新增快照路径

## 铁律

- **零引擎代码改动**（mangpai/objective、mangpai/subjective、engine.py 一律不碰）；只许改 cases.yaml / calib_assertions.yaml / docs/knowledge-base.md
- **不碰 heldout**（cases.yaml 只改 trainset 部分；heldout/cases.yaml 禁改）
- 每处修改须以书原文核证（grep 关键词定位），禁止凭记忆改值
- **不要 git commit**，完成报告后留给 Hermes 逐条验收
