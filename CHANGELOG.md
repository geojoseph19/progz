# Changelog

All notable changes to progz are documented here.

## [Unreleased]

### Added
- `Style.color_stops`: map progress percentages or ranges to bar fill colors via `(threshold, (r, g, b))` stops. Invalid stops raise `ValueError`.
- `Style.interpolate`: blend colors linearly between adjacent stops.
- `Style.color_by_position`: color each bar cell by its own position instead of current progress, so a finished bar shows every color of the journey.
- `RGB` type alias, exported from `progz`.
- `Component` enum and `Style.layout` for composable layouts. Stack `SPINNER`, `BAR`, `TEXT`, `PERCENT`, and `DESCRIPTION` in any order.
- `Component.PERCENT`: compact percentage readout.
- `Component.TEXT` with `Style.fill_text`: a fixed string rendered with the shimmer wave.

### Changed
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
