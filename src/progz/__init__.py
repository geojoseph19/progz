"""progz: terminal progress bar."""

from importlib.metadata import version

from .progress import ProgressBar
from .styles import ASCII, RGB, SHIMMER, Component, Style

__all__ = ["ProgressBar", "Style", "SHIMMER", "ASCII", "Component", "RGB"]
__version__ = version("progz")
