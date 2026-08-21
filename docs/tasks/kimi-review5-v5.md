# Kimi 任务：第五轮审查 V5 · 卫生抽查 + 六件套全量复跑 + 发布 go/no-go（收官批）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 第五轮方案（V5：卫生抽查+六件套全量复跑+发布版 go/no-go）+ V1-V4 结果（P0×1 免责声明缺失；P1×若干；P2×若干——全部记录待修清单，本批只汇总不改）+ 待修清单（`docs/tasks/review5-fix-backlog.md`）
2. 本批 = **V5 收官批**（卫生 + 六件套 + go/no-go；只审不改）
3. 汇报 300 字内

## 任务
1. **六件套全量复跑**（U4 后只做过增量，本批全量）：
   - verify_mangpai 432 / verify_dayun 70 / layer1 64 / layer3 20
   - pytest 全量（794+ 预期）
   - blind_eval --baseline snapshots/20260820_gap2.json 零翻转（含 trainset）
   - 67/famous/calib 回归
   - 双 seed
   - 快照链完整性（d1→gap2 + V3/V4 无快照合理）
2. **卫生抽查**（V1/V6 P2 复确认 + 新漂移）：
   - V6 P2×4 状态确认（docstring/Tuple/bot body/client.send——Tuple 已 V3 实锤必修）
   - V1 P2×2（行号/措辞）
   - V2 P2（@bot 前缀等）
   - KB/CHANGELOG/收工记录 vs 当前状态新漂移（V1-V4 报告是否入档？——若缺记录到待修清单）
3. **发布 go/no-go 汇总**（五轮完整）：
   - **P0 阻塞项**：免责声明缺失（V4）——修了才能发布
   - **P1 必清**：Tuple 环境崩溃（V2/V3 实锤）/ lark_md 三符 / xiangmao 丁眼锚注 / mark 模式死亡词展示 / 外发告知
   - P2/备案：清单化
   - 发布判定：修 P0+P1 后 = 可发布；否则 NO-GO
4. 产出：六件套实测表 + 漂移清单 + **最终发布 go/no-go + 统一修批规划**（把待修清单升级为排期）

## 红线
- 只审不改（六件套跑不改代码）
- 全部本地（不调 DeepSeek）

## 产出
1. 六件套实测表
2. 卫生漂移清单
3. **发布 go/no-go 判定**
4. **统一修批规划**（P0/P1/P2 排期——五轮后统一修的执行方案）
5. 汇报 300 字内
