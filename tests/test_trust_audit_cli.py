"""Tests for trust audit CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from oss_paper_ci.cli import main


def test_trust_audit_markdown(tmp_path: Path) -> None:
    """Trust audit markdown output works."""
    # Use oss-paper-ci entry point instead of python -m
    result = subprocess.run(
        ["oss-paper-ci", "trust", "audit", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "Trust & Supply-Chain Security Report" in result.stdout
    assert "Summary" in result.stdout
    assert "Limitations" in result.stdout


def test_trust_audit_json(tmp_path: Path) -> None:
    """Trust audit JSON output is valid."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "audit", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["schema_version"] == "0.1"
    assert data["report_type"] == "oss-paper-ci-trust-report"
    assert "summary" in data
    assert "findings" in data
    assert "limitations" in data


def test_trust_audit_html(tmp_path: Path) -> None:
    """Trust audit HTML output is self-contained."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "audit", str(tmp_path), "--format", "html"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "<!DOCTYPE html>" in result.stdout
    assert "cdn" not in result.stdout.lower()
    assert "googleapis" not in result.stdout.lower()


def test_trust_audit_output_file(tmp_path: Path) -> None:
    """Trust audit can write to file."""
    output_file = tmp_path / "report.md"
    result = subprocess.run(
        ["oss-paper-ci", "trust", "audit", str(tmp_path), "--output", str(output_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert output_file.exists()
    content = output_file.read_text(encoding="utf-8")
    assert "Trust & Supply-Chain Security Report" in content


def test_trust_audit_current_repo() -> None:
    """Trust audit works on current repository."""
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["oss-paper-ci", "trust", "audit", str(repo_root), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "inventory" in data
    assert "workflow_audit" in data
    assert "provenance" in data
