"""Tests for render_frame output correctness."""

import re

import pytest

from progz.renderer import render_frame, truncate_visible
from progz.styles import ASCII, SHIMMER, Component, Style
from progz.terminal import RESET


def _render(completed, total, elapsed=0.0, description="", style=None, use_color=False, rate=None):
    return render_frame(
        completed=completed,
        total=total,
        elapsed=elapsed,
        description=description,
        style=style or ASCII,
        use_color=use_color,
        rate=rate,
    )


class TestBarContent:
    def test_empty_bar(self):
        out = _render(0, 10)
        assert out == "-" * ASCII.bar_width

    def test_full_bar(self):
        out = _render(10, 10)
        assert out == "#" * ASCII.bar_width

    def test_half_bar(self):
        out = _render(5, 10)
        half = ASCII.bar_width // 2
        assert out.startswith("#" * half)
        assert out.endswith("-" * (ASCII.bar_width - half))

    def test_zero_total_renders_complete(self):
        out = _render(0, 0)
        assert out == "#" * ASCII.bar_width

    def test_completed_exceeds_total_full(self):
        out = _render(999, 10)
        assert out == "#" * ASCII.bar_width

    def test_description_appended(self):
        out = _render(0, 10, description="hello")
        assert out.endswith(" hello")

    def test_no_description_no_trailing_space(self):
        out = _render(0, 10, description="")
        assert not out.endswith(" ")

    def test_bar_length_equals_bar_width(self):
        out = _render(3, 10)
        assert len(out) == ASCII.bar_width


class TestUnicodeShimmer:
    def test_shimmer_filled_char(self):
        out = _render(10, 10, style=SHIMMER, use_color=False)
        assert "━" in out

    def test_shimmer_empty_char(self):
        out = _render(0, 10, style=SHIMMER, use_color=False)
        assert "─" in out

    def test_shimmer_mixed(self):
        out = _render(5, 10, style=SHIMMER, use_color=False)
        assert "━" in out
        assert "─" in out


class TestColorOutput:
    def test_color_output_contains_ansi(self):
        out = _render(5, 10, style=SHIMMER, use_color=True)
        assert "\033[" in out

    def test_no_color_output_clean(self):
        out = _render(5, 10, style=ASCII, use_color=False)
        assert "\033[" not in out

    def test_color_resets_at_end(self):
        out = _render(5, 10, style=SHIMMER, use_color=True)
        assert "\033[0m" in out

    def test_color_spinner_present(self):
        out = _render(5, 10, style=SHIMMER, use_color=True)
        assert any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))

    def test_no_spinner_when_not_in_layout(self):
        out = _render(5, 10, style=ASCII, use_color=True)
        assert not any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))

    def test_no_spinner_without_color(self):
        out = _render(5, 10, style=SHIMMER, use_color=False)
        assert not any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))


class TestFillText:
    def test_full_text_shown_at_zero_progress(self):
        style = Style(layout=(Component.TEXT,), fill_text="Loading")
        out = _render(0, 10, style=style)
        assert out == "Loading"

    def test_full_text_shown_at_full_progress(self):
        style = Style(layout=(Component.TEXT,), fill_text="Loading")
        out = _render(10, 10, style=style)
        assert out == "Loading"

    def test_text_mode_no_empty_chars(self):
        style = Style(layout=(Component.TEXT,), fill_text="Hi")
        out = _render(0, 10, style=style)
        assert style.empty_char not in out

    def test_text_mode_color_has_ansi(self):
        style = Style(layout=(Component.TEXT,), fill_text="Loading")
        out = _render(5, 10, style=style, use_color=True)
        assert "\033[" in out

    def test_text_mode_shimmer_varies_with_elapsed(self):
        style = Style(layout=(Component.TEXT,), fill_text="Loading")
        a = _render(5, 10, elapsed=0.0, style=style, use_color=True)
        b = _render(5, 10, elapsed=0.5, style=style, use_color=True)
        assert a != b

    def test_empty_fill_text_renders_nothing(self):
        style = Style(layout=(Component.TEXT,), fill_text="")
        out = _render(5, 10, style=style)
        assert out == ""

    def test_text_after_bar_has_leading_space(self):
        style = Style(layout=(Component.BAR, Component.TEXT), fill_text="Hi")
        out = _render(5, 10, style=style)
        assert out.endswith(" Hi")

    def test_text_then_description_resets(self):
        # TEXT sets a pending color reset; DESCRIPTION must emit it so the
        # label renders unstyled.
        style = Style(layout=(Component.TEXT, Component.DESCRIPTION), fill_text="Load")
        out = _render(5, 10, description="done", style=style, use_color=True)
        assert out.rfind("done") > out.rfind("\033[0m")


class TestPercent:
    def test_percent_at_zero(self):
        style = Style(layout=(Component.BAR, Component.PERCENT))
        out = _render(0, 10, style=style)
        assert out.endswith("  0%")

    def test_percent_at_half(self):
        style = Style(layout=(Component.BAR, Component.PERCENT))
        out = _render(5, 10, style=style)
        assert out.endswith(" 50%")

    def test_percent_at_full(self):
        style = Style(layout=(Component.BAR, Component.PERCENT))
        out = _render(10, 10, style=style)
        assert out.endswith("100%")

    def test_percent_standalone(self):
        style = Style(layout=(Component.PERCENT,))
        out = _render(3, 10, style=style)
        assert out == " 30%"

    def test_percent_not_colored_after_bar(self):
        # PERCENT after a colored BAR must reset first, else digits inherit
        # the bar's (dark) empty-zone color and are barely visible.
        style = Style(layout=(Component.BAR, Component.PERCENT))
        out = _render(5, 10, style=style, use_color=True)
        after = out[out.rfind("\033[0m") + len("\033[0m") :]
        assert "50%" in after
        assert "\033[38;2;" not in after


class TestLayout:
    def test_reversed_order_spinner_after_bar(self):
        style = Style(
            layout=(Component.BAR, Component.SPINNER, Component.DESCRIPTION),
            filled_char="#",
            empty_char="-",
        )
        out = _render(0, 10, description="x", style=style, use_color=True)
        bar_end = out.index("-" * 5)
        braille_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        spinner_pos = next(
            (out.index(ch) for ch in braille_chars if ch in out), -1
        )
        assert spinner_pos > bar_end

    def test_description_not_ansi_colored(self):
        style = Style(layout=(Component.BAR, Component.DESCRIPTION))
        out = _render(5, 10, description="label", style=style, use_color=True)
        reset_pos = out.rfind("\033[0m")
        label_pos = out.rfind("label")
        assert label_pos > reset_pos

    def test_no_description_component_hides_description(self):
        style = Style(layout=(Component.BAR,))
        out = _render(5, 10, description="hidden", style=style)
        assert "hidden" not in out

    def test_spinner_skipped_without_color(self):
        style = Style(layout=(Component.SPINNER, Component.BAR))
        out = _render(5, 10, style=style, use_color=False)
        assert not any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))
        assert "━" in out or "─" in out


def _flat_style(**kwargs):
    # min_brightness=255, brightness_range=0 pins the shimmer scale at 255,
    # so filled cells carry the stop color exactly.
    return Style(
        layout=(Component.BAR,),
        min_brightness=255,
        brightness_range=0,
        **kwargs,
    )


class TestColorStops:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)

    def test_state_mode_uses_current_progress_color(self):
        style = _flat_style(color_stops=((0.0, self.RED), (0.5, self.GREEN)))
        low = _render(2, 10, style=style, use_color=True)
        high = _render(8, 10, style=style, use_color=True)
        assert "\033[38;2;255;0;0m" in low
        assert "\033[38;2;0;255;0m" not in low
        assert "\033[38;2;0;255;0m" in high
        assert "\033[38;2;255;0;0m" not in high

    def test_stop_boundary_inclusive(self):
        style = _flat_style(color_stops=((0.0, self.RED), (0.5, self.GREEN)))
        out = _render(5, 10, style=style, use_color=True)
        assert "\033[38;2;0;255;0m" in out

    def test_position_mode_full_bar_shows_all_stop_colors(self):
        style = _flat_style(
            color_stops=((0.0, self.RED), (0.5, (0, 0, 255)), (1.0, self.GREEN)),
            color_by_position=True,
        )
        out = _render(10, 10, style=style, use_color=True)
        assert "\033[38;2;255;0;0m" in out
        assert "\033[38;2;0;0;255m" in out
        assert "\033[38;2;0;255;0m" in out

    def test_position_mode_partial_bar_lacks_final_color(self):
        style = _flat_style(
            color_stops=((0.0, self.RED), (1.0, self.GREEN)),
            color_by_position=True,
        )
        out = _render(3, 10, style=style, use_color=True)
        assert "\033[38;2;255;0;0m" in out
        assert "\033[38;2;0;255;0m" not in out

    def test_interpolate_midpoint(self):
        style = _flat_style(
            bar_width=3,
            color_stops=((0.0, (0, 0, 0)), (1.0, (200, 100, 50))),
            interpolate=True,
            color_by_position=True,
        )
        out = _render(3, 3, style=style, use_color=True)
        assert "\033[38;2;0;0;0m" in out
        assert "\033[38;2;100;50;25m" in out
        assert "\033[38;2;200;100;50m" in out

    def test_discrete_holds_last_stop_color(self):
        style = _flat_style(color_stops=((0.0, self.RED), (0.5, self.GREEN)))
        out = _render(10, 10, style=style, use_color=True)
        assert "\033[38;2;0;255;0m" in out

    def test_default_stops_render_greyscale(self):
        out = _render(10, 10, style=SHIMMER, use_color=True)
        for chunk in out.split("\033[38;2;")[1:]:
            r, g, b = chunk.split("m", 1)[0].split(";")
            if chunk.split("m", 1)[1].startswith(SHIMMER.filled_char):
                assert r == g == b

    def test_no_color_ignores_stops(self):
        style = _flat_style(color_stops=((0.0, self.RED),))
        out = _render(5, 10, style=style, use_color=False)
        assert "\033[" not in out


class TestCount:
    def test_count(self):
        style = Style(layout=(Component.COUNT,))
        assert _render(5, 10, style=style) == "5/10"

    def test_count_indeterminate(self):
        style = Style(layout=(Component.COUNT,))
        assert _render(1234, None, style=style) == "1234"

    def test_count_after_bar_separated(self):
        style = Style(layout=(Component.BAR, Component.COUNT), filled_char="#", empty_char="-")
        out = _render(5, 10, style=style)
        assert out.endswith(" 5/10")


class TestElapsed:
    def test_elapsed_minutes_seconds(self):
        style = Style(layout=(Component.ELAPSED,))
        assert _render(0, 10, elapsed=83.0, style=style) == "01:23"

    def test_elapsed_hours(self):
        style = Style(layout=(Component.ELAPSED,))
        assert _render(0, 10, elapsed=3661.0, style=style) == "1:01:01"


class TestRate:
    def test_rate_unknown(self):
        style = Style(layout=(Component.RATE,))
        assert _render(0, 10, style=style) == "-- it/s"

    def test_rate_small(self):
        style = Style(layout=(Component.RATE,))
        assert _render(0, 10, style=style, rate=2.5) == "2.5 it/s"

    def test_rate_kilo(self):
        style = Style(layout=(Component.RATE,))
        assert _render(0, 10, style=style, rate=1234.0) == "1.2k it/s"

    def test_rate_not_colored_after_bar(self):
        style = Style(layout=(Component.BAR, Component.RATE))
        out = _render(5, 10, style=style, use_color=True, rate=10.0)
        after = out[out.rfind(RESET) + len(RESET) :]
        assert "10.0 it/s" in after
        assert "\033[38;2;" not in after


class TestEta:
    def test_eta(self):
        style = Style(layout=(Component.ETA,))
        assert _render(5, 10, style=style, rate=5.0) == "~00:01"

    def test_eta_no_rate(self):
        style = Style(layout=(Component.ETA,))
        assert _render(5, 10, style=style) == "~--:--"

    def test_eta_zero_rate(self):
        style = Style(layout=(Component.ETA,))
        assert _render(5, 10, style=style, rate=0.0) == "~--:--"

    def test_eta_indeterminate(self):
        style = Style(layout=(Component.ETA,))
        assert _render(5, None, style=style, rate=5.0) == "~--:--"

    def test_eta_at_completion_zero(self):
        style = Style(layout=(Component.ETA,))
        assert _render(10, 10, style=style, rate=5.0) == "~00:00"


class TestIndeterminateBar:
    def test_width_constant(self):
        out = _render(0, None, style=ASCII)
        assert len(out) == ASCII.bar_width

    def test_segment_at_start(self):
        out = _render(0, None, elapsed=0.0, style=ASCII)
        seg = max(1, ASCII.bar_width // 4)
        assert out.startswith("#" * seg)
        assert out.endswith("-" * (ASCII.bar_width - seg))

    def test_segment_moves_with_elapsed(self):
        a = _render(0, None, elapsed=0.0, style=ASCII)
        b = _render(0, None, elapsed=0.5, style=ASCII)
        assert a != b

    def test_percent_shows_dashes(self):
        style = Style(layout=(Component.PERCENT,))
        assert _render(5, None, style=style) == " --%"

    def test_color_resets(self):
        style = Style(layout=(Component.BAR,))
        out = _render(0, None, elapsed=0.3, style=style, use_color=True)
        assert out.endswith(RESET)

    def test_no_color_clean(self):
        out = _render(0, None, elapsed=0.3, style=ASCII)
        assert "\033[" not in out


_EIGHTHS = ("▏", "▎", "▍", "▌", "▋", "▊", "▉")


def _blocks_style(width=8):
    return Style(
        layout=(Component.BAR,),
        bar_width=width,
        filled_char="█",
        empty_char="─",
        block_chars=_EIGHTHS,
    )


class TestBlockChars:
    def test_half_cell(self):
        # ratio 12/64 over width 8 = 1.5 cells: one full, one half
        out = _render(12, 64, style=_blocks_style())
        assert out == "█▌──────"

    def test_full_bar_no_partial(self):
        out = _render(64, 64, style=_blocks_style())
        assert out == "█" * 8

    def test_empty_bar_no_partial(self):
        out = _render(0, 64, style=_blocks_style())
        assert out == "─" * 8

    def test_width_constant_across_progress(self):
        style = _blocks_style()
        for completed in range(65):
            assert len(_render(completed, 64, style=style)) == 8

    def test_thinnest_glyph(self):
        # ratio 1/64 over width 8 = 0.125 cells -> eighth glyph
        out = _render(1, 64, style=_blocks_style())
        assert out == "▏───────"

    def test_color_partial_cell_colored(self):
        out = _render(12, 64, style=_blocks_style(), use_color=True)
        assert "▌" in out
        assert out.index("\033[38;2;") < out.index("▌")


class TestTruncateVisible:
    def test_plain_short_unchanged(self):
        assert truncate_visible("abc", 10) == "abc"

    def test_plain_exact_unchanged(self):
        assert truncate_visible("abc", 3) == "abc"

    def test_plain_cut(self):
        assert truncate_visible("abcdef", 3) == "abc"

    def test_zero_width(self):
        assert truncate_visible("abc", 0) == ""

    def test_ansi_zero_width(self):
        line = "\033[38;2;1;2;3ma\033[0mb"
        assert truncate_visible(line, 2) == line

    def test_ansi_cut_appends_reset(self):
        line = "\033[38;2;1;2;3mabcdef" + RESET
        out = truncate_visible(line, 3)
        assert out.endswith(RESET)
        assert "abc" in out
        assert "abcd" not in out

    def test_unterminated_escape_dropped(self):
        out = truncate_visible("ab\033[38;2;1", 10)
        assert out == "ab" + RESET

    def test_indeterminate_zero_width_bar_empty(self):
        style = Style(layout=(Component.BAR,), bar_width=0)
        assert _render(0, None, style=style) == ""

    def test_cut_colored_frame_visible_width(self):
        frame = render_frame(5, 10, 0.0, "description", SHIMMER, True)
        out = truncate_visible(frame, 10)
        assert len(re.sub(r"\033\[[0-9;]*m", "", out)) == 10
        assert out.endswith(RESET)


class TestDeterminism:
    def test_same_inputs_same_output(self):
        args = dict(completed=5, total=10, elapsed=1.0, description="x", style=SHIMMER, use_color=True)
        assert render_frame(**args) == render_frame(**args)

    def test_different_elapsed_different_shimmer(self):
        a = _render(5, 10, elapsed=0.0, style=SHIMMER, use_color=True)
        b = _render(5, 10, elapsed=0.5, style=SHIMMER, use_color=True)
        assert a != b
