"""Tests for reproduce documentation truthfulness.

Verifies that reproduce-related documentation is accurate and doesn't
make false claims about capabilities.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestReproduceCliExists:
    """Test that documented reproduce commands actually exist."""

    def test_reproduce_subcommand_in_cli(self):
        cli_source = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert 'add_parser("reproduce"' in cli_source

    def test_reproduce_module_exists(self):
        assert (ROOT / "src" / "oss_paper_ci" / "reproduce.py").exists()

    def test_reproduce_report_module_exists(self):
        assert (ROOT / "src" / "oss_paper_ci" / "reporting" / "reproduce_report.py").exists()


class TestDemoRepoExists:
    """Test that demo reproduce repo exists and is complete."""

    def test_demo_repo_dir_exists(self):
        assert (ROOT / "examples" / "demo-reproduce-repo").is_dir()

    def test_demo_repo_has_scripts(self):
        scripts = ROOT / "examples" / "demo-reproduce-repo" / "scripts"
        assert scripts.is_dir()
        assert (scripts / "train.py").exists()

    def test_demo_repo_has_requirements(self):
        assert (ROOT / "examples" / "demo-reproduce-repo" / "requirements.txt").exists()

    def test_demo_repo_has_reproducibility_yml(self):
        assert (ROOT / "examples" / "demo-reproduce-repo" / "reproducibility.yml").exists()


class TestReproduceReportsExist:
    """Test that example reproduce reports exist."""

    def test_dry_run_report_exists(self):
        assert (ROOT / "examples" / "reports" / "reproduce_demo_dry_run.md").exists()

    def test_json_report_exists(self):
        assert (ROOT / "examples" / "reports" / "reproduce_demo_report.json").exists()

    def test_md_report_exists(self):
        assert (ROOT / "examples" / "reports" / "reproduce_demo_report.md").exists()

    def test_html_report_exists(self):
        assert (ROOT / "examples" / "reports" / "reproduce_demo_report.html").exists()


class TestDocsNoFalseClaims:
    """Test that docs don't make false claims."""

    def test_no_claim_to_guarantee_reproduction(self):
        docs = ROOT / "docs" / "reproduce.md"
        if docs.exists():
            content = docs.read_text(encoding="utf-8").lower()
            assert "guarantee" not in content or "does not guarantee" in content

    def test_no_claim_to_verify_correctness(self):
        docs = ROOT / "docs" / "reproduce.md"
        if docs.exists():
            content = docs.read_text(encoding="utf-8").lower()
            # Check it doesn't claim to verify correctness
            if "verify" in content and "correctness" in content:
                assert "does not verify" in content or "not verify" in content

    def test_security_doc_exists(self):
        assert (ROOT / "docs" / "reproduce-security.md").exists()

    def test_security_doc_warns_about_execute(self):
        content = (ROOT / "docs" / "reproduce-security.md").read_text(encoding="utf-8").lower()
        assert "--execute" in content or "execute" in content

    def test_html_report_no_external_cdn(self):
        html_report = ROOT / "examples" / "reports" / "reproduce_demo_report.html"
        if html_report.exists():
            content = html_report.read_text(encoding="utf-8").lower()
            assert "cdn.jsdelivr" not in content
            assert "cdnjs.cloudflare" not in content
            assert "googleapis.com" not in content


class TestGitignoreExcludesReproduceArtifacts:
    """Test that .gitignore excludes reproduce artifacts."""

    def test_gitignore_excludes_repro_workdir(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".oss-paper-ci-repro" in gitignore


class TestReproduceInDocsTruthfulness:
    """Test that check_docs_truthfulness.py knows about reproduce."""

    def test_reproduce_in_valid_cli_commands(self):
        script = (ROOT / "scripts" / "check_docs_truthfulness.py").read_text(encoding="utf-8")
        assert '"reproduce"' in script
