"""OpenAI 兼容 LLM 后端（urllib 直连，不引 SDK；默认 DeepSeek）。

供 narrative/llm_channel 等叙事层调用。纯旁路：输出永不回写 compute_all dict。

配置（全部环境变量；未设任何 MANGPAI_LLM_* 变量时请求字段与 DeepSeek 旧版默认一致）：
- MANGPAI_LLM_BASE_URL → 缺省 https://api.deepseek.com/chat/completions
  （可指向任意 OpenAI 兼容端点：Ollama http://localhost:11434/v1/chat/completions、
  vLLM、其他厂商）
- MANGPAI_LLM_API_KEY → DEEPSEEK_API_KEY（仅官方默认端点）→ env 文件
  （MANGPAI_LLM_ENV_FILE 指定；缺省只读项目根 .env，不读 ~/.env）
- MANGPAI_USE_LLM → 缺省 0；1/true/on/yes 才允许外发，兼容 FEISHU_USE_LLM
- MANGPAI_LLM_MODEL → DEEPSEEK_MODEL → deepseek-flash（V4.1 正式 ID；旧名 deepseek-v4-flash）
- MANGPAI_LLM_THINKING=0 → 请求体剔除 thinking 与 reasoning_effort 两字段
  （DeepSeek V4 思考模式/OpenAI o 系参数，严格 OpenAI 兼容服务可能 400；
  缺省=1 即现状：thinking 开启 + reasoning_effort + JSON mode
  response_format={"type": "json_object"}，thinking 计入 output tokens）
- MANGPAI_LLM_REASONING_EFFORT → 缺省 low（仅 thinking 开启时发出）
- MANGPAI_LLM_TIMEOUT / MANGPAI_LLM_RETRIES → 缺省 120 / 2；合法范围 0<t≤600 / 0..5
- MANGPAI_LLM_MAX_TOKENS / MANGPAI_LLM_CONTEXT → 输出上限与可选上下文窗口预检
- 本地、私网 IP 和 .local 端点自动绕过环境代理；响应体限 2MB
- 重试：超时/5xx/429（尊重 Retry-After）/网络错误；总预算限制重试与退避；
  其余 4xx 及 HTTP 200 非 JSON 不重试，直接抛错由上层降级
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

import http.client
import ipaddress
import json
import logging
import math
import os
import time
import urllib.error
import urllib.parse
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
_MAX_RESPONSE = 2_000_000
_logger = logging.getLogger(__name__)

_BJT = timezone(timedelta(hours=8))
# 峰段（北京时间，整点边界）：09:00-12:00、14:00-18:00；其余半价
_PEAK_HOURS = ((9, 12), (14, 18))


class LLMBackendError(Exception):
    """后端调用失败（key 缺失/网络/非 200/返回体异常）——调用方负责降级。"""


def _env_float(name: str, default: float) -> float:
    raw = _env_value(name, '')
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = _env_value(name, '')
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_files() -> list:
    """MANGPAI_LLM_ENV_FILE 指定则只读它；否则只读项目根 .env。"""
    custom = os.environ.get('MANGPAI_LLM_ENV_FILE', '').strip()
    return [custom or str(_PROJECT_ENV_FILE)]


def _env_value(name: str, default=None):
    if name in os.environ:
        return os.environ[name].strip()
    for path in _env_files():
        try:
            with open(path, encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(name + '='):
                        return line.split('=', 1)[1].strip().strip('"').strip("'")
        except OSError:
            continue
        except UnicodeError as e:
            _logger.warning('env 文件编码错误，已跳过: %s (%s)', path, type(e).__name__)
            continue
    return default


def llm_enabled() -> bool:
    value = _env_value('MANGPAI_USE_LLM') or _env_value('FEISHU_USE_LLM') or '0'
    return value.lower() in ('1', 'true', 'on', 'yes')


def _load_api_key(base_url: str = _API_URL) -> str:
    key = _env_value('MANGPAI_LLM_API_KEY')
    if not key and base_url == _API_URL:
        key = _env_value('DEEPSEEK_API_KEY')
    if not key and base_url != _API_URL:
        raise LLMBackendError('自定义端点必须显式设置 MANGPAI_LLM_API_KEY')
    if not key or key.lower().startswith(('your-', 'sk-fake', 'sk-test', 'sk-your')) \
            or key.startswith('<') or key.lower() == 'xxx':
        raise LLMBackendError(
            'MANGPAI_LLM_API_KEY 未设置、为空或为占位符；官方端点可回退 '
            'DEEPSEEK_API_KEY，env 文件只读 MANGPAI_LLM_ENV_FILE 或项目根 .env')
    return key


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


def _bypass_proxy(base_url: str) -> bool:
    try:
        host = (urllib.parse.urlsplit(base_url).hostname or '').rstrip('.').lower()
        if host in ('localhost', '::1') or host.endswith('.local'):
            return True
        return ipaddress.ip_address(host).is_private
    except ValueError:
        return False


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    *,
    model: str | None = None,
    json_mode: bool = True,
    thinking: bool = True,
    reasoning_effort: str | None = None,
    max_tokens: int | None = None,
    timeout: float | None = None,
    retries: int | None = None,
) -> dict:
    """调 OpenAI 兼容 chat completion（默认 DeepSeek），返回
    {'text','usage','cost_cny','price_tier','elapsed_s','model',
     'requested_model','endpoint','thinking'}。model 取响应回显，模型不一致不计价。

    thinking 模式下 temperature 等采样参数无效（API 忽略），不传。
    失败抛 LLMBackendError，由调用方降级（同 narrative._call_llm 契约）。
    env 配置链见模块 docstring。默认不外发，须显式开启 MANGPAI_USE_LLM。
    """
    if not llm_enabled():
        raise LLMBackendError('LLM 未启用；请显式设置 MANGPAI_USE_LLM=1')
    model = (model or _env_value('MANGPAI_LLM_MODEL')
             or _env_value('DEEPSEEK_MODEL') or _DEFAULT_MODEL)
    base_url = _env_value('MANGPAI_LLM_BASE_URL', '') or _API_URL
    if reasoning_effort is None:
        reasoning_effort = _env_value('MANGPAI_LLM_REASONING_EFFORT', '') or 'low'
    if timeout is None:
        timeout = _env_float('MANGPAI_LLM_TIMEOUT', 120.0)
    if retries is None:
        retries = _env_int('MANGPAI_LLM_RETRIES', 2)
    if max_tokens is None:
        max_tokens = _env_int('MANGPAI_LLM_MAX_TOKENS', 8192)
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) \
            or not math.isfinite(timeout) or not 0 < timeout <= 600:
        _logger.warning('MANGPAI_LLM_TIMEOUT 非法，回退 120 秒')
        timeout = 120.0
    if isinstance(retries, bool) or not isinstance(retries, int) or not 0 <= retries <= 5:
        _logger.warning('MANGPAI_LLM_RETRIES 非法，回退 2 次')
        retries = 2
    if isinstance(max_tokens, bool) or not isinstance(max_tokens, int) or not 1 <= max_tokens <= 65536:
        _logger.warning('MANGPAI_LLM_MAX_TOKENS 非法，回退 8192')
        max_tokens = 8192
    context = _env_value('MANGPAI_LLM_CONTEXT', '')
    if context:
        try:
            context = int(context)
            estimated = (len(system_prompt) + len(user_prompt) + 1) // 2
            if context <= 0 or estimated + max_tokens > context:
                raise LLMBackendError(
                    f'上下文不足：估算输入 {estimated} + 输出 {max_tokens} 超过窗口 {context}')
        except ValueError:
            _logger.warning('MANGPAI_LLM_CONTEXT 非法，本次不做发送前窗口检查')
    key = _load_api_key(base_url)
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
    if (_env_value('MANGPAI_LLM_THINKING', '1') or '1') != '0':
        body['reasoning_effort'] = reasoning_effort
        body['thinking'] = {'type': 'enabled' if thinking else 'disabled'}
    if json_mode:
        body['response_format'] = {'type': 'json_object'}
    data = json.dumps(body).encode('utf-8')

    open_request = urllib.request.urlopen
    if _bypass_proxy(base_url):
        open_request = urllib.request.build_opener(urllib.request.ProxyHandler({})).open
    # shortcut: 总预算只约束重试/退避，不能中断滴流式响应；需硬截止时用独立进程隔离
    deadline = time.monotonic() + min(600.0, timeout * (retries + 1))
    last_err: Exception | None = None
    retry_delay = None
    for attempt in range(retries + 1):
        if attempt:
            delay = 2 ** attempt if retry_delay is None else retry_delay
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise LLMBackendError('总超时') from last_err
            time.sleep(min(delay, remaining))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise LLMBackendError('总超时') from last_err
        try:
            req = urllib.request.Request(
                base_url, data=data,
                headers={'Content-Type': 'application/json'}, method='POST')
            req.add_unredirected_header('Authorization', f'Bearer {key}')
        except ValueError as e:
            raise LLMBackendError(f'URL 畸形: {type(e).__name__}') from e
        t0 = time.monotonic()
        t0_wall = time.time()
        retry_delay = None
        try:
            with open_request(req, timeout=min(timeout, remaining)) as resp:
                raw = resp.read(_MAX_RESPONSE + 1)
            if len(raw) > _MAX_RESPONSE:
                raise LLMBackendError('响应过大（超过 2MB）')
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429:
                hint = ('（参数或上下文长度不被接受：请核对 THINKING=0、'
                        '模型上下文窗口和 max_tokens）') if e.code == 400 else ''
                raise LLMBackendError(f'HTTP {e.code}{hint}') from e
            if e.code == 429:
                try:
                    retry_delay = max(0.0, float(e.headers.get('Retry-After', '')))
                except (TypeError, ValueError):
                    retry_delay = None
            last_err = LLMBackendError(f'HTTP {e.code}')
            continue
        except ValueError as e:
            raise LLMBackendError(f'URL 畸形: {type(e).__name__}') from e
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError) as e:
            last_err = LLMBackendError(f'网络错误: {type(e).__name__}')
            continue
        try:
            payload = json.loads(raw.decode('utf-8'))
        except (UnicodeError, ValueError) as e:
            raise LLMBackendError('HTTP 200 但返回体非 JSON') from e
        try:
            msg = payload['choices'][0]['message']
            if not isinstance(msg, dict):
                raise TypeError('message 非对象')
            content = msg.get('content') or ''
            if isinstance(content, list):
                content = ''.join(str(p.get('text') or '') for p in content if isinstance(p, dict))
            usage = payload.get('usage') or {}
            if not isinstance(usage, dict):
                raise TypeError('usage 非对象')
            actual_model = payload.get('model') or model
            cost = _estimate_cost(actual_model, usage, at=t0_wall) \
                if actual_model == model else None
            if not isinstance(content, str) or not content.strip():
                error = LLMBackendError('content 为空或非字符串')
                error.usage = usage
                error.cost_cny = cost
                raise error
            return {
                'text': content,
                'usage': usage,
                'cost_cny': cost,
                'price_tier': _price_tier(t0_wall),
                'elapsed_s': time.monotonic() - t0,
                'model': actual_model,
                'requested_model': model,
                'endpoint': base_url,
                'thinking': body.get('thinking', {}).get('type') == 'enabled',
            }
        except (KeyError, IndexError, TypeError, AttributeError) as e:
            raise LLMBackendError(f'返回体结构异常: {type(e).__name__}') from e
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
