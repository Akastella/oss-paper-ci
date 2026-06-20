"""GitHub Actions workflow audit module."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Known safe official actions (major version pinned)
OFFICIAL_ACTIONS = {
    "actions/checkout",
    "actions/setup-python",
    "actions/upload-artifact",
    "actions/download-artifact",
    "actions/cache",
    "actions/github-script",
    "actions/stale",
    "actions/labeler",
    "actions/dependency-review-action",
    "github/codeql-action",
    "pypa/gh-action-pypi-publish",
    "softprops/action-gh-release",
    "peaceiris/actions-gh-pages",
    "peaceiris/actions-hugo",
    "docker/setup-buildx-action",
    "docker/build-push-action",
    "docker/login-action",
    "actionsattest/build-provenance",
}

# High-risk triggers
HIGH_RISK_TRIGGERS = [
    "pull_request_target",
    "workflow_run",
    "workflow_dispatch",  # Less risky but note it
    "repository_dispatch",
]


@dataclass
class WorkflowAuditResult:
    """Result of workflow audit."""

    findings: list[dict[str, Any]] = field(default_factory=list)
    workflows_scanned: int = 0
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": self.findings,
            "workflows_scanned": self.workflows_scanned,
            "limitations": self.limitations,
        }


def _parse_workflow_permissions(content: str) -> dict[str, str] | None:
    """Parse permissions block from workflow content."""
    # Match top-level permissions block
    m = re.search(r"^permissions:\s*$", content, re.MULTILINE)
    if not m:
        # Check for inline permissions
        m = re.search(r"permissions:\s*(.+)$", content, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            if val == "write-all":
                return {"all": "write-all"}
            elif val == "read-all":
                return {"all": "read-all"}
        return None

    # Parse multi-line permissions
    perms: dict[str, str] = {}
    lines = content[m.end():].splitlines()
    for line in lines:
        m2 = re.match(r"^\s+(\w+):\s*(\w+)", line)
        if m2:
            perms[m2.group(1)] = m2.group(2)
        elif line.strip() and not line.startswith(" "):
            break  # End of permissions block
    return perms if perms else None


def _parse_triggers(content: str) -> list[str]:
    """Parse workflow triggers."""
    triggers = []
    m = re.search(r"^on:\s*$", content, re.MULTILINE)
    if not m:
        m = re.search(r"^on:\s*\[([^\]]+)\]", content, re.MULTILINE)
        if m:
            triggers.extend(t.strip().strip("'\"") for t in m.group(1).split(","))
        else:
            m = re.search(r"^on:\s*(\w+)", content, re.MULTILINE)
            if m:
                triggers.append(m.group(1))
        return triggers

    lines = content[m.end():].splitlines()
    for line in lines:
        m2 = re.match(r"^\s+(\w[\w_]*):", line)
        if m2:
            triggers.append(m2.group(1))
        elif line.strip() and not line.startswith(" ") and not line.startswith("#"):
            break
    return triggers


def _parse_actions_used(content: str) -> list[dict[str, Any]]:
    """Parse actions used in workflow."""
    actions = []
    for m in re.finditer(r"uses:\s*([^\s#]+)", content):
        action_ref = m.group(1)
        line_num = content[:m.start()].count("\n") + 1

        # Parse action and version
        parts = action_ref.split("@")
        action_name = parts[0]
        version = parts[1] if len(parts) > 1 else "unknown"

        # Check if pinned to SHA (40 hex chars)
        is_sha_pin = bool(re.match(r"^[a-f0-9]{40}$", version))
        # Check if major version pin (vN)
        is_major_pin = bool(re.match(r"^v\d+$", version))

        # Check if official
        is_official = any(action_name.startswith(oa) for oa in OFFICIAL_ACTIONS)

        actions.append({
            "action": action_name,
            "version": version,
            "ref": action_ref,
            "line": line_num,
            "is_sha_pin": is_sha_pin,
            "is_major_pin": is_major_pin,
            "is_official": is_official,
        })

    return actions


def audit_workflows(repo_path: str | Path) -> WorkflowAuditResult:
    """Audit GitHub Actions workflows."""
    root = Path(repo_path).resolve()
    result = WorkflowAuditResult(
        limitations=[
            "Static analysis of workflow YAML files only.",
            "Does not verify action integrity or existence.",
            "Official action list may be incomplete.",
            "Does not check for secrets exposure in workflow logs.",
            "Major version pinning (e.g., @v4) is accepted for official actions.",
        ]
    )

    workflows_dir = root / ".github" / "workflows"
    if not workflows_dir.exists():
        return result

    for wf_file in sorted(workflows_dir.glob("*.yml")):
        result.workflows_scanned += 1
        try:
            content = wf_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        rel_path = str(wf_file.relative_to(root)).replace("\\", "/")

        # Check triggers
        triggers = _parse_triggers(content)
        for trigger in triggers:
            if trigger in HIGH_RISK_TRIGGERS:
                sev = "high" if trigger == "pull_request_target" else "medium"
                result.findings.append({
                    "id": f"workflow-trigger-{trigger}",
                    "severity": sev,
                    "category": "workflow",
                    "path": rel_path,
                    "title": f"High-risk trigger: {trigger}",
                    "message": f"Workflow uses '{trigger}' which can be exploited if it checks out PR code.",
                    "recommendation": "Avoid pull_request_target with PR code checkout. Use pull_request instead.",
                })

        # Check permissions
        perms = _parse_workflow_permissions(content)
        if perms is None:
            result.findings.append({
                "id": "workflow-missing-permissions",
                "severity": "medium",
                "category": "workflow",
                "path": rel_path,
                "title": "Missing explicit permissions",
                "message": "Workflow does not declare explicit permissions. Default token permissions may be overly broad.",
                "recommendation": "Add 'permissions: contents: read' or more specific permissions.",
            })
        elif perms.get("all") == "write-all":
            result.findings.append({
                "id": "workflow-permissions-write-all",
                "severity": "high",
                "category": "workflow",
                "path": rel_path,
                "title": "Overly broad permissions: write-all",
                "message": "Workflow uses 'permissions: write-all' which grants maximum access.",
                "recommendation": "Use specific permissions instead of write-all.",
            })

        # Check actions
        actions = _parse_actions_used(content)
        for action_info in actions:
            if action_info["is_official"]:
                if not action_info["is_major_pin"] and not action_info["is_sha_pin"]:
                    result.findings.append({
                        "id": "workflow-action-unpinned",
                        "severity": "low",
                        "category": "workflow",
                        "path": rel_path,
                        "line": action_info["line"],
                        "title": f"Unpinned official action: {action_info['action']}",
                        "message": f"Action '{action_info['ref']}' is not pinned to a major version or SHA.",
                        "recommendation": f"Pin to a major version (e.g., @{action_info['action']}@v4) or SHA.",
                    })
            else:
                # Third-party action
                if not action_info["is_sha_pin"]:
                    sev = "medium" if not action_info["is_major_pin"] else "low"
                    result.findings.append({
                        "id": "workflow-third-party-action",
                        "severity": sev,
                        "category": "workflow",
                        "path": rel_path,
                        "line": action_info["line"],
                        "title": f"Third-party action: {action_info['action']}",
                        "message": f"Action '{action_info['ref']}' is not from a known official source and is not SHA-pinned.",
                        "recommendation": "Pin third-party actions to SHA for supply-chain security.",
                    })

    return result


def format_workflow_audit_markdown(result: WorkflowAuditResult) -> str:
    """Format workflow audit result as Markdown."""
    lines = [
        "# GitHub Actions Workflow Audit",
        "",
        f"**Workflows Scanned:** {result.workflows_scanned}",
        "",
    ]

    if result.findings:
        lines.append("## Findings")
        lines.append("")
        for i, f in enumerate(result.findings, 1):
            lines.append(f"### {i}. {f.get('title', 'Untitled')}")
            lines.append("")
            lines.append(f"- **ID:** {f.get('id', 'n/a')}")
            lines.append(f"- **Severity:** {f.get('severity', 'n/a')}")
            lines.append(f"- **Category:** {f.get('category', 'n/a')}")
            lines.append(f"- **Path:** `{f.get('path', 'n/a')}`")
            if f.get("line"):
                lines.append(f"- **Line:** {f['line']}")
            lines.append(f"- **Message:** {f.get('message', '')}")
            if f.get("recommendation"):
                lines.append(f"- **Recommendation:** {f['recommendation']}")
            lines.append("")
    else:
        lines.append("No findings.")
        lines.append("")

    lines.append("## Limitations")
    lines.append("")
    for lim in result.limitations:
        lines.append(f"- {lim}")
    lines.append("")

    return "\n".join(lines)
