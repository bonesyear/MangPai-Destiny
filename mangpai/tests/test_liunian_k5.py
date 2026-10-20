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
    detect_hechong_yingqi,
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
        # 张克东例：甲寅运第 4 年（1975 乙卯），无刑冲合 → 分看干主事
        # 口径修正（2026-10-17）：起运岁为虚岁，start_year = 出生年+虚岁-1
        # （liunian.py 对齐 jiaoyun.py:277-279；书例 理象学:3916-3922
        # 2005 生 3 虚岁起运→2007）。1932 生 41 虚岁起运 → 1972 起，
        # 1975 = 第 4 年（旧口径错作第 3 年）。
        p = determine_dayun_phase(
            '甲', '寅', [{'gz': '乙卯', 'year': 1975}],
            birth_year=1932, dayun_start_age=41)
        assert p['phase'] == '分看'
        assert p['per_year'][1975] == {'position': 4, 'active': '干'}

    def test_fenkan_zhi_half(self):
        # 甲寅运第 7 年（1978 戊午，与运无刑冲合）→ 分看支主事
        # （口径修正同上：1972 起运，1978 = 第 7 年，旧口径错作第 6 年）
        p = determine_dayun_phase(
            '甲', '寅', [{'gz': '戊午', 'year': 1978}],
            birth_year=1932, dayun_start_age=41)
        assert p['phase'] == '分看'
        assert p['per_year'][1978] == {'position': 7, 'active': '支'}

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


# ── 批O 项1：冲起/冲去/冲开 强弱喜忌分流 marker（书锚：gaoji:19204「力量相当
#    为冲动；弱被强冲为冲去；冲开库墓为冲开」/gaoji:19211「喜用被合来、合动、
#    冲起则吉…忌仇反之」/zhongji:935「当运为冲去，不当运为冲起」/
#    gaoji:17460-17461「凶神入墓冲则发，吉神入墓冲则贫」）。
#    marker 级：chong_type 判定向不变，新增 xiji/xiji_direction/alias 三键。──

class TestChongXijiSplit:
    def test_chongqi_alias_xishen(self):
        # 冲旺·喜用=冲起（gaoji:19211）：庚日身弱（木火财官党众），申金体
        # 旺（月令双申）为喜，流年寅冲申→冲旺·喜，alias 冲起、吉向
        r = classify_chong_semantic(
            '寅', '申', ['丙', '甲', '庚', '丁'], ['寅', '申', '申', '卯'], '庚')
        assert r['chong_type'] == '冲旺'
        assert r['alias'] == '冲起'
        assert r['xiji'] == '喜'
        assert r['xiji_direction'] == '吉向'

    def test_chongqi_alias_dayun_ganyun(self):
        # 流年冲大运·正行干运=运支不当运→又名冲起（zhongji:935）；戊日辰辰辰
        # 土身强，申金食伤为喜→吉向。判定向不动（chong_type 仍冲动）
        r = classify_chong_semantic(
            '寅', '申', ['壬', '癸', '戊', '丙'], ['辰', '卯', '辰', '辰'], '戊',
            dayun_zhi='申', target_location='dayun', phase_active='干')
        assert r['chong_type'] == '冲动'
        assert r['alias'] == '冲起'
        assert r['xiji_direction'] == '吉向'
        assert 'zhongji:935' in r['desc']

    def test_chongkai_xiji_split_ji(self):
        # 墓库冲开·忌：己日从强（火土七党），丑土体党为忌，未冲丑仍判冲开
        # （定向不动），补凶神入墓冲则发（gaoji:17460）marker
        r = classify_chong_semantic(
            '未', '丑', ['丙', '戊', '己', '丙'], ['戌', '辰', '丑', '午'], '己')
        assert r['chong_type'] == '冲开'
        assert '凶神入墓冲则发' in r['desc']
        assert r['xiji_direction'] == '凶向'

    def test_chongkai_xiji_unknown_no_mark(self):
        # 反例（书例五原造，癸卯丙辰己丑乙亥）：扶抑中和→喜忌不明→冲开不附加
        # 喜忌 marker（保守：不明不出，书判发财不受影响）
        r = classify_chong_semantic(
            '未', '丑', ['癸', '丙', '己', '乙'], ['卯', '辰', '丑', '亥'], '己')
        assert r['chong_type'] == '冲开'
        assert '入墓' not in r['desc']
        assert r['xiji_direction'] == '中性'

    def test_chongkai_xiji_split_xi(self):
        # 墓库冲开·喜：庚日身弱（丙丁巳午官旺），丑土印星为喜，未冲丑→冲开+
        # 吉神入墓冲则贫（gaoji:17461）提示；两说酌参故中性
        r = classify_chong_semantic(
            '未', '丑', ['丙', '丁', '庚', '甲'], ['午', '巳', '丑', '寅'], '庚')
        assert r['chong_type'] == '冲开'
        assert '吉神入墓冲则贫' in r['desc']
        assert r['xiji_direction'] == '中性'

    def test_chongqu_xiji_directions(self):
        # 冲去喜忌分流（gaoji:19211「忌仇反之」）：冲大运·支运=当运为冲去
        # （zhongji:935）——运支为喜→凶向；运支为忌→吉向
        r_xi = classify_chong_semantic(
            '寅', '申', ['壬', '癸', '戊', '丙'], ['辰', '卯', '辰', '辰'], '戊',
            dayun_zhi='申', target_location='dayun', phase_active='支')
        assert r_xi['chong_type'] == '冲去'
        assert r_xi['xiji_direction'] == '凶向'  # 申=身强戊日之喜用，冲去喜神
        r_ji = classify_chong_semantic(
            '寅', '申', ['甲', '壬', '戊', '癸'], ['寅', '子', '辰', '亥'], '戊',
            dayun_zhi='申', target_location='dayun', phase_active='支')
        assert r_ji['chong_type'] == '冲去'
        assert r_ji['xiji_direction'] == '吉向'  # 身弱申=食伤为忌，冲去忌神

    def test_chongdong_neutral_no_alias(self):
        # 反例：力量相当之冲动（gaoji:19204）保持中性，不标冲起、无方向
        r = classify_chong_semantic(
            '卯', '酉', ['己', '庚', '甲', '癸'], ['酉', '午', '子', '酉'], '甲')
        assert r['chong_type'] == '冲动'
        assert r['alias'] == ''
        assert r['xiji_direction'] == '中性'


# ── 批O 项5：应期总则「合者见冲为应，冲者见合为应」（zhenbao:690/zhongji:934）
#    marker 级，analyze_liunian_mangpai 每流年附 hechong_yingqi 键（非空才写）。──

class TestHechongHuying:
    def test_he_jian_chong(self):
        # 合者见冲为应：原局子丑六合（年/月），流年午冲子→应期 marker
        ms = detect_hechong_yingqi(
            ['甲', '丙', '戊', '庚'], ['子', '丑', '午', '戌'], '丙', '午')
        assert any(m['huying_type'] == '合者见冲为应' and m['hit'] == '子'
                   and m['source'] == '流年' for m in ms)

    def test_chong_jian_he(self):
        # 冲者见合为应：原局子午六冲（年/日），流年未合午→应期 marker
        ms = detect_hechong_yingqi(
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '己', '未')
        assert any(m['huying_type'] == '冲者见合为应' and m['hit'] == '午'
                   for m in ms)

    def test_dayun_source(self):
        # 大运支同为运岁：原局卯戌六合，大运酉冲卯→source=大运
        ms = detect_hechong_yingqi(
            ['甲', '丙', '戊', '庚'], ['卯', '寅', '戌', '辰'], '', '', '壬', '酉')
        assert any(m['huying_type'] == '合者见冲为应' and m['source'] == '大运'
                   and m['hit'] == '卯' for m in ms)

    def test_no_relation_no_marker(self):
        # 反例：原局六合/六冲皆未被运岁触动→不出（辰冲戌，戌在原局无合）
        ms = detect_hechong_yingqi(
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '庚', '辰')
        assert ms == []

    def test_integrated_in_analyze(self):
        # 集成：analyze_liunian_mangpai 每流年附 hechong_yingqi（additive，
        # 不改 overall/signals——由全套件回归保证）
        out = analyze_liunian_mangpai(
            [{'gz': '丙午', 'year': 2026}],
            ['甲', '丙', '戊', '庚'], ['子', '丑', '午', '戌'], '戊')
        r = out['liunian'][0]
        assert any(m['huying_type'] == '合者见冲为应'
                   for m in r.get('hechong_yingqi', []))
        # 无关流年不写键（最小 diff）
        out2 = analyze_liunian_mangpai(
            [{'gz': '庚辰', 'year': 2000}],
            ['甲', '丙', '戊', '庚'], ['子', '寅', '午', '戌'], '戊')
        assert 'hechong_yingqi' not in out2['liunian'][0]
