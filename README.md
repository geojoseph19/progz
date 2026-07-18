# ProgZ

[![CI](https://github.com/geojoseph19/progz/actions/workflows/ci.yml/badge.svg)](https://github.com/geojoseph19/progz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/progz)](https://pypi.org/project/progz/)

Lightweight, dependency-free terminal progress bar with unique, customizable styles.

```
⠹ ━━━━━━━━━━━━━━────────── processing item 42
```

Zero runtime dependencies. Pure Python 3.10+ stdlib.

---

## Features

- 24-bit ANSI RGB rendering, no dependencies
- Braille spinner tied to elapsed time
- Composable layout: stack spinner, bar, text, percent, description in any order
- Progress-based colors: map any percentage or range to a color via `color_stops`, with optional gradient blending
- ASCII fallback for dumb terminals
- Context manager and manual API
- Fully customizable via `Style` dataclass
- Minimal writes: redraws only on `update()`
- Python 3.10+, fully typed

---

## Installation

```bash
pip install progz
```

---

## Quick Start

```python
from progz import ProgressBar

items = load_items()

with ProgressBar(total=len(items)) as bar:
    for item in items:
        process(item)
        bar.update()
```

---

## Examples

### With description

```python
with ProgressBar(total=100, description="loading") as bar:
    for i, item in enumerate(items):
        process(item)
        bar.update(description=f"item {i}")
```

### Update description without advancing

```python
with ProgressBar(total=100) as bar:
    bar.set_description("warming up")
    time.sleep(1)
    for item in items:
        process(item)
        bar.update()
```

### Manual (no context manager)

```python
bar = ProgressBar(total=100)
for item in items:
    process(item)
    bar.update()
bar.finish()
```

### ASCII fallback

```python
from progz import ProgressBar, ASCII

with ProgressBar(total=100, style=ASCII) as bar:
    ...
```

### Custom style

```python
from progz import ProgressBar, Style

style = Style(
    bar_width=40,
    speed=1.5,
    filled_char="█",
    empty_char="░",
)

with ProgressBar(total=100, style=style) as bar:
    ...
```

### Progress-based colors

`color_stops` maps progress to the bar fill color. Each stop is
`(threshold, (r, g, b))`; the fill uses the last stop at or below the
current progress ratio.

```python
from progz import ProgressBar, Style

# Red below 50%, yellow from 50%, green from 90%
style = Style(color_stops=(
    (0.0, (220, 60, 60)),
    (0.5, (230, 200, 60)),
    (0.9, (80, 200, 120)),
))
```

Add `interpolate=True` to blend colors smoothly between stops. Add
`color_by_position=True` to color each bar cell by its own position
instead of the current progress: the bar fills left to right and each
cell keeps its percentage's color, so a finished bar shows the full
color journey.

```python
# Smooth red-to-green gradient painted across the bar
style = Style(
    color_stops=((0.0, (220, 60, 60)), (1.0, (80, 200, 120))),
    interpolate=True,
    color_by_position=True,
)
```

---

## API Reference

### `ProgressBar(total, description="", style=None, file=None)`

| Parameter     | Type           | Default        | Description                     |
|---------------|----------------|----------------|---------------------------------|
| `total`       | `int`          | required       | Number of steps to completion   |
| `description` | `str`          | `""`           | Text shown to the right of bar  |
| `style`       | `Style \| None` | `SHIMMER`     | Visual style configuration      |
| `file`        | `TextIO \| None`| `sys.stderr`  | Output stream (pass `sys.stdout` to print inline) |

#### Methods

| Method                                | Description                              |
|---------------------------------------|------------------------------------------|
| `update(n=1, description=None)`       | Advance by n steps, optionally update description |
| `set_description(description)`        | Update description without advancing     |
| `finish()`                            | Complete bar and move to next line       |
| `completed` *(property)*             | Current completed count                  |
| `total` *(property)*                 | Total steps                              |

---

### `Style`

```python
@dataclass(frozen=True)
class Style:
    layout: tuple[Component, ...] = (Component.SPINNER, Component.BAR, Component.DESCRIPTION)
    bar_width: int = 24                              # characters wide
    speed: float = 0.6                               # shimmer sweep cycles/sec
    filled_char: str = "━"                           # character for filled portion
    empty_char: str = "─"                            # character for empty portion
    fill_text: str = ""                              # string rendered by Component.TEXT
    min_brightness: int = 80                         # grey floor (0 to 255)
    brightness_range: int = 175                      # grey range above floor
    empty_rgb: RGB = (60, 60, 60)                    # empty zone color
    spinner_color_rgb: RGB = (0, 200, 200)
    spinner_frames: tuple[str, ...] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    color_stops: tuple[tuple[float, RGB], ...] = ((0.0, (255, 255, 255)),)
    interpolate: bool = False                        # blend between adjacent stops
    color_by_position: bool = False                  # cells keep their own position color
```

`RGB` is a type alias for `tuple[int, int, int]`, exported from `progz`.

`color_stops` thresholds must be strictly increasing, in 0.0 to 1.0.
`Style` raises `ValueError` otherwise. Progress below the first
threshold uses the first stop's color. The shimmer wave modulates
brightness on top of the stop color; the default single white stop is
the classic greyscale shimmer. Stops are ignored when color is off.

### `Component`

The `layout` tuple selects which components render, and in what order (left to
right). Omit a component to hide it. Import from `progz`.

| Component               | Renders                                              |
|-------------------------|------------------------------------------------------|
| `Component.SPINNER`     | Animated braille frame; skipped when color is off    |
| `Component.BAR`         | Fill bar tied to progress percentage                 |
| `Component.TEXT`        | `fill_text` string with a shimmer wave               |
| `Component.PERCENT`     | Percentage readout, e.g. ` 42%`                      |
| `Component.DESCRIPTION` | The `description` label, rendered unstyled           |

Note: a layout containing only `Component.SPINNER` renders nothing when
color is off (for example in CI or with `NO_COLOR` set). Include `BAR`,
`PERCENT`, or `DESCRIPTION` if output must be visible without color.

```python
from progz import ProgressBar, Style, Component

# Bar with a percentage readout, no spinner
style = Style(layout=(Component.BAR, Component.PERCENT, Component.DESCRIPTION))

with ProgressBar(total=100, style=style) as bar:
    ...
```

### Pre-defined styles

| Name      | Description                        |
|-----------|------------------------------------|
| `SHIMMER` | Unique sine-wave brightness gradient, Unicode chars (default) |
| `ASCII`   | `#`/`-` chars, `(BAR, DESCRIPTION)` layout (no spinner) |

---

## Performance Notes

- No allocations outside of `update()` calls
- `render_frame()` is pure: no I/O, no side effects
- No background threads; redraws only on `update()`
- Uses `\r\033[2K` to overwrite in color mode; space-padding in ASCII mode
- 24-bit RGB via raw ANSI sequences, no terminal library needed

---

## Contributing

1. Fork the repo
2. `pip install -e ".[dev]"`
3. `pytest && mypy src/progz`
4. Submit a PR

---

## License

MIT
