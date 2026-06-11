"""Theme system for terminal output.

Defines color palettes and style presets for different output contexts.
All themes produce identical plain-text structure; only decoration differs.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Theme:
    """Color and style configuration for terminal output."""
    name: str
    description: str

    # Status colors (used for PASS/FAIL/WARN/SKIP)
    color_pass: str = "green"
    color_fail: str = "red"
    color_warn: str = "yellow"
    color_skip: str = "dim"
    color_info: str = "blue"

    # Structural colors
    color_title: str = "bold cyan"
    color_heading: str = "bold"
    color_border: str = "dim"
    color_accent: str = "cyan"
    color_muted: str = "dim"

    # Score colors
    color_score_high: str = "green"     # >= 80
    color_score_mid: str = "yellow"     # 50-79
    color_score_low: str = "red"        # < 50

    # Status symbols (plain text fallbacks)
    icon_pass: str = "[PASS]"
    icon_fail: str = "[FAIL]"
    icon_warn: str = "[WARN]"
    icon_skip: str = "[SKIP]"
    icon_info: str = "[INFO]"

    # Unicode symbols (only used when color is active)
    symbol_pass: str = "OK"
    symbol_fail: str = "X"
    symbol_warn: str = "!"
    symbol_skip: str = "-"
    symbol_info: str = "i"

    # Spinner frames
    spinner_frames: tuple[str, ...] = ("|", "/", "-", "\\")
    spinner_interval: float = 0.1

    # Layout
    panel_width: int = 72
    indent: int = 2


# --- Built-in themes ---

CLASSIC = Theme(
    name="classic",
    description="Default theme with balanced colors and symbols.",
)

MINIMAL = Theme(
    name="minimal",
    description="Reduced decoration, suitable for CI logs.",
    color_pass="green",
    color_fail="red",
    color_warn="yellow",
    color_skip="dim",
    color_info="blue",
    color_title="bold",
    color_heading="bold",
    color_border="dim",
    color_accent="",
    color_muted="dim",
    icon_pass="[PASS]",
    icon_fail="[FAIL]",
    icon_warn="[WARN]",
    icon_skip="[SKIP]",
    icon_info="[INFO]",
    symbol_pass="OK",
    symbol_fail="X",
    symbol_warn="!",
    symbol_skip="-",
    symbol_info="i",
    spinner_frames=("|", "/", "-", "\\"),
    panel_width=72,
    indent=2,
)

CONTRAST = Theme(
    name="contrast",
    description="High contrast for accessibility.",
    color_pass="bold green",
    color_fail="bold red",
    color_warn="bold yellow",
    color_skip="dim",
    color_info="bold blue",
    color_title="bold white",
    color_heading="bold white",
    color_border="white",
    color_accent="bold cyan",
    color_muted="white",
    icon_pass="[PASS]",
    icon_fail="[FAIL]",
    icon_warn="[WARN]",
    icon_skip="[SKIP]",
    icon_info="[INFO]",
    symbol_pass="OK",
    symbol_fail="X",
    symbol_warn="!",
    symbol_skip="-",
    symbol_info="i",
    spinner_frames=("|", "/", "-", "\\"),
    panel_width=72,
    indent=2,
)


THEMES: dict[str, Theme] = {
    "classic": CLASSIC,
    "minimal": MINIMAL,
    "contrast": CONTRAST,
}


def get_theme(name: str = "classic") -> Theme:
    """Get a theme by name. Falls back to classic."""
    return THEMES.get(name, CLASSIC)


def list_themes() -> list[dict[str, str]]:
    """Return theme metadata for display."""
    return [
        {"name": t.name, "description": t.description}
        for t in THEMES.values()
    ]
