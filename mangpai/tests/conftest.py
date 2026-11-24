import os
import urllib.parse
import urllib.request

import pytest

from mangpai.subjective import llm_backend


@pytest.fixture(autouse=True)
def _isolated_test_environment(monkeypatch):
    monkeypatch.setenv('MANGPAI_USE_LLM', '0')
    for name in tuple(os.environ):
        if name.startswith(('MANGPAI_LLM_', 'DEEPSEEK_', 'ANTHROPIC_')):
            monkeypatch.delenv(name, raising=False)
    for name in ('FEISHU_USE_LLM', 'FEISHU_VERIFICATION_TOKEN'):
        monkeypatch.delenv(name, raising=False)
    original_env_files = llm_backend._env_files
    original_project_env = llm_backend._PROJECT_ENV_FILE

    def isolated_env_files():
        if os.environ.get('MANGPAI_LLM_ENV_FILE') \
                or llm_backend._PROJECT_ENV_FILE != original_project_env:
            return original_env_files()
        return []

    monkeypatch.setattr(llm_backend, '_env_files', isolated_env_files)

    real_urlopen = urllib.request.urlopen

    def guarded_urlopen(request, *args, **kwargs):
        url = getattr(request, 'full_url', request)
        hostname = urllib.parse.urlparse(url).hostname
        if hostname not in ('127.0.0.1', 'localhost', '::1'):
            raise AssertionError(f'测试禁止非本机网络请求: {hostname or "未知主机"}')
        return real_urlopen(request, *args, **kwargs)

    monkeypatch.setattr(urllib.request, 'urlopen', guarded_urlopen)
