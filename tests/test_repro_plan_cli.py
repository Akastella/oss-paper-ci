"""Tests for reproduce plan CLI command."""

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


class TestReproducePlan:
    """Tests for reproduce plan command."""

    def test_plan_markdown(self):
        result = run_cli("reproduce", "plan", DEMO_REPO)
        assert result.returncode == 0
        assert "Reproduction Plan" in result.stdout
        assert "train" in result.stdout
        assert "evaluate" in result.stdout
        assert "make_figures" in result.stdout

    def test_plan_json(self):
        result = run_cli("reproduce", "plan", DEMO_REPO, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "steps" in data
        assert len(data["steps"]) == 3
        assert data["steps"][0]["command_id"] == "train"

    def test_plan_does_not_execute_code(self, tmp_path):
        """Plan must never execute any code."""
        marker = tmp_path / "marker.txt"
        result = run_cli("reproduce", "plan", DEMO_REPO)
        assert result.returncode == 0
        # No marker should have been created
        assert not marker.exists()

    def test_plan_output_to_file(self, tmp_path):
        out = tmp_path / "plan.md"
        result = run_cli("reproduce", "plan", DEMO_REPO, "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "Reproduction Plan" in content

    def test_plan_json_output_to_file(self, tmp_path):
        out = tmp_path / "plan.json"
        result = run_cli("reproduce", "plan", DEMO_REPO, "--format", "json", "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        data = json.loads(out.read_text(encoding="utf-8"))
        assert "steps" in data

    def test_plan_shows_safety_constraints(self):
        result = run_cli("reproduce", "plan", DEMO_REPO)
        assert result.returncode == 0
        assert "Safety Constraints" in result.stdout
        assert "blocked" in result.stdout

    def test_plan_shows_metrics(self):
        result = run_cli("reproduce", "plan", DEMO_REPO)
        assert result.returncode == 0
        assert "Expected Metrics" in result.stdout
        assert "accuracy" in result.stdout

    def test_plan_no_contract(self, tmp_path):
        """Plan for a directory without reproducibility.yml should warn."""
        result = run_cli("reproduce", "plan", str(tmp_path))
        assert "No reproducibility.yml found" in result.stdout
