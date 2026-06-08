"""Environment and dependency checkers for oss-paper-ci.

These checkers verify that the repository has proper environment
specification, lock files, Python version pinning, and documentation
of system/GPU dependencies.
"""

from __future__ import annotations

import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class EnvSpecificationExists(BaseChecker):
    """ENV001: Check that at least one environment specification file exists."""

    check_id = "ENV001"
    title = "Environment specification file exists"
    severity = Severity.ERROR
    category = "environment"
    description = "Checks that at least one environment specification file (requirements.txt, pyproject.toml, Dockerfile, etc.) exists."

    SPEC_FILES = [
        "requirements.txt",
        "environment.yml",
        "environment.yaml",
        "pyproject.toml",
        "Pipfile",
        "poetry.lock",
        "setup.py",
        "setup.cfg",
        "Dockerfile",
        "container.def",
        "Singularity",
        "apt.txt",
        "install.R",
        "renv.lock",
    ]

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found = [f for f in self.SPEC_FILES if ctx.has_file(f)]

        if not found:
            return [self._fail(
                "No environment specification file found",
                recommendation=(
                    "Add an environment specification file such as "
                    "requirements.txt, pyproject.toml, environment.yml, "
                    "or a Dockerfile so others can reproduce the environment."
                ),
            )]

        # Validate content of key specification files.
        warnings: list[str] = []

        if "requirements.txt" in found:
            content = ctx.read_file("requirements.txt")
            if content is not None:
                lines = [
                    line.strip()
                    for line in content.splitlines()
                    if line.strip() and not line.strip().startswith("#")
                ]
                if not lines:
                    warnings.append(
                        "requirements.txt exists but is empty (no packages listed)"
                    )

        if "pyproject.toml" in found:
            content = ctx.read_file("pyproject.toml")
            if content is not None:
                has_project = bool(re.search(
                    r"^\[(?:project|tool\.poetry)\]", content, re.MULTILINE,
                ))
                if not has_project:
                    warnings.append(
                        "pyproject.toml exists but has no [project] or "
                        "[tool.poetry] section"
                    )

        if "environment.yml" in found:
            content = ctx.read_file("environment.yml")
            if content is not None:
                if "dependencies" not in content:
                    warnings.append(
                        "environment.yml exists but has no 'dependencies' key"
                    )

        if "environment.yaml" in found:
            content = ctx.read_file("environment.yaml")
            if content is not None:
                if "dependencies" not in content:
                    warnings.append(
                        "environment.yaml exists but has no 'dependencies' key"
                    )

        if warnings:
            return [self._warn(
                f"Found {len(found)} environment specification file(s), "
                f"but with issues: {'; '.join(warnings)}",
                evidence=found,
                recommendation=(
                    "Fix the issues in the environment specification files "
                    "so that the environment can be properly reproduced."
                ),
            )]

        return [self._pass(
            f"Found {len(found)} environment specification file(s)",
            evidence=found,
        )]


@register
class LockFileExists(BaseChecker):
    """ENV002: Check that a lock file exists for reproducible installs."""

    check_id = "ENV002"
    title = "Lock file exists"
    severity = Severity.WARNING
    category = "environment"
    description = "Checks that a lock file (poetry.lock, Pipfile.lock, uv.lock, etc.) exists for reproducible installs."

    LOCK_FILES = [
        "poetry.lock",
        "Pipfile.lock",
        "conda-lock.yml",
        "uv.lock",
    ]

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []

        # Check dedicated lock files
        for name in self.LOCK_FILES:
            if ctx.has_file(name):
                found.append(name)

        # Check for requirements files with "lock" in the name
        for f in ctx.files:
            fname = f.name.lower()
            if fname.startswith("requirements") and "lock" in fname and fname.endswith(".txt"):
                found.append(str(f))

        # Check requirements.txt itself -- treat as lock if it has pinned versions
        if ctx.has_file("requirements.txt"):
            content = ctx.read_file("requirements.txt")
            if content and "==" in content:
                found.append("requirements.txt (pinned versions)")

        if found:
            return [self._pass(
                f"Found lock file(s): {', '.join(found)}",
                evidence=found,
            )]

        return [self._warn(
            "No lock file found",
            recommendation=(
                "Add a lock file (e.g. poetry.lock, Pipfile.lock, "
                "uv.lock, or conda-lock.yml) to ensure reproducible "
                "dependency resolution."
            ),
        )]


@register
class PythonVersionSpecified(BaseChecker):
    """ENV003: Check that a Python version is specified."""

    check_id = "ENV003"
    title = "Python version specified"
    severity = Severity.WARNING
    category = "environment"
    description = "Checks that a Python version is specified in pyproject.toml, setup.cfg, .python-version, or similar."

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        sources: list[str] = []

        # Check pyproject.toml for requires-python
        pyproject = ctx.read_file("pyproject.toml")
        if pyproject and "requires-python" in pyproject:
            sources.append("pyproject.toml (requires-python)")

        # Check setup.cfg for python_requires
        setup_cfg = ctx.read_file("setup.cfg")
        if setup_cfg and "python_requires" in setup_cfg:
            sources.append("setup.cfg (python_requires)")

        # Check runtime.txt (common in Heroku / Binder)
        if ctx.has_file("runtime.txt"):
            sources.append("runtime.txt")

        # Check .python-version (pyenv)
        if ctx.has_file(".python-version"):
            sources.append(".python-version")

        # Check Pipfile for python_version
        pipfile = ctx.read_file("Pipfile")
        if pipfile and "python_version" in pipfile:
            sources.append("Pipfile (python_version)")

        # Check README for Python version mentions
        readme = self._read_readme(ctx)
        if readme and re.search(r"[Pp]ython\s*\d+\.\d+", readme):
            sources.append("README.md (version mention)")

        if sources:
            return [self._pass(
                "Python version is specified",
                evidence=sources,
            )]

        return [self._warn(
            "No Python version specification found",
            recommendation=(
                "Specify the required Python version in pyproject.toml "
                "(requires-python), setup.cfg (python_requires), "
                ".python-version, or Pipfile."
            ),
        )]

    @staticmethod
    def _read_readme(ctx: CheckContext) -> str | None:
        """Read the first README file found (any common casing/extension)."""
        for name in ("README.md", "README.rst", "README.txt", "README", "readme.md"):
            content = ctx.read_file(name)
            if content:
                return content
        return None


@register
class SystemDependenciesDocumented(BaseChecker):
    """ENV004: Check that system-level dependencies are documented."""

    check_id = "ENV004"
    title = "System dependencies documented"
    severity = Severity.INFO
    category = "environment"
    description = "Checks that system-level dependencies (apt, brew, etc.) are documented in the README or dedicated files."

    SYSTEM_KEYWORDS = [
        r"\bapt\b",
        r"\bbrew\b",
        r"\bsystem\b",
        r"\binstall\b",
        r"\bprerequisite\b",
        r"\bdependency\b",
        r"\bsudo\b",
        r"\bapt-get\b",
        r"\byum\b",
    ]

    SYSTEM_FILES = [
        "apt.txt",
        "Brewfile",
        "install.sh",
    ]

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Check for dedicated system dependency files
        for name in self.SYSTEM_FILES:
            if ctx.has_file(name):
                evidence.append(name)

        # Check README for system dependency keywords
        readme = self._read_readme(ctx)
        if readme:
            for pattern in self.SYSTEM_KEYWORDS:
                if re.search(pattern, readme, re.IGNORECASE):
                    evidence.append(f"README mentions system dependency ({pattern})")
                    break  # One mention is enough

        if evidence:
            return [self._pass(
                "System dependencies appear to be documented",
                evidence=evidence,
            )]

        return [self._info(
            "No system dependency documentation found",
            recommendation=(
                "Document any system-level prerequisites (e.g. apt packages, "
                "brew packages, or OS-level libraries) in the README or a "
                "dedicated file like apt.txt or Brewfile."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Helper for INFO-level results (pass with info severity)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.PASS,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )

    @staticmethod
    def _read_readme(ctx: CheckContext) -> str | None:
        for name in ("README.md", "README.rst", "README.txt", "README", "readme.md"):
            content = ctx.read_file(name)
            if content:
                return content
        return None


@register
class GpuCpuRequirementsDocumented(BaseChecker):
    """ENV005: Check that GPU/CPU/hardware requirements are documented."""

    check_id = "ENV005"
    title = "GPU/CPU requirements documented"
    severity = Severity.INFO
    category = "environment"
    description = "Checks that GPU, CPU, or other hardware requirements are documented in the README."

    HARDWARE_KEYWORDS = [
        "GPU",
        "CUDA",
        "cpu",
        "gpu",
        "TPU",
        "hardware",
        "memory",
        "RAM",
    ]

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        readme = self._read_readme(ctx)
        if readme:
            found_keywords = [
                kw for kw in self.HARDWARE_KEYWORDS
                if kw in readme
            ]
            if found_keywords:
                return [self._pass(
                    "Hardware requirements mentioned in README",
                    evidence=[f"README contains: {', '.join(found_keywords)}"],
                )]

        return [self._info(
            "No GPU/CPU/hardware requirements documentation found",
            recommendation=(
                "If the project requires specific hardware (GPU, CUDA, "
                "large memory), document these requirements in the README."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Helper for INFO-level results (pass with info severity)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.PASS,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )

    @staticmethod
    def _read_readme(ctx: CheckContext) -> str | None:
        for name in ("README.md", "README.rst", "README.txt", "README", "readme.md"):
            content = ctx.read_file(name)
            if content:
                return content
        return None


@register
class MultipleEnvironmentFilesConsistent(BaseChecker):
    """ENV006: Check that multiple environment files have guidance in README."""

    check_id = "ENV006"
    title = "Multiple environment files consistent"
    severity = Severity.WARNING
    category = "environment"
    description = "Checks that when multiple environment files co-exist (e.g., requirements.txt and environment.yml), the README provides guidance on which to use."

    # Pairs of (file_a, file_b) to check for co-existence
    FILE_PAIRS = [
        ("requirements.txt", "environment.yml"),
        ("pyproject.toml", "requirements.txt"),
    ]

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []

        for file_a, file_b in self.FILE_PAIRS:
            if ctx.has_file(file_a) and ctx.has_file(file_b):
                readme = self._read_readme(ctx)
                if readme and self._explains_choice(readme, file_a, file_b):
                    results.append(self._pass(
                        f"Both {file_a} and {file_b} exist; README explains which to use",
                        evidence=[file_a, file_b, "README.md"],
                    ))
                else:
                    results.append(self._warn(
                        f"Both {file_a} and {file_b} exist but no clear guidance found in README",
                        evidence=[file_a, file_b],
                        recommendation=(
                            f"Document in the README which file ({file_a} or {file_b}) "
                            "users should use and under what circumstances."
                        ),
                    ))

        if not results:
            # No conflicting pairs found -- this is fine, nothing to report
            results.append(self._pass(
                "No conflicting environment file pairs detected",
            ))

        return results

    def _explains_choice(self, readme: str, file_a: str, file_b: str) -> bool:
        """Check if README mentions both files and provides guidance."""
        # Simple heuristic: if the README mentions both filenames, there's
        # likely some guidance about when to use each.
        mentions_a = file_a in readme
        mentions_b = file_b in readme
        return mentions_a and mentions_b

    @staticmethod
    def _read_readme(ctx: CheckContext) -> str | None:
        for name in ("README.md", "README.rst", "README.txt", "README", "readme.md"):
            content = ctx.read_file(name)
            if content:
                return content
        return None
