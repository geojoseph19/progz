"""progz: terminal progress bar."""

from importlib.metadata import version

from .progress import ProgressBar
from .styles import ASCII, SHIMMER, Style

__all__ = ["ProgressBar", "Style", "SHIMMER", "ASCII"]
__version__ = version("progz")
