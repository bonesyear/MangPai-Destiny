# -*- coding: utf-8 -*-
"""K5: liunian 冲五分合四分（九种语义）+ 大运分看统看 phase。

书例锚点（段氏高级篇 ch12 法则一/二、ch13 法则二）：
  冲五种：冲开（癸卯丙辰己丑乙亥，未冲丑库发财）/冲破（乙巳丙戌丙申丙申，
    满局火克申父星极衰）/冲动（己酉庚午甲子癸酉，卯冲双酉官星调动）/
    冲去（壬子壬寅庚辰辛巳，申衰冲寅旺姐远嫁）/冲旺（旺神激起按喜忌）
  合四种：合留（己酉丁丑癸卯庚申女命，癸合大运戊夫星结婚）/合动（流年合
    大运非配偶星引动）/合去（戊子辛酉壬戌壬子，丙合辛母星虚透丧母）/
    合绊（甲寅癸酉丁丑庚子，子丑贴丁丑年合绊用神）
  分看统看：甲寅运前五年分看（张克东例），己未年甲己合转统看；
    丙午同气附 note 不自动统看（口诀以流年冲合运为统看唯一机械触发）。
"""
import pytest

from mangpai.subjective.liunian import (
    analyze_liunian_mangpai,
    classify_chong_semantic,
    classify_he_semantic,
    determine_dayun_phase,
)


# ── 冲五种（书例原造） ──────────────────────────────────────────────

class TestChongFive:
    def test_chongkai_open_tomb(self):
        # 书例五：癸卯丙辰己丑乙亥，辛未年未冲丑开库，铝制品生意发财
        r = classify_chong_semantic(
            '未', '丑', ['癸', '丙', '己', '乙'], ['卯', '辰', '丑', '亥'], '己')
        assert r['chong_type'] == '冲开'

    def test_chongpo_extreme_weak(self):
        # 书例七：乙巳丙戌丙申丙申，申金父星燥土不生、满局火克，寅冲申为冲破
        r = classify_chong_semantic(
            '寅', '申', ['乙', '丙', '丙', '丙'], ['巳', '戌', '申', '申'], '丙')
        assert r['chong_type'] == '冲破'
        assert r['target_strength'] <= -2

    def test_chongdong_strong_change(self):
        # 书例四：己酉庚午甲子癸酉，双酉官星旺，丁卯年卯冲酉为冲动，调动外省
        r = classify_chong_semantic(
            '卯', '酉', ['己', '庚', '甲', '癸'], ['酉', '午', '子', '酉'], '甲')
        assert r['chong_type'] == '冲动'

    def test_chongqu_weak_liunian_repelled(self):
        # 书例六：壬子壬寅庚辰辛巳，申衰（局中无强根）冲寅旺，为冲去，姐远嫁
        r = classify_chong_semantic(
            '申', '寅', ['壬', '壬', '庚', '辛'], ['子', '寅', '辰', '巳'], '庚')
        assert r['chong_type'] == '冲去'
        assert '流年字自去' in r['desc']

    def test_chongwang_stir_jishen(self):
        # 冲旺：所冲旺、流年支有力（有根）且喜忌可判 → 激起。
        # 庚金身弱，卯财旺而为忌，流年酉（局中有根）冲卯 → 冲旺忌神发凶
        r = classify_chong_semantic(
            '酉', '卯', ['壬', '癸', '庚', '辛'], ['亥', '卯', '卯', '酉'], '庚')
        assert r['chong_type'] == '冲旺'
        assert '忌神' in r['desc'] or '用神' in r['desc']

    def test_dayun_phase_gan_dong(self):
        # 流年冲大运且正行干运 → 冲动（提前引动）
        r = classify_chong_semantic(
            '寅', '申', ['壬', '癸', '戊', '丙'], ['辰', '卯', '辰', '辰'], '戊',
            dayun_zhi='申', target_location='dayun', phase_active='干')
        assert r['chong_type'] == '冲动'

    def test_dayun_phase_zhi_qu(self):
        # 流年冲大运且正行支运 → 冲去（运支当令怕冲崩）
        r = classify_chong_semantic(
            '寅', '申', ['壬', '癸', '戊', '丙'], ['辰', '卯', '辰', '辰'], '戊',
            dayun_zhi='申', target_location='dayun', phase_active='支')
        assert r['chong_type'] == '冲去'


# ── 合四种（书例原造） ──────────────────────────────────────────────

class TestHeFour:
    def test_heliu_dayun_spouse(self):
        # 书例一：己酉丁丑癸卯庚申女命，癸酉年癸合大运戊土夫星，合留结婚
        r = classify_he_semantic(
            '天干合', '戊', ['己', '丁', '癸', '庚'], ['酉', '丑', '卯', '申'], '癸',
            target_location='dayun', gender='女')
        assert r['he_type'] == '合留'

    def test_hedong_dayun_non_spouse(self):
        # 流年合大运非配偶星 → 合动（引动大运所主）。亥为丁之正官，
        # 男命官非配偶星
        r = classify_he_semantic(
            '六合', '亥', ['丁', '壬', '丁', '辛'], ['未', '子', '巳', '亥'], '丁',
            target_location='dayun', gender='男')
        assert r['he_type'] == '合动'

    def test_hequ_weak_gan(self):
        # 书例三：戊子辛酉壬戌壬子，辛母星酉根被戌穿坏而虚，丙辰年丙合辛为合去
        r = classify_he_semantic(
            '天干合', '辛', ['戊', '辛', '壬', '壬'], ['子', '酉', '戌', '子'], '壬')
        assert r['he_type'] == '合去'

    def test_heban_adjacent(self):
        # 书例二：甲寅癸酉丁丑庚子，子丑相贴，丁丑年流年丑合原局子为合绊
        r = classify_he_semantic(
            '六合', '子', ['甲', '癸', '丁', '庚'], ['寅', '酉', '丑', '子'], '丁',
            target_idx=3)
        assert r['he_type'] == '合绊'

    def test_heban_priority_over_qu(self):
        # 相贴优先于衰（书例二 target 丑偏弱仍论合绊不论合去）
        r = classify_he_semantic(
            '六合', '丑', ['甲', '癸', '丁', '庚'], ['寅', '酉', '丑', '子'], '丁',
            target_idx=2)
        assert r['he_type'] == '合绊'

    def test_gender_default_no_spouse(self):
        # gender 缺省 → 不误判配偶星（合留不触发）
        r = classify_he_semantic(
            '天干合', '戊', ['己', '丁', '癸', '庚'], ['酉', '丑', '卯', '申'], '癸',
            target_location='dayun')
        assert r['he_type'] == '合动'


# ── 分看统看（书例：张克东 / 丙午统看例） ────────────────────────────

class TestDayunPhase:
    def test_fenkan_gan_half(self):
        # 张克东例：甲寅运第 3 年（1975 乙卯），无刑冲合 → 分看干主事
        p = determine_dayun_phase(
            '甲', '寅', [{'gz': '乙卯', 'year': 1975}],
            birth_year=1932, dayun_start_age=41)
        assert p['phase'] == '分看'
        assert p['per_year'][1975] == {'position': 3, 'active': '干'}

    def test_fenkan_zhi_half(self):
        # 甲寅运第 6 年（1978 戊午，与运无刑冲合）→ 分看支主事
        p = determine_dayun_phase(
            '甲', '寅', [{'gz': '戊午', 'year': 1978}],
            birth_year=1932, dayun_start_age=41)
        assert p['phase'] == '分看'
        assert p['per_year'][1978] == {'position': 6, 'active': '支'}

    def test_tongkan_on_liunian_he(self):
        # 张克东例转统看：己未年甲己合 → 十年统看
        p = determine_dayun_phase(
            '甲', '寅', [{'gz': '己未', 'year': 1979}],
            birth_year=1932, dayun_start_age=41)
        assert p['phase'] == '统看'
        assert p['active'] == '干支'
        assert '甲己' in p['reason'] or '五合' in p['reason']

    def test_tongkan_on_liunian_chong(self):
        p = determine_dayun_phase(
            '戊', '申', [{'gz': '甲寅', 'year': 1998}],
            birth_year=1952, dayun_start_age=40)
        assert p['phase'] == '统看'

    def test_same_qi_note_no_auto_tongkan(self):
        # 丙午同气：不自动统看（甲寅反例），附 note 提示人工酌定
        p = determine_dayun_phase(
            '丙', '午', [{'gz': '戊辰', 'year': 1928}],
            birth_year=1888, dayun_start_age=36)
        assert p['phase'] == '分看'
        assert p['same_qi'] is True
        assert '同气' in p['note']

    def test_no_anchor(self):
        p = determine_dayun_phase('庚', '辰', [{'gz': '丙子'}])
        assert p['phase'] == '分看'
        assert p['per_year'] == {}


# ── 集成：analyze_liunian_mangpai 输出九种语义 + phase ───────────────

class TestIntegration:
    def test_relations_enriched(self):
        # 流年庚辰冲原局戌（墓库）→ zhi_relations 附 chong_semantic=冲开
        out = analyze_liunian_mangpai(
            [{'gz': '庚辰', 'year': 2000}],
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '戊',
        )
        rels = out['liunian'][0]['zhi_relations']
        chong = [r for r in rels if r['type'] == '冲']
        assert chong and chong[0]['chong_semantic']['chong_type'] == '冲开'

    def test_dayun_phase_output(self):
        out = analyze_liunian_mangpai(
            [{'gz': '己未', 'year': 1979}],
            ['壬', '己', '癸', '辛'], ['申', '酉', '巳', '酉'], '癸',
            current_dayun={'gz': '甲寅', 'start_age': 41, 'end_age': 51},
            birth_year=1932,
        )
        assert out['dayun_phase']['phase'] == '统看'
        # 流年-大运天干合附 he_semantic
        inter = out['liunian'][0]['dayun_interaction']
        he = [i for i in inter if i['type'] == '天干合']
        assert he and he[0]['he_semantic']['he_type'] in (
            '合留', '合动', '合去', '合绊')

    def test_chongpo_adds_negative_signal(self):
        # 冲破 → negative_signals 补记 + overall 吉降吉凶参半（保守两端规则）
        out = analyze_liunian_mangpai(
            [{'gz': '庚寅', 'year': 1998}],
            ['乙', '丙', '丙', '丙'], ['巳', '戌', '申', '申'], '丙',
        )
        r = out['liunian'][0]
        assert any('冲破' in s for s in r['negative_signals'])

    def test_no_dayun_no_phase_key(self):
        out = analyze_liunian_mangpai(
            [{'gz': '甲子', 'year': 1984}],
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '戊',
        )
        assert 'dayun_phase' not in out

    def test_backward_compat_fields(self):
        # 旧字段（overall/ji_count/summary/dayun_interaction）保持原样存在
        out = analyze_liunian_mangpai(
            [{'gz': '甲子', 'year': 1984}, {'gz': '乙丑', 'year': 1985}],
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '戊',
            current_dayun={'gz': '丁卯'},
        )
        assert out['summary'].startswith('共2年')
        assert 'ji_count' in out and 'xiong_count' in out
        assert 'overall' in out['liunian'][0]
