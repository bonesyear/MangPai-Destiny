"""郝金阳风格叙事层 (narrative) 测试。

只测无网络的确定性路径：
  - summarize_engine_result：从 dict 抽取关键字段压成一行【引擎结论】；
  - render_hao_narrative(call_llm=False)：组装 system + few-shot + 引擎结论 + 所问 的 prompt 文本；
  - format_fewshot_block / FEWSHOT_EXAMPLES 结构完整。
LLM 实调（call_llm=True）依赖网络与 API key，不在此测。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.prompts.hao_style_fewshot import (
    FEWSHOT_EXAMPLES,
    HAO_STYLE_SYSTEM_PROMPT,
    format_fewshot_block,
)
from mangpai.subjective.narrative import (
    render_hao_narrative,
    summarize_engine_result,
    bundle_case_result,
)


# ---------- few-shot 数据结构 ----------

def test_fewshot_examples_count_and_shape():
    assert len(FEWSHOT_EXAMPLES) == 5
    for ex in FEWSHOT_EXAMPLES:
        assert set(ex) >= {'id', 'bazi', 'engine', 'hao'}
        assert ex['bazi']
        assert ex['engine']
        assert ex['hao']


def test_fewshot_block_three_segments():
    block = format_fewshot_block(FEWSHOT_EXAMPLES)
    # 每例三段，5 例 → 15 段标记
    assert block.count('【八字】') == 5
    assert block.count('【引擎结论】') == 5
    assert block.count('【郝断语】') == 5


def test_system_prompt_has_three_required_parts():
    """角色 / 风格约束 / 推理步骤三段齐备。"""
    assert '郝金阳传人' in HAO_STYLE_SYSTEM_PROMPT  # 角色
    assert '第二人称' in HAO_STYLE_SYSTEM_PROMPT and '先断后理' in HAO_STYLE_SYSTEM_PROMPT  # 风格
    # N2：数字须有出处——「敢下数字」旧口径已废，改为只许下引擎结论中出现的数字
    assert '敢下数字' not in HAO_STYLE_SYSTEM_PROMPT
    assert '数字须有出处' in HAO_STYLE_SYSTEM_PROMPT
    assert '只许下【引擎结论】' in HAO_STYLE_SYSTEM_PROMPT
    # 推理五步
    for step in ('取象', '锁定', '判条件', '应期', '结论'):
        assert step in HAO_STYLE_SYSTEM_PROMPT


def test_fewshot_covers_five_topics():
    ids = [ex['id'] for ex in FEWSHOT_EXAMPLES]
    assert '第1期·生孩子' in ids
    assert '第14期·演员' in ids
    assert '第19期·官员' in ids
    assert '第23期·二婚妻' in ids
    assert '第25期·富翁' in ids


# ---------- summarize_engine_result ----------

def test_summarize_empty_dict():
    assert summarize_engine_result({}) == ''


def test_summarize_bare_engine_output():
    """裸 compute_all() 输出（仅引擎维度）也能压成一行，缺失 subjective 段静默跳过。"""
    er = {
        'bazi': {'year': '戊戌', 'month': '己未', 'day': '乙巳', 'hour': '丁亥'},
        'zuogong': {'work_types': ['制用', '生用'], 'work_level': 2,
                    'work_tier': '双层做功', 'work_efficiency': '中'},
        'gongliang': {'level': 3, 'tier_name': '大富大贵',
                      'zhi_jing': '不净', 'fugui_pinjian': '第三档·大富大贵'},
        'zhengfan': {'configuration': '正局（土旺成势）', 'type': 'zheng'},
        'muku': {'open_tombs': [{'zhi': '戌'}], 'closed_tombs': [],
                 'tomb_relations': []},
        'shensha': {'劫煞': {'in_pillars': ['hour']}},
    }
    line = summarize_engine_result(er)
    assert '做功：制用+生用' in line
    assert 'L3' in line
    assert '正局' in line
    assert '开库戌' in line
    assert '劫煞' in line
    # 无 caiming/guanming/hunyin/zhiye/yingqi → 这些段不出现在行里
    assert '财命' not in line


def test_summarize_enriched_bundle():
    """bundle_case_result 合并后的 enriched dict 抽全维度。"""
    er = {
        'bazi': {'year': '壬子', 'month': '癸卯', 'day': '壬子', 'hour': '甲辰'},
        'zuogong': {'work_types': ['制用'], 'work_level': 1,
                    'work_tier': '单层做功', 'work_efficiency': '中'},
        'gongliang': {'level': 3, 'tier_name': '大富大贵', 'zhi_jing': '不净'},
        'zhengfan': {'configuration': '正局', 'type': 'zheng'},
        'muku': {'open_tombs': [], 'closed_tombs': [],
                 'tomb_relations': [{'from': {'zhi': '子'}}]},
        'shensha': {'羊刃': {'in_pillars': ['year']}},
        'caiming': {'tier': '小康', 'summary': '禄神当财·体力'},
        'guanming': {'is_guanming': True, 'level': {'grade': '中高（处级）'},
                     'summary': '伤食制官杀'},
        'hunyin': {'quality': '差', 'duohun': {'is_duohun': False}, 'summary': '独身之象'},
        'zhiye': {'primary_label': '医生/医疗'},
        'yingqi': {'conclusion': '应期成立', 'liunian_trigger': True},
    }
    line = summarize_engine_result(er)
    assert '财命：小康' in line
    assert '官命：是' in line
    assert '婚姻：差' in line
    assert '职业：医生' in line
    assert '应期：应期成立' in line
    assert '入墓1处' in line


# ---------- render_hao_narrative (call_llm=False 降级路径) ----------

def test_render_prompt_mode_returns_prompt_text():
    er = {
        'bazi': {'year': '戊戌', 'month': '己未', 'day': '乙巳', 'hour': '丁亥'},
        'zuogong': {'work_types': ['制用'], 'work_level': 2,
                    'work_tier': '双层', 'work_efficiency': '中'},
        'gongliang': {'level': 3, 'tier_name': '大富大贵', 'zhi_jing': '不净'},
    }
    out = render_hao_narrative(er, user_question='今年养车怎么样？', call_llm=False)
    # 组装 prompt：含 few-shot 范例 + 引擎结论 + 所问
    assert '【八字】' in out
    assert '【郝断语】' in out
    assert '做功：制用' in out  # 引擎结论注入
    assert '今年养车怎么样' in out  # 所问注入


def test_render_prompt_mode_no_question():
    er = {'bazi': {'year': '壬子'}, 'zuogong': {'work_types': ['制用'], 'work_level': 1}}
    out = render_hao_narrative(er, user_question=None, call_llm=False)
    assert '命主未明问' in out


def test_bundle_case_result_merges_subjective():
    res = {'bazi': {'year': '戊戌'}, 'zuogong': {'work_level': 2}}
    cm = {'tier': '富'}
    gm = {'is_guanming': False}
    hy = {'quality': '差'}
    zy = {'primary_label': '商人'}
    yq = {'conclusion': '成立'}
    er = bundle_case_result(res, cm, gm, hy, zy, yq,
                            dayun=('壬', '戌'), liunian=('戊', '辰', 1988))
    assert er['caiming'] is cm
    assert er['guanming'] is gm
    assert er['hunyin'] is hy
    assert er['zhiye'] is zy
    assert er['yingqi'] is yq
    assert er['dayun_gz'] == '壬戌'
    assert er['liunian_gz'] == '戊辰'
    # 引擎原字段仍保留
    assert er['zuogong']['work_level'] == 2


# ---------- N3：few-shot 口径一致性（2026-07-17 重跑后锁定） ----------

def test_fewshot_caliber_no_yiji_pocai_jump():
    """第1期：引擎结论不得再标「亿级」富档（岁运反局封顶后=小康），
    与郝断「除钱赚不下、两场官司」同向——锁定「富·亿级 vs 破财」口径跳跃已修复。"""
    ex1 = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第1期·生孩子')
    assert '亿' not in ex1['engine']
    assert '小康' in ex1['engine'] and '岁运反局' in ex1['engine']


def test_fewshot_wengweng_reconciled_by_kaiku():
    """第25期：引擎结论以「三库全开·开库运主大发」口径化解
    「原局贫 vs 癸未运发财」静态/运岁错位；郝断语不含精确金额（N2 口径）。"""
    ex5 = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第25期·富翁')
    assert '开库' in ex5['engine'] and '大发' in ex5['engine']
    assert '万' not in ex5['hao'] and '亿' not in ex5['hao']


def test_fewshot_engine_blocks_have_yunsui_context():
    """带运岁的案例，其引擎结论须含运岁干支（郝断数字的出处锚点）。"""
    ex1 = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第1期·生孩子')
    assert '壬戌' in ex1['engine'] and '戊辰' in ex1['engine']
    ex3 = next(e for e in FEWSHOT_EXAMPLES if e['id'] == '第19期·官员')
    assert '辛卯' in ex3['engine'] and '1993' in ex3['engine']


# ---------- N1：生成后数字校验 ----------

import mangpai.subjective.narrative as _narr
from mangpai.subjective.narrative import validate_narrative_numbers, _cn_to_int

_ER = {
    'input': {'year': 1958},
    'bazi': {'year': '戊戌', 'month': '己未', 'day': '乙巳', 'hour': '丁亥'},
    'dayun': {'dayun': [{'gz': '壬戌', 'start_age': 5, 'end_age': 15}]},
    'liunian': [{'gz': '戊辰', 'year': 1988}],
    'zuogong': {'work_level': 2},
    'gongliang': {'level': 3, 'score': 68},
    'summary': '共1步大运；共1流年',
    'caiming': {'tier': '小康', 'summary': '财命层级：小康；功量富档：百万级'},
}


def test_cn_to_int():
    assert _cn_to_int('三') == 3 and _cn_to_int('两') == 2
    assert _cn_to_int('十一') == 11 and _cn_to_int('二十') == 20
    assert _cn_to_int('') is None


def test_validate_year_in_whitelist_ok():
    r = validate_narrative_numbers('你1988年有官司，88年破财。', _ER)
    assert r['ok'], r['violations']


def test_validate_year_not_in_whitelist_flagged():
    r = validate_narrative_numbers('你1993年升官，93年又升。', _ER)
    assert not r['ok']
    assert any(v['kind'] == 'year' for v in r['violations'])


def test_validate_age_and_count():
    r = validate_narrative_numbers('你5岁起运，一生四次婚姻，有五个孩子。', _ER)
    # 5岁在白名单（start_age=5）；4次/5个不在引擎计数（白名单=1,2,3,68）→ 标记
    kinds = [v['kind'] for v in r['violations']]
    assert 'age' not in kinds
    assert kinds.count('count') == 2


def test_validate_amount_always_flagged():
    r = validate_narrative_numbers('你最多时有1800万资产。', _ER)
    assert any(v['kind'] == 'amount' for v in r['violations'])


def test_validate_band_must_match_caiming():
    r = validate_narrative_numbers('你是亿级富命。', _ER)
    assert any(v['kind'] == 'band' for v in r['violations'])
    r2 = validate_narrative_numbers('你是百万级小康命。', _ER)
    assert not any(v['kind'] == 'band' for v in r2['violations'])


def test_render_mark_mode_appends_note(monkeypatch):
    monkeypatch.setattr(_narr, '_call_llm', lambda s, u, model=None: '你1999年升官。')
    out = _narr.render_hao_narrative(_ER, call_llm=True, validate='mark')
    assert '你1999年升官。' in out
    assert '【引擎校验】' in out and '1999年' in out


def test_render_reject_mode_intercepts(monkeypatch):
    monkeypatch.setattr(_narr, '_call_llm', lambda s, u, model=None: '你1999年升官。')
    out = _narr.render_hao_narrative(_ER, call_llm=True, validate='reject')
    assert '拦截' in out and '你1999年升官。' not in out


def test_render_off_mode_skips_validation(monkeypatch):
    monkeypatch.setattr(_narr, '_call_llm', lambda s, u, model=None: '你1999年升官。')
    out = _narr.render_hao_narrative(_ER, call_llm=True, validate='off')
    assert out == '你1999年升官。'


def test_render_clean_text_no_note(monkeypatch):
    monkeypatch.setattr(_narr, '_call_llm', lambda s, u, model=None: '你1988年破财，5岁起运。')
    out = _narr.render_hao_narrative(_ER, call_llm=True, validate='mark')
    assert '【引擎校验】' not in out
