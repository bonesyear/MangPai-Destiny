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
