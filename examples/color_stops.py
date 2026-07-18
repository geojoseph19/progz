"""Progress-based colors via Style.color_stops, on realistic tasks. Run with: python examples/color_stops.py"""

import time

from progz import Component, ProgressBar, Style

STEPS = 60
DELAY = 0.08


def run(label: str, style: Style, description: str = "") -> None:
    print(f"\n  {label}")
    with ProgressBar(total=STEPS, style=style, description=description) as bar:
        for _ in range(STEPS):
            time.sleep(DELAY)
            bar.update()


# 1. File download: neutral while transferring, green once complete.
#    A single extra stop at 1.0 changes only the finished state.
run(
    "Download: neutral in flight, green when done",
    Style(
        layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION),
        color_stops=((0.0, (255, 255, 255)), (1.0, (80, 200, 120))),
    ),
    description="model-weights.bin",
)

# 2. Disk usage gauge: monitoring semantics, green to 70%, yellow to 90%,
#    red above. Block characters, no spinner, steady fill (no shimmer sweep).
run(
    "Disk usage: green, yellow at 70%, red at 90%",
    Style(
        layout=(Component.BAR, Component.PERCENT, Component.DESCRIPTION),
        bar_width=30,
        filled_char="█",
        empty_char=" ",
        min_brightness=255,
        brightness_range=0,
        color_stops=((0.0, (80, 200, 120)), (0.7, (230, 200, 60)), (0.9, (220, 60, 60))),
    ),
    description="/dev/sda1",
)

# 3. Capacity meter: color_by_position paints the zones onto the bar itself,
#    so the scale reads like a gauge. Filling reveals which zone you are in.
run(
    "Quota meter: zones painted at their positions",
    Style(
        layout=(Component.BAR, Component.PERCENT, Component.DESCRIPTION),
        bar_width=30,
        min_brightness=200,
        brightness_range=55,
        color_stops=((0.0, (80, 200, 120)), (0.7, (230, 200, 60)), (0.9, (220, 60, 60))),
        color_by_position=True,
    ),
    description="api quota",
)

# 4. Deploy pipeline: cold blue warming to white as rollout nears completion.
#    interpolate=True blends the whole fill smoothly with progress.
run(
    "Deploy: blue to white, smooth blend",
    Style(
        layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION),
        speed=0.3,
        color_stops=((0.0, (70, 140, 230)), (1.0, (255, 255, 255))),
        interpolate=True,
    ),
    description="rolling out v2.4.1",
)

# 5. Brand color: a single stop gives a solid theme color for the whole run,
#    shimmer wave kept. Useful for CLIs that match a product palette.
run(
    "Brand theme: single stop, solid teal",
    Style(
        layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION),
        color_stops=((0.0, (0, 190, 190)),),
        spinner_color_rgb=(0, 190, 190),
    ),
    description="indexing documents",
)

print()
