"""Ready-made :class:`~progz.styles.Style` presets.

Each preset is a frozen ``Style`` instance. Pass one as the ``style``
argument, or use it as a base for :func:`dataclasses.replace`.

Example::

    from progz import ProgressBar, presets

    with ProgressBar(total=100, style=presets.RAINBOW) as bar:
        ...
"""

from .styles import Component, Style

SHIMMER = Style()

ASCII = Style(
    filled_char="#",
    empty_char="-",
    layout=(Component.BAR, Component.DESCRIPTION),
)

MINIMAL = Style(layout=(Component.BAR, Component.PERCENT))

DETAILED = Style(
    layout=(
        Component.SPINNER,
        Component.BAR,
        Component.PERCENT,
        Component.COUNT,
        Component.RATE,
        Component.ETA,
        Component.ELAPSED,
    ),
)

BLOCKS = Style(
    filled_char="█",
    empty_char="─",
    block_chars=("▏", "▎", "▍", "▌", "▋", "▊", "▉"),
)

RAINBOW = Style(
    color_stops=(
        (0.0, (235, 70, 70)),
        (0.2, (240, 160, 60)),
        (0.4, (230, 220, 70)),
        (0.6, (80, 200, 120)),
        (0.8, (70, 130, 235)),
        (1.0, (170, 90, 220)),
    ),
    interpolate=True,
    color_by_position=True,
)

# progz brand banner: dark field, ember streaks cooling from deep red
# through orange and amber to a hot white-gold core (the glowing "Z").
EMBER = Style(
    color_stops=(
        (0.0, (120, 30, 0)),
        (0.35, (220, 80, 15)),
        (0.7, (255, 150, 40)),
        (1.0, (255, 232, 170)),
    ),
    interpolate=True,
    color_by_position=True,
    empty_rgb=(40, 20, 12),
    spinner_color_rgb=(255, 120, 30),
)
