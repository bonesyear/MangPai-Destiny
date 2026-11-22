"""S1 LLM 通道配置化哨兵（test_s1_llm_config.py）。

红线验证：未设任何 MANGPAI_LLM_* 新变量时，请求与旧版 DeepSeek 路径逐字节一致；
新配置项（BASE_URL/API_KEY/MODEL/THINKING/REASONING_EFFORT/TIMEOUT/RETRIES/
ENV_FILE/MAX_TOKENS/CONTEXT）各自生效；未知 provider 成本显式 None（未计价）；MANGPAI_USE_LLM
通用别名。全部 mock（urllib.request.urlopen 拦截 + tmp env 文件），不调真实 API。
"""
import json
import os
import sys
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mangpai.subjective.llm_backend as lb
from mangpai.subjective.llm_backend import LLMBackendError, call_deepseek
from mangpai.subjective.llm_channel import format_reading
from mangpai.feishu import service as feishu_service

_LLM_VARS = ('MANGPAI_LLM_BASE_URL', 'MANGPAI_LLM_API_KEY', 'MANGPAI_LLM_MODEL',
             'MANGPAI_LLM_THINKING', 'MANGPAI_LLM_REASONING_EFFORT',
             'MANGPAI_LLM_TIMEOUT', 'MANGPAI_LLM_RETRIES', 'MANGPAI_LLM_ENV_FILE',
             'MANGPAI_LLM_MAX_TOKENS', 'MANGPAI_LLM_CONTEXT',
             'DEEPSEEK_API_KEY', 'DEEPSEEK_MODEL',
             'MANGPAI_USE_LLM', 'FEISHU_USE_LLM')


class _FakeResp:
    def __init__(self, body: bytes):
        self._body = body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def read(self, n=-1):
        return self._body if n < 0 else self._body[:n]


_OK_BODY = json.dumps({
    'choices': [{'message': {'content': '{"ok": true}'}}],
    'usage': {'prompt_tokens': 10, 'completion_tokens': 5},
}).encode('utf-8')


@pytest.fixture
def clean_env(monkeypatch, tmp_path):
    for v in _LLM_VARS:
        monkeypatch.delenv(v, raising=False)
    monkeypatch.setattr(lb, '_PROJECT_ENV_FILE', tmp_path / 'no-project.env')
    return monkeypatch


def _capture(monkeypatch, body=_OK_BODY):
    """拦截 urlopen，返回 (captured, )——captured 收 (Request, timeout)。"""
    monkeypatch.setenv('MANGPAI_USE_LLM', '1')
    captured = []

    def fake_urlopen(req, timeout=None, **kw):
        captured.append((req, timeout))
        return _FakeResp(body)

    monkeypatch.setattr(urllib.request, 'urlopen', fake_urlopen)
    opener = type('Opener', (), {'open': staticmethod(fake_urlopen)})
    monkeypatch.setattr(urllib.request, 'build_opener', lambda *args: opener())
    return captured


def _expected_default_body():
    """旧版 DeepSeek 路径请求体（逐字节基准，键序敏感）。"""
    return {
        'model': 'deepseek-flash',
        'messages': [
            {'role': 'system', 'content': 'S'},
            {'role': 'user', 'content': 'U'},
        ],
        'max_tokens': 8192,
        'reasoning_effort': 'low',
        'thinking': {'type': 'enabled'},
        'response_format': {'type': 'json_object'},
    }


# ---------------------------------------------------------------- 回退链（红线）

def test_default_path_byte_identical(clean_env):
    """未设新变量：URL/请求体/密钥头与旧版 DeepSeek 路径逐字节一致。"""
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    captured = _capture(clean_env)
    resp = call_deepseek('S', 'U')
    assert len(captured) == 1
    req, timeout = captured[0]
    assert req.full_url == 'https://api.deepseek.com/chat/completions'
    assert req.data == json.dumps(_expected_default_body()).encode('utf-8')
    assert req.unredirected_hdrs['Authorization'] == 'Bearer sk-old'
    assert timeout == 120.0
    assert resp['model'] == 'deepseek-flash'
    assert isinstance(resp['cost_cny'], float)


def test_authorization_not_forwarded_on_redirect(clean_env):
    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-new')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    req = captured[0][0]
    redirected = urllib.request.HTTPRedirectHandler().redirect_request(
        req, None, 302, 'Found', {}, 'https://relay.example/chat/completions')
    assert 'Authorization' not in redirected.headers
    assert 'Authorization' not in redirected.unredirected_hdrs


def test_deepseek_model_env_still_works(clean_env):
    """旧变量 DEEPSEEK_MODEL 回退仍有效（兼容现状配置）。"""
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('DEEPSEEK_MODEL', 'deepseek-v4-pro')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    assert json.loads(captured[0][0].data)['model'] == 'deepseek-v4-pro'


# ---------------------------------------------------------------- 新配置项生效

def test_base_url_override(clean_env):
    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-new')
    clean_env.setenv('MANGPAI_LLM_BASE_URL', 'http://localhost:11434/v1/chat/completions')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    assert captured[0][0].full_url == 'http://localhost:11434/v1/chat/completions'


def test_api_key_precedence(clean_env):
    """MANGPAI_LLM_API_KEY 优先于 DEEPSEEK_API_KEY。"""
    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-new')
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    assert captured[0][0].unredirected_hdrs['Authorization'] == 'Bearer sk-new'


def test_model_precedence_chain(clean_env):
    """MANGPAI_LLM_MODEL > DEEPSEEK_MODEL > deepseek-flash；形参最优先。"""
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('MANGPAI_LLM_MODEL', 'qwen-local')
    clean_env.setenv('DEEPSEEK_MODEL', 'deepseek-v4-pro')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    assert json.loads(captured[0][0].data)['model'] == 'qwen-local'
    captured.clear()
    call_deepseek('S', 'U', model='explicit-model')
    assert json.loads(captured[0][0].data)['model'] == 'explicit-model'


def test_thinking_off_strips_provider_fields(clean_env):
    """MANGPAI_LLM_THINKING=0 → 请求体剔除 thinking 与 reasoning_effort。"""
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('MANGPAI_LLM_THINKING', '0')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    body = json.loads(captured[0][0].data)
    assert 'thinking' not in body
    assert 'reasoning_effort' not in body
    assert body['response_format'] == {'type': 'json_object'}  # JSON mode 保留


def test_reasoning_effort_env(clean_env):
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('MANGPAI_LLM_REASONING_EFFORT', 'high')
    captured = _capture(clean_env)
    call_deepseek('S', 'U')
    assert json.loads(captured[0][0].data)['reasoning_effort'] == 'high'


def test_timeout_retries_env(clean_env):
    """MANGPAI_LLM_TIMEOUT/RETRIES 生效；5xx 重试次数随 RETRIES=0 归零。"""
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('MANGPAI_USE_LLM', '1')
    clean_env.setenv('MANGPAI_LLM_TIMEOUT', '300')
    clean_env.setenv('MANGPAI_LLM_RETRIES', '0')
    clean_env.setattr(lb.time, 'sleep', lambda s: None)
    err = urllib.error.HTTPError('http://x', 500, 'srv', {}, None)

    def boom(req, timeout=None, **kw):
        boom.calls.append(timeout)
        raise err
    boom.calls = []
    clean_env.setattr(urllib.request, 'urlopen', boom)
    with pytest.raises(LLMBackendError, match='HTTP 500'):
        call_deepseek('S', 'U')
    assert boom.calls == [pytest.approx(300.0, abs=0.01)]  # 总时限内取剩余秒数；零重试


def test_env_file_custom_path(clean_env, tmp_path):
    """MANGPAI_LLM_ENV_FILE 指定 env 文件；两种键名皆可解析。"""
    f = tmp_path / 'my.env'
    f.write_text('MANGPAI_LLM_API_KEY="sk-file"\n', encoding='utf-8')
    clean_env.setenv('MANGPAI_LLM_ENV_FILE', str(f))
    assert lb._load_api_key() == 'sk-file'
    f.write_text("DEEPSEEK_API_KEY='sk-legacy-name'\n", encoding='utf-8')
    assert lb._load_api_key() == 'sk-legacy-name'


def test_env_file_does_not_read_home(clean_env, tmp_path, monkeypatch):
    """缺省只读项目根 .env，不读取其他项目留在家目录的 key。"""
    proj_env = tmp_path / 'proj.env'
    home_env = tmp_path / 'home.env'
    home_env.write_text('DEEPSEEK_API_KEY=sk-home\n', encoding='utf-8')
    monkeypatch.setattr(lb, '_PROJECT_ENV_FILE', proj_env)
    monkeypatch.setattr(os.path, 'expanduser', lambda p: str(home_env) if p == '~/.env' else p)
    with pytest.raises(LLMBackendError):
        lb._load_api_key()
    proj_env.write_text('MANGPAI_LLM_API_KEY=sk-proj\n', encoding='utf-8')
    assert lb._load_api_key() == 'sk-proj'


def test_key_missing_error_names_vars(clean_env):
    with pytest.raises(LLMBackendError, match='MANGPAI_LLM_API_KEY'):
        lb._load_api_key()


# ---------------------------------------------------------------- 成本估算降级

def test_unknown_model_cost_none(clean_env):
    """未知 provider/模型 cost_cny=None（未计价），不再误导性 ¥0。"""
    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-x')
    clean_env.setenv('MANGPAI_LLM_MODEL', 'qwen-local')
    captured = _capture(clean_env)
    resp = call_deepseek('S', 'U')
    assert resp['cost_cny'] is None
    assert resp['model'] == 'qwen-local'


def test_format_reading_unpriced_label():
    """展示层：cost_cny=None → 「未计价」；DeepSeek 计价路径显示不变。"""
    data = {dim: {'conclusion': 'x', 'basis': [], 'confidence': '中'}
            for dim in ('性格', '事业', '财运', '婚姻', '应期', '迁移', '相貌')}
    backend = {'model': 'qwen-local', 'usage': {}, 'cost_cny': None,
               'price_tier': 'offpeak', 'elapsed_s': 0.0}
    out = format_reading(data, {'ok': True, 'violations': []}, backend)
    assert '未计价' in out and '¥0.0000' not in out
    backend['cost_cny'] = 0.0123
    out = format_reading(data, {'ok': True, 'violations': []}, backend)
    assert 'cost≈¥0.0123' in out


# ---------------------------------------------------------------- 通用开关别名

def test_use_llm_alias(clean_env):
    """MANGPAI_USE_LLM 通用别名优先；FEISHU_USE_LLM 保兼容，缺省关闭。"""
    assert feishu_service.use_llm_default() is False
    clean_env.setenv('FEISHU_USE_LLM', '0')
    assert feishu_service.use_llm_default() is False
    clean_env.setenv('MANGPAI_USE_LLM', '1')
    assert feishu_service.use_llm_default() is True  # 新名优先
    clean_env.setenv('MANGPAI_USE_LLM', '0')
    assert feishu_service.use_llm_default() is False


def test_global_switch_off_blocks_backend(clean_env):
    """缺省及常见关闭写法均在真实网络入口前阻断。"""
    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-not-sent')
    captured = _capture(clean_env)
    for value in (None, '0', 'false', 'off', 'no', ''):
        if value is None:
            clean_env.delenv('MANGPAI_USE_LLM', raising=False)
        else:
            clean_env.setenv('MANGPAI_USE_LLM', value)
        with pytest.raises(LLMBackendError, match='未启用'):
            call_deepseek('S', 'U')
    assert captured == []


def test_placeholder_or_empty_key_never_sent(clean_env):
    captured = _capture(clean_env)
    for key in ('', 'your-api-key-here', 'xxx'):
        clean_env.setenv('MANGPAI_LLM_API_KEY', key)
        with pytest.raises(LLMBackendError):
            call_deepseek('S', 'U')
    assert captured == []


def test_structured_reading_respects_global_switch(clean_env):
    from mangpai.subjective.llm_channel import render_structured_reading

    clean_env.setenv('MANGPAI_LLM_API_KEY', 'sk-not-sent')
    captured = _capture(clean_env)
    clean_env.setenv('MANGPAI_USE_LLM', '0')
    out = render_structured_reading({'bazi': {}, 'input': {}})
    assert out.startswith('[LLM 不可用')
    assert captured == []


def test_env_file_settings_and_switch(clean_env, tmp_path):
    f = tmp_path / 'full.env'
    content = (
        'MANGPAI_LLM_API_KEY=sk-file\n'
        'MANGPAI_LLM_BASE_URL=http://localhost:11434/v1/chat/completions\n'
        'MANGPAI_LLM_MODEL=qwen-local\n'
        'MANGPAI_LLM_THINKING=0\n'
        'MANGPAI_USE_LLM=1\n'
    )
    f.write_text(content, encoding='utf-8')
    clean_env.setenv('MANGPAI_LLM_ENV_FILE', str(f))
    captured = _capture(clean_env)
    clean_env.delenv('MANGPAI_USE_LLM')
    call_deepseek('S', 'U')
    req = captured[0][0]
    assert req.full_url == 'http://localhost:11434/v1/chat/completions'
    body = json.loads(req.data)
    assert body['model'] == 'qwen-local'
    assert 'thinking' not in body and 'reasoning_effort' not in body

    f.write_text(content.replace('MANGPAI_USE_LLM=1', 'MANGPAI_USE_LLM=0'),
                 encoding='utf-8')
    with pytest.raises(LLMBackendError, match='未启用'):
        call_deepseek('S', 'U')
    assert len(captured) == 1


def test_custom_endpoint_does_not_inherit_deepseek_key(clean_env):
    clean_env.setenv('DEEPSEEK_API_KEY', 'sk-old')
    clean_env.setenv('MANGPAI_LLM_BASE_URL', 'http://localhost:8000/v1/chat/completions')
    captured = _capture(clean_env)
    with pytest.raises(LLMBackendError, match='自定义端点'):
        call_deepseek('S', 'U')
    assert captured == []


def test_legacy_narrative_respects_global_switch(clean_env):
    import mangpai.subjective.narrative as narr

    called = []
    real_call = narr._call_llm
    clean_env.setattr(narr, '_call_llm', lambda *a, **k: called.append((a, k)))
    clean_env.setenv('MANGPAI_USE_LLM', '0')
    out = narr.render_hao_narrative({
        'bazi': {'year': '甲子', 'month': '乙丑', 'day': '丙寅', 'hour': '丁卯'},
    }, call_llm=True)
    assert called == []
    assert '【八字】' in out
    with pytest.raises(RuntimeError, match='未启用'):
        real_call('S', 'U')


# ---------------------------------------------------------------- narrative 遗留通道标注

def test_narrative_marked_legacy():
    """narrative._call_llm 已标注遗留通道（第二家硬绑 provider 处置=标注）。"""
    import mangpai.subjective.narrative as narr
    assert '遗留通道' in narr._call_llm.__doc__
    assert '遗留通道' in narr.__doc__
