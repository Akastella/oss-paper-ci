"""Tests for the guide CLI command."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def _run_guide(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "guide", *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=str(ROOT), timeout=30,
    )


class TestGuideBasic:
    """Test basic guide functionality."""

    def test_guide_runs(self):
        result = _run_guide()
        assert result.returncode == 0
        assert "oss-paper-ci" in result.stdout.lower() or "guide" in result.stdout.lower()

    def test_guide_role_author(self):
        result = _run_guide("--role", "author")
        assert result.returncode == 0
        assert "author" in result.stdout.lower()

    def test_guide_role_reviewer(self):
        result = _run_guide("--role", "reviewer")
        assert result.returncode == 0
        assert "reviewer" in result.stdout.lower()

    def test_guide_role_maintainer(self):
        result = _run_guide("--role", "maintainer")
        assert result.returncode == 0
        assert "maintainer" in result.stdout.lower()

    def test_guide_topic_scan(self):
        result = _run_guide("--topic", "scan")
        assert result.returncode == 0
        assert "scan" in result.stdout.lower()

    def test_guide_topic_reproduce(self):
        result = _run_guide("--topic", "reproduce")
        assert result.returncode == 0
        assert "reproduce" in result.stdout.lower()

    def test_guide_topic_capsule(self):
        result = _run_guide("--topic", "capsule")
        assert result.returncode == 0
        assert "capsule" in result.stdout.lower()


class TestGuideOutput:
    """Test guide output formats."""

    def test_guide_json_format(self):
        result = _run_guide("--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "disclaimer" in data

    def test_guide_json_role(self):
        result = _run_guide("--role", "author", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["role"] == "author"
        assert "recommended_commands" in data

    def test_guide_json_topic(self):
        result = _run_guide("--topic", "reproduce", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["topic"] == "reproduce"
        assert "steps" in data

    def test_guide_output_file(self, tmp_path):
        out = tmp_path / "guide.md"
        result = _run_guide("--output", str(out))
        assert result.returncode == 0
        assert out.exists()


class TestGuideDisclaimer:
    """Test that guide includes important disclaimers."""

    def test_guide_has_disclaimer(self):
        result = _run_guide("--format", "json")
        data = json.loads(result.stdout)
        assert "not" in data["disclaimer"].lower()
        assert "correctness" in data["disclaimer"].lower() or "proof" in data["disclaimer"].lower()
