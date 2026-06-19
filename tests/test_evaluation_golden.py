"""Tests for golden regression files."""

import json
from pathlib import Path

import pytest


GOLDEN_DIR = Path(__file__).parent / "golden"
GOLDEN_JSON = GOLDEN_DIR / "evaluation_summary.json"
GOLDEN_MD = GOLDEN_DIR / "evaluation_matrix.md"


class TestGoldenFiles:
    """Test golden regression files exist and are valid."""

    def test_golden_json_exists(self):
        assert GOLDEN_JSON.exists(), "Run: python scripts/update_evaluation_golden.py"

    def test_golden_md_exists(self):
        assert GOLDEN_MD.exists(), "Run: python scripts/update_evaluation_golden.py"

    def test_golden_json_valid(self):
        data = json.loads(GOLDEN_JSON.read_text())
        assert "version" in data
        assert "repos" in data
        assert "summary" in data

    def test_golden_json_no_absolute_paths(self):
        """Golden files should not contain absolute paths."""
        content = GOLDEN_JSON.read_text()
        assert "C:\\" not in content
        assert "/home/" not in content
        assert "/Users/" not in content

    def test_golden_md_no_absolute_paths(self):
        """Golden markdown should not contain absolute paths."""
        content = GOLDEN_MD.read_text()
        assert "C:\\" not in content
        assert "/home/" not in content
        assert "/Users/" not in content
