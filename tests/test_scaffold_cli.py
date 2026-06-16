"""Tests for scaffold CLI command."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run(*args, env_extra=None):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    return subprocess.run(
        [sys.executable, "-m", "oss_paper_ci", *args],
        capture_output=True, text=True, timeout=60,
        encoding="utf-8", errors="replace", env=env,
    )


class TestAdoptCommand:
    """Test adopt command."""

    def test_adopt_runs(self):
        result = _run("adopt", "tests/fixtures/adoption_missing_repo")
        assert result.returncode == 0
        assert "Adoption Plan" in result.stdout

    def test_adopt_json_format(self):
        result = _run("adopt", "tests/fixtures/adoption_missing_repo", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "missing_files" in data

    def test_adopt_output_file(self, tmp_path):
        out = str(tmp_path / "plan.md")
        result = _run("adopt", "tests/fixtures/adoption_missing_repo", "--output", out)
        assert result.returncode == 0
        assert Path(out).exists()

    def test_adopt_plain_no_ansi(self):
        result = _run("--plain", "adopt", "tests/fixtures/adoption_missing_repo")
        assert "\x1b[" not in result.stdout


class TestScaffoldCommand:
    """Test scaffold command."""

    def test_scaffold_dry_run_default(self):
        result = _run("scaffold", "tests/fixtures/adoption_missing_repo")
        assert result.returncode == 0
        assert "Would create" in result.stdout or "Scaffold" in result.stdout

    def test_scaffold_dry_run_no_write(self, tmp_path):
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree("tests/fixtures/adoption_missing_repo", repo)
        result = _run("scaffold", str(repo))
        assert result.returncode == 0
        # Should not have created files
        assert not (repo / "reproducibility.yml").exists()

    def test_scaffold_apply_creates_files(self, tmp_path):
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree("tests/fixtures/adoption_missing_repo", repo)
        result = _run("scaffold", str(repo), "--apply")
        assert result.returncode == 0
        assert (repo / "reproducibility.yml").exists()

    def test_scaffold_apply_no_overwrite(self, tmp_path):
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree("tests/fixtures/adoption_missing_repo", repo)
        (repo / "reproducibility.yml").write_text("existing")
        result = _run("scaffold", str(repo), "--apply")
        assert result.returncode == 0
        # Should not overwrite
        assert (repo / "reproducibility.yml").read_text() == "existing"

    def test_scaffold_force_overwrites(self, tmp_path):
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree("tests/fixtures/adoption_missing_repo", repo)
        (repo / "reproducibility.yml").write_text("existing")
        result = _run("scaffold", str(repo), "--apply", "--force")
        assert result.returncode == 0
        assert (repo / "reproducibility.yml").read_text() != "existing"


class TestFixCommand:
    """Test fix command."""

    def test_fix_preview_runs(self):
        result = _run("fix", "preview", "tests/fixtures/adoption_missing_repo")
        assert result.returncode == 0
        assert "Adoption Plan" in result.stdout or "Missing" in result.stdout

    def test_fix_preview_json(self):
        result = _run("fix", "preview", "tests/fixtures/adoption_missing_repo", "--format", "json")
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert "missing_files" in data

    def test_fix_apply_requires_yes(self):
        result = _run("fix", "apply", "tests/fixtures/adoption_missing_repo")
        assert result.returncode != 0

    def test_fix_apply_with_yes(self, tmp_path):
        import shutil
        repo = tmp_path / "repo"
        shutil.copytree("tests/fixtures/adoption_missing_repo", repo)
        result = _run("fix", "apply", str(repo), "--yes")
        assert result.returncode == 0
