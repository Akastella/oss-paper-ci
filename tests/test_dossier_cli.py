"""Tests for the dossier CLI command."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


def _run_dossier(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", "dossier", *args],
        capture_output=True, text=True, encoding="utf-8",
        errors="replace", cwd=str(ROOT), timeout=30,
    )


def _make_scan_report(tmp_path: Path) -> Path:
    """Create a minimal scan report for testing."""
    data = {
        "summary": {"score": 75, "status": "warn"},
        "checks": [
            {"id": "META001", "title": "README", "severity": "info", "status": "pass", "message": "OK"},
            {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail", "message": "Missing"},
        ],
    }
    f = tmp_path / "scan.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


class TestDossierBasic:
    """Test basic dossier functionality."""

    def test_dossier_from_scan(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file))
        assert result.returncode == 0
        assert "Dossier" in result.stdout or "evidence" in result.stdout.lower()

    def test_dossier_author(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--audience", "author")
        assert result.returncode == 0

    def test_dossier_reviewer(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--audience", "reviewer")
        assert result.returncode == 0

    def test_dossier_maintainer(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--audience", "maintainer")
        assert result.returncode == 0

    def test_dossier_no_input(self):
        result = _run_dossier()
        assert result.returncode != 0


class TestDossierLanguages:
    """Test dossier language support."""

    def test_dossier_en(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "en")
        assert result.returncode == 0
        assert "Dossier" in result.stdout

    def test_dossier_zh_cn(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "zh-CN")
        assert result.returncode == 0

    def test_dossier_ja(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "ja")
        assert result.returncode == 0


class TestDossierFormats:
    """Test dossier output formats."""

    def test_dossier_json(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["schema_version"] == "0.1"

    def test_dossier_html(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "html")
        assert result.returncode == 0
        assert "<!DOCTYPE html>" in result.stdout

    def test_dossier_issue(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "issue")
        assert result.returncode == 0
        assert "Checklist" in result.stdout or "checklist" in result.stdout.lower()

    def test_dossier_pr_comment(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "pr-comment")
        assert result.returncode == 0

    def test_dossier_output_file(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        out = tmp_path / "dossier.md"
        result = _run_dossier("--scan-report", str(scan_file), "--output", str(out))
        assert result.returncode == 0
        assert out.exists()


class TestDossierContent:
    """Test dossier content quality."""

    def test_json_has_evidence_map(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "json")
        data = json.loads(result.stdout)
        assert "evidence_map" in data
        assert isinstance(data["evidence_map"], list)

    def test_json_has_risk_register(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "json")
        data = json.loads(result.stdout)
        assert "risk_register" in data

    def test_json_has_remediation(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "json")
        data = json.loads(result.stdout)
        assert "remediation_plan" in data

    def test_markdown_has_disclaimer(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "markdown")
        assert "not" in result.stdout.lower() or "does not" in result.stdout.lower()

    def test_html_no_cdn(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--format", "html")
        assert "cdn" not in result.stdout.lower()
        assert "googleapis" not in result.stdout.lower()

    def test_reviewer_no_accept_reject(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--audience", "reviewer", "--format", "markdown")
        content = result.stdout.lower()
        # Should not contain accept/reject recommendations
        assert "should accept" not in content
        assert "should reject" not in content
        assert "recommend accept" not in content
        assert "recommend reject" not in content
