"""Tests for the CLI entry point."""

import subprocess
import sys
from pathlib import Path

import pytest


FIXTURES = Path(__file__).parent / "fixtures"
BAD_REPO = FIXTURES / "minimal_bad_repo"
GOOD_REPO = FIXTURES / "paper_ready_repo"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Run the CLI as a subprocess."""
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True,
        text=True,
        timeout=30,
        encoding="utf-8",
        errors="replace",
    )


class TestVersionCommand:
    def test_version_output(self):
        result = run_cli("version")
        assert result.returncode == 0
        assert "oss-paper-ci" in result.stdout

    def test_version_flag(self):
        result = run_cli("--version")
        assert result.returncode == 0
        assert "oss-paper-ci" in result.stdout


class TestInitCommand:
    def test_init_creates_config(self, tmp_path):
        import os
        cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = run_cli("init")
            assert result.returncode == 0
            assert (tmp_path / ".oss-paper-ci.yml").exists()
        finally:
            os.chdir(cwd)

    def test_init_refuses_overwrite(self, tmp_path):
        import os
        cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            (tmp_path / ".oss-paper-ci.yml").write_text("existing")
            result = run_cli("init")
            assert result.returncode == 1
        finally:
            os.chdir(cwd)


class TestExplainCommand:
    def test_explain_known_check(self):
        result = run_cli("explain", "META001")
        assert result.returncode == 0
        assert "META001" in result.stdout
        assert "README" in result.stdout

    def test_explain_unknown_check(self):
        result = run_cli("explain", "FAKE999")
        assert result.returncode == 1


class TestScanCommand:
    def test_scan_bad_repo_json(self):
        result = run_cli("scan", str(BAD_REPO), "--format", "json")
        # Should complete without crash
        assert result.returncode in (0, 1, 2)
        # Should produce valid JSON
        import json
        data = json.loads(result.stdout)
        assert data["tool"] == "oss-paper-ci"
        assert "checks" in data
        assert "summary" in data

    def test_scan_bad_repo_markdown(self):
        result = run_cli("scan", str(BAD_REPO), "--format", "markdown")
        assert result.returncode in (0, 1, 2)
        assert "oss-paper-ci" in result.stdout

    def test_scan_good_repo_json(self):
        result = run_cli("scan", str(GOOD_REPO), "--format", "json")
        assert result.returncode in (0, 1, 2)
        import json
        data = json.loads(result.stdout)
        assert data["summary"]["score"] > 0

    def test_scan_good_repo_score_better_than_bad(self):
        bad = run_cli("scan", str(BAD_REPO), "--format", "json")
        good = run_cli("scan", str(GOOD_REPO), "--format", "json")
        import json
        bad_data = json.loads(bad.stdout)
        good_data = json.loads(good.stdout)
        assert good_data["summary"]["score"] >= bad_data["summary"]["score"]

    def test_scan_with_output_file(self, tmp_path):
        out = tmp_path / "report.json"
        result = run_cli("scan", str(BAD_REPO), "--format", "json", "--output", str(out))
        assert out.exists()
        import json
        data = json.loads(out.read_text())
        assert data["tool"] == "oss-paper-ci"

    def test_scan_nonexistent_path(self):
        result = run_cli("scan", "/nonexistent/path")
        assert result.returncode == 2

    def test_scan_with_config(self):
        result = run_cli("scan", str(GOOD_REPO), "--config", "nonexistent.yml")
        # Should still work with default config
        assert result.returncode in (0, 1, 2)


class TestNoCommand:
    def test_no_command_shows_help(self):
        result = run_cli()
        assert result.returncode == 0
