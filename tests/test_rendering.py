"""Tests for render_frame output correctness."""

import pytest

from progz.renderer import render_frame
from progz.styles import ASCII, SHIMMER, Component, Style


def _render(completed, total, elapsed=0.0, description="", style=None, use_color=False):
    return render_frame(
        completed=completed,
        total=total,
        elapsed=elapsed,
        description=description,
        style=style or ASCII,
        use_color=use_color,
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

    def test_zero_total_empty(self):
        out = _render(0, 0)
        assert out == "-" * ASCII.bar_width

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


class TestDeterminism:
    def test_same_inputs_same_output(self):
        args = dict(completed=5, total=10, elapsed=1.0, description="x", style=SHIMMER, use_color=True)
        assert render_frame(**args) == render_frame(**args)

    def test_different_elapsed_different_shimmer(self):
        a = _render(5, 10, elapsed=0.0, style=SHIMMER, use_color=True)
        b = _render(5, 10, elapsed=0.5, style=SHIMMER, use_color=True)
        assert a != b
