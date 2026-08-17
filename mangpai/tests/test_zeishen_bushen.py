"""段氏贼神捕神 / 净制 / 包制 / 冲链模块测试。

理论来源：段建业《段氏理象学-盲派命理研究》第六章（功量部分提及包制/冲链/
贼神捕神）。覆盖三检测函数输出契约、源文第6章命例回归、不成（气势浪费）判据、
普通八字弱制降档，及 analyze_zeishen_bushen 聚合 + Pillars 签名。

源文命例（与 test_gongliang 同口径）：
  李嘉诚  戊辰己未庚午丁亥  千亿富翁（午亥合制，净，非包制）
  乾隆    辛卯丁酉庚午丙子  帝王（子午酉卯金字塔冲链，净）
  克林顿  丙戌丙申乙丑戊寅  总统（寅戌火翼包制申金，净）
  蒋介石  丁亥庚戌己巳庚午  制不净（亥水原神庚金透干残存）
  岳飞    癸未乙卯甲子己巳  省部级（未巳土火包制子水，净）
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.zeishen_bushen import (
    detect_bao_zhi,
    detect_chong_lian,
    detect_zeishen_bushen,
    analyze_zeishen_bushen,
)
from mangpai.objective import Pillars

# ── 命例：(天干[年月日时], 地支[年月日时]) ──
LIJIACHENG = (['戊', '己', '庚', '丁'], ['辰', '未', '午', '亥'])
QIANLONG = (['辛', '丁', '庚', '丙'], ['卯', '酉', '午', '子'])
KELINTUN = (['丙', '丙', '乙', '戊'], ['戌', '申', '丑', '寅'])
JIANGJIESHI = (['丁', '庚', '己', '庚'], ['亥', '戌', '巳', '午'])
YUEFEI = (['癸', '乙', '甲', '已'], ['未', '卯', '子', '巳'])
# 构造：金党极旺（申酉申三金 + 庚辛透）克弱木（卯），overkill -> 不成
BUCHENG = (['庚', '辛', '庚', '辛'], ['申', '酉', '卯', '申'])
# 弱制普通四柱（木党旺克土，但土有原神火残存 -> 不净）
PUTONG = (['甲', '乙', '丙', '丁'], ['寅', '卯', '辰', '巳'])
# 全水局无冲克合 -> 无制
WUZHI = (['壬', '癸', '壬', '癸'], ['亥', '子', '亥', '子'])


def _zb(g, z):
    return analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)['zeishen_bushen']


# ════════════════════════════════════════════════════════════════════════
# 1. 包制 detect_bao_zhi
# ════════════════════════════════════════════════════════════════════════
class TestBaoZhi:
    """包制检测：年时同载制方五行 W，W 成势，W 克内柱主气。"""

    def test_clinton_fire_wrap_metal(self):
        """克林顿：寅戌火翼 + 两丙透干，围制申金（三合两翼）。"""
        g, z = KELINTUN
        r = detect_bao_zhi(g, z)
        assert r is not None
        assert r['detected'] is True
        assert r['wrap_wx'] == '火'
        assert r['target_wx'] == '金'
        assert r['wrap_pillars'] == ['year', 'hour']
        assert r['pattern'] == '三合两翼'
        assert r['points'] == 1
        assert r['party'] >= 4.0  # 成势

    def test_yuefei_earth_wrap_water(self):
        """岳飞：未巳同载土，包制子水（财包印）。"""
        g, z = YUEFEI
        r = detect_bao_zhi(g, z)
        assert r is not None
        assert r['wrap_wx'] == '土'
        assert r['target_wx'] == '水'
        assert r['target_pillar'] == 'day'  # 子在日柱

    def test_lijiacheng_no_bao_water_weak(self):
        """李嘉诚：辰亥同载水但水弱不成势（party<4），不判包制（功在合制）。"""
        g, z = LIJIACHENG
        assert detect_bao_zhi(g, z) is None

    def test_qianlong_no_bao(self):
        """乾隆：年卯时子无同载五行，非包制（功在冲链）。"""
        g, z = QIANLONG
        assert detect_bao_zhi(g, z) is None

    def test_output_contract(self):
        g, z = KELINTUN
        r = detect_bao_zhi(g, z)
        for k in ('detected', 'pattern', 'wrap_wx', 'target_wx', 'wrap_pillars',
                  'target_pillar', 'party', 'target_party', 'points', 'reason'):
            assert k in r, f'缺字段 {k}'
        assert isinstance(r['party'], float)
        assert isinstance(r['reason'], str) and r['reason']

    def test_degenerate_input(self):
        assert detect_bao_zhi([], []) is None
        assert detect_bao_zhi(['甲'], ['子']) is None  # 不足四柱


# ════════════════════════════════════════════════════════════════════════
# 2. 冲链 detect_chong_lian
# ════════════════════════════════════════════════════════════════════════
class TestChongLian:
    """冲链检测：有向制边（冲/克）最长路径 len>=2 且含冲边。"""

    def test_qianlong_pyramid_len3(self):
        """乾隆：子->午->酉->卯 三级相制金字塔（段氏源文）。"""
        g, z = QIANLONG
        r = detect_chong_lian(z, g)
        assert r is not None
        assert r['length'] == 3
        assert r['nodes'] == ['子', '午', '酉', '卯']
        # 链含冲边（子午冲、酉卯冲），午酉为克
        types = [t for t, _, _ in r['links']]
        assert '冲' in types
        assert r['has_chong'] is True
        assert r['points'] == 1

    def test_single_chong_not_counted(self):
        """单冲（链长 1）不计层层相制。子午单冲无续。"""
        z = ['子', '寅', '午', '亥']
        assert detect_chong_lian(z, ['甲', '丙', '庚', '丁']) is None

    def test_pure_ke_chain_no_chong_not_counted(self):
        """纯克链（无冲）不计（段氏层层相制以冲为骨）。寅->辰->子->巳 全克无冲。"""
        z = ['寅', '辰', '子', '巳']
        assert detect_chong_lian(z, ['甲', '戊', '壬', '丁']) is None

    def test_no_edge(self):
        """全水局无冲克，无链。"""
        z = ['亥', '子', '亥', '子']
        assert detect_chong_lian(z, ['壬', '癸', '壬', '癸']) is None

    def test_output_contract(self):
        g, z = QIANLONG
        r = detect_chong_lian(z, g)
        for k in ('detected', 'length', 'chain', 'nodes', 'links',
                  'has_chong', 'points', 'reason'):
            assert k in r
        assert isinstance(r['chain'], list)
        assert all(isinstance(t, tuple) and len(t) == 3 for t in r['links'])


# ════════════════════════════════════════════════════════════════════════
# 3. 贼神捕神 / 净制 detect_zeishen_bushen
# ════════════════════════════════════════════════════════════════════════
class TestZeishenBushen:
    """净/不净/不成/无制 四态判定。"""

    def test_qianlong_jing(self):
        """乾隆：捕火成势克金，金无原神土，净制。"""
        zb = _zb(*QIANLONG)
        assert zb['jing_zhi'] == '净'
        assert zb['bushen_wx'] == '火'
        assert zb['zeishen_wx'] == '金'
        assert zb['zeishen_isolated'] is True
        assert zb['momentum_waste'] is False

    def test_clinton_jing_via_bao_inner_yuanshen(self):
        """克林顿：包制申金，原神土=丑（日柱内柱）被围制 => 原神同制 => 净。"""
        g, z = KELINTUN
        bao = detect_bao_zhi(g, z)
        zb = detect_zeishen_bushen(g[2], g, z, bao_zhi=bao)
        assert zb['jing_zhi'] == '净'
        assert zb['bushen_wx'] == '火'
        assert zb['zeishen_wx'] == '金'
        # 原神土透干/本气实存（戌丑戊），但内柱被围 => 同制 => 孤立
        assert zb['zeishen_has_yuanshen'] is True
        assert zb['yuanshen_yi_zhi'] is True
        assert zb['zeishen_isolated'] is True

    def test_jiangjieshi_bujing_yuanshen_residual(self):
        """蒋介石：亥水贼神之原神庚金透干残存未被制 => 制不净，封顶三层。"""
        zb = _zb(*JIANGJIESHI)
        assert zb['jing_zhi'] == '不净'
        assert zb['zeishen_wx'] == '水'
        assert zb['zeishen_has_yuanshen'] is True
        assert zb['yuanshen_yi_zhi'] is False  # 原神金未被制
        assert zb['zeishen_isolated'] is False

    def test_jiangjieshi_wa_auxiliary_filtered(self):
        """F5 哨兵（书 6122-6126「制之不净，达不到四层功」）：透传 work_actions 时
        宾位 auxiliary 干克（丁克庚，non_day_ganke）不得塞入制局目标集——
        旧码未滤 auxiliary 致「金」入 target_wx_set → 原神同制误净。"""
        g, z = JIANGJIESHI
        wa_aux = [{'type': '克', 'from_pos': 'year_gan', 'to_pos': 'month_gan',
                   'auxiliary': True, 'non_day_ganke': True}]
        zb = detect_zeishen_bushen(g[2], g, z, work_actions=wa_aux)
        assert zb['jing_zhi'] == '不净'
        assert zb['yuanshen_yi_zhi'] is False
        # 对照：同一条非 auxiliary 真做功干克仍补目标集（金被制→原神同制→净）
        wa_main = [{'type': '克', 'from_pos': 'year_gan', 'to_pos': 'month_gan'}]
        zb2 = detect_zeishen_bushen(g[2], g, z, work_actions=wa_main)
        assert zb2['yuanshen_yi_zhi'] is True
        assert zb2['jing_zhi'] == '净'

    def test_yuefei_jing_no_yuanshen(self):
        """岳飞：子水贼神无原神金，未土捕神，净制。"""
        zb = _zb(*YUEFEI)
        assert zb['jing_zhi'] == '净'
        assert zb['zeishen_wx'] == '水'
        assert zb['zeishen_has_yuanshen'] is False
        assert zb['zeishen_isolated'] is True

    def test_lijiacheng_jing_he_zhi_not_bucheng(self):
        """李嘉诚：午亥合制（克合），捕火/贼水，净。关键：勿误判不成（气势浪费）。

        日主庚金生亥水=贼神，但日主不计残存原神；午未生合不计合制，午亥克合才计。
        """
        zb = _zb(*LIJIACHENG)
        assert zb['jing_zhi'] == '净'
        assert zb['bushen_wx'] == '火'  # 午亥合：午为 doer
        assert zb['zeishen_wx'] == '水'  # 亥为被合方（非未土）
        assert zb['momentum_waste'] is False
        # 日主庚（金，水之原神）不计 -> 水无残存原神 -> 孤立
        assert zb['zeishen_isolated'] is True

    def test_bucheng_momentum_waste(self):
        """不成：金党极旺（party14.5）克弱木（party3.0），overkill 做功落空。"""
        zb = _zb(*BUCHENG)
        assert zb['jing_zhi'] == '不成'
        assert zb['momentum_waste'] is True
        assert zb['bushen_wx'] == '金'
        assert zb['zeishen_wx'] == '木'
        assert zb['bushen_strength'] >= 6.0  # 太旺
        assert zb['bushen_strength'] / zb['zeishen_strength'] >= 3.0

    def test_putong_weak_control_bujing(self):
        """普通四柱：木党旺克土，但制非净（弱制或原神残存），不论高层。"""
        zb = _zb(*PUTONG)
        assert zb['jing_zhi'] in ('不净', '不成', '无制')
        assert zb['jing_zhi'] != '净'  # 普通八字不应判净制高层

    def test_wuzhi_no_control(self):
        """全水局无冲克合，无制局做功。"""
        zb = _zb(*WUZHI)
        assert zb['jing_zhi'] == '无制'

    def test_output_contract(self):
        zb = _zb(*QIANLONG)
        for k in ('jing_zhi', 'bushen_wx', 'zeishen_wx', 'bushen_strength',
                  'zeishen_strength', 'zeishen_isolated', 'zeishen_has_yuanshen',
                  'yuanshen_yi_zhi', 'cheng_dang', 'momentum_waste', 'reason',
                  'confidence'):
            assert k in zb, f'缺字段 {k}'
        assert zb['jing_zhi'] in ('净', '不净', '不成', '无制')
        assert zb['confidence'] == '中'

    def test_day_gan_not_counted_as_yuanshen(self):
        """铁律：日主不计贼神原神（做功之体非残存党）。

        李嘉诚日主庚金生亥水贼神，庚不计残存 -> 水判无原神 -> 净。
        对照：若误计日主，水有原神金残存 -> 不净（错）。
        """
        zb = _zb(*LIJIACHENG)
        assert zb['zeishen_wx'] == '水'
        assert zb['zeishen_has_yuanshen'] is False  # 庚（日主）不计


# ════════════════════════════════════════════════════════════════════════
# 4. 聚合 analyze_zeishen_bushen
# ════════════════════════════════════════════════════════════════════════
class TestAnalyze:
    """聚合入口：三路信号 + 功量点 + Pillars 签名。"""

    def test_aggregate_fields(self):
        r = analyze_zeishen_bushen(day_gan='庚', gans=QIANLONG[0], zhis=QIANLONG[1])
        for k in ('bao_zhi', 'chong_lian', 'zeishen_bushen', 'party_strength',
                  'points', 'reasons', 'confidence'):
            assert k in r
        assert isinstance(r['party_strength'], dict)
        assert set(r['party_strength']) == {'木', '火', '土', '金', '水'}

    def test_points_bao_plus_chonglian(self):
        """克林顿：包制(+1) + 冲链(+1) = 2 点；净制/不成不加点（调节封顶）。"""
        g, z = KELINTUN
        r = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        assert r['bao_zhi'] is not None
        assert r['chong_lian'] is not None
        assert r['points'] == 2.0

    def test_points_qianlong_chonglian_only(self):
        """乾隆：无包制，冲链(+1) = 1 点。"""
        g, z = QIANLONG
        r = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        assert r['bao_zhi'] is None
        assert r['chong_lian'] is not None
        assert r['points'] == 1.0

    def test_points_lijiacheng_zero(self):
        """李嘉诚：无包制无冲链，功在合制（净制不加点）= 0 点（净制为调节项）。"""
        g, z = LIJIACHENG
        r = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        assert r['bao_zhi'] is None
        assert r['chong_lian'] is None
        assert r['points'] == 0.0
        assert r['zeishen_bushen']['jing_zhi'] == '净'

    def test_pillars_signature(self):
        """Pillars 对象签名（与 analyze_gongliang 对齐）。"""
        p = Pillars(year_gan='辛', year_zhi='卯', month_gan='丁', month_zhi='酉',
                    day_gan='庚', day_zhi='午', hour_gan='丙', hour_zhi='子')
        r = analyze_zeishen_bushen(p)
        assert r['chong_lian'] is not None
        assert r['chong_lian']['length'] == 3
        assert r['zeishen_bushen']['jing_zhi'] == '净'

    def test_work_actions_passthrough(self):
        """work_actions 透传补全制局目标（不强依赖 zuogong）。"""
        g, z = QIANLONG
        # 透传空 work_actions，应与不传一致
        r1 = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        r2 = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z, work_actions=[])
        assert r1['zeishen_bushen']['jing_zhi'] == r2['zeishen_bushen']['jing_zhi']

    def test_reasons_nonempty_when_control(self):
        """有制局时 reasons 非空。"""
        g, z = KELINTUN
        r = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        assert len(r['reasons']) >= 2  # bao + chong_lian + zb
        assert all(isinstance(x, str) and x for x in r['reasons'])


# ════════════════════════════════════════════════════════════════════════
# 5. 源文命例回归总表
# ════════════════════════════════════════════════════════════════════════
class TestSourceRegression:
    """段氏源文第6章命例净态回归（5 例 + 不成 + 普通）。"""

    @pytest.mark.parametrize('name,g,z,expect_jing,expect_bao,expect_cl', [
        ('李嘉诚', *LIJIACHENG, '净', False, False),
        ('乾隆', *QIANLONG, '净', False, True),
        ('克林顿', *KELINTUN, '净', True, True),
        ('蒋介石', *JIANGJIESHI, '不净', False, True),
        ('岳飞', *YUEFEI, '净', True, False),
        ('不成case', *BUCHENG, '不成', True, False),
    ])
    def test_source_case(self, name, g, z, expect_jing, expect_bao, expect_cl):
        r = analyze_zeishen_bushen(day_gan=g[2], gans=g, zhis=z)
        zb = r['zeishen_bushen']
        assert zb['jing_zhi'] == expect_jing, (
            f'{name}: 期望 {expect_jing}，实际 {zb["jing_zhi"]}（{zb["reason"]}）')
        assert (r['bao_zhi'] is not None) == expect_bao, f'{name}: 包制检出不符'
        assert (r['chong_lian'] is not None) == expect_cl, f'{name}: 冲链检出不符'
