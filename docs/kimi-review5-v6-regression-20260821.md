# 第五轮审查 V6 · 回归复审批（锚回书/死数据/fuzz）· 2026-08-21

> 范围：只审不改，纯本地零 API（fuzz `call_llm=False`）。任务书 `docs/tasks/kimi-review5-v6.md`。
> 标准：旧归档仅参考，以原著原文 + 当前代码为准。fuzz 脚本 `/tmp/v6_fuzz.py`（易失），
> 报告 `/tmp/v6_fuzz_report.json`。解释器 = 项目口径 /usr/bin/python3（3.14.4）。

## 一、死数据/双轨复查表（R 轮重跑）

| 项 | 结论 | 依据 |
|----|------|------|
| D3 合成层 vs engine dayun | **一致，无双轨** | 两路径同吃 `analyze_dayun_mangpai`；方向逻辑两处实现（bazi_calc.compute_da_yun:708 / dayun_gz_sequence:683）但同口径（阳男阴女顺、性别集合相同、月柱 ±1、8 步）。实证 ×3 盘（1992男/1985女/1970男）：real 与 syn 的 gz 序列逐字相同；合成路径剥 start_age/end_age + age_note 防误锚（`subjective/__init__.py:96-114`），engine 输出零改动 |
| selectors 38→41 新键读者 | **无死键** | 41 键全量经 build_payload→JSON dump 进 LLM user prompt（llm_channel.py:319-323）；`dayun_analysis.*` 被 prompts/mangpai.md:52-67 显式引用；qianyi/xiangmao 按 V1 §三裁定=特征层消费（prompt 不扩系设计，非死键）。test_subjective.py:39 + test_a_llm_redline.py:121 双断言锁 41 |
| E5 feishu client/bot | **无死参数/死分支** | E5 五项（滚动去重/token 锁/123:45 guard/秒位 guard/四柱优先级/500 脱敏/HTTPServer 上限）全部活路径。观察：client.send()/build_content('post') 生产零调用（仅 test_feishu）——client API 面预留，非 E5 新增，见 P2-4 |
| 快照链结构 | **连续** | d1→d2→d3→d6b→e3→gap1→gap2 七件齐全，rubric_version 同版（v8-20260808），_meta.git_sha 父提交惯例链式吻合（gap2.sha=854bbf2=gap1 commit，gap1.sha=7c2109c=e3 后 CHANGELOG commit，e3.sha=5b8ace7=E2 commit） |

## 二、fuzz 报告（T 轮重跑，seed=20260820）

主链（同 T0 口径）：随机日期 1900-2100 × 性别池（男/女/乾/坤/male/female）× 经度 73-135，
`calc_mangpai_full → compute_all → build_payload → render_structured_reading(call_llm=False)`：

| 指标 | V6 结果 | T0 对照 |
|------|---------|---------|
| 样本 | 800 | 800 |
| 硬崩溃 | **0** | 0 |
| 异常慢（>5s/例） | **0**（全批 135s，~0.17s/例） | 0 |
| 异常输出（四柱畸形/payload 空/render 坏） | **0** | 0 |
| 静默模块失败（_safe_compute warning） | **0** | 0 |
| engine result 键数 | 恒 **48**（800/800 无抖动） | 恒 45（+3=zinv/qianyi/xiangmao，与批次一致） |
| payload 键数 | 恒 **41**（无抖动） | 恒 38（+3，selectors 同步） |
| dayun_analysis/qianyi/xiangmao 缺失 | 0/0/0 | — |

新增面覆盖：

| 面 | 用例 | 结果 |
|----|------|------|
| D2 入口 guard | 34（年 1899/1900/2100/2101、性别 None/''/未知/男人/六合法、lon None/abc/nan/inf/±181/±180/73、月 0/13、日 0/32/闰 2-29、时 24/-1/23:59/0:00、分 60/-1） | **34/34 期望命中**：界外一律 ValueError 带说明，合法边界跑通；T0 三项 P1/P2（性别缺省/裸 KeyError/lon None TypeError）全部不复发 |
| E5 HTTP 面 | 17（encrypt 体/url_verification 对错 token/空体/非 dict/缺 message/缺 mid/content 非 JSON/非 text/重复 mid/去重滚动 2100 灌入 + 真 HTTP：非法 JSON/超 1MB/合法 challenge/错 token） | 全兜住：401/413/脱敏 500/challenge 200；去重窗口滚至 2000 封顶不清空。观察：非 dict body 抛裸 TypeError（HTTP 层兜成脱敏 500，见 P2-3）；空 body→401（无 token 拒绝，合理） |
| qianyi/xiangmao marker 盘 | 6 触发 + 1 反例（月日冲申月寅日/日时合子日丑时/马临年时申年寅时/金水伤官辛日癸透/活木见火甲日丙透/秀气透干甲日时丙寅/全土反例） | **7/7 通过**：marker 全命中、payload 双键齐、反例不炸（首跑 6 FAIL 系脚本取错输出键，按 qianyi.py:245/xiangmao 实际形状复测全 OK） |

## 三、锚点独立回书表（E3/E4 改的锚）

| # | 锚 | 回书结果 | 判定 |
|---|----|---------|------|
| E3-1 | 县长-3 母逝补锚 chuji:3702 | 3702 行逐字：「亥运，水盛，壬戌年，戌母到位，被原局酉穿倒，此年母去逝。」= raw_quote 引文 | **A** |
| E3-2 | 刑警区间 3851→3852（zhongji:3843-3852） | 3843 造（丁未己酉癸巳丁巳）、3845「刑警队长…」、**3852 末句「行己酉运提升，辛巳年又提升。」**——扩一行后不再截末句 | **A** |
| E3-3 | zinv 锚 14374→14372-3 | 14372-14373 跨行逐字：「运岁填实开 / 墓库，或有转机续灯炉」=「运岁填实开墓库，或有转机续灯炉」（OCR 折行）；14008「运岁开库或填实，或有转机一线中」同核 | **A** |
| E3-4 | test_d6b 案例八 乾→坤（gaoji:14242） | 14242 行逐字：「坤造壬辰癸卯丙辰戊子」——书明写坤造，测试用造与性别（女）一致 | **A** |
| E4-1 | 穿引动改注 gaoji:14295-14312 | 案例十一书机制=「日支未土穿害月令子水七杀」+断语「运岁引动穿害力」逐字；其岁运己丑（无午）/辛巳（无寅）不构成六穿——注释「不触发本实现」属实，配对偏松备案准确 | **A** |
| E4-2 | 穿引动直锚降权 gaoji:17465-17484 | 「巳火到位穿寅木」（应期节）+「疑案例有误或指他刑」（书自承）逐字；机制=岁运支穿原局子息支，与本实现同构；抽查备案：14122「后巳运，巳亥冲，次子亦亡」逐字、17783-17810 确系同案例（辛巳庚寅辛亥戊戌）重出 | **A** |

**6/6 全 A，无 B/C。**

## 四、发现清单

**P0（违书/崩溃=阻塞）：0 条。**

**P1：0 条**（死数据零复生：D3 无双轨、41 键无死键、E5 无死分支）。

**P2：4 条（均为文档/潜伏级，零行为影响）**
- P2-1 `subjective/__init__.py:4` docstring 陈旧：「40 个 selector，D6b 追加 zinv、缺口批1 追加 qianyi」——实际 41，漏 xiangmao；`test_subjective.py:33` 函数名 `test_school_has_40_selectors` 同陈旧（断言已是 41）。改注即可。
- P2-2 `objective/zuogong_detect.py:997` 模块级注解 `List[Tuple[...]]` 但 typing 未导入 `Tuple`（:14 只导 Dict/List/Optional/Set）——Python 3.14 惰性注解（PEP 649）掩盖，**3.11 下 import 即 NameError**。项目口径 3.14 零影响，环境漂移即炸；typing import 加 `Tuple` 一词可清。
- P2-3 bot.handle_event 对非 dict body（None 等）抛裸 TypeError——经 HTTP 层兜成脱敏 500 不崩溃，仅直连调用方见原始异常。一行 isinstance guard 可清。
- P2-4（备案）feishu client.send()/build_content('post') 生产零调用（仅测试）——client 主动发消息 API 面预留，非 E5 新增，不删。

**备案（非问题）**：方向逻辑两处实现（compute_da_yun / dayun_gz_sequence）同口径同结果、docstring 互引，实证一致——非双轨漂移，不并。

## 五、发布判定（方案 v2 六条之 V6 三条）

锚回书全对 ✅（6/6 A）· 死数据零复生 ✅ · fuzz 零崩溃 ✅ → **V6 通过**。
