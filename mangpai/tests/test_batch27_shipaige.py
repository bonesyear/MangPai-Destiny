# -*- coding: utf-8 -*-
"""批次27B：十排歌与统一墓库事实。"""
from mangpai.objective.constants import GAN_WX, WX_KE_ME, TOMB_MAP, LU
from mangpai.subjective.shipaige import analyze_shipaige


def _run(y, m, d, h):
    return analyze_shipaige(d[0], d[1], y[0], y[1], m[0], m[1], h[0], h[1])


def test_h129_marriage_entomb_uses_shared_rule():
    single_zheng = _run('癸丑', '甲寅', '乙酉', '戊寅')
    assert '婚姻宫入墓难成家' not in single_zheng['domains'].get('婚姻', [])

    multiple_zheng = _run('辛酉', '丁酉', '乙酉', '丁丑')
    assert '婚姻宫入墓难成家' in multiple_zheng['domains'].get('婚姻', [])

    opened_xu = _run('甲辰', '丙戌', '丙午', '壬午')
    assert '婚姻宫入墓难成家' not in opened_xu['domains'].get('婚姻', [])


def test_g21_lu_and_qisha_tomb_can_cooccur_for_all_day_stems():
    for day_gan in '甲乙丙丁戊己庚辛壬癸':
        lu = LU[day_gan]
        sha_wx = WX_KE_ME[GAN_WX[day_gan]]
        sha_tomb = next(z for z, wxs in TOMB_MAP.items() if sha_wx in wxs)
        result = analyze_shipaige(
            day_gan, lu, day_gan, '寅', day_gan, lu, day_gan, sha_tomb)
        assert '禄神入杀库' in result['domains'].get('事业', []), day_gan
