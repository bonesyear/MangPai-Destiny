# -*- coding: utf-8 -*-
"""test_p1_guanming_zeibu — P1 官命检测簇批哨兵（A8 支杀化印 / A19 食合官支 / A11 贼捕制印）

书锚（逐字回书已核，预注册=docs/kimi-p1-guanming-prereg-20260918.md）：
- A8 支杀化印：chuji:1369-1371「子化了申生寅…这种结构就是当官的。化杀得权」
  （cj-正处级化杀）；zhongji:3911-3912 同造「现为正处，还升」；
  反锚 shouke:5768「可申杀空亡，不是真的兵刃相击，系国家足球队教练」（li112）。
- A19 食合官支：chuji:1751-1756「癸合了巳…官制了食，官在这里有功，所以是当官的」
  （cj-主席）；反锚 lixiangxue:6340「势实在太大…难以成大贵…只是个普通人」（普例1）。
- A11 贼捕制印：chuji:380-385「癸水成贼神…食伤制印的结构，印是权力。印被制了，
  制了就要得到」（cj-书记）；机制类锚 zhongji:3855-3857 朱镕基「制印得权」。

修法纪律：A8 新 type='支杀化印' 与 '杀印相生' 并列，不放宽明杀透干门；
仅入 work_actions 供官命域消费，不进 work_types（化用虚高 4 锚结构性免疫）。
"""
from mangpai.objective.zuogong_detect import detect_relations
from mangpai.subjective.guanming import classify_guanming_combo, analyze_guanming
from mangpai.subjective.zeishen_bushen import detect_zeibu_dangshi


def _split(gz4):
    return [g[0] for g in gz4], [g[1] for g in gz4]


# cj-正处级化杀：戊申 甲子 甲寅 丙寅（chuji:1362）
CHUJ = ('戊申', '甲子', '甲寅', '丙寅')
# shouke-li112 足球队教练：己卯 乙亥 甲子 壬申（shouke:5764，申杀旬空反锚）
LI112 = ('己卯', '乙亥', '甲子', '壬申')
# cj-书记：癸巳 丁巳 甲戌 己巳（chuji:380）
SHUJI = ('癸巳', '丁巳', '甲戌', '己巳')
# cj-主席：乙未 癸未 辛未 癸巳（chuji:1751）
ZHUXI = ('乙未', '癸未', '辛未', '癸巳')
# reg67-普例1普通人：丙戌 戊戌 辛巳 癸巳（lixiangxue:6340 反锚）
PU1 = ('丙戌', '戊戌', '辛巳', '癸巳')
# famous-李昌镐：乙卯 癸未 丙子 戊子（G6 制空锚）
LCG = ('乙卯', '癸未', '丙子', '戊子')
# zhenbao-01：戊戌 己未 乙巳 丁亥（calib 常驻锚，印有本气支非虚透）
ZB01 = ('戊戌', '己未', '乙巳', '丁亥')
# b67-岳飞：癸未 乙卯 甲子 己巳（捕未成太旺势反锚）
YUEFEI = ('癸未', '乙卯', '甲子', '己巳')


def _rel(gz4):
    gans, zhis = _split(gz4)
    return detect_relations(gans[2], zhis[2], gans[0], zhis[0], gans[1], zhis[1],
                            gans[3], zhis[3])


def _analyze(gz4):
    gans, zhis = _split(gz4)
    return analyze_guanming(gans[2], gans, zhis)


# ─────────── A8 支杀化印（新检测面，objective 新 type）───────────

def test_a8_zhisha_huayin_detected():
    """cj-正处级化杀：申杀（年支）合子印（月令）→ 新 type='支杀化印' 入 work_actions。"""
    wa = _rel(CHUJ)['work_actions']
    zs = [a for a in wa if a.get('type') == '支杀化印']
    assert zs, '支杀化印未检出（申杀合子印，chuji:1369）'
    assert not zs[0].get('auxiliary')


def test_a8_not_in_huayong_chain():
    """纪律：支杀化印仅入 work_actions 供官命域消费，不进 confirm 化用主功链
    ——confirm/gongliang/xiangfa 均以 type=='杀印相生' 精确匹配消费，新型
    结构性不可达（化用虚高 4 锚=制例三/合例六/墓例一/复例二 免疫）。"""
    from mangpai.subjective.zuogong_confirm import analyze_zuogong
    gans, zhis = _split(CHUJ)
    r = _rel(CHUJ)
    assert any(a.get('type') == '支杀化印' for a in r['work_actions'])
    zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                         gans[1], zhis[1], gans[3], zhis[3])
    assert zg['primary_work']['type'] != '化用', \
        f"支杀化印误入 confirm 化用主功链: {zg['primary_work']}"


def test_a8_guanming_consumed():
    """cj-正处级化杀：guanming 消费支杀化印 → 印化官杀 → is_guanming=True
    （「这种结构就是当官的。化杀得权」chuji:1371）。"""
    gans, zhis = _split(CHUJ)
    combo = classify_guanming_combo(gans[2], gans, zhis)
    assert '印化官杀' in combo['shengyong_huayong']
    assert _analyze(CHUJ)['is_guanming'] is True


def test_a8_kongwang_gate():
    """li112 足球队教练：申杀旬空（日/年并参）→ 不立支杀化印、不判官
    （「可申杀空亡，不是真的兵刃相击」shouke:5768）。"""
    wa = _rel(LI112)['work_actions']
    assert not [a for a in wa if a.get('type') == '支杀化印']
    assert _analyze(LI112)['is_guanming'] is False


# ─────────── A19 食合官支（G9 扩展）───────────

def test_a19_shihe_guanzhi():
    """cj-主席：时柱癸巳自合，癸食合巳官 → combo '合制·食合官支' → 官
    （「官制了食，官在这里有功，所以是当官的」chuji:1751）。"""
    gans, zhis = _split(ZHUXI)
    combo = classify_guanming_combo(gans[2], gans, zhis)
    assert '合制·食合官支' in combo['zhiyong_combos']
    assert _analyze(ZHUXI)['is_guanming'] is True


def test_a19_entomb_gate():
    """普例1 普通人：同构癸巳时柱但巳官入戌墓（入墓之物不做功）→ 不立
    （「所幸有巳入戌墓之功…难以成大贵…只是个普通人」lixiangxue:6340）。"""
    gans, zhis = _split(PU1)
    combo = classify_guanming_combo(gans[2], gans, zhis)
    assert '合制·食合官支' not in combo['zhiyong_combos']
    assert _analyze(PU1)['is_guanming'] is False


def test_a19_lichanggao_g6_holds():
    """李昌镐：戊子时柱虽命中食合官支检测，G6 官被制空亡仍判非官
    （「官星被制空亡，故他不入仕途」）。"""
    assert _analyze(LCG)['is_guanming'] is False


# ─────────── A11 贼捕制印（zeishen→guanming 新消费边）───────────

def test_a11_detect_zeibu_dangshi():
    """cj-书记：土党太旺（11.5）制虚透癸水印 → 党势级贼捕轴 贼=水（印）。
    （「火与燥土成势要制金水，癸水成贼神」chuji:380-385）"""
    gans, zhis = _split(SHUJI)
    axes = detect_zeibu_dangshi(gans[2], gans, zhis)
    assert any(ax['zeishen_wx'] == '水' for ax in axes), f'贼捕轴未检出: {axes}'


def test_a11_guanming_combo():
    """cj-书记：guanming 消费 → combo '贼捕制印'（印类，无官杀亦可立官）→ 官。"""
    gans, zhis = _split(SHUJI)
    combo = classify_guanming_combo(gans[2], gans, zhis)
    assert '贼捕制印' in combo['zhiyong_combos']
    assert _analyze(SHUJI)['is_guanming'] is True


def test_a11_zhenbao01_no_fire():
    """zhenbao-01：印有本气支（亥）非虚透 → 党势级贼捕不命中（calib 常驻锚保护）。"""
    gans, zhis = _split(ZB01)
    axes = detect_zeibu_dangshi(gans[2], gans, zhis)
    assert not axes, f'zhenbao-01 误中贼捕轴: {axes}'


def test_a11_yuefei_no_fire():
    """岳飞：印有本气支（子）非虚透 → 党势级贼捕不命中（净制锚不受影响）。"""
    gans, zhis = _split(YUEFEI)
    axes = detect_zeibu_dangshi(gans[2], gans, zhis)
    assert not axes, f'岳飞误中贼捕轴: {axes}'
