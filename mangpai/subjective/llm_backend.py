"""OpenAI 兼容 LLM 后端（urllib 直连，不引 SDK；默认 DeepSeek）。

供 narrative/llm_channel 等叙事层调用。纯旁路：输出永不回写 compute_all dict。

配置（全部环境变量；未设任何 MANGPAI_LLM_* 变量时请求字段与 DeepSeek 旧版默认一致）：
- MANGPAI_LLM_BASE_URL → 缺省 https://api.deepseek.com/chat/completions
  （可指向任意 OpenAI 兼容端点：Ollama http://localhost:11434/v1/chat/completions、
  vLLM、其他厂商）
- MANGPAI_LLM_API_KEY → DEEPSEEK_API_KEY → env 文件
  （MANGPAI_LLM_ENV_FILE 指定；缺省回退链 = 项目根 .env → ~/.env）
- MANGPAI_LLM_MODEL → DEEPSEEK_MODEL → deepseek-flash（V4.1 正式 ID；旧名 deepseek-v4-flash）
- MANGPAI_LLM_THINKING=0 → 请求体剔除 thinking 与 reasoning_effort 两字段
  （DeepSeek V4 思考模式/OpenAI o 系参数，严格 OpenAI 兼容服务可能 400；
  缺省=1 即现状：thinking 开启 + reasoning_effort + JSON mode
  response_format={"type": "json_object"}，thinking 计入 output tokens）
- MANGPAI_LLM_REASONING_EFFORT → 缺省 low（仅 thinking 开启时发出）
- MANGPAI_LLM_TIMEOUT / MANGPAI_LLM_RETRIES → 缺省 120 / 2（本地模型可调大超时）
- 重试：超时/5xx/网络错误重试，指数退避；4xx 不重试直接抛
- 成本：按官方定价表折算人民币（¥/1M tokens），按请求时间（北京时间）自动选峰/谷档，
  随返回 dict 带出 usage/cost/price_tier/elapsed；定价表仅 DeepSeek 有效——
  未知模型/其他 provider 的 cost_cny 显式返回 None（未计价），不显示误导性 ¥0

定价（¥/1M tokens，api-docs.deepseek.com/zh-cn/quick_start/pricing 2026-08-28 复核；
deepseek-flash = V4.1，价格沿用 V4 口径待官网逐项复核；cache miss 口径，含 thinking）：
                 peak            off-peak（半价）
  flash    input ¥3.0 / out ¥9.0   input ¥1.5 / out ¥4.5
  pro      input ¥9.0 / out ¥27.0  input ¥4.5 / out ¥13.5
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
from pathlib import Path

_API_URL = 'https://api.deepseek.com/chat/completions'
# 项目根 .env（mangpai/subjective/llm_backend.py 上三级 = 仓库根）
_PROJECT_ENV_FILE = Path(__file__).resolve().parents[2] / '.env'

# ¥/1M tokens: {'peak': (input, output), 'offpeak': (input, output)}。
# cache hit 更便宜，按 miss 保守估。2026-08-21 人民币口径（官方国内站报价）。
_PRICE = {
    'deepseek-flash': {'peak': (3.0, 9.0), 'offpeak': (1.5, 4.5)},
    'deepseek-v4-flash': {'peak': (3.0, 9.0), 'offpeak': (1.5, 4.5)},  # 旧 ID 别名（兼容历史配置）
    'deepseek-v4-pro': {'peak': (9.0, 27.0), 'offpeak': (4.5, 13.5)},
}
_DEFAULT_MODEL = 'deepseek-flash'

_BJT = timezone(timedelta(hours=8))
# 峰段（北京时间，整点边界）：09:00-12:00、14:00-18:00；其余半价
_PEAK_HOURS = ((9, 12), (14, 18))


class LLMBackendError(Exception):
    """后端调用失败（key 缺失/网络/非 200/返回体异常）——调用方负责降级。"""


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name, '').strip()
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, '').strip()
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_files() -> list:
    """env 文件回退链：MANGPAI_LLM_ENV_FILE 指定则只用它；否则 项目根 .env → ~/.env。"""
    custom = os.environ.get('MANGPAI_LLM_ENV_FILE', '').strip()
    if custom:
        return [custom]
    return [str(_PROJECT_ENV_FILE), os.path.expanduser('~/.env')]


def _load_api_key() -> str:
    key = os.environ.get('MANGPAI_LLM_API_KEY', '').strip()
    if key:
        return key
    key = os.environ.get('DEEPSEEK_API_KEY', '').strip()
    if key:
        return key
    for path in _env_files():
        try:
            with open(path, encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    for name in ('MANGPAI_LLM_API_KEY', 'DEEPSEEK_API_KEY'):
                        if line.startswith(name + '='):
                            return line.split('=', 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
    raise LLMBackendError(
        'MANGPAI_LLM_API_KEY/DEEPSEEK_API_KEY 未设置，且 env 文件回退链'
        '（MANGPAI_LLM_ENV_FILE 指定 → 项目根 .env → ~/.env）不可读/无此键')


def _price_tier(at: float | None = None) -> str:
    """请求时间（epoch 秒，缺省=现在）落在峰段 → 'peak'，否则 'offpeak'。"""
    dt = datetime.fromtimestamp(at if at is not None else time.time(), tz=_BJT)
    return 'peak' if any(h0 <= dt.hour < h1 for h0, h1 in _PEAK_HOURS) else 'offpeak'


def _estimate_cost(model: str, usage: dict, at: float | None = None) -> float | None:
    """按定价表折算单次调用成本（人民币 ¥），按请求时间自动选峰/谷档。

    定价表仅 DeepSeek 有效：未知模型/其他 provider 显式返回 None（未计价），
    展示层标「未计价」，不显示误导性 ¥0（S1）。"""
    rates = _PRICE.get(model)
    if not rates:
        return None
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
    reasoning_effort: str | None = None,
    max_tokens: int = 8192,
    timeout: float | None = None,
    retries: int | None = None,
) -> dict:
    """调 OpenAI 兼容 chat completion（默认 DeepSeek），返回
    {'text','usage','cost_cny','price_tier','elapsed_s','model'}。

    thinking 模式下 temperature 等采样参数无效（API 忽略），不传。
    失败抛 LLMBackendError，由调用方降级（同 narrative._call_llm 契约）。
    env 配置链见模块 docstring。
    """
    model = (model or os.environ.get('MANGPAI_LLM_MODEL')
             or os.environ.get('DEEPSEEK_MODEL') or _DEFAULT_MODEL)
    base_url = os.environ.get('MANGPAI_LLM_BASE_URL', '').strip() or _API_URL
    if reasoning_effort is None:
        reasoning_effort = os.environ.get('MANGPAI_LLM_REASONING_EFFORT', '').strip() or 'low'
    if timeout is None:
        timeout = _env_float('MANGPAI_LLM_TIMEOUT', 120.0)
    if retries is None:
        retries = _env_int('MANGPAI_LLM_RETRIES', 2)
    key = _load_api_key()
    body = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
        'max_tokens': max_tokens,
    }
    # provider 特有参数（DeepSeek V4 thinking/OpenAI o 系 reasoning_effort）：
    # MANGPAI_LLM_THINKING=0 时两字段整体剔除（严格兼容服务可能 400 unknown field）
    if os.environ.get('MANGPAI_LLM_THINKING', '1').strip() != '0':
        body['reasoning_effort'] = reasoning_effort
        body['thinking'] = {'type': 'enabled' if thinking else 'disabled'}
    if json_mode:
        body['response_format'] = {'type': 'json_object'}
    data = json.dumps(body).encode('utf-8')

    last_err: Exception | None = None
    for attempt in range(retries + 1):
        if attempt:
            time.sleep(2 ** attempt)  # 2s, 4s
        req = urllib.request.Request(
            base_url, data=data,
            headers={'Content-Type': 'application/json',
                     'Authorization': f'Bearer {key}'},
            method='POST')
        t0 = time.monotonic()
        t0_wall = time.time()  # 计价按请求发出的实际时段选峰/谷档
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            # 4xx（鉴权/参数错）重试无意义，直接抛
            if 400 <= e.code < 500:
                hint = ''
                if e.code == 400 and base_url != _API_URL:
                    hint = ('（若报错为 unknown field/不支持的参数：该服务不接受 '
                            'thinking/reasoning_effort，请设 MANGPAI_LLM_THINKING=0）')
                raise LLMBackendError(
                    f'HTTP {e.code}: {e.read().decode("utf-8", "replace")[:300]}{hint}'
                ) from e
            last_err = LLMBackendError(f'HTTP {e.code}')
            continue
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            last_err = LLMBackendError(f'网络错误: {e}')
            continue
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            # HTTP 200 但返回体非 JSON（网关错误页/代理拦截/编码异常）：
            # 包装为 LLMBackendError 走重试，禁止 JSONDecodeError 裸穿透（H4 P0）
            last_err = LLMBackendError(
                f'HTTP 200 但返回体非 JSON: {e}; 前 100 字符: {raw[:100]!r}')
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
                'cost_cny': _estimate_cost(model, usage, at=t0_wall),
                'price_tier': _price_tier(t0_wall),
                'elapsed_s': time.monotonic() - t0,
                'model': model,
            }
        except (KeyError, IndexError, TypeError) as e:
            raise LLMBackendError(f'返回体结构异常: {e}') from e
    raise last_err or LLMBackendError('未知失败')


def _self_check():
    """离线自检：成本折算与 key 解析逻辑（不触网）。"""
    usage = {'prompt_tokens': 10_000, 'completion_tokens': 5_000}
    peak = datetime(2026, 8, 18, 10, 0, tzinfo=_BJT).timestamp()    # 北京 10:00 峰
    off = datetime(2026, 8, 18, 20, 0, tzinfo=_BJT).timestamp()     # 北京 20:00 谷
    assert _price_tier(peak) == 'peak' and _price_tier(off) == 'offpeak'
    # 人民币口径（2026-08-21 起）：deepseek-flash 峰 ¥3.0/¥9.0、谷 ¥1.5/¥4.5（/1M tokens）
    assert abs(_estimate_cost('deepseek-flash', usage, at=peak)
               - (10_000 * 3.0 + 5_000 * 9.0) / 1e6) < 1e-12
    assert abs(_estimate_cost('deepseek-flash', usage, at=off)
               - (10_000 * 1.5 + 5_000 * 4.5) / 1e6) < 1e-12
    # 旧 ID 别名仍可计价（兼容历史配置）
    assert _estimate_cost('deepseek-v4-flash', usage, at=peak) == _estimate_cost('deepseek-flash', usage, at=peak)
    # 未知模型/其他 provider 显式 None（未计价），不显示误导性 ¥0（S1）
    assert _estimate_cost('unknown-model', {'prompt_tokens': 1}) is None
    print('llm_backend self-check OK')


if __name__ == '__main__':
    _self_check()
