"""Tests for GitHub Action workspace inputs."""

from __future__ import annotations

import yaml
from pathlib import Path


ACTION_FILE = Path(__file__).parent.parent / "action.yml"


def _load_action():
    """Load action.yml."""
    with open(ACTION_FILE, encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestActionInputs:
    """Test that action.yml has required workspace inputs."""

    def test_workspace_input_exists(self):
        action = _load_action()
        assert "workspace" in action.get("inputs", {})

    def test_workspace_input_default_empty(self):
        action = _load_action()
        ws = action["inputs"]["workspace"]
        assert ws.get("default") == ""

    def test_workspace_input_not_required(self):
        action = _load_action()
        ws = action["inputs"]["workspace"]
        assert ws.get("required") is False

    def test_jobs_input_exists(self):
        action = _load_action()
        assert "jobs" in action.get("inputs", {})

    def test_jobs_input_default_1(self):
        action = _load_action()
        jobs = action["inputs"]["jobs"]
        assert jobs.get("default") == "1"

    def test_cache_input_exists(self):
        action = _load_action()
        assert "cache" in action.get("inputs", {})

    def test_cache_input_default_false(self):
        action = _load_action()
        cache = action["inputs"]["cache"]
        assert cache.get("default") == "false"

    def test_batch_scan_step_exists(self):
        """Action should have a batch scan step."""
        action = _load_action()
        steps = action.get("runs", {}).get("steps", [])
        step_names = [s.get("name", "") for s in steps]
        assert any("batch" in name.lower() for name in step_names)

    def test_scan_step_conditional(self):
        """Scan step should only run when workspace is empty."""
        action = _load_action()
        steps = action.get("runs", {}).get("steps", [])
        scan_steps = [s for s in steps if s.get("name", "") == "Run oss-paper-ci scan"]
        if scan_steps:
            assert "workspace == ''" in scan_steps[0].get("if", "")

    def test_batch_step_conditional(self):
        """Batch step should only run when workspace is non-empty."""
        action = _load_action()
        steps = action.get("runs", {}).get("steps", [])
        batch_steps = [s for s in steps if "batch" in s.get("name", "").lower()]
        if batch_steps:
            assert "workspace != ''" in batch_steps[0].get("if", "")
