"""Tests for evidence bundle."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

from oss_paper_ci.evidence_bundle import (
    BundleVerification,
    create_evidence_bundle,
    inspect_evidence_bundle,
    verify_evidence_bundle,
)

DEMO_REPO = Path(__file__).parent.parent / "examples" / "demo-paper-repo"


class TestEvidenceBundle:
    """Test evidence bundle creation and verification."""

    def test_create_bundle(self, tmp_path):
        out = tmp_path / "bundle.zip"
        result = create_evidence_bundle(DEMO_REPO, out)
        assert result["ok"] is True
        assert out.exists()
        assert result["profile"] == "reviewer"

    def test_bundle_contents(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            assert any("evidence-report.json" in n for n in names)
            assert any("evidence-report.md" in n for n in names)
            assert any("evidence-report.html" in n for n in names)
            assert any("manifest.json" in n for n in names)
            assert any("SHA256SUMS" in n for n in names)
            assert any("limitations.md" in n for n in names)

    def test_bundle_no_forbidden(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        with zipfile.ZipFile(out) as zf:
            for name in zf.namelist():
                assert ".git" not in name
                assert "venv" not in name
                assert "__pycache__" not in name
                assert "node_modules" not in name

    def test_bundle_single_root(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        with zipfile.ZipFile(out) as zf:
            names = zf.namelist()
            for name in names:
                assert name.startswith("evidence-bundle/")

    def test_bundle_manifest_has_sha256(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        with zipfile.ZipFile(out) as zf:
            manifest_data = None
            for name in zf.namelist():
                if name.endswith("manifest.json"):
                    manifest_data = json.loads(zf.read(name))
                    break
            assert manifest_data is not None
            assert "files" in manifest_data
            for f in manifest_data["files"]:
                assert "sha256" in f
                assert len(f["sha256"]) == 64  # SHA256 hex length

    def test_inspect_bundle(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        info = inspect_evidence_bundle(out)
        assert info["ok"] is True
        assert info["profile"] == "reviewer"
        assert "summary" in info

    def test_verify_bundle(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)
        vr = verify_evidence_bundle(out)
        assert vr.ok is True
        assert len(vr.verified) > 0
        assert len(vr.failed) == 0

    def test_verify_tampered_bundle(self, tmp_path):
        out = tmp_path / "bundle.zip"
        create_evidence_bundle(DEMO_REPO, out)

        # Tamper with the bundle
        with zipfile.ZipFile(out, "a") as zf:
            zf.writestr("evidence-bundle/evidence-report.json", "{}")

        vr = verify_evidence_bundle(out)
        assert vr.ok is False
        assert len(vr.failed) > 0

    def test_bundle_inspect_nonexistent(self):
        info = inspect_evidence_bundle("/nonexistent/bundle.zip")
        assert "error" in info

    def test_bundle_verify_nonexistent(self):
        vr = verify_evidence_bundle("/nonexistent/bundle.zip")
        assert vr.ok is False
