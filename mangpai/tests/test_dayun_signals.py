# -*- coding: utf-8 -*-
"""哨兵：subjective.dayun 气势变化不一律标吉（2026-10-17 修复批）。

书证：mangpai-zhongji.txt:314-316「最怕行反局大运，即行运正好与原局表达的
意思相反，或行运与原局势力对抗而无法被原局制之，主此大运凶」——气势变化
非必吉：新主导五行克原局主导五行（势力对抗）判反局入 negative_signals；
其余变化为中性，不进 positive_signals，desc 标「须辨正反」。输出键结构不变。
"""
from mangpai.subjective.dayun import judge_pillar_signals


def _mk_qishi(natal_wx, new_wx):
    return {'changed': True, 'natal_dominant': natal_wx, 'new_dominant': new_wx,
            'desc': f'大运加入后{new_wx}旺成势（原{natal_wx}为主）'}


def test_qishi_fanju_goes_negative():
    """原木为主、运后金旺成势（金克木=势力对抗）-> 反局入负面信号。"""
    r = judge_pillar_signals({'qishi_change': _mk_qishi('木', '金')})
    assert any('反局' in s for s in r['negative_signals'])
    assert not any('成势' in s for s in r['positive_signals'])
    assert '反局' in r['desc']


def test_qishi_neutral_not_positive():
    """原火为主、运后土旺成势（火生土，非对抗）-> 中性：不进正/负信号。"""
    r = judge_pillar_signals({'qishi_change': _mk_qishi('火', '土')})
    assert not any('成势' in s for s in r['positive_signals'])
    assert not any('成势' in s for s in r['negative_signals'])
    assert '须辨正反' in r['desc']
    assert set(r.keys()) >= {'positive_signals', 'negative_signals', 'overall', 'desc'}
