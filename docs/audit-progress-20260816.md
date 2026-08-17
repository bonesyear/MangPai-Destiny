# 审计进度记录 · 2026-08-16（批 5 完成，等配额续批 6）

> 全模块独立复审（LLM 通路前置）：Kimi CLI 对照段氏原著逐模块审查，只审计不改码。
> 总纲：`docs/tasks/kimi-audit-plan.md`（含批5起强制的对照纪律：原著优先/挑战知识库/备案不豁免/带原著行号）

## 批次进度

| 批 | 模块 | 状态 | P0/P1/P2 |
|----|------|------|----------|
| 1 基础语法层 | constants/canggan/changsheng/nayin/zihe/he_types | ✅ | 0/5/12 |
| 2 做功层 | zuogong_detect/confirm、tiyong、binzhu、zeishen_bushen | ✅ | 1/10/13 |
| 3 功量象法层 | gongliang/muku/xiangfa(+ops) | ✅ | 6/19/26 |
| 4 命局正反层 | zhengfan/yunfan/yingqi(+subj) | ✅ | 11/34/39 |
| 5 岁运层 | dayun/liunian/jiaoyun/laoyu | ✅ | 4/22/18 |
| 6 判定层A | caiming/guanming/yongshen/juefa | ✅ | 11/33/24 |
| 7 判定层B | zhiye/hunyin/zaihuo/xueli/liuqin | ✅ | 29/57/45 |
| **累计（十批收官）** | | | **P0=96 / P1=245 / P2=259（共 600 项）** |
| 8 杂项层 | shensha/shenshu/shipaige/gongshen/gongfei/gongmen_wuzhi | ✅ | 24/44/31 |
| 7 判定层B | zhiye/hunyin/zaihuo/xueli/liuqin | ⏸ | — |
| 8 杂项层 | shensha/shenshu/shipaige/gongshen/gongfei/gongmen_wuzhi | ⏸ | — |
| 9 辅助层 | bazi_calc/advanced/biqi/body_parts/chuangong/soil/virtual/wood/anhe | ✅ | 10/15/40 |
| 10 主观层 | narrative/schools/engine编排/payload | ✅ | 0/6/11 |

## 已发现的重磅问题（修复规划时按此优先级）

### P0（22 条，真实违书 bug）
1. **laoyu.py:425 签名错配**——「反局+辰丑」条款实抛 TypeError 被 except 吞，**上线即死 3 年**；laoyu 零测试是存活原因（批5）
2. **zhengfan 7 书例仅 2 命中**——丙子戊戌/癸未丙辰两明文反局判正局（方向相反）；根因=气势门槛不识湿土水势/合坏未消费/日支追求之意未实现（批4）
3. **蒋介石 zb 误净**——zeishen 未滤 auxiliary 致 target_wx_set 污染，书明言「制之不净达不到四层功」；传导 gongliang 三条消费通道（批2/3）
4. **阎锡山 L4 自我撤销校准**——+3 降 +2 又以化用高层加回，三重背离书义，checkpoint 反锁（批3）
5. **奥纳西斯书断 4 层引擎仅 L2**——制库 san_he 门按书例反例立法（批3）
6. **laoyu 李嘉诚 risk=高假阳** + 七杀夹克方向反（上海庄家书锚漏检）+ 阳制阴两分支同值（批5）
7. **交运年份系统性晚一年**——书例 3 虚岁起运书口径 2007 引擎 2008；起运岁实岁小数 vs 书整数虚岁（批5）
8. **yunfan 3 条 P0**：资本运营酉运（T3 伏吟干泛化）/zj 丙戌运（T1 冲无开库豁免）/联动三刑无补全闸（一行可修最优先）（批4）
9. yingqi_subj 寿元星定位缺印星级/坏关系漏克绝/engine 不传 age（批4）

### 系统性疑点
- **断言集行号漂移**：test_liunian_yingqi 6 条锚行号系统性 +4~+11（内容真行号偏，转录版本差）——需一次系统复核；he4 书目张冠（正锚=理象学4072）（批4/5）
- **知识库勘误 2 处**：KB§4.10 统看条文漏「并」字；KB 对 laoyu 零条目（批5）
- **A14 新增规则零 pytest 锁定**是最大裸面（批4）
- jiaoyun/laoyu 零测试；muku/xiangfa/xiangfa_ops 零专项测试（批3/5）

## 下一步
1. 等 kimi 配额恢复 → 批 6（判定层A：caiming/guanming/yongshen/juefa）
2. 批 6-10 完成后 → 汇总全部问题 → 用户批准 → 规划修复批次（每个 P0 修复前回原著重验）
3. 修复优先级参考：laoyu 死条款 > 正反局方向 > 蒋介石 zb > 交运晚一年 > 其余

## 归档位置
`/root/.claude/projects/-root-metaphysics/memory/kimi-audit-{1,2,3,4,5}-*.md`（批 1-5 全落盘）

## 十批收官总结（2026-08-17）

**核心结论**：
1. 算法 P0 全集中在上游检测/判定层（zhengfan/laoyu/guanming/zhiye 等），主观编排层无新 P0（narrative/schools/engine 干净）
2. 主要风险 = **GIGO**：上游低质/敏感字段未经护栏直喂 LLM——**寿元红线只堵一半**（zaihuo.siwang 死亡档直进 LLM 通道，prompt 无一字禁令）
3. **死数据总清单 19 项**：整模块零消费 5（chuangong/body_parts/advanced/gongmen_wuzhi/zaihuo）+ 配置断路 4（桃花 day_ref/shensha_reference 等）+ 死字段 7（zihe/direction 等）+ 死函数分支 3
4. **失效模式定型**：「docstring 冠名引用≠实现合书义」贯穿判定层；「伪标置信度高+测试锁自造 spec」chuangong 最典型
5. 知识库勘误共 46 条（含 pytest 499≠KB 473、SOUL.md 验证数字过期、KB:247 例6 破从与书相反已传导代码注释）

**修复规划素材**：P0 96 条按优先级分档（确定性 bug > 传导断口 > 方向大修 > 死数据清理），每个 P0 修复前回原著重验。

## 修复决策（2026-08-17 用户批准）
- **F0-F19 批次方案批准**（Kimi 规划，依赖拓扑八层，详见归档 kimi-fix-plan-2026-08-17.md）
- **决策点 1**：批次顺序 OK
- **决策点 2**：同意解锁 constants 保护（F2 TOMB_MAP 加戌）
- **决策点 3**：同意解锁 prompts 目录（F14 寿元禁令写进 prompt；备选 payload 降级仍保留）
- 开工时机：等 kimi 配额重置（2026-08-17 下午，当前周期用掉 93%）
- 开工顺序：F0（KB 勘误）→ F1（死数据清理）→ F2-F19
