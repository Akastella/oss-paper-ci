"""PAP checks -- paper / manuscript reproducibility checks."""

from __future__ import annotations

import re
from pathlib import PurePosixPath

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


# ---------------------------------------------------------------------------
# PAP001 -- Paper directory detected
# ---------------------------------------------------------------------------


@register
class Pap001PaperDirectory(BaseChecker):
    """PAP001: Detect paper / manuscript directories and .tex files."""

    check_id = "PAP001"
    title = "Paper directory detected"
    severity = Severity.INFO

    _PAPER_DIRS = ("paper", "manuscript", "latex", "tex", "docs/paper")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found_dirs: list[str] = []
        for d in self._PAPER_DIRS:
            if ctx.has_file(d):
                # Verify it is actually a directory (not a stray file).
                if (ctx.root / d).is_dir():
                    found_dirs.append(d + "/")

        found_tex = [
            str(f)
            for f in ctx.files
            if f.suffix == ".tex"
        ]

        evidence = found_dirs + found_tex

        if evidence:
            return [self._info(
                "Found paper-related files: {}.".format(", ".join(evidence)),
                evidence=evidence,
            )]

        return [self._info(
            "No paper or manuscript files detected.",
            recommendation=(
                "If your project includes a paper, consider placing it in a "
                "paper/, manuscript/, or latex/ directory."
            ),
        )]

    def _info(
        self,
        message: str,
        evidence: list[str] | None = None,
        recommendation: str = "",
    ) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


# ---------------------------------------------------------------------------
# PAP002 -- README commands match existing scripts
# ---------------------------------------------------------------------------


@register
class Pap002ReadmeCommandsMatchScripts(BaseChecker):
    """PAP002: Check that script paths referenced in README code blocks exist."""

    check_id = "PAP002"
    title = "README commands match existing scripts"
    severity = Severity.WARNING

    # Match fenced code blocks and capture the language tag + body.
    _CODE_BLOCK_RE = re.compile(r"```(\w*)\n(.*?)```", re.DOTALL)

    # Patterns that invoke a script file as an argument to an interpreter or
    # directly.  Each group captures a candidate script path.
    _SCRIPT_PATTERNS: list[re.Pattern[str]] = [
        # python script.py / python3 script.py
        re.compile(r"python3?\s+(?:(?:-\S+\s+)*)(\S+\.py)"),
        # bash script.sh / sh script.sh
        re.compile(r"(?:ba)?sh\s+(?:(?:-\S+\s+)*)(\S+\.sh)"),
        # Rscript script.R
        re.compile(r"Rscript\s+(\S+\.R)"),
        # julia script.jl
        re.compile(r"julia\s+(\S+\.jl)"),
        # Direct ./script.sh or bash ./script.sh
        re.compile(r"(?:\./|bash\s+\.\/)(\S+\.(?:sh|py|R|jl))"),
    ]

    _COMMAND_LANGS = {"bash", "sh", "shell", "zsh", "console", "python", "py"}

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        readme = self._find_readme(ctx)
        if readme is None:
            return [self._pass("No README found; skipping command check.")]

        missing: list[str] = []
        found: list[str] = []

        for match in self._CODE_BLOCK_RE.finditer(readme):
            lang = match.group(1).lower()
            block = match.group(2)

            # Only inspect blocks that look like shell / python commands.
            if lang and lang not in self._COMMAND_LANGS:
                continue

            for pattern in self._SCRIPT_PATTERNS:
                for script_match in pattern.finditer(block):
                    script_path = script_match.group(1)
                    # Strip leading ./ if present.
                    script_path = script_path.lstrip("./")
                    if ctx.has_file(script_path):
                        found.append(script_path)
                    else:
                        missing.append(script_path)

        # De-duplicate while preserving order.
        missing = list(dict.fromkeys(missing))
        found = list(dict.fromkeys(found))

        if missing:
            return [self._warn(
                "README references scripts that do not exist: {}.".format(
                    ", ".join(missing)
                ),
                evidence=missing,
                recommendation=(
                    "Update the README commands to reference scripts that "
                    "exist in the repository, or add the missing scripts."
                ),
            )]

        if found:
            return [self._pass(
                "All {} referenced script(s) exist.".format(len(found)),
                evidence=found,
            )]

        return [self._pass("No script references found in README code blocks.")]

    @staticmethod
    def _find_readme(ctx: CheckContext) -> str | None:
        for name in ("README.md", "README.rst", "README"):
            content = ctx.read_file(name)
            if content is not None:
                return content
        return None


# ---------------------------------------------------------------------------
# PAP003 -- README directory references exist
# ---------------------------------------------------------------------------


@register
class Pap003ReadmeDirectoryReferences(BaseChecker):
    """PAP003: Check that directory paths mentioned in README actually exist."""

    check_id = "PAP003"
    title = "README directory references exist"
    severity = Severity.WARNING

    # Match directory-like references ending with / that look like real paths
    # (not URLs, not markdown links to other repos, etc.).
    _DIR_RE = re.compile(r"(?<![/\w])([a-zA-Z0-9_./-]{1,80}/)(?=[\s,)`]|$)")

    # Paths that are common documentation artifacts, not actual directories.
    _IGNORE = ("http://", "https://", "ftp://")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        readme = self._find_readme(ctx)
        if readme is None:
            return [self._pass(
                "No README found; skipping directory reference check."
            )]

        # Collect directory references from the README text.
        candidates: set[str] = set()
        for m in self._DIR_RE.finditer(readme):
            raw = m.group(1)
            # Skip obvious non-paths.
            if any(raw.startswith(prefix) for prefix in self._IGNORE):
                continue
            # Normalize: strip trailing slash for existence check.
            clean = raw.rstrip("/")
            # Skip things that look like file extensions only (e.g. ".py/").
            if clean.startswith("."):
                continue
            # Skip anything too deep (likely a URL path segment).
            if clean.count("/") > 4:
                continue
            candidates.add(clean)

        if not candidates:
            return [self._pass("No directory references found in README.")]

        missing: list[str] = []
        existing: list[str] = []
        for d in sorted(candidates):
            if ctx.has_file(d):
                existing.append(d)
            else:
                missing.append(d)

        if missing:
            return [self._warn(
                "README references non-existent directories: {}.".format(
                    ", ".join(missing)
                ),
                evidence=missing,
                recommendation=(
                    "Update the README to reference directories that exist, "
                    "or create the missing directories."
                ),
            )]

        if existing:
            return [self._pass(
                "All {} referenced directory(ies) exist.".format(len(existing)),
                evidence=existing,
            )]

        return [self._pass("No valid directory references found in README.")]

    @staticmethod
    def _find_readme(ctx: CheckContext) -> str | None:
        for name in ("README.md", "README.rst", "README"):
            content = ctx.read_file(name)
            if content is not None:
                return content
        return None


# ---------------------------------------------------------------------------
# PAP004 -- Citation keys consistent
# ---------------------------------------------------------------------------


@register
class Pap004CitationKeysConsistent(BaseChecker):
    """PAP004: Verify citation files reference the correct repo and are used."""

    check_id = "PAP004"
    title = "Citation keys consistent"
    severity = Severity.INFO

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        results: list[CheckResult] = []

        # --- CITATION.cff consistency ---
        citation_cff = ctx.read_file("CITATION.cff")
        if citation_cff is not None:
            results.extend(self._check_cff(ctx, citation_cff))

        # --- .bib files referenced somewhere ---
        bib_files = [
            str(f)
            for f in ctx.files
            if f.suffix == ".bib"
        ]
        if bib_files:
            results.extend(self._check_bib_refs(ctx, bib_files))

        if not results:
            return [self._info(
                "No citation files found to verify.",
                recommendation=(
                    "Add a CITATION.cff or .bib file so that users can "
                    "properly cite your work."
                ),
            )]

        return results

    # -- CITATION.cff -----------------------------------------------------------

    def _check_cff(self, ctx: CheckContext, content: str) -> list[CheckResult]:
        """Check CITATION.cff for repo-name consistency."""
        # The repo name is typically the last component of the repo path on disk.
        repo_name = ctx.root.name

        # CITATION.cff is YAML; look for a 'repository-code' field.
        repo_code_match = re.search(
            r"repository-code\s*:\s*(.+)",
            content,
            re.IGNORECASE,
        )
        if repo_code_match:
            url = repo_code_match.group(1).strip().strip('"').strip("'")
            # The URL should end with the repo name.
            url_name = PurePosixPath(url.rstrip("/")).name
            if url_name and url_name != repo_name:
                return [self._info(
                    "CITATION.cff repository-code URL name '{}' "
                    "does not match repo directory name '{}'.".format(
                        url_name, repo_name
                    ),
                    evidence=["repository-code: {}".format(url)],
                )]

        # Also check that 'title' is present (basic sanity).
        if not re.search(r"^title\s*:", content, re.MULTILINE):
            return [self._info(
                "CITATION.cff is missing a 'title' field.",
                evidence=["CITATION.cff"],
            )]

        return [self._info(
            "CITATION.cff present and looks consistent.",
            evidence=["CITATION.cff"],
        )]

    # -- .bib cross-references --------------------------------------------------

    def _check_bib_refs(
        self, ctx: CheckContext, bib_files: list[str]
    ) -> list[CheckResult]:
        """Check that each .bib file is referenced from README or .tex."""
        # Gather text from README and all .tex files.
        texts: list[str] = []
        for readme in ("README.md", "README.rst", "README"):
            content = ctx.read_file(readme)
            if content:
                texts.append(content)
        for f in ctx.files:
            if f.suffix == ".tex":
                try:
                    texts.append(f.read_text(encoding="utf-8", errors="replace"))
                except Exception:
                    pass

        combined = "\n".join(texts)
        unreferenced: list[str] = []
        for bib in bib_files:
            bib_stem = PurePosixPath(bib).stem
            # Check if the filename or its stem appears anywhere.
            if bib not in combined and bib_stem not in combined:
                unreferenced.append(bib)

        if unreferenced:
            return [self._info(
                "Bib file(s) not referenced in README or .tex: {}.".format(
                    ", ".join(unreferenced)
                ),
                evidence=unreferenced,
                recommendation=(
                    "Reference your .bib files in the README or LaTeX "
                    "documents so that users can find and use them."
                ),
            )]

        return [self._info(
            "All {} bib file(s) are referenced.".format(len(bib_files)),
            evidence=bib_files,
        )]

    def _info(
        self,
        message: str,
        evidence: list[str] | None = None,
        recommendation: str = "",
    ) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )


# ---------------------------------------------------------------------------
# PAP005 -- Figure paths in paper match files
# ---------------------------------------------------------------------------


@register
class Pap005FigurePathsMatch(BaseChecker):
    r"""PAP005: Check that \includegraphics paths in .tex files resolve."""

    check_id = "PAP005"
    title = "Figure paths in paper match files"
    severity = Severity.INFO

    # Matches \includegraphics[...]{path} and \includegraphics{path}.
    _INCLUDEGRAPHICS_RE = re.compile(
        r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}"
    )

    # Common image extensions to try when the path has no extension.
    _IMAGE_EXTS = (
        ".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg", ".gif", ".bmp",
        ".tiff",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        tex_files = [f for f in ctx.files if f.suffix == ".tex"]
        if not tex_files:
            return [self._info(
                "No .tex files found; skipping figure path check.",
            )]

        missing: list[str] = []
        found: list[str] = []

        for tex_file in tex_files:
            try:
                text = tex_file.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            tex_dir = tex_file.parent
            for m in self._INCLUDEGRAPHICS_RE.finditer(text):
                raw_path = m.group(1).strip()
                # LaTeX may use multiple paths separated by commas for fallbacks.
                for candidate in raw_path.split(","):
                    candidate = candidate.strip()
                    if not candidate:
                        continue
                    resolved = self._resolve_figure(ctx, tex_dir, candidate)
                    label = "{}: {}".format(tex_file.name, candidate)
                    if resolved:
                        found.append(label)
                    else:
                        missing.append(label)

        # De-duplicate.
        missing = list(dict.fromkeys(missing))
        found = list(dict.fromkeys(found))

        if missing:
            return [self._info(
                "Missing figure(s): {}.".format(", ".join(missing)),
                evidence=missing,
                recommendation=(
                    "Ensure that all figures referenced in LaTeX files are "
                    "present in the repository."
                ),
            )]

        if found:
            return [self._info(
                "All {} figure reference(s) resolve.".format(len(found)),
                evidence=found,
            )]

        return [self._info(
            "No \\includegraphics commands found in .tex files.",
        )]

    def _resolve_figure(
        self,
        ctx: CheckContext,
        tex_dir: PurePosixPath,
        fig_path: str,
    ) -> bool:
        """Try to resolve a figure path relative to repo root and the tex dir."""
        # Strip common LaTeX graphicspath prefixes that are not real dirs.
        clean = fig_path.lstrip("/")

        # Try as-is relative to repo root.
        if ctx.has_file(clean):
            return True

        # Try relative to the .tex file's directory.
        rel = str(tex_dir / clean)
        if ctx.has_file(rel):
            return True

        # If no extension, try common image extensions.
        if PurePosixPath(clean).suffix == "":
            for ext in self._IMAGE_EXTS:
                if ctx.has_file(clean + ext):
                    return True
                rel = str(tex_dir / (clean + ext))
                if ctx.has_file(rel):
                    return True

        return False

    def _info(
        self,
        message: str,
        evidence: list[str] | None = None,
        recommendation: str = "",
    ) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )
