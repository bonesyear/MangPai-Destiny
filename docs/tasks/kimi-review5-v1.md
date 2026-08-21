# Kimi 任务：第五轮审查 V1 · 新维度书锚终审（qianyi/xiangmao 过 U1 级复核）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 第五轮方案（`kimi-review5-plan-2026-08-20.md` 的 V1 定位：qianyi/xiangmao 08-20 落地晚于第四轮，是四轮审查体系外唯一引擎代码——只有哨兵测试，没过 U1 级书锚复核）+ 缺口批报告（gap1 qianyi / gap2 xiangmao）
2. **独立判断纪律**：旧归档仅参考，以原著原文 + 当前代码为准
3. 本批 = **V1 新维度书锚终审**（只审不改；纯本地零 API）
4. 汇报 300 字内

## 任务
1. **qianyi 书锚逐条回书**（参照 U1 标准——防锁自造 spec，chuangong 教训）：
   - qianyi.py 每条规则书锚行号 → 回原著逐字核对（规则是否真书明文支持）
   - 原局三 marker（月日冲背井离乡 gaoji:5857 / 日时合安居 gaoji:5858 / 马临年时 gaoji:6735）
   - 应期五机制（马逢冲 shouke:3602+gaoji:6757 / 合到门户 zhongji:4179+lixiangxue:6571 / 马星伏吟 shouke:6692 / 冲出年时 shouke:72 / 马逢合停留窗 zhongji:1567）
   - 哨兵反证：test_qianyi.py 11 测是否真锁书锚（A 书锚直锁/B 工程自洽/C 锁错）
2. **xiangmao 书锚逐条回书**：
   - 4 主线（秀气透干 zhongji:3914+6655 / 金水伤官限辛 zhongji:1484+shouke:5394 / 活木见火 zhongji:4513 / 眼象丙丁癸 zhongji:1482）+ 2 弱线（gaoji:5618 / zhongji:3981）
   - 哨兵反证：test_xiangmao.py 7 测分级（A/B/C）
3. **维度交付口径裁定**（方案 V1 顺带项）：新三维度（zinv/qianyi/xiangmao）只进特征 JSON 不进五维叙述——「维度交付」宣称口径建议（进叙述 or 保持特征层+文档口径）
4. 发现分级：P0（书锚违书=阻塞维度宣称）/ P1 / P2

## 红线
- 只审不改（问题清单记录，修复另排）
- 书锚铁律（每条核对带行号）

## 产出
1. qianyi 回书表 + 哨兵分级
2. xiangmao 回书表 + 哨兵分级
3. 维度交付口径裁定建议
4. P0/P1/P2 清单
5. 汇报 300 字内
