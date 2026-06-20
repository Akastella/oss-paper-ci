"""Tests for dependency inventory."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_inventory_json(tmp_path: Path) -> None:
    """Inventory JSON output is valid."""
    # Create minimal pyproject.toml
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "test-pkg"\nversion = "1.0.0"\ndependencies = ["requests>=2.0"]\n',
        encoding="utf-8",
    )

    result = subprocess.run(
        ["oss-paper-ci", "trust", "inventory", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["report_type"] == "oss-paper-ci-dependency-inventory"
    assert data["project"]["name"] == "test-pkg"
    assert "requests>=2.0" in data["dependencies"]["runtime"]


def test_inventory_markdown(tmp_path: Path) -> None:
    """Inventory markdown output works."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "inventory", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "Dependency Inventory" in result.stdout
    assert "Limitations" in result.stdout


def test_inventory_current_repo() -> None:
    """Inventory works on current repository."""
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["oss-paper-ci", "trust", "inventory", str(repo_root), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["project"]["name"] == "oss-paper-ci"
    assert "pyyaml>=6.0" in data["dependencies"]["runtime"]
    assert "rich>=13.0" in data["dependencies"]["runtime"]
    assert "github-actions" in data["ecosystems_detected"]
    assert "python" in data["ecosystems_detected"]


def test_inventory_output_file(tmp_path: Path) -> None:
    """Inventory can write to file."""
    output_file = tmp_path / "inventory.json"
    result = subprocess.run(
        ["oss-paper-ci", "trust", "inventory", str(tmp_path), "--format", "json", "--output", str(output_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert output_file.exists()
    data = json.loads(output_file.read_text(encoding="utf-8"))
    assert "schema_version" in data
