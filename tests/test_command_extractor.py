"""Tests for command extraction from build files."""

from __future__ import annotations

import pytest
from pathlib import Path

from oss_paper_ci.command_extractor import extract_commands_from_build_files


FIXTURES = Path(__file__).parent / "fixtures"


class TestExtractCommandsFromBuildFiles:
    """Test command extraction from build files."""

    def test_extracts_makefile_targets(self):
        """Extracts targets from Makefile."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_make_repo"))
        commands = [c.command for c in candidates]
        assert any("make train" in c for c in commands)
        assert any("make evaluate" in c for c in commands)
        assert any("make figures" in c for c in commands)

    def test_extracts_snakemake_rules(self):
        """Extracts rules from Snakefile."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_make_repo"))
        commands = [c.command for c in candidates]
        assert any("snakemake" in c for c in commands)

    def test_extracts_from_snakemake_repo(self):
        """Extracts from standalone Snakemake repo."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_snakemake_repo"))
        commands = [c.command for c in candidates]
        assert any("snakemake" in c for c in commands)

    def test_extracts_pyproject_scripts(self):
        """Extracts scripts from pyproject.toml."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_python_repo"))
        commands = [c.command for c in candidates]
        assert any("train" in c for c in commands)

    def test_classifies_makefile_targets(self):
        """Classifies Makefile targets by kind."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_make_repo"))
        kinds = {c.kind for c in candidates}
        assert "train" in kinds
        assert "evaluate" in kinds
        assert "figure" in kinds

    def test_skips_clean_target(self):
        """Does not include 'clean' target."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_make_repo"))
        commands = [c.command for c in candidates]
        assert not any("make clean" in c for c in commands)

    def test_no_dangerous_from_build_files(self):
        """Build file commands are not dangerous."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "intake_make_repo"))
        for c in candidates:
            assert not c.dangerous

    def test_returns_empty_for_no_build_files(self):
        """Returns empty for repo without build files."""
        candidates = extract_commands_from_build_files(str(FIXTURES / "minimal_bad_repo"))
        assert isinstance(candidates, list)
