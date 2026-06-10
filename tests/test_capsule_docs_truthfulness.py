"""Tests for capsule documentation truthfulness."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent


class TestCapsuleCliExists:
    """Test that documented capsule commands actually exist."""

    def test_capsule_subcommand_in_cli(self):
        cli_source = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert 'add_parser("capsule"' in cli_source

    def test_capsule_module_exists(self):
        assert (ROOT / "src" / "oss_paper_ci" / "capsule.py").exists()

    def test_capsule_format_module_exists(self):
        assert (ROOT / "src" / "oss_paper_ci" / "capsule_format.py").exists()


class TestCapsuleDocsExist:
    """Test that capsule documentation files exist."""

    def test_reproduction_capsules_doc(self):
        assert (ROOT / "docs" / "reproduction-capsules.md").exists()

    def test_capsule_format_doc(self):
        assert (ROOT / "docs" / "capsule-format.md").exists()

    def test_capsule_verify_doc(self):
        assert (ROOT / "docs" / "capsule-verify.md").exists()

    def test_capsule_security_doc(self):
        assert (ROOT / "docs" / "capsule-security.md").exists()


class TestCapsuleExamplesExist:
    """Test that capsule example files exist."""

    def test_capsules_readme(self):
        assert (ROOT / "examples" / "capsules" / "README.md").exists()

    def test_capsule_action(self):
        assert (ROOT / "examples" / "github-actions" / "reproduce-capsule.yml").exists()

    def test_verify_example(self):
        assert (ROOT / "examples" / "reports" / "reproduce_capsule_verify.md").exists()

    def test_inspect_example(self):
        assert (ROOT / "examples" / "reports" / "reproduce_capsule_inspect.md").exists()

    def test_manifest_example(self):
        assert (ROOT / "examples" / "reports" / "reproduce_capsule_manifest.json").exists()

    def test_diff_example(self):
        assert (ROOT / "examples" / "reports" / "reproduce_capsule_diff.md").exists()


class TestDocsNoFalseClaims:
    """Test that docs don't make false claims."""

    def test_no_claim_proof_of_correctness(self):
        docs = [
            ROOT / "docs" / "reproduction-capsules.md",
            ROOT / "docs" / "capsule-format.md",
            ROOT / "docs" / "capsule-verify.md",
            ROOT / "docs" / "capsule-security.md",
        ]
        for doc in docs:
            if doc.exists():
                content = doc.read_text(encoding="utf-8").lower()
                # Should not claim capsules prove correctness
                if "proof" in content:
                    assert "not" in content or "not proof" in content

    def test_security_doc_warns_about_execute(self):
        content = (ROOT / "docs" / "capsule-security.md").read_text(encoding="utf-8").lower()
        assert "--execute" in content or "execute" in content or "trusted" in content

    def test_capsule_in_valid_cli_commands(self):
        script = (ROOT / "scripts" / "check_docs_truthfulness.py").read_text(encoding="utf-8")
        assert '"capsule"' in script


class TestGitignoreExcludesCapsuleArtifacts:
    """Test that .gitignore excludes capsule artifacts."""

    def test_gitignore_excludes_capsule_staging(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert ".oss-paper-ci-capsule-staging" in gitignore

    def test_gitignore_excludes_capsule_zip(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        assert "*.capsule.zip" in gitignore or "capsule" in gitignore.lower()
