from datetime import datetime

import pytest

from mangpai.objective.bazi_calc import SOLAR_TERMS, SOLAR_TERM_YEAR_MIN, SOLAR_TERM_YEAR_MAX, _unpack
from mangpai.objective.jiaoyun import _jd_to_datetime


def _dates(year, values):
    return [datetime(year, *_unpack(value)) for value in values]


def test_solar_term_table_is_complete_and_increasing():
    for year, values in SOLAR_TERMS.items():
        assert len(values) == 24, year
        dates = _dates(year, values)
        assert len(set(dates)) == 24, year
    from mangpai.objective.bazi_calc import _JIE_DTS
    assert _JIE_DTS == sorted(_JIE_DTS)
    for left, right in zip(_JIE_DTS, _JIE_DTS[1:]):
        assert 28 <= (right - left).total_seconds() / 86400 <= 32, (left, right)


def test_solar_term_table_matches_sxtwl_minute_precision():
    pytest.importorskip('sxtwl')
    checked = 0
    for year in range(SOLAR_TERM_YEAR_MIN, SOLAR_TERM_YEAR_MAX + 1):
        import sxtwl
        actual = [_jd_to_datetime(item.jd)
                  for source_year in (year - 1, year)
                  for item in sxtwl.getJieQiByYear(source_year)]
        for expected in _dates(year, SOLAR_TERMS[year]):
            assert min(abs((candidate - expected).total_seconds())
                       for candidate in actual) <= 60, (year, expected)
            checked += 1
    assert checked == 4824


def test_layer1_require_all_fails_without_sxtwl(monkeypatch):
    import runpy
    import sys

    monkeypatch.setitem(sys.modules, 'sxtwl', None)
    monkeypatch.setattr(sys, 'argv', ['verify_layer1.py', '--require-all'])
    with pytest.raises(SystemExit) as exc:
        runpy.run_path('mangpai/verify_layer1.py', run_name='__main__')
    assert exc.value.code == 1


def test_jie_timeline_xiaohan_uses_source_year():
    from mangpai.objective.bazi_calc import _JIE_TIMELINE

    entry = next(item for item in _JIE_TIMELINE
                 if item[2] == '小寒' and item[0].year == 2026)
    assert entry[0] == datetime(2026, 1, 5, 16, 22)
