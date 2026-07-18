"""Rendering logic: converts progress state into a display string."""

import math

from .format import format_duration, format_si
from .styles import RGB, Component, Style
from .terminal import RESET, rgb


def render_frame(
    completed: int,
    total: int | None,
    elapsed: float,
    description: str,
    style: Style,
    use_color: bool,
    rate: float | None = None,
) -> str:
    """Render a single progress bar frame.

    Returns a string with ANSI codes if use_color is True, plain otherwise.
    Components are rendered left-to-right in the order defined by style.layout.
    SPINNER is silently skipped when use_color is False.

    A None total renders indeterminate mode: BAR becomes a bouncing segment
    driven by elapsed, PERCENT and ETA show ``--``, COUNT shows a plain count.
    rate is the smoothed steps-per-second estimate; None until one exists.
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
                if total is None:
                    _render_bar_indeterminate(parts, style, elapsed, use_color)
                else:
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

            case Component.DESCRIPTION:
                if description:
                    if needs_reset:
                        parts.append(RESET)
                        needs_reset = False
                    if started:
                        parts.append(" ")
                    parts.append(description)
                    started = True

            case (
                Component.PERCENT
                | Component.COUNT
                | Component.ELAPSED
                | Component.RATE
                | Component.ETA
            ):
                if needs_reset:
                    parts.append(RESET)
                    needs_reset = False
                if started:
                    parts.append(" ")
                parts.append(_render_readout(component, completed, total, elapsed, rate))
                started = True

    if needs_reset:
        parts.append(RESET)

    return "".join(parts)


def truncate_visible(line: str, width: int) -> str:
    """Cut line to at most width visible columns.

    ANSI escapes count as zero width. If the cut drops characters from a
    line that used color, a reset is appended so no color leaks.
    """
    if width <= 0:
        return ""
    if "\033" not in line:
        return line if len(line) <= width else line[:width]
    visible = 0
    i = 0
    while i < len(line):
        if line[i] == "\033":
            end = line.find("m", i)
            if end < 0:
                return line[:i] + RESET
            i = end + 1
            continue
        if visible >= width:
            return line[:i] + RESET
        visible += 1
        i += 1
    return line


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


def _cell_escape(i: int, width: int, elapsed: float, style: Style, base: RGB | None) -> str:
    """Color escape for bar cell i: stop color scaled by the shimmer wave."""
    if base is None:
        # Cells span the bar from 0% (leftmost) to 100% (rightmost).
        cell_ratio = i / (width - 1) if width > 1 else 1.0
        r, g, b = _stop_rgb(cell_ratio, style.color_stops, style.interpolate)
    else:
        r, g, b = base
    scale = _shimmer_scale(i, width, elapsed, style)
    return rgb(r * scale // 255, g * scale // 255, b * scale // 255)


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
    cells = ratio * width
    filled = int(cells)
    partial = ""
    if style.block_chars and filled < width:
        idx = int((cells - filled) * (len(style.block_chars) + 1))
        if idx > 0:
            partial = style.block_chars[idx - 1]
    empty = width - filled - len(partial)

    if not use_color:
        parts.append(style.filled_char * filled)
        parts.append(partial)
        parts.append(style.empty_char * empty)
        return

    base = None if style.color_by_position else _stop_rgb(ratio, style.color_stops, style.interpolate)
    for i in range(filled):
        parts.append(f"{_cell_escape(i, width, elapsed, style, base)}{style.filled_char}")
    if partial:
        parts.append(f"{_cell_escape(filled, width, elapsed, style, base)}{partial}")
    if empty > 0:
        er, eg, eb = style.empty_rgb
        parts.append(rgb(er, eg, eb))
        parts.append(style.empty_char * empty)


def _render_bar_indeterminate(
    parts: list[str],
    style: Style,
    elapsed: float,
    use_color: bool,
) -> None:
    """Bouncing segment for unknown totals, driven entirely by elapsed."""
    width = style.bar_width
    if width <= 0:
        return
    seg = min(max(1, width // 4), width)
    # Triangle wave: the segment sweeps right then left, one cycle per
    # 1/speed seconds, matching the shimmer clock.
    cycle = (elapsed * style.speed) % 1.0
    t = cycle * 2 if cycle < 0.5 else 2.0 - cycle * 2
    start = round((width - seg) * t)

    if not use_color:
        parts.append(style.empty_char * start)
        parts.append(style.filled_char * seg)
        parts.append(style.empty_char * (width - start - seg))
        return

    er, eg, eb = style.empty_rgb
    if start > 0:
        parts.append(rgb(er, eg, eb))
        parts.append(style.empty_char * start)
    for i in range(start, start + seg):
        parts.append(f"{_cell_escape(i, width, elapsed, style, None)}{style.filled_char}")
    if start + seg < width:
        parts.append(rgb(er, eg, eb))
        parts.append(style.empty_char * (width - start - seg))


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


def _render_readout(
    component: Component,
    completed: int,
    total: int | None,
    elapsed: float,
    rate: float | None,
) -> str:
    match component:
        case Component.PERCENT:
            return _render_percent(completed, total)
        case Component.COUNT:
            return _render_count(completed, total)
        case Component.ELAPSED:
            return format_duration(elapsed)
        case Component.RATE:
            return _render_rate(rate)
        case _:
            return _render_eta(completed, total, rate)


def _render_percent(completed: int, total: int | None) -> str:
    if total is None:
        return " --%"
    return f"{int(_ratio(completed, total) * 100):3d}%"


def _render_count(completed: int, total: int | None) -> str:
    return str(completed) if total is None else f"{completed}/{total}"


def _render_rate(rate: float | None) -> str:
    return "-- it/s" if rate is None else f"{format_si(rate)} it/s"


def _render_eta(completed: int, total: int | None, rate: float | None) -> str:
    if total is None or rate is None or rate <= 0:
        return "~--:--"
    return f"~{format_duration((total - completed) / rate)}"
