"""progz benchmark suite.

Run from the repo root:

    python benchmarks/bench.py

Stdlib only. Numbers are indicative; pin the CPU governor and close other
loads for anything citable.
"""

import io
import os
import subprocess
import sys
import time
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")
sys.path.insert(0, _SRC)

from progz import ProgressBar  # noqa: E402
from progz.renderer import render_frame  # noqa: E402
from progz.styles import SHIMMER  # noqa: E402


def bench_import_time(runs: int = 5) -> float:
    """Best-of-N import time in a fresh interpreter, seconds."""
    code = (
        "import time; t0 = time.perf_counter(); import progz; "
        "print(time.perf_counter() - t0)"
    )
    env = {**os.environ, "PYTHONPATH": _SRC}
    return min(
        float(
            subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            ).stdout
        )
        for _ in range(runs)
    )


def bench_update_throttled(n: int = 1_000_000) -> float:
    """Per-update cost with the default 30 Hz throttle, seconds."""
    bar = ProgressBar(total=n, file=io.StringIO())
    t0 = time.perf_counter()
    for _ in range(n):
        bar.update()
    return (time.perf_counter() - t0) / n


def bench_update_drawn(n: int = 20_000) -> float:
    """Per-update cost when every update draws a color frame, seconds."""
    bar = ProgressBar(total=n, file=io.StringIO(), refresh_rate=0)
    bar._use_color = True
    t0 = time.perf_counter()
    for _ in range(n):
        bar.update()
    return (time.perf_counter() - t0) / n


def bench_render_frame(n: int = 20_000) -> float:
    """Per-frame render cost, color path, seconds."""
    t0 = time.perf_counter()
    for i in range(n):
        render_frame(i % 100, 100, i / 1000.0, "benchmark", SHIMMER, True)
    return (time.perf_counter() - t0) / n


def main() -> None:
    print(f"import progz (best of 5):     {bench_import_time() * 1e3:8.2f} ms")
    print(f"update(), 30 Hz throttle:     {bench_update_throttled() * 1e9:8.0f} ns/update")
    print(f"update(), draw every frame:   {bench_update_drawn() * 1e6:8.2f} us/update")
    print(f"render_frame(), color:        {bench_render_frame() * 1e6:8.2f} us/frame")


if __name__ == "__main__":
    main()
