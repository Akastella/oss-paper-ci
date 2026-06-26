"""Tests for repro_dsl.migration -- migrate_legacy with v0.2 and v0.3."""
from __future__ import annotations

from pathlib import Path
import pytest

from oss_paper_ci.repro_dsl.loader import load_dsl_raw
from oss_paper_ci.repro_dsl.migration import migrate_legacy, migrate_legacy_with_report, MigrationReport
from oss_paper_ci.repro_dsl.schema import ReproDSL


FIXTURES = Path(__file__).parent / "fixtures" / "dsl"


class TestMigrateLegacyV03:
    def test_returns_repro_dsl(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert isinstance(dsl, ReproDSL)

    def test_version_is_1(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert dsl.version == 1

    def test_has_train_step(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert "train" in dsl.steps
        assert dsl.steps["train"].command == "python scripts/train.py"

    def test_has_datasets(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert "demo-data" in dsl.datasets

    def test_has_artifacts(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert len(dsl.artifacts) > 0

    def test_has_environment(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert "python" in dsl.environments

    def test_safety_defaults_to_restrictive(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl = migrate_legacy(data, version)
        assert dsl.safety.network is False
        assert dsl.safety.allow_install is False


class TestMigrateLegacyWithReportV03:
    def test_returns_dsl_and_report(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        dsl, report = migrate_legacy_with_report(data, version)
        assert isinstance(dsl, ReproDSL)
        assert isinstance(report, MigrationReport)

    def test_report_source_version(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        _, report = migrate_legacy_with_report(data, version)
        assert report.source_version == "v0.3"
        assert report.target_version == 1

    def test_report_steps_converted(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        _, report = migrate_legacy_with_report(data, version)
        assert report.steps_converted >= 1

    def test_report_datasets_converted(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        _, report = migrate_legacy_with_report(data, version)
        assert report.datasets_converted >= 1

    def test_report_to_dict(self):
        data, version = load_dsl_raw(FIXTURES / "legacy_config_v0" / "reproducibility.yml")
        _, report = migrate_legacy_with_report(data, version)
        d = report.to_dict()
        assert "source_version" in d
        assert "steps_converted" in d


class TestMigrateLegacyV02:
    def test_v02_with_empty_data(self):
        """v0.2 with empty data produces a DSL with no steps."""
        dsl = migrate_legacy({}, "v0.2")
        assert isinstance(dsl, ReproDSL)
        assert dsl.version == 1
        assert len(dsl.steps) == 0

    def test_v02_with_valid_data(self):
        data = {
            "project_name": "test-project",
            "commands": [
                {"id": "train", "run": "python train.py", "timeout_seconds": 60, "depends_on": [], "expected_artifacts": ["model.pkl"]},
                {"id": "eval", "run": "python eval.py", "timeout_seconds": 30, "depends_on": ["train"]},
            ],
            "artifacts": [{"path": "model.pkl", "type": "file"}],
            "metrics": [{"key": "accuracy", "expected_min": 0.0, "expected_max": 1.0}],
            "safety": {"network": False},
        }
        dsl = migrate_legacy(data, "v0.2")
        assert isinstance(dsl, ReproDSL)
        assert dsl.version == 1
        assert "train" in dsl.steps
        assert "eval" in dsl.steps
        assert dsl.steps["eval"].needs == ["train"]

    def test_v02_with_report(self):
        data = {
            "project_name": "test",
            "commands": [{"id": "step1", "run": "echo hi"}],
            "artifacts": [],
            "metrics": [],
            "safety": {},
        }
        dsl, report = migrate_legacy_with_report(data, "v0.2")
        assert report.source_version == "v0.2"
        assert report.steps_converted == 1


class TestMigrateLegacyErrors:
    def test_unsupported_version_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            migrate_legacy({}, "v99")

    def test_unsupported_version_with_report_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            migrate_legacy_with_report({}, "v99")
