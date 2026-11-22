# -*- coding: utf-8 -*-
"""批次18：正反局、从格、用神与虚实的边界反例。"""
from foundation.objective.ganqing import derive_states, match_ganqing
from mangpai.engine import MangpaiEngine
from mangpai.objective.virtual_solid import analyze_virtual_solid
from mangpai.subjective.laoyu import detect_fanju_chen_chou
from mangpai.subjective.yongshen import (
    assess_direction_signals, classify_strength, detect_caisheng_sha_gongshen,
)
from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _zf(gans, zhis):
    zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                         gans[1], zhis[1], gans[3], zhis[3])
    return analyze_zhengfan(zg['work_actions'], zg.get('day_he_type'), gans, zhis)


def test_h54_ren_cong_huotu_requires_all_conditions():
    for gans, zhis, expected in (
        (['乙', '壬', '癸', '戊'], ['未', '午', '未', '午'], False),
        (['庚', '壬', '辛', '戊'], ['午', '午', '未', '午'], False),
        (['甲', '丙', '壬', '丙'], ['午', '午', '午', '午'], True),
    ):
        states = derive_states(gans, zhis, exclude_gan='壬')
        rules = match_ganqing('壬', season='夏', stems=gans, branches=zhis,
                              tougian=gans, states=states)
        assert any(r.behavior == '从火土（相济）' for r in rules) is expected


def test_f12_peer_pillars_keep_virtual_and_work_signals():
    result = analyze_virtual_solid('甲', '子', '庚', '午', '戊', '寅', '甲', '戌')
    hour = next(r for r in result['virtual_solid'] if r['pillar'] == '时柱')
    assert hour['base_type'] == '虚透' and hour['vulnerable_to_ke']['level'] == '重'
    solid = analyze_virtual_solid('甲', '子', '甲', '子', '丙', '寅', '丙', '午')
    year = next(r for r in solid['virtual_solid'] if r['pillar'] == '年柱')
    assert year['is_solid'] and year['vulnerable_to_ke']['level'] == '无'
    work = analyze_zuogong('甲', '子', '庚', '午', '戊', '寅', '甲', '戌')
    action = next(a for a in work['work_actions']
                  if a.get('from_pos') == 'year_gan' and a.get('to_pos') == 'hour_gan'
                  and a.get('type') == '克')
    assert action.get('target_vulnerable') == '重'


def test_h151_cong_sha_is_not_caisheng_attack():
    gans, zhis = ['辛', '庚', '丙', '己'], ['亥', '子', '子', '丑']
    result = detect_caisheng_sha_gongshen('丙', gans, zhis)
    assert result['strength'] == '从弱' and not result['detected']
    direction = assess_direction_signals('丙', gans, zhis)
    assert not direction.get('mingju_xiong_severe')
    engine = MangpaiEngine({
        'bazi': dict(zip(('year', 'month', 'day', 'hour'),
                         ('辛亥', '庚子', '丙子', '己丑'))),
        'shishen': {}, 'kong_wang': {}, 'di_zhi_relations': {},
        'input': {'gender': '男'},
    }).compute_all()
    assert engine['caiming']['tier'] != '贫'


def test_h155_day_benqi_root_survives_single_chou_wei_chong():
    for pillars in (('癸亥', '甲子', '己未', '乙丑'),
                    ('癸亥', '甲子', '己丑', '乙未')):
        gans = [p[0] for p in pillars]
        zhis = [p[1] for p in pillars]
        assert classify_strength('己', gans, zhis) == '身弱'


def test_g15_month_control_direction_and_laoyu():
    # 月令→日支的真实反制入口修复；日支主动冲辰的反例A与书例锚冲突另列未决。
    reverse = ['壬', '甲', '戊', '壬'], ['辰', '辰', '戌', '子']
    assert _zf(*reverse)['type'] == 'fan'
    assert detect_fanju_chen_chou('戊', *reverse)['laoyu']


def test_h45_sanhe_participant_counts_as_main_position():
    left = _zf(['丙', '戊', '丙', '戊'], ['寅', '戌', '午', '子'])
    right = _zf(['丙', '戊', '丙', '戊'], ['子', '戌', '午', '寅'])
    assert left['type'] == right['type'] == 'zheng'
