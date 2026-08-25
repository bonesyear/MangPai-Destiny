# Kimi 任务：代码卫生审查 H7 · heldout/顶层验证 + 诊断脚本批（blind_eval/regression/calib 基建 + 诊断脚本）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划 + H1-H6 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×95——本批**重点查同型残留**：裸 except/快照写回原子性——H6 已发现 --write-baseline 缺原子写，本批深挖）+ 收工终态
2. 本批 = **代码卫生 H7 · heldout/验证基建批**（只审不改；纯本地零 API）
3. 汇报 300 字内

## 审查对象
**验证基建（核心）**：blind_eval.py / regression67.py / regression_famous.py / calib_assertions.py / verify_mangpai.py / verify_dayun.py / verify_layer1.py / verify_layer3_checkpoint.py（+ heldout/ 子目录 README）
**诊断脚本（批量）**：heldout/ 下 `_*.py` 诊断脚本（_a1_diag/_a14_diag/_b5_diag/_gm40_diag/_gm_all_dump/_gm_sim/_zy2_detail/_zy2_sim 等）+ output/ 下 19 个 `_*.py` 批跑/分析脚本（_llm_batch_* / _n2_* / _w4_sample / _w5_crosscheck / _t3_eval 等）+ scripts/build_book_index.py

## 审查维度（同前七维 + 验证基建特有）
1. **验证可信度**（验证基建最重要）：
   - `--write-baseline` 写回路径：原子性/校验/误写防护（H6 已标记——深挖具体风险）
   - 快照读写：with 关闭/原地 pop _meta/路径硬编码
   - 验证脚本与主引擎的耦合（改验证逻辑会不会改判定？）
2. **重复逻辑**：regression67/famous/calib 三脚本的结构重复（能否共用框架）
3. **复杂度**：blind_eval 主流程/分析函数
4. 异常处理一致性（裸 except/静默失败——诊断脚本容错性）
5. 死代码（历史诊断脚本残留——_zy2_detail/_gm_sim 等还有用吗）
6. 隐藏边界假设（硬编码路径/魔法数字/固定 seed）
7. import 卫生

## 重点（本批特有）
- **诊断脚本清理评估**：heldout/_*.py 与 output/_*.py 哪些是历史残留（可删/归档）、哪些在用的——死脚本清单
- **验证脚本的可信度**：验证基建本身有没有"假验证"（断言没锁住/写回无校验）
- **scripts/build_book_index.py**：新脚本卫生（索引生成器——行号准确性依赖它）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 死脚本清单（可删/归档/在用）
4. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H7 节）
5. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API

## 汇报（300 字内）
验证基建可信度（写回原子性/假验证）+ 诊断脚本清理清单 + P0/P1/P2 统计 + 高价值亮点
