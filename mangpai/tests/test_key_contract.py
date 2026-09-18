# -*- coding: utf-8 -*-
"""H-fix-6 哨兵：engine 产出键 ↔ selectors 登记键 ↔ payload 键 三方自动契约。

背景（H8 P1 / H11 selectors 机制评估 / H4 zinv 备案）：schools.selectors 是
手工维护的静态元组——engine 新增模块键忘登记 → 进不了 payload 静默丢功能；
selectors 残留 engine 不再产出的键 → 死键；payload 键无消费方 → 透传死数据。
本测试把三方对照固化为自动断言，任何漂移即红（H-fix-5 compute_all 拆分前置哨兵）。

三类断言：
1. engine → selectors 完整性（防漏登记）：engine 全量产出的每个顶层键，
   或在 selectors 登记，或在 INTERNAL_ENGINE_KEYS 显式白名单（集合相等，
   白名单腐化同样报红）。
2. selectors → engine 存在性（防死键）：selectors 登记的每个键，engine 在
   全量供给（注入 dayun）下实际产出；selectors 无重复登记。
3. payload → 消费方（防死键，H4 的 zinv 问题推广）：payload 每个键至少在
   一个消费源（narrative / feishu formatter / llm_prompt / llm_channel /
   prompts 模板）被静态引用，否则须显式备案为 LLM_FEATURE_ONLY_KEYS
   （特征 JSON 直喂）或 RESERVED_KEYS（预留，供未来扩展）。

实测基线（2026-09-18，hfix4c 快照口径）：engine 48 / selectors 41 / payload 41。
"""
import re
from pathlib import Path

import pytest

from mangpai.engine import MangpaiEngine
from mangpai.subjective import build_payload
from mangpai.subjective.schools import MANGPAI_SCHOOL

_REPO_ROOT = Path(__file__).resolve().parents[2]

# 全量供给样本盘：注入 dayun 使条件产出键 dayun_analysis 就位
# （engine.py:492 仅 dy_list 非空才计算；build_payload 缺供时另有
# _synthesize_dayun 合成补供，payload 侧两种路径同键）。
_SAMPLE_BAZI_DATA = {
    'bazi': {'year': '戊辰', 'month': '己未', 'day': '庚午', 'hour': '丁亥'},
    'input': {'year': 1988, 'gender': '男'},
    'dayun': [{'gz': '庚申', 'start_age': 8, 'end_age': 18},
              {'gz': '辛酉', 'start_age': 18, 'end_age': 28}],
}

# 断言 1 白名单：engine 产出但**刻意不进** selectors 的内部键（键: 处置依据）。
# 集合相等断言——engine 新增键未登记、或白名单键不再产出，双向皆红。
INTERNAL_ENGINE_KEYS = {
    'input': '输入回显（calc_bazi_full 原始 input），非分析产物',
    'summary': '规则摘要串（_build_summary，verify_dayun 文案断言消费），非 LLM 特征',
    'relations': '模块间总线（detect_relations 原始做功关系，gongliang/guanming 等内部消费）',
    'direction': 'F1 标注仅模块间透传（engine.py:635 注释），不进 payload',
    'gongshen': '预消化键——narrative 摘要间接消费；selector 排除系批10 A1 刻意防护（H8 P2 备案）',
    'gongmen_wuzhi': '修批A③ 摘除——is_wuzhi 98.8% 恒真零信息量；engine result 键保留存档',
    'jiaoyun_analysis': '批10 A1 刻意排除——扩 LLM 面与 F14 寿元红线反向（F19 收档维持）',
}

# 断言 3 备案 A：无静态消费方、经特征 JSON 全量嵌入直喂 LLM 的基础数据键
# （llm_channel render_structured_reading 把整个 payload JSON 嵌进 user prompt，
# 键清单 _key_manifest 动态枚举——LLM 可自由引用，但代码/prompt 无定点读者）。
LLM_FEATURE_ONLY_KEYS = {
    'chang_sheng': '长生十二宫基础特征，prompt 模板/代码零静态引用，特征 JSON 直喂',
    'narrative': '引擎规则摘要串，全仓零代码读取（仅特征 JSON 透传供 LLM 参考）',
}

# 断言 3 备案 B：预留键——engine 写入 + payload 透传，无任何消费方
# （H4 P1 zinv 备案的显式化；H-fix-5 拆分时参照，勿当死键误删）。
RESERVED_KEYS = {
    'zinv': '预留（供未来扩展）——D6a 设计为纯数据镜像 liuqin 通道；'
            'engine 写入 + payload 透传，prompt/formatter/narrative 零读者（H4 备案）',
}

# 断言 3 消费源：payload 键的静态读者（源码内出现键名即计）。
_CONSUMER_SOURCE_PATHS = (
    'mangpai/subjective/narrative.py',
    'mangpai/feishu/formatter.py',
    'mangpai/subjective/llm_prompt.py',
    'mangpai/subjective/llm_channel.py',
    'mangpai/subjective/prompts/mangpai.md',
)


@pytest.fixture(scope='module')
def engine_result():
    return MangpaiEngine(_SAMPLE_BAZI_DATA).compute_all()


@pytest.fixture(scope='module')
def payload(engine_result):
    return build_payload(engine_result)


def _static_consumer_hit(key: str) -> bool:
    pat = re.compile(r'\b' + re.escape(key) + r'\b')
    for rel in _CONSUMER_SOURCE_PATHS:
        if pat.search((_REPO_ROOT / rel).read_text(encoding='utf-8')):
            return True
    return False


def test_engine_keys_covered_by_selectors(engine_result):
    """断言 1：engine 产出键 = selectors 登记键 ∪ 内部白名单（集合相等）。"""
    engine_keys = set(engine_result.keys())
    selectors = set(MANGPAI_SCHOOL.selectors)
    uncovered = engine_keys - selectors - set(INTERNAL_ENGINE_KEYS)
    assert not uncovered, (
        f'engine 产出键未登记 selectors 且不在内部白名单（漏登记？）: {sorted(uncovered)}')
    stale_whitelist = set(INTERNAL_ENGINE_KEYS) - engine_keys
    assert not stale_whitelist, (
        f'内部白名单键 engine 已不再产出（白名单腐化）: {sorted(stale_whitelist)}')
    leaked = set(INTERNAL_ENGINE_KEYS) & selectors
    assert not leaked, f'内部白名单键被同时登记进 selectors（归类矛盾）: {sorted(leaked)}'


def test_selectors_exist_in_engine(engine_result):
    """断言 2：selectors 登记键 engine 全量供给下实际产出（防死键）。"""
    engine_keys = set(engine_result.keys())
    dead = set(MANGPAI_SCHOOL.selectors) - engine_keys
    assert not dead, f'selectors 登记键 engine 不产出（死键）: {sorted(dead)}'
    assert len(MANGPAI_SCHOOL.selectors) == len(set(MANGPAI_SCHOOL.selectors)), (
        'selectors 存在重复登记')


def test_payload_mirrors_selectors(payload):
    """payload 键集 = selectors 键集（全量供给下无缺漏），键数锁定 41。"""
    assert set(payload.keys()) == set(MANGPAI_SCHOOL.selectors)
    assert len(payload) == 41


def test_payload_keys_have_consumer(payload):
    """断言 3：payload 每个键有静态消费方，或显式备案（特征直喂/预留）。"""
    for key in payload:
        if key in LLM_FEATURE_ONLY_KEYS or key in RESERVED_KEYS:
            continue
        assert _static_consumer_hit(key), (
            f'payload 键 {key!r} 无静态消费方（narrative/formatter/llm_prompt/'
            f'llm_channel/prompts 模板均不引用）——请登记消费者，'
            f'或显式备案入 LLM_FEATURE_ONLY_KEYS / RESERVED_KEYS')


def test_reserved_keys_still_unconsumed(payload):
    """预留键防腐：预留键一旦出现静态消费方，须移出 RESERVED_KEYS 重新归类。"""
    for key in RESERVED_KEYS:
        assert key in payload, f'预留键 {key!r} 已不在 payload（备案腐化）'
        assert not _static_consumer_hit(key), (
            f'预留键 {key!r} 已有静态消费方——请移出 RESERVED_KEYS（预留备案失效）')


def test_feature_only_keys_in_payload(payload):
    """特征直喂备案防腐：备案键须仍在 payload（被摘除则备案失效须同步删）。"""
    for key in LLM_FEATURE_ONLY_KEYS:
        assert key in payload, f'特征直喂备案键 {key!r} 已不在 payload（备案腐化）'
