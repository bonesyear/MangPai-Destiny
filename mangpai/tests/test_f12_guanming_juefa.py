# -*- coding: utf-8 -*-
"""F12 哨兵：guanming 五 P0 + juefa 断语7（批6 审计，先红后绿）。

书锚：
  制用四类双向      zhongji:3700「伤食制官杀或官杀制伤食」、3842「财星制印或印制
                    财星」、3868「印制伤食或伤食制印」；理象学:7277「伤食制官杀局
                    或官杀制伤食局」
  布莱尔            乾 癸巳丁巳丁巳戊申——「戊土伤官又合了七杀，制杀为得权…巳申合，
                    制去官之原神，且制的好，当了大官」（zhongji:3833-3836），英国首相
  庭长              乾 壬子丙午壬辰丙午——「壬水自坐七杀当官…羊刃合杀…是个当官的，
                    法院经济庭庭长」（zhongji:3808-3813）
  丁未孪生造        乾 壬子丙午壬辰丁未——「年月支冲，日时干合…此造原局就反了！见辰
                    有牢狱」（zhongji:3814-3822 / shouke:3462），与庭长造唯反局可分
  报社总编          乾 甲辰丙寅甲午丁卯——「羊刃制印库，有权…是报社总编。正司级」
                    （zhongji:4105-4108）；印配比禄=章首列目（zhongji:3678-3679）
  官禄格            「印生禄的，禄在主位，禄当权力，为官禄格」（zhongji:3969；
                    shouke:6392），慈禧 坤 乙未丁亥乙丑己卯「时上见禄…官都大到了极点」
  主位字门槛        书规则三「印星、官杀、伤食或财星做功，其中必须有主位的字，其它
                    位置做功所话容易是发财的」（zhongji:3683-3684）
  grade 映射        「一层功能达到科级到处级；二层处级到厅级；三层厅级到省部级；
                    四层总理或元首级」（理象学:6103-6104），与 gongliang._RANK_GRADE 同口径
  juefa 断语7       「提纲（月）克年，亦主父母不全」（gaoji:20230）——旧码方向接反
"""
import pytest

from mangpai.subjective.guanming import (
    analyze_guanming, classify_guanming_combo, assess_guanming_level,
)
from mangpai.subjective.juefa import analyze_juefa


def _is(g, z):
    return analyze_guanming(g[2], g, z)['is_guanming']


# ── 三书锚恢复（制用四类双向 + 印配比禄 + G5 误杀解除）──────────────

class TestThreeBookAnchors:
    def test_blair(self):
        # 布莱尔：戊癸合=官杀制伤食（反向合制），制去官之原神当大官
        assert _is(['癸', '丁', '丁', '戊'], ['巳', '巳', '巳', '申']) is True

    def test_tingzhang(self):
        # 庭长：羊刃合杀（子辰半合刃杀相制），杀刃相制本身即制，无须另要印化
        assert _is(['壬', '丙', '壬', '丙'], ['子', '午', '辰', '午']) is True

    def test_dingwei_twin_not_guan(self):
        # 丁未孪生造：日时丁壬合+年月子午冲=原局反局（书「见辰有牢狱」）——
        # 与庭长造唯一区分依据即反局，引擎反局否决须生效（身弱官杀有根非正向）
        a = analyze_guanming('壬', ['壬', '丙', '壬', '丁'], ['子', '午', '辰', '未'])
        assert a['is_guanming'] is False
        assert any(r.startswith('反局') for r in a['veto_reasons'])

    def test_zongbian(self):
        # 报社总编：羊刃卯穿辰印库=印配比禄（比劫制印库），四柱无官印主权力
        assert _is(['甲', '丙', '甲', '丁'], ['辰', '寅', '午', '卯']) is True


# ── 官禄格=印生禄+禄在主位（旧「官星坐禄」口径废）─────────────────

class TestGuanluGe:
    def test_cixi_guanluge(self):
        # 慈禧：乙禄在卯居时支（主位），亥印生禄——官禄格（zhongji:3969-3973）
        r = classify_guanming_combo('乙', ['乙', '丁', '乙', '己'],
                                    ['未', '亥', '丑', '卯'])
        assert '官禄格' in r['shengyong_huayong']

    def test_old_def_abolished(self):
        # 旧口径「官星坐禄」非书义：辛官坐酉但日主之禄不在主位，不立官禄格
        r = classify_guanming_combo('甲', ['辛', '丙', '甲', '戊'],
                                    ['酉', '寅', '辰', '午'])
        assert '官禄格' not in r['shengyong_huayong']


# ── 主位字门槛（zhongji:3683-3684）────────────────────────────────

class TestZhuweiGate:
    def test_pure_binbin_not_guan(self):
        # 纯年月互制（子午冲=官杀制比劫，两端皆宾位）不立官命——书规则三
        assert _is(['戊', '己', '丙', '丁'], ['子', '午', '酉', '卯']) is False


# ── grade 映射与书同口径（理象学:6103-6104，联动 F6 备案）──────────

class TestGradeMap:
    @pytest.mark.parametrize("level,frag", [
        (4, '总理-元首级'), (3, '厅级-省部级'), (2, '处级-厅级'), (1, '科级-处级'),
    ])
    def test_grade_map(self, level, frag):
        r = assess_guanming_level('甲', ['甲', '丙', '甲', '戊'],
                                  ['子', '午', '辰', '申'],
                                  gongliang_result={'level': level})
        assert frag in r['grade']


# ── juefa 断语7：提纲（月）克年方向（gaoji:20230）──────────────────

class TestJuefa7Direction:
    @staticmethod
    def _detail7(gans, zhis):
        r = analyze_juefa(gans, zhis, gans[2])
        for h in r['duanyu_hits']:
            if h['id'] == 7:
                return h['detail']
        return ''

    def test_month_ke_year(self):
        # 月干庚克年干甲=提纲克年 → 星宫双坏可断（比劫重重+财孤前提已具）
        d = self._detail7(['甲', '庚', '甲', '乙'], ['戌', '午', '卯', '巳'])
        assert '星宫双坏' in d

    def test_year_ke_month_not_counted(self):
        # 年干庚克月干甲=年克月（反向）→ 非书之「提纲克年」，不据此断
        d = self._detail7(['庚', '甲', '甲', '乙'], ['戌', '午', '卯', '巳'])
        assert '星宫双坏' not in d
