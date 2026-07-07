"""Rendering logic: converts progress state into a display string."""

import math

from .styles import Style
from .terminal import RESET, rgb


def render_frame(
    completed: int,
    total: int,
    elapsed: float,
    description: str,
    style: Style,
    use_color: bool,
) -> str:
    """Render a single progress bar frame.

    Returns a string with ANSI codes if use_color is True, plain otherwise.
    """
    ratio = min(1.0, completed / total) if total > 0 else 0.0
    filled = int(ratio * style.bar_width)

    parts: list[str] = []

    if style.show_spinner and use_color:
        frame_idx = int(elapsed * 10) % len(style.spinner_frames)
        r, g, b = style.spinner_color_rgb
        parts.append(f"{rgb(r, g, b)}{style.spinner_frames[frame_idx]}{RESET} ")

    er, eg, eb = style.empty_rgb
    empty_esc = f"{rgb(er, eg, eb)}" if use_color else ""
    in_empty = False

    for i in range(style.bar_width):
        if i < filled:
            if use_color:
                phase = (i / style.bar_width) - (elapsed * style.speed % 1.0)
                brightness = (math.sin(phase * 2 * math.pi) + 1) / 2
                grey = max(0, min(255, int(style.min_brightness + brightness * style.brightness_range)))
                parts.append(f"{rgb(grey, grey, grey)}{style.filled_char}")
            else:
                parts.append(style.filled_char)
        else:
            if not in_empty:
                parts.append(empty_esc)
                in_empty = True
            parts.append(style.empty_char)

    if use_color:
        parts.append(RESET)

    if description:
        parts.append(f" {description}")

    return "".join(parts)
