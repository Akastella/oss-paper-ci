"""Matrix report generation: Markdown, JSON, HTML."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from oss_paper_ci.matrix import MatrixPlan, MatrixResult

_STATUS_EMOJI = {
    "passed": "✅",
    "failed": "❌",
    "unavailable": "❓",
    "planned": "📋",
    "pending": "⏳",
}


def generate_matrix_plan_markdown(plan: MatrixPlan, output_path: str | None = None) -> str:
    """Generate matrix plan as markdown."""
    lines: list[str] = []
    lines.append("# Matrix Plan")
    lines.append("")
    lines.append(f"**Repo:** `{plan.repo}`")
    if plan.config:
        lines.append(f"**Config:** `{plan.config}`")
    lines.append("")
    lines.append("## Variants")
    lines.append("")
    lines.append("| Variant | Python | Profile | Available |")
    lines.append("|---------|--------|---------|-----------|")
    for v in plan.variants:
        avail = "✅" if v.available else "❌"
        lines.append(f"| {v.variant_id} | {v.python_version or '-'} | {v.profile or '-'} | {avail} |")
    lines.append("")

    if plan.warnings:
        lines.append("## Warnings")
        for w in plan.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    text = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_matrix_result_markdown(result: MatrixResult, output_path: str | None = None) -> str:
    """Generate matrix result as markdown."""
    lines: list[str] = []
    lines.append("# Matrix Report")
    lines.append("")
    lines.append(f"**Repo:** `{result.repo}`")
    if result.config:
        lines.append(f"**Config:** `{result.config}`")
    lines.append("")

    # Summary
    s = result.summary
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|-------|")
    for key, val in s.items():
        lines.append(f"| {key.title()} | {val} |")
    lines.append("")

    # Variants
    lines.append("## Variants")
    lines.append("")
    lines.append("| Variant | Status | Session |")
    lines.append("|---------|--------|---------|")
    for v in result.variants:
        emoji = _STATUS_EMOJI.get(v.status, "")
        lines.append(f"| {v.variant_id} | {emoji} {v.status} | `{v.session_dir}` |")
    lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        for w in result.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    text = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_matrix_compare_markdown(
    matrix_dir: str,
    output_path: str | None = None,
) -> str:
    """Compare matrix variants and generate a comparison report.

    Args:
        matrix_dir: Path to the matrix output directory.
        output_path: Path to write the report.

    Returns:
        Markdown comparison report.
    """
    from oss_paper_ci.session_store import load_session

    lines: list[str] = []
    lines.append("# Matrix Comparison")
    lines.append("")

    base = Path(matrix_dir)
    if not base.exists():
        lines.append("Matrix directory not found.")
        text = "\n".join(lines)
        if output_path:
            Path(output_path).write_text(text, encoding="utf-8")
        return text

    # Load all variant sessions
    variants: list[dict[str, Any]] = []
    for d in sorted(base.iterdir()):
        if d.is_dir() and (d / "session.json").exists():
            try:
                manifest = load_session(str(d))
                variants.append({
                    "variant": d.name,
                    "status": manifest.status,
                    "summary": manifest.summary.to_dict(),
                    "commands": manifest.commands,
                })
            except Exception:
                pass

    if not variants:
        lines.append("No variant sessions found.")
        text = "\n".join(lines)
        if output_path:
            Path(output_path).write_text(text, encoding="utf-8")
        return text

    # Summary comparison table
    lines.append("## Summary Comparison")
    lines.append("")

    # Get all keys from summaries
    all_keys: set[str] = set()
    for v in variants:
        all_keys.update(v["summary"].keys())

    header = "| Variant | " + " | ".join(sorted(all_keys)) + " |"
    sep = "|---------|" + "|".join(["---"] * len(all_keys)) + "|"
    lines.append(header)
    lines.append(sep)

    for v in variants:
        vals = [str(v["summary"].get(k, 0)) for k in sorted(all_keys)]
        lines.append(f"| {v['variant']} | " + " | ".join(vals) + " |")
    lines.append("")

    # Command-level comparison
    lines.append("## Command Comparison")
    lines.append("")

    # Get all command IDs
    all_cmd_ids: set[str] = set()
    for v in variants:
        for cmd in v["commands"]:
            all_cmd_ids.add(cmd.command_id)

    if all_cmd_ids:
        header = "| Command | " + " | ".join(v["variant"] for v in variants) + " |"
        sep = "|---------|" + "|".join(["---"] * len(variants)) + "|"
        lines.append(header)
        lines.append(sep)

        for cmd_id in sorted(all_cmd_ids):
            statuses = []
            for v in variants:
                cmd = next((c for c in v["commands"] if c.command_id == cmd_id), None)
                if cmd:
                    emoji = _STATUS_EMOJI.get(cmd.status, "")
                    statuses.append(f"{emoji} {cmd.status}")
                else:
                    statuses.append("-")
            lines.append(f"| {cmd_id} | " + " | ".join(statuses) + " |")
        lines.append("")

    text = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text


def generate_matrix_json(result: MatrixResult, output_path: str | None = None) -> str:
    """Generate matrix result as JSON."""
    data = result.to_dict()
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if output_path:
        Path(output_path).write_text(text, encoding="utf-8")
    return text
