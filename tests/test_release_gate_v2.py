"""Tests for the release gate script."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestReleaseGate:
    """Test release_gate.py."""

    def test_release_gate_runs(self):
        """Test that release gate runs without error."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"),
             "--format", "json"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_release_gate_markdown(self):
        """Test markdown output."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"),
             "--format", "markdown"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0
        assert "Release Gate" in result.stdout

    def test_release_gate_check_mode(self):
        """Test --check mode."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"), "--check"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        # Should pass (exit 0) if all checks pass
        assert result.returncode == 0

    def test_release_gate_output_file(self, tmp_path):
        """Test writing to output file."""
        import subprocess
        import sys

        out = tmp_path / "gate.md"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "release_gate.py"),
             "--format", "markdown", "--output", str(out)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0
        assert out.exists()
