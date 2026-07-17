"""Progress bar style definitions."""

from dataclasses import dataclass
from enum import Enum, auto


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
    """

    layout: tuple[Component, ...] = (Component.SPINNER, Component.BAR, Component.DESCRIPTION)
    bar_width: int = 24
    speed: float = 0.6
    filled_char: str = "━"
    empty_char: str = "─"
    fill_text: str = ""
    min_brightness: int = 80
    brightness_range: int = 175
    empty_rgb: tuple[int, int, int] = (60, 60, 60)
    spinner_color_rgb: tuple[int, int, int] = (0, 200, 200)
    spinner_frames: tuple[str, ...] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")


SHIMMER = Style()

ASCII = Style(
    filled_char="#",
    empty_char="-",
    layout=(Component.BAR, Component.DESCRIPTION),
)
