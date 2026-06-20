"""Tests for release artifact verification."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def test_verify_artifacts_pass(tmp_path: Path) -> None:
    """Verification passes for correct artifacts."""
    # Create artifact
    artifact = tmp_path / "release.zip"
    content = b"fake release content"
    artifact.write_bytes(content)

    # Create SHA256SUMS
    sha256 = hashlib.sha256(content).hexdigest()
    sums_file = tmp_path / "SHA256SUMS"
    sums_file.write_text(f"{sha256}  release.zip\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "trust", "verify-artifacts", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["ok"] is True
    assert "release.zip" in data["verified"]


def test_verify_artifacts_fail(tmp_path: Path) -> None:
    """Verification fails for tampered artifacts."""
    # Create artifact
    artifact = tmp_path / "release.zip"
    artifact.write_bytes(b"original content")

    # Create SHA256SUMS with wrong hash
    sums_file = tmp_path / "SHA256SUMS"
    sums_file.write_text("0000000000000000000000000000000000000000000000000000000000000000  release.zip\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "trust", "verify-artifacts", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 1  # Fail
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert len(data["failed"]) > 0


def test_verify_artifacts_missing(tmp_path: Path) -> None:
    """Verification warns about missing artifacts."""
    sums_file = tmp_path / "SHA256SUMS"
    sums_file.write_text("abc123  nonexistent.zip\n", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "trust", "verify-artifacts", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert "nonexistent.zip" in data["missing"]


def test_verify_artifacts_markdown(tmp_path: Path) -> None:
    """Verification markdown output works."""
    sums_file = tmp_path / "SHA256SUMS"
    sums_file.write_text("", encoding="utf-8")

    result = subprocess.run(
        ["oss-paper-ci", "trust", "verify-artifacts", str(tmp_path), "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0
    assert "Artifact Verification Report" in result.stdout


def test_verify_artifacts_no_checksums(tmp_path: Path) -> None:
    """Verification warns when no SHA256SUMS file found."""
    result = subprocess.run(
        ["oss-paper-ci", "trust", "verify-artifacts", str(tmp_path), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 1
    data = json.loads(result.stdout)
    assert data["ok"] is False
    assert any("SHA256SUMS" in w for w in data["warnings"])
