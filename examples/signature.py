"""Signature presets: the shimmer wave (SHIMMER) and the brand gradient (EMBER)."""

import time

from progz import ProgressBar, presets

for name, style in (
    ("EMBER", presets.EMBER),
    ("SHIMMER", presets.SHIMMER),
):
    with ProgressBar(total=160, style=style, description=name) as bar:
        for _ in range(160):
            time.sleep(0.02)
            bar.update()
