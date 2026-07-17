# 盲派客观层 变更记录

## 2026-07-17 第一批 · 安全网 + 止血

| 项目 | 内容 | 文件 |
|------|------|------|
| V1 | 67例回归套件入git | tests/backtest/ |
| V2 | calib 46项断言化 | tests/calib_assertions.yaml |
| A2 | 时间锚点修复（current_dayun按年龄定位） | engine.py |
| N1 | 叙事层校验器（数字回对引擎字段） | narrative.py |
| N2 | 降温0.7→0.2 + 数字白名单 | prompts/hao_style_fewshot.py |
| N3 | 5例few-shot重跑（口径跳跃根除） | prompts/hao_style_fewshot.py |
| A1 | yunfan岁运反局接入方向否决链 | yunfan/yongshen/caiming/guanming/zhiye |
| M2 | dayun四项缺陷（死pass/戊刃双刃/开库口径/化气验月令） | objective/dayun.py, shensha.py |
| K2 | zhengfan原局四项（合官位置/时支归主/不可坏/冲合矛盾） | zhengfan.py |

验证：853全绿 + pytest 156 passed + 67例0回归 + calib 3项改进。

## 2026-07-17 第二批 · 方向层体系化

| 项目 | 内容 | 文件 |
|------|------|------|
| M3 | 婚姻加权（宫为主星为辅）+ duohun三检测 + 子息共振 | hunyin.py, liuqin.py |
| M4 | 柱位漏检补齐（生用/墓用/合制/天干克四放开） | zuogong_detect.py |
| M5 | gongliang收尾（气势浪费回接+高级篇三项+双轨对账） | gongliang.py |
| A3 | yongshen升格方向总线（五模块接入direction信号） | yongshen/liunian/zaihuo/hunyin/liuqin/xueli/gongmen_wuzhi |
| K3 | 授课教程逐章审计（263例断例集） | docs/k3-shouke-jiaocheng-audit-20260717.md |
| K4 | 象法回退三分支 + 连体/连墓/丙戊一家 | xiangfa_ops.py |
| V4 | verdict解冻（活算+回归报警） | tests/ |

验证：853全绿 + pytest 156 passed + 67例0回归 + calib 4项改进。

## 2026-07-17 第三期 · 独立模块 + 验证合并

不改核心判定逻辑（zuogong_detect/zuogong_confirm/gongliang 零触碰），
新模块均不接 engine（同 yunfan/zhiye 模式，仅 __init__ 重导出）。

### K7 新建模块

| 文件 | 说明 |
|------|------|
| `subjective/chuangong.py`（新建）| 串宫压运：同支≥2柱成串宫链（2弱串/3强串/4全串），大运/流年压入三型（增强/触发/引入）+冲散/合化/会局 conflict；空亡排除；需求见 docs/chuangong-spec.md |
| `subjective/juefa.py`（新建）| 诀法层（高级篇ch14）：伤官诀五行喜忌5类（金水喜见官/土金喜佩印怕见官/水木喜财官/木火喜见印/火土看组合，乾隆/张之洞等书例全验）+ 断语22项（15/17/19须yongshen_result防过杀、18须shensha_result、女命项须gender）+ 断句集8域26条可查表子集 + 巾箱字碰字6组 + 日元月令诀言词典（书载6条）|
| `objective/body_parts.py`（新建）| 干支身体部位映射（ch11.2主表：干主外/支主内 + ch4/中级扩展层 + 宫位身段 + 阴阳三态/五行病机7组合/穿破刑主病），纯数据查表零判断；为身体部位唯一事实源，xiangfa 'body' 保持速记不回写 |
| 宫位年龄统一 | `xiangfa.GONG_WEI_XIANG` 废弃 1-15/16-30/31-50/50+，全引擎统一大限套（1-18/18-35/35-55/55+），与 `yingqi.DAXIAN_MAP` 同源；MODULE_ATTRS 统一决定已改写 |

### V7 验证体系

| 项 | 说明 |
|------|------|
| verify 合并 | `objective/verify_mangpai.py`（422）与顶层（361）大面积重复，合并为唯一 `mangpai/verify_mangpai.py`，语义去重后并集 **432 项**（保留 objective 版全部 + 并入顶层版独有10项：天乙口诀分组5+柱位场景3+文昌庚干2）；旧 objective 副本删除 |
| xfail 严格化 | test_gongliang.py 3 个 xfail 加 `strict=True`（PUTONG2×2、乾隆冲链） |
| 属性化测试 | `tests/test_property.py`（新建）：100 随机四柱（60甲子+干支错配应力）+ 极端命例 + 60甲子日柱穷尽；不变量：不崩溃、gongliang.level∈[0,5]、work_level∈[0,5]、十神合法、空亡2支、summary为str、重复计算确定性 |

验证：verify_mangpai 432/432、verify_dayun 70/70、pytest 292 passed + 3 xfailed（0 fail）、
67例 vs baseline 无变化（0 回归）、calib 46 项 4 IMPROVE 0 REGRESSION。

存疑备案（本期未动）：`gongshen._PILLAR_BODY` 年/时柱身段与书中三处主表颠倒
（书：年=腿足、时=头面门户；码：年=头颈、时=腿足），另立 bug 单；body_parts.PILLAR_BODY
已按书主表收录，未回写 gongshen。

## 2026-07-09 第一批核心能力升级（高级篇补齐）

基于《盲派高级命理学》审计（memory/mangpai-gaoji-audit-2026-07.md）的第一批 12 项，
全走扩展现有模块（仅 yunfan.py 新建），不碰 schools.py/prompts/。三套验证全绿：
verify_mangpai 409/409、verify_dayun 70/70、pytest 92 passed。

| 文件 | 变更 |
|------|------|
| `subjective/xiangfa_ops.py` | +换象 huanxiang（制尽则主从易位，消费 zeishen_bushen 净制判据）+局象 juxiang（包局/夹局/全阴全阳/专旺/寒暖燥湿五类全局氛围象，与 gongliang 包局并行只做象意不加点）|
| `subjective/gongliang.py` | +层功补齐3项：带象+1（干生支承财官印象且参与做功，原神用神同制不成立方计避免双计）、统+1（消费 caiming 官统财/财统官，同制不成立方计）、富贵贫贱四档定性（wealth_grade/rank_grade/fugui_pinjian 按 level 落档）|
| `objective/zuogong_detect.py` | +夹局 detect_jia_ju()（夹禄/夹刃/夹库/夹财官/夹冲/夹合，纯检测无吉凶）|
| `objective/xiangfa.py` | +六十干支组合象表 LIUSHI_GANZHI_XIANG（11 组核心组合 nature/body/object/person/motto）+ get_liushi_ganzhi_xiang()|
| `subjective/caiming.py` | +过河拆桥分键：制尽(净制)=富格巨富(高级篇) / 制不尽=破财(中级篇)，加 _is_zhi_jin() 制尽判据 + _guan_mingxian_positions/_controlled_guan_positions 辅助；结果加 guohe_chaiqiao_type 字段|
| `objective/shensha.py` | +神煞三层收口：SHENSHA_LAYER 分类(盲派核心5/灾祸三煞/传统6降级) + 亡神表 _WANG_SHEN + 盲派多马星 _YI_MA_MANGPAI；各项带 layer 字段；compute_shensha_ext 加 亡神/马星|
| `subjective/yunfan.py`（新建）| 岁运反局三位一体：大运反局3类型(破坏功神/冲合互变/伏吟三刑) + 流年反局2类型(单独引动/岁运联动) + 岁运联动(天地合/三刑/双冲最凶)；冲合vs合冲、阴阳逆转(禄刃倒戈/忌神反客)；统一消费 zuogong_confirm+zhengfan+dayun+liunian|
| `objective/MODULE_ATTRS.md` | +过河拆桥分键口径标注 + 神煞三层收口口径（替换原神煞配置条目）|
| `tests/test_yunfan.py`（新建）| 8 项测试锁定高级篇 3.3 五命例反局类型检出（案例一/三/四/八/九）|
| `mangpai/__init__.py`、`objective/__init__.py` | 导出 SHENSHA_LAYER、get_liushi_ganzhi_xiang/LIUSHI_GANZHI_XIANG、analyze_yunfan|

去重口径（关键设计决定）：带象+1/统+1 均为高级篇1.4 补齐，与第六章原神用神同制(+2核心铁律)
重叠时不再单计——以「原神用神同制不成立方计」为门，保段氏理象学6章 14 例回归不跨书双计
（唯一触发的 PUTONG1 被相生之功 penalty 封顶一层，回归全绿）。

## 2026-07-08 大运/流年分析模块

### 新增模块
| 文件 | 说明 |
|------|------|
| `objective/dayun.py` | 大运盲派分析（~400行）：干支关系/墓库开闭/废神激活/禄刃应期/气势变化/长生位/综合吉凶 |
| `objective/liunian.py` | 流年盲派分析（~200行）：复用 dayun 核心逻辑 + 流年与大运互动（君臣关系） |
| `verify_dayun.py` | 大运/流年专项验证脚本（69 项测试） |

### 集成变更
| 文件 | 变更 |
|------|------|
| `objective/__init__.py` | +导入 dayun/liunian；`compute_all()` 集成大运流年分析（有数据才算）；`_build_summary()` 加大运摘要；`_raw_bazi_data` 存储 |
| `subjective/schools.py` | selectors 20→23（+`chang_sheng`/`dayun_analysis`/`liunian_analysis`） |
| `subjective/prompts/mangpai.md` | +岁运分析要点（7条大运+1条流年）；输出指引加大运/流年要求 |
| `tests/test_subjective.py` | 适配 23 selectors + 新字段 |
| `objective/README.md` | 模块数 21→23，统计更新 |
| `docs/duan-shi-lixiangxue-excerpts.md` | 覆盖表更新（大运/流年→✅，天乙→✅，交运时间→❌） |

### 大运分析维度（7项）
1. 天干十神定位 + 体用引入
2. 天干关系（合/克/被克）
3. 地支关系（冲/合/穿/刑/破/暗合/三合半合/生/克）
4. 墓库开闭（冲开需透干引拔，合闭）
5. 废神激活（废神遇运而动→新做功）
6. 禄刃应期（到禄位→吉，到刃位→凶）
7. 长生位（日主在大运地支的状态）+ 气势变化 + 空亡折扣

### 流年分析特点
- 复用 dayun `_analyze_pillar_interaction()` 核心逻辑
- 增加流年与大运互动分析（冲/合/穿/刑/生/克/暗合）
- 流年冲大运→运局动荡（降级吉运）；流年合大运→稳定（升级）

### 测试
- verify_mangpai.py: 348 passed（无回归）
- objective/verify_mangpai.py: 409 passed（无回归）
- tests/test_subjective.py: 27 passed（无回归）
- verify_dayun.py: 69 passed（新增）

---

# 盲派客观层 2026-07-07 修复记录

## 文件变更

| 文件 | 增量 |
|------|------|
| zuogong.py | 719 → +300+ |
| work_level.py | +11 |
| muku.py | 修改 |
| constants.py | +8 (LU 表) |
| zhengfan.py | 修改 |
| binzhu.py | 新增 layers 参数 |
| nayin.py | docstring 修正 |
| verify_mangpai.py | 170 → 303 (+133) |

## 修复清单

### 🐛 Bug 修复 (6)
- S1 重复计数去重：type 失配 '合'→'地支合' + frozenset 无序键
- 被动穿 harm 信号被去重吃掉 → _is_passive_chuan 保护
- 四库入墓误判 → 四库走"多而入墓"
- 禄做功触发条件过宽 → has_day_zuo_gong 前置检查
- 正反局不过滤 auxiliary → zhengfan 加 auxiliary 过滤
- 禄 action 追加太晚漏折扣 + 自坐禄双计 + work_types 含 S2 降级

### ✨ 新功能 (8)
- M1: binzhu 返回值消费 → layer 替代硬编码
- M2: tiyong 深度消费 → ti_elems/yong_elems 补充
- M3: 长生效率折扣真正消费
- M4: 天干入墓 → gan_entombed
- 空亡接入做功 → kong_wang 参数
- 伏吟/反吟检测
- 禄做功 → LU 表 + 禄 detection
- 天干克 → GAN_WX 干克检测

### 🔧 重构/修正 (7)
- S2 宾宾交互过滤
- M5 闭库抑制墓用
- 反向做功降级：不 +1 level，改为参考信号
- muku 透干引拔 → 天干透出才开库
- 正反局气势扩展 + 正局 fallback 改"局未定"
- binzhu 新增 layers=2 两层选项
- _is_passive_chuan 提环、work_level L156 修正、主动穿保护

### 审查结论
- 终审：5 个辅助语义/时序缺陷已全部修复
- 303 项测试全绿，零回归
