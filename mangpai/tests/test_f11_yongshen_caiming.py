# -*- coding: utf-8 -*-
"""F11 批书例哨兵（批6 审计 yongshen P0×2 + caiming P0×2 修复锁定）

书锚（逐条明文）：
- 22期例6（癸乙丙丙/巳丑子申）：zhenbao:739-743「丙火之根巳远隔无力，且被丑土
  晦尽，无法帮身；乙木印星虽紧贴但也属无根，子水不算乙木的根，所以此造论从，
  看八字气势在官，以从官格看」——旧判「中和」（缺「晦」坏根机制+成势闸误杀）。
- 22期例7（己乙丙己/丑丑辰亥）：zhenbao:744-747「乙木印星根在亥，印星有根，
  故不能从」「以身弱看」——旧判「从弱」（conc>=6 粗闸抢跑压过书明文细则；
  段氏明文反对衰旺计数取用，shouke:454）。
- 财统官书例（乙己壬辛/巳丑辰丑）：zhongji:2853-2859「官多而财星少，财可统官…
  俱归于自己，所以他会有巨富」；书之要件=多/少+财官相连（财生官）+只论原局
  （zhongji:2817-2822 注「少指只有一个，且财官必须相连了，即财生官了」），
  「制」是运中应期非原局要件——旧码书外硬前置「主位制宾官」致漏检。
- 过河拆桥须验「该财确生该宾官」（位置相连）：ans12（丁未壬子丁巳辛丑）巳中庚
  中气财与壬官（月干）无生系（支藏干不生异柱天干），旧码仅全局验五行即入富格
  =假富格（书断小康不贵不富，shouke-ans12:2560）；zhongji:2977 书例「主位的酉
  生了宾位的亥官」为具体相连。
  真阳锚（不得误杀）：qi05-财运一般（庚戌丁亥丁巳癸卯，巳中庚财生月支亥官，
  支对支相邻=相连，制不尽=破财）；qi20-好嫖（己丑乙亥丁巳庚戌，同构富格）。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.yongshen import classify_strength
from mangpai.subjective.caiming import classify_caifu_view, analyze_caiming


# ── P0-1：22期例6 从官格（论从）──

def test_li6_cong_guan_ge():
    # 癸乙丙丙/巳丑子申：巳根被丑晦尽+乙印无根 -> 从（书：从官格）
    assert classify_strength('丙', ['癸', '乙', '丙', '丙'],
                             ['巳', '丑', '子', '申']) == '从弱'


# ── P0-2：22期例7 未从以身弱看 ──

def test_li7_wei_cong_shenruo():
    # 己乙丙己/丑丑辰亥：乙印根在亥（亥中甲中气），印有根 -> 不能从，身弱
    assert classify_strength('丙', ['己', '乙', '丙', '己'],
                             ['丑', '丑', '辰', '亥']) == '身弱'


def test_cong_regression_anchors():
    # 22期既有锚不回退（批6 复核全复现）
    assert classify_strength('庚', ['辛', '庚', '庚', '己'],
                             ['亥', '寅', '寅', '卯']) == '从弱'   # 例1 从财
    assert classify_strength('辛', ['辛', '庚', '辛', '壬'],
                             ['卯', '寅', '卯', '辰']) == '从弱'   # 例2 从财
    assert classify_strength('壬', ['丙', '壬', '壬', '庚'],
                             ['戌', '辰', '戌', '戌']) == '从弱'   # 例4 从杀
    assert classify_strength('壬', ['丙', '壬', '壬', '庚'],
                             ['午', '辰', '戌', '戌']) == '身弱'   # 例5 未从
    assert classify_strength('辛', ['壬', '戊', '辛', '庚'],
                             ['寅', '申', '卯', '寅']) == '从弱'   # 例8 从财


# ── P0-3：财统官书外前置「主位制宾官」移除，书例不再漏检 ──

def test_caitongguan_zhongji2853():
    # 乙己壬辛/巳丑辰丑：巳财生丑官相连，官（湿土）多财少 -> 财统官（书断巨富）
    v = classify_caifu_view('壬', ['乙', '己', '壬', '辛'], ['巳', '丑', '辰', '丑'])
    assert '财统官' in v['views']


# ── P0-4：过河拆桥验财生官相连（ans12 假富格根因）──

def test_ans12_not_fake_fuge():
    # 丁未壬子丁巳辛丑：桥=壬（月干，丁壬宾宾合制首中），巳中庚支藏财不生异柱
    # 天干 -> 无生系，不过河拆桥富格（书断小康不贵不富）
    r = analyze_caiming('丁', ['丁', '壬', '丁', '辛'], ['未', '子', '巳', '丑'])
    assert not any(v.startswith('过河拆桥') for v in r['caifu_view']['views'])
    # 注：tier 由 gongliang L3 基阶定（富），本修复拔掉的是假富格定式本身
    # （「至少不再假富格」——KB§5.2 ans12 根因修复锚；层级残留属 gongliang
    # 局部最优备案，非本批范围）


def test_qi05_qi20_guohe_anchors_hold():
    # 真阳锚：巳中庚财生月支亥官（支支相生=相连）——破财/富格两型不动
    v05 = classify_caifu_view('丁', ['庚', '丁', '丁', '癸'], ['戌', '亥', '巳', '卯'])
    assert '过河拆桥·破财' in v05['views']     # qi05 制不尽破财真阳
    v20 = classify_caifu_view('丁', ['己', '乙', '丁', '庚'], ['丑', '亥', '巳', '戌'])
    assert '过河拆桥·富格' in v20['views']     # qi20 制尽富格真阳


def test_qi02_qi20_guoting_guohe_hold():
    # 支支相生不限柱位（五行之气流通）：隔柱支财生支官仍相连
    v = classify_caifu_view('乙', ['甲', '丙', '乙', '己'], ['申', '子', '丑', '卯'])
    assert '过河拆桥·破财' in v['views']       # qi02-夫死：丑财生年支申官
    v2 = classify_caifu_view('丁', ['甲', '乙', '丁', '庚'], ['寅', '亥', '卯', '戌'])
    assert '过河拆桥·富格' in v2['views']      # qi20-歌厅小姐：戌中辛财生亥官
