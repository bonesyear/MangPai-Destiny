"""飞书集成测试：客户端 mock / 命令路由 / 全链路（mock LLM，不调真实 DeepSeek）。"""
import json
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pytest

from mangpai.feishu import bot
from mangpai.feishu.client import FeishuClient, FeishuError
from mangpai.feishu.router import handle, parse_pillars, parse_solar, ParseError
from mangpai.feishu.service import paipan


# ---------------------------------------------------------------- 客户端（mock HTTP）
class FakeHTTP:
    """记录调用并按序返回响应。"""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url, payload, headers=None):
        self.calls.append({'url': url, 'payload': payload, 'headers': headers or {}})
        return self.responses.pop(0)


def _client(http):
    return FeishuClient(app_id='cli_x', app_secret='sec_y', http_post=http)


def test_token_fetch_and_cache():
    http = FakeHTTP([{'code': 0, 'tenant_access_token': 'tok1', 'expire': 7200}])
    c = _client(http)
    assert c.tenant_access_token() == 'tok1'
    assert c.tenant_access_token() == 'tok1'  # 缓存命中，不再请求
    assert len(http.calls) == 1
    assert http.calls[0]['url'].endswith('/auth/v3/tenant_access_token/internal')
    assert http.calls[0]['payload'] == {'app_id': 'cli_x', 'app_secret': 'sec_y'}


def test_token_refresh_after_expiry():
    http = FakeHTTP([{'code': 0, 'tenant_access_token': 'tok1', 'expire': 7200},
                     {'code': 0, 'tenant_access_token': 'tok2', 'expire': 7200}])
    c = _client(http)
    c.tenant_access_token()
    c._token_expire = 0  # 模拟过期
    assert c.tenant_access_token() == 'tok2'


def test_token_error_raises():
    http = FakeHTTP([{'code': 999, 'msg': 'bad secret'}])
    with pytest.raises(FeishuError):
        _client(http).tenant_access_token()


def test_send_and_reply_payload():
    http = FakeHTTP([{'code': 0, 'tenant_access_token': 't', 'expire': 7200},
                     {'code': 0, 'data': {}}, {'code': 0, 'data': {}}])
    c = _client(http)
    c.send('oc_chat', 'text', '你好')
    c.reply('om_mid', 'interactive', '**md**')
    send, reply = http.calls[1], http.calls[2]
    assert 'receive_id_type=chat_id' in send['url']
    assert send['headers']['Authorization'] == 'Bearer t'
    assert send['payload']['msg_type'] == 'text'
    assert json.loads(send['payload']['content']) == {'text': '你好'}
    assert reply['url'].endswith('/im/v1/messages/om_mid/reply')
    card = json.loads(reply['payload']['content'])
    assert card['elements'][0]['text'] == {'tag': 'lark_md', 'content': '**md**'}


def test_api_retries_once_on_token_invalid():
    """99991663（token 服务端作废）→ 清缓存重取 token 并重试一次成功。"""
    http = FakeHTTP([{'code': 0, 'tenant_access_token': 'tok1', 'expire': 7200},
                     {'code': 99991663, 'msg': 'token invalid'},
                     {'code': 0, 'tenant_access_token': 'tok2', 'expire': 7200},
                     {'code': 0, 'data': {}}])
    c = _client(http)
    c.send('oc_chat', 'text', 'hi')
    assert http.calls[2]['url'].endswith('/auth/v3/tenant_access_token/internal')
    assert http.calls[3]['headers']['Authorization'] == 'Bearer tok2'


def test_api_raises_after_retry_exhausted():
    """99991661 重试后仍失效 → 抛错，不无限重试。"""
    http = FakeHTTP([{'code': 0, 'tenant_access_token': 'tok1', 'expire': 7200},
                     {'code': 99991661, 'msg': 'invalid'},
                     {'code': 0, 'tenant_access_token': 'tok2', 'expire': 7200},
                     {'code': 99991661, 'msg': 'invalid'}])
    c = _client(http)
    with pytest.raises(FeishuError, match='99991661'):
        c.send('oc_chat', 'text', 'hi')
    assert len(http.calls) == 4  # 1 token + 1 api + 1 token + 1 retry


def test_post_content_shape():
    body = json.loads(FeishuClient.build_content('post', '多段'))
    assert body['zh_cn']['content'][0][0] == {'tag': 'text', 'text': '多段'}


def test_missing_credentials(monkeypatch):
    monkeypatch.delenv('FEISHU_APP_ID', raising=False)
    monkeypatch.delenv('FEISHU_APP_SECRET', raising=False)
    with pytest.raises(FeishuError):
        FeishuClient()


# ---------------------------------------------------------------- 命令路由
def test_parse_solar_city():
    spec = parse_solar('阳历 1992-10-09 13:58 男 河南信阳')
    assert (spec['year'], spec['month'], spec['day']) == (1992, 10, 9)
    assert (spec['hour'], spec['minute']) == (13, 58)
    assert spec['gender'] == '男' and spec['lon'] == 114.07


def test_parse_solar_direct_lon():
    spec = parse_solar('1992/10/09 13点58 女 114.07')
    assert spec['gender'] == '女' and spec['lon'] == 114.07


def test_parse_solar_gender_required():
    with pytest.raises(ParseError, match='性别必填'):
        parse_solar('阳历 1992-10-09 13:58 信阳')


def test_parse_solar_unknown_city():
    with pytest.raises(ParseError, match='经度'):
        parse_solar('阳历 1992-10-09 13:58 男 某小县城')


def test_parse_pillars_ok():
    spec = parse_pillars('四柱 戊辰 己未 庚午 丁亥 男')
    assert spec['pillars'] == ['戊辰', '己未', '庚午', '丁亥']
    assert spec['gender'] == '男' and spec['year'] is None


def test_parse_pillars_bad_parity():
    with pytest.raises(ValueError, match='阴阳错配'):
        paipan({'kind': 'pillars', 'pillars': ['甲丑', '己未', '庚午', '丁亥'],
                'gender': '男'}, use_llm=False)


def test_help_and_ver():
    assert '阳历' in handle('/help')
    assert '引擎基线' in handle('/ver')


def test_unknown_input_returns_help_hint():
    assert '输入有误' in handle('随便说点啥')


# ---------------------------------------------------------------- 全链路（LLM 关闭或 mock）
def test_e2e_solar_engine_only():
    md = handle('阳历 1992-10-09 13:58 男 河南信阳', use_llm=False)
    assert '壬申 庚戌 戊午 己未' in md
    for sec in ('**做功**', '**层功**', '**三维**', '**婚姻**', '**应期**', '**一句话**：'):
        assert sec in md


def test_e2e_pillars_engine_only():
    md = handle('四柱 戊辰 己未 庚午 丁亥 男', use_llm=False)
    assert '戊辰 己未 庚午 丁亥' in md and '**一句话**：' in md


def test_llm_success_appended(monkeypatch):
    monkeypatch.setattr('mangpai.feishu.service.render_structured_reading',
                        lambda res, validate='mark': '【性格】(高) mock 五维')
    md = handle('阳历 1992-10-09 13:58 男 信阳', use_llm=True)
    assert 'LLM 五维叙述' in md and 'mock 五维' in md


def test_llm_failure_degrades_to_engine(monkeypatch):
    monkeypatch.setattr('mangpai.feishu.service.render_structured_reading',
                        lambda res, validate='mark': '[LLM 不可用，降级返回 prompt 文本 | 原因: x]')
    md = handle('阳历 1992-10-09 13:58 男 信阳', use_llm=True)
    assert '引擎直出结论' in md and 'LLM 五维叙述' not in md


def test_llm_off_by_default_env(monkeypatch):
    monkeypatch.setenv('FEISHU_USE_LLM', '0')
    md = handle('阳历 1992-10-09 13:58 男 信阳')  # 不传 use_llm → 读环境变量
    assert 'LLM 五维叙述' not in md


# ---------------------------------------------------------------- webhook 事件
def _msg_event(mid='om_1', text='阳历 1992-10-09 13:58 男 信阳'):
    return {'schema': '2.0',
            'header': {'event_type': 'im.message.receive_v1', 'token': ''},
            'event': {'message': {'message_id': mid, 'message_type': 'text',
                                  'content': json.dumps({'text': text})}}}


class FakeClient:
    def __init__(self):
        self.replies = []

    def reply(self, mid, msg_type, text):
        self.replies.append((mid, msg_type, text))


def test_url_verification_challenge(monkeypatch):
    monkeypatch.delenv('FEISHU_VERIFICATION_TOKEN', raising=False)
    resp = bot.handle_event({'type': 'url_verification', 'token': 'x', 'challenge': 'abc'})
    assert resp == {'challenge': 'abc'}


def test_message_event_replies_and_dedupes():
    bot._seen_mids.clear()
    fc = FakeClient()
    assert bot.handle_event(_msg_event(), client=fc, background=False) == {}
    assert len(fc.replies) == 1
    mid, msg_type, text = fc.replies[0]
    assert mid == 'om_1' and msg_type == 'interactive' and '**做功**' in text
    bot.handle_event(_msg_event(), client=fc, background=False)  # 重复事件去重
    assert len(fc.replies) == 1


def test_bad_input_replies_error_not_raise():
    bot._seen_mids.clear()
    fc = FakeClient()
    bot.handle_event(_msg_event(mid='om_2', text='hello'), client=fc, background=False)
    assert '输入有误' in fc.replies[0][2]


def test_token_mismatch_rejected(monkeypatch):
    monkeypatch.setenv('FEISHU_VERIFICATION_TOKEN', 'want')
    with pytest.raises(PermissionError):
        bot.handle_event({'type': 'url_verification', 'token': 'nope', 'challenge': 'c'})


# ---------------------------------------------------------------- 修批 E1 哨兵
def test_reply_failure_fallback_not_silent(caplog):
    """client.reply 首次失败 → 记日志 + 兜底重发，不静默死线程。"""
    class FlakyClient:
        def __init__(self):
            self.calls = []

        def reply(self, mid, msg_type, text):
            self.calls.append(msg_type)
            if len(self.calls) == 1:
                raise RuntimeError('network down')

    fc = FlakyClient()
    with caplog.at_level('ERROR', logger='mangpai.feishu.bot'):
        bot._respond(fc, 'om_x', '/help')  # 不抛
    assert fc.calls == ['interactive', 'text']
    assert any('reply' in r.message for r in caplog.records)


def test_main_requires_verification_token(monkeypatch):
    """FEISHU_VERIFICATION_TOKEN 未配 → 启动即报错。"""
    monkeypatch.delenv('FEISHU_VERIFICATION_TOKEN', raising=False)
    with pytest.raises(RuntimeError, match='FEISHU_VERIFICATION_TOKEN'):
        bot.main()


def test_encrypt_body_warns_and_drops(caplog):
    """控制台误配 Encrypt Key → 回调体只有 encrypt 字段：告警并丢弃，不静默。"""
    with caplog.at_level('WARNING', logger='mangpai.feishu.bot'):
        assert bot.handle_event({'encrypt': 'deadbeef'}) == {}
    assert any('Encrypt Key' in r.message for r in caplog.records)


# ---------------------------------------------------------------- 修批 E5 哨兵
def test_dedupe_window_rolls_not_clears():
    """重放窗口滚动清最老，不整窗清空：窗口内近期消息重放仍去重。"""
    bot._seen_mids.clear()
    fc = FakeClient()
    for i in range(2002):
        bot.handle_event(_msg_event(mid=f'om_r{i}', text='/help'), client=fc, background=False)
    n = len(fc.replies)
    bot.handle_event(_msg_event(mid='om_r2000', text='/help'), client=fc, background=False)
    assert len(fc.replies) == n  # om_r2000 仍在滚动窗口内（旧实现全清会再回一条）
    bot.handle_event(_msg_event(mid='om_r0', text='/help'), client=fc, background=False)
    assert len(fc.replies) == n + 1  # 最老一条已滚出窗口，重放按新消息处理
    bot._seen_mids.clear()


def test_token_refresh_locked_concurrent():
    """8 线程并发发现 token 过期 → 刷新锁双检，只实际刷新 1 次。"""
    calls = []

    def http(url, payload, headers=None):
        calls.append(url)
        time.sleep(0.02)  # 放大竞态窗口
        return {'code': 0, 'tenant_access_token': 'tok', 'expire': 7200}

    c = FeishuClient(app_id='a', app_secret='b', http_post=http)
    with ThreadPoolExecutor(8) as ex:
        toks = list(ex.map(lambda _: c.tenant_access_token(), range(8)))
    assert toks == ['tok'] * 8
    assert len(calls) == 1


def test_time_rejects_three_digit_hour():
    """'123:45' 不得静默截断成 23:45，应报解析错。"""
    with pytest.raises(ParseError):
        parse_solar('阳历 1992-10-09 123:45 男 信阳')


def test_time_rejects_seconds():
    """秒位不静默丢弃：明确报错。"""
    with pytest.raises(ParseError, match='秒'):
        parse_solar('阳历 1992-10-09 13:58:59 男 信阳')


def test_solar_date_wins_over_sizhu_keyword():
    """文本同时含阳历日期和「四柱」触发词 → 阳历优先，不抢占。"""
    md = handle('阳历 1992-10-09 13:58 男 信阳 四柱 戊辰 己未 庚午 丁亥', use_llm=False)
    assert '壬申 庚戌 戊午 己未' in md  # 阳历盘，非四柱直排


def test_500_no_internal_echo():
    """回调处理异常 → 500 通用信息，不回显 str(e) 内部详情。"""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(('127.0.0.1', 0), bot._Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        req = urllib.request.Request(
            f'http://127.0.0.1:{srv.server_port}/feishu/callback',
            data=json.dumps({'header': {'token': ''}, 'event': 'oops'}).encode(),
            method='POST')
        with pytest.raises(urllib.error.HTTPError) as ei:
            urllib.request.urlopen(req, timeout=5)
        assert ei.value.code == 500
        body = ei.value.read().decode()
        assert 'attribute' not in body and 'oops' not in body
    finally:
        srv.shutdown()
