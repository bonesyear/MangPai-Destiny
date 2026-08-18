# Kimi 任务：通盘审查 R5 · LLM 前置检查（R1 后接）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/tasks/kimi-review-plan.md`（R5 定位）+ `/root/metaphysics/docs/knowledge-base.md`
2. **读 R1 结果**（同会话前批归档或 CHANGELOG）：P0 xiangfa_ops 换象门 raw wa 漏滤 auxiliary（locked 断语进 payload 与同帧 narrative 矛盾，11/509 例）；P1 zaihoo/laoyu year-only 神煞丢失、calib 不传 age
3. 本批=**LLM 通路前置检查**（构造盘实跑 payload，只核不修）
4. 汇报 300 字内

## 任务
1. **siwang 物理屏蔽复验**（F14 后）：构造含死亡/寿元断语的盘（如 zaihuo siwang 高、寿元星被坏），实跑 build_payload——payload 中确认无 siwang/寿元 marker；narrative digest 走 zaihuo_llm_view 确认
2. **selectors 39 键对齐**：compute_all 输出 → schools selectors 抽取 → payload 键齐全（对照 llm-channel 归档 39 键清单）
3. **换象 P0 影响面实测**（R1 P0）：构造触发换象的盘，确认 locked 断语确实进 payload + 与 narrative 同帧矛盾（复现 R1 发现，量化影响）
4. **gongmen_wuzhi 泄漏面确认**（R1 第 7 条附注）：selectors 内经 payload 进 LLM 的整块字段——确认其内容（is_wuzhi 近恒真字段进 LLM 的影响）
5. **age 跨年漂移**（R1 P2）：now().year 锚对 payload 的影响（不进 blind 快照但进 LLM 面）
6. 输出：LLM 前置检查表（每项实测结果）+ 阻塞判定（哪些会阻塞 MVP）

## 方法
- 构造 2-3 个代表盘（含死亡断语盘/换象盘/神煞盘）实跑 engine + payload
- 只核不修

## 产出
1. 五项检查实测结果表
2. 阻塞 MVP 判定（go/block 逐项）
3. 修复建议（承接 R1 P0/P1）
4. 汇报 300 字内
