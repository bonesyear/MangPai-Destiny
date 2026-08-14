# -*- coding: utf-8 -*-
"""liunian 应期语义 calib 断言集（16 条，2026-08-14 备查矿存档转录）。

样本来源：/tmp/g3_dropped.json 备查矿（应期/婚姻/健康/六亲事件断语），
逐条人工读 raw quote 打标（正则筛会混入非事件句）。书锚 = 原书行号：
cj1/cj2 = 《初级命理学》分区行号，yx2/yx3 = 《理象学研究版》分区行号。

覆盖九语义之 8（冲旺无书例样本，保持缺口，勿造样本）：
  合留 7 / 合去 1(xfail) / 合绊 1(xfail) / 合动（并入合留锚群，宫位之合）
  冲动 2 / 冲开 1 / 冲去 1(xfail) / 冲破 2+1(xfail)

筛除 2 条（非冲合机制，归 yingqi_subj/biqi 域，勿强塞）：
  - 壬子癸卯癸卯甲寅 坤 子运辛巳年死：「原局子卯破破禄…水绝于巳」
    （cj1:1838）——破/绝，无冲合对。
  - 壬子庚戌辛丑乙未 乾 甲申年兄死：「庚得禄被冲」（cj2:3841）——原局
    子戌丑未无寅，申无冲对，属禄到位应期域。

xfail 1 条 = 引擎缺口收档（书锚不足 ≥2 同构门槛，勿无锚强修）：
  - ch8 冲破：「辰戌冲坏了夫宫」惟戌为墓库引擎冲开规则在先；「夫宫
    无合被冲=冲破」仅此一锚（cj1:2355），且与 ch3（日支未官库被流年
    冲=冲开，吉）同构反例 + shouke:64/zhenbao:48「墓库被太岁冲谓冲开」
    正面冲突——收档保持 xfail。

已修复 3 缺口（2026-08-14 同日二批，书锚驱动）：
  - he6 合去：流年干虚透（不透原局）而为原局支所藏之透=代表原局之物，
    被原局合去（yx2:5877 + zhongji:6111 双锚）。
  - he7 合绊：运-局合=合绊，classify_he_semantic 加 he_partner_dayun
    参数（仿 gender 参数模式；cj1:1816 + gaoji:5558 + chuji:3097 锚）。
  - ch4 冲去：流年冲运支统看（phase_active='干支'）并入冲去分支
    （cj2:6042 + shouke:1370 + gaoji:19348 锚）。
"""
import pytest

from mangpai.subjective.liunian import (
    analyze_liunian_mangpai,
    classify_he_semantic,
)


def _run(bazi, gender, ln, dy=None):
    gans = [bazi[i] for i in (0, 2, 4, 6)]
    zhis = [bazi[i] for i in (1, 3, 5, 7)]
    return analyze_liunian_mangpai(
        [{'gz': ln}], gans, zhis, gans[2],
        current_dayun={'gz': dy} if dy else None,
        gender='男' if gender == '乾' else '女')['liunian'][0]


def _he(r, rel_type, target, pos=None):
    for rel in r.get('gan_relations', []) + r.get('zhi_relations', []):
        if rel['type'] == rel_type and rel.get('target') == target:
            if pos and rel.get('target_pos') != pos:
                continue
            s = rel.get('he_semantic')
            if s:
                return s['he_type']
    return None


def _chong(r, target, pos=None):
    for rel in r.get('zhi_relations', []):
        if rel['type'] == '冲' and rel.get('target') == target:
            if pos and rel.get('target_pos') != pos:
                continue
            s = rel.get('chong_semantic')
            if s:
                return s['chong_type']
    return None


# ── 合四种（9 条） ──────────────────────────────────────────────────

class TestHeSemantics:
    def test_he1a_jiaji_he_liu(self):
        # 己酉丁丑癸卯庚申 坤，甲戌年成婚：「甲己合住夫星」（cj1:2775）
        # 己=七杀=夫星，流年甲合之 -> 合留
        r = _run('己酉丁丑癸卯庚申', '坤', '甲戌')
        assert _he(r, '天干合', '己') == '合留'

    def test_he1b_maoxu_he_gong(self):
        # 同盘：「卯戌合住夫宫，星宫都动，成婚」（cj1:2775）
        # 流年戌合日支卯（夫宫） -> 合留
        r = _run('己酉丁丑癸卯庚申', '坤', '甲戌')
        assert _he(r, '六合', '卯', pos='day_zhi') == '合留'

    def test_he2_chenyou_he_liu(self):
        # 己酉庚午甲子癸酉 坤，戊辰年结婚：「辰酉合住夫妻星…此年结婚」
        # （cj1:2881）酉=正官夫星 -> 合留
        r = _run('己酉庚午甲子癸酉', '坤', '戊辰')
        assert _he(r, '六合', '酉', pos='year_zhi') == '合留'

    def test_he3_sanhe_cai_liu(self):
        # 辛亥丙申丁丑乙巳 乾，癸酉年结婚：「巳酉丑合金局成功…为财合到
        # 了」（cj1:3135）酉=偏财妻星 -> 合留。
        # 注：三合局关系不附 he_semantic（覆盖面备案），直调语义分类器验书判
        r = classify_he_semantic(
            '六合', '酉', list('辛丙丁乙'), list('亥申丑巳'), '丁',
            gender='男')
        assert r['he_type'] == '合留'

    def test_he4_zichou_he_gong(self):
        # 壬子庚戌辛丑乙未 乾，丙子年结婚：「妻星合到宫位」（cj2:3841）
        # 流年子合日支丑（妻宫） -> 合留
        r = _run('壬子庚戌辛丑乙未', '乾', '丙子')
        assert _he(r, '六合', '丑', pos='day_zhi') == '合留'

    def test_he5_chenyou_he_gong(self):
        # 癸巳甲寅甲辰丁卯 坤，己酉年结婚：「遇到财官年就结婚，定为戊申、
        # 己酉年」（yx3:13528）流年酉合日支辰（夫宫） -> 合留
        r = _run('癸巳甲寅甲辰丁卯', '坤', '己酉')
        assert _he(r, '六合', '辰', pos='day_zhi') == '合留'

    def test_he6_wugui_he_qu(self):
        # 丁未癸丑辛巳壬辰 坤，丁巳运戊子年离异：「戊代表巳火夫星虚透，
        # 戊癸一合，正式离异」（yx2:5877） -> 合去（书判）
        r = _run('丁未癸丑辛巳壬辰', '坤', '戊子', dy='丁巳')
        assert _he(r, '天干合', '癸') == '合去'

    def test_he7_zichou_he_ban(self):
        # 乙卯己卯壬子壬寅 乾，丁丑运甲戌年死：「丁壬合子丑合，切断了水…
        # 寿就到了」（cj1:1816）运支丑合日支子，用神被合住 -> 合绊（书判）
        r = classify_he_semantic(
            '六合', '子', list('乙己壬壬'), list('卯卯子寅'), '壬',
            dayun_zhi='丑', target_idx=2, gender='男', he_partner_dayun=True)
        assert r['he_type'] == '合绊'

    def test_ch2b_wugui_he_liu(self):
        # 癸卯壬戌丙戌丙申 坤，戊辰年成婚：「戊合了夫星…成婚」（cj1:2946）
        # 流年戊合年干癸（正官夫星） -> 合留
        r = _run('癸卯壬戌丙戌丙申', '坤', '戊辰')
        assert _he(r, '天干合', '癸') == '合留'


# ── 冲四种（7 条；冲旺无样本保持缺口） ────────────────────────────────

class TestChongSemantics:
    def test_ch1_you_chong_mao_dong(self):
        # 辛亥乙未乙卯戊寅 坤，戌运癸酉年成婚：「流年夫星（酉为辛的禄）
        # 冲入夫宫」（cj1:2936）夫宫卯原局有合（亥卯未） -> 冲动
        r = _run('辛亥乙未乙卯戊寅', '坤', '癸酉', dy='戊戌')
        assert _chong(r, '卯', pos='day_zhi') == '冲动'

    def test_ch2a_chen_chong_xu_dong(self):
        # 癸卯壬戌丙戌丙申 坤，戊辰年成婚：「辰是官杀库…冲动了夫宫」
        # （cj1:2946）夫宫戌原局卯戌合住 -> 冲动
        r = _run('癸卯壬戌丙戌丙申', '坤', '戊辰')
        assert _chong(r, '戌', pos='day_zhi') == '冲动'

    def test_ch3_chou_chong_wei_kai(self):
        # 丙辰癸巳己未丙寅 坤，丁丑年处男友：「丑未冲开了官库」
        # （cj1:2299，参 extra 2499）未=日支官库 -> 冲开
        r = _run('丙辰癸巳己未丙寅', '坤', '丁丑')
        assert _chong(r, '未', pos='day_zhi') == '冲开'

    def test_ch4_wu_chong_zi_qu(self):
        # 庚寅辛巳辛酉癸巳 坤，丙子运壬午年母子被杀：「午火冲去子水，癸水
        # 寿元星见子水为禄为寿，被午冲，主寿到了」（cj2:6042） -> 冲去（书判）
        r = _run('庚寅辛巳辛酉癸巳', '坤', '壬午', dy='丙子')
        hits = [i for i in r.get('dayun_interaction', []) if i['type'] == '冲']
        assert hits and hits[0]['chong_semantic']['chong_type'] == '冲去'

    def test_ch6_you_chong_lu_po(self):
        # 丁亥乙巳乙卯辛巳 乾，庚子运乙酉年急病死：「七杀冲禄主凶死…把禄
        # 给坏了」（cj2:5278）酉=七杀冲日主卯禄 -> 冲破
        r = _run('丁亥乙巳乙卯辛巳', '乾', '乙酉', dy='庚子')
        assert _chong(r, '卯', pos='day_zhi') == '冲破'

    @pytest.mark.xfail(reason='收档：戌为墓库冲开规则在先；「夫宫无合被冲='
                              '冲破」仅此一锚（cj1:2355），且与 ch3 冲开官库'
                              '同构反例+「墓库被太岁冲谓冲开」书诀冲突')
    def test_ch8_chen_chong_xu_po(self):
        # 乙巳辛巳甲戌壬申 坤，甲申运庚辰年离婚：「辰戌冲坏了夫宫戌土，
        # 此年离婚」（cj1:2355） -> 冲破（书判）
        r = _run('乙巳辛巳甲戌壬申', '坤', '庚辰', dy='甲申')
        assert _chong(r, '戌', pos='day_zhi') == '冲破'

    def test_ch9_you_chong_lu_po(self):
        # 丙午辛卯乙酉戊寅 乾，乙未运乙酉年车祸：「乙酉年是日主坐七杀，
        # 冲了卯禄…把人冲坏入院」（cj1:652）酉=七杀冲卯禄 -> 冲破
        r = _run('丙午辛卯乙酉戊寅', '乾', '乙酉', dy='乙未')
        assert _chong(r, '卯', pos='month_zhi') == '冲破'
