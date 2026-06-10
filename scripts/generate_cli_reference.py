#!/usr/bin/env python3
"""Generate CLI reference documentation from oss-paper-ci --help output.

Usage:
    python scripts/generate_cli_reference.py --output docs/cli-reference.md
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


COMMANDS = [
    ("scan", "Scan a repository for reproducibility readiness."),
    ("reproduce", "Attempt to reproduce a paper repository."),
    ("capsule", "Capsule management (verify, inspect, diff)."),
    ("init", "Generate config or contract templates."),
    ("config", "Configuration management."),
    ("diff", "Compare two scan reports."),
    ("doctor", "Diagnose repository and environment."),
    ("graph", "Build and display evidence graph."),
    ("baseline", "Baseline management."),
    ("smoke", "Run smoke tests safely."),
    ("workspace", "Workspace management."),
    ("batch", "Batch scanning."),
    ("rules", "Rule pack management."),
    ("cache", "Cache management."),
    ("explain", "Explain a check or policy profile."),
    ("list-checks", "List all available checks."),
    ("validate-contract", "Validate a reproducibility contract."),
    ("comment", "Generate PR comment from scan results."),
    ("version", "Print version."),
]


def get_help(command: str | None = None) -> str:
    """Get help text for a command."""
    cmd = [sys.executable, "-m", "oss_paper_ci"]
    if command:
        cmd.append(command)
    cmd.append("--help")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=10,
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error getting help: {e}"


def generate_reference(output_path: str | None = None) -> str:
    """Generate the CLI reference markdown."""
    lines = ["# CLI Reference\n"]
    lines.append("Auto-generated from `oss-paper-ci --help` output.\n")

    # Main help
    lines.append("## Main\n")
    lines.append("```")
    lines.append(get_help(None))
    lines.append("```\n")

    # Subcommands
    for cmd_name, description in COMMANDS:
        lines.append(f"## `oss-paper-ci {cmd_name}`\n")
        lines.append(f"{description}\n")
        lines.append("```")
        lines.append(get_help(cmd_name))
        lines.append("```\n")

    text = "\n".join(lines)

    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
        print(f"CLI reference written to {output_path}")
    else:
        print(text)

    return text


def main():
    parser = argparse.ArgumentParser(description="Generate CLI reference docs")
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    generate_reference(args.output)


if __name__ == "__main__":
    main()
