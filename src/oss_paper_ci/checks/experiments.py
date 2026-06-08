"""Experiment-related checks for oss-paper-ci.

Verifies that a research repository has clear experiment entry points,
reproduction instructions, smoke tests, seed handling, and configuration.
"""

from __future__ import annotations

import json
import re

from oss_paper_ci.checks import register
from oss_paper_ci.checks.base import BaseChecker, CheckContext
from oss_paper_ci.models import CheckResult, Severity, Status


def _find_readme(ctx: CheckContext) -> str | None:
    """Try to read the repository README (any common casing/extension)."""
    for name in ("README.md", "README.rst", "README.txt", "README"):
        content = ctx.read_file(name)
        if content is not None:
            return content
    return None


def _read_python_files(ctx: CheckContext) -> list[tuple[str, str]]:
    """Return (relative_path, content) for every .py file in the repo."""
    results: list[tuple[str, str]] = []
    for f in ctx.files:
        if f.suffix == ".py":
            content = ctx.read_file(str(f))
            if content is not None:
                results.append((str(f), content))
    return results


# ---------------------------------------------------------------------------
# EXP001 -- Experiment entry points exist
# ---------------------------------------------------------------------------

@register
class ExperimentEntryPointsChecker(BaseChecker):
    """Check that obvious experiment entry-point directories or scripts exist."""

    check_id = "EXP001"
    title = "Experiment entry points exist"
    severity = Severity.ERROR
    category = "experiments"
    description = "Checks that obvious experiment entry-point directories (scripts/, experiments/) or scripts (train.py, run.py) exist."

    _DIRS = ("scripts", "experiments", "src", "notebooks")
    _FILES = ("train.py", "eval.py", "run.py", "run_experiment.py", "main.py", "Makefile")

    # Patterns indicating a runnable script.
    _ENTRYPOINT_RE = re.compile(
        r"(?:if\s+__name__\s*==|def\s+main\s*\()",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        found: list[str] = []
        warnings: list[str] = []

        # Check directories (first-level existence)
        for dirname in self._DIRS:
            if (ctx.root / dirname).is_dir():
                # If scripts/ or experiments/, verify it has usable files.
                if dirname in ("scripts", "experiments"):
                    has_scripts = any(
                        f.suffix in (".py", ".sh")
                        and str(f.parent) == dirname
                        for f in ctx.files
                    )
                    if has_scripts:
                        found.append(f"directory: {dirname}/")
                    else:
                        warnings.append(
                            f"directory {dirname}/ exists but contains "
                            "no .py or .sh files"
                        )
                else:
                    found.append(f"directory: {dirname}/")

        # Check files
        names = ctx.file_names()
        for fname in self._FILES:
            if fname in names:
                # For root-level Python entry points, check for __main__ or def main.
                if fname in ("train.py", "run.py", "run_experiment.py", "main.py"):
                    content = ctx.read_file(fname)
                    if content and self._ENTRYPOINT_RE.search(content):
                        found.append(f"file: {fname}")
                    else:
                        warnings.append(
                            f"{fname} exists but has no 'if __name__' or 'def main'"
                        )
                else:
                    found.append(f"file: {fname}")

        if found:
            message = "Found experiment entry points."
            if warnings:
                message += " Warnings: " + "; ".join(warnings) + "."
            return [self._pass(
                message,
                evidence=found + warnings,
            )]
        return [self._fail(
            "No experiment entry points found.",
            evidence=[],
            recommendation=(
                "Add a scripts/, experiments/, or src/ directory, or a "
                "top-level entry-point script such as train.py or run.py."
            ),
        )]


# ---------------------------------------------------------------------------
# EXP002 -- One-command reproduction script exists
# ---------------------------------------------------------------------------

@register
class ReproductionScriptChecker(BaseChecker):
    """Check for a single-command reproduction path."""

    check_id = "EXP002"
    title = "One-command reproduction script exists"
    severity = Severity.WARNING
    category = "experiments"
    description = "Checks for a single-command reproduction path (run.sh, Makefile, or documented quickstart)."

    _SCRIPT_NAMES = ("run.sh", "run_all.sh", "reproduce.sh", "Makefile",
                     "justfile", "run_experiments.py")
    _README_KEYWORDS = re.compile(
        r"(?:^|\n)#+\s*(run|reproduc|quickstart|getting\s+started)",
        re.IGNORECASE,
    )
    _CODE_BLOCK = re.compile(r"```(?:bash|sh|shell|python|console)\s*\n(.*?)```",
                             re.DOTALL | re.IGNORECASE)

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []
        has_script = False

        # Look for dedicated reproduction scripts.
        names = ctx.file_names()
        for fname in self._SCRIPT_NAMES:
            if fname in names:
                has_script = True
                evidence.append(f"file: {fname}")

        # Inspect README for runnable guidance.
        readme = _find_readme(ctx)
        has_readme_section = False
        has_code_block = False

        if readme:
            if self._README_KEYWORDS.search(readme):
                has_readme_section = True
                evidence.append("README contains a run/reproduce/quickstart section")
            if self._CODE_BLOCK.search(readme):
                has_code_block = True
                evidence.append("README contains executable code blocks")

        if has_script or (has_readme_section and has_code_block):
            return [self._pass(
                "A one-command reproduction path was found.",
                evidence=evidence,
            )]

        return [self._warn(
            "No clear single-command reproduction path found.",
            evidence=evidence,
            recommendation=(
                "Add a run.sh or Makefile that reproduces the main results, "
                "or document a single command in the README."
            ),
        )]


# ---------------------------------------------------------------------------
# EXP003 -- Smoke test or quickstart exists
# ---------------------------------------------------------------------------

@register
class SmokeTestChecker(BaseChecker):
    """Check for a lightweight smoke-test or quickstart example."""

    check_id = "EXP003"
    title = "Smoke test or quickstart exists"
    severity = Severity.INFO
    category = "experiments"
    description = "Checks for a lightweight smoke test or quickstart example to verify setup works."

    _FILE_NAMES = ("quick_start.py", "smoke_test.py", "test_run.sh",
                   "demo.py", "example.py")
    _README_RE = re.compile(
        r"(quick|demo|example|test\s*run|fast)",
        re.IGNORECASE,
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []
        names = ctx.file_names()

        for fname in self._FILE_NAMES:
            if fname in names:
                evidence.append(f"file: {fname}")

        readme = _find_readme(ctx)
        if readme and self._README_RE.search(readme):
            evidence.append("README mentions quick/demo/example/test-run")

        if evidence:
            return [self._pass(
                "Smoke test or quickstart reference found.",
                evidence=evidence,
            )]

        return [self._warn(
            "No smoke test or quickstart found.",
            evidence=[],
            recommendation=(
                "Add a quick_start.py, smoke_test.py, or a short demo so "
                "users can verify the setup works before running the full "
                "experiment."
            ),
        )]


# ---------------------------------------------------------------------------
# EXP004 -- Long vs short experiment distinction
# ---------------------------------------------------------------------------

@register
class ExperimentDistinctionChecker(BaseChecker):
    """Check whether the repo distinguishes quick vs full experiments."""

    check_id = "EXP004"
    title = "Long vs short experiment distinction"
    severity = Severity.INFO
    category = "experiments"
    description = "Checks whether the repo distinguishes between quick/demo and full experiment runs."

    _KEYWORDS = re.compile(
        r"\b(quick|fast|full|long|short|demo|subset)\b",
        re.IGNORECASE,
    )
    _CONFIG_EXTENSIONS = {".yaml", ".yml", ".json", ".toml", ".cfg", ".ini"}

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Scan README and shell/python scripts for mode keywords.
        readme = _find_readme(ctx)
        if readme and self._KEYWORDS.search(readme):
            evidence.append("README mentions quick/fast/full/long/short/subset modes")

        for path_str, content in _read_python_files(ctx):
            if self._KEYWORDS.search(content):
                evidence.append(f"{path_str} references experiment modes")
                break  # one hit is enough for Python files

        # Scan config files.
        for f in ctx.files:
            if f.suffix in self._CONFIG_EXTENSIONS:
                file_content = ctx.read_file(str(f))
                if file_content and self._KEYWORDS.search(file_content):
                    evidence.append(f"{f} contains experiment mode settings")
                    break

        if evidence:
            return [self._pass(
                "Repository distinguishes between experiment modes.",
                evidence=evidence,
            )]

        return [self._warn(
            "No distinction between long and short experiment runs found.",
            evidence=[],
            recommendation=(
                "Document how to run a quick sanity-check experiment vs. the "
                "full experiment (e.g., --quick flag, separate config file, "
                "or a demo mode)."
            ),
        )]


# ---------------------------------------------------------------------------
# EXP005 -- Random seed setting detected
# ---------------------------------------------------------------------------

@register
class RandomSeedChecker(BaseChecker):
    """Check whether the codebase sets random seeds for reproducibility."""

    check_id = "EXP005"
    title = "Random seed setting detected"
    severity = Severity.INFO
    category = "experiments"
    description = "Checks whether the codebase sets random seeds (random.seed, torch.manual_seed, etc.) for reproducibility."

    _SEED_CODE_RE = re.compile(
        r"(?:"
        r"seed\s*=\s*\d+"
        r"|random\.seed\s*\("
        r"|np\.random\.seed\s*\("
        r"|torch\.manual_seed\s*\("
        r"|set_seed\s*\("
        r"|tf\.random\.set_seed\s*\("
        r"|RANDOM_SEED"
        r"|SEED\s*=\s*\d+"
        r")",
        re.IGNORECASE,
    )
    _SEED_README_RE = re.compile(
        r"\b(seed|reproducib|deterministic)\b",
        re.IGNORECASE,
    )
    _MAX_FILES = 10
    _SCAN_DIRS = ("scripts", "src")

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []

        # Scan Python files in scripts/ and src/ directories (limited to 10 files).
        scanned = 0
        for f in ctx.files:
            if scanned >= self._MAX_FILES:
                break
            if f.suffix != ".py":
                continue
            # Only scan files under scripts/ or src/ directories.
            rel = str(f)
            if not any(rel.startswith(d + "/") or rel.startswith(d + "\\")
                        for d in self._SCAN_DIRS):
                continue
            content = ctx.read_file(rel)
            if content and self._SEED_CODE_RE.search(content):
                evidence.append(f"{rel} sets a random seed")
            scanned += 1

        if not evidence:
            readme = _find_readme(ctx)
            if readme and self._SEED_README_RE.search(readme):
                evidence.append("README mentions seed/reproducibility/determinism")

        if evidence:
            return [self._pass(
                "Random seed or reproducibility mechanism detected.",
                evidence=evidence,
            )]

        return [self._info(
            "No random seed setting detected in scripts/ or src/.",
            evidence=[],
            recommendation=(
                "Set random seeds (e.g., random.seed(), np.random.seed(), "
                "torch.manual_seed()) so experiments are reproducible."
            ),
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
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
# EXP006 -- Configuration files exist
# ---------------------------------------------------------------------------

@register
class ConfigFilesChecker(BaseChecker):
    """Check that the project uses configuration files or CLI argument parsing."""

    check_id = "EXP006"
    title = "Configuration files exist"
    severity = Severity.INFO
    category = "experiments"
    description = "Checks that the project uses configuration files (config.yaml, .env) or CLI argument parsing."

    _CONFIG_FILENAMES = {
        "config.yaml", "config.yml", "config.json", "config.toml",
        ".env", "hydra.yaml", "hydra.yml", "args.yaml", "args.yml",
        "params.yaml", "params.yml", "settings.yaml", "settings.yml",
    }
    _ARGPARSE_RE = re.compile(
        r"(?:argparse|click|typer)\b",
    )

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        evidence: list[str] = []
        names = ctx.file_names()

        # Direct config file check.
        for fname in self._CONFIG_FILENAMES:
            if fname in names:
                evidence.append(f"file: {fname}")

        # Config directories (e.g., hydra configs live under conf/ or config/).
        for dirname in ("conf", "config", "configs", "settings"):
            if (ctx.root / dirname).is_dir():
                evidence.append(f"directory: {dirname}/")

        # CLI-argument parsing in Python source.
        if not evidence:
            for path_str, content in _read_python_files(ctx):
                if self._ARGPARSE_RE.search(content):
                    evidence.append(f"{path_str} uses argument parsing (argparse/click/typer)")
                    break

        if evidence:
            return [self._pass(
                "Configuration mechanism detected.",
                evidence=evidence,
            )]

        return [self._warn(
            "No configuration files or CLI argument parsing found.",
            evidence=[],
            recommendation=(
                "Add a config file (e.g., config.yaml) or use argparse/click "
                "so experiment parameters are explicit and reproducible."
            ),
        )]


# ---------------------------------------------------------------------------
# EXP007 -- Notebook risk assessment
# ---------------------------------------------------------------------------

@register
class Exp007NotebookRisk(BaseChecker):
    """EXP007: Check if notebooks are the only experiment entry point."""

    check_id = "EXP007"
    title = "Notebook risk assessment"
    severity = Severity.INFO
    category = "experiments"
    description = "Checks if notebooks are the only experiment entry point (risk: harder to reproduce)."

    def check(self, ctx: CheckContext) -> list[CheckResult]:
        # Find .ipynb files.
        notebook_files = [f for f in ctx.files if f.suffix == ".ipynb"]

        if not notebook_files:
            return [self._info(
                "No Jupyter notebooks found in the repository.",
            )]

        # Check if scripts/ directory has .py files as alternatives.
        has_script_alternatives = any(
            f.suffix == ".py"
            and (str(f.parent) == "scripts" or str(f.parent).startswith("scripts/"))
            for f in ctx.files
        )

        # Also check src/ for .py files.
        if not has_script_alternatives:
            has_script_alternatives = any(
                f.suffix == ".py"
                and (str(f.parent) == "src" or str(f.parent).startswith("src/"))
                for f in ctx.files
            )

        evidence: list[str] = []
        notebook_count = len(notebook_files)
        evidence.append(f"Found {notebook_count} notebook(s)")

        # Validate notebooks are parseable JSON.
        valid_count = 0
        for nb in notebook_files:
            content = ctx.read_file(str(nb))
            if content is not None:
                try:
                    json.loads(content)
                    valid_count += 1
                except (json.JSONDecodeError, ValueError):
                    evidence.append(f"{nb} is not valid JSON")

        if not has_script_alternatives:
            return [self._warn(
                f"Found {notebook_count} notebook(s) but no .py scripts in "
                "scripts/ or src/ directories. Notebooks are harder to "
                "reproduce and version-control.",
                evidence=evidence,
                recommendation=(
                    "Add Python scripts (.py) alongside notebooks so that "
                    "experiments can be run non-interactively. Consider "
                    "converting key notebooks to scripts with "
                    "'jupyter nbconvert --to script'."
                ),
            )]

        return [self._info(
            f"Found {notebook_count} notebook(s) with script alternatives available.",
            evidence=evidence,
        )]

    def _info(self, message: str, evidence: list[str] | None = None, recommendation: str = "") -> CheckResult:
        return CheckResult(
            id=self.check_id,
            title=self.title,
            severity=Severity.INFO,
            status=Status.WARN,
            message=message,
            evidence=evidence or [],
            recommendation=recommendation,
        )
