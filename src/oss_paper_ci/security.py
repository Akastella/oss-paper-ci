"""Security scanning module: secrets, dangerous patterns, package risks."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Secret patterns (redacted output only)
SECRET_PATTERNS = [
    {
        "id": "openai-api-key",
        "pattern": r"sk-[a-zA-Z0-9]{20,}T3Bl[a-zA-Z0-9]{4}FJ[a-zA-Z0-9]{20,}",
        "title": "OpenAI API Key",
        "severity": "high",
    },
    {
        "id": "github-token",
        "pattern": r"(ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{30,}",
        "title": "GitHub Token",
        "severity": "high",
    },
    {
        "id": "aws-access-key",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "title": "AWS Access Key ID",
        "severity": "high",
    },
    {
        "id": "private-key-block",
        "pattern": r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
        "title": "Private Key Block",
        "severity": "high",
    },
    {
        "id": "generic-bearer",
        "pattern": r"Bearer\s+[a-zA-Z0-9\-._~+/]+=*",
        "title": "Generic Bearer Token",
        "severity": "medium",
    },
    {
        "id": "generic-api-key",
        "pattern": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[a-zA-Z0-9\-._]{16,}",
        "title": "Generic API Key",
        "severity": "medium",
    },
]

# Dangerous shell patterns
DANGEROUS_SHELL_PATTERNS = [
    {
        "id": "curl-pipe-bash",
        "pattern": r"curl\s+.*\|\s*(ba)?sh",
        "title": "Curl pipe to shell",
        "severity": "high",
        "recommendation": "Download scripts first, review, then execute.",
    },
    {
        "id": "wget-pipe-sh",
        "pattern": r"wget\s+.*\|\s*(ba)?sh",
        "title": "Wget pipe to shell",
        "severity": "high",
        "recommendation": "Download scripts first, review, then execute.",
    },
    {
        "id": "rm-rf-root",
        "pattern": r"rm\s+-[a-z]*r[a-z]*f[a-z]*\s+/",
        "title": "Recursive force delete from root",
        "severity": "high",
        "recommendation": "Never delete from root. Use explicit paths.",
    },
    {
        "id": "sudo-in-ci",
        "pattern": r"\bsudo\b",
        "title": "Sudo usage",
        "severity": "medium",
        "recommendation": "Avoid sudo in CI; use containers or explicit permissions.",
    },
    {
        "id": "chmod-777",
        "pattern": r"chmod\s+777",
        "title": "World-writable permissions",
        "severity": "medium",
        "recommendation": "Use more restrictive permissions (e.g., 755 or 644).",
    },
    {
        "id": "eval-variable",
        "pattern": r"eval\s+\$",
        "title": "Eval with variable",
        "severity": "high",
        "recommendation": "Avoid eval with variables; use arrays or functions.",
    },
    {
        "id": "unsafe-pickle",
        "pattern": r"pickle\.load",
        "title": "Unsafe pickle load",
        "severity": "high",
        "recommendation": "Pickle can execute arbitrary code. Use safer formats like JSON.",
    },
]

# .env patterns
ENV_FILE_PATTERN = re.compile(r"^\.env(\..+)?$", re.IGNORECASE)

# Directories to skip
SKIP_DIRS = {
    ".git", "venv", ".venv", "node_modules", "target", "dist", "build",
    "site", "release-artifacts", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".oss-paper-ci-repro", ".oss-paper-ci-cache", ".oss-paper-ci-capsule-staging",
    "egg-info",
}


@dataclass
class SecurityScanResult:
    """Result of a security scan."""

    findings: list[dict[str, Any]] = field(default_factory=list)
    files_scanned: int = 0
    limitations: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "findings": self.findings,
            "files_scanned": self.files_scanned,
            "limitations": self.limitations,
        }


def redact_secret(value: str, show_chars: int = 4) -> str:
    """Redact a secret value, showing only the first and last few characters."""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return f"{value[:show_chars]}...{value[-show_chars:]}"


def _should_skip_dir(dirname: str) -> bool:
    """Check if directory should be skipped."""
    name = Path(dirname).name
    return name in SKIP_DIRS or name.endswith(".egg-info")


def _is_text_file(path: Path) -> bool:
    """Heuristic check if file is text-based."""
    try:
        # Check common text extensions
        text_exts = {
            ".py", ".yml", ".yaml", ".json", ".md", ".txt", ".toml", ".cfg",
            ".ini", ".sh", ".bash", ".zsh", ".fish", ".ps1", ".bat", ".cmd",
            ".html", ".css", ".js", ".ts", ".jsx", ".tsx", ".xml", ".rst",
            ".dockerfile", ".env", ".gitignore", ".dockerignore",
            ".pem", ".crt", ".key",
        }
        if path.suffix.lower() in text_exts:
            return True
        if path.name.lower() in {"makefile", "dockerfile", "procfile", "vagrantfile"}:
            return True
        # Check if no extension (could be script)
        if not path.suffix:
            return True
        return False
    except Exception:
        return False


def scan_file(path: Path, root: Path) -> list[dict[str, Any]]:
    """Scan a single file for security issues."""
    findings = []
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return findings

    rel_path = str(path.relative_to(root)).replace("\\", "/")

    # Check secret patterns
    for pat in SECRET_PATTERNS:
        for match in re.finditer(pat["pattern"], content):
            matched_text = match.group(0)
            line_num = content[:match.start()].count("\n") + 1
            findings.append({
                "id": pat["id"],
                "severity": pat["severity"],
                "category": "secret",
                "path": rel_path,
                "line": line_num,
                "title": pat["title"],
                "message": f"Possible {pat['title']} detected.",
                "redacted_preview": redact_secret(matched_text),
                "redacted": True,
                "recommendation": "Remove secret from code. Use environment variables or a secrets manager.",
            })

    # Check dangerous shell patterns
    for pat in DANGEROUS_SHELL_PATTERNS:
        for match in re.finditer(pat["pattern"], content, re.IGNORECASE):
            line_num = content[:match.start()].count("\n") + 1
            findings.append({
                "id": pat["id"],
                "severity": pat["severity"],
                "category": "execution",
                "path": rel_path,
                "line": line_num,
                "title": pat["title"],
                "message": f"Dangerous shell pattern detected: {match.group(0)[:60]}",
                "recommendation": pat.get("recommendation", "Review and fix."),
            })

    return findings


def run_security_scan(repo_path: str | Path) -> SecurityScanResult:
    """Run a full security scan on the repository."""
    import os

    root = Path(repo_path).resolve()
    result = SecurityScanResult(
        limitations=[
            "Pattern-based detection; may produce false positives.",
            "Does not scan binary files or archives.",
            "Secret detection is heuristic; not all secret types are covered.",
            "Does not execute code; static analysis only.",
        ]
    )

    for current_dir, dirnames, filenames in os.walk(root):
        current_path = Path(current_dir)
        # Filter out skip directories in-place
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]

        for filename in filenames:
            filepath = current_path / filename
            if not filepath.is_file():
                continue
            if not _is_text_file(filepath):
                continue

            result.files_scanned += 1
            file_findings = scan_file(filepath, root)
            result.findings.extend(file_findings)

    # Check for .env committed
    for current_dir, dirnames, filenames in os.walk(root):
        current_path = Path(current_dir)
        dirnames[:] = [d for d in dirnames if not _should_skip_dir(d)]
        for filename in filenames:
            if ENV_FILE_PATTERN.match(filename):
                rel_path = str((current_path / filename).relative_to(root)).replace("\\", "/")
                result.findings.append({
                    "id": "env-file-committed",
                    "severity": "medium",
                    "category": "secret",
                    "path": rel_path,
                    "title": "Environment file committed",
                    "message": f"File '{filename}' appears to be an environment file. It may contain secrets.",
                    "recommendation": "Add .env files to .gitignore and remove from history if secrets were committed.",
                })

    return result


def format_security_scan_markdown(result: SecurityScanResult) -> str:
    """Format security scan result as Markdown."""
    lines = [
        "# Security Scan Report",
        "",
        f"**Files Scanned:** {result.files_scanned}",
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
            if f.get("redacted_preview"):
                lines.append(f"- **Preview:** `{f['redacted_preview']}`")
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
