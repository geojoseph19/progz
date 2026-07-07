"""Tests for Style dataclass and pre-defined styles."""

import pytest

from progz.styles import ASCII, SHIMMER, Style


class TestStyleDefaults:
    def test_shimmer_defaults(self):
        s = Style()
        assert s.bar_width == 24
        assert s.speed == 0.6
        assert s.filled_char == "━"
        assert s.empty_char == "─"
        assert s.min_brightness == 80
        assert s.brightness_range == 175
        assert s.show_spinner is True

    def test_ascii_preset_chars(self):
        assert ASCII.filled_char == "#"
        assert ASCII.empty_char == "-"
        assert ASCII.show_spinner is False

    def test_shimmer_preset_chars(self):
        assert SHIMMER.filled_char == "━"
        assert SHIMMER.empty_char == "─"
        assert SHIMMER.show_spinner is True


class TestStyleCustomization:
    def test_custom_bar_width(self):
        s = Style(bar_width=40)
        assert s.bar_width == 40

    def test_custom_speed(self):
        s = Style(speed=1.5)
        assert s.speed == 1.5

    def test_custom_chars(self):
        s = Style(filled_char="█", empty_char="░")
        assert s.filled_char == "█"
        assert s.empty_char == "░"

    def test_custom_empty_rgb(self):
        s = Style(empty_rgb=(10, 20, 30))
        assert s.empty_rgb == (10, 20, 30)

    def test_custom_spinner_frames(self):
        frames = ("-", "\\", "|", "/")
        s = Style(spinner_frames=frames)
        assert s.spinner_frames == frames

    def test_styles_are_independent(self):
        s1 = Style(bar_width=10)
        s2 = Style(bar_width=20)
        assert s1.bar_width != s2.bar_width


class TestStylePresets:
    def test_shimmer_is_style_instance(self):
        assert isinstance(SHIMMER, Style)

    def test_ascii_is_style_instance(self):
        assert isinstance(ASCII, Style)

    def test_presets_are_distinct(self):
        assert SHIMMER is not ASCII
        assert SHIMMER.filled_char != ASCII.filled_char
