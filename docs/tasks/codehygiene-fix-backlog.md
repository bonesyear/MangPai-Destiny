# 代码卫生审查 · 统一待修清单

> 本文件登记各批次代码卫生审查发现的 P0/P1/P2 问题，按批次分组，修复后打勾归档。
> 格式：`文件:行号 | 维度 | 级别 | 问题描述 | 修法建议`

---

## H1 · objective 核心批（2026-08-25）

审查范围（25 文件）：
- 核心：`mangpai/objective/zuogong_detect.py`、`bazi_calc.py`、`dayun.py`
- 基础对象：`shensha.py`、`jiaoyun.py`、`xiangfa.py`、`muku.py`、`body_parts.py`、`gongshen.py`
- 小模块：`constants.py`、`advanced.py`、`he_types.py`、`yingqi.py`、`virtual_solid.py`、`shenshu.py`、`wood_type.py`、`soil_type.py`、`nayin.py`、`binzhu.py`、`biqi.py`、`anhe.py`、`canggan.py`、`changsheng.py`、`gongfei.py`、`zihe.py`、`tiyong.py`

### P0（运行时崩溃/阻塞发布）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `jiaoyun.py:374-380` | D4 | `safe_compute_jiaoyun()` 裸 `except Exception as e` 捕获所有异常并返回含 `error` 字段的字典，会吞掉 `TypeError`/`ValueError`；上游继续访问 `jiaoyun_dt` 可能二次崩溃。 | 仅捕获预期异常（`ImportError`、`ValueError`、sxtwl 异常），其他继续抛出。 |
| `jiaoyun.py:138-147` | D4 | `_jd_to_datetime()` 裸 `except Exception` 捕获 JD 转换错误并返回 `None`，掩盖数据问题。 | 细化异常类型，记录输入 JD，非预期异常继续抛出。 |
| `advanced.py:42-50` | D7 | `__getattr__` 通过 `from mangpai.subjective.zhengfan import ...` 做 lazy import，让 objective 层反向依赖 subjective 层，存在循环导入风险。 | 移除该 re-export 或在迁移期加显式错误；objective 层不应暴露 subjective 符号。 |
| `dayun.py:671-691` | D6 | `dayun_gz_sequence()` 直接 `GAN.index(year_gan)` / `ZHI.index(month_gz[1])`，对非法干支会抛 `ValueError`/`IndexError`，函数签名无入口校验。 | 增加非法干支校验并抛 `ValueError`。 |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `zuogong_detect.py:119` | D2/D1 | `detect_relations()` 约 850 行，含 6 组嵌套 `for i in range(4): for j in range(i+1,4):` 关系扫描块（冲/合/刑/害/破/生/克/墓），大量复制粘贴同一 O(n²) 脚手架。 | 拆分为 `_emit_action()` + 关系类型注册表，把循环体压缩到 1 个通用扫描循环。 |
| `zuogong_detect.py:161` | D5 | `work_types` 在函数内累加，但仅用于 817 行的 `if '化用' in work_types`，一个仅用于内部 gate 的 provisional 集合占整函数副作用。 | 把 gate 改成对 `work_actions` 的扫描，删除 `work_types`。 |
| `zuogong_detect.py:170-184,252-287,296-463,508-590,592-777` | D1 | 财/官杀目标列表在「天干食伤、地支食伤、内食神格」中各自独立实现同一套 `for g in gans / for z in zhis` 筛选。 | 抽出 `_find_wx_targets(wx, gans, zhis, exclude_idx)` helper。 |
| `zuogong_detect.py:80-89` | D3/D6 | `_pos_wx()` 用字符串拼接 `f'{key}_gan'` 匹配位置，依赖调用方 `from_pos/to_pos` 命名约定，schema 调整会静默返回空串。 | 改成结构化 `(pillar, gan/zhi)` 元组匹配，或增加非法位置 assert。 |
| `zuogong_detect.py:376-378` | D6 | `is_entomb(_zhi, zk, zhis, gans)` 在循环里重复调用，内部又遍历 `all_zhis/all_gans` 做计数，整体 O(n³)。 | 预计算各五行计数后改 O(1) 判断。 |
| `zuogong_detect.py:866-882` | D4/D6 | “日支合中心” gate 用 `>= 3` 硬 threshold 把日支食伤降级为 auxiliary，无命名常量，口径与 `_day_zhi_he_count` 耦合。 | 抽出常量 `_HE_CENTER_THRESHOLD = 3` 并补充单元测试覆盖 2/3/4 边界。 |
| `bazi_calc.py:681-761` | D2/D4 | `compute_da_yun()` 同时处理方向、起运岁、大运序列，边界 pos clamp 在越界时静默兜底。 | 越界情况显式抛 `ValueError` 而非 clamp。 |
| `bazi_calc.py:791-796` | D5 | `calc_bazi_full()` 的 `yin_method` 与 `shensha_reference` 为 dead parameters，函数内完全不使用。 | 在兼容版本后增加 deprecation warning，并在下一 major 清理签名。 |
| `bazi_calc.py:596-619` | D1/D7 | `_LIU_CHONG/_LIU_HE/_XING_PAIRS/_SAN_HE/_SAN_HUI` 与 `constants.py` 重复定义；`get_di_zhi_relations()` 与多个模块关系检测逻辑重叠。 | 统一从 `constants` 导入；关系扫描逻辑复用公共 helper。 |
| `bazi_calc.py:643-652` | D6 | `get_kong_wang()` 中 `xun_no = ((0 - xun_shou) // 2) % 6` 依赖 xun_shou 为偶数，无前置校验。 | 加 assert 或显式校验 `xun_shou % 2 == 0`。 |
| `bazi_calc.py:791` | D7 | `isinstance(city_lon, bool)` 放在 `int/float` 校验内，但 `bool` 已是 `int` 子类，且范围检查对 bool 会通过。 | 改为先 `type(city_lon) in (int, float)` 拒绝 bool。 |
| `dayun.py:67-69` | D1 | `_check_pair()` 与 `zuogong_detect.py:28-29`、`gongshen.py:101-103` 同名同实现复制粘贴。 | 抽到 `constants` 或 `utils` 作为公共 helper。 |
| `dayun.py:273-350` | D6 | `_analyze_tomb_effect()` 开头计算 `dy_wx = ZHI_WX.get(dy_zhi, '')` 但后续完全未使用，是 dead 局部变量。 | 删除。 |
| `dayun.py:637-645` | D6 | `work_types` 推导只检测了“体+食伤”为 `生用`，未覆盖墓用/化用/制用，与 `zuogong_detect` 口径可能不一致。 | 对齐 `work_types` 分类逻辑或说明 intentional 子集。 |
| `shensha.py:386-404` | D5 | 华盖 `year_ref` 注释明确“无生产读者”，是死字段；灾煞 `year_ref` 也仅一处活读者。 | 在文档/测试中标为 deprecated，后续批次清理。 |
| `jiaoyun.py:168-207` | D5/D6 | `_normalize_dayun_entries()` 中 `items = dayun_list if not span else list(dayun_list)[:span]`：默认 `span=9` 恒真，`if not span` 分支永不被覆盖到。 | 删除该分支或显式 `if span is None`。 |
| `jiaoyun.py:84-87` | D6 | `_year_gz()` 假定公元 4 年为甲子年并直接用 `(year-4)%10`；对公元前或 year<4 会给出无意义干支。 | 增加 year 校验或文档化限制。 |
| `jiaoyun.py:157-165` | D6 | `_advance_gz()` 直接 `gz[0]/gz[1]` 索引，对空串/单字会抛 `IndexError`；调用方退化路径传入 `''` 时会崩溃。 | 前置 `len(gz) >= 2` 校验。 |
| `muku.py:31-41` | D1 | `_is_chong/_is_he/_is_xing` 与 `zuogong_detect._check_pair()`、`dayun._check_pair()`、`gongshen._check_pair()` 功能完全重复。 | 抽到公共模块。 |
| `muku.py:298-318` | D6/D4 | `analyze_muku()` 的地支关系扫描里 `wx1/wx2` 用 `WU_XING_DZ[DI_ZHI.index(z1)]` 获取，而其他函数用 `ZHI_WX.get(z1,'')`；两套查表不一致。 | 统一使用 `ZHI_WX`。 |
| `muku.py:137-206` | D2/D6 | `is_entomb()` 分支多，`all_gans is None` 与空列表 `[]` 语义不同（None=仅地支，[]=天干为空但启用透干判定），极易误用。 | 用显式 flag `include_gans: bool` 替代 `None` 魔术语义。 |
| `body_parts.py:125-140` | D3/D1 | `PILLAR_BODY` 与 `gongshen.py._PILLAR_BODY` 内容矛盾（年=腿足 vs 年=头颈），注释已标注为 bug 单。 | 在 cleaning batch 中统一为书中主表，并删除重复定义。 |
| `gongshen.py:43-49` | D3/D1 | `_PILLAR_BODY` 与 `body_parts.PILLAR_BODY` 年/时颠倒，注释承认 bug。 | 统一数据源并修复。 |
| `he_types.py:205-307` | D2/D1 | `classify_he_types()` 与 `zuogong_detect.py` 大量重复：天干合、合化、三合局/半合、暗合判定逻辑几乎一致但独立实现。 | 复用 `zuogong_detect` 的 helper 或把公共逻辑下沉到 `he_types`。 |
| `he_types.py:116-151` | D1 | `_try_hua()` 与 `zuogong_detect.py:207-241` 的合化 gate 同功能但代码重复。 | 统一到一个 helper。 |
| `constants.py:282-287` | D6 | `is_pillars()` 仅检查 `year_gan` 与 `day_gan` 两个属性，对其他 6 个属性无要求；多个模块依赖完整属性列表。 | 增加对全部 8 个 pillar 属性的检查，或提供 `is_full_pillars` 严格版本。 |
| `virtual_solid.py:240-245` | D5 | `virtual_count/solid_count/vulnerable_count` 注释已标注为死字段。 | 清理或加 deprecation。 |
| `soil_type.py:103-121` | D5 | 注释已说明 `wet_soil`/`dry_soil` 无 Python 消费方，是 prompt-only 死字段。 | 若确认无用，在清理 batch 中删除。 |

### P2（技术债/建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `zuogong_detect.py:48-77` | D3/D6 | `_day_faction()` 用线性扫描 `WX_SHENG.items()` 反查印五行，返回值命名与函数名不完全对应。 | 建反向映射 `WX_BEI_SHENG` 或直接用常量查印，函数名改为 `_day_faction_wx`。 |
| `zuogong_detect.py:296` | D6 | 循环写死 `for idx in (0, 1, 3)` 表示年/月/时干，未解释为何跳开 2（日干）。 | 用常量 `DAY_IDX = 2` 与 `GAN_IDXS_EXCEPT_DAY = (0,1,3)`。 |
| `zuogong_detect.py:997` | D6 | `_JIA_PAIRS` 用裸整数索引 `(0,2,(1,))`，与 `PILLAR_KEYS` 顺序强耦合。 | 用 `PILLAR_KEYS.index('year')` 等具名常量构建。 |
| `bazi_calc.py:449-469` | D6 | `true_solar_components()` NOAA 公式里的常数 `229.18/0.000075/...` 为裸 magic numbers。 | 给 EoT 系数加命名常量。 |
| `bazi_calc.py:563-589` | D6 | 晚子时逻辑 `if ch == 23` 把 23:00-23:59 与时柱 23:00（子时）混在一起；分支分散。 | 封装 `_resolve_late_zi(day_idx, corrected_hour, method)` 独立函数。 |
| `bazi_calc.py:823-832` | D5 | `_self_check()` 只在 `__main__` 运行，只覆盖 2026 上半年。 | 迁移到 pytest 用例。 |
| `dayun.py:71-119` | D1/D3 | `_compute_shishen()` 与 `shenshu._compute_shishen()`、`bazi_calc.ten_god()` 三处实现同一十神规则；命名与模块同名易混淆。 | 统一复用并改名 `_ten_god_for_pillar`。 |
| `dayun.py:598-622` | D2 | `_analyze_pillar_interaction()` 把 7 个分析函数结果聚合；`has_*` 布尔值与 `work_types` 同时存在，数据冗余。 | 可考虑由 judge 层按需计算 `has_*`。 |
| `shensha.py:176-192` | D1 | `_shishen_cat()` 与 `dayun._compute_shishen()`、`bazi_calc.ten_god()` 重复。 | 统一复用。 |
| `shensha.py:34-47` | D1/D3 | `_YANG_REN`（单刃）与 `_YANG_REN_FULL`（双刃）同时存在；`_YANG_REN` 易让读者误以为是主表。 | 把单值表命名为 `_YANG_REN_PRIMARY`，并在模块顶部说明主/全关系。 |
| `shensha.py:252-279` | D2/D4 | `_dual_ref()` 内部定义 `_one()`，嵌套函数加深阅读成本。 | 把 `_one` 提到模块级并明确返回类型。 |
| `shensha.py:281-298` | D6 | 羊刃结果分支：阳干时 `zhi_all` 列全刃位，阴干时 `note` 字段描述“阴干无羊刃”；消费方可能同时依赖 `zhi`/`zhi_all` 不存在分支。 | 统一结构：阴干也返回 `zhi_all: []`。 |
| `xiangfa.py:108-128` | D3/D6 | `GONG_WEI_XIANG['年柱']` 年龄写死 `1-18/18-35/35-55/55+`，与 `yingqi.DAXIAN_MAP` 应保持一致。 | 从 `yingqi.DAXIAN_MAP` 动态生成或加单测断言二者一致。 |
| `xiangfa.py:14-106` | D3 | `GAN_XIANG['辛']['person']` 为“妓女”等敏感词；虽为原著直录，但属于敏感内容。 | 在 docstring 中说明来源与使用风险，或增加中性替代映射层。 |
| `xiangfa.py:260-282` | D5 | 五个 `get_*_xiang()` 简单封装，但 `LIUSHI_GANZHI_XIANG` 输出不含统一 fallback；下游需自行判空。 | 行为可接受，建议下游消费时统一处理 `{}`。 |
| `muku.py:188-193` | D6 | 土支入辰墓时 `tombed_wx == '土' and tombed_zhi != '辰'`，未排除 `tombed_zhi == '戌'` 火库土。 | 复核书例，补充注释或单测。 |
| `muku.py:209-228` | D4 | `analyze_muku()` 支持 `is_pillars(zhis)` 鸭子类型，但若对象缺 `.zhis`/`.gans` 会抛 `AttributeError`。 | 在 `is_pillars()` 成功后显式断言所需属性存在。 |
| `body_parts.py:31-37` | D5 | `__all__` 导出了大量数据表，但注释说明“本模块数据未接线”。 | 保留契约但加 deprecation 说明。 |
| `body_parts.py:296-314` | D2/D6 | `_self_check()` 仅在 `__main__` 触发，未加入 pytest。 | 迁移为测试用例。 |
| `gongshen.py:101-103` | D1 | `_check_pair()` 与 `zuogong_detect/dayun/muku` 重复。 | 复用公共 helper。 |
| `gongshen.py:106-132` | D6 | `_detect_zhi_relations()` 先收集 types 列表，再 if `'刑' in types and '穿' in types: types.remove('穿')`。 | 把“刑去重穿”封装为 `_dedup_xing_chuan()`。 |
| `gongshen.py:168-175` | D4 | `is_pillars(day_gan)` 成功后未验证 `day_gan` 对象是否真的有全部 8 个属性。 | 加 `hasattr` 校验或复用严格版 `is_pillars`。 |
| `gongshen.py:235-258` | D1/D6 | `palace_interactions` 与 `spouse_palace` 都从 `relations` 遍历，同一关系被扫描两次。 | 一次遍历产出两种结果。 |
| `constants.py:200-206,209-215` | D6 | `NAYIN_WEIGHT` 与 `NAYIN_WUXING` 在 `foundation` 层也有重复定义。 | 统一从 `foundation.objective.nayin` 导入。 |
| `constants.py:131` | D6 | `MANGPAI_WU_ZHI_CANG_DING` 全局开关在 `canggan.py` 读取，修改会改变模块行为，无线程安全/测试隔离。 | 改为参数化或上下文变量。 |
| `constants.py:273-276` | D6 | `EFFICIENCY_*` 阈值命名常量未在 objective 层使用，应确认是否漂移。 | 加 cross-module 引用测试。 |
| `yingqi.py:272-281` | D5/D3 | `detect_yingqi()` Pillars 分支里 `day_gan` 赋值重复且逻辑冗余。 | 简化为 `day_gan = p.day_gan`。 |
| `yingqi.py:75-96` | D6 | `daxian_of_age()` 的边界 `age < 1` 与 `age >= 55` 兜底逻辑，magic numbers 120 来自 `DAXIAN_MAP` 上界。 | 用 `DAXIAN_MAP['hour']['age_range'][1]` 或提取 `MAX_AGE`。 |
| `yingqi.py:99-171` | D6 | `detect_lu_yuanshen()` 未处理 `gans`/`zhis` 长度不是 4 的情况。 | 加长度校验。 |
| `he_types.py:50-65` | D6 | `_is_weak()` 使用 magic numbers `same_count <= 1` 与 `ke_count >= 2`。 | 抽 `_WEAK_SAME_MAX = 1`、`_WEAK_KE_MIN = 2`。 |
| `he_types.py:164-202` | D3 | `_classify_gan_he()` 修改外部传入的 `results` 列表，副作用不直观。 | 改为返回新列表再合并。 |
| `virtual_solid.py:74-111` | D1 | `_find_yin_support()` 与 `zuogong_detect`/`he_types` 中“找印/找财/找官杀”的逻辑结构重复。 | 抽公共 `_find_wx_in_pillars()`。 |
| `virtual_solid.py:28` | D5 | `_GAN_WX_LOOKUP = GAN_WX` 是多余别名。 | 删除。 |
| `virtual_solid.py:114-236` | D2 | `analyze_virtual_solid()` 约 120 行，分支嵌套到 3 层。 | 把 `vtype` 与 `vulnerable_to_ke` 计算抽到独立函数。 |
| `shenshu.py:127-148` | D1 | `_compute_shishen()` 与 `dayun._compute_shishen()`、`bazi_calc.ten_god()` 重复。 | 统一复用。 |
| `shenshu.py:151-159` | D6 | `_grade()` 与 `SHENSHU_GE` 的 7 上限是 magic number。 | 抽常量 `_SHENSHU_MAX = 7`。 |
| `shenshu.py:162-269` | D2 | `analyze_shenshu()` 约 110 行。 | 可把“收集 positions”与“汇总结果”拆成两个函数。 |
| `wood_type.py:33-46,61-76,79-89` | D1 | `_wx_zhis()`、`_has_wx_root()`、`_has_wx()` 对“地支含某五行”的扫描逻辑高度重叠。 | 合并为 `_pillars_contain_wx(gans, zhis, wx, mode)`。 |
| `wood_type.py:49-58` | D6 | `_water_sheng_root()` 先检查 `_MANGPAI_PO` 再检查 `LIU_CHONG/LIU_HAI`，顺序无注释说明。 | 加注释说明优先级或合并为“不生”集合。 |
| `wood_type.py:92-122` | D4 | Pillars 分支里 `other_gans` 仅取年/月/时干，遗漏其它可能天干；退化路径未透传天干。 | 文档化限制或统一透传完整 `gans`。 |
| `nayin.py:72` | D6 | `analyze_nayin_work()` 对每个 pillar 调用两次 `get_nayin(gz)`。 | 先计算 name，复用结果。 |
| `nayin.py:21-22` | D7 | `from foundation.objective.nayin import *` 后再显式 import 同名符号，冗余 import。 | 删除 `*` import，只用显式 import。 |
| `binzhu.py:21-24` | D6 | `layers` 参数仅判断 `== 2`，其他值都退化为 3；未对非法值警告。 | 加 `if layers not in (2,3): raise ValueError`。 |
| `zihe.py:46-53` | D5 | `_XU_ACTIVATORS` 构建时对 `XING_PAIRS` 用 `isinstance(_pair, tuple) else tuple(_pair)`；`constants.XING_PAIRS` 已保证是 tuple，防御代码是 dead branch。 | 删除 `isinstance` 分支。 |
| `zihe.py:81` | D6 | `detect_zihe()` 假设 `gans` 与 `zhis` 长度均为 4，否则静默返回空结果。 | 加长度校验并抛 `ValueError` 或 warning。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 4 |
| P1 | 32 |
| P2 | 47 |

---
