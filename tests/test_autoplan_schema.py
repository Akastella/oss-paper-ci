"""Tests for autoplan schema validation."""

from __future__ import annotations

import yaml
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


class TestAutoplanSchema:
    """Test autoplan schema validation."""

    def test_candidate_config_schema_version(self):
        """Candidate config has schema_version 0.2."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert result.candidate_config["schema_version"] == "0.2"

    def test_candidate_config_generated_mode(self):
        """Candidate config has generated_mode: candidate."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        assert result.candidate_config["generated_mode"] == "candidate"

    def test_candidate_config_has_commands(self):
        """Candidate config has commands list."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        commands = result.candidate_config.get("commands", [])
        assert isinstance(commands, list)
        assert len(commands) > 0

    def test_command_has_id_and_run(self):
        """Each command has id and run fields."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        for cmd in result.candidate_config.get("commands", []):
            assert "id" in cmd
            assert "run" in cmd
            assert cmd["id"]
            assert cmd["run"]

    def test_candidate_config_has_environment(self):
        """Candidate config has environment section."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        env = result.candidate_config.get("environment", {})
        assert "type" in env

    def test_candidate_config_has_safety(self):
        """Candidate config has safety section."""
        from oss_paper_ci.autoplan import run_autoplan
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        safety = result.candidate_config.get("safety", {})
        assert "network" in safety
        assert safety["network"] is False

    def test_validate_candidate_config(self):
        """Validate candidate config passes."""
        from oss_paper_ci.autoplan import run_autoplan, validate_candidate_config
        import tempfile
        result = run_autoplan(str(FIXTURES / "intake_python_repo"))
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(result.candidate_config, f)
            tmp_path = f.name
        try:
            warnings = validate_candidate_config(tmp_path)
            assert len(warnings) == 0
        finally:
            Path(tmp_path).unlink()

    def test_validate_existing_config(self):
        """Validate existing config passes."""
        from oss_paper_ci.autoplan import validate_candidate_config
        warnings = validate_candidate_config(
            str(FIXTURES / "intake_existing_reproducibility_repo" / "reproducibility.yml")
        )
        assert len(warnings) == 0

    def test_validate_missing_file(self):
        """Validate reports error for missing file."""
        from oss_paper_ci.autoplan import validate_candidate_config
        warnings = validate_candidate_config("/nonexistent/path.yml")
        assert len(warnings) > 0
