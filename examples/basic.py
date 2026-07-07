"""Basic usage example."""

import time

from progz import ProgressBar

items = list(range(50))

with ProgressBar(total=len(items), description="processing") as bar:
    for item in items:
        time.sleep(0.05)
        bar.update(description=f"item {item}")
