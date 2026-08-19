# 第四轮审查 U2 · 飞书包审查报告（2026-08-19）

对象：`mangpai/feishu/`（client/router/service/formatter/bot，754 行）。只审不改；全 mock，不触真实飞书/DeepSeek。
验证脚本（一次性，不入库）：`/tmp/feishu_audit/concurrency.py`、`/tmp/feishu_audit/fuzz_router.py`。
官方文档页面 JS 渲染无法抓取正文，契约对照以飞书开放平台公开稳定 API 规范为准（端点/字段均为长期未变契约）。

## 1. API 契约对照表

| API | 官方契约 | 实现 | 偏差 / 严重性 |
|---|---|---|---|
| tenant_access_token | POST `/open-apis/auth/v3/tenant_access_token/internal`，body `{app_id, app_secret}`，resp `{code, tenant_access_token, expire≤7200s}` | client.py:43 完全一致；进程内缓存+提前 60s 刷新 | ①服务端提前作废（code 99991663/99991661）无「刷新+重试一次」，缓存期内全失败（P1-1）②刷新无锁，并发重复刷新（P2-2） |
| 发送消息 | POST `/im/v1/messages?receive_id_type=…`，body `{receive_id, msg_type, content(JSON 字符串)}` | client.py:72 一致 | receive_id_type 硬编码 chat_id（open_id 私聊场景不支持，README 未注明）——记录 |
| 回复消息 | POST `/im/v1/messages/{message_id}/reply`，body `{content, msg_type}` | client.py:78 一致 | 无 |
| content 格式 | text=`{"text":…}`；post=`{"zh_cn":{title,content:[[{tag,text}]]}}`；interactive=卡片 JSON | build_content 三型结构正确 | 卡片用 legacy 格式（config/elements/lark_md），非官方主推 card JSON 2.0——当前可用，记录（P2） |
| url_verification | 回显 challenge，校验 token | bot.py:55-57 正确 | token 未配时零校验（README 标「建议」）（P2-4） |
| 事件接收 schema 2.0 | `header.token` 校验；官方建议按 `header.event_id` 去重；**若控制台配 Encrypt Key，回调体变为 `{"encrypt":…}` 须 AES 解密** | header.token 校验正确；按 message_id 去重（对本事件类型等效） | **Encrypt Key 完全不支持且 README 未警示**：配了则 VT 已配→401 全拒、未配→静默丢弃（P1-3） |
| 回调 ack | 秒级 ack，非 2xx 会触发飞书重试 | 立即 200 + 后台线程 ✅；重试同 mid 被去重 ✅ | 500 响应回显 `str(e)` 内部错误（P2-5）；单线程 HTTPServer + 无 body 上限/读超时，慢连接可阻塞全部回调（P2-6） |

## 2. 并发四场景（mock 实测）

- **重放/重复消息**：①同 mid 顺序重放→去重有效（既有测试覆盖）；②`_seen_mids >2000` 全清后重放最早消息→**再次处理**（已复现：塞 2001 条后重放 om_victim 多出 1 条回复；代码 ponytail 注释已自知）→P2-1；③同 mid 双线程并发 check-then-add 竞态 200 轮未复现（GIL+窗口极窄，且生产路径 main() 用单线程 HTTPServer 串行回调）→记录不升级。
- **token 过期并发刷新**：8 线程同时发现过期→**实际刷新 8 次**（理想 1 次），无锁竞态成立；功能后果=多余请求/限流面（飞书新旧 token 在各自 expire 内共存有效），无错误结果→P2-2。**服务端作废场景**：mock 返回 99991663→send 直接抛 FeishuError，无自动刷新重试，缓存期内（最长至本地 expire）全部发送失败→P1-1。
- **LLM 超时/失败并发降级**：mock `call_deepseek` 抛 LLMBackendError，8 线程并发 paipan→**8/8 正确降级**引擎直出、0 异常（llm_backend 把网络/超时/结构异常全包成 LLMBackendError，降级链完整）✅。**但最后一环断裂**：bot.py:50 `client.reply` 在 try 外，reply 失败时后台线程静默死亡，用户连「排盘失败」都收不到（已复现）→P1-2。
- **长文本/畸形输入**：10 万字符数字串走完整 webhook 路径→正常 ack、正常回「输入有误」，无卡顿无崩溃 ✅。

## 3. router fuzz 报告

200 例随机输入（unicode 垃圾/数字汤/干支汤/噪声骨架/超长）×2 解析函数 = 400 次调用 + 32 条定向边界用例全链 + 40 条解析成功者抽样过引擎：

- **崩溃 0、未预期异常 0、超时/ReDoS 0**；ParseError=176，其余正常返回。
- 越界值全部安全报错：month 0/13、day 0/32、2/30、hour 24/25、minute 60/99、year 1899/2101、lon ±200/999.99 → 引擎/handled 统一「输入有误」✅。
- **静默错解 3 类（P2-3）**：①`'123:45'`→hour=23 静默出报告（`\d{1,2}` 从第 2 位起匹配）；②`'13:58:59'`→秒位静默丢弃；③文本同时含「四柱」和阳历数据→静默走四柱路径丢弃阳历（`'阳历 … 女 北京 四柱 戊辰…'`→按四柱出盘）。
- 可用性瑕疵（P2）：性别粘连无空格（`男河南信阳`）报「性别必填」——安全失败但提示误导；pillars 路径非 19xx/20xx 年份静默忽略（按 2000 锚流年）。

## 4. 安全面

- token 校验：位置正确（url_verification 与 header.token 双查）；`!=` 非常量时间比较（本地风险极低，记录）；**FEISHU_VERIFICATION_TOKEN 未配则零校验**，伪造事件可白嫖排盘+LLM 成本——建议上线强制（P2-4）。
- prompt injection 面：**小**——用户原文不进 LLM prompt（paipan 不传 user_question），仅引擎特征入 prompt；LLM 输出经 validate=mark 后以 lark_md 渲染，附注需人工复核（已知通道纪律）。
- 异常处理：llm_backend 全包 LLMBackendError ✅；llm_channel 降级不抛错 ✅；`_respond` route 兜底 ✅、**reply 无兜底**（P1-2）；do_POST 500 回显内部错误（P2-5）。
- 凭证：环境变量读取、仓库零落地 ✅。

## 5. 分级清单

**P0（阻塞上线）：无。** 任务书三类 P0 判据逐项复核：本地过期有刷新 ✅（P0 仅指「无刷新」）、重放主路径有去重 ✅、降级链 8/8 有效 ✅。

- **P1-1** token 服务端提前作废（99991663/99991661）无「刷新+重试一次」，缓存期内消息全失败。修批 E：`_api` 捕获该 code 清缓存重试一次。
- **P1-2** bot.py:50 `client.reply` 在 try 外，发送失败用户零反馈。修批 E：reply 包 try，失败至少留日志。
- **P1-3** Encrypt Key 未支持且 README 未警示，控制台误配即全断。修批 E：README 红线注明「不要配置 Encrypt Key」或支持解密。
- **P2-1** `_seen_mids` 超 2000 全清重放窗口重开（注释已自知，量级上来换外部存储/滑动窗口）。
- **P2-2** token 刷新无锁，并发重复刷新（实测 8/8）。加 threading.Lock 即可。
- **P2-3** 静默错解：`'123:45'`→23:45、秒位丢弃、「四柱」触发词抢占阳历输入。router 加边界断言/优先级说明。
- **P2-4** verification token 未配=零校验；建议上线强制 + hmac.compare_digest。
- **P2-5** 500 响应回显 `str(e)` 内部信息。
- **P2-6** 单线程 HTTPServer 无 body 上限/读超时，慢连接阻塞全部回调（生产前置反代可缓解）。
- 记录项：legacy 卡片格式（非 card JSON 2.0）、receive_id_type 硬编码 chat_id、去重键用 message_id（本事件类型等效 event_id）。
