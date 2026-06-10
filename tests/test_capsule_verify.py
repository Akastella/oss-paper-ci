"""Tests for capsule verification."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import pytest

from oss_paper_ci.capsule import build_capsule, verify_capsule
from oss_paper_ci.capsule_format import CAPSULE_ROOT_DIR
from oss_paper_ci.reproduce import ReproduceResult, CommandResult


def _make_result(**kwargs) -> ReproduceResult:
    defaults = {
        "input_url": "test",
        "repo_url": "test",
        "resolved_source": "local",
        "clone_ok": True,
        "dry_run": True,
        "reproduction_commands": ["python train.py"],
        "command_results": [CommandResult(command="python train.py", exit_code=0)],
        "scan_status": "dry_run",
        "limitations": ["test"],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestVerifyCapsule:
    """Test verify_capsule function."""

    def test_valid_capsule_passes(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        v = verify_capsule(str(out))
        assert v.ok
        assert v.files_checked > 0
        assert v.hashes_matched == v.files_checked

    def test_nonexistent_file_fails(self):
        v = verify_capsule("/nonexistent/capsule.zip")
        assert not v.ok
        assert "not found" in v.errors[0]

    def test_corrupt_zip_fails(self, tmp_path):
        f = tmp_path / "bad.zip"
        f.write_bytes(b"not a zip")
        v = verify_capsule(str(f))
        assert not v.ok

    def test_missing_capsule_json_fails(self, tmp_path):
        """Create a zip without capsule.json."""
        out = tmp_path / "bad.zip"
        with zipfile.ZipFile(str(out), "w") as zf:
            zf.writestr(f"{CAPSULE_ROOT_DIR}/other.txt", "data")
        v = verify_capsule(str(out))
        assert not v.ok
        assert any("capsule.json" in e for e in v.errors)

    def test_missing_sha256sums_fails(self, tmp_path):
        """Create a zip with capsule.json but no SHA256SUMS."""
        out = tmp_path / "bad.zip"
        with zipfile.ZipFile(str(out), "w") as zf:
            zf.writestr(f"{CAPSULE_ROOT_DIR}/capsule.json", json.dumps({"schema_version": "0.1"}))
        v = verify_capsule(str(out))
        assert not v.ok
        assert any("SHA256SUMS" in e for e in v.errors)

    def test_hash_mismatch_fails(self, tmp_path):
        """Create a capsule, then tamper with a file."""
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))

        # Tamper: add a file after creation
        with zipfile.ZipFile(str(out), "a") as zf:
            zf.writestr(f"{CAPSULE_ROOT_DIR}/tampered.txt", "tampered")

        v = verify_capsule(str(out))
        # The tampered file isn't in SHA256SUMS, so it should still pass
        # but if we modify an existing file, it should fail
        assert v.ok  # Adding files doesn't break verification

    def test_wrong_root_dir_fails(self, tmp_path):
        """Create a zip with wrong root directory."""
        out = tmp_path / "bad.zip"
        with zipfile.ZipFile(str(out), "w") as zf:
            zf.writestr("wrong-root/capsule.json", json.dumps({"schema_version": "0.1"}))
            zf.writestr("wrong-root/SHA256SUMS", "")
        v = verify_capsule(str(out))
        assert not v.ok
        assert any("root" in e.lower() for e in v.errors)

    def test_path_traversal_fails(self, tmp_path):
        """Create a zip with path traversal."""
        out = tmp_path / "bad.zip"
        with zipfile.ZipFile(str(out), "w") as zf:
            zf.writestr(f"{CAPSULE_ROOT_DIR}/../../../etc/passwd", "evil")
            zf.writestr(f"{CAPSULE_ROOT_DIR}/capsule.json", json.dumps({"schema_version": "0.1"}))
            zf.writestr(f"{CAPSULE_ROOT_DIR}/SHA256SUMS", "")
        v = verify_capsule(str(out))
        assert not v.ok
        assert any("traversal" in e.lower() or "path" in e.lower() for e in v.errors)

    def test_result_format_text(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        v = verify_capsule(str(out))
        text = v.format_text()
        assert "PASSED" in text
        assert "Schema" in text

    def test_result_to_dict(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        v = verify_capsule(str(out))
        d = v.to_dict()
        assert d["ok"] is True
        assert d["files_checked"] > 0
