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
        assert "URL" in result.stdout or "url" in result.stdout.lower()


class TestReproduceDryRun:
    """Test reproduce dry-run mode."""

    def test_dry_run_local_path(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", str(demo), "--dry-run")
        assert result.returncode == 0
        assert "dry-run" in result.stdout.lower()

    def test_dry_run_markdown_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", str(demo), "--dry-run", "--format", "markdown")
        assert result.returncode == 0
        assert "Reproduction Attempt Report" in result.stdout

    def test_dry_run_json_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", str(demo), "--dry-run", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["dry_run"] is True

    def test_dry_run_html_format(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli("reproduce", str(demo), "--dry-run", "--format", "html")
        assert result.returncode == 0
        assert "<!DOCTYPE html>" in result.stdout

    def test_dry_run_output_file(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        out = tmp_path / "report.md"
        result = _run_cli(
            "reproduce", str(demo), "--dry-run",
            "--format", "markdown", "--output", str(out),
        )
        assert result.returncode == 0
        assert out.exists()
        assert "Reproduction Attempt Report" in out.read_text(encoding="utf-8")

    def test_dry_run_does_not_execute(self, tmp_path):
        """Verify dry-run does not actually run commands."""
        marker = tmp_path / "marker.txt"
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "train.py").write_text(
            f"Path('{marker.as_posix()}').write_text('executed')"
        )
        (tmp_path / "requirements.txt").write_text("")

        result = _run_cli("reproduce", str(tmp_path), "--dry-run")
        assert result.returncode == 0
        assert not marker.exists()


class TestReproduceExecute:
    """Test reproduce execute mode."""

    def test_execute_demo_repo(self):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        result = _run_cli(
            "reproduce", str(demo),
            "--execute", "--install",
            "--format", "json",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["clone_ok"] is True
        assert len(data["command_results"]) > 0

    def test_execute_with_output(self, tmp_path):
        demo = ROOT / "examples" / "demo-reproduce-repo"
        out = tmp_path / "report.json"
        result = _run_cli(
            "reproduce", str(demo),
            "--execute", "--install",
            "--format", "json", "--output", str(out),
        )
        assert result.returncode == 0
        assert out.exists()


class TestReproducePaperUrl:
    """Test reproduce with paper URLs."""

    def test_paper_url_without_repo(self):
        result = _run_cli("reproduce", "https://arxiv.org/abs/2301.00001")
        assert result.returncode != 0
        assert "--repo" in result.stdout or "--repo" in result.stderr


class TestReproduceEdgeCases:
    """Test edge cases."""

    def test_nonexistent_path(self):
        result = _run_cli("reproduce", "/nonexistent/path")
        assert result.returncode != 0

    def test_version_includes_reproduce(self):
        result = _run_cli("reproduce", "--help")
        assert result.returncode == 0
