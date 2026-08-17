"""F18 批哨兵（先红后绿）· shipaige 断语层郑氏碎片对齐 + gongmen_wuzhi 正式弃用 + 阳制阴口径

批8 审计 P0：
- shipaige P0-1「官杀为子」冠名错误（碎片:81「身旺财为子，身弱印作儿」无官杀为子之说）
- shipaige P0-2「劫财抗杀入牢狱」冠名冲突（碎片:90「劫财七杀两相连，要到边疆去从军」）
- shipaige P0-3「食神生旺子女聪慧」与自身数量诀「二食贪吃/三食愚钝」自相矛盾
- gongmen_wuzhi P0-5 阳制阴口径与 gaoji:11787-11788 相反
  （书：阳气=丙丁巳午戊戌 制 阴气=辛酉癸子丑，含天干、子归阴）

F18 决策落地：gongmen_wuzhi 正式弃用（F15 已在 zhiye 按书重写 8.2 六组组合，
不接本模块），narrative LLM 通道切断（is_wuzhi 近恒真零信息量行不再进结论）。
"""
from mangpai.subjective.shipaige import analyze_shipaige
from mangpai.subjective.gongmen_wuzhi import classify_gongjianfa
from mangpai.subjective.narrative import summarize_engine_result
import mangpai.subjective.gongmen_wuzhi as gw_mod


def _keys(res, domain=None):
    if domain:
        return res['domains'].get(domain, [])
    return [k for v in res['domains'].values() for k in v]


# ── shipaige：三 P0 修复 ──

def test_p0_1_guansha_weizi_abolished():
    """旧码 count(正官)==1 即断「官杀为子」；碎片无此说，须废。"""
    # 甲子日，辛=正官唯一明现（旧触发条件）
    r = analyze_shipaige('甲', '子', '辛', '未', '丙', '寅', '丁', '卯')
    assert '官杀为子' not in _keys(r)


def test_p0_1_shenwang_cai_weizi():
    """碎片:81 身旺财为子：身强（比劫印众）+ 财明现 → 子女域命中。"""
    # 甲日：比肩甲/劫财乙/印癸癸 vs 财戊己辰丑——self 4 > other 3
    r = analyze_shipaige('甲', '子', '戊', '辰', '甲', '子', '乙', '丑')
    assert '身旺财为子身弱印作儿' in _keys(r, '子女')


def test_p0_2_jiecai_qisha_congjun_not_laoyu():
    """碎片:90 劫财七杀两相连=从军（事业域），非牢狱「劫财抗杀」。"""
    # 甲日：年庚申七杀柱 与 月乙卯劫财柱 相邻（两相连）
    r = analyze_shipaige('甲', '戌', '庚', '申', '乙', '卯', '丙', '寅')
    assert '劫财七杀两相连' in _keys(r, '事业')
    assert '劫财抗杀' not in _keys(r)
    assert '劫财七杀两相连' not in _keys(r, '牢狱')


def test_p0_3_shishen_shengwang_abolished():
    """「食神生旺子女聪慧」与数量诀「二食贪吃/三食愚钝」矛盾，须废。"""
    # 甲日 丙丙透+午=食神≥2（旧触发条件）
    r = analyze_shipaige('甲', '寅', '丙', '午', '丙', '申', '庚', '子')
    assert '食神生旺' not in _keys(r)


# ── shipaige：碎片断语实现探针 ──

def test_fuyin_bujianzu():
    """碎片:64 年日伏吟不见祖。"""
    r = analyze_shipaige('甲', '子', '甲', '子', '丙', '寅', '戊', '申')
    assert '伏吟不见祖' in _keys(r, '父母')


def test_yin_zai_ym_bei_cai_huai():
    """碎片:62 印在年月被财坏，命与父无缘。"""
    r = analyze_shipaige('甲', '午', '戊', '申', '癸', '酉', '庚', '寅')
    assert '印在年月被财坏' in _keys(r, '父母')


def test_shuangnv_shuangyu():
    """碎片:84 双女双鱼占日支（巳/亥）。"""
    r = analyze_shipaige('丙', '巳', '甲', '寅', '庚', '申', '戊', '子')
    assert '双女双鱼占日支' in _keys(r, '子女')


def test_sanchen_jiazi():
    """碎片:85 辰月辰日与辰时，假子假女。"""
    r = analyze_shipaige('戊', '辰', '甲', '申', '壬', '辰', '庚', '辰')
    assert '三辰假子女' in _keys(r, '子女')


def test_rizuo_muku_xi_xingchong():
    """碎片:72 日坐墓库喜刑冲。"""
    r = analyze_shipaige('己', '丑', '甲', '子', '丙', '寅', '辛', '未')
    assert '日坐墓库喜刑冲' in _keys(r, '婚姻')


def test_jiecai_chuan_peiou():
    """碎片:74 劫财穿配偶宫一定离婚。"""
    # 甲辰日，卯（乙木=劫财）穿辰
    r = analyze_shipaige('甲', '辰', '庚', '卯', '戊', '寅', '丙', '子')
    assert '劫财穿配偶宫必离' in _keys(r, '婚姻')


def test_wu_zuo_xu_jian_you():
    """碎片:94 戊坐戌见酉做老师。"""
    r = analyze_shipaige('戊', '戌', '甲', '寅', '丙', '辰', '辛', '酉')
    assert '戊坐戌见酉做老师' in _keys(r, '事业')


def test_wugui():
    """碎片:108 五鬼：戌巳/辰亥/寅未 任一对在局。"""
    r = analyze_shipaige('甲', '戌', '丙', '寅', '戊', '巳', '庚', '申')
    assert '五鬼凶神' in _keys(r, '牢狱')


def test_ding_jian_bingyin():
    """碎片:114 丁见丙寅命早没。"""
    r = analyze_shipaige('丁', '卯', '甲', '寅', '戊', '申', '庚', '子')
    assert '丁见丙寅命早没' in _keys(r, '寿元')


def test_muyu_shuizai():
    """碎片:115 沐浴为水灾（甲日沐浴在子，阴阳同生同死）。"""
    r = analyze_shipaige('甲', '寅', '戊', '子', '庚', '申', '丙', '辰')
    assert '沐浴水灾' in _keys(r, '寿元')


# ── gongmen_wuzhi：阳制阴口径（gaoji:11787-11788）+ 弃用隔离 ──

def test_yangzhiyin_gan_koujing():
    """书口径含天干：丁火克辛金=阳制阴（旧码纯地支漏检）。"""
    r = classify_gongjianfa('甲', ['丁', '辛', '甲', '甲'], ['申', '酉', '丑', '亥'])
    assert any('阳制阴' in e for e in r['evidence'])


def test_yangzhiyin_zi_gui_yin():
    """子归阴：子水克巳火=阴制阳，方向相反不计（旧码子算阳误触）。"""
    r = classify_gongjianfa('甲', ['甲', '甲', '甲', '甲'], ['子', '巳', '丑', '寅'])
    assert not any('阳制阴' in e for e in r['evidence'])


def test_gongmen_deprecated_marker():
    """F18 正式弃用标注（接入决策落地：不接 zhiye，F15 已在 zhiye 重写 8.2）。"""
    assert '正式弃用' in (gw_mod.__doc__ or '')


def test_gongmen_isolated_from_narrative():
    """隔离：is_wuzhi 近恒真零信息量行不再进 LLM 结论行。"""
    out = summarize_engine_result({
        'gongmen_wuzhi': {'is_wuzhi': True, 'primary': '军官',
                          'summary': '公门武职：军官'},
    })
    assert '公门武职' not in out
