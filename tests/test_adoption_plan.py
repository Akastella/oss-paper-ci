"""Tests for adoption plan generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from oss_paper_ci.adoption import (
    build_adoption_plan, format_adoption_plan_markdown,
    AdoptionPlan, PatchItem,
)


class TestAdoptionPlan:
    """Test adoption plan data model."""

    def test_plan_to_dict(self):
        plan = AdoptionPlan(repo=".")
        d = plan.to_dict()
        assert d["schema_version"] == "0.1"
        assert d["plan_type"] == "oss-paper-ci-adoption-plan"

    def test_plan_to_json(self):
        plan = AdoptionPlan(repo=".")
        j = plan.to_json()
        data = json.loads(j)
        assert "patches" in data

    def test_patch_item_to_dict(self):
        item = PatchItem(
            id="test", title="Test", path="test.txt",
            action="create", reason="Missing",
        )
        d = item.to_dict()
        assert d["id"] == "test"
        assert d["risk"] == "low"


class TestBuildAdoptionPlan:
    """Test adoption plan building."""

    def test_missing_files_detected(self, tmp_path):
        # Create minimal repo
        (tmp_path / "README.md").write_text("# Test")
        plan = build_adoption_plan(str(tmp_path))
        assert "reproducibility.yml" in plan.missing_files
        assert "data/README.md" in plan.missing_files

    def test_existing_files_detected(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        (tmp_path / "reproducibility.yml").write_text("version: '0.3'")
        plan = build_adoption_plan(str(tmp_path))
        assert "reproducibility.yml" in plan.recommended_files
        assert "reproducibility.yml" not in plan.missing_files

    def test_patches_for_missing_files(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        plan = build_adoption_plan(str(tmp_path))
        patch_ids = [p.id for p in plan.patches]
        assert "reproducibility-yml" in patch_ids
        assert "data-readme" in patch_ids

    def test_ecosystem_stored(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        ecosystems = [{"id": "python", "display_name": "Python"}]
        plan = build_adoption_plan(str(tmp_path), ecosystems=ecosystems)
        assert len(plan.detected_ecosystems) == 1
        assert plan.detected_ecosystems[0]["id"] == "python"

    def test_format_markdown(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        plan = build_adoption_plan(str(tmp_path))
        md = format_adoption_plan_markdown(plan)
        assert "Adoption Plan" in md
        assert "Missing Files" in md

    def test_format_json(self, tmp_path):
        (tmp_path / "README.md").write_text("# Test")
        plan = build_adoption_plan(str(tmp_path))
        j = plan.to_json()
        data = json.loads(j)
        assert "missing_files" in data
