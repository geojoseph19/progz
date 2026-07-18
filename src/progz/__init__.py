"""progz: terminal progress bar."""

from .progress import ProgressBar
from .styles import ASCII, BLOCKS, MINIMAL, RAINBOW, RGB, SHIMMER, Component, Style
from .track import track

__all__ = [
    "ProgressBar",
    "track",
    "Style",
    "Component",
    "RGB",
    "SHIMMER",
    "ASCII",
    "BLOCKS",
    "MINIMAL",
    "RAINBOW",
]


def __getattr__(name: str) -> str:
    # Lazy so importing progz never pays the metadata read.
    if name == "__version__":
        from importlib.metadata import version

        return version("progz")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
