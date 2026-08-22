# 第五轮审查统一修批规划（V5 收官批升级：待修清单 → 排期）

> **【已收官 2026-08-22】F1（f3d3e5e 并行落地）/F2/F3 全部落地清零；第六轮发现及修批 G 排期见接替清单 `docs/tasks/review6-fix-backlog.md`。**
> 前身 = V1/V2/V6 后建立的待修清单；V5（2026-08-21）并入 V3/V4/V5 新发现并按依赖排期。
> 发布判定：**NO-GO**——F1+F2 落地并复跑六件套全绿后转 GO；P2 不阻塞发布。
> **认领状态（2026-08-21）**：F1 批认领 #1-6（含 #6 丁眼锚注，随代码批落地）；F2 批 = #7-10 **本批已落地清零**（锚注/行号/措辞/docstring + KB/CHANGELOG/收工五轮入档，见 CHANGELOG 2026-08-21 条）；F3 批认领 #11-15（max_tokens 8192/_self_check 人民币口径/isinstance guard/S7 统一/L2 拒答误报窗）。

## F1 发布闸修批（代码，P0+P1，一次六件套验收）

| # | 级 | 项 | 位置 | 修法 |
|---|----|----|------|------|
| 1 | **P0** | 免责声明两路径全缺（V4 P0-1；V5 复核全仓 0 命中） | feishu/formatter.py 报告尾、subjective/llm_channel.py format_reading 尾（飞书 HELP 可带） | 各加一行固定免责语（「仅供参考，不构成决策依据」） |
| 2 | **P1** | `Tuple` 未导入，≤3.13 环境 import 即崩（V2/V3/V6 三源实锤；V5 全仓扫描仅此一处） | objective/zuogong_detect.py:13（用在 :997） | `from typing import ... Tuple` 一词 |
| 3 | **P1** | lark_md 不支持 `- `/`> `/`---` 字面残留（V2 P1-2；V5 复核仍在） | feishu/formatter.py:49-50、service.py:74 | 去三符前缀（`**` 加粗已够用） |
| 4 | **P1** | mark 模式死亡词命中仍展示原文仅附注（V4 P1-1） | llm_channel.py render_structured_reading | 死亡词命中升 reject 级（该维降级引擎直出/不展示） |
| 5 | **P1** | 出生信息外发 DeepSeek 无告知（V4 P1-2；V5 复核 HELP 无字样） | feishu/router.py HELP | HELP/首次交互告知「排盘数据提交第三方大模型」，或 FEISHU_USE_LLM=0 默认关 |
| 6 | **P1** | xiangmao「丁=眼之象」marker 无锚注（V1 P1-1；V5 复核 :154 仍无锚） | subjective/xiangmao.py:154 | 补锚注一行（zhongji:2122-2147 / gaoji:15337 / lixiangxue:1777） |

## F2 文档清零批（零行为，随 F1 或紧随其后）

| # | 项 | 位置 |
|---|----|------|
| 7 | zhongji:4179→4180 行号偏 1（V1 P2-1；qianyi.py 5 处 + 测试 docstring） | subjective/qianyi.py:12/20/35/177/183 |
| 8 | 「结构同构」措辞失准（一合一冲，立论本身成立）（V1 P2-2） | qianyi.py:20-21 |
| 9 | docstring「40 个 selector」→41 + 测试函数名 test_school_has_40_selectors（V6 P2-1） | subjective/__init__.py:4、tests/test_subjective.py:33 |
| 10 | **V5 新漂移 D-V5-1**：五轮审查 V1-V5 结论入档 KB/CHANGELOG/收工记录（当前零条目） | docs/knowledge-base.md、mangpai/CHANGELOG.md、收工记录 |

## F3 健壮性批（P2，可与 F1 并批）

| # | 项 | 位置 |
|---|----|------|
| 11 | bot 非 dict body 裸 TypeError（V6 P2-3） | feishu/bot.py:67 前加 isinstance guard |
| 12 | S7 非预期异常回用户裸 `str(e)`，与 E5 脱敏口径不一（V2 P2-1；V5 补录） | feishu/bot.py:54 |
| 13 | max_tokens=4096 可截断致 JSON 解析失败（V4 P2-1） | llm_backend.py:93 → 8192 |
| 14 | _self_check 成本断言仍旧美元口径 0.44/1.32，跑自检即挂（V4 P2-4；V5 复核仍在） | llm_backend.py:170 |
| 15 | L2 死亡词 substring 误报合规拒答句（复述「寿数」记违规，污染口径）（V4 P2-2） | llm_channel.py _l2_enum |

## 备案不修 / 缓议

- client.send()/build_content('post') 生产零调用（V6 P2-4，API 面预留，不删）
- 断网双发送失败零反馈（V2，基础设施级，外部监控兜底）/ 非文本消息静默（建议回 HELP，不阻塞）
- compute 后台线程无上限（V2 P2-3；V5 补录；bot.py:95 ponytail 注释已认领部分 ceiling，量级上前置反代）
- judge prompt 未同步迭代 5「倾向性参考」许可（V3 F-V3-2，下轮评审/judge 前同步）
- @bot `<at>` 前缀解析（V2 P2-2，待真实群验证后再修）
- unemployed/laborer 桶被叙述成「无倾向+宜安稳」（V3 F-V3-1 真翻转残留，zhenbao-23a）——下轮 prompt 迭代补 `_zhiye_anchor` 锚定 + S1 复测，非发布阻塞
- 维度交付口径（已裁定）：zinv/qianyi/xiangmao 保持特征层不进五维叙述；若未来进叙述需先立 LLM 红线 + S1 复测

## 执行序

F1（P0+P1 六项）→ F2（文档清零）→ 六件套全量复跑 → **发布 GO**。F3 可并 F1 或紧随；备案项不排期。
