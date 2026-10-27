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
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.zuogong_confirm import _tiyong_of, analyze_zuogong


def _dr(*args):
    return detect_relations(*args)['work_actions']


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
    def test_hour_host_discount_follows_high_ratio(self):
        # R5 时支纳主后，巳申合与时干克都保留；四个动作中两个折扣，
        # 既有效率规则最终由高降中，不再沿用时干被过滤时的低档结果。
        r = analyze_zuogong('甲', '戌', '丙', '巳', '壬', '卯', '癸', '申')
        assert any(a['type'] == '地支合' and a['to_pos'] == 'hour_zhi'
                   and not a.get('auxiliary') for a in r['work_actions'])
        assert r['work_efficiency'] == '中'

    def test_all_low_caps_high_to_mid(self):
        # 等势子午冲是互克而非单向冲；低效制法仍按原规则让位「中」。
        r = analyze_zuogong('丙', '子', '壬', '子', '丙', '午', '壬', '午')
        assert r['work_efficiency'] == '中'


class TestR5DirectionAndQualification:
    def test_water_strong_reverses_si_hai(self):
        wa = _dr('壬', '巳', '癸', '午', '壬', '子', '壬', '亥')
        hit = next(a for a in wa if a['type'] == '冲'
                   and {a['from_pos'], a['to_pos']} == {'day_zhi', 'hour_zhi'})
        assert (hit['from_pos'], hit['to_pos']) == ('hour_zhi', 'day_zhi')
        assert not hit.get('auxiliary')

    def test_fire_strong_keeps_si_hai(self):
        wa = _dr('丙', '巳', '丁', '午', '丙', '子', '丁', '亥')
        hit = next(a for a in wa if a['type'] == '冲'
                   and {a['from_pos'], a['to_pos']} == {'day_zhi', 'hour_zhi'})
        assert (hit['from_pos'], hit['to_pos']) == ('day_zhi', 'hour_zhi')
        assert not hit.get('auxiliary')

    def test_metal_wood_cannot_reverse_by_pillar_order(self):
        wa = _dr('甲', '寅', '甲', '申', '甲', '戌', '甲', '子')
        hit = next(a for a in wa if a['type'] == '冲'
                   and {a['from_pos'], a['to_pos']} == {'year_zhi', 'day_zhi'})
        # 理象学:2617-2619 只能金克木，旧审计的“木势强制申”不成立。
        assert (hit['from_pos'], hit['to_pos']) == ('year_zhi', 'day_zhi')

    def test_equal_earth_chong_has_no_fake_direction(self):
        wa = _wa('戊', '辰', '戊', '戌', '戊', '辰', '戊', '戌')
        hit = next(a for a in wa if a['type'] == '冲'
                   and a['from_pos'] == 'year_zhi' and a['to_pos'] == 'month_zhi')
        assert hit['relation_direction'] == 'unknown'
        assert hit['auxiliary'] is True

    def test_hour_is_host_not_global_qi(self):
        # 壬亥、癸午、丁巳、壬子：水强，时支子冲月支午，不降宾宾全局气。
        wa = _wa('丁', '巳', '壬', '亥', '癸', '午', '壬', '子')
        hit = next(a for a in wa if a['type'] == '冲'
                   and a['from_pos'] == 'hour_zhi' and a['to_pos'] == 'month_zhi')
        assert not hit.get('auxiliary')
        assert not hit.get('global_qi')

    def test_self_lu_does_not_create_work(self):
        wa = _wa('甲', '寅', '癸', '卯', '庚', '申', '辛', '未')
        assert not any(a['type'] == '禄' for a in wa)
        wa = _wa('庚', '申', '癸', '未', '丁', '戌', '丙', '酉')
        assert not any(a['type'] == '禄' for a in wa)

    def test_strong_water_side_controls_day(self):
        result = analyze_zuogong('壬', '巳', '癸', '午', '壬', '子', '壬', '亥')
        hit = next(a for a in result['work_actions'] if a['type'] == '冲'
                   and {a['from_pos'], a['to_pos']} == {'day_zhi', 'hour_zhi'})
        assert (hit['from_pos'], hit['to_pos']) == ('hour_zhi', 'day_zhi')
        assert hit in result['passive_work'] and hit not in result['active_work']

    def test_fixed_metal_direction_and_weak_faction(self):
        result = analyze_zuogong('甲', '寅', '甲', '申', '甲', '戌', '甲', '子')
        hit = next(a for a in result['work_actions'] if a['type'] == '冲'
                   and a['from_pos'] == 'year_zhi' and a['to_pos'] == 'day_zhi')
        assert hit['relation_direction'] == 'directed'
        assert hit['auxiliary'] is True and hit['weak_faction'] is True

    def test_premier_binbin_ganke_not_weak(self):
        # 理象学:7332-7336 明言「戊克壬，制去印星，制印得权」。
        result = analyze_zuogong('乙', '未', '戊', '辰', '壬', '戌', '己', '卯')
        hit = next(a for a in result['work_actions'] if a['type'] == '克'
                   and a['from_pos'] == 'year_gan' and a['to_pos'] == 'month_gan')
        assert not hit.get('weak_faction')

    def test_mutual_he_does_not_invent_actor(self):
        wa = _dr('甲', '辰', '甲', '子', '丙', '丑', '庚', '巳')
        hit = next(a for a in wa if a['type'] == '地支合')
        assert (hit['from_pos'], hit['to_pos']) == ('year_zhi', 'month_zhi')
        assert hit['relation_direction'] == 'mutual'

    def test_earth_tie_has_no_directed_work_but_relation_kept(self):
        from mangpai.objective.gongfei import classify_gongshen
        result = analyze_zuogong('戊', '辰', '戊', '戌', '戊', '辰', '戊', '戌')
        chong = [a for a in result['work_actions'] if a['type'] == '冲']
        assert all(a.get('relation_direction') == 'unknown'
                   and a.get('auxiliary') for a in chong)
        # 未知方向仍是辅助关系，不等于 relation_only 或全局无主之宾宾动作。
        gong_shen = classify_gongshen(chong, ['year', 'month'], ['戊', '戊'],
                                      ['戌', '辰'])['gong_shen']
        assert {'year_zhi', 'month_zhi'} <= set(gong_shen)
        assert '制用' not in result['work_types']

    def test_qianlong_natural_direction_without_single_party(self):
        # 理象学:6156-6166 乾隆没有一方之势，子水伤官制主位午火官星。
        result = analyze_zuogong('庚', '午', '辛', '卯', '丁', '酉', '丙', '子')
        hit = next(a for a in result['work_actions'] if a['type'] == '冲'
                   and {a['from_pos'], a['to_pos']} == {'day_zhi', 'hour_zhi'})
        assert (hit['from_pos'], hit['to_pos']) == ('hour_zhi', 'day_zhi')
        assert not hit.get('auxiliary')
        assert hit in result['passive_work']

    def test_tomb_covered_pair_not_normal_ke(self):
        result = analyze_zuogong('庚', '午', '戊', '辰', '己', '未', '丁', '亥')
        hit = next(a for a in result['work_actions']
                   if a['type'] == '克' and a['from_pos'] == 'year_zhi'
                   and a['to_pos'] == 'hour_zhi')
        assert hit['auxiliary'] is True and hit['tomb_covered'] is True
        assert not hit.get('efficiency_discount')
