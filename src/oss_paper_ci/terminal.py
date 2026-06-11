"""Terminal detection and environment awareness.

Provides TTY detection, color support, CI detection, and animation gating.
All UI rendering should check these before using color or animation.
"""

from __future__ import annotations

import os
import sys


def is_tty(stream=None) -> bool:
    """Check if the given stream (default stdout) is a TTY."""
    if stream is None:
        stream = sys.stdout
    return hasattr(stream, "isatty") and stream.isatty()


def is_ci() -> bool:
    """Detect common CI environments."""
    ci_vars = [
        "CI", "GITHUB_ACTIONS", "TRAVIS", "CIRCLECI", "JENKINS_URL",
        "GITLAB_CI", "AZURE_PIPELINES_TEAMFOUNDATION", "BUILDKITE",
        "CODEBUILD_BUILD_ID", "TF_BUILD", "BITBUCKET_PIPELINE",
    ]
    return any(os.environ.get(v) for v in ci_vars)


def no_color_requested() -> bool:
    """Check if NO_COLOR convention is active or --no-color was passed."""
    if os.environ.get("NO_COLOR"):
        return True
    if os.environ.get("OSS_PAPER_CI_NO_COLOR", "").lower() in ("1", "true", "yes"):
        return True
    return False


def no_animate_requested() -> bool:
    """Check if animation should be disabled."""
    if os.environ.get("OSS_PAPER_CI_NO_ANIMATE", "").lower() in ("1", "true", "yes"):
        return True
    if is_ci():
        return True
    return False


def plain_mode_requested() -> bool:
    """Check if plain mode is forced via environment."""
    if os.environ.get("OSS_PAPER_CI_PLAIN", "").lower() in ("1", "true", "yes"):
        return True
    return False


def supports_color(stream=None) -> bool:
    """Determine if the terminal supports color output."""
    if no_color_requested():
        return False
    if plain_mode_requested():
        return False
    if is_ci():
        return False
    if not is_tty(stream):
        return False
    # Windows: modern terminals (Windows Terminal, ConEmu, mintty) support ANSI
    if sys.platform == "win32":
        # Windows Terminal and ConEmu set these
        if os.environ.get("WT_SESSION") or os.environ.get("ConEmuPID"):
            return True
        # Check if ANSICON is set (older Windows)
        if os.environ.get("ANSICON"):
            return True
        # Try to enable ANSI on Windows 10+
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Enable virtual terminal processing
            handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
            mode = ctypes.c_ulong()
            kernel32.GetConsoleMode(handle, ctypes.byref(mode))
            if mode.value & 0x0004:  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                return True
            # Try to enable it
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
            return True
        except Exception:
            return False
    # Unix: check TERM
    term = os.environ.get("TERM", "")
    if term == "dumb":
        return False
    return True


def supports_animation(stream=None) -> bool:
    """Check if animation (spinners, progress) should be shown."""
    if no_animate_requested():
        return False
    if plain_mode_requested():
        return False
    if not is_tty(stream):
        return False
    return supports_color(stream)


class OutputMode:
    """Resolved output mode based on environment and flags."""

    def __init__(
        self,
        plain: bool = False,
        no_color: bool = False,
        no_animate: bool = False,
    ):
        self._plain = plain
        self._no_color = no_color
        self._no_animate = no_animate

    @property
    def plain(self) -> bool:
        return self._plain or plain_mode_requested()

    @property
    def use_color(self) -> bool:
        if self._no_color or self.plain:
            return False
        return supports_color()

    @property
    def use_animation(self) -> bool:
        if self._no_animate or self.plain:
            return False
        return supports_animation()

    @property
    def use_rich(self) -> bool:
        if self.plain:
            return False
        if not self.use_color:
            return False
        try:
            import rich  # noqa: F401
            return True
        except ImportError:
            return False

    @property
    def is_interactive(self) -> bool:
        return is_tty() and not is_ci() and not self.plain


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    import re
    ansi_escape = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\].*?\x07")
    return ansi_escape.sub("", text)
