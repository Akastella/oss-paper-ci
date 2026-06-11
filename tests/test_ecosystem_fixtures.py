"""Tests for multi-language fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


class TestRFixture:
    """Test R fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "r_ready_repo" / "README.md").exists()

    def test_has_description(self):
        assert (FIXTURES / "r_ready_repo" / "DESCRIPTION").exists()

    def test_has_renv_lock(self):
        assert (FIXTURES / "r_ready_repo" / "renv.lock").exists()

    def test_has_scripts(self):
        scripts = list((FIXTURES / "r_ready_repo" / "scripts").glob("*.R"))
        assert len(scripts) > 0


class TestJuliaFixture:
    """Test Julia fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "julia_ready_repo" / "README.md").exists()

    def test_has_project_toml(self):
        assert (FIXTURES / "julia_ready_repo" / "Project.toml").exists()

    def test_has_scripts(self):
        scripts = list((FIXTURES / "julia_ready_repo" / "scripts").glob("*.jl"))
        assert len(scripts) > 0


class TestMatlabFixture:
    """Test MATLAB fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "matlab_minimal_repo" / "README.md").exists()

    def test_has_run_m(self):
        assert (FIXTURES / "matlab_minimal_repo" / "run.m").exists()


class TestNodeFixture:
    """Test Node.js fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "node_minimal_repo" / "README.md").exists()

    def test_has_package_json(self):
        assert (FIXTURES / "node_minimal_repo" / "package.json").exists()


class TestRustFixture:
    """Test Rust fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "rust_minimal_repo" / "README.md").exists()

    def test_has_cargo_toml(self):
        assert (FIXTURES / "rust_minimal_repo" / "Cargo.toml").exists()

    def test_has_src(self):
        assert (FIXTURES / "rust_minimal_repo" / "src" / "main.rs").exists()


class TestJavaFixture:
    """Test Java fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "java_minimal_repo" / "README.md").exists()

    def test_has_pom_xml(self):
        assert (FIXTURES / "java_minimal_repo" / "pom.xml").exists()

    def test_has_source(self):
        assert (FIXTURES / "java_minimal_repo" / "src" / "main" / "java" / "Demo.java").exists()


class TestCppFixture:
    """Test C++ fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "cpp_minimal_repo" / "README.md").exists()

    def test_has_cmake(self):
        assert (FIXTURES / "cpp_minimal_repo" / "CMakeLists.txt").exists()

    def test_has_source(self):
        assert (FIXTURES / "cpp_minimal_repo" / "src" / "main.cpp").exists()


class TestWorkflowFixture:
    """Test workflow fixture completeness."""

    def test_has_readme(self):
        assert (FIXTURES / "workflow_repo" / "README.md").exists()

    def test_has_snakefile(self):
        assert (FIXTURES / "workflow_repo" / "Snakefile").exists()

    def test_has_makefile(self):
        assert (FIXTURES / "workflow_repo" / "Makefile").exists()

    def test_has_run_sh(self):
        assert (FIXTURES / "workflow_repo" / "run.sh").exists()


class TestNoBinaries:
    """Test that fixtures contain no binaries."""

    def test_no_executables(self):
        binary_extensions = {".exe", ".dll", ".so", ".dylib", ".o", ".class"}
        for fixture_dir in FIXTURES.iterdir():
            if not fixture_dir.is_dir():
                continue
            for f in fixture_dir.rglob("*"):
                if f.suffix.lower() in binary_extensions:
                    pytest.fail(f"Binary found in fixture: {f}")
