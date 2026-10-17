# -*- coding: utf-8 -*-
"""F16 hunyin 四格机制重写哨兵（先红后绿）。

书锚：
  好婚姻=宫制/冲去夫妻星忌神（zhongji:4289-4294/4300）、宫坐库喜刑冲（:4493）、
        穿去忌神（:4504/4340）——冲穿刑非一律凶；
  制不住反坏（zhongji:4290/4303-4308，戴安娜:4509-4518）；
  水中捞月三要素=正星坐宫+日主日支自合+天干偏星干扰（zhongji:5081-5083/
        gaoji:12904-12910，自合柱:5098，扩大型:5099-5105）；
  独身四格=宫占比劫禄印/宫星互害反成克/星入墓库不开/水中捞月偏星扰
        （gaoji:13068-13070/zhongji:4924-4928，纯阳纯阴/华盖无书锚）；
  关财门=女命专属、运岁比劫夺财（财是官之原神）离婚应期
        （gaoji:12963-12967/zhongji:3578）；
  禄绊桃花=日主之禄与他星六合/三合（zhongji:1517/gaoji:13259-13310 案例八/九）。
"""
from mangpai.subjective.hunyin import (
    classify_hunyin_quality, detect_shuizhong_laoyue, classify_dushen_sige,
    detect_guan_caimen, detect_lu_ban_taohua, _spouse_wx,
)


def _q(gans, zhis, gender):
    return classify_hunyin_quality(gans[2], gans, zhis, gender)['quality']


class TestGongZhiXingHaohun:
    """宫制/冲去夫妻星忌神=好婚姻（P0-1 + 冲穿刑四吉例）。"""

    def test_4294_gong_chong_qu_xing_jishen(self):
        # 坤 癸庚庚壬/丑申子午：金水成势，子水宫为用神冲去午官忌神，好婚姻
        assert _q(['癸', '庚', '庚', '壬'], ['丑', '申', '子', '午'], '女') == '好'

    def test_4300_hai_chong_si(self):
        # 坤 癸癸辛癸/丑亥亥巳：金水有势，亥宫冲巳官忌神，婚姻很好
        assert _q(['癸', '癸', '辛', '癸'], ['丑', '亥', '亥', '巳'], '女') == '好'

    def test_4493_gong_zuo_ku_xi_xingchong(self):
        # 乾 壬庚壬癸/寅戌辰卯：夫妻宫坐辰库，戌冲开库，库喜刑冲，好婚姻
        assert _q(['壬', '庚', '壬', '癸'], ['寅', '戌', '辰', '卯'], '男') == '好'

    def test_4504_chuan_qu_jishen(self):
        # 乾 乙丙甲甲/未戌子戌：火与燥土成势，未穿去子宫忌神，婚姻较好
        assert _q(['乙', '丙', '甲', '甲'], ['未', '戌', '子', '戌'], '男') == '好'


class TestZhiBuZhuFanHuai:
    """宫制星制不住/宫有用被坏=差（防吉制条款过杀）。"""

    def test_diana_zhi_buzhu(self):
        # 坤 辛甲乙丙/丑午未戌：未欲制丑被戌刑坏，制不住→必离（zhongji:4516-4518）
        assert _q(['辛', '甲', '乙', '丙'], ['丑', '午', '未', '戌'], '女') == '差'

    def test_4303_shuihuo_xiangdang_zhi_buzhu(self):
        # 坤 壬乙庚壬/子巳子午：水火力量相当，夫宫制不住夫星，婚难好
        assert _q(['壬', '乙', '庚', '壬'], ['子', '巳', '子', '午'], '女') == '差'

    def test_4365_gong_yong_bei_chong(self):
        # 乾 戊己乙丁/戌未巳亥：火土成势，巳宫用神被亥冲坏，感情不好
        assert _q(['戊', '己', '乙', '丁'], ['戌', '未', '巳', '亥'], '男') == '差'


class TestShuizhongLaoyue:
    """水中捞月三要素（P0-2）。"""

    def test_anli10_zihe_zhengcai_piancai_tou(self):
        # 乾 辛庚己癸/卯子亥酉：亥正星+己亥自合+癸偏财透（zhongji:5068-5084）
        r = detect_shuizhong_laoyue('己', ['辛', '庚', '己', '癸'], ['卯', '子', '亥', '酉'], '男')
        assert r['is_laoyue']

    def test_5085_nv_zhengguan_qisha_tou(self):
        # 坤 乙丙己庚/卯戌亥午：亥中甲正官+己亥自合+乙七杀透（zhongji:5085-5090）
        r = detect_shuizhong_laoyue('己', ['乙', '丙', '己', '庚'], ['卯', '戌', '亥', '午'], '女')
        assert r['is_laoyue']

    def test_5099_kuoda_xing(self):
        # 坤 己丙壬己/丑寅午酉：午宫正官+壬午自合+丙偏财（自合对象正财之偏）
        r = detect_shuizhong_laoyue('壬', ['己', '丙', '壬', '己'], ['丑', '寅', '午', '酉'], '女')
        assert r['is_laoyue']

    def test_fanli_wu_zihe_bu_laoyue(self):
        # 乾 乙癸辛戊/亥未亥戌：无自合，闲注「按水中捞月三要素看就不是」
        r = detect_shuizhong_laoyue('辛', ['乙', '癸', '辛', '戊'], ['亥', '未', '亥', '戌'], '男')
        assert not r['is_laoyue']


class TestDuShenSiGe:
    """独身四格书诀（P0-5）。"""

    def test_ge1_gong_zhan_bijie(self):
        # 乾 甲丙己戊/辰子未辰（教授）：宫占比肩，子水妻星被未穿不得入
        r = classify_dushen_sige('己', ['甲', '丙', '己', '戊'], ['辰', '子', '未', '辰'], '男')
        assert any('宫占比劫' in g for g in r['grids']) and r['is_dushen']

    def test_ge2_gong_zhi_xing_fan_huai(self):
        # 坤 丁壬庚壬/未寅子午：子宫伤官欲制午官，木火有势反坏宫（gaoji:12862 案例八）
        r = classify_dushen_sige('庚', ['丁', '壬', '庚', '壬'], ['未', '寅', '子', '午'], '女')
        assert any('互' in g or '反' in g for g in r['grids']) and r['is_dushen']

    def test_ge3_xing_ru_mu_bu_kai(self):
        # 坤 辛辛丙甲/卯丑辰午（老姑娘）：夫宫辰=夫星水之墓，无冲刑开库
        r = classify_dushen_sige('丙', ['辛', '辛', '丙', '甲'], ['卯', '丑', '辰', '午'], '女')
        assert any('入墓' in g for g in r['grids']) and r['is_dushen']

    def test_ge4_laoyue_ge(self):
        # 水中捞月=独身第四格（zhongji:4939-4940「应属于水中捞月结构」）
        r = classify_dushen_sige('己', ['辛', '庚', '己', '癸'], ['卯', '子', '亥', '酉'], '男')
        assert any('捞月' in g for g in r['grids']) and r['is_dushen']

    def test_fanli_haohun_bu_dushen(self):
        # 好婚姻例（4294）不得误中独身
        r = classify_dushen_sige('庚', ['癸', '庚', '庚', '壬'], ['丑', '申', '子', '午'], '女')
        assert not r['is_dushen']


class TestGuanCaimen:
    """关财门=女命运岁比劫夺财（P0-4）。"""

    def test_anli12_mao_yun_chong_you_cai(self):
        # 坤 辛己丙丁/丑亥午酉，癸卯大运：卯冲酉财，财门一关官无源，闹离
        r = detect_guan_caimen('丙', ['辛', '己', '丙', '丁'], ['丑', '亥', '午', '酉'], '女',
                               dayun_gan='癸', dayun_zhi='卯')
        assert r['is_guanmen']

    def test_nanming_bu_lun(self):
        # 书限女命（gaoji:12963「女命关财门最验」），男命同构不论
        r = detect_guan_caimen('丙', ['辛', '己', '丙', '丁'], ['丑', '亥', '午', '酉'], '男',
                               dayun_gan='癸', dayun_zhi='卯')
        assert not r['is_guanmen']

    def test_wu_yunsui_bu_chu(self):
        # 无运岁引动（仅原局）不触发——关财门是应期概念
        r = detect_guan_caimen('丙', ['辛', '己', '丙', '丁'], ['丑', '亥', '午', '酉'], '女')
        assert not r['is_guanmen']


class TestLuBanTaohua:
    """禄绊桃花=禄与他星合（F13 机制锁，gaoji 案例八/九）。"""

    def test_anli8_chen_you_he_lu(self):
        # 坤 乙辛辛壬/卯巳酉辰：辛禄酉，辰酉合，辰藏癸食神→禄绊桃花
        r = detect_lu_ban_taohua('辛', ['乙', '辛', '辛', '壬'], ['卯', '巳', '酉', '辰'], '女')
        assert r['is_lu_ban']

    def test_anli9_mao_xu_he_lu(self):
        # 坤 戊壬乙丁/午戌卯亥：乙禄卯，卯戌合，戌藏辛七杀→禄绊桃花
        r = detect_lu_ban_taohua('乙', ['戊', '壬', '乙', '丁'], ['午', '戌', '卯', '亥'], '女')
        assert r['is_lu_ban']


class TestSpouseStarSubstitute:
    """配偶星替代规则（zhongji:4280「如无则另看：男命无财看伤食，女命无官杀
    看印星」；gaoji:12361 口诀互证）。藏干口径同 _star_positions。"""

    def test_nan_wu_cai_qu_shishang(self):
        # 乾 甲子/甲子/甲子/甲酉：全局无土（财），取食伤=火
        assert _spouse_wx('甲', '男', list('甲甲甲甲'), list('子子卯酉')) == '火'

    def test_nv_wu_guansha_qu_yin(self):
        # 坤 甲午/丙卯/甲午/丁亥：全局无金（官杀），取印=水
        assert _spouse_wx('甲', '女', list('甲丙甲丁'), list('午卯午亥')) == '水'

    def test_you_cai_bu_tidai(self):
        # 乾 甲寅/甲卯/甲子/甲酉：寅中戊余气为财，财现不替代
        assert _spouse_wx('甲', '男', list('甲甲甲甲'), list('寅卯子酉')) == '土'


class TestGongZhiXingZhengPian:
    """宫制星分正偏（zhongji:4466-4468「偏星可以制，正星不可以制。正星受制，
    婚姻易出问题」；仅夫妻星得位坐宫时论）。"""

    def test_zhengxing_zuogong_shouzhi(self):
        # 乾 癸亥/甲子/甲丑/庚戌：日支丑本气己=正财（正星得位坐宫），戌刑丑
        # → 正星受制，不加好婚姻分，出负向信号（旧代码不分正偏 +2.0 判好）
        r = classify_hunyin_quality('甲', ['癸', '甲', '甲', '庚'],
                                    ['亥', '子', '丑', '戌'], '男')
        assert any('正星坐宫被制' in s for s in r['signals'])
        assert r['quality'] != '好'

    def test_pianxing_zuogong_kezhi_weichi(self):
        # 乾 癸亥/甲子/甲辰/辛戌：日支辰本气戊=偏财（偏星坐宫），戌冲辰
        # → 偏星可以制，维持宫制星加分判好
        r = classify_hunyin_quality('甲', ['癸', '甲', '甲', '辛'],
                                    ['亥', '子', '辰', '戌'], '男')
        assert r['quality'] == '好'
        assert any('宫制去夫妻星忌神' in s for s in r['signals'])


# ── 批E：结/离婚应期前提补全 + 结婚/离婚信号冲突消解 ──
# (a) 冲宫为婚期须原局有合、合处逢冲（中级:5283-5284）；
# (b) 支合宫须来支为/含配偶星（中级:5143-5147）；
# (c) 干合日干须验是配偶星且有根（中级:5217/5219-5220「无根虚浮，逢合
#     必制之坏之，不能定为婚姻的应期」）；
# (d) 冲宫事件分向（chuji:6096「原局逢合大运和流年逢冲时为应期，原局
#     有冲时大运和流年逢合时为应期」）：原局宫有合时冲=结婚向（离婚侧
#     不再出「宫动散」）；裸冲（原局无合）不再出结婚向。

from mangpai.subjective.hunyin import infer_jiehun_yingqi, infer_lihun_yingqi


def test_e_chong_gong_he_chu_feng_chong():
    """原局宫有合（日时卯戌合），流年酉冲卯=合处逢冲→结婚应期；
    同一冲宫事件离婚侧不再出「夫妻宫动散」。"""
    g, z = ['甲', '丙', '戊', '辛'], ['子', '午', '卯', '戌']
    j = infer_jiehun_yingqi('戊', g, z, '男', liunian_zhi='酉')
    l = infer_lihun_yingqi('戊', g, z, '男', liunian_zhi='酉')
    assert any('合处逢冲' in s for s in j['signals'])
    assert not any('动散' in s for s in l['signals'])


def test_e_bare_chong_no_jiehun_signal():
    """裸冲（原局宫无合）：结婚侧不出冲宫信号；离婚侧保留宫动散。"""
    g, z = ['甲', '丙', '戊', '辛'], ['子', '午', '卯', '辰']
    j = infer_jiehun_yingqi('戊', g, z, '男', liunian_zhi='酉')
    l = infer_lihun_yingqi('戊', g, z, '男', liunian_zhi='酉')
    assert not any('冲婚姻宫' in s for s in j['signals'])
    assert any('动散' in s for s in l['signals'])


def test_e_he_gong_requires_spouse_star():
    """支合宫须来支为/含配偶星：丙日（财=金，局有酉金）申宫，
    流年巳（藏庚=财）巳申合 → 出信号；寅宫流年亥（壬甲，不含金）
    寅亥合 → 不出。"""
    j1 = infer_jiehun_yingqi('丙', ['乙', '丁', '丙', '辛'],
                             ['酉', '子', '申', '卯'], '男', liunian_zhi='巳')
    assert any('合婚姻宫' in s for s in j1['signals'])
    j2 = infer_jiehun_yingqi('丙', ['乙', '丁', '丙', '辛'],
                             ['酉', '子', '寅', '卯'], '男', liunian_zhi='亥')
    assert not any('合婚姻宫' in s for s in j2['signals'])


def test_e_gan_he_daygan_requires_rooted_star():
    """干合日干须是配偶星且有根：甲日己（正财）合甲——局有土根（辰）
    → 出信号；局全无土（财不存、己无根虚浮）→ 不出。"""
    j1 = infer_jiehun_yingqi('甲', ['乙', '丁', '甲', '庚'],
                             ['寅', '辰', '子', '申'], '男', liunian_gan='己')
    assert any('合日干' in s for s in j1['signals'])
    j2 = infer_jiehun_yingqi('甲', ['乙', '丁', '甲', '庚'],
                             ['卯', '子', '酉', '亥'], '男', liunian_gan='己')
    assert not any('合日干' in s for s in j2['signals'])
