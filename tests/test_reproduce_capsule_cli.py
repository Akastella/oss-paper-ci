"""Tests for capsule CLI integration."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def _run_cli(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd or str(ROOT),
        timeout=180,
    )


class TestCapsuleHelp:
    """Test capsule command help."""

    def test_capsule_help(self):
        result = _run_cli("capsule", "--help")
        assert result.returncode == 0
        assert "verify" in result.stdout
        assert "inspect" in result.stdout
        assert "diff" in result.stdout

    def test_capsule_verify_help(self):
        result = _run_cli("capsule", "verify", "--help")
        assert result.returncode == 0

    def test_capsule_inspect_help(self):
        result = _run_cli("capsule", "inspect", "--help")
        assert result.returncode == 0

    def test_capsule_diff_help(self):
        result = _run_cli("capsule", "diff", "--help")
        assert result.returncode == 0


class TestReproduceCapsule:
    """Test reproduce --capsule integration."""

    def test_dry_run_capsule(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        result = _run_cli(
            "reproduce", str(demo), "--dry-run",
            "--capsule", str(capsule),
        )
        assert result.returncode == 0
        assert capsule.exists()

    def test_dry_run_capsule_verify(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        _run_cli("reproduce", str(demo), "--dry-run", "--capsule", str(capsule))
        result = _run_cli("capsule", "verify", str(capsule))
        assert result.returncode == 0
        assert "PASSED" in result.stdout

    def test_dry_run_capsule_inspect(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        _run_cli("reproduce", str(demo), "--dry-run", "--capsule", str(capsule))
        result = _run_cli("capsule", "inspect", str(capsule), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema_version"] == "0.1"

    def test_execute_capsule(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        result = _run_cli(
            "reproduce", str(demo),
            "--execute", "--install",
            "--capsule", str(capsule),
        )
        assert result.returncode == 0
        assert capsule.exists()


class TestCapsuleVerify:
    """Test capsule verify CLI."""

    def test_verify_nonexistent(self):
        result = _run_cli("capsule", "verify", "/nonexistent/capsule.zip")
        assert result.returncode != 0

    def test_verify_json_format(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        _run_cli("reproduce", str(demo), "--dry-run", "--capsule", str(capsule))
        result = _run_cli("capsule", "verify", str(capsule), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "ok" in data

    def test_verify_output_file(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        capsule = tmp_path / "test.zip"
        out = tmp_path / "verify.md"
        _run_cli("reproduce", str(demo), "--dry-run", "--capsule", str(capsule))
        result = _run_cli("capsule", "verify", str(capsule), "--format", "markdown", "--output", str(out))
        assert result.returncode == 0
        assert out.exists()


class TestCapsuleDiff:
    """Test capsule diff CLI."""

    def test_diff_two_capsules(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        old = tmp_path / "old.zip"
        new = tmp_path / "new.zip"
        _run_cli("reproduce", str(demo), "--dry-run", "--capsule", str(old))
        _run_cli("reproduce", str(demo), "--execute", "--install", "--capsule", str(new))
        result = _run_cli("capsule", "diff", str(old), str(new), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "old_mode" in data
