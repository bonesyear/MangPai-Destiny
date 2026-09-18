# 收工记录 · H-fix 序列收官（2026-09-17 立项，2026-09-18 收官）

> H-fix-1~8 全批落地。本文件 = 序列终态 + 剩余待议项汇总（backlog「未删待议」/「待议问题」/v2 计划⏸️节）。
> 详账：`docs/tasks/codehygiene-fix-backlog.md` H-fix 各节；快照链：`mangpai/tests/heldout/snapshots/README.md`。

## 一、H-fix 序列终态

| 批 | 内容 | 快照 |
|----|------|------|
| H-fix-1 | import/typing 崩溃面（3.11/3.14 双绿）+ 轻量抽查 12 条登记 | 20260917_hfix1 |
| H-fix-2a/2b/2c | 异常策略三层：传导/降级/白名单分类，裸 except 103→3（全合规残留）；test_inject_faults 79 测 | hfix2a/2b/2c |
| H-fix-3 | 原子写 19 处 + `tests/_atomic_io.py` + 写入前校验 + llm_channel 免责提级 | 20260918_hfix3 |
| H-fix-4a | 死代码清理：删 advanced/chuangong 模块、死调用/死分支/死变量、cost_cny 改名、8 诊断脚本归档 | hfix4a |
| H-fix-4b | 重复逻辑下沉：shishen/_relation_utils/utils 三公共模块，十神/_ensure_*/_check_pair 单一权威，6 组 O(n²) 循环注册表 | hfix4b |
| H-fix-4c | 局部 import 93→8、循环依赖方向矫正顶层无环、`scripts/check_layering.py` 入库 | hfix4c |
| H-fix-6 → 5 | selectors/engine-keys 契约测试 6 测（48=41+7）→ 大函数拆分三函数逐字等价（sha256 三重对拍） | hfix6/hfix5 |
| H-fix-7 | 评测框架统一：`output/_eval_common.py` 五节 + 11 脚本薄包装，口径对拍全绿 | hfix7 |
| H-fix-8 | 文档/基线同步（本批）：README 数字、快照 LATEST 指针、归档、三件套 | —（引擎零改动，基线不推进） |

- **当前基线**：`snapshots/LATEST` → `20260918_hfix7.json`（`blind_eval.py --baseline latest` 可解）。
- **验证口径**：verify 432+70+64+20 / pytest 1059 passed+1xf / 双 seed 逐字节一致 / 67/famous/calib 零新增回归 / check_layering+check_typing_imports 通过。
- **裸 except 残留 3 处（全合规）**：`feishu/bot.py:53,119`（边界兜底+防重试风暴，刻意）、`verify_heldout.py:51`（失败通道，异常即失败 exit 1）。
- **模块数**：58 → 59（Foundation 2 / Objective 27 / Subjective 30）。
- **引擎判定零改动**：全序列 blind 零翻转零抖动（官 48✅/财 47✅/职 24✅ 保）。

## 二、剩余事项（L0 关闭标记批 2026-09-18 重构）

> 6 项「待议」经评估裁定**明示关闭**（勿再立项）；评估=`~/.claude/projects/-root-metaphysics/memory/kimi-leftover-assessment-20260918.md`，方案=`kimi-leftover-fix-plan-20260918.md`。本批纯文档零代码。

### 已关闭（附理由，2026-09-18 评估裁定）

| # | 项 | 关闭理由 |
|---|----|---------|
| A1 | SHIPAI_DOMAINS/METHODOLOGY | 修批C「留作碎片原文档案」决议在先，4a 待删动议属重复立项（**非待删项**，此前误列） |
| A2 | gongmen_wuzhi 整模块 | 修批A③/F18 锁定决策 + `test_a_llm_redline.py` 哨兵 + `test_key_contract.py` 契约白名单三层防护，删除违输出红线零收益（**非待删项**，此前误列） |
| A4 | jiaoyun `if not span`（:189） | 公开 API `_normalize_dayun_entries` 边缘语义承载（span=0/None→用全表），非死码；删/改皆变公开边缘行为而无收益 |
| B5 | gongliang 4 处自调吞异常 / 13 书例 hua_chengju +1 无命中 | 吞异常 H-fix-2b 已实质处置（安全降级 18 显式化+compute_error 标记，改传导零收益）；13 书例=F6 既有备案非缺陷 |
| B6 | detect_relations 返回含 set | 内部总线键不进 payload/selectors，无序列化泄漏面（2026-09-18 实测三键消费方全安全），消费方排序纪律已够——过度防御型遗留 |
| C4 | magic numbers ~45 处 | v2 计划 ⏸️ 裁定维持；~45 处判定代码换纯可读性风险收益倒挂，相当部分阈值系自造启发式（KB 已备案无书定量） |

### 条件项（不悬置，触发条件随批）

- **A3 输出面死字段**（virtual_solid counts / soil wet·dry / 华盖 year_ref）——零消费方零误判风险；删除=正常路径字节变更须换基线，性价比为负。**随未来输出面/payload 精简批顺手**，否则维持。
- **feishu 并发两 P1**（后台线程无界 / `_seen_mids` 非原子）——单聊影响低，**群聊上线前再修**（v2 ⏸️ 节维持）。

### 待办 · L1 遗留清理批（单批两阶段，半天~1 天）

- **阶段甲·零输出项**（落地后 blind 零翻转零抖动+双 seed 一致，不碰基线）：
  - **B2** `engine.py:577-578` liunian_data truthy 非 dict/list 入口守卫（套 :542-551 既有 isinstance 形态，建议显式 `EngineInputError`）+注入测试；
  - **B3** `_auto_liunian_injected` `__init__` 置 False + `_compute_yunshi` 开头重置双保险（潜伏 bug：生产三通道全为一实例一 compute_all，复调场景当前不存在）+复调哨兵；
  - **B4** 美容删除：`_scan_shengyong` 内层冗余 `if day_wx:`（`objective/zuogong_detect.py:490`，**外层 :348 承重守卫保留**）+ `_prepare_inputs` 死代码块（**`subjective/gongliang.py:431-433`，函数 def :369——行号更正：旧记「engine.py」系误记**）；
  - **C2** DISCLAIMER 单源化：`feishu/formatter.py:17` 改从 `llm_channel._DISCLAIMER_LINE` 导入（feishu→subjective 边已存在，不违分层，check_layering 验证）；
  - **C3** 新建 `mangpai/tests/test_snapshot_hygiene.py`（LATEST 可解/meta 完整/rubric_version 一致/命名规范，纯测试新增）。
- **阶段乙·输出变更项**（blind diff 抖动逐条归因后**一次**换基线）：
  - **B1** xiangfa_ops set 迭代序排序化 4 处（`:336` / `:677` / `:811-813` / `:1090`+`:1096`——`.pop()` 取任意元素是真不确定性源；消费点 sorted，同 M1 既有 11 处先例）；
  - **C1** zaihuo label 修正（`zaihuo.py:319-322`——行号已从 :388 漂移；按实际十神标「正官」/「七杀」可并存；**计数不动**——score/判定零触碰，书锚 gaoji:~14843-14848）。
- **时机条件（居一即独立先做）**：① 近期要跑 LLM 批跑/双 seed 校验且要求 xiangfa_ops 全量输出可复现（B1 唯一活影响——H-fix-7 t3_dump 实证 287 例 features 序差）；② 引擎批排期 >2~4 周且希望清零待议列表。否则 L1 整体等**下个引擎判定批前置位**（L1 先换基线 `…_l1.json`，引擎批从新基线起跑；**拒绝同批合并**——混入文本抖动会让引擎批 diff 归因失焦）。

### 待办 · D 真实凭证冒烟（上线 checklist #3，事件触发）

执行项非代码项（review7 已定性：仅存盲区=真实凭证冒烟/群聊 @bot，执行项非审查缺口）。前置：真实飞书企业自建应用凭证（`FEISHU_APP_ID`/`FEISHU_APP_SECRET`/`FEISHU_VERIFICATION_TOKEN`，**不配 Encrypt Key**=README 红线）+测试群+@bot 权限+可收回调网络环境+DeepSeek API key（LLM 链路冒烟）。随首次上线冒烟窗口与 #4 群聊 @bot 同批执行（小时级），结果回写上线 checklist 8/8 闭环（当前 6/8）。

### 其他备案（维持）

- output/ 批跑脚本 + tests 18 文件 `sys.path.insert`——**保留备案已结案**（H-fix-8：非包/安装化成本高/批跑工具非生产代码）。
- `candidates.json`/`review.txt`/`merged.json`/`dropped.txt` 为构建产物，heldout README 已标注管线口径。

### 后续方向（若重启引擎批，KB §9）

官命 fp 窄修簇 A12-A18 + 检测簇 A8/A11/A19、财命 A13/A4/G5 残簇、职业中医/军警/lawyer 盲区——均须新突破面，旧窄通道已尽。L1 与下个引擎批捆绑=前置批模式（见上）。
