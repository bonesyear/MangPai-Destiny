"""F14 哨兵：zaihuo（马星/墓绝空亡/牢狱衔接）+ LLM 寿元红线。

书锚：
- 马星：书死例一（gaoji:16165 丙午癸巳辛酉癸巳）全局无马——批7 P0-1
  「count=并集恒真死判据」，F13 已改消费 in_pillars，本哨兵锁定。
- 死亡「高」：gaoji:16323「墓绝空亡齐相见，神仙难救必归西」——
  墓/绝/空亡三类齐见方判高；单一类（书真死例一/九/十）只到中。
- 禄落空亡：gaoji:16434-16436 死例九「禄神空亡，根基虚浮」。
- 牢狱衔接：gaoji ch11 牢狱（11.1）为灾祸之首，laoyu.risk 入 max_risk。
- LLM 红线（批10）：zaihuo.siwang 死亡档/寿元星 markers 物理屏蔽出
  LLM 通道（payload + narrative），prompt 明禁死亡/寿数断言。
"""
import json

from mangpai.objective.bazi_calc import get_kong_wang
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective import MANGPAI_SCHOOL, assemble, build_payload, load_template
from mangpai.subjective.narrative import summarize_engine_result
from mangpai.subjective.zaihuo import (
    analyze_zaihuo, detect_chehuo, detect_siwang,
)


def _rel(gz: str):
    """按 engine 生产口径构造 relations（含空亡）。"""
    gans = [gz[i] for i in (0, 2, 4, 6)]
    zhis = [gz[i] for i in (1, 3, 5, 7)]
    kw = get_kong_wang(gz[4], gz[5])
    rel = detect_relations(gz[4], gz[5], gz[0], gz[1], gz[2], gz[3],
                           gz[6], gz[7], kw)
    return gans, zhis, rel


# ───────────────── 马星死判据（批7 P0-1，F13 修复锁定） ─────────────────

def test_ma_count_book_case1_no_ma_in_pillars():
    """书死例一（丙午癸巳辛酉癸巳）全局无马——ma_count 须为 0，
    不得报「马星N颗」（旧 count=并集口径恒≥3 的死判据）。"""
    gans, zhis, rel = _rel('丙午癸巳辛酉癸巳')
    ch = detect_chehuo('辛', gans, zhis, rel)
    assert ch['ma_count'] == 0
    assert '马星' not in ch['desc']


# ───────────────── 死亡「高」收窄：墓绝空亡齐见（gaoji:16323） ─────────────────

def test_siwang_high_requires_mu_jue_kong_all_three():
    """墓/绝/空亡三类齐见方判高（构造盘：丑墓被冲开+寅绝+空亡）。"""
    gans, zhis, rel = _rel('癸寅庚申己未丁丑')
    sw = detect_siwang('己', gans, zhis, rel)
    assert {'墓', '绝', '空亡'} <= {
        c for m in sw['mu_jue_kong']
        for c in ('墓', '绝', '空亡') if c in m
    }
    assert sw['risk'] == '高'


def test_siwang_jue_plus_kong_without_mu_not_high():
    """绝+空亡而墓不见 → 不得判高（批7 P0-2 假阳方向收窄）。"""
    gans, zhis, rel = _rel('甲申辛未壬子壬寅')
    sw = detect_siwang('壬', gans, zhis, rel)
    mjk = sw['mu_jue_kong']
    assert any('绝' in m for m in mjk) and any('空亡' in m for m in mjk)
    assert not any('墓' in m for m in mjk)
    assert sw['risk'] != '高'


def test_siwang_book_case1_jue_only_not_high():
    """书死例一（食神坐绝，gaoji:16165）——单一「绝」只到中。"""
    gans, zhis, rel = _rel('丙午癸巳辛酉癸巳')
    sw = detect_siwang('辛', gans, zhis, rel)
    assert any('绝' in m for m in sw['mu_jue_kong'])
    assert sw['risk'] == '中'


def test_siwang_book_case10_kong_only_not_high():
    """书死例十（食神空亡溺水，gaoji:16455-16457 乙巳戊子壬子壬寅）——单一空亡只到中。"""
    gans, zhis, rel = _rel('乙巳戊子壬子壬寅')
    sw = detect_siwang('壬', gans, zhis, rel)
    assert any('空亡' in m for m in sw['mu_jue_kong'])
    assert sw['risk'] == '中'


def test_siwang_book_case9_lu_kong_detected():
    """书死例九（禄神空亡早夭，gaoji:16434-16436 庚辰戊寅甲辰戊辰）——
    禄落空亡条款（批7 P1 补实现）须出 marker，单一空亡只到中。"""
    gans, zhis, rel = _rel('庚辰戊寅甲辰戊辰')
    sw = detect_siwang('甲', gans, zhis, rel)
    assert any('禄' in m and '空亡' in m for m in sw['mu_jue_kong'])
    assert sw['risk'] == '中'


# ───────────────── 牢狱接入 max_risk（gaoji ch11 牢狱为灾祸之首） ─────────────────

def test_laoyu_joins_max_risk():
    """laoyu risk 入灾祸总风险与 summary（批7 P1 漏接修复）。"""
    gans, zhis, rel = _rel('丙午癸巳辛酉癸巳')
    zh = analyze_zaihuo('辛', gans, zhis, relations=rel,
                        laoyu_result={'risk': '高', 'summary': '反局辰丑'})
    assert zh['max_risk'] == '高'
    assert '牢狱' in zh['summary']


def test_laoyu_absent_keeps_old_behavior():
    gans, zhis, rel = _rel('丙午癸巳辛酉癸巳')
    zh = analyze_zaihuo('辛', gans, zhis, relations=rel)
    assert '牢狱' not in zh['summary']


# ───────────────── LLM 红线：siwang 物理屏蔽 + prompt 禁令 ─────────────────

def _engine_result():
    from mangpai.engine import MangpaiEngine
    gz = '甲申辛未壬子壬寅'  # 带「寿元星遭破」级 markers 的盘
    bazi_data = {
        'bazi': {'year': gz[:2], 'month': gz[2:4], 'day': gz[4:6], 'hour': gz[6:]},
        'kong_wang': get_kong_wang(gz[4], gz[5]),
        'input': {'gender': '男'},
    }
    return MangpaiEngine(bazi_data).compute_all()


def test_payload_zaihuo_siwang_masked():
    """payload 侧 zaihuo 物理屏蔽 siwang（死亡档/寿元星 markers）。"""
    res = _engine_result()
    assert res['zaihuo'].get('siwang')  # 引擎内部结果保留
    payload = build_payload(res)
    zh = payload['zaihuo']
    assert 'siwang' not in zh
    blob = json.dumps(zh, ensure_ascii=False)
    assert '寿元' not in blob and '死亡' not in blob


def test_narrative_zaihuo_line_no_death():
    """narrative digest 行不带死亡/寿元文本。"""
    res = _engine_result()
    text = summarize_engine_result(res)
    assert '死亡' not in text and '寿元' not in text


def test_prompt_death_ban():
    """prompt（模板 + ENVELOPE 规则）明禁死亡/寿数断言。"""
    system, _user = assemble(' test ', {}, school=MANGPAI_SCHOOL)
    assert '死亡' in system and '寿' in system
    tpl = load_template(MANGPAI_SCHOOL)
    assert '死亡' in tpl and '寿' in tpl
