"""Tests for reproduce run CLI command."""

import json
import subprocess
import sys

import pytest

DEMO_REPO = "examples/repro-system-demo"


def run_cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True,
        text=True,
        timeout=120,
        encoding="utf-8",
        errors="replace",
    )


class TestReproduceRun:
    """Tests for reproduce run command."""

    def test_run_default_dry_run(self):
        """Default run should be dry-run (no execution)."""
        result = run_cli("reproduce", "run", DEMO_REPO)
        assert result.returncode == 0
        assert "dry_run" in result.stdout.lower() or "dry run" in result.stdout.lower() or "Dry run: Yes" in result.stdout

    def test_run_execute(self):
        """Run with --execute should actually execute commands."""
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local")
        assert result.returncode == 0
        assert "success" in result.stdout.lower()
        assert "train" in result.stdout
        assert "evaluate" in result.stdout

    def test_run_captures_stdout(self):
        """Run should capture command stdout."""
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local")
        assert result.returncode == 0
        assert "Training complete" in result.stdout

    def test_run_validates_artifacts(self):
        """Run should validate expected artifacts."""
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local")
        assert result.returncode == 0
        assert "Artifacts" in result.stdout
        assert "**Found:** 4" in result.stdout or "Found: 4" in result.stdout

    def test_run_validates_metrics(self):
        """Run should validate metrics."""
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local")
        assert result.returncode == 0
        assert "Metrics" in result.stdout
        assert "**In range:** 2" in result.stdout or "In range: 2" in result.stdout

    def test_run_json_format(self):
        """Run should support JSON output."""
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "overall_status" in data
        assert data["overall_status"] == "success"

    def test_run_html_format(self, tmp_path):
        """Run should support HTML output."""
        out = tmp_path / "report.html"
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--format", "html", "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "<html" in content
        assert "reproduction" in content.lower()

    def test_run_output_dir(self, tmp_path):
        """Run should support explicit output directory."""
        out_dir = tmp_path / "run-output"
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--output-dir", str(out_dir))
        assert result.returncode == 0
        assert out_dir.exists()

    def test_run_fail_on_failed_command(self, tmp_path):
        """Run with --fail-on failed-command should exit non-zero on failure."""
        # Create a repo with a failing command
        repo = tmp_path / "failing-repo"
        repo.mkdir()
        (repo / "reproducibility.yml").write_text(
            'schema_version: "0.2"\n'
            'commands:\n'
            '  - id: fail\n'
            '    run: python -c "import sys; sys.exit(1)"\n'
            '    timeout_seconds: 10\n',
            encoding="utf-8",
        )
        result = run_cli("reproduce", "run", str(repo), "--execute", "--sandbox", "local", "--fail-on", "failed-command")
        assert result.returncode == 1
