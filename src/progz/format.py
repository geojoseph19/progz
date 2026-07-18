"""Pure string formatting helpers for readout components."""

import math


def format_duration(seconds: float) -> str:
    """Format seconds as ``mm:ss``, or ``h:mm:ss`` from one hour up.

    Non-finite or negative input renders as ``--:--``.
    """
    if not math.isfinite(seconds) or seconds < 0:
        return "--:--"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def format_si(value: float) -> str:
    """Format a magnitude with one decimal and a k/M/G suffix from 1000 up.

    Examples: ``2.5`` -> ``2.5``, ``1234.0`` -> ``1.2k``, ``2.5e6`` -> ``2.5M``.
    """
    for divisor, suffix in ((1_000_000_000, "G"), (1_000_000, "M"), (1_000, "k")):
        if value >= divisor:
            return f"{value / divisor:.1f}{suffix}"
    return f"{value:.1f}"
