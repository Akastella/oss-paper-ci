"""Tests that trust checks can use DSL safety."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl
from oss_paper_ci.repro_dsl.safety import check_dsl_safety


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestTrustChecksDslSafety:
    def test_safe_pipeline_trustworthy(self):
        """A pipeline with no safety issues should be considered trustworthy."""
        dsl = load_dsl(FIXTURES / "valid_python_pipeline" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.safety_level == "safe"
        assert not report.has_blocks
        assert not report.requires_network
        assert not report.requires_install

    def test_unsafe_command_trust_issue(self):
        """A pipeline with sudo should be flagged as blocked."""
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.safety_level == "blocked"
        assert report.has_blocks
        assert report.requires_explicit_execute

    def test_undeclared_network_trust_warning(self):
        """A pipeline with undeclared network should raise a warning."""
        dsl = load_dsl(FIXTURES / "undeclared_network" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.has_warnings
        assert report.requires_network
        assert report.requires_explicit_execute

    def test_undeclared_install_trust_warning(self):
        """A pipeline with undeclared install should raise a warning."""
        dsl = load_dsl(FIXTURES / "undeclared_install" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert report.has_warnings
        assert report.requires_install
        assert report.requires_explicit_execute

    def test_safety_report_serializable_for_trust_audit(self):
        """Safety report can be serialized for trust audit storage."""
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        d = report.to_dict()
        assert isinstance(d, dict)
        assert "safety_level" in d
        assert "blocked_commands" in d
        assert "findings" in d

    def test_blocked_commands_identified(self):
        """Blocked commands are explicitly listed for trust review."""
        dsl = load_dsl(FIXTURES / "unsafe_command" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        assert "setup" in report.blocked_commands

    def test_findings_have_severity(self):
        """All safety findings have severity for trust scoring."""
        dsl = load_dsl(FIXTURES / "undeclared_network" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        for finding in report.findings:
            assert finding.severity in ("blocked", "warning", "info")

    def test_findings_have_category(self):
        """All safety findings have category for trust classification."""
        dsl = load_dsl(FIXTURES / "undeclared_network" / "reproducibility.yml")
        report = check_dsl_safety(dsl)
        for finding in report.findings:
            assert finding.category in ("command", "path", "network", "install", "secret", "gpu")
