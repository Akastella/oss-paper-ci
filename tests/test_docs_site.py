"""Tests for the docs site builder."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestBuildDocsSite:
    """Test build_docs_site.py."""

    def test_build_creates_html_files(self, tmp_path):
        """Test that the builder creates HTML files from markdown."""
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_docs_site.py"),
             "--docs", str(ROOT / "docs"), "--output", str(tmp_path / "site")],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=30,
        )
        assert result.returncode == 0

        site = tmp_path / "site"
        assert site.exists()
        assert (site / "style.css").exists()
        assert (site / "index.html").exists()

    def test_html_no_external_cdn(self, tmp_path):
        """Test that generated HTML has no external CDN references."""
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_docs_site.py"),
             "--docs", str(ROOT / "docs"), "--output", str(tmp_path / "site")],
            capture_output=True, timeout=30,
        )

        site = tmp_path / "site"
        for html_file in site.glob("*.html"):
            content = html_file.read_text(encoding="utf-8")
            assert "cdn.jsdelivr" not in content
            assert "cdnjs.cloudflare" not in content
            assert "googleapis.com" not in content

    def test_html_has_nav(self, tmp_path):
        """Test that generated HTML has navigation."""
        import subprocess
        import sys

        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "build_docs_site.py"),
             "--docs", str(ROOT / "docs"), "--output", str(tmp_path / "site")],
            capture_output=True, timeout=30,
        )

        site = tmp_path / "site"
        index = site / "index.html"
        if index.exists():
            content = index.read_text(encoding="utf-8")
            assert "<nav" in content
