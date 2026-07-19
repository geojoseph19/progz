"""Built-in presets, one after another. See signature.py for EMBER and SHIMMER."""

import time

from progz import ProgressBar, presets

for name, style in (
    ("ASCII", presets.ASCII),
    ("BLOCKS", presets.BLOCKS),
    ("MINIMAL", presets.MINIMAL),
    ("DETAILED", presets.DETAILED),
    ("RAINBOW", presets.RAINBOW),
):
    with ProgressBar(total=120, style=style, description=name) as bar:
        for _ in range(120):
            time.sleep(0.015)
            bar.update()
