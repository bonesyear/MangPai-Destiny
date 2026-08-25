# Kimi 任务：代码卫生审查 H3 · subjective 辅助批（yunfan/zaihuo/zeishen_bushen/yingqi_subj 等）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（七维：重复/复杂度/命名/异常一致性/死代码/隐藏边界/import 卫生）+ H1/H2 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×72——本批**重点查同型残留**：裸 except/循环导入/裸 index/死 shim）+ 收工终态
2. 本批 = **代码卫生 H3 · subjective 辅助批**（只审不改；纯本地零 API；≤30 文件）
3. 汇报 300 字内

## 审查对象（subjective 剩余判断模块，本批 11 文件）
yunfan.py（891 行）/ zaihuo.py / zeishen_bushen.py / yingqi_subj.py / xueli.py / shipaige.py / gongmen_wuzhi.py / juefa.py / chuangong.py / zhengfan.py / narrative.py（LLM 叙述留 LLM 通道批——若本批文件数超预算可顺延 narrative）

## 审查维度（同 H1/H2 七维）
1. 重复逻辑（跨模块/模块内——**重点：十神计算第 N 处实现**（H2 发现主观层 8 处，查辅助批还有没有）、_ensure_* 重复族）
2. 复杂度（>80 行函数/嵌套>4/圈复杂度）
3. 命名（与书理术语冲突/误导）
4. 异常处理一致性（**裸 except/TypeError 未捕获/静默失败——H1/H2 P0 同型重点**）
5. 死代码（未引用函数/死参数/死分支）
6. 隐藏边界假设（硬编码/魔法数字/隐含依赖）
7. import 卫生（延迟绑定/循环导入——H1 advanced.py / H2 gongliang↔caiming 同型）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H3 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API
- subjective 判断层——审查只评实现质量不评判定逻辑（Spec 轴不重复）

## 汇报（300 字内）
11 文件审查结果 + P0/P1/P2 统计 + 与 H1/H2 同型残留检查（裸 except/循环导入/死 shim/十神第 N 处）+ 高价值亮点
