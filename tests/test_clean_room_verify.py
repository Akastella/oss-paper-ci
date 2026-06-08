"""Tests for clean room verification script."""

import zipfile
from pathlib import Path

import pytest


class TestCleanRoomScript:
    """Test the verify_clean_package.py script exists and is importable."""

    def test_script_exists(self):
        assert Path("scripts/verify_clean_package.py").exists()

    def test_forbidden_patterns_callable(self):
        from scripts.verify_clean_package import check_forbidden
        assert callable(check_forbidden)

    def test_required_patterns_callable(self):
        from scripts.verify_clean_package import check_required
        assert callable(check_required)

    def test_forbidden_list_defined(self):
        from scripts.verify_clean_package import FORBIDDEN
        assert len(FORBIDDEN) > 0
        assert ".git" in FORBIDDEN

    def test_required_list_defined(self):
        from scripts.verify_clean_package import REQUIRED
        assert len(REQUIRED) > 0
        assert "README.md" in REQUIRED
        assert "pyproject.toml" in REQUIRED

    def test_forbidden_catches_git(self, tmp_path):
        """A ZIP containing .git should fail forbidden check."""
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(".git/config", "some content")
        issues = check_forbidden(zip_path)
        assert len(issues) > 0
        assert any(".git" in i for i in issues)

    def test_forbidden_catches_pycache(self, tmp_path):
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("src/__pycache__/mod.cpython-312.pyc", "bytecode")
        issues = check_forbidden(zip_path)
        assert len(issues) > 0

    def test_forbidden_catches_dev_history(self, tmp_path):
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "test.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("dev-history/notes.md", "content")
        issues = check_forbidden(zip_path)
        assert len(issues) > 0

    def test_forbidden_clean_zip_passes(self, tmp_path):
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "clean.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("README.md", "# Hello")
            zf.writestr("src/main.py", "print('hi')")
        issues = check_forbidden(zip_path)
        assert len(issues) == 0

    def test_required_catches_missing_readme(self, tmp_path):
        from scripts.verify_clean_package import check_required
        zip_path = tmp_path / "noreadme.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("pyproject.toml", "[project]")
        issues = check_required(zip_path)
        assert any("README.md" in i for i in issues)

    def test_required_all_present_passes(self, tmp_path):
        from scripts.verify_clean_package import check_required
        zip_path = tmp_path / "complete.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("README.md", "# Hello")
            zf.writestr("LICENSE", "MIT")
            zf.writestr("pyproject.toml", "[project]")
            zf.writestr("src/oss_paper_ci/__init__.py", "")
            zf.writestr("src/oss_paper_ci/cli.py", "")
            zf.writestr("tests/test_cli.py", "")
            zf.writestr("docs/usage.md", "# Usage")
            zf.writestr("action.yml", "name: test")
        issues = check_required(zip_path)
        assert len(issues) == 0

    def test_forbidden_catches_sarif(self, tmp_path):
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "sarif.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("test.sarif", '{"version": "2.1.0"}')
        issues = check_forbidden(zip_path)
        assert len(issues) > 0

    def test_forbidden_catches_release_artifacts(self, tmp_path):
        from scripts.verify_clean_package import check_forbidden
        zip_path = tmp_path / "release.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr("release-artifacts/old.zip", "data")
        issues = check_forbidden(zip_path)
        assert len(issues) > 0
