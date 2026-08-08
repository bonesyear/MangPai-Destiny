# K3 任务：294 例训练集 · 职业 55❌ 根因分类（纯分析）

## ⚠️ 执行指引
- 纯分析任务：**全部结论写归档** `/root/.claude/projects/-root-metaphysics/memory/k3-trainset294-zhiye-2026-08-08.md`，stdout 只报 300 字摘要
- 不要读留出集（铁律：只评估不反推）；分析对象是训练集 294 例
- 可参考财命/官命分析的先例框架（A 引擎/B 数据/C 备案 + 簇划分 + 逐例总表）

## 背景
财命（52.21%）、官命（83.48%）已修完。职业是最后的大头：trainset 职业 25.29%（22✅/10⚠️/55❌）——三维最弱。heldout 职业 40.38%。

## 任务：职业 55❌ 逐例分类
1. 提取训练集职业 55 个 ❌ 的全部明细（id/八字/verdict（职业断语）/primary/primary_label/evidence）
2. 逐例分类为三型：
   - **A 引擎规则缺陷**（primary 判错桶，规则可修——指到 zhiye.py 具体逻辑：桶打分/merchant 通道/co-occurrence）
   - **B 标注质量问题**（verdict 转录/桶映射有误，数据侧修正）
   - **C 书锚边界**（书判如此、引擎口径差异，无简单修复——备案）
3. 关键维度：**桶分布**——55❌ 里金标桶各多少（merchant/teacher/lawyer/doctor/laborer/unemployed/military/performer/accountant）、引擎判到哪去了（confusion 矩阵重点：哪两个桶互相串）
4. 已知线索（历史备案）：
   - merchant 商业类召回（批11 修过，现在漏判还有多少？）
   - 职业桶粗口径 _ZY_RULES（批12 修过假阳性）
   - famous 罗斯切尔德 ❌（merchant 判 teacher，批11 存量）
   - 官命联动：批29 后官命大涨，职业是否受联动影响（如 military/公检法 与官命同源）
5. 每型统计 + 清单 + 根因 + 修复建议（A/B 型给具体方案，C 型备案）

## 注意
- 55 例逐个过，不要抽样
- ⚠️ 与官命/财命的联动：官命 veto 链修复（批29）是否误伤/助益职业判定（如 military 桶靠 guanming 信号）——分类时标注
- 职业是「桶集合」判定（primary 命中即✅）——fp/fn 的概念不同于财命/官命，用「错桶」表述

## 输出（写归档，300 字摘要到 stdout）
三型统计 + 桶分布/confusion 重点 + A 型修复清单（按收益排序）+ B 型数据修正 + C 型备案 + 官命联动影响
