# 收工记录 · 2026-08-08（下次开工必读）

> 本文件是 6 天后的开工上下文。引擎状态、批次进度、下一步、文件位置全在这。

## 一、当前基线（2026-08-08 收工时，全部复跑确认）

**留出集（215 例）**：
- 财命 **66.67%**（46✅/15⚠️/8❌）
- 官命 **74.24%**（49✅/17❌，批29 后 56.06%→74.24%）
- 职业 **44.23%**（23✅/7⚠️/22❌，批2 后 40.38%→44.23%）

**训练集（294 例，G1-G3 扩容后）**：
- 财命 **52.21%**（59✅/42⚠️/12❌，批1-6 收官）
- 官命 **83.48%**（96✅/19❌，批29 收官）
- 职业 **43.53%**（37✅/13⚠️/35❌，批2 主体后 36.47%→43.53%）

**工程状态**：verify 432+70 全绿、pytest 473 passed、双 seed 逐字节一致、全库 0 xfail。

## 二、批次进度（共 31 批，全部已 commit+push）

- 第七~九批：财命 50% 攻坚 P0/P1/P2（42.9%→57.97%）
- 第十批(F)：P3 测量卫生（M1/M2/M5）
- 第十一~十三批：职业 merchant 修复 + 假阳性剔除 + famous 官命 4 例
- 第十四~十六批：乾隆 xfail + 上浮链收敛 + yongshen 3 项
- 第十七~十九批：巨富 overshoot + gongliang 校准 + E 收官（xfail 清零）
- 第二十~二十二批：G1/G2/G3 训练集扩容（23→294 例）
- 第二十三~二十八批：294 例财命批1-6（38.05%→52.21%）
- 第二十九批：294 例官命批（65.22%→83.48%，命中模拟上限）
- 第三十批：294 例职业批1（25.29%→32.94%，heldout 商人 3 例无损）
- 第三十一批：职业批2 首步（32.94%→36.47%，配额中断部分落地）
- 第三十二批（2026-08-14）：职业批2 主体（36.47%→43.53%，**heldout 40.38%→44.23%**，commit 85e9337；五规则栈：印食文墨三型/食伤鬻文/月令印主气化/金水声音/卯酉冲门户，sim3 否决粗版四案）

CHANGELOG：`mangpai/CHANGELOG.md`（到第三十一批）
K3 分析归档：`/root/.claude/projects/-root-metaphysics/memory/`（24+ 个，CC 自动加载）

## 三、下一步（开工顺序）

1. **职业批 3 接续**：剩余 35❌（清单在 CHANGELOG 第三十二批第 16 行 + K3 记忆；模拟脚本 `_zy2_sim.py`/`_zy2_sim2.py`/`_zy2_sim3.py` 复用）
   - 已知残留簇：中医 3 簇（merchant 7-11 分差过大）、military C 备案簇（岳飞/戴笠/公安×2）、lawyer yx-2/3、laborer 4（base_career 可达性）、accountant 6（桃花 fp 压平误伤真艺人被否，待新通道）、performer 阿炳/帕瓦罗蒂/导演（财明现豁免挡无桃花通道）、马云/图书管理员/校长/组织部/记者等
   - **⚠️ 本批两个变差点名（A1 水财算帐通道误伤疑似）**：heldout ans12 下岗穷命 ⚠️→❌（未分类→会计）、trainset yx-中介 ⚠️→❌（投资中介→会计）——下批先修，书锚驱动
   - 预期：35❌ → ~28-32❌（职业 ~46%）
   - 红线：heldout 职业 23✅ 不回退（44.23% 底线）
2. **杂项清理**（1 批）：M3 Wilson CI 报告、_p2_diag.py 留删、gongshen 备案、GitHub remote tracking 刷新
3. 三维收官后：待办清单 docs/remaining-tasks-20260802.md 里的长期项（跨流派暂缓、LLM 推演通道未启动）

## 四、关键上下文（防失忆）

- **kimi 配额**：5h 账单周期非整点重置。2026-08-08 耗尽、**08-14 已恢复**（职业批2 主体已用掉一批余量，下一批再耗尽需用户查重置时间）。
- **基线快照**：最新 `snapshots/20260814_a.json`（第三十二批后，职业 heldout 44.23%/trainset 43.53%；注意 20260808_r.json 是批1 后状态，trainset 职业 32.94% 已过时）
- **GitHub push**：直连不通。用临时 URL：
  `git push "https://bonesyear:${GITHUB_TOKEN}@gh-proxy.com/https://github.com/bonesyear/MangPai-Destiny.git" main`（GITHUB_TOKEN 在 /root/.hermes/.env；push 后 `git ls-remote origin main` 验证，本地 ahead 是 tracking 假象）
- **K3 启动**：`cd /root/metaphysics && set -a && . /root/.hermes/.env && set +a && export CLAUDE_CODE_AUTO_COMPACT_WINDOW=1048576 && export CLAUDE_CODE_EFFORT_LEVEL=max && cat <任务文件> | claude --print --output-format text --max-turns 150`
- **任务文件备份**：/tmp 下历史任务文件已复制到 `docs/tasks/`（/tmp 可能被清）
- **长输出风控**：分析/混合任务须限输出（300 字摘要/写归档），见技能 mangpai-workflow 6a
- **配额中断处理模式**：K3 中途 403 → 验证已改代码（自洽+heldout 无损就收尾 commit），剩余等恢复接续
- **铁律**：留出集只评估不反推；回归检测反馈用书锚修；heldout 是闸门（职业批1 首版 merchant 误伤 3 商人被回退的教训）
- **K3 记忆**：分析归档自动加载（CC 项目记忆），K3 记得全部历史；Hermes 记忆在 ~/.hermes profile

## 五、明确不做

- 跨流派（子平/紫微）——用户暂缓
- LLM 推演通道（DeepSeek 思考+JSON 模式已消化文档，未启动）
