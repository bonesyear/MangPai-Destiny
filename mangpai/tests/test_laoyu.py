"""laoyu 牢狱书例哨兵（F9 批：批5 laoyu 四 P0 修复锁定——全模块此前零测试，
签名错配因此存活 3 年，本文件为最低哨兵面）

书锚（逐条明文，《盲派中级命理学》牢狱专辑）：
- 中级:5580-5582 「亥水、丑土、辰土…有阳性的有用的东西，被这些坏了，可能会
  有牢狱。如是阳制阴不为牢狱」
- 中级:5592 「凡出现反局的情况，有辰、丑等字在局中，多数应牢狱」（法五）
- 中级:5825-5829 上海庄家（戊申己未癸巳己未）「双杀夹克身，是有官灾之象」
  （月时双己未夹日主，日柱无杀）
- 中级:445-447 「此造也是七杀夹克日主，为牢狱命。且因罪大，已被枪毙」
  （己丁辛丁/未卯卯酉，月时双丁夹辛）
- 中级:5652-5659 冲合反局例（己壬己乙/巳申未丑）「成了反局（冲合反局）…
  大部分的反局结构都主牢狱之象，并且丑土也为牢狱象」
- 中级:5830-5834 判十年例（乙己壬辛/巳丑辰丑）「辰丑有牢象，阳被阴晦…
  牢狱是因为阴灭了阳，又见丑辰」
- 李嘉诚（戊辰己未庚午丁亥）：午亥克合制亥=阳制阴（同制四点书锚，KB§5.1），
  巨富无牢狱——阴灭阳假阳锚
"""
from mangpai.subjective.laoyu import (
    analyze_laoyu, detect_shaqie_zhi, detect_fanju_chen_chou, detect_laoyu_zi,
)


# ── P0-2：七杀夹克方向（月时双杀夹日主，日柱无杀；旧判据要求日柱带杀=方向反）──

def test_sha_jia_ke_shanghai_zhuangjia():
    # 上海庄家：月时双己未夹癸日主，书「双杀夹克身，是有官灾之象」（中级:5827）
    r = detect_shaqie_zhi('癸', list('戊己癸己'), list('申未巳未'))
    assert r['sha_jia_ke'] is True


def test_sha_jia_ke_qiangbi():
    # 枪毙例：月时双丁七杀夹辛日主（中级:445-447）
    r = detect_shaqie_zhi('辛', list('己丁辛丁'), list('未卯卯酉'))
    assert r['sha_jia_ke'] is True


def test_sha_jia_ke_no_false_positive():
    # 日柱带杀+仅月柱带杀（时柱无杀）不判夹克（旧方向反判据的误伤面）
    r = detect_shaqie_zhi('癸', list('戊己癸戊'), list('申未未子'))
    assert r['sha_jia_ke'] is False


# ── P0-1：法五「反局+辰丑」复活（旧调用 TypeError 被吞，上线即死 3 年）──

def test_fanju_chen_chou_book_case():
    # 冲合反局书例（己壬己乙/巳申未丑，中级:5652-5659）：主位逢冲宾位合=反局，
    # 丑在局——书「大部分的反局结构都主牢狱之象，并且丑土也为牢狱象」
    r = detect_fanju_chen_chou('己', list('己壬己乙'), list('巳申未丑'))
    assert r['fanju'] is True
    assert r['has_chen_chou'] is True
    assert r['laoyu'] is True  # 法五成立（旧码此处恒 False）


def test_fanju_chen_chou_not_fanju():
    # 正局+辰丑不触发法五
    r = detect_fanju_chen_chou('庚', list('戊己庚丁'), list('辰未午亥'))
    assert r['laoyu'] is False


# ── P0-4：阴灭阳收窄（阳火克合制牢狱字=阳制阴，书:5582「如是阳制阴不为牢狱」）──

def test_yin_mie_yang_book_true():
    # 判十年例（乙己壬辛/巳丑辰丑，中级:5832-5834）：辰丑晦巳=以阴灭阳（真阳锚）
    r = detect_laoyu_zi('壬', list('乙己壬辛'), list('巳丑辰丑'))
    assert r['yin_mie_yang'] is True


def test_yin_mie_yang_lijiacheng_false():
    # 李嘉诚：午亥克合制亥=阳制阴（同制四点书锚），阴灭阳不成立（假阳锚）
    r = detect_laoyu_zi('庚', list('戊己庚丁'), list('辰未午亥'))
    assert r['yin_mie_yang'] is False
    assert r['yang_zhi_yin'] is True


def test_lijiacheng_risk_not_high():
    # 李嘉诚巨富无牢狱：risk 不得为「高」（批5 实测旧码=高，四中假阳；
    # 修复后 高->中，残留枭神夺食/劫煞亡神两条=批5 P1 宽条款，留后续批）
    r = analyze_laoyu('庚', list('戊己庚丁'), list('辰未午亥'))
    assert r['risk'] != '高'
    assert '牢狱字(阴灭阳)' not in r['methods']
    assert '劫伤抗官' not in r['methods']  # 日主不算比劫 actor（KB§7.3）


# ── P0-3：阳制阴减凶兑现（旧码 :820 两分支同值「低」，减凶从未生效）──

def test_yang_zhi_yin_jianxiong():
    # 单法命中（水多金沉）+阳制阴（午亥克合制亥）在场 -> 减凶为「无」
    # （书:5582「如是阳制阴不为牢狱」；旧码必得「低」）
    # F13 传导同步：神煞默认改日支起算（gaoji:7912）后，旧盘 day=午→劫煞亥
    # 在局会多中「劫煞亡神」法（书口径日支查劫煞，命中本身正确）；本哨兵
    # 考的是阳制阴减凶，将午移至月支保持「单法命中」前提（合成盘，非书例）。
    r = analyze_laoyu('庚', list('壬辛庚壬'), list('未午亥亥'))
    assert r['hit_count'] == 1
    assert r['laoyu_zi']['yang_zhi_yin'] is True
    assert r['risk'] == '无'


# ── 真阳回归锚：比劫伤官怕见官（日主外比劫仍计，中级:5602-5608 抢劫判五年）──

def test_jieshang_guansha_still_fires():
    # 甲丁乙庚/寅卯丑辰：年干甲劫财+寅中伤官+庚官=比劫伤官怕见官（书判五年）
    r = analyze_laoyu('乙', list('甲丁乙庚'), list('寅卯丑辰'))
    assert '劫伤抗官' in r['methods']
