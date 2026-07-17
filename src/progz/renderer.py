"""Rendering logic: converts progress state into a display string."""

import math

from .styles import Component, Style
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
    Components are rendered left-to-right in the order defined by style.layout.
    SPINNER is silently skipped when use_color is False.
    """
    parts: list[str] = []
    started = False
    needs_reset = False

    for component in style.layout:
        match component:
            case Component.SPINNER:
                if use_color:
                    if started:
                        parts.append(" ")
                    _render_spinner(parts, style, elapsed)
                    started = True

            case Component.BAR:
                if started:
                    parts.append(" ")
                _render_bar(parts, style, completed, total, elapsed, use_color)
                needs_reset = use_color
                started = True

            case Component.TEXT:
                if style.fill_text:
                    if started:
                        parts.append(" ")
                    _render_text(parts, style, elapsed, use_color)
                    needs_reset = use_color
                    started = True

            case Component.PERCENT:
                if needs_reset:
                    parts.append(RESET)
                    needs_reset = False
                if started:
                    parts.append(" ")
                _render_percent(parts, completed, total)
                started = True

            case Component.DESCRIPTION:
                if description:
                    if needs_reset:
                        parts.append(RESET)
                        needs_reset = False
                    if started:
                        parts.append(" ")
                    parts.append(description)
                    started = True

    if needs_reset:
        parts.append(RESET)

    return "".join(parts)


def _ratio(completed: int, total: int) -> float:
    # A zero-total bar has no work to do, so it is trivially complete.
    return min(1.0, completed / total) if total > 0 else 1.0


def _render_spinner(parts: list[str], style: Style, elapsed: float) -> None:
    frame_idx = int(elapsed * 10) % len(style.spinner_frames)
    r, g, b = style.spinner_color_rgb
    parts.append(f"{rgb(r, g, b)}{style.spinner_frames[frame_idx]}{RESET}")


def _render_bar(
    parts: list[str],
    style: Style,
    completed: int,
    total: int,
    elapsed: float,
    use_color: bool,
) -> None:
    filled = int(_ratio(completed, total) * style.bar_width)

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


def _render_text(
    parts: list[str],
    style: Style,
    elapsed: float,
    use_color: bool,
) -> None:
    text = style.fill_text
    for i, char in enumerate(text):
        if use_color:
            phase = (i / len(text)) - (elapsed * style.speed % 1.0)
            brightness = (math.sin(phase * 2 * math.pi) + 1) / 2
            grey = max(0, min(255, int(style.min_brightness + brightness * style.brightness_range)))
            parts.append(f"{rgb(grey, grey, grey)}{char}")
        else:
            parts.append(char)


def _render_percent(parts: list[str], completed: int, total: int) -> None:
    parts.append(f"{int(_ratio(completed, total) * 100):3d}%")
