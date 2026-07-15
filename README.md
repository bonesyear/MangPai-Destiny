# MangPai · Chinese Bazi Analysis Engine

基于段建业/郝金阳盲派理论的八字命理推演引擎，49 模块四层架构，919+ 验证用例全绿。

---

## 架构

```
八字输入 → Foundation（公共基础）→ Objective（确定性检测）→ Subjective（解释性判断）→ Narrative（叙事层）

foundation/objective/    2 模块   干支性情 · 纳音计算（跨流派共享）
mangpai/objective/      25 模块   排盘 · 做功检测 · 神煞 · 墓库 · 虚实 · 应期
mangpai/subjective/     22 模块   层功 · 财官婚姻 · 象法 · 岁运反局 · 职业 · 六亲 · 灾祸
```

## 验证

| 验证 | 用例 | 状态 |
|------|------|:--:|
| verify_mangpai | 853 | ✅ |
| verify_dayun | 70 | ✅ |
| pytest | 103 | ✅ |

## 三层审计

| 层 | 内容 | 通过率 |
|:--:|------|:--:|
| 第一层 | 基础数据（纳音/节气/藏干/长生/干支性情）vs 经典原著 | 100% |
| 第二层 | 模块算法 67 例 vs 段建业原著 | 72%✅ 28%⚠️ 0%❌ |
| 第三层 | 端到端 10 例 vs 郝金阳断语 | 47%✅ 75%✅+⚠️ |

## 快速开始

```python
from mangpai.engine import calc_mangpai_full
result = calc_mangpai_full(1992, 10, 9, 13, 58, 'male', 114.09)
print(result['summary'])
```

## 理论来源

基于段建业盲派方法论，核心理论参照《段氏理象学》《盲派命理研究》《盲派初级/中级/高级命理学》《命理授课教程》及《命理珍宝50期》。基础语法层参照《渊海子平》《子平真诠》《滴天髓阐微》等子平经典。

## 依赖

Python 3.10+，标准库。无外部日历库或其他依赖。

## 许可

MIT
