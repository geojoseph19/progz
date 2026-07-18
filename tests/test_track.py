"""Tests for the track() iteration wrapper."""

import io

import pytest

from progz import ASCII, Component, Style, track


@pytest.fixture(autouse=True)
def _no_forced_color(monkeypatch):
    monkeypatch.delenv("FORCE_COLOR", raising=False)


def _out(**kwargs) -> io.StringIO:
    f = io.StringIO()
    kwargs.setdefault("style", ASCII)
    kwargs.setdefault("file", f)
    return f, kwargs


class TestTrack:
    def test_yields_items_in_order(self):
        f, kwargs = _out()
        assert list(track([1, 2, 3], **kwargs)) == [1, 2, 3]

    def test_total_inferred_from_len(self):
        f, kwargs = _out(refresh_rate=0)
        list(track([1, 2, 3, 4], **kwargs))
        # bar completed: last frame is a full bar plus newline
        last = f.getvalue().rstrip("\n").rsplit("\r", 1)[-1]
        assert last.startswith("#" * ASCII.bar_width)
        assert f.getvalue().endswith("\n")

    def test_explicit_total_wins(self):
        f, kwargs = _out(refresh_rate=0, style=Style(layout=(Component.COUNT,)))
        list(track(iter([1, 2]), total=2, **kwargs))
        assert "2/2" in f.getvalue()

    def test_generator_without_len_is_indeterminate(self):
        f, kwargs = _out(refresh_rate=0, style=Style(layout=(Component.COUNT,)))
        list(track((x for x in range(3)), **kwargs))
        out = f.getvalue()
        assert "3" in out
        assert "/" not in out

    def test_empty_iterable_finishes(self):
        f, kwargs = _out(refresh_rate=0)
        assert list(track([], **kwargs)) == []
        last = f.getvalue().rstrip("\n").rsplit("\r", 1)[-1]
        assert last.startswith("#" * ASCII.bar_width)

    def test_lazy_no_output_until_iterated(self):
        f, kwargs = _out()
        track([1, 2, 3], **kwargs)
        assert f.getvalue() == ""

    def test_exception_does_not_force_completion(self):
        f, kwargs = _out(refresh_rate=0)

        def run():
            for item in track([1, 2, 3, 4, 5], **kwargs):
                if item == 3:
                    raise RuntimeError("boom")

        with pytest.raises(RuntimeError):
            run()
        out = f.getvalue()
        assert out.endswith("\n")
        last = out.rstrip("\n").rsplit("\r", 1)[-1]
        assert "#" * ASCII.bar_width not in last

    def test_early_break_leaves_partial_bar(self):
        f, kwargs = _out(refresh_rate=0)
        for item in track([1, 2, 3, 4, 5], **kwargs):
            if item == 2:
                break
        out = f.getvalue()
        assert out.endswith("\n")
        last = out.rstrip("\n").rsplit("\r", 1)[-1]
        assert "#" * ASCII.bar_width not in last

    def test_description_passed_through(self):
        f, kwargs = _out(refresh_rate=0)
        list(track([1], description="working", **kwargs))
        assert "working" in f.getvalue()
