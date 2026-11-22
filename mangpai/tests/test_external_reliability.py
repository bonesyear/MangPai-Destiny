# -*- coding: utf-8 -*-
"""批次15：外部服务可靠性，全部使用本地 HTTP 或 mock。"""
import http.client
import io
import json
import logging
import signal
import threading
import time
import urllib.error
import urllib.request

import pytest

from mangpai.feishu import bot
from mangpai.feishu.client import FeishuClient
from mangpai.feishu import service
from mangpai.subjective import llm_backend as lb
from mangpai.subjective import llm_channel as lc
from mangpai.subjective import narrative


class _Response:
    def __init__(self, body):
        self.body = body if isinstance(body, bytes) else json.dumps(body).encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, n=-1):
        return self.body if n is None or n < 0 else self.body[:n]


@pytest.fixture(autouse=True)
def _clean_external_env(monkeypatch, tmp_path):
    for name in ('MANGPAI_LLM_BASE_URL', 'MANGPAI_LLM_TIMEOUT', 'MANGPAI_LLM_RETRIES',
                 'MANGPAI_LLM_MAX_TOKENS', 'MANGPAI_LLM_CONTEXT', 'MANGPAI_LLM_ENV_FILE'):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv('MANGPAI_USE_LLM', '1')
    monkeypatch.setenv('MANGPAI_LLM_API_KEY', 'sk-file')
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'want')
    monkeypatch.setattr(lb, '_PROJECT_ENV_FILE', tmp_path / 'missing.env')
    monkeypatch.setattr(bot, '_stopping', threading.Event(), raising=False)
    monkeypatch.setattr(bot, '_log_events', {}, raising=False)
    monkeypatch.setattr(bot, '_jobs', {}, raising=False)
    bot._seen_mids.clear()
    bot._rate_events.clear()
    bot._llm_calls.clear()


def _llm_response(raw):
    return {'text': raw, 'usage': {}, 'cost_cny': None,
            'price_tier': 'offpeak', 'elapsed_s': 0.0, 'model': 'mock'}


def _reading(conclusion='平稳', basis=None):
    return {d: {'conclusion': conclusion, 'basis': basis or [], 'confidence': '低'}
            for d in lc.DIMENSIONS}


def _event(token='wrong'):
    return {'header': {'token': token, 'event_id': 'evt-reliability',
                       'create_time': str(int(time.time() * 1000))},
            'event': {'sender': {'sender_type': 'user', 'sender_id': {'open_id': 'u1'}},
                      'message': {'message_id': 'om_reliability', 'message_type': 'text',
                                  'chat_type': 'p2p', 'content': '{"text":"/help"}'}}}


def _post(server, body):
    conn = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=2)
    try:
        conn.request('POST', '/feishu/callback', json.dumps(body).encode(),
                     {'Content-Type': 'application/json'})
        resp = conn.getresponse()
        resp.read()
        return resp.status
    finally:
        conn.close()


def test_env_utf8_bom_key_is_read(tmp_path, monkeypatch):
    path = tmp_path / 'bom.env'
    path.write_text('MANGPAI_LLM_API_KEY=sk-file\n', encoding='utf-8-sig')
    monkeypatch.setenv('MANGPAI_LLM_ENV_FILE', str(path))
    monkeypatch.delenv('MANGPAI_LLM_API_KEY')
    assert lb._load_api_key() == 'sk-file'


def test_env_bad_encoding_falls_back_without_leaking_error(tmp_path, monkeypatch, caplog):
    path = tmp_path / 'gbk.env'
    path.write_bytes('# 中文注释\n'.encode('gbk'))
    monkeypatch.setenv('MANGPAI_LLM_ENV_FILE', str(path))
    assert lb._env_value('MISSING', 'fallback') == 'fallback'
    assert 'UnicodeError' not in caplog.text


def test_max_tokens_and_context_limit(monkeypatch):
    monkeypatch.setenv('MANGPAI_LLM_MAX_TOKENS', '2048')
    seen = []
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda req, timeout=None: seen.append(req) or _Response({
                            'choices': [{'message': {'content': '{}'}}], 'usage': {}}))
    lb.call_deepseek('S', 'U')
    assert json.loads(seen[0].data)['max_tokens'] == 2048
    monkeypatch.setenv('MANGPAI_LLM_CONTEXT', '16')
    with pytest.raises(lb.LLMBackendError, match='上下文不足'):
        lb.call_deepseek('S', 'U')
    assert len(seen) == 1


@pytest.mark.parametrize('host', ['localhost', '127.0.0.1', '192.168.1.50'])
def test_local_and_private_endpoints_bypass_proxy(host, monkeypatch):
    monkeypatch.setenv('MANGPAI_LLM_BASE_URL', f'http://{host}:8000/v1/chat/completions')
    calls = []

    class Opener:
        def open(self, req, timeout=None):
            calls.append((req, timeout))
            return _Response({'choices': [{'message': {'content': '{}'}}], 'usage': {}})

    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: Opener())
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda *a, **kw: (_ for _ in ()).throw(AssertionError('走了系统代理')))
    lb.call_deepseek('S', 'U')
    assert len(calls) == 1


@pytest.mark.parametrize('name,value', [
    ('MANGPAI_LLM_TIMEOUT', 'inf'), ('MANGPAI_LLM_TIMEOUT', 'nan'),
    ('MANGPAI_LLM_TIMEOUT', '-1'), ('MANGPAI_LLM_RETRIES', '-1'),
    ('MANGPAI_LLM_RETRIES', '99'),
])
def test_invalid_timeout_and_retries_use_safe_default(name, value, monkeypatch):
    monkeypatch.setenv(name, value)
    calls = []
    if name == 'MANGPAI_LLM_RETRIES':
        monkeypatch.setattr(lb.time, 'sleep', lambda seconds: None)

        def fail(req, timeout=None):
            calls.append(timeout)
            raise urllib.error.HTTPError(req.full_url, 500, 'mock', {}, None)
        monkeypatch.setattr(urllib.request, 'urlopen', fail)
        with pytest.raises(lb.LLMBackendError, match='HTTP 500'):
            lb.call_deepseek('S', 'U')
        assert len(calls) == 3
    else:
        monkeypatch.setattr(urllib.request, 'urlopen',
                            lambda req, timeout=None: calls.append(timeout) or _Response({
                                'choices': [{'message': {'content': '{}'}}], 'usage': {}}))
        assert lb.call_deepseek('S', 'U')['text'] == '{}'
        assert calls == [120.0]


def test_http_200_non_json_is_not_retried(monkeypatch):
    calls = []
    monkeypatch.setattr(lb.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda req, timeout=None: calls.append(1) or _Response(b'<html>bad</html>'))
    with pytest.raises(lb.LLMBackendError, match='非 JSON'):
        lb.call_deepseek('S', 'U')
    assert len(calls) == 1


def test_response_body_has_size_limit(monkeypatch):
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda req, timeout=None: _Response(b'x' * 2_000_001))
    with pytest.raises(lb.LLMBackendError, match='响应过大'):
        lb.call_deepseek('S', 'U', retries=0)


def test_content_parts_are_joined(monkeypatch):
    body = {'choices': [{'message': {'content': [{'text': '{"a":'}, {'text': '1}'}]}}],
            'usage': {}}
    monkeypatch.setattr(urllib.request, 'urlopen', lambda req, timeout=None: _Response(body))
    assert lb.call_deepseek('S', 'U')['text'] == '{"a":1}'


def test_incomplete_read_is_backend_error(monkeypatch):
    def broken(req, timeout=None):
        raise http.client.IncompleteRead(b'{}', 10)
    monkeypatch.setattr(urllib.request, 'urlopen', broken)
    with pytest.raises(lb.LLMBackendError, match='网络错误'):
        lb.call_deepseek('S', 'U', retries=0)


@pytest.mark.parametrize('raw', [
    '[]', '{"性格":"中等"}',
    json.dumps(_reading()) + ' ' * 17_000,
    '{"n":' + '1' * 5000 + '}',
])
def test_bad_or_oversized_llm_output_degrades(raw, monkeypatch):
    monkeypatch.setattr(lc, 'call_deepseek', lambda *a, **kw: _llm_response(raw))
    out = lc.render_structured_reading({'bazi': {}, 'input': {}})
    assert out.startswith('[LLM 输出非合法 JSON')


def test_service_preserves_engine_on_unexpected_llm_error(monkeypatch):
    monkeypatch.setattr(service, 'engine_result_pillars', lambda *args: {})
    monkeypatch.setattr(service, 'format_report', lambda *args, **kw: 'ENGINE-REPORT')
    monkeypatch.setattr(service, 'render_structured_reading',
                        lambda *a, **kw: (_ for _ in ()).throw(AttributeError('mock schema')))
    out = service.paipan({'kind': 'pillars', 'pillars': ['甲子', '乙丑', '丙寅', '丁卯'],
                          'gender': '男'}, use_llm=True)
    assert 'ENGINE-REPORT' in out and 'LLM 通道暂不可用' in out


@pytest.mark.parametrize('text', [
    '丈夫有三个', '与女人只能处到三份情', '一生要嫁三任',
    '头一段顶多一年', '每段不过两载',
])
def test_numeric_variants_cannot_escape_validation(text):
    report = narrative.validate_narrative_numbers(text, {'summary': '共1步大运'})
    assert not report['ok'], text


def test_legacy_channel_rejects_redline_in_mark_and_reject(monkeypatch):
    monkeypatch.setattr(narrative, '_call_llm',
                        lambda *a, **kw: '你这命寿元不长，大限将至，早逝之象。')
    for mode in ('mark', 'reject'):
        out = narrative.render_hao_narrative({}, call_llm=True, validate=mode)
        assert '早逝之象' not in out and '拦截' in out


def test_legacy_channel_type_error_degrades(monkeypatch):
    monkeypatch.setattr(narrative, '_call_llm',
                        lambda *a, **kw: (_ for _ in ()).throw(TypeError('missing key')))
    out = narrative.render_hao_narrative({}, call_llm=True)
    assert out.startswith('[LLM 不可用')


def test_larkmd_disables_llm_links_mentions_and_details():
    payload = '[点击](https://evil.example/pay) <at id=all></at>'
    data = _reading(payload, [payload])
    validation = {'ok': False, 'violations': [{'layer': 'L1', 'detail': payload}]}
    out = lc.format_reading(data, validation, None)
    assert '](https://' not in out and '<at' not in out and '</at>' not in out


def test_basis_count_length_and_depth_are_bounded():
    data = _reading()
    data['性格']['basis'] = ['a.' * 8 + 'x'] + ['missing'] * 20
    report = lc.validate_reading(data, {}, {})
    assert any('超过20条' in v['detail'] for v in report['violations'])
    assert any('层级过深' in v['detail'] for v in report['violations'])


def test_llm_backend_failure_is_logged_without_prompt(monkeypatch, caplog):
    def unavailable(*args, **kwargs):
        raise lb.LLMBackendError('HTTP 402')
    monkeypatch.setattr(lc, 'call_deepseek', unavailable)
    with caplog.at_level(logging.WARNING, logger='mangpai.subjective.llm_channel'):
        out = lc.render_structured_reading({'bazi': {}, 'input': {}})
    assert out.startswith('[LLM 不可用') and 'HTTP 402' in caplog.text


def test_feishu_http_400_json_reaches_existing_error_handling(monkeypatch):
    error = urllib.error.HTTPError('https://open.feishu.cn/test', 400, 'Bad Request', {},
                                   io.BytesIO(b'{"code":230099,"msg":"bad card"}'))
    monkeypatch.setattr(urllib.request, 'urlopen', lambda *a, **kw: (_ for _ in ()).throw(error))
    client = FeishuClient(app_id='cli_x', app_secret='sec_y')
    assert client._urllib_post('https://open.feishu.cn/test', {})['code'] == 230099


def test_feishu_http_400_refreshes_token(monkeypatch):
    tokens = []

    def transport(req, timeout=None):
        if '/tenant_access_token/' in req.full_url:
            token = 'tok2' if tokens else 'tok1'
            tokens.append(token)
            return _Response({'code': 0, 'tenant_access_token': token, 'expire': 7200})
        if req.get_header('Authorization') == 'Bearer tok1':
            raise urllib.error.HTTPError(req.full_url, 400, 'Bad Request', {},
                                         io.BytesIO(b'{"code":99991663,"msg":"expired"}'))
        return _Response({'code': 0, 'data': {}})

    monkeypatch.setattr(urllib.request, 'urlopen', transport)
    client = FeishuClient(app_id='cli_x', app_secret='sec_y')
    client.reply('om_x', 'text', 'ok')
    assert tokens == ['tok1', 'tok2']


def test_main_rejects_missing_and_placeholder_credentials(monkeypatch):
    monkeypatch.setattr(bot, '_get_client', lambda: object())
    monkeypatch.setattr(bot, 'ThreadingHTTPServer', lambda *args: (_ for _ in ()).throw(
        AssertionError('无效配置不应启动服务')))
    monkeypatch.setenv('FEISHU_APP_ID', 'cli-reliability-123456')
    monkeypatch.setenv('FEISHU_APP_SECRET', 'secret-reliability-123456')
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'xxx')
    with pytest.raises(RuntimeError, match='FEISHU_VERIFICATION_TOKEN'):
        bot.main()
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'token-reliability-123456')
    monkeypatch.delenv('FEISHU_APP_SECRET')
    with pytest.raises(RuntimeError, match='FEISHU_APP_SECRET'):
        bot.main()


def test_encrypt_is_400_and_log_rate_limited(caplog):
    server = bot.ThreadingHTTPServer(('127.0.0.1', 0), bot._Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with caplog.at_level(logging.WARNING, logger='mangpai.feishu.bot'):
            statuses = [_post(server, {'encrypt': 'x'}), _post(server, {'encrypt': 'x'})]
        assert statuses == [400, 400]
        assert sum('Encrypt Key' in r.message for r in caplog.records) == 1
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_auth_failure_logs_rate_limited_without_token(caplog):
    server = bot.ThreadingHTTPServer(('127.0.0.1', 0), bot._Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with caplog.at_level(logging.WARNING, logger='mangpai.feishu.bot'):
            assert _post(server, _event()) == 401
            assert _post(server, _event()) == 401
        messages = [r.message for r in caplog.records if '鉴权失败' in r.message]
        assert len(messages) == 1 and 'wrong' not in messages[0]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_stopping_task_does_not_call_route(monkeypatch):
    bot._stopping.set()
    calls = []
    replies = []

    class Client:
        def reply(self, mid, kind, text):
            replies.append(text)

    monkeypatch.setattr(bot, 'route', lambda *a, **kw: calls.append(1) or 'should not run')
    assert bot._sem.acquire(False)
    bot._respond_managed(Client(), 'om_stop', '/help')
    assert calls == [] and replies == ['服务正在重启，请稍后重发']


def test_main_registers_signals_and_drains_jobs(monkeypatch):
    for name in ('FEISHU_APP_ID', 'FEISHU_APP_SECRET', 'FEISHU_VERIFICATION_TOKEN'):
        monkeypatch.setenv(name, name.lower() + '-reliability-123456')
    monkeypatch.setattr(bot, '_get_client', lambda: object())
    signals = []
    drained = []
    monkeypatch.setattr(signal, 'signal', lambda sig, handler: signals.append(sig))

    class Server:
        def __init__(self, *args):
            pass

        def serve_forever(self):
            return

        def server_close(self):
            return

    monkeypatch.setattr(bot, 'ThreadingHTTPServer', Server)
    monkeypatch.setattr(bot, '_drain_jobs', lambda: drained.append(1), raising=False)
    bot.main()
    assert signal.SIGTERM in signals and signal.SIGINT in signals and drained == [1]


def test_client_init_failure_allows_redelivery(monkeypatch):
    from mangpai.feishu.client import FeishuError
    attempts = []

    class Client:
        def __init__(self):
            self.replies = []

        def reply(self, mid, kind, text):
            self.replies.append(mid)

    client = Client()

    def get_client():
        attempts.append(1)
        if len(attempts) == 1:
            raise FeishuError('missing config')
        return client

    monkeypatch.setattr(bot, '_get_client', get_client)
    with pytest.raises(FeishuError):
        bot.handle_event(_event('want'), background=False)
    bot.handle_event(_event('want'), background=False)
    assert client.replies == ['om_reliability']


def test_retry_after_header_controls_delay(monkeypatch):
    calls = []
    sleeps = []

    def transport(req, timeout=None):
        calls.append(1)
        if len(calls) == 1:
            raise urllib.error.HTTPError(req.full_url, 429, 'limited',
                                         {'Retry-After': '7'}, None)
        return _Response({'choices': [{'message': {'content': '{}'}}], 'usage': {}})

    monkeypatch.setattr(urllib.request, 'urlopen', transport)
    monkeypatch.setattr(lb.time, 'sleep', lambda seconds: sleeps.append(seconds))
    assert lb.call_deepseek('S', 'U', retries=1)['text'] == '{}'
    assert sleeps == [7.0]


def test_total_budget_stops_before_another_retry(monkeypatch):
    calls = []
    monkeypatch.setattr(lb.time, 'monotonic', lambda: next(times))
    times = iter([0.0, 0.0, 0.0, 2.0, 2.0])
    monkeypatch.setattr(urllib.request, 'urlopen',
                        lambda req, timeout=None: calls.append(1) or (_ for _ in ()).throw(
                            urllib.error.URLError('offline')))
    with pytest.raises(lb.LLMBackendError, match='总超时'):
        lb.call_deepseek('S', 'U', timeout=1, retries=1)
    assert len(calls) == 1


def test_drain_cancels_queued_job_and_asks_redelivery(monkeypatch):
    replies = []

    class Future:
        def __init__(self):
            self._cancelled = False

        def done(self):
            return self._cancelled

        def cancelled(self):
            return self._cancelled

        def cancel(self):
            self._cancelled = True

    class Client:
        def reply(self, mid, kind, text):
            replies.append((mid, text))

    future = Future()

    class Executor:
        def shutdown(self, wait=False, cancel_futures=False):
            assert cancel_futures
            future.cancel()

    monkeypatch.setattr(bot, '_executor', Executor())
    monkeypatch.setattr(bot, 'wait', lambda futures, timeout: (set(), set(futures)))
    assert bot._sem.acquire(False)
    bot._jobs['om_queued'] = (Client(), future)
    bot._drain_jobs()
    assert replies == [('om_queued', '服务正在重启，请稍后重发')]
    assert 'om_queued' not in bot._jobs
