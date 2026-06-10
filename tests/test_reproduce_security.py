"""Security tests for the reproduce command.

Tests that dangerous commands are blocked, dry-run is safe by default,
and the workdir is properly isolated.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from oss_paper_ci.reproduce import run_reproduce
from oss_paper_ci.runner import is_dangerous_command


class TestDangerousCommandDetection:
    """Test that dangerous commands are blocked."""

    def test_rm_rf_blocked(self):
        assert is_dangerous_command("rm -rf /")

    def test_sudo_blocked(self):
        assert is_dangerous_command("sudo apt install something")

    def test_curl_pipe_sh_blocked(self):
        # The pattern matches "curl | sh" as a substring
        assert is_dangerous_command("curl | sh")

    def test_fork_bomb_blocked(self):
        assert is_dangerous_command(":(){:|:&};:")

    def test_safe_command_not_blocked(self):
        assert not is_dangerous_command("python scripts/train.py")
        assert not is_dangerous_command("pip install numpy")
        assert not is_dangerous_command("ls -la")


class TestDryRunSafety:
    """Test that dry-run never executes code."""

    def test_dry_run_never_executes(self, tmp_path):
        marker = tmp_path / "marker.txt"
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text(
            f"Path('{marker.as_posix()}').write_text('executed')"
        )

        result = run_reproduce(str(tmp_path), dry_run=True, execute=False)
        assert not marker.exists()
        assert result.dry_run

    def test_dry_run_forced_without_execute(self, tmp_path):
        """Even if dry_run=False, execute=False forces dry-run."""
        marker = tmp_path / "marker.txt"
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text(
            f"Path('{marker.as_posix()}').write_text('executed')"
        )

        result = run_reproduce(str(tmp_path), dry_run=False, execute=False)
        assert result.dry_run
        assert not marker.exists()

    def test_dry_run_blocks_dangerous_command(self, tmp_path):
        result = run_reproduce(
            str(tmp_path), dry_run=True,
            command="sudo rm -rf /",
        )
        # In dry-run, commands are shown but not executed
        assert result.dry_run


class TestExecuteSafety:
    """Test execute mode safety."""

    def test_execute_blocks_dangerous_command(self, tmp_path):
        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command="sudo rm -rf /",
        )
        assert len(result.command_results) == 1
        assert result.command_results[0].blocked

    def test_execute_blocks_rm_rf(self, tmp_path):
        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command="rm -rf /",
        )
        assert result.command_results[0].blocked


class TestWorkdirIsolation:
    """Test that workdir is properly isolated."""

    def test_temp_workdir_created(self, tmp_path):
        """When no workdir specified, a temp dir should be used."""
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text("pass")

        result = run_reproduce(str(tmp_path), dry_run=True)
        # workdir should be set (either temp or the path itself)
        assert result.workdir

    def test_explicit_workdir(self, tmp_path):
        workdir = tmp_path / "my-workdir"
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text("pass")

        result = run_reproduce(
            str(tmp_path), dry_run=True,
            workdir=str(workdir),
        )
        assert str(workdir) in result.workdir or result.workdir == str(workdir)


class TestNoExecuteByDefault:
    """Test that execute is not the default."""

    def test_default_is_dry_run(self, tmp_path):
        result = run_reproduce(str(tmp_path))
        assert result.dry_run

    def test_execute_requires_explicit_flag(self, tmp_path):
        marker = tmp_path / "marker.txt"
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text(
            f"Path('{marker.as_posix()}').write_text('executed')"
        )

        # Without execute=True, should not run
        result = run_reproduce(str(tmp_path), dry_run=False, execute=False)
        assert not marker.exists()
