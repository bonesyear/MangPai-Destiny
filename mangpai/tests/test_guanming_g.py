# -*- coding: utf-8 -*-
"""官命 over-fire G0-G5 收口规则（残余处级误判修复）。

共性（正向结构门槛生效后残余）：杀刃类组合（劫刃制官杀/官杀制比劫）无格
即立官 + 劫刃制财误入官命 + 象法单独立官。书锚：
  G2「七杀制刃，要杀刃力量相当」（高级篇5.2 刃为权看，弱/强>=0.5 为相当）
  G3「伤官制官不为官」（授课 li263；官为忌/伤官去官格者去官得官保留）
  G5「杀先天无制无化，杀为忌，冲开则凶」（郝批初中例·授课教案）——
    F12 废除：刃制杀本身就是制，额外要印制化无书据，且误杀庭长书锚
    （zhongji:3808-3813 羊刃合杀当官）；丁未孪生造改由反局否决收口
  li112「杀刃俱全…申杀空亡非真兵刃相击，实为足球队教练」（空亡不计根）
锚定案例：处级误判四例（23b 农民/初中/司机/抢劫）+ 真官六例（67 例 cat4）
+ 伤官去官格（朱元璋）+ 日禄归时贵命（qi32 过路财神，G1 例外）。
"""
import pytest

from mangpai.subjective.guanming import classify_guanming_combo


def _is(g, z, **kw):
    return classify_guanming_combo(g[2], g, z, **kw)['is_guanming']


def _details(g, z, **kw):
    return classify_guanming_combo(g[2], g, z, **kw)['details']


# ── 处级误判四例（金标准：非官命）──────────────────────────────────

class TestOverFireFixed:
    @pytest.mark.xfail(strict=True, reason='R7 印重泄杀与正常化用尚不可分，shouke:1316-1322')
    def test_qi29_yin_over_shed_not_guanming(self):
        # qi29 戊辛壬癸/辰酉子卯：印绶两重泄尽杀气，无法为官或入公门
        # （shouke:1316-1322），不是壬癸壬甲/子卯子辰婚姻例。
        c = classify_guanming_combo('壬', ['戊', '辛', '壬', '癸'],
                                    ['辰', '酉', '子', '卯'])
        assert '印化官杀' not in c['shengyong_huayong']
        assert c['is_guanming'] is False

    def test_chuzhong_soldier_painter(self):
        # 壬子丙午壬辰丁未（庭长孪生造）：F12 起 G5「杀无制化」条款废除（刃制杀
        # 本身就是制，额外要印制化无书据，且误杀庭长书锚 zhongji:3808-3813）——
        # 本造与庭长造（同盘丙午时）唯一区分依据=原局反局（日时丁壬合，书
        # 「年月支冲，日时干合…此造原局就反了！见辰有牢狱」zhongji:3814-3822），
        # 由反局否决收口；身弱官杀有根非正向结构，反局否决不被门槛剥离
        from mangpai.subjective.guanming import analyze_guanming
        a = analyze_guanming('壬', ['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未'])
        assert a['is_guanming'] is False
        assert any(r.startswith('反局') for r in a['veto_reasons'])

    def test_zhenbao04_driver(self):
        # 丁未丙午庚申丁丑：官3劫1 制之太过（G2）+ 带帽单独不立（G4）
        d = _details(['丁', '丙', '庚', '丁'], ['未', '午', '申', '丑'])
        assert _is(['丁', '丙', '庚', '丁'], ['未', '午', '申', '丑']) is False
        assert any('力量悬殊' in x for x in d)
        assert any('不立官命' in x for x in d)

    def test_robber(self):
        # 甲寅丁卯乙丑庚辰：官1为用神被制（G3）+ 劫刃制财归财命（G1）
        d = _details(['甲', '丁', '乙', '庚'], ['寅', '卯', '丑', '辰'])
        assert _is(['甲', '丁', '乙', '庚'], ['寅', '卯', '丑', '辰']) is False
        assert any('伤官制官不为官' in x for x in d)


# ── 真官六例（67 例 cat4 锚）───────────────────────────────────────

class TestTruePositivesKept:
    @pytest.mark.parametrize("name,g,z,exp", [
        ('伤食制官杀', ['丙', '甲', '乙', '甲'], ['申', '午', '卯', '申'], True),
        ('劫刃制官杀', ['甲', '丁', '甲', '甲'], ['申', '卯', '申', '子'], True),
        ('财制印',     ['丁', '己', '癸', '丁'], ['未', '酉', '巳', '巳'], True),
        # 印制伤食市长（乙未丁亥甲午丙子）：书明文「四柱无官，印主权力，所以
        # 此造是个官员…升任市长」——旧值 False 系 G7 误挡印制伤食+印类无官杀
        # 门槛的引擎 bug 编码（K3-294官命批 A4/A5 修复后按书锚改 True）
        ('印制伤食',   ['乙', '丁', '甲', '丙'], ['未', '亥', '午', '子'], True),
        ('带帽',       ['壬', '己', '壬', '甲'], ['寅', '酉', '申', '辰'], True),
        ('公门武职',   ['己', '辛', '戊', '甲'], ['卯', '未', '辰', '寅'], True),
    ])
    def test_cat4_anchors(self, name, g, z, exp):
        assert _is(g, z) is exp, name


# ── 豁免路径 ───────────────────────────────────────────────────────

class TestExemptions:
    def test_zhuyuanzhang_shangguan_quguan(self):
        # 朱元璋 戊辰壬戌丁丑丁未：伤官去官格（食伤土5≥3）保留官命
        assert _is(['戊', '壬', '丁', '丁'], ['辰', '戌', '丑', '未']) is True

    def test_qi32_lone_bijie_exception(self):
        # 丙申己亥甲申甲子：比劫孤（1）+官有根（2），劫刃制财计入（G1 例外）
        assert _is(['丙', '己', '甲', '甲'], ['申', '亥', '申', '子']) is True

    def test_kongwang_sha_not_rooted(self):
        # li112 足球队教练：申杀空亡不计根→杀刃不相当（G2 空亡口径）
        # 构造：庚官坐申空亡，劫刃众
        c = classify_guanming_combo(
            '乙', ['甲', '丁', '乙', '庚'], ['寅', '卯', '丑', '申'],
            kong_wang=['申'])
        # 申空亡→官力0：杀刃类与制官杀类俱不入
        assert c['is_guanming'] is False

    def test_cong_ge_exempts_g2_g5(self):
        # qi27 比劫去杀连升 癸酉甲寅戊卯戊寅：从强杀为忌，G2/G5 豁免保官命
        assert _is(['癸', '甲', '戊', '戊'], ['酉', '寅', '卯', '寅']) is True


# ── 批E：支象行业通道（中级:3685-3687「官命组合中，如出现申、酉两字做功，
#    一般是检察、法院、法律有关的官职；如出现申、酉、丑、寅字的组合做功，
#    一般与公安部门的官」）——classify_hangye_xiang 旧仅有天干象通道 ──

from mangpai.subjective.guanming import classify_hangye_xiang

_COMBO_GUAN = {'is_guanming': True, 'zhiyong_combos': [], 'shengyong_huayong': []}


def test_e_zhixiang_shenyou_jiancha_fayuan():
    """甲日：申（杀）酉（官）两字皆参与做功（巳申合、午克申酉）→ 检察/法院/法律。"""
    r = classify_hangye_xiang('甲', ['丙', '丁', '甲', '庚'], ['巳', '午', '申', '酉'],
                              dict(_COMBO_GUAN))
    assert '检察' in r['by_zhixiang'] and '法院' in r['by_zhixiang']


def test_e_zhixiang_sgcy_gongan():
    """甲日：申酉丑寅四字中 申丑寅≥3 字在局且交织做功（申寅冲）→ 公安部门。"""
    r = classify_hangye_xiang('甲', ['丙', '丁', '甲', '戊'], ['巳', '丑', '申', '寅'],
                              dict(_COMBO_GUAN))
    assert '公安' in r['by_zhixiang']


def test_e_zhixiang_requires_guanming_premise():
    """书口径「官命组合中」：非官命（is_guanming=False）支象通道不启动。"""
    r = classify_hangye_xiang('甲', ['丙', '丁', '甲', '庚'], ['巳', '午', '申', '酉'],
                              {'is_guanming': False, 'zhiyong_combos': [],
                               'shengyong_huayong': []})
    assert r['by_zhixiang'] == ''


# ── 批P2：规则五残余 食神合印行业（zhongji:3693-3695「食神合印（佩印）为做
#    带有思想文化性的行业」——批1 审计：模块只映射了同条的羊刃七杀→执法/军队，
#    漏了这条）+ 规则二 官杀印星必须有根硬门槛（zhongji:3681-3682「官命的官杀
#    及印星不管如何做功，都必须有根。官杀虚当名气看」；gaoji:11114 同）──

def test_p2_shishen_heyin_hangye():
    """丁日甲己合=正印(甲)×食神(己)（佩印），官命前提下出思想文化性行业。
    （甲己合非日干合且非合制，做功层不载——本通道直扫原局天干五合。）"""
    r = classify_hangye_xiang('丁', ['甲', '丙', '丁', '己'], ['寅', '卯', '巳', '午'],
                              dict(_COMBO_GUAN))
    assert any('思想文化' in h for h in r['by_combo'])


def test_p2_shishen_heyin_requires_guanming():
    """同规则四支象通道口径：非官命（is_guanming=False）不出此象。"""
    r = classify_hangye_xiang('丁', ['甲', '丙', '丁', '己'], ['寅', '卯', '巳', '午'],
                              {'is_guanming': False, 'zhiyong_combos': [],
                               'shengyong_huayong': []})
    assert not any('思想文化' in h for h in r['by_combo'])


def test_p2_shishen_heyin_negative_pair():
    """甲己合但非食神×印（甲日：甲=比肩、己=正财，比肩合财）不出此象。"""
    r = classify_hangye_xiang('甲', ['甲', '丙', '甲', '己'], ['寅', '卯', '巳', '午'],
                              dict(_COMBO_GUAN))
    assert not any('思想文化' in h for h in r['by_combo'])


class TestRule2MarkerP2:
    """规则二（zhongji:3681-3682「官杀及印星必须有根，虚透当名气看」）批P2 落地
    为 marker（details 存证，不翻转判定）——硬门槛版经 blind_eval 逐案归因被书
    例否决（虚透立官书例 8 例：周恩来/袁世凯/李世民/尚书/厅级/校长/处长/普通
    干部，翻转全变差零收益；书注「大运落实时也易当官」:3696 属岁运域）。
    根口径=四支藏干（本气/中气/余气）见同五行。"""

    def test_xutou_guan_marker(self):
        # 庚辛甲乙/午寅卯未：官杀庚辛双透而四支藏干无金 → marker 存证，判定不翻
        # （书例城建处长/袁世凯同型皆虚透立官，硬门槛被数据否决）
        c = classify_guanming_combo('甲', ['庚', '辛', '甲', '乙'], ['午', '寅', '卯', '未'])
        assert c['is_guanming'] is True
        assert any('官杀虚透无根' in x and '当名气看' in x for x in c['details'])

    def test_yougen_guan_no_marker(self):
        # 同造官杀落地（申=杀本气根）→ 不立 marker
        c = classify_guanming_combo('甲', ['庚', '辛', '甲', '乙'], ['申', '寅', '卯', '午'])
        assert c['is_guanming'] is True
        assert not any('虚透无根' in x for x in c['details'])

    def test_xutou_yin_marker_zeibu_anchor(self):
        # cj-书记（癸巳丁巳甲戌己巳）：癸水印虚透无根（四支无水）→ 印 marker
        # 存证；贼捕制印=去印得权族（印虚透被制为定义性前提），判定不翻仍立官
        c = classify_guanming_combo('甲', ['癸', '丁', '甲', '己'], ['巳', '巳', '戌', '巳'])
        assert '贼捕制印' in c['zhiyong_combos']
        assert c['is_guanming'] is True
        assert any('印星虚透无根' in x for x in c['details'])


# ── 批S2-01（官命专批）：zhenbao-01 官命假阳收口 ────────────────────
# 案情：戊戌己未乙巳丁亥（50qi 第1期），书判「普通人有官司」（50qi:10 郝先生
#   原话断语、:16「戌为忌神中含七杀主官司，因七杀不明透克身，故不为刑事官司，
#   俱是民事纠纷」），金标官命 False；批13（4585428）「藏杀被制→has_guansha」
#   起误判 True（批12 98b50f8 仍合书 False），批29 _yin_combo_hit 与 F12 反向
#   又添财制印/印制伤食/伤食制印独立路径，四路径齐顶假阳。
# 修法（批S2 草图 + 本批全库扫面实证细化，反锚逐盘验证）：
#   ①藏杀被制须 ≥2 不同来方（围制成势方称「制死/得权」——慈禧丑支未冲/卯克/
#     未刑三方、希特勒丑支酉半合/寅克两方、曾国藩亥杀主气明现不赖此腿），或单方
#     来方支本气五行成势（干支主气计数≥2：岳飞子水得癸透；黄兴「甲木得势而有
#     土金之病」shouke:1682；处级-2「火与燥土之势…只是午来克申…形成匪制，故
#     官级能至处级」yanjiu:7792-7796；戊寅升官从强制辰中癸病神 shouke:6782）
#     ——01 巳中庚仅被亥一方克且亥水孤立（反遭戌未巳围攻），触及≠制死，不立。
#   ②印制伤食「护官自反」：被制伤食支藏干含官杀且与制方互战（存在反向非辅助
#     制/合制动作）者，制伤食=连官并制，护官不成，不立——01 亥克巳而巳藏庚官、
#     巳亥互冲；反锚 reg67-市长（被制午藏丁己无金）、cj-县长（亥藏壬甲无火）、
#     岳飞（子克巳、巳无反向动作）皆不伤。
#   ③伤食制印「同源裁断」：制方伤食支藏官杀且互战者，官随伤动与印互战，
#     「去印得权」不立（01 巳藏庚冲亥印、亥亦克巳；县委书记/市长同盘制方
#     午藏丁己无金，不伤）。
#   ④财制印「宾制主+制方财支藏官杀」不立：宾位之财带杀气（财支藏干含官杀）
#     制主位之印=外财带杀夺我权、失权非得权——01 戌宾财藏辛杀制亥主印，书明言
#     「戌为忌神中含七杀主官司」（50qi:16）；得官书锚皆不命中（ans46 行长纯
#     宾位、cj-处级-5 制方居主、cj-5536 丞相主制主、yx-3290 制方酉藏辛非官杀、
#     刑警队长主制宾、岳飞/厅级-2 制方未无金）。
class TestS2G1Zhenbao01FalsePositive:
    def test_zhenbao01_not_guanming(self):
        # 目标：藏杀/伤食印/财印/印伤食四路径均不得假立官命。
        # 主功为食伤生财时，次要财制印不得独立立官；其余三路径也不得假立。
        c = classify_guanming_combo('乙', ['戊', '己', '乙', '丁'],
                                    ['戌', '未', '巳', '亥'])
        assert c['is_guanming'] is False
        assert '藏杀被制' not in c['zhiyong_combos']
        assert '财制印' not in c['zhiyong_combos']
        assert '印制伤食' not in c['zhiyong_combos']
        assert '伤食制印' not in c['zhiyong_combos']

    @pytest.mark.parametrize('name,g,z', [
        ('慈禧',       ['乙', '丁', '乙', '己'], ['未', '亥', '丑', '卯']),
        ('希特勒',     ['己', '戊', '丙', '丁'], ['丑', '辰', '寅', '酉']),
        ('曾国藩',     ['辛', '己', '丙', '己'], ['未', '亥', '辰', '亥']),
        ('岳飞',       ['癸', '乙', '甲', '己'], ['未', '卯', '子', '巳']),
        ('蒋介石',     ['丁', '庚', '己', '庚'], ['亥', '戌', '巳', '午']),
        ('黄兴',       ['甲', '甲', '甲', '甲'], ['戌', '戌', '寅', '戌']),
        ('戊寅升官',   ['甲', '甲', '丙', '甲'], ['午', '戌', '辰', '午']),
        ('台湾总统',   ['乙', '丙', '乙', '丙'], ['巳', '戌', '未', '戌']),
        ('yx-处级-2',  ['丁', '丁', '丙', '甲'], ['未', '未', '申', '午']),
        ('cj-市长',    ['丙', '辛', '己', '辛'], ['午', '丑', '未', '未']),
        ('周恩来',     ['戊', '甲', '丁', '甲'], ['戌', '寅', '卯', '辰']),
    ])
    def test_zangsha_leg_anchors_kept(self, name, g, z):
        # 藏杀被制腿真阳锚：多方围制或单方成势，收窄后官命不翻
        assert _is(g, z) is True, name

    def test_cixi_hitler_leg_combo_kept(self):
        # 慈禧丑支三方、希特勒丑支两方，藏杀被制本体保留。
        for g, z in [(['乙', '丁', '乙', '己'], ['未', '亥', '丑', '卯']),
                     (['己', '戊', '丙', '丁'], ['丑', '辰', '寅', '酉'])]:
            c = classify_guanming_combo(g[2], g, z)
            assert '藏杀被制' in c['zhiyong_combos']

    def test_jianchachang_shangguan_jue_not_fake_zangsha(self):
        # 理象学:7993-8006「看不出任何做功…水木伤官成局」——不伪造藏杀做功。
        c = classify_guanming_combo('癸', ['壬', '壬', '癸', '甲'],
                                    ['午', '寅', '卯', '寅'])
        assert '藏杀被制' not in c['zhiyong_combos']
        assert '伤官诀' in c['shengyong_huayong']
        assert c['is_guanming'] is True

    def test_neishishen_does_not_borrow_shangguan_jue(self):
        # 理象学:6616-6619 内食神有功，不借:7993-8006 的无功纯局伤官诀解释。
        c = classify_guanming_combo('壬', ['壬', '癸', '壬', '壬'],
                                    ['寅', '卯', '子', '寅'])
        assert '伤官诀' not in c['shengyong_huayong']

    def test_yin_combo_anchors_kept(self):
        # ②反锚：reg67-市长按书为伤食制印；cj-县长（亥藏壬甲无火）印制伤食不伤；
        # 岳飞子克巳无互战，印制伤食=贵格做功保留（test_yongshen_r2r3 同盘锚）
        c1 = classify_guanming_combo('甲', ['乙', '丁', '甲', '丙'],
                                     ['未', '亥', '午', '子'])
        assert c1['is_guanming'] is True
        assert '伤食制印' in c1['zhiyong_combos']  # 理象学:7354 伤官星制印
        c2 = classify_guanming_combo('辛', ['戊', '壬', '辛', '甲'],
                                     ['戌', '戌', '亥', '午'])
        assert c2['is_guanming'] is True
        assert '印制伤食' in c2['zhiyong_combos']
        c3 = classify_guanming_combo('甲', ['癸', '乙', '甲', '己'],
                                     ['未', '卯', '子', '巳'])
        assert c3['is_guanming'] is True
        assert '印制伤食' in c3['zhiyong_combos']

    def test_caizhiyin_anchors_kept(self):
        # ④反锚：财制印得官书锚皆不命中「宾制主+财支藏官杀」——ans46 行长
        # （纯宾位）/处级-5（制方居主）/5536 丞相（主制主）/yx-3290（制方酉藏
        # 辛非官杀）/刑警队长（主制宾）
        for name, g, z in [
                ('ans46行长',   ['乙', '戊', '乙', '壬'], ['未', '子', '卯', '午']),
                ('cj-处级-5',   ['壬', '甲', '庚', '戊'], ['寅', '辰', '寅', '寅']),
                ('cj-5536丞相', ['戊', '辛', '丙', '庚'], ['申', '酉', '申', '寅']),
                ('yx-3290',     ['丁', '丙', '丙', '丁'], ['酉', '午', '寅', '酉']),
                ('刑警队长',    ['丁', '己', '癸', '丁'], ['未', '酉', '巳', '巳'])]:
            c = classify_guanming_combo(g[2], g, z)
            assert c['is_guanming'] is True, name
            assert '财制印' in c['zhiyong_combos'], name
