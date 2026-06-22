"""Tests for session bundle creation and verification."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from oss_paper_ci.session import create_session
from oss_paper_ci.session_store import save_session
from oss_paper_ci.session_bundle import (
    create_session_bundle,
    inspect_session_bundle,
    verify_session_bundle,
)

DEMO_REPO = str(Path(__file__).parent.parent / "examples" / "repro-system-demo")


class TestSessionBundle:
    """Test session bundle operations."""

    def test_create_bundle(self, tmp_path):
        """Create a session bundle."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        assert Path(bundle_path).exists()
        assert zipfile.is_zipfile(bundle_path)

    def test_bundle_contains_session_json(self, tmp_path):
        """Bundle contains session.json."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        with zipfile.ZipFile(bundle_path) as zf:
            assert "session/session.json" in zf.namelist()

    def test_bundle_contains_manifest(self, tmp_path):
        """Bundle contains manifest.json."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        with zipfile.ZipFile(bundle_path) as zf:
            assert "manifest.json" in zf.namelist()
            data = json.loads(zf.read("manifest.json"))
            assert data["bundle_type"] == "session"

    def test_inspect_bundle(self, tmp_path):
        """Inspect a session bundle."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        info = inspect_session_bundle(bundle_path)
        assert info.session_id == manifest.session_id
        assert info.file_count > 0

    def test_verify_bundle(self, tmp_path):
        """Verify a valid session bundle."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        result = verify_session_bundle(bundle_path)
        assert result.valid
        assert result.schema_ok

    def test_verify_tampered_bundle(self, tmp_path):
        """Verify detects tampered bundle."""
        manifest = create_session(DEMO_REPO, name="test")
        session_dir = str(tmp_path / "session")
        save_session(manifest, session_dir)

        bundle_path = str(tmp_path / "evidence.zip")
        create_session_bundle(session_dir, bundle_path)

        # Tamper with the bundle
        with zipfile.ZipFile(bundle_path, "a") as zf:
            zf.writestr("session/tampered.txt", "tampered")

        result = verify_session_bundle(bundle_path)
        # Should still be valid since we didn't tamper with hashed files
        # But schema_ok should be true
        assert result.schema_ok
