"""Tests for capsule builder."""

from __future__ import annotations

import json
import os
import zipfile
from pathlib import Path

import pytest

from oss_paper_ci.capsule import build_capsule
from oss_paper_ci.capsule_format import CAPSULE_ROOT_DIR
from oss_paper_ci.reproduce import ReproduceResult, CommandResult
from oss_paper_ci.environment import EnvironmentPlan, EnvironmentFile, InstallStep


def _make_result(**kwargs) -> ReproduceResult:
    """Create a ReproduceResult with sensible defaults."""
    defaults = {
        "input_url": "https://github.com/owner/repo",
        "repo_url": "https://github.com/owner/repo",
        "resolved_source": "github",
        "clone_ok": True,
        "dry_run": True,
        "environment": EnvironmentPlan(
            environment_files=[EnvironmentFile("requirements.txt", "requirements.txt")],
            install_steps=[InstallStep("Install deps", "pip install -r requirements.txt", "pip")],
        ),
        "reproduction_commands": ["python scripts/train.py"],
        "command_results": [CommandResult(command="python scripts/train.py", exit_code=0, block_reason="dry_run")],
        "scan_status": "dry_run",
        "limitations": ["Test limitation"],
    }
    defaults.update(kwargs)
    return ReproduceResult(**defaults)


class TestBuildCapsule:
    """Test build_capsule function."""

    def test_creates_zip(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        assert out.exists()
        assert zipfile.is_zipfile(str(out))

    def test_zip_has_root_dir(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert any(n.startswith(f"{CAPSULE_ROOT_DIR}/") for n in names)

    def test_has_capsule_json(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            manifest = json.loads(zf.read(f"{CAPSULE_ROOT_DIR}/capsule.json"))
            assert manifest["schema_version"] == "0.1"
            assert manifest["capsule_type"] == "oss-paper-ci-reproduction-capsule"

    def test_has_sha256sums(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            sha = zf.read(f"{CAPSULE_ROOT_DIR}/SHA256SUMS").decode("utf-8")
            assert len(sha.strip().split("\n")) > 0

    def test_has_reports(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert f"{CAPSULE_ROOT_DIR}/reports/reproduce_report.json" in names
            assert f"{CAPSULE_ROOT_DIR}/reports/reproduce_report.md" in names
            assert f"{CAPSULE_ROOT_DIR}/reports/reproduce_report.html" in names

    def test_has_metadata(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert f"{CAPSULE_ROOT_DIR}/metadata/source.json" in names
            assert f"{CAPSULE_ROOT_DIR}/metadata/environment.json" in names
            assert f"{CAPSULE_ROOT_DIR}/metadata/commands.json" in names
            assert f"{CAPSULE_ROOT_DIR}/metadata/limitations.md" in names

    def test_has_logs(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            names = zf.namelist()
            assert f"{CAPSULE_ROOT_DIR}/logs/command_000.stdout.txt" in names

    def test_has_artifact_index(self, tmp_path):
        result = _make_result()
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            idx = json.loads(zf.read(f"{CAPSULE_ROOT_DIR}/artifacts/artifact_index.json"))
            assert "total_artifacts" in idx

    def test_redacts_absolute_paths(self, tmp_path):
        result = _make_result(
            input_url="C:\\Users\\test\\repo",
            repo_url="/home/user/repo",
        )
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            source = json.loads(zf.read(f"{CAPSULE_ROOT_DIR}/metadata/source.json"))
            assert "C:\\" not in source["input_url"]
            assert "/home/" not in source["repo_url"]

    def test_execute_mode_capsule(self, tmp_path):
        result = _make_result(
            dry_run=False,
            command_results=[
                CommandResult(command="python train.py", exit_code=0, stdout_excerpt="done"),
            ],
        )
        out = tmp_path / "test.zip"
        build_capsule(result, str(out))
        with zipfile.ZipFile(str(out)) as zf:
            manifest = json.loads(zf.read(f"{CAPSULE_ROOT_DIR}/capsule.json"))
            assert manifest["execution"]["mode"] == "execute"
