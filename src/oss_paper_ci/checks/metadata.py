"""META checks -- repository metadata and documentation quality."""

from __future__ import annotations

import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class Meta001ReadmeExists(BaseChecker):
    """META001: README file exists."""

    check_id = "META001"
    title = "README file exists"
    severity = Severity.ERROR

    _README_NAMES = ("README.md", "README.rst", "README")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        for name in self._README_NAMES:
            if ctx.has_file(name):
                return [self._pass(
                    f"Found {name}.",
                    evidence=[name],
                )]
        return [self._fail(
            "No README file found.",
            recommendation=(
                "Add a README.md (or README.rst / README) to your repository "
                "so that others can understand and reproduce your work."
            ),
        )]


@register
class Meta002LicenseExists(BaseChecker):
    """META002: LICENSE file exists."""

    check_id = "META002"
    title = "LICENSE file exists"
    severity = Severity.ERROR

    _LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE", "COPYING")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        for name in self._LICENSE_NAMES:
            if ctx.has_file(name):
                return [self._pass(
                    f"Found {name}.",
                    evidence=[name],
                )]
        return [self._fail(
            "No LICENSE file found.",
            recommendation=(
                "Add a LICENSE file to your repository to clarify the terms "
                "under which your code and data may be reused."
            ),
        )]


@register
class Meta003CitationExists(BaseChecker):
    """META003: Citation information exists."""

    check_id = "META003"
    title = "Citation information exists"
    severity = Severity.WARNING

    _CITATION_FILES = ("CITATION.cff", "CITATION", "CITATION.bib")
    _CITATION_SECTION_RE = re.compile(
        r"^#+\s*(?:cite|citation|how\s+to\s+cite|referencing)\b",
        re.IGNORECASE | re.MULTILINE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Check for dedicated citation files.
        for name in self._CITATION_FILES:
            if ctx.has_file(name):
                return [self._pass(
                    f"Found {name}.",
                    evidence=[name],
                )]

        # Check for a citation section in the README.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._CITATION_SECTION_RE.search(content):
                return [self._pass(
                    f"Found citation section in {readme}.",
                    evidence=[readme],
                )]

        return [self._warn(
            "No citation information found.",
            recommendation=(
                "Add a CITATION.cff file or a 'Citation' section to your "
                "README so that users know how to properly cite your work."
            ),
        )]


@register
class Meta004ReproductionInstructions(BaseChecker):
    """META004: Reproduction instructions exist."""

    check_id = "META004"
    title = "Reproduction instructions exist"
    severity = Severity.WARNING

    _KEYWORDS = re.compile(
        r"\b(?:reproduc|getting\s+started|quickstart|installation|usage)\b",
        re.IGNORECASE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._KEYWORDS.search(content):
                return [self._pass(
                    f"Found reproduction / setup instructions in {readme}.",
                    evidence=[readme],
                )]

        return [self._warn(
            "No reproduction instructions found in README.",
            recommendation=(
                "Add sections such as 'Getting Started', 'Installation', or "
                "'Usage' to your README so that others can reproduce your "
                "results."
            ),
        )]


@register
class Meta005ContributingGuidelines(BaseChecker):
    """META005: Contributing guidelines exist."""

    check_id = "META005"
    title = "Contributing guidelines exist"
    severity = Severity.INFO

    _PATHS = (
        "CONTRIBUTING.md",
        "CONTRIBUTING",
        ".github/ISSUE_TEMPLATE",
        "docs/contributing.md",
        "docs/contributing.rst",
        "docs/contributing",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []
        for path in self._PATHS:
            if ctx.has_file(path):
                found.append(path)

        if found:
            return [self._pass(
                f"Found contributing guidelines: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._info(
            "No contributing guidelines found.",
            recommendation=(
                "Consider adding a CONTRIBUTING.md file or an issue template "
                "to encourage community contributions."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Create an INFO-severity result (checker severity is already INFO)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


@register
class Meta006VersionInfo(BaseChecker):
    """META006: Version or release information."""

    check_id = "META006"
    title = "Version or release information"
    severity = Severity.INFO

    _VERSION_FILES = (
        "CHANGELOG.md",
        "CHANGELOG",
        "CHANGES",
        "CHANGES.md",
        "HISTORY",
        "HISTORY.md",
        "VERSION",
        "VERSION.txt",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []
        for name in self._VERSION_FILES:
            if ctx.has_file(name):
                found.append(name)

        # Check pyproject.toml for a version field.
        pyproject = ctx.read_file("pyproject.toml")
        if pyproject and re.search(r'^\s*version\s*=', pyproject, re.MULTILINE):
            found.append("pyproject.toml (version)")

        if found:
            return [self._pass(
                f"Found version/release information: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._info(
            "No version or release information found.",
            recommendation=(
                "Add a CHANGELOG, VERSION file, or a version field in "
                "pyproject.toml so users can track releases."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


@register
class Meta007ArtifactMetadata(BaseChecker):
    """META007: Artifact metadata file exists."""

    check_id = "META007"
    title = "Artifact metadata file exists"
    severity = Severity.INFO

    _METADATA_FILES = (
        "oss-paper-ci.yml",
        "artifact.yml",
        "reproducibility.yml",
        ".reproducibility.yml",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []
        for name in self._METADATA_FILES:
            if ctx.has_file(name):
                found.append(name)

        if found:
            return [self._pass(
                f"Found artifact metadata: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._info(
            "No artifact metadata file found.",
            recommendation=(
                "Add an artifact metadata file (e.g. artifact.yml or "
                "reproducibility.yml) to describe how to reproduce your "
                "experiments."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )
