"""CLI handlers for language adapter commands."""
from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any
from .adapters.registry import get_registry
from .adapters.schema import build_adapter_report, validate_report

def _format_detection_markdown(detections):
    lines = ["# Language Adapter Detection\n"]
    if not detections:
        lines.append("No language adapters detected.\n")
        return "\n".join(lines)
    lines.append(f"Detected **{len(detections)}** adapter(s):\n")
    for det in detections:
        lines.append(f"## {det['display_name']} (`{det['name']}`)\n")
        lines.append(f"- **Confidence**: {det['confidence']:.0%}")
        runtime = det.get("runtime", {})
        if runtime:
            avail = "available" if runtime.get("available") else "not available"
            lines.append(f"- **Runtime**: {runtime['name']} -- {avail}")
            if runtime.get("version"):
                lines.append(f"  - Version: {runtime['version']}")
        evidence = det.get("evidence", [])
        if evidence:
            lines.append(f"- **Evidence**: {', '.join(evidence[:5])}")
        limitations = det.get("limitations", [])
        if limitations:
            lines.append("- **Limitations**:")
            for lim in limitations:
                lines.append(f"  - {lim}")
        lines.append(f"- **Dry-run**: {'yes' if det.get('supports_dry_run') else 'no'}")
        lines.append(f"- **Execute**: {'yes' if det.get('supports_execute') else 'no'}")
        lines.append("")
    return "\n".join(lines)

def _format_plan_markdown(plan):
    lines = [f"# Adapter Plan: {plan['adapter_name']}\n"]
    install = plan.get("install_steps", [])
    if install:
        lines.append("## Install Steps\n")
        for i, step in enumerate(install, 1):
            desc = step.get("description", step["command"])
            lines.append(f"{i}. `{step['command']}` -- {desc}")
        lines.append("")
    run = plan.get("run_steps", [])
    if run:
        lines.append("## Run Steps\n")
        for i, step in enumerate(run, 1):
            desc = step.get("description", step["command"])
            lines.append(f"{i}. `{step['command']}` -- {desc}")
        lines.append("")
    warnings = plan.get("warnings", [])
    if warnings:
        lines.append("## Warnings\n")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")
    notes = plan.get("notes", [])
    if notes:
        lines.append("## Notes\n")
        for n in notes:
            lines.append(f"- {n}")
        lines.append("")
    return "\n".join(lines)

def cmd_adapters_list(fmt="text"):
    registry = get_registry()
    adapters = registry.list_adapters()
    if fmt == "json":
        print(json.dumps(adapters, indent=2))
    else:
        print(f"Registered language adapters ({len(adapters)}):\n")
        for a in adapters:
            execute = "yes" if a["supports_execute"] else "no"
            dry_run = "yes" if a["supports_dry_run"] else "no"
            runtimes = ", ".join(a["requires_runtime"]) or "none"
            print(f"  {a['name']:<12} {a['display_name']:<20} execute={execute} dry-run={dry_run} runtime={runtimes}")
    return 0

def cmd_adapters_inspect(path, fmt="markdown", output=None):
    registry = get_registry()
    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2
    detections = registry.detect(repo_path)
    det_dicts = [d.to_dict() for d in detections]
    if fmt == "json":
        report = build_adapter_report(repo_path, det_dicts)
        text = json.dumps(report, indent=2)
    else:
        text = _format_detection_markdown(det_dicts)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Report written to {output}")
    else:
        print(text)
    return 0

def cmd_adapters_explain(adapter_name, fmt="markdown"):
    registry = get_registry()
    adapter = registry.get(adapter_name)
    if not adapter:
        print(f"Error: unknown adapter: {adapter_name}", file=sys.stderr)
        return 2
    if fmt == "json":
        info = {"name": adapter.name, "display_name": adapter.display_name, "aliases": adapter.aliases, "ecosystem": adapter.ecosystem, "supports_execute": adapter.supports_execute, "supports_dry_run": adapter.supports_dry_run, "requires_runtime": adapter.requires_runtime}
        print(json.dumps(info, indent=2))
    else:
        print(f"# {adapter.display_name} ({adapter.name})\n")
        if adapter.aliases:
            print(f"Aliases: {', '.join(adapter.aliases)}")
        print(f"Ecosystem: {adapter.ecosystem}")
        print(f"Supports execute: {'yes' if adapter.supports_execute else 'no'}")
        print(f"Supports dry-run: {'yes' if adapter.supports_dry_run else 'no'}")
        if adapter.requires_runtime:
            print(f"Required runtime: {', '.join(adapter.requires_runtime)}")
    return 0

def cmd_adapters_plan(path, fmt="markdown", output=None, adapter_name=None):
    registry = get_registry()
    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2
    try:
        plan = registry.plan(repo_path, adapter_name)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    plan_dict = plan.to_dict()
    if fmt == "json":
        text = json.dumps(plan_dict, indent=2)
    else:
        text = _format_plan_markdown(plan_dict)
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text, encoding="utf-8")
        print(f"Plan written to {output}")
    else:
        print(text)
    return 0

def cmd_adapters_validate(path):
    registry = get_registry()
    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2
    detections = registry.detect(repo_path)
    det_dicts = [d.to_dict() for d in detections]
    report = build_adapter_report(repo_path, det_dicts)
    errors = validate_report(report)
    if errors:
        print("Validation errors:")
        for err in errors:
            print(f"  - {err}")
        return 1
    print("Adapter report is valid.")
    return 0

def cmd_adapters_doctor(path):
    registry = get_registry()
    repo_path = Path(path).resolve()
    if not repo_path.exists():
        print(f"Error: path does not exist: {path}", file=sys.stderr)
        return 2
    detections = registry.detect(repo_path)
    print("Adapter Runtime Diagnostics\n")
    if not detections:
        print("No adapters detected for this repository.")
        return 0
    for det in detections:
        runtime = det.runtime
        if runtime:
            status = "available" if runtime.available else "not available"
            print(f"  {det.display_name}: {runtime.name} -- {status}")
            if runtime.version:
                print(f"    Version: {runtime.version}")
        else:
            print(f"  {det.display_name}: no runtime required")
    available = sum(1 for d in detections if d.runtime and d.runtime.available)
    total = len(detections)
    print(f"\n{available}/{total} detected adapters have runtimes available.")
    return 0
