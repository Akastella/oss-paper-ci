"""Security tests for capsules."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from oss_paper_ci.capsule import build_capsule, verify_capsule
from oss_paper_ci.capsule_format import CAPSULE_ROOT_DIR, EXCLUDED_PATTERNS
from oss_paper_ci.reproduce import ReproduceResult, CommandResult


def _make_result(**kwargs) -> ReproduceResult:
    defaults = {
        "input_url": "test",
        "repo_url": "test",
        "resolved_source": "local",
        "clone_ok": True,
        "dry_run": True,
        "reproduction_commands": [],
        "command_results": [],
        "scan_status": "dry_run",
        "limitations": ["test"],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestPathTraversal:
    """Test that path traversal is prevented."""

    def test_no_path_traversal_in_zip(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            for name in zf.namelist():
                assert ".." not in name, f"Path traversal in: {name}"

    def test_verify_detects_traversal(self, tmp_path):
        out = tmp_path / "bad.zip"
        with zipfile.ZipFile(str(out), "w") as zf:
            zf.writestr(f"{CAPSULE_ROOT_DIR}/../../../evil.txt", "evil")
            zf.writestr(f"{CAPSULE_ROOT_DIR}/capsule.json", json.dumps({"schema_version": "0.1"}))
            zf.writestr(f"{CAPSULE_ROOT_DIR}/SHA256SUMS", "")
        v = verify_capsule(str(out))
        assert not v.ok
        assert any("traversal" in e.lower() or "path" in e.lower() for e in v.errors)


class TestAbsolutePath:
    """Test that absolute paths are prevented."""

    def test_no_absolute_paths_in_zip(self, tmp_path):
        result = _make_result(input_url="/absolute/path", repo_url="C:\\absolute\\path")
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            for name in zf.namelist():
                assert not name.startswith("/"), f"Absolute path in: {name}"
                assert not (len(name) >= 2 and name[1] == ":"), f"Absolute path in: {name}"


class TestExclusions:
    """Test that excluded patterns are not packaged."""

    def test_venv_not_in_capsule(self, tmp_path):
        """Even if workdir has venv, it should not be in capsule."""
        workdir = tmp_path / "workdir"
        workdir.mkdir()
        venv = workdir / "venv" / "lib"
        venv.mkdir(parents=True)
        (venv / "module.py").write_text("# venv module")

        result = _make_result(workdir=str(workdir))
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            for name in zf.namelist():
                assert "venv/" not in name, f"venv in capsule: {name}"

    def test_git_not_in_capsule(self, tmp_path):
        workdir = tmp_path / "workdir"
        workdir.mkdir()
        gitdir = workdir / ".git" / "objects"
        gitdir.mkdir(parents=True)
        (gitdir / "obj").write_bytes(b"data")

        result = _make_result(workdir=str(workdir))
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            for name in zf.namelist():
                assert ".git/" not in name, f".git in capsule: {name}"


class TestRedaction:
    """Test that absolute paths are redacted in metadata."""

    def test_absolute_url_redacted(self, tmp_path):
        result = _make_result(
            input_url="/home/user/paper-repo",
            repo_url="/home/user/paper-repo",
        )
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            source = json.loads(zf.read(f"{CAPSULE_ROOT_DIR}/metadata/source.json"))
            assert "/home/" not in source["input_url"]
            assert "paper-repo" in source["input_url"]
