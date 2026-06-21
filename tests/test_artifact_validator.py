"""Tests for artifact and metric validators."""

import json
import pytest
from pathlib import Path

from oss_paper_ci.artifact_validator import validate_artifacts, compute_artifact_hashes
from oss_paper_ci.metric_validator import validate_metrics


class TestArtifactValidator:
    """Tests for artifact validation."""

    def test_existing_artifacts(self, tmp_path):
        (tmp_path / "results").mkdir()
        (tmp_path / "results" / "out.json").write_text("{}")
        report = validate_artifacts(str(tmp_path), ["results/out.json"])
        assert report.ok
        assert report.found == 1
        assert report.missing == 0

    def test_missing_artifacts(self, tmp_path):
        report = validate_artifacts(str(tmp_path), ["results/missing.json"])
        assert not report.ok
        assert report.missing == 1

    def test_hash_computation(self, tmp_path):
        (tmp_path / "file.txt").write_text("hello")
        hashes = compute_artifact_hashes(str(tmp_path), ["file.txt"])
        assert "file.txt" in hashes
        assert len(hashes["file.txt"]) == 64  # SHA256 hex

    def test_size_check(self, tmp_path):
        (tmp_path / "big.bin").write_bytes(b"x" * (2 * 1024 * 1024))  # 2 MB
        report = validate_artifacts(str(tmp_path), ["big.bin"], max_artifact_mb=1)
        assert report.found == 1
        assert len(report.warnings) > 0

    def test_artifact_types(self, tmp_path):
        (tmp_path / "m.json").write_text("{}")
        report = validate_artifacts(
            str(tmp_path), ["m.json"], artifact_types={"m.json": "metrics"}
        )
        assert report.artifacts[0].type == "metrics"


class TestMetricValidator:
    """Tests for metric validation."""

    def test_metric_in_range(self, tmp_path):
        (tmp_path / "metrics.json").write_text(json.dumps({"accuracy": 0.85}))
        report = validate_metrics(str(tmp_path), [
            {"file": "metrics.json", "key": "accuracy", "expected_min": 0.0, "expected_max": 1.0}
        ])
        assert report.ok
        assert report.in_range == 1

    def test_metric_out_of_range(self, tmp_path):
        (tmp_path / "metrics.json").write_text(json.dumps({"accuracy": 1.5}))
        report = validate_metrics(str(tmp_path), [
            {"file": "metrics.json", "key": "accuracy", "expected_min": 0.0, "expected_max": 1.0}
        ])
        assert not report.ok
        assert report.out_of_range == 1

    def test_metric_missing_file(self, tmp_path):
        report = validate_metrics(str(tmp_path), [
            {"file": "missing.json", "key": "accuracy"}
        ])
        assert not report.ok
        assert report.errors == 1

    def test_metric_missing_key(self, tmp_path):
        (tmp_path / "metrics.json").write_text(json.dumps({"loss": 0.5}))
        report = validate_metrics(str(tmp_path), [
            {"file": "metrics.json", "key": "accuracy"}
        ])
        assert not report.ok
        assert report.errors == 1

    def test_nested_key(self, tmp_path):
        (tmp_path / "metrics.json").write_text(json.dumps({"model": {"acc": 0.9}}))
        report = validate_metrics(str(tmp_path), [
            {"file": "metrics.json", "key": "model.acc", "expected_min": 0.0, "expected_max": 1.0}
        ])
        assert report.ok
        assert report.checks[0].actual_value == 0.9
