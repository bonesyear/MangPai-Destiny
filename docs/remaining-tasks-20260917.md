# 收工记录 · H-fix 序列收官（2026-09-17 立项，2026-09-18 收官）

> **后续指针**：P2 官命 fp 窄修簇批已于 2026-09-18 落地收官，收工记录=`docs/remaining-tasks-20260918.md`（本文件保留 H-fix/L0/L1 终态档案职责）。

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

- **当前基线**：`snapshots/LATEST` → `20260918_l1.json`（L1 遗留清理批 2026-09-18 落地换基线；`blind_eval.py --baseline latest` 可解）。
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

- **A3 输出面死字段**（virtual_solid counts / soil wet·dry / 华盖 year_ref）——零消费方零误判风险；删除=正常路径字节变更须换基线，性价比为负。**随未来输出面/payload 精简批顺手**，否则维持。（终判批 2026-09-18 复核维持条件项）
- ~~**feishu 并发两 P1**（后台线程无界 / `_seen_mids` 非原子）——单聊影响低，群聊上线前再修~~ **已关闭（终判批 2026-09-18）**：唯一触发条件=群聊上线，已被用户决策（群聊 bot 不做）撤销；单聊场景实际风险低于阈值。若未来重启群聊 bot，随重启一并激活修复。

### 已办 · L1 遗留清理批（2026-09-18 落地，单批两阶段一次换基线）

> 详账=backlog 文末「L1 遗留清理批」节；快照链=`snapshots/README.md`；基线推进=`20260918_l1.json`。

- **阶段甲·零输出项（5 项全落地，blind vs hfix7 零翻转零抖动）**：B2 liunian 入口守卫（truthy 非 list/dict → `EngineInputError`，注入测试 3 测）/ B3 `_auto_liunian_injected` `__init__` 初始化+方法开头重置（复调哨兵红→绿）/ B4 冗余+死块删除（外层承重守卫保留）/ C2 DISCLAIMER 单源化（文本逐字一致确认，纯代码统一零抖动）/ C3 `test_snapshot_hygiene.py`（首战抓出 e3/gap2 两快照 note 空，已补录）。
- **阶段乙·输出变更项（抖动全归因后一次换基线）**：B1 xiangfa_ops 排序化 4 处 + **同族补漏 frozenset join 2 处**（`gongmen_wuzhi.py:266`/`zhiye.py:552`——三 seed 对拍实测抓出，B6 关闭裁定的 join 消费漏网）/ C1 zaihuo 官杀 label 修正（计数不动）。
- **验收**：payload 特征 JSON 509 例 seed 0/7/42 全一致（B1 核心价值达成）；抖动归因白名单外 0 路径（xiangfa_ops/zaihuo-chehuo/zhiye-lawyer/gongmen/narrative 五域全设计内）；评分字段零翻转；六件套全绿（pytest 1066+1xf）。
- **下批衔接**：L1 已换基线，**P1 官命检测簇批已于 2026-09-18 落地**（从 `20260918_l1.json` 起跑，基线推进 `20260918_p1.json`——新检测面×2（A8 支杀化印/A19 食合官支）+新消费边×2（A11 贼捕制印/G9 扩展），trainset 官 96→100✅ 全预注册、heldout 三维零翻转零抖动、财/职零翻转、六件套全绿；预注册=`docs/kimi-p1-guanming-prereg-20260918.md`，详账=backlog P1 节）。**P2 官命 fp 窄修簇批亦于 2026-09-18 落地收官**（基线推进 `20260918_p2.json`，trainset 官 100→102✅，收工=`docs/remaining-tasks-20260918.md`）。**下批=P3**（财命残簇批 A4/A12/A13，方案 `kimi-engine-precision-plan-20260918.md` P3 节，从 `20260918_p2.json` 起跑）。

### 待办 · D 真实凭证冒烟（上线 checklist #3，事件触发）

执行项非代码项（review7 已定性：仅存盲区=真实凭证冒烟/群聊 @bot，执行项非审查缺口）。前置：真实飞书企业自建应用凭证（`FEISHU_APP_ID`/`FEISHU_APP_SECRET`/`FEISHU_VERIFICATION_TOKEN`，**不配 Encrypt Key**=README 红线）+可收回调网络环境+DeepSeek API key（LLM 链路冒烟）。**终判批 2026-09-18 更新**：#4 群聊 @bot 已随用户决策（群聊 bot 不做）**关闭**，冒烟范围=**单聊**；拿到凭证后按方案 `kimi-remaining-plan-20260918.md` §C1 九步清单执行（小时级），结果回写上线 checklist 8/8 闭环（当前 6/8 + #4 关闭=7/7 待 #3）。

### 其他备案（维持）

- output/ 批跑脚本 + tests 18 文件 `sys.path.insert`——**保留备案已结案**（H-fix-8：非包/安装化成本高/批跑工具非生产代码）。
- `candidates.json`/`review.txt`/`merged.json`/`dropped.txt` 为构建产物，heldout README 已标注管线口径。

### 后续方向（若重启引擎批，KB §9）

官命 fp 窄修簇 A12-A18 + 检测簇 A8/A11/A19、财命 A13/A4/G5 残簇、职业中医/军警/lawyer 盲区——均须新突破面，旧窄通道已尽。L1 与下个引擎批捆绑=前置批模式（见上）。
