# -*- coding: utf-8 -*-
"""zhengfan 原局四项测试（K2）——《盲派中高级命理学》正反局章。

锁定四条规则的判定口径：
  1. 合官位置区分：合时干官=被官控制（时支规则生效）；
     合年/月干官=管理别人（不生效）。
  2. 时支做功归日主：合时干官时，时支（官之兵卒）发起的实质做功并入日主之功。
  3. 时支不可坏特判：合时干官+时支为体（印/劫）+被得势方所坏 → 反局；
     无势之穿刑不为坏（制例三 戌穿酉制食神局=大富正例，不判反）。
  4. 年月 vs 日时冲合矛盾：一冲一合，八字自乱 → 反局。
"""
import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.zhengfan import analyze_zhengfan, _he_guan_position
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _zf(gans, zhis):
    zg = analyze_zuogong(zhis[2] and gans[2], zhis[2],
                         gans[0], zhis[0], gans[1], zhis[1], gans[3], zhis[3])
    return analyze_zhengfan(zg.get('work_actions', []), zg.get('day_he_type'), gans, zhis)


# ── 1. 合官位置区分 ──

def test_he_guan_position_hour():
    """己日甲戌时（甲=正官在时干）→ hour；辛日丙申时 → hour。"""
    assert _he_guan_position('己', ['癸', '戊', '己', '甲']) == 'hour'
    assert _he_guan_position('辛', ['乙', '庚', '辛', '丙']) == 'hour'


def test_he_guan_position_month_year():
    """癸日合月干戊官 → month（管理别人，不入时支规则）；合年干官 → year。"""
    assert _he_guan_position('癸', ['甲', '戊', '癸', '己']) == 'month'
    assert _he_guan_position('癸', ['戊', '甲', '癸', '己']) == 'year'


def test_he_guan_position_not_guan():
    """合财/合非官不命中：戊日合癸（癸=财）→ ''；无合 → ''。"""
    assert _he_guan_position('戊', ['甲', '戊', '癸', '己']) == ''  # 月干戊比肩
    assert _he_guan_position('庚', ['甲', '丙', '庚', '壬']) == ''


def test_he_guan_meaning_in_reason():
    """合时干官的 reason 带「被官控制」注记（位置区分入文案）。"""
    zf = _zf(['乙', '庚', '辛', '丙'], ['巳', '辰', '卯', '申'])
    assert '被官控制' in (zf.get('reason') or '')


# ── 2. 时支做功归日主 ──

def test_hour_zhi_work_attributed_to_day():
    """合时干官时，时支发起的实质做功归日主（全局侧不再计该功）。

    构造：己日甲戌时（合官），时支戌与月支子无特殊关系仅五行克（土克水）；
    归功后时支之功于 day 侧可考。用直接构造的 work_actions 锁定归功语义。
    """
    wa = [
        {'type': '天干合', 'from_pos': 'day_gan', 'to_pos': 'hour_gan'},
        {'type': '克', 'from_pos': 'hour_zhi', 'to_pos': 'month_zhi'},  # 时支之功
    ]
    # 归功：hour_zhi 发起的克并入日柱之功 → 日柱有做功，不判「无功不为局」
    zf = analyze_zhengfan(wa, '合官', ['丙', '戊', '己', '甲'], ['午', '子', '酉', '戌'])
    assert zf['configuration'] != '无功不为局'
    # 对照：无合官（他干），同一 hour_zhi 克不归功 → 日柱仅合，判无功不为局
    wa2 = [{'type': '克', 'from_pos': 'hour_zhi', 'to_pos': 'month_zhi'}]
    zf2 = analyze_zhengfan(wa2, None, ['丙', '戊', '庚', '甲'], ['午', '子', '辰', '戌'])
    assert '无功不为局' in zf2['configuration']


# ── 3. 时支不可坏特判 ──

def test_hour_zhi_ti_damaged_by_qishi_side_fan():
    """戊申 庚申 己丑 甲戌：土旺成势，日支丑（土，得势）刑时支戌（劫财=体）→ 反局。"""
    zf = _zf(['戊', '庚', '己', '甲'], ['申', '申', '丑', '戌'])
    assert zf['type'] == 'fan'
    assert '时支' in (zf.get('reason') or '') and '不可坏' in (zf.get('reason') or '')


def test_zhili3_hour_zhi_not_damaged_no_fan():
    """制例三（癸卯 戊午 己酉 甲戌）：戌穿酉制食神局=大富正例——
    无明确成势，酉穿戌不为坏，不得判反局（特判保护）。"""
    zf = _zf(['癸', '戊', '己', '甲'], ['卯', '午', '酉', '戌'])
    assert zf['type'] != 'fan'


def test_hour_zhi_yong_can_be_damaged():
    """时支是用（财/官/食伤）则可以坏：化例三中堂（己丑日甲子时，子=财）
    子丑合中子被合绊不触发特判；且规则对用时支不兜底判反。"""
    zf = _zf(['甲', '丙', '己', '甲'], ['子', '寅', '丑', '子'])
    assert zf['type'] != 'fan'


# ── 4. 年月 vs 日时冲合矛盾 ──

def test_chong_he_contradiction_fan():
    """年月冲+日时合（合例六两妻：酉卯冲+戌卯合）→ 反局。"""
    wa = [{'type': '地支合', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'}]
    zf = analyze_zhengfan(wa, None, ['己', '丁', '庚', '己'], ['酉', '卯', '戌', '卯'])
    assert zf['type'] == 'fan'
    assert '冲合' in (zf.get('reason') or '') or '矛盾' in (zf.get('reason') or '')


def test_he_chong_contradiction_fan():
    """年月合+日时冲（例9型：寅申冲/巳申合 之镜像——巳申合年月+申寅冲日时）→ 反局。"""
    wa = [{'type': '冲', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'}]
    zf = analyze_zhengfan(wa, None, ['甲', '丙', '戊', '庚'], ['巳', '申', '申', '寅'])
    assert zf['type'] == 'fan'


def test_same_mode_no_contradiction():
    """年月冲+日时冲（同为冲局）→ 不触发矛盾特判（子午卯酉全局冲）。"""
    wa = [{'type': '冲', 'from_pos': 'day_zhi', 'to_pos': 'hour_zhi'},
          {'type': '冲', 'from_pos': 'year_zhi', 'to_pos': 'month_zhi'}]
    zf = analyze_zhengfan(wa, None, ['甲', '丙', '戊', '庚'], ['子', '午', '卯', '酉'])
    # 不因 K2-4 判反（既有 柱位/五行 规则可能判反，但 reason 不含矛盾注记）
    assert '矛盾' not in (zf.get('reason') or '')
