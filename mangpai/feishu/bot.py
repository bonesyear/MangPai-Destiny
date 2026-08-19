"""飞书 webhook 接入：事件回调 → 后台线程排盘 → reply API 回推。

选型：webhook（stdlib http.server，零新依赖）。长连接模式依赖 lark-oapi SDK，
未安装不引入；如需免公网回调地址，二期再评估加 SDK。

飞书事件回调要求秒级 ack，排盘+LLM 可能 ~20s → 立即 200，后台线程算完
走 reply 接口回原消息。LLM 失败由 service 层降级为引擎直出，此处不感知。

上线：
  1. 飞书开放平台建自建应用，拿 app_id/app_secret；
  2. 事件订阅 → 回调地址填 https://<公网域名>/feishu/callback（webhook 方式），
     订阅事件 im.message.receive_v1，开通 im:message 相关权限；
  3. 环境变量：FEISHU_APP_ID / FEISHU_APP_SECRET（必填），
     FEISHU_VERIFICATION_TOKEN（事件订阅的 Verification Token，必填，不配启动即报错；
     切勿配置 Encrypt Key——不支持解密，配了事件全丢），
     FEISHU_USE_LLM=0 可关 LLM 段，FEISHU_PORT 默认 9700；
  4. python3 -m mangpai.feishu.bot
"""
from __future__ import annotations

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from mangpai.feishu.client import FeishuClient
from mangpai.feishu.router import handle as route

log = logging.getLogger(__name__)

_seen_mids = set()  # ponytail: 内存去重有界 2000，重启即清；量级上来换外部存储
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = FeishuClient()
    return _client


def _check_token(token):
    want = os.environ.get('FEISHU_VERIFICATION_TOKEN', '').strip()
    if want and token != want:
        raise PermissionError('verification token 不匹配')


def _respond(client, message_id, text):
    try:
        reply = route(text)
    except Exception as e:  # 边界兜底：引擎/网络异常也要回用户一句
        reply = f'排盘失败：{e}'
    try:
        client.reply(message_id, 'interactive', reply)
    except Exception as e:  # reply 失败不能静默死线程：记日志 + 尽力纯文本兜底
        log.error('reply 发送失败 mid=%s: %s', message_id, e)
        try:
            client.reply(message_id, 'text', reply)
        except Exception as e2:
            log.error('reply 兜底也失败 mid=%s: %s', message_id, e2)


def handle_event(body: dict, client=None, background=True) -> dict:
    """飞书事件回调入口（可注入 client/background=False 供测试）。"""
    if 'encrypt' in body:  # 控制台误配 Encrypt Key：本实现不支持解密，告警丢弃
        log.error('回调体已加密：请勿在飞书控制台配置 Encrypt Key（本实现不支持解密），事件已丢弃')
        return {}
    if body.get('type') == 'url_verification':  # 回调地址配置时的挑战
        _check_token(body.get('token'))
        return {'challenge': body.get('challenge')}
    header = body.get('header') or {}
    _check_token(header.get('token') or body.get('token'))
    msg = (body.get('event') or {}).get('message') or {}
    mid = msg.get('message_id')
    if not mid or mid in _seen_mids:
        return {}
    if len(_seen_mids) > 2000:
        _seen_mids.clear()
    _seen_mids.add(mid)
    if (msg.get('message_type') or msg.get('msg_type')) == 'text':
        try:
            text = json.loads(msg.get('content') or '{}').get('text', '')
        except json.JSONDecodeError:
            return {}
        client = client or _get_client()
        if background:
            threading.Thread(target=_respond, args=(client, mid, text), daemon=True).start()
        else:
            _respond(client, mid, text)
    return {}


class _Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            n = int(self.headers.get('Content-Length') or 0)
            body = json.loads(self.rfile.read(n) or b'{}')
            resp = handle_event(body)
            code, data = 200, json.dumps(resp).encode('utf-8')
        except PermissionError as e:
            code, data = 401, str(e).encode('utf-8')
        except Exception as e:  # 回调必须尽量 200 之外的明确错误也要返回，避免飞书重试风暴
            code, data = 500, str(e).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):  # 静默
        pass


def main():
    if not os.environ.get('FEISHU_VERIFICATION_TOKEN', '').strip():
        raise RuntimeError('FEISHU_VERIFICATION_TOKEN 未配置：不配则回调零校验可被伪造事件白嫖，上线必配')
    port = int(os.environ.get('FEISHU_PORT', '9700'))
    HTTPServer(('0.0.0.0', port), _Handler).serve_forever()


if __name__ == '__main__':
    main()
