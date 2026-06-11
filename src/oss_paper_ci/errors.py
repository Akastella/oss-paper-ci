"""Structured error handling for user-friendly error display.

Provides error codes, structured error information, and formatted output.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OssPaperError:
    """Structured error with user-friendly information."""
    code: str
    what: str
    why: str = ""
    next_steps: list[str] = field(default_factory=list)
    retry_command: str = ""
    docs_url: str = ""
    traceback: str = ""

    def to_dict(self) -> dict:
        d = {
            "error_code": self.code,
            "what": self.what,
        }
        if self.why:
            d["why"] = self.why
        if self.next_steps:
            d["next_steps"] = self.next_steps
        if self.retry_command:
            d["retry_command"] = self.retry_command
        if self.docs_url:
            d["docs_url"] = self.docs_url
        return d


# Predefined error codes
ERRORS = {
    "E001": OssPaperError(
        code="E001",
        what="Repository path does not exist.",
        why="The specified path was not found on disk.",
        next_steps=["Check the path spelling.", "Use '.' for the current directory."],
        retry_command="oss-paper-ci scan .",
    ),
    "E002": OssPaperError(
        code="E002",
        what="Configuration file not found or invalid.",
        why="The config file could not be parsed as valid YAML.",
        next_steps=[
            "Run 'oss-paper-ci config validate' to check your config.",
            "Run 'oss-paper-ci init' to generate a fresh config.",
        ],
        retry_command="oss-paper-ci init --dry-run",
    ),
    "E003": OssPaperError(
        code="E003",
        what="Output directory already exists.",
        why="The target output directory already contains files.",
        next_steps=[
            "Use --force to overwrite.",
            "Choose a different --output-dir.",
        ],
    ),
    "E004": OssPaperError(
        code="E004",
        what="Required dependency not available.",
        why="A Python package needed for this feature is not installed.",
        next_steps=[
            "Install dev dependencies: pip install -e '.[dev]'",
            "Check your Python environment.",
        ],
    ),
    "E005": OssPaperError(
        code="E005",
        what="Scan failed with errors.",
        why="One or more checks could not complete.",
        next_steps=[
            "Run with --verbose for detailed output.",
            "Check the error messages above.",
        ],
        retry_command="oss-paper-ci scan . --verbose",
    ),
    "E006": OssPaperError(
        code="E006",
        what="Workbench step failed.",
        why="One or more workbench pipeline steps encountered errors.",
        next_steps=[
            "Review the step status in the summary above.",
            "Run the failing command individually for more detail.",
            "Check the output directory for partial results.",
        ],
    ),
    "E007": OssPaperError(
        code="E007",
        what="Theme not found.",
        why="The specified theme name is not available.",
        next_steps=[
            "Run 'oss-paper-ci theme list' to see available themes.",
            "Use 'classic', 'minimal', or 'contrast'.",
        ],
    ),
}


def get_error(code: str) -> OssPaperError | None:
    """Get a predefined error by code."""
    return ERRORS.get(code)


def format_error_plain(error: OssPaperError, debug: bool = False) -> str:
    """Format error for plain text display."""
    lines = [f"Error [{error.code}]: {error.what}"]
    if error.why:
        lines.append(f"  Why: {error.why}")
    if error.next_steps:
        lines.append("  Suggested next steps:")
        for i, step in enumerate(error.next_steps, 1):
            lines.append(f"    {i}. {step}")
    if error.retry_command:
        lines.append(f"  Retry: {error.retry_command}")
    if error.docs_url:
        lines.append(f"  Docs: {error.docs_url}")
    if debug and error.traceback:
        lines.append(f"\n  Traceback:\n{error.traceback}")
    return "\n".join(lines)
