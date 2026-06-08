"""Tests for cross-language detection and checks."""

import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"


class TestRDetection:
    """Test R repository detection and scanning."""

    def test_r_ready_repo_has_description(self):
        repo = FIXTURES / "r_ready_repo"
        if not repo.exists():
            pytest.skip("r_ready_repo fixture not found")
        assert (repo / "DESCRIPTION").exists()

    def test_r_ready_repo_has_renv(self):
        repo = FIXTURES / "r_ready_repo"
        if not repo.exists():
            pytest.skip("r_ready_repo fixture not found")
        assert (repo / "renv.lock").exists()

    def test_r_ready_repo_has_scripts(self):
        repo = FIXTURES / "r_ready_repo"
        if not repo.exists():
            pytest.skip("r_ready_repo fixture not found")
        r_files = list((repo / "scripts").glob("*.R"))
        assert len(r_files) > 0

    def test_r_scan_produces_results(self):
        if not (FIXTURES / "r_ready_repo").exists():
            pytest.skip("r_ready_repo fixture not found")
        from oss_paper_ci.scanner import scan
        repo = str(FIXTURES / "r_ready_repo")
        report = scan(repo)
        assert len(report.checks) > 0
        assert report.summary.score > 0

    def test_r_detected_language(self):
        if not (FIXTURES / "r_ready_repo").exists():
            pytest.skip("r_ready_repo fixture not found")
        from oss_paper_ci.scanner import scan
        report = scan(str(FIXTURES / "r_ready_repo"))
        assert "R" in report.repository.detected_languages

    def test_r_repo_has_data_dir(self):
        repo = FIXTURES / "r_ready_repo"
        if not repo.exists():
            pytest.skip("r_ready_repo fixture not found")
        assert (repo / "data").is_dir()

    def test_r_repo_has_figures_dir(self):
        repo = FIXTURES / "r_ready_repo"
        if not repo.exists():
            pytest.skip("r_ready_repo fixture not found")
        assert (repo / "figures").is_dir()


class TestJuliaDetection:
    """Test Julia repository detection and scanning."""

    def test_julia_ready_repo_has_project(self):
        repo = FIXTURES / "julia_ready_repo"
        if not repo.exists():
            pytest.skip("julia_ready_repo fixture not found")
        assert (repo / "Project.toml").exists()

    def test_julia_ready_repo_has_manifest(self):
        repo = FIXTURES / "julia_ready_repo"
        if not repo.exists():
            pytest.skip("julia_ready_repo fixture not found")
        assert (repo / "Manifest.toml").exists()

    def test_julia_ready_repo_has_scripts(self):
        repo = FIXTURES / "julia_ready_repo"
        if not repo.exists():
            pytest.skip("julia_ready_repo fixture not found")
        jl_files = list((repo / "scripts").glob("*.jl"))
        assert len(jl_files) > 0

    def test_julia_scan_produces_results(self):
        if not (FIXTURES / "julia_ready_repo").exists():
            pytest.skip("julia_ready_repo fixture not found")
        from oss_paper_ci.scanner import scan
        repo = str(FIXTURES / "julia_ready_repo")
        report = scan(repo)
        assert len(report.checks) > 0

    def test_julia_detected_language(self):
        if not (FIXTURES / "julia_ready_repo").exists():
            pytest.skip("julia_ready_repo fixture not found")
        from oss_paper_ci.scanner import scan
        report = scan(str(FIXTURES / "julia_ready_repo"))
        assert "Julia" in report.repository.detected_languages

    def test_julia_repo_has_data_dir(self):
        repo = FIXTURES / "julia_ready_repo"
        if not repo.exists():
            pytest.skip("julia_ready_repo fixture not found")
        assert (repo / "data").is_dir()

    def test_julia_repo_has_results_dir(self):
        repo = FIXTURES / "julia_ready_repo"
        if not repo.exists():
            pytest.skip("julia_ready_repo fixture not found")
        assert (repo / "results").is_dir()


class TestMATLABDetection:
    """Test MATLAB repository detection and scanning."""

    def test_matlab_repo_has_scripts(self):
        repo = FIXTURES / "matlab_minimal_repo"
        if not repo.exists():
            pytest.skip("matlab_minimal_repo fixture not found")
        m_files = list((repo / "scripts").glob("*.m"))
        assert len(m_files) > 0

    def test_matlab_repo_has_startup(self):
        repo = FIXTURES / "matlab_minimal_repo"
        if not repo.exists():
            pytest.skip("matlab_minimal_repo fixture not found")
        assert (repo / "startup.m").exists()

    def test_matlab_scan_produces_results(self):
        if not (FIXTURES / "matlab_minimal_repo").exists():
            pytest.skip("matlab_minimal_repo fixture not found")
        from oss_paper_ci.scanner import scan
        repo = str(FIXTURES / "matlab_minimal_repo")
        report = scan(repo)
        assert len(report.checks) > 0


class TestMakeSnakemake:
    """Test Make/Snakemake repository detection and scanning."""

    def test_make_repo_has_makefile(self):
        repo = FIXTURES / "make_snakemake_repo"
        if not repo.exists():
            pytest.skip("make_snakemake_repo fixture not found")
        assert (repo / "Makefile").exists()

    def test_make_repo_has_snakefile(self):
        repo = FIXTURES / "make_snakemake_repo"
        if not repo.exists():
            pytest.skip("make_snakemake_repo fixture not found")
        assert (repo / "Snakefile").exists()

    def test_make_repo_has_scripts(self):
        repo = FIXTURES / "make_snakemake_repo"
        if not repo.exists():
            pytest.skip("make_snakemake_repo fixture not found")
        assert (repo / "scripts" / "train.py").exists()

    def test_make_scan_produces_results(self):
        if not (FIXTURES / "make_snakemake_repo").exists():
            pytest.skip("make_snakemake_repo fixture not found")
        from oss_paper_ci.scanner import scan
        repo = str(FIXTURES / "make_snakemake_repo")
        report = scan(repo)
        assert len(report.checks) > 0


class TestMultilanguageDetection:
    """Test language detection for existing cross-language fixtures."""

    def test_r_file_extension_detected(self):
        if not (FIXTURES / "r_ready_repo").exists():
            pytest.skip("r_ready_repo fixture not found")
        from oss_paper_ci.scanner import _detect_languages
        config = type('C', (), {'ignore': type('I', (), {'paths': []})()})()
        langs = _detect_languages(str(FIXTURES / "r_ready_repo"), config)
        assert "R" in langs

    def test_julia_file_extension_detected(self):
        if not (FIXTURES / "julia_ready_repo").exists():
            pytest.skip("julia_ready_repo fixture not found")
        from oss_paper_ci.scanner import _detect_languages
        config = type('C', (), {'ignore': type('I', (), {'paths': []})()})()
        langs = _detect_languages(str(FIXTURES / "julia_ready_repo"), config)
        assert "Julia" in langs
