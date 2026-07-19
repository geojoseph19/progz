# ProgZ

[![CI](https://github.com/geojoseph19/progz/actions/workflows/ci.yml/badge.svg)](https://github.com/geojoseph19/progz/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/progz)](https://pypi.org/project/progz/)

![progz banner](https://raw.githubusercontent.com/geojoseph19/progz/main/docs/progz_banner.png)

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

Presets, in the `progz.presets` namespace (`presets.SHIMMER`, `presets.ASCII`, `presets.BLOCKS`, `presets.MINIMAL`, `presets.DETAILED`, `presets.RAINBOW`):

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
from progz import ProgressBar, Style, presets

# built-in fallback style
with ProgressBar(total=100, style=presets.ASCII) as bar:
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

Full parameter tables, `Style`/`Component` fields, pre-defined styles,
color/platform detection rules, and performance notes:
[docs/API.md](https://github.com/geojoseph19/progz/blob/main/docs/API.md).

---

## Contributing

1. Fork the repo
2. `pip install -e ".[dev]"`
3. `pytest && mypy src/progz`
4. Submit a PR

## License

MIT
