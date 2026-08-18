# Kimi 任务：散项清 · direction 最小传参版（R2 P2 重算簇）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + R2 归档（`/root/.claude/projects/-root-metaphysics/memory/kimi-review-r2-2026-08-18.md` 的 direction 总线重算簇：engine:505 未传 zhengfan/laoyu → `_ensure_zhengfan`（yongshen.py:1520）重跑 analyze_zuogong；caiming:1850/1855、guanming:954、zhiye:1496 各自再跑——单次 compute_all analyze_zuogong≈6 遍、analyze_laoyu≈6 遍）
2. **方案 A（最小传参版，用户批准）**：只做 engine 传 zhengfan_result/laoyu_result 给消费方，**不做共享缓存**（缓存生命周期是最大风险源——_auto_liunian_injected 有同款边角教训）
3. 基线 = `snapshots/20260818_fb.json`（M5 链）
4. 汇报 300 字内

## 任务
1. **engine 透传**：engine.py:505 附近补传 zhengfan_result/laoyu_result（进 direction 或独立键，按 R2 建议）
2. **三消费方收参**：caiming:1850/1855、guanming:954、zhiye:1496 改收 engine 已算结果（不再各自 `_ensure_zhengfan`/重跑）
3. **yongshen._ensure_zhengfan 保留**（其它调用方仍用；仅 3 消费方改走透传）
4. **验证值一致性**：修后与修前 509 例全量对拍（direction/type/cfg 零 diff）——这是本批核心验收（值一致是方案 A 的安全前提）

## 红线
- **值一致铁律**：509 例对拍零 diff（direction 相关字段），任何 diff 即回退或查明
- **heldout 财 47✅/官 48✅/职 24✅ 不回退**
- 不做共享缓存（方案 A 边界）

## 验证
1. 509 例全量对拍（修前 vs 修后 direction 字段零 diff）
2. verify 432
3. pytest 全绿
4. blind --baseline snapshots/20260818_fb.json 零翻转
5. 67/famous/calib 0 回归
6. 双 seed 一致

## 汇报（300 字内）
改动/行号 + 509 例对拍结果（核心）+ 验证 6 项 + 算力收益估算（analyze_zuogong 6遍→1遍的实际耗时对比）
