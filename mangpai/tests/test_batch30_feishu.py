import http.client
import json
import logging
import threading

import pytest

from mangpai.engine import EngineComputeError, MangpaiEngine
from mangpai.feishu import bot
from mangpai.feishu.router import handle, help_text, parse_solar
from mangpai.feishu.service import engine_result_pillars, paipan
from mangpai.subjective.llm_channel import DIMENSIONS, render_structured_reading


def test_pillars_year_must_match_and_help_example_valid():
    with pytest.raises(ValueError, match='出生年与年柱不符'):
        engine_result_pillars(['戊辰', '己未', '庚午', '丁亥'], '男', 1992)
    md = handle('四柱 己卯 丙子 戊午 戊午 男 2000', use_llm=False)
    assert '输入有误' not in md and '己卯' in md
    assert '[2000]' in help_text()


def test_negative_and_west_longitude():
    assert parse_solar('阳历 1990-05-01 08:00 男 -74.01 标准时（虚构示例）')['lon'] == -74.01
    assert parse_solar('阳历 1990-05-01 08:00 男 西经74.01 标准时（虚构示例）')['lon'] == -74.01
    assert parse_solar('阳历 1990-05-01 08:00 男 W74.01 标准时（虚构示例）')['lon'] == -74.01


def test_solar_reply_omits_full_birth_input():
    md = handle('阳历 1990-05-15 13:30 女 上海 标准时（虚构示例）', use_llm=False)
    assert '1990-05-15' not in md
    assert '13:30' not in md
    assert '上海' not in md
    assert '女' in md


def test_engine_error_log_has_module_location_but_not_message(monkeypatch, caplog):
    from mangpai.feishu.service import engine_result_solar

    def boom(*args, **kwargs):
        try:
            raise UnboundLocalError('sensitive-local-marker')
        except UnboundLocalError as exc:
            raise EngineComputeError('zhiye', exc)

    monkeypatch.setattr(bot, 'route', boom)
    with caplog.at_level(logging.ERROR, logger='mangpai.feishu.bot'):
        bot._respond(type('Client', (), {'reply': lambda self, *args: None})(),
                     'om_x', 'anything')
    assert 'zhiye' in caplog.text
    assert 'UnboundLocalError' in caplog.text
    assert '.py:' in caplog.text
    assert 'sensitive-local-marker' not in caplog.text
    assert 'Traceback' not in caplog.text


def test_safe_compute_warning_is_sanitized(caplog):
    def boom():
        raise RuntimeError('sensitive-local-marker')

    engine = MangpaiEngine({'bazi': {
        'year': '甲子', 'month': '乙丑', 'day': '丙寅', 'hour': '丁卯'},
        'input': {'gender': '男'}})
    with caplog.at_level(logging.WARNING, logger='mangpai.engine'):
        assert engine._safe_compute('hunyin', boom) is None
    assert 'RuntimeError' in caplog.text
    assert '.py:' in caplog.text
    assert 'sensitive-local-marker' not in caplog.text
    assert 'Traceback' not in caplog.text


def test_main_configures_logging(monkeypatch):
    monkeypatch.setattr(bot, '_validate_startup', lambda: None)
    monkeypatch.setattr(bot, '_drain_jobs', lambda: None)
    monkeypatch.setattr(bot.signal, 'signal', lambda *args: None)

    class Server:
        def __init__(self, address, handler):
            pass

        def serve_forever(self):
            return None

        def server_close(self):
            return None

    monkeypatch.setattr(bot, 'ThreadingHTTPServer', Server)
    monkeypatch.setattr(bot, '_stopping', threading.Event())
    calls = {}
    with monkeypatch.context() as m:
        m.setattr(logging, 'basicConfig', lambda **kwargs: calls.update(kwargs))
        bot.main()
    assert calls['level'] == logging.INFO
    assert '%(asctime)s' in calls['format']


def _post(port, body):
    conn = http.client.HTTPConnection('127.0.0.1', port, timeout=5)
    try:
        conn.request('POST', '/feishu/callback', body,
                     {'Expect': '100-continue'})
        response = conn.getresponse()
        response.read()
        return response.status
    finally:
        conn.close()


def test_body_limit_and_non_object_rejected(monkeypatch):
    from http.server import ThreadingHTTPServer

    monkeypatch.setattr(bot, '_MAX_BODY', 1024)
    server = ThreadingHTTPServer(('127.0.0.1', 0), bot._Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert _post(server.server_port, b' ' * (bot._MAX_BODY + 1)) == 413
        assert _post(server.server_port, b'[]') == 400
    finally:
        server.shutdown()
        server.server_close()


def test_feishu_hides_telemetry(monkeypatch):
    data = {dim: {'conclusion': '数据不足', 'basis': [], 'confidence': '低'}
            for dim in DIMENSIONS}
    response = {
        'text': json.dumps(data), 'usage': {'prompt_tokens': 10, 'completion_tokens': 5},
        'cost_cny': 0.01, 'price_tier': 'offpeak', 'elapsed_s': 0.1,
        'model': 'ft:private-model',
    }
    monkeypatch.setattr('mangpai.subjective.llm_channel.call_deepseek',
                        lambda *args, **kwargs: response)
    md = paipan(parse_solar('阳历 2000-01-01 12:00 男 北京（虚构示例）'), use_llm=True)
    assert 'model=' not in md and 'cost≈' not in md and 'ft:private-model' not in md
    direct = render_structured_reading({'caiming': {}, 'guanming': {}}, validate='off')
    assert 'model=ft:private-model' in direct
