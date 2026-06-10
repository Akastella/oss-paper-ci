"""Tests for CLI reference generation."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestCliReference:
    """Test CLI reference generation."""

    def test_generate_cli_reference(self, tmp_path):
        """Test that CLI reference can be generated."""
        import subprocess
        import sys

        out = tmp_path / "cli-reference.md"
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_cli_reference.py"),
             "--output", str(out)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0
        assert out.exists()

        content = out.read_text(encoding="utf-8")
        assert "oss-paper-ci scan" in content
        assert "oss-paper-ci reproduce" in content
        assert "oss-paper-ci capsule" in content

    def test_cli_reference_in_docs(self):
        """Test that CLI reference exists in docs."""
        ref = ROOT / "docs" / "cli-reference.md"
        assert ref.exists()
        content = ref.read_text(encoding="utf-8")
        assert "scan" in content
        assert "reproduce" in content
        assert "capsule" in content
