"""Tests for workflow audit."""

from __future__ import annotations

from pathlib import Path

from oss_paper_ci.workflow_audit import audit_workflows


def test_detects_missing_permissions(tmp_path: Path) -> None:
    """Detects workflow missing permissions block."""
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    wf.write_text("name: CI\non: push\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8")

    result = audit_workflows(tmp_path)
    assert result.workflows_scanned == 1
    assert any(f["id"] == "workflow-missing-permissions" for f in result.findings)


def test_detects_write_all_permissions(tmp_path: Path) -> None:
    """Detects overly broad permissions."""
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    wf.write_text("name: CI\non: push\npermissions: write-all\njobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    result = audit_workflows(tmp_path)
    assert any(f["id"] == "workflow-permissions-write-all" for f in result.findings)


def test_detects_pull_request_target(tmp_path: Path) -> None:
    """Detects pull_request_target trigger."""
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    wf.write_text("name: CI\non:\n  pull_request_target:\njobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    result = audit_workflows(tmp_path)
    assert any("pull_request_target" in f["id"] for f in result.findings)


def test_accepts_official_action_major_pin(tmp_path: Path) -> None:
    """Accepts official actions pinned to major version."""
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    wf.write_text(
        "name: CI\non: push\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    result = audit_workflows(tmp_path)
    # Should not flag official action as third-party
    assert not any(f["id"] == "workflow-third-party-action" for f in result.findings)


def test_detects_third_party_action(tmp_path: Path) -> None:
    """Detects third-party action not SHA-pinned."""
    wf_dir = tmp_path / ".github" / "workflows"
    wf_dir.mkdir(parents=True)
    wf = wf_dir / "ci.yml"
    wf.write_text(
        "name: CI\non: push\npermissions:\n  contents: read\njobs:\n  test:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: some-org/some-action@v1\n",
        encoding="utf-8",
    )

    result = audit_workflows(tmp_path)
    assert any(f["id"] == "workflow-third-party-action" for f in result.findings)


def test_no_workflows(tmp_path: Path) -> None:
    """No workflows dir returns empty result."""
    result = audit_workflows(tmp_path)
    assert result.workflows_scanned == 0
    assert len(result.findings) == 0
