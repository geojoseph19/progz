# ProgZ

[![CI](https://github.com/geojoseph19/progz/actions/workflows/ci.yml/badge.svg)](https://github.com/geojoseph19/progz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/progz)](https://pypi.org/project/progz/)

Lightweight, dependency-free terminal progress bar with unique, customizable styles.

![progz](https://raw.githubusercontent.com/geojoseph19/progz/main/docs/gifs/track.gif)

Zero runtime dependencies. Pure Python 3.10+ stdlib. Fully typed.

---

## Features

- One-liner: `for item in track(items):`
- Composable layout: spinner, bar, text, percent, count, rate, ETA, elapsed, description, in any order
- 24-bit ANSI RGB rendering with progress-based color stops and gradients
- Indeterminate mode for unknown totals
- Throttled redraws (30 Hz default): O(1) per-update cost, cheap over millions of items
- `bar.write()` to log above a live bar; transient bars that erase on finish
- ASCII fallback for dumb terminals; works on Windows 10+ out of the box

---

## Installation

```bash
pip install progz
```

## Quick Start

```python
from progz import track

for item in track(items, description="processing"):
    process(item)
```

Or with explicit control:

```python
from progz import ProgressBar

with ProgressBar(total=len(items)) as bar:
    for item in items:
        process(item)
        bar.update()
```

---

## Gallery

Presets (`SHIMMER`, `ASCII`, `BLOCKS`, `MINIMAL`, `RAINBOW`):

![presets](https://raw.githubusercontent.com/geojoseph19/progz/main/docs/gifs/presets.gif)

Numeric readouts (`PERCENT`, `COUNT`, `RATE`, `ETA`, `ELAPSED`):

![numbers](https://raw.githubusercontent.com/geojoseph19/progz/main/docs/gifs/numbers.gif)

More recordings, including indeterminate mode and `bar.write()`, are in `examples/` and `docs/tapes/`.

---

## Examples

### Numeric readouts

```python
from progz import ProgressBar, Style, Component

style = Style(layout=(
    Component.SPINNER, Component.BAR, Component.PERCENT,
    Component.COUNT, Component.RATE, Component.ETA, Component.ELAPSED,
))

with ProgressBar(total=10_000, style=style) as bar:
    ...
```

Renders readouts like ` 42% 4200/10000 1.2k it/s ~00:04 00:03`. Rate is an
exponentially weighted moving average with O(1) state; ETA derives from it.

### Unknown total

```python
for chunk in track(stream(), description="receiving"):
    handle(chunk)
```

`track()` falls back to indeterminate mode automatically for iterables
without `len()`. `BAR` renders a bouncing segment, `PERCENT`/`ETA` show
`--`, and `COUNT` shows a plain count.

### Logging above a live bar

```python
with ProgressBar(total=100) as bar:
    for i, item in enumerate(items):
        if i % 10 == 0:
            bar.write(f"checkpoint {i}")
        process(item)
        bar.update()
```

`bar.write()` erases the bar line, prints the message plus a newline, and
redraws the bar below it. Pass `transient=True` to `ProgressBar` to erase
the bar itself on `finish()`.

### Styling

```python
from progz import ProgressBar, ASCII, Style

# built-in fallback style
with ProgressBar(total=100, style=ASCII) as bar:
    ...

# custom style
style = Style(bar_width=40, filled_char="█", empty_char="░")

# progress-based color: red below 50%, yellow from 50%, green from 90%
style = Style(color_stops=(
    (0.0, (220, 60, 60)),
    (0.5, (230, 200, 60)),
    (0.9, (80, 200, 120)),
))
```

Add `interpolate=True` to blend colors smoothly between stops. Add
`color_by_position=True` to color each cell by its own position instead of
current progress, so a finished bar shows the full color journey.

---

## API Reference

### `track(iterable, description="", total=None, style=None, file=None, refresh_rate=30.0, transient=False)`

Iterate while drawing a progress bar. `total` is inferred via `len()` when
available; otherwise the bar runs in indeterminate mode. The bar always
reaches a final state, including when the loop raises or stops early.
Remaining parameters match `ProgressBar`.

### `ProgressBar(total, description="", style=None, file=None, refresh_rate=30.0, transient=False)`

| Parameter      | Type            | Default       | Description                     |
|----------------|-----------------|---------------|---------------------------------|
| `total`        | `int \| None`   | required      | Steps to completion; `None` for indeterminate mode |
| `description`  | `str`           | `""`          | Text shown to the right of bar  |
| `style`        | `Style \| None` | `SHIMMER`     | Visual style configuration      |
| `file`         | `TextIO \| None`| `sys.stderr`  | Output stream (pass `sys.stdout` to print inline) |
| `refresh_rate` | `float`         | `30.0`        | Max redraws per second; `0` disables throttling |
| `transient`    | `bool`          | `False`       | Erase the bar on finish instead of keeping it |

#### Methods

| Method                           | Description                              |
|----------------------------------|-------------------------------------------|
| `update(n=1, description=None)` | Advance by n steps, optionally update description |
| `set_description(description)`  | Update description without advancing     |
| `write(message)`                 | Print a line above the live bar          |
| `finish()`                       | Complete bar and move to next line       |
| `completed` *(property)*        | Current completed count                  |
| `total` *(property)*            | Total steps; `None` in indeterminate mode |

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
    block_chars: tuple[str, ...] = ()                # partial-fill glyphs for sub-cell resolution
```

`RGB` is a type alias for `tuple[int, int, int]`, exported from `progz`.
`color_stops` thresholds must be strictly increasing, in 0.0 to 1.0;
`Style` raises `ValueError` otherwise.

### `Component`

The `layout` tuple selects which components render, and in what order (left
to right). Omit a component to hide it. Import from `progz`.

| Component               | Renders                                              |
|--------------------------|------------------------------------------------------|
| `Component.SPINNER`     | Animated braille frame; skipped when color is off    |
| `Component.BAR`         | Fill bar tied to progress; bouncing segment when total is unknown |
| `Component.TEXT`        | `fill_text` string with a shimmer wave               |
| `Component.PERCENT`     | Percentage readout, e.g. ` 42%`; ` --%` when total is unknown |
| `Component.DESCRIPTION` | The `description` label, rendered unstyled           |
| `Component.COUNT`       | `42/1000` readout; plain count when total is unknown |
| `Component.ELAPSED`     | Elapsed time, `01:23` (`h:mm:ss` past one hour)      |
| `Component.RATE`        | Smoothed throughput, e.g. `1.2k it/s`                |
| `Component.ETA`         | Estimated time remaining, e.g. `~00:45`              |

Note: a layout containing only `Component.SPINNER` renders nothing when
color is off (for example in CI or with `NO_COLOR` set). Include `BAR`,
`PERCENT`, or `DESCRIPTION` if output must be visible without color.

### Pre-defined styles

| Name      | Description                        |
|-----------|-------------------------------------|
| `SHIMMER` | Unique sine-wave brightness gradient, Unicode chars (default) |
| `ASCII`   | `#`/`-` chars, `(BAR, DESCRIPTION)` layout (no spinner) |
| `BLOCKS`  | Eighth-block sub-cell fill (`▏▎▍▌▋▊▉█`): 8 visible states per cell |
| `MINIMAL` | Bar plus percent, nothing else     |
| `RAINBOW` | Interpolated multi-color gradient painted across the bar |

---

## Color and platform handling

Detection runs once, at construction time:

- `NO_COLOR` disables color and wins over everything.
- `FORCE_COLOR` enables color even for non-TTY streams.
- `TERM=dumb` disables color.
- On Windows 10+, virtual terminal processing is enabled automatically
  (stdlib `ctypes`, no colorama). If the console rejects it, progz falls
  back to plain output instead of escape garbage.

## Performance

- Between draws, `update()` is a counter bump plus one `time.monotonic()`
  call; redraws are throttled (default 30 Hz). `finish()` always draws the
  final frame, so no state change is lost.
- Per-update cost is O(1) in `total`.
- `render_frame()` is pure: no I/O, no side effects.
- No background threads; animation samples elapsed time on `update()`.
- `benchmarks/bench.py` measures import time, per-update cost, and frame
  render cost; CI enforces an import-time budget.

---

## Contributing

1. Fork the repo
2. `pip install -e ".[dev]"`
3. `pytest && mypy src/progz`
4. Submit a PR

## License

MIT
