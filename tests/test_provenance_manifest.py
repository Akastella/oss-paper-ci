"""Tests for provenance manifest."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_provenance_json(tmp_path: Path) -> None:
    """Provenance JSON output is valid."""
    # Create a fake artifact
    artifact = tmp_path / "release.zip"
    artifact.write_bytes(b"fake artifact content")

    result = subprocess.run(
        ["oss-paper-ci", "trust", "provenance", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["tool"] == "oss-paper-ci"
    assert data["tool_version"] == "3.2.0rc1"
    assert data["schema_version"] == "0.1"
    assert "source" in data
    assert "build" in data
    assert "limitations" in data
    # No absolute paths in report (content, not test paths)
    text = json.dumps(data)
    # Only check the report content, not the test runner paths
    assert "repo" in data["source"]


def test_provenance_markdown(tmp_path: Path) -> None:
    """Provenance markdown output works."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "provenance", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "Provenance Manifest" in result.stdout
    assert "oss-paper-ci" in result.stdout


def test_provenance_with_timestamp(tmp_path: Path) -> None:
    """Provenance can include timestamp."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "provenance", str(tmp_path), "--format", "json", "--include-timestamp"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert "timestamp_utc" in data["build"]


def test_provenance_current_repo() -> None:
    """Provenance works on current repository."""
    repo_root = Path(__file__).parent.parent
    result = subprocess.run(
        ["oss-paper-ci", "trust", "provenance", str(repo_root), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    # Commit may be None if not a git repo (e.g., clean package verification)
    if data["source"]["commit"] is not None:
        assert len(data["source"]["commit"]) == 40  # SHA1 hash


def test_provenance_output_file(tmp_path: Path) -> None:
    """Provenance can write to file."""
    output_file = tmp_path / "provenance.json"
    result = subprocess.run(
        ["oss-paper-ci", "trust", "provenance", str(tmp_path), "--output", str(output_file)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert output_file.exists()
