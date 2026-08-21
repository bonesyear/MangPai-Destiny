"""引擎/LLM 通道接线：排盘输入 spec → compute_all 全链 → Markdown 报告。

- 阳历路径走 calc_mangpai_full（吃 D2 入口校验：性别/年份/lon 强制）；
- 四柱直输路径手工合成最小 bazi_data（同 blind_eval._bazi_data 口径，
  无 da_yun → 大运相关键缺省，性别仍必填）；
- LLM 通道默认开（validate='mark'），失败/非 JSON/被拦截 → 降级为
  引擎直出格式化结论（不加 LLM 段），不抛错；
- LLM 输出不落 compute_all dict（通道红线维持）。
"""
from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from mangpai import MangpaiEngine, calc_mangpai_full
from mangpai.feishu.formatter import format_report
from mangpai.subjective.llm_channel import render_structured_reading

# llm_channel 降级/拦截成品的固定前缀（llm_channel.py 契约：降级不抛错，
# 返回带方括号前缀的说明文本）。命中即视为 LLM 不可用 → 引擎直出。
_LLM_FAIL_PREFIXES = ('[LLM 不可用', '[LLM 输出非合法 JSON', '[断语被')

_GAN = '甲乙丙丁戊己庚辛壬癸'
_ZHI = '子丑寅卯辰巳午未申酉戌亥'
_PILLAR_RE = re.compile(f'^[{_GAN}][{_ZHI}]$')


def engine_result_solar(year, month, day, hour, minute, gender, lon) -> Dict[str, Any]:
    return calc_mangpai_full(year, month, day, hour, minute, gender, lon)


def engine_result_pillars(pillars, gender, year: Optional[int] = None) -> Dict[str, Any]:
    """四柱直输：最小 bazi_data。pillars = [年, 月, 日, 时] 各为干支两字。"""
    if len(pillars) != 4 or not all(_PILLAR_RE.match(p) for p in pillars):
        raise ValueError(f'四柱须为 4 组干支（如 戊辰 己未 庚午 丁亥），收到: {pillars}')
    for p in pillars:
        if _GAN.index(p[0]) % 2 != _ZHI.index(p[1]) % 2:
            raise ValueError(f'干支阴阳错配（非六十甲子）: {p}')
    if not gender:
        raise ValueError('性别必填（大运方向依赖性别）')
    bazi_data = {
        'bazi': dict(zip(('year', 'month', 'day', 'hour'), pillars)),
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': gender, 'year': year or 2000},
    }
    return MangpaiEngine(bazi_data).compute_all()


def use_llm_default() -> bool:
    return os.environ.get('FEISHU_USE_LLM', '1').strip() != '0'


def paipan(spec: Dict[str, Any], use_llm: Optional[bool] = None) -> str:
    """spec → Markdown 报告。

    spec: {'kind':'solar', year, month, day, hour, minute, gender, lon, label}
       或 {'kind':'pillars', pillars, gender, year(可选), label}
    """
    if spec['kind'] == 'solar':
        res = engine_result_solar(spec['year'], spec['month'], spec['day'],
                                  spec['hour'], spec['minute'], spec['gender'], spec['lon'])
    else:
        res = engine_result_pillars(spec['pillars'], spec['gender'], spec.get('year'))
    md = format_report(res, meta=spec.get('label', ''))

    if use_llm is None:
        use_llm = use_llm_default()
    if use_llm:
        out = render_structured_reading(res, validate='mark')
        if out.startswith(_LLM_FAIL_PREFIXES):
            md += '\n\n（LLM 通道暂不可用，以上为引擎直出结论）'
        else:
            md += '\n\n**LLM 五维叙述**（validate=mark，违规附注请人工复核）\n' + out
    return md
