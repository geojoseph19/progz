"""Tests for ProgressBar public API."""

import io
import os
import time

import pytest

from progz import Component, ProgressBar, Style
from progz.presets import ASCII, SHIMMER
from progz.terminal import ERASE_LINE


def _bar(total: int | None = 10, **kwargs) -> tuple[ProgressBar, io.StringIO]:
    f = io.StringIO()
    bar = ProgressBar(total=total, file=f, **kwargs)
    bar._use_color = False
    return bar, f


class _FakeClock:
    def __init__(self, t: float = 1000.0):
        self.t = t

    def advance(self, dt: float) -> None:
        self.t += dt

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def clock(monkeypatch):
    fake = _FakeClock()
    monkeypatch.setattr(time, "monotonic", fake)
    return fake


class _FakeTty(io.StringIO):
    def isatty(self) -> bool:
        return True


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


class TestThrottle:
    def test_updates_within_interval_draw_once(self, clock):
        bar, f = _bar(total=100, refresh_rate=30)
        bar.update()
        bar.update()
        bar.update()
        assert f.getvalue().count("\r") == 1
        assert bar.completed == 3

    def test_draws_again_after_interval(self, clock):
        bar, f = _bar(total=100, refresh_rate=30)
        bar.update()
        clock.advance(0.1)
        bar.update()
        assert f.getvalue().count("\r") == 2

    def test_refresh_rate_zero_draws_every_update(self, clock):
        bar, f = _bar(total=100, refresh_rate=0)
        bar.update()
        bar.update()
        bar.update()
        assert f.getvalue().count("\r") == 3

    def test_finish_draws_despite_throttle(self, clock):
        bar, f = _bar(total=100, refresh_rate=30)
        bar.update()
        bar.finish()
        assert f.getvalue().count("\r") == 2

    def test_deferred_state_shown_at_next_boundary(self, clock):
        bar, f = _bar(total=100, style=ASCII, refresh_rate=30)
        bar.update()
        bar.update(1, description="deferred")
        assert "deferred" not in f.getvalue()
        clock.advance(0.1)
        bar.update()
        assert "deferred" in f.getvalue()


class TestRate:
    def test_rate_none_before_first_draw_interval(self, clock):
        bar, _ = _bar(total=100)
        assert bar._rate is None

    def test_rate_sampled_at_draw(self, clock):
        bar, _ = _bar(total=1000, refresh_rate=10)
        clock.advance(1.0)
        bar.update(50)
        assert bar._rate == pytest.approx(50.0)

    def test_rate_smooths_toward_new_value(self, clock):
        bar, _ = _bar(total=100000, refresh_rate=10)
        clock.advance(1.0)
        bar.update(50)
        clock.advance(1.0)
        bar.update(150)
        assert bar._rate is not None
        assert 50.0 < bar._rate < 150.0

    def test_rate_rendered_in_output(self, clock):
        style = Style(layout=(Component.RATE, Component.ETA))
        bar, f = _bar(total=1000, style=style, refresh_rate=10)
        clock.advance(1.0)
        bar.update(100)
        out = f.getvalue()
        assert "it/s" in out
        assert "~" in out


class TestIndeterminate:
    def test_total_none(self):
        bar, _ = _bar(total=None)
        assert bar.total is None

    def test_update_never_autofinishes(self):
        bar, _ = _bar(total=None)
        bar.update(10**9)
        assert not bar._finished
        assert bar.completed == 10**9

    def test_finish_keeps_completed(self):
        bar, _ = _bar(total=None)
        bar.update(7)
        bar.finish()
        assert bar.completed == 7
        assert bar._finished

    def test_draws_bouncing_bar(self):
        bar, f = _bar(total=None, style=ASCII)
        bar.update()
        out = f.getvalue()
        assert "#" in out
        assert "-" in out

    def test_context_manager(self):
        f = io.StringIO()
        with ProgressBar(total=None, file=f) as bar:
            bar._use_color = False
            bar.update(3)
        assert bar._finished
        assert f.getvalue().endswith("\n")


class TestWrite:
    def test_message_on_own_line_then_redraw(self):
        bar, f = _bar(style=ASCII, refresh_rate=0)
        bar.update(2)
        bar.write("hello")
        out = f.getvalue()
        assert "hello" in out
        line_after_msg = out.split("hello", 1)[1]
        assert line_after_msg.startswith(" " * (ASCII.bar_width - len("hello")) + "\n")
        assert "#" in line_after_msg  # bar redrawn below the message

    def test_color_path_erases_line(self):
        f = io.StringIO()
        bar = ProgressBar(total=10, file=f)
        bar._use_color = True
        bar.update()
        bar.write("msg")
        assert f"{ERASE_LINE}msg\n" in f.getvalue()

    def test_write_after_finish_message_only(self):
        bar, f = _bar(style=ASCII)
        bar.finish()
        before = f.getvalue()
        bar.write("done note")
        after = f.getvalue()[len(before) :]
        assert "done note" in after
        assert "#" not in after


class TestTransient:
    def test_finish_erases_no_newline(self):
        f = io.StringIO()
        bar = ProgressBar(total=10, file=f, transient=True)
        bar._use_color = True
        bar.update()
        bar.finish()
        assert f.getvalue().endswith(f"\r{ERASE_LINE}")
        assert not f.getvalue().endswith("\n")

    def test_finish_no_color_pads_with_spaces(self):
        bar, f = _bar(transient=True, style=ASCII, refresh_rate=0)
        bar.update()
        bar.finish()
        assert f.getvalue().endswith("\r" + " " * ASCII.bar_width + "\r")

    def test_abandon_erases(self):
        f = io.StringIO()
        try:
            with ProgressBar(total=10, file=f, transient=True) as bar:
                bar._use_color = True
                bar.update()
                raise ValueError("boom")
        except ValueError:
            pass
        assert f.getvalue().endswith(f"\r{ERASE_LINE}")


class TestWidthTruncation:
    def test_line_truncated_to_terminal_width(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "get_terminal_size", lambda: os.terminal_size((10, 24)))
        f = _FakeTty()
        bar = ProgressBar(total=10, file=f, style=ASCII, refresh_rate=0)
        bar._use_color = False
        bar.update(5, description="a very long description that would wrap")
        line = f.getvalue().rsplit("\r", 1)[-1]
        assert len(line) == 10

    def test_padding_capped_at_terminal_width(self, monkeypatch):
        import shutil

        monkeypatch.setattr(shutil, "get_terminal_size", lambda: os.terminal_size((30, 24)))
        f = _FakeTty()
        bar = ProgressBar(total=10, file=f, style=ASCII, refresh_rate=0)
        bar._use_color = False
        bar._last_visible_len = 1000
        bar.update()
        line = f.getvalue().rsplit("\r", 1)[-1]
        assert len(line) <= 30

    def test_non_tty_not_truncated(self):
        bar, f = _bar(total=10, style=ASCII, refresh_rate=0)
        bar.update(5, description="x" * 500)
        line = f.getvalue().rsplit("\r", 1)[-1]
        assert len(line) > 400


class TestModuleAttrs:
    def test_version_is_string(self):
        import progz

        assert isinstance(progz.__version__, str)

    def test_unknown_attribute_raises(self):
        import progz

        with pytest.raises(AttributeError):
            progz.nonexistent_attribute

    def test_exit_after_inner_finish_is_noop(self):
        f = io.StringIO()
        with ProgressBar(total=2, file=f) as bar:
            bar._use_color = False
            bar.update(2)  # reaches total; finish() runs here
            pos = len(f.getvalue())
        assert len(f.getvalue()) == pos


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
