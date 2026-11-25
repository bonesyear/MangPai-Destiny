# 飞书机器人接入（mangpai/feishu）

外层应用，引擎零改动：feishu → engine/subjective 单向只消费，LLM 输出不落 compute_all dict。
**飞书仅为可选接入层**——核心流程（排盘 → 判定 → LLM 叙述）完全可脱离飞书运行，库调用方式见根目录 README「完整流程示例」节。

> **外部验收状态：永久结项（2026-11-25，用户决定）**。不再进行真实飞书调用、测试群或 webhook 验收，也不重开此项；飞书代码及现有离线测试保留，用于防止后续改动引入回归。

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `FEISHU_APP_ID` | ✅ | 自建应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 自建应用 App Secret |
| `FEISHU_VERIFICATION_TOKEN` | ✅ | 事件订阅的 Verification Token（不配则拒绝请求，启动也会报错） |
| `MANGPAI_USE_LLM` | 否 | 默认关闭；`1/true/on/yes` 显式开启（validate=mark，失败自动降级引擎直出）；通用别名优先，旧名 `FEISHU_USE_LLM` 仍兼容 |
| `FEISHU_HOST` / `FEISHU_PORT` | 否 | 默认 `127.0.0.1:9700`；对外服务须由 HTTPS 反代转发，不要直接暴露明文 HTTP |
| `FEISHU_RATE_PER_MIN` | 否 | 每个 open_id 每分钟最多处理消息数，默认 3；超限回复不含生辰的繁忙提示 |
| `FEISHU_LLM_DAILY_MAX` | 否 | 本进程每日 LLM 调用额度，默认 100；超额只返回引擎结果。重启会重置，非多实例共享限额 |
| `FEISHU_SHUTDOWN_TIMEOUT` | 否 | 停机等待已接收任务的秒数，默认 60；未开始任务取消并提示重发 |
| `MANGPAI_LLM_API_KEY` | LLM 开时必填 | 完整配置项（端点/模型/THINKING/超时等）见根目录 README「配置你自己的 LLM」节与 [`.env.example`](../../.env.example)；旧名 `DEEPSEEK_API_KEY` 仍兼容（峰谷价计价仅对 DeepSeek 有效，其他 provider 显示「未计价」） |

凭证一律走环境变量，仓库内不落地。

## 飞书开放平台配置

1. 建自建应用，开通权限：`im:message`、`im:message:send_as_bot`、读取消息事件相关权限；
2. 事件订阅 → 回调方式选 **webhook**，地址 `https://<公网域名>/feishu/callback`（POST），订阅事件 `im.message.receive_v1`；
3. 发布版本并在单聊中使用；不支持群聊，不要开通「获取群组中所有消息」类权限。

> ⛔ **红线：不要在事件订阅里配置 Encrypt Key。** 本实现不支持解密——配了之后回调体变成 `{"encrypt": …}`，所有事件被丢弃（仅日志告警），机器人完全无响应。只填 Verification Token 即可。

## 上线 checklist

1. `FEISHU_VERIFICATION_TOKEN` 必配（不配启动即报错）；
2. 事件订阅**不填 Encrypt Key**；
3. 权限 `im:message` 等已开通并发布版本；
4. 回调地址已验证通过（url_verification 挑战）；
5. 默认仅监听 `127.0.0.1`，公网入口必须经 HTTPS/TLS 反向代理转发。

（长连接模式依赖 lark-oapi SDK，本实现零新依赖选 webhook；如需免公网地址二期再评估。）

## 运行

先在 `.env` 填入真实的 `FEISHU_*` 和可选 LLM 配置，再显式导出；占位值、短于 16 位或含空白的飞书凭证会拒绝启动：

```bash
set -a; . ./.env; set +a
python3 -m mangpai.feishu.bot
```

上述命令须在仓库根目录执行；其他目录需先设置 `PYTHONPATH=<仓库根>`。systemd 示例：

```ini
[Service]
WorkingDirectory=/opt/MangPai-Destiny
Environment=PYTHONPATH=/opt/MangPai-Destiny
ExecStart=/usr/bin/python3 -m mangpai.feishu.bot
```

`FEISHU_*` 不会由飞书组件自动从 `.env` 读取，必须导出为进程环境。控制台重置 Verification Token 后也须同步更新并重启。

事件回调立即 200 ack，排盘+LLM 在后台线程算完走 reply 接口回原消息（markdown 卡片）。

SIGINT/SIGTERM 会停止接收新回调；未开始任务取消并回复「服务正在重启，请稍后重发」，不再排盘或调用 LLM。已开始任务最多等待 `FEISHU_SHUTDOWN_TIMEOUT` 秒，超时仍运行的只记日志，不另发可能重复的回复。Docker/ systemd 应配置足够的 stop 宽限期并传递信号；强杀、断电和崩溃不提供恢复保证。

## 服务参数（webhook 加固）

`ThreadingHTTPServer` 每连接一线程，配合以下常量（`bot.py` 顶部，按需改）：

| 参数 | 默认 | 说明 |
|---|---|---|
| `_MAX_WORKERS` | 32 | 后台排盘工作线程数 |
| `_sem` | 64 | 在途任务上限（含执行和排队），满员即回繁忙，不再无限入队 |
| `_MAX_BODY` | 128 KB | 回调 body 上限，超出返回 413；负数和非 identity 编码返回 400。原始字节上限不代表解析后的内存放大倍数，反代还应限制并发连接数 |
| `_READ_TIMEOUT` | 15 s | 整个请求体读取截止；请求行/头也有 15 秒超时 |

反代须终止 TLS，并限制请求体大小、读取时长和每 IP 连接数。事件去重为内存滚动窗口（上限 2000），去重、用户限流和 LLM 日额度均不跨重启或多实例共享；需要严格防重放或集群限额时换外部存储。

## 用户命令

- `阳历 2000-01-01 12:00 男 北京`（虚构示例）—— 阳历排盘（农历请自转阳历；性别必填；城市未收录可直给经度 `… 男 114.07`）
- `四柱 己卯 丙子 戊午 戊午 男 [2000]`（虚构示例）—— 四柱直排（年份可选）
- 中国大陆 1986–1991 年历史夏令时区间须在阳历命令末尾注明「夏令时」或「标准时」；未注明会追问，不自行猜测
- `/help` 用法 · `/ver` 版本基线
- 细挖 `focus=财运/婚姻` 二期预留

## 测试

在仓库根目录运行，全部使用本地 HTTP/mock，不触真实飞书或 LLM：

```bash
python3 -m pytest mangpai/tests/test_feishu.py mangpai/tests/test_feishu_security.py mangpai/tests/test_external_reliability.py -q
```
