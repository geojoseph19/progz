"""Unknown totals: track() a plain generator, or pass total=None."""

import time

from progz import Component, Style, track


def stream():
    for i in range(200):
        time.sleep(0.03)
        yield i


style = Style(
    layout=(
        Component.SPINNER,
        Component.BAR,
        Component.COUNT,
        Component.ELAPSED,
        Component.DESCRIPTION,
    )
)

for _ in track(stream(), description="receiving", style=style):
    pass
