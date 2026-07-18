"""Built-in presets, one after another."""

import time

from progz import ASCII, BLOCKS, MINIMAL, RAINBOW, SHIMMER, ProgressBar

for name, style in (
    ("SHIMMER", SHIMMER),
    ("ASCII", ASCII),
    ("BLOCKS", BLOCKS),
    ("MINIMAL", MINIMAL),
    ("RAINBOW", RAINBOW),
):
    with ProgressBar(total=120, style=style, description=name) as bar:
        for _ in range(120):
            time.sleep(0.015)
            bar.update()
