# 盲派客观层（mangpai-system/objective）

盲派命理计算引擎，以「宾主体用做功」为核心分析框架。理论来源：段建业《段氏理象学》、盲师口传体系。

## 模块总览

| 模块 | 说明 |
|------|------|
| `constants.py` | 所有盲派常量表（藏干表、长生起点、暗合、闭气、燥湿、纳音权重、化用、墓库、六破等） |
| `canggan.py` | 盲派藏干（午只藏丁、巳丙戊庚顺序等） |
| `changsheng.py` | 阴阳同生同死十二长生（盲派特有规则） |
| `nayin.py` | 纳音计算 + 纳音权重做功分析 |
| `anhe.py` | 暗合（寅丑/午亥/卯申/子巳） |
| `biqi.py` | 闭气（子丑闭金/辰酉闭水/午未闭木/卯戌闭火） |
| `wood_type.py` | 活木/死木分类 |
| `soil_type.py` | 燥土/湿土分类 |
| `binzhu.py` | 三层宾主分析（以日柱为体，年/月/时为宾） |
| `tiyong.py` | 体用分类（天干十神分体用） |
| `muku.py` | 墓库规则（开库/闭库/入墓） |
| `shensha.py` | 扩展神煞（羊刃/劫煞/灾煞/孤辰/寡宿等） |
| `xiangfa.py` | 象法数据（天干象/地支象/十神象/宫位象） |
| `zuogong.py` | **核心做功引擎**：制用/合用/墓用/生用/化用五类做功分析 |
| `gongshen.py` | 功神/废神分类 |
| `he_types.py` | 合的类型细分（天干合、地支六合、三合、半合等） |
| `work_level.py` | 做功层次评估（Level 0-5） |
| `virtual_solid.py` | 虚实分析（天干根气、通根） |
| `zhengfan.py` | 正局/反局判断 |
| `dayun.py` | **大运盲派分析**：干支关系/墓库开闭/废神激活/禄刃应期/气势变化/综合吉凶 |
| `liunian.py` | **流年盲派分析**：流年与命局互动+流年与大运互动（君臣关系） |
| `advanced.py` | 后向兼容 shim |

## 安装

```bash
# 将 objective/ 目录放到项目根下即可
# 目录结构：
project/
├── main.py              # 需提供 calc_bazi_full() 函数（八字基础排盘）
└── objective/           # 盲派模块
    ├── __init__.py
    ├── constants.py
    └── ...
```

## 依赖

**强依赖：** `main.calc_bazi_full()` — 需提供八字基础排盘函数，返回以下字段：
- `bazi`: {year, month, day, hour} 四柱（如 "甲子"）
- `shishen`: 十神映射
- `kong_wang`: 空亡数据
- `di_zhi_relations`: 地支关系
- `input`: 输入信息

**Python 环境：** Python 3.9+，无额外第三方依赖，仅使用标准库（`dataclasses`, `logging`, `typing`）。

## API

```python
from objective import MangpaiEngine, calc_mangpai_full

# 方式一：直接排盘（需 main.calc_bazi_full）
result = calc_mangpai_full(
    year=1984, month=6, day=15, hour=8, minute=0,
    gender='男', city_lon=121.47,
    yin_method='same_as_yang',   # 盲派阴阳同生同死
    shensha_reference='year',    # 神煞参考柱
)

# 方式二：使用已有的八字数据
bazi_data = calc_bazi_full(...)  # 你已有的八字排盘
engine = MangpaiEngine(bazi_data, shensha_reference='year')
result = engine.compute_all()
```

## 输出结构

```python
result = {
    'bazi': {...},           # 四柱原始数据
    'input': {...},          # 输入信息
    'canggan': {...},        # 藏干（盲派规则）
    'chang_sheng': {...},    # 十二长生（阴阳同生同死）
    'nayin': [...],          # 纳音
    'nayin_work': {...},     # 纳音做功分析
    'shensha': {...},        # 神煞
    'binzhu': {...},         # 宾主分析
    'tiyong': {...},         # 体用分类
    'zuogong': {             # 做功分析（核心）
        'work_types': [...], # 做功类型
        'work_tier': '...',  # 做功层次描述
        'work_level': 0-5,   # 做功层级
        'work_efficiency': '...', # 效率
        'work_actions': [...],    # 具体做功动作
    },
    'muku': {...},           # 墓库分析
    'anhe': {...},           # 暗合
    'biqi': {...},           # 闭气
    'wood_type': {...},      # 木性
    'soil': {...},           # 土性
    'he_types': {...},       # 合类型
    'virtual_solid': {...},  # 虚实
    'zhengfan': {...},       # 正反局
    'xiangfa': {             # 象法
        'gan_xiang': {...},
        'zhi_xiang': {...},
        'shishen_xiang': {...},
        'gongwei_xiang': {...},
    },
    'kong_wang': {...},      # 空亡
    'di_zhi_relations': {...}, # 地支关系
    'summary': '日主：甲子；做功类型：制用；...',  # 中文摘要
}
```

## 统计

- 23 个模块，约 3300 行代码
- 每个模块独立 try/except，单模块失败不影响其他
- 测试：`tests/test_subjective.py`（27 个测试，用于主观层联调）
- 独立验证脚本：`verify_mangpai.py`（根目录，V7 合并版 432 项，原 `objective/verify_mangpai.py` 已并入）、`verify_dayun.py`（70 项大运流年专项）
