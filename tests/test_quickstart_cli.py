"""Tests for quickstart CLI command."""

import json
import subprocess
import sys

import pytest


class TestQuickstartCLI:
    """Test quickstart command."""

    def test_quickstart_runs(self):
        """quickstart should run without error."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert len(result.stdout) > 0

    def test_quickstart_text_output(self):
        """quickstart should produce text output."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        # Should contain some guidance
        assert "oss-paper-ci" in result.stdout.lower() or "scan" in result.stdout.lower()

    def test_quickstart_markdown_format(self):
        """quickstart --format markdown should work."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--format", "markdown"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "#" in result.stdout or "```" in result.stdout

    def test_quickstart_json_format(self):
        """quickstart --format json should produce valid JSON."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--format", "json"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "recommendations" in data

    def test_quickstart_topic_install(self):
        """quickstart --topic install should show install guidance."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--topic", "install"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "install" in result.stdout.lower() or "clone" in result.stdout.lower()

    def test_quickstart_topic_github_action(self):
        """quickstart --topic github-action should show action guidance."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--topic", "github-action"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "github" in result.stdout.lower() or "action" in result.stdout.lower()

    def test_quickstart_topic_reproduce(self):
        """quickstart --topic reproduce should show reproduce guidance."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--topic", "reproduce"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "reproduce" in result.stdout.lower() or "dry-run" in result.stdout.lower()

    def test_quickstart_topic_eval(self):
        """quickstart --topic eval should show eval guidance."""
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart", "--topic", "eval"],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
        assert "eval" in result.stdout.lower() or "corpus" in result.stdout.lower()

    def test_quickstart_no_external_network(self):
        """quickstart should not require external network."""
        # Just verify it runs (network would cause timeout)
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "quickstart"],
            capture_output=True, text=True, timeout=10,
            encoding="utf-8", errors="replace",
        )
        assert result.returncode == 0
