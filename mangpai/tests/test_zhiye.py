"""zhiye 职业象法测试 - 最低分阈值 fallback「无明确职业倾向」。

验证：五桶（医生/教师/律师/商人/军政，外加会计/演艺）取最高分定位职业，
但最高分低于阈值（_MIN_SCORE_THRESHOLD=6）时各桶均为弱信号共现、不足成象，
fallback「无明确职业倾向」而非硬塞最像的一桶。

校准（《命理珍宝》郝金阳10例端到端）：
  非标命局（乞丐/坐牢/破财/找二婚）最高分≤5 -> fallback；
  真职业（律师7/军警10/演艺7/教师7）≥6 -> 保留。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.zhiye import analyze_zhiye, classify_zhiye, _MIN_SCORE_THRESHOLD


# ── 郝金阳断语案例：(名, 天干[年月日时], 地支[年月日时]) ──
QIGAI      = (['壬','癸','壬','丙'], ['子','卯','子','午'])    # 第9期·乞丐
ZUOLAO     = (['戊','戊','戊','甲'], ['戌','午','午','寅'])    # 第14期·贪财坐牢
POCAI      = (['庚','戊','壬','庚'], ['戌','子','午','子'])    # 第23期·官司破财
ZHAOERHUN  = (['壬','癸','壬','甲'], ['子','卯','子','辰'])    # 第23期·找二婚
LIFANDING  = (['壬','壬','庚','辛'], ['子','寅','辰','巳'])    # 第10期·李凡丁(律师)
YANXISHAN  = (['癸','辛','乙','丁'], ['未','酉','酉','丑'])    # 第12期·阎锡山(军警)
YANYUAN    = (['乙','丙','甲','乙'], ['未','戌','子','亥'])    # 第14期·演员(演艺)


def _run(case):
    gans, zhis = case
    return analyze_zhiye(gans[2], gans, zhis)


class TestMinScoreThreshold:
    """最低分阈值：最高分 < 阈值 -> fallback「无明确职业倾向」。"""

    def test_threshold_is_6(self):
        assert _MIN_SCORE_THRESHOLD == 6

    def test_qigai_fallback(self):
        # 乞丐：merchant5 < 6 -> 无明确职业倾向（非商人）
        r = _run(QIGAI)
        assert r['fallback_no_clear'] is True
        assert r['primary'] == ''
        assert r['primary_label'] == '无明确职业倾向'
        assert max(r['scores'].values()) < _MIN_SCORE_THRESHOLD

    def test_zuolao_fallback(self):
        # 贪财坐牢：teacher4 < 6 -> 无明确职业倾向（非教师）
        r = _run(ZUOLAO)
        assert r['fallback_no_clear'] is True
        assert r['primary_label'] == '无明确职业倾向'

    def test_pocai_fallback(self):
        # 官司破财：merchant4 < 6 -> 无明确职业倾向
        r = _run(POCAI)
        assert r['fallback_no_clear'] is True
        assert r['primary_label'] == '无明确职业倾向'

    def test_real_profession_not_suppressed(self):
        # 真职业最高分≥6，不被阈值抑制
        assert _run(LIFANDING)['primary'] == 'lawyer'      # 律师7
        assert _run(YANXISHAN)['primary'] == 'military'    # 军警10
        assert _run(YANYUAN)['primary'] == 'performer'     # 演艺7
        for case in (LIFANDING, YANXISHAN, YANYUAN):
            r = _run(case)
            assert r['fallback_no_clear'] is False
            assert max(r['scores'].values()) >= _MIN_SCORE_THRESHOLD

    def test_fallback_desc_carries_top_score(self):
        r = _run(QIGAI)
        top = max(r['scores'].values())
        assert f'各桶最高分{top}<{_MIN_SCORE_THRESHOLD}' in r['desc']

    def test_incomplete_pillars_returns_empty(self):
        r = classify_zhiye('甲', ['甲'], ['子'])
        assert r['primary'] == ''
        assert r['primary_label'] == ''
        assert r['fallback_no_clear'] is False
