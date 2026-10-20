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
    analyze_zaihuo, classify_jibing, detect_chehuo, detect_siwang,
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


# ───────────────── 批D：_PO_DISEASE 收窄 + 羊刃逢冲必见血 ─────────────────

def test_po_disease_traditional_pairs_removed():
    """批D：子酉/丑辰/寅亥/巳申/未戌 5 对传统六破系书外移入（段氏全书零命中，
    理象学:2930 盲派破仅子卯/卯午两对）——子酉破不再报病。"""
    jb = classify_jibing('甲', ['甲', '癸', '甲', '庚'], ['子', '酉', '午', '申'])
    assert jb['po'] == []


def test_po_disease_maowu_kept():
    """卯午破保留（gaoji:15468-15471「卯午破：木不生火，主血管破裂、心脏出血、
    心梗脑溢」）；子卯破主病已由 _XING_DISEASE 子卯刑覆盖（gaoji:15521
    「子卯刑（亦作破）」）。"""
    jb = classify_jibing('甲', ['甲', '丁', '甲', '庚'], ['卯', '午', '子', '申'])
    assert jb['po'] == ['血管/心出血/脑溢']


def test_yangren_fengchong_marker():
    """批D：羊刃逢冲必见血（gaoji:16223/16548/16562 三处重申；detect_siwang
    docstring 早承诺未实现）——原局刃支逢冲录死亡风险 marker（中性措辞）。"""
    gans, zhis = ['甲', '辛', '甲', '庚'], ['卯', '酉', '子', '午']
    sw = detect_siwang('甲', gans, zhis)
    assert any('羊刃' in m and '逢冲' in m for m in sw['markers'])


def test_yangren_fenghe_marker():
    """刃逄冲合命难全（gaoji:16548）——原局刃支逢合（卯戌合）亦录。"""
    gans, zhis = ['甲', '丙', '甲', '戊'], ['卯', '戌', '寅', '子']
    sw = detect_siwang('甲', gans, zhis)
    assert any('羊刃' in m and '逢合' in m for m in sw['markers'])


def test_yangren_yunsui_marker():
    """运岁羊刃被冲（消费 yunfan 禄刃倒戈链）录 marker；原局无冲合者不双报。"""
    yf = {'dayun_fan': [{'gz': '辛酉', 'fans': [
        {'fan_type': '大运反局·类型一(禄刃倒戈)', 'severity': '重',
         'reason': '羊刃(卯)被冲——本护身之禄刃反戈攻身（阴阳逆转）'}]}],
        'liunian_fan': [], 'sui_yun_liandong': []}
    gans, zhis = ['甲', '丙', '甲', '戊'], ['卯', '寅', '子', '丑']
    sw = detect_siwang('甲', gans, zhis, yunfan_result=yf)
    assert any('羊刃' in m and '运岁' in m for m in sw['markers'])
    # 原局无刃冲/合 → 原局 marker 不出（仅运岁一条）
    assert not any('羊刃' in m and '运岁' not in m for m in sw['markers'])


# ───────────────── 批Q2：生之过四则/自刑心郁/宫位定病灶/驿马逢冲合/对称车象 ─────────────────

def test_q2_shengzhiguo_muduo_huosai():
    """批Q2：生之过（母多子病）病机四则（gaoji:15620-15623，书仅列此四则）——
    木多火塞：木≥3、火 1-2（工程化阈值，书无定量）→ 肝郁化火伤心神经。"""
    jb = classify_jibing('丁', ['甲', '乙', '丁', '庚'], ['卯', '辰', '戌', '酉'])
    assert any('木多火塞（母多子病' in s for s in jb['wx_bingji'])
    assert any('金多水浊（母多子病' in s for s in jb['wx_bingji'])


def test_q2_shengzhiguo_child_absent_no_trigger():
    """子行全无（火=0）不属「弱」→ 木多火塞不出（书「乙木多而丁火弱」须见弱丁）。"""
    jb = classify_jibing('癸', ['甲', '乙', '癸', '辛'], ['卯', '辰', '丑', '酉'])
    assert not any('木多火塞' in s for s in jb['wx_bingji'])
    assert any('金多水浊' in s for s in jb['wx_bingji'])  # 金4水2 仍在


def test_q2_zixing_xinyu():
    """批Q2：自刑主心郁（gaoji:15401「三刑聚处多疾厄，自刑多见心郁烦」）——
    XING_PAIRS 同支对（辰辰/午午/酉酉/亥亥），同支两见即成。"""
    jb = classify_jibing('甲', ['甲', '丙', '戊', '庚'], ['辰', '辰', '子', '丑'])
    assert any('自刑' in s and '心郁' in s for s in jb['xing'])
    # 单辰不成自刑
    jb2 = classify_jibing('甲', ['甲', '丙', '戊', '庚'], ['辰', '寅', '子', '丑'])
    assert not any('自刑' in s for s in jb2['xing'])


def test_q2_gongwei_dingbingzao():
    """批Q2：宫位定病灶（gaoji:15751「宫位年腿月胸腹，日腑时窍生殖专」）——
    子未穿落年/月柱 → 宫位 marker 随行（marker 级，不改 risk）。"""
    jb = classify_jibing('甲', ['甲', '丙', '庚', '壬'], ['子', '未', '申', '午'])
    assert '脾胃/腹疾' in jb['chuan_hai']
    assert '年柱（腿）' in jb['gongwei'] and '月柱（胸腹）' in jb['gongwei']
    assert '宫位：' in jb['desc']


def test_q2_yima_fengchong_jiaxian():
    """批Q2：驿马逢冲加险（gaoji:15777「马星逄冲车疾驰」+:15807「车祸概率
    大增」）——原局在局马星支逢冲录加险 marker。"""
    ch = detect_chehuo('庚', ['庚', '丙', '庚', '壬'], ['申', '子', '申', '午'])
    assert any('马星午逢冲（车疾驰，加险）' in m for m in ch['ma_feng'])
    assert any('马星子逢冲（车疾驰，加险）' in m for m in ch['ma_feng'])


def test_q2_yima_fenghe_jianxian():
    """批Q2：驿马逢合=合绊减险（gaoji:15778「马星合绊车停留」）——
    全合无冲盘：四条马星全逢合绊、零逢冲 marker。"""
    ch = detect_chehuo('庚', ['庚', '庚', '庚', '庚'], ['寅', '亥', '子', '丑'])
    assert ch['ma_feng']
    assert all('逢合绊（车停留，减险）' in m for m in ch['ma_feng'])
    assert not any('逢冲' in m for m in ch['ma_feng'])


def test_q2_duichen_chexiang():
    """批Q2：对称车象（gaoji:15792「对称出现：如双酉、双申、子午冲等，可象
    两个轮子或两辆车」）——车象支成双录佐证 marker（不计分）；子午冲类已由
    triggers 收录不重复。"""
    ch = detect_chehuo('庚', ['庚', '丙', '庚', '壬'], ['申', '子', '申', '午'])
    assert '双申' in ch['duichen']
    assert '对称车象' in ch['desc']
    # 无双支 → 不出
    ch2 = detect_chehuo('庚', ['庚', '庚', '庚', '庚'], ['寅', '亥', '子', '丑'])
    assert ch2['duichen'] == []
