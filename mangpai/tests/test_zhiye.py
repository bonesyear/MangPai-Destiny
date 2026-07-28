"""zhiye 职业象法测试 - 最低分阈值 fallback + M2 基础职业类目。

验证：七桶（医生/教师/律师/商人/军政，外加会计/演艺）取最高分定位职业，
但最高分低于阈值（_MIN_SCORE_THRESHOLD=6）时各桶均为弱信号共现、不足成象，
不硬塞最像的一桶——M2 起 fallback 升格为合法第一输出：
  1. 基础职业类目命中（段氏《中级》体力取财：比劫/禄神做功+效率低=农民民工
     阶层；严重破财凶向=无业）-> laborer/unemployed；
  2. 未命中 -> 「未分类」+ 最高分桶名提示（hint_bucket/hint_label）。

校准（《命理珍宝》郝金阳10例端到端）：
  非标命局（乞丐/坐牢/破财/找二婚）最高分≤5 -> fallback 区（无业/未分类）；
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
    """最低分阈值：最高分 < 阈值 -> fallback 区（M2：基础类目/未分类+hint）。"""

    def test_threshold_is_6(self):
        assert _MIN_SCORE_THRESHOLD == 6

    def test_qigai_unemployed(self):
        # 乞丐：merchant5 < 6 -> 非商人；比劫夺财 severe（清家荡产）-> 无业（M2）
        r = _run(QIGAI)
        assert r['fallback_no_clear'] is True
        assert max(r['scores'].values()) < _MIN_SCORE_THRESHOLD
        assert r['primary'] == 'unemployed'
        assert r['primary_label'] == '无业'
        assert r['base_career']['bucket'] == 'unemployed'

    def test_zuolao_unclassified(self):
        # 贪财坐牢：teacher4 < 6 -> 非教师；凶向命局不判体力劳动者 -> 未分类+hint
        r = _run(ZUOLAO)
        assert r['fallback_no_clear'] is True
        assert r['primary'] == ''
        assert r['primary_label'] == '未分类'
        assert r['hint_bucket'] == 'teacher'
        assert r['hint_label'] == '教师/教育'

    def test_pocai_unemployed(self):
        # 官司破财（清家荡产）：merchant4 < 6 -> 非商人；比劫夺财 severe -> 无业
        r = _run(POCAI)
        assert r['fallback_no_clear'] is True
        assert r['primary'] == 'unemployed'
        assert r['primary_label'] == '无业'

    def test_laborer_base_career(self):
        # 找二婚：七桶未成象(top3<6)，禄神当财+比劫做功+小康 -> 体力劳动者（偏农）
        r = _run(ZHAOERHUN)
        assert r['fallback_no_clear'] is True
        assert r['primary'] == 'laborer'
        assert '体力劳动者' in r['primary_label']
        assert r['base_career']['bucket'] == 'laborer'
        assert r['base_career']['hint'] == '农'

    def test_real_profession_not_suppressed(self):
        # 真职业最高分≥6，不被阈值抑制（七桶照常，不进基础类目）
        assert _run(LIFANDING)['primary'] == 'lawyer'      # 律师7
        assert _run(YANXISHAN)['primary'] == 'military'    # 军警10
        assert _run(YANYUAN)['primary'] == 'performer'     # 演艺7
        for case in (LIFANDING, YANXISHAN, YANYUAN):
            r = _run(case)
            assert r['fallback_no_clear'] is False
            assert r['base_career'] == {}
            assert max(r['scores'].values()) >= _MIN_SCORE_THRESHOLD

    def test_fallback_desc_carries_top_score(self):
        r = _run(ZUOLAO)  # 未分类（非基础类目）desc 携带最高分与 hint
        top = max(r['scores'].values())
        assert f'各桶最高分{top}<{_MIN_SCORE_THRESHOLD}' in r['desc']
        assert '倾向参考：教师/教育' in r['desc']

    def test_incomplete_pillars_returns_empty(self):
        r = classify_zhiye('甲', ['甲'], ['子'])
        assert r['primary'] == ''
        assert r['primary_label'] == ''
        assert r['fallback_no_clear'] is False
