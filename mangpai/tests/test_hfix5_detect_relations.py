# -*- coding: utf-8 -*-
"""H-fix-5 detect_relations 拆分哨兵。

锁两件事：
1. 结构（先红后绿）：拆分出的子函数必须存在于 zuogong_detect 顶层
   （_scan_gan_relations/_scan_shengyong/_scan_shayin_huayong/_scan_zhi_pairs/
   _scan_sanhe_banhe/_scan_zhi_ke/_scan_gan_ke/_scan_shengfu/_scan_tomb/
   _calibrate_huayong/_apply_he_center_skip/_scan_fuyin_fanyin/_collect_raw_facts）。
2. 行为（改动前后皆绿）：各子函数的现有逻辑覆盖行为——全部用真实盘构造，
   判定值取自拆分前 detect_relations 的实测输出（等价性捕获口径），
   不断言任何新规则。
"""
from mangpai.objective.zuogong_detect import (
    _ZHI_PAIR_SPECS,
    _calibrate_huayong,
    _apply_he_center_skip,
    _collect_raw_facts,
    _scan_fuyin_fanyin,
    _scan_gan_ke,
    _scan_gan_relations,
    _scan_sanhe_banhe,
    _scan_shengfu,
    _scan_shengyong,
    _scan_shayin_huayong,
    _scan_tomb,
    _scan_zhi_ke,
    _scan_zhi_pairs,
    detect_relations,
)

# ─────────── 盘定义（拆分前实测探针盘，见任务书）───────────
# 日干合+合化：甲己合（合财）、月令丑土合化土、无克破
PAN_HE_HUA = ('甲', '木', ['庚', '己', '甲', '壬'], ['午', '丑', '子', '申'], '丑')
# 争合：月时两己争合一甲
PAN_ZHENG_HE = ('甲', '木', ['辛', '己', '甲', '己'], ['未', '巳', '卯', '酉'], '巳')
# 非日干合（宾宾合制）：癸戊合，丁日，官杀水×食伤土
PAN_NONDAY_HE = ('丁', '火', ['癸', '戊', '丁', '庚'], ['未', '申', '卯', '戌'], '申')
# 天干食伤生财：甲日 月干丙食神 + 月支午藏丁伤官
PAN_SS_GAN = ('甲', '木', ['戊', '丙', '甲', '庚'], ['辰', '午', '子', '未'], '午')
# 年干食伤远泄（aux）：甲日 年干丙食神
PAN_SS_YEAR = ('甲', '木', ['丙', '戊', '甲', '壬'], ['午', '辰', '子', '申'], '辰')
# 内食神格：壬癸壬壬/寅卯子寅（郝金阳企业家例，段氏内食神）
PAN_NEISHISHEN = ('壬', '水', ['壬', '癸', '壬', '壬'], ['寅', '卯', '子', '寅'], '卯')
# 食伤无财杀目标：乙日 全木火
PAN_SS_NONE = ('乙', '木', ['甲', '甲', '乙', '甲'], ['卯', '午', '卯', '卯'], '午')
# 杀印相生（化用保留）：丙日 壬年杀 甲月印
PAN_SHAYIN = ('丙', '火', ['壬', '甲', '丙', '戊'], ['子', '寅', '午', '申'], '寅')
# 六合：子丑（非日支参与，desc 无「日支参与」后缀）
PAN_LIUHE = ('甲', '木', ['甲', '丙', '甲', '庚'], ['子', '丑', '辰', '巳'], '丑')
# 暗合无日支参与 → 不检出（寅丑在年月）
PAN_ANHE_NODAY = ('甲', '木', ['庚', '丙', '甲', '壬'], ['寅', '丑', '辰', '午'], '丑')
# 暗合日支参与 → 检出（寅年丑日）
PAN_ANHE_DAY = ('甲', '木', ['庚', '丙', '甲', '壬'], ['寅', '辰', '丑', '午'], '辰')
# 自刑：辰辰（年日）
PAN_ZIXING = ('甲', '木', ['戊', '丙', '甲', '壬'], ['辰', '午', '辰', '申'], '午')
# 三合：申子辰
PAN_SANHE = ('甲', '木', ['庚', '丙', '甲', '壬'], ['申', '子', '辰', '午'], '子')
# 半合：申子
PAN_BANHE = ('甲', '木', ['庚', '丙', '甲', '壬'], ['申', '子', '寅', '午'], '子')
# 无三合半合
PAN_NO_SANHE = ('甲', '木', ['甲', '丙', '甲', '庚'], ['子', '丑', '寅', '卯'], '丑')
# 地支克：申金克卯木
PAN_ZHI_KE = ('甲', '木', ['甲', '丙', '甲', '庚'], ['申', '卯', '午', '辰'], '卯')
# 天干克：庚金克甲木（涉日干）+ 壬水克丙火（宾位 aux）
PAN_GAN_KE = ('甲', '木', ['庚', '丙', '甲', '壬'], ['午', '丑', '子', '申'], '丑')
# 天干克：甲己合对不计克
PAN_GAN_KE_HE = ('丙', '火', ['甲', '己', '丙', '辛'], ['午', '丑', '子', '申'], '丑')
# 生扶（日支参与）：寅木生午火
PAN_SHENGFU = ('甲', '木', ['甲', '丙', '甲', '庚'], ['寅', '巳', '午', '申'], '巳')
# 生扶无日支参与 → 不检出（日支酉与其余支无相生：寅酉/巳酉/卯酉皆不生）
PAN_SHENGFU_NODAY = ('甲', '木', ['甲', '丙', '甲', '庚'], ['寅', '巳', '酉', '卯'], '巳')
# 墓用：亥（日）入辰墓、未（时）入辰墓（宾位 aux）
PAN_TOMB = ('壬', '水', ['辛', '癸', '壬', '壬'], ['卯', '辰', '亥', '未'], '辰')
# 伏吟（年日子子）+ 反吟（甲子日 vs 庚午时）
PAN_FUYIN_FANYIN = ('甲', '木', ['丙', '戊', '甲', '庚'], ['子', '寅', '子', '午'], '寅')
# 伏吟/反吟均无日柱参与 → 不检出（年月子子）
PAN_FUYIN_NODAY = ('甲', '木', ['丙', '戊', '甲', '庚'], ['子', '子', '寅', '午'], '子')
# 化用降级（戌酉穿涉日支，两端非印；月干庚非印）
PAN_HUA_DOWN = ('丙', '火', ['壬', '庚', '丙', '甲'], ['子', '戌', '酉', '卯'], '戌')
# 化用保留（子午冲涉日支，月干甲印成局豁免）
PAN_HUA_KEEP = ('丙', '火', ['壬', '甲', '丙', '戊'], ['子', '寅', '午', '申'], '寅')
# 化用降级（墓用主功路径）：午（日）入戌（时）墓
PAN_HUA_TOMB = ('丙', '火', ['壬', '甲', '丙', '戊'], ['子', '寅', '午', '戌'], '寅')
# 合中心（日支午三种合：午未六合+亥午暗合+午戌半合）→ 日支食伤降 auxiliary
PAN_HE_CENTER = ('甲', '木', ['戊', '庚', '甲', '壬'], ['未', '亥', '午', '戌'], '亥')
# 合不足三种 → 不降
PAN_HE_CENTER_2 = ('甲', '木', ['戊', '庚', '甲', '壬'], ['未', '子', '午', '戌'], '子')


def _descs(actions):
    return [a['desc'] for a in actions]


# ─────────── 1. _scan_gan_relations（日干合/争合/合化/非日干合）───────────

def test_scan_gan_relations_day_he_and_hua():
    dg, dwx, gans, zhis, mz = PAN_HE_HUA
    r = _scan_gan_relations(dg, dwx, gans, zhis, mz)
    assert r['day_he_type'] == '合财'
    assert r['zheng_he'] is False
    assert r['work_types'] == {'合用'}
    wa = r['work_actions']
    assert len(wa) == 2
    assert wa[0]['type'] == '天干合' and wa[0]['action'] == '合用'
    assert wa[0]['to'] == '月干(己)'
    assert wa[0]['desc'] == '甲己合，合财'
    assert wa[1]['type'] == '合化' and wa[1]['action'] == '化用'
    assert wa[1]['desc'] == '甲己合化土，月令丑为土气，无克破'


def test_scan_gan_relations_zheng_he_blocks_hua():
    dg, dwx, gans, zhis, mz = PAN_ZHENG_HE
    r = _scan_gan_relations(dg, dwx, gans, zhis, mz)
    assert r['zheng_he'] is True
    assert r['day_he_type'] == '合财'
    wa = r['work_actions']
    assert len(wa) == 2  # 争合不化：无争化动作
    assert wa[0]['to'] == '月干(己)'
    assert wa[1]['to'] == '时干(己)'
    assert all(a['desc'] == '甲己合，合财（争合）' for a in wa)


def test_scan_gan_relations_non_day_he_binbin():
    dg, dwx, gans, zhis, mz = PAN_NONDAY_HE
    r = _scan_gan_relations(dg, dwx, gans, zhis, mz)
    assert r['day_he_type'] is None and r['zheng_he'] is False
    wa = r['work_actions']
    assert len(wa) == 1
    a = wa[0]
    assert a['type'] == '天干合' and a['action'] == '合用'
    assert a['from'] == '年干(癸)' and a['to'] == '月干(戊)'
    assert a['auxiliary'] is True and a['bin_bin_hezhi'] is True
    assert a['desc'] == '癸戊合（非日干合，合制做功）（宾宾合制，不做主功）'
    assert r['work_types'] == {'合用'}


def test_scan_gan_relations_empty():
    r = _scan_gan_relations('甲', '木', ['', '', '', ''], ['', '', '', ''], '')
    assert r['work_actions'] == []
    assert r['work_types'] == set()
    assert r['day_he_type'] is None
    assert r['zheng_he'] is False


# ─────────── 2. _scan_shengyong（天干/地支食伤 + 内食神格）───────────

def test_scan_shengyong_gan_and_zhi():
    dg, dwx, gans, zhis, mz = PAN_SS_GAN
    r = _scan_shengyong(dg, dwx, gans, zhis)
    assert r['work_types'] == {'生用'}
    wa = r['work_actions']
    assert len(wa) == 2
    assert wa[0]['to'] == '月干(丙)'
    assert wa[0]['desc'] == '食神丙泄秀，生财(年干戊、年支辰、时支未)、制杀(时干庚)'
    assert wa[1]['to'] == '月支(午藏丁)'
    assert wa[1]['desc'] == '午藏伤官(丁)泄秀，生财(时支未)、制杀(时干庚)'
    assert r['sheng_yong_actions'] == wa  # 引用同一动作对象


def test_scan_shengyong_year_gan_aux():
    dg, dwx, gans, zhis, mz = PAN_SS_YEAR
    r = _scan_shengyong(dg, dwx, gans, zhis)
    wa = r['work_actions']
    assert len(wa) == 1
    a = wa[0]
    assert a['to'] == '年干(丙)'
    assert a['auxiliary'] is True and a['year_gan_shengyong'] is True
    assert a['desc'].endswith('（年干远泄，不做主功）')
    assert r['sheng_yong_actions'] == [a]


def test_scan_shengyong_neishishen():
    dg, dwx, gans, zhis, mz = PAN_NEISHISHEN
    r = _scan_shengyong(dg, dwx, gans, zhis)
    wa = r['work_actions']
    assert len(wa) == 1
    a = wa[0]
    assert a['subtype'] == '食伤生财'
    assert a['to'] == '时支(寅藏甲)'
    assert a['to_pos'] == 'hour_zhi'
    assert a['desc'] == '寅藏食神(甲)泄秀，内食神生坐支藏财（食神藏财·才华）'
    assert 'auxiliary' not in a


def test_scan_shengyong_no_target_no_action():
    dg, dwx, gans, zhis, mz = PAN_SS_NONE
    r = _scan_shengyong(dg, dwx, gans, zhis)
    assert r['work_actions'] == []
    assert r['sheng_yong_actions'] == []
    assert r['work_types'] == set()


def test_scan_shengyong_empty_day_wx():
    r = _scan_shengyong('甲', '', ['丙', '丙', '甲', '丙'], ['午'] * 4)
    assert r['work_actions'] == []


# ─────────── 3. _scan_shayin_huayong（杀印相生/化用）───────────

def test_scan_shayin_huayong():
    dg, dwx, gans, zhis, mz = PAN_SHAYIN
    r = _scan_shayin_huayong(dg, dwx, gans, zhis)
    assert r['work_types'] == {'化用'}
    wa = r['work_actions']
    assert len(wa) == 1
    a = wa[0]
    assert a['type'] == '杀印相生' and a['action'] == '化用'
    assert a['to'] == '年干(壬)'
    assert a['desc'] == '官杀(壬水)生印(木)生日主(丙火)，杀印相生化用做功'
    assert 'auxiliary' not in a


def test_scan_shayin_huayong_empty_day_wx():
    r = _scan_shayin_huayong('丙', '', ['壬', '甲', '丙', '戊'], ['子', '寅', '午', '申'])
    assert r['work_actions'] == []
    assert r['work_types'] == set()


# ─────────── 4. _scan_zhi_pairs（注册表六合/暗合/刑穿破）───────────

def test_scan_zhi_pairs_liuhe():
    _, _, _, zhis, _ = PAN_LIUHE
    wa, wt = _scan_zhi_pairs(zhis, _ZHI_PAIR_SPECS[:2])
    assert len(wa) == 1
    assert wa[0]['type'] == '地支合' and wa[0]['action'] == '合用'
    assert wa[0]['desc'] == '子丑合'  # 非日支参与，无后缀
    assert wt == {'合用'}


def test_scan_zhi_pairs_anhe_requires_day():
    _, _, _, zhis_no, _ = PAN_ANHE_NODAY
    wa, wt = _scan_zhi_pairs(zhis_no, _ZHI_PAIR_SPECS[:2])
    assert wa == [] and wt == set()
    _, _, _, zhis_day, _ = PAN_ANHE_DAY
    wa, wt = _scan_zhi_pairs(zhis_day, _ZHI_PAIR_SPECS[:2])
    assert len(wa) == 1
    assert wa[0]['type'] == '暗合'
    assert wa[0]['desc'] == '寅丑暗合（日支参与），主隐秘做功、暗中获取'
    assert wt == {'合用'}


def test_scan_zhi_pairs_zixing():
    _, _, _, zhis, _ = PAN_ZIXING
    wa, wt = _scan_zhi_pairs(zhis, _ZHI_PAIR_SPECS[3:])
    assert len(wa) == 1
    assert wa[0]['type'] == '刑' and wa[0]['severity'] == 'normal'
    assert wa[0]['desc'] == '辰辰刑（自刑）'
    assert wt == {'制用'}


def test_scan_zhi_pairs_empty():
    wa, wt = _scan_zhi_pairs(['', '', '', ''], _ZHI_PAIR_SPECS)
    assert wa == [] and wt == set()


# ─────────── 5. _scan_sanhe_banhe（三合/半合）───────────

def test_scan_sanhe_banhe_sanhe_formed():
    _, _, _, zhis, _ = PAN_SANHE
    wa, wt, formed = _scan_sanhe_banhe(zhis)
    assert formed is True
    assert wt == {'成势'}
    assert len(wa) == 1
    a = wa[0]
    assert a['type'] == '三合局' and a['action'] == '成势做功'
    assert a['participants'] == ['year_zhi', 'month_zhi', 'day_zhi']
    assert a['desc'] == '申子辰水局成势，参与字均为功神'


def test_scan_sanhe_banhe_banhe():
    _, _, _, zhis, _ = PAN_BANHE
    wa, wt, formed = _scan_sanhe_banhe(zhis)
    assert formed is False
    assert wt == {'合用'}
    # 寅午戌/申子辰两组各半合成对（SAN_HE 表序：寅午半合在前）
    assert [a['desc'] for a in wa] == ['寅午半合火局，气未全',
                                       '申子半合水局，气未全']
    assert wa[0]['type'] == '半合' and wa[0]['action'] == '半成势'
    assert wa[0]['from'] == '日支(寅)' and wa[0]['to'] == '时支(午)'
    assert wa[1]['from'] == '年支(申)' and wa[1]['to'] == '月支(子)'


def test_scan_sanhe_banhe_none():
    _, _, _, zhis, _ = PAN_NO_SANHE
    wa, wt, formed = _scan_sanhe_banhe(zhis)
    assert wa == [] and wt == set() and formed is False
    wa, wt, formed = _scan_sanhe_banhe(['', '', '', ''])
    assert wa == [] and wt == set() and formed is False


# ─────────── 6. _scan_zhi_ke / _scan_gan_ke（地支克/天干克）───────────

def test_scan_zhi_ke_direction():
    _, _, _, zhis, _ = PAN_ZHI_KE
    wa, wt = _scan_zhi_ke(zhis)
    assert wt == {'制用'}
    assert [(a['from'], a['to'], a['desc']) for a in wa] == [
        ('年支(申)', '月支(卯)', '申金克卯木'),
        ('日支(午)', '年支(申)', '午火克申金'),
        ('月支(卯)', '时支(辰)', '卯木克辰土'),
    ]
    assert wa[0]['severity'] == 'normal'
    # 反方向排布：克方在月，from/to 随之对调
    wa2, _ = _scan_zhi_ke(['卯', '申', '午', '辰'])
    assert wa2[0]['from'] == '月支(申)' and wa2[0]['to'] == '年支(卯)'


def test_scan_gan_ke_day_vs_non_day():
    _, _, gans, _, _ = PAN_GAN_KE
    wa, wt = _scan_gan_ke(gans)
    assert wt == {'制用'}
    assert [(a['from'], a['to'], a['desc'], a.get('auxiliary')) for a in wa] == [
        ('月干(丙)', '年干(庚)', '丙火克庚金（宾位干相克，不做主功）', True),
        ('年干(庚)', '日干(甲)', '庚金克甲木', None),
        ('时干(壬)', '月干(丙)', '壬水克丙火（宾位干相克，不做主功）', True),
    ]
    assert wa[1].get('non_day_ganke') is None


def test_scan_gan_ke_he_pair_skipped():
    _, _, gans, _, _ = PAN_GAN_KE_HE
    wa, _ = _scan_gan_ke(gans)
    # 甲己/丙辛两组合对均以合论不计克；唯辛金克甲木（宾位 aux）检出
    assert [(a['from'], a['to'], a['desc']) for a in wa] == [
        ('时干(辛)', '年干(甲)', '辛金克甲木（宾位干相克，不做主功）'),
    ]


# ─────────── 7. _scan_shengfu（生扶，auxiliary）───────────

def test_scan_shengfu_requires_day():
    _, _, _, zhis, _ = PAN_SHENGFU
    wa = _scan_shengfu(zhis)
    assert len(wa) == 1
    a = wa[0]
    assert a['type'] == '生' and a['action'] == '生扶'
    assert a['auxiliary'] is True
    assert a['desc'] == '寅木生午火（生扶，非做功）'
    # 无日支参与之生扶对（寅巳）不检出，且其余对亦无相生
    _, _, _, zhis_no, _ = PAN_SHENGFU_NODAY
    assert _scan_shengfu(zhis_no) == []
    assert _scan_shengfu(['', '', '', '']) == []


# ─────────── 8. _scan_tomb（墓用）───────────

def test_scan_tomb_day_vs_binbin():
    _, _, gans, zhis, _ = PAN_TOMB
    tw, wt = _scan_tomb(zhis, gans)
    assert wt == {'墓用'}
    assert len(tw) == 2
    assert tw[0]['from'] == '月支(辰)' and tw[0]['to'] == '日支(亥)'
    assert tw[0]['desc'] == '亥(水)入辰墓'
    assert 'auxiliary' not in tw[0]
    assert tw[1]['from'] == '月支(辰)' and tw[1]['to'] == '时支(未)'
    assert tw[1]['auxiliary'] is True and tw[1]['non_day_tomb'] is True
    assert tw[1]['desc'] == '未(土)入辰墓（宾位入墓，不做主功）'


# ─────────── 9. _scan_fuyin_fanyin（伏吟/反吟）───────────

def test_scan_fuyin_fanyin():
    _, _, gans, zhis, _ = PAN_FUYIN_FANYIN
    wa = _scan_fuyin_fanyin(gans, zhis)
    assert len(wa) == 2
    assert wa[0]['type'] == '伏吟' and wa[0]['auxiliary'] is True
    assert wa[0]['desc'] == '子子伏吟（日柱参与，原地伏滞）'
    assert wa[1]['type'] == '反吟' and wa[1]['severity'] == 'high'
    assert wa[1]['auxiliary'] is True
    assert wa[1]['desc'] == '甲子与庚午天克地冲（反吟，动荡反复）'


def test_scan_fuyin_fanyin_requires_day():
    _, _, gans, zhis, _ = PAN_FUYIN_NODAY
    assert _scan_fuyin_fanyin(gans, zhis) == []
    assert _scan_fuyin_fanyin(['', '', '', ''], ['', '', '', '']) == []


# ─────────── 10. _calibrate_huayong（化用前置校准）───────────

def _assemble_for_calibration(pan):
    """按 detect_relations 主序装配校准所需输入（真实扫描器输出）。"""
    dg, dwx, gans, zhis, mz = pan
    wa, wt = [], set()
    r = _scan_shayin_huayong(dg, dwx, gans, zhis)
    wa += r['work_actions']
    wt |= r['work_types']
    for specs in (_ZHI_PAIR_SPECS[:2], _ZHI_PAIR_SPECS[2:3], _ZHI_PAIR_SPECS[3:]):
        a, t = _scan_zhi_pairs(zhis, specs)
        wa += a
        wt |= t
    a, t = _scan_zhi_ke(zhis)
    wa += a
    wt |= t
    a, t = _scan_gan_ke(gans)
    wa += a
    wt |= t
    tw, tt = _scan_tomb(zhis, gans)
    wt |= tt
    return dg, gans, zhis, wa, tw, wt


def test_calibrate_huayong_keep_when_yueyin_chengju():
    dg, gans, zhis, wa, tw, wt = _assemble_for_calibration(PAN_HUA_KEEP)
    _calibrate_huayong(dg, gans, zhis, wa, tw, wt)
    shayin = [a for a in wa if a['type'] == '杀印相生']
    assert len(shayin) == 1
    assert 'auxiliary' not in shayin[0]
    assert '化用' in wt


def test_calibrate_huayong_downgrade_by_real_zhiyong():
    dg, gans, zhis, wa, tw, wt = _assemble_for_calibration(PAN_HUA_DOWN)
    _calibrate_huayong(dg, gans, zhis, wa, tw, wt)
    shayin = [a for a in wa if a['type'] == '杀印相生']
    assert len(shayin) == 1
    assert shayin[0].get('auxiliary') is True
    assert '化用' not in wt


def test_calibrate_huayong_downgrade_by_tomb_main():
    dg, gans, zhis, wa, tw, wt = _assemble_for_calibration(PAN_HUA_TOMB)
    _calibrate_huayong(dg, gans, zhis, wa, tw, wt)
    shayin = [a for a in wa if a['type'] == '杀印相生']
    assert len(shayin) == 1
    assert shayin[0].get('auxiliary') is True
    assert '化用' not in wt


# ─────────── 11. _apply_he_center_skip（日支合中心·食伤不作生用）───────────

def _assemble_he_center(pan):
    dg, dwx, gans, zhis, mz = pan
    wa, wt = [], set()
    r = _scan_shengyong(dg, dwx, gans, zhis)
    wa += r['work_actions']
    wt |= r['work_types']
    a, t = _scan_zhi_pairs(zhis, _ZHI_PAIR_SPECS[:2])
    wa += a
    wt |= t
    a, t, _ = _scan_sanhe_banhe(zhis)
    wa += a
    wt |= t
    return wa, wt


def test_he_center_skip_when_3_he():
    wa, wt = _assemble_he_center(PAN_HE_CENTER)
    _apply_he_center_skip(wa, wt)
    ss = [a for a in wa if a['type'] == '食伤' and a['to_pos'] == 'day_zhi']
    assert len(ss) == 1
    assert ss[0].get('auxiliary') is True
    assert ss[0].get('he_center_skip') is True
    assert '生用' not in wt


def test_he_center_no_skip_below_3_he():
    wa, wt = _assemble_he_center(PAN_HE_CENTER_2)
    _apply_he_center_skip(wa, wt)
    ss = [a for a in wa if a['type'] == '食伤' and a['to_pos'] == 'day_zhi']
    assert len(ss) == 1
    assert 'auxiliary' not in ss[0]
    assert 'he_center_skip' not in ss[0]
    assert '生用' in wt


# ─────────── 12. _collect_raw_facts（长生/弱支/空亡/入墓干）───────────

def test_collect_raw_facts_changsheng_and_weak():
    facts = _collect_raw_facts('甲', ['甲', '丙', '甲', '庚'], ['亥', '午', '申', '子'], None)
    assert facts['day_changsheng']['亥'] == '长生'
    assert facts['day_changsheng']['午'] == '死'
    assert facts['day_changsheng']['申'] == '绝'
    assert facts['day_weak_zhis'] == {'午', '申'}
    assert facts['kong_wang_zhis'] == set()
    assert facts['entombed_gan_pillars'] == set()


def test_collect_raw_facts_empty_day_gan():
    facts = _collect_raw_facts('', ['', '', '', ''], ['亥', '午', '未', '申'], None)
    assert facts['day_changsheng'] == {}
    assert facts['day_weak_zhis'] == set()


def test_collect_raw_facts_entombed_gan():
    # 丙（日干）坐戌（火墓）-> day 柱入墓
    facts = _collect_raw_facts('丙', ['甲', '乙', '丙', '丁'], ['辰', '卯', '戌', '丑'], None)
    assert facts['entombed_gan_pillars'] == {'day'}
    # 戊寄戌（《五行精纪》严格墓位）-> 戊日坐戌同样 day 柱入墓
    facts = _collect_raw_facts('戊', ['甲', '乙', '戊', '丙'], ['辰', '卯', '戌', '午'], None)
    assert facts['entombed_gan_pillars'] == {'day'}


def test_collect_raw_facts_kong_wang_forms():
    gans, zhis = ['甲', '丙', '甲', '庚'], ['亥', '午', '未', '申']
    assert _collect_raw_facts('甲', gans, zhis, None)['kong_wang_zhis'] == set()
    assert _collect_raw_facts('甲', gans, zhis, [])['kong_wang_zhis'] == set()
    assert _collect_raw_facts('甲', gans, zhis, ['子', '午'])['kong_wang_zhis'] == {'子', '午'}
    assert _collect_raw_facts('甲', gans, zhis, {'zhi': ['寅']})['kong_wang_zhis'] == {'寅'}
    assert _collect_raw_facts('甲', gans, zhis,
                              {'kong_wang_zhi': ['巳']})['kong_wang_zhis'] == {'巳'}
    # 脏数据过滤：非地支字符串被剔除
    assert _collect_raw_facts('甲', gans, zhis, ['子', 'X'])['kong_wang_zhis'] == {'子'}


# ─────────── 13. 主函数编排契约 ───────────

def test_detect_relations_return_key_order():
    r = detect_relations('甲', '卯', '庚', '丑', '丙', '午', '壬', '子')
    assert list(r.keys()) == [
        'work_actions', 'tomb_works', 'sheng_yong_actions', 'day_he_type',
        'san_he_formed', 'zheng_he', 'day_changsheng', 'day_weak_zhis',
        'kong_wang_zhis', 'entombed_gan_pillars',
    ]


def test_detect_relations_end_to_end_calibration_and_he_center():
    # 化用校准端到端（拆分前实测：杀印相生降 auxiliary）
    r = detect_relations('丙', '酉', '壬', '子', '庚', '戌', '甲', '卯')
    shayin = [a for a in r['work_actions'] if a['type'] == '杀印相生']
    assert len(shayin) == 1 and shayin[0].get('auxiliary') is True
    # 日支合中心端到端（拆分前实测：日支食伤降 auxiliary + he_center_skip）
    r2 = detect_relations('甲', '午', '戊', '未', '庚', '亥', '壬', '戌')
    ss = [a for a in r2['work_actions']
          if a['type'] == '食伤' and a['to_pos'] == 'day_zhi']
    assert len(ss) == 1 and ss[0].get('auxiliary') is True
    assert ss[0].get('he_center_skip') is True
