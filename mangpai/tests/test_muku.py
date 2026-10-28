"""muku 墓库书例哨兵（F2 批：批3 muku 三 P0 + 批1 TOMB_MAP 缺戌修复锁定）

书锚（逐条明文）：
- 《段氏理象学》:2035 「木墓在未，火墓在戌，金墓在丑，水墓在辰，土墓在辰、戌」
- 《段氏理象学》:3002-3005 「多而墓之，即只要是天干地支合在一起，有两个或两个以上，
  见墓即入，如辛酉柱见丑，即辛酉入丑墓，不论酉丑拱局」
- 《段氏理象学》:3008-3009 「地支土之墓库比较特别，丑入辰墓，未也入辰墓」（无「多」前提）
- 《段氏理象学》:3080-3084 书例（己辛戊甲/卯未辰寅）「未入辰墓，自己控制着军队」
- 《理象学研究》:6200 蒋介石例「主位巳、午同入戌墓，墓加一层功」
- 《理象学研究》:12311 「未运刑开戌中之火使巳火不入戌」（戌开则释火）
- 奥纳西斯（乙巳己丑己未庚午）：丑未冲开库、制库得财（KB§5.1）
"""
from mangpai.objective.constants import TOMB_MAP
from mangpai.objective.muku import is_entomb, analyze_muku


# ── P0-3：TOMB_MAP 戌=土墓（理象学:2035 土墓在辰、戌双位）──

def test_tomb_map_tu_shuangwei():
    assert '土' in TOMB_MAP['辰']
    assert '土' in TOMB_MAP['戌']  # 书:2035「土墓在辰、戌」
    assert '火' in TOMB_MAP['戌']


# ── P0-1：多而墓之计天干（书:3002-3005 辛酉柱见丑）──

def test_duo_er_mu_zhi_counts_gan():
    # 辛酉柱见丑：辛（干金）+酉（支金）=两个金，见丑即入，不论拱局
    assert is_entomb('酉', '丑', ['酉', '丑', '卯', '巳'],
                     ['辛', '丙', '甲', '己']) is True
    # 无金透干、盘仅一酉 → 非多，不入（旧口径保护：天干不参与则维持地支计数）
    assert is_entomb('酉', '丑', ['酉', '丑', '卯', '巳'],
                     ['丙', '丁', '甲', '己']) is False
    # 两酉见一丑（书:3004 明文第二例）仍入
    assert is_entomb('酉', '丑', ['酉', '酉', '丑', '午']) is True


# ── P0-2：四库之土直接入辰墓（书:3008 无「多」前提；书例:3080-3084）──

def test_siku_tu_ru_chen_direct():
    # 书例：己辛戊甲/卯未辰寅「未入辰墓」——盘仅一未（非多）亦入
    assert is_entomb('未', '辰', ['卯', '未', '辰', '寅']) is True
    # 丑入辰墓（书:3008 明文）
    assert is_entomb('丑', '辰', ['丑', '午', '辰', '寅']) is True
    # 原则5只列丑、未，不把戌也套入辰墓（R6 纠偏）
    assert is_entomb('戌', '辰', ['子', '寅', '辰', '戌']) is False


# ── 戌特判（火）：蒋介石巳午入戌 + 戌开释火（KB§4.9，勿删）──

def test_jiang_jieshi_si_wu_ru_xu():
    # 蒋介石：丁亥庚戌己巳庚午，戌未开（无辰、无丑未）→ 巳午同入戌墓
    zhis = ['亥', '戌', '巳', '午']
    assert is_entomb('巳', '戌', zhis) is True   # 四生见墓直进
    assert is_entomb('午', '戌', zhis) is True   # 巳+午两火=多而墓之


def test_xu_opened_releases_fire():
    # 戌被辰冲开 → 释火，巳午不入戌（研究:12311）
    zhis = ['辰', '戌', '巳', '午']
    assert is_entomb('巳', '戌', zhis) is False
    assert is_entomb('午', '戌', zhis) is False


# ── 端到端：奥纳西斯丑未冲开库 / 无透干刑冲亦有用 ──

def test_onassis_chou_wei_chong_kai_ku():
    # 奥纳西斯 乙巳己丑己未庚午：丑未冲，庚透引拔丑金、乙透引拔未木 → 皆开库
    r = analyze_muku(['巳', '丑', '未', '午'], ['乙', '己', '己', '庚'])
    opened = {t['zhi'] for t in r['open_tombs']}
    assert {'丑', '未'} <= opened


def test_no_tougan_near_chong_is_controlled_not_open():
    # 无透干近冲可做功，但只记制库，不把「有用」误作开财主大发
    r = analyze_muku(['巳', '丑', '未', '午'], ['丙', '丙', '戊', '壬'])
    controlled = {t['zhi'] for t in r['controlled_tombs']}
    assert {'丑', '未'} <= controlled
    assert not r['open_tombs']


def test_caiku_no_tougan_is_not_open_wealth():
    from mangpai.subjective.caiming import _detect_caiku
    rows = _detect_caiku('甲', ['庚', '庚', '庚', '甲'],
                         ['午', '戌', '巳', '丑'], None)
    statuses = {t['zhi']: (t['status'], t['view']) for t in rows}
    assert statuses['戌'] == ('制库', '制财库')


def test_remote_chong_is_touched_not_open():
    # 初级:3447「遥冲为冲动，也有冲开之意」：年时遥冲只记动库，不冒充明确开库
    zhis = ['辰', '午', '巳', '戌']
    r = analyze_muku(zhis, ['庚', '庚', '庚', '甲'])
    assert any(t['zhi'] == '戌' and t['status'] == '动库'
               for t in r['touched_tombs'])
    assert not any(t['zhi'] == '戌' for t in r['open_tombs'])
    assert is_entomb('巳', '戌', zhis) is True


def test_remote_chong_with_tougan_can_open():
    # 理象学:2039「墓神透干或引出方有用」：遥冲有引出时仍可开库
    r = analyze_muku(['辰', '午', '巳', '戌'], ['戊', '戊', '戊', '甲'])
    assert any(t['zhi'] == '戌' and t['status'] == '开库'
               for t in r['open_tombs'])


def test_distant_xing_can_open_without_tougan():
    # 授课:418「远则可刑开墓库而得用」；无透干不妨碍远刑开库
    r = analyze_muku(['戌', '午', '巳', '丑'], ['庚', '庚', '庚', '甲'])
    assert any(t['zhi'] == '戌' for t in r['open_tombs'])


def test_chou_wei_chen_together_not_chong():
    # 理象学:3008-3009「丑未辰都出现时，丑则被墓，丑未不冲」
    zhis = ['丑', '未', '辰', '寅']
    r = analyze_muku(zhis, ['乙', '己', '壬', '辛'])
    assert not r['open_tombs']
    rels = {t['relation'] for t in r['tomb_relations']}
    assert {'丑(土)入辰墓', '未(土)入辰墓'} <= rels


def test_sanhe_tomb_priority_direct_examples():
    from mangpai.objective.muku import sanhe_tomb_priority
    # 两午见戌以入墓看；普通三字齐且无重复中神仍保留三合，不全局互斥
    assert sanhe_tomb_priority('寅午戌', ['戌', '午', '午', '寅'],
                               ['戊', '戊', '戊', '甲']) is True
    assert sanhe_tomb_priority('申子辰', ['申', '子', '辰', '卯'],
                               ['庚', '壬', '戊', '乙']) is False


def test_tomb_relations_shuli():
    # 书例卯未辰寅端到端：tomb_relations 应检出 未入辰墓
    r = analyze_muku(['卯', '未', '辰', '寅'], ['己', '辛', '戊', '甲'])
    rels = {t['relation'] for t in r['tomb_relations']}
    assert '未(土)入辰墓' in rels


def test_caiku_dongku_is_not_reported_as_open():
    from mangpai.subjective.caiming import _detect_caiku
    rows = _detect_caiku('甲', ['庚', '庚', '庚', '甲'],
                         ['辰', '午', '午', '戌'], None)
    xu = next(t for t in rows if t['zhi'] == '戌')
    assert xu['status'] == '动库'
    assert xu['view'] != '开财库'


def test_r4_natal_self_xing_does_not_open_tomb():
    """理象学:2883 自刑不应验，原局辰辰不把水库伪报为刑开。"""
    r = analyze_muku(['辰', '午', '辰', '申'], ['戊', '丙', '甲', '壬'])
    chen = next(t for t in r['tombs'] if t['zhi'] == '辰' and t['pillar'] == '年柱')
    assert chen['status'] == '墓库'
    assert not any(t['zhi'] == '辰' for t in r['open_tombs'])
