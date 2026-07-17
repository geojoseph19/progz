# Changelog

All notable changes to progz are documented here.

## [Unreleased]

### Added
- `Component` enum and `Style.layout` for composable layouts. Stack `SPINNER`, `BAR`, `TEXT`, `PERCENT`, and `DESCRIPTION` in any order.
- `Component.PERCENT`: compact percentage readout.
- `Component.TEXT` with `Style.fill_text`: a fixed string rendered with the shimmer wave.

### Changed
- Replaced `Style.show_spinner: bool` with the `layout` tuple. To hide the spinner, omit `Component.SPINNER` from `layout` (for example `layout=(Component.BAR, Component.DESCRIPTION)`).
- `ASCII` preset now uses `layout=(Component.BAR, Component.DESCRIPTION)`.

### Removed
- `Style.show_spinner`. Use `layout` instead.

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
