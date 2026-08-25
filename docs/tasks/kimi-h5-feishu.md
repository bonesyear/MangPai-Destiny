# Kimi 任务：代码卫生审查 H5 · 飞书集成批（client/router/service/formatter/bot）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 代码卫生规划（七维）+ H1-H4 报告（`docs/tasks/codehygiene-fix-backlog.md` 已有 P0×91——本批**重点查同型残留**：裸 except/循环导入/裸 index/死 shim/局部 import）+ 收工终态
2. 本批 = **代码卫生 H5 · 飞书集成批**（只审不改；纯本地零 API；6 文件细审）
3. 汇报 300 字内

## 审查对象（mangpai/feishu/ 6 文件）
client.py / router.py / service.py / formatter.py / bot.py / README.md（README 只评文档完整性——env 清单/红线/启动步骤）

## 审查维度（同前七维）
1. 重复逻辑（formatter 与 llm_channel 的免责/文案重复？router 与 service 的解析重复？）
2. 复杂度（>80 行函数/嵌套——bot 消息处理链、router 自然语言解析）
3. 命名
4. 异常处理一致性（**裸 except/静默失败——webhook 入口的异常面**：非 dict body/畸形事件/LLM 超时/发送失败）
5. 死代码（client.send 生产零调用（V6 已备案）——复查；未用参数/分支）
6. 隐藏边界假设（硬编码——34 城市经度表？超时值？）
7. import 卫生

## 重点（飞书层特有的）
- **入口健壮性**：webhook 畸形输入 → 是否全兜住（U2 fuzz 17 例已过——复查实现有没有漏洞）
- **降级链完整性**：LLM 失败 → service 降级引擎直出（G1 后带迁移/相貌两段）——复查降级路径异常面
- **并发面**：ThreadingHTTPServer + 信号量（E5 加固）——复查线程安全
- **消息去重**：_seen_mids 滚动窗口（E5）——复查边界
- **与引擎/LLM 层的一致性**：formatter 输出与 narrative 输出是否重复造轮子（复用行函数 vs 重抄——飞书集成当时"复用 narrative 行函数零重抄"——复查）

## 产出
1. 问题表：`文件:行号 | 问题类型 | 严重级 | 描述 | 修法建议`
2. P0/P1/P2 统计
3. 追加写入 `docs/tasks/codehygiene-fix-backlog.md`（H5 节）
4. 汇报 300 字内

## 红线
- 只审不改；纯本地零 API

## 汇报（300 字内）
6 文件审查结果 + P0/P1/P2 统计 + 同型残留 + 飞书层特有发现（入口健壮性/降级链/并发/去重）
