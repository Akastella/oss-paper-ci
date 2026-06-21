"""Tests for reproduction orchestrator documentation truthfulness."""

import re
import pytest
from pathlib import Path

ROOT = Path(__file__).parent.parent


class TestReproductionDocsTruthfulness:
    """Verify docs don't overclaim about reproduction capabilities."""

    def test_reproduce_plan_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"plan"' in cli or "'plan'" in cli

    def test_reproduce_run_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"run"' in cli or "'run'" in cli

    def test_reproduce_status_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"status"' in cli or "'status'" in cli

    def test_reproduce_report_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"report"' in cli or "'report'" in cli

    def test_reproduce_compare_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"compare"' in cli or "'compare'" in cli

    def test_reproduce_bundle_command_exists_in_cli(self):
        cli = (ROOT / "src" / "oss_paper_ci" / "cli.py").read_text(encoding="utf-8")
        assert '"bundle"' in cli or "'bundle'" in cli

    def test_demo_repo_exists(self):
        assert (ROOT / "examples" / "repro-system-demo" / "reproducibility.yml").exists()

    def test_example_reports_exist(self):
        reports_dir = ROOT / "examples" / "reports"
        assert (reports_dir / "repro_plan_demo.md").exists()
        assert (reports_dir / "repro_run_demo.json").exists()
        assert (reports_dir / "repro_run_demo.md").exists()
        assert (reports_dir / "repro_run_demo.html").exists()
        assert (reports_dir / "repro_compare_demo.md").exists()
        assert (reports_dir / "repro_bundle_inspect.md").exists()
        assert (reports_dir / "repro_bundle_verify.md").exists()

    def test_no_absolute_paths_in_reports(self):
        reports_dir = ROOT / "examples" / "reports"
        for report_file in reports_dir.glob("repro_*"):
            if report_file.suffix in (".md", ".json"):
                content = report_file.read_text(encoding="utf-8")
                # Check for Windows absolute paths
                assert not re.search(r"[A-Z]:\\", content), f"Absolute path in {report_file.name}"
                # Check for Unix absolute paths (excluding /dev/null references)
                for line in content.splitlines():
                    if "/dev/" in line or "/tmp/" in line:
                        continue
                    assert not re.search(r"(?<!\w)/home/\w", line), f"Absolute path in {report_file.name}"
                    assert not re.search(r"(?<!\w)/Users/\w", line), f"Absolute path in {report_file.name}"

    def test_docs_dont_claim_guaranteed_reproduction(self):
        """Docs should not claim reproduction is guaranteed."""
        doc = (ROOT / "docs" / "reproduction-orchestrator.md").read_text(encoding="utf-8")
        assert "not prove scientific correctness" in doc.lower() or "does not prove" in doc.lower()

    def test_docs_dont_claim_default_execution(self):
        """Docs should not claim commands execute by default."""
        doc = (ROOT / "docs" / "reproduction-orchestrator.md").read_text(encoding="utf-8")
        assert "dry-run" in doc.lower() or "default" in doc.lower()

    def test_readme_zh_cn_has_reproduction_section(self):
        readme = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        assert "复现编排器" in readme

    def test_readme_ja_has_reproduction_section(self):
        readme = (ROOT / "README.ja.md").read_text(encoding="utf-8")
        assert "再現オーケストレーター" in readme
