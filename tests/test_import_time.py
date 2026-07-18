"""CI guard for the weightless import claim."""

import os
import subprocess
import sys
from pathlib import Path

_SRC = str(Path(__file__).resolve().parents[1] / "src")

# Generous versus the a few milliseconds progz actually takes, so slow CI
# machines do not flake, while a heavyweight import still fails loudly.
_BUDGET_S = 0.050


def test_import_time_under_budget():
    code = (
        "import time; t0 = time.perf_counter(); import progz; "
        "print(time.perf_counter() - t0)"
    )
    env = {**os.environ, "PYTHONPATH": _SRC}
    samples = [
        float(
            subprocess.run(
                [sys.executable, "-c", code],
                capture_output=True,
                text=True,
                check=True,
                env=env,
            ).stdout
        )
        for _ in range(5)
    ]
    assert min(samples) < _BUDGET_S, f"import progz took {min(samples) * 1000:.1f} ms"
