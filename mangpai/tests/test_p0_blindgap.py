# -*- coding: utf-8 -*-
"""盲测鸿沟四修复（P0-a/P0-b/P0-c/P1-a）回归测试。

根因（memory: blind-gap-rootcause-2026-07-28）：
  A 岁运反局 artifact 压原局档位（15例假阴）；B 原局凶向承重墙缺失
  （凶✅靠岁运 artifact 偶然供给）；C 职业 merchant 通道上限5<阈值6 结构性
  压死（全是 co-occurrence 信号）；D 功量→tier 基阶「百万级→贫」误映。

  P0-a caiming 原局/运岁分离：tier_static（原局轨）+ yunsui_delta（岁运增量），
      原局断语评原局轨、流年事件断语评含 delta 轨；
  P0-b yongshen 原局级凶向三式：伤官见官为忌(N1)/财生杀攻身(N2, severe)/
      官杀入墓(N3)，段氏高级篇锚定，扶抑用忌定吉凶向（对偶结构豁免）；
  P0-c zhiye merchant 重构：真实做功信号（财入局/主位合制财/食伤生财）替换
      co-occurrence，上限 5→9 阈值 6 可达；比劫夺财/富屋贫人 gating；
      teacher 木火通明收窄为天干口径、lawyer 共存加分压低；
  P1-a 功量→tier 基阶校准：有功一层=小富小贵（百万级）基阶小康非贫；
      财星当财·经营带原神+主位者基阶不落下富。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.caiming import analyze_caiming, assess_caiming_level
from mangpai.subjective.yongshen import (
    detect_shangguan_jianguan, detect_caisheng_sha_gongshen,
    detect_guansha_rumu_xiong, assess_direction_signals,
)
from mangpai.subjective.zhiye import classify_zhiye, _score_merchant, _score_teacher, _score_lawyer
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _wa(dg, gans, zhis):
    zg = analyze_zuogong(dg, zhis[2], gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3])
    return zg.get('work_actions') or []


# ───────────────────── P0-a：原局/运岁分离 ─────────────────────

class TestTierStaticYunsuiDelta:
    """caiming 双轨输出：tier_static + yunsui_delta。"""

    # C批换造：旧造丁丙庚丁/未午申丑（zhenbao-04）为零财局——C批零财 guard
    # （《中级》零财之局官杀当财不成立）起 zbj 不带上浮，原局档落小康，
    # 不再满足「原局档>封顶」的双轨演示前提；换 li001-乙亥发财造
    # （财统官封顶富：原局档富、全量轨岁运反局封顶小康），双轨语义不变。
    GANS = ['辛', '戊', '甲', '丁']
    ZHIS = ['卯', '戌', '申', '卯']
    FAKE_SLICE = {'dayun_fan': [{'gz': '癸卯', 'fans': [{'fan_type': '测试反局'}]}]}

    def test_no_yunfan_delta_none(self):
        """无运岁输入：yunsui_delta=None，tier == tier_static。"""
        cm = analyze_caiming('甲', self.GANS, self.ZHIS)
        assert cm['yunsui_delta'] is None
        assert cm['tier'] == cm['tier_static']
        assert cm['summary_static'] == cm['summary']

    def test_suiyun_cap_only_in_full_track(self):
        """岁运反局切片：全量轨封顶、原局轨不动——原局断语不再被 artifact 压档。"""
        # 注：本造为财统官杀当财独力上浮——K3 批A 起按「财统官须财量级支撑」
        # 封顶「富」不到巨富（财有原神且归主位/净制者不在此限），双轨语义不变。
        cm = analyze_caiming('甲', self.GANS, self.ZHIS,
                             yunfan_result=self.FAKE_SLICE)
        assert cm['tier_static'] == '富'        # 原局档不受岁运反局影响
        assert cm['tier'] == '小康'             # 全量轨被岁运反局封顶
        d = cm['yunsui_delta']
        assert d and d['suiyun_fanju'] is True
        assert d['capped'] is True
        assert d['tier_static'] == '富' and d['tier_final'] == '小康'

    def test_static_summary_free_of_suiyun_markers(self):
        """原局轨 summary 不含岁运文本（评分器凶向标记不吃 artifact）。"""
        cm = analyze_caiming('甲', self.GANS, self.ZHIS,
                             yunfan_result=self.FAKE_SLICE)
        assert '岁运' not in cm['summary_static']
        assert '下浮封顶' not in cm['summary_static']
        assert '岁运' in cm['summary']  # 全量轨保留

    def test_level_static_dict_present(self):
        cm = analyze_caiming('甲', self.GANS, self.ZHIS,
                             yunfan_result=self.FAKE_SLICE)
        assert cm['level_static']['tier'] == cm['tier_static']


# ───────────────────── P0-b：原局级凶向三式 ─────────────────────

class TestN1ShangguanJianguan:
    """伤官见官为忌：官为用神被伤=凶；官为忌神被去（伤官去官格）=吉不触发。"""

    def test_positive_shenqiang(self):
        # 身强庚：伤官壬/子（时）× 正官丁/午（日支），子午冲紧贴做功。
        # 月令取辰（非亥子丑申酉）——避开金水伤官诀「喜见官」豁免（总诀
        # 「伤官见官分宜畏，全在五行与节令」，诀法五行喜忌优先于凶向）。
        n1 = detect_shangguan_jianguan('庚', ['戊', '辛', '庚', '壬'],
                                       ['申', '辰', '午', '子'])
        assert n1['detected'] is True
        assert n1['severity'] == 'normal'
        assert '贵气损' in n1['reason'] or '伤官见官' in n1['reason']

    def test_jinshui_jue_exempt(self):
        # 金水伤官喜见官豁免：同上身强庚但月令酉（金水伤官变格，金旺生水），
        # 原局有火（午）-> 诀法「喜见官（调候暖局）」，N1 不触发。
        n1 = detect_shangguan_jianguan('庚', ['戊', '辛', '庚', '壬'],
                                       ['申', '酉', '午', '子'])
        assert n1['detected'] is False
        assert '喜见官' in n1.get('exemption', '')

    def test_negative_shenruo_quguan(self):
        # 身弱甲：官为忌神，伤官去官=吉（伤官去官格），不触发
        n1 = detect_shangguan_jianguan('甲', ['丁', '辛', '甲', '丙'],
                                       ['午', '酉', '寅', '亥'])
        assert n1['detected'] is False

    def test_negative_no_action(self):
        # 身强但伤官与正官无做功动作（仅共存），不触发
        n1 = detect_shangguan_jianguan('庚', ['戊', '辛', '庚', '壬'],
                                       ['申', '酉', '寅', '子'])
        assert n1['detected'] is False

    def test_peiyin_exempt(self):
        # 伤官配印豁免：丁日伤官（辰）见官（亥），寅印紧贴克辰伤官
        # （第三方纯印位、主位参与非宾宾）-> 伤官被制伏，见官不凶
        n1 = detect_shangguan_jianguan('丁', ['甲', '丙', '丁', '甲'],
                                       ['申', '寅', '辰', '亥'])
        assert n1['hits']  # 伤官见官动作存在
        assert n1['detected'] is False
        assert '伤官配印' in n1.get('exemption', '')

    def test_cai_tongguan_exempt(self):
        # 财星通关豁免：伤官见官动作为「克」（非冲穿实战）且财明现（申） ->
        # 伤官贪生财忘克官。丁日：辰伤官克亥官，申财明现
        n1 = detect_shangguan_jianguan('丁', ['丙', '丙', '丁', '甲'],
                                       ['申', '巳', '辰', '亥'])
        assert n1['detected'] is False
        assert '财星通关' in n1.get('exemption', '')


class TestN2CaishengShaGongshen:
    """财生杀攻身：身弱财旺生杀贴身无制、印化无力=因财致祸凶格（凶向标记，
    封顶小康不强行压贫——段氏财生杀局亦有大富潜质者）。"""

    def test_book_case4_detected(self):
        # 段氏高级篇案例四（财党杀攻身，因财致祸）：甲寅丙寅庚辰戊寅
        n2 = detect_caisheng_sha_gongshen('庚', ['甲', '丙', '庚', '戊'],
                                          ['寅', '寅', '辰', '寅'])
        assert n2['detected'] is True
        assert n2['severity'] == 'normal'

    def test_book_case2_cong_ruo_exempt(self):
        # 段氏案例二（财生杀，杀当财看，巨富）：从弱杀为用神，不触发
        n2 = detect_caisheng_sha_gongshen('戊', ['壬', '癸', '戊', '甲'],
                                          ['寅', '卯', '子', '寅'])
        assert n2['detected'] is False

    def test_shenqiang_exempt(self):
        # 身强能担财杀，不触发
        n2 = detect_caisheng_sha_gongshen('庚', ['戊', '己', '庚', '丁'],
                                          ['辰', '未', '午', '亥'])
        assert n2['detected'] is False

    def test_he_sha_exempt(self):
        # 合杀豁免（《授课》「癸水杀星为忌虚透，戊癸合去之无害」）：
        # 下海百万造（乙巳癸未丁丑戊申）：身弱丁、财明现（丑中辛+申中壬？
        # 财=金：丑/申）、杀（癸）贴身，然戊癸合去 -> 杀有制化，不触发
        n2 = detect_caisheng_sha_gongshen('丁', ['乙', '癸', '丁', '戊'],
                                          ['巳', '未', '丑', '申'])
        assert n2['detected'] is False


class TestN3GuanshaRumu:
    """官杀入墓为忌（限身弱：杀忌入墓=被官方关押；身强官用入墓属官运域，
    富贵局过火不入财命凶链；从格统杀为权豁免）。"""

    def test_positive_shenruo(self):
        # 身弱丙：官杀水（壬/子）明现，水墓辰在局未开（辰酉合非冲刑开库）
        n3 = detect_guansha_rumu_xiong('丙', ['壬', '甲', '丙', '戊'],
                                       ['辰', '子', '午', '酉'])
        assert n3['detected'] is True
        assert n3['strength'] == '身弱'

    def test_shenqiang_not_in_chain(self):
        # 身强官为用神入墓：官运域（失权罢官），不入财命凶向链
        n3 = detect_guansha_rumu_xiong('丙', ['壬', '甲', '丙', '丙'],
                                       ['辰', '寅', '午', '酉'])
        assert n3['detected'] is False

    def test_yanxishan_cong_exempt(self):
        # 阎锡山（从弱，丑统七杀掌兵权）：从格统杀为权，不论凶
        n3 = detect_guansha_rumu_xiong('乙', ['癸', '辛', '乙', '丁'],
                                       ['未', '酉', '酉', '丑'])
        assert n3['detected'] is False

    def test_tomb_zhuwei_exempt(self):
        # 墓之宾主归属（高级篇2.5「主位之墓库…墓库制忌，其祸自消」）：
        # 身弱丙、官杀水入墓辰在**日支**（主位）-> 制忌自消，不以被关押论
        n3 = detect_guansha_rumu_xiong('丙', ['壬', '甲', '丙', '戊'],
                                       ['子', '午', '辰', '酉'])
        assert n3['detected'] is False
        assert '主位' in n3.get('exemption', '')
        # 同构造但墓在年支（宾位）-> 官方收藏，仍触发
        n3b = detect_guansha_rumu_xiong('丙', ['壬', '甲', '丙', '戊'],
                                        ['辰', '子', '午', '酉'])
        assert n3b['detected'] is True


class TestMingjuXiongAggregation:
    """三式接入方向总线：mingju_xiong 聚合 + 财命封顶。"""

    def test_direction_signals_aggregates(self):
        # N2 案例四：mingju_xiong=True，normal（severe 留给比劫夺财）
        ds = assess_direction_signals('庚', ['甲', '丙', '庚', '戊'],
                                      ['寅', '寅', '辰', '寅'])
        assert ds['mingju_xiong'] is True
        assert ds['direction'] == '凶'
        assert any('财生杀' in r for r in ds['reasons'])

    def test_caiming_cap_via_mingju_xiong(self):
        # N2(normal) -> 财命封顶小康不压贫：案例四基阶本低（小康），不重复封顶
        cm = analyze_caiming('庚', ['甲', '丙', '庚', '戊'], ['寅', '寅', '辰', '寅'])
        assert cm['tier_static'] == '小康'
        # 封顶链路单测：高基阶 + mingju_xiong(normal) -> 封顶小康（severe 才压贫）
        lv = assess_caiming_level(
            '庚', ['甲', '丙', '庚', '戊'], ['寅', '寅', '辰', '寅'],
            gongliang_result={'level': 4, 'gong_points': 4.0, 'penalty': None,
                              'wealth_grade': '百亿-千亿级'},
            caifu_view={'views': [], 'cai_count': 0, 'guohe_chaiqiao_type': None,
                        'has_open_caiku': False, 'caixing_path': {}},
            direction_signals={'mingju_xiong': True, 'mingju_xiong_severe': False,
                               'reasons': ['财生杀攻身']})
        assert lv['tier'] == '小康'
        assert '封顶' in lv['adjust']

    def test_clean_rich_chart_unaffected(self):
        # 李嘉诚：三式俱不中，无 mingju_xiong
        ds = assess_direction_signals('庚', ['戊', '己', '庚', '丁'],
                                      ['辰', '未', '午', '亥'])
        assert ds['mingju_xiong'] is False


# ───────────────────── P0-c：merchant 通道重构 ─────────────────────

class TestMerchantChannel:
    """真实做功信号使 merchant 阈值可达；夺财/富屋贫人 gating 防过火。"""

    def test_real_work_signals_reach_threshold(self):
        # 复例四老师经商：财入局+主位合制财+食伤生财+门户 >= 6（书：经商）
        s, ev = _score_merchant('丁', ['戊', '丙', '丁', '癸'], ['申', '辰', '巳', '卯'],
                                _wa('丁', ['戊', '丙', '丁', '癸'], ['申', '辰', '巳', '卯']))
        assert s >= 6
        assert any('做功' in e for e in ev)
        r = classify_zhiye('丁', ['戊', '丙', '丁', '癸'], ['申', '辰', '巳', '卯'])
        assert r['primary'] == 'merchant'

    def test_duocai_chart_gated(self):
        # 乞丐（zhenbao-09）：比劫夺财 severe，merchant gating -> 落无业
        r = classify_zhiye('壬', ['壬', '癸', '壬', '丙'], ['子', '卯', '子', '午'])
        assert r['scores']['merchant'] == 0
        assert r['primary'] == 'unemployed'

    def test_fuwu_pinren_gated(self):
        # 富屋贫人（b67-初中）：身弱财旺无印，比劫全在宾位（年柱壬子）不帮身，
        # merchant gating
        r = classify_zhiye('壬', ['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未'])
        assert r['scores']['merchant'] == 0
        assert r['primary'] != 'merchant'

    def test_fuwu_pinren_zhuwei_bijiao_exempt(self):
        # K3 豁免：主位比劫帮身者非富屋贫人（段氏宾主论：主位比劫=自家人帮身
        # 任财）——qi14 亿万企业家（书例）：日支寅禄+时干甲比，财3位而富，
        # 不 gate（旧版无印即 gate 误杀）
        r = classify_zhiye('甲', ['辛', '戊', '甲', '甲'], ['巳', '戌', '寅', '戌'])
        assert r['scores']['merchant'] > 0

    def test_duocai_action_not_counted_as_work(self):
        # 比劫夺财动作（子冲午，日支比劫冲财）不计入「财星入局做功」
        s, ev = _score_merchant('壬', ['壬', '癸', '壬', '丙'], ['子', '卯', '子', '午'],
                                _wa('壬', ['壬', '癸', '壬', '丙'], ['子', '卯', '子', '午']))
        assert not any('冲财' in e for e in ev)


class TestTeacherLawyerCoexistenceSuppression:
    """teacher/lawyer 压低共存加分。"""

    def test_teacher_muhuo_gan_level(self):
        # 天干甲乙见丙丁（段氏口径）-> +2
        s, ev = _score_teacher('辛', ['甲', '丙', '辛', '己'], ['子', '午', '卯', '辰'], [])
        assert any('木火通明' in e for e in ev)
        # 仅地支木火共存 -> 弱信号 +1（无 +2）
        s2, ev2 = _score_teacher('辛', ['庚', '戊', '辛', '己'], ['寅', '午', '卯', '辰'], [])
        assert any('弱信号' in e for e in ev2)
        assert s - s2 >= 1

    def test_lawyer_no_coexistence_point(self):
        # 食神透干+官杀明现但无做功动作：旧版共存 +1，重构后 0
        s, ev = _score_lawyer('乙', ['丁', '甲', '乙', '辛'], ['卯', '辰', '未', '申'], [])
        assert not any('伤官见官' in e or '食神制官' in e for e in ev)


# ───────────────────── P1-a：功量→tier 基阶校准 ─────────────────────

class TestTierBaseCalibration:
    """有功一层=小康（百万级非贫）；财星当财·经营带原神+主位基阶不落下富。"""

    # 合成最小 caifu_view（无任何看法/路径）+ 纯比劫/印中性图表（无财/官杀，
    # 制不尽当财亦无从检出），隔离 view 系调整，专测基阶校准一
    _CV = {'views': [], 'cai_count': 0, 'guohe_chaiqiao_type': None,
           'has_open_caiku': False, 'caixing_path': {}}
    _DG = '甲'
    _GANS = ['甲', '乙', '甲', '甲']
    _ZHIS = ['寅', '卯', '亥', '子']

    def test_level1_with_gong_xiaokang(self):
        # 有功一层（points>0 非无功）-> 基阶小康（旧映「百万级→贫」复审修正）
        lv = assess_caiming_level(
            self._DG, self._GANS, self._ZHIS,
            gongliang_result={'level': 1, 'gong_points': 1.0, 'penalty': None,
                              'wealth_grade': '百万级'},
            caifu_view=dict(self._CV), direction_signals={})
        assert lv['tier'] == '小康'
        assert '基阶校准' in lv['adjust']

    def test_level1_no_gong_stays_pin(self):
        # 无功/半层（points=0 且 penalty=无功）-> 仍为贫（乞丐口径）
        lv = assess_caiming_level(
            self._DG, self._GANS, self._ZHIS,
            gongliang_result={'level': 1, 'gong_points': 0.0, 'penalty': '无功',
                              'wealth_grade': '百万级'},
            caifu_view=dict(self._CV), direction_signals={})
        assert lv['tier'] == '贫'

    def test_level1_xiong_not_calibrated(self):
        # 凶向命中者不做基阶校准（方向封顶收尾，免留升后复降矛盾文本）
        lv = assess_caiming_level(
            self._DG, self._GANS, self._ZHIS,
            gongliang_result={'level': 1, 'gong_points': 1.0, 'penalty': None,
                              'wealth_grade': '百万级'},
            caifu_view=dict(self._CV),
            direction_signals={'pocai': True, 'pocai_severe': True,
                               'reasons': ['比劫夺财破财']})
        assert lv['tier'] == '贫'
        assert '基阶校准' not in lv['adjust']

    def test_solid_caishang_floor3(self):
        # 生例一富婆：财星当财+原神（食伤）+主位财+经营做功，纵功量层低估（一层
        # 无功量点）基阶不落下富——段氏「有财则伤食是其原神，可以当投资之财」
        cm = analyze_caiming('庚', ['辛', '庚', '庚', '己'], ['亥', '子', '寅', '卯'])
        assert cm['tier_static'] == '富'
        assert '基阶校准（财星当财' in cm['level_static']['adjust']

    def test_shenruo_caiwang_no_floor(self):
        # 身弱财旺（富屋贫人）豁免基阶校准二
        cm = analyze_caiming('壬', ['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未'])
        assert '基阶校准（财星当财' not in cm['level_static']['adjust']
