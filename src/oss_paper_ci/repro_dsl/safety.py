"""Safety checks for Reproducibility DSL v1.

Checks commands for dangerous patterns, undeclared network access,
undeclared installs, path traversal, secret exposure, and more.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from .schema import ReproDSL, StepSpec, SafetySpec


@dataclass
class SafetyFinding:
    """A single safety finding."""
    severity: str  # "blocked", "warning", "info"
    category: str  # "command", "path", "network", "install", "secret", "gpu"
    step_id: str  # "" for global findings
    message: str
    pattern: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = {
            "severity": self.severity,
            "category": self.category,
            "step_id": self.step_id,
            "message": self.message,
        }
        if self.pattern:
            d["pattern"] = self.pattern
        return d


@dataclass
class SafetyReport:
    """Complete safety report for a DSL specification."""
    findings: list[SafetyFinding]
    blocked_commands: list[str]  # step_ids with blocked commands
    requires_explicit_execute: bool
    requires_network: bool
    requires_install: bool
    safety_level: str  # "safe", "caution", "blocked"

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": [f.to_dict() for f in self.findings],
            "blocked_commands": sorted(self.blocked_commands),
            "requires_explicit_execute": self.requires_explicit_execute,
            "requires_network": self.requires_network,
            "requires_install": self.requires_install,
            "safety_level": self.safety_level,
        }

    @property
    def has_blocks(self) -> bool:
        return len(self.blocked_commands) > 0

    @property
    def has_warnings(self) -> bool:
        return any(f.severity == "warning" for f in self.findings)


# Dangerous command patterns that are always blocked
BLOCKED_PATTERNS: list[tuple[str, str]] = [
    (r'\brm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/\s*$', "rm -rf /"),
    (r'\brm\s+-rf\s+/', "rm -rf / (root)"),
    (r'curl\s.*\|\s*(ba)?sh', "curl pipe to shell"),
    (r'wget\s.*\|\s*(ba)?sh', "wget pipe to shell"),
    (r'\bsudo\b', "sudo command"),
    (r'\bchmod\s+777\s+/', "chmod 777 on system path"),
    (r'>\s*/etc/', "write to /etc/"),
    (r'>\s*/usr/', "write to /usr/"),
    (r'>\s*/bin/', "write to /bin/"),
    (r'>\s*/sbin/', "write to /sbin/"),
    (r'\bmkfs\b', "filesystem format"),
    (r'\bdd\s+.*of=', "dd write"),
    (r':\(\)\s*\{.*\|.*&\s*\}', "fork bomb"),
]

# Patterns indicating network usage
NETWORK_PATTERNS: list[tuple[str, str]] = [
    (r'\bcurl\b', "curl"),
    (r'\bwget\b', "wget"),
    (r'\bgit\s+clone\b', "git clone"),
    (r'\bgit\s+pull\b', "git pull"),
    (r'\bgit\s+fetch\b', "git fetch"),
    (r'\bpip\s+install\b', "pip install"),
    (r'\bpip3\s+install\b', "pip3 install"),
    (r'\bconda\s+install\b', "conda install"),
    (r'\bnpm\s+install\b', "npm install"),
    (r'\bnpx\b', "npx"),
    (r'\byarn\s+add\b', "yarn add"),
    (r'\bcargo\s+install\b', "cargo install"),
    (r'\bmaven\b.*download|maven\b.*resolve', "maven download"),
    (r'\bapt-get\s+install\b', "apt-get install"),
    (r'\bapt\s+install\b', "apt install"),
    (r'\byum\s+install\b', "yum install"),
    (r'\bbrew\s+install\b', "brew install"),
]

# Patterns indicating install operations
INSTALL_PATTERNS: list[tuple[str, str]] = [
    (r'\bpip\s+install\b', "pip install"),
    (r'\bpip3\s+install\b', "pip3 install"),
    (r'\bconda\s+install\b', "conda install"),
    (r'\bnpm\s+install\b', "npm install"),
    (r'\byarn\s+install\b', "yarn install"),
    (r'\bcargo\s+install\b', "cargo install"),
    (r'\bapt-get\s+install\b', "apt-get install"),
    (r'\bapt\s+install\b', "apt install"),
    (r'\bpackage\.restore\b', "dotnet restore"),
    (r'\bnuget\s+restore\b', "nuget restore"),
    (r'\bcomposer\s+install\b', "composer install"),
    (r'\bgem\s+install\b', "gem install"),
    (r'\binstall\b.*\brequirements\b', "install requirements"),
    (r'\binstall\b.*\bdependencies\b', "install dependencies"),
]

# Patterns indicating secret/token exposure
SECRET_PATTERNS: list[tuple[str, str]] = [
    (r'\$[A-Z_]*SECRET[A-Z_]*', "environment variable containing SECRET"),
    (r'\$[A-Z_]*TOKEN[A-Z_]*', "environment variable containing TOKEN"),
    (r'\$[A-Z_]*PASSWORD[A-Z_]*', "environment variable containing PASSWORD"),
    (r'\$[A-Z_]*API_KEY[A-Z_]*', "environment variable containing API_KEY"),
    (r'\$[A-Z_]*AWS_SECRET[A-Z_]*', "AWS secret key"),
    (r'\becho\s+.*\$[A-Z_]*(SECRET|TOKEN|PASSWORD|KEY)', "echo secret variable"),
    (r'\bcat\s+.*\.env\b', "reading .env file"),
]

# System path patterns
SYSTEM_PATH_PATTERNS: list[str] = [
    r'^/',
    r'/etc/',
    r'/usr/',
    r'/bin/',
    r'/sbin/',
    r'/root/',
    r'/home/',
    r'/var/',
    r'/tmp/',
    r'\.\./',  # path traversal
]


def check_command_safety(command: str, step_id: str, safety: SafetySpec) -> list[SafetyFinding]:
    """Check a single command for safety issues.

    Returns findings for:
    - Blocked patterns (always dangerous)
    - Undeclared network usage
    - Undeclared install operations
    - Secret/token exposure
    """
    findings = []
    cmd_lower = command.lower()

    # Check blocked patterns
    for pattern, desc in BLOCKED_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            findings.append(SafetyFinding(
                severity="blocked",
                category="command",
                step_id=step_id,
                message=f"Blocked: {desc}",
                pattern=pattern,
            ))

    # Check undeclared network
    if not safety.network:
        for pattern, desc in NETWORK_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                findings.append(SafetyFinding(
                    severity="warning",
                    category="network",
                    step_id=step_id,
                    message=f"Undeclared network usage: {desc}",
                    pattern=pattern,
                ))

    # Check undeclared install
    if not safety.allow_install:
        for pattern, desc in INSTALL_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                findings.append(SafetyFinding(
                    severity="warning",
                    category="install",
                    step_id=step_id,
                    message=f"Undeclared install operation: {desc}",
                    pattern=pattern,
                ))

    # Check secret exposure
    for pattern, desc in SECRET_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            findings.append(SafetyFinding(
                severity="warning",
                category="secret",
                step_id=step_id,
                message=f"Potential secret exposure: {desc}",
                pattern=pattern,
            ))

    return findings


def check_path_safety(path: str, step_id: str) -> list[SafetyFinding]:
    """Check a path for safety issues (traversal, system paths)."""
    findings = []
    if '..' in path:
        findings.append(SafetyFinding(
            severity="warning",
            category="path",
            step_id=step_id,
            message=f"Path traversal detected: {path}",
        ))
    for pattern in SYSTEM_PATH_PATTERNS[:6]:  # absolute system paths
        if re.match(pattern, path):
            findings.append(SafetyFinding(
                severity="warning",
                category="path",
                step_id=step_id,
                message=f"Absolute system path: {path}",
            ))
            break
    return findings


def check_dsl_safety(dsl: ReproDSL) -> SafetyReport:
    """Run all safety checks on a DSL specification.

    Checks:
    1. All step commands for dangerous patterns
    2. All declared paths for traversal/system paths
    3. Safety declarations vs actual command content
    4. Secret exposure in commands
    """
    findings: list[SafetyFinding] = []
    blocked_commands: list[str] = []
    requires_network = False
    requires_install = False

    # Check each step
    for step_id in sorted(dsl.steps.keys()):
        step = dsl.steps[step_id]
        step_findings = check_command_safety(step.command, step_id, dsl.safety)
        findings.extend(step_findings)

        # Track blocked
        if any(f.severity == "blocked" for f in step_findings):
            blocked_commands.append(step_id)

        # Track network/install requirements
        if any(f.category == "network" for f in step_findings):
            requires_network = True
        if any(f.category == "install" for f in step_findings):
            requires_install = True

        # Check produced paths
        for path in step.produces:
            findings.extend(check_path_safety(path, step_id))

    # Check dataset paths
    for ds_id in sorted(dsl.datasets.keys()):
        ds = dsl.datasets[ds_id]
        findings.extend(check_path_safety(ds.path, ""))

    # Check artifact paths
    for artifact in dsl.artifacts:
        findings.extend(check_path_safety(artifact.path, ""))

    # Determine safety level
    if blocked_commands:
        safety_level = "blocked"
    elif any(f.severity == "warning" for f in findings):
        safety_level = "caution"
    else:
        safety_level = "safe"

    requires_explicit_execute = bool(blocked_commands or requires_network or requires_install)

    return SafetyReport(
        findings=findings,
        blocked_commands=blocked_commands,
        requires_explicit_execute=requires_explicit_execute,
        requires_network=requires_network,
        requires_install=requires_install,
        safety_level=safety_level,
    )
