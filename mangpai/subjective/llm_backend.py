"""DeepSeek LLM 后端（urllib 直连，不引 SDK）。

供 narrative/llm_channel 等叙事层调用。纯旁路：输出永不回写 compute_all dict。

- key 来源：环境变量 DEEPSEEK_API_KEY，缺省回退解析 /root/.hermes/.env
- 端点：POST https://api.deepseek.com/chat/completions（OpenAI 兼容）
- 默认 model=deepseek-v4-flash，thinking 开启 + JSON mode
  （response_format={"type": "json_object"}，thinking 计入 output tokens）
- 重试：超时/5xx/网络错误重试，指数退避；4xx 不重试直接抛
- 成本：按官方定价表折算人民币（¥/1M tokens），按请求时间（北京时间）自动选峰/谷档，
  随返回 dict 带出 usage/cost/price_tier/elapsed

定价（¥/1M tokens，api-docs.deepseek.com/zh-cn/quick_start/pricing 2026-08-21 复核；
cache miss 口径，含 thinking）：
                 peak            off-peak（半价）
  v4-flash input ¥3.0 / out ¥9.0   input ¥1.5 / out ¥4.5
  v4-pro   input ¥9.0 / out ¥27.0  input ¥4.5 / out ¥13.5
峰段（官方：北京时间 09:00-12:00、14:00-18:00），其余时段半价。
2026-08-16 峰谷价生效；历史批次成本（如 2026-08-18 五轮批跑）按当时美元口径计，不回算。
2026-08-21 改人民币口径（官方国内站直接人民币报价）；cache hit 另有 0.10/0.05 档未用。
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

_API_URL = 'https://api.deepseek.com/chat/completions'
_ENV_FILE = '/root/.hermes/.env'

# ¥/1M tokens: {'peak': (input, output), 'offpeak': (input, output)}。
# cache hit 更便宜，按 miss 保守估。2026-08-21 人民币口径（官方国内站报价）。
_PRICE = {
    'deepseek-v4-flash': {'peak': (3.0, 9.0), 'offpeak': (1.5, 4.5)},
    'deepseek-v4-pro': {'peak': (9.0, 27.0), 'offpeak': (4.5, 13.5)},
}
_DEFAULT_MODEL = 'deepseek-v4-flash'

_BJT = timezone(timedelta(hours=8))
# 峰段（北京时间，整点边界）：09:00-12:00、14:00-18:00；其余半价
_PEAK_HOURS = ((9, 12), (14, 18))


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


def _price_tier(at: float | None = None) -> str:
    """请求时间（epoch 秒，缺省=现在）落在峰段 → 'peak'，否则 'offpeak'。"""
    dt = datetime.fromtimestamp(at if at is not None else time.time(), tz=_BJT)
    return 'peak' if any(h0 <= dt.hour < h1 for h0, h1 in _PEAK_HOURS) else 'offpeak'


def _estimate_cost(model: str, usage: dict, at: float | None = None) -> float:
    """按定价表折算单次调用成本（人民币 ¥），按请求时间自动选峰/谷档。
    未知模型返回 0 并照常放行。"""
    rates = _PRICE.get(model)
    if not rates:
        return 0.0
    rin, rout = rates[_price_tier(at)]
    pin = usage.get('prompt_tokens', 0) or 0
    pout = usage.get('completion_tokens', 0) or 0
    return (pin * rin + pout * rout) / 1_000_000


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    json_mode: bool = True,
    thinking: bool = True,
    reasoning_effort: str = 'low',
    max_tokens: int = 8192,
    timeout: float = 120.0,
    retries: int = 2,
) -> dict:
    """调 DeepSeek chat completion，返回 {'text','usage','cost_usd','price_tier','elapsed_s','model'}。

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
        t0_wall = time.time()  # 计价按请求发出的实际时段选峰/谷档
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
                'cost_usd': _estimate_cost(model, usage, at=t0_wall),
                'price_tier': _price_tier(t0_wall),
                'elapsed_s': time.monotonic() - t0,
                'model': model,
            }
        except (KeyError, IndexError, TypeError) as e:
            raise LLMBackendError(f'返回体结构异常: {e}') from e
    raise last_err or LLMBackendError('未知失败')


def _self_check():
    """离线自检：成本折算与 key 解析逻辑（不触网）。"""
    from datetime import datetime
    usage = {'prompt_tokens': 10_000, 'completion_tokens': 5_000}
    peak = datetime(2026, 8, 18, 10, 0, tzinfo=_BJT).timestamp()    # 北京 10:00 峰
    off = datetime(2026, 8, 18, 20, 0, tzinfo=_BJT).timestamp()     # 北京 20:00 谷
    assert _price_tier(peak) == 'peak' and _price_tier(off) == 'offpeak'
    # 人民币口径（2026-08-21 起）：v4-flash 峰 ¥3.0/¥9.0、谷 ¥1.5/¥4.5（/1M tokens）
    assert abs(_estimate_cost('deepseek-v4-flash', usage, at=peak)
               - (10_000 * 3.0 + 5_000 * 9.0) / 1e6) < 1e-12
    assert abs(_estimate_cost('deepseek-v4-flash', usage, at=off)
               - (10_000 * 1.5 + 5_000 * 4.5) / 1e6) < 1e-12
    assert _estimate_cost('unknown-model', {'prompt_tokens': 1}) == 0.0
    print('llm_backend self-check OK')


if __name__ == '__main__':
    _self_check()
