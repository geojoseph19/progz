# progz

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
    empty_rgb: tuple[int, int, int] = (60, 60, 60)  # empty zone color
    spinner_color_rgb: tuple[int, int, int] = (0, 200, 200)
    spinner_frames: tuple[str, ...] = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
```

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
