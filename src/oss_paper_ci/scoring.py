"""Scoring engine for oss-paper-ci.

Deduction model with finding classification:
- blocking: error-severity fail → always fail status
- important: warning-severity fail, error-severity warn → affects status
- advisory: info-severity warn, maintenance items → only affects score, not status

Status rules:
- fail: score < 50, or any blocking finding
- warn: score 50-84, or any important finding
- pass: score >= 85, no blocking, no important findings
"""

from __future__ import annotations

from oss_paper_ci.models import CheckResult, Severity, Status

# Per-check deduction by (severity, status)
_UNIT_DEDUCTION: dict[tuple[str, str], int] = {
    ("error", "fail"): 5,
    ("error", "warn"): 2,
    ("error", "unknown"): 3,
    ("warning", "fail"): 4,
    ("warning", "warn"): 1,
    ("warning", "unknown"): 1,
    ("info", "fail"): 2,
    ("info", "unknown"): 0,
    ("info", "pass"): 0,
}

# Per-category deduction cap
_CATEGORY_CAP: dict[str, int] = {
    "META": 20,
    "ENV": 20,
    "EXP": 15,
    "DATA": 10,
    "RES": 8,
    "PAP": 8,
    "CI": 8,
}

# Critical penalties — applied ON TOP of per-check deductions
_CRITICAL_CHECKS: dict[str, int] = {
    "META001": 15,  # README — most critical
    "META002": 10,  # LICENSE
    "ENV001": 15,   # Environment file — most critical
}

# Advisory checks — these are maintenance items, not reproducibility blockers
_ADVISORY_CHECKS: set[str] = {
    "CI003",  # Linting/formatting
    "CI004",  # Issue/PR templates
    "CI005",  # Security policy
    "CI006",  # Package metadata
    "META005",  # Contributing guidelines
    "META007",  # Artifact metadata
}


def classify_finding(check: CheckResult) -> str:
    """Classify a check result as blocking, important, or advisory.

    Returns:
        "blocking", "important", or "advisory"
    """
    sev = check.severity.value if hasattr(check.severity, 'value') else check.severity
    stat = check.status.value if hasattr(check.status, 'value') else check.status

    # Advisory: maintenance items that don't affect reproducibility
    if check.id in _ADVISORY_CHECKS:
        return "advisory"
    if sev == "info" and stat == "warn":
        return "advisory"

    # Blocking: error-severity failures
    if sev == "error" and stat == "fail":
        return "blocking"

    # Important: warning-severity failures, error-severity warnings
    if sev == "warning" and stat == "fail":
        return "important"
    if sev == "error" and stat == "warn":
        return "important"

    # Everything else (pass, unknown) is advisory
    if stat == "pass":
        return "advisory"

    return "advisory"


def compute_score(checks: list[CheckResult]) -> tuple[int, str, dict[str, int]]:
    """Compute the reproducibility score from check results.

    Returns:
        Tuple of (score 0-100, overall status, severity counts).
    """
    if not checks:
        return 0, "unknown", {"info": 0, "warning": 0, "error": 0}

    counts = {"info": 0, "warning": 0, "error": 0}
    for c in checks:
        if c.severity == Severity.INFO:
            counts["info"] += 1
        elif c.severity == Severity.WARNING:
            counts["warning"] += 1
        elif c.severity == Severity.ERROR:
            counts["error"] += 1

    # Per-category deduction
    category_deductions: dict[str, int] = {}
    for c in checks:
        prefix = c.id[:3] if len(c.id) >= 3 else c.id
        sev = c.severity.value if hasattr(c.severity, 'value') else c.severity
        stat = c.status.value if hasattr(c.status, 'value') else c.status
        unit = _UNIT_DEDUCTION.get((sev, stat), 0)
        if unit > 0:
            category_deductions[prefix] = category_deductions.get(prefix, 0) + unit

    # Apply category caps
    total_deduction = 0
    for prefix, raw in category_deductions.items():
        cap = _CATEGORY_CAP.get(prefix, 10)
        total_deduction += min(raw, cap)

    # Critical penalties
    for c in checks:
        if c.id in _CRITICAL_CHECKS and c.status == Status.FAIL:
            total_deduction += _CRITICAL_CHECKS[c.id]

    score = max(0, 100 - total_deduction)

    # Status determination using finding classification
    has_blocking = any(classify_finding(c) == "blocking" for c in checks)
    has_important = any(classify_finding(c) == "important" for c in checks)

    if score < 50 or has_blocking:
        status = "fail"
    elif score < 85 or has_important:
        status = "warn"
    else:
        status = "pass"

    return score, status, counts


def get_score_breakdown(checks: list[CheckResult]) -> list[dict[str, object]]:
    """Get a breakdown of deductions for each non-passing check."""
    breakdown = []
    for c in checks:
        sev = c.severity.value if hasattr(c.severity, 'value') else c.severity
        stat = c.status.value if hasattr(c.status, 'value') else c.status
        unit = _UNIT_DEDUCTION.get((sev, stat), 0)
        critical = _CRITICAL_CHECKS.get(c.id, 0) if c.status == Status.FAIL else 0
        total = unit + critical
        classification = classify_finding(c)
        if total > 0:
            breakdown.append({
                "id": c.id,
                "title": c.title,
                "severity": sev,
                "status": stat,
                "deduction": total,
                "classification": classification,
            })
    return breakdown
