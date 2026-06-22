"""Tests for autoplan confidence scoring."""

from __future__ import annotations

import pytest

from oss_paper_ci.autoplan_score import compute_confidence, ConfidenceScores


class TestConfidenceScoring:
    """Test confidence score computation."""

    def test_empty_inputs_low_confidence(self):
        """Empty inputs produce low confidence."""
        scores = compute_confidence(
            ecosystems=[], env_files=[], command_candidates=[],
            artifact_paths=[],
        )
        assert scores.overall < 0.3

    def test_full_inputs_high_confidence(self):
        """Full inputs produce high confidence."""
        scores = compute_confidence(
            ecosystems=[{"id": "python", "support_level": "native",
                        "install_plan": ["pip install -r requirements.txt"],
                        "runtime_available": True}],
            env_files=["requirements.txt"],
            command_candidates=[
                {"kind": "train", "confidence": 0.8, "dangerous": False},
                {"kind": "evaluate", "confidence": 0.7, "dangerous": False},
            ],
            artifact_paths=["results/metrics.json", "figures/plot.png"],
            has_metrics_file=True,
        )
        assert scores.overall > 0.7

    def test_environment_score_with_native(self):
        """Native ecosystem gets high environment score."""
        scores = compute_confidence(
            ecosystems=[{"id": "python", "support_level": "native",
                        "install_plan": ["pip install"], "runtime_available": True}],
            env_files=["requirements.txt"],
            command_candidates=[], artifact_paths=[],
        )
        assert scores.environment > 0.8

    def test_commands_score_with_classified(self):
        """Classified commands get higher score."""
        scores = compute_confidence(
            ecosystems=[], env_files=[],
            command_candidates=[
                {"kind": "train", "confidence": 0.8, "dangerous": False},
            ],
            artifact_paths=[],
        )
        assert scores.commands > 0.5

    def test_dangerous_commands_reduce_score(self):
        """All-dangerous commands reduce score."""
        scores = compute_confidence(
            ecosystems=[], env_files=[],
            command_candidates=[
                {"kind": "unknown", "confidence": 0.5, "dangerous": True},
            ],
            artifact_paths=[],
        )
        assert scores.commands <= 0.2

    def test_existing_config_boost(self):
        """Existing config boosts overall score."""
        scores_without = compute_confidence(
            ecosystems=[{"id": "python", "support_level": "native",
                        "install_plan": [], "runtime_available": False}],
            env_files=[], command_candidates=[], artifact_paths=[],
            has_existing_config=False,
        )
        scores_with = compute_confidence(
            ecosystems=[{"id": "python", "support_level": "native",
                        "install_plan": [], "runtime_available": False}],
            env_files=[], command_candidates=[], artifact_paths=[],
            has_existing_config=True,
        )
        assert scores_with.overall > scores_without.overall

    def test_to_dict_returns_floats(self):
        """to_dict returns rounded floats."""
        scores = compute_confidence(
            ecosystems=[], env_files=[], command_candidates=[],
            artifact_paths=[],
        )
        d = scores.to_dict()
        assert isinstance(d["overall"], float)
        assert isinstance(d["environment"], float)

    def test_scores_between_0_and_1(self):
        """All scores are between 0 and 1."""
        scores = compute_confidence(
            ecosystems=[{"id": "python", "support_level": "native",
                        "install_plan": ["pip install"], "runtime_available": True}],
            env_files=["requirements.txt"],
            command_candidates=[
                {"kind": "train", "confidence": 0.9, "dangerous": False},
                {"kind": "evaluate", "confidence": 0.8, "dangerous": False},
            ],
            artifact_paths=["results/metrics.json"],
            has_metrics_file=True,
            has_existing_config=True,
        )
        d = scores.to_dict()
        for k, v in d.items():
            assert 0.0 <= v <= 1.0, f"{k} = {v} is out of range"
