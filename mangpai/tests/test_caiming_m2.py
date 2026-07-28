# -*- coding: utf-8 -*-
"""caiming M2 财命基座测试 - 财星源头/路径检测 + tier 三件套（档位+路径+阻因）。

段氏贫富三要素（《中级》财命专辑「八字有财，伤食是其原神」）：
  1. 财星是否有原神：食伤明现=有源头；无原神且财不在主位（日/时）=浮财 -> 降一阶；
  2. 生财路径是否畅通：明现财星被紧贴合绊（受害方口径同 yongshen R3）、
     财星本气支入墓未开 -> 各降一阶（官杀当财/制不尽当财路径不适用）；
  3. 制财得财 vs 制不净破财：过河拆桥（已有）与浮财/阻通同入 blockers。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.caiming import (
    analyze_caiming, classify_caifu_view, _assess_caixing_path,
)


# ── 受控 prom/wa 直接测检测器 ──

class TestCaixingPath:
    """_assess_caixing_path 受控单元测试。"""

    def test_fucai_no_yuanshen_no_zhuwei(self):
        # 戊日（财=水）：财透年干、无食伤、主位无财 -> 浮财
        prom = [{'财': 'gan'}, {'官杀': 'gan'}, {'比劫': 'gan'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['癸', '甲', '戊', '丙'],
                                 ['未', '寅', '辰', '辰'], prom, [], None)
        assert r['fucai'] is True
        assert r['has_yuanshen'] is False
        assert r['zhuwei_cai'] is False
        assert any('浮财' in b for b in r['blockers'])

    def test_not_fucai_when_yuanshen(self):
        # 有食伤明现 -> 非浮财
        prom = [{'财': 'gan'}, {'食伤': 'gan'}, {'比劫': 'gan'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['癸', '庚', '戊', '丙'],
                                 ['未', '寅', '辰', '辰'], prom, [], None)
        assert r['fucai'] is False
        assert r['has_yuanshen'] is True

    def test_not_fucai_when_zhuwei(self):
        # 财在主位（日支本气）-> 非浮财
        prom = [{'比劫': 'gan'}, {'比劫': 'gan'}, {'财': 'benqi'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['戊', '戊', '戊', '丙'],
                                 ['未', '寅', '子', '辰'], prom, [], None)
        assert r['fucai'] is False
        assert r['zhuwei_cai'] is True

    def test_heban_liuhe_victim(self):
        # 子丑合（两伤）：日支子为财本气 -> 财被合绊
        prom = [{'比劫': 'gan'}, {'比劫': 'benqi'}, {'财': 'benqi'}, {'比劫': 'gan'}]
        r = _assess_caixing_path('戊', ['戊', '戊', '戊', '戊'],
                                 ['午', '丑', '子', '申'], prom, [], None)
        assert len(r['heban']) == 1
        assert '子' in r['heban'][0]
        assert any('合绊' in b for b in r['blockers'])

    def test_heban_suppressed_by_chong(self):
        # 财支参与冲/穿做功 -> 已入局交战，不论绊（R3 同口径抑制）
        prom = [{'比劫': 'gan'}, {'比劫': 'benqi'}, {'财': 'benqi'}, {'比劫': 'gan'}]
        wa = [{'type': '冲', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'}]
        r = _assess_caixing_path('戊', ['戊', '戊', '戊', '戊'],
                                 ['午', '丑', '子', '申'], prom, wa, None)
        assert r['heban'] == []

    def test_heban_gan_wuhe(self):
        # 年×月干五合互绊：月干辛为透干财（丁日）被丙辛合绊
        prom = [{'比劫': 'gan'}, {'财': 'gan'}, {'比劫': 'gan'}, {'比劫': 'gan'}]
        r = _assess_caixing_path('丁', ['丙', '辛', '丁', '庚'],
                                 ['子', '丑', '卯', '戌'], prom, [], None)
        assert len(r['heban']) == 1
        assert '辛' in r['heban'][0]

    def test_rumu_tomb_not_open(self):
        # 申（金=财，丙日）入丑墓未开 -> 阻；开库 -> 不阻
        prom = [{'财': 'benqi'}, {'比劫': 'gan'}, {'比劫': 'gan'}, {'食伤': 'gan'}]
        muku_closed = {'tombs': [{'zhi': '丑', 'status': '墓库'}],
                       'tomb_relations': [{'from': {'zhi': '申'}, 'to': {'zhi': '丑'},
                                           'relation': '申(金)入丑墓'}]}
        r = _assess_caixing_path('丙', ['甲', '甲', '丙', '甲'],
                                 ['申', '午', '子', '丑'], prom, [], muku_closed)
        assert r['rumu'] == ['申(金)入丑墓']
        assert any('入墓' in b for b in r['blockers'])
        muku_open = {'tombs': [{'zhi': '丑', 'status': '开库'}],
                     'tomb_relations': [{'from': {'zhi': '申'}, 'to': {'zhi': '丑'},
                                        'relation': '申(金)入丑墓'}]}
        r2 = _assess_caixing_path('丙', ['甲', '甲', '丙', '甲'],
                                  ['申', '午', '子', '丑'], prom, [], muku_open)
        assert r2['rumu'] == []

    def test_no_cai_no_path(self):
        # 无明现财 -> 路径评估空（禄/食伤/官杀当财另行判定）
        prom = [{'比劫': 'gan'}, {'比劫': 'gan'}, {'比劫': 'gan'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['戊', '戊', '戊', '丙'],
                                 ['未', '寅', '辰', '辰'], prom, [], None)
        assert r['fucai'] is False and r['heban'] == [] and r['rumu'] == []


# ── 端到端：tier 三件套输出 ──

class TestCaimingTierTriplet:
    """analyze_caiming 输出「档位 + 生财路径(path) + 阻因(blockers)」。"""

    def test_triplet_fields_present(self):
        # 李嘉诚（戊辰 己未 庚午 丁亥）：巨富保持，三件套字段齐全
        cm = analyze_caiming('庚', ['戊', '己', '庚', '丁'], ['辰', '未', '午', '亥'])
        assert cm['tier'] == '巨富'
        assert cm['path'].startswith('财星当财')
        assert '原神' in cm['path'] or '源头' in cm['path']
        assert cm['blockers'] == []
        assert '生财路径' in cm['summary']
        assert cm['level']['path'] == cm['path']

    def test_guancai_path_no_fucai_downgrade(self):
        # 官杀当财路径（财统官/官统财/过河拆桥富格）：浮财口径不适用
        # 23a 清家荡产（庚戌 戊子 壬午 庚子）：财统官 + 凶向封顶，无浮财降档叠加
        cm = analyze_caiming('壬', ['庚', '戊', '壬', '庚'], ['戌', '子', '午', '子'])
        assert cm['tier'] == '贫'  # 凶向严重封顶保持
        assert '下浮（财星无原神' not in cm['level']['adjust']

    def test_lu_path_desc(self):
        # 禄神当财 -> 路径含「身体力行」
        cm = analyze_caiming('己', ['乙', '己', '己', '庚'], ['巳', '丑', '未', '午'])
        if cm['primary_view'] == '禄神当财':
            assert '身体力行' in cm['path']

    def test_blockers_avoid_xiong_markers(self):
        # 浮财/合绊/入墓阻因措辞不得含凶向标记词（评估器 rubric 口径）：
        # 破财/比劫夺财/坐牢/牢狱/官非/下浮封顶 —— 仅真凶向（过河拆桥破财）可用
        prom = [{'财': 'gan'}, {'官杀': 'gan'}, {'比劫': 'gan'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['癸', '甲', '戊', '丙'],
                                 ['未', '寅', '辰', '辰'], prom, [], None)
        for b in r['blockers']:
            for marker in ('破财', '比劫夺财', '坐牢', '牢狱', '官非', '下浮封顶'):
                assert marker not in b
