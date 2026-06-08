"""RES checks -- results directory, figures, and regeneration quality."""

from __future__ import annotations

import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


@register
class Res001ResultsDirectoryExists(BaseChecker):
    """RES001: Results directory exists."""

    check_id = "RES001"
    title = "Results directory exists"
    severity = Severity.WARNING

    _RESULT_DIRS = (
        "results",
        "output",
        "figures",
        "plots",
        "tables",
        "logs",
        "artifacts",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []
        for dirname in self._RESULT_DIRS:
            if ctx.has_file(dirname):
                found.append(dirname)

        if found:
            return [self._pass(
                f"Found results directories: {', '.join(found)}.",
                evidence=found,
            )]

        return [self._warn(
            "No results directories found.",
            recommendation=(
                "Create a results directory (e.g. results/, output/, figures/) "
                "to store experiment outputs so reviewers can inspect them."
            ),
        )]


@register
class Res002FiguresReferencedInReadmeExist(BaseChecker):
    """RES002: Figures referenced in README exist."""

    check_id = "RES002"
    title = "Figures referenced in README exist"
    severity = Severity.WARNING

    # Markdown image: ![alt](path)
    _MD_IMG_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
    # HTML img tag: <img src="path">
    _HTML_IMG_RE = re.compile(r'<img\s[^>]*src=["\']([^"\']+)["\']', re.IGNORECASE)

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        readme_content: str | None = None
        readme_name = ""
        for name in ("README.md", "README.rst", "README"):
            content = ctx.read_file(name)
            if content is not None:
                readme_content = content
                readme_name = name
                break

        if readme_content is None:
            return [self._pass(
                "No README found, skipping figure reference check.",
            )]

        # Collect all referenced image paths.
        refs: list[str] = []
        refs.extend(self._MD_IMG_RE.findall(readme_content))
        refs.extend(self._HTML_IMG_RE.findall(readme_content))

        if not refs:
            return [self._pass(
                "No figure references found in README.",
                evidence=[readme_name],
            )]

        missing: list[str] = []
        existing: list[str] = []
        for ref in refs:
            # Strip URL fragments and query strings for local paths.
            clean = ref.split("#")[0].split("?")[0]
            if clean.startswith(("http://", "https://", "data:")):
                continue
            if ctx.has_file(clean):
                existing.append(clean)
            else:
                missing.append(clean)

        if not missing:
            return [self._pass(
                f"All {len(existing)} referenced figures exist.",
                evidence=existing,
            )]

        return [self._warn(
            f"{len(missing)} referenced figure(s) not found: {', '.join(missing)}.",
            evidence=missing,
            recommendation=(
                "Ensure all images referenced in the README are committed "
                "to the repository, or update broken references."
            ),
        )]


@register
class Res003ResultsHaveGenerationScripts(BaseChecker):
    """RES003: Results have generation scripts."""

    check_id = "RES003"
    title = "Results have generation scripts"
    severity = Severity.INFO

    _RESULT_DIRS = ("results", "figures", "output", "plots", "tables")
    _SCRIPT_PATTERNS = ("plot", "generate", "make_figure", "visualize")
    _SCRIPT_DIRS = ("scripts", "src")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Only run if at least one results directory exists.
        has_results = any(ctx.has_file(d) for d in self._RESULT_DIRS)
        if not has_results:
            return [self._pass(
                "No results directories found; skipping generation script check.",
            )]

        found_scripts: list[str] = []

        # Check for script files matching known patterns.
        for f in ctx.files:
            name_lower = f.name.lower()
            if f.suffix != ".py":
                continue
            for script_dir in self._SCRIPT_DIRS:
                if str(f.parent) == script_dir or str(f.parent).startswith(script_dir + "/"):
                    for pattern in self._SCRIPT_PATTERNS:
                        if name_lower.startswith(pattern):
                            found_scripts.append(str(f))
                            break

        # Check Makefile for figure/result targets.
        makefile = ctx.read_file("Makefile")
        if makefile:
            target_re = re.compile(
                r"^[a-zA-Z0-9_.-]+\s*:(?:.*\n)*.*(?:figure|result|plot|table)",
                re.IGNORECASE | re.MULTILINE,
            )
            if target_re.search(makefile):
                found_scripts.append("Makefile (result-related targets)")

        if found_scripts:
            return [self._pass(
                f"Found generation scripts: {', '.join(found_scripts)}.",
                evidence=found_scripts,
            )]

        return [self._info(
            "No generation scripts found for results.",
            recommendation=(
                "Add scripts (e.g. plot_*.py, generate_*.py) that produce "
                "your figures and tables so results can be regenerated."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Create an INFO-severity result (checker severity is already INFO)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


@register
class Res004NoOrphanFigures(BaseChecker):
    """RES004: No orphan figures."""

    check_id = "RES004"
    title = "No orphan figures"
    severity = Severity.INFO

    _IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".eps"}

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Collect all image files, excluding ignored directories.
        image_files: list[str] = []
        for f in ctx.files:
            if f.suffix.lower() in self._IMAGE_EXTS:
                image_files.append(str(f))

        if not image_files:
            return [self._pass(
                "No image files found in the repository.",
            )]

        # Gather text content from README, paper/, and scripts/ for reference checking.
        searchable_text = ""
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content:
                searchable_text += content + "\n"
                break

        # Search for references in paper/ and scripts/ files.
        for f in ctx.files:
            f_str = str(f)
            if f_str.startswith("paper/") or f_str.startswith("scripts/") or f_str.startswith("src/"):
                if f.suffix in (".md", ".rst", ".tex", ".py", ".sh", ".yml", ".yaml"):
                    content = ctx.read_file(f_str)
                    if content:
                        searchable_text += content + "\n"

        # Check each image for references.
        orphans: list[str] = []
        referenced: list[str] = []
        for img in image_files:
            # Use the filename (and optionally parent path) for matching.
            img_name = img.rsplit("/", 1)[-1] if "/" in img else img
            if img_name in searchable_text or img in searchable_text:
                referenced.append(img)
            else:
                orphans.append(img)

        if not orphans:
            return [self._pass(
                f"All {len(image_files)} image file(s) are referenced.",
                evidence=referenced,
            )]

        return [self._info(
            f"{len(orphans)} unreferenced image(s) found: {', '.join(orphans)}.",
            evidence=orphans,
            recommendation=(
                "Remove unused image files or reference them in your "
                "README, paper, or scripts to keep the repository clean."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Create an INFO-severity result (checker severity is already INFO)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


@register
class Res005ResultRegenerationInstructions(BaseChecker):
    """RES005: Result regeneration instructions."""

    check_id = "RES005"
    title = "Result regeneration instructions"
    severity = Severity.INFO

    _REGEN_KEYWORDS = re.compile(
        r"\b(?:regenerat|re-run|rerun|reproduce\s+(?:figure|table|result))\b",
        re.IGNORECASE,
    )
    _MAKEFILE_RESULT_TARGET = re.compile(
        r"^[a-zA-Z0-9_.-]+\s*:(?:.*\n)*.*(?:figure|result|plot|table)",
        re.IGNORECASE | re.MULTILINE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found_evidence: list[str] = []

        # Check README for regeneration keywords.
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content and self._REGEN_KEYWORDS.search(content):
                found_evidence.append(f"{readme} (regeneration keywords)")
                break

        # Check Makefile for result-related targets.
        makefile = ctx.read_file("Makefile")
        if makefile and self._MAKEFILE_RESULT_TARGET.search(makefile):
            found_evidence.append("Makefile (result-related targets)")

        if found_evidence:
            return [self._pass(
                f"Found regeneration instructions: {', '.join(found_evidence)}.",
                evidence=found_evidence,
            )]

        return [self._info(
            "No result regeneration instructions found.",
            recommendation=(
                "Add instructions to your README (e.g. 'To reproduce Figure 1, "
                "run ...') or a Makefile with result-related targets so others "
                "can regenerate your results."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        """Create an INFO-severity result (checker severity is already INFO)."""
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )
