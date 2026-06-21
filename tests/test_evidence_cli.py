"""Tests for evidence CLI commands."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "demo-paper-repo")


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["oss-paper-ci", *args],
        capture_output=True, text=True, timeout=120,
    )


class TestEvidenceReport:
    """Test evidence report command."""

    def test_evidence_default(self):
        result = _run("evidence", DEMO_REPO)
        assert result.returncode == 0
        assert "Unified Evidence Report" in result.stdout

    def test_evidence_report_markdown(self):
        result = _run("evidence", "report", DEMO_REPO, "--format", "markdown")
        assert result.returncode == 0
        assert "Unified Evidence Report" in result.stdout
        assert "Summary" in result.stdout

    def test_evidence_report_json(self):
        result = _run("evidence", "report", DEMO_REPO, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema_version"] == "0.1"
        assert data["report_type"] == "oss-paper-ci-evidence-report"
        assert "summary" in data
        assert "sections" in data
        assert "findings" in data
        assert "limitations" in data

    def test_evidence_report_html(self, tmp_path):
        out = tmp_path / "report.html"
        result = _run("evidence", "report", DEMO_REPO, "--format", "html", "--output", str(out))
        assert result.returncode == 0
        content = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        # No external CDN
        assert "cdn." not in content.lower()
        assert "googleapis" not in content.lower()

    def test_evidence_report_output_file(self, tmp_path):
        out = tmp_path / "report.md"
        result = _run("evidence", "report", DEMO_REPO, "--output", str(out))
        assert result.returncode == 0
        assert out.exists()
        content = out.read_text(encoding="utf-8")
        assert "Unified Evidence Report" in content

    def test_evidence_shorthand(self):
        """Test `evidence .` as shorthand for `evidence report .`"""
        result = _run("evidence", DEMO_REPO, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["report_type"] == "oss-paper-ci-evidence-report"

    def test_evidence_no_absolute_paths(self):
        result = _run("evidence", "report", DEMO_REPO, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        text = json.dumps(data)
        # No Windows absolute paths
        assert "C:\\" not in text
        assert "D:\\" not in text
        # No Unix absolute paths in user dirs
        import re
        assert not re.findall(r"/home/\S+", text)
        assert not re.findall(r"/Users/\S+", text)

    def test_evidence_no_secrets(self):
        result = _run("evidence", "report", DEMO_REPO, "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        text = json.dumps(data)
        # No actual secret values
        assert "sk-" not in text
        assert "ghp_" not in text
