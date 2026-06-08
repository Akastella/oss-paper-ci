"""CI checks -- continuous integration, testing, and project hygiene."""

from __future__ import annotations

import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class CI001WorkflowsExist(BaseChecker):
    """CI001: GitHub Actions workflows exist."""

    check_id = "CI001"
    title = "GitHub Actions workflows exist"
    severity = Severity.INFO

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        workflows = [
            str(f)
            for f in ctx.files
            if ".github" in f.parts
            and "workflows" in f.parts
            and f.suffix in (".yml", ".yaml")
        ]

        if workflows:
            return [self._pass(
                f"Found {len(workflows)} GitHub Actions workflow(s).",
                evidence=workflows,
            )]

        return [self._pass(
            "No GitHub Actions workflows found (informational).",
        )]


@register
class CI002TestsExist(BaseChecker):
    """CI002: Tests exist."""

    check_id = "CI002"
    title = "Tests exist"
    severity = Severity.WARNING

    _TEST_FILE_PATTERNS = (
        re.compile(r".*_test\.py$"),
        re.compile(r"^test_.*\.py$"),
    )

    _TEST_CONFIG_FILES = (
        "pytest.ini",
        "conftest.py",
        "tox.ini",
    )

    _TEST_DIRS = ("tests", "test")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []

        # Check for test directories.
        for d in self._TEST_DIRS:
            for f in ctx.files:
                if d in f.parts and f.suffix == ".py":
                    found.append(f"{d}/ (Python test directory)")
                    break

        # Check for test files by naming convention.
        for f in ctx.files:
            rel = f
            name = f.name
            if any(pat.match(name) for pat in self._TEST_FILE_PATTERNS):
                entry = str(rel)
                if entry not in found:
                    found.append(entry)

        # Check for test config files.
        for name in self._TEST_CONFIG_FILES:
            if ctx.has_file(name):
                found.append(name)

        # Check pyproject.toml for [tool.pytest] section.
        pyproject = ctx.read_file("pyproject.toml")
        if pyproject and re.search(
            r"^\[tool\.pytest", pyproject, re.MULTILINE | re.IGNORECASE,
        ):
            found.append("pyproject.toml ([tool.pytest])")

        if found:
            return [self._pass(
                f"Found test infrastructure: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._warn(
            "No test files or test configuration found.",
            recommendation=(
                "Add a tests/ directory with unit tests and configure pytest "
                "so that others can verify the correctness of your code."
            ),
        )]


@register
class CI003LintingConfigured(BaseChecker):
    """CI003: Linting or formatting configured."""

    check_id = "CI003"
    title = "Linting or formatting configured"
    severity = Severity.INFO

    _LINT_FILES = (
        ".flake8",
        ".pylintrc",
        ".pre-commit-config.yaml",
        ".editorconfig",
        "ruff.toml",
    )

    _PYPROJECT_TOOLS = (
        "[tool.ruff]",
        "[tool.black]",
        "[tool.isort]",
        "[tool.flake8]",
        "[tool.pylint]",
        "[tool.mypy]",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []

        # Check for standalone lint/format config files.
        for name in self._LINT_FILES:
            if ctx.has_file(name):
                found.append(name)

        # Check pyproject.toml for linting tool sections.
        pyproject = ctx.read_file("pyproject.toml")
        if pyproject:
            for tool in self._PYPROJECT_TOOLS:
                if re.search(re.escape(tool), pyproject, re.MULTILINE):
                    found.append(f"pyproject.toml ({tool})")

        if found:
            return [self._pass(
                f"Found linting/formatting configuration: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._pass(
            "No linting or formatting configuration found (informational).",
        )]


@register
class CI004IssuePRTemplates(BaseChecker):
    """CI004: Issue or PR templates exist."""

    check_id = "CI004"
    title = "Issue or PR templates exist"
    severity = Severity.INFO

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []

        # Check for .github/ISSUE_TEMPLATE/ directory contents.
        for f in ctx.files:
            rel = f
            parts = rel.parts
            if (
                ".github" in parts
                and "ISSUE_TEMPLATE" in parts
                and f.suffix in (".md", ".yml", ".yaml")
            ):
                found.append(str(rel))
                break

        # Check for specific template files.
        for path in (
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/ISSUE_TEMPLATE.md",
        ):
            if ctx.has_file(path):
                found.append(path)

        if found:
            return [self._pass(
                f"Found issue/PR templates: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._warn(
            "No issue or PR templates found.",
            recommendation=(
                "Consider adding issue and pull request templates in "
                ".github/ to standardize contributions."
            ),
        )]


@register
class CI005SecurityPolicy(BaseChecker):
    """CI005: Security policy exists."""

    check_id = "CI005"
    title = "Security policy exists"
    severity = Severity.INFO

    _POLICY_PATHS = (
        "SECURITY.md",
        "SECURITY",
        ".github/SECURITY.md",
        "security.md",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        for name in self._POLICY_PATHS:
            if ctx.has_file(name):
                return [self._pass(
                    f"Found security policy: {name}.",
                    evidence=[name],
                )]

        return [self._pass(
            "No security policy found (informational).",
            recommendation=(
                "Consider adding a SECURITY.md file to describe how "
                "users should report security vulnerabilities."
            ),
        )]


@register
class CI006PackageMetadata(BaseChecker):
    """CI006: Package metadata complete."""

    check_id = "CI006"
    title = "Package metadata complete"
    severity = Severity.INFO

    _REQUIRED_FIELDS = ("name", "version", "description", "license", "authors")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Try pyproject.toml first.
        pyproject = ctx.read_file("pyproject.toml")
        if pyproject:
            return self._check_pyproject(pyproject)

        # Fall back to setup.py / setup.cfg.
        if ctx.has_file("setup.py") or ctx.has_file("setup.cfg"):
            return self._check_setup(ctx)

        return [self._pass(
            "No package metadata files found (informational).",
            recommendation=(
                "Add a pyproject.toml (or setup.py/setup.cfg) with "
                "name, version, description, license, and authors fields."
            ),
        )]

    def _check_pyproject(self, content: str) -> list[CheckResult]:
        """Check pyproject.toml for required metadata fields."""
        missing: list[str] = []

        for field in self._REQUIRED_FIELDS:
            # Look for the field at the top level (under [project] or [tool.poetry]).
            pattern = rf'^\s*{field}\s*='
            if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                missing.append(field)

        if not missing:
            return [self._pass(
                "Package metadata is complete in pyproject.toml.",
                evidence=["pyproject.toml"],
            )]

        return [self._pass(
            f"Package metadata incomplete in pyproject.toml; missing: {', '.join(missing)}.",
            evidence=["pyproject.toml"],
            recommendation=(
                f"Add the following fields to pyproject.toml: {', '.join(missing)}."
            ),
        )]

    def _check_setup(self, ctx: CheckContext) -> list[CheckResult]:
        """Check setup.py/setup.cfg for required metadata fields."""
        missing: list[str] = []
        found_in: list[str] = []

        setup_cfg = ctx.read_file("setup.cfg")
        setup_py = ctx.read_file("setup.py")
        content = (setup_cfg or "") + "\n" + (setup_py or "")

        if setup_cfg:
            found_in.append("setup.cfg")
        if setup_py:
            found_in.append("setup.py")

        for field in self._REQUIRED_FIELDS:
            if not re.search(
                rf'\b{field}\s*[=:]',
                content,
                re.MULTILINE | re.IGNORECASE,
            ):
                missing.append(field)

        if not missing:
            return [self._pass(
                f"Package metadata is complete in {'/'.join(found_in)}.",
                evidence=found_in,
            )]

        return [self._pass(
            f"Package metadata incomplete in {'/'.join(found_in)}; missing: {', '.join(missing)}.",
            evidence=found_in,
            recommendation=(
                f"Add the following fields to your setup configuration: {', '.join(missing)}."
            ),
        )]
