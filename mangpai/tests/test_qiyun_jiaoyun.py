# -*- coding: utf-8 -*-
"""F3 岁运地基批·书例哨兵：起运岁 / 晚子时 / 交运时间。

书锚（《段氏理象学》理象学版行号——修批C 更正标签，旧误标「研究版」，R3）：
  - 起运岁 :3854-3856「用三除之，除不尽时，余一舍掉，余二进一」
            :3864-3873「最大为十，最小则为一…不足一天，也是以一岁起运排」
            :3875-3877「所算出的起运岁数是以虚岁定」
            :3916-3922 书例：2005-3-15 巳时生男，逆数至惊蛰(3-5)差10天，
             10/3 余一舍 → 3 虚岁起运，大运 03戊寅 13丁丑 23丙子
  - 晚子时 :3703-3709「夜子时所配天干以本日日上起时歌推转一轮再纳天干」
            （甲子日晚子 → 丙子）；:3713-3716 书例：2010-12-9 晚23:30
            → 日柱癸巳（本日）+ 时柱甲子；早子时 0:30 → 癸巳壬子全对
  - 交运   :3882-3895 五行交运规则（水命冬至前三天亥时）；
            :3916-3922 书例 2005 生 3 虚岁起运 → 交运年 = 2005+3-1 = 2007
"""
from mangpai.objective.bazi_calc import (
    calc_bazi_full,
    compute_four_pillars,
    day_gz,
)
from mangpai.objective.jiaoyun import compute_jiaoyun_timeline

LON = 116.4  # 北京


# ── 起运岁 ─────────────────────────────────────────────────────

def test_qiyun_book_example_2005():
    """书例（:3916-3922）：2005-3-15 巳时男，整日差 10，余一舍 → 3 虚岁。"""
    dy = calc_bazi_full(2005, 3, 15, 10, 0, '男', LON)['da_yun']
    assert dy['days'] == 10, dy['days']
    assert dy['start_age'] == 3, dy['start_age']
    steps = [(d['gz'], d['start_age'], d['end_age']) for d in dy['dayun'][:3]]
    assert steps == [('戊寅', 3, 13), ('丁丑', 13, 23), ('丙子', 23, 33)], steps


def test_qiyun_yu_er_jin_yi():
    """余二进一（:3854-3856）：顺排距下节整日差 11 天 → 11/3 余二进一 = 4 虚岁。"""
    # 2025 乙巳阴年女顺排；2025-5-25 → 下一节芒种 2025-6-5，整日差 11
    dy = calc_bazi_full(2025, 5, 25, 12, 0, '女', LON)['da_yun']
    assert dy['days'] == 11, dy['days']
    assert dy['start_age'] == 4, dy['start_age']


def test_qiyun_less_than_one_day_is_one():
    """不足一天也以一岁起运（:3864-3873）：当日交节 → 1 虚岁。"""
    # 2025 立春 2-3 约 22:10；2-3 23:30 阴年男逆排，距立春不足一天
    dy = calc_bazi_full(2025, 2, 3, 23, 30, '男', LON)['da_yun']
    assert dy['days'] == 0, dy['days']
    assert dy['start_age'] == 1, dy['start_age']


# ── 晚子时（理象学 :3703-3716 书例） ─────────────────────────────

def test_late_zi_same_day_book():
    """子正换日（书例口径）：2010-12-9 晚 23:30 → 日柱癸巳 + 时柱甲子（推转一轮）。"""
    fp = compute_four_pillars(2010, 12, 9, 23, 30, LON, late_zi_method='same_day')
    assert fp['day_gz'] == '癸巳', fp
    assert fp['hour_gz'] == '甲子', fp


def test_late_zi_next_day_book():
    """子初换日：日柱归次日甲午，时柱同为次日干起子时甲子。"""
    fp = compute_four_pillars(2010, 12, 9, 23, 30, LON, late_zi_method='next_day')
    assert fp['day_gz'] == '甲午', fp
    assert fp['hour_gz'] == '甲子', fp


def test_early_zi_both_modes_unchanged():
    """早子时 0:30 书例（:3709-3712）：两模式皆 癸巳日 壬子时。"""
    for m in ('same_day', 'next_day'):
        fp = compute_four_pillars(2010, 12, 9, 0, 30, LON, late_zi_method=m)
        assert fp['day_gz'] == '癸巳', (m, fp)
        assert fp['hour_gz'] == '壬子', (m, fp)


def test_late_zi_jiazi_day_tui_zhuan():
    """书定义例（:3705-3709）：甲子日晚子时 → 丙子时（甲己还加甲推转一轮）。"""
    from datetime import date, timedelta
    d = date(2010, 12, 1)
    while day_gz(d.year, d.month, d.day) != '甲子':
        d += timedelta(days=1)
    fp = compute_four_pillars(d.year, d.month, d.day, 23, 30, LON,
                              late_zi_method='same_day')
    assert fp['day_gz'] == '甲子', fp
    assert fp['hour_gz'] == '丙子', fp


# ── 交运时间（理象学 :3882-3922 书例） ──────────────────────────

def test_jiaoyun_book_2005_xu_sui():
    """2005 生 3 虚岁起运，乙酉水命 → 交运 2007 冬至前三天亥时（非 2008）。"""
    r = calc_bazi_full(2005, 3, 15, 10, 0, '男', LON)
    tl = compute_jiaoyun_timeline(
        2005, dayun_list=r['da_yun']['dayun'],
        start_age=r['da_yun']['start_age'])
    first = tl[0]
    assert first['jiaoyun_age'] == 3, first
    assert first['jiaoyun_year'] == 2007, first
    assert first['rule'] == '冬至前三天亥时'
    # 2007 冬至 12-22，前三天 = 12-19，亥时中点 22:00
    assert first['jiaoyun_iso'].startswith('2007-12-19T22:00'), first['jiaoyun_iso']
    # 支交运点：8 虚岁 → 2012 年
    assert tl[1]['jiaoyun_age'] == 8 and tl[1]['jiaoyun_year'] == 2012, tl[1]
