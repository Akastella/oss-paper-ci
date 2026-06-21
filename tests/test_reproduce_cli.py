"""Tests for the reproduce CLI subcommand."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def _run_cli(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    """Run oss-paper-ci CLI."""
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd or str(ROOT),
        timeout=120,
    )


class TestReproduceHelp:
    """Test reproduce command help."""

    def test_reproduce_help(self):
        result = _run_cli("reproduce", "--help")
        assert result.returncode == 0
        # Now a subcommand group -- should list available subcommands
        assert "run" in result.stdout


class TestReproduceDryRun:
    """Test reproduce dry-run mode (default, no --dry-run flag)."""

    def test_dry_run_local_path(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", "run", str(demo))
        assert result.returncode == 0

    def test_dry_run_markdown_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", "run", str(demo), "--format", "markdown")
        assert result.returncode == 0
        assert "Reproduction Run Report" in result.stdout

    def test_dry_run_json_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", "run", str(demo), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["dry_run"] is True

    def test_dry_run_html_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", "run", str(demo), "--format", "html")
        assert result.returncode == 0
        assert "<!DOCTYPE html>" in result.stdout

    def test_dry_run_output_file(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        out = tmp_path / "report.md"
        result = _run_cli(
            "reproduce", "run", str(demo),
            "--format", "markdown", "--output", str(out),
        )
        assert result.returncode == 0
        assert out.exists()
        assert "Reproduction Run Report" in out.read_text(encoding="utf-8")

    def test_dry_run_does_not_execute(self, tmp_path):
        """Verify dry-run does not actually run commands."""
        marker = tmp_path / "marker.txt"
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "train.py").write_text(
            f"Path('{marker.as_posix()}').write_text('executed')"
        )
        (tmp_path / "requirements.txt").write_text("")
        (tmp_path / "reproducibility.yml").write_text(
            "reproduction:\n  commands:\n    - id: train\n      run: python scripts/train.py\n"
        )

        result = _run_cli("reproduce", "run", str(tmp_path))
        assert result.returncode == 0
        assert not marker.exists()


class TestReproduceExecute:
    """Test reproduce execute mode."""

    def test_execute_demo_repo(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli(
            "reproduce", "run", str(demo),
            "--execute",
            "--format", "json",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data["command_results"]) > 0

    def test_execute_with_output(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        out = tmp_path / "report.json"
        result = _run_cli(
            "reproduce", "run", str(demo),
            "--execute",
            "--format", "json", "--output", str(out),
        )
        assert result.returncode == 0
        assert out.exists()


class TestReproduceEdgeCases:
    """Test edge cases."""

    def test_nonexistent_path(self):
        result = _run_cli("reproduce", "run", "/nonexistent/path")
        assert result.returncode != 0

    def test_version_includes_reproduce(self):
        result = _run_cli("reproduce", "--help")
        assert result.returncode == 0
