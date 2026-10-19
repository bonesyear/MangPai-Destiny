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

    def test_qigai_cong_qiang(self):
        """乞丐（壬子癸卯壬子丙午）：书判「此造从强，禄神有泄，财里有生」
        （trainset:111 zhenbao-09 raw_quote 原文）——批N2 勘误：旧注/旧测
        「书判比劫夺财身强局」系误读；异党丙火得午刃（本气根）非墓库依托，
        不阻断从强（对比 ans29 癸得两辰库方「不能从」）。"""
        assert classify_strength('壬', ['壬', '癸', '壬', '丙'], ['子', '卯', '子', '午']) == '从强'

    def test_additive_no_reverse(self):
        """additive 口径：既有从格标签不被细则反向改判（阎锡山从弱保持）。"""
        assert classify_strength('乙', ['癸', '辛', '乙', '丁'], ['未', '酉', '酉', '丑']) == '从弱'
        assert classify_strength('己', ['乙', '己', '己', '庚'], ['巳', '丑', '未', '午']) == '从强'


# ───────────────────── 批N2 从格判定修复（金标回归哨兵）─────────────────────

class TestCongGeN2:
    """批N2 哨兵：每类修复=误判案例归位 + 反例不误伤。书锚见各 docstring。"""

    # ── 修1 粗闸从弱侧：日主有未坏之根（本气禄/劫财余气）者不能从 ──
    @pytest.mark.parametrize('name,dg,g,z', [
        ('li004车祸死（身弱有禄不能从——酉禄未坏）', '辛',
         ['丙', '癸', '辛', '丁'], ['午', '巳', '巳', '酉']),
        ('li131乙亥发财（两辰中乙劫财余气根，身弱不从）', '甲',
         ['甲', '庚', '甲', '庚'], ['辰', '午', '辰', '午']),
        ('li139靠丈夫富（亥未拱禄/未中乙劫财余气根，不从）', '乙',
         ['丁', '辛', '乙', '丙'], ['未', '亥', '未', '戌']),
        ('li263三陪女（戌中丁劫财余气——书「丁羊刃有根而不从」）', '丙',
         ['壬', '辛', '丙', '丁'], ['戌', '亥', '子', '酉']),
        ('li002闹离婚（书「八字不从」——丑中己劫财本气根）', '戊',
         ['辛', '辛', '戊', '癸'], ['亥', '卯', '申', '丑']),
    ])
    def test_xiu1_root_saved_not_cong(self, name, dg, g, z):
        assert classify_strength(dg, g, z) == '身弱', name

    def test_xiu1_tengluo_not_cong(self):
        """li208淫贱：乙见甲为藤萝系甲而不从（劫财甲透时干，书明文不从）。"""
        assert classify_strength('乙', ['庚', '己', '乙', '甲'],
                                 ['戌', '丑', '巳', '申']) == '身弱'

    def test_xiu1_fanli_li141_still_cong(self):
        """反例不误伤：例141（癸卯乙卯辛卯辛卯）无根无扶，仍从弱（书：此造从财）。"""
        assert classify_strength('辛', ['癸', '乙', '辛', '辛'],
                                 ['卯', '卯', '卯', '卯']) == '从弱'

    # ── 修2 粗闸从强侧：异党透干得墓库根≥2（两库）=有依托不能从 ──
    def test_xiu2_ans29_two_tombs_not_cong(self):
        """ans29一贫如洗（癸丙戊丙/未辰戌辰）：「水得两库而不能从，以身旺劫印
        为忌神看」——异党癸得两辰库=有依托，落身强不从。"""
        assert classify_strength('戊', ['癸', '丙', '戊', '丙'],
                                 ['未', '辰', '戌', '辰']) == '身强'

    def test_xiu2_fanli_ans33_one_tomb_still_cong(self):
        """反例不误伤：ans33博彩大发（癸酉戊午己巳戊辰）癸财只得一辰库，
        书仍判「此造是从强格以财作忌神」。"""
        assert classify_strength('己', ['癸', '戊', '己', '戊'],
                                 ['酉', '午', '巳', '辰']) == '从强'

    # ── 修3 从强侧门槛：5:3 月令自党 + 合会化势计数 + 两停从禄 ──
    @pytest.mark.parametrize('name,dg,g,z', [
        ('li099洪秀全（5:3 月令自党+酉丑化金，书「日主从强，金为用神」）', '癸',
         ['癸', '甲', '癸', '癸'], ['酉', '子', '卯', '丑']),
        ('qi35肾炎住院（5:3 月令自党，书「木旺从强」）', '乙',
         ['乙', '己', '乙', '己'], ['丑', '卯', '卯', '卯']),
        ('li263走私被扣（4:4 寅午戌化火→5:3，书「从强」）', '丙',
         ['庚', '壬', '丙', '丙'], ['寅', '午', '戌', '申']),
        ('qi32过路财神（4:4 申子化水→6:2，书「从禄格…日禄归时」）', '甲',
         ['丙', '己', '甲', '甲'], ['申', '亥', '申', '子']),
        ('b67制例三（两停4:4 月令为己禄+午戌化火，书「我认为是从禄格」）', '己',
         ['癸', '戊', '己', '甲'], ['卯', '午', '酉', '戌']),
    ])
    def test_xiu3_cong_qiang(self, name, dg, g, z):
        assert classify_strength(dg, g, z) == '从强', name

    def test_xiu3_ans37b_beian_residual(self):
        """备案残误：ans37b 得200万（壬寅辛亥甲戌壬申）5:3 亥月寅禄书判「后造
        从强」，与 ans37a（同盘仅时支 申/戌 一字差，书判为别人理财赚钱之富）
        及 li054 掌兵权大贵/富丑运发迹（俱 5:3 印月禄刃在局、书判扶抑贵富）
        不可机械分离——印月支径已从 C 径撤除（从强侧宁缺勿滥），本造现依扶抑
        侧判身强，残误待裁（批N2-N3 备案）。"""
        assert classify_strength('甲', ['壬', '辛', '甲', '壬'],
                                 ['寅', '亥', '戌', '申']) == '身强'

    def test_xiu3_fanli_liangting_no_lu_not_cong(self):
        """反例不误伤：li202乞丐（庚辰乙酉丁丑乙巳）两停4:4 但月令非日主之禄，
        不得经两停从禄入从强侧。"""
        assert classify_strength('丁', ['庚', '乙', '丁', '乙'],
                                 ['辰', '酉', '丑', '巳']) != '从强'

    def test_xiu3_fanli_lijiacheng_deling_not_cong(self):
        """反例不误伤：李嘉诚（戊辰己未庚午丁亥）5:3 月令自党但未月非禄刃、
        局中无申酉禄刃——得令闸挡回身强（书以身强用财论巨富，非从强）。"""
        assert classify_strength('庚', ['戊', '己', '庚', '丁'],
                                 ['辰', '未', '午', '亥']) == '身强'

    # ── 修4 坏根口径双向修正 ──
    def test_xiu4_li128_dayzhi_benqi_chuan_not_broken(self):
        """li128壬子运穷（壬子戊申戊戌辛酉）：日支戌本气强根不被酉戌穿判坏——
        书「日主坐强根，此造不从…戌根原自己的」，落身弱。"""
        assert classify_strength('戊', ['壬', '戊', '戊', '辛'],
                                 ['子', '申', '戌', '酉']) == '身弱'

    def test_xiu4_li002_sishen_he_xing_not_broken(self):
        """li002亥年结婚（辛亥丙申己巳壬申）：巳申刑合相兼以合论、不判坏印根——
        书「日主有巳印不从，身弱，以巳印为用」。"""
        assert classify_strength('己', ['辛', '丙', '己', '壬'],
                                 ['亥', '申', '巳', '申']) == '身弱'

    def test_xiu4_qi19_tu_chong_xu(self):
        """qi19伤官去官官员（辛丑乙未戊申辛酉）：土日主之土根被邻支土单冲
        即冲虚——书「土冲变虚…戊土无所依托，以从格看」（从伤官），归从弱。"""
        assert classify_strength('戊', ['辛', '乙', '戊', '辛'],
                                 ['丑', '未', '申', '酉']) == '从弱'

    def test_xiu4_b67_jianzhu_dan_chong_huai_lu(self):
        """b67建筑（丁未癸卯辛卯丁酉）：非月令/非日支之根（时支酉禄）被邻支
        紧贴单冲即坏（「强有力的邻支冲掉」zhenbao:715），归从弱（书：此造从财）。"""
        assert classify_strength('辛', ['丁', '癸', '辛', '丁'],
                                 ['未', '卯', '卯', '酉']) == '从弱'

    def test_xiu4_fanli_qi03_dayzhi_benqi_chong_not_broken(self):
        """反例不误伤：qi03赵宇（丁未壬子丁巳辛亥）日支巳本气根虽被亥单冲，
        坐强根不判坏——书「信口开河说此人从了财，实际不是」，仍身弱。"""
        assert classify_strength('丁', ['丁', '壬', '丁', '辛'],
                                 ['未', '子', '巳', '亥']) == '身弱'

    # ── 修5 所从分类：伤食生财线路财优先 / tie 财优先 ──
    @pytest.mark.parametrize('name,dg,g,z,exp', [
        ('ans06车祸身亡（土3金2 伤食生财，书「以土泄火生财作用神」从财）', '丙',
         ['壬', '庚', '丙', '壬'], ['辰', '戌', '申', '辰'], '从财'),
        ('qi27厅级（木4火2 伤食生财，书「日主无依必从财」）', '癸',
         ['甲', '丁', '癸', '乙'], ['午', '卯', '酉', '卯'], '从财'),
        ('li211台湾总统（火土3:3 tie 财优先，书「现作从财说」）', '乙',
         ['乙', '丙', '乙', '丙'], ['巳', '戌', '未', '戌'], '从财'),
    ])
    def test_xiu5_shangshi_shengcai_cai_first(self, name, dg, g, z, exp):
        from mangpai.subjective.yongshen import classify_cong_target
        assert classify_cong_target(dg, g, z)['label'] == exp, name

    def test_xiu5_fanli_li209_still_conger(self):
        """反例不误伤：li209从儿亡（丁卯壬寅癸卯丙辰）木3火2 但火无本气根，
        书仍「从儿格喜用财」——所从为儿不转财。"""
        from mangpai.subjective.yongshen import classify_cong_target
        assert classify_cong_target('癸', ['丁', '壬', '癸', '丙'],
                                    ['卯', '寅', '卯', '辰'])['label'] == '从儿'

    # ── 修7 备案（书内冲突未裁，逻辑不动）──
    def test_xiu7_li214_beian_unchanged(self):
        """备案：li214李敖 印透有根书仍判从儿 vs 例7 印有根不能从（zhenbao:747）
        ——书内两套口径，现依例7口径（印有根不从），逻辑不动仍身弱。"""
        assert classify_strength('辛', ['乙', '己', '辛', '壬'],
                                 ['亥', '卯', '亥', '辰']) == '身弱'


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
