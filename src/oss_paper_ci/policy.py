"""Policy profiles for oss-paper-ci.

Profiles are named parameter bundles that control scoring thresholds,
severity classifications, and check-level overrides.  They let users
pick a rigor level without hand-tuning every config knob.

Profiles:
  lenient     – early-stage projects; fewer blocking, more advisory
  default     – current behavior; balanced for general use
  strict      – stricter on LICENSE, environment, data, scripts
  publication – repos preparing for public release or appendix
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PolicyProfile:
    """A named set of policy parameters."""

    name: str
    description: str
    # Scoring thresholds
    pass_score: int = 85
    warn_score: int = 60
    fail_under: int = 50
    # Which severity+status combos count as blocking / important / advisory.
    # Users rarely touch this; it exists for profile authors.
    blocking_classifications: list[str] = field(
        default_factory=lambda: ["error+fail"]
    )
    important_classifications: list[str] = field(
        default_factory=lambda: ["warning+fail", "error+warn"]
    )
    # Check-level overrides: {check_id: new_severity}
    check_overrides: dict[str, str] = field(default_factory=dict)
    # Additional checks to treat as blocking regardless of default classification
    treat_as_blocking: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "pass_score": self.pass_score,
            "warn_score": self.warn_score,
            "fail_under": self.fail_under,
            "blocking_classifications": self.blocking_classifications,
            "important_classifications": self.important_classifications,
            "check_overrides": dict(self.check_overrides),
            "treat_as_blocking": list(self.treat_as_blocking),
        }


# ── Built-in profiles ────────────────────────────────────────────────────────

_PROFILES: dict[str, PolicyProfile] = {}


def _register(profile: PolicyProfile) -> None:
    _PROFILES[profile.name] = profile


_register(PolicyProfile(
    name="lenient",
    description=(
        "Early-stage projects.  Fewer blocking findings; more items are "
        "advisory-only.  Useful when you want feedback without hard failures."
    ),
    pass_score=70,
    warn_score=50,
    fail_under=30,
    check_overrides={
        "META003": "info",    # citation → advisory
        "META004": "info",    # quickstart → advisory
        "META005": "info",    # contributing → advisory
        "ENV002": "info",     # pinned deps → advisory
        "DATA001": "info",    # data description → advisory
        "RES001": "info",     # results dir → advisory
        "CI001": "info",      # CI workflow → advisory
    },
))


_register(PolicyProfile(
    name="default",
    description=(
        "Balanced defaults.  Equivalent to pre-v1.5 behavior when no "
        "profile is specified."
    ),
    pass_score=85,
    warn_score=60,
    fail_under=50,
))


_register(PolicyProfile(
    name="strict",
    description=(
        "Stricter governance.  Missing LICENSE, environment spec, data "
        "description, and reproducibility script are all blocking."
    ),
    pass_score=90,
    warn_score=70,
    fail_under=50,
    check_overrides={
        "META002": "error",   # LICENSE → always blocking
        "ENV001": "error",    # environment → always blocking
        "DATA001": "warning", # data description → important
        "RES001": "warning",  # results dir → important
        "EXP001": "warning",  # experiment description → important
    },
    treat_as_blocking=["META002", "ENV001", "DATA001"],
))


_register(PolicyProfile(
    name="publication",
    description=(
        "Publication-ready repos.  Requires LICENSE, environment, data "
        "description, results directory, experiment description, and "
        "reproduction script.  Does NOT judge paper quality or correctness."
    ),
    pass_score=90,
    warn_score=75,
    fail_under=50,
    check_overrides={
        "META002": "error",
        "META003": "warning",
        "META004": "warning",
        "ENV001": "error",
        "ENV002": "warning",
        "DATA001": "warning",
        "RES001": "warning",
        "EXP001": "warning",
        "EXP002": "warning",
    },
    treat_as_blocking=["META002", "ENV001", "DATA001", "EXP001"],
))


# ── Public API ───────────────────────────────────────────────────────────────

def get_profile(name: str) -> PolicyProfile:
    """Return a profile by name.

    Raises:
        ValueError: if *name* is not a known profile.
    """
    if name not in _PROFILES:
        available = ", ".join(sorted(_PROFILES))
        raise ValueError(
            f"Unknown policy profile: {name!r}. "
            f"Available profiles: {available}"
        )
    return _PROFILES[name]


def list_profiles() -> list[str]:
    """Return sorted list of available profile names."""
    return sorted(_PROFILES)


def explain_profile(name: str) -> str:
    """Return a human-readable explanation of a profile."""
    profile = get_profile(name)
    lines = [
        f"Profile: {profile.name}",
        f"",
        f"  {profile.description}",
        f"",
        f"Thresholds:",
        f"  pass_score:  {profile.pass_score}",
        f"  warn_score:  {profile.warn_score}",
        f"  fail_under:  {profile.fail_under}",
    ]

    if profile.check_overrides:
        lines.append("")
        lines.append("Check severity overrides:")
        for cid, sev in sorted(profile.check_overrides.items()):
            lines.append(f"  {cid}: {sev}")

    if profile.treat_as_blocking:
        lines.append("")
        lines.append("Treat as blocking:")
        for cid in sorted(profile.treat_as_blocking):
            lines.append(f"  {cid}")

    return "\n".join(lines)
