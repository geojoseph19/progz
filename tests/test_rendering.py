"""Tests for render_frame output correctness."""

import pytest

from progz.renderer import render_frame
from progz.styles import ASCII, SHIMMER, Style


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
        style = Style(show_spinner=True)
        out = _render(5, 10, style=style, use_color=True)
        # Spinner is one of the braille frames
        assert any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))

    def test_no_spinner_when_disabled(self):
        out = _render(5, 10, style=ASCII, use_color=True)
        assert not any(ch in out for ch in ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"))


class TestDeterminism:
    def test_same_inputs_same_output(self):
        args = dict(completed=5, total=10, elapsed=1.0, description="x", style=SHIMMER, use_color=True)
        assert render_frame(**args) == render_frame(**args)

    def test_different_elapsed_different_shimmer(self):
        a = _render(5, 10, elapsed=0.0, style=SHIMMER, use_color=True)
        b = _render(5, 10, elapsed=0.5, style=SHIMMER, use_color=True)
        # Different elapsed → different shimmer phase → different ANSI codes
        assert a != b
