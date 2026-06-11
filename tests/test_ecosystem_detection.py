"""Tests for language ecosystem detection."""

from __future__ import annotations

from pathlib import Path

import pytest

from oss_paper_ci.ecosystems import (
    ECOSYSTEMS,
    LanguageEcosystem,
    detect_ecosystems,
    get_ecosystem_info,
    list_ecosystems,
)

FIXTURES = Path(__file__).parent / "fixtures"


class TestDetectPython:
    """Test Python ecosystem detection."""

    def test_detects_python_in_ml_repo(self):
        eco = detect_ecosystems(str(FIXTURES / "realistic_ml_repo"))
        ids = [e.id for e in eco]
        assert "python" in ids

    def test_python_support_level(self):
        eco = detect_ecosystems(str(FIXTURES / "realistic_ml_repo"))
        python_eco = next(e for e in eco if e.id == "python")
        assert python_eco.support_level == "native"


class TestDetectR:
    """Test R ecosystem detection."""

    def test_detects_r(self):
        eco = detect_ecosystems(str(FIXTURES / "r_ready_repo"))
        ids = [e.id for e in eco]
        assert "r" in ids

    def test_r_has_env_files(self):
        eco = detect_ecosystems(str(FIXTURES / "r_ready_repo"))
        r_eco = next(e for e in eco if e.id == "r")
        assert len(r_eco.environment_files) > 0
        assert "renv.lock" in r_eco.environment_files or "DESCRIPTION" in r_eco.environment_files

    def test_r_support_level(self):
        eco = detect_ecosystems(str(FIXTURES / "r_ready_repo"))
        r_eco = next(e for e in eco if e.id == "r")
        assert r_eco.support_level == "execute-if-runtime-present"

    def test_r_has_limitations(self):
        eco = detect_ecosystems(str(FIXTURES / "r_ready_repo"))
        r_eco = next(e for e in eco if e.id == "r")
        assert len(r_eco.limitations) > 0


class TestDetectJulia:
    """Test Julia ecosystem detection."""

    def test_detects_julia(self):
        eco = detect_ecosystems(str(FIXTURES / "julia_ready_repo"))
        ids = [e.id for e in eco]
        assert "julia" in ids

    def test_julia_has_project_toml(self):
        eco = detect_ecosystems(str(FIXTURES / "julia_ready_repo"))
        julia_eco = next(e for e in eco if e.id == "julia")
        assert "Project.toml" in julia_eco.environment_files


class TestDetectMatlab:
    """Test MATLAB/Octave ecosystem detection."""

    def test_detects_matlab(self):
        eco = detect_ecosystems(str(FIXTURES / "matlab_minimal_repo"))
        ids = [e.id for e in eco]
        assert "matlab" in ids or "octave" in ids


class TestDetectNode:
    """Test Node.js ecosystem detection."""

    def test_detects_node(self):
        eco = detect_ecosystems(str(FIXTURES / "node_minimal_repo"))
        ids = [e.id for e in eco]
        assert "node" in ids

    def test_node_has_package_json(self):
        eco = detect_ecosystems(str(FIXTURES / "node_minimal_repo"))
        node_eco = next(e for e in eco if e.id == "node")
        assert "package.json" in node_eco.environment_files


class TestDetectRust:
    """Test Rust ecosystem detection."""

    def test_detects_rust(self):
        eco = detect_ecosystems(str(FIXTURES / "rust_minimal_repo"))
        ids = [e.id for e in eco]
        assert "rust" in ids

    def test_rust_has_cargo_toml(self):
        eco = detect_ecosystems(str(FIXTURES / "rust_minimal_repo"))
        rust_eco = next(e for e in eco if e.id == "rust")
        assert "Cargo.toml" in rust_eco.environment_files


class TestDetectJava:
    """Test Java ecosystem detection."""

    def test_detects_java(self):
        eco = detect_ecosystems(str(FIXTURES / "java_minimal_repo"))
        ids = [e.id for e in eco]
        assert "java" in ids

    def test_java_has_pom_xml(self):
        eco = detect_ecosystems(str(FIXTURES / "java_minimal_repo"))
        java_eco = next(e for e in eco if e.id == "java")
        assert "pom.xml" in java_eco.environment_files


class TestDetectCpp:
    """Test C++ ecosystem detection."""

    def test_detects_cpp(self):
        eco = detect_ecosystems(str(FIXTURES / "cpp_minimal_repo"))
        ids = [e.id for e in eco]
        assert "cpp" in ids

    def test_cpp_has_cmake(self):
        eco = detect_ecosystems(str(FIXTURES / "cpp_minimal_repo"))
        cpp_eco = next(e for e in eco if e.id == "cpp")
        assert "CMakeLists.txt" in cpp_eco.environment_files


class TestDetectWorkflow:
    """Test workflow manager detection."""

    def test_detects_snakemake(self):
        eco = detect_ecosystems(str(FIXTURES / "workflow_repo"))
        ids = [e.id for e in eco]
        assert "snakemake" in ids

    def test_detects_make(self):
        eco = detect_ecosystems(str(FIXTURES / "workflow_repo"))
        ids = [e.id for e in eco]
        assert "make" in ids

    def test_detects_shell(self):
        eco = detect_ecosystems(str(FIXTURES / "workflow_repo"))
        ids = [e.id for e in eco]
        assert "shell" in ids


class TestMultipleEcosystems:
    """Test repositories with multiple ecosystems."""

    def test_workflow_repo_has_multiple(self):
        eco = detect_ecosystems(str(FIXTURES / "workflow_repo"))
        assert len(eco) >= 2


class TestEcosystemInfo:
    """Test get_ecosystem_info function."""

    def test_get_python_info(self):
        info = get_ecosystem_info("python")
        assert info is not None
        assert info["id"] == "python"
        assert info["support_level"] == "native"

    def test_get_r_info(self):
        info = get_ecosystem_info("r")
        assert info is not None
        assert info["display_name"] == "R"

    def test_get_unknown(self):
        info = get_ecosystem_info("nonexistent")
        assert info is None


class TestListEcosystems:
    """Test list_ecosystems function."""

    def test_list_not_empty(self):
        ecosystems = list_ecosystems()
        assert len(ecosystems) > 0

    def test_list_has_python(self):
        ecosystems = list_ecosystems()
        ids = [e["id"] for e in ecosystems]
        assert "python" in ids


class TestSerialization:
    """Test to_dict serialization."""

    def test_to_dict(self):
        eco = detect_ecosystems(str(FIXTURES / "r_ready_repo"))
        r_eco = next(e for e in eco if e.id == "r")
        d = r_eco.to_dict()
        assert d["id"] == "r"
        assert "environment_files" in d
        assert "limitations" in d
