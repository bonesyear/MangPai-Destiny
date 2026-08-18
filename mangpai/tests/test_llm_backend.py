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
    peak = _estimate_cost('deepseek-v4-flash', _U, at=_at(10))
    off = _estimate_cost('deepseek-v4-flash', _U, at=_at(20))
    assert abs(peak - (10_000 * 0.44 + 5_000 * 1.32) / 1e6) < 1e-12
    assert abs(off - (10_000 * 0.22 + 5_000 * 0.66) / 1e6) < 1e-12
    assert abs(peak - 2 * off) < 1e-12  # 谷档=峰档半价


def test_estimate_cost_pro_and_unknown():
    off = _estimate_cost('deepseek-v4-pro', _U, at=_at(20))
    assert abs(off - (10_000 * 0.66 + 5_000 * 1.98) / 1e6) < 1e-12
    assert _estimate_cost('unknown-model', _U) == 0.0
