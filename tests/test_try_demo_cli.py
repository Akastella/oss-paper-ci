"""Tests for try-demo CLI command."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestTryDemoCLI:
    """Test try-demo command."""

    def test_try_demo_runs(self):
        """try-demo should run without error."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0

    def test_try_demo_text_output(self):
        """try-demo should produce demo output."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "demo" in result.stdout.lower() or "step" in result.stdout.lower()

    def test_try_demo_markdown_format(self):
        """try-demo --format markdown should work."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo", "--format", "markdown"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "#" in result.stdout

    def test_try_demo_json_format(self):
        """try-demo --format json should work."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo", "--format", "json"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        # Should contain demo results
        assert "step" in result.stdout.lower() or "demo" in result.stdout.lower()

    def test_try_demo_output_file(self, tmp_path):
        """try-demo --output should write to file."""
        output_file = tmp_path / "demo-output.md"
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo", "--output", str(output_file)],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert output_file.exists()
        content = output_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_try_demo_no_dangerous_execution(self):
        """try-demo should NOT execute dangerous scripts."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        # Should not contain evidence of script execution
        assert "rm -rf" not in result.stdout.lower()
        assert "eval(" not in result.stdout

    def test_try_demo_plain_mode(self):
        """try-demo --plain should work."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "try-demo", "--plain"],
            capture_output=True, text=True, timeout=120,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        # No ANSI escape codes
        assert "\x1b[" not in result.stdout
