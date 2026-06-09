"""Tests for the v1.5 config system: profiles, validation, diff."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent


# ── Policy Profiles ──────────────────────────────────────────────────────────

class TestPolicyProfiles:
    """Test policy profile definitions and lookup."""

    def test_list_profiles(self):
        from oss_paper_ci.policy import list_profiles
        profiles = list_profiles()
        assert "lenient" in profiles
        assert "default" in profiles
        assert "strict" in profiles
        assert "publication" in profiles

    def test_get_default_profile(self):
        from oss_paper_ci.policy import get_profile
        p = get_profile("default")
        assert p.name == "default"
        assert p.pass_score == 85
        assert p.fail_under == 50

    def test_get_lenient_profile(self):
        from oss_paper_ci.policy import get_profile
        p = get_profile("lenient")
        assert p.name == "lenient"
        assert p.pass_score == 70
        assert p.fail_under == 30

    def test_get_strict_profile(self):
        from oss_paper_ci.policy import get_profile
        p = get_profile("strict")
        assert p.name == "strict"
        assert p.pass_score == 90
        assert "META002" in p.treat_as_blocking

    def test_get_publication_profile(self):
        from oss_paper_ci.policy import get_profile
        p = get_profile("publication")
        assert p.name == "publication"
        assert p.pass_score == 90
        assert "EXP001" in p.treat_as_blocking

    def test_unknown_profile_raises(self):
        from oss_paper_ci.policy import get_profile
        with pytest.raises(ValueError, match="Unknown policy profile"):
            get_profile("nonexistent")

    def test_explain_profile(self):
        from oss_paper_ci.policy import explain_profile
        text = explain_profile("strict")
        assert "strict" in text
        assert "pass_score" in text

    def test_profile_to_dict(self):
        from oss_paper_ci.policy import get_profile
        d = get_profile("strict").to_dict()
        assert d["name"] == "strict"
        assert "pass_score" in d
        assert "check_overrides" in d


# ── Config Loading ───────────────────────────────────────────────────────────

class TestConfigLoading:
    """Test config loading with profile support."""

    def test_no_config_returns_defaults(self):
        from oss_paper_ci.config import load_config
        config = load_config()
        assert config.profile == "default"
        assert config.thresholds.pass_score == 85

    def test_config_with_profile(self, tmp_path):
        from oss_paper_ci.config import load_config
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: strict\n", encoding="utf-8")
        config = load_config(config_path=cfg)
        assert config.profile == "strict"

    def test_config_path_recorded(self, tmp_path):
        from oss_paper_ci.config import load_config
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: lenient\n", encoding="utf-8")
        config = load_config(config_path=cfg)
        assert config.config_path == str(cfg)

    def test_v01_config_backward_compat(self, tmp_path):
        from oss_paper_ci.config import load_config
        cfg = tmp_path / "oss-paper-ci.yml"
        cfg.write_text(
            'version: "0.1"\nchecks:\n  min_score: 80\n',
            encoding="utf-8",
        )
        config = load_config(config_path=cfg)
        assert config.checks.min_score == 80
        assert config.profile == "default"

    def test_full_v1_config(self, tmp_path):
        from oss_paper_ci.config import load_config
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text(
            "version: 1\n"
            "profile: strict\n"
            "thresholds:\n"
            "  pass_score: 90\n"
            "  warn_score: 70\n"
            "  fail_under: 50\n"
            "checks:\n"
            "  disabled:\n"
            "    - CI005\n"
            "  severity_overrides:\n"
            "    META005: info\n",
            encoding="utf-8",
        )
        config = load_config(config_path=cfg)
        assert config.profile == "strict"
        assert config.thresholds.pass_score == 90
        assert "CI005" in config.checks.disabled
        assert config.checks.severity_overrides["META005"] == "info"


# ── Config Validation ────────────────────────────────────────────────────────

class TestConfigValidation:
    """Test config schema validation."""

    def test_valid_config(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: default\n", encoding="utf-8")
        result = validate_config_file(cfg)
        assert result.valid

    def test_invalid_profile(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: nonexistent\n", encoding="utf-8")
        result = validate_config_file(cfg)
        assert not result.valid
        assert any("nonexistent" in i.message for i in result.issues)

    def test_invalid_threshold(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text(
            "version: 1\nthresholds:\n  pass_score: 150\n",
            encoding="utf-8",
        )
        result = validate_config_file(cfg)
        assert not result.valid

    def test_unknown_key_warning(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nunknown_key: value\n", encoding="utf-8")
        result = validate_config_file(cfg)
        assert result.valid  # warnings don't make it invalid
        assert any("unknown_key" in i.message.lower() or "unknown" in i.message.lower()
                   for i in result.issues)

    def test_invalid_yaml(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text(":\n  - invalid\n  yaml: [", encoding="utf-8")
        result = validate_config_file(cfg)
        assert not result.valid

    def test_missing_file(self):
        from oss_paper_ci.schema import validate_config_file
        result = validate_config_file("/nonexistent/path.yml")
        assert not result.valid

    def test_threshold_logic(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text(
            "version: 1\nthresholds:\n  pass_score: 50\n  warn_score: 80\n",
            encoding="utf-8",
        )
        result = validate_config_file(cfg)
        assert not result.valid
        assert any("warn_score" in i.message for i in result.issues)

    def test_validation_result_format(self):
        from oss_paper_ci.schema import ValidationResult
        r = ValidationResult()
        r.add_error("test.field", "test error")
        r.add_warning("test.field2", "test warning")
        d = r.to_dict()
        assert not d["valid"]
        assert len(d["issues"]) == 2

    def test_format_text(self, tmp_path):
        from oss_paper_ci.schema import validate_config_file
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\n", encoding="utf-8")
        result = validate_config_file(cfg)
        text = result.format_text()
        assert "valid" in text.lower() or "Configuration" in text


# ── Diff Command ─────────────────────────────────────────────────────────────

class TestReportDiff:
    """Test the diff command."""

    def test_diff_basic(self, tmp_path):
        """Test basic diff between two reports."""
        from oss_paper_ci.cli import _compute_diff

        old = {
            "summary": {"score": 65, "status": "warn"},
            "checks": [
                {"id": "META002", "title": "License", "severity": "error", "status": "fail", "message": "No LICENSE"},
                {"id": "ENV001", "title": "Env", "severity": "error", "status": "pass", "message": "OK"},
            ],
        }
        new = {
            "summary": {"score": 82, "status": "warn"},
            "checks": [
                {"id": "META002", "title": "License", "severity": "error", "status": "pass", "message": "MIT LICENSE"},
                {"id": "ENV001", "title": "Env", "severity": "error", "status": "pass", "message": "OK"},
            ],
        }

        diff = _compute_diff(old, new)
        assert diff["score_delta"] == 17
        assert diff["old_score"] == 65
        assert diff["new_score"] == 82
        # META002 went from fail to pass → severity_improved
        assert len(diff["severity_improved"]) == 1
        assert diff["severity_improved"][0]["id"] == "META002"

    def test_diff_new_findings(self):
        from oss_paper_ci.cli import _compute_diff

        old = {"summary": {"score": 80, "status": "warn"}, "checks": []}
        new = {
            "summary": {"score": 60, "status": "warn"},
            "checks": [
                {"id": "DATA001", "title": "Data", "severity": "warning", "status": "fail", "message": "No data"},
            ],
        }

        diff = _compute_diff(old, new)
        assert diff["score_delta"] == -20
        assert len(diff["new_findings"]) == 1
        assert diff["new_findings"][0]["id"] == "DATA001"

    def test_diff_worsened(self):
        from oss_paper_ci.cli import _compute_diff

        old = {
            "summary": {"score": 80, "status": "warn"},
            "checks": [
                {"id": "ENV001", "severity": "error", "status": "warn", "title": "Env"},
            ],
        }
        new = {
            "summary": {"score": 60, "status": "fail"},
            "checks": [
                {"id": "ENV001", "severity": "error", "status": "fail", "title": "Env"},
            ],
        }

        diff = _compute_diff(old, new)
        assert len(diff["severity_worsened"]) == 1

    def test_diff_improved(self):
        from oss_paper_ci.cli import _compute_diff

        old = {
            "summary": {"score": 60, "status": "warn"},
            "checks": [
                {"id": "ENV001", "severity": "error", "status": "fail", "title": "Env"},
            ],
        }
        new = {
            "summary": {"score": 80, "status": "warn"},
            "checks": [
                {"id": "ENV001", "severity": "error", "status": "pass", "title": "Env"},
            ],
        }

        diff = _compute_diff(old, new)
        assert len(diff["severity_improved"]) == 1

    def test_diff_no_changes(self):
        from oss_paper_ci.cli import _compute_diff

        data = {
            "summary": {"score": 80, "status": "warn"},
            "checks": [
                {"id": "ENV001", "severity": "error", "status": "pass", "title": "Env"},
            ],
        }

        diff = _compute_diff(data, data)
        assert diff["score_delta"] == 0
        assert not diff["new_findings"]
        assert not diff["resolved_findings"]
        assert not diff["severity_worsened"]
        assert not diff["severity_improved"]

    def test_diff_markdown_format(self):
        from oss_paper_ci.cli import _compute_diff, _format_diff_markdown

        old = {
            "version": "1.4.0rc1",
            "summary": {"score": 65, "status": "warn"},
            "checks": [
                {"id": "META002", "title": "License", "severity": "error", "status": "fail", "message": "No LICENSE"},
            ],
            "policy": {"profile": "default"},
        }
        new = {
            "version": "1.6.0rc1",
            "summary": {"score": 82, "status": "warn"},
            "checks": [
                {"id": "META002", "title": "License", "severity": "error", "status": "pass", "message": "MIT LICENSE"},
            ],
            "policy": {"profile": "strict"},
        }

        diff = _compute_diff(old, new)
        md = _format_diff_markdown(diff, old, new)
        assert "score_delta" in md or "+17" in md or "17" in md
        assert "strict" in md

    def test_diff_cli_files(self, tmp_path):
        """Test diff CLI with actual files."""
        old_data = {
            "summary": {"score": 70, "status": "warn"},
            "checks": [
                {"id": "META002", "severity": "error", "status": "fail", "title": "License", "message": "No LICENSE"},
            ],
        }
        new_data = {
            "summary": {"score": 90, "status": "pass"},
            "checks": [
                {"id": "META002", "severity": "error", "status": "pass", "title": "License", "message": "MIT LICENSE"},
            ],
        }

        old_file = tmp_path / "old.json"
        new_file = tmp_path / "new.json"
        old_file.write_text(json.dumps(old_data), encoding="utf-8")
        new_file.write_text(json.dumps(new_data), encoding="utf-8")

        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "diff",
             "--old", str(old_file), "--new", str(new_file),
             "--format", "json"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        diff = json.loads(result.stdout)
        assert diff["score_delta"] == 20


# ── CLI Integration ──────────────────────────────────────────────────────────

class TestCLIIntegration:
    """Test CLI commands for new features."""

    def test_version_bump(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "version"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        assert "1.6.0rc1" in result.stdout

    def test_scan_with_profile(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "scan",
             str(ROOT / "tests" / "fixtures" / "minimal_bad_repo"),
             "--profile", "lenient", "--format", "json"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        assert result.returncode <= 2
        data = json.loads(result.stdout)
        assert data["policy"]["profile"] == "lenient"

    def test_scan_default_profile(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "scan",
             str(ROOT / "tests" / "fixtures" / "minimal_bad_repo"),
             "--format", "json"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        assert result.returncode <= 2
        data = json.loads(result.stdout)
        assert data["policy"]["profile"] == "default"

    def test_config_validate_valid(self, tmp_path):
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: default\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "validate",
             "--config", str(cfg)],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0

    def test_config_validate_invalid(self, tmp_path):
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: nonexistent\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "validate",
             "--config", str(cfg)],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 1

    def test_config_init_dry_run(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "init",
             "--profile", "strict", "--dry-run"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        assert "strict" in result.stdout

    def test_config_init_no_overwrite(self, tmp_path):
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("existing", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "init",
             "--output", str(cfg)],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 1
        assert cfg.read_text() == "existing"

    def test_config_init_force_overwrite(self, tmp_path):
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("existing", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "init",
             "--output", str(cfg), "--force"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        assert "profile" in cfg.read_text()

    def test_explain_policy(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "explain", "policy", "publication"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        assert "publication" in result.stdout

    def test_explain_policy_unknown(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "explain", "policy", "nonexistent"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 1

    def test_config_explain(self, tmp_path):
        cfg = tmp_path / ".oss-paper-ci.yml"
        cfg.write_text("version: 1\nprofile: strict\n", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "config", "explain",
             "--config", str(cfg)],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["profile"] == "strict"


# ── Action.yml ───────────────────────────────────────────────────────────────

class TestActionYml:
    """Test action.yml has the new inputs."""

    def test_has_profile_input(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "profile" in data["inputs"]

    def test_has_github_annotations_input(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "github-annotations" in data["inputs"]

    def test_has_step_summary_input(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert "step-summary" in data["inputs"]

    def test_uses_github_action_path(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        assert "github.action_path" in content

    def test_profile_default_is_default(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert data["inputs"]["profile"]["default"] == "default"

    def test_yaml_parseable(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert data["runs"]["using"] == "composite"
        assert len(data["runs"]["steps"]) > 0


# ── Example Files ────────────────────────────────────────────────────────────

class TestExampleFiles:
    """Test example config and workflow files."""

    def test_lenient_config_valid(self):
        from oss_paper_ci.schema import validate_config_file
        result = validate_config_file(ROOT / "examples" / "configs" / "lenient.yml")
        assert result.valid

    def test_strict_config_valid(self):
        from oss_paper_ci.schema import validate_config_file
        result = validate_config_file(ROOT / "examples" / "configs" / "strict.yml")
        assert result.valid

    def test_publication_config_valid(self):
        from oss_paper_ci.schema import validate_config_file
        result = validate_config_file(ROOT / "examples" / "configs" / "publication.yml")
        assert result.valid

    def test_diff_example_old_parseable(self):
        data = json.loads((ROOT / "examples" / "reports" / "diff_example_old.json").read_text())
        assert "summary" in data
        assert "checks" in data

    def test_diff_example_new_parseable(self):
        data = json.loads((ROOT / "examples" / "reports" / "diff_example_new.json").read_text())
        assert "summary" in data
        assert "checks" in data

    def test_diff_example_has_policy(self):
        data = json.loads((ROOT / "examples" / "reports" / "diff_example_old.json").read_text())
        assert "policy" in data
        assert data["policy"]["profile"] == "default"

    def test_policy_strict_workflow_parseable(self):
        wf = ROOT / "examples" / "github-actions" / "policy-strict.yml"
        data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        assert data is not None
        assert "jobs" in data

    def test_publication_workflow_parseable(self):
        wf = ROOT / "examples" / "github-actions" / "publication-profile.yml"
        data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        assert data is not None

    def test_config_file_workflow_parseable(self):
        wf = ROOT / "examples" / "github-actions" / "config-file.yml"
        data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        assert data is not None

    def test_diff_regression_workflow_parseable(self):
        wf = ROOT / "examples" / "github-actions" / "diff-regression.yml"
        data = yaml.safe_load(wf.read_text(encoding="utf-8"))
        assert data is not None

    def test_benchmark_readme_exists(self):
        assert (ROOT / "examples" / "benchmark" / "README.md").exists()


# ── Docs ─────────────────────────────────────────────────────────────────────

class TestDocsExistence:
    """Test that new docs exist."""

    def test_policy_profiles_doc(self):
        assert (ROOT / "docs" / "policy-profiles.md").exists()

    def test_report_diff_doc(self):
        assert (ROOT / "docs" / "report-diff.md").exists()

    def test_benchmark_doc(self):
        assert (ROOT / "docs" / "benchmark.md").exists()

    def test_configuration_doc_updated(self):
        content = (ROOT / "docs" / "configuration.md").read_text(encoding="utf-8")
        assert "profile" in content

    def test_action_usage_doc_updated(self):
        content = (ROOT / "docs" / "action-usage.md").read_text(encoding="utf-8")
        assert "profile" in content

    def test_readme_updated(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "policy" in content.lower() or "profile" in content.lower()


# ── Version Consistency ──────────────────────────────────────────────────────

class TestVersionConsistency:
    """Verify version strings are consistent."""

    def test_init_version(self):
        content = (ROOT / "src" / "oss_paper_ci" / "__init__.py").read_text()
        assert "1.6.0rc1" in content

    def test_pyproject_version(self):
        content = (ROOT / "pyproject.toml").read_text()
        assert 'version = "1.6.0rc1"' in content

    def test_cli_version_output(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "version"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert "1.6.0rc1" in result.stdout
