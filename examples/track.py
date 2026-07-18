"""track(): the one-line progress bar."""

import time

from progz import track

for item in track(range(50), description="processing"):
    time.sleep(0.05)
