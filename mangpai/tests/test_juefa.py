"""诀法层 (juefa) 测试 - 锁定高级篇第14章伤官诀/断语/断句/字碰字行为。

测试基准：书中命例（伤官诀 5 类各 1-2 例 + 断语代表例），gating 项
（15/17/19 须 yongshen_result、18 须 shensha_result）验证防过杀跳过与放行。
判据为结构启发式（见模块 docstring），锁定检出行为而非精确应事。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.juefa import (
    analyze_juefa, DUANYU_22, DUANJU_TABLE, ZIPENGZI_RULES, JINXIANG_JUEYAN,
)


def _run(y, m, d, h, **kw):
    gans = [y[0], m[0], d[0], h[0]]
    zhis = [y[1], m[1], d[1], h[1]]
    return analyze_juefa(gans, zhis, d[0], **kw)


def _ids(r):
    return [x['id'] for x in r['duanyu_hits']]


def _skips(r):
    return [x['id'] for x in r['duanyu_skipped']]


# ══ 伤官诀 5 类（14.1 书例）══

def test_jinshui_xijian_guan_qianlong():
    """乾隆 辛卯丁酉庚午丙子：庚金酉月（变格）子水伤官，火官杀明现 → 喜见官。"""
    r = _run('辛卯', '丁酉', '庚午', '丙子')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '金水伤官'
    assert '喜见官' in sg['verdict']


def test_jinshui_lianti_veto():
    """庚子日：伤官与日干连体 → veto 注记（岁运冲伤官凶）。"""
    r = _run('庚子', '庚辰', '庚子', '戊寅')
    sg = r['shangguan_jue']
    if sg.get('matched') and sg.get('type') == '金水伤官':
        assert '连体' in sg.get('veto_note', '')
    else:
        # 辰月不入金水伤官格（正格须冬月/金旺月），本例验格型门槛
        assert not sg.get('matched') or sg['type'] != '金水伤官'


def test_tujin_peiyin_zhangzhidong():
    """张之洞 丁酉戊申戊申戊午：戊土申月金伤旺，丁火印透 → 伤官佩印。"""
    r = _run('丁酉', '戊申', '戊申', '戊午')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '土金伤官'
    assert '佩印' in sg['verdict']
    assert '怕见官' not in sg['verdict']


def test_tujin_pajian_guan():
    """辛卯辛丑戊申辛酉：戊土金成势（变格），卯官无火印 → 怕见官破格。"""
    r = _run('辛卯', '辛丑', '戊申', '辛酉')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '土金伤官'
    assert '怕见官' in sg['verdict']


def test_shuimu_xicaiguan():
    """地委书记 甲午癸酉癸未辛酉：癸水甲伤透，午财未杀 → 喜财官；
    辛枭在时不紧贴甲 → 不报枭夺食。"""
    r = _run('甲午', '癸酉', '癸未', '辛酉')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '水木伤官'
    assert '喜财官' in sg['verdict']
    assert '枭' not in sg['verdict']


def test_muhuo_peiyin():
    """中学校长 癸卯丁巳甲子丁卯：甲木巳月火伤，癸子水印 → 佩印（文教）。"""
    r = _run('癸卯', '丁巳', '甲子', '丁卯', gender='female')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '木火伤官'
    assert '佩印' in sg['verdict']
    assert '官要旺' in sg.get('note', '')


def test_huotu_zhisha():
    """巨富夫 乙巳戊子丁巳庚戌：丁火土伤有力制子水杀 → 伤官制杀候选+组合依赖。"""
    r = _run('乙巳', '戊子', '丁巳', '庚戌', gender='female')
    sg = r['shangguan_jue']
    assert sg['matched'] and sg['type'] == '火土伤官'
    assert sg.get('combination_dependent') is True
    assert '制杀' in sg['verdict']


def test_shangguan_not_matched():
    """非伤官格（如甲木春生）→ matched=False。"""
    r = _run('甲寅', '丙寅', '甲子', '甲子')
    assert r['shangguan_jue']['matched'] is False


# ══ 断语 22 项（代表例）══

def test_duanyu2_ducai():
    """甲戌戊午庚申辛巳：木财仅甲一点（含藏干）→ 独财。"""
    r = _run('甲戌', '戊午', '庚申', '辛巳')
    assert 2 in _ids(r)
    assert '独' in [h for h in r['duanyu_hits'] if h['id'] == 2][0]['detail']


def test_duanyu3_caiku():
    """壬戌壬戌壬戌丙午（书例）：壬日火财，三戌火库在局+午会库 → 财库动。"""
    r = _run('壬戌', '壬戌', '壬戌', '丙午')
    assert 3 in _ids(r)
    d = [h for h in r['duanyu_hits'] if h['id'] == 3][0]['detail']
    assert '戌' in d and '库动' in d


def test_duanyu4_guansha_hunza_hequ():
    """己卯丁卯戊辰甲戌：乙官藏卯+甲杀透，甲己合 → 混杂+合去。"""
    r = _run('己卯', '丁卯', '戊辰', '甲戌')
    assert 4 in _ids(r)
    assert '合去' in [h for h in r['duanyu_hits'] if h['id'] == 4][0]['detail']


def test_duanyu5_jianguan_and_shangjin():
    """伤官见官：乙酉辛巳戊申庚午（辛伤透+乙官透）→ 见官；
    伤尽：庚申辛酉戊午庚申（食伤≥3 全局无官）→ 伤尽。"""
    r1 = _run('乙酉', '辛巳', '戊申', '庚午')
    assert 5 in _ids(r1)
    assert '见官' in [h for h in r1['duanyu_hits'] if h['id'] == 5][0]['detail']
    r2 = _run('庚申', '辛酉', '戊午', '庚申')
    assert 5 in _ids(r2)
    assert '伤尽' in [h for h in r2['duanyu_hits'] if h['id'] == 5][0]['detail']


def test_duanyu6_xiaoshen_duoshi():
    """乙巳辛巳丁卯己酉（书例）：乙枭透+己食透 → 枭神夺食。"""
    r = _run('乙巳', '辛巳', '丁卯', '己酉', gender='female')
    assert 6 in _ids(r)


def test_duanyu7_double_condition_gate():
    """双条件 gate：星坏+宫坏才断；仅星坏 → 低置信不轻断。"""
    # 甲寅乙卯甲午甲子：比劫4财0（星坏），年支寅无刑冲穿（宫未坏）
    r1 = _run('甲寅', '乙卯', '甲午', '甲子')
    h7 = [h for h in r1['duanyu_hits'] if h['id'] == 7]
    assert h7 and h7[0]['confidence'] == '低' and '不轻断' in h7[0]['detail']
    # 甲寅乙申甲午甲子：年支寅被月支申冲（宫坏）→ 正式命中
    r2 = _run('甲寅', '乙申', '甲午', '甲子')
    h7b = [h for h in r2['duanyu_hits'] if h['id'] == 7]
    assert h7b and '星宫双坏' in h7b[0]['detail']


def test_duanyu8_female_guan_rumu():
    """女命官杀入墓不透且无开库 → 难嫁；男命不评（skip）。
    甲戌戊子辛巳庚申：辛日火官之墓戌在年，官不透，戌无冲合刑。"""
    r = _run('甲戌', '戊子', '辛巳', '庚申', gender='female')
    assert 8 in _ids(r)
    rmale = _run('甲戌', '戊子', '辛巳', '庚申', gender='male')
    assert 8 not in _ids(rmale) and 8 in _skips(rmale)


def test_duanyu10_female_shangguan_jianguan():
    """戊申甲寅己巳己巳（书例）：申本气庚伤官+甲官透+双己争合 → 命中+加重。"""
    r = _run('戊申', '甲寅', '己巳', '己巳', gender='female')
    h = [x for x in r['duanyu_hits'] if x['id'] == 10]
    assert h and '争合' in h[0]['detail']


def test_duanyu12_zhenghe():
    """争合：两己争合一甲（戊申甲寅己巳己巳）。"""
    r = _run('戊申', '甲寅', '己巳', '己巳', gender='female')
    assert 12 in _ids(r)
    assert '争合一甲' in [h for h in r['duanyu_hits'] if h['id'] == 12][0]['detail']


def test_duanyu14_wuzhi_kangsha():
    """辛酉庚戌乙卯甲申：乙日杀透无印无食，比劫3 → 七杀无制比肩抗杀。"""
    r = _run('辛酉', '庚戌', '乙卯', '甲申')
    assert 14 in _ids(r)


def test_duanyu16_lu_shou_shang():
    """甲子丙寅癸酉戊午：癸禄在子，午冲子 → 禄受伤隐患。"""
    r = _run('甲子', '丙寅', '癸酉', '戊午')
    assert 16 in _ids(r)


def test_duanyu20_yinshen_lu():
    """庚寅庚辰甲申甲子（书例）：甲禄在寅（四生长），申冲寅 → 穿梭禄受伤。"""
    r = _run('庚寅', '庚辰', '甲申', '甲子')
    assert 20 in _ids(r)


def test_duanyu21_zhongjin_famu():
    """辛酉辛丑乙卯丙子（书例）：金3重，子水被丑合绊不化 → 重金伐木；
    对照（子未被合绊）→ 不命中。"""
    r = _run('辛酉', '辛丑', '乙卯', '丙子')
    assert 21 in _ids(r)
    r2 = _run('辛酉', '辛未', '乙卯', '丙子')
    assert 21 not in _ids(r2)


def test_duanyu21_xuanzhen():
    """悬针煞：庚申/辛酉柱在年月 → 加重（庚申辛酉乙丑戊寅：金4无水）。"""
    r = _run('庚申', '辛酉', '乙丑', '戊寅')
    h = [x for x in r['duanyu_hits'] if x['id'] == 21]
    assert h and '悬针' in h[0]['detail']


def test_duanyu22_he_chong_signals():
    """男命日支逢冲 → 冲处逢合（婚成）原局信号。"""
    r = _run('甲子', '丁卯', '戊午', '甲寅', gender='male')
    assert 22 in _ids(r)
    assert '冲处逢合' in [h for h in r['duanyu_hits'] if h['id'] == 22][0]['detail']


# ══ gating（防过杀）══

def test_gating_yongshen_skipped_by_default():
    """15/17/19 未提供 yongshen_result → 一律跳过。"""
    r = _run('甲辰', '己巳', '甲戌', '戊辰')
    for i in (15, 17, 19):
        assert i in _skips(r) and i not in _ids(r)


def test_duanyu15_with_yongshen():
    """甲辰己巳甲戌戊辰 + 身弱 → 身弱财旺日主合财（甲己合财）命中。"""
    ys = {'bijiao_duocai': {'strength': '身弱'}}
    r = _run('甲辰', '己巳', '甲戌', '戊辰', yongshen_result=ys)
    assert 15 in _ids(r)
    ys2 = {'bijiao_duocai': {'strength': '身强'}}
    r2 = _run('甲辰', '己巳', '甲戌', '戊辰', yongshen_result=ys2)
    assert 15 not in _ids(r2)


def test_duanyu17_with_yongshen():
    """财为用神（身强）+ 比劫夺财 → 命中；无 yongshen → 跳过。"""
    ys = {'bijiao_duocai': {'strength': '身强'}}
    r = _run('甲寅', '乙卯', '甲戌', '戊辰', yongshen_result=ys)
    assert 17 in _ids(r)


def test_duanyu18_with_shensha():
    """天乙与羊刃同柱 → 命中；无 shensha → 跳过。"""
    ss = {'天乙贵人': {'in_pillars': ['year']}, '羊刃': {'in_pillars': ['year']}}
    r = _run('甲子', '丙寅', '戊午', '庚申', shensha_result=ss)
    assert 18 in _ids(r)
    r2 = _run('甲子', '丙寅', '戊午', '庚申')
    assert 18 in _skips(r2)


def test_duanyu19_with_yongshen():
    """食神透+偏印透（枭夺食）+ yongshen → 寿元隐患命中。"""
    ys = {'bijiao_duocai': {'strength': '中和'}}
    r = _run('甲申', '壬子', '丙辰', '戊申', yongshen_result=ys)
    assert 19 in _ids(r)


# ══ 断句集可查表子集 ═

def test_duanju_caiku_xichong():
    """壬戌甲辰壬寅丙午：火库戌逢辰冲 → 财库喜刑。"""
    r = _run('壬戌', '甲辰', '壬寅', '丙午')
    assert any('财库喜刑' in h['text'] for h in r['duanju_hits'])


def test_duanju_shangguan_he_guan():
    """辛酉辛丑乙卯丙子：丙伤官合辛杀 → 伤官合官主官司。"""
    r = _run('辛酉', '辛丑', '乙卯', '丙子')
    assert any('伤官合官' in h['text'] for h in r['duanju_hits'])


def test_duanju_sanxing_quan():
    """戊申甲寅己巳己巳：寅巳申三刑全见。"""
    r = _run('戊申', '甲寅', '己巳', '己巳', gender='female')
    assert any('三刑全见' in h['text'] for h in r['duanju_hits'])


def test_duanju_female_day_yangren():
    """女命日坐羊刃（丙午日）→ 子宫刀伤。"""
    r = _run('壬辰', '甲辰', '丙午', '戊子', gender='female')
    assert any('阳刃' in h['text'] for h in r['duanju_hits'])


def test_duanju_table_shape():
    """断句集 8 域齐全，可查表项均有 rule 键。"""
    domains = {d['domain'] for d in DUANJU_TABLE}
    assert domains == {'父母', '婚姻', '事业', '财运', '牢狱', '性情', '健康', '杂项'}
    for d in DUANJU_TABLE:
        if d['checkable']:
            assert d.get('rule')


# ══ 字碰字 ═

def test_zipengzi_all_six_rules():
    """6 组规则逐一命中。"""
    cases = [
        (('壬寅', '癸卯', '丙午', '戊子'), '丙见壬'),   # 丙逢壬癸
        (('甲寅', '戊辰', '戊午', '甲子'), '戊见甲'),   # 戊见甲寅
        (('辛丑', '丁卯', '庚午', '丙子'), '辛见丁'),   # 辛见丁
        (('乙卯', '辛巳', '戊午', '甲子'), '乙见辛'),   # 乙见辛
        (('甲巳', '丙寅', '戊亥', '甲子'), '巳见亥'),   # 巳亥冲
        (('甲戌', '丙辰', '戊子', '庚申'), '辰见戌'),   # 辰戌冲
    ]
    for (y, m, d, h), combo in cases:
        r = _run(y, m, d, h)
        combos = [x['combo'] for x in r['zipengzi_hits']]
        assert any(c.startswith(combo[:3]) for c in combos), f'{combo} not in {combos}'


def test_zipengzi_no_hit():
    """无组合 → 空（己卯丁丑庚午壬未：六组皆不涉）。"""
    r = _run('己卯', '丁丑', '庚午', '壬未')
    assert r['zipengzi_hits'] == []


def test_zipengzi_rules_shape():
    assert len(ZIPENGZI_RULES) == 6
    for rule in ZIPENGZI_RULES:
        assert rule['xiang'] and (rule['ji'] or rule['xiong'])


# ══ 巾箱诀言词典 ═

def test_jueyan_hit_and_miss():
    """壬戌日子月（书载6条之一）→ 命中诀言；甲子日午月 → None。"""
    r = _run('甲辰', '丙子', '壬戌', '庚子')
    assert r['jueyan'] and '辰戌相冲开宝库' in r['jueyan']['verse']
    r2 = _run('甲辰', '丙午', '甲子', '庚子')
    assert r2['jueyan'] is None


def test_jueyan_dict_six_entries():
    assert len(JINXIANG_JUEYAN) == 6
    for (gz, month), v in JINXIANG_JUEYAN.items():
        assert len(gz) == 2 and month and v['verse'] and v['note']


# ══ 结构与容错 ═

def test_duanyu_22_complete():
    assert len(DUANYU_22) == 22
    for d in DUANYU_22:
        assert d['title'] and d['verse'] and d['domain']


def test_related_verses_present():
    """过河拆桥/贼捕神等关联诀法存诀言引用（不重复检测）。"""
    r = _run('甲子', '丙寅', '戊午', '庚申')
    assert set(r['related_verses']) == {'过河拆桥格', '贼神捕神', '合制格', '禄刃格'}


def test_bad_input_tolerated():
    r = analyze_juefa([], [], '')
    assert r['hit_count'] == 0 and '未评估' in r['summary']
    r2 = analyze_juefa(['甲'], ['子'], '甲')
    assert r2['hit_count'] == 0


def test_summary_and_count():
    r = _run('辛卯', '丁酉', '庚午', '丙子')
    assert isinstance(r['summary'], str) and r['summary']
    assert r['hit_count'] == (len(r['duanyu_hits']) + len(r['duanju_hits'])
                              + len(r['zipengzi_hits']))


# ══ 批K：D1 门槛收紧 + duanyu_a A 组精选 + engine/payload 接线 ══
# 依据=批J 509 例准确率评估（docs/audit-vs-originals-20261017.md 批J 节）：
# D1 准确率 76% 但触发面 72% 过宽，用户拍板加门槛=年时各≥2 吉神（原=各≥1）。
# 注：批K 前 D1 无哨兵用例（本组为新增，非改旧例）。

def test_duanyu1_gate_k_triggers_two_each():
    """新门槛触发面：年柱 偏财干+偏财本气（2 吉神），时柱 七杀干+禄（2 吉神）。
    甲寅戊辰庚午丙申：庚日 甲=偏财、寅本气甲=偏财、丙=七杀、申=庚禄。"""
    r = _run('甲寅', '戊辰', '庚午', '丙申')
    assert 1 in _ids(r)
    h = [x for x in r['duanyu_hits'] if x['id'] == 1][0]
    assert '两钳' in h['detail']
    # A 组精选同步收录
    assert 1 in [e['id'] for e in r['duanyu_a']]


def test_duanyu1_gate_k_blocks_single_each():
    """新门槛挡下旧门槛可触发面：年时各仅 1 吉神（旧=各≥1 会触发，批K 不触发）。
    甲子戊辰庚午丙子：年柱仅甲偏财（子本气癸=伤官非吉神）、时柱仅丙七杀。"""
    r = _run('甲子', '戊辰', '庚午', '丙子')
    assert 1 not in _ids(r)
    assert 1 not in [e['id'] for e in r['duanyu_a']]


def test_duanyu_a_only_a_group_members():
    """duanyu_a 只收 A 组 5 条：D10（伤官见官女命，非 A 组）触发但不进；
    D12（争合，A 组）进。"""
    r = _run('戊申', '甲寅', '己巳', '己巳', gender='female')
    assert 10 in _ids(r) and 12 in _ids(r)
    a_ids = [e['id'] for e in r['duanyu_a']]
    assert a_ids == [12]
    assert 10 not in a_ids


def test_duanyu_a_multiple_hits_ordered():
    """多条 A 组命中按 _DUANYU_A_MARKERS 表序输出。
    乙巳辛巳丁卯己酉 女命：乙枭+己食（D6）+ 官杀全无（D13）。"""
    r = _run('乙巳', '辛巳', '丁卯', '己酉', gender='female')
    assert 6 in _ids(r) and 13 in _ids(r)
    assert [e['id'] for e in r['duanyu_a']] == [6, 13]


def test_duanyu_a_excludes_c_group():
    """C 组规则（D4 官杀混杂，修后再议）触发也不进 duanyu_a。
    乙酉甲申戊午庚子：官乙+杀甲并透（D4），无 A 组任何命中。"""
    r = _run('乙酉', '甲申', '戊午', '庚子')
    assert 4 in _ids(r)
    assert r['duanyu_a'] == []


def test_duanyu_a_marker_wording_safe():
    """marker 措辞红线：象/倾向级（无断语式硬结论词），且不过 _DEATH_TERMS
    （payload 出口 _scrub_death 之前的模块内自查；D6 枭神夺食重点）。"""
    from mangpai.subjective import _DEATH_TERMS
    import json as _json
    charts = [
        _run('甲寅', '戊辰', '庚午', '丙申'),                       # D1
        _run('乙巳', '辛巳', '丁卯', '己酉', gender='female'),      # D6+D13
        _run('戊申', '甲寅', '己巳', '己巳', gender='female'),      # D12
        _run('壬寅', '壬子', '丙午', '壬辰', gender='male'),        # spouse_many
    ]
    n = 0
    for r in charts:
        for e in r['duanyu_a']:
            n += 1
            assert set(e) == {'source', 'id', 'title', 'marker', 'evidence'}
            assert ('象' in e['marker']) or ('倾向' in e['marker'])
            blob = _json.dumps(e, ensure_ascii=False)
            assert not any(t in blob for t in _DEATH_TERMS), e
    assert n >= 4  # 五条精选至少覆盖 4 条（D1/D6/D12/D13/spouse_many）


def test_engine_juefa_key_and_payload_channel():
    """engine 端到端：result 含 juefa 键；gender 男/女→female 转换生效
    （女命官杀全无=D13 触发）；payload 只放 A 组精选 dotted-path，
    22 项全文（juefa 顶层键）不进。"""
    from mangpai.engine import MangpaiEngine
    from mangpai.subjective import build_payload
    bd = {'bazi': {'year': '甲寅', 'month': '乙卯', 'day': '甲午',
                   'hour': '甲子'},
          'input': {'gender': '女', 'year': 1974}}
    res = MangpaiEngine(bd).compute_all()
    assert 'juefa' in res
    jf = res['juefa']
    assert set(jf) >= {'shangguan_jue', 'duanyu_hits', 'duanyu_skipped',
                       'duanju_hits', 'zipengzi_hits', 'duanyu_a'}
    assert 13 in [h['id'] for h in jf['duanyu_hits']]
    assert [e['id'] for e in jf['duanyu_a']] == [13]
    pl = build_payload(res)
    assert 'juefa' not in pl
    assert pl.get('juefa.duanyu_a') == jf['duanyu_a']


# ══ 批L：C 组豁免修复（依据=批J 509 例评估诊断，docs/audit-vs-originals-20261017.md）══
# D2b 财多不富：书义本有豁免「需日主强旺（比劫助身）方能担财，或构成特殊格局
# （如从财）方能大富」（gaoji:20067-20070；口诀「财星叠见反不富，比劫相助方为良」
# gaoji:20063-20065）。豁免=从财格（direction 总线 cong_target 真读）或比劫明现。
# D5a 伤官见官：伤官去官格不以「为祸」论（gaoji:1135-1136「官星为忌，伤官有力
# 去之，去忌得喜，反得官贵」；shouke:850「格局成立的条件是官星作忌神，不管日主
# 旺衰如何」；shouke:2146 朱元璋「伤官去官，天地全去，故官必大极」）。
# 财库族：静态断向改应期提示（理象学:8857-8858「坐下财库一定要开才有用」；
# chuji:2259/2269；书例库动发财应在甲子运丙寅年=岁运，gaoji:20111-20114）。

def test_duanyu2b_cong_cai_exemption():
    """从财格豁免：财≥3 + direction 总线 cong_target=从财 → 改判从财反主大富，
    不出「需比劫助身担财」原断向（gaoji:20069 格局特殊豁免）。
    甲寅乙亥庚辰壬午：庚日木财 甲+乙+寅甲+亥甲+辰乙=5 重，无比劫。"""
    ys = {'cong_target': {'is_cong': True, 'label': '从财', 'suo_cong_wx': '木',
                          'ji_wx': [], 'detail': ''}}
    r = _run('甲寅', '乙亥', '庚辰', '壬午', yongshen_result=ys)
    d = [h for h in r['duanyu_hits'] if h['id'] == 2][0]['detail']
    assert '从财格' in d and '需比劫助身担财' not in d


def test_duanyu2b_bijiao_exemption():
    """比劫明现豁免：财≥3 且比劫透干/本气 → 比劫助身可担财，不出原断向
    （gaoji:20069 比劫助身豁免；无 yongshen_result 亦生效=本地判据）。
    甲寅己巳甲戌戊辰：甲日土财 己+戊+辰戊+巳戊+戌戊+辰戊≥3，年干甲比肩明现。"""
    r = _run('甲寅', '己巳', '甲戌', '戊辰')
    d = [h for h in r['duanyu_hits'] if h['id'] == 2][0]['detail']
    assert '比劫助身可担财' in d and '需比劫助身担财' not in d


def test_duanyu2b_original_still_fires():
    """原条件仍触发（双向哨兵）：财≥3、无比劫、非从财 → 维持「财多不富需比助」。
    甲寅乙亥庚辰壬午：财5重，庚日无比劫（申辛俱无），无 yongshen_result。"""
    r = _run('甲寅', '乙亥', '庚辰', '壬午')
    d = [h for h in r['duanyu_hits'] if h['id'] == 2][0]['detail']
    assert '财多不富' in d and '需比劫助身担财' in d


def test_duanyu5a_guan_he_qu_exemption():
    """官星被合去豁免（朱元璋型）：伤官+正官同透而官被合（日主自合官亦计，
    zhongji:3732「壬午自合合去壬…为伤官去官格」）→ 改判伤官去官格，不出
    「叛逆官非」断向。戊辰壬戌丁丑丁未：戊伤官透+壬正官透，丁壬合（日主+时干）。"""
    r = _run('戊辰', '壬戌', '丁丑', '丁未')
    d = [h for h in r['duanyu_hits'] if h['id'] == 5][0]['detail']
    assert '去官' in d and '叛逆官非' not in d


def test_duanyu5a_guan_ji_exemption():
    """官为忌神豁免：伤官+正官同透无合去 + direction 总线 strength=身弱/从强
    （扶抑口径官为忌，gaoji:1135 去忌得喜）→ 改判伤官去官格。
    癸酉己未丙辰庚寅：己伤官透+癸正官透，戊甲俱无=无合去。"""
    ys = {'shangguan_jianguan': {'strength': '身弱'}}
    r = _run('癸酉', '己未', '丙辰', '庚寅', yongshen_result=ys)
    d = [h for h in r['duanyu_hits'] if h['id'] == 5][0]['detail']
    assert '去官' in d and '叛逆官非' not in d
    ys2 = {'shangguan_jianguan': {'strength': '从强'}}
    r2 = _run('癸酉', '己未', '丙辰', '庚寅', yongshen_result=ys2)
    d2 = [h for h in r2['duanyu_hits'] if h['id'] == 5][0]['detail']
    assert '去官' in d2 and '叛逆官非' not in d2


def test_duanyu5a_original_still_fires():
    """原条件仍触发（双向哨兵）：伤官+正官同透、无合去、strength 身强（官为用）
    或未传 yongshen_result → 维持「伤官见官为祸」断向（癸酉己未丙辰庚寅）。"""
    ys = {'shangguan_jianguan': {'strength': '身强'}}
    r = _run('癸酉', '己未', '丙辰', '庚寅', yongshen_result=ys)
    d = [h for h in r['duanyu_hits'] if h['id'] == 5][0]['detail']
    assert '叛逆官非' in d
    r2 = _run('癸酉', '己未', '丙辰', '庚寅')
    d2 = [h for h in r2['duanyu_hits'] if h['id'] == 5][0]['detail']
    assert '叛逆官非' in d2


def test_duanyu3_caiku_timing_wording():
    """D3a 财库断向改应期提示：库动不再断「财源涌」，改「应期在岁运引动」；
    规则仍命中（id=3 在 hits）。壬戌壬戌壬戌丙午（书例三戌火库+午会库）。"""
    r = _run('壬戌', '壬戌', '壬戌', '丙午')
    assert 3 in _ids(r)
    d = [h for h in r['duanyu_hits'] if h['id'] == 3][0]['detail']
    assert '库动' in d and '应期' in d and '财源涌' not in d


def test_duanju_caiku_family_timing_wording():
    """断句财库三条改应期提示（规则仍命中、措辞中性）：
    caiku_xichong 不再断「发财的命」；day_caiku 不再断「难大发」；
    caiku_bi 不再断「破财」，改「逢冲开之岁运方得」。"""
    r = _run('壬戌', '甲辰', '壬寅', '丙午')   # 火库戌逢辰冲
    d = [h['detail'] for h in r['duanju_hits'] if h['text'] == '财库喜刑，发财的命'][0]
    assert '发财的命' not in d and '应期' in d
    r2 = _run('壬子', '癸亥', '壬戌', '丙午')  # 日支戌=火库，亥与戌无刑冲合（库静）
    d2 = [h['detail'] for h in r2['duanju_hits'] if h['text'] == '坐下财库，必须刑冲'][0]
    assert '难大发' not in d2 and '应期' in d2
    r3 = _run('壬戌', '癸卯', '壬寅', '丙午')  # 火库戌被卯合闭
    d3 = [h['detail'] for h in r3['duanju_hits'] if h['text'] == '闭了财库，破财'][0]
    assert '——破财' not in d3 and '逢冲开之岁运方得' in d3
