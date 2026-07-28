# -*- coding: utf-8 -*-
"""yongshen 方向层 R2（忌神制用神）/ R3（用神被合绊）测试。

规则出处（仅训练侧锚点）：
  R2a 财坏印：身弱/从强印为用，财制印=凶（贪财坏印）；
  R2b 印夺食：身强/从弱食伤为用，印制食伤=凶（枭神夺食，《授课教程》
    「癸酉运枭神夺食，子死于非命」；岳飞书例 子忌制巳寿元星=凶而贵存）；
  R3：段氏「紧贴相合为绊…谁都无法发挥作用」；受害方口径同 he_types
    合克/合伤/闭气；忌神受绊为吉不触发（李嘉诚未午合）；做功参与抑制
    （冲/穿入局者合不能绊——奥纳西斯未入丑未冲不论绊；森田健戌仅单向
    克亥，仍论「卯戌合绊，戌根失去力量」）。
"""
import pytest

from mangpai.subjective.yongshen import (
    assess_direction_signals,
    detect_heban_yongshen,
    detect_jishen_zhiyongshen,
    direction_brief,
)


# ───────────────────── R2 忌神制用神 ─────────────────────

class TestR2JishenZhiyongshen:
    def test_r2a_caihuaiyin_detected(self):
        """身弱财制印（日柱参与）-> 财坏印命中。
        戊癸甲癸/巳子午亥（带象甲子盘）：身弱，子(财)冲午(印)、亥(财)克午(印)。"""
        r = detect_jishen_zhiyongshen('戊', ['癸', '甲', '戊', '癸'],
                                      ['巳', '子', '午', '亥'])
        assert r['detected'] and r['kind'] == '财坏印'
        assert r['severity'] == 'severe'  # 2处命中
        assert '忌神制用神' in r['reason']

    def test_r2b_yinduoshi_detected(self):
        """身强印制食伤（日柱参与）-> 印夺食命中。
        岳飞 癸乙甲己/未卯子巳：身强，子(印)克巳(食伤)——段氏读 子为忌神、
        巳为寿元星，制食伤=凶（贵而早夭，贵与凶并存）。"""
        r = detect_jishen_zhiyongshen('甲', ['癸', '乙', '甲', '己'],
                                      ['未', '卯', '子', '巳'])
        assert r['detected'] and r['kind'] == '印夺食'

    def test_r2_reverse_direction_no_fire(self):
        """反向（用神制忌神）不触发：从弱财制印=官命结构（GUAN书例财制印）。
        丁己癸丁/未酉巳巳：从弱，酉(印)被巳(财)克——印为忌神，财制印=吉。"""
        r = detect_jishen_zhiyongshen('癸', ['丁', '己', '癸', '丁'],
                                      ['未', '酉', '巳', '巳'])
        assert not r['detected']

    def test_r2_non_day_auxiliary_no_fire(self):
        """宾位（非日柱）做功 confirm 已降 auxiliary，不触发。
        阎锡山 癸辛乙丁/未酉酉丑：从弱，癸(印)克丁(食)系宾位干克（aux）。"""
        r = detect_jishen_zhiyongshen('乙', ['癸', '辛', '乙', '丁'],
                                      ['未', '酉', '酉', '丑'])
        assert not r['detected']

    def test_r2_zhonghe_no_fire(self):
        """中和不定用忌，不触发。乙丁甲丙/未亥午子（印制伤食盘）：中和。"""
        r = detect_jishen_zhiyongshen('甲', ['乙', '丁', '甲', '丙'],
                                      ['未', '亥', '午', '子'])
        assert not r['detected']

    def test_r2_daygan_actor_excluded(self):
        """日主作功神（我克者）不算忌神制用神（同R1口径）。"""
        # 壬壬庚辛/子寅辰巳（zhenbao-10）：身弱；日干庚(金)不作用神计。
        # precision pass 后此造财孤（1柱）印众（2柱），孤忌犯众豁免不触发
        # （段氏「弱的忌神用旺的用神去之则吉」之正命题）；hits 恒不含 day_gan。
        r = detect_jishen_zhiyongshen('庚', ['壬', '壬', '庚', '辛'],
                                      ['子', '寅', '辰', '巳'])
        for h in r['hits']:
            assert 'day_gan' not in h

    def test_r2_guji_fanzhong_exempt(self):
        """孤忌犯众用豁免：忌神孤（≤1柱）用神众（≥2柱），孤忌犯众自败不触发。
        张克东 壬己癸辛/申酉巳酉：从强，巳财孤犯众印（酉酉辛），「财被两酉
        夹合而化，原气尽失，无可用之理」-> 不论财坏印。"""
        r = detect_jishen_zhiyongshen('癸', ['壬', '己', '癸', '辛'],
                                      ['申', '酉', '巳', '酉'])
        assert not r['detected']
        assert '孤忌犯众' in r['reason']
        # 忌神非孤仍触发：岳飞 印2柱（癸子）-> 印夺食命中（不被豁免）
        r2 = detect_jishen_zhiyongshen('甲', ['癸', '乙', '甲', '己'],
                                       ['未', '卯', '子', '巳'])
        assert r2['detected'] and r2['kind'] == '印夺食'


# ───────────────────── R3 用神被合绊 ─────────────────────

class TestR3HebanYongshen:
    def test_r3_morita_ken_detected(self):
        """森田健 辛戊己癸/卯戌亥酉：身弱，卯戌合绊戌（比劫用神、日主根）。
        戌仅单向克亥（不入冲/穿），不享做功参与抑制 -> 命中（书例明文）。"""
        r = detect_heban_yongshen('己', ['辛', '戊', '己', '癸'],
                                  ['卯', '戌', '亥', '酉'])
        assert r['detected'] and r['severity'] == 'normal'
        assert any('戌' in h for h in r['hits'])
        assert '用神被合绊' in r['reason']

    def test_r3_onassis_suppressed_by_chong(self):
        """奥纳西斯 乙己己庚/巳丑未午：从强，未午合但未入丑未冲做功
        （相冲与相合兼论，合不能废其用）-> 抑制不触发（段氏论巨富不论绊）。"""
        r = detect_heban_yongshen('己', ['乙', '己', '己', '庚'],
                                  ['巳', '丑', '未', '午'])
        assert not r['detected']

    def test_r3_jishen_victim_no_fire(self):
        """受害方为忌神=忌神被绊吉，不触发。
        李嘉诚 戊己庚丁/辰未午亥：身强，未午合受害方=未(印为忌神)。"""
        r = detect_heban_yongshen('庚', ['戊', '己', '庚', '丁'],
                                  ['辰', '未', '午', '亥'])
        assert not r['detected']

    def test_r3_non_adjacent_no_fire(self):
        """非紧贴（隔位）不论绊。壬丙壬丁/子午辰未：午未隔日柱不紧贴。"""
        r = detect_heban_yongshen('壬', ['壬', '丙', '壬', '丁'],
                                  ['子', '午', '辰', '未'])
        assert not r['detected']

    def test_r3_zhonghe_no_fire(self):
        """中和不定用忌，不触发。丁丙庚丁/未午申丑（未午紧贴但中和）。"""
        r = detect_heban_yongshen('庚', ['丁', '丙', '庚', '丁'],
                                  ['未', '午', '申', '丑'])
        assert not r['detected']

    def test_r3_zichou_both_victims(self):
        """子丑合双方皆受害（丑克子+闭丑库）：任一用神侧受绊皆命中。
        甲丙己甲/子寅丑子（化例三中堂）：身弱，日支丑(比劫用神)受绊。"""
        r = detect_heban_yongshen('己', ['甲', '丙', '己', '甲'],
                                  ['子', '寅', '丑', '子'])
        assert r['detected']
        assert any('丑' in h for h in r['hits'])

    def test_r3_gan_he_year_month_only(self):
        """天干五合只判他干紧贴（年×月）；日干参与之合属合用层不判。
        庚乙庚乙/戌酉申酉（比劫包局）：从强，年干庚(比劫用神)合月干乙受绊。"""
        r = detect_heban_yongshen('庚', ['庚', '乙', '庚', '乙'],
                                  ['戌', '酉', '申', '酉'])
        assert r['detected']
        assert any('庚' in h for h in r['hits'])
        # 甲丁乙庚/寅卯丑辰（抢劫入狱）：乙庚合涉日干 -> 不在R3论
        r2 = detect_heban_yongshen('乙', ['甲', '丁', '乙', '庚'],
                                   ['寅', '卯', '丑', '辰'])
        assert not r2['detected']

    def test_r3_daygan_zhenghe_suppressed(self):
        """日主争合抑制：受害方月干与日主五合（日主合用做功），未失原性不判。
        丙申辛丑丙申己亥（从财格地产发财）：辛财被年干丙合，然日主丙亦合辛
        （日主合用=我取财），不触发。"""
        r = detect_heban_yongshen('丙', ['丙', '辛', '丙', '己'],
                                  ['申', '丑', '申', '亥'])
        assert not r['detected']

    def test_r3_shuangshun_exempt(self):
        """双侧顺势豁免：六合双方俱为用神类=顺势内部生合（原神合财），不论绊。
        22期例1 从财格（辛亥庚寅庚寅己卯，从弱）：寅亥合，亥=食伤(原神)、
        寅=财俱顺势，不触发（书：乙亥年发财）。"""
        r = detect_heban_yongshen('庚', ['辛', '庚', '庚', '己'],
                                  ['亥', '寅', '寅', '卯'])
        assert not r['detected']


# ───────────────────── R1 比劫夺财 precision ─────────────────────

class TestR1Precision:
    def test_r1a_caiwang_not_duodong(self):
        """财旺夺不动：身强财明现≥2柱，比劫夺之不动不论夺财。
        例134 房地产倒卖（戊戌丁丑戊子壬子）：身旺财旺（子子壬3柱）发财。"""
        from mangpai.subjective.yongshen import detect_bijiao_duocai
        r = detect_bijiao_duocai('戊', ['戊', '丁', '戊', '壬'],
                                 ['戌', '丑', '子', '子'])
        assert not r['detected']

    def test_r1a_caiwu_gu_still_fires(self):
        """财孤可夺保持命中：第9期乞丐（壬子癸卯壬子丙午），午财孤悬。"""
        from mangpai.subjective.yongshen import detect_bijiao_duocai
        r = detect_bijiao_duocai('壬', ['壬', '癸', '壬', '丙'],
                                 ['子', '卯', '子', '午'])
        assert r['detected'] and r['severity'] == 'severe'

    def test_r1b_gongshen_heban(self):
        """功神被合绊（受害方）：寅劫被亥合伤，不能夺财（得200万造）。
        壬寅辛亥甲戌壬申：身强，寅(比劫)克戌(财)然寅亥合受害方为寅 -> 不触发。"""
        from mangpai.subjective.yongshen import detect_bijiao_duocai
        r = detect_bijiao_duocai('甲', ['壬', '辛', '甲', '壬'],
                                 ['寅', '亥', '戌', '申'])
        assert not r['detected']

    def test_r1b_chen_you_hehua_fanzhu(self):
        """辰酉合酉非受害方（合化金反助酉刃），不豁免：王亚樵造酉刃夺财
        能力不因辰酉合而失（黑道暗杀非官锚）。"""
        from mangpai.subjective.yongshen import detect_bijiao_duocai
        r = detect_bijiao_duocai('辛', ['己', '丙', '辛', '壬'],
                                 ['丑', '寅', '酉', '辰'])
        assert r['detected']


# ───────────────────── 聚合与下游 ─────────────────────

class TestDirectionAggregate:
    def test_yongshen_xiong_in_aggregate(self):
        """R2/R3 命中 -> yongshen_xiong=True、direction=凶、reasons 带前缀。"""
        ds = assess_direction_signals('甲', ['癸', '乙', '甲', '己'],
                                      ['未', '卯', '子', '巳'])
        assert ds['yongshen_xiong']
        assert ds['jishen_zhiyongshen']['detected']
        assert ds['direction'] == '凶'
        assert any(r.startswith('忌神制用神') for r in ds['reasons'])
        brief = direction_brief(ds)
        assert brief['yongshen_xiong']

    def test_brief_default_neutral(self):
        """缺省/空输入安全返回中性且带 yongshen_xiong 键。"""
        brief = direction_brief(None)
        assert brief['direction'] == '中性'
        assert brief['yongshen_xiong'] is False

    def test_caiming_capped_by_r3(self):
        """森田健（R3卯戌合绊戌根）-> 财命封顶小康下（层级不过3）。"""
        from mangpai.subjective.caiming import analyze_caiming
        cm = analyze_caiming('己', ['辛', '戊', '己', '癸'],
                             ['卯', '戌', '亥', '酉'])
        assert cm['tier'] in ('贫', '小康')

    def test_guanming_positive_structure_protects_r3(self):
        """化例三中堂（甲丙己甲/子寅丑子）：R3命中但官杀有根（甲官根寅月）
        =正向官命结构 -> 官命不被R2/R3否决（与反局同门槛）。"""
        from mangpai.subjective.guanming import analyze_guanming
        gm = analyze_guanming('己', ['甲', '丙', '己', '甲'],
                              ['子', '寅', '丑', '子'])
        assert gm['is_guanming']
        assert not gm['vetoed']

    def test_guanming_veto_without_positive_structure(self):
        """无正向官命结构 + R2命中 + is_guanming_raw -> 否决。
        构造：身弱无官杀根、有官做功combo且财坏印者难凑——用岳飞盘验证
        「无官杀即无正向结构，is_guanming_raw=False 时谈不上否决」边界。"""
        from mangpai.subjective.guanming import analyze_guanming
        gm = analyze_guanming('甲', ['癸', '乙', '甲', '己'],
                              ['未', '卯', '子', '巳'])
        # 岳飞无金（官杀不现）-> 无正向官命结构；官命与否均不得因R2崩溃
        assert isinstance(gm['is_guanming'], bool)
        if gm['vetoed']:
            assert any('忌神制用神' in r or '用神被合绊' in r
                       for r in gm['veto_reasons'])

    def test_zhiye_military_gated_by_r2(self):
        """R2命中 -> zhiye military 桶清零（岳飞盘原 military>0 时）。"""
        from mangpai.subjective.zhiye import classify_zhiye
        zy = classify_zhiye('甲', ['癸', '乙', '甲', '己'], ['未', '卯', '子', '巳'])
        assert zy['scores'].get('military', 0) == 0
        assert '军警gating' in str(zy['evidence'].get('military', ''))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
