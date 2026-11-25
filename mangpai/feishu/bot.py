"""飞书 webhook 接入：事件回调 → 后台线程排盘 → reply API 回推。

选型：webhook（stdlib http.server，零新依赖），仅处理单聊用户消息。
长连接模式依赖 lark-oapi SDK，未安装不引入；如需免公网回调地址，二期再评估加 SDK。

飞书事件回调要求秒级 ack，排盘+LLM 可能 ~20s → 立即 200，后台线程算完
走 reply 接口回原消息。LLM 失败由 service 层降级为引擎直出，此处不感知。

上线：
  1. 飞书开放平台建自建应用，拿 app_id/app_secret；
  2. 事件订阅 → 回调地址填 https://<公网域名>/feishu/callback（webhook 方式），
     订阅事件 im.message.receive_v1，开通 im:message 相关权限；
  3. 环境变量：FEISHU_APP_ID / FEISHU_APP_SECRET（必填），
     FEISHU_VERIFICATION_TOKEN（事件订阅的 Verification Token，必填；三项凭证遇缺失、
     占位值、过短或空白均拒绝启动。切勿配置 Encrypt Key——不支持解密，事件返回400），
     MANGPAI_USE_LLM=0 可关 LLM 段（旧名 FEISHU_USE_LLM 兼容），FEISHU_PORT 默认 9700；
     默认只监听 127.0.0.1，经 HTTPS 反代对外；FEISHU_HOST 可改监听地址，
     FEISHU_RATE_PER_MIN=3、FEISHU_LLM_DAILY_MAX=100 限制费用与刷屏；
  4. python3 -m mangpai.feishu.bot
"""
from __future__ import annotations

import hmac
import json
import logging
import math
import os
import re
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, wait
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mangpai.feishu.client import FeishuClient, FeishuError
from mangpai.feishu.router import handle as route
from mangpai.engine import EngineComputeError
from mangpai.subjective.utils import exception_log_detail

log = logging.getLogger(__name__)

_seen_mids = {}  # shortcut: 去重仅进程内，需跨重启防重放时换持久化存储
_seen_lock = threading.Lock()
_SEEN_MAX = 2000
_rate_events = {}
_llm_calls = {'day': '', 'count': 0}
_rate_lock = threading.Lock()
_log_events = {}
_jobs = {}
_jobs_lock = threading.Lock()
_stopping = threading.Event()
_client = None


def _log_limited(key, message):
    now = time.monotonic()
    with _rate_lock:
        count, last = _log_events.get(key, (0, None))
        count += 1
        if last is not None and now - last < 600:
            _log_events[key] = (count, last)
            return
        _log_events[key] = (0, now)
    log.warning('%s（累计%d次）', message, count)


def _forget_event(event_key):
    with _seen_lock:
        _seen_mids.pop(event_key, None)


def _get_client():
    global _client
    if _client is None:
        _client = FeishuClient()
    return _client


def _check_token(token):
    want = os.environ.get('FEISHU_VERIFICATION_TOKEN', '').strip()
    if not want or not hmac.compare_digest(str(token or ''), want):
        raise PermissionError('verification token 缺失或不匹配')


def _rate_allowed(sender: str) -> bool:
    limit = int(os.environ.get('FEISHU_RATE_PER_MIN', '3'))
    now = time.monotonic()
    with _rate_lock:
        events = [t for t in _rate_events.get(sender, []) if now - t < 60]
        if len(events) >= limit:
            _rate_events[sender] = events
            return False
        events.append(now)
        _rate_events[sender] = events
        return True


def _llm_allowed() -> bool:
    from mangpai.feishu.service import use_llm_default
    if not use_llm_default():
        return False
    today = time.strftime('%Y-%m-%d')
    limit = int(os.environ.get('FEISHU_LLM_DAILY_MAX', '100'))
    with _rate_lock:
        if _llm_calls.get('day') != today:
            _llm_calls.update(day=today, count=0)
        if _llm_calls['count'] >= limit:
            return False
        _llm_calls['count'] += 1
        return True


def _respond(client, message_id, text, use_llm=None):
    try:
        reply = route(text) if use_llm is None else route(text, use_llm=use_llm)
    except Exception as e:  # 边界兜底：引擎/网络异常也要回用户一句；日志只记类型，脱敏
        if isinstance(e, EngineComputeError):
            detail = f'{e.key}/{exception_log_detail(e.orig)}'
        else:
            detail = exception_log_detail(e)
        log.error('排盘异常 mid=%s: %s', message_id, detail)
        reply = '排盘失败：内部错误，请稍后重试'
    try:
        client.reply(message_id, 'interactive', reply)
    except FeishuError as e:  # 仅明确 API 拒绝才兜底；网络结果未知不重发，防重复回复
        log.error('reply 发送失败 mid=%s: %s', message_id, type(e).__name__)
        try:
            client.reply(message_id, 'text', reply)
        except Exception as e2:
            log.error('reply 兜底也失败 mid=%s: %s', message_id, type(e2).__name__)
    except Exception as e:
        log.error('reply 发送失败 mid=%s: %s', message_id, type(e).__name__)


def _respond_managed(client, message_id, text, use_llm=None):
    try:
        if _stopping.is_set():
            try:
                client.reply(message_id, 'text', '服务正在重启，请稍后重发')
            except Exception as e:
                log.warning('停机提示发送失败 mid=%s: %s', message_id, type(e).__name__)
            return
        _respond(client, message_id, text, use_llm=use_llm)
    finally:
        with _jobs_lock:
            _jobs.pop(message_id, None)
        _sem.release()


def handle_event(body: dict, client=None, background=True) -> dict:
    """飞书事件回调入口（可注入 client/background=False 供测试）。"""
    if not isinstance(body, dict):
        raise ValueError('回调体须为 JSON 对象')
    if 'encrypt' in body:
        _log_limited('encrypt', '回调体已加密：请勿配置 Encrypt Key，事件已拒绝')
        raise ValueError('不支持加密回调')
    if body.get('type') == 'url_verification':
        _check_token(body.get('token'))
        return {'challenge': body.get('challenge')}
    header = body.get('header') or {}
    _check_token(header.get('token') or body.get('token'))
    try:
        created = float(header.get('create_time', ''))
    except (TypeError, ValueError):
        return {}
    if created > 10_000_000_000:
        created /= 1000
    if not math.isfinite(created) or abs(time.time() - created) > 300:
        return {}
    event = body.get('event') or {}
    msg = event.get('message') or {}
    if msg.get('chat_type') != 'p2p':
        return {}
    sender = event.get('sender') or {}
    if sender.get('sender_type') != 'user':
        return {}
    mid = msg.get('message_id') or ''
    if not re.fullmatch(r'om_[0-9A-Za-z_-]+', mid):
        return {}
    event_key = header.get('event_id') or mid
    with _seen_lock:
        if event_key in _seen_mids:
            return {}
        _seen_mids[event_key] = None
        while len(_seen_mids) > _SEEN_MAX:
            _seen_mids.pop(next(iter(_seen_mids)))
    if (msg.get('message_type') or msg.get('msg_type')) != 'text':
        return {}
    try:
        text = json.loads(msg.get('content') or '{}').get('text', '')
    except json.JSONDecodeError:
        return {}
    try:
        client = client or _get_client()
    except Exception:
        _forget_event(event_key)
        raise
    if background:
        sender_id = str((sender.get('sender_id') or {}).get('open_id') or 'unknown')
        if not _rate_allowed(sender_id):
            client.reply(mid, 'text', '当前请求较多，繁忙，请稍后再试')
            return {}
        if not _sem.acquire(False):
            client.reply(mid, 'text', '当前请求较多，繁忙，请稍后再试')
            return {}
        try:
            with _jobs_lock:
                future = _executor.submit(_respond_managed, client, mid, text, _llm_allowed())
                _jobs[mid] = (client, future)
        except Exception:
            with _jobs_lock:
                _jobs.pop(mid, None)
            _sem.release()
            _forget_event(event_key)
            raise
    else:
        _respond(client, mid, text, use_llm=_llm_allowed())
    return {}


_MAX_WORKERS = 32
_MAX_BODY = 131_072     # 回调 body 上限 128KB，超出 413
_READ_TIMEOUT = 15.0    # 整个请求体读取截止（秒）
_sem = threading.BoundedSemaphore(64)  # 最多64个在途任务；入队前非阻塞拒绝
_executor = ThreadPoolExecutor(max_workers=_MAX_WORKERS)


def _drain_jobs():
    _stopping.set()
    with _jobs_lock:
        jobs = list(_jobs.items())
    try:
        timeout = float(os.environ.get('FEISHU_SHUTDOWN_TIMEOUT', '60'))
    except ValueError:
        timeout = 60.0
    if not math.isfinite(timeout) or timeout < 0:
        timeout = 60.0
    if jobs:
        _, pending = wait([future for _mid, (_client, future) in jobs], timeout=timeout)
    else:
        pending = set()
    _executor.shutdown(wait=False, cancel_futures=True)
    for mid, (client, future) in jobs:
        if future not in pending or future.done() and not future.cancelled():
            continue
        if future.cancelled():
            try:
                client.reply(mid, 'text', '服务正在重启，请稍后重发')
            except Exception as e:
                log.warning('停机提示发送失败 mid=%s: %s', mid, type(e).__name__)
            with _jobs_lock:
                _jobs.pop(mid, None)
            _sem.release()
        else:
            # shortcut: 不强杀执行中线程，避免重复回复；需硬停时用进程级隔离
            log.warning('停机宽限期结束，任务仍在执行 mid=%s', mid)


class _Handler(BaseHTTPRequestHandler):
    timeout = 15  # 请求行/头阶段也有超时，空闲连接不能长期占线程

    def do_POST(self):
        self.request.settimeout(_READ_TIMEOUT)
        try:
            if (self.headers.get('Transfer-Encoding') or '').strip().lower() not in ('', 'identity'):
                raise ValueError('unsupported transfer encoding')
            n = int(self.headers.get('Content-Length') or 0)
            if n < 0:
                raise ValueError('negative content length')
            if n > _MAX_BODY:
                code, data = 413, b'{"error":"body too large"}'
                self.send_response(code)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(data)
                return
            deadline = time.monotonic() + _READ_TIMEOUT
            chunks = []
            remaining = n
            while remaining:
                left = deadline - time.monotonic()
                if left <= 0:
                    raise TimeoutError('body read deadline exceeded')
                self.request.settimeout(max(0.1, left))
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            if remaining:
                raise ValueError('incomplete body')
            raw = b''.join(chunks) or b'{}'
            if raw.lstrip()[:1] != b'{':
                raise ValueError('callback body must be a JSON object')
            body = json.loads(raw)
            resp = handle_event(body)
            code, data = 200, json.dumps(resp).encode('utf-8')
        except PermissionError as e:
            _log_limited('auth:' + self.client_address[0],
                         '回调鉴权失败：请检查 Verification Token 是否已同步')
            code, data = 401, str(e).encode('utf-8')
        except (ValueError, TimeoutError, json.JSONDecodeError):
            code, data = 400, b'{"error":"bad request"}'
        except Exception as e:
            log.error('回调处理异常: %s', type(e).__name__)
            code, data = 500, b'{"error":"internal error"}'
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(data)

    def log_error(self, fmt, *args):
        _log_limited('protocol:' + self.client_address[0], 'HTTP 协议或请求错误')

    def log_message(self, *a):  # 正常访问静默；错误由 log_error 限频记录
        pass


def _validate_startup():
    for name in ('FEISHU_VERIFICATION_TOKEN', 'FEISHU_APP_ID', 'FEISHU_APP_SECRET'):
        value = os.environ.get(name, '').strip()
        lower = value.lower()
        if not value:
            raise RuntimeError(f'{name} 未配置；须作为进程环境变量提供')
        if len(value) < 16 or any(c.isspace() for c in value) \
                or lower.startswith(('your-', 'sk-fake', 'sk-test', 'sk-file')) \
                or lower in ('xxx', '<redacted>') or set(value) == {'*'}:
            raise RuntimeError(f'{name} 为过短、空白或公开占位值，请换成真实配置')
    _get_client()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s')
    _validate_startup()
    port = int(os.environ.get('FEISHU_PORT', '9700'))
    host = os.environ.get('FEISHU_HOST', '127.0.0.1')
    server = ThreadingHTTPServer((host, port), _Handler)

    def stop(signum, _frame):
        log.warning('收到停机信号 %s，停止接收新回调', signum)
        _stopping.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, stop)
    try:
        server.serve_forever()
    finally:
        _stopping.set()
        server.server_close()
        _drain_jobs()


if __name__ == '__main__':
    main()
