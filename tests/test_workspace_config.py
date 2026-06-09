"""Tests for workspace configuration loading and validation."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml

from oss_paper_ci.workspace import (
    WorkspaceConfig,
    load_workspace,
    resolve_project_path,
    validate_workspace,
    validate_workspace_data,
)


@pytest.fixture
def workspace_dir(tmp_path):
    """Create a temporary workspace directory with fixture repos."""
    ws_dir = tmp_path / "workspace"
    ws_dir.mkdir()

    # Create minimal project dirs
    for name in ["proj-a", "proj-b", "proj-c"]:
        proj_dir = ws_dir / name
        proj_dir.mkdir()
        (proj_dir / "README.md").write_text(f"# {name}\n", encoding="utf-8")
        (proj_dir / "LICENSE").write_text("MIT\n", encoding="utf-8")

    return ws_dir


def _write_workspace(ws_dir: Path, data: dict) -> Path:
    """Write workspace YAML and return path."""
    ws_file = ws_dir / "oss-paper-ci-workspace.yml"
    ws_file.write_text(yaml.dump(data, default_flow_style=False), encoding="utf-8")
    return ws_file


class TestWorkspaceValidation:
    """Test workspace validation."""

    def test_valid_workspace(self, workspace_dir):
        data = {
            "version": 1,
            "name": "test",
            "projects": [
                {"id": "a", "path": "proj-a"},
                {"id": "b", "path": "proj-b"},
            ],
        }
        result = validate_workspace_data(data)
        assert result.valid is True
        assert result.errors == []

    def test_missing_version(self):
        data = {"projects": [{"id": "a", "path": "."}]}
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("version" in e.field for e in result.errors)

    def test_wrong_version(self):
        data = {"version": 2, "projects": [{"id": "a", "path": "."}]}
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("version" in e.field for e in result.errors)

    def test_missing_projects(self):
        data = {"version": 1}
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("projects" in e.field for e in result.errors)

    def test_empty_projects(self):
        data = {"version": 1, "projects": []}
        result = validate_workspace_data(data)
        assert result.valid is False

    def test_duplicate_project_ids(self):
        data = {
            "version": 1,
            "projects": [
                {"id": "same", "path": "a"},
                {"id": "same", "path": "b"},
            ],
        }
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("Duplicate" in e.message for e in result.errors)

    def test_missing_project_id(self):
        data = {
            "version": 1,
            "projects": [{"path": "a"}],
        }
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("id" in e.field for e in result.errors)

    def test_missing_project_path(self):
        data = {
            "version": 1,
            "projects": [{"id": "a"}],
        }
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("path" in e.field for e in result.errors)

    def test_invalid_allow_failure_type(self):
        data = {
            "version": 1,
            "projects": [{"id": "a", "path": ".", "allow_failure": "yes"}],
        }
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("allow_failure" in e.field for e in result.errors)

    def test_invalid_fail_under_type(self):
        data = {
            "version": 1,
            "projects": [{"id": "a", "path": ".", "fail_under": "high"}],
        }
        result = validate_workspace_data(data)
        assert result.valid is False
        assert any("fail_under" in e.field for e in result.errors)


class TestWorkspaceLoading:
    """Test workspace loading from file."""

    def test_load_valid_workspace(self, workspace_dir):
        data = {
            "version": 1,
            "name": "test-ws",
            "defaults": {"profile": "strict"},
            "projects": [
                {"id": "a", "path": "proj-a"},
                {"id": "b", "path": "proj-b", "profile": "publication"},
            ],
        }
        ws_file = _write_workspace(workspace_dir, data)
        ws = load_workspace(ws_file)

        assert ws.name == "test-ws"
        assert ws.version == 1
        assert len(ws.projects) == 2
        assert ws.projects[0].profile == "strict"  # from defaults
        assert ws.projects[1].profile == "publication"  # override

    def test_load_nonexistent_file(self):
        with pytest.raises(FileNotFoundError):
            load_workspace("/nonexistent/workspace.yml")

    def test_load_invalid_workspace(self, workspace_dir):
        ws_file = workspace_dir / "bad.yml"
        ws_file.write_text("version: 2\nprojects: []\n", encoding="utf-8")
        with pytest.raises(ValueError):
            load_workspace(ws_file)

    def test_defaults_applied(self, workspace_dir):
        data = {
            "version": 1,
            "defaults": {
                "profile": "publication",
                "fail_under": 80,
                "rules": ["rules.yml"],
            },
            "projects": [
                {"id": "a", "path": "proj-a"},
                {"id": "b", "path": "proj-b", "profile": "strict", "fail_under": 90},
            ],
        }
        ws_file = _write_workspace(workspace_dir, data)
        ws = load_workspace(ws_file)

        assert ws.projects[0].profile == "publication"
        assert ws.projects[0].fail_under == 80
        assert ws.projects[0].rules == ["rules.yml"]
        assert ws.projects[1].profile == "strict"
        assert ws.projects[1].fail_under == 90

    def test_allow_failure_default_false(self, workspace_dir):
        data = {
            "version": 1,
            "projects": [{"id": "a", "path": "proj-a"}],
        }
        ws_file = _write_workspace(workspace_dir, data)
        ws = load_workspace(ws_file)
        assert ws.projects[0].allow_failure is False


class TestPathResolution:
    """Test project path resolution."""

    def test_relative_path(self, workspace_dir):
        from oss_paper_ci.workspace import WorkspaceProject
        proj = WorkspaceProject(id="a", path="proj-a")
        resolved = resolve_project_path(proj, workspace_dir)
        assert resolved == (workspace_dir / "proj-a").resolve()

    def test_absolute_path(self, workspace_dir):
        from oss_paper_ci.workspace import WorkspaceProject
        abs_path = str(workspace_dir / "proj-b")
        proj = WorkspaceProject(id="b", path=abs_path)
        resolved = resolve_project_path(proj, workspace_dir)
        assert resolved == Path(abs_path).resolve()
