"""Tests for expected_outcomes.yml schema."""

from pathlib import Path

import pytest
import yaml


CORPUS_DIR = Path(__file__).parent.parent / "examples" / "evaluation-corpus"
OUTCOMES_FILE = CORPUS_DIR / "expected_outcomes.yml"


@pytest.fixture
def outcomes():
    """Load expected outcomes as list."""
    with open(OUTCOMES_FILE, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def outcomes_dict(outcomes):
    """Convert outcomes list to dict keyed by repo_id."""
    return {item["repo_id"]: item for item in outcomes}


class TestExpectedOutcomesSchema:
    """Test expected outcomes YAML schema."""

    def test_file_exists(self):
        assert OUTCOMES_FILE.exists()

    def test_is_list(self, outcomes):
        assert isinstance(outcomes, list)

    def test_has_entries(self, outcomes):
        assert len(outcomes) > 0

    def test_all_have_repo_id(self, outcomes):
        """Each entry should have repo_id."""
        for item in outcomes:
            assert "repo_id" in item, f"Entry missing repo_id"

    def test_all_required_fields(self, outcomes):
        """Each entry should have required fields."""
        required = ["repo_id", "expected_ecosystems", "expected_status"]
        for item in outcomes:
            for field in required:
                assert field in item, f"{item.get('repo_id', '?')} missing {field}"

    def test_ecosystems_are_lists(self, outcomes):
        for item in outcomes:
            assert isinstance(item["expected_ecosystems"], list), \
                f"{item['repo_id']}: expected_ecosystems should be list"

    def test_valid_status(self, outcomes):
        valid_statuses = {"good", "needs-work", "critical", "varies"}
        for item in outcomes:
            status = item.get("expected_status")
            assert status in valid_statuses, \
                f"{item['repo_id']}: invalid status '{status}'"

    def test_score_band_format(self, outcomes):
        """Score bands should be [min, max] lists."""
        for item in outcomes:
            if "expected_score_band" in item:
                band = item["expected_score_band"]
                assert isinstance(band, list), f"{item['repo_id']}: score_band should be list"
                assert len(band) == 2, f"{item['repo_id']}: score_band should have 2 elements"
                assert band[0] <= band[1], f"{item['repo_id']}: min should be <= max"

    def test_should_execute_default_false(self, outcomes):
        """No repo should execute by default."""
        for item in outcomes:
            if "should_execute_by_default" in item:
                assert item["should_execute_by_default"] is False, \
                    f"{item['repo_id']}: should_execute_by_default must be false"


class TestExpectedOutcomesCoverage:
    """Test that outcomes cover all repos."""

    def test_all_repos_have_outcomes(self, outcomes_dict):
        """Every repo directory should have an outcome entry."""
        for repo_dir in CORPUS_DIR.iterdir():
            if repo_dir.is_dir() and not repo_dir.name.startswith("."):
                repo_id = repo_dir.name
                # Skip if it's a before/after parent
                if (repo_dir / "before").exists() or (repo_dir / "after").exists():
                    continue
                assert repo_id in outcomes_dict, \
                    f"{repo_id} missing from expected_outcomes.yml"
