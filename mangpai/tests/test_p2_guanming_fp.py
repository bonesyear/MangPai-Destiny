# -*- coding: utf-8 -*-
"""test_p2_guanming_fp — P2 官命 fp 窄修簇批哨兵（A12 女命夫宫域分流 / A17 旺杀入墓不开）

书锚（逐字回书已核，预注册=docs/kimi-p2-guanming-prereg-20260918.md）：
- A12 女命夫宫：chuji:2206-2209「此造女命不为当官，因夫宫巳火做功，巳火透天干
  戊土为丈夫，丈夫合制子水，为丈夫发财。如果是男命就为官了」（cj-2206）；
  yanjiu:5646-5652 同造重出「巳是夫宫…夫宫的原身戊去子」。
  真阳锚：cj-2097（chuji:2097 县级干部，印类豁免+印化官杀）、yx-部长
  （yanjiu:13114，移除涉日支 combo 后仍余 4 个非日支 combo）。
- A17 旺杀入墓墓不开不作功：chuji:1403-1405「旺杀入墓，墓又不开，所以不当官」
  +chuji:1409「七杀过旺而入丑墓，杀旺入墓主没事做」（cj-1395）；
  第二独立锚 chuji:3161「印入墓，墓又不开，不作功，穷命、无官」。
  真阳锚：曾国藩「四柱的功在墓杀」（lixiangxue:6972/yanjiu:10556，有官杀做功）、
  军官师级（lixiangxue:3137，官杀制比劫 combo 在场）——豁免=「功在墓杀」vs
  「墓不开不作功」的书内区分本身。

修法纪律：全部走 guanming 消费侧（classify_guanming_combo 域级过滤/flag），
objective 检测器零改动；gender 经 analyze_guanming 新增 kwarg 透传（旧调用
不传=零行为变化）。
"""
from mangpai.subjective.guanming import classify_guanming_combo, analyze_guanming


def _split(gz4):
    return [g[0] for g in gz4], [g[1] for g in gz4]


# cj-2206：乙巳 戊子 丁巳 庚戌（坤，chuji:2206）
CJ2206 = ('乙巳', '戊子', '丁巳', '庚戌')
# cj-2097：癸卯 甲寅 丙戌 庚子（坤，chuji:2097 县级干部，真阳锚）
CJ2097 = ('癸卯', '甲寅', '丙戌', '庚子')
# yx-部长：甲申 丙寅 乙卯 辛巳（坤，yanjiu:13114，真阳锚）
YXBUZHANG = ('甲申', '丙寅', '乙卯', '辛巳')
# cj-1395：癸卯 辛酉 乙酉 丁丑（乾，chuji:1395）
CJ1395 = ('癸卯', '辛酉', '乙酉', '丁丑')
# reg67-曾国藩乙未：乙未 己亥 丙辰 己亥（lixiangxue:6972「功在墓杀」真阳锚）
ZENG_BF = ('乙未', '己亥', '丙辰', '己亥')
# reg67-军官师级：己卯 辛未 戊辰 甲寅（lixiangxue:3137 真阳锚）
JUNGUAN = ('己卯', '辛未', '戊辰', '甲寅')
# reg67-公安：戊申 丙辰 乙丑 戊寅（lixiangxue:9376 保护锚）
GONGAN = ('戊申', '丙辰', '乙丑', '戊寅')


def _analyze(gz4, **kw):
    gans, zhis = _split(gz4)
    return analyze_guanming(gans[2], gans, zhis, **kw)


# ─────────── A12 女命夫宫做功归夫荣域（消费侧域级分流）───────────

def test_a12_cj2206_female_not_guanming():
    """cj-2206 女命：夫宫巳火做功（子水克巳火官杀制比劫涉日支）→ 归夫荣域，
    不计己官（「此造女命不为当官…如果是男命就为官了」chuji:2206）。"""
    r = _analyze(CJ2206, gender='女')
    assert r['is_guanming'] is False
    assert any('夫宫' in d and '夫荣' in d for d in r['combo']['details'])


def test_a12_cj2206_male_unchanged():
    """对照：同盘男命（「如果是男命就为官了」）——夫宫分流不触发，判定不变。"""
    r = _analyze(CJ2206, gender='男')
    assert r['is_guanming'] is True


def test_a12_gender_default_unchanged():
    """向后兼容：不传 gender（calib/旧测试路径）→ 零行为变化。"""
    r = _analyze(CJ2206)
    assert r['is_guanming'] is True


def test_a12_cj2097_true_anchor_kept():
    """真阳锚 cj-2097（坤，县级干部）：印类 combo（印制伤食）豁免+印化官杀
    兜底，夫宫分流后不翻（chuji:2097「癸卯带象，为当文化类的官」）。"""
    r = _analyze(CJ2097, gender='女')
    assert r['is_guanming'] is True


def test_a12_yxbuzhang_true_anchor_kept():
    """真阳锚 yx-部长（坤）：涉日支 combo 被移除后仍余非日支 combo（巳火克
    申金伤食制官杀等），判定不翻（yanjiu:13114）。"""
    r = _analyze(YXBUZHANG, gender='女')
    assert r['is_guanming'] is True
    # 夫宫 combo（申卯暗合/申克卯涉日支卯）确被分流移除
    assert any('夫宫' in d for d in r['combo']['details'])


# ─────────── A17 旺杀入墓墓不开+无官杀做功 → 不立官 ───────────

def test_a17_cj1395_not_guanming():
    """cj-1395：酉酉旺杀多而入丑墓、丑无冲刑未开、无官杀做功 combo →
    「墓又不开，所以不当官」（chuji:1405/1409）。"""
    r = _analyze(CJ1395)
    assert r['is_guanming'] is False
    assert any('入墓' in d and '墓不开' in d for d in r['combo']['details'])


def test_a17_zeng_guofan_true_anchor_kept():
    """真阳锚 曾国藩（亥亥入辰墓未开）：伤食制官杀 combo 在场=「功在墓杀」
    （墓统杀为所用），豁免不否（lixiangxue:6972，官至极品）。"""
    r = _analyze(ZENG_BF)
    assert r['is_guanming'] is True


def test_a17_junguan_true_anchor_kept():
    """真阳锚 军官师级（卯寅入未墓）：官杀制比劫 combo 在场=官杀做功，
    豁免不否（lixiangxue:3137，师级）。"""
    r = _analyze(JUNGUAN)
    assert r['is_guanming'] is True


# ─────────── 保护锚 margin 复验（预注册 §六）───────────

def test_protect_anchor_gongan_kept():
    """保护锚 reg67-公安（男）：A12 不适用；A17 官主气支=申1支<2 不满足。"""
    r = _analyze(GONGAN)
    assert r['is_guanming'] is True


def test_a17_vacuous_without_two_guan_branches():
    """A17 须≥2 官杀主气支方判（防 vacuous 误火）：公安锚申官 1 支不触发。"""
    gans, zhis = _split(GONGAN)
    combo = classify_guanming_combo(gans[2], gans, zhis)
    assert combo['is_guanming'] is True
    assert not any('墓不开' in d and '不立官命' in d for d in combo['details'])
