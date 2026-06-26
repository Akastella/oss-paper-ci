"""Integration tests for adapter registry with reproduce system."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.ecosystems import detect_ecosystems, get_ecosystem_info, list_ecosystems


class TestEcosystemsDelegatesToRegistry:
    """Test that ecosystems.py properly delegates to adapter registry."""

    def test_detect_ecosystems_finds_python(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname="test"\n')
        (tmp_path / "main.py").write_text("print('hello')\n")
        ecosystems = detect_ecosystems(str(tmp_path))
        ids = [e.id for e in ecosystems]
        assert "python" in ids

    def test_detect_ecosystems_finds_r(self, tmp_path):
        (tmp_path / "DESCRIPTION").write_text("Package: test\n")
        ecosystems = detect_ecosystems(str(tmp_path))
        ids = [e.id for e in ecosystems]
        assert "r" in ids

    def test_detect_ecosystems_empty(self, tmp_path):
        ecosystems = detect_ecosystems(str(tmp_path))
        assert len(ecosystems) == 0

    def test_ecosystem_has_required_fields(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text('[project]\nname="test"\n')
        ecosystems = detect_ecosystems(str(tmp_path))
        python_eco = next(e for e in ecosystems if e.id == "python")
        d = python_eco.to_dict()
        assert "id" in d
        assert "display_name" in d
        assert "support_level" in d
        assert "runtime_available" in d
        assert "limitations" in d

    def test_get_ecosystem_info_python(self):
        info = get_ecosystem_info("python")
        assert info is not None
        assert info["id"] == "python"
        assert info["support_level"] == "native"

    def test_get_ecosystem_info_unknown(self):
        info = get_ecosystem_info("nonexistent")
        assert info is None

    def test_list_ecosystems(self):
        ecosystems = list_ecosystems()
        assert len(ecosystems) >= 12
        ids = [e["id"] for e in ecosystems]
        assert "python" in ids
        assert "r" in ids
        assert "shell" in ids


class TestReproduceAdapterCompatibility:
    """Test that reproduce system still works with adapter-based ecosystems."""

    def test_detect_ecosystems_returns_language_ecosystem(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("numpy\n")
        ecosystems = detect_ecosystems(str(tmp_path))
        python_eco = next(e for e in ecosystems if e.id == "python")
        # Should be a LanguageEcosystem dataclass
        assert hasattr(python_eco, "id")
        assert hasattr(python_eco, "support_level")
        assert hasattr(python_eco, "runtime_available")
