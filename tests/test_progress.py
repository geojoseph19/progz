"""Tests for ProgressBar public API."""

import io

import pytest

from progz import ASCII, SHIMMER, ProgressBar, Style
from progz.terminal import ERASE_LINE


def _bar(total: int = 10, **kwargs) -> tuple[ProgressBar, io.StringIO]:
    f = io.StringIO()
    bar = ProgressBar(total=total, file=f, **kwargs)
    bar._use_color = False
    return bar, f


class TestInit:
    def test_defaults(self):
        bar, _ = _bar()
        assert bar.total == 10
        assert bar.completed == 0

    def test_negative_total_clamped(self):
        bar, _ = _bar(total=-5)
        assert bar.total == 0

    def test_zero_total(self):
        bar, f = _bar(total=0)
        bar.update()
        assert bar._finished

    def test_custom_style(self):
        bar, _ = _bar(style=ASCII)
        assert bar._style is ASCII


class TestUpdate:
    def test_single_step(self):
        bar, f = _bar()
        bar.update()
        assert bar.completed == 1
        output = f.getvalue()
        assert "━" in output  # SHIMMER is default; filled_char="━"

    def test_update_with_ascii_style(self):
        bar, f = _bar(style=ASCII)
        bar.update(5)
        output = f.getvalue()
        assert "#####" in output

    def test_update_advances_completed(self):
        bar, _ = _bar()
        bar.update(3)
        assert bar.completed == 3

    def test_update_clamps_to_total(self):
        bar, _ = _bar()
        bar.update(100)
        assert bar.completed == 10

    def test_update_description(self):
        bar, f = _bar()
        bar.update(1, description="hello")
        assert "hello" in f.getvalue()

    def test_update_after_finish_no_op(self):
        bar, f = _bar()
        bar.finish()
        pos = len(f.getvalue())
        bar.update(1)
        assert len(f.getvalue()) == pos  # no extra writes

    def test_multiple_updates_accumulate(self):
        bar, _ = _bar()
        bar.update(3)
        bar.update(3)
        assert bar.completed == 6

    def test_completes_at_total(self):
        bar, _ = _bar(total=3)
        bar.update()
        bar.update()
        bar.update()
        assert bar._finished


class TestFinish:
    def test_finish_writes_newline(self):
        bar, f = _bar()
        bar.finish()
        assert f.getvalue().endswith("\n")

    def test_finish_idempotent(self):
        bar, f = _bar()
        bar.finish()
        val1 = f.getvalue()
        bar.finish()
        assert f.getvalue() == val1

    def test_finish_sets_completed_to_total(self):
        bar, _ = _bar()
        bar.update(3)
        bar.finish()
        assert bar.completed == bar.total


class TestContextManager:
    def test_context_manager_calls_finish(self):
        f = io.StringIO()
        with ProgressBar(total=5, file=f) as bar:
            bar._use_color = False
            bar.update(3)
        assert bar._finished
        assert f.getvalue().endswith("\n")

    def test_context_manager_on_exception(self):
        f = io.StringIO()
        try:
            with ProgressBar(total=5, file=f) as bar:
                bar._use_color = False
                bar.update(2)
                raise ValueError("test error")
        except ValueError:
            pass
        assert bar._finished
        assert f.getvalue().endswith("\n")

    def test_exception_does_not_force_completion(self):
        f = io.StringIO()
        try:
            with ProgressBar(total=5, file=f) as bar:
                bar._use_color = False
                bar.update(2)
                raise ValueError("test error")
        except ValueError:
            pass
        assert bar.completed == 2
        # last drawn frame reflects 2/5 progress, not a full bar
        last_frame = f.getvalue().rstrip("\n").rsplit("\r", 1)[-1]
        assert "━" * SHIMMER.bar_width not in last_frame
        assert "─" in last_frame


class TestDraw:
    def test_color_path_uses_erase_line(self):
        f = io.StringIO()
        bar = ProgressBar(total=10, file=f)
        bar._use_color = True
        bar.update()
        assert ERASE_LINE in f.getvalue()

    def test_no_color_pads_when_line_shrinks(self):
        bar, f = _bar(total=10)
        bar._last_visible_len = 1000  # simulate long prior line
        bar.update()
        # rendered line is ~24 chars; gap to 1000 should be space-padded
        after_cr = f.getvalue().split("\r")[-1]
        assert len(after_cr) == 1000


class TestSetDescription:
    def test_set_description(self):
        bar, f = _bar()
        bar.set_description("step 1")
        bar.update(1)
        assert "step 1" in f.getvalue()

    def test_set_description_then_update_with_new(self):
        bar, f = _bar()
        bar.set_description("old")
        bar.update(1, description="new")
        assert "new" in f.getvalue()
