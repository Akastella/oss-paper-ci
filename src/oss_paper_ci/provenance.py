"""Provenance manifest module."""

from __future__ import annotations

import hashlib
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from . import __version__


@dataclass
class ProvenanceManifest:
    """Local provenance manifest."""

    schema_version: str = "0.1"
    tool: str = "oss-paper-ci"
    tool_version: str = __version__
    source: dict[str, Any] = field(default_factory=dict)
    build: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "tool": self.tool,
            "tool_version": self.tool_version,
            "source": self.source,
            "build": self.build,
            "artifacts": self.artifacts,
            "limitations": self.limitations,
        }


def _get_git_info(repo_path: Path) -> dict[str, Any]:
    """Get git commit and dirty status."""
    info: dict[str, Any] = {"commit": None, "dirty": None}
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info["commit"] = result.stdout.strip()

        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            info["dirty"] = bool(result.stdout.strip())
    except Exception:
        pass
    return info


def _compute_sha256(path: Path) -> str:
    """Compute SHA256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def build_provenance(
    repo_path: str | Path,
    artifact_paths: list[str | Path] | None = None,
    include_timestamp: bool = False,
) -> ProvenanceManifest:
    """Build a provenance manifest."""
    root = Path(repo_path).resolve()
    manifest = ProvenanceManifest(
        source={
            "repo": root.name,
            **_get_git_info(root),
        },
        build={
            "python_version": platform.python_version(),
            "platform": f"{platform.system()} {platform.machine()}",
        },
        limitations=[
            "Local provenance manifest; not a signed attestation.",
            "Not SLSA compliant.",
            "Does not verify third-party dependency integrity.",
            "Source repository path is relative to build directory.",
        ],
    )

    if include_timestamp:
        manifest.build["timestamp_utc"] = datetime.now(timezone.utc).isoformat()

    # Process artifacts
    if artifact_paths:
        for ap in artifact_paths:
            p = Path(ap).resolve()
            if p.exists() and p.is_file():
                manifest.artifacts.append({
                    "path": p.name,  # Use filename only, no absolute paths
                    "sha256": _compute_sha256(p),
                    "size_bytes": p.stat().st_size,
                })

    return manifest


def verify_artifacts(
    artifact_dir: str | Path,
    checksums_file: str | Path | None = None,
) -> dict[str, Any]:
    """Verify artifacts against SHA256SUMS."""
    art_dir = Path(artifact_dir).resolve()
    result: dict[str, Any] = {
        "ok": True,
        "verified": [],
        "failed": [],
        "missing": [],
        "warnings": [],
    }

    # Find checksums file
    sums_path = None
    if checksums_file:
        sums_path = Path(checksums_file).resolve()
    else:
        candidates = [
            art_dir / "SHA256SUMS",
            art_dir / "SHA256SUMS.txt",
            art_dir.parent / "SHA256SUMS",
            art_dir.parent / "SHA256SUMS.txt",
        ]
        for c in candidates:
            if c.exists():
                sums_path = c
                break

    if not sums_path or not sums_path.exists():
        result["ok"] = False
        result["warnings"].append("No SHA256SUMS file found.")
        return result

    # Parse checksums
    expected: dict[str, str] = {}
    try:
        content = sums_path.read_text(encoding="utf-8")
        for line in content.strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split(None, 1)
            if len(parts) == 2:
                expected[parts[1].strip()] = parts[0].strip()
    except Exception as e:
        result["ok"] = False
        result["warnings"].append(f"Failed to parse SHA256SUMS: {e}")
        return result

    # Verify each artifact
    for filename, expected_hash in expected.items():
        artifact_path = art_dir / filename
        if not artifact_path.exists():
            result["missing"].append(filename)
            result["ok"] = False
            continue

        actual_hash = _compute_sha256(artifact_path)
        if actual_hash == expected_hash:
            result["verified"].append(filename)
        else:
            result["failed"].append({
                "file": filename,
                "expected": expected_hash,
                "actual": actual_hash,
            })
            result["ok"] = False

    return result


def format_provenance_markdown(manifest: ProvenanceManifest) -> str:
    """Format provenance manifest as Markdown."""
    lines = [
        "# Provenance Manifest",
        "",
        f"**Tool:** {manifest.tool} v{manifest.tool_version}",
        f"**Schema:** {manifest.schema_version}",
        "",
        "## Source",
        "",
        f"- **Repository:** {manifest.source.get('repo', 'unknown')}",
        f"- **Commit:** {manifest.source.get('commit', 'unknown')}",
        f"- **Dirty:** {manifest.source.get('dirty', 'unknown')}",
        "",
        "## Build",
        "",
        f"- **Python:** {manifest.build.get('python_version', 'unknown')}",
        f"- **Platform:** {manifest.build.get('platform', 'unknown')}",
    ]

    if manifest.build.get("timestamp_utc"):
        lines.append(f"- **Timestamp (UTC):** {manifest.build['timestamp_utc']}")
    lines.append("")

    if manifest.artifacts:
        lines.append("## Artifacts")
        lines.append("")
        lines.append("| File | SHA256 | Size |")
        lines.append("|------|--------|------|")
        for a in manifest.artifacts:
            lines.append(f"| `{a['path']}` | `{a['sha256'][:16]}...` | {a['size_bytes']} bytes |")
        lines.append("")

    lines.append("## Limitations")
    lines.append("")
    for lim in manifest.limitations:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)


def format_verification_markdown(result: dict[str, Any]) -> str:
    """Format verification result as Markdown."""
    lines = [
        "# Artifact Verification Report",
        "",
        f"**Status:** {'PASS' if result['ok'] else 'FAIL'}",
        "",
    ]

    if result["verified"]:
        lines.append("## Verified")
        lines.append("")
        for f in result["verified"]:
            lines.append(f"- ✅ `{f}`")
        lines.append("")

    if result["failed"]:
        lines.append("## Failed")
        lines.append("")
        for f in result["failed"]:
            lines.append(f"- ❌ `{f['file']}` (expected `{f['expected'][:16]}...`, got `{f['actual'][:16]}...`)")
        lines.append("")

    if result["missing"]:
        lines.append("## Missing")
        lines.append("")
        for f in result["missing"]:
            lines.append(f"- ⚠️ `{f}`")
        lines.append("")

    if result["warnings"]:
        lines.append("## Warnings")
        lines.append("")
        for w in result["warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines)
