# -*- coding: utf-8 -*-
"""批次20：财命定档的封顶、柱位与阻断边界。"""
import sys
import yaml

from mangpai.engine import MangpaiEngine
sys.path.insert(0, 'mangpai/tests/heldout')
from blind_eval import _bazi_data
from mangpai.subjective.caiming import (
    _detect_guohe_chaiqiao, _detect_zhiku_decai, _pillar_cats,
    assess_caiming_level, classify_caifu_view,
)


def _assess(gans, zhis, level):
    return assess_caiming_level(gans[2], gans, zhis, {'level': level})


def test_f19_caitongguan_and_guohe_caps_are_not_mutually_exempt():
    result = _assess(['庚', '丁', '丁', '癸'], ['寅', '亥', '巳', '卯'], 3)
    assert result['tier'] == '富'
    gans, zhis = ['辛', '庚', '丙', '丁'], ['卯', '子', '申', '酉']
    assert '官统财（官杀当财）' in classify_caifu_view('丙', gans, zhis)['views']
    assert _assess(gans, zhis, 2)['tier'] == '富'


def test_f20_level_four_also_caps_and_does_not_mislabel_path():
    capped = _assess(['庚', '丁', '丁', '癸'], ['寅', '亥', '酉', '卯'], 4)
    assert capped['tier'] == '富'
    clean = _assess(['甲', '丙', '丁', '丙'], ['午', '子', '巳', '午'], 4)
    assert '禄/食伤当财量级有限' not in clean['adjust']


def test_h7_open_tomb_cannot_cross_guohe_cap_at_any_level():
    gans, zhis = ['壬', '甲', '癸', '丁'], ['戌', '辰', '未', '巳']
    tiers = [_assess(gans, zhis, level)['tier'] for level in (1, 2, 3, 4)]
    assert all(tier in ('贫', '小康', '富') for tier in tiers)
    assert tiers == sorted(tiers, key=('贫', '小康', '富', '巨富').index)


def test_h75_yinhuan_does_not_reapply_fucai_blocker():
    result = _assess(['丁', '癸', '丁', '癸'], ['酉', '卯', '卯', '卯'], 3)
    assert result['tier'] == '富'
    assert '封顶小康' not in result['adjust']
    assert not result['blockers']


def test_h77_open_tomb_is_scoped_to_month_pillar():
    gans, zhis = ['乙', '己', '丙', '戊'], ['丑', '丑', '寅', '戌']
    assert not _detect_zhiku_decai('丙', gans, zhis)['found']
    # 月库不冒充开库；独立的年柱开库仍按既有规则上浮，不沿用审查假设的「富」。
    assert _assess(gans, zhis, 3)['tier'] == '巨富'


def test_h77_active_tombs_keep_position_identity(monkeypatch):
    gans, zhis = ['乙', '己', '丙', '戊'], ['丑', '丑', '寅', '戌']
    active = set()

    def capture(*args):
        active.update(args[-1])
        return {}

    monkeypatch.setattr('mangpai.subjective.caiming._detect_guohe_chaiqiao', capture)
    result = classify_caifu_view('丙', gans, zhis)
    assert {'year_zhi', 'month_zhi'} <= active
    assert result['cai_count'] == 2


def test_h78_zhenghe_guard_covers_both_completion_branches(monkeypatch):
    gans, zhis = ['己', '己', '甲', '丙'], ['戌', '申', '巳', '卯']
    cats = _pillar_cats('甲', gans, zhis)
    actions = [{'type': '克', 'from_pos': 'year_zhi', 'to_pos': 'month_zhi'}]
    for completed in (False, True):
        monkeypatch.setattr('mangpai.subjective.caiming._is_zhi_jin',
                            lambda *args, _done=completed, **kwargs: _done)
        result = _detect_guohe_chaiqiao('甲', gans, zhis, cats, actions, set())
        assert not result


def test_yishi_and_chali3_residuals_are_explicit():
    wanted = {'yx-医师', 'yx-贫一生没有富贵'}
    results = {}
    for path in ('mangpai/tests/heldout/cases.yaml', 'mangpai/tests/trainset/cases.yaml'):
        with open(path, encoding='utf-8') as f:
            doc = yaml.safe_load(f)
        cases = doc if isinstance(doc, list) else doc.get('cases', doc)
        if isinstance(cases, dict):
            cases = list(cases.values())
        for case in cases:
            if case.get('id') in wanted:
                results[case['id']] = MangpaiEngine(_bazi_data(case)).compute_all()
    assert results['yx-医师']['caiming']['tier'] != '巨富'
    assert results['yx-贫一生没有富贵']['gongliang']['level'] == 0
