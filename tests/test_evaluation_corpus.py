"""Tests for evaluation corpus structure."""

from pathlib import Path

import pytest


CORPUS_DIR = Path(__file__).parent.parent / "examples" / "evaluation-corpus"


class TestCorpusStructure:
    """Test corpus directory structure."""

    def test_corpus_dir_exists(self):
        assert CORPUS_DIR.exists()
        assert CORPUS_DIR.is_dir()

    def test_corpus_readme_exists(self):
        readme = CORPUS_DIR / "README.md"
        assert readme.exists()
        content = readme.read_text()
        assert "synthetic" in content.lower()

    def test_expected_outcomes_exists(self):
        outcomes = CORPUS_DIR / "expected_outcomes.yml"
        assert outcomes.exists()

    def test_minimum_repo_count(self):
        """Should have at least 12 repos."""
        repos = [d for d in CORPUS_DIR.iterdir()
                 if d.is_dir() and not d.name.startswith(".")]
        assert len(repos) >= 12


class TestCorpusRepos:
    """Test individual corpus repos."""

    def test_all_repos_have_readme(self):
        """Every repo should have a README."""
        for repo_dir in CORPUS_DIR.iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                # Check for README directly or in before/after subdirs
                has_readme = (repo_dir / "README.md").exists()
                if not has_readme:
                    # Check before/after structure
                    for sub in ["before", "after"]:
                        sub_path = repo_dir / sub
                        if sub_path.is_dir():
                            assert (sub_path / "README.md").exists(), \
                                f"{repo_dir.name}/{sub} missing README.md"
                else:
                    assert has_readme, f"{repo_dir.name} missing README.md"

    def test_no_large_files(self):
        """No file should exceed 10KB."""
        for path in CORPUS_DIR.rglob("*"):
            if path.is_file():
                size = path.stat().st_size
                assert size < 10240, f"{path} is too large ({size} bytes)"

    def test_no_binary_files(self):
        """No binary files allowed."""
        binary_extensions = {'.exe', '.dll', '.so', '.dylib', '.o', '.class',
                            '.zip', '.tar', '.gz', '.rar', '.7z'}
        for path in CORPUS_DIR.rglob("*"):
            if path.is_file():
                assert path.suffix.lower() not in binary_extensions, \
                    f"Binary file found: {path}"

    def test_python_good_repro_structure(self):
        """python_good_repro should have complete structure."""
        repo = CORPUS_DIR / "python_good_repro"
        assert (repo / "README.md").exists()
        assert (repo / "requirements.txt").exists()
        assert (repo / "scripts").is_dir()
        assert (repo / "data" / "README.md").exists()
        assert (repo / "results" / "metrics.json").exists()

    def test_unsafe_script_not_executable(self):
        """unsafe_script_project should have safety warnings."""
        repo = CORPUS_DIR / "unsafe_script_project"
        readme = repo / "README.md"
        if readme.exists():
            content = readme.read_text()
            # Should mention dry-run or safety
            assert any(word in content.lower() for word in
                       ["dry-run", "dry run", "not executed", "safety", "testing"])


class TestLanguageFixtures:
    """Test language-specific fixtures."""

    def test_python_fixtures(self):
        """Should have multiple Python fixtures."""
        python_repos = list(CORPUS_DIR.glob("python_*"))
        assert len(python_repos) >= 4

    def test_r_fixture(self):
        """Should have R fixture."""
        assert (CORPUS_DIR / "r_repro_project").exists()

    def test_julia_fixture(self):
        """Should have Julia fixture."""
        assert (CORPUS_DIR / "julia_project").exists()

    def test_node_fixture(self):
        """Should have Node.js fixture."""
        assert (CORPUS_DIR / "node_analysis_project").exists()

    def test_make_fixture(self):
        """Should have Make fixture."""
        assert (CORPUS_DIR / "make_workflow_project").exists()

    def test_snakemake_fixture(self):
        """Should have Snakemake fixture."""
        assert (CORPUS_DIR / "snakemake_project").exists()

    def test_cpp_fixture(self):
        """Should have C++ fixture."""
        assert (CORPUS_DIR / "cpp_build_project").exists()
