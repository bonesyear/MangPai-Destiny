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

## 二、剩余待议项（勿再立重复项）

### 明示暂不修（v2 计划⏸️节）

- **feishu 并发两 P1**（后台线程无界 / `_seen_mids` 非原子）——单聊影响低，**群聊上线前再修**。
- **magic numbers ~45 处 P2**——可接受后置，明示不修。

### 未删待议（H-fix-4a）

- SHIPAI_DOMAINS/METHODOLOGY（修批C 明议留档优先）。
- gongmen_wuzhi 整模块（engine 键保留=修批A③ 锁定决策，删除违输出红线）。
- 输出面死字段（virtual_solid counts / soil wet·dry / 华盖 year_ref）——须专门输出面批。
- jiaoyun `if not span` 边缘语义。

### 待议问题（H-fix-5 登记，后续卫生批裁定）

1. xiangfa_ops 全量 result set 迭代序随 PYTHONHASHSEED 旋转（存量不确定性，blind 评分零抖动）。
2. `engine.py:578` liunian_data truthy 非 dict → `.get` AttributeError（2a 遗留 P2）。
3. `engine.__init__` 未初始化 `_auto_liunian_injected`（H8 P2，getattr 兜底）。
4. `_scan_shengyong` 嵌套冗余 `if day_wx:` / `_prepare_inputs` 死代码块（逐字等价保留）。
5. gongliang 4 处自调吞异常（H11 已录）/ 13 书例 hua_chengju +1 无命中——维持备案。
6. detect_relations 返回 dict 内含 set，消费方序列化须先排序。

### 其他备案

- `zaihuo.py:388` 正官误标「七杀」label——计数有书锚不动，label 修正=文本变更，延后文本/判定批（修法已给定，backlog H-fix-2a 节）。
- output/ 批跑脚本 + tests 18 文件 `sys.path.insert`——**保留备案已结案**（H-fix-8：非包/安装化成本高/批跑工具非生产代码）。
- H5 P1 formatter.DISCLAIMER 与 llm_channel._DISCLAIMER_LINE 文本重复（统一化=清理面小事）。
- H9 P2 建议项：`test_snapshot_hygiene.py`（快照 meta 链自动校验）未立，留作可选；`candidates.json`/`review.txt`/`merged.json`/`dropped.txt` 为构建产物，heldout README 已标注管线口径。
- 上线 checklist 6/8：#3 真实凭证冒烟 / #4 群聊 @bot 后置，随首次上线冒烟。

### 后续方向（若重启引擎批，KB §9）

官命 fp 窄修簇 A12-A18 + 检测簇 A8/A11/A19、财命 A13/A4/G5 残簇、职业中医/军警/lawyer 盲区——均须新突破面，旧窄通道已尽。
