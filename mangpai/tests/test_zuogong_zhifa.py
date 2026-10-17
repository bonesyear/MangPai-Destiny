# -*- coding: utf-8 -*-
"""批D 哨兵：zuogong_confirm _tiyong_of 食伤双口径 + 制法效率分级。

书证：
- 体用：理象学:5288-5296「如一定区分它们，则食神更近于体，伤官则接近于用」
  ——_tiyong_of 伤官归用、食神归体（与 objective/tiyong.py _NEUTRAL_BIAS
  食神偏体/伤官偏用合书口径对齐；旧实现食伤全归体，丢失「伤官接近于用」）。
- 制法效率：理象学:7462-7489 合制排序——巳申最高；卯戌/卯申/午亥/巳酉次
  （也很高）；子丑/寅丑略差；寅亥/辰酉/午戌/卯未/亥未较低；午未合两字相生
  不制。初级:322-324「子午是力量相当的对冲，是能量的湮灭，效率不高」——
  水火字数相等（双方势力相当的工程近似）时子午冲标「湮灭」。
"""
from mangpai.subjective.zuogong_confirm import _tiyong_of, analyze_zuogong


class TestTiyongShishangSplit:
    def test_shangguan_gui_yong(self):
        assert _tiyong_of('甲', '丁') == '用'   # 甲日丁=伤官（异性我生）
        assert _tiyong_of('甲', '午') == '用'   # 午本气丁=伤官（地支取本气）

    def test_shishen_gui_ti(self):
        assert _tiyong_of('甲', '丙') == '体'   # 甲日丙=食神（同性我生）
        assert _tiyong_of('甲', '巳') == '体'   # 巳本气丙=食神

    def test_other_categories_unchanged(self):
        assert _tiyong_of('甲', '庚') == '用'   # 七杀
        assert _tiyong_of('甲', '壬') == '体'   # 偏印
        assert _tiyong_of('甲', '寅') == '体'   # 比劫
        assert _tiyong_of('甲', '辰') == '用'   # 财


def _wa(*a):
    return analyze_zuogong(*a)['work_actions']


class TestZhifaEfficiencyTags:
    def test_sishen_he_tagged_highest(self):
        # 巳申合效率最高（理象学:7462）；巳申对兼有刑/破，S1 去重后地支合降级
        # 为辅助，但标签仍打在原地支合动作上
        wa = _wa('丙', '巳', '庚', '寅', '辛', '申', '壬', '子')
        hits = [a for a in wa if a.get('type') == '地支合'
                and a.get('zhifa_efficiency') == '最高']
        assert hits, '巳申合应标最高'

    def test_maoxu_he_tagged_high(self):
        wa = _wa('甲', '戌', '丙', '巳', '壬', '卯', '癸', '申')
        hits = [a for a in wa if a.get('type') == '地支合'
                and a.get('zhifa_efficiency') == '高']
        assert hits, '卯戌合应标高'

    def test_wuwei_he_tagged_buzhi(self):
        # 午未合两字相生不制（理象学:7489）
        wa = _wa('甲', '午', '丙', '巳', '壬', '未', '癸', '子')
        hits = [a for a in wa if a.get('type') == '地支合'
                and a.get('zhifa_efficiency') == '不制']
        assert hits, '午未合应标不制'

    def test_ziwu_chong_yanmie_when_even(self):
        # 水 4 字（壬壬子子）vs 火 4 字（丙丙午午）力量相当 → 湮灭（初级:322-324）
        wa = _wa('丙', '子', '壬', '子', '丙', '午', '壬', '午')
        hits = [a for a in wa if a.get('type') == '冲'
                and a.get('zhifa_efficiency') == '湮灭']
        assert hits, '力量相当之子午冲应标湮灭'

    def test_ziwu_chong_no_yanmie_when_uneven(self):
        # 水 3 字 vs 火 5 字，一方成势 → 不标湮灭
        wa = _wa('丙', '子', '丙', '午', '丙', '午', '壬', '子')
        hits = [a for a in wa if a.get('type') == '冲'
                and a.get('zhifa_efficiency') == '湮灭']
        assert not hits


class TestZhifaEfficiencyAggregate:
    def test_high_ratio_lifts_low_to_mid(self):
        # 唯一非辅助动作=卯戌合（高）：原动作数阈值判「低」（兜底保留），
        # 高效率制法占比 1/1 ≥1/2 → 升「中」
        r = analyze_zuogong('甲', '戌', '丙', '巳', '壬', '卯', '癸', '申')
        assert r['work_efficiency'] == '中'

    def test_all_low_caps_high_to_mid(self):
        # 子午湮灭×2 + 天干克×2（未分级）共 4 动作，原阈值判「高」；
        # 已分级制法全部低效（湮灭）→ 让位「中」
        r = analyze_zuogong('丙', '子', '壬', '子', '丙', '午', '壬', '午')
        assert r['work_efficiency'] == '中'
