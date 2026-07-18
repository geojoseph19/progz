"""bar.write(): print above a live bar without shredding it."""

import time

from progz import ProgressBar

with ProgressBar(total=50, description="working") as bar:
    for i in range(50):
        time.sleep(0.05)
        if i and i % 10 == 0:
            bar.write(f"checkpoint at item {i}")
        bar.update()
