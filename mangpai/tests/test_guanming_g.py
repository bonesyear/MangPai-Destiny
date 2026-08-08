# -*- coding: utf-8 -*-
"""官命 over-fire G0-G5 收口规则（残余处级误判修复）。

共性（正向结构门槛生效后残余）：杀刃类组合（劫刃制官杀/官杀制比劫）无格
即立官 + 劫刃制财误入官命 + 象法单独立官。书锚：
  G2「七杀制刃，要杀刃力量相当」（高级篇5.2 刃为权看，弱/强>=0.5 为相当）
  G3「伤官制官不为官」（授课 li263；官为忌/伤官去官格者去官得官保留）
  G5「杀先天无制无化，杀为忌，冲开则凶」（郝批初中例·授课教案）
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
    def test_zhenbao23b_farmer(self):
        # 壬子癸卯壬子甲辰：杀刃类从格豁免仍被 G0（辅助做功）收口
        assert _is(['壬', '癸', '壬', '甲'], ['子', '卯', '子', '辰']) is False

    def test_chuzhong_soldier_painter(self):
        # 壬子丙午壬辰丁未：杀无制化（无印无食伤）→ G5 收口
        d = _details(['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未'])
        assert _is(['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未']) is False
        assert any('杀无制化' in x for x in d)

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
