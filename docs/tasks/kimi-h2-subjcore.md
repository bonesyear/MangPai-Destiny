# Kimi 任务：代码卫生审查 H2 · subjective 核心批（caiming/yongshen/zhiye/xiangfa_ops 等）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（七维：重复/复杂度/命名/异常一致性/死代码/隐藏边界/import 卫生；分级 P0/P1/P2）+ H1 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 H1 的 P0×4——本批**重点查同类型残留**：裸 except/循环导入/裸 index/死 shim）+ 收工终态
2. 本批 = **代码卫生 H2 · subjective 核心批**（只审不改；纯本地零 API；≤30 文件）
3. 汇报 300 字内

## 审查对象（subjective 按行数优先，本批核心 10 文件）
caiming.py（1998 行）/ yongshen.py（1861）/ zhiye.py（1754）/ xiangfa_ops.py（1651）/ gongliang.py（1462）/ liuqin.py（1232）/ hunyin.py（1134）/ zuogong_confirm.py（1106）/ guanming.py（1085）/ laoyu.py（926）

## 审查维度（同 H1 七维）
1. 重复逻辑（跨模块/模块内——注意与 objective 层的重复：十神计算等 H1 已发现三处独立实现，检查 subjective 是否还有第四处）
2. 复杂度（>80 行函数/嵌套>4/圈复杂度）
3. 命名（与书理术语冲突/误导）
4. 异常处理一致性（**裸 except/TypeError 未捕获/静默失败——H1 P0 同型重点**）
5. 死代码（未引用函数/死参数/死分支——注意 schools selectors 保护链下的死键）
6. 隐藏边界假设（硬编码/魔法数字/隐含依赖）
7. import 卫生（延迟绑定/循环导入——H1 advanced.py 同型）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H2 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API
- 注意 subjective 是判断层（书锚铁律）——审查只评实现质量不评判定逻辑（Spec 轴不重复）

## 汇报（300 字内）
10 文件审查结果 + P0/P1/P2 统计 + 与 H1 同型残留检查（裸 except/循环导入/死 shim）+ 高价值亮点
