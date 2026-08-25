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
