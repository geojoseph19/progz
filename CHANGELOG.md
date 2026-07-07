# Changelog

All notable changes to progz are documented here.

## [0.1.1] - 2026-07-07

### Fixed
- Remove unused `type: ignore` comment in `terminal.py` (mypy strict compliance)

## [0.1.0] - 2026-07-07

### Added
- `ProgressBar` with context manager and manual API
- `Style` dataclass for full visual customization
- `SHIMMER` preset: Unicode `━`/`─` with sine-wave shimmer gradient
- `ASCII` preset: `#`/`-` for terminals without Unicode or color support
- Braille spinner tied to elapsed time
- Zero dependencies (stdlib only)
- Python 3.10+ type hints throughout
