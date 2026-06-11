"""Tests for dossier i18n support."""

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
    data = {
        "summary": {"score": 75, "status": "warn"},
        "checks": [
            {"id": "ENV001", "title": "Deps", "severity": "error", "status": "fail", "message": "Missing"},
        ],
    }
    f = tmp_path / "scan.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    return f


class TestDossierI18n:
    """Test dossier internationalization."""

    def test_en_has_english_title(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "en")
        assert "Dossier" in result.stdout

    def test_zh_cn_has_chinese(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "zh-CN")
        # Should contain Chinese characters
        assert any("一" <= c <= "鿿" for c in result.stdout)

    def test_ja_has_japanese(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "ja")
        # Should contain Japanese characters
        assert any("぀" <= c <= "ヿ" for c in result.stdout) or \
               any("一" <= c <= "鿿" for c in result.stdout)

    def test_json_language_field(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        for lang in ("en", "zh-CN", "ja"):
            result = _run_dossier("--scan-report", str(scan_file), "--language", lang, "--format", "json")
            data = json.loads(result.stdout)
            assert data["language"] == lang

    def test_zh_cn_has_limitation(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "zh-CN", "--format", "json")
        data = json.loads(result.stdout)
        assert len(data.get("non_claims", [])) > 0

    def test_ja_has_limitation(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        result = _run_dossier("--scan-report", str(scan_file), "--language", "ja", "--format", "json")
        data = json.loads(result.stdout)
        assert len(data.get("non_claims", [])) > 0

    def test_html_lang_attribute(self, tmp_path):
        scan_file = _make_scan_report(tmp_path)
        for lang in ("en", "zh-CN", "ja"):
            result = _run_dossier("--scan-report", str(scan_file), "--language", lang, "--format", "html")
            assert f'lang="{lang}"' in result.stdout
