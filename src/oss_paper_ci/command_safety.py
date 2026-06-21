"""Enhanced dangerous command detection for the reproduction orchestrator.

Extends the base DANGEROUS_PATTERNS from runner.py with additional patterns
specific to the orchestrator's safety model.  All commands are checked before
execution; dangerous commands are blocked unless the user modifies the config
(no --allow-dangerous flag is provided).
"""

from __future__ import annotations

import re

# Extended dangerous patterns for the orchestrator.
# These are checked in addition to runner.DANGEROUS_PATTERNS.
ORCHESTRATOR_DANGEROUS_PATTERNS: list[str] = [
    # Disk/filesystem destruction
    "rm -rf /",
    "rm -rf /*",
    "rmdir /s /q",
    "format ",
    "del /s",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",   # fork bomb
    "> /dev/sd",
    # Privilege escalation
    "sudo ",
    "su -",
    "chmod 777",
    "chown root",
    # Network exfiltration / remote code execution
    "curl | sh",
    "curl |bash",
    "curl|bash",
    "wget | sh",
    "wget | bash",
    "wget|bash",
    "curl.*\\|.*sh",
    "wget.*\\|.*sh",
    "powershell Invoke-Expression",
    "iwr.*\\|.*iex",
    "iex\\(",
    # Destructive git operations
    "git push",
    "git push --force",
    "git push -f",
    "git clean -fd",
    "git reset --hard",
    # Repository destruction
    "gh repo delete",
    "gh repo archive",
    # SSH key overwrite
    "ssh-keygen",
    # Package manager abuse
    "npm publish",
    "twine upload",
    "pip install --index-url",
    # Process/system manipulation
    "shutdown",
    "reboot",
    "halt",
    "poweroff",
    "kill -9 1",
    "killall",
    # Encoding evasion (base64 decode + execute)
    "base64 -d",
    "base64 --decode",
    "python -c \"import base64",
]

# Compiled regex for fast matching.
_ALL_PATTERNS = ORCHESTRATOR_DANGEROUS_PATTERNS
_DANGEROUS_RE = re.compile(
    "|".join(re.escape(p) if "\\|" not in p and "\\(" not in p else p
             for p in _ALL_PATTERNS),
    re.IGNORECASE,
)


def is_dangerous_command(command: str) -> bool:
    """Return True if *command* matches any known dangerous pattern.

    The check is intentionally conservative -- false positives are preferred
    over false negatives.  This is the orchestrator-level check; the base
    runner.py check is also called during execution.
    """
    # Also check the base patterns from runner.py
    from oss_paper_ci.runner import is_dangerous_command as _base_check
    if _base_check(command):
        return True
    return bool(_DANGEROUS_RE.search(command))


def check_command_allowlist(
    command: str,
    allowlist: list[str] | None = None,
) -> bool:
    """Check if a command is on the allowlist.

    If no allowlist is provided, all non-dangerous commands are allowed.
    If an allowlist is provided, the command must match one of the patterns.

    Returns True if the command is allowed.
    """
    if is_dangerous_command(command):
        return False
    if not allowlist:
        return True
    for pattern in allowlist:
        if pattern in command or command.startswith(pattern):
            return True
    return False


def get_block_reason(command: str) -> str:
    """Return a human-readable reason why a command was blocked."""
    if not is_dangerous_command(command):
        return ""
    # Find the matching pattern
    from oss_paper_ci.runner import DANGEROUS_PATTERNS
    for pat in DANGEROUS_PATTERNS:
        if pat.lower() in command.lower():
            return f"Blocked: matches dangerous pattern '{pat}'"
    for pat in ORCHESTRATOR_DANGEROUS_PATTERNS:
        try:
            if re.search(pat, command, re.IGNORECASE):
                return f"Blocked: matches dangerous pattern '{pat}'"
        except re.error:
            if pat.lower() in command.lower():
                return f"Blocked: matches dangerous pattern '{pat}'"
    return "Blocked: matches a dangerous command pattern"
