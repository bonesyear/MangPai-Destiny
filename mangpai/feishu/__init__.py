"""飞书集成（外层应用，引擎零改动）。

    mangpai/feishu/
    ├── client.py     # 飞书 API 客户端（token 缓存/发消息/回复，stdlib urllib）
    ├── router.py     # 命令路由（自然语言排盘 + /help /ver）
    ├── service.py    # 引擎 compute_all 全链 + LLM 通道接线（失败降级引擎直出）
    ├── formatter.py  # compute_all dict → Markdown 报告模板
    └── bot.py        # webhook 事件回调（http.server）+ 后台线程回推

依赖方向：feishu → engine/subjective，单向只消费，不回写引擎 dict。
"""
from mangpai.feishu.client import FeishuClient, FeishuError
from mangpai.feishu.router import handle
from mangpai.feishu.service import paipan

__all__ = ['FeishuClient', 'FeishuError', 'handle', 'paipan']
