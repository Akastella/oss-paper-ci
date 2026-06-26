"""Tests for the Node.js language adapter."""
from __future__ import annotations
from pathlib import Path
import pytest
from oss_paper_ci.adapters.node import NodeAdapter


@pytest.fixture
def adapter():
    return NodeAdapter()


@pytest.fixture
def node_project(tmp_path):
    (tmp_path / "package.json").write_text('{"name":"test","version":"1.0.0"}\n')
    (tmp_path / "index.js").write_text("console.log('hello')\n")
    return tmp_path


class TestNodeDetect:
    def test_detect_with_package_json(self, adapter, node_project):
        detection = adapter.detect(node_project)
        assert detection is not None
        assert detection.name == "node"

    def test_detect_empty(self, adapter, tmp_path):
        detection = adapter.detect(tmp_path)
        assert detection is None


class TestNodePlan:
    def test_plan(self, adapter, node_project):
        plan = adapter.plan(node_project)
        assert plan.adapter_name == "node"
        assert len(plan.install_steps) > 0
        assert any("npm" in s.command for s in plan.install_steps)


class TestNodeProperties:
    def test_name(self, adapter):
        assert adapter.name == "node"

    def test_display_name(self, adapter):
        assert adapter.display_name == "Node.js"

    def test_aliases(self, adapter):
        assert "javascript" in adapter.aliases
        assert "js" in adapter.aliases

    def test_requires_runtime(self, adapter):
        assert "node" in adapter.requires_runtime
