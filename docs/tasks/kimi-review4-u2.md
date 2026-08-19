# Kimi 任务：第四轮审查 U2 · 飞书包审查（API 契约 + 并发场景 + router fuzz）

## ⚠️ 执行指引
1. **先读** `/root/metaphysics/docs/knowledge-base.md` + 第四轮方案（U2 定位：逐 API 对照官方文档 + 并发四类场景 + router fuzz）+ `mangpai/feishu/` 全部代码（client/router/service/formatter/bot）+ `mangpai/feishu/README.md`
2. **独立判断纪律**：以飞书官方开放平台文档 + 代码实际行为为准
3. 本批 = **U2 飞书包审查**（只审不改；本地 mock 验证，不连真实飞书、不调 DeepSeek）
4. 汇报 300 字内

## 任务
1. **API 契约对照**（逐 API 对官方文档）：
   - tenant_access_token 获取（endpoint/参数/缓存/过期处理）
   - 消息发送（text/post/markdown 格式契约；回复 vs 主动消息区别）
   - webhook 事件接收（事件订阅/加密/验签）
   - 逐项：实现 vs 官方文档 → 偏差清单（含严重性）
2. **并发四类场景**（mock 验证）：
   - 消息重放/重复消息（bot.py 去重是否真的防住）
   - token 过期并发刷新（多个请求同时发现过期 → 是否重复刷新/竞态）
   - LLM 超时/失败并发（多个请求同时触发降级 → 降级链是否正确）
   - 长文本/畸形输入（router fuzz：乱码/超长/边界）
3. **router fuzz**：解析函数（parse_solar/parse_pillars）fuzz 100+ 随机输入 → 崩溃/异常/静默错解
4. **安全面**：token 校验、消息注入（LLM prompt injection 面）、异常处理（是否吞错）
5. 发现分级：P0（token 过期无刷新/重放未防/降级失效=阻塞上线）/P1/P2

## 红线
- 只审不改（修批 E 另排）
- 不连真实飞书（mock）；不调真实 DeepSeek（LLM mock）

## 产出
1. API 契约对照表（实现 vs 官方 → 偏差/严重性）
2. 并发四场景测试结果（复现路径）
3. router fuzz 报告（N 例/崩溃/异常/静默错解）
4. P0/P1/P2 清单
5. 汇报 300 字内
