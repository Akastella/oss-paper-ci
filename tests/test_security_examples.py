"""Tests for security/trust examples."""

from __future__ import annotations

from pathlib import Path


def test_trust_examples_dir_exists() -> None:
    """examples/trust directory exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust").is_dir()


def test_trust_report_json_exists() -> None:
    """examples/trust/trust_report.json exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "trust_report.json").exists()


def test_trust_report_md_exists() -> None:
    """examples/trust/trust_report.md exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "trust_report.md").exists()


def test_provenance_json_exists() -> None:
    """examples/trust/provenance.json exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "provenance.json").exists()


def test_security_scan_json_exists() -> None:
    """examples/trust/security_scan.json exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "security_scan.json").exists()


def test_dependency_inventory_json_exists() -> None:
    """examples/trust/dependency_inventory.json exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "dependency_inventory.json").exists()


def test_trust_report_json_structure() -> None:
    """Trust report JSON has correct structure."""
    import json

    repo_root = Path(__file__).parent.parent
    report_path = repo_root / "examples" / "trust" / "trust_report.json"
    if report_path.exists():
        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert "schema_version" in data
        assert "report_type" in data
        assert "summary" in data


def test_provenance_json_structure() -> None:
    """Provenance JSON has correct structure."""
    import json

    repo_root = Path(__file__).parent.parent
    prov_path = repo_root / "examples" / "trust" / "provenance.json"
    if prov_path.exists():
        data = json.loads(prov_path.read_text(encoding="utf-8"))
        assert "tool" in data
        assert "tool_version" in data
        assert "source" in data


def test_trust_readme_exists() -> None:
    """examples/trust/README.md exists."""
    repo_root = Path(__file__).parent.parent
    assert (repo_root / "examples" / "trust" / "README.md").exists()
