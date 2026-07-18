"""Rendering logic: converts progress state into a display string."""

import math

from .styles import RGB, Component, Style
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


def _shimmer_scale(i: int, n: int, elapsed: float, style: Style) -> int:
    """Brightness scale 0..255 for position i of n in the shimmer wave."""
    phase = (i / n) - (elapsed * style.speed % 1.0)
    brightness = (math.sin(phase * 2 * math.pi) + 1) / 2
    return max(0, min(255, int(style.min_brightness + brightness * style.brightness_range)))


def _stop_rgb(ratio: float, stops: tuple[tuple[float, RGB], ...], interpolate: bool) -> RGB:
    """Resolve the color for a progress ratio from sorted color stops."""
    idx = 0
    for i, (threshold, _) in enumerate(stops):
        if threshold > ratio:
            break
        idx = i
    t0, c0 = stops[idx]
    if not interpolate or idx == len(stops) - 1 or ratio <= t0:
        return c0
    t1, c1 = stops[idx + 1]
    t = (ratio - t0) / (t1 - t0)
    return (
        int(c0[0] + (c1[0] - c0[0]) * t),
        int(c0[1] + (c1[1] - c0[1]) * t),
        int(c0[2] + (c1[2] - c0[2]) * t),
    )


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
    width = style.bar_width
    ratio = _ratio(completed, total)
    filled = int(ratio * width)

    if not use_color:
        parts.append(style.filled_char * filled)
        parts.append(style.empty_char * (width - filled))
        return

    stops = style.color_stops
    base = None if style.color_by_position else _stop_rgb(ratio, stops, style.interpolate)
    for i in range(filled):
        if base is None:
            # Cells span the bar from 0% (leftmost) to 100% (rightmost).
            cell_ratio = i / (width - 1) if width > 1 else 1.0
            r, g, b = _stop_rgb(cell_ratio, stops, style.interpolate)
        else:
            r, g, b = base
        scale = _shimmer_scale(i, width, elapsed, style)
        parts.append(f"{rgb(r * scale // 255, g * scale // 255, b * scale // 255)}{style.filled_char}")

    if filled < width:
        er, eg, eb = style.empty_rgb
        parts.append(rgb(er, eg, eb))
        parts.append(style.empty_char * (width - filled))


def _render_text(
    parts: list[str],
    style: Style,
    elapsed: float,
    use_color: bool,
) -> None:
    text = style.fill_text
    if not use_color:
        parts.append(text)
        return
    for i, char in enumerate(text):
        grey = _shimmer_scale(i, len(text), elapsed, style)
        parts.append(f"{rgb(grey, grey, grey)}{char}")


def _render_percent(parts: list[str], completed: int, total: int) -> None:
    parts.append(f"{int(_ratio(completed, total) * 100):3d}%")
