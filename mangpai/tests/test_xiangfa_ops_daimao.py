# -*- coding: utf-8 -*-
"""哨兵：xiangfa_ops 带象（带帽）财印互带的书口径（2026-10-17 修复批）。

书证：mangpai-zhongji.txt:2435-2436「印带财帽：表薪水，即上班领工资，印为
单位，财来自印中之意。财带印帽也是同样的意思」——两向同义，均表薪水/
工薪安稳（正象）。旧版 ('印','财') 误判「财来坏印、破印失信」（凶象），
且缺 ('财','印')「印带财帽」同义键。
"""
from mangpai.subjective.xiangfa_ops import daixiang


def _combos(day_gan, gans, zhis):
    return {f['combo']: f for f in daixiang(day_gan, gans, zhis)}


def test_cai_dai_yin_mao_zhengxiang():
    """壬戌柱（甲日主）：印帽壬坐财身戊 -> 财带印帽=表薪水（正象，非破印）。"""
    fs = _combos('甲', ['壬', '戊', '甲', '丙'], ['戌', '子', '寅', '卯'])
    assert '财带印帽' in fs
    f = fs['财带印帽']
    assert f['subject'] == '薪水'
    assert '领工资' in f['desc'] or '薪水' in f['desc']
    assert '破印' not in f['desc'] and '坏印' not in f['combo']


def test_yin_dai_cai_mao_tongyi():
    """戊子柱（甲日主）：财帽戊坐印身癸 -> 印带财帽（同义键，书「同样的意思」）。"""
    fs = _combos('甲', ['壬', '戊', '甲', '丙'], ['戌', '子', '寅', '卯'])
    assert '印带财帽' in fs
    f = fs['印带财帽']
    assert f['subject'] == '薪水'
    assert '薪水' in f['desc'] or '领工资' in f['desc']


# ── 批P2 哨兵：合象定义组合库 + 三合局归化象 ──
# 书证：mangpai-zhongji.txt:2204-2212「合象的第二种情形是：天干五合与地支六合，
# 相合的双方可以互用对方的象……如"劫财合财"，能表示此财的性质，是"劫取而得到
# 的财"；"食神合印"印是学问，食神是思想，可表示是一种思想性的学问，即为"学术"」；
# mangpai-gaoji-ocr.txt:8193-8225 口诀一「劫财合财定财性，食神合印学术专。伤官
# 合杀权柄握」+ 五组明文（增伤官合杀=权柄、官杀合身=日主追求官职）。
# 批4 审计「三合局归错原则」：zhongji:2276-2278 化象原则「如生、三合局、半合局
# 都是一种转化」——三合成势属化象「转化」非合象互用，归正移入 huaxiang。

from mangpai.subjective.xiangfa_ops import hexiang, huaxiang


def _he_defs(day_gan, gans, zhis):
    out = []
    for f in hexiang(day_gan, gans, zhis):
        out.extend(f.get('hexiang_defs') or [])
    return out


def test_hexiang_def_jiecai_hecai():
    """劫财合财=劫取而得之财（中级:2207-2213 书例 辛甲丁丙/丑午丑午 赌徒造，
    时干丙劫财合年干辛偏财——非日干合且非合制，做功层不载（zuogong_detect
    只检合制），定义库须直扫天干五合）。"""
    defs = _he_defs('丁', ['辛', '甲', '丁', '丙'], ['丑', '午', '丑', '午'])
    assert any(d.startswith('劫财合财') for d in defs)


def test_hexiang_def_shishen_heyin():
    """食神合印=学术（高级:8213-8218 书例 壬己乙丁/子酉丑丑 坤造，丁壬合
    食神×正印——「丁合到壬水印星…工作单位是文化机构」）。"""
    defs = _he_defs('乙', ['壬', '己', '乙', '丁'], ['子', '酉', '丑', '丑'])
    assert any(d.startswith('食神合印') for d in defs)


def test_hexiang_def_shangguan_heyin_liuhe():
    """地支六合互用同论（书「天干五合与地支六合」）：丁日卯戌合=伤官(戌)×
    偏印(卯) → 伤官合印=技艺。"""
    defs = _he_defs('丁', ['甲', '丙', '丁', '庚'], ['子', '丑', '卯', '戌'])
    assert any(d.startswith('伤官合印') for d in defs)


def test_hexiang_def_shangguan_hesha():
    """伤官合杀=权柄（高级口诀一「伤官合杀权柄握」）：丁日戊癸合=伤官×七杀
    （wa 合制动作既有检出，定义附于其上）。"""
    defs = _he_defs('丁', ['戊', '丙', '丁', '癸'], ['寅', '卯', '巳', '未'])
    assert any(d.startswith('伤官合杀') for d in defs)


def test_hexiang_def_guansha_heshen():
    """官杀合身=日主追求官职/管理/约束（高级:8224-8226）：己日甲己合=日主×正官。"""
    defs = _he_defs('己', ['甲', '丙', '己', '乙'], ['寅', '卯', '巳', '午'])
    assert any(d.startswith('官杀合身') for d in defs)


def test_hexiang_def_no_he_no_def():
    """无合之局不出定义象（甲乙丙丁/寅辰午申：天干五合、地支六合皆无）。"""
    assert _he_defs('丙', ['甲', '乙', '丙', '丁'], ['寅', '辰', '午', '申']) == []


def test_sanheju_gui_huaxiang():
    """三合局归错归正（中级:2276-2278「三合局…都是一种转化」=化象）：
    申子辰三合成势不再归合象，改归化象。"""
    gans, zhis = ['丙', '甲', '戊', '庚'], ['申', '子', '辰', '午']
    assert not any(f['subject'] == '三合成势' for f in hexiang('戊', gans, zhis))
    assert any(f['subject'] == '三合成势' and f['principle'] == '化象'
               for f in huaxiang('戊', gans, zhis))


def test_r4_gan_he_xiang_has_no_huaqi():
    """初级:2663 只有合象没有合化，甲己合也不再生成化气或合化化象。"""
    gans, zhis = ['庚', '己', '甲', '壬'], ['午', '丑', '子', '申']
    gan_he = [f for f in hexiang('甲', gans, zhis)
              if f['evidence'] and '甲己合' in f['evidence'][0]]
    assert gan_he
    assert all(f['domain'] == '' for f in gan_he)
    assert all(not any('合化气' in e for e in f['evidence']) for f in gan_he)
    assert not any(f['subject'].startswith('合化') for f in huaxiang('甲', gans, zhis))
