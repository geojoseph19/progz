"""ProgressBar class."""

import shutil
import sys
import time
from types import TracebackType
from typing import TextIO

from .presets import SHIMMER
from .renderer import render_frame, truncate_visible
from .styles import Style
from .terminal import ERASE_LINE, supports_color

_RATE_TAU = 1.0
"""EWMA time constant in seconds for the rate estimate."""


class ProgressBar:
    """Terminal progress bar with configurable styles.

    Usage (context manager, recommended)::

        with ProgressBar(total=100) as bar:
            for item in items:
                process(item)
                bar.update()

    Usage, manual::

        bar = ProgressBar(total=100)
        for item in items:
            process(item)
            bar.update()
        bar.finish()
    """

    def __init__(
        self,
        total: int | None,
        description: str = "",
        style: Style | None = None,
        file: TextIO | None = None,
        refresh_rate: float = 30.0,
        transient: bool = False,
    ) -> None:
        """Create a progress bar.

        Args:
            total: Number of steps to completion, or None for
                indeterminate mode (bouncing bar, plain count readouts,
                no auto-finish).
            description: Text shown to the right of the bar.
            style: Visual style; defaults to ``presets.SHIMMER``.
            file: Output stream; defaults to ``sys.stderr``.
            refresh_rate: Maximum redraws per second. Every update still
                counts; skipped frames are drawn at the next boundary, and
                ``finish()`` always draws the final frame. Zero or negative
                disables throttling (redraw on every update).
            transient: Erase the bar on finish instead of moving to the
                next line.
        """
        self._total = None if total is None else max(0, total)
        self._completed = 0
        self._description = description
        self._style = style if style is not None else SHIMMER
        self._file: TextIO = file if file is not None else sys.stderr
        self._use_color = supports_color(self._file)
        self._is_tty = hasattr(self._file, "isatty") and self._file.isatty()
        self._min_interval = 1.0 / refresh_rate if refresh_rate > 0 else 0.0
        self._transient = transient
        self._start = time.monotonic()
        self._last_draw = float("-inf")
        self._rate: float | None = None
        self._rate_ts = self._start
        self._rate_completed = 0
        self._last_visible_len = 0
        self._finished = False

    @property
    def completed(self) -> int:
        """Number of completed steps."""
        return self._completed

    @property
    def total(self) -> int | None:
        """Total steps; None in indeterminate mode."""
        return self._total

    def update(self, n: int = 1, description: str | None = None) -> None:
        """Advance the bar by n steps and redraw if due.

        Args:
            n: Steps to advance.
            description: Replace the current description text.
        """
        if self._finished:
            return
        if self._total is None:
            self._completed += n
        else:
            self._completed = min(self._total, self._completed + n)
        if description is not None:
            self._description = description
        if self._total is not None and self._completed >= self._total:
            self.finish()
            return
        now = time.monotonic()
        if now - self._last_draw >= self._min_interval:
            self._sample_rate(now)
            self._draw(now)

    def set_description(self, description: str) -> None:
        """Update description text without advancing progress."""
        self._description = description

    def write(self, message: str) -> None:
        """Print message on its own line above the live bar.

        Erases the bar line, writes the message plus a newline, then
        redraws the bar. Lets ``print()``-style output and logging coexist
        with an active bar.
        """
        if self._use_color:
            self._file.write(f"\r{ERASE_LINE}{message}\n")
        else:
            pad = self._last_visible_len - len(message)
            self._file.write("\r" + message + (" " * pad if pad > 0 else "") + "\n")
            self._last_visible_len = 0
        if self._finished:
            self._file.flush()
        else:
            self._draw(time.monotonic())

    def finish(self) -> None:
        """Complete the bar and move to the next line.

        With ``transient=True`` the bar line is erased instead. In
        indeterminate mode the count stays where it is.
        """
        if self._finished:
            return
        now = time.monotonic()
        if self._total is not None:
            self._completed = self._total
        self._sample_rate(now)
        if self._transient:
            self._erase()
        else:
            self._draw(now)
            self._file.write("\n")
            self._file.flush()
        self._finished = True

    def _sample_rate(self, now: float) -> None:
        """Fold steps since the last drawn frame into the EWMA rate."""
        dt = now - self._rate_ts
        if dt <= 0.0:
            return
        inst = (self._completed - self._rate_completed) / dt
        if self._rate is None:
            self._rate = inst
        else:
            self._rate += (inst - self._rate) * (dt / (dt + _RATE_TAU))
        self._rate_ts = now
        self._rate_completed = self._completed

    def _draw(self, now: float) -> None:
        line = render_frame(
            self._completed,
            self._total,
            now - self._start,
            self._description,
            self._style,
            self._use_color,
            self._rate,
        )

        # Re-checked at each drawn frame (the throttle boundary), so a
        # resized terminal is picked up without per-update cost.
        max_width = shutil.get_terminal_size().columns if self._is_tty else 0
        if max_width > 0:
            line = truncate_visible(line, max_width)

        if self._use_color:
            # \r returns to column 0; \033[2K erases the line
            self._file.write(f"\r{ERASE_LINE}{line}")
        else:
            # No ANSI: overwrite manually using spaces
            self._file.write(f"\r{line}")
            visible_len = len(line)
            pad = self._last_visible_len - visible_len
            if max_width > 0:
                pad = min(pad, max_width - visible_len)
            if pad > 0:
                self._file.write(" " * pad)
            self._last_visible_len = visible_len

        self._file.flush()
        self._last_draw = now

    def _erase(self) -> None:
        if self._use_color:
            self._file.write(f"\r{ERASE_LINE}")
        else:
            self._file.write("\r" + " " * self._last_visible_len + "\r")
        self._file.flush()

    def _abandon(self) -> None:
        """Stop drawing without forcing completion; move to the next line."""
        if self._finished:
            return
        if self._transient:
            self._erase()
        else:
            self._file.write("\n")
            self._file.flush()
        self._finished = True

    def __enter__(self) -> "ProgressBar":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        """Finish the bar on clean exit.

        If the block raised, the bar is left at its current progress
        instead of being forced to 100%, so failed runs do not display
        as complete.
        """
        if self._finished:
            return
        if exc_type is None:
            self.finish()
        else:
            self._abandon()
