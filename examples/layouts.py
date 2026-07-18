"""Demonstrates the Component stacking system. Run with: python examples/layouts.py"""

import time

from progz import Component, ProgressBar, Style

STEPS = 40
DELAY = 0.04


def run(label: str, style: Style) -> None:
    print(f"\n  {label}")
    with ProgressBar(total=STEPS, style=style) as bar:
        for _ in range(STEPS):
            time.sleep(DELAY)
            bar.update()


# 1. Default (spinner + bar + description)
run(
    "Default: SPINNER, BAR, DESCRIPTION",
    Style(),
)

# 2. No spinner
run(
    "No spinner: BAR, DESCRIPTION",
    Style(layout=(Component.BAR, Component.DESCRIPTION)),
)

# 3. With percentage
run(
    "Percentage: SPINNER, BAR, PERCENT, DESCRIPTION",
    Style(layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION)),
)

# 4. Spinner after bar
run(
    "Reversed: BAR, PERCENT, SPINNER, DESCRIPTION",
    Style(layout=(Component.BAR, Component.PERCENT, Component.SPINNER, Component.DESCRIPTION)),
)

# 5. Shimmer text banner, no fill bar
run(
    "Text banner: SPINNER, TEXT, DESCRIPTION",
    Style(
        layout=(Component.SPINNER, Component.TEXT, Component.DESCRIPTION),
        fill_text="  Processing  ",
        speed=0.4,
    ),
)

# 6. Percent only (minimal)
run(
    "Minimal: PERCENT only",
    Style(layout=(Component.PERCENT,)),
)

# 7. ASCII + percent (no color, CI-friendly)
run(
    "ASCII + percent: BAR, PERCENT, DESCRIPTION",
    Style(
        filled_char="#",
        empty_char="-",
        layout=(Component.BAR, Component.PERCENT, Component.DESCRIPTION),
    ),
)

print()
