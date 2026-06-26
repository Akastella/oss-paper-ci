"""Tests for adapter documentation truthfulness."""
from __future__ import annotations
from pathlib import Path
import pytest

ROOT = Path(__file__).parent.parent


class TestAdapterDocsExist:
    """Test that required adapter documentation files exist."""

    REQUIRED_DOCS = [
        "docs/adapter-schema.md",
        "docs/adapter-registry.md",
        "docs/python-adapter.md",
        "docs/r-adapter.md",
        "docs/julia-adapter.md",
        "docs/node-adapter.md",
        "docs/rust-adapter.md",
        "docs/java-adapter.md",
        "docs/cpp-adapter.md",
        "docs/make-adapter.md",
        "docs/snakemake-adapter.md",
        "docs/nextflow-adapter.md",
        "docs/shell-adapter.md",
        "docs/adapter-safety.md",
        "docs/adapter-limitations.md",
    ]

    @pytest.mark.parametrize("doc_path", REQUIRED_DOCS)
    def test_adapter_doc_exists(self, doc_path):
        assert (ROOT / doc_path).exists(), f"Missing adapter doc: {doc_path}"


class TestAdapterDocsNoOverclaim:
    """Test that adapter docs don't make exaggerated claims."""

    def test_no_correctness_claims(self):
        """Docs should not claim scientific correctness."""
        docs_dir = ROOT / "docs"
        if not docs_dir.exists():
            pytest.skip("docs/ not found")
        for doc in docs_dir.glob("*adapter*"):
            if doc.is_file():
                content = doc.read_text(encoding="utf-8").lower()
                assert "proves correctness" not in content, f"{doc.name} claims correctness"
                assert "scientifically correct" not in content, f"{doc.name} claims correctness"

    def test_no_auto_fix_claims(self):
        """Docs should not claim automatic code fixing."""
        docs_dir = ROOT / "docs"
        if not docs_dir.exists():
            pytest.skip("docs/ not found")
        for doc in docs_dir.glob("*adapter*"):
            if doc.is_file():
                content = doc.read_text(encoding="utf-8").lower()
                assert "automatically fix" not in content, f"{doc.name} claims auto-fix"

    def test_shell_adapter_docs_warn_about_dangerous(self):
        """Shell adapter docs should warn about dangerous commands."""
        shell_doc = ROOT / "docs" / "shell-adapter.md"
        if shell_doc.exists():
            content = shell_doc.read_text(encoding="utf-8").lower()
            assert "dangerous" in content or "safety" in content or "block" in content


class TestAdapterExamplesExist:
    """Test that adapter examples exist."""

    def test_python_example_exists(self):
        example = ROOT / "examples" / "adapters" / "python"
        assert example.exists(), "Missing examples/adapters/python/"

    def test_shell_unsafe_example_exists(self):
        example = ROOT / "examples" / "adapters" / "shell-unsafe"
        assert example.exists(), "Missing examples/adapters/shell-unsafe/"
