"""Evidence bundle: create, inspect, and verify shareable evidence packages."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import __version__
from .evidence import EvidenceReport, build_evidence_report, format_evidence_html, format_evidence_markdown


# ── Forbidden paths in bundles ──────────────────────────────────────────────

BUNDLE_FORBIDDEN = {
    ".git", "venv", ".venv", "node_modules", "__pycache__",
    ".pytest_cache", ".mypy_cache", "dist", "build", "site",
    ".oss-paper-ci-repro", ".oss-paper-ci-cache",
    ".oss-paper-ci-capsule-staging", "release-artifacts",
}


# ── Data models ─────────────────────────────────────────────────────────────


@dataclass
class BundleManifest:
    """Manifest for an evidence bundle."""

    schema_version: str = "0.1"
    tool: str = "oss-paper-ci"
    tool_version: str = __version__
    profile: str = "reviewer"
    included_sections: list[str] = field(default_factory=list)
    files: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool": self.tool,
            "tool_version": self.tool_version,
            "profile": self.profile,
            "included_sections": self.included_sections,
            "files": self.files,
            "limitations": self.limitations,
        }


@dataclass
class BundleVerification:
    """Result of bundle verification."""

    ok: bool = True
    verified: list[str] = field(default_factory=list)
    failed: list[dict[str, str]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "verified": self.verified,
            "failed": self.failed,
            "warnings": self.warnings,
        }


def _compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ── Bundle creation ─────────────────────────────────────────────────────────


def create_evidence_bundle(
    repo_path: str | Path,
    output_path: str | Path,
    profile: str = "reviewer",
    include_sections: list[str] | None = None,
) -> dict[str, Any]:
    """Create an evidence bundle ZIP.

    Args:
        repo_path: Path to the repository.
        output_path: Path for the output ZIP file.
        profile: Report profile (reviewer, author, maintainer).
        include_sections: Sections to include. None = all defaults.

    Returns:
        Dict with status info.
    """
    root = Path(repo_path).resolve()
    out = Path(output_path).resolve()

    # Build the evidence report
    report = build_evidence_report(root, profile=profile, include_sections=include_sections)

    # Create temp directory for bundle contents
    with tempfile.TemporaryDirectory() as tmpdir:
        bundle_dir = Path(tmpdir) / "evidence-bundle"
        bundle_dir.mkdir()

        # Write reports
        json_path = bundle_dir / "evidence-report.json"
        json_path.write_text(
            json.dumps(report.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        md_path = bundle_dir / "evidence-report.md"
        md_path.write_text(format_evidence_markdown(report), encoding="utf-8")

        html_path = bundle_dir / "evidence-report.html"
        html_path.write_text(format_evidence_html(report), encoding="utf-8")

        # Write limitations
        lim_path = bundle_dir / "limitations.md"
        lim_lines = ["# Limitations", ""]
        for lim in report.limitations:
            lim_lines.append(f"- {lim}")
        lim_path.write_text("\n".join(lim_lines), encoding="utf-8")

        # Build manifest
        manifest = BundleManifest(
            profile=profile,
            included_sections=list(report.sections.keys()),
            limitations=[
                "This bundle is locally generated; not a signed attestation.",
                "Does not contain user data files or experiment artifacts.",
                "All paths are relative to the repository root.",
            ],
        )

        # Compute hashes for all bundle files
        for f in sorted(bundle_dir.iterdir()):
            if f.is_file():
                manifest.files.append({
                    "path": f.name,
                    "sha256": _compute_sha256(f),
                    "size_bytes": f.stat().st_size,
                })

        # Write manifest
        manifest_path = bundle_dir / "manifest.json"
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Write SHA256SUMS
        sums_lines = []
        for entry in manifest.files:
            sums_lines.append(f"{entry['sha256']}  {entry['path']}")
        sums_path = bundle_dir / "SHA256SUMS"
        sums_path.write_text("\n".join(sums_lines) + "\n", encoding="utf-8")

        # Update manifest with SHA256SUMS itself
        manifest.files.append({
            "path": "SHA256SUMS",
            "sha256": _compute_sha256(sums_path),
            "size_bytes": sums_path.stat().st_size,
        })
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        # Create ZIP with single root directory
        out.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in sorted(bundle_dir.iterdir()):
                if f.is_file():
                    zf.write(f, f"evidence-bundle/{f.name}")

    return {
        "ok": True,
        "output": str(out),
        "profile": profile,
        "files_count": len(manifest.files),
    }


# ── Bundle inspection ───────────────────────────────────────────────────────


def inspect_evidence_bundle(bundle_path: str | Path) -> dict[str, Any]:
    """Inspect an evidence bundle ZIP.

    Returns:
        Dict with bundle metadata.
    """
    bpath = Path(bundle_path).resolve()
    if not bpath.exists():
        return {"error": f"Bundle not found: {bpath}"}

    result: dict[str, Any] = {
        "path": str(bpath),
        "ok": True,
        "files": [],
    }

    try:
        with zipfile.ZipFile(bpath, "r") as zf:
            names = zf.namelist()
            result["total_files"] = len(names)

            # Check for forbidden content
            for name in names:
                for forbidden in BUNDLE_FORBIDDEN:
                    if forbidden in name:
                        result["warnings"] = result.get("warnings", [])
                        result["warnings"].append(f"Forbidden content: {name}")

            # Read manifest if present
            manifest_name = None
            for name in names:
                if name.endswith("manifest.json"):
                    manifest_name = name
                    break

            if manifest_name:
                manifest_data = json.loads(zf.read(manifest_name))
                result["manifest"] = manifest_data
                result["profile"] = manifest_data.get("profile", "unknown")
                result["tool_version"] = manifest_data.get("tool_version", "unknown")
                result["included_sections"] = manifest_data.get("included_sections", [])

            # List files
            for name in names:
                info = zf.getinfo(name)
                result["files"].append({
                    "path": name,
                    "size_bytes": info.file_size,
                })

            # Read evidence report JSON summary if present
            report_name = None
            for name in names:
                if name.endswith("evidence-report.json"):
                    report_name = name
                    break

            if report_name:
                report_data = json.loads(zf.read(report_name))
                result["summary"] = report_data.get("summary", {})

    except Exception as e:
        result["ok"] = False
        result["error"] = str(e)

    return result


# ── Bundle verification ─────────────────────────────────────────────────────


def verify_evidence_bundle(bundle_path: str | Path) -> BundleVerification:
    """Verify an evidence bundle's integrity.

    Returns:
        BundleVerification with results.
    """
    bpath = Path(bundle_path).resolve()
    vr = BundleVerification()

    if not bpath.exists():
        vr.ok = False
        vr.warnings.append(f"Bundle not found: {bpath}")
        return vr

    try:
        with zipfile.ZipFile(bpath, "r") as zf:
            names = zf.namelist()

            # Find SHA256SUMS
            sums_name = None
            for name in names:
                if name.endswith("SHA256SUMS"):
                    sums_name = name
                    break

            if not sums_name:
                vr.ok = False
                vr.warnings.append("No SHA256SUMS file found in bundle.")
                return vr

            # Parse SHA256SUMS
            sums_content = zf.read(sums_name).decode("utf-8")
            expected: dict[str, str] = {}
            for line in sums_content.strip().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    expected[parts[1].strip()] = parts[0].strip()

            # Verify each file
            for filename, expected_hash in expected.items():
                # Find the file in the ZIP (may have bundle prefix)
                zip_path = None
                for name in names:
                    if name.endswith(filename):
                        zip_path = name
                        break

                if zip_path is None:
                    vr.ok = False
                    vr.failed.append({
                        "file": filename,
                        "reason": "missing",
                    })
                    continue

                # Compute hash
                file_data = zf.read(zip_path)
                actual_hash = hashlib.sha256(file_data).hexdigest()

                if actual_hash == expected_hash:
                    vr.verified.append(filename)
                else:
                    vr.ok = False
                    vr.failed.append({
                        "file": filename,
                        "expected": expected_hash[:16] + "...",
                        "actual": actual_hash[:16] + "...",
                    })

            # Check for forbidden content
            for name in names:
                for forbidden in BUNDLE_FORBIDDEN:
                    if forbidden in name:
                        vr.warnings.append(f"Forbidden content found: {name}")

    except Exception as e:
        vr.ok = False
        vr.warnings.append(f"Verification error: {e}")

    return vr


# ── Formatters ──────────────────────────────────────────────────────────────


def format_bundle_inspect_markdown(info: dict[str, Any]) -> str:
    """Format bundle inspection as Markdown."""
    lines = [
        "# Evidence Bundle Inspection",
        "",
    ]

    if "error" in info:
        lines.append(f"**Error:** {info['error']}")
        return "\n".join(lines)

    lines.append(f"- **Profile:** {info.get('profile', 'unknown')}")
    lines.append(f"- **Tool version:** {info.get('tool_version', 'unknown')}")
    lines.append(f"- **Total files:** {info.get('total_files', 0)}")
    lines.append("")

    sections = info.get("included_sections", [])
    if sections:
        lines.append("## Included Sections")
        lines.append("")
        for s in sections:
            lines.append(f"- {s}")
        lines.append("")

    summary = info.get("summary", {})
    if summary:
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Score:** {summary.get('readiness_score', 'N/A')}/100")
        lines.append(f"- **Status:** {summary.get('status', 'unknown')}")
        lines.append(f"- **Risk Level:** {summary.get('risk_level', 'unknown')}")
        lines.append("")

    files = info.get("files", [])
    if files:
        lines.append("## Files")
        lines.append("")
        lines.append("| Path | Size |")
        lines.append("|------|------|")
        for f in files:
            lines.append(f"| `{f['path']}` | {f['size_bytes']} bytes |")
        lines.append("")

    warnings = info.get("warnings", [])
    if warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)


def format_bundle_verify_markdown(vr: BundleVerification) -> str:
    """Format bundle verification as Markdown."""
    lines = [
        "# Evidence Bundle Verification",
        "",
        f"**Status:** {'PASS' if vr.ok else 'FAIL'}",
        "",
    ]

    if vr.verified:
        lines.append("## Verified")
        lines.append("")
        for f in vr.verified:
            lines.append(f"- ✅ `{f}`")
        lines.append("")

    if vr.failed:
        lines.append("## Failed")
        lines.append("")
        for f in vr.failed:
            reason = f.get("reason", "hash mismatch")
            lines.append(f"- ❌ `{f['file']}`: {reason}")
        lines.append("")

    if vr.warnings:
        lines.append("## Warnings")
        lines.append("")
        for w in vr.warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)
