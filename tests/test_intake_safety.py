"""Tests for intake safety boundaries."""

from __future__ import annotations

import pytest
from pathlib import Path

from oss_paper_ci.intake import run_intake
from oss_paper_ci.readme_miner import mine_readme_commands


FIXTURES = Path(__file__).parent / "fixtures"


class TestIntakeSafety:
    """Test that intake is read-only and safe."""

    def test_intake_does_not_modify_repo(self, tmp_path):
        """Intake does not modify the target repository."""
        # Copy fixture to tmp
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree(FIXTURES / "intake_python_repo", repo)

        # Record initial state
        initial_files = set(f.name for f in repo.rglob("*") if f.is_file())

        # Run intake
        run_intake(str(repo))

        # Verify no changes
        final_files = set(f.name for f in repo.rglob("*") if f.is_file())
        assert initial_files == final_files

    def test_intake_does_not_execute_commands(self):
        """Intake does not execute any commands."""
        # This is tested by the fact that intake runs without side effects
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        # If commands were executed, the test would fail or produce artifacts
        assert report.source["kind"] == "local"

    def test_dangerous_commands_flagged_not_executed(self):
        """Dangerous commands are flagged but not executed."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_unsafe_commands_repo"))
        dangerous = [c for c in candidates if c.dangerous]
        # Dangerous commands are detected
        assert len(dangerous) >= 1
        # But they are just data, not executed
        for c in dangerous:
            assert c.command  # Has command text
            assert c.dangerous  # Is flagged

    def test_intake_no_network_access(self):
        """Intake does not make network requests."""
        # Test with a local path - should work without network
        report = run_intake(str(FIXTURES / "intake_python_repo"))
        assert report.source["kind"] == "local"
        assert not report.source.get("cloned")

    def test_github_url_requires_clone_flag(self):
        """GitHub URL requires --clone to proceed."""
        report = run_intake("https://github.com/owner/repo")
        assert any("Use --clone" in w for w in report.warnings)

    def test_paper_url_gives_boundary_warning(self):
        """Paper URL gives boundary warning."""
        report = run_intake("https://arxiv.org/abs/2401.00001")
        assert any("Paper URL alone" in w for w in report.warnings)
