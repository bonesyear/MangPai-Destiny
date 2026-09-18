# Kimi 任务：遗留问题评估（判断哪些该修/不该修，纯规划）

## ⚠️ 执行指引
- 纯评估：报告写 `/root/.claude/projects/-root-metaphysics/memory/kimi-leftover-assessment-20260918.md`，stdout 400 字内摘要
- **只判断不动手**（不改代码、不建批）
- **先读**：`docs/remaining-tasks-20260917.md`（收工记录 §二 全部待议项）+ `docs/tasks/codehygiene-fix-backlog.md`（H-fix-4a「未删待议」/ H-fix-5「待议问题」/ H-fix-2a zaihuo label 节）+ `docs/review7-assessment-20260822.md`（审查可停的元判断——作为"是否值得再动"的参照）

## 评估对象（**排除 feishu 群聊相关**）
**A. 未删待议 4 项**：
1. SHIPAI_DOMAINS/METHODOLOGY（修批C 明议留档优先）
2. gongmen_wuzhi 整模块（engine 键保留=锁定决策）
3. 输出面死字段（virtual_solid counts / soil wet·dry / 华盖 year_ref）
4. jiaoyun `if not span` 边缘语义

**B. 待议问题 6 项**：
1. xiangfa_ops set 迭代序随 PYTHONHASHSEED 旋转
2. `engine.py:578` liunian_data truthy 非 dict → AttributeError（P2 bug）
3. `engine.__init__` 未初始化 `_auto_liunian_injected`
4. `_scan_shengyong` 嵌套冗余 / `_prepare_inputs` 死代码块
5. gongliang 4 处自调吞异常 / 13 书例无命中
6. detect_relations 返回含 set（消费方须排序）

**C. 其他备案**：
1. `zaihuo.py:388` 正官误标「七杀」label（修法已定，延后的理由是"文本变更"）
2. `formatter.DISCLAIMER` 与 `llm_channel._DISCLAIMER_LINE` 文本重复
3. `test_snapshot_hygiene.py`（快照 meta 链自动校验）未立
4. magic numbers ~45 处

**D. 上线 checklist #3 真实凭证冒烟**（群聊 #4 已排除——此条你只需评估"是否值得在真实环境补跑"）

## 每项请给出
1. **判断**：修 / 不修 / 待条件（明确表态）
2. **理由**：技术依据（风险面/影响面/维护成本）——不要泛泛而谈
3. **若修**：工作量估计（小时级/一次小批/需专门批）+ 风险（是否触碰判定/输出面）+ 依赖（是否需要其他批先做）
4. **优先级**：🔴 应尽快 / 🟡 可顺手 / 🟢 可后置 / ⚪ 明示不修

## 汇总结论需回答
1. 这些项里**哪些是真正值得动的**（合并成"遗留清理批"是否合理，大概几批）
2. 哪些**应该明确关闭**（写"不修"而非留着悬置）——理由
3. 是否存在"**看起来是遗留、实际已无意义**"的项（如过度防御、已失效的兼容）
4. 若重启引擎判定精度批（官命 A12-A18 残簇等），这些遗留项中哪些**会自然被覆盖**

## 红线
- 只评估不改动
- 不调外部 API
