"""llm_backend 峰谷计价自检（离线，不触网）。

官方口径（api-docs.deepseek.com 2026-08-18 复核）：峰段=北京时间 09:00-12:00、
14:00-18:00（UTC 01:00-04:00/06:00-10:00），谷档=峰档半价。
"""
from datetime import datetime

from mangpai.subjective.llm_backend import _BJT, _estimate_cost, _price_tier

_U = {'prompt_tokens': 10_000, 'completion_tokens': 5_000}


def _at(h, m=0):
    """2026-08-18（周二）北京时间 h:m 的 epoch 秒。"""
    return datetime(2026, 8, 18, h, m, tzinfo=_BJT).timestamp()


def test_price_tier_peak_windows():
    assert _price_tier(_at(9)) == 'peak'        # 峰段起点含 09:00
    assert _price_tier(_at(11, 59)) == 'peak'
    assert _price_tier(_at(12)) == 'offpeak'    # 午间落谷
    assert _price_tier(_at(14)) == 'peak'       # 午后峰段起点
    assert _price_tier(_at(17, 59)) == 'peak'
    assert _price_tier(_at(18)) == 'offpeak'    # 峰段终点不含 18:00
    assert _price_tier(_at(0)) == 'offpeak'


def test_estimate_cost_flash_tiers():
    # 2026-08-21 人民币口径：峰 ¥3.0/¥9.0，谷 ¥1.5/¥4.5（/1M tokens）
    peak = _estimate_cost('deepseek-flash', _U, at=_at(10))
    off = _estimate_cost('deepseek-flash', _U, at=_at(20))
    assert abs(peak - (10_000 * 3.0 + 5_000 * 9.0) / 1e6) < 1e-12
    assert abs(off - (10_000 * 1.5 + 5_000 * 4.5) / 1e6) < 1e-12
    assert abs(peak - 2 * off) < 1e-12  # 谷档=峰档半价


def test_estimate_cost_pro_and_unknown():
    off = _estimate_cost('deepseek-v4-pro', _U, at=_at(20))
    assert abs(off - (10_000 * 4.5 + 5_000 * 13.5) / 1e6) < 1e-12
    # S1：未知模型/其他 provider 显式 None（未计价），不再误导性 ¥0
    assert _estimate_cost('unknown-model', _U) is None


# ---------- 红6：429 可重试 + 畸形 URL 包装 ----------

import io
import json
import urllib.error

import pytest

from mangpai.subjective import llm_backend as _lb


class _FakeResp:
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self):
        return json.dumps({'choices': [{'message': {'content': '{}'}}],
                           'usage': {}}).encode('utf-8')


def test_http_429_retried_like_5xx(monkeypatch):
    """红6a：HTTP 429 限流与 5xx 同策略重试（修复前 429 落入 4xx 分支直接抛）。"""
    monkeypatch.setattr(_lb, '_load_api_key', lambda: 'k')
    monkeypatch.setattr(_lb.time, 'sleep', lambda s: None)
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(1)
        if len(calls) < 3:
            raise urllib.error.HTTPError(req.full_url, 429, 'Too Many Requests',
                                         {}, None)
        return _FakeResp()

    monkeypatch.setattr('urllib.request.urlopen', fake_urlopen)
    out = _lb.call_deepseek('s', 'u')
    assert out['text'] == '{}' and len(calls) == 3

    # 对照：其余 4xx（400）仍不重试直接抛
    calls.clear()

    def fake_400(req, timeout=None):
        calls.append(1)
        raise urllib.error.HTTPError(req.full_url, 400, 'Bad Request', {},
                                     io.BytesIO(b'bad'))

    monkeypatch.setattr('urllib.request.urlopen', fake_400)
    with pytest.raises(_lb.LLMBackendError):
        _lb.call_deepseek('s', 'u')
    assert len(calls) == 1


def test_malformed_url_wrapped_as_backend_error(monkeypatch):
    """红6b：畸形 URL 的 ValueError 包装为 LLMBackendError——
    llm_channel.render_structured_reading 的 except 能接住降级（不裸穿透）。"""
    monkeypatch.setattr(_lb, '_load_api_key', lambda: 'k')
    monkeypatch.setenv('MANGPAI_LLM_BASE_URL', 'not-a-url')
    with pytest.raises(_lb.LLMBackendError, match='URL 畸形'):
        _lb.call_deepseek('s', 'u')
    # 调用方视角：render 层接住降级而非 ValueError 穿透
    from mangpai.subjective.llm_channel import render_structured_reading
    out = render_structured_reading({'bazi': {}, 'input': {}}, validate='mark')
    assert out.startswith('[LLM 不可用')


def test_error_paths_do_not_echo_sensitive_content(monkeypatch):
    """HTTP 错误、非 JSON 响应和畸形 URL 均不得回显敏感内容。"""
    monkeypatch.setattr(_lb, '_load_api_key', lambda: 'k')
    monkeypatch.setenv('MANGPAI_LLM_RETRIES', '0')
    marker = 'sensitive-birth-data'

    def bad_request(req, timeout=None):
        raise urllib.error.HTTPError(
            req.full_url, 400, 'Bad Request', {}, io.BytesIO(marker.encode()))

    monkeypatch.setattr('urllib.request.urlopen', bad_request)
    with pytest.raises(_lb.LLMBackendError) as exc:
        _lb.call_deepseek('s', 'u')
    assert marker not in str(exc.value)

    class BadJSON:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return marker.encode()

    monkeypatch.setattr('urllib.request.urlopen', lambda req, timeout=None: BadJSON())
    with pytest.raises(_lb.LLMBackendError) as exc:
        _lb.call_deepseek('s', 'u')
    assert marker not in str(exc.value)

    monkeypatch.setenv('MANGPAI_LLM_BASE_URL', 'not-a-url-' + marker)
    with pytest.raises(_lb.LLMBackendError) as exc:
        _lb.call_deepseek('s', 'u')
    assert marker not in str(exc.value)
