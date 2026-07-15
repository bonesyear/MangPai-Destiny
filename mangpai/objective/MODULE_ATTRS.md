# mangpai/objective 模块属性标注

标注每个客观层模块的「流派属性」，区分**中性（可下沉 foundation）**与**盲派特异（须留 mangpai）**。
分层原则：`foundation（中性） <- mangpai/objective（盲派客观） <- subjective <- engine`。
中性模块=各流派共识或经典原典不依附盲派机制者；盲派特异=依赖段氏做功/宾主/体用/虚实/墓库等特异概念者。

## 属性总表

| 模块 | 属性 | 说明 |
|------|------|------|
| `canggan.py` | 中性但有流派变体 | 藏干表存在盲派/子平版本差异（午藏丁己 vs 午只藏丁；亥藏壬甲不含戊）|
| `changsheng.py` | 中性但有流派变体 | 长生表「阴阳同生同死」及己墓分歧（辰/戌双轨）是盲派特色，非书房派共识 |
| `shensha.py` | 中性但运用方式特化 | 神煞计算各流派共用，盲派在取用与应事上特化（如羊刃只取阳干、桃花以日支起）。**神煞配置口径**：盲派核心只用 5 个（禄神/羊刃/墓库/驿马/空亡），本模块其余为书房派扩展（见下方「神煞配置（核心5+扩展）」），暂不删减，等多流派开关再裁剪 |
| `nayin.py` | -> foundation（计算已迁移） | 纯计算（NAYIN_TABLE/NAYIN_WUXING/get_nayin）已迁至 `foundation.objective.nayin`；本模块仅保留盲派纳音权重与做功分析（get_nayin_mangpai/analyze_nayin_work），并 `from foundation.objective.nayin import *` 重新导出 |
| `ganqing`（滴天髓干支性情） | 在 `foundation/objective/` | 滴天髓天干/地支性情赋，结构化为「条件->行为」规则，附原注与任氏曰；中性，不依附盲派机制 |
| `constants.py` | 混合（中性常量 + 盲派特异常量） | 含中性数据（DI_ZHI/WU_XING/LIU_HE/LIU_CHONG/NAYIN_TABLE 等）与盲派特异常量（CANG_GAN_MANGPAI/CHANGSHENG_START_MANGPAI/NAYIN_WEIGHT/TOMB_MAP 等）；纳音表已与 foundation 同源（未删本处副本以不动其余模块逻辑）|
| `anhe.py` | 盲派特异 | 暗合（寅丑/午亥/卯申/子巳）——盲派独有，私下联系/隐秘之事 |
| `biqi.py` | 盲派特异 | 闭气——六合闭墓库藏干（子丑闭丑金、辰酉闭辰水…），逢冲方解 |
| `binzhu.py` | 盲派特异 | 宾主——四柱分主/宾/远宾三层，看日柱做功取外物还是内聚 |
| `tiyong.py` | 盲派特异 | 体用——日主+印+比劫+禄为体，财+官杀为用，食伤居中 |
| `muku.py` | 盲派特异 | 墓库——开库（冲/刑）/闭库（合）/多而入墓，盲派重要做功手段 |
| `he_types.py` | 盲派特异 | 合的类型细分（合绊/合克/合制/合化/闭气），不同类型应事不同 |
| `virtual_solid.py` | 盲派特异 | 虚实——天干虚实取决于地支同五行根，虚透怕克、坐实不怕克 |
| `wood_type.py` | 盲派特异 | 木的活死——活木见火开花泄秀、死木见火燃烧，行为完全不同 |
| `soil_type.py` | 盲派特异 | 四土燥湿——辰丑湿土生金晦火、未戌燥土脆金克水 |
| `gongfei.py` | 盲派特异 | 功神/废神分类——参与做功者为功神、不参与者为废神（**勿与 gongshen 合并/改名**：gongfei=功废，gongshen=宫身，二者同音异义）|
| `gongshen.py` | 盲派特异 | 宫身（宫位六亲）——年祖/月父母/日配偶/时子女，星宫配合断六亲 |
| `shenshu.py` | 盲派特异 | 十神数量歌诀（郑民生《十排歌》）——按十神出现数量分级断事 |
| `zuogong_detect.py` | 盲派特异 | 做功·纯关系检测——只检测四柱间存在哪些关系，产出原始 work_actions，判定交 subjective |
| `xiangfa.py` | 盲派特异 | 象法四层（干支象/宫位象/十神象/神煞象）——取象直断数据 |
| `yingqi.py` | 盲派特异 | 应期客观检测——大限映射/禄与原身/遁藏透干三机制（段氏第二章应期），纯检测产事实、推断交 `subjective.yingqi_subj`。宫位年龄采用书中大限值（见下方「宫位年龄统一决定」）|
| `jiaoyun.py` | 盲派特异 | 交运时间——按出生年纳音五行定「命」算交运时刻（盲派特有）|
| `dayun.py` | 盲派特异 | 大运分析——大运为宾、四柱为主，看大运来做什么、是否激活废神 |
| `advanced.py` | 兼容层（重导出） | 旧聚合模块的向后兼容 shim，新代码应直导对应子模块 |

## 备注

- **穿=害**：`LIU_HAI`（六害）即穿，二者等价，**勿改名**（见 `constants.py`）。
- **gongfei / gongshen 勿合并**：同音异义——gongfei=功神/废神（做功效率），gongshen=宫身（宫位六亲），分属不同理论维度。
- **nayin 迁移不切断路径**：`mangpai.objective.nayin` 经 `from foundation.objective.nayin import *` 重新导出纯计算，`jiaoyun.py` 等仍可 `from mangpai.objective.constants import NAYIN_TABLE`（constants 副本保留，逻辑未改）。
- **受保护勿改**：`mangpai/schools.py`、`mangpai/prompts/` 不在本标注范围，禁止改动。
- 中性模块（canggan/changsheng/shensha）「有流派变体/运用特化」故暂留 mangpai；若未来抽离变体开关，纯表部分可下沉 foundation，与 nayin 同例。
- **宫位年龄区间统一决定**：引擎内并存两套宫位年龄，分属不同理论维度，**并存不替换、不统一为一套**：
  - 应期大限（`yingqi.py` 的 `DAXIAN_MAP`）：年柱 1-18 / 月柱 18-35 / 日柱 35-55 / 时柱 55+（段氏《盲派中级命理学》第二章应期篇大限值），用于「原局某柱结构在哪个年龄段兑现」的应期定位；
  - 六亲宫位取象（`xiangfa.py` 的 `GONG_WEI_XIANG`）：年柱 1-15 / 月柱 16-30 / 日柱 31-50 / 时柱 50+（六亲宫位时限取象口径），用于六亲星宫配合断事。
  - 二者口径不同源、语义不同（应期 vs 六亲时限），各自服务于自己的模块，**不交叉混用**。`yingqi.py` 与 `xiangfa.py` 均已在此标注此决定。
- **神煞三层收口（`shensha.py`，高级篇灾祸章+中级篇核心5）**：段氏《盲派中级命理学》明确盲派核心只用 5 个神煞——**禄神 / 羊刃 / 墓库 / 驿马 / 空亡**。三层分类（`SHENSHA_LAYER`，本函数所算各项均带 `layer` 字段，供消费侧按层取用/裁剪）：
  - **盲派核心5（盲派默认取用）**：禄神=`constants.LU`、墓库=`constants.TOMB_MAP`+`muku.py`、空亡=作 `kong_wang` 参数传入 `zuogong_detect.detect_relations`（消费侧）、羊刃/驿马/`马星`(盲派多马星，四柱各起)=`shensha.py`；
  - **凶性三煞 → 灾祸模块**：空亡（兼核心5，必算但凶应入灾祸）/`亡神`/`劫煞`/`灾煞`=`shensha.py`（亡神表与驿马不同位：申子辰→亥、寅午戌→巳、巳酉丑→申、亥卯未→寅）；
  - **传统6 → 降级 `traditional_shensha`**：天乙贵人/文昌/华盖/桃花/孤辰/寡宿（书房派扩展，本模块保留计算、layer 标「传统(降级)」）。
  **暂不做代码删减**，等 `schools.py` 多流派开关落地后按 `layer` 裁剪扩展神煞；当前全量保留以不破现有测试与 `verify_mangpai.py`。
- **过河拆桥分键口径（`subjective/caiming.py`，高级篇财命补齐）**：过河拆桥（日支财生宾官、宾官被宾字制）按制尽/制不尽分两路，**口径同源不同深、并存不替换**：
  - **破财路径（中级篇口径）**：宾官被制但**制不尽**（官杀残存同党未俱制）→ 财过河生宾官、宾官未制尽反夺财 → 财流失破财。判据 `_is_zhi_jin()=False`。
  - **富格路径（高级篇财命章口径）**：宾官被制且**制尽（净制）**（官杀明现位俱被制、无残存）→ 制官得财、七杀当财量级 → 过河拆桥富格（巨富）。判据 `_is_zhi_jin()=True`。
  - 制尽判据为工程化启发式（位置覆盖度：官杀明现位俱为制用/合制目标），成势制尽须 `zeishen_bushen` 党势判定，此处保守兜底可能偏宽。结果字段 `guohe_chaiqiao_type` ∈ {'富格','破财',None}；views 标 `过河拆桥·富格`/`过河拆桥·破财`。
