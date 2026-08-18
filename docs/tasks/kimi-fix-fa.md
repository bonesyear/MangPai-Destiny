# Kimi 任务：修批 A · LLM 红线（siwang scrub → zeishen 单源化 → gongmen 摘除）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + `/root/metaphysics/docs/audit-progress-20260816.md`
2. **读 R5 归档**：`/root/.claude/projects/-root-metaphysics/memory/kimi-review-r5-2026-08-18.md`（3 block 证据链：siwang 键外泄漏三处/shipaige+liuqin+xiangfa_ops；换象 11 例矛盾 10 train+1 heldout 样例 zhenbao-09；gongmen 98.8% 恒真）+ R6 结论（修批 A 顺序即依赖）
3. **先预注册后动手**（本批铁律，见下）
4. 汇报 300 字内

## 任务（三项，顺序即依赖）
### A① siwang 死亡词典 scrub（最高危，先行）
- 泄漏三处：shipaige「寿元：食伤被制短命」「父死母再嫁」、liuqin「手足早夭」、xiangfa_ops.xiangfa_fallback lianti warning「寿命」、guanming「制死」（R5 实测）
- 修法：payload 装配层统一死亡词典 scrub（非逐键补丁）——LLM 视图层过滤，引擎内部保留
- 验证：构造死亡盘实跑 payload——零死亡词汇命中

### A② zeishen 单源化（同根根治换象 P0 + caiming wa=空）
- 根：huanxiang()（xiangfa_ops.py:994）用裸 detect_relations wa（engine.py:442）缺 zuogong_confirm 的 auxiliary 标记 → 假「净」；caiming `_zeishen_jingzhi` 调 zeishen 不传 zg→wa=空
- 修法：换象改消费引擎已算的 zeishen_bushen 结果（净制口径单源化），或对传入 wa 套 zuogong_confirm 同款 auxiliary 标记；caiming 补传 zg
- 预期：11/509 矛盾例（10 train + 1 heldout）口径统一；heldout 那 1 例可能翻转

### A③ gongmen 从 selectors 摘除（一行级，殿后）
- is_wuzhi 98.8% 恒真零信息量——selectors 摘除 + engine 键处理（F18 已切断 narrative 通道，本步落 payload 通道）
- 注意：selectors 39 键变 38 键（文档同步）

## ⚠️ 预注册铁律（Kimi R6 评估采纳版）
1. **A② 动手前**：从 R5 临时语料（/tmp/r5_corpus.json 若在）或重跑全量定位 heldout 那 1 例的**身份**，写明其**预期翻转方向**（预注册，写进本批汇报）
2. **翻转判据**：heldout 翻转逐条审原因——**书锚方向允许（预注册的 1 例）**，非书锚方向回退；不机械凑零翻转
3. 该例外仅限预注册 1 例，不普适放宽

## 红线
- **heldout 财 47✅/官 48✅/职 24✅ 基准不回退**（除预注册 1 例外）
- siwang scrub 只动 LLM 视图层，引擎内部 siwang 保留（F14 设计不变）
- 书锚铁律

## 验证（六件套）
1. 哨兵红绿（A①②③ 各新增测试） 2. verify 432 3. pytest 全绿 4. blind --baseline snapshots/20260817_f19.json 翻转明细（含预注册 1 例确认） 5. 67/famous/calib 0 回归 6. 双 seed 一致 + 构造死亡盘 payload 零命中复验

## 汇报（300 字内）
三项改动/行号 + 预注册 heldout 例身份与预期方向 + 哨兵红绿 + 验证 6 项 + heldout 翻转明细
