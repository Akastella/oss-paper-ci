"""Terminal UI components.

Provides panels, status displays, progress indicators, tables, and
summary cards. All components degrade gracefully to plain text when
color or rich is unavailable.
"""

from __future__ import annotations

import sys
import time
import threading
from typing import TextIO

from oss_paper_ci.terminal import OutputMode
from oss_paper_ci.themes import Theme, get_theme


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _try_rich():
    """Try to import rich components. Returns (Console, Panel, Table) or None."""
    try:
        from rich.console import Console
        from rich.panel import Panel
        from rich.table import Table
        from rich.text import Text
        from rich import box
        return Console, Panel, Table, Text, box
    except ImportError:
        return None


def _status_icon(status: str, theme: Theme, mode: OutputMode) -> str:
    """Get status display text for a given status string."""
    mapping = {
        "pass": (theme.icon_pass, theme.symbol_pass, theme.color_pass),
        "fail": (theme.icon_fail, theme.symbol_fail, theme.color_fail),
        "warn": (theme.icon_warn, theme.symbol_warn, theme.color_warn),
        "skip": (theme.icon_skip, theme.symbol_skip, theme.color_skip),
        "info": (theme.icon_info, theme.symbol_info, theme.color_info),
    }
    plain_icon, _symbol, color = mapping.get(
        status.lower(), (f"[{status.upper()}]", status.upper(), "")
    )
    if mode.use_rich:
        return f"[{color}]{_symbol}[/{color}]"
    return plain_icon


def _score_color(score: int, theme: Theme) -> str:
    if score >= 80:
        return theme.color_score_high
    elif score >= 50:
        return theme.color_score_mid
    return theme.color_score_low


# ---------------------------------------------------------------------------
# High-level components
# ---------------------------------------------------------------------------

def render_title(
    title: str,
    subtitle: str = "",
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a top-level title banner."""
    theme = theme or get_theme()
    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, Panel, _Table, Text, box = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            text = Text(title, style=theme.color_title)
            if subtitle:
                text.append(f"\n{subtitle}", style=theme.color_muted)
            console.print(Panel(text, box=box.HEAVY, style=theme.color_border, expand=True))
            return
    # Plain fallback
    width = theme.panel_width
    stream.write("=" * width + "\n")
    stream.write(f"  {title}\n")
    if subtitle:
        stream.write(f"  {subtitle}\n")
    stream.write("=" * width + "\n")
    stream.flush()


def render_step(
    step_num: int,
    total: int,
    name: str,
    status: str,
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a single step in a multi-step workflow."""
    theme = theme or get_theme()
    prefix = f"[{step_num}/{total}]"
    icon = _status_icon(status, theme, mode)

    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, _P, _T, Text, _B = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            line = Text()
            line.append(f" {prefix} ", style=theme.color_muted)
            line.append(f"{name:<40}", style=theme.color_heading)
            line.append(f" {icon}")
            console.print(line)
            return

    # Plain fallback
    status_plain = {
        "pass": theme.icon_pass,
        "fail": theme.icon_fail,
        "warn": theme.icon_warn,
        "skip": theme.icon_skip,
        "info": theme.icon_info,
    }.get(status.lower(), f"[{status.upper()}]")
    stream.write(f" {prefix} {name:<40} {status_plain}\n")
    stream.flush()


def render_steps(
    steps: list[dict],
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render multiple steps. Each step dict: {name, status}."""
    total = len(steps)
    for i, step in enumerate(steps, 1):
        render_step(i, total, step["name"], step["status"], mode, theme, stream)


def render_panel(
    title: str,
    content: str,
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a titled content panel."""
    theme = theme or get_theme()
    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, Panel, _T, _Txt, box = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            console.print(Panel(content, title=title, box=box.ROUNDED, style=theme.color_border, expand=True))
            return
    # Plain fallback
    width = theme.panel_width
    stream.write(f"\n{'-' * width}\n")
    stream.write(f"  {title}\n")
    stream.write(f"{'-' * width}\n")
    for line in content.split("\n"):
        stream.write(f"  {line}\n")
    stream.write(f"{'-' * width}\n")
    stream.flush()


def render_table(
    headers: list[str],
    rows: list[list[str]],
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a table with aligned columns."""
    theme = theme or get_theme()
    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, _P, Table, _Txt, box = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style=theme.color_heading)
            for h in headers:
                table.add_column(h)
            for row in rows:
                table.add_row(*[str(c) for c in row])
            console.print(table)
            return
    # Plain fallback: fixed-width columns
    if not rows:
        return
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    # Header
    header_line = "  ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    stream.write(f"  {header_line}\n")
    sep_line = "  ".join("-" * col_widths[i] for i in range(len(headers)))
    stream.write(f"  {sep_line}\n")
    for row in rows:
        line = "  ".join(str(row[i]).ljust(col_widths[i]) if i < len(row) else "" for i in range(len(headers)))
        stream.write(f"  {line}\n")
    stream.flush()


def render_summary(
    items: list[dict],
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a summary panel. items: [{label, value, status?}]."""
    theme = theme or get_theme()
    lines = []
    for item in items:
        label = item["label"]
        value = item["value"]
        status = item.get("status")
        if status:
            icon = _status_icon(status, theme, mode)
            lines.append(f"{icon} {label}: {value}")
        else:
            lines.append(f"  {label}: {value}")
    content = "\n".join(lines)
    render_panel("Summary", content, mode, theme, stream)


def render_next_actions(
    actions: list[str],
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render suggested next actions."""
    theme = theme or get_theme()
    if not actions:
        return
    lines = []
    for i, action in enumerate(actions, 1):
        lines.append(f"  {i}. {action}")
    content = "\n".join(lines)
    render_panel("Suggested Next Actions", content, mode, theme, stream)


def render_score(
    score: int,
    components: dict[str, int] | None = None,
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render score display with optional component breakdown."""
    theme = theme or get_theme()
    color = _score_color(score, theme)

    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, _P, Table, Text, box = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            score_text = Text(f"Score: {score}/100", style=color)
            if components:
                table = Table(box=box.SIMPLE, show_header=True, header_style=theme.color_heading)
                table.add_column("Component")
                table.add_column("Score")
                for name, val in components.items():
                    c = _score_color(val, theme)
                    table.add_column()
                    table.add_row(name, Text(str(val), style=c))
                console.print(table)
            else:
                console.print(score_text)
            return
    # Plain fallback
    stream.write(f"  Score: {score}/100\n")
    if components:
        for name, val in components.items():
            stream.write(f"    {name}: {val}/100\n")
    stream.flush()


def render_warning(
    message: str,
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a warning message."""
    theme = theme or get_theme()
    icon = _status_icon("warn", theme, mode)
    if mode.use_rich:
        rich_mods = _try_rich()
        if rich_mods:
            Console, _P, _T, Text, _B = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            text = Text()
            text.append(f" {icon} ", style=theme.color_warn)
            text.append(message)
            console.print(text)
            return
    stream.write(f" {icon} {message}\n")
    stream.flush()


def render_error_card(
    what: str,
    why: str = "",
    next_steps: list[str] | None = None,
    retry_command: str = "",
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Render a structured error explanation card."""
    theme = theme or get_theme()
    lines = [f"What happened: {what}"]
    if why:
        lines.append(f"Why: {why}")
    if next_steps:
        lines.append("Suggested next steps:")
        for i, step in enumerate(next_steps, 1):
            lines.append(f"  {i}. {step}")
    if retry_command:
        lines.append(f"Retry: {retry_command}")
    content = "\n".join(lines)
    render_panel("Error", content, mode, theme, stream)


# ---------------------------------------------------------------------------
# Spinner
# ---------------------------------------------------------------------------

class Spinner:
    """Animated spinner for TTY, silent for non-TTY."""

    def __init__(
        self,
        message: str = "Working...",
        mode: OutputMode = OutputMode(),
        theme: Theme | None = None,
        stream: TextIO = sys.stdout,
    ):
        self.message = message
        self.mode = mode
        self.theme = theme or get_theme()
        self.stream = stream
        self._running = False
        self._thread: threading.Thread | None = None
        self._frame_index = 0

    def start(self) -> None:
        if not self.mode.use_animation:
            self.stream.write(f"  {self.message}...\n")
            self.stream.flush()
            return
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def _animate(self) -> None:
        frames = self.theme.spinner_frames
        interval = self.theme.spinner_interval
        while self._running:
            frame = frames[self._frame_index % len(frames)]
            self.stream.write(f"\r  {frame} {self.message}")
            self.stream.flush()
            self._frame_index += 1
            time.sleep(interval)

    def stop(self, final_message: str = "") -> None:
        if self._thread and self._running:
            self._running = False
            self._thread.join(timeout=1.0)
            # Clear spinner line
            self.stream.write(f"\r{' ' * (len(self.message) + 10)}\r")
            self.stream.flush()
        if final_message:
            self.stream.write(f"  {final_message}\n")
            self.stream.flush()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()
