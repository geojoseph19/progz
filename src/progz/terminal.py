"""Terminal detection and ANSI escape code helpers."""

import os
import sys

_vt_enabled: bool | None = None


def _enable_windows_vt() -> bool:
    """Enable ANSI escape processing on Windows 10+ consoles.

    Runs at most once per process; the result is cached. Returns False on
    consoles that reject virtual terminal processing, where ANSI output
    would show as escape garbage.
    """
    global _vt_enabled
    if _vt_enabled is None:
        _vt_enabled = False
        if sys.platform == "win32":
            import ctypes

            kernel32 = ctypes.windll.kernel32
            enable_vt = 0x0004  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
            for std_handle in (-11, -12):  # stdout, stderr
                handle = kernel32.GetStdHandle(std_handle)
                mode = ctypes.c_uint32()
                if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                    if kernel32.SetConsoleMode(handle, mode.value | enable_vt):
                        _vt_enabled = True
    return _vt_enabled


def supports_color(file: object) -> bool:
    """Return True if file supports ANSI color output.

    Honors NO_COLOR (disables, wins over everything), FORCE_COLOR
    (enables), and TERM=dumb (disables). On Windows, enables virtual
    terminal processing first and reports whether that succeeded.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not (hasattr(file, "isatty") and file.isatty()):
        return False
    if os.environ.get("TERM", "") == "dumb":
        return False
    if sys.platform == "win32":
        return _enable_windows_vt()
    return True


RESET = "\033[0m"
ERASE_LINE = "\033[2K"


def rgb(r: int, g: int, b: int) -> str:
    """24-bit foreground color escape sequence."""
    return f"\033[38;2;{r};{g};{b}m"
