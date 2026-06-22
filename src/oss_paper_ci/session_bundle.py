"""Session evidence bundle creation and verification.

Creates a ZIP bundle containing session manifest, reports, and logs.
Supports inspection and integrity verification.
"""

from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from oss_paper_ci import __version__


@dataclass
class SessionBundleInfo:
    """Information about a session evidence bundle."""

    path: str = ""
    file_count: int = 0
    total_size_bytes: int = 0
    session_id: str = ""
    session_name: str = ""
    status: str = ""
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "file_count": self.file_count,
            "total_size_bytes": self.total_size_bytes,
            "session_id": self.session_id,
            "session_name": self.session_name,
            "status": self.status,
            "files": self.files,
        }


@dataclass
class SessionBundleVerification:
    """Result of verifying a session evidence bundle."""

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


def create_session_bundle(
    session_dir: str,
    output_path: str,
) -> str:
    """Create a session evidence bundle.

    Args:
        session_dir: Path to the session directory.
        output_path: Path for the output ZIP file.

    Returns:
        Path to the created bundle.
    """
    from oss_paper_ci.session_store import compute_session_checksums, save_checksums

    session_path = Path(session_dir)

    # Save checksums first
    save_checksums(session_dir)

    # Create ZIP
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add session.json
        session_json = session_path / "session.json"
        if session_json.exists():
            zf.write(session_json, "session/session.json")

        # Add plan.json
        plan_json = session_path / "plan.json"
        if plan_json.exists():
            zf.write(plan_json, "session/plan.json")

        # Add command data (not stdout/stderr to keep bundle small)
        runs_dir = session_path / "runs"
        if runs_dir.exists():
            for cmd_dir in sorted(runs_dir.iterdir()):
                if cmd_dir.is_dir():
                    cmd_json = cmd_dir / "command.json"
                    if cmd_json.exists():
                        zf.write(cmd_json, f"session/runs/{cmd_dir.name}/command.json")

        # Add reports
        reports_dir = session_path / "reports"
        if reports_dir.exists():
            for f in sorted(reports_dir.iterdir()):
                if f.is_file():
                    zf.write(f, f"session/reports/{f.name}")

        # Add SHA256SUMS
        sha_file = session_path / "SHA256SUMS"
        if sha_file.exists():
            zf.write(sha_file, "session/SHA256SUMS")

        # Add bundle manifest
        manifest = {
            "schema_version": "0.1",
            "tool_version": __version__,
            "bundle_type": "session",
            "session_dir": str(session_path),
        }
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))

    return output_path


def inspect_session_bundle(bundle_path: str) -> SessionBundleInfo:
    """Inspect a session evidence bundle.

    Args:
        bundle_path: Path to the bundle ZIP.

    Returns:
        SessionBundleInfo with details about the bundle.
    """
    info = SessionBundleInfo(path=bundle_path)

    with zipfile.ZipFile(bundle_path, "r") as zf:
        info.file_count = len(zf.namelist())
        info.files = sorted(zf.namelist())
        info.total_size_bytes = sum(i.file_size for i in zf.infolist())

        # Read session.json if present
        if "session/session.json" in zf.namelist():
            try:
                data = json.loads(zf.read("session/session.json"))
                info.session_id = data.get("session_id", "")
                info.session_name = data.get("name", "")
                info.status = data.get("status", "")
            except Exception:
                pass

    return info


def verify_session_bundle(bundle_path: str) -> SessionBundleVerification:
    """Verify a session evidence bundle.

    Args:
        bundle_path: Path to the bundle ZIP.

    Returns:
        SessionBundleVerification with verification results.
    """
    result = SessionBundleVerification()

    if not Path(bundle_path).exists():
        result.error = f"Bundle not found: {bundle_path}"
        return result

    try:
        with zipfile.ZipFile(bundle_path, "r") as zf:
            result.file_count = len(zf.namelist())

            # Check for required files
            required = ["manifest.json", "session/session.json"]
            for f in required:
                if f not in zf.namelist():
                    result.warnings.append(f"Missing required file: {f}")

            # Verify manifest
            if "manifest.json" in zf.namelist():
                manifest = json.loads(zf.read("manifest.json"))
                if manifest.get("bundle_type") == "session":
                    result.schema_ok = True
                else:
                    result.warnings.append("Unknown bundle type")

            # Verify SHA256SUMS if present
            if "session/SHA256SUMS" in zf.namelist():
                sha_content = zf.read("session/SHA256SUMS").decode("utf-8")
                for line in sha_content.strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = line.strip().split("  ", 1)
                    if len(parts) != 2:
                        continue
                    expected_hash, file_path = parts
                    full_path = f"session/{file_path}"
                    if full_path in zf.namelist():
                        actual_hash = hashlib.sha256(zf.read(full_path)).hexdigest()
                        if actual_hash != expected_hash:
                            result.hashes_ok = False
                            result.hash_mismatches.append({
                                "file": file_path,
                                "expected": expected_hash,
                                "actual": actual_hash,
                            })

            result.valid = result.schema_ok and result.hashes_ok

    except Exception as e:
        result.error = f"Failed to verify bundle: {e}"

    return result


def format_bundle_inspect_markdown(info: SessionBundleInfo) -> str:
    """Format bundle inspection as markdown."""
    lines: list[str] = []
    lines.append("# Session Bundle Inspection")
    lines.append("")
    lines.append(f"**Path:** `{info.path}`")
    lines.append(f"**Session ID:** `{info.session_id}`")
    lines.append(f"**Session Name:** {info.session_name}")
    lines.append(f"**Status:** {info.status}")
    lines.append(f"**Files:** {info.file_count}")
    lines.append(f"**Size:** {info.total_size_bytes} bytes")
    lines.append("")
    lines.append("## Files")
    for f in info.files:
        lines.append(f"- `{f}`")
    lines.append("")
    return "\n".join(lines)


def format_bundle_verify_markdown(result: SessionBundleVerification) -> str:
    """Format bundle verification as markdown."""
    lines: list[str] = []
    lines.append("# Session Bundle Verification")
    lines.append("")
    lines.append(f"**Valid:** {'✅ Yes' if result.valid else '❌ No'}")
    lines.append(f"**Schema OK:** {'✅' if result.schema_ok else '❌'}")
    lines.append(f"**Hashes OK:** {'✅' if result.hashes_ok else '❌'}")
    lines.append(f"**Files:** {result.file_count}")
    lines.append("")

    if result.hash_mismatches:
        lines.append("## Hash Mismatches")
        for m in result.hash_mismatches:
            lines.append(f"- `{m['file']}`: expected `{m['expected'][:16]}...`, got `{m['actual'][:16]}...`")
        lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        for w in result.warnings:
            lines.append(f"- ⚠️ {w}")
        lines.append("")

    return "\n".join(lines)
