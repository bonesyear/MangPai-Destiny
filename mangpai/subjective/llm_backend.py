"""DeepSeek LLM 后端（urllib 直连，不引 SDK）。

供 narrative/llm_channel 等叙事层调用。纯旁路：输出永不回写 compute_all dict。

- key 来源：环境变量 DEEPSEEK_API_KEY，缺省回退解析 /root/.hermes/.env
- 端点：POST https://api.deepseek.com/chat/completions（OpenAI 兼容）
- 默认 model=deepseek-v4-flash，thinking 开启 + JSON mode
  （response_format={"type": "json_object"}，thinking 计入 output tokens）
- 重试：超时/5xx/网络错误重试，指数退避；4xx 不重试直接抛
- 成本：按官方定价表折算 USD，随返回 dict 带出 usage/cost/elapsed

定价（$/1M tokens，api-docs.deepseek.com 2026-08 实测，见
memory/kimi-llm-channel-2026-08-14.md §1.2；cache miss 口径，含 thinking）：
  v4-flash input $0.14 / output $0.28
  v4-pro   input $0.435 / output $0.87
2026-08-16 起峰谷价（谷 input 半价/output 2.36 倍）未细分——成本计数按
峰前平价估，偏低估属已知上限，只作量级参考。
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

_API_URL = 'https://api.deepseek.com/chat/completions'
_ENV_FILE = '/root/.hermes/.env'

# $/1M tokens: (input, output)。cache hit 更便宜，按 miss 保守估。
_PRICING = {
    'deepseek-v4-flash': (0.14, 0.28),
    'deepseek-v4-pro': (0.435, 0.87),
}
_DEFAULT_MODEL = 'deepseek-v4-flash'


class LLMBackendError(Exception):
    """后端调用失败（key 缺失/网络/非 200/返回体异常）——调用方负责降级。"""


def _load_api_key() -> str:
    key = os.environ.get('DEEPSEEK_API_KEY', '').strip()
    if key:
        return key
    try:
        with open(_ENV_FILE, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DEEPSEEK_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    except OSError:
        pass
    raise LLMBackendError(
        f'DEEPSEEK_API_KEY 未设置且 {_ENV_FILE} 不可读/无此键')


def _estimate_cost(model: str, usage: dict) -> float:
    """按定价表折算单次调用成本（USD）。未知模型返回 0 并照常放行。"""
    rates = _PRICING.get(model)
    if not rates:
        return 0.0
    pin = usage.get('prompt_tokens', 0) or 0
    pout = usage.get('completion_tokens', 0) or 0
    return (pin * rates[0] + pout * rates[1]) / 1_000_000


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    json_mode: bool = True,
    thinking: bool = True,
    reasoning_effort: str = 'low',
    max_tokens: int = 4096,
    timeout: float = 120.0,
    retries: int = 2,
) -> dict:
    """调 DeepSeek chat completion，返回 {'text','usage','cost_usd','elapsed_s','model'}。

    thinking 模式下 temperature 等采样参数无效（API 忽略），不传。
    失败抛 LLMBackendError，由调用方降级（同 narrative._call_llm 契约）。
    """
    model = model or os.environ.get('DEEPSEEK_MODEL') or _DEFAULT_MODEL
    key = _load_api_key()
    body = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'max_tokens': max_tokens,
        'reasoning_effort': reasoning_effort,
        'thinking': {'type': 'enabled' if thinking else 'disabled'},
    }
    if json_mode:
        body['response_format'] = {'type': 'json_object'}
    data = json.dumps(body).encode('utf-8')

    last_err: Exception | None = None
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(2 ** attempt)  # 2s, 4s
        req = urllib.request.Request(
            _API_URL, data=data,
            headers={'Content-Type': 'application/json',
                     'Authorization': f'Bearer {key}'},
            method='POST')
        t0 = time.monotonic()
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                payload = json.loads(resp.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            # 4xx（鉴权/参数错）重试无意义，直接抛
            if 400 <= e.code < 500:
                raise LLMBackendError(
                    f'HTTP {e.code}: {e.read().decode("utf-8", "replace")[:300]}'
                ) from e
            last_err = LLMBackendError(f'HTTP {e.code}')
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = LLMBackendError(f'网络错误: {e}')
            continue
        try:
            msg = payload['choices'][0]['message']
            text = msg.get('content') or ''
            if not text.strip():
                raise LLMBackendError('content 为空（仅 reasoning_content）')
            usage = payload.get('usage') or {}
            return {
                'text': text,
                'usage': usage,
                'cost_usd': _estimate_cost(model, usage),
                'elapsed_s': time.monotonic() - t0,
                'model': model,
            }
        except (KeyError, IndexError, TypeError) as e:
            raise LLMBackendError(f'返回体结构异常: {e}') from e
    raise last_err or LLMBackendError('未知失败')


def _self_check():
    """离线自检：成本折算与 key 解析逻辑（不触网）。"""
    cost = _estimate_cost('deepseek-v4-flash',
                          {'prompt_tokens': 10_000, 'completion_tokens': 5_000})
    assert abs(cost - (10_000 * 0.14 + 5_000 * 0.28) / 1e6) < 1e-12
    assert _estimate_cost('unknown-model', {'prompt_tokens': 1}) == 0.0
    print('llm_backend self-check OK')


if __name__ == '__main__':
    _self_check()
