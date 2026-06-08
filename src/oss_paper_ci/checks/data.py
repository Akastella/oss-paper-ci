"""DATA checks -- data sourcing, documentation, and management."""

from __future__ import annotations

import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class Data001DataSourceDocumentation(BaseChecker):
    """DATA001: Data source documentation exists."""

    check_id = "DATA001"
    title = "Data source documentation exists"
    severity = Severity.WARNING
    category = "data"
    description = "Checks that data sources are documented in the README or a dedicated data directory."

    _KEYWORDS = re.compile(
        r"\b(?:data(?:set)?|download|data\s+source)\b",
        re.IGNORECASE,
    )

    _DOC_PATHS = (
        "DATASET.md",
        "DATASET",
        "data/README.md",
        "data/README",
        "data/README.rst",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Check README for data-related keywords.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._KEYWORDS.search(content):
                evidence.append(f"{readme} (data keywords)")

        # Check for data directory or dedicated data docs.
        if ctx.has_file("data"):
            evidence.append("data/")
        for path in self._DOC_PATHS:
            if ctx.has_file(path):
                evidence.append(path)

        if evidence:
            return [self._pass(
                "Found data source documentation.",
                evidence=evidence,
            )]

        return [self._warn(
            "No data source documentation found.",
            recommendation=(
                "Add data-related information to your README (e.g. where "
                "the dataset comes from, how to obtain it) or create a "
                "dedicated data/README or DATASET.md file."
            ),
        )]


@register
class Data002DownloadInstructions(BaseChecker):
    """DATA002: Data download instructions exist."""

    check_id = "DATA002"
    title = "Data download instructions exist"
    severity = Severity.WARNING
    category = "data"
    description = "Checks for data download instructions (wget/curl commands, download scripts, or data URLs)."

    _DOWNLOAD_KEYWORDS = re.compile(
        r"\b(?:wget|curl|gdown|kaggle|huggingface|zenodo|figshare|"
        r"download\s+(?:data|dataset)|data\s+download)\b",
        re.IGNORECASE,
    )
    _URL_PATTERN = re.compile(
        r"https?://\S+(?:\.zip|\.tar|\.gz|\.csv|\.h5|\.parquet|\.json)",
        re.IGNORECASE,
    )
    _DOI_PATTERN = re.compile(
        r"\b(?:doi\.org/|DOI:\s*\S+|10\.\d{4,}/\S+)\b",
        re.IGNORECASE,
    )

    _SCRIPT_PATHS = (
        "download_data.sh",
        "get_data.py",
        "download.py",
        "scripts/download_data.sh",
        "scripts/get_data.py",
        "scripts/download.py",
        "scripts/download_data.py",
        "data/download_data.sh",
        "data/get_data.py",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Check README for download instructions.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content:
                if self._DOWNLOAD_KEYWORDS.search(content):
                    evidence.append(f"{readme} (download keywords)")
                if self._URL_PATTERN.search(content):
                    evidence.append(f"{readme} (data URL)")
                if self._DOI_PATTERN.search(content):
                    evidence.append(f"{readme} (DOI reference)")

        # Check for download scripts.
        for path in self._SCRIPT_PATHS:
            if ctx.has_file(path):
                evidence.append(path)

        if evidence:
            return [self._pass(
                "Found data download instructions.",
                evidence=evidence,
            )]

        return [self._warn(
            "No data download instructions found.",
            recommendation=(
                "Add download instructions to your README (e.g. wget/curl "
                "commands, links to Zenodo/Figshare/HuggingFace) or include "
                "a download_data.sh / get_data.py script."
            ),
        )]


@register
class Data003DataCategories(BaseChecker):
    """DATA003: Data categories distinguished."""

    check_id = "DATA003"
    title = "Data categories distinguished"
    severity = Severity.INFO
    category = "data"
    description = "Checks that data is organized into categories (raw/, processed/, interim/) to clarify the pipeline."

    _CATEGORY_DIRS = (
        "data/raw",
        "data/processed",
        "data/interim",
        "data/external",
    )

    _CATEGORY_KEYWORDS = re.compile(
        r"\b(?:raw\s+data|processed\s+data|intermediate(?:\s+data)?)\b",
        re.IGNORECASE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Check for category subdirectories.
        for path in self._CATEGORY_DIRS:
            if ctx.has_file(path):
                evidence.append(path + "/")

        # Check README for category mentions.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._CATEGORY_KEYWORDS.search(content):
                evidence.append(f"{readme} (data categories)")

        if evidence:
            return [self._pass(
                "Data categories are distinguished.",
                evidence=evidence,
            )]

        return [self._info(
            "No distinction between data categories found.",
            recommendation=(
                "Consider organizing your data into subdirectories such as "
                "raw/, processed/, interim/, and external/ to clarify the "
                "data processing pipeline."
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
class Data004LargeFilesNotCommitted(BaseChecker):
    """DATA004: Large files not in repository."""

    check_id = "DATA004"
    title = "Large files not in repository"
    severity = Severity.WARNING
    category = "data"
    description = "Checks that large data files are not committed directly, or are managed via Git LFS or .gitignore."

    _LARGE_EXTENSIONS = frozenset({
        ".h5", ".hdf5", ".pkl", ".pickle", ".npy", ".npz",
        ".parquet", ".feather", ".zip", ".tar", ".gz",
    })
    _CSV_EXTENSION = ".csv"
    _MAX_CSV_BYTES = 1_048_576  # 1 MB

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        large_files: list[str] = []

        for f in ctx.files:
            suffix = f.suffix.lower()
            if suffix in self._LARGE_EXTENSIONS:
                large_files.append(str(f))
            elif suffix == self._CSV_EXTENSION:
                try:
                    if f.stat().st_size > self._MAX_CSV_BYTES:
                        large_files.append(f"{f} ({f.stat().st_size / 1_048_576:.1f} MB)")
                except OSError:
                    pass

        if not large_files:
            return [self._pass(
                "No large data files found in the repository.",
            )]

        # Check for LFS configuration.
        has_lfs = False
        gitattributes = ctx.read_file(".gitattributes")
        if gitattributes and re.search(r"\blfs\b", gitattributes, re.IGNORECASE):
            has_lfs = True

        # Check .gitignore for data patterns.
        has_gitignore_patterns = False
        gitignore = ctx.read_file(".gitignore")
        if gitignore and re.search(
            r"\*\.(?:h5|hdf5|pkl|pickle|npy|npz|parquet|feather|zip|tar|gz)\b",
            gitignore,
            re.IGNORECASE,
        ):
            has_gitignore_patterns = True

        if has_lfs:
            return [self._pass(
                f"Large files detected but Git LFS is configured.",
                evidence=large_files[:10],
            )]

        if has_gitignore_patterns:
            return [self._pass(
                f"Large file extensions found in .gitignore.",
                evidence=large_files[:10],
            )]

        return [self._warn(
            f"Found {len(large_files)} large file(s) without LFS or .gitignore protection.",
            evidence=large_files[:10],
            recommendation=(
                "Use Git LFS (git lfs track '*.h5') or add large file "
                "extensions to .gitignore to avoid bloating the repository."
            ),
        )]


@register
class Data005DataPathsInGitignore(BaseChecker):
    """DATA005: Data paths in .gitignore."""

    check_id = "DATA005"
    title = "Data paths in .gitignore"
    severity = Severity.INFO
    category = "data"
    description = "Checks that data-related patterns (data/, *.csv, *.h5) are listed in .gitignore."

    _DATA_PATTERNS = re.compile(
        r"(?:^|\s)(?:"
        r"data/|"
        r"\*\.(?:csv|h5|hdf5|pkl|pickle|npy|npz|parquet|feather|zip|tar|gz)\b|"
        r"(?:raw|processed|interim|external)/"
        r")",
        re.IGNORECASE | re.MULTILINE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        gitignore = ctx.read_file(".gitignore")

        if gitignore:
            matches = self._DATA_PATTERNS.findall(gitignore)
            if matches:
                return [self._pass(
                    "Found data-related patterns in .gitignore.",
                    evidence=[m.strip() for m in matches[:10]],
                )]

        return [self._info(
            "No data-related patterns found in .gitignore.",
            recommendation=(
                "Add data patterns to .gitignore (e.g. data/, *.csv, "
                "*.h5, *.parquet) to prevent accidental commits of large "
                "or sensitive data files."
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
class Data006PrivacyAndLicensing(BaseChecker):
    """DATA006: Privacy and licensing for data."""

    check_id = "DATA006"
    title = "Privacy and licensing for data"
    severity = Severity.INFO
    category = "data"
    description = "Checks for data privacy or licensing information (DATA_LICENSE, consent, anonymization notes)."

    _PRIVACY_KEYWORDS = re.compile(
        r"\b(?:license|privacy|public|synthetic|simulated|anonymized|consent)\b",
        re.IGNORECASE,
    )

    _LICENSING_PATHS = (
        "DATA_LICENSE",
        "DATA_LICENSE.md",
        "DATA_LICENSE.txt",
        "data/README.md",
        "data/README",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Check README for privacy/licensing keywords.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._PRIVACY_KEYWORDS.search(content):
                matches = self._PRIVACY_KEYWORDS.findall(content)
                evidence.append(f"{readme} ({', '.join(set(m.lower() for m in matches))})")

        # Check for dedicated data licensing files.
        for path in self._LICENSING_PATHS:
            if ctx.has_file(path):
                evidence.append(path)

        if evidence:
            return [self._pass(
                "Found data privacy or licensing information.",
                evidence=evidence,
            )]

        return [self._info(
            "No data privacy or licensing information found.",
            recommendation=(
                "Add information about data licensing, privacy, or usage "
                "terms to your README or create a DATA_LICENSE file. Mention "
                "whether data is public, synthetic, anonymized, or requires "
                "consent."
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
