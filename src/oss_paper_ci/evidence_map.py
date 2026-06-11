"""Evidence map for reproducibility dossiers.

Maps repository evidence to structured categories with status,
significance, and audience-specific notes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class EvidenceItem:
    """A single piece of reproducibility evidence."""

    category: str
    item: str
    status: str  # present, missing, partial, unknown
    source: str
    why_it_matters: str
    suggested_action: str = ""
    audience_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "item": self.item,
            "status": self.status,
            "source": self.source,
            "why_it_matters": self.why_it_matters,
            "suggested_action": self.suggested_action,
            "audience_note": self.audience_note,
        }


def build_evidence_map_from_scan(scan_data: dict[str, Any]) -> list[EvidenceItem]:
    """Build evidence map from a scan report."""
    items: list[EvidenceItem] = []
    checks = scan_data.get("checks", [])

    check_index = {c["id"]: c for c in checks}

    # Metadata evidence
    _add_if_check(items, "metadata", check_index, "META001", "README file",
                  "A README helps others understand the project.",
                  "Add a README.md with project description and setup instructions.")
    _add_if_check(items, "metadata", check_index, "META002", "License",
                  "A license clarifies usage rights.",
                  "Add a LICENSE file.")
    _add_if_check(items, "metadata", check_index, "META003", "Citation information",
                  "Citation info helps others give proper credit.",
                  "Add CITATION.cff or citation instructions in README.")

    # Environment evidence
    _add_if_check(items, "environment", check_index, "ENV001", "Dependency file",
                  "Dependency files let others install the same environment.",
                  "Add requirements.txt or pyproject.toml.")
    _add_if_check(items, "environment", check_index, "ENV003", "Python version",
                  "Specifying Python version prevents compatibility issues.",
                  "Add python_requires to pyproject.toml or specify in README.")

    # Execution evidence
    _add_if_check(items, "execution", check_index, "EXP001", "Entry point scripts",
                  "Entry points tell others how to run the code.",
                  "Ensure scripts/ directory has clear entry points.")
    _add_if_check(items, "execution", check_index, "EXP003", "Reproduction contract",
                  "A reproducibility.yml declares how to reproduce results.",
                  "Run `oss-paper-ci init --contract` to create one.")

    # Data evidence
    _add_if_check(items, "data", check_index, "DATA001", "Data documentation",
                  "Data documentation explains what data is needed.",
                  "Add a data/README.md or data documentation.")

    # Results evidence
    _add_if_check(items, "results", check_index, "RES001", "Output directories",
                  "Output directories show where results are stored.",
                  "Create results/ and figures/ directories.")

    # CI evidence
    _add_if_check(items, "automation", check_index, "CI001", "CI workflow",
                  "CI workflows automate reproducibility checks.",
                  "Add .github/workflows/ with oss-paper-ci scan.")

    return items


def build_evidence_map_from_reproduce(reproduce_data: dict[str, Any]) -> list[EvidenceItem]:
    """Build evidence map from a reproduce report."""
    items: list[EvidenceItem] = []

    # Environment
    env = reproduce_data.get("environment", {})
    env_files = env.get("environment_files", []) if env else []
    if env_files:
        items.append(EvidenceItem(
            category="environment",
            item="Environment files detected",
            status="present",
            source=", ".join(f["type"] for f in env_files),
            why_it_matters="Environment files enable dependency installation.",
        ))
    else:
        items.append(EvidenceItem(
            category="environment",
            item="Environment files",
            status="missing",
            source="reproduce detection",
            why_it_matters="Without environment files, dependencies cannot be installed.",
            suggested_action="Add requirements.txt or pyproject.toml.",
        ))

    # Execution
    cmds = reproduce_data.get("reproduction_commands", [])
    if cmds:
        items.append(EvidenceItem(
            category="execution",
            item="Reproduction commands",
            status="present",
            source="reproduce detection",
            why_it_matters="Declared commands tell others how to reproduce.",
        ))
    else:
        items.append(EvidenceItem(
            category="execution",
            item="Reproduction commands",
            status="missing",
            source="reproduce detection",
            why_it_matters="Without commands, reproduction cannot be attempted.",
            suggested_action="Add reproducibility.yml or use --command.",
        ))

    # Results
    artifacts = reproduce_data.get("generated_artifacts", [])
    if artifacts:
        items.append(EvidenceItem(
            category="results",
            item="Generated artifacts",
            status="present",
            source=f"{len(artifacts)} artifacts found",
            why_it_matters="Artifacts show what the reproduction produced.",
        ))

    # Provenance
    commit = reproduce_data.get("commit_sha", "")
    if commit:
        items.append(EvidenceItem(
            category="provenance",
            item="Commit SHA recorded",
            status="present",
            source=commit[:12],
            why_it_matters="Commit SHA links the attempt to a specific code version.",
        ))

    return items


def _add_if_check(
    items: list[EvidenceItem],
    category: str,
    check_index: dict,
    check_id: str,
    item_name: str,
    why: str,
    action: str,
) -> None:
    """Add evidence item if check exists in report."""
    check = check_index.get(check_id)
    if check is None:
        return

    status = check.get("status", "unknown")
    if status == "pass":
        mapped = "present"
    elif status == "fail":
        mapped = "missing"
    else:
        mapped = "partial"

    items.append(EvidenceItem(
        category=category,
        item=item_name,
        status=mapped,
        source=f"check {check_id}: {check.get('message', '')}",
        why_it_matters=why,
        suggested_action=action if mapped != "present" else "",
    ))
