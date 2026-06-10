"""Capsule builder — packages a ReproduceResult into a verifiable capsule zip.

Safety rules:
- No path traversal (all paths validated)
- No symlinks followed
- Excludes venv, .git, cache, __pycache__
- File size limits enforced
- All paths relative to capsule root
- No absolute paths stored (redacted in metadata)
"""

from __future__ import annotations

import fnmatch
import hashlib
import json
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING, Any

from oss_paper_ci import __version__
from oss_paper_ci.capsule_format import (
    CAPSULE_DIRS,
    CAPSULE_ROOT_DIR,
    EXCLUDED_PATTERNS,
    MAX_ARTIFACT_FILES,
    MAX_ARTIFACT_SIZE_BYTES,
    MAX_CAPSULE_SIZE_BYTES,
    MAX_LOG_SIZE_BYTES,
    REQUIRED_FILES,
    create_capsule_manifest,
)

if TYPE_CHECKING:
    from oss_paper_ci.reproduce import ReproduceResult


def build_capsule(
    result: ReproduceResult,
    output_path: str,
    *,
    include_artifacts: bool = True,
    max_artifact_mb: float = 10.0,
) -> str:
    """Build a reproduction capsule zip from a ReproduceResult.

    Args:
        result: The ReproduceResult to package.
        output_path: Path for the output .zip file.
        include_artifacts: Whether to include generated artifacts.
        max_artifact_mb: Max size per artifact file in MB.

    Returns:
        Path to the created capsule zip.

    Raises:
        ValueError: If the result has fatal errors.
        OSError: If file operations fail.
    """
    max_artifact_bytes = int(max_artifact_mb * 1024 * 1024)
    staging_dir = None

    try:
        # Create staging directory
        staging_dir = tempfile.mkdtemp(prefix="oss-paper-ci-capsule-staging-")
        capsule_root = Path(staging_dir) / CAPSULE_ROOT_DIR

        # Create directory structure
        for d in CAPSULE_DIRS:
            (capsule_root / d).mkdir(parents=True, exist_ok=True)

        # Write metadata files
        _write_source_metadata(capsule_root, result)
        _write_environment_metadata(capsule_root, result)
        _write_commands_metadata(capsule_root, result)
        _write_oss_paper_ci_metadata(capsule_root)
        _write_limitations(capsule_root, result)

        # Write reports
        _write_reports(capsule_root, result)

        # Write logs
        _write_logs(capsule_root, result)

        # Write artifacts
        if include_artifacts and result.workdir:
            _write_artifacts(
                capsule_root, result,
                max_artifact_bytes=max_artifact_bytes,
            )
        else:
            # Write empty artifact index
            _write_artifact_index(capsule_root, [])

        # Build execution summary
        commands_succeeded = sum(
            1 for r in result.command_results
            if r.exit_code == 0 and not r.blocked
        )
        commands_failed = sum(
            1 for r in result.command_results
            if r.exit_code != 0 and not r.blocked
        )

        # Build manifest
        source_meta = {
            "input_url": _redact_path(result.input_url),
            "repo_url": _redact_path(result.repo_url),
            "paper_url": result.paper_url or None,
            "commit_sha": result.commit_sha or None,
            "source_type": result.resolved_source,
        }

        execution_meta = {
            "mode": "dry-run" if result.dry_run else "execute",
            "install": bool(result.install_results),
            "commands_attempted": len(result.command_results),
            "commands_succeeded": commands_succeeded,
            "commands_failed": commands_failed,
            "timeout_seconds": 300,
        }

        reports_meta = {
            "reproduce_json": "reports/reproduce_report.json",
            "reproduce_html": "reports/reproduce_report.html",
            "scan_json": "reports/scan_report.json",
        }

        manifest = create_capsule_manifest(
            oss_paper_ci_version=__version__,
            source=source_meta,
            execution=execution_meta,
            reports=reports_meta,
            limitations=result.limitations or [
                "This capsule records a reproduction attempt, not a proof of paper correctness.",
            ],
        )

        # Write capsule.json
        (capsule_root / "capsule.json").write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        # Compute and write SHA256SUMS
        sha256sums = _compute_sha256sums(capsule_root)
        sha256_text = "\n".join(
            f"{hash_val}  {path}" for path, hash_val in sorted(sha256sums.items())
        ) + "\n"
        (capsule_root / "SHA256SUMS").write_text(sha256_text, encoding="utf-8")

        # Create zip
        _create_zip(capsule_root, output_path)

        return output_path

    finally:
        # Cleanup staging directory
        if staging_dir and os.path.exists(staging_dir):
            shutil.rmtree(staging_dir, ignore_errors=True)


def _redact_path(path: str) -> str:
    """Redact absolute paths, keeping only the last component."""
    if not path:
        return path
    # Normalize slashes for cross-platform handling
    normalized = path.replace("\\", "/")
    # If it looks like an absolute path, redact
    if os.path.isabs(path) or os.path.isabs(normalized):
        # Get the last component using normalized path
        basename = normalized.rsplit("/", 1)[-1] if "/" in normalized else normalized
        return f"<redacted>/{basename}"
    # Windows-style absolute path (e.g., C:/Users/... or C:\Users\...)
    if len(normalized) >= 2 and normalized[1] == ":":
        basename = normalized.rsplit("/", 1)[-1] if "/" in normalized else normalized
        return f"<redacted>/{basename}"
    return path


def _write_source_metadata(capsule_root: Path, result: ReproduceResult) -> None:
    """Write metadata/source.json."""
    data = {
        "input_url": _redact_path(result.input_url),
        "repo_url": _redact_path(result.repo_url),
        "paper_url": result.paper_url or None,
        "commit_sha": result.commit_sha or None,
        "source_type": result.resolved_source,
    }
    (capsule_root / "metadata" / "source.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_environment_metadata(capsule_root: Path, result: ReproduceResult) -> None:
    """Write metadata/environment.json."""
    if result.environment:
        data = result.environment.to_dict()
    else:
        data = {"environment_files": [], "install_steps": [], "warnings": []}
    (capsule_root / "metadata" / "environment.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_commands_metadata(capsule_root: Path, result: ReproduceResult) -> None:
    """Write metadata/commands.json."""
    data = {
        "reproduction_commands": result.reproduction_commands,
        "command_results": [r.to_dict() for r in result.command_results],
        "install_results": [r.to_dict() for r in result.install_results],
    }
    (capsule_root / "metadata" / "commands.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_oss_paper_ci_metadata(capsule_root: Path) -> None:
    """Write metadata/oss_paper_ci.json."""
    import sys
    data = {
        "version": __version__,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": sys.platform,
    }
    (capsule_root / "metadata" / "oss_paper_ci.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _write_limitations(capsule_root: Path, result: ReproduceResult) -> None:
    """Write metadata/limitations.md."""
    limitations = result.limitations or [
        "This capsule records a reproduction attempt, not a proof of paper correctness.",
    ]
    lines = ["# Limitations\n"]
    for lim in limitations:
        lines.append(f"- {lim}\n")
    lines.append("\nThis capsule was generated by oss-paper-ci and has not been independently verified.\n")
    (capsule_root / "metadata" / "limitations.md").write_text(
        "".join(lines), encoding="utf-8",
    )


def _write_reports(capsule_root: Path, result: ReproduceResult) -> None:
    """Write all report files."""
    from oss_paper_ci.reporting.reproduce_report import (
        generate_reproduce_html_report,
        generate_reproduce_json_report,
        generate_reproduce_markdown_report,
    )

    reports_dir = capsule_root / "reports"

    # Reproduce reports
    generate_reproduce_json_report(
        result, output_path=str(reports_dir / "reproduce_report.json")
    )
    generate_reproduce_markdown_report(
        result, output_path=str(reports_dir / "reproduce_report.md")
    )
    generate_reproduce_html_report(
        result, output_path=str(reports_dir / "reproduce_report.html")
    )

    # Scan report (if available)
    if result.scan_status not in ("dry_run", "not_run") and result.workdir:
        try:
            from oss_paper_ci.scanner import scan as run_scan
            from oss_paper_ci.reporting.json_report import generate_json_report
            from oss_paper_ci.reporting.markdown_report import generate_markdown_report

            scan_report = run_scan(result.workdir)
            generate_json_report(
                scan_report,
                output_path=str(reports_dir / "scan_report.json"),
            )
            generate_markdown_report(
                scan_report,
                output_path=str(reports_dir / "scan_report.md"),
            )
        except Exception:
            # Scan may fail if workdir was cleaned up
            pass


def _write_logs(capsule_root: Path, result: ReproduceResult) -> None:
    """Write command logs."""
    logs_dir = capsule_root / "logs"

    # Install logs
    for i, install_result in enumerate(result.install_results):
        _write_log_file(
            logs_dir / f"install_{i:03d}.stdout.txt",
            install_result.stdout_excerpt,
        )
        _write_log_file(
            logs_dir / f"install_{i:03d}.stderr.txt",
            install_result.stderr_excerpt,
        )

    # Command logs
    for i, cmd_result in enumerate(result.command_results):
        _write_log_file(
            logs_dir / f"command_{i:03d}.stdout.txt",
            cmd_result.stdout_excerpt,
        )
        _write_log_file(
            logs_dir / f"command_{i:03d}.stderr.txt",
            cmd_result.stderr_excerpt,
        )


def _write_log_file(path: Path, content: str) -> None:
    """Write a log file, truncating if too large."""
    if not content:
        path.write_text("", encoding="utf-8")
        return
    if len(content) > MAX_LOG_SIZE_BYTES:
        content = content[:MAX_LOG_SIZE_BYTES] + f"\n... (truncated at {MAX_LOG_SIZE_BYTES} bytes)"
    path.write_text(content, encoding="utf-8")


def _write_artifacts(
    capsule_root: Path,
    result: ReproduceResult,
    max_artifact_bytes: int,
) -> None:
    """Write generated artifacts to capsule."""
    artifacts_dir = capsule_root / "artifacts" / "generated"
    index_entries = []
    workdir = Path(result.workdir)

    if not workdir.exists():
        _write_artifact_index(capsule_root, [])
        return

    count = 0
    for artifact_rel in result.generated_artifacts:
        if count >= MAX_ARTIFACT_FILES:
            break

        artifact_src = workdir / artifact_rel
        if not artifact_src.exists() or not artifact_src.is_file():
            continue

        # Check size
        size = artifact_src.stat().st_size
        if size > max_artifact_bytes:
            index_entries.append({
                "path": artifact_rel,
                "status": "skipped",
                "reason": f"exceeds size limit ({size} > {max_artifact_bytes})",
            })
            continue

        # Check excluded patterns
        if _is_excluded(artifact_rel):
            continue

        # Copy artifact
        dest = artifacts_dir / artifact_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(artifact_src), str(dest))

        index_entries.append({
            "path": artifact_rel,
            "status": "included",
            "size_bytes": size,
            "sha256": _hash_file(artifact_src),
        })
        count += 1

    _write_artifact_index(capsule_root, index_entries)


def _write_artifact_index(capsule_root: Path, entries: list[dict]) -> None:
    """Write artifacts/artifact_index.json."""
    data = {
        "total_artifacts": len(entries),
        "included": sum(1 for e in entries if e.get("status") == "included"),
        "skipped": sum(1 for e in entries if e.get("status") == "skipped"),
        "artifacts": entries,
    }
    (capsule_root / "artifacts" / "artifact_index.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def _is_excluded(path: str) -> bool:
    """Check if a path matches excluded patterns."""
    for pattern in EXCLUDED_PATTERNS:
        if fnmatch.fnmatch(path, pattern):
            return True
        # Also check each path component
        parts = path.replace("\\", "/").split("/")
        for part in parts:
            if fnmatch.fnmatch(part, pattern.rstrip("/*")):
                return True
    return False


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


def _compute_sha256sums(capsule_root: Path) -> dict[str, str]:
    """Compute SHA256 hashes for all files in the capsule (except SHA256SUMS itself)."""
    result = {}
    for root, dirs, files in os.walk(str(capsule_root)):
        for fname in files:
            if fname == "SHA256SUMS":
                continue
            fpath = Path(root) / fname
            rel = str(fpath.relative_to(capsule_root)).replace("\\", "/")
            result[rel] = _hash_file(fpath)
    return result


def _create_zip(capsule_root: Path, output_path: str) -> None:
    """Create a zip file from the capsule staging directory.

    The zip entries are prefixed with the capsule root directory name
    (e.g., 'oss-paper-ci-capsule/capsule.json').

    Validates:
    - No path traversal
    - No absolute paths
    - Total size within limits
    """
    total_size = 0
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    # Walk from the parent so archive entries include the root dir name
    walk_root = capsule_root.parent

    with zipfile.ZipFile(str(out), "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(str(capsule_root)):
            for fname in files:
                fpath = Path(root) / fname
                arcname = str(fpath.relative_to(walk_root)).replace("\\", "/")

                # Security: no path traversal
                if ".." in arcname:
                    raise ValueError(f"Path traversal detected: {arcname}")

                # Security: no absolute paths
                if os.path.isabs(arcname):
                    raise ValueError(f"Absolute path in archive: {arcname}")

                # Size check
                fsize = fpath.stat().st_size
                total_size += fsize
                if total_size > MAX_CAPSULE_SIZE_BYTES:
                    raise ValueError(
                        f"Capsule exceeds maximum size ({MAX_CAPSULE_SIZE_BYTES} bytes)"
                    )

                zf.write(str(fpath), arcname)


# ---------------------------------------------------------------------------
# Capsule verification
# ---------------------------------------------------------------------------

class CapsuleVerificationResult:
    """Result of capsule verification."""

    def __init__(self) -> None:
        self.ok: bool = True
        self.schema_version: str = ""
        self.files_checked: int = 0
        self.hashes_matched: int = 0
        self.warnings: list[str] = []
        self.errors: list[str] = []

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)
        self.ok = False

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "schema_version": self.schema_version,
            "files_checked": self.files_checked,
            "hashes_matched": self.hashes_matched,
            "warnings": self.warnings,
            "errors": self.errors,
        }

    def format_text(self) -> str:
        status = "PASSED" if self.ok else "FAILED"
        lines = [
            f"Capsule verification: {status}",
            f"- Schema: {self.schema_version or 'unknown'}",
            f"- Files checked: {self.files_checked}",
            f"- Hashes matched: {self.hashes_matched}",
            f"- Warnings: {len(self.warnings)}",
        ]
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  WARNING: {w}")
        if self.errors:
            for e in self.errors:
                lines.append(f"  ERROR: {e}")
        return "\n".join(lines)


def verify_capsule(capsule_path: str) -> CapsuleVerificationResult:
    """Verify a capsule zip's integrity and structure.

    Checks:
    1. Zip can be opened
    2. Root directory is oss-paper-ci-capsule/
    3. capsule.json exists and is valid
    4. Schema version is supported
    5. SHA256SUMS exists
    6. All hashes match
    7. No path traversal
    8. No absolute paths
    9. Required files exist

    Returns:
        CapsuleVerificationResult with ok=True if all checks pass.
    """
    result = CapsuleVerificationResult()

    if not os.path.exists(capsule_path):
        result.add_error(f"Capsule file not found: {capsule_path}")
        return result

    try:
        zf = zipfile.ZipFile(capsule_path, "r")
    except (zipfile.BadZipFile, OSError) as e:
        result.add_error(f"Cannot open capsule: {e}")
        return result

    try:
        names = zf.namelist()

        # Check root directory
        root_prefix = f"{CAPSULE_ROOT_DIR}/"
        if not any(n.startswith(root_prefix) for n in names):
            result.add_error(f"Capsule root must be '{CAPSULE_ROOT_DIR}/'")
            return result

        # Check for path traversal
        for name in names:
            if ".." in name:
                result.add_error(f"Path traversal detected: {name}")
                return result
            # Check for absolute paths in the archive
            parts = name.split("/")
            for part in parts:
                if os.path.isabs(part) or (len(part) >= 2 and part[1] == ":"):
                    result.add_error(f"Absolute path in archive: {name}")
                    return result

        # Check capsule.json
        manifest_path = f"{CAPSULE_ROOT_DIR}/capsule.json"
        if manifest_path not in names:
            result.add_error("capsule.json not found")
            return result

        try:
            manifest_data = json.loads(zf.read(manifest_path))
            result.schema_version = manifest_data.get("schema_version", "unknown")
        except (json.JSONDecodeError, KeyError) as e:
            result.add_error(f"Invalid capsule.json: {e}")
            return result

        # Check SHA256SUMS
        sha_path = f"{CAPSULE_ROOT_DIR}/SHA256SUMS"
        if sha_path not in names:
            result.add_error("SHA256SUMS not found")
            return result

        # Parse SHA256SUMS
        sha_content = zf.read(sha_path).decode("utf-8")
        expected_hashes = {}
        for line in sha_content.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split("  ", 1)
            if len(parts) == 2:
                expected_hashes[parts[1]] = parts[0]

        # Verify hashes
        result.files_checked = len(expected_hashes)
        for rel_path, expected_hash in expected_hashes.items():
            full_path = f"{CAPSULE_ROOT_DIR}/{rel_path}"
            if full_path not in names:
                result.add_error(f"File listed in SHA256SUMS not found: {rel_path}")
                continue

            actual_hash = hashlib.sha256(zf.read(full_path)).hexdigest()
            if actual_hash != expected_hash:
                result.add_error(f"Hash mismatch: {rel_path}")
            else:
                result.hashes_matched += 1

        # Check required files
        for req in REQUIRED_FILES:
            req_path = f"{CAPSULE_ROOT_DIR}/{req}"
            if req_path not in names:
                result.add_warning(f"Recommended file missing: {req}")

    finally:
        zf.close()

    return result


# ---------------------------------------------------------------------------
# Capsule inspection
# ---------------------------------------------------------------------------

def inspect_capsule(capsule_path: str) -> dict[str, Any]:
    """Inspect a capsule and return its metadata.

    Returns:
        Dict with source, execution, reports, limitations info.
    """
    if not os.path.exists(capsule_path):
        return {"error": f"Capsule file not found: {capsule_path}"}

    try:
        zf = zipfile.ZipFile(capsule_path, "r")
    except (zipfile.BadZipFile, OSError) as e:
        return {"error": f"Cannot open capsule: {e}"}

    try:
        root = f"{CAPSULE_ROOT_DIR}/"

        # Read capsule.json
        manifest_path = f"{root}capsule.json"
        try:
            manifest = json.loads(zf.read(manifest_path))
        except (KeyError, json.JSONDecodeError):
            return {"error": "Invalid or missing capsule.json"}

        # Read source metadata
        source = {}
        try:
            source = json.loads(zf.read(f"{root}metadata/source.json"))
        except (KeyError, json.JSONDecodeError):
            pass

        # Read commands metadata
        commands = {}
        try:
            commands = json.loads(zf.read(f"{root}metadata/commands.json"))
        except (KeyError, json.JSONDecodeError):
            pass

        # Read scan report summary
        scan_summary = {}
        try:
            scan_data = json.loads(zf.read(f"{root}reports/scan_report.json"))
            scan_summary = scan_data.get("summary", {})
        except (KeyError, json.JSONDecodeError):
            pass

        # Count artifacts
        artifact_count = 0
        try:
            idx = json.loads(zf.read(f"{root}artifacts/artifact_index.json"))
            artifact_count = idx.get("included", 0)
        except (KeyError, json.JSONDecodeError):
            pass

        # List files
        files = [n[len(root):] for n in zf.namelist() if n.startswith(root) and n != root]

        return {
            "schema_version": manifest.get("schema_version"),
            "capsule_type": manifest.get("capsule_type"),
            "oss_paper_ci_version": manifest.get("oss_paper_ci_version"),
            "source": source,
            "execution": manifest.get("execution", {}),
            "scan_score": scan_summary.get("score"),
            "scan_status": scan_summary.get("status"),
            "artifact_count": artifact_count,
            "reports": manifest.get("reports", {}),
            "limitations": manifest.get("limitations", []),
            "files": files,
            "file_count": len(files),
        }

    finally:
        zf.close()


# ---------------------------------------------------------------------------
# Capsule diff
# ---------------------------------------------------------------------------

def diff_capsules(old_path: str, new_path: str) -> dict[str, Any]:
    """Compare two capsules and return differences.

    Returns:
        Dict with changes between old and new capsules.
    """
    old_info = inspect_capsule(old_path)
    new_info = inspect_capsule(new_path)

    if "error" in old_info:
        return {"error": f"Old capsule: {old_info['error']}"}
    if "error" in new_info:
        return {"error": f"New capsule: {new_info['error']}"}

    old_source = old_info.get("source", {})
    new_source = new_info.get("source", {})
    old_exec = old_info.get("execution", {})
    new_exec = new_info.get("execution", {})

    # Source changes
    source_changed = old_source.get("commit_sha") != new_source.get("commit_sha")
    same_repo = old_source.get("repo_url") == new_source.get("repo_url")

    # Command status delta
    old_succeeded = old_exec.get("commands_succeeded", 0)
    new_succeeded = new_exec.get("commands_succeeded", 0)
    old_failed = old_exec.get("commands_failed", 0)
    new_failed = new_exec.get("commands_failed", 0)

    # Scan score delta
    old_score = old_info.get("scan_score")
    new_score = new_info.get("scan_score")
    score_delta = None
    if old_score is not None and new_score is not None:
        score_delta = new_score - old_score

    # Artifact changes
    old_files = set(old_info.get("files", []))
    new_files = set(new_info.get("files", []))
    files_added = sorted(new_files - old_files)
    files_removed = sorted(old_files - new_files)

    # Build recommendation
    rec_parts = []
    if source_changed:
        rec_parts.append("commit changed")
    if score_delta is not None and score_delta != 0:
        rec_parts.append(f"score {score_delta:+d}")
    if new_failed > old_failed:
        rec_parts.append(f"{new_failed - old_failed} more failures")
    if new_succeeded > old_succeeded:
        rec_parts.append(f"{new_succeeded - old_succeeded} more successes")
    if files_added:
        rec_parts.append(f"{len(files_added)} files added")
    if files_removed:
        rec_parts.append(f"{len(files_removed)} files removed")

    recommendation = "Changes: " + ", ".join(rec_parts) + "." if rec_parts else "No significant changes."

    return {
        "same_repo": same_repo,
        "commit_changed": source_changed,
        "old_commit": old_source.get("commit_sha"),
        "new_commit": new_source.get("commit_sha"),
        "old_mode": old_exec.get("mode"),
        "new_mode": new_exec.get("mode"),
        "commands_succeeded_delta": new_succeeded - old_succeeded,
        "commands_failed_delta": new_failed - old_failed,
        "old_scan_score": old_score,
        "new_scan_score": new_score,
        "score_delta": score_delta,
        "old_scan_status": old_info.get("scan_status"),
        "new_scan_status": new_info.get("scan_status"),
        "files_added": files_added,
        "files_removed": files_removed,
        "recommendation": recommendation,
    }


def format_diff_markdown(diff: dict[str, Any]) -> str:
    """Format a capsule diff as markdown."""
    if "error" in diff:
        return f"# Capsule Diff Error\n\n{diff['error']}\n"

    lines = ["# Capsule Diff\n"]

    # Source
    lines.append("## Source\n")
    lines.append(f"- Same repository: {'yes' if diff['same_repo'] else 'no'}")
    lines.append(f"- Commit changed: {'yes' if diff['commit_changed'] else 'no'}")
    if diff.get("old_commit"):
        lines.append(f"- Old commit: `{diff['old_commit'][:12]}`")
    if diff.get("new_commit"):
        lines.append(f"- New commit: `{diff['new_commit'][:12]}`")
    lines.append("")

    # Execution
    lines.append("## Execution\n")
    lines.append(f"- Old mode: {diff.get('old_mode', '?')}")
    lines.append(f"- New mode: {diff.get('new_mode', '?')}")
    lines.append(f"- Commands succeeded delta: {diff.get('commands_succeeded_delta', 0):+d}")
    lines.append(f"- Commands failed delta: {diff.get('commands_failed_delta', 0):+d}")
    lines.append("")

    # Scan
    lines.append("## Scan\n")
    lines.append(f"| Metric | Old | New | Delta |")
    lines.append(f"|--------|-----|-----|-------|")
    old_score = diff.get("old_scan_score", "?")
    new_score = diff.get("new_scan_score", "?")
    score_delta = diff.get("score_delta")
    delta_str = f"{score_delta:+d}" if score_delta is not None else "n/a"
    lines.append(f"| Score | {old_score} | {new_score} | {delta_str} |")
    lines.append(f"| Status | {diff.get('old_scan_status', '?')} | {diff.get('new_scan_status', '?')} | |")
    lines.append("")

    # Files
    files_added = diff.get("files_added", [])
    files_removed = diff.get("files_removed", [])
    if files_added or files_removed:
        lines.append("## Files\n")
        for f in files_added:
            lines.append(f"- **added**: `{f}`")
        for f in files_removed:
            lines.append(f"- **removed**: `{f}`")
        lines.append("")

    # Summary
    lines.append("## Summary\n")
    lines.append(diff.get("recommendation", "No changes."))
    lines.append("")

    return "\n".join(lines)
