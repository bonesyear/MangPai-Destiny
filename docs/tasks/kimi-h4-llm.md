# Kimi 任务：代码卫生审查 H4 · LLM 通道批（llm_backend/llm_channel/llm_prompt/schools）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（七维）+ H1-H3 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×89——本批**重点查同型残留**：裸 except/循环导入/裸 index/死 shim/局部 import）+ 收工终态
2. 本批 = **代码卫生 H4 · LLM 通道批**（只审不改；纯本地零 API；本批文件少可细审）
3. 汇报 300 字内

## 审查对象（LLM 通道 5 文件 + 关联）
llm_backend.py / llm_channel.py / llm_prompt.py / schools.py（⚠️ 受保护文件——审查只评实现质量，不评数据表内容）/ narrative.py（若 H3 已读则只补查）

## 审查维度（同前七维）
1. 重复逻辑（与 subjective 层重复/模块内重复）
2. 复杂度（>80 行函数/嵌套/圈复杂度——llm_prompt 的 _key_manifest/锚定行生成、llm_channel 的校验器链）
3. 命名
4. 异常处理一致性（**裸 except/静默失败——LLM 层失败降级路径的异常面**：llm_backend 网络层重试/llm_channel 降级返回是否吞了不该吞的）
5. 死代码（_self_check 使用、历史残留校验器规则）
6. 隐藏边界假设（硬编码/魔法数字——_PRICE 价表/峰谷时段/黑名单词表）
7. import 卫生（延迟绑定/循环导入）

## 重点（LLM 层特有的）
- **降级路径完整性**：llm_channel 三条降级返回（LLM 不可用/JSON 解析失败/校验失败）是否都带免责 + 不泄漏 prompt
- **校验器规则死代码**：L0/L1/L2/N1 各规则是否有从未触发的（G 系列迭代后残留）
- **_PRICE/峰谷**：价表与时段硬编码的健康度（是否该配置化）
- **schools selectors**：保护链下新增键（dayun/qianyi/xiangmao/zinv）的读者检查

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H4 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API
- schools.py 只评实现质量不评数据表（受保护）

## 汇报（300 字内）
5 文件审查结果 + P0/P1/P2 统计 + 同型残留 + LLM 层特有发现（降级路径/死校验器规则/价表硬编码）
