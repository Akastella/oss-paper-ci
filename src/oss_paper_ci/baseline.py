"""Baseline creation and comparison for oss-paper-ci.

Allows users to snapshot the current scan state and later compare against it
to detect regressions and improvements -- without requiring git.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class Baseline:
    """A point-in-time snapshot of scan results."""

    schema_version: str = "0.3"
    created_at: str = ""
    repo_path: str = ""
    score: int = 0
    status: str = ""
    check_results: list[dict[str, Any]] = field(default_factory=list)

    def save(self, path: str) -> None:
        """Save baseline to a JSON file.

        Args:
            path: Destination file path. Parent directories are created
                  automatically.
        """
        dest = Path(path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> Baseline:
        """Load a baseline from a JSON file.

        Args:
            path: Path to the baseline JSON file.

        Returns:
            Baseline instance.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is not valid JSON or is missing required
                fields.
        """
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Baseline file not found: {path}")
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in baseline file: {exc}") from exc
        if not isinstance(data, dict):
            raise ValueError("Baseline file must contain a JSON object")
        return cls.from_dict(data)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a plain dict."""
        return {
            "schema_version": self.schema_version,
            "created_at": self.created_at,
            "repo_path": self.repo_path,
            "score": self.score,
            "status": self.status,
            "check_results": self.check_results,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Baseline:
        """Deserialize from a plain dict."""
        return cls(
            schema_version=data.get("schema_version", "0.3"),
            created_at=data.get("created_at", ""),
            repo_path=data.get("repo_path", ""),
            score=data.get("score", 0),
            status=data.get("status", ""),
            check_results=data.get("check_results", []),
        )


def create_baseline(repo_path: str, config: Any = None) -> Baseline:
    """Create a baseline snapshot from a fresh scan of *repo_path*.

    Args:
        repo_path: Path to the repository root.
        config: Optional configuration object (passed to the scanner).

    Returns:
        Baseline populated with the current scan results.
    """
    from oss_paper_ci.scanner import scan

    report = scan(repo_path, config)

    check_results = []
    for c in report.checks:
        check_results.append({
            "id": c.id,
            "title": c.title,
            "severity": c.severity.value if hasattr(c.severity, "value") else str(c.severity),
            "status": c.status.value if hasattr(c.status, "value") else str(c.status),
            "message": c.message,
        })

    return Baseline(
        schema_version="0.3",
        created_at=datetime.now(timezone.utc).isoformat(),
        repo_path=str(Path(repo_path).resolve()),
        score=report.summary.score,
        status=report.summary.status,
        check_results=check_results,
    )


def compare_baseline(current: Baseline, baseline: Baseline) -> dict[str, Any]:
    """Compare *current* scan results against a *baseline*.

    Returns a dict with:
        score_delta: int -- positive means improvement.
        status_delta: str -- human-readable transition, e.g. "pass -> warn".
        new_findings: list[dict] -- checks that got worse.
        resolved_findings: list[dict] -- checks that improved.
        regressions: list[dict] -- checks that are new failures.
        improvements: list[dict] -- checks that are newly passing.
    """
    _STATUS_ORDER = {"pass": 0, "warn": 1, "fail": 2, "unknown": 1}

    baseline_by_id: dict[str, dict[str, Any]] = {
        cr["id"]: cr for cr in baseline.check_results
    }
    current_by_id: dict[str, dict[str, Any]] = {
        cr["id"]: cr for cr in current.check_results
    }

    all_ids = sorted(set(baseline_by_id) | set(current_by_id))

    new_findings: list[dict[str, Any]] = []
    resolved_findings: list[dict[str, Any]] = []
    regressions: list[dict[str, Any]] = []
    improvements: list[dict[str, Any]] = []

    for cid in all_ids:
        base = baseline_by_id.get(cid)
        curr = current_by_id.get(cid)

        # Brand-new check not in baseline -- treat as a regression if it
        # didn't pass.
        if base is None and curr is not None:
            if curr["status"] != "pass":
                regressions.append(curr)
            continue

        # Check disappeared from current scan -- treat as resolved.
        if base is not None and curr is None:
            resolved_findings.append(base)
            continue

        # Both exist -- compare statuses.
        assert base is not None and curr is not None  # for type checker
        base_sev = _STATUS_ORDER.get(base["status"], 1)
        curr_sev = _STATUS_ORDER.get(curr["status"], 1)

        if curr_sev > base_sev:
            new_findings.append({
                "id": cid,
                "title": curr.get("title", ""),
                "from_status": base["status"],
                "to_status": curr["status"],
                "message": curr.get("message", ""),
            })
        elif curr_sev < base_sev:
            if base["status"] == "fail" and curr["status"] == "pass":
                improvements.append(curr)
            else:
                resolved_findings.append({
                    "id": cid,
                    "title": curr.get("title", ""),
                    "from_status": base["status"],
                    "to_status": curr["status"],
                    "message": curr.get("message", ""),
                })

    score_delta = current.score - baseline.score
    status_delta = f"{baseline.status} -> {current.status}"

    return {
        "score_delta": score_delta,
        "status_delta": status_delta,
        "new_findings": new_findings,
        "resolved_findings": resolved_findings,
        "regressions": regressions,
        "improvements": improvements,
    }
