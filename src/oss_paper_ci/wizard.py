"""Guided wizard for new users.

Provides non-blocking guided output that suggests safe next steps
based on the current repository state. In non-interactive environments,
prints recommended commands without waiting for input.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TextIO

from oss_paper_ci.terminal import OutputMode, is_tty, is_ci
from oss_paper_ci.themes import Theme, get_theme
from oss_paper_ci.ui import render_title, render_panel, render_next_actions


def _detect_repo_state(path: str = ".") -> dict:
    """Detect repository characteristics for wizard recommendations."""
    repo = Path(path)
    state = {
        "has_config": (repo / "oss-paper-ci.yml").exists() or (repo / "oss-paper-ci.yaml").exists(),
        "has_readme": (repo / "README.md").exists(),
        "has_data_dir": (repo / "data").is_dir(),
        "has_scripts_dir": (repo / "scripts").is_dir() or (repo / "src").is_dir(),
        "has_requirements": any(
            (repo / f).exists()
            for f in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile", "environment.yml"]
        ),
        "has_ci": (repo / ".github" / "workflows").is_dir(),
        "has_contract": (repo / "reproducibility.yml").exists(),
        "is_git": (repo / ".git").is_dir(),
    }
    return state


def _build_recommendations(state: dict) -> list[dict]:
    """Build wizard recommendations based on repo state."""
    steps = []

    # Always suggest starting with a scan
    steps.append({
        "title": "Check your repository",
        "description": "Scan for reproducibility readiness and get a score.",
        "command": "oss-paper-ci scan .",
        "safe": True,
    })

    if not state["has_config"]:
        steps.append({
            "title": "Create a configuration file",
            "description": "Generate a default oss-paper-ci.yml to customize checks.",
            "command": "oss-paper-ci init --dry-run",
            "safe": True,
        })

    if state["has_data_dir"]:
        steps.append({
            "title": "Check data documentation",
            "description": "Verify that your data directory has proper documentation.",
            "command": "oss-paper-ci data diagnose .",
            "safe": True,
        })

    if state["has_scripts_dir"]:
        steps.append({
            "title": "Validate result claims",
            "description": "Check that claimed results can be traced to evidence.",
            "command": "oss-paper-ci results validate .",
            "safe": True,
        })

    steps.append({
        "title": "Run the workbench",
        "description": "Run a full pipeline: scan + diagnose + validate + dossier.",
        "command": "oss-paper-ci workbench . --plain",
        "safe": True,
    })

    steps.append({
        "title": "Generate a reproducibility dossier",
        "description": "Create a human-readable summary of your repo's reproducibility.",
        "command": "oss-paper-ci dossier . --output dossier.md",
        "safe": True,
    })

    return steps


def run_wizard(
    path: str = ".",
    mode: OutputMode = OutputMode(),
    theme: Theme | None = None,
    stream: TextIO = sys.stdout,
) -> int:
    """Run the guided wizard.

    In interactive TTY mode, shows a formatted guide.
    In non-interactive mode, prints recommended commands.

    Returns exit code 0.
    """
    theme = theme or get_theme()
    state = _detect_repo_state(path)
    recommendations = _build_recommendations(state)

    # Title
    render_title(
        "OSS-Paper-CI Wizard",
        "Guided setup for reproducibility checking",
        mode, theme, stream,
    )

    # Repo info
    repo_info = []
    repo_info.append(f"Path: {os.path.abspath(path)}")
    if state["is_git"]:
        repo_info.append("Git: detected")
    if state["has_config"]:
        repo_info.append("Config: found")
    else:
        repo_info.append("Config: not found (will use defaults)")
    if state["has_data_dir"]:
        repo_info.append("Data directory: found")
    if state["has_ci"]:
        repo_info.append("CI: detected")

    render_panel("Repository", "\n".join(repo_info), mode, theme, stream)
    stream.write("\n")
    stream.flush()

    # Recommendations
    actions = []
    for step in recommendations:
        safe_marker = "" if step["safe"] else " (requires confirmation)"
        actions.append(f"{step['command']}{safe_marker}")
        if mode.plain or not mode.use_rich:
            stream.write(f"  {step['title']}: {step['description']}\n")
            stream.write(f"    $ {step['command']}\n\n")
            stream.flush()

    if mode.use_rich:
        rich_mods = None
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich import box
            rich_mods = (Console, Panel, Table, box)
        except ImportError:
            pass

        if rich_mods:
            Console, Panel, Table, box = rich_mods
            console = Console(file=stream, width=theme.panel_width)
            table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style=theme.color_heading)
            table.add_column("#", style=theme.color_muted, width=3)
            table.add_column("Step", style=theme.color_heading)
            table.add_column("Command", style=theme.color_accent)
            for i, step in enumerate(recommendations, 1):
                table.add_row(str(i), step["title"], step["command"])
            console.print(table)
            stream.write("\n")
            console.print(Panel(
                "These are safe, read-only commands. Nothing will be executed automatically.",
                title="Note",
                box=box.ROUNDED,
                style=theme.color_border,
            ))
            stream.flush()

    # Non-interactive note
    if not is_tty() or is_ci():
        stream.write("\n")
        stream.write("  Tip: Run these commands manually in your terminal.\n")
        stream.write("  Use --plain for machine-readable output.\n")
        stream.flush()

    return 0
