"""Text scanning utilities for repository content analysis."""

from __future__ import annotations

import re
from pathlib import Path


def find_urls(text: str) -> list[str]:
    """Extract URLs from text."""
    return re.findall(r"https?://[^\s\)\]\}\"\'>]+", text)


def find_paths_in_text(text: str) -> list[str]:
    """Find file/directory paths mentioned in text."""
    # Match patterns like path/to/file or ./path
    paths = re.findall(r'(?:^|\s)([.\/\w][\w./\-]+\.\w+)', text, re.MULTILINE)
    return list(set(paths))


def find_commands_in_text(text: str) -> list[str]:
    """Find shell commands mentioned in text (code blocks, inline code)."""
    commands = []
    # Find code blocks
    for match in re.finditer(r'```(?:bash|sh|shell)?\s*\n(.*?)```', text, re.DOTALL):
        for line in match.group(1).strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                commands.append(line)
    # Find inline commands
    for match in re.finditer(r'`([^`]+)`', text):
        cmd = match.group(1).strip()
        if any(cmd.startswith(p) for p in ['python', 'pip', 'conda', 'make', 'bash', 'sh', './', 'docker']):
            commands.append(cmd)
    return commands


def has_seed_setting(text: str) -> bool:
    """Check if text contains random seed setting patterns."""
    patterns = [
        r'seed\s*=\s*\d+',
        r'random\.seed\s*\(',
        r'np\.random\.seed\s*\(',
        r'torch\.manual_seed\s*\(',
        r'tf\.random\.set_seed\s*\(',
        r'set_seed\s*\(',
        r'RANDOM_SEED',
        r'SEED\s*=',
    ]
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def extract_headings(text: str) -> list[str]:
    """Extract markdown headings from text."""
    return re.findall(r'^#{1,6}\s+(.+)$', text, re.MULTILINE)
