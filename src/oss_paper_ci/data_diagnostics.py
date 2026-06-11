"""Data availability diagnostics for reproducibility.

Checks data documentation, availability statements, external data
declarations, sample data, large files, and data-related metadata.
Does NOT download or verify data online.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class DataDiagnostic:
    """A single data diagnostic result."""

    check_id: str
    title: str
    status: str  # present, missing, partial, unknown
    message: str
    recommendation: str = ""
    severity: str = "info"  # info, warning, error

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "status": self.status,
            "message": self.message,
            "recommendation": self.recommendation,
            "severity": self.severity,
        }


def run_data_diagnostics(repo_path: str) -> list[DataDiagnostic]:
    """Run data availability diagnostics on a repository.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of DataDiagnostic results.
    """
    root = Path(repo_path)
    diagnostics: list[DataDiagnostic] = []

    # 1. data/ directory exists
    data_dir = root / "data"
    if data_dir.exists():
        diagnostics.append(DataDiagnostic(
            check_id="DATA_DIR",
            title="Data directory",
            status="present",
            message="data/ directory exists",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_DIR",
            title="Data directory",
            status="missing",
            message="No data/ directory found",
            recommendation="Create a data/ directory or document where data can be found.",
            severity="warning",
        ))

    # 2. data/README.md exists
    data_readme = root / "data" / "README.md"
    if data_readme.exists():
        diagnostics.append(DataDiagnostic(
            check_id="DATA_README",
            title="Data documentation",
            status="present",
            message="data/README.md exists",
            severity="info",
        ))
    else:
        # Check if data directory has any documentation
        if data_dir.exists():
            has_docs = any(data_dir.glob("*.md")) or any(data_dir.glob("*.txt"))
            if has_docs:
                diagnostics.append(DataDiagnostic(
                    check_id="DATA_README",
                    title="Data documentation",
                    status="partial",
                    message="data/ has documentation but no README.md",
                    recommendation="Add data/README.md for clarity.",
                    severity="warning",
                ))
            else:
                diagnostics.append(DataDiagnostic(
                    check_id="DATA_README",
                    title="Data documentation",
                    status="missing",
                    message="No data documentation found",
                    recommendation="Add data/README.md explaining data sources and access.",
                    severity="warning",
                ))

    # 3. Data availability statement in README
    readme = root / "README.md"
    has_availability = False
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="replace").lower()
        availability_keywords = [
            "data availability", "data source", "data access",
            "download data", "data url", "dataset available",
            "data can be found", "data is available at",
        ]
        has_availability = any(kw in content for kw in availability_keywords)

    if has_availability:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_AVAILABILITY",
            title="Data availability statement",
            status="present",
            message="README contains data availability information",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_AVAILABILITY",
            title="Data availability statement",
            status="missing",
            message="No data availability statement found in README",
            recommendation="Add a data availability section to README.",
            severity="warning",
        ))

    # 4. External data URLs or DOIs
    external_urls = _find_external_data_urls(root)
    if external_urls:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_EXTERNAL_URLS",
            title="External data declarations",
            status="present",
            message=f"Found {len(external_urls)} external data reference(s): {', '.join(external_urls[:3])}",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_EXTERNAL_URLS",
            title="External data declarations",
            status="unknown",
            message="No external data URLs or DOIs detected",
            recommendation="If data is hosted externally, add URLs to data/README.md.",
            severity="info",
        ))

    # 5. Sample data presence
    sample_data = _find_sample_data(root)
    if sample_data:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_SAMPLE",
            title="Sample data",
            status="present",
            message=f"Found sample/example data: {', '.join(sample_data[:3])}",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_SAMPLE",
            title="Sample data",
            status="missing",
            message="No sample or example data found",
            recommendation="Consider adding sample data for testing.",
            severity="info",
        ))

    # 6. Large file check
    large_files = _find_large_files(root, threshold_mb=10)
    if large_files:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_LARGE_FILES",
            title="Large files",
            status="present",
            message=f"Found {len(large_files)} file(s) > 10MB: {', '.join(str(f) for f in large_files[:3])}",
            recommendation="Use .gitignore to exclude large data files. Consider Git LFS.",
            severity="warning",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_LARGE_FILES",
            title="Large files",
            status="present",
            message="No large files (>10MB) detected in repository",
            severity="info",
        ))

    # 7. .gitignore data patterns
    gitignore = root / ".gitignore"
    has_data_exclusions = False
    if gitignore.exists():
        content = gitignore.read_text(encoding="utf-8", errors="replace")
        data_patterns = ["data/", "*.csv", "*.h5", "*.hdf5", "*.parquet", "*.feather"]
        has_data_exclusions = any(p in content for p in data_patterns)

    if has_data_exclusions:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_GITIGNORE",
            title="Data .gitignore patterns",
            status="present",
            message=".gitignore excludes data-related patterns",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_GITIGNORE",
            title="Data .gitignore patterns",
            status="missing",
            message="No data-related patterns in .gitignore",
            recommendation="Add data patterns to .gitignore if large files are not tracked.",
            severity="info",
        ))

    # 8. Data license/usage restrictions
    has_data_license = False
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="replace").lower()
        license_keywords = ["data license", "data usage", "data restriction", "cc-by", "cc0"]
        has_data_license = any(kw in content for kw in license_keywords)

    if has_data_license:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_LICENSE",
            title="Data license/usage",
            status="present",
            message="README contains data license or usage information",
            severity="info",
        ))
    else:
        diagnostics.append(DataDiagnostic(
            check_id="DATA_LICENSE",
            title="Data license/usage",
            status="unknown",
            message="No data license or usage restrictions found",
            recommendation="Consider adding data usage terms if applicable.",
            severity="info",
        ))

    return diagnostics


def _find_external_data_urls(root: Path) -> list[str]:
    """Find external data URLs in README and data docs."""
    import re
    urls = []
    for f in [root / "README.md", root / "data" / "README.md"]:
        if not f.exists():
            continue
        content = f.read_text(encoding="utf-8", errors="replace")
        # Find URLs that look like data sources
        found = re.findall(r"https?://[^\s)>\]]+", content)
        for url in found:
            if any(kw in url.lower() for kw in ["data", "dataset", "download", "zenodo", "figshare", "dryad"]):
                urls.append(url)
    return urls[:5]


def _find_sample_data(root: Path) -> list[str]:
    """Find sample/example data files."""
    found = []
    for pattern in ["sample*", "example*", "demo*", "test_data*", "*.sample"]:
        for f in root.glob(f"data/{pattern}"):
            if f.is_file():
                found.append(f.name)
    return found[:5]


def _find_large_files(root: Path, threshold_mb: int = 10) -> list[Path]:
    """Find files larger than threshold."""
    threshold_bytes = threshold_mb * 1024 * 1024
    found = []
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    for f in root.rglob("*"):
        if f.is_file():
            parts = f.relative_to(root).parts
            if any(p in skip_dirs for p in parts):
                continue
            try:
                if f.stat().st_size > threshold_bytes:
                    found.append(f.relative_to(root))
            except OSError:
                pass
    return found[:10]
