# Kimi 任务：通盘审查 R3 · 哨兵质量（防锁自造 spec）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（R3 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读历史教训**：chuangong 案例（20 测锁自造 spec，docstring 伪标「置信度高」，非段氏体系）——R3 的核心是防这类「测试锁错行为」在 F0-F19 新增测试中重演
3. 本批=**新增哨兵质量审查**（F0-F19 新增 ~60 个测试文件/哨兵，检查锁的是不是书锚行为）
4. 汇报 300 字内

## 任务
1. **F0-F19 新增测试全扫**：tests/ 下 F 批新增的测试文件（test_anhe/test_muku/test_qiyun_jiaoyun/test_virtual_solid/test_wood_type/test_gongfei/test_jiangjieshi_wa/test_f11~f19 等）——逐文件检查：
   - 断言的是书锚行为还是工程自洽行为？（书例引用 vs 自造 spec）
   - 有没有「锁错」的（与书例冲突/与审计结论冲突/锁的是中间态）
   - 有没有裸断言（无来源注释、无行号、无法追溯）
2. **哨兵质量分级**：A（书锚直锁）/ B（工程自洽可接受）/ C（锁错或锁自造 spec 需修）
3. **重点抽查**：
   - test_gongliang 阎锡山 L3/奥纳西斯 L4（F6 哨兵——书锚直锁？）
   - test_zhengfan_shuli 7 书例（F7）
   - test_f12_guanming_juefa（F12）
   - test_f18_shipaige_gongmen（F18）
   - chuangong 19 xpassed 备查（F1 处置后状态）
4. 输出：测试文件清单（每个：断言类型/书锚来源/质量分级）+ 问题清单（C 级需修项）

## 方法
- 读测试文件 + 对照书锚行号（grep 注释里的行号 vs 原著）
- 只核不修

## 产出
1. F 批新增测试质量总表（分级 A/B/C）
2. C 级清单（测试名/锁了什么错/建议修法）
3. 汇报 300 字内
