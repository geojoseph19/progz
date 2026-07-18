"""Tests for Style dataclass and pre-defined styles."""

import pytest

from progz.styles import ASCII, BLOCKS, MINIMAL, RAINBOW, SHIMMER, Component, Style


class TestStyleDefaults:
    def test_shimmer_defaults(self):
        s = Style()
        assert s.bar_width == 24
        assert s.speed == 0.6
        assert s.filled_char == "━"
        assert s.empty_char == "─"
        assert s.min_brightness == 80
        assert s.brightness_range == 175
        assert Component.SPINNER in s.layout

    def test_ascii_preset_chars(self):
        assert ASCII.filled_char == "#"
        assert ASCII.empty_char == "-"
        assert Component.SPINNER not in ASCII.layout

    def test_shimmer_preset_chars(self):
        assert SHIMMER.filled_char == "━"
        assert SHIMMER.empty_char == "─"
        assert Component.SPINNER in SHIMMER.layout


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


class TestColorStops:
    def test_default_single_white_stop(self):
        s = Style()
        assert s.color_stops == ((0.0, (255, 255, 255)),)
        assert s.interpolate is False
        assert s.color_by_position is False

    def test_custom_stops(self):
        stops = ((0.0, (220, 60, 60)), (0.5, (230, 200, 60)), (0.9, (80, 200, 120)))
        s = Style(color_stops=stops)
        assert s.color_stops == stops

    def test_empty_stops_rejected(self):
        with pytest.raises(ValueError, match="at least one stop"):
            Style(color_stops=())

    def test_threshold_above_one_rejected(self):
        with pytest.raises(ValueError, match="outside"):
            Style(color_stops=((1.5, (0, 0, 0)),))

    def test_threshold_below_zero_rejected(self):
        with pytest.raises(ValueError, match="outside"):
            Style(color_stops=((-0.1, (0, 0, 0)),))

    def test_unsorted_thresholds_rejected(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            Style(color_stops=((0.5, (0, 0, 0)), (0.2, (1, 1, 1))))

    def test_duplicate_thresholds_rejected(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            Style(color_stops=((0.5, (0, 0, 0)), (0.5, (1, 1, 1))))


class TestLayout:
    def test_default_layout_order(self):
        s = Style()
        assert s.layout == (Component.SPINNER, Component.BAR, Component.DESCRIPTION)

    def test_custom_layout_no_spinner(self):
        s = Style(layout=(Component.BAR, Component.DESCRIPTION))
        assert Component.SPINNER not in s.layout
        assert Component.BAR in s.layout

    def test_custom_layout_with_percent(self):
        s = Style(layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION))
        assert s.layout.index(Component.PERCENT) > s.layout.index(Component.BAR)

    def test_text_layout(self):
        s = Style(layout=(Component.TEXT, Component.DESCRIPTION), fill_text="Loading")
        assert Component.BAR not in s.layout
        assert Component.TEXT in s.layout
        assert s.fill_text == "Loading"

    def test_layout_immutable(self):
        s = Style()
        with pytest.raises(Exception):
            s.layout = (Component.BAR,)  # type: ignore[misc]

    def test_ascii_layout(self):
        assert ASCII.layout == (Component.BAR, Component.DESCRIPTION)

    def test_shimmer_layout(self):
        assert SHIMMER.layout == (Component.SPINNER, Component.BAR, Component.DESCRIPTION)


class TestStylePresets:
    def test_all_presets_are_style_instances(self):
        for preset in (SHIMMER, ASCII, BLOCKS, MINIMAL, RAINBOW):
            assert isinstance(preset, Style)

    def test_presets_are_distinct(self):
        assert SHIMMER is not ASCII
        assert SHIMMER.filled_char != ASCII.filled_char

    def test_blocks_has_eighth_glyphs(self):
        assert len(BLOCKS.block_chars) == 7
        assert BLOCKS.filled_char == "█"
        assert all(len(ch) == 1 for ch in BLOCKS.block_chars)

    def test_minimal_layout(self):
        assert MINIMAL.layout == (Component.BAR, Component.PERCENT)

    def test_rainbow_gradient_settings(self):
        assert RAINBOW.interpolate is True
        assert RAINBOW.color_by_position is True
        assert len(RAINBOW.color_stops) >= 5

    def test_block_chars_default_empty(self):
        assert Style().block_chars == ()
