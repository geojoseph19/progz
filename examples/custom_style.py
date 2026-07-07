"""Custom style example: wide bar, fast shimmer, block characters."""

import time

from progz import ProgressBar, Style

style = Style(
    bar_width=40,
    speed=1.5,
    filled_char="█",
    empty_char="░",
    min_brightness=100,
    brightness_range=155,
)

with ProgressBar(total=30, style=style, description="custom") as bar:
    for i in range(30):
        time.sleep(0.06)
        bar.update()
