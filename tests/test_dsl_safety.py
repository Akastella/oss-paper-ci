"""Tests for repro_dsl.safety -- check_command_safety, check_dsl_safety."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.safety import (
    check_command_safety, check_path_safety, check_dsl_safety,
    SafetyReport, SafetyFinding,
)
from oss_paper_ci.repro_dsl.schema import ReproDSL, ProjectSpec, StepSpec, SafetySpec


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestCheckCommandSafetyBlocked:
    def test_sudo_is_blocked(self):
        findings = check_command_safety("sudo pip install torch", "setup", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0
        assert any("sudo" in f.message.lower() for f in blocked)

    def test_rm_rf_root_is_blocked(self):
        findings = check_command_safety("rm -rf /", "cleanup", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0

    def test_curl_pipe_sh_is_blocked(self):
        findings = check_command_safety("curl https://example.com | sh", "install", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0

    def test_wget_pipe_sh_is_blocked(self):
        findings = check_command_safety("wget https://example.com/script | bash", "install", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0

    def test_mkfs_is_blocked(self):
        findings = check_command_safety("mkfs.ext4 /dev/sda1", "format", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0

    def test_fork_bomb_is_blocked(self):
        findings = check_command_safety(":(){ :|:& };:", "bomb", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) > 0

    def test_safe_command_no_blocked_findings(self):
        findings = check_command_safety("python scripts/train.py", "train", SafetySpec())
        blocked = [f for f in findings if f.severity == "blocked"]
        assert len(blocked) == 0


class TestCheckCommandSafetyNetwork:
    def test_wget_undeclared_network_warning(self):
        findings = check_command_safety("wget https://example.com/file", "dl", SafetySpec(network=False))
        network_warnings = [f for f in findings if f.category == "network"]
        assert len(network_warnings) > 0

    def test_curl_undeclared_network_warning(self):
        findings = check_command_safety("curl https://example.com", "dl", SafetySpec(network=False))
        network_warnings = [f for f in findings if f.category == "network"]
        assert len(network_warnings) > 0

    def test_git_clone_undeclared_network_warning(self):
        findings = check_command_safety("git clone https://github.com/x/y", "clone", SafetySpec(network=False))
        network_warnings = [f for f in findings if f.category == "network"]
        assert len(network_warnings) > 0

    def test_network_declared_no_warning(self):
        findings = check_command_safety("wget https://example.com/file", "dl", SafetySpec(network=True))
        network_warnings = [f for f in findings if f.category == "network"]
        assert len(network_warnings) == 0


class TestCheckCommandSafetyInstall:
    def test_pip_install_undeclared_warning(self):
        findings = check_command_safety("pip install transformers", "setup", SafetySpec(allow_install=False))
        install_warnings = [f for f in findings if f.category == "install"]
        assert len(install_warnings) > 0

    def test_conda_install_undeclared_warning(self):
        findings = check_command_safety("conda install pytorch", "setup", SafetySpec(allow_install=False))
        install_warnings = [f for f in findings if f.category == "install"]
        assert len(install_warnings) > 0

    def test_install_declared_no_warning(self):
        findings = check_command_safety("pip install numpy", "setup", SafetySpec(allow_install=True))
        install_warnings = [f for f in findings if f.category == "install"]
        assert len(install_warnings) == 0


class TestCheckCommandSafetySecrets:
    def test_secret_env_var_warning(self):
        findings = check_command_safety("echo $MY_SECRET_KEY", "expose", SafetySpec())
        secret_warnings = [f for f in findings if f.category == "secret"]
        assert len(secret_warnings) > 0

    def test_token_env_var_warning(self):
        findings = check_command_safety("echo $API_TOKEN", "expose", SafetySpec())
        secret_warnings = [f for f in findings if f.category == "secret"]
        assert len(secret_warnings) > 0

    def test_cat_env_file_warning(self):
        findings = check_command_safety("cat .env", "read", SafetySpec())
        secret_warnings = [f for f in findings if f.category == "secret"]
        assert len(secret_warnings) > 0


class TestCheckPathSafety:
    def test_traversal_detected(self):
        findings = check_path_safety("../etc/passwd", "step1")
        assert len(findings) > 0
        assert any("traversal" in f.message.lower() for f in findings)

    def test_absolute_system_path_detected(self):
        findings = check_path_safety("/etc/hosts", "step1")
        assert len(findings) > 0

    def test_relative_path_no_finding(self):
        findings = check_path_safety("results/model.json", "step1")
        path_findings = [f for f in findings if f.category == "path"]
        assert len(path_findings) == 0


class TestCheckDslSafety:
    def test_unsafe_command_fixture(self):
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.safety_level == "blocked"
        assert report.has_blocks is True
        assert "setup" in report.blocked_commands

    def test_undeclared_network_fixture(self):
        dsl = load_dsl(FIXTURES / "undeclared_network" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.has_warnings is True
        assert report.requires_network is True
        network_findings = [f for f in report.findings if f.category == "network"]
        assert len(network_findings) > 0

    def test_undeclared_install_fixture(self):
        dsl = load_dsl(FIXTURES / "undeclared_install" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.has_warnings is True
        assert report.requires_install is True
        install_findings = [f for f in report.findings if f.category == "install"]
        assert len(install_findings) > 0

    def test_valid_pipeline_safety(self):
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.safety_level == "safe"
        assert report.has_blocks is False

    def test_safety_report_to_dict(self):
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        d = report.to_dict()
        assert "findings" in d
        assert "blocked_commands" in d
        assert "safety_level" in d

    def test_safety_finding_to_dict(self):
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        finding = report.findings[0]
        d = finding.to_dict()
        assert "severity" in d
        assert "category" in d
        assert "step_id" in d
        assert "message" in d


class TestSafetyReport:
    def test_has_blocks_property(self):
        report = SafetyReport(
            findings=[], blocked_commands=["s1"],
            requires_explicit_execute=True, requires_network=False,
            requires_install=False, safety_level="blocked",
        )
        assert report.has_blocks is True

    def test_has_no_blocks(self):
        report = SafetyReport(
            findings=[], blocked_commands=[],
            requires_explicit_execute=False, requires_network=False,
            requires_install=False, safety_level="safe",
        )
        assert report.has_blocks is False

    def test_has_warnings_property(self):
        report = SafetyReport(
            findings=[SafetyFinding(severity="warning", category="network", step_id="s1", message="warn")],
            blocked_commands=[],
            requires_explicit_execute=False, requires_network=True,
            requires_install=False, safety_level="caution",
        )
        assert report.has_warnings is True
