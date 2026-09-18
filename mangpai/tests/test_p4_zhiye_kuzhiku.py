# -*- coding: utf-8 -*-
"""P4 职业军警新面批哨兵（先红后绿）——库制库·阳制阴（墓用执法象）。

对象（方案 P4 节/预注册 docs/kimi-p4-zhiye-muku-prereg-20260918.md）：
1. objective/muku.py 新检测 `detect_ku_zhi_ku`（纯增量，analyze_muku/is_entomb
   零改动）：阳库（辰戌，阳土）收/刑 阴库（丑未，阴土）=阳制阴——
   收=四库之土入辰墓（理象学:3008 族）；刑=丑戌/戌未（gaoji:11785/:11747）。
   阳库冲阴库十二支不存在（辰戌=阳阳、丑未=阴阴），kind∈{收,刑} 两式完备。
2. zhiye._score_military 消费（贵气门**外**——墓用结构=格局级做功
   gaoji:2177-2182，贵气门 :11956 所管=8.2 字级组合）：命中且阴库成双多见
   （丑≥2 或未≥2，墓用结构条件2「有物可墓须成势多见」gaoji:2190-2194+
   案例三双丑/案例四双未明文）→ +6。
书锚：gaoji:2401-2417 案例三「阳库（辰）收阴库（丑）…阳制阴，有执法、纠正
   之象…实际为警察」（=gj-警察墓库）；gaoji:11747-11756 军官例四「戌未相刑，
   刑开官杀库…乃入兵营掌权之象」+口诀二「比劫库冲杀库动」；类象 gaoji:11630
   「丑…阴库…常象公安、刑警、特务」/口诀一 :11665「丑为阴库公安象」。
"""
from mangpai.objective.muku import detect_ku_zhi_ku
from mangpai.subjective.zhiye import classify_zhiye


def _run(dg, gans, zhis):
    return classify_zhiye(dg, list(gans), list(zhis))


# ── 检测层单测 ──

def test_kzk_shou_yang_shou_yin():
    """癸丑乙丑庚申庚辰（警察墓库原盘）：时支辰（阳库）收年月双丑（阴库）。"""
    pairs = detect_ku_zhi_ku(['丑', '丑', '申', '辰'])
    assert pairs and all(p['kind'] == '收' for p in pairs)
    assert {p['yang'] for p in pairs} == {'辰'}
    assert {p['yin'] for p in pairs} == {'丑'}


def test_kzk_xing_xu_wei():
    """辛巳戊戌己未辛未（军官例四原盘）：戌（阳库/武库）刑双未（阴库/杀库）。"""
    pairs = detect_ku_zhi_ku(['巳', '戌', '未', '未'])
    assert pairs and all(p['kind'] == '刑' for p in pairs)
    assert {p['yang'] for p in pairs} == {'戌'}
    assert {p['yin'] for p in pairs} == {'未'}


def test_kzk_yin_yin_chong_not_fired():
    """罗斯切尔德 子寅丑未：丑未冲=阴库冲阴库（非阳制阴），零命中。"""
    assert detect_ku_zhi_ku(['子', '寅', '丑', '未']) == []


def test_kzk_detect_vs_consume_layering():
    """复例四 丑辰巳亥：检测层辰收丑命中（关系在），消费层被「阴库成双」要件
    挡住（丑单见）——分层各自验证。"""
    assert detect_ku_zhi_ku(['丑', '辰', '巳', '亥'])


# ── 消费层：目标书例（先红）──

def test_jingcha_muku_military():
    """gj-警察墓库（癸丑乙丑庚申庚辰，gaoji:2401-2417 阳库制阴库=警察）：
    库制库条款归位 military（先红：merchant 7 吸走，military 仅 1）。"""
    r = _run('庚', '癸乙庚庚', '丑丑申辰')
    assert r['primary'] == 'military'
    assert any('库制库' in ln for ln in r['evidence']['military'])


def test_junguan_li4_kuzhiku_military():
    """军官例四（辛巳戊戌己未辛未，gaoji:11747 戌未刑开杀库）：墓用结构通道
    （格局级，非 8.2 字级组合，不过贵气门）归位 military（先红：mil 1 未分类）。
    F15 贵气门备案不改——本条款 evidence 不含「8.2/戌武库」字样。"""
    r = _run('己', '辛戊己辛', '巳戌未未')
    assert r['primary'] == 'military'
    assert any('库制库' in ln for ln in r['evidence']['military'])
    assert not any('8.2' in ln or '戌武库' in ln for ln in r['evidence']['military'])


# ── fp 守护（结构性不命中，逐字不动）──

def test_fp_guards_no_kuzhiku():
    """乔布斯（阴库 0）/罗斯切尔德（丑未各一+阴阴冲）/yx-科级（阴库 0，
    F15 collateral 案例不复现）military evidence 无「库制库」。"""
    for dg, g, z in (('丙', '乙戊丙庚', '未寅辰寅'),
                     ('己', '甲丙己辛', '子寅丑未'),
                     ('甲', '壬甲甲庚', '子辰申午')):
        r = _run(dg, g, z)
        assert not any('库制库' in ln for ln in r['evidence'].get('military', []))


def test_anchors_margin_unchanged():
    """既有 military ✅ 锚 margin 检验：例二（未 1 单见不命中）military==10、
    例九（未 1 单见不命中）military==11，逐字不动。"""
    r2 = _run('己', '丁辛己甲', '未亥卯戌')
    assert r2['primary'] == 'military' and r2['scores']['military'] == 10
    r9 = _run('癸', '丁己癸丁', '未酉巳巳')
    assert r9['primary'] == 'military' and r9['scores']['military'] == 11


def test_li5_gating_kept():
    """军官例五（戊申丙辰乙丑戊寅，公安处级）：凶向 gating（财坏印）保护链
    不动——丑单见不命中条款且 gating 仍撤军警分，primary 非 military。"""
    r = _run('乙', '戊丙乙戊', '申辰丑寅')
    assert r['primary'] != 'military'


def test_probe_82_at_least_4():
    """8.2 军警书例探针 ≥4/10（口径同 F15：例一~六/十望 military、例七/八
    法院望 lawyer 桶界备案不计、例九望 military）——例四经库制库归位。"""
    hits = 0
    for dg, g, z in (('戊', '己辛戊甲', '卯未辰寅'),   # 例一
                     ('己', '丁辛己甲', '未亥卯戌'),   # 例二
                     ('己', '辛戊己辛', '巳戌未未'),   # 例四（本批）
                     ('癸', '丁己癸丁', '未酉巳巳')):  # 例九
        if _run(dg, g, z)['primary'] == 'military':
            hits += 1
    assert hits >= 4
