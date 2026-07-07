"""Multiple sequential progress bars."""

import time

from progz import ProgressBar

stages = [
    ("Loading data", 20, 0.04),
    ("Processing", 40, 0.02),
    ("Writing output", 15, 0.06),
]

for name, steps, delay in stages:
    with ProgressBar(total=steps, description=name) as bar:
        for _ in range(steps):
            time.sleep(delay)
            bar.update()
