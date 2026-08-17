# Kimi 任务：修复批 F1 · 死数据/伪标清理（决策批）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/audit-progress-20260816.md`（F1 定位：死数据/伪标决策与清理，不动算法零风险）+ `/root/metaphysics/docs/knowledge-base.md`（§10 勘误后版本）
2. **读审计归档**：批10（死数据总清单 19 项）、批8（chuangong 伪标、gongmen_wuzhi 未接入）、批9（advanced 死 shim、chuangong 锁自造 spec）
3. 本批清理**死数据/伪标/死模块**，**不改任何判定算法**；若某清理会碰算法 → 记录留对应批次
4. 汇报 300 字内

## 任务（按死数据总清单 19 项逐项处理）
1. **整模块零消费 5 项决策**：
   - chuangong（伪标「置信度高」+20 测试锁自造 spec，非段氏体系）：**下线 or 去冠名**——建议去冠名+标注「非段氏体系参考模块」，测试改 xfail 或删
   - advanced（死 shim，仅 zhengfan 单符号告警）：删除 or 保留告警？建议保留最小接口
   - body_parts（「唯一事实源」名不副实零接线）：接线 or 去冠名？
   - gongmen_wuzhi（实现未接入 zhiye，is_wuzhi 近恒真）：本批**标记弃用**（接入决策留 F18）
   - zaihuo（假阳普遍但**不是死模块**——它是 LLM 通路红线相关）：**不清理**，F14 修
2. **配置断路 4 项**：桃花 day_ref（全库无读者）、shensha_reference（0 处传 'day'）、yin_method、juefa 断语18——统一修复接线 or 标注弃用
3. **死字段 7 项**：zihe 死输出（engine 计算无消费方）、direction 透传、gongshen 四子字段、narrative 回退键、jiaoyun_analysis 等——清理 or 标注
4. **死函数分支 3 项**：anhe alt_key、hunyin _is_zhu、zaihuo for-in-[0] 死壳——删除 or 标注
5. **测试配套**：chuangong 20 条锁自造 spec 的测试 → 改 xfail 或删；每项清理后跑 pytest 确认绿

## 决策原则
- **判定算法零改动**（任何会改变结果的行为变化 → 留对应修复批）
- 清理以「标注弃用/去冠名/删除死代码」为主，接线类仅当零风险
- 每项决策记录：处理方式 + 理由 + 受影响文件

## 红线
- 引擎判定结果不变（盲测快照必须零 diff）
- 不碰留出集；pytest 全绿

## 验证（全部通过后回报，300 字内）
1. `python3 mangpai/verify_mangpai.py` — 432 全绿
2. `python3 -m pytest mangpai/tests/ -q` — 全绿（xfail 数可能变化，说明变化原因）
3. `python3 mangpai/tests/heldout/blind_eval.py --baseline mangpai/tests/heldout/snapshots/20260814_f.json` — **零 diff**（判定不变）
4. 19 项处理明细（每项：处理方式）

## 汇报（300 字内）
19 项逐项处理方式 + 测试/盲测数字 + 判定零变化确认
