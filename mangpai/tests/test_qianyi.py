# -*- coding: utf-8 -*-
"""缺口批1 哨兵：qianyi 迁移/远行 marker + 迁移应期窗。

书锚（设计 = 缺口方案归档 kimi-gaps-plan-2026-08-20 §一，行号已回书核对）：
- 合到门户：乾 丁未己酉戊子丙辰 辛巳年（zhongji:4179「丙辛合到门户上」）；
  坤 辛亥庚子庚寅己卯 甲运（lixiangxue:6571「甲运合己，合到门户」）。
- 马逢冲：乾 壬子壬寅庚辰辛巳 申运（shouke:3600-3602「姐妹宫受申冲……
  马冲在哪儿，离开哪儿」）。
- 马星伏吟：乾 甲寅丙寅癸卯丁巳 辛巳年（shouke:6692「辛巳年马星伏吟而
  出国」——书断语级别，引擎措辞上限「迁移/远行」）。
- 冲出年时（或然）：shouke:72「流年冲年支、冲时支谓冲出……未必所有人
  都会出门」。
- 马临年时（原局）：乾 丁未辛亥乙巳丁丑（gaoji:6735 案例九「马星在年
  时，主远行」）。
- 月日冲=背井离乡 / 日时合=安居（gaoji:5857-5858）；马逢合=停留
  （zhongji:1567 + gaoji:6757 口诀「马星逢合动则止」）。
- 反例 guard：日时合安居造 + 平和岁运 → 零迁移窗。

红线：输出任何 desc/note/summary 不得含「出国/移民」硬断语（书无级别判据，
zhongji:4179 与 gaoji:17390 结构同构而结论一为出国一为调动外省）。
岁运序列手动喂入（zinv 哨兵惯例），不改引擎岁运逻辑。
"""
import json

from mangpai.subjective.qianyi import analyze_qianyi


def _split8(bazi):
    gans = [bazi[i] for i in (0, 2, 4, 6)]
    zhis = [bazi[i] for i in (1, 3, 5, 7)]
    return gans, zhis


def _run(bazi, dys=(), lns=()):
    gans, zhis = _split8(bazi)
    return analyze_qianyi(
        gans[2], gans, zhis,
        dayun_list=[{'gz': d} for d in dys],
        liunian_list=[{'gz': l} for l in lns],
    )


def _moves(r):
    return r['qianyi_yingqi']['move_windows']


def _stays(r):
    return r['qianyi_yingqi']['stay_windows']


# ── 1. 应期·合到门户（双锚：zhongji:4179 + lixiangxue:6571）──

def test_hedaomenhu_liunian_zhongji4179():
    """乾 丁未己酉戊子丙辰：辛巳年丙辛合，合端落时干（门户）→ 迁移窗。"""
    r = _run('丁未己酉戊子丙辰', lns=['辛巳'])
    hits = [w for w in _moves(r)
            if w['liunian'] == '辛巳' and w['mechanism'] == '合到门户']
    assert hits and hits[0]['pillar'] == 'hour'


def test_hedaomenhu_dayun_lixiangxue6571():
    """坤 辛亥庚子庚寅己卯：甲运合己（时干）→ 合到门户迁移窗。"""
    r = _run('辛亥庚子庚寅己卯', dys=['甲寅'])
    assert any(w['dayun'] == '甲寅' and w['mechanism'] == '合到门户'
               for w in _moves(r))


# ── 2. 应期·马逢冲（shouke:3600-3602 总纲「马冲在哪儿，离开哪儿」）──

def test_mafengchong_shouke3600():
    """乾 壬子壬寅庚辰辛巳 庚申运：申冲寅（月宫马星）→ 迁移窗落月宫。"""
    r = _run('壬子壬寅庚辰辛巳', dys=['庚申'])
    hits = [w for w in _moves(r)
            if w['dayun'] == '庚申' and w['mechanism'] == '马逢冲']
    assert hits and hits[0]['pillar'] == 'month'


# ── 3. 应期·马星伏吟（shouke:6692，或然标签）──

def test_maxing_fuyin_shouke6692():
    """乾 甲寅丙寅癸卯丁巳 辛巳年：巳伏吟且为马星 → 迁移窗（或然）。"""
    r = _run('甲寅丙寅癸卯丁巳', lns=['辛巳'])
    hits = [w for w in _moves(r)
            if w['liunian'] == '辛巳' and w['mechanism'] == '马星伏吟']
    assert hits and hits[0]['confidence'] == '或然'


# ── 4. 应期·冲出年时（shouke:72，书自承或然）──

def test_chongchu_nianshi_shouke72():
    """乾 甲寅丙寅癸卯丁巳 辛亥年：亥冲时支巳（门户）→ 冲出年时（或然）。"""
    r = _run('甲寅丙寅癸卯丁巳', lns=['辛亥'])
    hits = [w for w in _moves(r)
            if w['liunian'] == '辛亥' and w['mechanism'] == '冲出年时']
    assert hits and hits[0]['confidence'] == '或然'


# ── 5. 应期·马逢合=停留（zhongji:1567 + gaoji:6757 口诀）──

def test_mafenghe_stay():
    """乾 壬子壬寅庚辰辛巳 己丑运：丑合子（年宫马星）→ 停留窗，非迁移窗。"""
    r = _run('壬子壬寅庚辰辛巳', dys=['己丑'])
    hits = [w for w in _stays(r)
            if w['dayun'] == '己丑' and w['mechanism'] == '马逢合']
    assert hits and hits[0]['pillar'] == 'year'
    assert not any(w['dayun'] == '己丑' for w in _moves(r))


# ── 6. 原局 marker：马临年时（gaoji:6735 案例九「马星在年时，主远行」）──

def test_yuanju_ma_lin_nianshi_gaoji6735():
    """乾 丁未辛亥乙巳丁丑：未为日支巳之马落年柱 → 马临年时；癸未年伏吟应期。"""
    r = _run('丁未辛亥乙巳丁丑', lns=['癸未'])
    m = r['qianyi_yuanju']['ma_lin_nianshi']
    assert m['hit'] is True and 'year' in m['positions']
    assert any(w['liunian'] == '癸未' and w['mechanism'] == '马星伏吟'
               for w in _moves(r))


# ── 7. 原局 marker：月日冲=背井离乡（gaoji:5857）──

def test_yuanju_beijing_lixiang_gaoji5857():
    """乾 丙寅甲午戊子癸丑：午子冲（月日）→ 背井离乡 marker。"""
    r = _run('丙寅甲午戊子癸丑')
    assert r['qianyi_yuanju']['beijing_lixiang'] is True
    assert '背井离乡' in r['qianyi_yuanju']['desc']


# ── 8. 反例 guard：日时合=安居（gaoji:5858），平和岁运零迁移窗 ──

def test_guard_anju_no_move_windows():
    """乾 己亥丁卯辛巳丙申：巳申合（日时）→ 安居；戊辰运/丙子年零冲合马 → 零迁移窗。"""
    r = _run('己亥丁卯辛巳丙申', dys=['戊辰'], lns=['丙子'])
    assert r['qianyi_yuanju']['anju'] is True
    assert r['qianyi_yuanju']['beijing_lixiang'] is False
    assert _moves(r) == []
    assert _stays(r) == []


# ── 9. schema + 红线措辞（上限「迁移/远行」，不出「出国/移民」）──

def test_schema_and_wording_redline():
    r = _run('丁未己酉戊子丙辰', dys=['庚申'], lns=['辛巳'])
    assert set(r) >= {'qianyi_yuanju', 'qianyi_yingqi', 'summary'}
    blob = json.dumps(r, ensure_ascii=False)
    for term in ('出国', '移民', '海外'):
        assert term not in blob


# ── 10. engine 接线 + 特征 JSON 通道（镜像 zinv D6b 口径）──

def test_engine_wiring_and_payload_channel():
    """compute_all 产出 result['qianyi']；build_payload 经 selectors 进特征 JSON。"""
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    bazi_data = {
        'bazi': {'year': '丁未', 'month': '己酉', 'day': '戊子', 'hour': '丙辰'},
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': '男', 'year': 1967},
        'da_yun': {'start_age': 3, 'dayun': [
            {'gz': '庚戌', 'start_age': 3, 'end_age': 13},
            {'gz': '辛亥', 'start_age': 13, 'end_age': 23},
        ]},
        'liunian': [{'gz': '辛巳', 'year': 2001}],
    }
    res = MangpaiEngine(bazi_data).compute_all()
    assert 'qianyi' in res
    assert any(w['mechanism'] == '合到门户'
               for w in res['qianyi']['qianyi_yingqi']['move_windows'])
    payload = build_payload(res)
    assert 'qianyi' in payload
    assert payload['qianyi']['qianyi_yingqi']['move_windows']
