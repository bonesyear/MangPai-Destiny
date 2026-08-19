"""D2 入口批哨兵：calc_bazi_full 入口校验（T0 P1/P2）。

- 性别缺失/未知 → ValueError（大运方向依赖性别，静默逆排=语义错，
  飞书交互侧强制必填；阳男阴女顺排/阴男阳女逆排 理象学:3854+）
- 年份出节气表范围（1900-2100）→ ValueError（原裸 KeyError）
- city_lon 非数值/越界（[-180, 180]）→ ValueError（原 None 裸 TypeError）
"""
import math

import pytest

from mangpai.objective.bazi_calc import calc_bazi_full

LON = 116.4


class TestGenderRequired:
    @pytest.mark.parametrize('g', [None, '', '未知', 'unknown', '男 '])
    def test_missing_or_unknown_raises(self, g):
        with pytest.raises(ValueError, match='性别'):
            calc_bazi_full(1990, 6, 15, 10, 0, g, LON)

    @pytest.mark.parametrize('g', ['男', '女', 'male', 'female', '乾', '坤'])
    def test_valid_genders_accepted(self, g):
        r = calc_bazi_full(1990, 6, 15, 10, 0, g, LON)
        assert r['da_yun']['direction'] in ('顺', '逆')

    def test_qian_kun_match_hanzi(self):
        """乾/坤 与 男/女 同向（旧口径 乾 被静默当阴=逆排，属同型陷阱）。"""
        for a, b in [('乾', '男'), ('坤', '女')]:
            ra = calc_bazi_full(1990, 6, 15, 10, 0, a, LON)
            rb = calc_bazi_full(1990, 6, 15, 10, 0, b, LON)
            assert ra['da_yun']['direction'] == rb['da_yun']['direction']
            assert ra['da_yun']['dayun'] == rb['da_yun']['dayun']


class TestYearRange:
    @pytest.mark.parametrize('y', [1899, 2101, 0, -1, 9999])
    def test_out_of_range_raises(self, y):
        with pytest.raises(ValueError, match='1900'):
            calc_bazi_full(y, 6, 15, 10, 0, '男', LON)

    @pytest.mark.parametrize('y', [1900, 2100])
    def test_boundary_years_ok(self, y):
        r = calc_bazi_full(y, 6, 15, 10, 0, '男', LON)
        assert len(r['bazi']['full'].split()) == 4


class TestCityLon:
    @pytest.mark.parametrize('lon', [None, 'abc', 999.0, -999.0, 180.5,
                                     -180.5, math.nan, math.inf])
    def test_invalid_lon_raises(self, lon):
        with pytest.raises(ValueError, match='经度'):
            calc_bazi_full(1990, 6, 15, 10, 0, '男', lon)

    @pytest.mark.parametrize('lon', [73.5, 120.0, 135.0, -180.0, 180.0, 0])
    def test_valid_lon_ok(self, lon):
        r = calc_bazi_full(1990, 6, 15, 10, 0, '男', lon)
        assert r['input']['city_lon'] == lon
