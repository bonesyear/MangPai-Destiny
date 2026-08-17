# -*- coding: utf-8 -*-
"""yingqi_subj 寿元机制推演断言集（10 盘 11 事件，2026-08-14 备查矿存档转录）。

样本来源：/tmp/g3_dropped.json 备查矿 + 归档 kimi-yingqi-mining-2026-08-14 §2.3
超九语义样本，逐条人工读 raw quote 打标。书锚 = 原书行号：
cj1/cj2 = 《初级命理学》，yx1/yx2 = 《理象学研究版》。

红线：只做推演验证（识别「带病逢引动」结构），不做死亡/寿数预测断言；
detect_shouyuan_jixie 不进 engine 消费链。

机制分组与书锚数（均 ≥2 同构锚方落地）：
  破禄（2 锚）：cj1:1838「原局子卯破破禄，破禄而死」（书言子卯破=引擎子卯刑）
               + cj2:5278「子卯破禄…杀冲禄把禄给坏了」
  禄到位（3 正锚+1 吉反锚）：cj1:1838「禄到为寿到」+ cj1:2477「行子运变实，
               子为癸的禄」+ cj1:2741「己卯运父禄到，死父」；
               反锚 cj1:697「酉到为日主到了…高考状元」（无带病则吉）
  寿元星被坏（2 锚）：cj2:6042「癸水寿元星见子水为禄为寿，被午冲，主寿到了」
               + cj2:3704 盲师诀「穿倒食神损寿元」（食伤全坏）
  原局字到位（3 锚）：yx2:7486「申金到位被局中官星火正克」+ cj2:5230「丁丑年
               日主到位」+ cj2:4160「丁虚透为原局的戌到了，丁代表戌的象」

收档（无书明文机制或非死亡，勿强塞）：yx1:5071 杀嫂 / yx3:14841 预测失误反例 /
cj2:6130 车祸死 / yx1:2429 脑出血 / yx2:7477、yx1:2473（伤非死）/ yx3:13528 夫死 /
cj2:3904 子死（星被制单锚）/ yx2:5702 非死亡事件 / cj2:3841 父死（丑刑戌单锚）。
"""
import pytest

from mangpai.subjective.yingqi_subj import detect_shouyuan_jixie


def _split_gz(gz):
    """'丙子'->('丙','子')；单字按干支表消歧（'子'运=支运，'丁'运=干运）。"""
    if len(gz) == 2:
        return gz[0], gz[1]
    if len(gz) == 1:
        return (gz, '') if gz in '甲乙丙丁戊己庚辛壬癸' else ('', gz)
    return '', ''


def _run(bazi, dy='', ln=''):
    gans = [bazi[i] for i in (0, 2, 4, 6)]
    zhis = [bazi[i] for i in (1, 3, 5, 7)]
    dg, dz = _split_gz(dy)
    lg, lz = _split_gz(ln)
    return detect_shouyuan_jixie(
        gans[2], gans, zhis,
        dayun_gan=dg, dayun_zhi=dz, liunian_gan=lg, liunian_zhi=lz)


# ── 破禄 ────────────────────────────────────────────────────────────

class TestPoLu:
    def test_polu_natal_disease_lu_dao(self):
        # 壬子癸卯癸卯甲寅 坤，子运辛巳年死：「子为日主的禄，禄到为寿到。
        # 原局子卯破破禄。破禄而死」（cj1:1838）——原局带病 + 运禄到位
        r = _run('壬子癸卯癸卯甲寅', dy='子', ln='辛巳')
        assert '破禄' in r['mechanisms'] and '禄到位' in r['mechanisms']
        assert r['risk'] is True

    def test_polu_dayun_trigger(self):
        # 丁亥乙巳乙卯辛巳 乾，庚子运乙酉年急病死：「庚合乙，子卯破禄…
        # 乙酉年杀冲禄，把禄给坏了。七杀冲禄主凶死」（cj2:5278）——运岁引动坏禄
        r = _run('丁亥乙巳乙卯辛巳', dy='庚子', ln='乙酉')
        assert '破禄' in r['mechanisms']
        assert r['risk'] is True


# ── 禄到位 ──────────────────────────────────────────────────────────

class TestLuDaowei:
    def test_shouyuanxing_lu_bianshi(self):
        # 辛卯丙申辛未癸巳 乾，子运戊申年死：「行子运变实，子为癸的禄，
        # 原局癸水虚透被制，不能见根被未穿」（cj1:2477）——寿元星禄到位被穿
        r = _run('辛卯丙申辛未癸巳', dy='子', ln='戊申')
        assert '禄到位' in r['mechanisms']
        assert '寿元星被坏' in r['mechanisms']
        assert r['risk'] is True

    def test_fu_lu_dao_fu_si(self):
        # 乙巳庚辰辛卯丙申 乾，己卯运死父（八岁）：「乙木根全坏了，走己卯运
        # 为父的禄到了，所以此运死父」（cj1:2741）——他干（父星乙）禄原局被辰穿，
        # 运禄到位
        r = _run('乙巳庚辰辛卯丙申', dy='己卯')
        assert '破禄' in r['mechanisms'] and '禄到位' in r['mechanisms']
        assert r['risk'] is True

    def test_fanmao_lu_dao_ji(self):
        # 吉反锚：丙寅己亥辛酉己亥 乾，丁丑运乙酉年高考状元：「酉到为日主
        # 到了」（cj1:697）——禄到位但原局无带病，risk 不得为真（到位本身中性）
        r = _run('丙寅己亥辛酉己亥', dy='丁丑', ln='乙酉')
        assert '禄到位' in r['mechanisms']
        assert r['risk'] is False


# ── 寿元星被坏 ──────────────────────────────────────────────────────

class TestShouyuanxing:
    def test_shouyuanxing_lu_chongqu(self):
        # 庚寅辛巳辛酉癸巳 坤，丙子运壬午年母子被杀：「癸水寿元星见子水为禄
        # 为寿，被午冲，主寿到了」（cj2:6042）——流年冲去大运寿元星之禄
        r = _run('庚寅辛巳辛酉癸巳', dy='丙子', ln='壬午')
        assert '寿元星被坏' in r['mechanisms']
        assert r['risk'] is True

    def test_chuandao_shishen(self):
        # 丁酉丙午乙丑辛巳 乾，寅运丁丑年死：「原局午已坏…寅巳穿…丑杀库到位，
        # 穿倒午食…盲师诀：穿倒食神损寿元」（cj2:3704）——运岁穿坏食伤之禄
        r = _run('丁酉丙午乙丑辛巳', dy='寅', ln='丁丑')
        assert '寿元星被坏' in r['mechanisms']
        assert r['risk'] is True


# ── 原局字到位 ──────────────────────────────────────────────────────

class TestYuanjuDaowei:
    def test_liunian_zhi_daowei_beike(self):
        # 壬寅戊申辛巳戊戌 乾，辛亥运壬申年高压电死：「申金到位被局中官星火
        # 正克」（yx2:7486）——流年支重现原局月支申（寅申冲/巳申刑带病）
        r = _run('壬寅戊申辛巳戊戌', dy='辛亥', ln='壬申')
        assert '原局字到位' in r['mechanisms']
        assert r['risk'] is True

    def test_day_gan_daowei(self):
        # 壬子辛亥丁巳辛亥 坤，丙子年白血病、丁丑年死：「丁丑年日主到位，
        # 丑是与金水结党来灭火，死了」（cj2:5230）——流年干日主重现 + 原局巳亥冲带病
        r = _run('壬子辛亥丁巳辛亥', ln='丁丑')
        assert '原局字到位' in r['mechanisms']
        assert r['risk'] is True

    def test_xutou_tou_canggan(self):
        # 乙未乙酉丙戌己丑 坤，丁运癸丑年父死、丑运丁丑年自死（尿毒症）：
        # 「丁虚透为原局的戌到了，丁代表戌的象」（cj2:4160）——运干透原局戌藏干
        r = _run('乙未乙酉丙戌己丑', dy='丁', ln='癸丑')
        assert '原局字到位' in r['mechanisms']
        assert r['risk'] is True
        r2 = _run('乙未乙酉丙戌己丑', dy='丑', ln='丁丑')
        assert '原局字到位' in r2['mechanisms']
        assert r2['risk'] is True


# ── 高级寿元章书例（gaoji 11.4，F10 哨兵：一漏一错）──────────────────

class TestGaojiShouyuanShuli:
    def test_anli1_shishen_zuo_jue_zhengke(self):
        # 丙午癸巳辛酉癸巳 乾，丁酉运乙酉年肝癌死：「癸水食神虚浮无根，坐巳火
        # 绝地…火旺克金…运逢丁杀熬癸水…食神寿星绝尽而亡」（gaoji:16164-16185）。
        # 机制=寿元星(癸)坐绝带病（总诀「穿害克绝命难长」gaoji:16148/16547）
        #   + 酉（日主禄/原局字）到位被原局午火正克（yx2:7486「正克」同型）。
        r = _run('丙午癸巳辛酉癸巳', dy='丁酉', ln='乙酉')
        assert '寿元星被坏' in r['mechanisms']
        assert r['risk'] is True

    def test_anli2_yinxing_gen_chongsan(self):
        # 癸卯丙辰甲辰乙丑 坤，庚申运甲戌年死：「无食神（丙坐辰无功）以印星
        # 为寿…癸水印星之根辰土被坏…流年甲戌，戌土冲辰，辰中癸水印根被冲散。
        # 印根被拔寿星倒」（gaoji:16190-16216）。
        # 机制=定位诀「无食看印印为根」（gaoji:16148/16157）印级补位
        #   + 寿元星(癸)之根辰原局被坏、流年戌冲辰引动。
        r = _run('癸卯丙辰甲辰乙丑', dy='庚申', ln='甲戌')
        assert '寿元星被坏' in r['mechanisms']
        assert any('辰' in s and '癸' in s for s in r['signals'])
        assert r['risk'] is True


# ── engine 传 age（F10：三要素 commit 名副其实）─────────────────────

class TestEnginePassesAge:
    def test_engine_yingqi_daxian_active(self):
        # engine 链路须传 age → has_daxian 不再恒 False（批4 P1-3/P0 传导）
        from mangpai.engine import MangpaiEngine
        bazi_data = {
            'bazi': {'year': '丙午', 'month': '癸巳', 'day': '辛酉', 'hour': '癸巳'},
            'input': {'year': 1966},
        }
        r = MangpaiEngine(bazi_data).compute_all()
        assert r['yingqi_subj']['daxian_yingqi']['active'] is not None

    def test_engine_yingqi_no_year_daxian_absent(self):
        # 无出生年 → 大限仍缺省空转（回退行为不变）
        from mangpai.engine import MangpaiEngine
        bazi_data = {
            'bazi': {'year': '丙午', 'month': '癸巳', 'day': '辛酉', 'hour': '癸巳'},
            'input': {},
        }
        r = MangpaiEngine(bazi_data).compute_all()
        assert r['yingqi_subj']['daxian_yingqi']['active'] is None
