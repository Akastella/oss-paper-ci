"""Tests for evidence report profiles."""

from __future__ import annotations

import json
from pathlib import Path

from oss_paper_ci.evidence import build_evidence_report

DEMO_REPO = Path(__file__).parent.parent / "examples" / "demo-paper-repo"


class TestEvidenceProfiles:
    """Test that profiles change output but not facts."""

    def test_reviewer_profile(self):
        report = build_evidence_report(DEMO_REPO, profile="reviewer")
        assert report.profile == "reviewer"
        assert "engineering completeness" in report.summary["plain_language_summary"].lower() or \
               "does not judge" in report.summary["plain_language_summary"].lower()

    def test_author_profile(self):
        report = build_evidence_report(DEMO_REPO, profile="author")
        assert report.profile == "author"
        # Author profile should mention next steps
        assert len(report.recommended_next_steps) > 0

    def test_maintainer_profile(self):
        report = build_evidence_report(DEMO_REPO, profile="maintainer")
        assert report.profile == "maintainer"

    def test_profiles_same_score(self):
        """Different profiles should produce the same score."""
        reviewer = build_evidence_report(DEMO_REPO, profile="reviewer")
        author = build_evidence_report(DEMO_REPO, profile="author")
        maintainer = build_evidence_report(DEMO_REPO, profile="maintainer")
        assert reviewer.summary["readiness_score"] == author.summary["readiness_score"]
        assert reviewer.summary["readiness_score"] == maintainer.summary["readiness_score"]

    def test_profiles_same_findings_count(self):
        """Different profiles should produce the same findings."""
        reviewer = build_evidence_report(DEMO_REPO, profile="reviewer")
        author = build_evidence_report(DEMO_REPO, profile="author")
        assert reviewer.summary["total_findings"] == author.summary["total_findings"]

    def test_profiles_different_summaries(self):
        """Different profiles should produce different plain-language summaries."""
        reviewer = build_evidence_report(DEMO_REPO, profile="reviewer")
        author = build_evidence_report(DEMO_REPO, profile="author")
        assert reviewer.summary["plain_language_summary"] != author.summary["plain_language_summary"]

    def test_profiles_different_next_steps(self):
        """Different profiles should produce different next steps."""
        reviewer = build_evidence_report(DEMO_REPO, profile="reviewer")
        author = build_evidence_report(DEMO_REPO, profile="author")
        assert reviewer.recommended_next_steps != author.recommended_next_steps
