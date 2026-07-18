"""Progress bar style definitions."""

from dataclasses import dataclass
from enum import Enum, auto

RGB = tuple[int, int, int]


class Component(Enum):
    """Visual components that can be stacked left-to-right in a progress bar layout.

    SPINNER:     Animated braille character; silently omitted when color is off.
    BAR:         Left-to-right fill bar tied to progress percentage.
    TEXT:        Fixed string rendered with a continuous shimmer wave.
    PERCENT:     Compact percentage readout, e.g. `` 42%``.
    DESCRIPTION: Plain-text label; always rendered unstyled after any ANSI resets.

    Example, percent before description::

        Style(layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION))

    Example, spinner only, no bar::

        Style(layout=(Component.SPINNER, Component.DESCRIPTION))
    """

    SPINNER = auto()
    BAR = auto()
    TEXT = auto()
    PERCENT = auto()
    DESCRIPTION = auto()


@dataclass(frozen=True)
class Style:
    """Visual configuration for a progress bar.

    The ``layout`` tuple controls which components are rendered and in what
    order (left to right). Omit a component to hide it entirely.

    Example, no spinner::

        Style(layout=(Component.BAR, Component.DESCRIPTION))

    Example, percentage readout::

        Style(layout=(Component.SPINNER, Component.BAR, Component.PERCENT, Component.DESCRIPTION))

    Example, shimmer text banner instead of a fill bar::

        Style(layout=(Component.TEXT, Component.DESCRIPTION), fill_text="Loading...")

    ``color_stops`` maps progress to bar fill color. Each stop is
    ``(threshold, (r, g, b))`` with thresholds strictly increasing in 0.0
    to 1.0. The fill takes the color of the last stop whose threshold is
    at or below the progress ratio; progress below the first threshold
    uses the first stop's color. ``interpolate=True`` blends linearly
    between adjacent stops instead. With ``color_by_position=True`` each
    bar cell is colored by its own position rather than the current
    progress, so a finished bar displays every color of the journey. The
    shimmer wave modulates brightness on top of the stop color; the
    default single white stop yields the classic greyscale shimmer.

    Example, red to yellow to green by progress::

        Style(color_stops=(
            (0.0, (220, 60, 60)),
            (0.5, (230, 200, 60)),
            (0.9, (80, 200, 120)),
        ))

    Example, smooth gradient painted across the bar, all colors visible
    at 100%::

        Style(
            color_stops=((0.0, (220, 60, 60)), (1.0, (80, 200, 120))),
            interpolate=True,
            color_by_position=True,
        )

    Raises:
        ValueError: if ``color_stops`` is empty, a threshold falls outside
            0.0 to 1.0, or thresholds are not strictly increasing.
    """

    layout: tuple[Component, ...] = (Component.SPINNER, Component.BAR, Component.DESCRIPTION)
    bar_width: int = 24
    speed: float = 0.6
    filled_char: str = "━"
    empty_char: str = "─"
    fill_text: str = ""
    min_brightness: int = 80
    brightness_range: int = 175
    empty_rgb: RGB = (60, 60, 60)
    spinner_color_rgb: RGB = (0, 200, 200)
    spinner_frames: tuple[str, ...] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    color_stops: tuple[tuple[float, RGB], ...] = ((0.0, (255, 255, 255)),)
    interpolate: bool = False
    color_by_position: bool = False

    def __post_init__(self) -> None:
        if not self.color_stops:
            raise ValueError("color_stops must contain at least one stop")
        prev = -1.0
        for threshold, _ in self.color_stops:
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"color_stops threshold {threshold} outside 0.0 to 1.0")
            if threshold <= prev:
                raise ValueError("color_stops thresholds must be strictly increasing")
            prev = threshold


SHIMMER = Style()

ASCII = Style(
    filled_char="#",
    empty_char="-",
    layout=(Component.BAR, Component.DESCRIPTION),
)
