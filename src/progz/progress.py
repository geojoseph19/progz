"""ProgressBar class."""

import sys
import time
from typing import TextIO

from .renderer import render_frame
from .styles import ASCII, SHIMMER, Style
from .terminal import ERASE_LINE, supports_color


class ProgressBar:
    """Terminal progress bar with configurable styles.

    Usage (context manager, recommended)::

        with ProgressBar(total=100) as bar:
            for item in items:
                process(item)
                bar.update()

    Usage — manual::

        bar = ProgressBar(total=100)
        for item in items:
            process(item)
            bar.update()
        bar.finish()
    """

    def __init__(
        self,
        total: int,
        description: str = "",
        style: Style | None = None,
        file: TextIO | None = None,
    ) -> None:
        """Create a progress bar.

        Args:
            total:       Number of steps to completion.
            description: Text shown to the right of the bar.
            style:       Visual style; defaults to SHIMMER.
            file:        Output stream; defaults to sys.stderr.
        """
        self._total = max(0, total)
        self._completed = 0
        self._description = description
        self._style = style if style is not None else SHIMMER
        self._file: TextIO = file if file is not None else sys.stderr
        self._use_color = supports_color(self._file)
        self._start = time.monotonic()
        self._last_visible_len = 0
        self._finished = False

    @property
    def completed(self) -> int:
        """Number of completed steps."""
        return self._completed

    @property
    def total(self) -> int:
        """Total steps."""
        return self._total

    def update(self, n: int = 1, description: str | None = None) -> None:
        """Advance the bar by n steps and redraw.

        Args:
            n:           Steps to advance.
            description: Replace the current description text.
        """
        if self._finished:
            return
        self._completed = min(self._total, self._completed + n)
        if description is not None:
            self._description = description
        if self._completed >= self._total:
            self.finish()
        else:
            self._draw()

    def set_description(self, description: str) -> None:
        """Update description text without advancing progress."""
        self._description = description

    def finish(self) -> None:
        """Complete the bar and move to the next line."""
        if self._finished:
            return
        self._completed = self._total
        self._draw()
        self._file.write("\n")
        self._file.flush()
        self._finished = True

    def _draw(self) -> None:
        elapsed = time.monotonic() - self._start
        line = render_frame(
            self._completed,
            self._total,
            elapsed,
            self._description,
            self._style,
            self._use_color,
        )

        if self._use_color:
            # \r returns to column 0; \033[2K erases the line
            self._file.write(f"\r{ERASE_LINE}{line}")
        else:
            # No ANSI: overwrite manually using spaces
            self._file.write(f"\r{line}")
            visible_len = len(line)
            if visible_len < self._last_visible_len:
                self._file.write(" " * (self._last_visible_len - visible_len))
            self._last_visible_len = visible_len

        self._file.flush()

    def __enter__(self) -> "ProgressBar":
        return self

    def __exit__(self, *args: object) -> None:
        if not self._finished:
            self.finish()
