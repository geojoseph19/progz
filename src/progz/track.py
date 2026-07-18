"""Iteration wrapper: a one-line progress bar over any iterable."""

from collections.abc import Iterable, Iterator, Sized
from typing import TextIO, TypeVar

from .progress import ProgressBar
from .styles import Style

T = TypeVar("T")


def track(
    iterable: Iterable[T],
    description: str = "",
    total: int | None = None,
    style: Style | None = None,
    file: TextIO | None = None,
    refresh_rate: float = 30.0,
    transient: bool = False,
) -> Iterator[T]:
    """Iterate while drawing a progress bar.

    Usage::

        from progz import track

        for item in track(items, description="Processing"):
            process(item)

    total is inferred via ``len()`` when the iterable supports it. Pass it
    explicitly for sized generators, or leave it None for indeterminate
    mode. The bar always reaches a final state: finished on completion,
    left at its current progress if the loop raises or stops early.

    Args match ``ProgressBar``; see its docstring for details.
    """
    if total is None and isinstance(iterable, Sized):
        total = len(iterable)
    with ProgressBar(
        total=total,
        description=description,
        style=style,
        file=file,
        refresh_rate=refresh_rate,
        transient=transient,
    ) as bar:
        for item in iterable:
            yield item
            bar.update()
