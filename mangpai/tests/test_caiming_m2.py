# -*- coding: utf-8 -*-
"""caiming M2 财命基座测试 - 财星源头/路径检测 + tier 三件套（档位+路径+阻因）。

段氏贫富三要素（《中级》财命专辑「八字有财，伤食是其原神」）：
  1. 财星是否有原神：食伤明现=有源头；无原神且财不在主位（日/时）=浮财 -> 降一阶；
  2. 生财路径是否畅通：明现财星被紧贴合绊（受害方口径同 yongshen R3）、
     财星本气支入墓未开 -> 各降一阶（官杀当财/制不尽当财路径不适用）；
  3. 制财得财：过河拆桥（结构成立即富格，制尽只影响量级，zhongji:2976-2978）。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.caiming import (
    analyze_caiming, classify_caifu_view, _assess_caixing_path,
    assess_direction_signals,
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

    def test_r4_relation_only_po_still_counts_as_cai_damage(self):
        # 破退出做功，不退出「财被众破」的坏义；两卯破午为受控结构例。
        prom = [{'印': 'gan'}, {'比劫': 'gan'}, {'财': 'benqi'}, {'印': 'gan'}]
        wa = [
            {'type': '破', 'from_pos': 'year_zhi', 'to_pos': 'day_zhi',
             'relation_only': True, 'auxiliary': True},
            {'type': '破', 'from_pos': 'hour_zhi', 'to_pos': 'day_zhi',
             'relation_only': True, 'auxiliary': True},
        ]
        r = _assess_caixing_path('壬', ['壬', '壬', '壬', '壬'],
                                 ['卯', '子', '午', '卯'], prom, wa, None)
        assert len(r['cai_zhonggong']) == 1
        assert '2方' in r['cai_zhonggong'][0]

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
        # 破财/比劫夺财/坐牢/牢狱/官非/下浮封顶 —— 仅真凶向可用
        prom = [{'财': 'gan'}, {'官杀': 'gan'}, {'比劫': 'gan'}, {'印': 'gan'}]
        r = _assess_caixing_path('戊', ['癸', '甲', '戊', '丙'],
                                 ['未', '寅', '辰', '辰'], prom, [], None)
        for b in r['blockers']:
            for marker in ('破财', '比劫夺财', '坐牢', '牢狱', '官非', '下浮封顶'):
                assert marker not in b


# ── 批E：合财身强弱书口径（理象学:6672-6684「只有合财的时候讲身强身弱…
#    合财就像背一个包袱，身强可以胜财，身弱就不能胜财。此时的身强并不是
#    党多为强，只要坐支得旺就表示强」）——坐支得旺=日支为日主禄/旺/生扶
#    之根（比劫/印本气），仅用于合财相关判定的强弱分流，全局扶抑口径不变 ──

from mangpai.subjective.caiming import assess_caiming_level
from mangpai.subjective.yongshen import classify_strength

_GL2 = {'level': 2, 'wealth_grade': '小康', 'gong_points': 1}


def test_e_hecai_zuozhi_dewang_not_suppressed():
    """甲日坐寅（禄=坐支得旺），甲己合财做功+财3位有原神+财归主位：
    全局扶抑身弱，但合财以坐支得旺为强——不按身弱财旺（富屋贫人）
    抑制升档（哨兵：坐支得旺的身弱合财不再判穷）。"""
    g, z = ['丙', '己', '甲', '戊'], ['午', '亥', '寅', '辰']
    assert classify_strength('甲', g, z) == '身弱'  # 全局口径前提不变
    cv = classify_caifu_view('甲', g, z)
    lv = assess_caiming_level('甲', g, z, dict(_GL2), cv, direction_signals={})
    assert lv['tier'] == '富'


def test_e_hecai_zuozhi_buwang_still_suppressed():
    """对照：甲日坐申（七杀，非禄/旺/生扶之根），同构身弱合财——
    富屋贫人抑制不动，仍封顶小康。"""
    g, z = ['壬', '己', '甲', '戊'], ['亥', '巳', '申', '辰']
    assert classify_strength('甲', g, z) == '身弱'
    cv = classify_caifu_view('甲', g, z)
    lv = assess_caiming_level('甲', g, z, dict(_GL2), cv, direction_signals={})
    assert lv['tier'] == '小康'


# ── 批P1：财命遗漏规则补全哨兵（批1 审计遗漏清单 caiming 节，书例行号均
#    经 sed 复核 docs/duan-books/ 原文）──

from mangpai.subjective.caiming import classify_qucai_method


class TestLuDangcaiTiaojian:
    """条目1：禄当财成立条件（zhongji:2603-2607「命中占禄，无伤食泄时，或八字
    无财时，禄可以当财看…禄是现成之福，其条件是印生禄…（注：以禄当财，喜印，
    忌伤食劫财）」）——旧码仅「无财+见禄」一腿。"""

    def test_book_anchor_yin_sheng_lu(self):
        # 书例 zhongji:2610-2614 乾：癸丁丁丙/卯巳巳午——书判「故为印生禄，
        # 以禄当财，享受之命」（无财+禄午居时+卯印本气；巳中戊中气伤食泄禄
        # 不挡「无财」腿——书以「或」并联两腿）
        v = classify_caifu_view('丁', ['癸', '丁', '丁', '丙'], ['卯', '巳', '巳', '午'])
        assert '禄神当财' in v['views']
        assert any('印生禄' in d for d in v['details'])

    def test_leg_a_cai_present_no_shishang(self):
        # (a)腿：占禄无伤食泄时，有财亦禄当财（zhongji:2603「命中占禄，无伤食
        # 泄时」与「无财」或并联）。辛日禄酉（酉独气，无食伤中气）；财木乙/卯
        # 明现；局无水（食伤）——旧码漏检此腿
        v = classify_caifu_view('辛', ['戊', '己', '辛', '乙'], ['戌', '丑', '酉', '卯'])
        assert v['has_cai'] and v['has_lu'] and not v['has_shishang']
        assert '禄神当财' in v['views']

    def test_fanju_shishang_xie_lu(self):
        # 反例不误伤：忌伤食泄禄（zhongji:2607）——李嘉诚（戊辰己未庚午丁亥）
        # 己禄午居主位，但亥水食伤本气明现泄禄、局有财（未中乙中气）——
        # (a)腿被伤食泄禄排除、(b)腿被有财排除，禄不当财（旧码本不命中，锁回归）
        v = classify_caifu_view('庚', ['戊', '己', '庚', '丁'], ['辰', '未', '午', '亥'])
        assert v['has_cai'] and v['has_lu'] and v['has_shishang']
        assert '禄神当财' not in v['views']


class TestLuZhiCaiFacai:
    """条目2：「以禄当财富时，禄神制财星可发财」（zhongji:2637；同页闲注
    「禄神合财或制财都为得财」）。"""

    def test_lu_zhi_cai_hit(self):
        # 辛日禄酉居日支，酉冲时支卯财（卯酉冲，禄制财）→ 禄得财发财信号
        v = classify_caifu_view('辛', ['戊', '己', '辛', '乙'], ['戌', '丑', '酉', '卯'])
        assert '禄神当财' in v['views']
        assert v.get('lu_zhi_cai') is True
        assert any('禄' in d and '财' in d and '发财' in d for d in v['details'])

    def test_no_cai_no_lu_zhi_cai(self):
        # 反例：无财局（书例癸丁丁丙造）禄当财而无财可制/合 -> 不命中
        v = classify_caifu_view('丁', ['癸', '丁', '丁', '丙'], ['卯', '巳', '巳', '午'])
        assert '禄神当财' in v['views']
        assert not v.get('lu_zhi_cai')


class TestGuanshaDaixiang:
    """条目3：官杀带财象（官杀当财第三式，zhongji:2819-2820「还有种情况是干财
    支官（或者杀），为官杀带财象，官杀可统财」）。"""

    def test_book_anchor_xinhai_daixiang(self):
        # 书例 zhongji:2823-2828 乾：丙庚丁辛/午寅亥亥——时柱辛亥=干财支官
        # （闲注「辛亥带象」）；财2官2平数，统两式不立，唯带财象命中
        v = classify_caifu_view('丁', ['丙', '庚', '丁', '辛'], ['午', '寅', '亥', '亥'])
        assert any('带财象' in x for x in v['views'])
        assert '财统官' not in v['views'] and '官统财（官杀当财）' not in v['views']

    def test_fanju_guan_gan_cai_zhi(self):
        # 反例：干官支财（壬申：壬官/申财）非「干财支官」-> 带财象不命中
        v = classify_caifu_view('丁', ['壬', '辛', '丁', '庚'], ['申', '寅', '亥', '午'])
        assert not any('带财象' in x for x in v['views'])


class TestYangzhuShashenDangcai:
    """条目4：阳日主七杀当财（gaoji:10021-10022「阳日主，七杀当财富：如戊土
    日主见甲木七杀，常以七杀为财富目标」；旁证 zhongji:752「戊土长生在寅，
    杀当财看。因为没有印，有印当权看」）。"""

    def test_book_anchor_wu_jiayin(self):
        # 书例 zhongji:751-753 乾：丁甲戊甲/酉辰辰寅——戊阳日主，甲杀双透
        # +寅杀本气；丁印虚透无本气根（书判「没有印」）-> 杀当财看
        v = classify_caifu_view('戊', ['丁', '甲', '戊', '甲'], ['酉', '辰', '辰', '寅'])
        assert any('七杀当财' in x for x in v['views'])

    def test_fanju_yin_rooted(self):
        # 反例：印有本气根（午火印本气+丙透，化杀有力）-> 当权看，不立杀当财
        v = classify_caifu_view('戊', ['甲', '丙', '戊', '庚'], ['寅', '午', '辰', '申'])
        assert not any('七杀当财' in x for x in v['views'])

    def test_fanju_yin_day_master(self):
        # 反例：阴日主（乙见辛杀双透）不立此式（书限「阳日主」）
        v = classify_caifu_view('乙', ['丁', '辛', '乙', '辛'], ['酉', '丑', '巳', '酉'])
        assert not any('七杀当财' in x for x in v['views'])


class TestXutouHecai:
    """条目5：财星虚透合财→财虚主才能，不主财富（理象学:6682-6684「身强或
    身弱，遇财星虚透合财时，要看此财代表什么，若无所指代，财虚主才能，不
    主财富」）。"""

    def test_xutou_hecai_blocker(self):
        # 财虚透（癸透月干、支无本/中气财根）+日主戊癸合财做功 -> 阻因在档
        prom = [{'比劫': 'benqi'}, {'财': 'gan'}, {'比劫': 'gan'}, {'印': 'benqi'}]
        wa = [{'type': '天干合', 'from_pos': 'month_gan', 'to_pos': 'day_gan'}]
        r = _assess_caixing_path('戊', ['甲', '癸', '戊', '丙'],
                                 ['寅', '酉', '午', '巳'], prom, wa, None)
        assert r['xutou_hecai'] is True
        assert any('虚透' in b and '才能' in b for b in r['blockers'])

    def test_rooted_cai_not_xutou(self):
        # 反例：财有支根（时支子本气财）合财 -> 非虚透（理象学:6686 例一
        # 庚丙壬丁/子戌申未「身强财旺，合财可发财」之属，不记阻）
        prom = [{'比劫': 'benqi'}, {'财': 'gan'}, {'比劫': 'gan'}, {'财': 'benqi'}]
        wa = [{'type': '天干合', 'from_pos': 'month_gan', 'to_pos': 'day_gan'}]
        r = _assess_caixing_path('戊', ['甲', '癸', '戊', '丙'],
                                 ['寅', '酉', '午', '子'], prom, wa, None)
        assert r['xutou_hecai'] is False
        assert not any('虚透' in b for b in r['blockers'])

    def test_xutou_without_hecai_not_blocked(self):
        # 反例：财虚透但无合财做功 -> 书的前提（「虚透合财时」）不成立，不记阻
        prom = [{'比劫': 'benqi'}, {'财': 'gan'}, {'比劫': 'gan'}, {'印': 'benqi'}]
        r = _assess_caixing_path('戊', ['甲', '癸', '戊', '丙'],
                                 ['寅', '酉', '午', '巳'], prom, [], None)
        assert r['xutou_hecai'] is False

    def test_ku_zhongqi_root_not_xutou(self):
        # 反例（库根非虚）：透干财通根库中气（辛丑柱——丑中辛中气=财之库根）。
        # prom 每柱每类只留最高气位（透干财掩盖同柱中气财根），根判须直扫藏干；
        # 书锚 reg67-癸巳管财官（辛丑辛卯丙寅癸巳）「丑是财库…可以肯定，他是
        # 个管理财的官」——库根之财不当虚看
        prom = [{'财': 'gan', '食伤': 'benqi'}, {'印': 'benqi'}, {'比劫': 'gan'}, {'官杀': 'gan'}]
        wa = [{'type': '天干合', 'from_pos': 'year_gan', 'to_pos': 'day_gan'}]
        r = _assess_caixing_path('丙', ['辛', '辛', '丙', '癸'],
                                 ['丑', '卯', '寅', '巳'], prom, wa, None)
        assert r['xutou_hecai'] is False


class TestShengyongSanshi:
    """条目6：生用三式细分（理象学:6553-6559「其一是财在主位，由宾位之食伤
    生之为功，这种情形一般是自己做生意取财；其二是主位的食神去生宾位的财，
    也为做功，主我的智力头脑为他人服务，做经理人之类的职业；其三是原局伤食
    旺相，生财为用，谓秀气发越」）——批1窄化补全：经营旧仅财星+合/制财、
    工薪旧仅制官得官，生用宾主两式无路径。"""

    def test_shishi1_bin_ss_sheng_zhu_cai(self):
        # 式一：宾位食伤（壬月干/子月支本气）生主位财（寅日支）-> 自己做生意
        qm = classify_qucai_method('庚', ['丙', '壬', '庚', '丁'], ['午', '子', '寅', '亥'])
        assert '经营' in qm['methods']
        assert any('自己做生意' in d for d in qm['details'])

    def test_shishi2_zhu_ss_sheng_bin_cai(self):
        # 式二：主位食伤（壬时干）生宾位财（甲乙寅卯在年月）-> 经理人（工薪，
        # 旧码此局无制官得官动作、工薪不立——哨兵先红）
        qm = classify_qucai_method('庚', ['甲', '乙', '庚', '壬'], ['寅', '卯', '辰', '巳'])
        assert '工薪' in qm['methods']
        assert any('经理人' in d for d in qm['details'])

    def test_shishi3_xiuqi_fayue(self):
        # 式三：伤食旺相（壬/子/亥三位明现）生财为用 -> 秀气发越（智力在档）
        qm = classify_qucai_method('庚', ['丙', '壬', '庚', '丁'], ['午', '子', '寅', '亥'])
        assert '智力' in qm['methods']
        assert any('秀气发越' in d for d in qm['details'])

    def test_fanju_no_ss_shengcai(self):
        # 反例：无食伤生财做功 -> 三式俱不命中（工薪不因生用误增）
        qm = classify_qucai_method('庚', ['甲', '丙', '庚', '戊'], ['寅', '午', '辰', '戌'])
        assert not any('自己做生意' in d or '经理人' in d or '秀气发越' in d
                       for d in qm['details'])


class TestS2Zb14bTierAnchor:
    """zhenbao-14b：R4 入墓优先取消半合双计，基阶 L1 直接落贫，不伪造下浮。"""

    GANS = ['戊', '戊', '戊', '甲']
    ZHIS = ['戌', '午', '午', '寅']

    def test_zb14b_tier_static_pin(self):
        r = analyze_caiming('戊', self.GANS, self.ZHIS)
        assert r['tier_static'] == '贫'
        assert r['level_static']['base_level'] == 1
        assert r['level_static']['adjust'] == '持平'

    def test_zb14b_direction_xiong(self):
        d = assess_direction_signals('戊', self.GANS, self.ZHIS)
        assert d['direction'] == '凶'


class TestCaihuaiyinTongguanCap:
    """财命专批（2026-10-25）：R2 财坏印 severe 的「藏官出库暗合」通关豁免
    （仅 caiming 封顶链；R2 检出不变）。

    书证 mingli-zhenbao-50qi:494-496（第14期 刘XX 乙未/丙戌/甲子/乙亥）：
    「辛金不明现，暗藏在戌中又被未土刑开，丙辛暗合」「因未戌之刑戌开库，
    辛会出库」「弱忌神被合去主吉，而戌土之财是通过丙辛之暗合取得的」——
    官星通关（财生官、官生印）/合去坏印之力，财路不被坏印切断，书判富
    （卖身起家/靠权赚钱）。反锚：无通关的 R2 财坏印 severe 照旧封顶小康。
    """

    # 第14期 刘XX：乙未 丙戌 甲子 乙亥（坤）
    GANS = ['乙', '丙', '甲', '乙']
    ZHIS = ['未', '戌', '子', '亥']

    def test_14a_tier_fu_not_capped(self):
        r = analyze_caiming('甲', self.GANS, self.ZHIS)
        assert r['tier_static'] == '富'
        assert '下浮封顶' not in r['summary_static']
        assert '官星通关' in r['level_static']['adjust']

    def test_reverse_anchor_no_tongguan_capped(self):
        # reg67-甲子地矿局长 癸甲戊癸/巳子午亥：R2 财坏印 severe（财2处），
        # 局无「财库藏官出库暗合」-> 照旧封顶小康
        r = analyze_caiming('戊', ['癸', '甲', '戊', '癸'],
                            ['巳', '子', '午', '亥'])
        assert r['tier_static'] == '小康'
        assert '下浮封顶2阶' in r['summary_static']

    def test_only_xiong_source_exempted(self):
        # 豁免只对「唯一凶向=R2 财坏印 severe」成立：通关之外另有反局/
        # 原局凶向/R3 者，照旧封顶小康
        ds = assess_direction_signals('甲', self.GANS, self.ZHIS)
        cv = classify_caifu_view('甲', self.GANS, self.ZHIS)
        gl = {'level': 2, 'gong_points': 2.5, 'penalty': None, 'wealth_grade': ''}
        base = assess_caiming_level('甲', self.GANS, self.ZHIS, dict(gl), cv,
                                    direction_signals=ds)
        assert base['tier'] == '富'
        for key in ('fanju', 'mingju_xiong'):
            lv = assess_caiming_level('甲', self.GANS, self.ZHIS, dict(gl), cv,
                                      direction_signals=dict(ds, **{key: True}))
            assert lv['tier'] == '小康'
        lv = assess_caiming_level(
            '甲', self.GANS, self.ZHIS, dict(gl), cv,
            direction_signals=dict(ds, heban_yongshen={'detected': True}))
        assert lv['tier'] == '小康'
