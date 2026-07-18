# Changelog

All notable changes to progz are documented here.

## [1.0.0] - 2026-07-18

### Added
- `track()`: one-line iteration wrapper. Infers `total` via `len()`, falls back to indeterminate mode, always leaves the bar in a final state.
- `Component.COUNT`, `Component.ELAPSED`, `Component.RATE`, `Component.ETA` readouts. Rate is an exponentially weighted moving average with O(1) state; ETA derives from it.
- Redraw throttling: `ProgressBar(refresh_rate=30.0)` caps draws per second. Updates between draws only bump counters; `finish()` always draws the final frame. Pass `0` to redraw on every update.
- Indeterminate mode: `ProgressBar(total=None)`. `BAR` renders a bouncing segment, `PERCENT` and `ETA` show `--`, `COUNT` shows a plain count.
- `ProgressBar.write(message)`: print a line above the live bar, then redraw it.
- `ProgressBar(transient=True)`: erase the bar on finish instead of moving to the next line.
- Terminal width truncation: rendered lines are cut to the terminal width (ANSI-aware) at each drawn frame, preventing wrap corruption.
- Windows 10+ ANSI support: `supports_color()` enables virtual terminal processing via stdlib `ctypes`; consoles that reject it fall back to plain output.
- Presets ship in the `progz.presets` namespace (`progz.presets.SHIMMER`, `ASCII`, `BLOCKS`, `MINIMAL`, `RAINBOW`). The top-level import stays limited to the core API: `ProgressBar`, `track`, `Style`, `Component`, `RGB`.
- `BLOCKS` preset and `Style.block_chars`: eighth-block sub-cell fill for 8 visible states per bar cell.
- `MINIMAL` preset: bar plus percent.
- `DETAILED` preset: every readout at once (spinner, bar, percent, count, rate, ETA, elapsed) for long-running jobs.
- `RAINBOW` preset: interpolated multi-color gradient painted across the bar.
- `benchmarks/bench.py`: import time, per-update cost with and without draw, frame render cost. Stdlib only.
- Import-time regression test in CI, enforcing the weightless-import claim.
- Property-based tests (`hypothesis`, dev extra) for `render_frame()` invariants and `Style` validation.
- `Style.color_stops`: map progress percentages or ranges to bar fill colors via `(threshold, (r, g, b))` stops. Invalid stops raise `ValueError`.
- `Style.interpolate`: blend colors linearly between adjacent stops.
- `Style.color_by_position`: color each bar cell by its own position instead of current progress, so a finished bar shows every color of the journey.
- `RGB` type alias, exported from `progz`.
- `Component` enum and `Style.layout` for composable layouts. Stack `SPINNER`, `BAR`, `TEXT`, `PERCENT`, and `DESCRIPTION` in any order.
- `Component.PERCENT`: compact percentage readout.
- `Component.TEXT` with `Style.fill_text`: a fixed string rendered with the shimmer wave.

### Documentation
- README gallery: GIF recordings of the presets, numeric readouts, indeterminate mode, and `bar.write()`.

### Changed
- `ProgressBar` redraws are throttled by default (30 Hz). Set `refresh_rate=0` to restore draw-on-every-update.
- `ProgressBar.total` and the `total` parameter are now `int | None`.
- `__version__` is resolved lazily so `import progz` skips the package metadata read.
- Replaced `Style.show_spinner: bool` with the `layout` tuple. To hide the spinner, omit `Component.SPINNER` from `layout` (for example `layout=(Component.BAR, Component.DESCRIPTION)`).
- `ASCII` preset now uses `layout=(Component.BAR, Component.DESCRIPTION)`.

### Removed
- `Style.show_spinner`. Use `layout` instead.

### Fixed
- An exception inside a `with ProgressBar(...)` block no longer forces the bar to 100%. The bar stays at its current progress and moves to the next line, so failed runs do not display as complete.
- A bar with `total=0` now renders as complete (full bar, 100%) instead of empty at 0%.

## [0.1.2] - 2026-07-07

### Documentation
- Add PyPI version badge to README
- Fix `Style` field types in README (`tuple` → `tuple[int, int, int]`, full `spinner_frames` list)
- Add `set_description()` example
- Note `file=sys.stdout` option on `ProgressBar`
- Add `mypy` to Contributing steps

## [0.1.1] - 2026-07-07

### Added
- `ProgressBar` with context manager and manual API
- `Style` dataclass for full visual customization
- `SHIMMER` preset: Unicode `━`/`─` with sine-wave shimmer gradient
- `ASCII` preset: `#`/`-` for terminals without Unicode or color support
- Braille spinner tied to elapsed time
- Zero dependencies (stdlib only)
- Python 3.10+ type hints throughout
