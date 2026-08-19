# 飞书机器人接入（mangpai/feishu）

外层应用，引擎零改动：feishu → engine/subjective 单向只消费，LLM 输出不落 compute_all dict。

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `FEISHU_APP_ID` | ✅ | 自建应用 App ID |
| `FEISHU_APP_SECRET` | ✅ | 自建应用 App Secret |
| `FEISHU_VERIFICATION_TOKEN` | 建议 | 事件订阅的 Verification Token（配了就校验） |
| `FEISHU_USE_LLM` | 否 | `0` 关闭 LLM 五维段（默认开，validate=mark，失败自动降级引擎直出） |
| `FEISHU_PORT` | 否 | webhook 监听端口，默认 9700 |
| `DEEPSEEK_API_KEY` | LLM 开时必填 | 见 `docs/llm-channel-20260818.md`（谷段半价） |

凭证一律走环境变量，仓库内不落地。

## 飞书开放平台配置

1. 建自建应用，开通权限：`im:message`、`im:message:send_as_bot`、读取消息事件相关权限；
2. 事件订阅 → 回调方式选 **webhook**，地址 `https://<公网域名>/feishu/callback`（POST），订阅事件 `im.message.receive_v1`；
3. 发布版本并拉机器人进群/单聊。

（长连接模式依赖 lark-oapi SDK，本实现零新依赖选 webhook；如需免公网地址二期再评估。）

## 运行

```bash
FEISHU_APP_ID=cli_xxx FEISHU_APP_SECRET=xxx \
FEISHU_VERIFICATION_TOKEN=xxx DEEPSEEK_API_KEY=xxx \
python3 -m mangpai.feishu.bot
```

事件回调立即 200 ack，排盘+LLM 在后台线程算完走 reply 接口回原消息（markdown 卡片）。

## 用户命令

- `阳历 1992-10-09 13:58 男 河南信阳` —— 阳历排盘（农历请自转阳历；性别必填；城市未收录可直给经度 `… 男 114.07`）
- `四柱 戊辰 己未 庚午 丁亥 男 [1992]` —— 四柱直排（年份可选）
- `/help` 用法 · `/ver` 版本基线
- 细挖 `focus=财运/婚姻` 二期预留

## 测试

```bash
python3 -m pytest mangpai/tests/test_feishu.py -q   # 23 测，全 mock，不触网
```
