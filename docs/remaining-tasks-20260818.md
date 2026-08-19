# 收工记录 · 2026-08-18（终态，下次开工必读）

> 上一份收工记录（remaining-tasks-20260808.md）已归档到 docs/archive/（如需历史对照）。
> 本文件是 08-18 引擎+LLM 通道双轨终态。所有里程碑 commit 均在 GitHub。
> **08-19 D1 数据批已执行**（见下方「D1 快报」），三、四、五节仍有效。

## D3 快报（2026-08-19，供给批 · dayun_analysis 死 selector 修复）

- **断裂点**：selector 声明与转发均正常；LLM 批跑/评估路径 bazi_data 无 da_yun 键 → engine `if dy_list:` 不成立 → compute_all 不产出 → 声明静默落空。修复=build_payload 层补供（`objective/dayun.dayun_gz_sequence` + 复用 analyze_dayun_mangpai），**engine 零改动**；合成路径起运岁诚实缺省（缺精确出生时刻），order 为锚。
- **验证**：哨兵 test_d3_dayun_payload.py 先红 3 后绿 5/5；verify 432+dayun 70（顺手修 39→38 断言）全绿；pytest 722+1xf+19xp；blind vs d2 零翻转零抖动；67/famous 0 回归；calib 常驻 2 条无新增；双 seed payload 探针一致。基线 `snapshots/20260819_d3.json`。token +约 4500/命。
- **下一批**：D4 prompt 迭代 5（L1 职业锚定+L2 应期逐年锚定，prompts 受保护须批准；dayun_analysis 已就位可直接引 `dayun_analysis.dayun` 整组）。D1 存量② KB pytest 记数已随批更正。

## D1 快报（2026-08-19，commit `7eb7ca5`）

- **改动**：gold 标注错 5 条（calib zhenbao-05 官命 lv4→3/层功[3,4]→[2,3]、zhenbao-23a 层功 max1→2；trainset cj-处级-5 财 富→小康、cj-足球 财 小康→富）+ source 锚漂移 15 处 + raw_quote 张冠剔除（cj-贫穷命）+ calib zhenbao-10 dayun 误录删除（戊寅=1998 流年非大运，50qi:313-315）+ cj-老总口径注。**纯数据批，引擎零改动**。任务书 `docs/tasks/kimi-d1-data-batch-20260819.md`。
- **验证（Hermes 复核）**：calib 常驻回归 4→2（余 zhenbao-01 官命/zhenbao-14a 财命=引擎错存量）；trainset 财 51.33→**52.21%**（59✅/44⚠️/10❌，翻转 2 条皆改善）；heldout vs fb **零翻转零抖动**（官 72.73/财 68.12/职 46.15）；verify 432 全绿；pytest 704（684+1xf+19xp）。
- **基线**：trainset 新基线 `snapshots/20260819_d1.json`（全量）；KB §0/§6.3/§6.4/§9 已同步。
- **存量备案（非本批引入）**：①verify_dayun 69/70——selectors 总数断言 39 vs 实际 38（修批A③ 摘 gongmen_wuzhi 后断言未同步，KB §10.1 #42 已载 38 键口径）；②KB pytest 记 682 过期（实测 704）——均留修批D/下批顺手。
- **下一批候选**：D2 入口批（E1 性别缺省策略须用户拍板：显式必填 vs payload 标注；E3 界外年份 guard；E4 lon 校验）→ D3 供给批（E2 dayun_analysis 死 selector：摘死键 vs engine 补供，用户拍板）→ D4 prompt 迭代 5（L1 职业锚定+L2 应期逐年锚定，S1 复验闸门）。规划详见 `docs/kimi-review3-t4-summary-20260818.md` §2。

## 一、引擎终态（2026-08-18 复跑确认）

**留出集（215 例）**：财命 **47✅ 68.12%** / 官命 **48✅ 72.73%** / 职业 **24✅ 46.15%**
**训练集（294 例）**：财命 58✅ 51.33% / 官命 96✅ 83.48% / 职业 40✅ 47.06%
**工程**：pytest **701 collected（681+1xf+19xp）** / verify 432+70+64+20 全绿 / 双 seed 确定 / M5 快照链至 `20260818_fb`（修批D 后未更新快照——修批D 是纯性能改动 509 例对拍 0diff，最新基线仍可用 fb）

## 二、LLM 通道终态（08-18 达标）

- **四指标全达标**：L0 0.36% / N1 0.36% / **L1 0.00%**（remap 后）/ L2 4.98%
- **4 轮迭代轨迹**：L1 40.21→23.88→12.76→9.62→3.41%→remap **0.00%**
- **组件**：llm_backend（DeepSeek v4-flash 直连，**峰谷计价**）/ llm_prompt（五维 schema+死亡禁令）/ llm_channel（三层校验+remap 规则 A-D）
- **文档**：`docs/llm-channel-20260818.md`（五节交付文档）+ `docs/llm-batch-report-20260818.md`（验证报告）
- **成本**：单命 ~¥0.09 峰 / ¥0.045 谷（**DeepSeek 已涨价**：v4-flash 峰 $0.44/$1.32 谷半价，8-16 生效；旧 $0.14/$0.28 作废）

## 三、全链路里程碑（07-31 → 08-18）

```
段氏理论消费 → 三维攻坚(财68.12/官72.73/职46.15 heldout) → 扩容294例
→ 十批审计(600项) → F0-F19修复(19批) → R0-R6通盘审查(7批)
→ 修批A/B/C/D(审查发现全清) → LLM通路MVP → 4轮迭代 → remap → L1归零
→ 峰谷价+正式通道文档 ✅ 双轨可交付
```

commit 链：审计 `d056cb1` → F 系列 `3a8fda1..cdb184a` → 修批 `6264b46..c4f87c5` → LLM `fa191f0..beb3949`

## 四、剩余（全部可选/长期，无硬待办）

| 项 | 状态 |
|----|------|
| 飞书集成（LLM 通道接日常推演） | 未做——通道已达标，想做随时接 |
| 单命调用体验打磨 | 未做 |
| P3 信息级 2 项（_safe_compute 吞异常/三煞名实） | 可忽略 |
| 跨流派（子平/紫微） | 暂缓 |
| 十排歌完整版（付费） | 暂且这样 |
| KB §6.5 收档 15 项/三维残留 | 已收档不追 |

## 五、关键环境与教训（防再踩）

- **Kimi CLI**：`/root/.kimi-code/bin/kimi -p "先读 knowledge-base.md，然后…"`——任务开头必带知识库（记忆替代机制）；kimi 配额=5h 账单周期非整点重置
- **push 通道**：GitHub 直连超时 → 临时 URL（gh-proxy+token）push，`ls-remote` 验证；origin 保持干净 URL
- **DeepSeek 峰谷**：北京 09-12/14-18 = peak（涨价价），其余半价；大批量跑低峰期
- **验证六件套**：verify_mangpai 432 / verify_dayun 70 / layer1 64 / layer3 20 / pytest / blind_eval（基线快照链）
- **铁律**：heldout 是闸门（财 47✅/官 48✅/职 24✅ 不回退）；书锚铁律（规则改动带书明文行号）；LLM 输出永不入 compute_all dict；prompt 调优只吃 trainset
