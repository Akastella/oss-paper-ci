"""Tests for the Rust language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.rust import RustAdapter


@pytest.fixture
def adapter():
    return RustAdapter()


@pytest.fixture
def rust_project(tmp_path):
    (tmp_path / "Cargo.toml").write_text('[package]\nname="test"\nversion="0.1.0"\n')
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.rs").write_text('fn main() { println!("hello"); }\n')
    return tmp_path


class TestRustDetect:
    def test_detect_with_cargo_toml(self, adapter, rust_project):
        detection = adapter.detect(rust_project)
        assert detection is not None
        assert detection.name == "rust"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestRustPlan:
    def test_plan(self, adapter, rust_project):
        plan = adapter.plan(rust_project)
        assert plan.adapter_name == "rust"
        assert len(plan.install_steps) > 0
        assert any("cargo build" in s.command for s in plan.install_steps)


class TestRustProperties:
    def test_name(self, adapter):
        assert adapter.name == "rust"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Rust"

    def test_requires_runtime(self, adapter):
        assert "cargo" in adapter.requires_runtime
