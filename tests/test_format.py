"""Tests for pure formatting helpers."""

import math

from progz.format import format_duration, format_si


class TestFormatDuration:
    def test_zero(self):
        assert format_duration(0) == "00:00"

    def test_seconds_truncated(self):
        assert format_duration(59.9) == "00:59"

    def test_minutes(self):
        assert format_duration(83) == "01:23"

    def test_hours(self):
        assert format_duration(3661) == "1:01:01"

    def test_many_hours(self):
        assert format_duration(360000) == "100:00:00"

    def test_negative(self):
        assert format_duration(-1) == "--:--"

    def test_nan(self):
        assert format_duration(math.nan) == "--:--"

    def test_inf(self):
        assert format_duration(math.inf) == "--:--"


class TestFormatSi:
    def test_zero(self):
        assert format_si(0) == "0.0"

    def test_small(self):
        assert format_si(2.5) == "2.5"

    def test_below_thousand(self):
        assert format_si(999.94) == "999.9"

    def test_kilo(self):
        assert format_si(1234) == "1.2k"

    def test_mega(self):
        assert format_si(2.5e6) == "2.5M"

    def test_giga(self):
        assert format_si(3.2e9) == "3.2G"
