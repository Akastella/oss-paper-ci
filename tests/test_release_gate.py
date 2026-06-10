"""Release gate tests for v2.1.0rc1.

Tests that verify the release package is truthful, clean, and ready for public upload.
Covers: clean zip structure, docs truthfulness, action.yml correctness,
workflow YAML parsing, cross-language fixtures, and version consistency.
"""

from __future__ import annotations

import fnmatch
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent

# Construct fake URL dynamically to avoid self-detection
_FAKE_OWNER = "oss-paper-ci"
_FAKE_URL = f"github.com/{_FAKE_OWNER}/{_FAKE_OWNER}"
RELEASE_ARTIFACTS = ROOT / "release-artifacts"


# ── Helper ──────────────────────────────────────────────────────────────────

def _find_clean_zip() -> Path | None:
    """Find the latest clean zip in release-artifacts."""
    if not RELEASE_ARTIFACTS.exists():
        return None
    zips = sorted(RELEASE_ARTIFACTS.glob("oss-paper-ci-v*-github-clean.zip"))
    return zips[-1] if zips else None


def _zip_names() -> list[str]:
    """Get names from the latest clean zip."""
    zpath = _find_clean_zip()
    if zpath is None:
        pytest.skip("No clean zip found in release-artifacts")
    with zipfile.ZipFile(zpath) as zf:
        return zf.namelist()


# ── Clean ZIP Structure ─────────────────────────────────────────────────────

class TestCleanZipRootless:
    """Verify clean ZIP is rootless (no wrapper directory)."""

    def test_no_wrapper_directory(self):
        names = _zip_names()
        top_levels = set()
        for name in names:
            parts = name.split("/")
            if len(parts) > 1:
                top_levels.add(parts[0])
        assert "oss-paper-ci" not in top_levels or len(top_levels) > 1, \
            "ZIP is wrapped in oss-paper-ci/ directory"

    def test_readme_at_root(self):
        names = _zip_names()
        assert "README.md" in names, "README.md not at ZIP root"

    def test_src_at_root(self):
        names = _zip_names()
        assert any(n.startswith("src/") for n in names), "src/ not at ZIP root"

    def test_docs_at_root(self):
        names = _zip_names()
        assert any(n.startswith("docs/") for n in names), "docs/ not at ZIP root"

    def test_tests_at_root(self):
        names = _zip_names()
        assert any(n.startswith("tests/") for n in names), "tests/ not at ZIP root"

    def test_examples_at_root(self):
        names = _zip_names()
        assert any(n.startswith("examples/") for n in names), "examples/ not at ZIP root"


class TestCleanZipGitignore:
    """Verify .gitignore is present and .git/ is excluded."""

    def test_gitignore_present(self):
        names = _zip_names()
        assert ".gitignore" in names, ".gitignore not in clean zip"

    def test_git_dir_excluded(self):
        names = _zip_names()
        assert not any(".git/" in n for n in names), ".git/ found in clean zip"

    def test_no_git_directory(self):
        names = _zip_names()
        git_entries = [n for n in names if n.startswith(".git/") or n == ".git"]
        assert len(git_entries) == 0, f".git entries found: {git_entries}"


class TestCleanZipNoCaches:
    """Verify no cache/build artifacts in clean zip."""

    def test_no_pycache(self):
        names = _zip_names()
        assert not any("__pycache__" in n for n in names)

    def test_no_pyc(self):
        names = _zip_names()
        assert not any(n.endswith(".pyc") for n in names)

    def test_no_egg_info(self):
        names = _zip_names()
        assert not any(".egg-info" in n for n in names)

    def test_no_pytest_cache(self):
        names = _zip_names()
        assert not any(".pytest_cache" in n for n in names)

    def test_no_dist(self):
        names = _zip_names()
        assert not any(n.startswith("dist/") for n in names)

    def test_no_build(self):
        names = _zip_names()
        assert not any(n.startswith("build/") for n in names)


class TestCleanZipNoStaleContent:
    """Verify no stale stage reports or old dogfooding in clean zip."""

    def test_no_round_reports(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert not basename.startswith("ROUND"), f"Round report found: {n}"

    def test_no_final_deliverables(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert not basename.startswith("FINAL_DELIVERABLES"), f"Deliverables found: {n}"

    def test_no_red_team_audit(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert not basename.startswith("RED_TEAM_AUDIT"), f"Audit found: {n}"

    def test_no_old_dogfooding_rounds(self):
        names = _zip_names()
        old_rounds = ["round3", "round4", "round5", "round6", "round7", "round8", "round9"]
        for n in names:
            if "dogfooding" not in n:
                continue
            for old in old_rounds:
                assert old not in n, f"Old dogfooding round found: {n}"

    def test_workspace_examples_included(self):
        zpath = _find_clean_zip()
        if zpath is None:
            pytest.skip("No clean zip found")
        if "v1.7" not in zpath.name:
            pytest.skip("Workspace examples only in v1.7+ clean zip")
        names = _zip_names()
        assert any("workspaces" in n for n in names), "Workspace examples not included"

    def test_no_stale_dogfooding_summary(self):
        """Root-level dogfooding_summary.md should not be in clean zip."""
        names = _zip_names()
        assert "dogfooding/results/dogfooding_summary.md" not in names, \
            "Stale dogfooding_summary.md found at root of results/"

    def test_no_release_truth_audit(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert "RELEASE_TRUTH" not in basename, f"Stage file found: {n}"

    def test_no_release_quarantine_files(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert "RELEASE_QUARANTINE" not in basename, f"Stage file found: {n}"

    def test_no_audit_taskboard_deliverables(self):
        names = _zip_names()
        for n in names:
            basename = n.split("/")[-1]
            assert not basename.endswith("_AUDIT.md"), f"Audit file found: {n}"
            assert not basename.endswith("_TASKBOARD.md"), f"Taskboard found: {n}"
            assert not basename.endswith("_DELIVERABLES.md"), f"Deliverables found: {n}"


class TestSourceCodeNoFakeUrl:
    """Verify source code does not contain fake GitHub URLs."""

    def test_no_fake_url_in_src(self):
        fake = _FAKE_URL
        src_dir = ROOT / "src"
        for py_file in src_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            content = py_file.read_text(encoding="utf-8", errors="replace")
            assert fake not in content, f"Fake URL in {py_file}"

    def test_sarif_metadata_no_fake_url(self):
        sarif_file = ROOT / "src" / "oss_paper_ci" / "reporting" / "sarif_report.py"
        if sarif_file.exists():
            content = sarif_file.read_text(encoding="utf-8")
            assert _FAKE_OWNER + "/" + _FAKE_OWNER not in content, \
                "SARIF metadata contains fake URL"


class TestReadmeCorrectness:
    """Verify README uses correct commands and paths."""

    def test_quickstart_uses_cd_repo(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        # Should use cd oss-paper-ci (actual repo name)
        assert "cd oss-paper-ci" in content, "README quickstart should use 'cd oss-paper-ci'"

    def test_uses_list_checks_command(self):
        # list-checks is documented in CLI reference, not README
        cli_ref = ROOT / "docs" / "cli-reference.md"
        if cli_ref.exists():
            content = cli_ref.read_text(encoding="utf-8")
            assert "list-checks" in content, \
                "CLI reference should document 'list-checks'"
        else:
            content = (ROOT / "README.md").read_text(encoding="utf-8")
            assert "oss-paper-ci list-checks" in content, \
                "README should use 'oss-paper-ci list-checks'"

    def test_no_explain_list_command(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "explain --list" not in content, \
            "README should not use deprecated 'explain --list'"


# ── Cross-Language Fixtures ─────────────────────────────────────────────────

class TestCrossLanguageFixtures:
    """Verify cross-language test fixtures are in the clean zip."""

    def test_r_ready_repo(self):
        names = _zip_names()
        assert any("r_ready_repo" in n for n in names)

    def test_julia_ready_repo(self):
        names = _zip_names()
        assert any("julia_ready_repo" in n for n in names)

    def test_matlab_minimal_repo(self):
        names = _zip_names()
        assert any("matlab_minimal_repo" in n for n in names)

    def test_make_snakemake_repo(self):
        names = _zip_names()
        assert any("make_snakemake_repo" in n for n in names)

    def test_realistic_ml_repo(self):
        names = _zip_names()
        assert any("realistic_ml_repo" in n for n in names)

    def test_paper_ready_repo(self):
        names = _zip_names()
        assert any("paper_ready_repo" in n for n in names)

    def test_broken_paper_repo(self):
        names = _zip_names()
        assert any("broken_paper_repo" in n for n in names)

    def test_minimal_bad_repo(self):
        names = _zip_names()
        assert any("minimal_bad_repo" in n for n in names)


# ── Docs Truthfulness ────────────────────────────────────────────────────────

class TestDocsTruthfulness:
    """Verify documentation is truthful."""

    def test_no_fake_github_url_in_readme(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert _FAKE_URL not in content

    def test_no_fake_github_url_in_docs(self):
        for md in (ROOT / "docs").glob("*.md"):
            content = md.read_text(encoding="utf-8", errors="replace")
            assert _FAKE_URL not in content, \
                f"Fake URL in {md}"

    def test_no_fake_github_url_in_examples(self):
        for f in (ROOT / "examples").rglob("*.yml"):
            content = f.read_text(encoding="utf-8", errors="replace")
            assert _FAKE_URL not in content, \
                f"Fake URL in {f}"

    def test_no_fake_github_url_in_contributing(self):
        content = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
        assert _FAKE_URL not in content

    def test_no_fake_github_url_in_action_yml(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        assert _FAKE_URL not in content

    def test_no_fake_github_url_in_pyproject(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert _FAKE_URL not in content

    def test_pyproject_urls_use_real_repo(self):
        content = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        assert "Akastella/oss-paper-ci" in content, "pyproject.toml should use real repo URL"

    def test_docs_truthfulness_script_exists(self):
        assert (ROOT / "scripts" / "check_docs_truthfulness.py").exists()

    def test_docs_truthfulness_script_runs(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "check_docs_truthfulness.py"),
             "--format", "json", "--check"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
        )
        assert result.returncode == 0, f"Docs truthfulness check failed:\n{result.stdout}\n{result.stderr}"


# ── Action.yml Correctness ───────────────────────────────────────────────────

class TestActionYmlCorrectness:
    """Verify action.yml is correct."""

    def test_uses_github_action_path(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        assert "github.action_path" in content, "action.yml should use github.action_path"

    def test_no_pip_install_dot(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        assert "pip install ." not in content, "action.yml should not use 'pip install .'"

    def test_no_unqualified_pip_install(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        # Should not have bare "pip install oss-paper-ci" without qualifier
        lines = content.split("\n")
        for line in lines:
            if "pip install oss-paper-ci" in line:
                assert "after PyPI" in line.lower() or "github.action_path" in line, \
                    f"Unqualified pip install in action.yml: {line}"

    def test_yaml_parseable(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert data is not None
        assert "runs" in data
        assert data["runs"]["using"] == "composite"

    def test_has_steps(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        steps = data["runs"]["steps"]
        assert len(steps) > 0

    def test_steps_have_names(self):
        content = (ROOT / "action.yml").read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        for step in data["runs"]["steps"]:
            assert "name" in step, f"Step missing name: {step}"


# ── Workflow YAML Parsing ────────────────────────────────────────────────────

class TestWorkflowYamlParsing:
    """Verify all example workflow YAML files are parseable."""

    def _workflow_files(self):
        wf_dir = ROOT / "examples" / "github-actions"
        if not wf_dir.exists():
            pytest.skip("No examples/github-actions directory")
        return list(wf_dir.glob("*.yml"))

    def test_all_workflows_parseable(self):
        for wf in self._workflow_files():
            content = wf.read_text(encoding="utf-8")
            try:
                data = yaml.safe_load(content)
                assert data is not None, f"{wf.name} parsed to None"
            except yaml.YAMLError as e:
                pytest.fail(f"{wf.name} is not valid YAML: {e}")

    def test_full_ci_exists(self):
        wf = ROOT / "examples" / "github-actions" / "full-ci.yml"
        assert wf.exists(), "full-ci.yml not found"

    def test_full_ci_has_scan_step(self):
        wf = ROOT / "examples" / "github-actions" / "full-ci.yml"
        content = wf.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        jobs = data.get("jobs", {})
        for job_name, job in jobs.items():
            steps = job.get("steps", [])
            for step in steps:
                # Check for Action usage (uses:) or run command
                uses = step.get("uses", "")
                run = step.get("run", "")
                name = step.get("name", "")
                if "oss-paper-ci" in str(uses) or "oss-paper-ci" in str(run) or "oss-paper-ci" in str(name):
                    return
        pytest.fail("full-ci.yml has no oss-paper-ci step")

    def test_full_ci_uses_action(self):
        wf = ROOT / "examples" / "github-actions" / "full-ci.yml"
        content = wf.read_text(encoding="utf-8")
        assert "uses: Akastella/oss-paper-ci@" in content

    def test_sarif_upload_exists(self):
        wf = ROOT / "examples" / "github-actions" / "sarif-upload.yml"
        assert wf.exists()

    def test_pr_comment_exists(self):
        wf = ROOT / "examples" / "github-actions" / "pr-comment.yml"
        assert wf.exists()

    def test_baseline_regression_exists(self):
        wf = ROOT / "examples" / "github-actions" / "baseline-regression.yml"
        assert wf.exists()

    def test_use_action_exists(self):
        wf = ROOT / "examples" / "github-actions" / "use-action.yml"
        assert wf.exists()

    def test_source_checkout_exists(self):
        wf = ROOT / "examples" / "github-actions" / "source-checkout.yml"
        assert wf.exists()

    def test_pypi_after_publication_exists(self):
        wf = ROOT / "examples" / "github-actions" / "pypi-after-publication.yml"
        assert wf.exists()


# ── Version Consistency ──────────────────────────────────────────────────────

class TestVersionConsistency:
    """Verify version strings are consistent across files."""

    def test_init_version(self):
        content = (ROOT / "src" / "oss_paper_ci" / "__init__.py").read_text()
        assert "__version__" in content
        # Extract version
        for line in content.split("\n"):
            if "__version__" in line:
                assert "2.1.0rc1" in line
                return
        pytest.fail("Version not found in __init__.py")

    def test_pyproject_version(self):
        content = (ROOT / "pyproject.toml").read_text()
        assert 'version = "2.1.0rc1"' in content

    def test_cli_version_output(self):
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "version"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        assert result.returncode == 0
        assert "2.1.0rc1" in result.stdout

    def test_cli_version_matches_pyproject(self):
        # Get CLI version
        result = subprocess.run(
            [sys.executable, "-m", "oss_paper_ci", "version"],
            capture_output=True, text=True, cwd=ROOT, timeout=10,
        )
        cli_version = result.stdout.strip().split()[-1]

        # Get pyproject version
        content = (ROOT / "pyproject.toml").read_text()
        for line in content.split("\n"):
            if line.startswith("version"):
                py_version = line.split('"')[1]
                assert cli_version == py_version, \
                    f"CLI version {cli_version} != pyproject version {py_version}"
                return
        pytest.fail("Version not found in pyproject.toml")


# ── README References ────────────────────────────────────────────────────────

class TestReadmeReferences:
    """Verify README references point to existing files."""

    def test_docs_references_exist(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        import re
        refs = re.findall(r"\[.*?\]\((docs/[^)]+)\)", content)
        for ref in refs:
            ref_path = ROOT / ref
            assert ref_path.exists(), f"README references non-existent: {ref}"

    def test_license_reference(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "LICENSE" in content
        assert (ROOT / "LICENSE").exists()

    def test_readme_has_quickstart(self):
        content = (ROOT / "README.md").read_text(encoding="utf-8")
        assert "## Quickstart" in content or "## Quick start" in content


# ── Docs References ──────────────────────────────────────────────────────────

class TestDocsReferences:
    """Verify docs reference existing examples and files."""

    def test_github_actions_doc_references_workflows(self):
        content = (ROOT / "docs" / "github-actions.md").read_text(encoding="utf-8")
        # Should reference some workflow examples
        assert "oss-paper-ci" in content

    def test_cross_language_doc_exists(self):
        assert (ROOT / "docs" / "cross-language.md").exists()

    def test_troubleshooting_doc_exists(self):
        assert (ROOT / "docs" / "troubleshooting.md").exists()

    def test_clean_room_doc_exists(self):
        assert (ROOT / "docs" / "clean-room-verification.md").exists()


# ── Package Build ────────────────────────────────────────────────────────────

class TestPackageBuild:
    """Verify package can be built and passes twine check."""

    def test_build_succeeds(self):
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            capture_output=True, text=True, cwd=ROOT, timeout=120,
        )
        assert result.returncode == 0, f"Build failed:\n{result.stderr}"

    def test_twine_check_passes(self):
        result = subprocess.run(
            [sys.executable, "-m", "twine", "check", "dist/*"],
            capture_output=True, text=True, cwd=ROOT, timeout=30,
            shell=True,
        )
        assert result.returncode == 0, f"Twine check failed:\n{result.stderr}"
