# mangpai-system — 盲派命理计算系统

## 项目概述

基于段建业《段氏理象学》和郑民生《十排歌》体系的盲派八字命理计算引擎。以"宾主体用做功"为核心分析框架，覆盖客观层（计算引擎）和主观层（分析解读）。

## 目录结构

```
mangpai-system/
├── objective/           ← 客观层：纯计算引擎
│   ├── __init__.py      # 主引擎入口 MangpaiEngine + compute_all()
│   ├── README.md        # 模块说明
│   ├── constants.py     # 全局常量（天干地支五行冲合刑害等表）
│   ├── canggan.py       # 藏干规则（段氏：午藏丁己，巳藏丙戊庚）
│   ├── changsheng.py    # 长生十二宫（阴阳同生同死）
│   ├── nayin.py         # 纳音五行 + 纳音做功分析
│   ├── shensha.py       # 神煞计算（天乙/文昌/华盖/桃花/劫煞/灾煞等）
│   ├── zuogong.py       # 做功引擎（制用/合用/墓用/生用/化用）
│   ├── binzhu.py        # 宾主三层分法（主→近宾→远宾）
│   ├── tiyong.py        # 体用分类（比/禄/印/食 vs 财/官/伤）
│   ├── muku.py          # 墓库：开库/闭库/入墓/透干引拔
│   ├── anhe.py          # 暗合：寅丑午亥卯申子巳
│   ├── biqi.py          # 闭气：子丑辰酉午未卯戌
│   ├── wood_type.py     # 木死活分类（甲木喜庚/乙木喜癸）
│   ├── soil_type.py     # 土燥湿分类
│   ├── he_types.py      # 合类型分析（天干合/地支六合/三合/半合）
│   ├── virtual_solid.py # 虚实分析
│   ├── zhengfan.py      # 正反局判定
│   ├── gongshen.py      # 宫身分析
│   ├── work_level.py    # 做功层次评估
│   ├── shenshu.py       # 十神数量歌诀（郑民生十排歌）409 测试通过
│   ├── shipaige.py      # 十排歌扩展：断语集锦（六大领域）+ 方法论 ★新增
│   ├── xiangfa.py       # 象法（干支象/十神象/宫位象）
│   ├── dayun.py         # 大运盲派分析 ★新增
│   ├── liunian.py       # 流年盲派分析 ★新增
│   ├── jiaoyun.py       # 交运时间模块（段氏五行交运表+sxtwl） ★新增
│   ├── advanced.py      # 高级分析
│   └── verify_mangpai.py# 客观层全量验证脚本
│
├── subjective/          ← 主观层：分析解读
│   ├── __init__.py      # 主观层入口
│   ├── schools.py       # 学派选择器（段氏/盲师/综合）
│   └── prompts/
│       ├── __init__.py
│       └── mangpai.md   # 盲派分析 prompt 模板
│
├── docs/                ← 文档 & 需求规格
│   ├── duan-shi-lixiangxue-excerpts.md  # 段氏理象学摘录
│   ├── zhengminsheng-shipaige-fragments.md  # 郑民生十排歌碎片
│   └── chuangong-spec.md               # 串宫压运模块需求文档 ★
│
├── tests/
│   └── test_subjective.py  # 主观层测试
│
├── verify_mangpai.py    # 全量验证入口（409 测试通过）
└── verify_dayun.py      # 大运验证（69 测试通过）
```

## 核心模块详细说明

### objective/ — 客观层计算引擎

| 模块 | 大小 | 说明 | 置信度 |
|------|------|------|--------|
| `constants.py` | 12KB | 全局常量表：天干地支、五行生克、冲合刑害、纳音、神煞等 | 高 |
| `canggan.py` | 2KB | 藏干规则：段氏体系午藏丁己、巳藏丙戊庚 | 高 |
| `changsheng.py` | 2KB | 长生十二宫：段氏阴阳同生同死 | 高 |
| `nayin.py` | 3KB | 纳音五行表 + 纳音做功权重 | 高 |
| `shensha.py` | 9KB | 神煞：天乙贵人、文昌、华盖、桃花、劫煞、灾煞、孤辰、寡宿、羊刃 | 高 |
| `zuogong.py` | 51KB | 做功引擎：制用/合用/墓用/生用/化用 + 成势判别 | 高 |
| `binzhu.py` | 4KB | 宾主三层：主(日柱)→近宾(月时)→远宾(年) | 高 |
| `tiyong.py` | 2KB | 体用：体(比禄印食) vs 用(财官伤) | 高 |
| `muku.py` | 11KB | 墓库六原则：开库/闭库/入墓/透干引拔/坐墓不墓/多而入墓 | 高 |
| `anhe.py` | 2KB | 暗合四对：寅丑/午亥/卯申/子巳 | 高 |
| `biqi.py` | 2KB | 闭气四对：子丑/辰酉/午未/卯戌 | 高 |
| `wood_type.py` | 3KB | 木死活：甲木喜庚/乙木喜癸 | 高 |
| `soil_type.py` | 2KB | 土燥湿：辰丑为湿/未戌为燥 | 高 |
| `he_types.py` | 4KB | 天干合/地支合类型分类 | 高 |
| `virtual_solid.py` | 5KB | 虚实判断 | 高 |
| `zhengfan.py` | 10KB | 正反局判定 | 高 |
| `gongshen.py` | 2KB | 宫身分析 | 高 |
| `work_level.py` | 8KB | 做功层次评估 | 高 |
| `shenshu.py` | 8KB | 十神数量歌诀：郑民生十排歌，1清纯/7成势/2-6混杂 | 高 |
| `shipaige.py` | 12KB | 十排歌扩展：断语（父母/婚姻/子女/事业/牢狱/寿元）+ 方法论 | 低(待校订) |
| `xiangfa.py` | 8KB | 象法表：干支象/十神象/宫位象 | 中 |
| `dayun.py` | 27KB | 大运分析：宾主第三层、废神遇运、墓库冲合、禄刃应期 | 中 |
| `liunian.py` | 7KB | 流年分析：复用大运核心 + 君臣互动 | 中 |
| `jiaoyun.py` | 11KB | 交运时间：段氏五行交运表 + sxtwl 精确计算 | 高 |
| `advanced.py` | 2KB | 高级分析接口 | 中 |
| `__init__.py` | 17KB | 主引擎：MangpaiEngine + compute_all() + 全模块集成 | 高 |

### 验证测试

| 文件 | 测试数 | 状态 |
|------|--------|------|
| `verify_mangpai.py` | 409 | ✅ 全通过 |
| `verify_dayun.py` | 69 | ✅ 全通过 |

### 待开发模块

| 模块 | 规格文档 | 优先级 |
|------|----------|--------|
| `objective/chuangong.py` | `docs/chuangong-spec.md` | 高 |
| 全量回归测试 | — | 高 |
| 贼神捕神（特殊格局） | — | 低 |
| 命宫胎元 | — | 低 |

## 工作进展时间线

| 日期 | 内容 |
|------|------|
| 7/7 | 全量客观层模块搭建（25个py文件） |
| 7/7 | verify_mangpai.py 409测试通过 |
| 7/7 | 神煞补充：天乙贵人、文昌、华盖（+81用例） |
| 7/7 | subjective/ 主观层基础搭建 |
| 7/7 | dayun.py（27KB）+ liunian.py（7KB）大运流年模块 |
| 7/7 | verify_dayun.py 69测试通过 |
| 7/8 | jiaoyun.py 交运时间模块（段氏五行+sxtwl） |
| 7/8 | shipaige.py 十排歌断语集锦+方法论 |
| 7/8 | chuangong-spec.md 串宫压运需求规格 |
