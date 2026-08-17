# -*- coding: utf-8 -*-
"""zhengfan 书第一章 7 书例哨兵（F7 批：批4 zhengfan P0×4 修复锁定）。

《盲派中级命理学》第一章正反局 7 书例全量（批4 审计：7 书例仅 2 完全命中，
丙子戊戌/癸未丙辰两明文反局被判正局=方向相反）：
  案例1 辛亥丙申己丑甲戌  反局（:176-188 丑借金水之势刑戌坏体）
  案例2 甲辰戊辰癸卯己未  正局（:189-192/:220-227 合月官=管理别人）
  案例3 乙巳庚辰辛卯丙申  反局（:198-206/闲注:215 巳申合坏申）
  案例4 丙子戊戌丁丑丁未  反局（:236-247 日支合追求子水，与火土势相反）
  案例5 壬子庚戌辛丑己未  正局（:248-265 金水成势，子丑合顺势）
  案例6 癸未丙辰戊戌丙辰  反局（:266-275 辰临月令党众反制日支戌）
  案例7 己卯己巳辛亥甲午  正局（:139-140/:147-151 无势能做功亦正局）
朱元璋 guard：戊辰壬戌丁丑丁未 正局（:228-235 火与燥土势大，去湿土库）。
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangpai.subjective.zhengfan import analyze_zhengfan
from mangpai.subjective.zuogong_confirm import analyze_zuogong


def _zf(gans, zhis):
    zg = analyze_zuogong(gans[2], zhis[2], gans[0], zhis[0],
                         gans[1], zhis[1], gans[3], zhis[3])
    return analyze_zhengfan(zg.get('work_actions', []), zg.get('day_he_type'), gans, zhis)


def test_case1_shixin_bingshen_jichou_jiaxu_fan():
    """案例1：丑借金水之势刑戌坏体 → 反局（湿土丑计入金水党方成势）。"""
    zf = _zf(['辛', '丙', '己', '甲'], ['亥', '申', '丑', '戌'])
    assert zf['type'] == 'fan'
    assert '时支' in zf.get('reason', '') and '不可坏' in zf.get('reason', '')


def test_case2_jiachen_wuchen_maomao_jiwei_zheng():
    """案例2：合月干官=管理控制别人，卯穿辰与合官意一致 → 正局。"""
    zf = _zf(['甲', '戊', '癸', '己'], ['辰', '辰', '卯', '未'])
    assert zf['type'] == 'zheng'


def test_case3_yisi_gengchen_xinmao_bingshen_fan():
    """案例3：巳申合坏申（官党克合坏时支体）→ 反局。"""
    zf = _zf(['乙', '庚', '辛', '丙'], ['巳', '辰', '卯', '申'])
    assert zf['type'] == 'fan'
    assert '合坏' in zf.get('reason', '')


def test_case4_bingzi_wuxu_dingchou_dingwei_fan():
    """案例4：日支丑合子=追求子水，与火土成势去金水相反 → 反局。"""
    zf = _zf(['丙', '戊', '丁', '丁'], ['子', '戌', '丑', '未'])
    assert zf['type'] == 'fan'
    assert '追求' in zf.get('reason', '')


def test_case5_renzi_gengxu_xinchou_jiwei_zheng():
    """案例5：金水成势，子为势党己方，子丑合顺势 → 正局（不误触追求条款）。"""
    zf = _zf(['壬', '庚', '辛', '己'], ['子', '戌', '丑', '未'])
    assert zf['type'] == 'zheng'


def test_case6_guiwei_bingchen_wuxu_bingchen_fan():
    """案例6：日支戌冲辰欲制，辰临月令党众（两辰）反制戌 → 反局。"""
    zf = _zf(['癸', '丙', '戊', '丙'], ['未', '辰', '戌', '辰'])
    assert zf['type'] == 'fan'
    assert '反制' in zf.get('reason', '')


def test_case7_jimao_jisi_xinhai_jiawu_zheng():
    """案例7：八字无势，日主能做功=正局（中级139-140 书明文）。"""
    zf = _zf(['己', '己', '辛', '甲'], ['卯', '巳', '亥', '午'])
    assert zf['type'] == 'zheng'


def test_zhuyuanzhang_guard_zheng():
    """朱元璋 guard：火与燥土势大去湿土库 → 正局（反制条款不误伤）。"""
    zf = _zf(['戊', '壬', '丁', '丁'], ['辰', '戌', '丑', '未'])
    assert zf['type'] == 'zheng'
