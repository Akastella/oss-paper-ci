"""Tests for the adapter registry."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.registry import get_registry, reset_registry, AdapterRegistry
from oss_paper_ci.adapters.base import AdapterBase, AdapterDetection, AdapterPlan


class TestRegistryBasic:
    """Basic registry functionality tests."""

    def test_get_registry_returns_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2

    def test_registry_has_adapters(self):
        registry = get_registry()
        adapters = registry.list_adapters()
        assert len(adapters) >= 12

    def test_registry_lists_all_expected_adapters(self):
        registry = get_registry()
        names = registry.get_adapter_names()
        expected = {"python", "r", "julia", "matlab", "node", "rust", "java", "cpp", "make", "snakemake", "nextflow", "shell"}
        assert expected.issubset(set(names))

    def test_reset_registry(self):
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2

    def test_get_by_name(self):
        registry = get_registry()
        adapter = registry.get("python")
        assert adapter is not None
        assert adapter.name == "python"

    def test_get_by_alias(self):
        registry = get_registry()
        adapter = registry.get("py")
        assert adapter is not None
        assert adapter.name == "python"

    def test_get_unknown_returns_none(self):
        registry = get_registry()
        adapter = registry.get("nonexistent")
        assert adapter is None


class TestRegistryDetection:
    """Test detection through registry."""

    def test_detect_python_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        (tmp_path / "main.py").write_text("print('hello')\n")
        registry = get_registry()
        detections = registry.detect(tmp_path)
        names = [d.name for d in detections]
        assert "python" in names

    def test_detect_best(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        registry = get_registry()
        best = registry.detect_best(tmp_path)
        assert best is not None
        assert best.name == "python"

    def test_detect_empty_returns_empty(self, tmp_path):
        registry = get_registry()
        detections = registry.detect(tmp_path)
        assert len(detections) == 0

    def test_detect_sorted_by_confidence(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
        (tmp_path / "main.py").write_text("print('hello')\n")
        (tmp_path / "run.sh").write_text("#!/bin/bash\necho hello\n")
        registry = get_registry()
        detections = registry.detect(tmp_path)
        confidences = [d.confidence for d in detections]
        assert confidences == sorted(confidences, reverse=True)


class TestRegistryPlan:
    """Test planning through registry."""

    def test_plan_python(self, tmp_path):
        (tmp_path / "requirements.txt").write_text("numpy\n")
        registry = get_registry()
        plan = registry.plan(tmp_path, "python")
        assert plan.adapter_name == "python"
        assert len(plan.install_steps) > 0

    def test_plan_unknown_adapter_raises(self, tmp_path):
        registry = get_registry()
        with pytest.raises(ValueError, match="Unknown adapter"):
            registry.plan(tmp_path, "nonexistent")

    def test_plan_no_detection_raises(self, tmp_path):
        registry = get_registry()
        with pytest.raises(ValueError, match="No adapter detected"):
            registry.plan(tmp_path)


class TestRegistryListAdapters:
    """Test list_adapters output."""

    def test_list_has_required_fields(self):
        registry = get_registry()
        adapters = registry.list_adapters()
        for a in adapters:
            assert "name" in a
            assert "display_name" in a
            assert "supports_dry_run" in a
            assert "supports_execute" in a
            assert "requires_runtime" in a

    def test_python_adapter_info(self):
        registry = get_registry()
        adapters = registry.list_adapters()
        python = next(a for a in adapters if a["name"] == "python")
        assert python["supports_execute"] is True
        assert python["supports_dry_run"] is True


class TestAdapterBase:
    """Test AdapterBase helper methods."""

    def test_check_runtime_available(self, tmp_path):
        registry = get_registry()
        adapter = registry.get("python")
        # python3 should be available in test environment
        info = adapter._check_runtime_available("python3")
        # May or may not be available depending on platform
        assert info.name == "python3"

    def test_find_files(self, tmp_path):
        (tmp_path / "test.py").write_text("pass\n")
        registry = get_registry()
        adapter = registry.get("python")
        found = adapter._find_files(tmp_path, ["*.py"])
        assert "test.py" in found

    def test_confidence_from_evidence(self):
        registry = get_registry()
        adapter = registry.get("python")
        conf = adapter._confidence_from_evidence(["a.txt"], ["b.py"])
        assert 0 < conf <= 1.0
        conf_empty = adapter._confidence_from_evidence([], [])
        assert conf_empty == 0.0
