# 收工记录 · 2026-09-18（S2 对外文档批落地 · 分享目标「看得懂」部分——纯文档零代码）

> 接续本文件 S1 节（其「文档待修清单」6 项，本批全清）。本批 = 分享可用性修批 S2（评估报告 `~/.claude/projects/-root-metaphysics/memory/kimi-shareability-assessment-20260918.md` S2 方案节；任务书 `docs/tasks/kimi-s2-docs.md`）。详账=`docs/tasks/codehygiene-fix-backlog.md` S2 节。**零 `.py` 改动、零基线推进**（纯文档批，同 F2/E2 先例，六件套不必跑）。

## 一、S2 落地终态

| 项 | 内容 |
|---|---|
| `.env.example`（新建，仓库根） | 全部配置项 **16 项**（`MANGPAI_LLM_*` 八项 + `MANGPAI_USE_LLM` + `DEEPSEEK_*` 兼容×2 + `FEISHU_*`×5），每项带用途/缺省/必填注释，**零真实凭证**（占位符） |
| README 三节 | ①**安装**：Python 3.10+（3.11/3.14 实测）+ 依赖三分层（引擎核心零依赖 / pyyaml 工具链 / sxtwl·anthropic 可选）——修正「纯标准库」误导；②**配置你自己的 LLM**：配置总表 + DeepSeek/OpenAI/Ollama/vLLM 四示例 + `THINKING=0` 适用场景 + 关闭 LLM（`MANGPAI_USE_LLM=0`/不配 key）；③**完整流程示例**：`calc_mangpai_full` → `render_structured_reading` 端到端 + CLI demo（标注 cwd 限制） |
| 失实点修正×4 | `README.md` 隐私节开关名→`MANGPAI_USE_LLM`；`privacy-policy.md:78/79/123` 措辞与 S1 能力同步（可替换成真+具体操作路径）；`feishu/README.md` 变量表改指新变量+「飞书=可选接入层」；`llm-channel-20260818.md` 补配置链接+「计价表仅 DeepSeek 有效，其他 provider 未计价」+顺带修 `_PRICING`→`_PRICE` 两处 |
| 可复现性自检 | 干净 venv（3.11.15 零安装）按 README 实跑：[A] 引擎 ✅；[B] 无 key 自动降级 ✅；[C] mock 本地端点（127.0.0.1）完整流程 ✅（THINKING=0 剔字段/未计价显示）——**零外部 API** |

## 二、剩余事项

- **下批=S3 CLI 入口批**（可选可缓）：`python3 -m mangpai.cli` 两段式一条命令 + `llm_channel.py:483` cwd 相对路径改 `Path(__file__)` 锚定（本批已文档标注）。
- 分享目标终态：S1（技术可配）+S2（看得懂）落地后，外部使用者可凭 README 三节 + `.env.example` 用任意 OpenAI 兼容 LLM 跑通完整流程——评估报告 B1/B2/B3/B4/B6 阻碍项全清，B5（通用 CLI 入口）待 S3。
- 本文件此前各节所载事项（D 真实凭证冒烟待办、A3 条件项等）原样维持。

---

# 收工记录 · 2026-09-18（S1 LLM 通道配置化批落地 · 分享目标前提批——叙事旁路层，引擎零触）

> 接续本文件 T-教授节。本批 = 分享可用性修批 S1（评估报告 `~/.claude/projects/-root-metaphysics/memory/kimi-shareability-assessment-20260918.md` S1 方案节；任务书 `docs/tasks/kimi-s1-llm-config.md`）。详账=`docs/tasks/codehygiene-fix-backlog.md` S1 节。**无基线推进**（引擎判定零改动、DeepSeek 默认路径零变化，快照链不动）。

## 一、S1 落地终态

| 项 | 内容 |
|---|---|
| 配置项 | `MANGPAI_LLM_BASE_URL/API_KEY/MODEL/THINKING/REASONING_EFFORT/TIMEOUT/RETRIES/ENV_FILE` 八项 + `MANGPAI_USE_LLM` 开关别名（feishu service）；回退链全保现状——未设新变量时 DeepSeek 路径**逐字节一致**（哨兵锁键序级请求体比对） |
| thinking 开关 | `MANGPAI_LLM_THINKING=0` 剔 `thinking`+`reasoning_effort` 两字段（严格 OpenAI 兼容服务 400 对策）；自定义端点 400 报错附设置提示（DeepSeek 错误文本逐字不变） |
| 清私有路径 | `_load_api_key` 改 env 链：两变量 → `MANGPAI_LLM_ENV_FILE`/`~/.env` → legacy `/root/.hermes/.env`（链尾兜底守红线，标注后续主版本移除） |
| 成本估算 | 未知 provider `_estimate_cost`→**None（未计价）**替代误导性 ¥0；format_reading 显示「未计价」；output 批跑工具四处汇总 None 兜底 |
| narrative 处置 | **方案 b 标注遗留通道**（正式通道=llm_channel，`render_hao_narrative` 无生产调用点）：docstring 标注需自配 anthropic SDK+`ANTHROPIC_API_KEY`，哨兵锁定 |
| 六件套 | verify 432+70+64+20 ✔；pytest **1128 passed+1xf**（+15 哨兵全 mock 零外部 API）✔；blind vs `snapshots/20260918_t1.json` heldout/trainset **零翻转零抖动** ✔；双 seed 剥 _meta 逐字节一致 ✔；67/famous 无变化 ✔；calib 常驻 2 条零新增（pytest 覆盖）✔；分层两件套 ✔ |
| 文档待修清单 | **6 项留 S2**（README:89/privacy-policy:78-79,123/feishu README/快速开始+`.env.example`+安装清单/llm-channel 文档链接+计价口径声明/llm_channel.py:480 cwd 相对路径随 S3）——详=backlog S1 节 |

## 二、剩余事项

- **下批=S2 文档批**（必须）：`.env.example` + README 安装/配置 LLM 两节 + privacy-policy 措辞同步 + feishu README 变量表；S3 CLI 入口批（可选可缓）。
- 代码改动未提交（工作树，用户未要求 commit）。
- 本文件此前各节所载事项（D 真实凭证冒烟待办、A3 条件项等）原样维持。

---

# 收工记录 · 2026-09-18（T-教授 财命窄条款微批落地）

> 接续本文件终判批节（其 cj-教授=可立窄条款候选、两道必答题，本批立项落地）。本批 = 引擎精度批·窄条款微批（判定改动批，caiming 消费侧单点，objective/总线零改动）。详账=`docs/tasks/codehygiene-fix-backlog.md` T-教授节；预注册=`docs/kimi-t-jiaoshou-caiming-prereg-20260918.md`；快照链=`mangpai/tests/heldout/snapshots/README.md`。

## 一、T-教授落地终态

| 项 | 内容 |
|---|---|
| 条款 | **日支穿月令财 → 封顶小康**（`caiming.py` `assess_caiming_level` 凶向封顶链后、tier_map 前）：谓词=`pair_in(日支,月令,LIU_HAI)`+月令**本气**五行=日主之财；仅 tier_idx>2 时 cap+追加文本，≤2 完全 no-op；文案避「下浮封顶」（不入凶向直杀链）。书锚 chuji:2379-2384/3678-3681+5995（教授）+zhongji:2322-2323（邢铭芬） |
| 必答题 | ①马云探针实跑：本气口径 False/藏干口径 True（误中证明）→本气口径，famous 红线不触（书自反例 zhongji:2323 即马云结构）；②§7-15 核对：谓词纯结构条件不含身弱/财旺判定，与「身弱财旺 cap」双锚否决无交集（贫穷命实测从弱，命中经由穿财结构自带双锚，只到 ⚠️） |
| 误伤面 | 509 扫本气口径命中 6 例（藏干口径 14 例含马云=终判批口径，差异已登记）；可评分者 ✅变差=0；famous 67 命中=0；李嘉诚/保尔森/奥纳西斯/煤矿谓词全 False |
| 指标 | trainset 财 **61→63✅**（+2 全预注册：cj-教授 ❌→✅/zj-邢铭芬 ⚠️→✅/yx-贫穷命贫困线上 ❌→⚠️改善非✅；M3 噪声带内，CI 下界 44.8%→46.6%）；heldout 三维**零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）；trainset 官 102✅/职 41✅ 零翻转 |
| 归因 | 翻转 3 条全预注册；**文本抖动 1 条**（yx-书法家-2 caiming_adjust 条款文本，设计内）；偏差备案（良性）=预注册预期抖动含佛具/普金，实测两例全量轨岁运反局先行压小康→条款 no-op 零抖动 |
| 六件套 | verify 432+70+64+20 ✔；pytest **1113 passed+1xf**（+6 哨兵，先红 3 后绿 6）✔；blind vs p4 上记 ✔；双 seed 剥 _meta 逐字节一致 ✔；67/famous 无变化（**马云不 REGRESSION**）✔；calib 常驻 2 条零新增（pytest 19 测全绿）✔；check_layering+check_typing_imports ✔；3.11.15/3.14.4 双版本 blind 冒烟剥 _meta 逐字节一致 ✔（blind 链路不触 sxtwl，父会话复跑补拍） |
| 基线 | `snapshots/LATEST` → **`20260918_t1.json`**（README 链总账已补录） |

## 二、残留与剩余事项

- **财命残留 ❌10→8**（KB §6.3 已同步）：cj-教授已清、yx-贫穷命贫困线上 ❌→⚠️ 移出❌清单；余 8 例终判全部原位（终判批/P3 节）。
- 代码改动未提交（工作树，用户未要求 commit）。
- 本文件终判批节所载其余事项（D 真实凭证冒烟待办、A3 条件项、G5/A1 重启条件等）原样维持。

---

# 收工记录 · 2026-09-18（终判批落地 · 本周期正式收官——财 3 例诊断 + 全量终态汇总，docs-only 零代码）

> 接续本文件 P4 节。本批 = **终判批**（纯文档/诊断：diag_case+509 例同构面全扫均为只读分析，零代码改动、零基线推进、零外部 API）。终态汇总=`docs/final-state-20260918.md`（55 例残留终判总表+系统/测试终态+剩余事项全清单）；依据=`~/.claude/projects/-root-metaphysics/memory/kimi-remaining-plan-20260918.md`。

## 一、财 3 例终判（诊断详账=final-state §一）

| 例 | 结论 | 一句话理由 |
|---|---|---|
| cj-装璜（⚠️差1，富 vs 巨富） | **收档** | 不净封顶漏检族属实（`_assess_zhi_jing` 无「用神本身透干」信号，chuji:4755-4766），但窄口径 509 扫：改善 4⚠️ vs 误伤 3✅巨富锚（含 cj-巨富制尽「制尽」书锚正面冲突）+新信号单例孤锚（铁律 4 不达）+须动 gongliang 总线 → 风险收益倒挂。重启条件见 final-state §一.1 |
| cj-妓女（❌，贫 vs 富） | **收档（关闭）** | 书机制=官带财入主位墓不开损夫伤财（chuji:2334）；509 扫可修同构面=1 例（铁律 4 不达）、无双锚、与 N3「主位墓=制忌自消」豁免语义正面冲突、误伤 3✅锚 |
| cj-教授（❌差2，小康 vs 巨富） | **可立窄条款候选（本批不实施，另行立预注册微批）** | 双锚齐（chuji:2375+3674 / zhongji:2316 邢铭芬「穿了财…只能发点小财」）+同构 3 例+✅误伤面 0；预注册必答题=famous-马云 collateral（⚠️→❌ 触 famous 零回归红线）豁免要件+§7-15 口径边界 |

## 二、关闭项落档（本批裁定）

- **G5 破从/A1 反局** → **收档关闭**（理由=方案 A 节四点：收益噪声带内不可证/方向总线全链传导风险/F7-F11 已修尽书锚面/无双锚；重启触发条件=final-state §四，勿再立项）。
- **官 ❌13 / 职 ❌32** → **收档确认**（13/13、32/32 全部已判，逐例理由=backlog P2/P4 节+KB §6.2/§6.1，无遗漏无新面）。
- **feishu 并发两 P1**（后台线程无界/`_seen_mids` 非原子）→ **关闭**（唯一触发条件=群聊上线，已被用户决策撤销；重启群聊时一并激活）。
- **A3 输出面死字段** → **维持条件项**（不关闭不立项；随未来输出面/payload 精简批顺手，触发条件=方案 §C2）。
- **上线 checklist**：#4 群聊 @bot → **关闭**（用户决策群聊不做）；#3 真实凭证冒烟 → **待凭证保留**（范围修正=单聊，九步清单=方案 §C1）；`docs/ops-plan-20260822.md` checklist 已同步。

---

# 收工记录 · 2026-09-18（P4 职业军警新面批落地 · P 系列收官）

> 接续本文件 P3 节（其「下批衔接」已定 P4）。本批 = 引擎精度批 P 系列第四批=**收官批**（判定改动批，objective muku 纯增量检测+zhiye military 窄消费）。详账=`docs/tasks/codehygiene-fix-backlog.md` P4 节；预注册=`docs/kimi-p4-zhiye-muku-prereg-20260918.md`；快照链=`mangpai/tests/heldout/snapshots/README.md`。

## 一、P4 落地终态

| 项 | 内容 |
|---|---|
| 检测面（objective 纯增量） | `muku.detect_ku_zhi_ku(zhis)`：库制库=阳库（辰戌）收/刑 阴库（丑未），阳为制方（收式唯辰、刑=丑戌/戌未、阳冲阴十二支不存在）；**analyze_muku/is_entomb 既有输出零改动**（muku 13 消费方契约不变，F2 先例全量回归=六件套实证零回归） |
| 消费条款（military 单桶，贵气门**外**） | 「库制库·阳制阴（墓用执法象）+6」=检测命中+阴库成双多见（丑≥2 或未≥2，gaoji:2190-2194+案例三双丑/例四双未明文）；墓用结构=格局级做功（:2177-2182）不走贵气门；军警 gating 照旧撤分。书锚 gaoji:2401-2417（警察）+:11747-11756（例四刑杀库）+:11630（丑=阴库公安象） |
| 指标 | trainset 职 **40→41✅**（+1 全预注册=gj-警察墓库；⚠️ 预警带 +2~4 **未达=偏差备案**：书锚仅 2 例同构，铁律4 不为追指标放宽）；heldout 三维**零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）；trainset 官 102✅/财 61✅ 零翻转 |
| 探针与锚 | 军警探针 3/10→**4/10**（军官例四戌未刑开杀库归位）；例二（margin 6）/例九（margin 1）条款结构性不命中逐字不动；yx-科级 collateral 不复现（阴库 0，哨兵锁定） |
| 归因 | 快照字段级 diff 唯一变更=gj-警察墓库；**文本抖动 0**；命中面 12 例全归因（数亿坐牢/qi22 无职 verdict 快照不收、足球/建筑-2/8721/qi50 分升 primary 不变、li139/qi05/li141 gating 撤分——li141=blind 上下文喂运触发岁运反局 gating） |
| 六件套 | verify 432+70+64+20 ✔；pytest **1107 passed+1xf**（+10 哨兵）✔；blind vs p3 上记 ✔；双 seed 剥 _meta 逐字节一致 ✔；67/famous 无变化 ✔；calib 常驻 2 条零新增 ✔；check_layering+check_typing_imports ✔；3.11.15/3.14.4 双版本 blind 冒烟逐字节一致 ✔ |
| 基线 | `snapshots/LATEST` → **`20260918_p4.json`**（README 链总账已补录） |

## 二、P 系列收官终态（四批全落地）

- P1 官命检测簇（官 +4）→ P2 官命 fp 窄修（官 +2）→ P3 财命残簇（财 +2）→ P4 职业军警新面（职 +1）；trainset 官 96→102✅/财 59→61✅/职 40→41✅，**heldout 三维四批贯穿零回退**（官 48✅/财 47✅/职 24✅）。
- 方案单列项=财命 G5 破从/A1 反局（触 classify_strength/zhengfan 总线，高风险单列专项或收档，方案四节已定，本周期不动）。
- 残留：官 ❌13（§6.2）/财 ❌10（§6.3）/职 ❌32（§6.1，军警备案簇警察墓库已清、余收档=backlog P4 节清单，勿再立项）。

## S3 处置（2026-09-18 用户决策）
- **CLI 入口：取消**——用户规划**未来以 web 页面作为入口**（比 CLI 更贴近使用者场景）；届时入口工程另立批。
- **cwd 相对路径修复：已完成**（`llm_channel.py` demo 的 `cases.yaml` 路径 → `_demo_cases_path()` 锚定 `__file__`，与 cwd 无关）+ 哨兵 `test_demo_cases_path_cwd_independent`。
- 剩余（若有）：web 入口工程（未来）；S3 原方案中的 CLI 相关项全部关闭。

## 三、剩余事项

- 代码改动未提交（工作树，用户未要求 commit）。
- 0917 文件所载其余事项（D 真实凭证冒烟待办、A3 条件项、feishu 并发两 P1 等）原样维持，见该文件 §二。

---

# 收工记录 · 2026-09-18（P3 财命残簇批落地）

> 接续本文件 P2 节（其「下批衔接」已定 P3）。本批 = 引擎精度批 P 系列第三批（判定改动批，caiming 消费侧，objective 零改动）。详账=`docs/tasks/codehygiene-fix-backlog.md` P3 节；预注册=`docs/kimi-p3-caiming-prereg-20260918.md`；快照链=`mangpai/tests/heldout/snapshots/README.md`。

## 一、P3 落地终态

| 项 | 内容 |
|---|---|
| 前提复核收档 2/3 | A4 土金伤官怕见官（传导已由 yongshen N1「成势怕见官」severe 条款承担，yongshen.py:879-921；509 例探针 scored 残余=零，b67-过河拆桥富锚具怕见官 facet=反向锚）/A12 体坏（N5 已接入 mingju_xiong，yongshen.py:1682-1684；独眼乞食 ✅，残余=零）——方案 P3 节两项现场核实过时，以码+书为准 |
| 条款实现 1/3（A13 制库基阶落位两条款） | 条款一上限=制库独力上浮封顶富、库同藏官杀（`ku_han_guansha` 新输出字段，「财库加官杀做功能量很大」yx-煤矿 yanjiu:7689-7691）豁免保巨富；条款二下限 sticky=制库在档明财阻断落富不落小康（制例二 lixiangxue:6478-6484「虽也是富命，但远不如前者」） |
| 指标 | trainset 财 **59→61✅**（+2 全预注册，方案带 +2~4 下沿，CI 下界 43.1%→44.8%）；heldout 三维零翻转（官 48✅/财 47✅/职 24✅ 保）；trainset 官 102✅/职 40✅ 零翻转 |
| 翻转明细 | cj-富火运发财数百（巨富→富，chuji:5526-5530「财不大」）/reg67-制例二（小康→富）——全预注册 |
| 文本抖动 7 条 | 条款一 adjust×5（ans06/li222/qi05/cj-市长/famous-李世民）+条款二 li240+gj-入狱一年 tier_static 巨富→富（凶 verdict 评全量轨小康不变✅）——全归因，无白名单外路径 |
| 六件套 | verify 432+70+64+20 ✔；pytest **1097 passed+1xf**（+10 哨兵）✔；blind 快照 `20260918_p3.json` vs p2 翻转 2 全预注册 ✔；双 seed 同 note 复跑逐字节一致 ✔；67/famous 无变化 ✔；calib 常驻 2 条零新增 ✔；check_layering+check_typing_imports ✔；3.11/3.14 冒烟一致 ✔ |
| 富命锚复验 | 李嘉诚/保尔森（zhiku=False 结构性不动）/奥纳西斯（L4 直达不经上浮链）/煤矿（ku_han_guansha 豁免保巨富）全保；M2 七组无失衡恶化（trainset 富组 13✅→15✅ 改善，余六组逐字不动；heldout 七组不动） |
| 红线复查 | 凶向标注只写全量轨：本批不触强制标注段（caiming.py:1883+），静态轨零凶向词新增 |
| 基线 | `snapshots/LATEST` → **`20260918_p3.json`**（README 链总账已补录） |

## 二、偏差备案（vs 方案/预注册）

1. 方案 P3 节「juefa 土金伤官条款在而 caiming 零消费」「体坏信号未接入 mingju_xiong 聚合」两条现场核实**均过时**（N1 条款 K3-294批5 已消费 juefa 分向；N5 K3-294批6 已接入聚合）——A4/A12 收档，证据入预注册 §一。
2. 条款一豁免闸最终取「库同藏官杀」（煤矿书明文「财库加官杀」），弃用初拟「gongliang L4/成势」双闸——L4 闸保不住煤矿（L2）、成势闸分不开富火运（同火主气3）；预注册 §二 已按终稿登记。
3. ❌10 中 yx-贫家境贫寒一贫（阳日见阴官族）/yx-贫穷命贫困线上（身弱财旺+财不做功族，§7-15 有双锚否决记录）非 P3 三簇对象，入 backlog P3 收档候选；cj-装璜 overshoot 根因在 gongliang L4（书「没有制干净」应封顶 L3），须动功量层，超本批消费侧范围留后续。

## 三、剩余事项

- **财命残留 ❌10 原位**（KB §6.3 逐例处置表=P3 预注册 §四）；⚠️ 侧 42 例收敛空间仍大（非本批对象）。
- **下批=P4**（职业军警墓库做功：objective muku 域「库制库」检测+zhiye military 消费扩展，方案 P4 节，从 `20260918_p3.json` 起跑）；财命 G5 破从/A1 反局=高风险单列或收档（方案四节已定）。
- 代码改动未提交（工作树，用户未要求 commit）。
- 0917 文件所载其余事项（D 真实凭证冒烟待办、A3 条件项、feishu 并发两 P1 等）原样维持，见该文件 §二。

---

# 收工记录 · 2026-09-18（P2 官命 fp 窄修簇批落地）

> 接续 `docs/remaining-tasks-20260917.md`（H-fix 序列收官+L0 关闭+L1 已办，其「下批衔接」已定 P2）。
> 本批 = 引擎精度批 P 系列第二批（判定改动批，objective 零改动）。详账=`docs/tasks/codehygiene-fix-backlog.md` P2 节；预注册=`docs/kimi-p2-guanming-prereg-20260918.md`；快照链=`mangpai/tests/heldout/snapshots/README.md`。

## 一、P2 落地终态

| 项 | 内容 |
|---|---|
| 条款实现 2/7 | A12 女命夫宫域分流（gender 透传 guanming 消费侧，chuji:2206+yanjiu:5646）/A17 旺杀入墓墓不开无做功不立官（功在墓杀豁免，chuji:1405/1409+3161 双锚） |
| 收档 5/7 | A13 争合官无力（孤锚+机制不符+R3GUAN 冲突）/A14 合绊无功（触方向门 10 锚禁令）/A15 合用官被穿破（印化官杀独立立官撤 combo 不足翻判；KB 旧标「制不尽」与书原文不符，以书为准）/A16 禄上坐官（孤例+须动印类）/A18 制财尽（与 G7 豁免锚 cj-县长同构不可分） |
| 指标 | trainset 官 **100→102✅**（+2 全预注册，方案带 +2~5 下沿，CI 下界 79.6%→81.6%）；heldout 三维零翻转（官 48✅/财 47✅/职 24✅ 保）；trainset 财/职零翻转 |
| 文本抖动 2 条 | cj-妓女/shouke-qi23-闹婚不离 veto_reasons 岁运剥除连锁（A12 设计内，官维 unscorable） |
| 六件套 | verify 432+70+64+20 ✔；pytest **1087 passed+1xf** ✔；blind 快照 `20260918_p2.json` vs p1 翻转 2 全归因 ✔；双 seed 同 note 复跑逐字节一致 ✔；67/famous 无变化 ✔；calib 常驻 2 条零新增 ✔；check_layering+check_typing_imports ✔；3.11/3.14 冒烟一致 ✔ |
| 基线 | `snapshots/LATEST` → **`20260918_p2.json`**（README 链总账已补录） |
| 四保护锚 margin | cj-2097/yx-部长/reg67-公安/cj-公安全保 True；朱元璋（heldout 只评估）True；本批无降分条款，margin≤1 禁降分规则不适用；A4 印类方向门 10 锚复验 10/10 True |

## 二、偏差备案

1. 任务书称四保护锚「均在 trainset 可查到」——实测**朱元璋仅在 heldout**（shouke-qi47-朱元璋），以只评估不反推方式核验（不以其设计条款）。
2. KB §6.2 未给 A13-A18 case id，本批以代码+书原文实测定位（预注册 §一）；**A15 KB 标「制不尽」与书原文机制不符**（cj-老总实=合用官被穿破，chuji:3258-3262），以书为准收档。
3. 探针（combo key 并集 positions）预判 reg67-制例二/shouke-li084 翻转，实码按动作逐个判定更窄，两例实际不变（良性偏差）。
4. 散落 1 例=zj-工薪无官（§6.5 F11 软断语收档在先，本批未动）。

## 三、剩余事项

- **官命残留 ❌13**（KB §6.2）：fp 簇余 5（收档，勿再立项）+C 备案 7+散落 1。
- **下批=P3**（财命残簇批：A4 土金伤官 juefa→caiming 新消费边+A12 体坏凶向链+A13 制库基阶，方案 `kimi-engine-precision-plan-20260918.md` P3 节，从 `20260918_p2.json` 起跑）；P4=职业军警墓库做功。
- 代码改动未提交（工作树，用户未要求 commit）。
- 0917 文件所载其余事项（D 真实凭证冒烟待办、A3 条件项、feishu 并发两 P1 等）原样维持，见该文件 §二。
