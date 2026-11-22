# -*- coding: utf-8 -*-
"""批次14：飞书 webhook 安全与输入解析，全部本地/离线。"""
import json
import socket
import threading
import time
from datetime import date

import pytest

from mangpai.feishu import bot
from mangpai.feishu.router import parse_solar, ParseError
from mangpai.subjective.llm_channel import DIMENSIONS, _l2_enum


class Client:
    def __init__(self):
        self.replies = []

    def reply(self, mid, msg_type, text):
        self.replies.append((mid, msg_type, text))


def event(mid='om_1', text='/help', chat_type='p2p', sender='user-1', age_ms=0):
    return {
        'header': {'event_type': 'im.message.receive_v1', 'token': 'want',
                   'event_id': 'event-' + mid,
                   'create_time': str(int(time.time() * 1000) - age_ms)},
        'event': {'sender': {'sender_id': {'open_id': sender}, 'sender_type': 'user'},
                  'message': {'message_id': mid, 'message_type': 'text',
                              'chat_type': chat_type,
                              'content': json.dumps({'text': text})}},
    }


@pytest.fixture(autouse=True)
def security_env(monkeypatch):
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'want')
    bot._seen_mids.clear()
    bot._rate_events.clear()
    bot._llm_calls.clear()


def test_group_and_bot_messages_are_not_processed():
    client = Client()
    bot.handle_event(event(chat_type='group'), client=client, background=False)
    bot_message = event(mid='om_2', sender='bot-1')
    bot_message['event']['sender']['sender_type'] = 'app'
    bot.handle_event(bot_message, client=client, background=False)
    # sender_type 非 user 也不处理
    other = event(mid='om_3')
    other['event']['sender']['sender_type'] = 'app'
    bot.handle_event(other, client=client, background=False)
    missing = event(mid='om_4')
    del missing['event']['sender']['sender_type']
    bot.handle_event(missing, client=client, background=False)
    assert client.replies == []


def test_p2p_message_still_processed():
    client = Client()
    bot.handle_event(event(), client=client, background=False)
    assert len(client.replies) == 1


def test_missing_token_and_stale_event_rejected(monkeypatch):
    client = Client()
    monkeypatch.delenv('FEISHU_VERIFICATION_TOKEN')
    with pytest.raises(PermissionError):
        bot._check_token('want')
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'want')
    bot.handle_event(event(age_ms=10 * 60 * 1000), client=client, background=False)
    for created in ('nan', 'inf', ''):
        invalid = event(mid='om_' + (created or 'empty'))
        invalid['header']['create_time'] = created
        bot.handle_event(invalid, client=client, background=False)
    assert client.replies == []


@pytest.mark.parametrize('mid', ['om_x/../../chats/oc_y', 'bad id', ''])
def test_message_id_cannot_change_api_path(mid):
    client = Client()
    bot.handle_event(event(mid=mid), client=client, background=False)
    assert client.replies == []


def test_sender_rate_limit_returns_busy(monkeypatch):
    monkeypatch.setenv('FEISHU_RATE_PER_MIN', '3')
    client = Client()
    for i in range(3):
        bot.handle_event(event(mid=f'om_{i}'), client=client, background=True)
    bot.handle_event(event(mid='om_3'), client=client, background=True)
    assert any('繁忙' in text for _mid, _kind, text in client.replies)


def test_queue_full_returns_busy(monkeypatch):
    monkeypatch.setattr(bot._sem, 'acquire', lambda blocking=False: False)
    client = Client()
    bot.handle_event(event(), client=client, background=True)
    assert client.replies and '繁忙' in client.replies[0][2]


@pytest.mark.parametrize('text, hour, minute', [
    ('下午3点', 15, 0), ('晚上11点', 23, 0), ('3点半', 3, 30),
    ('PM 3点', 15, 0), ('中午12点', 12, 0),
])
def test_time_of_day_and_half_hour(text, hour, minute):
    spec = parse_solar(f'阳历 2000-01-01 {text} 男 北京（虚构示例）')
    assert (spec['hour'], spec['minute']) == (hour, minute)


def test_lunar_and_inconsistent_period_rejected():
    with pytest.raises(ParseError, match='农历'):
        parse_solar('农历 2000-03-15 08:30 男 北京（虚构示例）')
    with pytest.raises(ParseError, match='下午'):
        parse_solar('下午13点 2000-01-01 男 北京（虚构示例）')


@pytest.mark.parametrize('place', ['湖南宁乡', '湖北京山', '江西安远'])
def test_unknown_place_does_not_borrow_city(place):
    with pytest.raises(ParseError):
        parse_solar(f'阳历 2000-01-01 12:00 男 {place}（虚构示例）')


def test_city_and_beijing_time_parsing():
    assert parse_solar('阳历 2000-01-01 12:00 男 广西南宁（虚构示例）')['lon'] == 108.37
    spec = parse_solar('北京时间 2000-01-01 12:00 男 成都（虚构示例）')
    assert spec['place'] == '成都' and spec['lon'] == 104.07


def test_redline_words_reject_instead_of_human_review(monkeypatch):
    from mangpai.feishu.service import paipan
    from mangpai.subjective import llm_channel
    spec = parse_solar('阳历 2000-01-01 12:00 男 北京（虚构示例）')
    for dim, text in (('迁移', '中年有移民海外之象'), ('相貌', '此人长得很漂亮')):
        data = {d: {'conclusion': text if d == dim else '平稳', 'basis': [],
                    'confidence': '低'} for d in DIMENSIONS}
        assert any(v.get('reject') for v in _l2_enum(data, {}))
        monkeypatch.setattr(llm_channel, 'call_deepseek',
                            lambda *a, _data=data, **kw: {'text': json.dumps(_data, ensure_ascii=False)})
        md = paipan(spec, use_llm=True)
        assert text not in md and '安全过滤' in md


def test_http_negative_length_and_chunked_rejected(monkeypatch):
    monkeypatch.setattr(bot, '_READ_TIMEOUT', 0.1)
    server = bot.ThreadingHTTPServer(('127.0.0.1', 0), bot._Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        for header in ('Content-Length: -1', 'Transfer-Encoding: chunked'):
            with socket.create_connection(('127.0.0.1', server.server_port), timeout=2) as sock:
                sock.sendall(f'POST /feishu/callback HTTP/1.1\r\nHost: localhost\r\n{header}\r\n\r\n'.encode())
                response = sock.recv(1024).decode('latin-1')
            assert ' 400 ' in response.split('\r\n', 1)[0]
        with socket.create_connection(('127.0.0.1', server.server_port), timeout=2) as sock:
            sock.sendall(b'POST /feishu/callback HTTP/1.1\r\nHost: localhost\r\nContent-Length: 5\r\n\r\n{')
            time.sleep(0.2)
            response = sock.recv(1024).decode('latin-1')
        assert ' 400 ' in response.split('\r\n', 1)[0]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_daily_llm_limit_switches_to_engine_only(monkeypatch):
    monkeypatch.setenv('MANGPAI_USE_LLM', '1')
    monkeypatch.setenv('FEISHU_LLM_DAILY_MAX', '1')
    seen = []
    monkeypatch.setattr(bot, '_respond',
                        lambda _client, _mid, _text, use_llm=None: seen.append(use_llm))
    client = Client()
    bot.handle_event(event(mid='om_daily1'), client=client, background=False)
    bot.handle_event(event(mid='om_daily2'), client=client, background=False)
    assert seen == [True, False]


def test_feishu_llm_uses_short_timeout_without_retry(monkeypatch):
    from mangpai.feishu.service import paipan
    captured = {}

    def fake_render(_res, validate='mark', **kwargs):
        captured.update(kwargs)
        return '[LLM 不可用，降级返回 prompt 文本]'

    monkeypatch.setattr('mangpai.feishu.service.render_structured_reading', fake_render)
    paipan(parse_solar('阳历 2000-01-01 12:00 男 北京（虚构示例）'), use_llm=True)
    assert captured == {'timeout': 30, 'retries': 0}
