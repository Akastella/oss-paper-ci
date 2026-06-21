"""Tests for the reproduction system demo repository."""

import subprocess
import sys
import json
import pytest
from pathlib import Path

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


class TestDemoRepo:
    """Tests that the demo repo works end-to-end."""

    def test_demo_repo_exists(self):
        assert Path(DEMO_REPO).exists()
        assert Path(DEMO_REPO, "reproducibility.yml").exists()
        assert Path(DEMO_REPO, "scripts", "train.py").exists()
        assert Path(DEMO_REPO, "scripts", "evaluate.py").exists()
        assert Path(DEMO_REPO, "scripts", "make_figures.py").exists()

    def test_demo_scripts_run_deterministically(self, tmp_path):
        """Demo scripts should produce identical output on repeated runs."""
        import shutil
        repo1 = tmp_path / "run1"
        repo2 = tmp_path / "run2"
        shutil.copytree(DEMO_REPO, repo1)
        shutil.copytree(DEMO_REPO, repo2)

        # Run train in both
        subprocess.run([sys.executable, "scripts/train.py"], cwd=repo1, check=True)
        subprocess.run([sys.executable, "scripts/train.py"], cwd=repo2, check=True)

        m1 = (repo1 / "results" / "model.json").read_text()
        m2 = (repo2 / "results" / "model.json").read_text()
        assert m1 == m2

    def test_demo_plan_succeeds(self):
        result = run_cli("reproduce", "plan", DEMO_REPO)
        assert result.returncode == 0
        assert "Reproduction Plan" in result.stdout

    def test_demo_run_execute_succeeds(self):
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local")
        assert result.returncode == 0
        assert "success" in result.stdout.lower()

    def test_demo_run_json_succeeds(self):
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["overall_status"] == "success"
        assert len(data["command_results"]) == 3
        assert all(cr["status"] == "success" for cr in data["command_results"])

    def test_demo_artifacts_validated(self):
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--format", "json")
        data = json.loads(result.stdout)
        av = data.get("artifact_validation", {})
        assert av.get("found", 0) == 4
        assert av.get("missing", 0) == 0

    def test_demo_metrics_validated(self):
        result = run_cli("reproduce", "run", DEMO_REPO, "--execute", "--sandbox", "local", "--format", "json")
        data = json.loads(result.stdout)
        mv = data.get("metric_validation", {})
        assert mv.get("in_range", 0) == 2
        assert mv.get("out_of_range", 0) == 0

    def test_demo_no_dangerous_commands(self):
        from oss_paper_ci.command_safety import is_dangerous_command
        contract_path = Path(DEMO_REPO, "reproducibility.yml")
        import yaml
        with open(contract_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        for cmd in data.get("commands", []):
            assert not is_dangerous_command(cmd["run"]), f"Dangerous command in demo: {cmd['run']}"
