"""progz: terminal progress bar."""

from importlib.metadata import version

from .progress import ProgressBar
from .styles import ASCII, SHIMMER, Component, Style

__all__ = ["ProgressBar", "Style", "SHIMMER", "ASCII", "Component"]
__version__ = version("progz")
