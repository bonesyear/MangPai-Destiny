# -*- coding: utf-8 -*-
"""P2 从格细则（classify_strength 22期四规则+从旺/从禄）+ 包局2.6 + 从财格顺势档 测试。

规则出处（仅训练侧锚点）：
  从格（《授课教程》第22期「如何分辨八字的从格」）：
    ①日主无根无扶者从；②有根无生扶但根被坏者从（根被坏=双夹冲/邻支刑穿/
      合会转化为异党；双夹冲印难救——例4 三戌冲辰 vs 例5 一贴一不贴冲不坏）；
    ③无根有印而印无根者从；④无根印有根而印根被坏者从；唯年支根远无扶者从。
    从格须一方成势（异党单五行≥3——生例一富婆 水木两停不从）；
    印根只计本/中气（例1/例2 书判「印也无根」），日主根计余气（例5 辰中癸）。
    从旺/从禄：自党≥5 且月令异党被坏且异党天干无本气根（ans30 从禄格；
    乞丐 丙火根在午，异党有依托，身强不从）。
  包局2.6（《高级内容篇》2.6 + 层功法则6）：年时干/支/十神包围 + 制化所包
    （包围载体亲自发起/承受）+1 层；反局破包（官杀×食伤、财×比劫）不计；
    支系异字十神包局暂缓（四墓库两两必同土，例6 未戌误中备案）。
  从财格顺势档（caiming）：从弱财为所从——财成局（巳酉丑合财局发大财）/
    财有原神转化（22期例1）基阶不落下富；财伏吟单一无转化（例141）从财亦贫。
"""
import pytest

from mangpai.subjective.yongshen import classify_strength
from mangpai.subjective.gongliang import analyze_gongliang
from mangpai.subjective.caiming import analyze_caiming


# ───────────────────── 22期 从格四规则 ─────────────────────

class TestCongGeRules:
    @pytest.mark.parametrize('name,dg,g,z,exp', [
        ('例1从财（无根印亦无根）', '庚', ['辛', '庚', '庚', '己'], ['亥', '寅', '寅', '卯'], '从弱'),
        ('例2从财（无根印根被穿坏）', '辛', ['辛', '庚', '辛', '壬'], ['卯', '寅', '卯', '辰'], '从弱'),
        ('例3从儿（根被合会转化）', '甲', ['戊', '戊', '甲', '己'], ['午', '午', '寅', '巳'], '从弱'),
        ('例4从杀（双夹冲坏根印难救）', '壬', ['丙', '壬', '壬', '庚'], ['戌', '辰', '戌', '戌'], '从弱'),
        ('例5王庆不从（单夹冲辰癸不坏）', '壬', ['丙', '壬', '壬', '庚'], ['午', '辰', '戌', '戌'], '身弱'),
        ('ans30从禄格（月令官被巳刑坏，异党无本气根）', '己',
         ['丁', '壬', '己', '庚'], ['未', '寅', '巳', '午'], '从强'),
    ])
    def test_book_cases(self, name, dg, g, z, exp):
        assert classify_strength(dg, g, z) == exp, name

    def test_fupo_shuiting_not_cong(self):
        """生例一富婆（辛亥庚子庚寅己卯）：水木两停非一方成势（异党<3），
        不从（书作生用做功富婆，非从格）。"""
        assert classify_strength('庚', ['辛', '庚', '庚', '己'], ['亥', '子', '寅', '卯']) == '中和'

    def test_qigai_yidang_yougen_not_cong(self):
        """乞丐（壬子癸卯壬子丙午）：月令卯被子刑似破，然异党丙火根在午
        （本气刃根）有所依托——身强比劫夺财局，不从。"""
        assert classify_strength('壬', ['壬', '癸', '壬', '丙'], ['子', '卯', '子', '午']) == '身强'

    def test_additive_no_reverse(self):
        """additive 口径：既有从格标签不被细则反向改判（阎锡山从弱保持）。"""
        assert classify_strength('乙', ['癸', '辛', '乙', '丁'], ['未', '酉', '酉', '丑']) == '从弱'
        assert classify_strength('己', ['乙', '己', '己', '庚'], ['巳', '丑', '未', '午']) == '从强'


# ───────────────────── 包局2.6（gongliang +1）─────────────────────

class TestBaoju26:
    def test_zhuangjia_shishen_baoju(self):
        """股票庄家（戊申己未癸巳己未）：年时戊/己官杀十神包局，巳申合制劫财
        制化所包 -> +1（书：合官、制劫财、包局复合，巨富庄家）。"""
        gl = analyze_gongliang(day_gan='癸', gans=['戊', '己', '癸', '己'],
                               zhis=['申', '未', '巳', '未'])
        assert any('包局2.6' in r for r in gl['reasons'])
        assert gl['gong_points'] >= 3.0

    def test_liu6_yizi_zhi_not_counted(self):
        """理象学例6（乙未丙戌甲子甲戌）：未/戌异字支系十神（财）包局暂缓
        （四墓库两两必同土过宽，书定层功2层）-> 不计包局2.6。"""
        gl = analyze_gongliang(day_gan='甲', gans=['乙', '丙', '甲', '甲'],
                               zhis=['未', '戌', '子', '戌'])
        assert not any('包局2.6' in r for r in gl['reasons'])
        assert gl['level'] == 2

    def test_po_bao_opposite_gans(self):
        """反局破包：年干正官×时干伤官（十神相克对）-> 干系包围破局不计。
        构造：甲年官（辛）×时伤官（丁）于丙日，支无同字。"""
        gl = analyze_gongliang(day_gan='丙', gans=['辛', '丙', '丙', '丁'],
                               zhis=['辰', '午', '申', '酉'])
        assert not any('包局2.6' in r for r in gl['reasons'])

    def test_fuhe_annotation_present(self):
        """复合结构标注：制用+生用并存 -> fuhe.detected + synergy（协同）。"""
        gl = analyze_gongliang(day_gan='癸', gans=['戊', '己', '癸', '己'],
                               zhis=['申', '未', '巳', '未'])
        fuhe = gl.get('fuhe') or {}
        assert fuhe.get('detected') is True
        assert 'synergy' in fuhe and 'conflicts' in fuhe

    def test_cong_ge_annotation_present(self):
        """从格标注：gongliang 结果带 strength/cong_ge（阎锡山从弱）。"""
        gl = analyze_gongliang(day_gan='乙', gans=['癸', '辛', '乙', '丁'],
                               zhis=['未', '酉', '酉', '丑'])
        assert gl.get('cong_ge') is True
        assert gl.get('strength') == '从弱'


# ───────────────────── 从财格顺势档（caiming）─────────────────────

class TestCongCaiTier:
    def test_chengju_floor_fu(self):
        """从财富有（辛巳丁酉丁酉辛丑）：巳酉丑合财局 -> 基阶不落下富
        （书：弃命从财，得别人之财，很富有）。"""
        cm = analyze_caiming('丁', ['辛', '丁', '丁', '辛'], ['巳', '酉', '酉', '丑'])
        assert cm['tier_static'] in ('富', '巨富')
        assert '从财成局' in cm['level_static']['adjust']

    def test_yuanshen_floor_fu(self):
        """22期例1 从财格（辛亥庚寅庚寅己卯）：财有原神（亥）且明现≥2 ->
        基阶不落下富（书：作从财格看，用神是水木，乙亥年发财）。"""
        cm = analyze_caiming('庚', ['辛', '庚', '庚', '己'], ['亥', '寅', '寅', '卯'])
        assert cm['tier_static'] in ('富', '巨富')

    def test_fuyin_pin(self):
        """例141 从财非常穷（癸卯乙卯辛卯辛卯）：卯财伏吟单一（同名≥3）无
        转化 -> 从财亦贫（书：卯财是单个的，没有转化，缺乏连贯性）。"""
        cm = analyze_caiming('辛', ['癸', '乙', '辛', '辛'], ['卯', '卯', '卯', '卯'])
        assert cm['tier_static'] == '贫'
        assert '伏吟' in cm['level_static']['adjust']

    def test_xutou_bijiao_not_duocai(self):
        """R1c 从弱虚根豁免：22期例1 辛劫虚透无本气根（「天干比肩再多也
        无用」）-> 不论比劫夺财。"""
        from mangpai.subjective.yongshen import detect_bijiao_duocai
        r = detect_bijiao_duocai('庚', ['辛', '庚', '庚', '己'], ['亥', '寅', '寅', '卯'])
        assert not r['detected']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
