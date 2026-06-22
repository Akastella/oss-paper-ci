"""README command mining: extract install/run/evaluate commands from documentation.

Scans README.md, docs/, and other markdown/text files for fenced code blocks,
inline commands, and common patterns that indicate reproducibility steps.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CommandCandidate:
    """A candidate command extracted from documentation or config files."""

    id: str = ""
    command: str = ""
    source: str = ""
    line: int = 0
    kind: str = "unknown"  # install | train | evaluate | test | figure | data | unknown
    confidence: float = 0.0
    dangerous: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "command": self.command,
            "source": self.source,
            "line": self.line,
            "kind": self.kind,
            "confidence": self.confidence,
            "dangerous": self.dangerous,
            "reason": self.reason,
        }


# Patterns for classifying command kind from surrounding text
_KIND_PATTERNS: list[tuple[str, list[str]]] = [
    ("install", [
        r"install", r"setup", r"depend", r"requir", r"pip\s+install",
        r"conda\s+install", r"npm\s+install", r"apt\s+install",
        r"brew\s+install", r"environment", r"venv", r"virtualenv",
    ]),
    ("train", [
        r"train", r"fit", r"finetune", r"fine-tune", r"epoch",
        r"learn", r"model", r"gpu", r"cuda",
    ]),
    ("evaluate", [
        r"evaluat", r"assess", r"metric", r"score", r"accura",
        r"benchmark", r"test\s+model", r"predict", r"infer",
    ]),
    ("test", [
        r"test", r"pytest", r"unittest", r"check", r"lint", r"verify",
    ]),
    ("figure", [
        r"figure", r"plot", r"chart", r"visuali", r"graph", r"draw",
        r"matplotlib", r"seaborn", r"plotly",
    ]),
    ("data", [
        r"data", r"download", r"fetch", r"preprocess", r"clean",
        r"split", r"augment", r"dataset",
    ]),
]

# Patterns that indicate dangerous commands
_DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/", r"sudo\s+", r"curl\s*\|\s*sh", r"wget\s*\|\s*sh",
    r"chmod\s+777", r"mkfs", r"dd\s+if=", r"format\s+[a-zA-Z]:",
    r"git\s+push", r"npm\s+publish", r"twine\s+upload",
    r"shutdown", r"reboot", r"kill\s+-9\s+1",
]

_DANGEROUS_RE = re.compile("|".join(_DANGEROUS_PATTERNS), re.IGNORECASE)


def mine_readme_commands(repo_path: str) -> list[CommandCandidate]:
    """Mine commands from README and documentation files.

    Args:
        repo_path: Path to the repository root.

    Returns:
        List of CommandCandidate objects, sorted by source and line.
    """
    root = Path(repo_path)
    candidates: list[CommandCandidate] = []

    # Find README and doc files
    doc_files = _find_doc_files(root)

    for doc_file in doc_files:
        try:
            text = doc_file.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        rel_path = str(doc_file.relative_to(root))
        candidates.extend(_extract_from_markdown(text, rel_path))

    # Deduplicate and assign stable IDs
    candidates = _deduplicate(candidates)
    _assign_ids(candidates)

    return candidates


def _find_doc_files(root: Path) -> list[Path]:
    """Find README and documentation files."""
    files: list[Path] = []

    # README files at root
    for pattern in ["README*", "readme*"]:
        files.extend(root.glob(pattern))

    # docs/ directory
    docs_dir = root / "docs"
    if docs_dir.is_dir():
        files.extend(docs_dir.glob("**/*.md"))
        files.extend(docs_dir.glob("**/*.rst"))
        files.extend(docs_dir.glob("**/*.txt"))

    # INSTALL / CONTRIBUTING / SETUP files
    for name in ["INSTALL*", "CONTRIBUTING*", "SETUP*", "USAGE*"]:
        files.extend(root.glob(name))

    return [f for f in files if f.is_file()]


def _extract_from_markdown(text: str, source: str) -> list[CommandCandidate]:
    """Extract commands from a markdown document."""
    candidates: list[CommandCandidate] = []
    lines = text.split("\n")

    # Extract fenced code blocks
    candidates.extend(_extract_fenced_blocks(lines, source))

    # Extract inline commands (backtick-wrapped commands)
    candidates.extend(_extract_inline_commands(lines, source))

    return candidates


def _extract_fenced_blocks(lines: list[str], source: str) -> list[CommandCandidate]:
    """Extract commands from fenced code blocks (```bash, ```sh, etc.)."""
    candidates: list[CommandCandidate] = []
    in_block = False
    block_lang = ""
    block_start = 0
    block_lines: list[str] = []
    section_heading = ""

    for i, line in enumerate(lines):
        # Track section headings for context
        if line.startswith("#"):
            section_heading = line.lstrip("#").strip().lower()

        # Start of fenced block
        fence_match = re.match(r"^```(\w*)", line.strip())
        if fence_match and not in_block:
            in_block = True
            block_lang = fence_match.group(1).lower()
            block_start = i + 1  # 1-based
            block_lines = []
            continue

        # End of fenced block
        if line.strip().startswith("```") and in_block and len(block_lines) > 0:
            in_block = False
            if block_lang in ("bash", "sh", "shell", "zsh", "console", "terminal", ""):
                candidates.extend(
                    _parse_block_commands(block_lines, source, block_start, section_heading)
                )
            block_lines = []
            continue

        if in_block:
            block_lines.append(line)

    return candidates


def _extract_inline_commands(lines: list[str], source: str) -> list[CommandCandidate]:
    """Extract inline commands wrapped in backticks."""
    candidates: list[CommandCandidate] = []
    section_heading = ""

    for i, line in enumerate(lines):
        if line.startswith("#"):
            section_heading = line.lstrip("#").strip().lower()

        # Match `command` patterns that look like shell commands
        for m in re.finditer(r"`([^`]+)`", line):
            cmd = m.group(1).strip()
            if _looks_like_command(cmd):
                kind = _classify_command(cmd, section_heading)
                candidates.append(CommandCandidate(
                    command=cmd,
                    source=source,
                    line=i + 1,
                    kind=kind,
                    confidence=0.5,
                    dangerous=bool(_DANGEROUS_RE.search(cmd)),
                    reason=f"Inline command in {source}:{i+1}",
                ))

    return candidates


def _parse_block_commands(
    block_lines: list[str],
    source: str,
    start_line: int,
    section_heading: str,
) -> list[CommandCandidate]:
    """Parse individual commands from a code block."""
    candidates: list[CommandCandidate] = []

    for j, raw_line in enumerate(block_lines):
        line = raw_line.strip()

        # Skip comments and empty lines
        if not line or line.startswith("#"):
            continue

        # Skip lines that are clearly not commands
        if line.startswith("$ ") or line.startswith("> "):
            line = line[2:]

        # Handle multi-line continuations
        if line.endswith("\\"):
            # Collect continuation lines
            combined = line.rstrip("\\")
            for k in range(j + 1, len(block_lines)):
                next_line = block_lines[k].strip()
                if next_line.endswith("\\"):
                    combined += " " + next_line.rstrip("\\")
                else:
                    combined += " " + next_line
                    break
            line = combined

        # Skip if it doesn't look like a command
        if not _looks_like_command(line):
            continue

        kind = _classify_command(line, section_heading)
        candidates.append(CommandCandidate(
            command=line,
            source=source,
            line=start_line + j,
            kind=kind,
            confidence=0.7,
            dangerous=bool(_DANGEROUS_RE.search(line)),
            reason=f"Code block in {source}:{start_line+j}, section '{section_heading}'",
        ))

    return candidates


def _looks_like_command(text: str) -> bool:
    """Check if text looks like a shell command."""
    # Common command prefixes
    cmd_prefixes = [
        "python", "python3", "pip", "pip3", "conda", "jupyter",
        "Rscript", "R ", "julia", "node", "npm", "npx",
        "cargo", "java", "javac", "mvn", "gradle",
        "make", "cmake", "gcc", "g++", "clang",
        "bash", "sh", "zsh", "source",
        "docker", "singularity",
        "snakemake", "nextflow",
        "git clone", "git pull",
        "curl", "wget",
        "ls", "cd", "mkdir", "cp", "mv",
        "export", "echo", "cat",
        "pytest", "unittest",
        "sphinx", "mkdocs",
    ]

    text_lower = text.lower().strip()
    for prefix in cmd_prefixes:
        if text_lower.startswith(prefix.lower()):
            return True

    # Check for common patterns
    if re.match(r"^[a-zA-Z_][\w-]*\s", text):
        # Looks like "command args..."
        return True

    # Check for environment variable assignment
    if re.match(r"^[A-Z_]+=", text):
        return True

    return False


def _classify_command(command: str, section_heading: str) -> str:
    """Classify a command's kind based on content and context."""
    combined = (command + " " + section_heading).lower()

    for kind, patterns in _KIND_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return kind

    return "unknown"


def _deduplicate(candidates: list[CommandCandidate]) -> list[CommandCandidate]:
    """Remove duplicate commands."""
    seen: set[str] = set()
    result: list[CommandCandidate] = []

    for c in candidates:
        key = (c.command, c.source)
        if key not in seen:
            seen.add(key)
            result.append(c)

    return result


def _assign_ids(candidates: list[CommandCandidate]) -> None:
    """Assign stable IDs to candidates based on kind and order."""
    counters: dict[str, int] = {}

    for c in candidates:
        kind = c.kind if c.kind != "unknown" else "cmd"
        count = counters.get(kind, 0) + 1
        counters[kind] = count
        if count == 1:
            c.id = kind
        else:
            c.id = f"{kind}_{count}"


def format_commands_markdown(candidates: list[CommandCandidate]) -> str:
    """Format command candidates as markdown."""
    lines: list[str] = []
    lines.append("# README Command Candidates")
    lines.append("")

    if not candidates:
        lines.append("No commands found in documentation files.")
        return "\n".join(lines)

    lines.append(f"Found **{len(candidates)}** candidate command(s).")
    lines.append("")
    lines.append("| ID | Kind | Command | Source | Confidence |")
    lines.append("|-----|------|---------|--------|------------|")

    for c in candidates:
        danger = " ⚠️" if c.dangerous else ""
        cmd_display = c.command[:60] + ("..." if len(c.command) > 60 else "")
        lines.append(
            f"| {c.id} | {c.kind} | `{cmd_display}`{danger} | {c.source}:{c.line} | {c.confidence:.2f} |"
        )

    lines.append("")
    return "\n".join(lines)
