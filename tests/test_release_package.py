"""Tests for release packaging."""

import zipfile
from pathlib import Path

import pytest


class TestShouldExclude:
    """Tests for the should_exclude function in make_release_package."""

    def test_excludes_git_config(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".git/config")

    def test_excludes_git_directory(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".git")

    def test_excludes_pycache(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("src/__pycache__/mod.py")

    def test_excludes_egg_info(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("src/pkg.egg-info/PKG-INFO")

    def test_excludes_pytest_cache(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".pytest_cache/v/cache/lastfailed")

    def test_excludes_dist(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("dist/old.tar.gz")

    def test_excludes_build(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("build/bdist.win/test")

    def test_excludes_dev_history(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("dev-history/notes.md")

    def test_excludes_round_json(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("round3_minimal_bad.json")

    def test_excludes_round_md(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("ROUND4_TASKBOARD.md")

    def test_excludes_final_deliverables(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("FINAL_DELIVERABLES_ROUND3.md")

    def test_excludes_red_team_audit(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("RED_TEAM_AUDIT_ROUND2.md")

    def test_excludes_report_md(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("OSS_PAPER_CI_REPORT.md")

    def test_excludes_report_sarif(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("OSS_PAPER_CI_REPORT.sarif")

    def test_excludes_sarif_files(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("test.sarif")

    def test_excludes_eggs_dir(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".eggs/pkg.egg")

    def test_excludes_claude_dir(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".claude/settings.json")

    def test_excludes_coverage(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude(".coverage")

    def test_excludes_htmlcov(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("htmlcov/index.html")

    def test_excludes_pyc_files(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("src/mod.cpython-312.pyc")

    def test_excludes_pyo_files(self):
        from scripts.make_release_package import should_exclude
        assert should_exclude("src/mod.pyo")


class TestShouldInclude:
    """Tests that important files are NOT excluded."""

    def test_includes_readme(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("README.md")

    def test_includes_source(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("src/oss_paper_ci/__init__.py")

    def test_includes_tests(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("tests/test_cli.py")

    def test_includes_docs(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("docs/usage.md")

    def test_includes_action_yml(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("action.yml")

    def test_includes_license(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("LICENSE")

    def test_includes_pyproject(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("pyproject.toml")

    def test_includes_changelog(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("CHANGELOG.md")

    def test_includes_contributing(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("CONTRIBUTING.md")

    def test_includes_security(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("SECURITY.md")

    def test_includes_github_dir(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude(".github/workflows/ci.yml")

    def test_includes_gitignore(self):
        # .gitignore must be included in clean package (GitHub requires it)
        from scripts.make_release_package import should_exclude
        assert not should_exclude(".gitignore")

    def test_excludes_git_directory(self):
        # .git/ directory must be excluded
        from scripts.make_release_package import should_exclude
        assert should_exclude(".git/config")
        assert should_exclude(".git/HEAD")

    def test_includes_examples(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("examples/github-actions/oss-paper-ci.yml")

    def test_includes_scripts(self):
        from scripts.make_release_package import should_exclude
        assert not should_exclude("scripts/comment_pr.py")
