"""Numeric readouts: PERCENT, COUNT, RATE, ETA, ELAPSED."""

import time

from progz import Component, ProgressBar, Style

style = Style(
    layout=(
        Component.SPINNER,
        Component.BAR,
        Component.PERCENT,
        Component.COUNT,
        Component.RATE,
        Component.ETA,
        Component.ELAPSED,
        Component.DESCRIPTION,
    )
)

with ProgressBar(total=200, style=style, description="crunching") as bar:
    for _ in range(200):
        time.sleep(0.02)
        bar.update()
