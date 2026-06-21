"""Tests for evidence documentation truthfulness."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestEvidenceDocsTruthfulness:
    """Test that evidence docs don't overclaim."""

    def test_evidence_report_docs_exist(self):
        assert (ROOT / "docs" / "evidence-report.md").exists()

    def test_evidence_bundle_docs_exist(self):
        assert (ROOT / "docs" / "evidence-bundle.md").exists()

    def test_reviewer_pack_docs_exist(self):
        assert (ROOT / "docs" / "reviewer-pack.md").exists()

    def test_evidence_examples_exist(self):
        assert (ROOT / "examples" / "evidence").is_dir()
        assert (ROOT / "examples" / "evidence" / "README.md").exists()

    def test_evidence_report_no_scientific_proof_claim(self):
        content = (ROOT / "docs" / "evidence-report.md").read_text(encoding="utf-8").lower()
        assert "prove" not in content or "does not prove" in content or "does not" in content

    def test_reviewer_pack_no_acceptance_claim(self):
        content = (ROOT / "docs" / "reviewer-pack.md").read_text(encoding="utf-8").lower()
        assert "acceptance" not in content or "does not" in content or "not" in content

    def test_evidence_bundle_no_signed_claim(self):
        content = (ROOT / "docs" / "evidence-bundle.md").read_text(encoding="utf-8").lower()
        assert "signed attestation" not in content or "not" in content

    def test_readme_has_evidence_section(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "evidence" in content.lower()

    def test_zh_readme_has_evidence_section(self):
        content = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        assert "evidence" in content.lower() or "证据" in content

    def test_ja_readme_has_evidence_section(self):
        content = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        assert "evidence" in content.lower() or "エビデンス" in content

    def test_evidence_json_no_absolute_paths(self):
        report_path = ROOT / "examples" / "evidence" / "reviewer_report.json"
        if report_path.exists():
            import json
            import re
            data = json.loads(report_path.read_text(encoding="utf-8"))
            text = json.dumps(data)
            assert "C:\\" not in text
            assert not re.findall(r"/home/\S+", text)
            assert not re.findall(r"/Users/\S+", text)

    def test_evidence_html_no_cdn(self):
        html_path = ROOT / "examples" / "evidence" / "reviewer_report.html"
        if html_path.exists():
            content = html_path.read_text(encoding="utf-8").lower()
            assert "cdn." not in content
            assert "googleapis" not in content
            assert "cloudflare" not in content
