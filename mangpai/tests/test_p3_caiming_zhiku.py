# -*- coding: utf-8 -*-
"""test_p3_caiming_zhiku — P3 财命残簇批哨兵（A13 制库基阶落位两条款）

书锚（逐字回书已核，预注册=docs/kimi-p3-caiming-prereg-20260918.md）：
- 条款一（上限）：制库独力上浮封顶富，库同藏官杀（「财库加官杀」）者除外。
  保端=yx-煤矿（yanjiu:7689-7691「丑为财库加官杀，做功能量很大…发财十几亿」）
  /奥纳西斯（lixiangxue:6470-6474 四层功量，gongliang L4 直达不经上浮链）；
  杀端=cj-富火运（chuji:5526-5530「戌中辛偏弱…财不大…数百万」）
  /reg67-制例二（lixiangxue:6478-6484「虽也是富命，但远不如前者…数千万」）。
- 条款二（下限 sticky）：制库在档，明财三阻（浮财/合绊/入墓）下浮落富不落小康——
  库财通道独立于明财，与既有 floor「基阶不落下富」同口径收束「升后复降」矛盾。
  杀端=制例二（明财壬坐壬戌自合柱被合绊，48期天地合；书判富命，引擎小康=直接矛盾）。

A4/A12 收档（前提复核见预注册 §一）：A4 怕见官传导已由 yongshen N1「成势怕见官」
severe 条款承担（:879-921，gj-低保伤官 gaoji:19657），scored 残余目标=零，b67-过河拆桥
富锚具怕见官 facet 为反向锚；A12 体坏=N5 已接入 mingju_xiong（yongshen.py:1682-1684，
独眼乞食 ✅），全库命中面仅此 1 例。两项各立 guard 测锁现状。

修法纪律：全走 caiming 消费侧（_detect_zhiku_decai 增输出字段 ku_han_guansha
+上浮链新增封顶+阻断降档落位），objective 零改动，不动既有上浮链其他分支。
"""
from mangpai.subjective.caiming import analyze_caiming, _detect_zhiku_decai


def _split(gz4):
    return [g[0] for g in gz4], [g[1] for g in gz4]


def _tier_static(gz4):
    gans, zhis = _split(gz4)
    r = analyze_caiming(gans[2], gans, zhis)
    return r['level_static']['tier'], r


# yx-煤矿：丁巳 癸丑 丙戌 甲午（保端①，丑=财库加官杀，能量大→巨富）
MEIKUANG = ('丁巳', '癸丑', '丙戌', '甲午')
# b67-制例一奥纳西斯：乙巳 己丑 己未 庚午（保端②，L4 直达）
AONAXIS = ('乙巳', '己丑', '己未', '庚午')
# cj-富火运发财数百：乙巳 丙戌 丁未 庚戌（杀端②，戌中辛偏弱财不大→富）
FUHUOYUN = ('乙巳', '丙戌', '丁未', '庚戌')
# reg67-制例二：丙午 辛丑 戊寅 壬戌（杀端①，虽也是富命→富）
ZHILI2 = ('丙午', '辛丑', '戊寅', '壬戌')
# gj-入狱一年：丙午 辛丑 戊戌 戊午（凶向全量轨封顶小康保；static 落富）
RUYU = ('丙午', '辛丑', '戊戌', '戊午')
# b67-李嘉诚：戊辰 己未 庚午 丁亥（净制豁免锚，zhiku=False 结构性不动）
LIJIACHENG = ('戊辰', '己未', '庚午', '丁亥')
# famous-保尔森：丙申 壬辰 戊辰 壬戌→以 trainset famous-保尔森盘复核（zhiku=False）
# zj-独眼乞食：丁亥 癸丑 丁未 辛亥（N5 severe 封顶贫保）
DUYAN = ('丁亥', '癸丑', '丁未', '辛亥')
# gj-低保伤官：辛卯 辛丑 戊申 辛酉（A4 收档 guard——N1 已承担封顶贫）
DIBAO = ('辛卯', '辛丑', '戊申', '辛酉')
# b67-过河拆桥：辛卯 戊戌 己亥 癸酉（A4 反向锚：怕见官 facet 而书判富，财明现通关）
GUOHE = ('辛卯', '戊戌', '己亥', '癸酉')


# ─────────── 条款一：制库独力上浮封顶富（库无官杀同藏）───────────

def test_ku_han_guansha_schema():
    """新字段 ku_han_guansha：煤矿丑藏癸=丙日官杀→True；制例二丑无木官→False。"""
    gans, zhis = _split(MEIKUANG)
    assert _detect_zhiku_decai(gans[2], gans, zhis)['ku_han_guansha'] is True
    gans, zhis = _split(ZHILI2)
    assert _detect_zhiku_decai(gans[2], gans, zhis)['ku_han_guansha'] is False


def test_t1_fuhuoyun_capped_fu():
    """cj-富火运：戌藏戊辛丁、丁日官杀=水无藏 → 独力上浮封顶富（书「财不大…数百万」）。"""
    tier, _ = _tier_static(FUHUOYUN)
    assert tier == '富'


def test_t1_zhili2_capped_fu():
    """reg67-制例二：丑无木官 → 封顶富（书「虽也是富命，但远不如前者…数千万」）。"""
    tier, _ = _tier_static(ZHILI2)
    assert tier == '富'


def test_t1_meikuang_exempt_jufu():
    """yx-煤矿：丑藏癸官杀（财库加官杀，做功能量很大）→ 豁免封顶，保巨富。"""
    tier, _ = _tier_static(MEIKUANG)
    assert tier == '巨富'


def test_t1_aonaxisi_jufu_unchanged():
    """奥纳西斯：gongliang L4 直达巨富（base=4 不经上浮链），结构性不动。"""
    tier, _ = _tier_static(AONAXIS)
    assert tier == '巨富'


# ─────────── 条款二：制库在档，明财阻断下浮落富不落小康 ───────────

def test_t2_zhili2_heban_floor_fu():
    """制例二：明财壬坐壬戌自合柱被合绊（48期天地合），制库在档 → 落富不落小康。"""
    tier, r = _tier_static(ZHILI2)
    assert tier == '富'
    assert '制库' in r['level_static']['adjust']


def test_t2_ruyu_xiong_cap_unchanged():
    """gj-入狱一年：static 落富（条款一）；全量轨岁运反局封顶小康由 blind diff
    兜底（本测直调 analyze_caiming 不喂运岁，岁运反局链不在此触发）。"""
    gans, zhis = _split(RUYU)
    r = analyze_caiming(gans[2], gans, zhis)
    assert r['level_static']['tier'] == '富'


# ─────────── 富命锚/A4·A12 收档 guard ───────────

def test_anchor_lijiacheng_jufu():
    """李嘉诚：净制巨富锚（zhiku=False，结构性不动）。"""
    tier, _ = _tier_static(LIJIACHENG)
    assert tier == '巨富'


def test_a12_guard_duyan_pin():
    """A12 收档 guard：独眼乞食 N5 体坏 severe 已接入 mingju_xiong → 封顶贫保。"""
    tier, _ = _tier_static(DUYAN)
    assert tier == '贫'


def test_a4_guard_dibao_pin_and_guohe_fu():
    """A4 收档 guard：低保伤官（N1 成势怕见官 severe）封顶贫保；过河拆桥富锚
    （具怕见官 facet 而财明现通关）不触封顶，保富。"""
    tier, _ = _tier_static(DIBAO)
    assert tier == '贫'
    tier, _ = _tier_static(GUOHE)
    assert tier == '富'
