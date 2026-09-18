# 飞书机器人接入（mangpai/feishu）

外层应用，引擎零改动：feishu → engine/subjective 单向只消费，LLM 输出不落 compute_all dict。
**飞书仅为可选接入层**——核心流程（排盘 → 判定 → LLM 叙述）完全可脱离飞书运行，库调用方式见根目录 README「完整流程示例」节。

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `FEISHU_APP_ID` | ✅ | 自建应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 自建应用 App Secret |
| `FEISHU_VERIFICATION_TOKEN` | ✅ | 事件订阅的 Verification Token（不配则启动即报错，零校验可被伪造事件白嫖） |
| `MANGPAI_USE_LLM` | 否 | `0` 关闭 LLM 七维段（默认开，validate=mark，失败自动降级引擎直出）；通用别名优先，旧名 `FEISHU_USE_LLM` 仍兼容 |
| `FEISHU_PORT` | 否 | webhook 监听端口，默认 9700 |
| `MANGPAI_LLM_API_KEY` | LLM 开时必填 | 完整配置项（端点/模型/THINKING/超时等）见根目录 README「配置你自己的 LLM」节与 [`.env.example`](../../.env.example)；旧名 `DEEPSEEK_API_KEY` 仍兼容（峰谷价计价仅对 DeepSeek 有效，其他 provider 显示「未计价」） |

凭证一律走环境变量，仓库内不落地。

## 飞书开放平台配置

1. 建自建应用，开通权限：`im:message`、`im:message:send_as_bot`、读取消息事件相关权限；
2. 事件订阅 → 回调方式选 **webhook**，地址 `https://<公网域名>/feishu/callback`（POST），订阅事件 `im.message.receive_v1`；
3. 发布版本并拉机器人进群/单聊。

> ⛔ **红线：不要在事件订阅里配置 Encrypt Key。** 本实现不支持解密——配了之后回调体变成 `{"encrypt": …}`，所有事件被丢弃（仅日志告警），机器人完全无响应。只填 Verification Token 即可。

## 上线 checklist

1. `FEISHU_VERIFICATION_TOKEN` 必配（不配启动即报错）；
2. 事件订阅**不填 Encrypt Key**；
3. 权限 `im:message` 等已开通并发布版本；
4. 回调地址已验证通过（url_verification 挑战）。

（长连接模式依赖 lark-oapi SDK，本实现零新依赖选 webhook；如需免公网地址二期再评估。）

## 运行

```bash
FEISHU_APP_ID=cli_xxx FEISHU_APP_SECRET=xxx \
FEISHU_VERIFICATION_TOKEN=xxx MANGPAI_LLM_API_KEY=your-api-key \
python3 -m mangpai.feishu.bot
```

事件回调立即 200 ack，排盘+LLM 在后台线程算完走 reply 接口回原消息（markdown 卡片）。

## 服务参数（webhook 加固，修批 E5）

`ThreadingHTTPServer` 每连接一线程，配合以下常量（`bot.py` 顶部，按需改）：

| 参数 | 默认 | 说明 |
|---|---|---|
| `_MAX_WORKERS` | 32 | 并发回调上限，超出排队（慢连接不再阻塞全部回调） |
| `_MAX_BODY` | 1 MB | 回调 body 上限，超出返回 413 |
| `_READ_TIMEOUT` | 15 s | 单连接读超时 |

量级上来建议前置反代（nginx）限流；重放去重为内存滚动窗口（上限 2000，超了滚出最老不整窗清空），重启即清，量级上来换外部存储。

## 用户命令

- `阳历 1992-10-09 13:58 男 河南信阳` —— 阳历排盘（农历请自转阳历；性别必填；城市未收录可直给经度 `… 男 114.07`）
- `四柱 戊辰 己未 庚午 丁亥 男 [1992]` —— 四柱直排（年份可选）
- `/help` 用法 · `/ver` 版本基线
- 细挖 `focus=财运/婚姻` 二期预留

## 测试

```bash
python3 -m pytest mangpai/tests/test_feishu.py -q   # 34 测，全 mock，不触网
```
