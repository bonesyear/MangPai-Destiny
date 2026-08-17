"""gongfei（功神/废神）模块测试 — F5 哨兵。

书锚：理象学:6008-6010「参与做功的字也分主要功神和辅助功神。如巳火制申金，
遇卯木，卯木生巳火为辅助功神」——辅助功神仍是功神（auxiliary=主功权重
标记，非「不参与做功」）；定义锚 理象学:5332-5334。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.objective.gongfei import classify_gongshen

PILLAR_KEYS = ['year', 'month', 'day', 'hour']
GANS = ['甲', '庚', '丙', '辛']
ZHIS = ['卯', '申', '巳', '亥']


def test_auxiliary_sheng_rengong():
    """卯木生巳火（auxiliary 生扶）= 辅助功神，仍入功神集（书 6008-6010）。"""
    wa = [
        {'type': '克', 'from_pos': 'day_zhi', 'to_pos': 'month_zhi'},   # 巳火制申金（主功）
        {'type': '生', 'from_pos': 'year_zhi', 'to_pos': 'day_zhi',
         'auxiliary': True},                                            # 卯木生巳火（辅助）
    ]
    r = classify_gongshen(wa, PILLAR_KEYS, GANS, ZHIS)
    assert 'year_zhi' in r['gong_shen']   # 辅助功神仍是功神
    assert 'day_zhi' in r['gong_shen']
    assert 'month_zhi' in r['gong_shen']
    assert 'year_zhi' not in r['fei_shen']


def test_idle_positions_are_fei():
    """未参与者=废神（闲置）：hour_gan/hour_zhi/year_gan 无动作。"""
    wa = [{'type': '克', 'from_pos': 'day_zhi', 'to_pos': 'month_zhi'}]
    r = classify_gongshen(wa, PILLAR_KEYS, GANS, ZHIS)
    assert set(r['fei_shen']) == {'year_gan', 'year_zhi', 'month_gan',
                                  'day_gan', 'hour_gan', 'hour_zhi'}
