# Kimi 任务：文档数字闸门（check_doc_numbers）——防数字漂移

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md`
2. 本批 = 新建**入库的文档数字校验闸门** + 哨兵 + 归入常驻闸门
3. 汇报 400 字内

## 背景
README / KB 里的「N 模块 / M 验证用例」**已漂移三次**（794→1066→1129→1149，每次加测试就过期，靠人记不住）。刚由主会话手工修到实测值；本批把它**机制化**：测试数一变，闸门立刻指出哪份文档该同步。

## 当前**正确**口径（2026-09-19 实测，作为脚本的基准）
- **pytest**：`1150 collected` / `1149 passed + 1 xfailed`
- **模块数 59**，分层口径（**务必照此口径，否则又错**）：
  - `foundation` = **2** —— 注意在**仓库根**（`/root/metaphysics/foundation/`），**不在 `mangpai/` 下**；递归 `find foundation -name "*.py" ! -name "__init__.py"`
  - `mangpai/objective` = **27**（递归，`! -name "__init__.py"`）
  - `mangpai/subjective` = **30** —— **只算顶层**（`-maxdepth 1`；`subjective/prompts/` 子目录**不计入**，这是 README 的既有口径）
  - 合计 **59**
- **verify 四件套**：432 / 70 / 64 / 20（可校验，但需**不实际运行 verify**（慢）——改为解析各 verify 脚本里的期望总数常量，或标记为"低频项"跳过；你判断哪种可靠）

## 任务 A：新建 `scripts/check_doc_numbers.py`（入库，零依赖）

**校验对象=「权威声明位置」**（**不要全量 grep**——KB 里有大量历史口径如「旧记 1129 均作废」，全量扫会误报）：
1. `README.md` 首行：「…**59** 模块四层架构，**1149** 验证用例全绿（+1 xfail）」→ 正则锚定 `(\d+)\s*模块.*?(\d+)\s*验证用例`
2. `README.md` 验证表：「| pytest（…） | **1149** passed + 1 xfailed | ✅ |」→ 锚定 `\|\s*pytest.*?\|\s*(\d+)\s*passed`
3. `README.md` 架构表：Foundation / Objective / Subjective 三行的分层数字（`| **Foundation** | … | 2 |`）
4. `docs/knowledge-base.md` §1 验证口径行：`pytest mangpai/tests/` **1150** collected（**1149** passed+1 xfailed → 锚定该行的 collected/passed 两个数
5. `docs/knowledge-base.md` §8 工具表的 pytest 行（同上锚定）

**实测来源**（脚本内自己算，不信任声明）：
- pytest：`python3 -m pytest --collect-only -q` 解析最后一行 `N tests collected`；passed 数 = collected − xfail 数（**注意**：别真跑全量 pytest，collect 只要 ~0.5s）
- 模块数：按上面口径用 `pathlib` 遍历计数

**行为**：
- 默认 print 每个「位置 / 声明值 / 实测值 / ✅或❌」，退出码：**全部一致 → 0；任一不一致 → 1**
- `--quiet` 只输出不一致项；`--json` 可选（你判断是否需要）
- **零依赖**（纯标准库 + subprocess 调 pytest collect）
- **不得**把任何凭证/隐私模式写进脚本（本仓已有脱敏闸门，别自己踩）

## 任务 B：归入常驻闸门 + 可选 hook
1. **常驻闸门清单**（`README.md` 的「入仓前的脱敏闸门」节附近、`docs/knowledge-base.md` §8 工具表）加入本脚本 → 变成 **6 件套**（分层 / typing / 键契约 / 防假-green / 脱敏 / **文档数字**）
2. **不算 pre-commit 默认项**（collect 要 0.5s，且只在文档/测试数变动时才需跑）——但请给出**怎么接**的说明（README 一句：`python3 scripts/check_doc_numbers.py`，建议在改了测试数量后跑）

## 任务 C：哨兵测试 `mangpai/tests/test_doc_numbers.py`（先红后绿）
1. 构造临时 README/KB 副本，**篡改数字** → 脚本必须报不一致 + 退出码 1
2. 正确数字 → 通过 + 退出码 0
3. 模块数口径：断言 `subjective` 只算顶层（构造一个含子目录的场景，验证子目录 .py 不计入）
4. 解析函数单测（正则捕获组正确性，含 KB 里「旧记 X 均作废」的历史口径**不得**被当作声明）

## DoD
- [ ] A：脚本对**当前**仓库运行 → 全绿（退出码 0）；篡改任一数字 → 报错（退出码 1）
- [ ] A：口径正确 = 59 模块 / 1150 collected / 1149 passed（与你独立实测一致）
- [ ] B：两份文档的常驻闸门清单更新为 6 件套
- [ ] C：哨兵 4 类全绿（先红后绿）
- [ ] 六件套：pytest 全绿（新增测试计入）+ verify 432/70/64/20 + **blind vs `snapshots/20260918_t1.json` 零翻转** + 双 seed + 分层两件套（含新的脱敏闸门）
- [ ] `git status --short` 核对；提交（**不 push**）
- [ ] 汇报 400 字内（脚本行为 + 哨兵数 + 六件套数字 + 对当前仓库的实跑结果）

## 红线
- 零依赖、纯标准库；不实际运行 verify（慢）；不真跑全量 pytest（只用 --collect-only）
- 不动引擎判定；不修改文档里的**历史口径**（只校验权威声明位置）
- 提交前 `git status` 扫改动范围
