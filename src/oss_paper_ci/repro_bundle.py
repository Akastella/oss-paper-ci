"""Reproduction evidence bundle creation and verification.

Creates a ZIP bundle containing all reproduction evidence: run manifest,
reports (MD/JSON/HTML), artifact hashes, and logs.  Supports inspection
and integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import os
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__


@dataclass
class BundleInfo:
    """Information about a reproduction evidence bundle."""

    path: str = ""
    file_count: int = 0
    total_size_bytes: int = 0
    schema_version: str = ""
    tool_version: str = ""
    overall_status: str = ""
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "file_count": self.file_count,
            "total_size_bytes": self.total_size_bytes,
            "schema_version": self.schema_version,
            "tool_version": self.tool_version,
            "overall_status": self.overall_status,
            "files": self.files,
        }


@dataclass
class BundleVerification:
    """Result of verifying a reproduction evidence bundle."""

    valid: bool = False
    schema_ok: bool = False
    hashes_ok: bool = True
    hash_mismatches: list[dict[str, str]] = field(default_factory=list)
    file_count: int = 0
    error: str = ""
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "schema_ok": self.schema_ok,
            "hashes_ok": self.hashes_ok,
            "hash_mismatches": self.hash_mismatches,
            "file_count": self.file_count,
            "error": self.error,
            "warnings": self.warnings,
        }


def create_bundle(
    run_dir: str,
    output_path: str,
) -> str:
    """Create a reproduction evidence bundle from a run directory.

    Args:
        run_dir: Path to the run directory (containing run-manifest.json).
        output_path: Path for the output ZIP file.

    Returns:
        Path to the created bundle.
    """
    run_path = Path(run_dir)
    if not run_path.exists():
        raise FileNotFoundError(f"Run directory does not exist: {run_dir}")

    # Collect files to include
    files_to_bundle: list[tuple[str, Path]] = []
    _collect_files(run_path, files_to_bundle)

    # Build bundle manifest
    bundle_manifest = {
        "schema_version": "1.0",
        "type": "oss-paper-ci-reproduction-bundle",
        "tool_version": __version__,
        "files": [],
    }

    # Create ZIP
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    hashes: dict[str, str] = {}
    with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as zf:
        for arc_name, file_path in files_to_bundle:
            file_hash = _hash_file(file_path)
            hashes[arc_name] = file_hash
            zf.write(str(file_path), arc_name)
            bundle_manifest["files"].append({
                "path": arc_name,
                "sha256": file_hash,
                "size": file_path.stat().st_size,
            })

        # Add SHA256SUMS
        sha_content = "\n".join(
            f"{hash}  {path}" for path, hash in sorted(hashes.items())
        )
        zf.writestr("SHA256SUMS", sha_content)

        # Add bundle manifest
        zf.writestr(
            "bundle-manifest.json",
            json.dumps(bundle_manifest, indent=2, ensure_ascii=False),
        )

    return str(out)


def inspect_bundle(bundle_path: str) -> BundleInfo:
    """Inspect a reproduction evidence bundle.

    Args:
        bundle_path: Path to the bundle ZIP file.

    Returns:
        BundleInfo with bundle metadata.
    """
    info = BundleInfo(path=bundle_path)

    if not Path(bundle_path).exists():
        return info

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            info.file_count = len(zf.namelist())
            info.files = zf.namelist()
            info.total_size_bytes = sum(e.file_size for e in zf.infolist())

            # Read bundle manifest if present
            if "bundle-manifest.json" in zf.namelist():
                manifest = json.loads(zf.read("bundle-manifest.json"))
                info.schema_version = manifest.get("schema_version", "")
                info.tool_version = manifest.get("tool_version", "")

            # Read run manifest if present
            if "run-manifest.json" in zf.namelist():
                run_manifest = json.loads(zf.read("run-manifest.json"))
                info.overall_status = run_manifest.get("overall_status", "unknown")
    except Exception:
        pass

    return info


def verify_bundle(bundle_path: str) -> BundleVerification:
    """Verify the integrity of a reproduction evidence bundle.

    Args:
        bundle_path: Path to the bundle ZIP file.

    Returns:
        BundleVerification with verification results.
    """
    result = BundleVerification()

    if not Path(bundle_path).exists():
        result.error = f"Bundle file does not exist: {bundle_path}"
        return result

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            # Check ZIP integrity
            bad = zf.testzip()
            if bad:
                result.error = f"Corrupt file in bundle: {bad}"
                return result

            names = zf.namelist()
            result.file_count = len(names)

            # Check required files
            if "bundle-manifest.json" not in names:
                result.warnings.append("Missing bundle-manifest.json")
            else:
                manifest = json.loads(zf.read("bundle-manifest.json"))
                result.schema_ok = manifest.get("type") == "oss-paper-ci-reproduction-bundle"

            if "SHA256SUMS" not in names:
                result.warnings.append("Missing SHA256SUMS")
            else:
                # Verify hashes
                sha_content = zf.read("SHA256SUMS").decode("utf-8")
                expected_hashes = _parse_sha256sums(sha_content)
                for arc_name, expected_hash in expected_hashes.items():
                    if arc_name in ("SHA256SUMS", "bundle-manifest.json"):
                        continue
                    if arc_name not in names:
                        result.hash_mismatches.append({
                            "file": arc_name,
                            "expected": expected_hash,
                            "actual": "missing",
                        })
                        continue
                    actual_data = zf.read(arc_name)
                    actual_hash = hashlib.sha256(actual_data).hexdigest()
                    if actual_hash != expected_hash:
                        result.hash_mismatches.append({
                            "file": arc_name,
                            "expected": expected_hash,
                            "actual": actual_hash,
                        })

                result.hashes_ok = len(result.hash_mismatches) == 0

            result.valid = result.schema_ok and result.hashes_ok

    except zipfile.BadZipFile:
        result.error = "Not a valid ZIP file"
    except Exception as exc:
        result.error = f"Verification failed: {exc}"

    return result


def _collect_files(
    directory: Path,
    files: list[tuple[str, Path]],
    prefix: str = "",
) -> None:
    """Recursively collect files for bundling."""
    skip = {".git", "__pycache__", "venv", ".venv", "node_modules"}
    for item in sorted(directory.iterdir()):
        if item.name in skip:
            continue
        arc_name = f"{prefix}{item.name}" if prefix else item.name
        if item.is_file():
            files.append((arc_name, item))
        elif item.is_dir():
            _collect_files(item, files, prefix=f"{arc_name}/")


def _hash_file(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(8192)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _parse_sha256sums(content: str) -> dict[str, str]:
    """Parse a SHA256SUMS file into a dict."""
    result: dict[str, str] = {}
    for line in content.strip().splitlines():
        parts = line.split("  ", 1)
        if len(parts) == 2:
            result[parts[1]] = parts[0]
    return result


def format_bundle_inspect_markdown(info: BundleInfo) -> str:
    """Format bundle inspection as Markdown."""
    lines = [
        "# Reproduction Evidence Bundle Inspection",
        "",
        f"**File:** `{info.path}`",
        f"**Files:** {info.file_count}",
        f"**Size:** {info.total_size_bytes:,} bytes",
        f"**Schema:** {info.schema_version}",
        f"**Tool:** {info.tool_version}",
        f"**Status:** {info.overall_status}",
        "",
    ]

    if info.files:
        lines.append("## Contents")
        lines.append("")
        for f in info.files:
            lines.append(f"- `{f}`")
        lines.append("")

    return "\n".join(lines)


def format_bundle_verify_markdown(result: BundleVerification) -> str:
    """Format bundle verification as Markdown."""
    lines = [
        "# Reproduction Evidence Bundle Verification",
        "",
        f"**Valid:** {'✅ Yes' if result.valid else '❌ No'}",
        f"**Schema OK:** {'✅' if result.schema_ok else '❌'}",
        f"**Hashes OK:** {'✅' if result.hashes_ok else '❌'}",
        f"**Files:** {result.file_count}",
        "",
    ]

    if result.hash_mismatches:
        lines.append("## Hash Mismatches")
        lines.append("")
        lines.append("| File | Expected | Actual |")
        lines.append("|------|----------|--------|")
        for m in result.hash_mismatches:
            lines.append(
                f"| `{m['file']}` | `{m['expected'][:16]}...` | `{m['actual'][:16]}...` |"
            )
        lines.append("")

    if result.warnings:
        lines.append("## ⚠️ Warnings")
        lines.append("")
        for w in result.warnings:
            lines.append(f"- {w}")
        lines.append("")

    if result.error:
        lines.append(f"**Error:** {result.error}")
        lines.append("")

    return "\n".join(lines)
