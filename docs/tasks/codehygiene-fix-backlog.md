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

## H2 · subjective 核心批（2026-08-25）

审查范围（10 文件）：`caiming.py`、`yongshen.py`、`zhiye.py`、`xiangfa_ops.py`、`gongliang.py`、`liuqin.py`、`hunyin.py`、`zuogong_confirm.py`、`guanming.py`、`laoyu.py`。

### P0（运行时崩溃 / 静默失败）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `caiming.py:239,251,526,585,684,1335,1385,1406,1510,1535,1853` | D4 | 11 处 `except Exception:` 吞掉 TypeError/ValueError 等并返回 `{}`/`None`/`pass`，含 `_ensure_relations/_ensure_muku`、自合检测、从格判定、gongliang 自调等路径 | 逐处捕获预期异常；非预期异常继续抛出并记录 |
| `yongshen.py:242,344,449,716,909,1257,1358,1531,1540` | D4 | 9 处 `except Exception:` 吞异常并返回空/None/pass（`_ensure_*`、强弱判定、类象等） | 同上 |
| `zhiye.py:157,1281,1352,1356,1486,1505,1534,1573,1649,1682` | D4 | 10 处 `except Exception:` 吞异常 | 同上 |
| `xiangfa_ops.py:58,142,342,354,1213,1343,1480` | D4 | 7 处 `except Exception:` 吞异常 | 同上 |
| `gongliang.py:297,321,774,1110` | D4 | 4 处 `except Exception:` 吞异常 | 同上 |
| `liuqin.py:102,287,422,550,707,855,879,1107,1165` | D4 | 9 处 `except Exception:` 吞异常 | 同上 |
| `hunyin.py:74,179,828,893,1084` | D4 | 5 处 `except Exception:` 吞异常 | 同上 |
| `zuogong_confirm.py:467,494,875,879,884` | D4 | 5 处 `except Exception:` 吞异常 | 同上 |
| `guanming.py:128,336,556,950` | D4 | 4 处 `except Exception:` 吞异常 | 同上 |
| `laoyu.py:138,475,642` | D4 | 3 处 `except Exception:` 吞异常 | 同上 |
| `zuogong_confirm.py:713` | D6 | `_cand_hua` 中 `hua_actions` 可能为空，直接 `[0]` 引发 `IndexError` | 先判空或改用 `next()`/`.get()` |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `caiming.py:69` / `yongshen.py:808` / `zhiye.py:80` / `xiangfa_ops.py:179` / `liuqin.py:56` / `hunyin.py:91` / `guanming.py:57` / `laoyu.py:55` | D1 | 8 个 subjective 文件各自独立实现 `_compute_shishen` / `_shishen_cat`；叠加 H1 objective 层 3 处，十神计算严重分散 | 统一复用 objective 或 yongshen 的十神接口 |
| `caiming.py:229,243` / `guanming.py:118` / `hunyin.py:169` / `xiangfa_ops.py:327,346` / `zhiye.py:147` / `liuqin.py:92` / `laoyu.py:128` / `yongshen.py:334,1520,1535` | D1 | 12 个 `_ensure_relations/_ensure_muku/_ensure_work_actions/_ensure_zhengfan/_ensure_laoyu` 重复实现 | 抽到 `subjective.utils` 统一 helper |
| `caiming.py:394,616,954,1111,1339,1787` | D2 | 6 个函数 >80 行（最长 `assess_caiming_level` 444 行），嵌套最深 6 | 拆分职责 / 抽子函数 |
| `yongshen.py:91,209,374,624,875,1051,1282,1666` | D2 | 8 个函数 >80 行，嵌套最深 7 | 同上 |
| `zhiye.py:305,483,616,930,1072,1200,1297` | D2 | 7 个函数 >80 行（最长 `classify_zhiye` 424 行），嵌套最深 7 | 同上 |
| `xiangfa_ops.py:502,617,845,1000,1115,1285,1428` | D2 | 7 个函数 >80 行（最长 `xiangfa_fallback` 215 行） | 同上 |
| `gongliang.py:226` | D2 | `analyze_gongliang` 957 行、嵌套 5 | 拆分为解析 / 计分 / 汇总子函数 |
| `liuqin.py:170,255,523,640,998,1122` | D2 | 6 个函数 >80 行 | 同上 |
| `hunyin.py:265,404,913,1021` | D2 | 4 个函数 >80 行 | 同上 |
| `zuogong_confirm.py:70,307` | D2 | `assess_work_level` 143 行、`analyze_zuogong` 800 行，嵌套均 7 | 同上 |
| `guanming.py:134,891` | D2 | `classify_guanming_combo` 491 行、嵌套 6 | 同上 |
| `laoyu.py:179,803` | D2 | 2 个函数 >80 行 | 同上 |
| `caiming.py`（8 处） / `yongshen.py`（26 处） / `zhiye.py`（6 处） / `xiangfa_ops.py`（2 处） / `gongliang.py`（2 处） / `liuqin.py`（4 处） / `guanming.py`（7 处） / `laoyu.py`（1 处） | D7 | 56 处函数内局部 import；`gongliang` 顶层导入 `caiming`，`caiming` 局部导入 `gongliang`，形成双向依赖；`yongshen` 作为星型中心被多模块顶层引用，又在局部回边导入 `zuogong_confirm/laoyu/juefa/zhengfan` | 将局部导入上提到模块级并消除循环；或抽取共享接口层 |
| `caiming.py:850,911,1787` / `yongshen.py:72,1520` / `zhiye.py:290` / `xiangfa_ops.py:1115` / `gongliang.py:1240,1365` / `liuqin.py:485` / `hunyin.py:570,713,730,800,913` / `guanming.py:891` / `laoyu.py:438` | D5 | 18 个函数参数在函数体内未被引用（`shensha_result`、`relations`、`gender` 等占位参数） | 清理占位参数或显式标注保留原因 |

### P2（建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `caiming.py:52,58` / `zhiye.py:57` / `xiangfa_ops.py:33,38,44,48` / `liuqin.py:40` / `hunyin.py:37,43` / `zuogong_confirm.py:37` / `guanming.py:41` / `laoyu.py:31` | D5 | 25 个未使用顶层 import（`CANG_GAN_MANGPAI`、`analyze_binzhu`、`compute_shensha_ext`、xiangfa 数据表等） | 删除或注释说明保留原因 |
| `全部 10 文件` | D6 | 判定中大量未命名阈值（如 `>=2`、`>=3`、百分比常数）分散在函数中 | 抽取命名常量并加单测覆盖边界 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 68 |
| P1 | 139 |
| P2 | 26 |

---

## H3 · subjective 辅助批（2026-08-25）

审查范围（11 文件）：`yunfan.py`、`zaihuo.py`、`zeishen_bushen.py`、`yingqi_subj.py`、`xueli.py`、`shipaige.py`、`gongmen_wuzhi.py`、`juefa.py`、`chuangong.py`、`zhengfan.py`、`narrative.py`。

### P0（运行时崩溃 / 静默失败）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `yunfan.py:720` | D4 | 缺省自调 `analyze_zuogong` 裸 `except Exception:`，吞 TypeError/ValueError 并回退空做功。 | 仅捕获预期异常（如参数缺失），非预期异常抛出并记录输入四柱。 |
| `yunfan.py:735` | D4 | 缺省自调 `analyze_zhengfan` 裸 `except Exception:`，基线判定静默失败。 | 细化异常类型，非预期异常继续抛出。 |
| `yunfan.py:745` | D4 | 缺省自调 `classify_strength/classify_cong_target` 裸 `except Exception:`，从格行运规则失效。 | 同上。 |
| `zaihuo.py:146-157` | D4 | `_ensure_relations` 裸 `except Exception:`，非法输入吞异常返回 `{}`。 | 仅捕获 `detect_relations` 预期异常，其他抛出。 |
| `zaihuo.py:285-289` | D4 | `classify_jibing` 中 `analyze_muku` 裸 `except Exception:`，特殊病分支静默失败。 | 细化异常，保留失败原因。 |
| `zaihuo.py:352-354` | D4 | `detect_chehuo` 中 `resolve_shensha` 裸 `except Exception:`，多马星计算静默归零。 | 同上。 |
| `zaihuo.py:534-536` | D4 | `detect_siwang` 中首次 `analyze_muku` 裸 `except Exception:`，墓库信号丢失。 | 同上。 |
| `zaihuo.py:573-579` | D4 | `detect_siwang` 中第二次 `analyze_muku` 裸 `except Exception:`，禄入墓信号丢失。 | 同上。 |
| `zaihuo.py:583-585` | D4 | `detect_siwang` 中 `resolve_shensha` 裸 `except Exception:`，凶性三煞丢失。 | 同上。 |
| `zaihuo.py:692` | D4 | `analyze_zaihuo` 中 `assess_direction_signals` 裸 `except Exception:`，方向总线信号丢失。 | 同上。 |
| `xueli.py:120` | D4 | `_ensure_relations` 裸 `except Exception:`，关系数据静默失败。 | 仅捕获预期异常。 |
| `xueli.py:543` | D4 | `analyze_xueli` 中 `assess_direction_signals` 裸 `except Exception:`，方向信号丢失。 | 同上。 |
| `gongmen_wuzhi.py:142` | D4 | `_ensure_relations` 裸 `except Exception:`，做功数据静默失败。 | 同上。 |
| `gongmen_wuzhi.py:191` | D4 | `classify_junguan` 中 `resolve_shensha` 裸 `except Exception:`，羊刃信号丢失。 | 同上。 |
| `gongmen_wuzhi.py:270` | D4 | `classify_gongjianfa` 中 `analyze_muku` 裸 `except Exception:`，墓库信号丢失。 | 同上。 |
| `gongmen_wuzhi.py:378` | D4 | `detect_gongmen_wuzhi_xiang` 中 `resolve_shensha` 裸 `except Exception:`，羊刃/武职信号丢失。 | 同上。 |
| `gongmen_wuzhi.py:524` | D4 | `analyze_gongmen_wuzhi` 中缺省自调 `analyze_gongliang` 裸 `except Exception:`，层次评定丢失。 | 同上。 |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `zaihuo.py:94-110` / `yingqi_subj.py:54-71` / `xueli.py:39-55` / `gongmen_wuzhi.py:64-80` | D1 | 4 处独立实现 `_compute_shishen`，叠加 H2 已发现的 8 处，十神计算继续扩散。 | 统一复用 `objective.bazi_calc.ten_god` 或下沉公共 helper。 |
| `zaihuo.py:113-126` / `xueli.py:58-69` / `gongmen_wuzhi.py:83-96` | D1 | 3 处独立实现十神大类 `_cat`。 | 抽到公共模块（如 `subjective.utils`）。 |
| `zaihuo.py:129-143` / `gongmen_wuzhi.py:99-113` | D1 | 2 处独立实现五行大类 `_wx_cat`。 | 同上。 |
| `zaihuo.py:146-157` / `xueli.py:110-121` / `gongmen_wuzhi.py:131-142` | D1 | 3 处 `_ensure_relations` 重复实现。 | 抽到 `subjective.utils` 统一 helper。 |
| `yunfan.py:215,305,316,528` / `gongmen_wuzhi.py:516-517` | D7 | 函数内局部 import（shensha/canggan/constants/gongliang），破坏静态依赖可读性。 | 上提到模块级；gongmen_wuzhi 对 gongliang 的局部 import 说明存在循环依赖风险，需解耦。 |
| `yunfan.py:364-548` / `yunfan.py:669-849` / `zhengfan.py:222-688` / `juefa.py:328-623` / `xueli.py:307-435` / `gongmen_wuzhi.py:475-565` | D2 | 6 个函数 >80 行（最长 `zhengfan.analyze_zhengfan` 466 行），嵌套最深 4-5。 | 拆分子函数 / 按判定阶段分块。 |
| `yunfan.py:258-261` / `zeishen_bushen.py:133-138` | D3/D6 | 线性扫描 `WX_SHENG.items()` 反查印五行 / 原神五行，效率低且语义不清。 | 建反向映射 `WX_BEI_SHENG` 或直接用常量查表。 |
| `zaihuo.py:160-176` / `xueli.py:90-107` / `gongmen_wuzhi.py:116-129` | D1 | 逐柱藏干取十神/五行的扫描逻辑高度相似，仅深度阈值不同。 | 合并为 `_pillar_cats(day_gan, gans, zhis, depth=...)`。 |
| `shipaige.py:107-114` / `shipaige.py:120-148` | D5 | `SHIPAI_DOMAINS` / `METHODOLOGY` 数据表注释已说明消费者删除，为死数据档案。 | 确认无引用后清理，或移到 docs 存档。 |
| `gongmen_wuzhi.py:1-46` | D5 | 模块 docstring 已声明「正式弃用」，但代码仍在 `__all__` 暴露并可能被 engine 保留键引用。 | 若确认弃用，加 deprecation warning 或在下一批次移除入口。 |

### P2（建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `yunfan.py` / `zaihuo.py` / `xueli.py` / `gongmen_wuzhi.py` / `yingqi_subj.py` / `juefa.py` / `zhengfan.py` | D6 | 判定中大量未命名阈值（`>=2` / `>=3` / `>=4` / `score>=3` 等）分散在函数中。 | 抽取命名常量并加单测覆盖边界。 |
| `zaihuo.py:221-244` / `zaihuo.py:279-291` | D6 | 疾病判定中穿/破/刑逻辑复制粘贴，仅字典不同。 | 抽出 `_collect_rel_disease(type, wa, map)` 通用函数。 |
| `yingqi_subj.py:76-141` / `yingqi_subj.py:190-395` | D6 | `infer_comprehensive_yingqi` 中交集判定阈值 `hit_count >= 2` 为 magic 口径，无单测。 | 抽常量 `_YINGQI_COMMIT_THRESHOLD` 并补边界测试。 |
| `chuangong.py:143-204` | D5 | 模块注释说明 engine 零消费、测试 xfail，但入口仍暴露。 | 若长期不用，加 deprecation 或移入 archive。 |
| `narrative.py:355` | D7 | `_call_llm` 局部 import `anthropic` 是软依赖设计，可接受；但 `model` 回退字符串 `claude-sonnet-5` 为硬编码占位。 | 抽到模块级常量并允许环境变量覆盖。 |
| `zhengfan.py:62-153` | D6 | `_compute_qishi` 中势党阈值 4/8、两神成象阈值 6 为裸 magic numbers。 | 抽 `_QISHI_HALF=4`、`_QISHI_TWO_GOD=6` 等常量。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 17 |
| P1 | 10 |
| P2 | 6 |

---

## H4 · LLM 通道批（2026-08-25）

审查范围（5 文件）：`mangpai/subjective/llm_backend.py`、`llm_channel.py`、`llm_prompt.py`、`schools.py`、`narrative.py`。

### P0（运行时崩溃 / 静默失败）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `llm_backend.py:131` | D4 | `json.loads(resp.read())` 未捕获 `JSONDecodeError`；HTTP 200 但返回非 JSON（如中间盒 HTML）时该异常会穿透 `call_deepseek`，而 `llm_channel` 只捕获 `LLMBackendError`，导致崩溃。 | 将 `json.JSONDecodeError` 纳入内层捕获并包装为 `LLMBackendError`。 |
| `narrative.py:563` | D4 | `render_hao_narrative` 调 `_call_llm` 用裸 `except Exception:`，吞掉 SDK/网络/参数等所有异常并静默返回 prompt 文本；既无免责声明，也让真正 Bug 无法上浮。 | 仅捕获预期异常（`anthropic.AuthenticationError`、`urllib.error.URLError` 等）；非预期异常继续抛出。 |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `llm_channel.py:467-469` | D4 | `validate='reject'` 且 L0 不通过时，降级返回无 `_DISCLAIMER_LINE`；与死亡红线拦截、LLM 不可用/JSON 失败等路径不一致。 | 统一追加免责声明行。 |
| `llm_backend.py:152` | D3 | 返回字段名 `cost_usd` 实际保存人民币（2026-08-21 已改人民币口径），命名与数据不符。 | 字段改名 `cost_cny` 并同步 `format_reading`；或保留旧键做兼容别名。 |
| `llm_channel.py:428,444` | D7 | `render_structured_reading` 内局部导入 `prompts.hao_style_fewshot` 与 `llm_backend`；无循环依赖，降低静态可读性。 | 上提到模块级。 |
| `narrative.py:412,424` | D4 | `_engine_number_whitelist` 内两处裸 `except Exception:`，分别吞 `json.dumps` 失败与年龄计算失败，静默降级。 | 细化异常类型；非预期异常抛出。 |
| `llm_prompt.py:77,80` | D1 | `_TIER_ORDER` / `_BUCKET_LABELS` 与 `llm_channel` / `zhiye` 重复，注释虽说明“各留一份”，但迭代中易漂移。 | 抽到公共常量模块（如 `subjective.llm_constants`）或显式断言两边一致。 |
| `schools.py:43` | D5 | `selectors` 含 `zinv`，但生产侧仅 `engine.py` 写入、`build_payload` 透传，无 prompt/formatter 消费方（设计为纯数据），保护链下游读者缺失。 | 确认 D6a 口径后：若长期不进 LLM 叙述，加注释备案或从 selectors 移除并保留 engine 键。 |
| `narrative.py:355` | D6 | `_call_llm` 默认模型回退字符串 `claude-sonnet-5` 为硬编码占位。 | 抽到模块级常量并允许环境变量覆盖（H3 已指出，仍未修）。 |
| `llm_channel.py:285-359` | D2 | `_l2_enum` 虽 75 行未越界，但死亡词/财档/官命/迁移/相貌五段校验耦合在一起，新增维度需改本函数。 | 按维度拆为 `_l2_death/_l2_tier/_l2_guan/_l2_qianyi/_l2_xiangmao` 五小函数。 |
| `narrative.py:507-581` | D2 | `render_hao_narrative` 65 行，承担 prompt 组装、LLM 调用、降级、N1 校验，职责过多。 | 将 LLM 调用与 N1 校验拆为独立函数。 |

### P2（技术债 / 建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `llm_backend.py:36-39,44` | D6 | `_PRICE` 价表与 `_PEAK_HOURS` 峰谷时段硬编码；模型/价格调整需改代码。 | 支持环境变量或外部配置覆盖，保留当前值为默认值。 |
| `llm_backend.py:32` | D6 | `_ENV_FILE = '/root/.hermes/.env'` 硬编码绝对路径。 | 抽到常量并允许环境变量覆盖。 |
| `llm_backend.py:162-175` | D5 | `_self_check` 仅在 `__main__` 运行，未加入 pytest。 | 迁移为测试用例。 |
| `llm_channel.py:447-450` / `narrative.py:565-569` | D4/D6 | LLM 不可用时按设计返回完整 prompt 文本，若直接展示给终端用户会泄漏 system/user prompt。 | 加 `debug=True` 开关区分内部调试与终端返回；终端路径只给原因与免责声明。 |
| `llm_channel.py:46-57,63-81` | D6 | `_DEATH_WORDS` / `_QIANYI_FORBID` / `_XIANGMAO_FORBID` / `_GUAN_POSITIVE` 等词表硬编码；迭代增删靠手工。 | 提供外部词表配置入口（默认回退到当前硬编码）。 |
| `narrative.py:168,405-407,448` | D7 | `_zaihuo_line`、`_engine_number_whitelist`、`validate_narrative_numbers` 内局部 import；无循环依赖必要。 | 上提到模块级。 |
| `narrative.py:419` | D6 | `_engine_number_whitelist` 中 `ages.update((18, 35, 55))` 为硬编码大限宫位边界，与 `yingqi.DAXIAN_MAP` 强耦合。 | 从 `DAXIAN_MAP` 动态读取边界。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 2 |
| P1 | 9 |
| P2 | 7 |

---

## H5 · 飞书集成批（2026-08-25）

审查范围（6 文件）：`mangpai/feishu/client.py`、`router.py`、`service.py`、`formatter.py`、`bot.py`、`README.md`。

### P0（运行时崩溃/阻塞发布）

无。

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `formatter.py:17` | D1 | `DISCLAIMER` 与 `llm_channel.py:38` `_DISCLAIMER_LINE` 文本重复，维护易漂移。 | 统一从 `llm_channel` 导入或抽到公共常量。 |
| `service.py:22-23` | D1/D6 | `_LLM_FAIL_PREFIXES` 字符串硬编码，与 `llm_channel` 降级文本强耦合；前缀格式一变即漏检。 | `llm_channel` 返回结构化字段或导出失败原因常量。 |
| `bot.py:53` | D4 | `_respond` 裸 `except Exception` 吞掉所有排盘异常，日志后返回固定提示，掩盖根因。 | 仅捕获预期异常（FeishuError/LLMBackendError/EngineError），未预期异常继续抛出。 |
| `bot.py:58/62` | D4 | reply 发送及纯文本兜底连续两处裸 `except Exception`，过度吞异常。 | 细化异常类型，非预期异常抛出。 |
| `bot.py:119` | D4 | `_Handler.do_POST` 裸 `except Exception` 返回 500，吞掉所有回调处理异常。 | 区分已知异常；非预期异常记录后继续抛出或保留 traceback。 |
| `bot.py:92-95/99-102` | D6 | `_MAX_WORKERS` 信号量仅限制 HTTP handler 线程，`handle_event` 后台排盘线程无界，高并发下可能耗尽资源。 | 把信号量语义延伸至后台任务，或用有界线程池。 |
| `bot.py:81-85` | D6 | `_seen_mids` 检查-写入-滚动窗口非原子，多线程同 mid 可能重复处理。 | 加锁保护去重窗口操作。 |

### P2（技术债/建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `client.py:34-39` | D4 | `_urllib_post` 未捕获 `json.JSONDecodeError`，非 JSON 响应会穿透。 | 捕获并包装为 `FeishuError`。 |
| `client.py:83-87` | D5 | `send()` 生产零调用（V6 已备案），`build_content('post')` 同，属死 API 面。 | 加 deprecation 或移入 archive。 |
| `router.py:17-27` | D6 | `CITY_LON` 36 城市经度表硬编码，更新需改代码。 | 支持外部配置或说明更新机制。 |
| `router.py:66-75` | D6 | `_pop_lon_or_city` 对越界经度静默转城市匹配，错误提示不准确。 | 非法经度显式报错。 |
| `router.py:103-110` | D6 | `parse_pillars` 未校验干支数量/性别是否弹出，不完整输入流入 service。 | 前置 `len(pillars)==4` 与 gender 必填校验。 |
| `service.py:46` | D6 | 四柱直排默认 `year=2000`，影响流年锚，用户无感知。 | 抽常量并提示默认年份。 |
| `bot.py:87-90` | D6 | 文本 content 只处理 JSON 对象，对 JSON 数组/字符串会抛 `AttributeError`，依赖外层裸 except。 | 校验 `isinstance(content, dict)`。 |
| `README.md` | D6 | 缺“机器人无响应”排查指引（Encrypt Key/Token/权限）。 | 加 FAQ 小节。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 0 |
| P1 | 7 |
| P2 | 8 |

---

## H6 · 测试基建批（2026-08-25）

审查范围（51 文件）：`mangpai/tests/` 下全部 `test_*.py` + `calib_assertions.py`，含 `heldout/` 子目录测试/诊断脚本与快照基建。

### P0（运行时崩溃/阻塞发布）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `heldout/blind_eval.py:288-291` | D4/D6 | `_load_snapshot()` 直接用 `json.load(open(...))` 无 `with`，异常时文件句柄泄漏；且 `data.pop('_meta', None)` 原地修改已加载的快照字典，若调用方仍引用原对象则 meta 丢失。 | 改为 `with open(...) as f: data = json.load(f); meta = data.pop('_meta', None); return data, meta` 并在文档说明返回的是副本。 |
| `calib_assertions.py:257-296` | D4/D6 | `--write-baseline` 直接原地改写 `calib_assertions.yaml`，无备份、无校验、无上锁；误操作会破坏校准基线。 | 写回前校验 items 数量与键集合，先写 `.yaml.tmp` 再原子重命名，或要求 `--force` 显式确认。 |
| `backtest/regression67.py:241-297` / `regression_famous.py:119-169` | D4/D6 | 同样 `--write-baseline` 原地改写 `baseline67.json` / `famous_baseline.json`，存在误写风险。 | 同上：校验+临时文件+原子替换。 |
| `heldout/_zy_all_dump.py:52` / `_zy55_dump.py:55` / `_b5_diag.py:48` / `_zy3_dump.py:53,72,76` / `verify_heldout.py:51` | D4 | 诊断/考古脚本裸 `except Exception:` 吞掉所有异常，考古时可能静默跳过失败案例。 | 仅捕获预期异常（如引擎内部已知豁免），非预期异常记录四柱并抛出。 |

### P1（必修/测试纪律）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `test_chuangong.py:21` | D1/D3 | 全模块 `pytestmark = pytest.mark.xfail(strict=False)`，20 个用例实际不执行；模块本身锁自造 spec 无书锚，属于「保留备查」的死测试。 | 要么删除该模块（已备案伪标），要么改为正常执行并明确标记为内部 spec 契约测试。 |
| `test_f1_gate.py:147-149` | D2 | `test_self_check_rmb_offline` 仅调用 `llm_backend._self_check()`，无返回值/副作用断言，属于「只跑不查」。 | 断言 `_self_check()` 不抛异常并返回预期峰谷价，或至少断言 `_PRICE` 表非空。 |
| `test_subjective.py:185-187` | D2 | `test_payload_is_json_serializable` 仅执行 `json.dumps(payload)`，无 `assert`；异常外无验证。 | 增加 `assert isinstance(json.dumps(...), str)` 或断言 dumps 成功且结果非空。 |
| `test_caiming_m2.py:16` / `test_f1_gate.py:15` / `test_subjective.py:5,13` | D5 | 真·未使用顶层导入：`classify_caifu_view`、`format_report`、`Path`、`ENVELOPE_RULES`。 | 删除。 |
| `test_dayun_objective.py:18` / `test_g9_zihe_g5_g1.py:2` / `test_liunian_k5.py:14` / `test_narrative.py:12` / `test_yingqi_shouyuan.py:26` / `test_yunfan.py:12` / `test_zhengfan_k2.py:15` / `test_zhiye.py:17` / `test_zuogong_m9.py:12` | D5 | 11 个文件导入 `pytest` 但未使用任何 `pytest.raises/mark/fixture`。 | 删除冗余导入。 |
| `test_p0_blindgap.py:22` / `test_body_parts.py:10` / `test_yunfan.py:14` / `test_g9_zihe_g5_g1.py:22` / `test_juefa.py:10` / `test_chuangong.py:17` / `test_gongliang.py:13` / `test_property.py:21` / `test_gongfei.py:10` / `test_zhengfan_shuli.py:18` / `test_f11_yongshen_caiming.py:25` / `test_zeishen_bushen.py:19` / `test_subjective.py:9` / `test_narrative.py:14` / `test_zhengfan_k2.py:17` / `test_dayun_objective.py:20` / `test_zhiye.py:19` / `test_caiming_m2.py:13` | D5/D7 | 18 个测试文件重复 `sys.path.insert(0, os.path.dirname(...))` 手动改路径；pytest 已能发现 `mangpai` 包，冗余且污染全局路径。 | 统一删除；若确有需要，下沉到 `conftest.py` 或 `pyproject.toml`/`pytest.ini` 配置。 |
| `test_body_parts.py:1-30` | D3 | 测试一个已备案「未接线」模块的数据表，测试本身维护 dead data 而非行为契约。 | 若模块长期不接线，将测试改为「数据表存在性+结构」契约并注释说明；或随模块清理一并移除。 |

### P2（建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `test_llm_channel.py:1-757` | D2 | 单文件 757 行、51 个测试函数，虽函数短但维度混杂（L0/L1/L2/N1/锚定/键清单）。 | 按维度拆分为 `test_llm_l0_l1.py`、`test_llm_l2_enum.py`、`test_llm_anchor.py`、`test_llm_n1.py`。 |
| `test_feishu.py:17-140` | D2/D1 | `FakeHTTP`/`FakeClient` 等 mock 类只在本文件使用，其他 feishu 测试难以复用。 | 提取到 `tests/conftest.py` 或 `tests/feishu_fixtures.py`。 |
| `test_juefa.py:17-30` / `test_zeishen_bushen.py:19-46` / `test_p0_blindgap.py:33-35` / `test_g9_zihe_g5_g1.py:26-31` | D1 | 各文件重复定义 `_run(gans, zhis)` / `_ids(r)` / `_skips(r)` / `_wa(...)` 等 helper。 | 下沉到公共 `tests/conftest.py` 或 `tests/helpers.py`。 |
| `heldout/blind_eval.py:304-327` | D3 | `summarize_groups` 按 verdict 文本首词分组，对新增分组或 verdict 文案改动敏感，无单测锁定分组行为。 | 增加 `summarize_groups` 单元测试，覆盖新增未知分组与空分组。 |
| `heldout/snapshots/` | D6 | 快照文件名依赖人工约定，无脚本校验 meta 链连续性（`_meta.note` / `rubric_version` / git_sha）。 | 增加 `tests/test_snapshot_hygiene.py`：校验最新快照存在、meta 完整、文件名符合 `YYYYMMDD_x.json`、rubric_version 与 blind_eval 当前版本一致。 |
| `test_a_llm_redline.py:55-66` / `test_xiangmao.py:102` / `test_d6b_zinv.py:134` / `test_qianyi.py:146` | D2 | 多文件重复「json.dumps 后字符串 in/not in」红线检查模式，无公共 helper。 | 抽 `assert_no_redline(blob, keywords)` 到 helper。 |

### 「绿但没验证」风险清单

| 文件:行号 | 风险 | 说明 |
|---|---|---|
| `test_chuangong.py:21` | 全模块 xfail 不执行 | 20 个测试标记 xfail(strict=False)，pytest 报 XPASS/XFAIL 但实际不验证行为；是最大「绿但不验证」风险。 |
| `test_f1_gate.py:147-149` | 无显式断言 | `_self_check()` 调用即通过，未验证峰谷价/币种结构。 |
| `test_subjective.py:185-187` | 无显式断言 | `json.dumps` 成功即通过，未验证序列化结果结构。 |
| `test_property.py:92-119` | 误报风险 | 顶层语句无 `assert`，实际通过 `_assert_invariants` 内部断言；需保留 helper 命名清晰以避免误读。 |

### 哨兵纪律核查

- **各批次哨兵结构良好**：`test_f1_gate.py`、`test_f11_yongshen_caiming.py`、`test_f12_guanming_juefa.py`、`test_f13_shensha.py`、`test_f14_zaihuo_llm.py`、`test_f15_zhiye.py`、`test_f16_hunyin.py`、`test_f17_xueli_liuqin.py`、`test_f18_shipaige_gongmen.py`、`test_f19_yunfan.py`、`test_d6b_zinv.py`、`test_qianyi.py`、`test_xiangmao.py` 均明确标注书锚/批次，断言具体（命中类型/具体文案/档位/字段），符合「先红后绿」可复现要求。
- **`test_chuangong.py` 非真哨兵**：全模块 xfail，未参与回归门禁，需在后续批次决定删除或转正。

### 快照基建核查

- `blind_eval.py` 快照读写逻辑基本健康：支持 `--out`/`--baseline`/`--diff`/`--rescore`，`_meta` 带 `git_sha`/`rubric_version`/`note`。
- 主要风险在**基线写回**：`calib_assertions.py`、`regression67.py`、`regression_famous.py` 均支持 `--write-baseline`，缺乏原子写与校验，存在人为误操作风险。
- `heldout/snapshots/` 文件 49 份，meta 完整，但缺少自动化校验脚本确认链连续性。

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 4 |
| P1 | 7 |
| P2 | 6 |

---

## H7 · heldout/顶层验证 + 诊断脚本批（2026-08-25）

审查范围：
- 验证基建（核心）：`mangpai/tests/heldout/blind_eval.py`、`mangpai/tests/backtest/regression67.py`、`regression_famous.py`、`mangpai/tests/calib_assertions.py`、`mangpai/verify_mangpai.py`、`mangpai/verify_dayun.py`、`mangpai/verify_layer1.py`、`mangpai/verify_layer3_checkpoint.py`、`mangpai/tests/heldout/verify_heldout.py`、`mangpai/tests/heldout/README.md`
- 诊断脚本（heldout）：`_a1_diag.py`、`_a1_diag2.py`、`_a14_diag.py`、`_b5_diag.py`、`_gm40_diag.py`、`_gm_all_dump.py`、`_gm_sim.py`、`_zy2_detail.py`、`_zy2_sim.py`、`_zy2_sim2.py`、`_zy2_sim3.py`、`_zy3_dump.py`、`_zy3_sim.py`、`_zy4_sim.py`、`_zy_all_dump.py`、`_zy55_dump.py`、`_zy55_feat.py`、`_zy55_sim.py`、`_zy_margin.py`、`_zy_master.py` 等
- 诊断脚本（output）：`_llm_batch_*.py`、`_n2_*.py`、`_w4_sample.py`、`_w5_crosscheck.py`、`_t3_eval.py`、`_t3_dump.py`、`_t3_calibrate.py`、`_t3_anchor_scan.py`、`_v3_*.py`、`_kang_*.py` 等
- 其他：`scripts/build_book_index.py`

### P0（验证基建可信度/误写防护）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `blind_eval.py:288-291` | D4/D6 | `_load_snapshot()` 无 `with`、原地 `pop('_meta')` 修改已加载字典；H6 已标记，本次确认仍影响 `--rescore`/`--diff` 调用方。 | `with open(...) as f: data = json.load(f)`；返回 `data.copy()` 或文档说明副作用。 |
| `blind_eval.py:528` | D4/D6 | `--out` 快照直接 `json.dump(..., open(...,'w'))`，无原子写/校验；中断会留下半写 JSON。 | 先写 `.tmp` 再 `os.replace`；写后可选校验 key 集合。 |
| `calib_assertions.py:300-328` | D4/D6 | `--write-baseline` 用正则逐行改写 `calib_assertions.yaml`，无备份、无校验、无上锁；误操作破坏校准基线。 | 写前校验 items 数量与键集合；先写 `.yaml.tmp` 再原子重命名；或要求 `--force`。 |
| `regression67.py:296-297` | D4/D6 | `--write-baseline` 直接覆盖 `baseline67.json`；同时 `current67.json` 也裸写。 | 同上：校验+临时文件+原子替换。 |
| `regression_famous.py:167-169` | D4/D6 | `--write-baseline` 直接覆盖 `famous_baseline.json`；`current_famous.json` 裸写。 | 同上。 |
| `blind_eval.py:225` | D4 | `eval_cases()` 中 `MangpaiEngine.compute_all()` 裸 `except Exception`，引擎异常被吞并记 `error`，汇总时不区分「单例异常」与「评分结果」。 | 仅捕获预期异常（如输入校验），非预期异常记录 case id 后抛出，避免假 green。 |
| `verify_layer3_checkpoint.py:51-62` | D4 | 10 例校验循环裸 `except Exception: traceback.print_exc(); dir_results[name] = {}`，引擎异常被吞并继续跑，可能假 PASS。 | 仅捕获已知异常；非预期异常抛出让验证脚本以非零退出。 |

### P1（必修/验证纪律）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `calib_assertions.py:300-328` | D3/D6 | `_write_baseline()` 依赖正则匹配 `baseline: [✅⚠️❌]` 单行，YAML 格式一旦换行/加引号即失效；且 `⚠️` 含 VS16 需特殊处理。 | 用 `yaml` 库加载→修改→安全写回，或加格式断言。 |
| `regression67.py:239-297` / `regression_famous.py:117-171` | D1/D4 | 两脚本 judge/统计/写回逻辑高度重复（`order` 字典、回归判定、CAT 分类打印）。 | 抽到 `backtest/_baseline.py` 共享 `BaselineRunner`。 |
| `verify_layer3_checkpoint.py:21-32` | D1 | `CASES` 列表与 `mangpai/calib_zhenbao.py` 的 `CASES` 重复；一处改书锚另一处易漏。 | 从 `calib_zhenbao` 导入或加同步单测。 |
| `blind_eval.py:304-327` | D3 | `summarize_groups()` 按 verdict 文本首词分组，对新增 verdict 文案或标点敏感，无单测锁定。 | 补单元测试覆盖未知分组/空分组；或改用 `score_caiming` 解析函数统一口径。 |
| `heldout/_*.py` 诊断脚本 | D4/D6 | 大量脚本裸写 `/tmp/*.json`（`_zy_all_dump.py:68`、`_zy3_dump.py:121`、`_zy55_dump.py:83`、`_gm_all_dump.py:40`、`_gm40_diag.py:65`），无 `with`、无清理、路径硬编码。 | 统一用 `with open`/临时目录；输出路径改为命令行参数或 `tempfile`。 |
| `scripts/build_book_index.py:75-93` | D4 | 写 `book-index/*.md` 与 `book-index.md` 无原子写；目录不存在时依赖 `mkdir(exist_ok=True)` 但写入失败无恢复。 | 先写 `.md.tmp` 再 `os.replace`；加 try/except 记录失败文件。 |
| `output/_llm_batch_trainset.py:40` | D4 | `MangpaiEngine.compute_all()` 裸 `except Exception`，引擎错误被记 `engine_error` 后该例无校验即落入 batch 结果。 | 细化异常；非预期异常应让批跑失败而非混入有效结果。 |
| `output/_n2_eval.py:148-188` / `_t3_eval.py:145-184` | D1 | `run()` 函数（ThreadPoolExecutor + jsonl append + 汇总）与 prompt 组装大量重复。 | 抽到 `output/_eval_common.py` 共享 runner。 |
| `output/_n2_calibrate.py` / `_t3_calibrate.py` / `_v3_calibrate.py` | D1 | 校准逻辑（一致率、翻转召回、达标判定）三份实现几乎一致。 | 抽到公共校准模块。 |

### P2（技术债/建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `blind_eval.py:476-490` | D4 | `--rescore` 读写快照均无 `with`。 | 改 `with open(...)`。 |
| `regression67.py:270` / `regression_famous.py:143` | D4 | 基线读取 `json.load(open(...))` 无 `with`。 | 改 `with open(...)`。 |
| `heldout/_zy_all_dump.py:52`、`_zy55_dump.py:55`、`_b5_diag.py:48`、`_zy3_dump.py:53,72,76`、`_zy2_detail.py:67`、`_zy_master.py:106`、`_zy55_feat.py:72` | D4 | 诊断脚本为容错使用裸 `except Exception`，会吞 `ImportError`/`SyntaxError` 等。 | 仅捕获 `ValueError`/`AttributeError` 等预期异常。 |
| 全部 heldout/output 诊断脚本 | D7 | 大量 `sys.path.insert(0, ...)` 手动改路径；pytest 已能发现包，冗余。 | 删除；需要时下沉到 `conftest.py` 或 `pyproject.toml`。 |
| 全部 heldout/output 诊断脚本 | D6 | 硬编码 `/tmp/`、快照文件名、batch 目录名（如 `llm_batch_20260818_v5`）、模型名（`deepseek-v4-pro`）。 | 抽到模块级常量并允许环境变量覆盖。 |
| `scripts/build_book_index.py:37-44` | D3/D6 | `is_noise()` 过滤逻辑可能误杀合法短章节标题；`gaoji-ocr` 特殊过滤硬编码。 | 加白名单/注释说明；将 OCR 过滤规则参数化。 |
| `verify_mangpai.py:1-1483` | D2 | 单文件 1483 行，432 项检查全部内联；新增检查需改大文件。 | 按节拆分为 `verify_mangpai_*.py` 或测试函数分组。 |
| `verify_dayun.py` / `verify_layer1.py` / `verify_layer3_checkpoint.py` | D2 | 验证脚本使用全局 `passed`/`failed` 计数器，非 pytest 结构，CI 集成弱。 | 逐步迁移为 `pytest` 用例或至少封装 `main()` 返回非零退出码。 |

### 死脚本/历史残留清单

| 类别 | 文件 | 状态 | 说明 |
|---|---|---|---|
| 在用（CI/管线） | `blind_eval.py`、`verify_heldout.py`、`build_yaml.py`、`extract_cases.py`、`curate.py`、`annotations_heldout.py`、`annotations_meta.py` | 保留 | 留出集管线与盲测门禁核心 |
| 在用（验证） | `verify_mangpai.py`、`verify_dayun.py`、`verify_layer1.py`、`verify_layer3_checkpoint.py` | 保留 | 六件套验证 |
| 在用（LLM 通道评审） | `output/_llm_batch_trainset.py`、`_llm_batch_analyze.py`、`_n2_eval.py`、`_n2_analyze.py`、`_n2_sample.py`、`_n2_calibrate.py`、`_w4_sample.py`、`_w5_crosscheck.py`、`_t3_dump.py` | 保留 | 当前 LLM 加料层评审/校准管线 |
| 历史诊断（可归档） | `heldout/_a1_exp.py`、`_zy2_sim2.py`、`_zy2_sim3.py`、`_zy3_sim.py`、`_zy4_sim.py`、`_zy55_feat.py`、`_zy55_sim.py`、`_zy_margin.py` | 归档 | 已收敛/被后续条款替代的历史模拟 |
| 历史诊断（保留备查） | `heldout/_a1_diag.py`、`_a1_diag2.py`、`_a14_diag.py`、`_b5_diag.py`、`_gm40_diag.py`、`_gm_all_dump.py`、`_gm_sim.py`、`_zy2_detail.py`、`_zy2_sim.py`、`_zy3_dump.py`、`_zy_all_dump.py`、`_zy55_dump.py`、`_zy_master.py` | 保留但注释说明 | 偶尔用于根因分析，不纳入 CI |
| 历史 output（可归档） | `output/t1_gold_review/`、`output/review5_v*/`、`output/review5_v2_e2e_20260821/` 下脚本 | 归档 | 旧轮次评审脚本/结果 |
| 新脚本 | `scripts/build_book_index.py` | 保留 | 索引生成器，需补原子写 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 7 |
| P1 | 9 |
| P2 | 8 |

---

## H8 · 引擎编排 + 边角批（2026-08-25）

审查范围：
- 引擎编排核心：`mangpai/engine.py`
- objective 边角：`mangpai/__init__.py`、`mangpai/objective/__init__.py`（`verify_mangpai.py` 由 H7 覆盖，本批不复审）
- subjective 边角：`mangpai/subjective/__init__.py`、`mangpai/subjective/schools.py`（selectors 注册/保护链机制）
- foundation 首审：`foundation/__init__.py`、`foundation/objective/__init__.py`、`foundation/objective/nayin.py`、`foundation/objective/ganqing.py`

### P0（运行时崩溃 / 静默失败 / 阻塞导入）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `mangpai/subjective/guanming.py:39,139` | D7 | 模块仅导入 `Dict/List/Optional/Set`，但 `classify_guanming_combo` 形参注解使用 `Any`，导致 `from mangpai import ...` / engine 导入链触发 `NameError`，整个包目前无法导入。 | `from typing import Dict, List, Optional, Set, Any`。 |
| `mangpai/engine.py:15,133,145,157` | D7 | `typing.Optional` 未导入，却用于 `_current_age`/`_current_dayun`/`_pair` 注解；修复 guanming.py 后继续触发 `NameError`。 | 在 `from typing import ...` 中补 `Optional`。 |
| `mangpai/engine.py:107-113` | D4 | `_safe_compute` 裸 `except Exception` 捕获所有异常并返回 `None`，engine 编排层统一吞掉所有模块的 `TypeError/ValueError/AttributeError`，导致模块 Bug 静默降级为空结果。 | 仅捕获预期异常（如输入校验），非预期异常记录后抛出；或引入 `EngineComputeError` 显式降级。 |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `mangpai/engine.py:194-683` | D2 | `compute_all()` 约 490 行、40+ 模块调用，顺序耦合强，单文件承担 objective→subjective→summary 全链路。 | 拆分为 `_compute_objective`/`_compute_subjective`/`_build_summary` 三阶段。 |
| `mangpai/engine.py:208-679` | D4/D6 | 模块结果回写模式不一致：`canggan/chang_sheng/xiangfa` 用 `if is not None`，其余用 `or {}`/`or []`；失败时有的缺键、有的空容器，消费者无法区分「无信号」与「异常降级」。 | 统一回写模式：异常时缺键，或统一返回结构化 `{"_error": ...}`。 |
| `mangpai/engine.py:126,142` | D4 | `_auto_liunian_list` / `_current_age` 裸 `except Exception`，系统时间/输入年份异常静默回退。 | 细化异常类型；非法输入显式返回 `None` 并记录原因。 |
| `mangpai/engine.py:524` | D7 | `assess_direction_signals` 在函数体内局部导入，依赖关系被隐藏。 | 上提到模块级；若存在循环导入则解耦。 |
| `mangpai/__init__.py:42-43,58` | D5/D7 | 公共 API 仍导出 `analyze_juefa`/`analyze_chuangong`（chuangong 已弃用、juefa 仅 yongshen 内部使用），却未导出活跃的 `analyze_zinv`/`analyze_qianyi`/`analyze_xiangmao`。 | 清理死导出，补齐当前 selectors 对应模块；或在 __all__ 中显式标注 deprecated。 |
| `mangpai/__init__.py:26-29,61-63` | D7 | `__all__` 与导入符号不一致：导入了 `get_shensha_xiang`/`get_liushi_ganzhi_xiang`/`SHENSHA_XIANG`/`LIUSHI_GANZHI_XIANG` 但未导出。 | 同步 __all__ 或删除未导出导入。 |
| `mangpai/subjective/schools.py:24-44` | D6/D7 | selectors 为硬编码元组，无机制保证 engine 新增/删除键与 selectors 同步；build_payload 对缺失 selector 静默跳过。 | 增加 `test_selectors_cover_engine_keys` 契约测试，或 engine 侧导出 `ENGINE_KEYS`。 |
| `mangpai/subjective/__init__.py:210-216` | D6 | `_synthesize_dayun` 直接访问 `analysis['ji_count']`/`analysis['dayun']`，未验证返回形状；数据异常会崩溃。 | 加形状断言或 `get` 回退。 |

### P2（技术债 / 建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `foundation/objective/__init__.py:19-34` | D7 | 包级 `__all__` 未包含子模块已导出的 `get_nayin_wuxing`/`BEHAVIOR_TYPES`。 | 同步包级 __all__。 |
| `foundation/objective/ganqing.py:671-682` | D6 | `get_ganqing` 返回的 `rules` 是 `GanQingRule` dataclass 列表，非 JSON 序列化；若被上层误入 payload 会触发序列化失败。 | 返回时 `asdict()` 转换，或明确标注「非 payload」。 |
| `foundation/objective/ganqing.py:620` | D6 | `state` 条件匹配使用子串 `s in states`，弱契约，易误命中。 | 改为精确集合成员判定或文档化子串语义。 |
| `mangpai/objective/__init__.py:29` | D7 | `detect_zihe` 被导入但不在 `__all__`，`from mangpai.objective import *` 不可见。 | 加入 __all__ 或删除冗余导入。 |
| `mangpai/engine.py:356` | D5/D6 | `gongshen` 被计算但不在 selectors，仅通过 `narrative` 摘要间接进入 payload；无文档说明是否 intentional。 | 明确是否加入 selectors，或在注释中说明「预消化、不进 LLM 原始 JSON」。 |
| `mangpai/engine.py:401-403` | D6 | `_auto_liunian_injected` 未在 `__init__` 初始化，依赖 `getattr` 兜底；同实例多次调用 compute_all 会残留 True。 | 在 `__init__` 中初始化为 `False`。 |
| `mangpai/subjective/__init__.py:154-169` | D6 | `_resolve` 把纯数字字符串键（如 `'0'`）一律视为列表下标，dict 键为数字字符串时误解析。 | 区分 `isinstance(cur, list)` 与 `isinstance(cur, dict)` 的索引逻辑。 |
| `mangpai/subjective/__init__.py:191-198` | D6 | `selectors == ("*",)` 分支不走 `_trim_dayun`/`_synthesize_dayun`，与显式 selectors 行为不一致。 | 统一补 trim/synthesize。 |
| `mangpai/subjective/schools.py:37-42` | D3 | `zinv/qianyi/xiangmao` 注释写「LLM 七维不扩不进 prompt」，但这三个键均在 selectors 中，会进入 prompt。 | 修正注释，明确「进特征 JSON / 七维叙述」两层区别。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 3 |
| P1 | 8 |
| P2 | 9 |

---

## H9 · 数据/快照基建批（2026-08-25）

审查范围：`mangpai/tests/heldout/cases.yaml`、`merged.json`、`candidates.json`、`review.txt`、`trainset/cases.yaml`、`calib_assertions.yaml`、`heldout/snapshots/`、快照读写逻辑（数据侧）。

### P0（评估污染/运行时崩溃）

无。

### P1（必修/数据卫生）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `mangpai/tests/heldout/README.md:11-12` | 数据卫生/文档陈旧 | README 写 `trainset/cases.yaml` 仅 23 例，实际 294 例；污染路由说明未覆盖 reg67/famous 扩容。 | 更新表格与污染路由说明，与实际文件一致。 |
| `mangpai/tests/heldout/annotations_heldout.py:487` | 数据漂移 | `MANUAL` 4 例（qi04-双胞胎弟弟丧妻、阮玲玉、美容师、卜文命学禄当财）未进入 `merged.json`/`candidates.json`，与 extract→curate→build 管线来源不一致。 | 将 manual 源补录到 merged，或显式声明为旁路并加一致性校验。 |
| `mangpai/tests/heldout/verify_heldout.py:51` | D4 | 排盘循环裸 `except Exception`，非预期引擎异常被吞并仅记错误字符串。 | 仅捕获预期异常；非预期异常记录 case id 后抛出。 |
| `mangpai/tests/heldout/snapshots/` | 快照链/死数据 | 14 份快照无代码/文档引用（20260801_f/f_rescore/p2、20260802_c/l、20260807_m、20260808_n/o/q_rescore、20260814_c、20260817_f8/f9/f14/f15）；且缺少最新基线指针文件。 | 未引用快照归档或加白名单；建立 `LATEST`/`baseline.json` 指针。 |
| `mangpai/tests/heldout/blind_eval.py:524-528` | D4/D6 | `--out` 快照直接覆盖写，中断会留下半写 JSON；无基线指针机制（H7 已报脚本侧，数据侧复现）。 | 先写 `.tmp` 再 `os.replace`；增加 `--baseline latest` 或 `LATEST` 指针。 |

### P2（技术债/建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `mangpai/tests/heldout/blind_eval.py:18-22` | D6/文档 | 帮助文本使用 `snapshots/YYYYMMDD_x.json` 与 `snapshots/上一批.json` 占位名，无实际文件。 | 占位示例加 `<占位>` 标记或改用真实文件名。 |
| `mangpai/tests/heldout/snapshots/` | D6 | 54 份快照 rubric 版本跨度 v3-v8，缺少自动化脚本校验 meta 链与命名一致性（H7 P2 已建议）。 | 增加 `test_snapshot_hygiene.py`。 |
| `mangpai/tests/heldout/candidates.json` 等 | D5 | `candidates.json`、`review.txt`、`merged.json`、`dropped.txt` 仅构建管线引用，CI/测试运行时不消费。 | 在 README 标注为构建产物或移入 archive。 |

### 关键确认

- **评估污染红线**：heldout 215 例与 trainset 294 例按 `bazi+gender` 零重叠；`calib_assertions.yaml` 10 例全部在 trainset 中，且 bazi/gender 与 `trainset/cases.yaml` 完全一致，未进入 heldout。
- **数据漂移**：`merged.json` 与 `candidates.json` 键集合完全一致；`heldout/cases.yaml` 4 例 manual 案例未入 merged，已作为 P1 记录。
- **快照链**：54 份快照均有 `_meta`（git_sha/rubric_version/note），最新 `20260822_g3.json` rubric 为 `v8-20260808`，与 `blind_eval.py` 当前版本一致。

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 0 |
| P1 | 5 |
| P2 | 3 |

---

## H10 · 工具脚本收尾批（output 批跑脚本 + scripts + foundation 深审，2026-08-25）

审查范围：
- output/ 批跑脚本：`_llm_batch_trainset.py`、`_llm_batch_retry.py`、`_llm_batch_analyze.py`、`_llm_batch_rescore.py`、`_n2_eval.py`、`_n2_analyze.py`、`_n2_calibrate.py`、`_n2_sample.py`、`_t3_eval.py`、`_t3_dump.py`、`_t3_calibrate.py`、`_t3_anchor_scan.py`、`_v3_calibrate.py`、`_v3_sample.py`、`_v3_judge_sample.py`、`_w4_sample.py`、`_w5_crosscheck.py`、`_kang_dump.py`、`_kang_verify.py`
- scripts/：`build_book_index.py`
- foundation/：`__init__.py`、`objective/__init__.py`、`objective/nayin.py`、`objective/ganqing.py`

### P0（运行时崩溃 / 脚本无法运行）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `_llm_batch_trainset.py:38-42` | D4 | 裸 `except Exception` 吞引擎异常，错误记录混入 batch（H7 已标残留）。 | 仅捕获预期异常；非预期异常记录 case id 后抛出。 |
| `_w5_crosscheck.py:18,169` | D7 | 导入/调用 G3 已删除的 `_xm_sanitize`，运行即 ImportError/AttributeError。 | 删除该导入与调用，改用锚定行直传。 |
| `_kang_dump.py:5` / `_kang_verify.py:5` | D7 | 硬编码引入 `/root/.openclaw/workspace/fate-system/fate-objective` 外部模块，干净环境无法导入。 | 归档或改为仅依赖本仓库入口。 |

### P1（必修）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `output/_llm_batch_*.py、_n2_*.py、_t3_*.py、_v3_*.py、_w*.py` | D4 | 大量 `open(...)` 读取 yaml/jsonl/json 未用 `with`，句柄泄漏/异常时文件未关。 | 统一改为 `with open(...)`。 |
| `output/_n2_analyze.py:85-87` / `_llm_batch_rescore.py:27` / `_t3_dump.py:102` / `_w4_sample.py:35` / `_w5_crosscheck.py:84` | D4 | 引擎 `compute_all()` 重算无 try，单例异常中断整批分析。 | 捕获预期异常并记录 case id，非预期异常抛出。 |
| `output/_n2_eval.py:148-188` / `_t3_eval.py:145-184` | D1 | runner（ThreadPoolExecutor + jsonl append + prompt 组装）与 `_materials`/`_reading_text` 高度重复。 | 抽到 `output/_eval_common.py` 公共 runner。 |
| `output/_n2_calibrate.py:10-14` / `_t3_calibrate.py:10-14` / `_v3_calibrate.py:10-14` | D1 | 一致率/翻转召回/达标判定逻辑三份重复。 | 抽到公共校准模块。 |
| `output/_n2_sample.py:17-49` / `_v3_sample.py:17-65` | D1 | 抽样逻辑（强制集 + 分层随机补足）重复。 | 合并为统一抽样器。 |
| `output/_w4_sample.py:30-76` / `_w5_crosscheck.py:31-37,56-70` | D1 | `engine_fe`、禁词扫描、无信号如实判定跨脚本重复实现。 | 抽到 `output/_dim_check_common.py`。 |
| `output/_n2_analyze.py:46-58` | D1 | `_has_xiangmao_marker` 与 `llm_prompt._xiangmao_anchor` 重复。 | 复用 `llm_prompt` 的判定函数。 |
| `output/_llm_batch_trainset.py:52` / `_llm_batch_analyze.py:58-62` | D3 | `cost_usd` 实际存人民币（H4），analyze 又按美元乘 7.2，统计口径错误。 | 字段改名 `cost_cny` 并修正输出换算。 |
| `output/_t3_dump.py:126` | D6 | `scrub_hits` 路径拆分假设至少两级 `.`，可能 IndexError。 | 用 `split('.', 2)` 或安全前缀提取。 |
| `output/_t3_anchor_scan.py:17-18` | D7 | 导入 `llm_channel` / `blind_eval` 的私有符号（`_tier_rank`、`_ZY_RULES` 等），brittle。 | 通过公共 API 暴露所需符号或复制必要常量。 |
| `scripts/build_book_index.py:75-93` | D4 | 写 `book-index/*.md` 与 `book-index.md` 无原子写（H7 已标残留）。 | 先写 `.tmp` 再 `os.replace`。 |

### P2（技术债 / 建议）

| 文件:行号 | 维度 | 问题描述 | 修法建议 |
|---|---|---|---|
| `output/*.py` | D7 | 大部分脚本用 `sys.path.insert(0, ...)` + `noqa: E402` 手动改路径；pytest 已能发现包。 | 删除路径操作或下沉到 `pyproject.toml`。 |
| `output/*.py` | D6 | 硬编码 batch 目录名（`llm_batch_20260818`、`llm_batch_20260821_n2_r4`）、模型名（`deepseek-v4-pro`）、seed、达标阈值。 | 抽到模块级常量并允许环境变量覆盖。 |
| `output/_t3_eval.py:1-19` | D5 | 文档自称"五维历史存档"，却仍被 `_v3_judge_sample` 间接使用，职责模糊。 | 归档或让 v3 改用 `_n2_eval` 公共 runner。 |
| `output/_t3_anchor_scan.py:23-39` | D6 | 词族/阈值/GRADE_RANK 硬编码，与校验器口径可能漂移。 | 从 `llm_channel` 复用或外部配置。 |
| `scripts/build_book_index.py:14-25,52,71-72` | D6 | 书目、标题长度过滤、`gaoji-ocr` 特殊规则硬编码。 | 参数化或加注释说明更新机制。 |
| `foundation/objective/__init__.py:23-34` | D7 | `__all__` 遗漏 `get_nayin_wuxing`（H8 残留）。 | 同步 `__all__`。 |
| `foundation/objective/ganqing.py:671-682` | D6 | `get_ganqing` 返回 `GanQingRule` dataclass 列表，误入 payload 会序列化失败（H8 残留）。 | 返回时 `asdict()` 转换或标注非 payload。 |
| `foundation/objective/ganqing.py:620` | D6 | `state` 条件使用子串匹配，弱契约（H8 残留）。 | 改为精确集合成员或文档化子串语义。 |
| `foundation/objective/ganqing.py:563-566` | D6 | `_norm_gan` 多字干只取首字且无警告。 | 加非法输入校验/警告。 |
| `foundation/objective/__init__.py:19-21` | D1 | `NAYIN_WUXING` 与 `mangpai/objective/constants.py` 重复定义（H1 残留）。 | 统一从 foundation 导入。 |
| `foundation/objective/*.py` | D5 | 中性层无任何单元测试，跨流派扩展缺乏回归保护。 | 补 `foundation/objective/test_nayin.py`、`test_ganqing.py` 基础契约测试。 |

### 统计

| 级别 | 数量 |
|---|---|
| P0 | 3 |
| P1 | 11 |
| P2 | 11 |


---

## H11 · subjective 深度补充批（2026-08-25）

> 本批只审不改、零 API，针对 H1/H2/H4/H8 标记的复杂点做**可执行拆分深挖**，输出修复批（H-fix）可直接落地的拆分方案。

### 拆分方案表（3 个大函数）

| 函数 | 行数 | 建议子函数（边界/参数/返回值） | 拆分理由 |
|---|---|---|---|
| `gongliang.analyze_gongliang` | 957 | `_prepare_inputs(zuogong_result, day_gan, gans, zhis, zb_res) -> (day_wx, wa_list, wtypes, fei, gshen, tomb_works, san_he_formed, _zb_*)`：统一 Pillars/自调/上游信号解析<br>`_compute_position_sets(day_wx, gans, zhis, wa_list, fei, gshen) -> (involved_positions, zhi_targets, involved_cats, gong_cats, gan_cats, fei_cats, strong_pos, destructive_pos)`：把位置与十神集合计算抽出<br>`_apply_gong_point_rules(...) -> (points, reasons, yuanshen_hit, yuanshen_pos, chain_len, _zhiku_tombs, _fang_ju_formed, hua_chengju)`：14 条计分规则集中在此<br>`_apply_caps_and_direction(level, raw_level, points, zhi_jing, penalty, hua_chengju, _fangju_zhiku, pocai, yongshen_xiong, fuhe) -> level`：封顶/降档/方向标注<br>`_build_gongliang_result(...) -> Dict`：装配输出、双轨对账、zb 信号录入 | 五阶段职责清晰，可逐阶段写单元测试；当前计分/封顶/装配全挤在一段，嵌套达 5 层 |
| `zuogong_detect.detect_relations` | 850 | `_scan_gan_relations(day_gan, gans, zhis) -> work_actions, work_types, day_he_type, zheng_he`：合并日干合、非日干合、天干克<br>`_scan_shengyong(day_gan, gans, zhis) -> work_actions, sheng_yong_actions, work_types`：天干食伤/地支食伤/内食神格<br>`_scan_zhi_pair_relations(zhis, gans) -> work_actions, work_types`：用注册表一次性扫描六合/暗合/六冲/刑/害/破<br>`_scan_sanhe_banhe(zhis) -> work_actions, work_types, san_he_formed`<br>`_scan_tomb_fuyin_fanyin(zhis, gans, work_actions) -> tomb_works, work_types`<br>`_collect_raw_facts(day_gan, gans, zhis, kong_wang) -> day_changsheng, day_weak_zhis, kong_wang_zhis, entombed_gan_pillars` | 6 组 O(n²) 复制循环可合并为一次通用扫描；生用、三合、墓用逻辑差异大，保留独立子函数 |
| `engine.compute_all` | 490 | `_compute_objective_base(p) -> result`：canggan/chang_sheng/nayin/shensha/binzhu/tiyong/muku/anhe/biqi/wood/soil/he/virtual/zhengfan/shenshu/xiangfa/gongshen<br>`_compute_zuogong_and_derivatives(p) -> (zg, zb_res, result)`：zuogong、zeishen_bushen、gongliang<br>`_compute_yunshi(p, zg) -> result`：dayun/liunian/jiaoyun/shipaige<br>`_compute_subjective_domain(p, zg, relations, yunfan_slice, laoyu_res, direction) -> result`：caiming/guanming/hunyin/.../yingqi_subj/narrative<br>`_assemble_summary(result) -> str`：现有 `_build_summary` 直接挪用 | objective→subjective→summary 三阶段顺序耦合强，拆分后可分别回归；运岁计算集中便于处理 dy_list/liunian 分支 |

### 6 组 O(n²) 复制循环差异与合并方案

| # | 代码位置 | 关系类型 | 核心差异点 | 合并策略 |
|---|---|---|---|---|
| 1 | `zuogong_detect.py:508-525` | 地支六合 | `_check_pair(z1,z2,LIU_HE)`；加 `is_day` 描述 | 统一为 `_scan_zhi_pair_relations`，通过注册表配置：`(type, action, pair_set, require_day, severity, extra_tag)` |
| 2 | `zuogong_detect.py:531-546` | 暗合 | `AN_HE.get(z1)==z2`（有方向）；必须日支参与 | 注册表增加 `directional=True`、`require_day=True` |
| 3 | `zuogong_detect.py:593-609` | 六冲 | `_check_pair(z1,z2,LIU_CHONG)`；`severity='normal'` | 注册表 `severity='normal'` |
| 4 | `zuogong_detect.py:684-701` | 刑 | `_check_pair(z1,z2,XING_PAIRS)`；自刑标记 | 注册表增加 `zi_xing=(z1==z2)` 标签 |
| 5 | `zuogong_detect.py:706-723` | 穿/害 | `_check_pair(z1,z2,LIU_HAI)`；`severity='high'` | 注册表 `severity='high'` |
| 6 | `zuogong_detect.py:726-742` | 六破 | `_check_pair(z1,z2,LIU_PO)`；`severity='high'` | 注册表 `severity='high'` |

合并后只剩一次 `for i in range(4): for j in range(i+1,4):`，循环体按注册表类型判断，减少 5 份复制代码。三合/半合、生、墓用逻辑差异大，不强行合并。

### _safe_compute 模块对照表

| 模块键 | 是否 `_safe_compute` 包裹 | 失败回退值 | 异常是否被吞 | 备注 |
|---|---|---|---|---|
| `bazi` / `input` | 否（直接赋值） | — | 否 | 无计算 |
| `kong_wang` / `di_zhi_relations` | 否（透传） | — | 否 | 无计算 |
| `canggan` | 是 | key 缺失 | 是 | `if is not None` 才写入 |
| `chang_sheng` | 是 | key 缺失 | 是 | 同上 |
| `nayin` | 是 | `[]` | 是 | `or []` |
| `nayin_work` | 是 | `{}` | 是 | `or {}` |
| `shensha` | 是 | `{}` | 是 | `or {}` |
| `binzhu` | 是 | `{}` | 是 | `or {}` |
| `tiyong` | 是 | `{}` | 是 | `or {}` |
| `zuogong` | 是 | `zg={}` | 是 | `if zg is not None` |
| `zeishen_bushen` | 是 | `{}` | 是 | 局部变量 |
| `gongliang` | 是 | `{}` | 是 | `or {}` |
| `muku` | 是 | `{}` | 是 | `or {}` |
| `anhe` | 是 | `{'anhe':[]}` | 是 | 异常/空结果均回退默认值 |
| `biqi` | 是 | `{'biqi':[]}` | 是 | 同上 |
| `wood_type` | 是 | `{}` | 是 | `or {}` |
| `soil` | 是 | `{}` | 是 | `or {}` |
| `he_types` | 是 | `{'he_types':[]}` | 是 | `or {}` 后包装 |
| `virtual_solid` | 是 | `{}` | 是 | `or {}` |
| `zhengfan` | 是 | `{'configuration':'无做功，不论正反','type':'neutral'}` | 是 | 带默认值 |
| `shenshu` | 是 | `{}` | 是 | `or {}` |
| `xiangfa` | 是 | key 缺失 | 是 | `if is not None` |
| `gongshen` | 是 | `{}` | 是 | `or {}`；**selectors 未登记** |
| `dayun_analysis` | 条件+是 | `{}` | 是 | dy_list 非空才计算 |
| `liunian_analysis` | 条件+是 | `{}` | 是 | liunian_data 非空才计算 |
| `jiaoyun_analysis` | 条件+是 | `{}` | 是 | 年份/月柱存在才计算；不在 selectors |
| `shipaige` | 是 | `{}` | 是 | `or {}` |
| `relations` | 是 | `{}` | 是 | `or {}` |
| `yunfan` | 是 | `{}` | 是 | `or {}` |
| `laoyu` | 是 | `{}` | 是 | 局部变量，后复用 |
| `direction` | 是 | `{}` | 是 | 局部 import；不在 selectors |
| `caiming` | 是 | `{}` | 是 | `or {}` |
| `guanming` | 是 | `{}` | 是 | `or {}` |
| `hunyin` | 是 | `{}` | 是 | `or {}` |
| `xueli` | 是 | `{}` | 是 | `or {}` |
| `xiangfa_ops` | 是 | `{}` | 是 | `or {}` |
| `zhiye` | 是 | `{}` | 是 | `or {}` |
| `gongmen_wuzhi` | 是 | `{}` | 是 | `or {}`；已从 selectors 摘除 |
| `liuqin` | 是 | `{}` | 是 | `or {}` |
| `zinv` | 是 | `{}` | 是 | `or {}` |
| `qianyi` | 是 | `{}` | 是 | `or {}` |
| `xiangmao` | 是 | `{}` | 是 | `or {}` |
| `zaihuo` | 是 | `{}` | 是 | `or {}`；payload 再走 `zaihuo_llm_view` |
| `yingqi_subj` | 是 | `{}` | 是 | `or {}` |
| `narrative` | 是 | `''` | 是 | `or ''` |
| `summary` | **否** | 崩溃传播 | **否** | `_build_summary` 直接调用，异常会击穿上层 |

结论：**全部计算模块异常均被 `_safe_compute` 吞掉**，没有任何模块能正确传导非预期异常；仅 `summary` 未包裹会整体崩溃。这是 H8 P0 `_safe_compute` 裸 `except Exception` 的具象化表现。

### selectors 机制评估

- 当前 `MANGPAI_SCHOOL.selectors` 是硬编码元组（41 项），`build_payload` 对缺失 selector 静默跳过、对 engine 多出来的键直接丢弃（如 `gongshen` 已计算但不在 selectors）。
- 保护链：死亡/灾祸通过 `zaihuo_llm_view` + `_scrub_death` 二次过滤；新模块必须同时改 `schools.py`、`tests/test_subjective.py`、`verify_dayun.py` 三处，否则要么进不了 payload，要么测试 count 失败。
- **脆弱点**：缺少 engine 输出键 ↔ selectors 的自动契约。新增键漏登记时，数据会静默丢失（D6b zinv/qianyi/xiangmao 就是人工三处同步才补上）。
- **修复建议（P1）**：增加 `test_engine_keys_covered_by_selectors`：跑一次 reference `compute_all`，断言所有计划进 LLM 的顶层键都在 `selectors` 中；反向断言 `selectors` 中无 engine 永不产出的键。或在 engine 模块导出 `ENGINE_LLM_KEYS` 与 `selectors` 做静态同步断言。

### 同型残留复查

- 裸 `except Exception`：gongliang 自调 `analyze_zuogong`（:297）、自调 `analyze_zeishen_bushen`（:321）、自调 `classify_caifu_view`（:774）、自调 `classify_strength`（:1109）全部吞异常，属于 H2 已统计 4 处的细化确认。
- 口径漂移：`gongliang:864-868` 与 `_day_faction` 同样用 `WX_SHENG.items()` 线性反查印五行，H1/H3 P2 残留，建议统一建 `WX_BEI_SHENG` 反向映射。
- 状态残留：`engine._auto_liunian_injected` 在 `__init__` 未初始化，H8 P2 残留，同实例复调会残留 `True`。

### 本批新发现统计

| 级别 | 数量 | 项 |
|---|---|---|
| P0 | 0 | 无新增运行时崩溃点；H8 P0 `_safe_compute` 裸 `except` 经本批全模块确认 |
| P1 | 4 | ① `analyze_gongliang` 五阶段可执行拆分<br>② `detect_relations` 6 组 O(n²) 循环合并 + 子函数拆分<br>③ `compute_all` 四阶段拆分<br>④ selectors/engine-key 自动契约测试 |
| P2 | 2 | ① `WX_BEI_SHENG` 反向映射替换 `_day_faction`/`gongliang:864` 线性扫描<br>② `engine.__init__` 初始化 `_auto_liunian_injected` |

---

## H12 · 覆盖率核查 + 补漏批（2026-08-25）

审查范围：mangpai/ 全部 Python 文件 + scripts/ + output/ 的 `_*.py` + 顶层 `verify_*.py`。

### 覆盖率核查

全仓范围内共 **176** 个 Python 文件；H1-H11 已覆盖 **162** 个，漏网 **14** 个。

| 文件 | H 批覆盖情况 | 状态 |
|------|-------------|------|
| `mangpai/__init__.py` | H8 | 已审 |
| `mangpai/calib_zhenbao.py` | — | 漏网 |
| `mangpai/engine.py` | H8,H11 | 已审 |
| `mangpai/feishu/__init__.py` | — | 漏网 |
| `mangpai/feishu/bot.py` | H5 | 已审 |
| `mangpai/feishu/client.py` | H5 | 已审 |
| `mangpai/feishu/formatter.py` | H5 | 已审 |
| `mangpai/feishu/router.py` | H5 | 已审 |
| `mangpai/feishu/service.py` | H5 | 已审 |
| `mangpai/objective/__init__.py` | H8 | 已审 |
| `mangpai/objective/advanced.py` | H1 | 已审 |
| `mangpai/objective/anhe.py` | H1 | 已审 |
| `mangpai/objective/bazi_calc.py` | H1 | 已审 |
| `mangpai/objective/binzhu.py` | H1 | 已审 |
| `mangpai/objective/biqi.py` | H1 | 已审 |
| `mangpai/objective/body_parts.py` | H1 | 已审 |
| `mangpai/objective/canggan.py` | H1 | 已审 |
| `mangpai/objective/changsheng.py` | H1 | 已审 |
| `mangpai/objective/constants.py` | H1 | 已审 |
| `mangpai/objective/dayun.py` | H1 | 已审 |
| `mangpai/objective/gongfei.py` | H1 | 已审 |
| `mangpai/objective/gongshen.py` | H1 | 已审 |
| `mangpai/objective/he_types.py` | H1 | 已审 |
| `mangpai/objective/jiaoyun.py` | H1 | 已审 |
| `mangpai/objective/muku.py` | H1 | 已审 |
| `mangpai/objective/nayin.py` | H1 | 已审 |
| `mangpai/objective/shensha.py` | H1 | 已审 |
| `mangpai/objective/shenshu.py` | H1 | 已审 |
| `mangpai/objective/soil_type.py` | H1 | 已审 |
| `mangpai/objective/tiyong.py` | H1 | 已审 |
| `mangpai/objective/virtual_solid.py` | H1 | 已审 |
| `mangpai/objective/wood_type.py` | H1 | 已审 |
| `mangpai/objective/xiangfa.py` | H1 | 已审 |
| `mangpai/objective/yingqi.py` | H1 | 已审 |
| `mangpai/objective/zihe.py` | H1 | 已审 |
| `mangpai/objective/zuogong_detect.py` | H1,H11 | 已审 |
| `mangpai/subjective/__init__.py` | H8 | 已审 |
| `mangpai/subjective/caiming.py` | H2 | 已审 |
| `mangpai/subjective/chuangong.py` | H3 | 已审 |
| `mangpai/subjective/dayun.py` | — | 漏网 |
| `mangpai/subjective/gongliang.py` | H2,H11 | 已审 |
| `mangpai/subjective/gongmen_wuzhi.py` | H3 | 已审 |
| `mangpai/subjective/guanming.py` | H2 | 已审 |
| `mangpai/subjective/hunyin.py` | H2 | 已审 |
| `mangpai/subjective/juefa.py` | H3 | 已审 |
| `mangpai/subjective/laoyu.py` | H2 | 已审 |
| `mangpai/subjective/liunian.py` | — | 漏网 |
| `mangpai/subjective/liuqin.py` | H2 | 已审 |
| `mangpai/subjective/llm_backend.py` | H4 | 已审 |
| `mangpai/subjective/llm_channel.py` | H4 | 已审 |
| `mangpai/subjective/llm_prompt.py` | H4 | 已审 |
| `mangpai/subjective/narrative.py` | H3,H4 | 已审 |
| `mangpai/subjective/qianyi.py` | — | 漏网 |
| `mangpai/subjective/schools.py` | H4,H8 | 已审 |
| `mangpai/subjective/shipaige.py` | H3 | 已审 |
| `mangpai/subjective/xiangfa_ops.py` | H2 | 已审 |
| `mangpai/subjective/xiangmao.py` | — | 漏网 |
| `mangpai/subjective/xueli.py` | H3 | 已审 |
| `mangpai/subjective/yingqi_subj.py` | H3 | 已审 |
| `mangpai/subjective/yongshen.py` | H2 | 已审 |
| `mangpai/subjective/yunfan.py` | H3 | 已审 |
| `mangpai/subjective/zaihuo.py` | H3 | 已审 |
| `mangpai/subjective/zeishen_bushen.py` | H3 | 已审 |
| `mangpai/subjective/zhengfan.py` | H3 | 已审 |
| `mangpai/subjective/zhiye.py` | H2 | 已审 |
| `mangpai/subjective/zinv.py` | — | 漏网 |
| `mangpai/subjective/zuogong_confirm.py` | H2 | 已审 |
| `mangpai/tests/backtest/__init__.py` | — | 漏网 |
| `mangpai/tests/backtest/famous_cases.py` | — | 漏网 |
| `mangpai/tests/backtest/harness.py` | — | 漏网 |
| `mangpai/tests/backtest/regression67.py` | H7 | 已审 |
| `mangpai/tests/backtest/regression_famous.py` | H7 | 已审 |
| `mangpai/tests/calib_assertions.py` | H6,H7 | 已审 |
| `mangpai/tests/heldout/_a14_diag.py` | H7 | 已审 |
| `mangpai/tests/heldout/_a1_diag.py` | H7 | 已审 |
| `mangpai/tests/heldout/_a1_diag2.py` | H7 | 已审 |
| `mangpai/tests/heldout/_a1_exp.py` | H7 | 已审 |
| `mangpai/tests/heldout/_b5_diag.py` | H7 | 已审 |
| `mangpai/tests/heldout/_gm40_diag.py` | H7 | 已审 |
| `mangpai/tests/heldout/_gm_all_dump.py` | H7 | 已审 |
| `mangpai/tests/heldout/_gm_sim.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy2_detail.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy2_sim.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy2_sim2.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy2_sim3.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy3_dump.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy3_sim.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy4_sim.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy55_dump.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy55_feat.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy55_sim.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy_all_dump.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy_margin.py` | H7 | 已审 |
| `mangpai/tests/heldout/_zy_master.py` | H7 | 已审 |
| `mangpai/tests/heldout/annotations_heldout.py` | H9 | 已审 |
| `mangpai/tests/heldout/annotations_meta.py` | H9 | 已审 |
| `mangpai/tests/heldout/blind_eval.py` | H7 | 已审 |
| `mangpai/tests/heldout/build_yaml.py` | — | 漏网 |
| `mangpai/tests/heldout/curate.py` | — | 漏网 |
| `mangpai/tests/heldout/diag_case.py` | — | 漏网 |
| `mangpai/tests/heldout/extract_cases.py` | — | 漏网 |
| `mangpai/tests/heldout/verify_heldout.py` | H7 | 已审 |
| `mangpai/tests/test_a_llm_redline.py` | H6 | 已审 |
| `mangpai/tests/test_anhe.py` | H6 | 已审 |
| `mangpai/tests/test_body_parts.py` | H6 | 已审 |
| `mangpai/tests/test_caiming_m2.py` | H6 | 已审 |
| `mangpai/tests/test_chuangong.py` | H6 | 已审 |
| `mangpai/tests/test_d3_dayun_payload.py` | H6 | 已审 |
| `mangpai/tests/test_d6b_zinv.py` | H6 | 已审 |
| `mangpai/tests/test_dayun_objective.py` | H6 | 已审 |
| `mangpai/tests/test_entry_guards.py` | H6 | 已审 |
| `mangpai/tests/test_f11_yongshen_caiming.py` | H6 | 已审 |
| `mangpai/tests/test_f12_guanming_juefa.py` | H6 | 已审 |
| `mangpai/tests/test_f13_shensha.py` | H6 | 已审 |
| `mangpai/tests/test_f14_zaihuo_llm.py` | H6 | 已审 |
| `mangpai/tests/test_f15_zhiye.py` | H6 | 已审 |
| `mangpai/tests/test_f16_hunyin.py` | H6 | 已审 |
| `mangpai/tests/test_f17_xueli_liuqin.py` | H6 | 已审 |
| `mangpai/tests/test_f18_shipaige_gongmen.py` | H6 | 已审 |
| `mangpai/tests/test_f19_yunfan.py` | H6 | 已审 |
| `mangpai/tests/test_f1_gate.py` | H6 | 已审 |
| `mangpai/tests/test_fb_shensha_yearref.py` | H6 | 已审 |
| `mangpai/tests/test_feishu.py` | H6 | 已审 |
| `mangpai/tests/test_g9_zihe_g5_g1.py` | H6 | 已审 |
| `mangpai/tests/test_gongfei.py` | H6 | 已审 |
| `mangpai/tests/test_gongliang.py` | H6 | 已审 |
| `mangpai/tests/test_guanming_g.py` | H6 | 已审 |
| `mangpai/tests/test_juefa.py` | H6 | 已审 |
| `mangpai/tests/test_laoyu.py` | H6 | 已审 |
| `mangpai/tests/test_liunian_k5.py` | H6 | 已审 |
| `mangpai/tests/test_liunian_yingqi.py` | H6 | 已审 |
| `mangpai/tests/test_llm_backend.py` | H6 | 已审 |
| `mangpai/tests/test_llm_channel.py` | H6 | 已审 |
| `mangpai/tests/test_muku.py` | H6 | 已审 |
| `mangpai/tests/test_narrative.py` | H6 | 已审 |
| `mangpai/tests/test_p0_blindgap.py` | H6 | 已审 |
| `mangpai/tests/test_p2_cong_baoju.py` | H6 | 已审 |
| `mangpai/tests/test_property.py` | H6 | 已审 |
| `mangpai/tests/test_qianyi.py` | H6 | 已审 |
| `mangpai/tests/test_qiyun_jiaoyun.py` | H6 | 已审 |
| `mangpai/tests/test_subjective.py` | H6 | 已审 |
| `mangpai/tests/test_virtual_solid.py` | H6 | 已审 |
| `mangpai/tests/test_wood_type.py` | H6 | 已审 |
| `mangpai/tests/test_xiangmao.py` | H6 | 已审 |
| `mangpai/tests/test_yingqi_shouyuan.py` | H6 | 已审 |
| `mangpai/tests/test_yongshen_r2r3.py` | H6 | 已审 |
| `mangpai/tests/test_yunfan.py` | H6 | 已审 |
| `mangpai/tests/test_zeishen_bushen.py` | H6 | 已审 |
| `mangpai/tests/test_zhengfan_k2.py` | H6 | 已审 |
| `mangpai/tests/test_zhengfan_shuli.py` | H6 | 已审 |
| `mangpai/tests/test_zhiye.py` | H6 | 已审 |
| `mangpai/tests/test_zuogong_m9.py` | H6 | 已审 |
| `mangpai/verify_dayun.py` | H7 | 已审 |
| `mangpai/verify_layer1.py` | H7 | 已审 |
| `mangpai/verify_layer3_checkpoint.py` | H7 | 已审 |
| `mangpai/verify_mangpai.py` | H7 | 已审 |
| `output/_kang_dump.py` | H10 | 已审 |
| `output/_kang_verify.py` | H10 | 已审 |
| `output/_llm_batch_analyze.py` | H10 | 已审 |
| `output/_llm_batch_rescore.py` | H10 | 已审 |
| `output/_llm_batch_retry.py` | H10 | 已审 |
| `output/_llm_batch_trainset.py` | H10 | 已审 |
| `output/_n2_analyze.py` | H10 | 已审 |
| `output/_n2_calibrate.py` | H10 | 已审 |
| `output/_n2_eval.py` | H10 | 已审 |
| `output/_n2_sample.py` | H10 | 已审 |
| `output/_t3_anchor_scan.py` | H10 | 已审 |
| `output/_t3_calibrate.py` | H10 | 已审 |
| `output/_t3_dump.py` | H10 | 已审 |
| `output/_t3_eval.py` | H10 | 已审 |
| `output/_v3_calibrate.py` | H10 | 已审 |
| `output/_v3_judge_sample.py` | H10 | 已审 |
| `output/_v3_sample.py` | H10 | 已审 |
| `output/_w4_sample.py` | H10 | 已审 |
| `output/_w5_crosscheck.py` | H10 | 已审 |
| `scripts/build_book_index.py` | H7 | 已审 |

漏网文件清单：

- `mangpai/calib_zhenbao.py`
- `mangpai/feishu/__init__.py`
- `mangpai/subjective/dayun.py`
- `mangpai/subjective/liunian.py`
- `mangpai/subjective/qianyi.py`
- `mangpai/subjective/xiangmao.py`
- `mangpai/subjective/zinv.py`
- `mangpai/tests/backtest/__init__.py`
- `mangpai/tests/backtest/famous_cases.py`
- `mangpai/tests/backtest/harness.py`
- `mangpai/tests/heldout/build_yaml.py`
- `mangpai/tests/heldout/curate.py`
- `mangpai/tests/heldout/diag_case.py`
- `mangpai/tests/heldout/extract_cases.py`

### 漏网文件补审问题表

| 文件:行号 | 维度 | 级别 | 问题描述 | 修法建议 |
|---|---|---|---|---|
| `zinv.py:143-149` | D4 | P0 | `detect_relations` 裸 `except Exception:`，子息模块入口在关系计算失败时静默降级为空字典，丢失信号且可能隐藏引擎 Bug。 | 仅捕获预期输入异常；非预期异常抛出并记录四柱。 |
| `zinv.py:151-155` | D4 | P0 | `analyze_liuqin` 裸 `except Exception:`，六亲结果静默失败，下游使用空 `liuqin_result` 导致子息星定位回退到私有启发式。 | 细化异常，非预期异常抛出。 |
| `liunian.py:88` | D1 | P1 | 局部定义 `_check_pair`，与 `constants`/`dayun`/`zuogong_detect` 中同名 helper 重复。 | 复用公共 helper。 |
| `liunian.py:43` | D5 | P1 | `_YANG_GANS` 集合定义后未被使用。 | 删除或注释说明保留原因。 |
| `liunian.py:152,321,361` | D7 | P1 | 多处函数内局部 import `yongshen` 符号，降低静态可读性。 | 上提到模块级。 |
| `qianyi.py:63` | D1 | P1 | `_pair_in` 与 `zinv.py` 中同名 helper 重复。 | 抽到 `subjective.utils` 或复用现有工具。 |
| `zinv.py:66,82,88` | D1 | P1 | `_pair_in`/`_gz_of`/`_benqi_shishen` 与 `qianyi`/`liunian` 重复实现。 | 下沉为公共 helper。 |
| `calib_zhenbao.py:118` | D4 | P1 | 顶层循环裸 `except Exception:`，校准案例失败仅打印 traceback 继续执行，可能隐藏回归。 | 仅捕获预期异常；非预期异常记录 case id 后抛出。 |
| `liunian.py:207` | D6 | P2 | `_sheng_wx_of` 线性扫描 `WX_SHENG.items()` 反查印五行，与 H1/H3 指出的低效模式一致。 | 建 `WX_BEI_SHENG` 反向映射统一替换。 |
| `liunian.py:215-265` | D6 | P2 | 地支旺衰评分中月令双倍/当令 +2 等权重为裸 magic numbers，无命名常量。 | 抽 `_MONTH_WEIGHT=2`、`_LING_WEIGHT=2` 等常量。 |
| `qianyi.py:67` | D1 | P2 | `_gz_of` 与 `zinv.py` 重复，岁运条目解析未统一。 | 复用 `zinv._gz_of` 或下沉公共 helper。 |
| `harness.py:10-12` | D7 | P2 | 手动 `sys.path.insert` 改路径；pytest 已能发现包。 | 删除或下沉到 conftest。 |
| `diag_case.py:18-20` | D7 | P2 | 手动 `sys.path.insert` 改路径。 | 删除。 |
| `build_yaml.py:47` | D4 | P2 | `json.load(open(...))` 无 `with`，句柄泄漏。 | 改为 `with open(...)`。 |
| `curate.py:30,49,69` | D4 | P2 | 多处 `json.load/dump(open(...))` 无 `with`；数据文件写回亦非原子。 | 统一 `with open`；关键输出加 `.tmp`+`os.replace`。 |
| `extract_cases.py:179,269` | D4 | P2 | `open(path).read()` 与 `json.dump(..., open(...))` 无 with / 非原子写。 | 统一 `with open`；草稿输出可原子写。 |

> 注：`subjective/dayun.py`、`xiangmao.py`、`feishu/__init__.py`、`tests/backtest/__init__.py`、`tests/backtest/famous_cases.py` 经补审未发现新增 P0/P1/P2 问题。

### 同型残留最终计数（全仓最后一次扫描）

| 同型问题 | 总数 | 涉及文件数 | 说明 |
|---|---|---|---|
| 裸 `except Exception:` | 115 | 30 | 覆盖 H1-H11 已标位置及漏网文件；修复批主要规模依据 |
| 原子写缺失（`json.dump(..., open(...))` 等直接覆盖写） | 12 | 11 | 快照/基线/诊断脚本为主，H7/H10 已大部分标记 |

### 本批统计

| 级别 | 数量 | 项 |
|---|---|---|
| P0 | 2 | `zinv.py` 两处裸 `except Exception:` 吞异常 |
| P1 | 6 | `liunian.py` 重复 helper/死变量/局部导入；`qianyi.py`/`zinv.py` 重复 helper；`calib_zhenbao.py` 顶层裸 except |
| P2 | 8 | `liunian.py` 线性扫描/magic number；`qianyi.py` 重复 `_gz_of`；`harness.py`/`diag_case.py`/`build_yaml.py`/`curate.py`/`extract_cases.py` 路径/句柄/原子写 |

---

## H13 · 代码卫生审查 H-fix 汇总收官批（2026-08-25）

> 本批只审不改、零 API，汇总 H1-H12 全量发现，输出去重总账、H-fix 分批规划、go/no-go 建议与风险提示。

### 一、问题总账（H1-H12 去重后）

H1-H12 原始触发 **498** 处：P0×110 / P1×247 / P2×141。按问题类型去重后约 **45 项核心问题**：

| 严重级 | 问题类型 | 去重后核心项 | 原始触发（文件数） | 代表位置 |
|---|---|---|---|---|
| P0 | 裸 `except Exception:` 吞异常 | ~10 | 115 / 30 | `engine._safe_compute`, `zaihuo.py`, `yunfan.py`, `zinv.py`, `jiaoyun.py` |
| P0 | import/typing 崩溃面 | 2 | 3 / 2 | `guanming.py` `Any`, `engine.py` `Optional`, `advanced.py` 反向依赖 |
| P0 | 入口校验/索引越界 | 3 | 6 / 4 | `dayun_gz_sequence`, `_jd_to_datetime`, `_advance_gz`, `_cand_hua[0]` |
| P0 | 原子写/基线误写 | 3 | 5 / 3 | `calib_assertions.yaml`, `baseline67.json`, `famous_baseline.json`, `blind_eval --out` |
| P1 | 重复代码/工具函数 | ~10 | ~40 / 25 | `_check_pair`, `_compute_shishen`, `_ensure_relations`, `_find_wx_targets`, eval runners |
| P1 | 大函数/高复杂度 | ~8 | ~60 / 18 | `gongliang.analyze_gongliang`, `detect_relations`, `engine.compute_all` |
| P1 | 死代码/未使用参数/导出漂移 | ~8 | ~50 / 20 | `bazi_calc` dead params, `shensha` dead fields, `mangpai/__init__` `__all__`, `chuangong` |
| P1 | selectors/模块契约 | 2 | 3 / 2 | `schools.selectors` 与 `engine` keys, `__all__` 不同步 |
| P1 | 局部导入/循环依赖 | 3 | ~70 / 22 | H2 56 处函数内 import, H3/H8 局部导入, `sys.path.insert` |
| P2 | 命名常量/魔法数 | ~12 | ~45 / 20 | `>=2/>=3` 阈值, NOAA 系数, `DAXIAN` 边界 |
| P2 | 数据/序列化/文档 | ~6 | ~15 / 12 | `json.load(open(...))`, `GanQingRule` dataclass, 快照 README |

P0 中裸 except 约占 **88%**；全量中裸 except 约占 **23%**，重复/局部导入/死代码/复杂度合计约占 **55%**。

### 二、H-fix 分批规划

按依赖拓扑与风险面分批，每批验证均执行六件套红线：`verify_mangpai` / `verify_dayun` / `verify_layer1` / `verify_layer3_checkpoint` / `pytest` / `blind_eval` 快照。

| 批次 | 内容 | 原始触发 | 依赖 | 验证 | 优先级 |
|---|---|---|---|---|---|
| H-fix-1 import/typing 崩溃面 | 补 `Any`/`Optional` 导入；移除 `advanced.py` objective→subjective 反向依赖 | 3 / 2 | 无 | `pytest` import smoke、`verify_mangpai` 全绿 | P0 先行 |
| H-fix-2 异常处理策略批 | 115 处裸 except 按场景改造：输入校验改显式 `ValueError`/警告；模块内部 bug 改抛出 `EngineComputeError`；诊断脚本仅捕获已知异常 | 115 / 30 | H-fix-1 | 错误注入测试 + `blind_eval` 零翻转零抖动 + `verify` 引擎判定零改动 | P0 先行 |
| H-fix-3 原子写批 | 快照/基线/诊断脚本统一 `with open` + `.tmp` + `os.replace`；批跑脚本异常时停止而非混入结果 | 12 / 11 | 无 | 写回 roundtrip、基线哈希不变、`pytest` | P0 先行 |
| H-fix-4 死代码/重复清理批 | 下沉 `_check_pair`/`_compute_shishen`/`_ensure_relations`/`_find_wx_targets`；清理 dead params/死字段/弃用模块 | ~40 / 25 | H-fix-1 | consumers 全替换、`pytest`、heldout 全绿 | P1 |
| H-fix-5 大函数拆分批 | 按 H11 方案拆分 `gongliang.analyze_gongliang`（五阶段）、`detect_relations`（注册表 + 子函数）、`engine.compute_all`（四阶段） | 3 / 3 | H-fix-2 | 新增函数级单元测试 + 六件套全绿 + blind_eval 零翻转 | P1 |
| H-fix-6 selectors 契约批 | 增加 `test_engine_keys_covered_by_selectors`；同步 `__all__`；明确 `gongshen` 等不进 LLM 键 | 3 / 2 | 无 | `test_subjective` count 不抖、`verify_dayun` 全绿 | P1 |
| H-fix-7 评测框架统一批（可选） | `test_snapshot_hygiene.py`、公共 `assert_no_redline` helper、诊断脚本 `sys.path` 清理 | ~10 / 8 | H-fix-3 | `pytest` | P2 |
| H-fix-8 文档/基线同步批 | 更新 heldout README、建立 `LATEST` 快照指针、归档旧 output 脚本 | ~5 / 4 | H-fix-3 | 文档 review + 快照链校验 | P2 |

### 三、go/no-go 建议

| 批次 | 判定 | 理由 |
|---|---|---|
| H-fix-1/2/3 | **阻塞，必须先 go** | 对应 P0 部署机崩溃面、异常吞没导致静默失败、基线误写导致评估污染 |
| H-fix-4/5/6 | **建议进下一 milestone，不阻塞发版** | 纯代码质量与可维护性，改错会触发六件套红，但当前引擎输出已稳定 |
| H-fix-7/8 | **可后置** | 测试框架与文档卫生，不影响线上判定 |

### 四、风险提示

1. **异常处理改造**：把“吞”改为“抛”可能暴露当前被掩盖的真实崩溃面。必须先用错误注入测试（构造非法干支、空 actions、越界索引）验证每处改造只抛预期异常；再以 heldout 215 例盲测确保零翻转、零抖动。
2. **大函数拆分**：`detect_relations`/`analyze_gongliang` 是 subjective 核心，拆分后即使逻辑等价也可能因返回值结构或副作用变化导致下游误判。每阶段拆分后先加函数级哨兵，再跑六件套；禁止在拆分中顺带改口径。
3. **死代码/重复清理**：`soil_type` 等字段可能是 prompt-only，删除前必须确认 `build_payload`/`formatter` 无隐式读取；`_check_pair` 等公共 helper 下沉后需同步 `liunian.py`/`qianyi.py` 等漏网文件。
4. **selectors 契约**：新增键若漏登记会静默丢失信号，新增测试必须在 engine 改键时先红后绿。

### 五、本批统计

| 级别 | 原始触发 | 去重后核心项 |
|---|---|---|
| P0 | 110 | ~18 |
| P1 | 247 | ~31 |
| P2 | 141 | ~18 |
| 合计 | 498 | ~45（跨级合并后） |

---

## H-fix-1 新发现（2026-09-17，执行中登记）

| 文件:行号 | 维度 | 级别 | 问题描述 | 处置 |
|---|---|---|---|---|
| `mangpai/subjective/yunfan.py:653` | D7 | P0 | f-string 内嵌同名单引号 `f'{''.join(...)}'`，PEP 701（3.12+）才合法，3.11 import 即 SyntaxError；H8 仅报 typing 两处，此系双版本冒烟实测抓到的第三处崩溃面 | **本批已修**（内层改双引号，输出逐字节不变） |
| `mangpai/tests/test_f1_gate.py:46` vs `mangpai/feishu/router.py:35` | 测试漂移 | P1 | e88d6bc 将 HELP 隐私告知去 DeepSeek 具体名（通用化「第三方大模型服务」），但测试仍断言 `'DeepSeek' in h`——HEAD 即存量红，pytest 1 failed（839+1xf+19xp 绿） | 待修（改测试断言对齐 router 文案，或回书裁定）；非 H-fix-1 引入 |

### H-fix-1 轻量抽查（5 关键模块，只记录不改；k3-256k 子代理执行，主会话复核）

| 文件:行号 | 级别 | 问题描述 |
|---|---|---|
| `engine.py:179` | P1 | `_current_dayun` 对显式 `end_age: None` 注入未防 TypeError；:411/:465 调用不在 `_safe_compute` 内会炸 compute_all |
| `engine.py:407` | P2 | `liunian_data` 注入 truthy 非 dict 时 `.get` 抛 AttributeError，同在保护网外 |
| `guanming.py:725,775,780` | P2 | `classify_hangye_xiang`/`detect_guansha_yougen` 无四柱长度校验，短列表 IndexError（同文件 :196 有校验，口径不一） |
| `guanming.py:514,520` | P2 | `PILLAR_KEYS.index(...)` 无 `in` 前置校验，异构 relations 触发 ValueError |
| `zuogong_detect.py:551-570` | P2 | `san_he_participants` 循环外初始化只 append 不重置，双三合组时串组（当前四柱下实际不可达，潜伏改漏） |
| `zuogong_detect.py:1004-1009` | P2 | `_chong_pair`/`_he_pair` 与既有 `_check_pair` 完全等价的冗余封装 |
| `gongliang.py:720-721` | P2 | `_po_bao` 过滤「天干包局」为死代码（互斥前提，永滤不到） |
| `zaihuo.py:388-389` | P1 | 凶神汇聚用 `_cat=='官杀'`（含正官）却标 `'七杀'`——正官误标且误计入凶神计数影响 risk 升档 |
| `zaihuo.py:734,736` | P2 | `zaihuo_llm_view` 缺 `'risk'` 键时 `.get` 放过、直取抛 KeyError |
| `zaihuo.py:226-227,238-239,274,367-368` | P2 | 导出的 `classify_jibing`/`detect_chehuo` 无四柱长度校验（`analyze_zaihuo` :674 有，导出入口无） |
| `zaihuo.py:571-577` | P2 | 「禄入墓被冲开」未走 `is_entomb` 验证禄真实入墓，可误报 marker；与 :532-545 口径差无注释 |
| `zaihuo.py:517-526,478` | P2 | 注释「刑破穿害」与代码 `('刑','破','穿','冲')` 不符（含冲），未备案 |

> 合计 12 条（P1×2、P2×10），无 P0。两个 P1 建议 H-fix-2a 错误注入框架落地时优先处置。

---

## H-fix-2a（2026-09-17，执行登记）

### 本批落地

| 项 | 处置 |
|---|---|
| 错误注入框架 | `mangpai/tests/test_inject_faults.py` 36 测（非法干支/畸形 bazi_data/空 actions/越界/JSONDecodeError/end_age=None + calib 10 例冒烟）；红阶段实测 8 注入点全暴露旧失败面（裸 `substring not found`/IndexError/AttributeError 穿透、畸形输入静默接受、end_age=None TypeError 击穿 compute_all、JSONDecodeError 穿透） |
| `_safe_compute` 37+ 模块分类 | 传导 14（shensha/zuogong/zeishen_bushen/gongliang/muku/zhengfan/relations/yunfan/laoyu/direction/caiming/guanming/zhiye/zaihuo → `EngineComputeError` 包装传导）；降级 29（warning + `_write` 回写 `_MODULE_DEFAULTS` 明确结构）；白名单 2（`_auto_liunian_list`/`_current_age` 收窄为时钟/数值类异常+记录原因） |
| 回写契约统一（H8 P1） | `or {}`/`or []`/`or ''`/缺键三态 → `_write()` 显式 `is not None` + 失败写 `_MODULE_DEFAULTS` 深拷贝；engine.py 裸 `except Exception` 3→1（仅剩 _safe_compute 分流转折点） |
| 入口校验 3 项 P0 | `dayun_gz_sequence`/`_advance_gz` 非法干支 → ValueError 带「非法干支」定位；`_cand_hua[0]` 同源复用 `_hua_actions`+判空守卫（当前不可达，防御纵深）；`MangpaiEngine.__init__` 新增 `_validate_bazi_data`（非 dict/缺四柱/非法干支 → `EngineInputError`） |
| `JSONDecodeError` 包装（H4 P0） | llm_backend HTTP 200 非 JSON/非法 UTF-8 → `LLMBackendError('HTTP 200 但返回体非 JSON…')` 走重试，不再穿透 |
| `engine.py:179` end_age=None（H-fix-1 抽查 P1） | `_current_dayun` 显式 None→`sa+10` 缺省 + 非数值 sa/ea 跳过守卫 |

### H-fix-2a 暴露/裁定（既有问题处置记录）

| 项 | 裁定 |
|---|---|
| `zaihuo.py:388` 正官误标「七杀」（H-fix-1 抽查 P1） | **书锚已核**：gaoji 牢狱章「正官、七杀：代表法律、规章、约束、官非。为牢狱之灾的直接符号」（gaoji-ocr ~14843-14848）——`_cat=='官杀'` 计入凶神**计数**有书锚，不动；误在 **label 文本**（正官盘标「七杀」）。但 label 进 `xiong_shen`→`desc` 输出文本，修正=正常路径字节变更，违本批红线「引擎正常路径输出逐字节不变」→ **延后至文本/判定批**，修法已给定：按实际十神标「正官」/「七杀」（可并存），计数逻辑不动 |
| 吞改抛暴露真实 bug | 六件套全量（215 heldout + 294 trainset 经 blind/pytest + 67 + famous + calib）无一传导类模块在合法输入下抛异常——未暴露存量崩溃面 |

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict `.get` AttributeError（P2，H-fix-2b/c 或守卫批）
- `_auto_liunian_injected` `__init__` 未初始化（P2 备案维持）
- subjective 层 67 处裸 except → H-fix-2b；诊断/验证脚本 → H-fix-2c

---

## H-fix-2b（2026-09-18，执行登记）

### 阶段 0 计数定边界（实测为准）

- 实测 `grep -rn "except Exception" mangpai/subjective/*.py` = **91 处**（v2 计划口径 67，漂移 +24）：`except Exception:` ×90 + `except Exception as e:` ×1；裸 `except:` = 0。
- 逐文件：caiming 11 / zhiye 10 / yongshen 9 / liuqin 9 / zaihuo 7 / xiangfa_ops 7 / gongmen_wuzhi 7 / zuogong_confirm 5 / hunyin 5 / guanming 4 / gongliang 4 / yunfan 3 / narrative 3 / laoyu 3 / xueli 2 / zinv 2。

### 改造分类（91 处全处置，复用 2a 模式）

- **传导 70**：删 try/except（`_ensure_relations`×10、`_ensure_muku`×2、缺省自调 analyze_zuogong/zhengfan/muku/resolve_shensha/classify_strength 等主链计算），异常上抛交 engine `_safe_compute` 统一分流（传导类→EngineComputeError、降级类→warning+`_MODULE_DEFAULTS` 整体降级，消灭「部分空」）；前置守卫原样保留。
- **安全降级 18**：保留 catch 显式化（`except Exception as e:` + `_logger.warning(exc_info=True)`），降级 dict 加 `'compute_error': True`——可选增强信号：方向总线 A3 只读切片×4（hunyin/liuqin/gongmen_wuzhi/zaihuo 特例核实 engine 恒传后转传导）、zuogong_confirm 装饰信号×5（binzhu/tiyong/wood/soil/virtual）、caiming zihe/G9×3、yongshen juefa、gongliang 从格标注、zhiye xiangfa 互证、liuqin 换象互证、narrative LLM 边界。
- **白名单 4**：xiangfa_ops foundation 软依赖→`ImportError`；narrative json.dumps→`(TypeError, ValueError)`；narrative 年龄计算→`(TypeError, ValueError, OverflowError)`；narrative LLM 调用→`(ImportError, OSError)+anthropic.APIError`（软解析）。
- **改后计数 91→17**（17 处全为显式 `except Exception as e:` 降级点，零裸 except）。

### 注入扩展（test_inject_faults.py 36→79 测，+43）

7a `_ensure_relations` 传导 10 模块参数化×2（含守卫语义不变反断言）/ 7b `_ensure_muku`×2 / 7c yunfan 缺省自调×3 / 7d gongliang×2 / 7e zinv×2（H12 P0 私有启发式回退封死）/ 7f 降级契约×2 / 7g engine 层契约×12（降级类 6 键 `_MODULE_DEFAULTS` 一致性 + 传导类 6 键 EngineComputeError）。
**哨兵纪律**：stash 未修复代码实测 **19 红**（全传导注入点：7a×10+7b×2+7c×3+7d×2+7e×2）→ 修复后 79 全绿。

### H-fix-2b 暴露/发现登记

| 项 | 裁定 |
|---|---|
| 吞改抛暴露真实崩溃面 | **无**——509 例六件套+分片累计 3000+ 例横扫零触发，无 load-bearing catch |
| `gongmen_wuzhi.classify_gongjianfa` muku 自调结果（open_tombs）从未使用=死调用 | P2 转 H-fix-4 死代码批 |
| `xiangfa_ops.py:1331-1334` if/else 两分支相同死逻辑 | P2 转后续批 |
| `caiming._zeishen_jingzhi` docstring 残留旧吞咽口径（「异常一律按不净」） | 本批顺手清（注释零行为） |
| `zaihuo.py:388` 正官误标「七杀」 | 维持 2a 裁定：正常路径字节变更，延后文本/判定批 |

### 六件套（全绿）

verify 432+70+64+20 / pytest **919 passed**+1xf+19xp / blind vs `snapshots/20260917_hfix2a.json` **heldout+trainset 零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）/ 双 seed 逐字节一致 / 67/famous 无变化 / calib 常驻 2 条零新增。引擎判定零改动（compute_all 正常路径逐字节不变）。快照=`snapshots/20260918_hfix2b.json`；回滚点=tag `hfix2b-pre`。

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict `.get` AttributeError（2a 遗留 P2，2c/守卫批）。
- 诊断/验证脚本 ~20 处裸 except → H-fix-2c。

---

## H-fix-2c（2026-09-18，执行登记 · 异常策略线收官）

### 阶段 0 计数定边界（实测为准）

- 任务书口径两 grep = **15 处**（`output/*.py` 3：`_kang_dump`×2/`_llm_batch_trainset`×1；`mangpai/tests/*.py`+`scripts/`+`heldout/` 12：blind_eval×2/verify_heldout×1/诊断脚本×9）。
- 加任务书 H7/阶段1 显式点名的验证脚本 3 处（`verify_layer3_checkpoint.py:58,71`、`calib_zhenbao.py:118`），**实际改造 18 处**。

### 改造分类（18 处全处置，脚本层三原则）

- **验证脚本 6 处（禁吞引擎异常，假 green 清零）**：
  - `blind_eval.py:225` **传导**——引擎异常记 case id + 快照 error 字段 + 打印，main() 收尾按 error 计数 `sys.exit(1)`（快照/diff 照常产出供诊断）；正常路径零 error → 输出逐字节不变。
  - `verify_layer3_checkpoint.py:71`（B 环节）**传导**——异常补 `check(..., False)` 显式失败；旧版静默置 `{}`，未被下游断言覆盖的案例（如第1期）失败可假绿（哨兵实证 exit 0）。A 环节 :58 旧版已 `check False` 计失败，维持。
  - `calib_zhenbao.py:118` **传导**——打印 case id + traceback 后 `raise`（H12 P1）。
  - `verify_heldout.py:51` **传导（失败通道，既已合规）**——异常即案例失败、exit 1；哨兵锁回归，代码不动。
  - `blind_eval.py:284` `_git_sha` **白名单**——收窄为 `(OSError, subprocess.SubprocessError)`（git 不可用环境降级，与引擎无关）。
- **批跑脚本 3 处（单例失败不中断整批，不静默）**：`_llm_batch_trainset.py:40` 已有 engine_error 记录+汇总计数，本批补失败案例 id 清单打印；`_kang_dump.py:41,47` 补 traceback 留痕。
- **诊断脚本 9 处（允许降级但必须打日志）**：`_b5_diag:48`（补 case id）/`_zy2_detail:67`/`_zy3_dump:53,72,76`/`_zy55_dump:55`/`_zy55_feat:72`/`_zy_all_dump:52`/`_zy_master:106`——降级默认值保留，逐处补 `!! {case_id} {函数} 异常` 打印。
- 改后脚本层裸 `except Exception`（无 `as e` 无日志）仅剩 `verify_heldout.py:51` 一处（失败通道合规）；无裸 `except:`。

### 哨兵（test_verify_integrity.py 6 测，先红后绿）

注入引擎异常 → 验证脚本必失败：blind_eval error 记录/exit 1、layer3 compute_all 异常 exit≠0、layer3 B 环节选择性注入（第1期，旧版假绿洞）exit≠0、calib re-raise、verify_heldout exit 1 回归锁。**红阶段实测 3 红 3 绿**（3 红=真假绿洞：blind_eval 退出码/layer3 B 环节/calib re-raise；3 绿=既合规项），修复后 6/6 绿。

### 暴露/发现登记

- 吞改抛暴露真实崩溃面：**无**（六件套 509 例零触发）。
- `verify_layer3.py:51-62` A 环节旧版实为显式失败（check False），H7「假 PASS」定性仅 B 环节成立——已按实况修正认知并只改 B。

### 六件套（全绿）

verify 432+70+64+20 / pytest **925 passed**+1xf+19xp（919+6 哨兵）/ blind vs `snapshots/20260918_hfix2b.json` heldout+trainset 零翻转零抖动 / 双 seed 逐字节一致 / 67/famous 无变化 / calib 常驻 2 条零新增。引擎判定零改动（脚本层全部改动只在异常路径）。快照=`snapshots/20260918_hfix2c.json`；回滚点=tag `hfix2c-pre`。

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict `.get` AttributeError（2a 遗留 P2，守卫批）。
- 异常策略线（2a 引擎层 / 2b subjective 层 / 2c 脚本层）**收官**。

---

## H-fix-3（2026-09-18，执行登记 · 原子写批 + llm_channel 免责提级项）

### 阶段 0 写回点清点（复核 grep，补全任务书清单）

- **基线/快照级（原子写 + 写入前校验 + backup）**：`calib_assertions.py`（calib YAML，最高优先）/ `blind_eval.py` 快照 `--out` + `--rescore` 写 / `regression67.py` / `regression_famous.py`（`--write-baseline` 与 current 存档两路）。
- **管线产物（原子写 + 校验）**：`curate.py` merged.json + review.txt / `extract_cases.py` candidates.json / **补全项** `build_yaml.py` heldout/trainset cases.yaml + dropped.txt（评估数据源，原清单未列）。
- **索引**：`scripts/build_book_index.py` 总表 + 分文件 2 处。
- **诊断 /tmp 写（顺带，6 处全改）**：`_gm_all_dump`/`_zy_all_dump`/`_zy55_dump`/`_gm40_diag`/`_zy_margin`/`_zy3_dump`。
- **读取侧句柄泄漏顺带修**（H6/H7 P0/P2）：`blind_eval._load_snapshot` + `--rescore` 读 / `regression67`/`regression_famous` baseline 读 / `curate.py` candidates 读 / `extract_cases.py` 原文读 / `build_yaml.py` merged 读，全部 `with open`。

### 落地

| 项 | 处置 |
|---|---|
| 公共工具 | `mangpai/tests/_atomic_io.py`：`atomic_write`（写 `.tmp`+fsync+`os.replace`，`backup=True` 留存 `.bak`）+ `atomic_write_json`（dumps→loads 反解析 + `validate(parsed)` 回调，抛错即拒绝写入） |
| 基线写回校验 | calib：`_validate_baseline_yaml`（YAML 反解析 + cases/items 条数对齐计算结果 + baseline_counts 在场）；regression67/famous：`_validate_baseline`（非空 + verdict 值域 ✅⚠️❌——⚠️ 双码点 U+26A0+VS16，须用字符串元组，frozenset('✅⚠️❌') 拆码点会全漏，calib 注释同款教训）；blind 快照：`_validate_snapshot`（_meta.rubric_version 在场 + 至少一 split 非空）；curate/extract/build_yaml 各自关键字段校验 |
| `--write-baseline` 防护 | 不加 `--force`（保持既有调用方兼容），改采**非破坏性防护**：覆盖既有基线前自动留存 `<path>.bak` + 写入前校验拒绝异常内容；原子替换杜绝半写 |
| llm_channel 免责提级（H4 P1） | `validate='reject'` L0 拦截降级补 `_DISCLAIMER_LINE`（llm_channel.py:467）；四条降级路径逐条核对：LLM 不可用 ✓ / JSON 失败 ✓ / 死亡红线 ✓ / L0 拦截 **补后 ✓**。`not call_llm` 调试预览路径（:442）非降级通道，不带免责=设计内 |

### 哨兵（先红后绿）

- `test_atomic_io.py` 8 测：写入中途失败（fsync/replace 注入 OSError）→ 目标完好 + `.tmp` 残留；validate 抛错拒绝写入；backup 留存 `.bak`；calib 非法 YAML/条数不符拒绝写入（SystemExit）；calib 端到端改写 + `.bak` + 源 YAML 结构异常拒写原文件不动。
- `test_f1_gate.py::test_reject_l0_degrade_carries_disclaimer`：L0 reject 路径免责——**stash 实测先红后绿**（旧码 1 failed，修复后绿）。

### 六件套（全绿）

verify 432+70+64+20 / pytest **934 passed**+1xf+19xp（925+9 哨兵）/ blind vs `snapshots/20260918_hfix2c.json` heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）/ 双 seed 逐字节一致 / 67/famous 无变化（current67/current_famous 重写后逐字节不变）/ calib 常驻 2 条零新增 / build_book_index 重跑输出逐字节不变。引擎/主观层判定零改动（本批只改脚本 IO 与 llm_channel 降级文案）。快照=`snapshots/20260918_hfix3.json`。

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict `.get` AttributeError（2a 遗留 P2，守卫批）。
- H5 P1 formatter.DISCLAIMER 与 llm_channel._DISCLAIMER_LINE 文本重复（统一化属 H-fix-4 清理面）。
- output/ 批跑脚本的 jsonl append 写（`_n2_eval`/`_t3_eval` 等）为追加模式非覆盖写，不入原子写范围，标注不改。

---

## H-fix-4a（2026-09-18，执行登记 · 死代码/死数据清理批——纯删除类）

### 阶段 0 「真死」核查（全仓 grep 证据，覆盖 mangpai/ + foundation/ + scripts/ + tests/ + output/ + docs/）

| 项 | 证据 | 处置 |
|---|---|---|
| `objective/advanced.py` 整模块（6 eager re-export + `__getattr__` lazy-import subjective.zhengfan 反向依赖） | `grep advanced` 全 .py 仅自引用 6 处（自身 docstring/函数），零调用方 | **整模块删除**（git rm） |
| `SHIPAI_DOMAINS`/`METHODOLOGY`（shipaige.py:107/120） | 全仓仅自身定义 + 修批C 明议「留作碎片原文档案」（KB 2026-08-22 记载） | **不删**（既有留档决议优先，见「未删待议」） |
| `subjective/chuangong.py` + `test_chuangong.py` | engine 零消费；消费方仅 `mangpai/__init__.py` 死导出 + 20 条全 xfail 锁自造 spec 测试（H6 裁定可删）；grep 无其它 import | **删模块+删死测试+删 `mangpai/__init__.py` 导出**；`docs/chuangong-spec.md` 留档 |
| `subjective/gongmen_wuzhi.py` 整模块 | engine.py:718 仍写 `result['gongmen_wuzhi']`（`test_a_llm_redline.py:127` 断言键保留=修批A③锁定决策）；删除将改 compute_all 输出键 → 违红线 | **不删整模块**（见「未删待议」），仅删内部死调用 |
| gongmen `classify_gongjianfa` muku 死调用（:261-262） | `muku`/`open_tombs` 赋值后函数体（264-349）零引用；`analyze_muku` 顶层导入仍被 :189（classify_junguan）使用故保留 | **删 2 行死调用** |
| `xiangfa_ops.py:1326-1329` if/else 同支 | 两分支均 `day_gan = p.day_gan` | **塌缩为单赋值** |
| `gongliang.py:717-718` `_po_bao` 滤「天干包局」 | 互斥前提证明：天干包局须 `_gy==_gh`（:697）→ `_cat_gy==_cat_gh` → 单元 frozenset 不可能命中 `_OPPOSITE`（两元集）→ `_po_bao` 恒 False 于该形态在场时，过滤永不生效 | **删死过滤**（`_po_bao` 变量仍用于 :715 十神包局 gate，保留） |
| `dayun.py:285` `_analyze_tomb_effect` 死局部 `dy_wx` | 函数体内零引用（grep dy_wx 仅 84-228 他函数活用途） | **删 1 行** |
| `liunian.py:43` 死常量 `_YANG_GANS` | 全仓零引用 | **删 1 行** |
| `virtual_solid.py:28` 死别名 `_GAN_WX_LOOKUP = GAN_WX` | 仅本模块 3 处自用；改直用 `GAN_WX` 后删别名 | **改名引用 3 处 + 删别名** |
| `zihe.py:50-51` isinstance 防御死分支 | `constants.XING_PAIRS:88-94` 全部字面 tuple（12 条全核对），防御分支永不可达 | **删分支** |
| `jiaoyun.py:189` `if not span` 分支 | H1 称 span=9 恒真；但该分支承载公开 API `span=0/None` 边界语义，删除改变边缘行为 | **不删**（宁留勿删，见待议） |
| `detect_relations` 死分支 | H1 所报均为重复逻辑/大函数拆分面（work_types 内部 gate 等），无纯死分支 | 留 H-fix-4b |
| `foundation/objective/__init__.py` `__all__` 遗漏 `get_nayin_wuxing`（H10/H8 P2） | 子模块已导出、verify_layer1:13/71 为活读者 | **补齐 import + __all__**（非删除） |
| `NAYIN_WUXING` constants 副本（H10/H1 P2） | 改前程序化断言两副本逐字节相等（30/30 键值全同）；foundation 为单一事实源 | **constants.py 改为 re-export import**，`jiaoyun.py` 等消费方零改动 |
| `virtual_solid` 死计数字段 / `soil_type` wet/dry / `shensha` 华盖 year_ref 等输出面死字段 | 均为 engine/payload 输出字段，删除=正常路径字节变更，违本批红线 | **不删**（须专门输出面批，见待议） |
| 8 历史模拟脚本（H7 清单） | 全 .py 零 import（仅 docs/CHANGELOG 历史记述提及） | **git mv → `mangpai/tests/heldout/archive/`**（保留历史，不删） |

### 改名（D 类：cost_usd → cost_cny）

- 字段实际存人民币（2026-08-21 起，H4 P1 + H10 P1 确认的命名滞后）。全仓消费面 12 处全改：`llm_backend.py:98,161`（docstring+返回键）、`llm_channel.py:409`（format_reading ¥ 标签处）、`output/_llm_batch_trainset.py:52,85`（写+汇总）、`output/_llm_batch_analyze.py:58,62`（读+**修正错误换算**：删 `×7.2` 美元折算，直出 `¥`）、`output/_n2_eval.py:170,186-188`、`_t3_eval.py:167,184-186`、`_llm_batch_retry.py:41-42`（读侧均双键兼容历史批 `cost_usd`）、`output/review5_v4_20260821/audit_v4.py:59`（归档脚本活调用侧同步）、`test_f1_gate.py:67`、`test_llm_channel.py:750`（mock 同步）。**首轮 grep 被 head_limit 截断漏 4 处在用管线脚本，二轮全量复核补齐**。
- 历史 jsonl 数据文件不改（旧键值口径不变，读侧双键兼容）；`output/t1_gold_review/v4pro_review.py` 读历史数据不归档不动（H7 已标可归档，留 H-fix-8）。
- 文档同步：`docs/llm-channel-20260818.md` 3 处字段名更新（历史口径节保留 `cost_usd` 字样=史实）。
- 抽查：`llm_backend._self_check()` 离线跑过（峰 ¥3.0/¥9.0、谷 ¥1.5/¥4.5 断言绿）；pytest test_llm_backend 绿。

### 未删待议清单（分诊纪律：宁留勿误删）

| 项 | 理由 |
|---|---|
| `SHIPAI_DOMAINS`/`METHODOLOGY` 死数据 | 修批C 明议「留作碎片原文档案」，与本批删除清单冲突 → 从旧议，不删 |
| `gongmen_wuzhi.py` 整模块下线 | engine result 键保留是修批A③/F18 锁定决策且有哨兵断言；删除违「输出逐字节不变」红线 → 须专门批（先撤 engine 键+快照换基线） |
| 输出面死字段（virtual_solid counts / soil wet·dry / 华盖 year_ref 等） | 删除即变 payload/compute_all 字节 → 须专门「输出面」批（红线冲突） |
| `jiaoyun.py:189` `if not span` | 公开 API 边缘语义（span=0/None），非纯死 → 留 |
| `liunian.py:47` `_YANG_REN`/`_YANG_REN_FULL` 别名 import | F13 明注「别名兼容」刻意保留（noqa F401）→ 不动 |
| `mangpai/__init__.py` `analyze_juefa` 导出 | H8 P1 列为候选但 juefa 为活模块，导出非死 → 宁留 |
| `mangpai/objective/MODULE_ATTRS.md` 中 advanced/chuangong 记述 | 文档记述待 H-fix-8 文档批统一清 |

> **L0 关闭标记（2026-09-18 评估裁定，docs-only）**：本表 SHIPAI 两表（A1）/ gongmen_wuzhi 整模块（A2）/ jiaoyun `if not span`（A4）三项**已关闭（明示不修，勿再立项）**；输出面死字段（A3）不关闭、降为**条件项**（随未来输出面/payload 精简批顺手，否则维持）。理由见文末「L0 遗留关闭标记」节。

### 六件套（vs `snapshots/20260918_hfix3.json`）

- verify 432 + 70 + 64 + 20 全绿（layer1 须 sxtwl 环境=/usr/bin/python3.14；本机 3.11 无 sxtwl 为环境既有事实，非本批引入）
- pytest **934 passed**+1xf（hfix3 口径 934+1xf+19xp → 删 test_chuangong 19 条 xpassed 死测试后 xp 归零，passed 数不变；改名适配 2 处 mock）
- blind vs hfix3：heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）
- 双 seed（剥 _meta）逐字节一致 ✅
- 67/famous 无变化；calib 由 pytest 覆盖
- payload 探针：键数 41 与 selectors/hfix3 口径一致，`gongmen_wuzhi` engine 键保留；无 prompt-only 字段误删（本批零输出字段删除）
- import 冒烟：3.11 + 3.14 双绿（advanced/chuangong 删除后 `import mangpai`/`import foundation` 正常）
- 引擎判定零改动：compute_all 正常路径输出逐字节不变（blind 零抖动坐实）
- 回滚点：tag `hfix4a-pre`；快照=`snapshots/20260918_hfix4a.json`

---

## H-fix-4b（2026-09-18，执行登记 · 重复逻辑下沉/统一批——重构类，等价性第一红线）

### 差异分析记录（每项：差异点 + 判定 + 处置）

| 家族 | 副本 | 差异点 | 判定 | 处置 |
|---|---|---|---|---|
| `_check_pair` | zuogong_detect / dayun / gongshen 逐字同；muku `_is_chong/_is_he/_is_xing` 为其特化；liunian 两处函数内局部复制；zuogong `_chong_pair/_he_pair` 冗余封装（H-fix-1 抽查 P2） | 仅 muku 三分写死表名 | **真等价**（改前真值表 12 支×12 支×5 表全等断言） | 下沉 `objective/_relation_utils.pair_in`；四文件别名、muku 三函数改薄包装、liunian 两局部副本删除、`_chong_pair/_he_pair` 改委托（该 P2 项清零） |
| `_compute_shishen` ×14 + `bazi_calc.ten_god` | objective 3 + subjective 12 | 唯一差异=边界：ten_god 非法干抛 KeyError，其余 `.get` 守卫返 ''；藏干权重/主中余气/阴阳判定**全部一致**（100 干对+空边界真值表改动前互断言全等） | **真等价**（正常路径非法干不可达） | 下沉 `objective/shishen.py`（`god_from_wx`/`shishen_of`）；14 处别名；`ten_god` 保留 KeyError 严格契约改薄壳委托 `god_from_wx`；`shensha._shishen_cat(day_gan,gan)`=`shishen_cat(shishen_of(...))` 包装 |
| `_cat`/`_shishen_cat` ×10 | caiming/guanming/xiangfa_ops（fallback `return ss`）vs hunyin/gongmen/zhiye/liuqin/laoyu/xueli/zaihuo（fallback `return ''`） | 仅未知串 fallback 不同；全部调用点 grep 核实只喂 `_compute_shishen` 输出（10 标准名/''），'日主' 等不可达 | **真等价（可达输入）** | 统一 `shishen.shishen_cat`（'' fallback）；10 处别名。复捕真值表仅 3 处白名单差异='日主'/None 不可达输入 |
| `_wx_cat` ×6 | (day_gan,wx) 四份（gongmen/zhiye/liuqin/zaihuo + xiangfa_ops `_wx_to_shishen_cat`）全同；yongshen/gongliang 为 (day_wx,wx) 同逻辑 | yongshen 版无空守卫（`('','')→'比劫'` vs 守卫 ''），day_wx='' 不可达；判定顺序不同但条件互斥 | **真等价（可达输入）** | `shishen.wx_cat(day_wx,wx)` + `gan_wx_cat(day_gan,wx)` 包装；六处别名（yongshen/gongliang 直别 wx_cat，余别 gan_wx_cat） |
| `_ensure_relations` ×10 / `_ensure_muku` ×2 | caiming/guanming/hunyin/xiangfa_ops/zhiye/liuqin/laoyu/zaihuo/xueli/gongmen_wuzhi；caiming/xiangfa_ops | 逐字全同（H-fix-2b 已同步去 try/except） | **真等价** | 下沉 `subjective/utils.py`（仅依赖 objective，单向分层不破）；10+2 处别名；10 文件 detect_relations 局部导入、caiming/xiangfa_ops analyze_muku 导入随之清理 |
| 相貌判定（H10） | `output/_n2_analyze._has_xiangmao_marker` vs `llm_prompt._xiangmao_anchor` 内联判据 | 逐条件等价（5 主线 hit&desc + 眼象 bing/ding/gui&desc）；anchor 多一层「非 dict 早返 ''」分支 | **真等价**（bool( parts) 同判） | 下沉 `xiangmao.marker_descriptions`（公开 API，防 _t3_anchor_scan 式私有导入脆弱）；`_has_xiangmao_marker` 改薄包装；`_xiangmao_anchor` 复用且**保留非 dict 早返 '' 分支**（塌缩会改 prompt 行为，等价性复核抓出） |
| detect_relations 6 组 O(n²) 循环（H11） | 六合/暗合/冲/刑/穿/破六段 `for i: for j>i` 复制 | 差异=匹配表/日支要求/type/action/desc 模板/severity 键有无/work_types 类；**排放位置散在三位**（六合暗合→三合半合→冲→克→天干克→刑穿破） | **真等价但须保序** | `_ZHI_PAIR_SPECS` 注册表 + 统一扫描闭包 `_scan_zhi_pairs`，按 `[:2]`/`[2:3]`/`[3:]` 三次调用放回原位（初版单次扫描改变 work_actions 顺序被黄金 sha256 锁抓到，已修正）；克/天干克/生/墓用/三合半合不并入（H11 既定：结构差异大） |

### 判定不等价不合并清单（分诊纪律：宁留重复勿改行为）

| 项 | 理由 |
|---|---|
| `bazi_calc.ten_god` KeyError 严格边界 | 与守卫版边界语义不同，保留为薄壳（契约不并入） |
| yongshen `_ensure_work_actions/_ensure_zhengfan/_ensure_laoyu` | 单份非重复，搬动无去重收益且含局部 import 循环风险，不动 |
| `_pillar_cats` 族（zaihuo/zhiye/gongmen 单柱版 vs xueli 全柱版） | 签名/粒度不同（H3 P1「仅深度阈值不同」实还有签名差），留后续批裁定 |
| 克/天干克/生/墓用/三合半合循环 | H11 既定不并入注册表 |
| `_xiangmao_anchor` 非 dict 早返 '' | 与「无 marker 模板行」语义不同，不可塌缩（已保） |

### 重构暴露/顺清

- 本批**未发现存量行为 bug**（全部等价性差异均落在不可达输入，白名单逐条列出）。
- 过程内发现：注册表初版排放顺序改变 work_actions 顺序（黄金 sha256 锁抓到），修正为三次保序调用；300 随机盘新旧 detect_relations 对拍逐字节一致。
- H-fix-1 抽查 P2 `_chong_pair/_he_pair` 冗余封装 → 本批清零。
- H-fix-2b 哨兵适配：test_inject_faults 7a/7b patch 目标由模块本地 `detect_relations`/`analyze_muku`（已随副本删除移除）改 `subjective.utils` 单一源（12 测语义不变）。
- 死物顺清：shensha `_YANG_GANS`（全仓零引用）、bazi_calc `_WX_SHENG/_WX_KE` 本地副本（ten_god 下沉后零引用）、8 文件 `_YANG_GANS` 随副本删除。

### 代码量

生产代码 23 文件 +243/−861（净 −618）；新增 `objective/shishen.py` + `_relation_utils.py` + `subjective/utils.py`（约 150 行含注释）+ 哨兵 `test_hfix4b_unify.py` 11 测。

### 六件套（vs `snapshots/20260918_hfix4a.json`）

- verify 432+70+64+20 全绿；pytest **945 passed**+1xf（934+11 哨兵）
- blind vs hfix4a：heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）
- 双 seed（剥 _meta）逐字节一致 ✅；67/famous 无变化；calib 由 pytest 覆盖
- 十神/_cat/_wx_cat/pair_in 真值表 53 键改动前后复捕：仅 3 处白名单差异（'日主'/None 不可达输入）；detect_relations 300 随机盘对拍 hfix4b-pre 逐字节一致
- import 冒烟：3.11 + 3.14 双绿
- 引擎判定零改动：compute_all 正常路径输出逐字节不变（blind 零抖动 + 随机对拍双坐实）
- 回滚点：tag `hfix4b-pre`；快照=`snapshots/20260918_hfix4b.json`

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict（2a 遗留 P2，守卫批）。
- `_pillar_cats` 族签名统一、H-fix-5 大函数拆分（detect_relations 850→~760 行，主体拆分留 H-fix-5）、selectors 契约（H-fix-6）。

---

## H-fix-4c（2026-09-18，执行登记 · 局部 import / 循环依赖整理批——显式化+方向正确，行为零变更）

### 阶段 0 实测计数（改前口径复核）

- 任务书 grep 口径 `grep -rn "^\s\+import \|^\s\+from " mangpai/ foundation/ scripts/` = **205 处**。
- 其中生产层（mangpai/subjective+objective+engine+foundation）**94 行**，含 `nayin.py:15` docstring 内文本 1 行 → **实 93 处**（复核 H2 的 56 处口径：caiming 8/yongshen 25（4b 已减 1）/zhiye 6/xiangfa_ops 3/gongliang 2/liuqin 4/guanming 7/laoyu 1 = 56 ✓；其余 37 = H3 yunfan 5+gongmen 2、H4 llm 三件套 13、H8 engine 4+__init__ 4、H12 liunian 4、objective 5、juefa 1）。
- 测试/诊断/脚本（D 类，保留不动）= 205−94 = **111 处**。

### 分类处置统计（生产 93 处）

| 类 | 数量 | 处置 |
|----|------|------|
| **A 纯冗余**（顶层已导入同符号/同模块，重复） | 13 | 删除：guanming:260/820 classify_strength（顶层 :51 已有）、gongliang:1085（并入顶层 yongshen 组）、llm_backend:173 datetime、yunfan:392 `_YR`（与 :215 重复）、caiming:1469 detect_zihe（与 :461 重复）、yongshen get_canggan×3/detect_zihe×3/LIU_CHONG 重复 |
| **B 循环依赖规避** | 1 边保留 + 星型回边上提 | 见下「循环破除」 |
| **C 重型/软依赖延迟** | 5 | **保留**（均有注释）：narrative anthropic×2、xiangfa_ops foundation（try/ImportError 降级）、jiaoyun sxtwl×2 |
| **D 工具/CLI** | 3（生产内）+111（测试脚本） | 保留：llm_channel demo()/main 的 yaml/engine/sys（补注释说明）；测试/脚本 111 处不动 |
| **安全上提**（无环局部→顶层） | 71 | 全部上提合并：subjective→objective 一律安全（objective 不反导）；subjective→subjective 逐边核查目标模块无反向顶层依赖后上提；别名 `_SH2/_SH/_SAN_HE/_LC/_LC4/_XP4/_LH4/_gcm/_gcm4/_YR/_SANHE/_cs/_cs2/_cs4/_cls_st` 统一改回正名 |
| **改后剩余** | **8 处**（93→8） | B 1 + C 5 + D 3（另 nayin docstring 文本 1 行非代码） |

### 阶段 1 循环破除记录

- **`gongliang ↔ caiming` 双向依赖**：改前=gongliang 顶层 `from caiming import classify_caifu_view` + caiming:1782 局部 `from gongliang import analyze_gongliang`。**方向矫正**：caiming（领域层）→ gongliang（功量层）为正向，caiming 侧上提至顶层；gongliang 对 caiming 的反向消费（7c 官统财/财统官，gongliang.py:755）改为函数内局部导入+显式注释（全模块唯一使用点）。结果：**subjective 顶层依赖图无环**，回边 1 处显式备案。
- **`yongshen` 星型中心回边**（局部导入 zuogong_confirm×2/laoyu×2/juefa/zhengfan）：逐一核查目标模块顶层零 subjective 依赖（laoyu 仅→zhengfan，zhengfan/juefa/zuogong_confirm 零）→ **非真循环，全部上提**，星型中心出边显式化。
- **`gongmen_wuzhi.py` 局部回导 gongliang**（H3，现 :443-444）：核查 gongliang 顶层不依赖 gongmen_wuzhi → 无环，**上提**（+zuogong_confirm 同边上提）。
- **分诊纪律执行**：循环「能不破不破」——真循环仅 gongliang⇄caiming 1 条，采方向矫正+回边显式化（非大改）；其余局部导入均非循环规避，属历史堆积，安全上提。

### 阶段 2 sys.path.insert 评估（H10/H6 遗留）

- output/ 批跑脚本 `sys.path.insert`：**保留+备案**。output/ 非包（无 `__init__.py`），相对导入不可用；改包安装需新建 pyproject + `pip install -e`，工程成本高且改变批跑工具调用习惯——批跑工具非生产代码，维持现状，归档/安装化留 H-fix-8 议。
- tests 内 18 文件 `sys.path.insert`（H6 P1）：本批不动（删除即动测试文件，留 H-fix-7/8 随评测框架统一批处理）。

### subjective 顶层依赖图（`scripts/check_layering.py --graph` 实测，供 H-fix-5 拆分参考）

```
caiming        -> gongliang, utils, yongshen, zeishen_bushen, zuogong_confirm
gongliang      -> yongshen, zeishen_bushen, zuogong_confirm        （~~> caiming 函数内回边，显式备案）
gongmen_wuzhi  -> gongliang, utils, yongshen, zuogong_confirm
guanming       -> gongliang, utils, xiangfa_ops, yongshen, zuogong_confirm
hunyin         -> utils, yongshen, zhengfan
laoyu          -> utils, zhengfan, zuogong_confirm
liunian        -> dayun, yongshen
liuqin         -> utils, xiangfa_ops, yongshen
llm_channel    -> subjective(包), llm_backend, llm_prompt, narrative, prompts
llm_prompt     -> xiangmao
narrative      -> prompts, zaihuo
xiangfa_ops    -> utils, zeishen_bushen, zuogong_confirm
xiangmao       -> liuqin
xueli          -> utils, yongshen
yongshen       -> juefa, laoyu, zhengfan, zuogong_confirm          （星型中心出边，全顶层显式）
yunfan         -> yongshen, zhengfan, zuogong_confirm
zaihuo         -> utils, yongshen
zhiye          -> caiming, utils, xiangfa_ops, yongshen
zinv           -> liuqin
__init__       -> dayun, schools, zaihuo
```
- **双向边：0**（顶层图 DAG；唯一函数内回边 = gongliang~~>caiming）。
- 入度中心：yongshen（9 模块）、utils（10）、zuogong_confirm（7）、zhengfan（4）、gongliang（4）——H-fix-5 拆分时 gongliang/caiming 在同强连通分量候选区，拆分顺序建议 utils/zuogong_confirm/zeishen_bushen → yongshen/zhengfan → gongliang → caiming/guanming/zhiye。

### 分层铁律验证（新入库 `scripts/check_layering.py`）

- AST 全量扫描 foundation+mangpai/objective+subjective+engine（66 文件）：断言 foundation 不导入 objective/subjective/engine、objective 不导入 subjective/engine、subjective 不导入 engine + subjective 顶层图无环，反向依赖即 exit 1。
- 白名单 1 条例外显式备案：llm_channel demo()/main 函数内局部导入 engine（CLI 调试入口，延迟加载）。
- 实测：**通过，无反向依赖，顶层图无环**。

### 六件套（vs `snapshots/20260918_hfix4b.json`）

- verify 432+70+64+20 全绿；pytest **945 passed**+1xf（修 5 处测试 mock 漂移：llm_channel.call_deepseek×4 + gongliang.analyze_zeishen_bushen×1 patch 目标随导入上提改消费侧，同 4b 先例；`test_l2_death_refusal_passes_render` 原误过——patch 未命中走真实降级路径碰巧断言成立，一并修正）；blind vs hfix4b heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）；双 seed（剥 _meta）逐字节一致 ✅；67/famous 无变化 ✅；calib 由 pytest 覆盖
- import 冒烟：3.11 + 3.14 双绿（`import mangpai` + 全部改动模块）
- 引擎判定零改动：本批仅移动 import 位置+别名正名，无任何语句/表达式变更
- 回滚点：tag `hfix4c-pre`；快照=`snapshots/20260918_hfix4c.json`

### 残留（转后续批）

- `engine.py:407` liunian_data truthy 非 dict（2a 遗留 P2，守卫批）。
- output/ 脚本 sys.path.insert 安装化、tests 18 文件 sys.path.insert（H-fix-7/8）。
- H-fix-5 大函数拆分（依赖图见上）、selectors 契约（H-fix-6）。
- H-fix-5 大函数拆分（依赖图见上）、selectors 契约（H-fix-6）。

---

## H-fix-6（2026-09-18，执行登记 · selectors/engine-keys 契约测试批——纯新增测试，引擎/payload 零改动）

> 核销 H8 P1（`schools.py:24-44` selectors 无同步保护）+ H11 P1-④（selectors/engine-key 自动契约测试）+ H4 P1（zinv selector 无消费方）的显式化处置。定位=H-fix-5 compute_all 拆分的前置哨兵。

### 阶段 0 三方实测（注入 dayun 全量供给样本盘 戊辰己未庚午丁亥）

| 方 | 键数 | 口径 |
|----|------|------|
| engine `compute_all` | **48** | 注入 dayun 后含条件键 `dayun_analysis`（engine.py:492 仅 dy_list 非空才计算）；不注入=47 |
| `schools.py` selectors | **41** | 静态元组 |
| `build_payload` | **41** | 与 selectors 全等（engine 产出 dayun_analysis 走 `_trim_dayun`；缺供时 `_synthesize_dayun` 合成补供，同键） |

### 三方对照差异处置（全部显式化入 `mangpai/tests/test_key_contract.py`）

- **engine 有而 selectors 无（7）→ `INTERNAL_ENGINE_KEYS` 白名单（集合相等断言，双向防腐）**：`input`（输入回显）/ `summary`（规则摘要串，verify_dayun 消费）/ `relations`（模块间总线）/ `direction`（F1 标注仅透传）/ `gongshen`（预消化，批10 A1 防护）/ `gongmen_wuzhi`（修批A③ 摘除，engine 键保留存档）/ `jiaoyun_analysis`（批10 A1 刻意排除，F14 红线）。
- **selectors 有而 engine 无（0）**：`dayun_analysis` 为条件产出键，注入 dayun 即产出；条件性在测试样本盘注释固化。
- **payload 无静态消费方（3）**：`chang_sheng`/`narrative` → `LLM_FEATURE_ONLY_KEYS` 备案（特征 JSON 全量嵌入 user prompt 直喂 LLM，代码/prompt 无定点读者）；`zinv` → `RESERVED_KEYS` 预留备案（H4 结案：engine 写入+payload 透传，prompt/formatter/narrative 零读者，D6a 设计纯数据——**显式标注「预留（供未来扩展）」**，H-fix-5 拆分时勿当死键误删）。

### 阶段 1 契约测试（`mangpai/tests/test_key_contract.py`，6 测）

1. `test_engine_keys_covered_by_selectors`：engine 键 = selectors ∪ 内部白名单（集合相等；漏登记/白名单腐化/归类矛盾三向皆红）。
2. `test_selectors_exist_in_engine`：selectors ⊆ engine 全量产出 + 无重复登记（防死键）。
3. `test_payload_mirrors_selectors`：payload 键集 = selectors 键集，键数锁 41。
4. `test_payload_keys_have_consumer`：payload 每键至少在 narrative/formatter/llm_prompt/llm_channel/prompts 模板一处静态引用，否则须入两个备案集之一。
5. `test_reserved_keys_still_unconsumed`：预留键防腐——zinv 一旦有静态读者须移出预留。
6. `test_feature_only_keys_in_payload`：特征直喂备案防腐。

**红验证（非恒真实证）**：临时删 selectors `shipaige` → 断言 1+3 红（2 failed）；临时加幽灵键 `ghost_key` → 断言 2+3 红（2 failed）；恢复后 6/6 绿。

### 阶段 2 登记机制评估（结论：不引入自动派生）

断言 1 的集合相等已构成「新增键强制显式归类」的自动契约；selectors 机械派生会抹掉 gongmen_wuzhi 式「刻意摘除」语义。测试作哨兵、登记仍手工但受闸，机制不再改。

### 六件套（vs `snapshots/20260918_hfix4c.json`）

- verify 432+70+64+20 全绿；pytest **951 passed**+1xf（945+6 新测）；blind vs hfix4c heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）；双 seed（剥 _meta）逐字节一致 ✅；67/famous 无变化 ✅；calib 由 pytest 覆盖；`scripts/check_layering.py` 通过（66 文件无反向依赖无环）
- 引擎判定与 payload 结构零改动：本批仅新增 1 测试文件 + 文档，生产代码零触；payload 键数 41 不变
- 快照=`snapshots/20260918_hfix6.json`

### 预留键清单（供 H-fix-5 参照）

| 键 | 归类 | 处置 |
|----|------|------|
| `zinv` | 预留 | 勿删勿拆并；若未来接 LLM 叙述维，先移出 RESERVED_KEYS 再走七维扩展流程 |
| `chang_sheng` / `narrative` | 特征直喂 | 保留透传；若加定点读者（prompt 锚/formatter 段），移出 LLM_FEATURE_ONLY_KEYS |
| `gongmen_wuzhi` | 内部白名单 | 修批A③ 锁定决策：engine 键保留存档，不回 selectors |


---

## H-fix-5（2026-09-18，执行登记 · 大函数拆分批——H-fix 序列最后一批功能批，逐字等价第一红线）

> 核销 H11 P1-①/②/③（三大函数拆分）。依赖前置：H-fix-4b（注册表化）+ H-fix-4c（依赖图）+ H-fix-6（契约哨兵）。回滚点 tag `hfix5-pre`。

### 拆分后结构说明

**① `objective/zuogong_detect.py` — `detect_relations`（772 行 → ~150 行编排器，13 子函数）**

- `_scan_gan_relations`（日干五合/争合/合化+非日干合制）/ `_scan_shengyong`（天干食伤/地支食伤/内食神格）/ `_scan_shayin_huayong`（杀印相生，H11 遗漏段）/ `_scan_zhi_pairs`（4b 注册表扫描闭包提升模块级，仍按 `[:2]`/`[2:3]`/`[3:]` 三次调用保序）/ `_scan_sanhe_banhe` / `_scan_zhi_ke` / `_scan_gan_ke` / `_scan_shengfu` / `_scan_tomb` / `_calibrate_huayong`（化用前置校准，原地修订）/ `_apply_he_center_skip`（合中心 skip，原地修订）/ `_scan_fuyin_fanyin` / `_collect_raw_facts`（长生/弱支/空亡支/入墓干）。
- 与 H11 偏差：天干克未并入 `_scan_gan_relations`（原排放位在六冲后，并入变序违序等价）；墓用/伏吟反吟按现状语句序分两段；克/生扶/三合半合不并入注册表（H11 既定）。

**② `subjective/gongliang.py` — `analyze_gongliang`（949 行 → 154 行编排器，5 子函数按 H11 五阶段）**

- `_prepare_inputs`（Pillars 签名/自调 analyze_zuogong/zb 上游信号/day_wx；Pillars 分支解析的 gans/zhis 经返回 dict 回传）→ `_compute_position_sets`（non_aux/involved/zhi_targets/cats×4/strong/destructive）→ `_apply_gong_point_rules`（14 条计分规则集中，caiming 消费保持函数内局部导入=4c 备案回边）→ `_apply_caps_and_direction`（制净/zb 净制增强/降档/层次映射+封顶/pocai R1/yongshen_xiong/fuhe 标注）→ `_build_gongliang_result`（score/boundary/装配/双轨对账/zb 信号录入）。
- 偏差：各阶段返回 dict 而非 tuple（显式传递需要）；早退守卫留编排器；caps/build 函数体首各加 `reasons = list(reasons)` 别名防御（可观察输出经 1627 项 sha256 证明一致）。

**③ `engine.py` — `compute_all`（489 行 → 38 行编排器，6 段）**

- `_compute_objective_base(result, p)`（bazi/input..tiyong）→ `_compute_zuogong_and_derivatives → {'zg','zb_res'}` → `_compute_objective_extended(result, p, zg)`（muku..gongshen+kong_wang/di_zhi_relations）→ `_compute_yunshi → {'dy_list','liunian_data'}`（dayun/liunian/jiaoyun/shipaige，`_auto_liunian_injected` 条件赋值原样）→ `_compute_subjective_domain(result, p, zg, zb_res, yunshi_ctx)`（relations..narrative）→ `_build_summary` 挪用（H11 ⑤）。
- 偏差：H11 ①原定含 muku..gongshen，但 zuogong 系实位于 tiyong 与 muku 之间（全链上游），故①拆为 base/extended 两段夹住②保调用/回写顺序逐字等价；`_current_dayun` 被调两次原样保留。

### 哨兵（先红后绿）

- `test_hfix5_detect_relations.py` 36 测（先红 ImportError 子函数不存在）；`test_hfix5_gongliang.py` 7 函数 60 例（9 书例盘×5 阶段中间态钉值+13 盘端到端+2 Pillars 签名）；`test_hfix5_compute_all.py` 12 测（先红 11 failed；含 48 键全序锁/条件键分支/手工逐阶段==compute_all）。合计 +108 collected。

### 等价性验证

- detect_relations：809 例（heldout 215+trainset 294+300 随机盘）canonical sha256 pre=post 逐字节一致，hashseed 0/7/42 三重稳定。
- analyze_gongliang：1627 项（509 例×自调/显式双路径+300 随机盘+9 合成边界含正确构造 Pillars）sha256 一致；过程曾引入 Pillars 分支 gans/zhis 未回传真 bug（old L4 vs new L1），等价捕获+新增哨兵抓到并已修复。
- compute_all：518 样本（509 例+9 注入分支盘：dayun/liunian list/dict/空、无 input、str-liunian 异常路径）sha256+键序+sidecar 逐字节一致，三 seed 各自对拍零失配；契约测试 test_key_contract 6/6（48=41+7 归类不变、payload 锁 41）。

### 六件套（vs `snapshots/20260918_hfix6.json`）

- verify 432+70+64+20 全绿；pytest **1059 passed**+1xf（951+108）；blind vs hfix6 heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）；双 seed（剥 _meta）逐字节一致 ✅；67/famous 无变化 ✅；calib 由 pytest 覆盖；`scripts/check_layering.py` 通过；import 冒烟 3.11+3.14 双绿
- 引擎判定零改动：compute_all 正常路径输出逐字节不变（三路对拍+blind 零抖动坐实）
- 快照=`snapshots/20260918_hfix5.json`；执行机口径注意：本机 PATH `python3`=3.11 venv 无 pytest，测试/盲测用 `/usr/bin/python3`（3.14）跑，等价捕获 pre/post 同一解释器

### 发现的待议问题（只记录未修，分诊纪律：拆分与修复不混）

1. **xiangfa_ops 全量 result 的 set 迭代序随 PYTHONHASHSEED 旋转**（jiexiang/all_findings/zhixiang 条目序；同 seed 逐字节一致；blind 评分字段不受影响零抖动）——拆分前已存在的存量不确定性，M1 既有 11 处排序化未覆盖此族，归属后续卫生批。
2. `engine.py:578` liunian_data truthy 非 dict/list → `.get` AttributeError 穿透（2a 遗留 P2，pre/post 异常 repr 逐字一致）。
3. `engine.__init__` 未初始化 `_auto_liunian_injected`（H8 P2），getattr 兜底行为原样保留。
4. `_scan_shengyong` 内食神格嵌套冗余 `if day_wx:`（外层已判，内层恒真）；`_prepare_inputs` 内 `(not day_gan or not gans or not zhis) and wa_list: pass` 死代码块——均按逐字等价原样保留。
5. gongliang 4 处自调吞异常（H11 已录）、13 书例 `hua_chengju` +1 高层加分无命中（与 F6 记录一致）——维持备案。
6. detect_relations 返回 dict 内含 set（`day_weak_zhis` 等），消费方序列化须先排序（引擎自身输出确定性已由 blind 零抖动坐实）。

> **L0 处置（2026-09-18 评估裁定，docs-only）**：#5（B5）/#6（B6）**已关闭（明示不修，勿再立项）**——B5 吞异常 H-fix-2b 已实质处置（安全降级 18 显式化）、13 书例=F6 既有备案；B6 内部总线键不进 payload/selectors 无泄漏面（实测三键消费方全安全）。#1-#4（B1/B2/B3/B4）转入 **L1 遗留清理批**（阶段甲零输出项 B2/B3/B4+C2/C3 → 阶段乙输出项 B1/C1，一次换基线；时机=下个引擎批前置位或 LLM 批跑需求独立先做）。**行号更正**：#4 `_prepare_inputs` 死块实在 **`subjective/gongliang.py:431-433`**（函数 def :369），非 engine.py；#2 行号已漂至 `engine.py:577-578`。详见文末「L0 遗留关闭标记」节。

### 残留（转后置批）

- H-fix-7 评测框架统一 / H-fix-8 文档基线同步（v2 计划 🟢 后置）。
- 上述待议问题 1-3 归后续卫生批裁定。

---

## H-fix-7（2026-09-18，执行登记 · 评测框架统一批——防口径漂移，🟢 可选批）

> 核销 H10 P1 四组重复（runner/校准/抽样/检查）。回滚点 tag `hfix7-pre`。零 API（对拍全用历史数据）。执行机：`/usr/bin/python3`（3.14，venv python3 无 pytest/sxtwl）。

### 公共模块（新建 `output/_eval_common.py`，五节）

1. **runner** `run_llm_eval`：评审/judge 双实例批跑（ThreadPoolExecutor 8 并发 + jsonl 断点续跑 + 成本累加 + 异常计数汇总）。2c 纪律继承：LLMBackendError/JSONDecodeError 记 `api_error`/`parse_error` 不吞；其它异常不捕获；llm_backend 惰性 import（检查脚本不依赖 LLM 后端）。
2. **材料组装** `build_engine_materials` / `reading_text`：脚本间差异以显式形保——`truncate_hunyin_signals`（_t3 旧口径）/`include_newdims`（_n2 七维）/`dims`，禁止静默统一。
3. **校准** `load_jsonl`/`review_stats`/`agreement_stats`/`judge_stats`/`judge_acceptance`：一致率/翻转召回/达标判定（≥85% 且召回 100%）单份实现；divergences 详略、judge flips 带不带 ref、new_dims 红线——三处历史差异全走形参；cal schema/打印留各脚本。
4. **抽样** `stratified_fill`：tier_static × is_guanming 分层轮转补足，seed 调用方持有。
5. **检查** `engine_fe`/`QIANYI_FORBID`/`XM_FORBID`/`xm_forbidden_scan`/`qianyi_info`/`xiangmao_info`/`qianyi_honest_nosignal`：引擎重算入口 + 迁移/相貌禁词扫描 + 无信号如实判定（原 _w4/_w5/_n2_analyze/_t3_dump 跨脚本重复）。

### 改造脚本（11 个全改薄包装，命令行接口/输出 schema 不变）

`_n2_eval` `_t3_eval`（runner+材料）｜`_n2_calibrate` `_t3_calibrate` `_v3_calibrate`（校准）｜`_n2_sample` `_v3_sample`（抽样）｜`_w4_sample` `_w5_crosscheck`（检查）｜`_n2_analyze` `_t3_dump`（engine_fe/禁词表/无信号判定顺带下沉）。`_v3_judge_sample` 不动（`_t3_eval.run` 签名保）；`_t3_anchor_scan` 无共享逻辑不动。
**顺带修 H10 P0**：`_w5_crosscheck` 导入已删的 `_xm_sanitize` 运行即 ImportError——按 H10 处方改锚定行直传（G3 起 desc 不含「漂亮」，sanitize 本为恒等）。

### 口径对拍（新老实现同跑历史数据，逐项比对——本批核心验证）

| 对拍项 | 数据 | 结果 |
|---|---|---|
| prompt 组装 | t3_s1（281 例）+ t3_s1_n2（294 例）×（_materials/_reading_text/_review_user/_judge_user）+ 2×2 system prompt | **全量逐字节一致，0 失配** |
| 校准 | t3_s1 / t3_s1_d4 / t3_s1_v3 / t3_s1_n2 四批 calibration.json + stdout | **4/4 逐字节一致**（一致率/翻转数/召回/达标判定全同） |
| 抽样 | t3_s1_n2 / t3_s1_v3 sample30.json + stdout | **2/2 逐字节一致**（seed 复现，forced/fill 全同） |
| w4 样张 | llm_batch_20260821_n2_r4 全量 294 例 stdout | **逐字节一致** |
| w5 对照 | 旧实现已坏（H10 P0），仅证新实现可跑 | 10 例跑通，❌ 检查标记 3 处=存量发现非回归 |
| n2_analyze | n2_r1 批 294 例：stdout（路径回显行归一化后）+ l2_ids/newdim_ids.json | **逐字节一致**（锚定引用率 264/264 等命中数全同） |
| t3_dump | v5 批 293 例：dump.json + payload_fidelity.json + stdout | 随机 seed 下 287 例 features 序差=**存量** xiangfa_ops set 迭代序随 PYTHONHASHSEED 旋转（H-fix-5 待议 1，非本批引入）；**PYTHONHASHSEED=0 复跑三者逐字节一致** |

分诊纪律执行：对拍不一致项 0；唯一差异源=引擎存量不确定性，归既有备案，不改历史数字。

### 六件套（全绿）

verify 432+70+64+20 / pytest **1059 passed**+1xf（无新增测试——本批哨兵=对拍 harness）/ blind vs `snapshots/20260918_hfix5.json` heldout+trainset **零翻转零抖动**（官 48✅/财 47✅/职 24✅ 保）/ 双 seed（剥 _meta）逐字节一致 / 67/famous 无变化 / calib 由 pytest 覆盖 / `scripts/check_layering.py` 通过。引擎/主观层零改动（只动 output/ 工具脚本）。快照=`snapshots/20260918_hfix7.json`。

### 残留

- xiangfa_ops set 迭代序不确定性（本批对拍再次实证）——归 H-fix-5 待议 1，后续卫生批裁定。
- H-fix-8 文档/基线同步（v2 计划 🟢 后置最后一批）。

---

## H-fix-8（2026-09-18，执行登记 · 文档/基线同步批——H-fix 序列收尾，纯文档/基建，引擎/主观层零改动）

> 核销 H9 P1 三条（README 23 例过期 / MANUAL 4 例未入 merged+candidates / 14 份无引用快照+缺 LATEST 指针）+ H10 sys.path.insert 备案结案 + H-fix 全序列文档同步。唯一代码改动=`blind_eval.py` 新增 `_resolve_snapshot_path`（评估链指针解析，正常路径输出不变）。

### 任务 A · README/文档数字同步（实测为准）

| 项 | 旧值 | 实测新值 | 处置 |
|---|---|---|---|
| 根 README 验证用例数 | 860 | **1059 passed+1 xfailed**（1060 collected） | 已改 |
| 根 README 模块数 | 58 | **59**（H-fix-4a 删 2 → 56，H-fix-4b 增 3 → 59） | 已改 |
| 各层模块数（架构表） | F2/O26/S30 | **Foundation 2 / Objective 27 / Subjective 30** | 已改（职责行删「串宫压运」——chuangong 已删） |
| 新模块入架构说明 | — | `objective/shishen.py`·`_relation_utils.py`、`subjective/utils.py` | 架构表下补一句说明（公共 helper 下沉产物，分层不破） |
| heldout README trainset 例数 | 23 | **294**（污染路由补 famous_cases；管线段 375/293 标注为初次构建历史计数） | 已改 |
| MANUAL 4 例（H9 P1） | 未入 merged/candidates | 裁定=**显式旁路**（build_yaml 直接路由，非数据漂移） | annotations_heldout.py 注释+heldout README 双备案结案 |

### 任务 B · 快照基线机制（H9 P1）

- **`snapshots/LATEST` 指针**：纯文本单行 → `20260918_hfix7.json`；`blind_eval.py --baseline latest` / `--diff latest X` 可解（`_resolve_snapshot_path`）；**刻意不随 `--out` 自动更新**——推进基线=人工改写指针，防误推。
- **14 份无引用快照**：git mv → `snapshots/archive/`（保留历史不删，快照链是审计证据）：20260801_f/f_rescore/p2、20260802_c/l、20260807_m、20260808_n/o/q_rescore、20260814_c、20260817_f8/f9/f14/f15。
- **快照链文档**：新建 `snapshots/README.md`——当前基线指针用法 + H-fix 全序列链表（prehfix+hfix1~7，git_sha/对照基线/结果全录，hfix6→hfix5 顺序注记）+ 主链（2026-07~08）+ 归档清单 + 卫生规则。

### 任务 C · 收尾同步

- **sys.path.insert 备案（H10 P2 结案）**：output/ 批跑脚本 `sys.path.insert` **保留+备案**——output/ 非包（无 `__init__.py`）相对导入不可用；安装化需新建 pyproject+`pip install -e`，工程成本高且改变批跑工具调用习惯；批跑工具非生产代码。维持现状，不再立项。tests 内 18 文件 sys.path.insert 同理维持（动测试文件无收益）。
- **KB 同步**：§0 验证口径（1059+1xf+两件套脚本）/§1.1（subjective 32→30、snapshots 指针、test 1059）/§8（pytest 计数、check_layering/check_typing_imports 行、`--baseline latest`、六件套代码块）/§9（H-fix-8 终态+序列总账：裸 except 残留 3 处合规、模块 58→59、明示暂不修项）。
- **CHANGELOG**：补 H-fix-1/2a/2b/2c/3/4c/5 七条缺漏 + H-fix-8 本条（4a/4b/6/7 前批已写，核对无误）。
- **收工记录**：`docs/remaining-tasks-20260917.md` 新建（H-fix 序列终态 + 剩余待议项清单）。

### 六件套（全绿）

verify 432+70+64+20 / pytest **1059 passed+1xf** / blind vs `snapshots/20260918_hfix7.json`（=`--baseline latest`）heldout+trainset **零翻转零抖动** / 双 seed（剥 _meta）逐字节一致 / 67/famous 无变化 / `check_layering.py`+`check_typing_imports.py` 通过。引擎/主观层零改动。

### H-fix 序列收官声明

H-fix 1~8 全批落地，每批六件套全绿+blind 零翻转零抖动+批前 tag 回滚点。剩余待议项（backlog「未删待议」/「待议问题」+v2 计划⏸️节）汇总入 `docs/remaining-tasks-20260917.md`，勿再立重复项。

---

## L0 遗留关闭标记（2026-09-18，docs-only 批——零代码改动）

> 依据：评估 `~/.claude/projects/-root-metaphysics/memory/kimi-leftover-assessment-20260918.md` + 方案 `kimi-leftover-fix-plan-20260918.md`。以下 6 项裁定**明示关闭（附理由，勿再立项）**；同步落档 `docs/remaining-tasks-20260917.md` §二。

| # | 项（backlog 出处） | 关闭理由 |
|---|----|---------|
| A1 | SHIPAI_DOMAINS/METHODOLOGY（H-fix-4a 未删待议） | 修批C「留作碎片原文档案」决议在先，待删动议属重复立项（非待删项） |
| A2 | gongmen_wuzhi 整模块（H-fix-4a 未删待议） | 修批A③/F18 锁定 + `test_a_llm_redline` 哨兵 + `test_key_contract` 契约白名单三层防护，删除违输出红线零收益（非待删项） |
| A4 | jiaoyun `if not span`（H-fix-4a 未删待议；H1 P1 :189） | 公开 API `_normalize_dayun_entries` 边缘语义承载非死码，改则变行为无收益 |
| B5 | gongliang 4 处自调吞异常 / 13 书例 hua_chengju 无命中（H-fix-5 待议 #5） | H-fix-2b 已实质处置（安全降级 18 显式化，改传导零收益）；13 书例=F6 既有备案非缺陷 |
| B6 | detect_relations 返回含 set（H-fix-5 待议 #6） | 内部总线键不进 payload/selectors，无序列化泄漏面（2026-09-18 实测三键消费方全安全）；消费方排序纪律已够 |
| C4 | magic numbers ~45 处（H2/H3 P2；v2 计划 ⏸️ 节） | v2 ⏸️ 裁定维持；~45 处判定代码换纯可读性，风险收益倒挂 |

### 转出待办（非关闭）

- **L1 遗留清理批**（单批两阶段，半天~1 天，一次换基线；明细与修法见方案 §二）：
  - 阶段甲·零输出项=**B2**（`engine.py:577-578` liunian_data 入口守卫，旧记 :407 已漂移）/ **B3**（`_auto_liunian_injected` `__init__` 初始化+`_compute_yunshi` 开头重置）/ **B4**（删 `zuogong_detect.py:490` 内层冗余 `if day_wx:`——外层 :348 承重守卫保留 + 删 `_prepare_inputs` 死块 **`subjective/gongliang.py:431-433`**——**行号更正：旧记「engine.py」系误记**）/ **C2**（formatter.DISCLAIMER 单源化，H5 P1）/ **C3**（新建 `test_snapshot_hygiene.py`，H6/H9 P2）；
  - 阶段乙·输出变更项=**B1**（xiangfa_ops 排序化 4 处：`:336`/`:677`/`:811-813`/`:1090`+`:1096`，H-fix-5 待议 #1）/ **C1**（zaihuo label 修正 `zaihuo.py:319-322`——已从 :388 漂移；计数不动只改展示 label）。
- **时机条件**：L1 等下个引擎判定批**前置位**（先换基线，引擎批从新基线起跑；拒绝同批合并）；或近期有 LLM 批跑/双 seed 可复现需求（B1 唯一活影响）/ 引擎批排期 >2~4 周时独立先做。
- **A3 输出面死字段**（virtual_solid counts / soil wet·dry / 华盖 year_ref）：不关闭，降为条件项——随未来输出面/payload 精简批顺手，否则维持。
- **D 真实凭证冒烟**：上线 checklist #3 执行项（事件触发非代码项），前置=真实飞书凭证+DeepSeek key，随首次上线冒烟窗口与 #4 群聊 @bot 同批执行。

---

## L1 遗留清理批（2026-09-18，执行登记 · 单批两阶段一次换基线——引擎精度批紧前批）

> 依据：方案 `~/.claude/projects/-root-metaphysics/memory/kimi-leftover-fix-plan-20260918.md`。批前回滚点 tag `l1-pre`。
> 阶段甲（B2/B3/B4/C2/C3）零输出逐项验证；阶段乙（B1/C1）输出变更一次换基线。

### 阶段甲 · 零输出项（落地后 blind vs hfix7 零翻转零抖动 ✓）

| 项 | 位置 | 落地 |
|---|---|---|
| B2 liunian 入口守卫 | `engine.py` `_compute_yunshi` | truthy 非 list/dict → 显式 `EngineInputError`（旧版 `.get` 裸穿 AttributeError）；注入测试 3 测入 `test_inject_faults.py`（str/int 红→绿 + list/dict 正常路径） |
| B3 `_auto_liunian_injected` | `engine.py` `__init__` + `_compute_yunshi` | `__init__` 置 False + 方法开头重置双保险；读点 getattr 兜底改直读；复调哨兵入 `test_hfix5_compute_all.py`（同实例两次 compute_all 不残留，红→绿） |
| B4 冗余/死块删除 | `objective/zuogong_detect.py` 内层 `if day_wx:`（外层 :348 承重守卫保留）+ `subjective/gongliang.py` `_prepare_inputs` `pass` 死块 | 已删，等价性由阶段甲 blind 零抖动坐实 |
| C2 DISCLAIMER 单源化 | `feishu/formatter.py:17` | 文本逐字一致确认后改 `DISCLAIMER = '\n' + llm_channel._DISCLAIMER_LINE`（feishu→subjective 边已存在，check_layering 通过） |
| C3 快照卫生测试 | 新建 `mangpai/tests/test_snapshot_hygiene.py` 2 测 | LATEST 可解/meta 完整/基线 rubric==当前/命名规范 + tmp 反向构造证红；**首战即立功**：抓出 `20260819_e3`/`20260820_gap2` 两快照 `_meta.note` 为空，已补录（meta 剥离不参与评分，零行为影响） |

### 阶段乙 · 输出变更项（一次换基线 `snapshots/20260918_l1.json` + LATEST 推进 ✓）

| 项 | 位置 | 落地 |
|---|---|---|
| B1 xiangfa_ops 排序化 | `xiangfa_ops.py:336`（共象域聚合）/`:677`（zhixiang controlled_cats）/`:813/:828`（jiexiang a_only/b_only）/`:1090`+`:1093`（juxiang 包局 set 迭代 + **`.pop()` 任意元素→sorted 取首**） | 消费点 sorted，同 M1 既有 11 处先例 |
| B1 同族补漏（方案外同形态，实测抓出） | `gongmen_wuzhi.py:266` / `zhiye.py:552` `''.join(frozenset)` | frozenset join 排序化——B1 修后三 seed 对拍仍现 102 例序差，逐例定位为此两处（B6 关闭裁定仅覆盖 membership 消费方，join 消费系漏网） |
| C1 zaihuo 官杀 label | `zaihuo.py:319-322` | 凡官杀皆误标「七杀」→ 按实际十神 sorted 收集（正官/七杀可并存）；**计数语义不动**（官杀在场即 +1，书锚 gaoji:~14843-14848）；哨兵 `test_f13_shensha.py::test_chehuo_guansha_label_l1` 红→绿 |

### 验证（全绿）

- **双 seed 复现（B1 核心价值）**：trainset+heldout 509 例 **payload 特征 JSON** `PYTHONHASHSEED=0/7/42` 三轮 sha256 全一致（修前 H-fix-7 实证 287 例 features 序差；B1 四点修后仍 102 例，补 frozenset join 两处后清零）；blind 快照双 seed 剥 _meta 逐字节一致。全量输出残留序差 68 例全部限 `relations/day_weak_zhis` 内部总线键（B6 关闭裁定域，不进 payload/selectors，维持不修）。
- **blind vs hfix7（换基线前）**：heldout+trainset **评分字段零翻转零抖动**（快照不录 zaihuo desc/xiangfa_ops 文本域，评分面不动）。
- **抖动逐条归因**（509 例全量输出 pre/post 对拍）：白名单外路径 **0**——xiangfa_ops 34290 路径（B1 序/域文本）/ zaihuo 129 例×2（`chehuo.xiong_shen`+`desc`，「七杀→正官」或「+正官」，score/risk 零触碰）/ zhiye 30 例（lawyer evidence「酉卯冲→卯酉冲」）/ gongmen_wuzhi 30 例×2（同族）/ narrative 167 例（digest 下游传导，全部有上游解释）。
- **六件套**：verify 432+70+64+20 / pytest **1066 passed+1xf**（1059+新增 7：B2×3、B3×1、C1×1、C3×2）/ 67/famous 无变化 / calib 常驻 2 条零新增 / check_layering+check_typing_imports 通过 / 3.11+3.14 import 冒烟 ok。
- **非目标维零翻转**：官 48✅/财 47✅/职 24✅ 保；引擎判定（score/层级）零改动。

## P1 官命检测簇批（2026-09-18，执行登记 · 引擎精度批 P 系列首批——判定改动批，非卫生批）

> 依据：方案 `~/.claude/projects/-root-metaphysics/memory/kimi-engine-precision-plan-20260918.md` P1 节；预注册 `docs/kimi-p1-guanming-prereg-20260918.md`（动工前落盘：受影响书例清单+双端锚+4锚/10锚）。基线推进 `snapshots/20260918_l1.json` → **`20260918_p1.json`**（LATEST 已推进）。

### 落地项（新检测面×2 + 新消费边×2）

| 项 | 位置 | 落地 |
|---|---|---|
| A8 支杀化印（新检测面①） | `objective/zuogong_detect.py` `_scan_shayin_huayong` | 新 type='支杀化印' 与 '杀印相生' **并列**，明杀透干门未动：杀不透干+印 active（透干/月令/坐下）+杀支与印支六合/半合+杀支非旬空（日/年并参）。**仅入 work_actions 不进 work_types**——confirm/gongliang/xiangfa 均以 type=='杀印相生' 精确匹配消费，新型结构性不可达（化用虚高 4 锚免疫）。书锚 chuji:1369-1371/zhongji:3911-3912·3932-3933/shouke:6648；反锚 shouke:5768（申杀旬空，li112 保） |
| A19 食合官支（新检测面②合关系识别+消费边④G9 扩展） | `subjective/guanming.py` G9 循环扩展 | 非日柱激活自合柱+柱干食伤+坐支主气官杀 → combo '合制·食合官支'；**时柱主位门**（书规则三 zhongji:3683，主席例在时柱；F12 主位门合成例保）+**官支入墓门**（入墓之物不做功 KB §4.1；反锚 lixiangxue:6340 普例1「巳入戌墓…难以成大贵」）。书锚 chuji:1751-1756 |
| A11 贼捕制印/制官杀（新消费边③ zeishen→guanming） | `subjective/zeishen_bushen.py` 新公开 `detect_zeibu_dangshi` + `guanming.py` 消费 | 党势级贼捕轴：贼虚透（透干无本气支）+捕=贼克星党≥_TAI_WANG(6.0)+捕/贼≥3+贼原神不救；贼=印→combo '贼捕制印'（入印类家族 `_yin_combo_hit`/`_yin_now`，方向门禁令沿用）；贼=官杀→combo '贼捕制官杀'（G3 同口径门）。书锚 chuji:380-385/zhongji:3855-3857/gaoji:11171·11380。纯新增函数，zeishen 既有输出零改动（gongliang/caiming 零传导），engine.py 零改动 |
| 哨兵 | `mangpai/tests/test_p1_guanming_zeibu.py` 11 测 | 先红（ImportError）后绿（11/11）；含 A8 不进化用主功链契约（confirm primary_work≠化用）、li112 旬空门、普例1 入墓门、李昌镐 G6 保、zhenbao-01/岳飞 A11 不命中反锚 |

### 翻转明细与逐条归因（全量 blind diff，vs l1）

- **trainset 官 96→100✅（+4，方案带 +3~5 内；M3：Δ+3.5%<半宽和12.9% 噪声带内，CI 下界 75.6%→79.6%）**：cj-正处级化杀（A8，chuji:1371）/cj-书记（A11，chuji:380）/cj-主席（A19，chuji:1751）/cj-戴笠（A11——⚠️机制类书锚路径修复，该例书文机制=制财军权 C 备案 8，已在预注册声明）。**财/职零翻转**。
- **heldout 三维零翻转零抖动**：官 48✅/财 47✅/职 24✅ 保（红线①②达成；scored ❌18 无一命中三机制，li207 杀透干属旧型校准域非本批对象）。
- **文本抖动 1 条**：zj-平常八字 veto_reasons ['反局']→[]——A8 命中（申子合化杀生身，与 cj-正处级同构）→印化官杀=正向结构→官命域门槛剥反局，机制设计内（官命维 unscored 零评分影响）。

### 验证（全绿）

- 哨兵 11 测先红后绿；pytest **1077 passed+1xf**（1066+新增 11）；verify 432+70+64+20 全绿。
- 双 seed（PYTHONHASHSEED=0 vs 默认）blind 快照剥 _meta 逐字节一致。
- regression67/famous 无变化（化用虚高 4 锚 CAT1 在内✓）；calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财）零新增（探针实证两例三机制均不命中，存量维持）。
- A4 印类方向门 10 锚逐例复验全 True（岳飞/蒋介石/周恩来×2/例6副省级/曾国藩×2/银行行长×3）。
- check_layering+check_typing_imports 通过；3.11.15/3.14.4 双版本 compute_all 冒烟一致。
- 残留：本批代码改动未提交（工作树）；P2（A12+A13-A18 可机制化者）为下一批。

## P2 官命 fp 窄修簇批（2026-09-18，执行登记 · 引擎精度批 P 系列第二批——判定改动批，objective 零改动）

> 依据：方案 `~/.claude/projects/-root-metaphysics/memory/kimi-engine-precision-plan-20260918.md` P2 节；预注册 `docs/kimi-p2-guanming-prereg-20260918.md`（动工前落盘：fp 簇 7 例定位+双端锚+四保护锚 margin+收档清单）。基线推进 `snapshots/20260918_p1.json` → **`20260918_p2.json`**（LATEST 已推进）。

### 落地项（2 条，全走 guanming 消费侧）

| 项 | 位置 | 落地 |
|---|---|---|
| A12 女命夫宫域分流 | `subjective/guanming.py` `classify_guanming_combo`+`analyze_guanming` 增 `gender` 形参；`engine.py` 调用补 gender（编排侧接线） | 女命日支（夫宫）参与做功的官杀类 combo 归「夫荣」域不计己官；印类/财域/藏杀被制/G9/食合官支/贼捕/化用不动；gender 缺省 None 零行为变化。书锚 chuji:2206-2209+yanjiu:5646；真阳锚 cj-2097/yx-部长，假阳锚 cj-2206 |
| A17 旺杀入墓墓不开不作功 | `subjective/guanming.py` 新 flag（仿 G6 形态，消费 `muku.analyze_muku` 公共 API） | 官杀主气支≥2 全入同一在局墓+墓未开+无官杀做功 combo/印化官杀 → 不立官命；豁免=有官杀做功（曾国藩「功在墓杀」/阎百川 lixiangxue:7182 墓统杀为所用）；detail 仅决定性时追加。书锚 chuji:1405/1409+第二独立锚 chuji:3161；真阳锚 曾国藩×2/军官师级，假阳锚 cj-1395 |
| 哨兵 | `mangpai/tests/test_p2_guanming_fp.py` 10 测 | 先红（5 红：gender kwarg 不存在+A17 未立）后绿（10/10）；含男命对照/缺省兼容/双真阳锚/公安保护锚/vacuous 防误火 |

### 收档清单（A13/A14/A15/A16/A18，5 条不机制化）

- **A13 争合官无力**（reg67-申机器工人，zhongji:1233）：单例孤锚（全书官域争合唯一处，余皆婚姻域）；「争合」只解释合官一支，翻判须连撤 3 个硬制 combo 机制不符；与 R3GUAN「官合身=官来找我」（cj-处级-2「合身，肯定是个官」）锚冲突。
- **A14 合绊无功**（zj-教师无官，zhongji:2308）：翻判须否决印类 combo（印制伤食寅克戌纯宾位）——触方向门禁令（KB §4.7，10 锚）；「子丑合不做功」系闲注案例语非通用条款。
- **A15 制不尽→实测=合用官被穿破**（cj-老总，chuji:3258-3262「卯辰穿，子卯破，日主合用的东西地支不能坏」）：该盘另有印化官杀 shengyong 独立立官（化用真功单独可立），撤 combo 不足以翻判；单例无书明文条款。**侦察偏差备案**：KB 标 A15=制不尽，实测该例书文机制=合用官被穿破，以书原文为准。
- **A16 禄上坐官**（cj-平辛辛苦苦挣钱，chuji:2285）：孤例（全书唯一处）；翻判须同时撤印类 combo（印制财/财制印），触方向门禁令。
- **A18 制财尽**（cj-巨富制尽，chuji:916-922）：与 G7 窄豁免真阳锚 cj-县长（戊戌壬戌辛亥甲午）同构不可分（同为辛亥日两戌制日支亥印制伤食），动之则翻 cj-县长 ✅——同 F15 C4 教训。

### 翻转明细与逐条归因（全量 blind diff，vs p1）

- **trainset 官 100→102✅（+2，方案带 +2~5 下沿；M3：Δ+1.7%<半宽和 12.0% 噪声带内，CI 下界 79.6%→81.6%）**：cj-2206（A12，chuji:2206）/cj-1395（A17，chuji:1405）。**财/职零翻转**。
- **heldout 三维零翻转**：官 48✅/财 47✅/职 24✅ 保（红线①②达成；scored 命中面=零，预注册命中）。
- **文本抖动 2 条**：cj-妓女（trainset）/shouke-qi23-闹婚不离（heldout）veto_reasons []→[岁运反局…]——A12 夫宫分流后 is_guanming_raw=False，官命域 veto 链收窄（含岁运剥除）不再适用，机制设计内连锁；两例官命维 unscorable 零评分影响。
- **落地偏差备案**：预注册探针（按 combo key 并集 positions）曾预判 reg67-制例二/shouke-li084-夫不要她翻转，实码按动作逐个判定更窄，两例实际不变（colateral 小于预注册，良性偏差）。

### 验证（全绿）

- 哨兵 10 测先红后绿；pytest **1087 passed+1xf**（1077+新增 10）；verify 432+70+64+20 全绿。
- 双 seed（PYTHONHASHSEED=0 vs 默认，同 note 复跑）blind 快照逐字节一致（cmp 通过）。
- regression67/famous 无变化；calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财）零新增。
- 四保护锚 margin 检验全保（cj-2097/yx-部长/reg67-公安/cj-公安 True；朱元璋=heldout 只评估 True——⚠️偏差备案：任务书称四锚「均在 trainset 可查到」，实测朱元璋仅在 heldout，以只评估方式核验）；本批无降分条款，margin≤1 禁降分规则不适用；邻近锚曾国藩×2/军官师级靠「有官杀做功」豁免（=条款核心区分非补丁）。
- A4 印类方向门 10 锚逐例复验全 True。
- check_layering+check_typing_imports 通过；3.11.15（verify）/3.14.4（pytest 全量+verify_layer1）双版本冒烟一致。
- 残留：本批代码改动未提交（工作树）；官命残留 ❌13（§6.2：fp 簇余 5 收档+C 备案 7+散落 1）；P3（财命残簇 A4/A12/A13）为下一批。

## P3 财命残簇批（2026-09-18，执行登记 · 引擎精度批 P 系列第三批——判定改动批，caiming 消费侧，objective 零改动）

> 依据：方案 `~/.claude/projects/-root-metaphysics/memory/kimi-engine-precision-plan-20260918.md` P3 节；预注册 `docs/kimi-p3-caiming-prereg-20260918.md`（动工前落盘：509 例 A4/A12/A13 探针命中面+书锚逐字行号+双端锚+预期翻转清单）。基线推进 `snapshots/20260918_p2.json` → **`20260918_p3.json`**（LATEST 已推进）。

### 前提复核：A4/A12 收档（方案现场核实过时）

- **A4 土金伤官怕见官→caiming 封顶：收档**。方案称「juefa 检测有、caiming 零消费」半过时——juefa 分向 verdict 已被 `yongshen.detect_shangguan_jianguan`（N1）消费（yongshen.py:879-921「成势怕见官」severe 条款，K3-294批5 立，书锚 gj-低保伤官 gaoji:19657），经 mingju_xiong→caiming 凶向封顶链（caiming.py:1692-1700）传导已通。探针实测 509 例怕见官 facet 命中面：b67-过河拆桥（✅富，**反向锚**，财明现通关）/gj-煤矿工人（✅贫）/gj-低保伤官（✅贫）/cj-邓小平（财维 unscored）——**scored ❌/⚠️ 目标=零**，再立宽条款只有误伤富锚面无收益面。
- **A12 体坏未入凶向链：收档**。方案前提已过时——`detect_zhuwei_ti_chonghuai`（N5，yongshen.py:1416-1471，独眼乞食 zhongji:5049 族书锚）于 K3-294批6 已接入 mingju_xiong（yongshen.py:1682-1684），severe 封顶贫；全库命中面仅 zj-独眼乞食 1 例且已 ✅，残余=零。

### 落地项（A13 制库基阶落位两条款，全走 caiming 消费侧）

| 项 | 位置 | 落地 |
|---|---|---|
| 条款一（上限） | `subjective/caiming.py` `_detect_zhiku_decai` 增输出 `ku_han_guansha`（库藏干同含官杀=「财库加官杀」）+制库独力上浮分支新增封顶 | 制库独力上浮触巨富时，库无官杀同藏→封顶富（`_liangji_cap` sticky 开库不得翻越）；库同藏官杀者豁免保巨富。保端=yx-煤矿（yanjiu:7689-7691「丑为财库加官杀，做功能量很大…十几亿」）/奥纳西斯（lixiangxue:6470-6474 四层功量 L4 直达不经上浮链）；杀端=cj-富火运（chuji:5526-5530「戌中辛偏弱…财不大…数百万」）/reg67-制例二（lixiangxue:6478-6484「虽也是富命，但远不如前者…数千万」） |
| 条款二（下限 sticky） | `subjective/caiming.py` 浮财/合绊/入墓阻断降档分支 | `has_zhiku` 在档→落富（3）不落小康（2）——库财通道独立于明财，收束 floor「基阶不落下富」与阻断降档的「升后复降」矛盾（同 F6 禄/伤食下浮制库豁免形态）。杀端=制例二（明财壬坐壬戌自合柱被合绊仍书判富命）；保端=无制库 blocked 例结构性不动+凶向已压例（独眼乞食/入狱一年终档不变） |
| 哨兵 | `mangpai/tests/test_p3_caiming_zhiku.py` 10 测 | 先红（5 红：schema/富火运/制例二×2/入狱一年 static）后绿（10/10）；含 ku_han_guansha schema/煤矿·奥纳西斯保端/李嘉诚锚/A4·A12 收档 guard（低保伤官贫/过河拆桥富/独眼乞食贫） |

### 翻转明细与逐条归因（全量 blind diff，vs p2）

- **trainset 财 59→61✅（+2，方案带 +2~4 下沿；M3：Δ+1.8%<半宽和 18.1% 噪声带内，CI 下界 43.1%→44.8%）**：cj-富火运发财数百（条款一，巨富→富）/reg67-制例二（条款一+二，小康→富）——全预注册。**官 102✅/职 40✅ 零翻转**（红线②达成）。
- **heldout 三维零翻转**：官 48✅/财 47✅/职 24✅ 保（红线①达成；scored 财维命中面=零，预注册命中——zhiku 命中 8 例逐一核：li002/li211/qi50/li240 库藏官杀豁免或不经上浮分支，ans06/li222 财维 unscored）。
- **文本抖动 7 条全归因**：条款一 caiming_adjust×5（heldout ans06/li222/qi05 + trainset cj-市长/famous-李世民）+gj-入狱一年（adjust+tier_static 巨富→富，凶 verdict 评全量轨小康不变✅）+条款二×1（heldout li240 adjust 补记岁运反局封顶2阶——条款二落富后原已在 cap 下的凶向封顶文本显形，tier 终值不变）。无白名单外路径。
- **M2 分组门禁**：trainset 富组 13✅→15✅（⚠️18→16，改善）；巨富/小康/平/贫/破财/凶六组逐字不动；heldout 七组逐字不动。无失衡恶化。
- **富命锚复验**：李嘉诚/保尔森（zhiku=False 结构性不动）/奥纳西斯（L4 直达不动）/煤矿（ku_han_guansha 豁免保巨富）/巨富组 M2 不动——全保。

### 收档候选（❌10 中非 P3 三簇对象，入档不立）

- yx-贫家境贫寒一贫（yanjiu:1618-1626）：阳日见阴官之害（双胞胎对照：甲寅时=yx-富富有百万 富有百万 ⚠️/乙卯时=贫）——机制=十干喜忌域（戊喜见甲），非伤官诀/体坏/制库簇。
- yx-贫穷命贫困线上（yanjiu:6782-6788）：「日主太弱财星太旺，日主无力取财，财星又不做功」——身弱财旺 cap 有 §7-15 双锚（qi14/森田健）否决记录；「财不做功」腿单例孤锚，未达立法门槛。
- cj-装璜（chuji:4755-4766）：书「原局没有制干净」应不净封顶 L3，gongliang 实测 L4——须动功量层，超 P3 caiming 消费侧范围，留后续批。
- 余 7 例=既有备案原位（zhenbao-14a calib 常驻/cj-种地/yx-破财那几年/yx-建筑化象/cj-包工头 C 备案族/cj-妓女/cj-教授待研）。

### 验证（全绿）

- 哨兵 10 测先红后绿；pytest **1097 passed+1xf**（1087+新增 10）；verify 432+70+64+20 全绿。
- 双 seed（PYTHONHASHSEED=0 vs 默认，同 note 复跑）blind 快照逐字节一致（cmp 通过）。
- regression67/famous 无变化；calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财）零新增。
- 凶向标注只写全量轨红线复查：本批不触 :1883-1897 强制标注段；diff 中静态轨（tier_static/level_static）零凶向词新增（入狱一年 tier_static 巨富→富为档位变化非凶向标注）。
- check_layering+check_typing_imports 通过；3.11.15（verify 432+70）/3.14.4（pytest 全量+verify 64+20）双版本冒烟一致。
- 残留：财命 ❌10 原位（条款目标为 ⚠️ 侧 overshoot/落位，❌ 侧全为非三簇机制或既有备案）；代码改动未提交（工作树）；P4（职业军警墓库做功）为下一批。

## P4 职业军警新面批（2026-09-18，执行登记 · 引擎精度批 P 系列第四批=收官批——判定改动批，objective muku 纯增量检测+zhiye military 窄消费）

> 依据：方案 `~/.claude/projects/-root-metaphysics/memory/kimi-engine-precision-plan-20260918.md` P4 节；预注册 `docs/kimi-p4-zhiye-muku-prereg-20260918.md`（动工前落盘：509 例候选命中面扫描+书锚逐字行号+双端锚+预期翻转清单+gating 吸收面）。基线推进 `snapshots/20260918_p3.json` → **`20260918_p4.json`**（LATEST 已推进）。

### 落地项

| 项 | 位置 | 落地 |
|---|---|---|
| 检测面（objective 纯增量） | `objective/muku.py` 新增 `detect_ku_zhi_ku(zhis)` | 库制库=阳库（辰戌，阳土）收/刑 阴库（丑未，阴土），阳库恒为制方（阳制阴）：收=is_entomb 四库之土入辰墓（理象学:3008 族；戌论冲开不入墓故土支入戌不成立，收式唯辰）；刑=丑戌/戌未。阳库冲阴库十二支不存在（辰戌=阳阳、丑未=阴阴），kind∈{收,刑} 两式完备。**analyze_muku/is_entomb/GAN_TOMB_ZHI/TOMB_MAP 既有输出零改动** |
| 消费条款（窄消费桶=military 单桶） | `subjective/zhiye.py` `_score_military` F15 块后（贵气门**外**） | **库制库·阳制阴（墓用执法象）+6**，要件与门：① detect_ku_zhi_ku 命中；② 阴库成双多见（丑≥2 或未≥2——墓用结构条件2「有物可墓…成势、多见」gaoji:2190-2194，案例三双丑/例四双未明文；单库孤见不成墓用）。墓用结构=格局级做功（gaoji:2177-2182），不走贵气门（:11956 所管=8.2 字级组合）；8.2 六组组合与封顶+6 零改动；mingju_xiong 军警 gating（classify 层）照旧撤分 |
| 哨兵 | `mangpai/tests/test_p4_zhiye_kuzhiku.py` 10 测 | 先红（ImportError→检测/警察墓库/例四红）后绿（10/10）：检测层 4 测（含复例四 检测层命中/消费层被成双要件挡住的分层验证）+目标书例 2+fp 守护（乔布斯/罗斯切尔德/yx-科级结构性不命中）+锚 margin（例二 mil==10/例九 mil==11 逐字不动）+例五 gating 保护链+探针 ≥4/10 |

### 书锚（回书逐字核行号，mangpai-gaoji-ocr.txt）

- 真阳锚① gaoji:2401-2417 第二章 2.5 墓用结构·案例三（=trainset gj-警察墓库）：「阳库（辰）收阴库（丑），有制阴得阳之象」「阳制阴，有执法、纠正之象」「墓用结构，阳库制阴库。实际为警察」。
- 真阳锚② gaoji:11747-11756 8.2 军官例四：「戌未相刑，刑开官杀库。戌为火库，即火药库、刀枪库。刑杀库做功，乃入兵营掌权之象」+口诀二「比劫库冲杀库动，麾下兵众听号响」。
- 要件锚 gaoji:2190-2194（墓用结构三条件之二「成势、多见」）；类象锚 gaoji:11630-11632（丑=阴库公安象）/:11665（口诀一）/:11785-11788（丑戌刑阳制阴扫黑破案）。
- 假阳锚（结构性不命中实证）：罗斯切尔德（丑未各一+阴阴冲）/复例四经商（丑单见）/乔布斯（阴库 0）/yx-科级（阴库 0，F15 collateral 案例不复现）/朱元璋（丑未各一，heldout 官命锚不动）。

### 翻转明细与逐条归因（全量 blind diff，vs p3）

- **trainset 职 40→41✅（+1）**：gj-警察墓库 merchant(7)→military(7，tie_pri military>merchant)——全预注册唯一 scored 翻转。**官 102✅/财 61✅ 零翻转**（zhiye 单模块改动，官/财链零消费 zhiye，结构性保证+diff 实证）。
- **heldout 三维零翻转零抖动**：官 48✅/财 47✅/职 24✅ 保；M2 财命七组双集逐字不动；M3 全维「噪声带内」。
- **文本抖动 0 条**。快照字段级 diff 唯一变更=trainset gj-警察墓库（zhiye_primary/label+职 ❌→✅）。
- **命中面 12 例的 gating/快照吸收归因**（预注册 §四命中面 vs 实测）：条款命中=train 5+heldout 6+探针例四。其中 zj-数亿坐牢/heldout-qi22 无职业 verdict 快照不收（unscorable，引擎侧 primary 有变但零评分面）；cj-足球（mil 8→14 primary 不变 unscorable）/yx-建筑-2（1→7）/yx-8721（2→8）/heldout-qi50（0→6）分数升而 primary 不变；heldout-li139/qi05 原局凶向 gating 撤分为 0 零变化；**heldout-li141  standalone 命中但 blind 上下文喂运（壬戌运/庚辰年）触发岁运反局军警 gating（流年反局·类型一破坏功神）撤分**，快照零变化——gating 保护链全数按设计工作，无白名单外路径。
- **军警探针 3/10→4/10**：军官例四（mil 1→7 过阈，laborer fallback→military）归位；例一/二/九保（例二 margin 6、例九 margin 1 逐字不动——条款对两锚结构性不命中：未 1 单见）。

### 验收对照（方案 P4 节 5 条+全系列红线）

① heldout 职 24✅ 零回退 ✔；② 探针 4/10 ≥4 ✔；③ 例二/例九 margin 检验保（逐字不动）✔；④ yx-科级 collateral 类不复现（阴库 0 结构性不命中+哨兵锁定）✔；⑤ 哨兵先红后绿+六件套全绿 ✔。预警指标 trainset 职 +2~4 **未达（+1）——偏差备案**：库制库书锚仅 2 例同构（警察墓库+例四，例四不在两集），yx-公安/reg67-公安/cj-戴笠等军警残留分差 6-10 且无第二同构书锚（铁律4），不为追指标放宽条款（窄检测面纪律优先于预警带）。

### 收档清单（本批复核后维持，勿再立项）

- 8.2 例三（金水成势无库+凶向 gating，书机制=岁运火来炼金非原局面）/例五（凶向 gating 财坏印）/例六（lawyer 桶抢；书机制「官库戌被冲开」系大运辰运应期面）/例七（performer tie，伤官制官归 lawyer 桶界）/例八（羊刃合杀落 military=公检法/武职桶界张力，F15 备案）/例十（比劫库制印：政委例十 vs 复例四双锚同构不可分，F15 铁律16 已撤）。
- 军警备案簇余：岳飞（官杀 0）/cj-戴笠（无官杀，贵气门所挡）/reg67-公安（merchant 10 分差不可及）/yx-公安（卧底，merchant 10 分差；日支丑入辰墓单见不成双）/reg67-财制印刑警=例九同盘已 ✅。
- 「库藏何物」细分（杀库/印库分级加权）：两锚各执（例四杀库/案例三印库），无第三锚定级，不立。

### 验证（全绿）

- 哨兵 10 测先红后绿；pytest **1107 passed+1xf**（1097+新增 10）；verify 432+70+64+20 全绿。
- 双 seed（PYTHONHASHSEED=0 vs 默认）blind 快照剥 _meta 逐字节一致。
- regression67/famous 无变化；calib 常驻 2 条（zhenbao-01 官/zhenbao-14a 财）零新增。
- **muku 消费方全量回归（F2 先例）**：供给契约零改动（纯增量新函数），13 调用点（verify_mangpai×9/zuogong_detect/dayun/zaihuo×3/caiming/gongliang/utils._ensure/liuqin×4/zhiye/gongmen_wuzhi/xiangfa_ops/guanming/engine）由 pytest 全量+blind 双集+67/famous/calib 实证零回归。
- check_layering+check_typing_imports 通过；3.11.15/3.14.4 双版本 blind 冒烟剥 _meta 逐字节一致。
- **P 系列收官终态**：P1（官+4）/P2（官+2）/P3（财+2）/P4（职+1）四批全落地，trainset 官 96→102✅/财 59→61✅/职 40→41✅，heldout 三维全程零回退（官 48✅/财 47✅/职 24✅ 四批贯穿）；方案单列项=财命 G5 破从/A1 反局（高风险单列或收档，方案四节已定）；残留=官 ❌13/财 ❌10/职 ❌32（§6.1 军警备案簇警察墓库已清，余收档）。
- 代码改动未提交（工作树，用户未要求 commit）。
