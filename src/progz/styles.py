"""Progress bar style definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Style:
    """Visual configuration for a progress bar."""

    bar_width: int = 24
    speed: float = 0.6
    filled_char: str = "━"
    empty_char: str = "─"
    min_brightness: int = 80
    brightness_range: int = 175
    empty_rgb: tuple[int, int, int] = field(default_factory=lambda: (60, 60, 60))
    show_spinner: bool = True
    spinner_color_rgb: tuple[int, int, int] = field(default_factory=lambda: (0, 200, 200))
    spinner_frames: tuple[str, ...] = field(
        default_factory=lambda: ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    )


SHIMMER = Style()

ASCII = Style(
    filled_char="#",
    empty_char="-",
    show_spinner=False,
)
