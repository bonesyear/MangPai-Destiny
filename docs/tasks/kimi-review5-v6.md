# Kimi 任务：第五轮审查 V6 · 回归复审批（三项过时复查：锚回书/死数据/fuzz）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 第五轮方案 v2（`kimi-review5-plan-2026-08-20.md` 的 V6：承接三项过时复查——①R 轮死数据/双轨（D3 dayun 补供引入 build_payload 合成层=新双轨风险，selectors 38→41 三连跳）②T 轮 fuzz（E5 改 HTTP 面、D2 入口 guard、qianyi/xiangmao 接入 compute_all=新 fuzz 面）③第一轮锚点（E3/E4 自己改的锚需独立回书））
2. **独立判断纪律**：旧归档仅参考，以原著原文 + 当前代码为准
3. 本批 = **V6 回归复审批**（只审不改；**纯本地零 API**——fuzz 用 call_llm=False）
4. 汇报 300 字内

## 任务
### 1. 死数据/双轨复查（R 轮重跑）
- D3 build_payload 合成层（dayun_gz_sequence + dayun_analysis 合成）：有没有新死数据/新双轨（合成路径 vs engine compute_all 路径的 dayun 是否一致）
- selectors 38→41（+dayun/qianyi/xiangmao）：新键是否有读者/死键
- E5 飞书改动（client/bot）：有没有死参数/死分支
- 快照链：gap1/gap2 后仍连续（V5 六件套会全量复跑，本批只查结构）

### 2. fuzz 重跑（T 轮）
- 同 T0 口径：随机日期（1900-2100）×性别跑全链（compute_all + build_payload + render call_llm=False）
- **新增 fuzz 面**：E5 后 HTTP 面（bot 输入畸形 webhook）、D2 入口 guard（性别/年份/lon 边界）、qianyi/xiangmao 新模块（构造触发 marker 的盘）
- 统计：崩溃/异常慢/异常输出/静默模块失败

### 3. 锚点独立回书（第一轮 E3/E4 改的锚）
- E3 改的锚：县长-3 chuji:3702 / 刑警 3843-3852 / zinv 14372-14373 / test_d6b 坤造 gaoji:14242——独立回书核对
- E4 改注：zinv 穿引动（gaoji:14295-14312 / 17465-17484）——注释口径 vs 书原文再核
- 判定：A 对/B 偏差/C 错（书锚铁律）

### 4. 发现分级：P0（违书/崩溃=阻塞）/ P1 / P2

## 红线
- 只审不改（修复另排）
- 纯本地零 API（fuzz call_llm=False；不调 DeepSeek）

## 产出
1. 死数据/双轨复查表（新死键/新双轨/读者缺失）
2. fuzz 报告（N 例/崩溃/异常/新增面覆盖）
3. 锚点回书表（E3/E4 锚逐条判定）
4. P0/P1/P2 清单
5. 汇报 300 字内
