"""Terminal detection and ANSI escape code helpers."""

import os


def supports_color(file: object) -> bool:
    """Return True if file supports ANSI color output."""
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return (
        hasattr(file, "isatty")
        and file.isatty()  # type: ignore[union-attr]
        and os.environ.get("TERM", "") != "dumb"
    )


RESET = "\033[0m"
ERASE_LINE = "\033[2K"


def rgb(r: int, g: int, b: int) -> str:
    """24-bit foreground color escape sequence."""
    return f"\033[38;2;{r};{g};{b}m"
