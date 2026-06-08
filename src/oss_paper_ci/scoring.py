"""Scoring engine for oss-paper-ci.

The reproducibility score is a weighted sum of check results.
It is NOT a quality score for the paper itself — only an indicator
of whether the repository has the engineering basics for reproducibility.
"""

from __future__ import annotations

from oss_paper_ci.models import CheckResult, Severity, Status

# Weight mapping: each check ID prefix maps to a category weight.
# Weights reflect how critical each category is for reproducibility.
CATEGORY_WEIGHTS: dict[str, float] = {
    "META": 15,    # Repository metadata (README, LICENSE, CITATION)
    "ENV": 20,     # Environment reproducibility
    "EXP": 20,     # Experiment entry points
    "DATA": 15,    # Data availability
    "RES": 10,     # Results and figures
    "PAP": 10,     # Paper/code consistency
    "CI": 10,      # CI and maintenance
}

# Penalty per failed check within a category
FAIL_PENALTY = {
    Status.PASS: 0,
    Status.WARN: 0.3,    # 30% penalty
    Status.FAIL: 1.0,    # 100% penalty
    Status.UNKNOWN: 0.1, # 10% penalty for unknown
}


def compute_score(checks: list[CheckResult]) -> tuple[int, str, dict[str, int]]:
    """Compute the reproducibility score from check results.

    Returns:
        Tuple of (score 0-100, overall status, severity counts).
    """
    if not checks:
        return 0, "unknown", {"info": 0, "warning": 0, "error": 0}

    # Count severities
    counts = {"info": 0, "warning": 0, "error": 0}
    for c in checks:
        if c.severity == Severity.INFO:
            counts["info"] += 1
        elif c.severity == Severity.WARNING:
            counts["warning"] += 1
        elif c.severity == Severity.ERROR:
            counts["error"] += 1

    # Group checks by category (prefix of check ID)
    category_results: dict[str, list[CheckResult]] = {}
    for c in checks:
        prefix = c.id[:3] if len(c.id) >= 3 else c.id
        category_results.setdefault(prefix, []).append(c)

    # Compute weighted score
    total_weight = 0.0
    weighted_score = 0.0

    for prefix, weight in CATEGORY_WEIGHTS.items():
        cat_checks = category_results.get(prefix, [])
        if not cat_checks:
            continue

        total_weight += weight

        # Calculate category score: start at 1.0, subtract penalties
        cat_penalty = 0.0
        for c in cat_checks:
            cat_penalty += FAIL_PENALTY.get(c.status, 0.1)

        # Normalize penalty by number of checks in category
        avg_penalty = cat_penalty / len(cat_checks) if cat_checks else 0
        cat_score = max(0.0, 1.0 - avg_penalty)
        weighted_score += weight * cat_score

    # Handle checks with unknown prefixes
    known_prefixes = set(CATEGORY_WEIGHTS.keys())
    unknown_checks = [c for c in checks if c.id[:3] not in known_prefixes]
    if unknown_checks:
        weight = 10.0
        total_weight += weight
        avg_penalty = sum(FAIL_PENALTY.get(c.status, 0.1) for c in unknown_checks) / len(unknown_checks)
        weighted_score += weight * max(0.0, 1.0 - avg_penalty)

    if total_weight == 0:
        return 0, "unknown", counts

    score = round(100 * weighted_score / total_weight)
    score = max(0, min(100, score))

    # Determine overall status based on actual check outcomes
    has_fail = any(c.status == Status.FAIL for c in checks)
    has_warn = any(c.status == Status.WARN for c in checks)
    if has_fail:
        status = "fail"
    elif has_warn:
        status = "warn"
    else:
        status = "pass"

    return score, status, counts
