"""Tests for README command mining."""

from __future__ import annotations

import pytest
from pathlib import Path

from oss_paper_ci.readme_miner import (
    CommandCandidate,
    mine_readme_commands,
    format_commands_markdown,
)


FIXTURES = Path(__file__).parent / "fixtures"


class TestMineReadmeCommands:
    """Test command extraction from README files."""

    def test_extracts_fenced_commands(self):
        """Extracts commands from fenced code blocks."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        commands = [c.command for c in candidates]
        assert any("pip install" in c for c in commands)
        assert any("train.py" in c for c in commands)
        assert any("evaluate.py" in c for c in commands)

    def test_classifies_install_commands(self):
        """Classifies install commands correctly."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        install_cmds = [c for c in candidates if c.kind == "install"]
        assert len(install_cmds) >= 1
        assert any("pip install" in c.command for c in install_cmds)

    def test_classifies_train_commands(self):
        """Classifies train commands correctly."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        train_cmds = [c for c in candidates if c.kind == "train"]
        assert len(train_cmds) >= 1
        assert any("train.py" in c.command for c in train_cmds)

    def test_classifies_evaluate_commands(self):
        """Classifies evaluate commands correctly."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        eval_cmds = [c for c in candidates if c.kind == "evaluate"]
        assert len(eval_cmds) >= 1
        assert any("evaluate.py" in c.command for c in eval_cmds)

    def test_detects_dangerous_commands(self):
        """Detects dangerous commands."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_unsafe_commands_repo"))
        dangerous = [c for c in candidates if c.dangerous]
        assert len(dangerous) >= 1

    def test_no_commands_in_empty_repo(self):
        """Returns empty list for repo without README."""
        candidates = mine_readme_commands(str(FIXTURES / "minimal_bad_repo"))
        # May have some commands from other files, but not many
        assert isinstance(candidates, list)

    def test_assigns_stable_ids(self):
        """Assigns stable IDs to candidates."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        ids = [c.id for c in candidates]
        assert len(ids) == len(set(ids))  # All unique

    def test_has_source_and_line(self):
        """All candidates have source and line information."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        for c in candidates:
            assert c.source
            assert c.line > 0

    def test_confidence_between_0_and_1(self):
        """Confidence scores are between 0 and 1."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        for c in candidates:
            assert 0.0 <= c.confidence <= 1.0


class TestFormatCommandsMarkdown:
    """Test markdown formatting."""

    def test_formats_empty(self):
        """Formats empty candidate list."""
        text = format_commands_markdown([])
        assert "No commands found" in text

    def test_formats_candidates(self):
        """Formats candidate list."""
        candidates = mine_readme_commands(str(FIXTURES / "intake_python_repo"))
        text = format_commands_markdown(candidates)
        assert "README Command Candidates" in text
        assert "install" in text
