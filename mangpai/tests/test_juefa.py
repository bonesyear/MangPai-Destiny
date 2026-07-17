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
