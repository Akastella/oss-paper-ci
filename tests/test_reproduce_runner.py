"""Tests for the reproduce runner module."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from oss_paper_ci.reproduce import (
    CommandResult,
    ReproduceResult,
    detect_reproduction_commands,
    run_reproduce,
)


class TestReproduceResultModel:
    """Test ReproduceResult dataclass."""

    def test_default_values(self):
        result = ReproduceResult()
        assert result.input_url == ""
        assert result.dry_run is True
        assert result.clone_ok is False
        assert result.scan_status == "not_run"

    def test_to_dict(self):
        result = ReproduceResult(input_url="test", dry_run=True)
        d = result.to_dict()
        assert d["input_url"] == "test"
        assert d["dry_run"] is True
        assert "environment" in d
        assert "command_results" in d

    def test_ok_when_no_error(self):
        result = ReproduceResult(clone_ok=True)
        assert result.ok

    def test_not_ok_when_error(self):
        result = ReproduceResult(error="something failed")
        assert not result.ok

    def test_not_ok_when_clone_failed(self):
        result = ReproduceResult(clone_ok=False)
        assert not result.ok


class TestCommandResultModel:
    """Test CommandResult dataclass."""

    def test_default_values(self):
        result = CommandResult()
        assert result.exit_code == -1
        assert result.blocked is False

    def test_to_dict(self):
        result = CommandResult(command="test", exit_code=0)
        d = result.to_dict()
        assert d["command"] == "test"
        assert d["exit_code"] == 0


class TestDetectReproductionCommands:
    """Test command detection."""

    def test_from_reproducibility_yml(self, tmp_path):
        (tmp_path / "reproducibility.yml").write_text(
            "experiments:\n  - id: smoke\n    command: python scripts/train.py\n"
        )
        cmds = detect_reproduction_commands(str(tmp_path))
        assert len(cmds) == 1
        assert "train.py" in cmds[0]

    def test_from_common_scripts(self, tmp_path):
        scripts = tmp_path / "scripts"
        scripts.mkdir()
        (scripts / "train.py").write_text("print('train')")
        (scripts / "evaluate.py").write_text("print('eval')")
        cmds = detect_reproduction_commands(str(tmp_path))
        assert len(cmds) >= 2
        assert any("train.py" in c for c in cmds)

    def test_no_commands_found(self, tmp_path):
        cmds = detect_reproduction_commands(str(tmp_path))
        assert len(cmds) == 0


class TestRunReproduceDryRun:
    """Test dry-run mode (safe, no execution)."""

    def test_dry_run_local_path(self, tmp_path):
        # Create a minimal repo
        (tmp_path / "requirements.txt").write_text("numpy\n")
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text("print('train')")

        result = run_reproduce(str(tmp_path), dry_run=True)
        assert result.dry_run
        assert result.clone_ok
        assert result.environment is not None
        assert len(result.environment.environment_files) > 0

    def test_dry_run_does_not_execute(self, tmp_path):
        marker = tmp_path / "marker.txt"
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text(
            f"Path('{marker}').write_text('executed')"
        )

        result = run_reproduce(str(tmp_path), dry_run=True)
        assert not marker.exists()

    def test_dry_run_without_execute_flag(self, tmp_path):
        """Without --execute, dry_run is forced even if requested."""
        result = run_reproduce(str(tmp_path), dry_run=False, execute=False)
        assert result.dry_run


class TestRunReproduceExecute:
    """Test execute mode."""

    def test_execute_runs_commands(self, tmp_path):
        marker = tmp_path / "marker.txt"
        (tmp_path / "scripts").mkdir()
        marker_posix = marker.as_posix()
        (tmp_path / "scripts" / "train.py").write_text(
            f"from pathlib import Path\nPath('{marker_posix}').write_text('executed')"
        )

        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command=f"{sys.executable} scripts/train.py",
        )
        assert marker.exists()
        assert len(result.command_results) == 1
        assert result.command_results[0].exit_code == 0

    def test_execute_captures_stdout(self, tmp_path):
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text("print('hello world')")

        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command=f"{sys.executable} scripts/train.py",
        )
        assert "hello world" in result.command_results[0].stdout_excerpt

    def test_execute_captures_exit_code(self, tmp_path):
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text("exit(42)")

        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command=f"{sys.executable} scripts/train.py",
        )
        assert result.command_results[0].exit_code == 42

    def test_execute_blocks_dangerous_commands(self, tmp_path):
        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command="sudo rm -rf /",
        )
        assert len(result.command_results) == 1
        assert result.command_results[0].blocked


class TestRunReproduceTimeout:
    """Test timeout handling."""

    def test_timeout_on_slow_command(self, tmp_path):
        (tmp_path / "scripts").mkdir()
        (tmp_path / "scripts" / "train.py").write_text(
            "import time; time.sleep(60)"
        )

        result = run_reproduce(
            str(tmp_path), dry_run=False, execute=True,
            command=f"{sys.executable} scripts/train.py",
            timeout=2,
        )
        assert result.command_results[0].timed_out


class TestRunReproduceWorkdir:
    """Test working directory handling."""

    def test_keep_workdir(self, tmp_path):
        workdir = tmp_path / "work"
        workdir.mkdir()

        result = run_reproduce(
            str(tmp_path), dry_run=True,
            workdir=str(workdir), keep_workdir=True,
        )
        assert workdir.exists()


class TestRunReproducePaperUrl:
    """Test paper URL handling."""

    def test_paper_url_without_repo_gives_error(self):
        result = run_reproduce("https://arxiv.org/abs/2301.00001")
        assert result.error
        assert "--repo" in result.error
