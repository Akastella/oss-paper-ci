#!/usr/bin/env python3
"""Check documentation and examples for truthfulness issues.

Scans README, docs, examples, action.yml, pyproject.toml, src/, and scripts/ for:
- Unqualified pip install of oss-paper-ci (no PyPI publication qualifier)
- Fake GitHub URLs (unconfirmed repository addresses)
- Composite action using pip install .
- Docs referencing non-existent files
- Workflow referencing non-existent CLI commands
- External program/benefit-oriented language
- Exaggerated claims (production-ready, perfect, fully supports)
- Old round file references
- Old dogfooding references

Usage:
    python scripts/check_docs_truthfulness.py --format markdown --output report.md
    python scripts/check_docs_truthfulness.py --format json --output report.json
    python scripts/check_docs_truthfulness.py --check  # exit non-zero on issues
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Patterns that indicate problems
# Construct fake URL pattern dynamically to avoid self-detection
_FAKE_OWNER = "oss-paper-ci"
FAKE_GITHUB_URL = re.compile(r"github\.com/" + re.escape(_FAKE_OWNER) + r"/" + re.escape(_FAKE_OWNER))
UNQUALIFIED_PIP_INSTALL = re.compile(
    r"(?:python\s+-m\s+)?pip\s+install\s+oss-paper-ci(?![^#\n]*#\s*after\s+PyPI)", re.IGNORECASE
)
PIP_INSTALL_DOT = re.compile(r"pip\s+install\s+\.")
EXAGGERATED_CLAIMS = re.compile(
    r"(production[- ]ready|production[- ]grade|perfect\s+score|"
    r"fully\s+supports\s+all|comprehensive\s+support|"
    r"enterprise[- ]grade|world[- ]class)",
    re.IGNORECASE,
)
EXTERNAL_PROGRAM = re.compile(
    r"(credits?\s+program|Pro\s+plan|account\s+benefit|"
    r"apply\s+for\s+(?:GitHub|Google|AWS|Azure)|"
    r"(?:GitHub|Google|AWS|Azure)\s+(?:credits?|benefits?|program))",
    re.IGNORECASE,
)
OLD_ROUND_REFERENCE = re.compile(
    r"(round[3-7]|ROUND[3-7]|FINAL_DELIVERABLES_ROUND|RED_TEAM_AUDIT_ROUND)"
)

# --- Evaluation check functions ---

def check_eval_command_exists(root: Path) -> list[dict]:
    """Check that eval CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "eval" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "eval-command-missing",
                "message": "eval command not found in cli.py",
            })
    return issues


def check_eval_corpus_exists(root: Path) -> list[dict]:
    """Check that evaluation corpus directory exists."""
    issues = []
    corpus_dir = root / "examples" / "evaluation-corpus"
    if not corpus_dir.exists():
        issues.append({
            "file": "examples/evaluation-corpus",
            "line": 0,
            "severity": "major",
            "rule": "eval-corpus-missing",
            "message": "examples/evaluation-corpus/ not found",
        })
    elif not (corpus_dir / "README.md").exists():
        issues.append({
            "file": "examples/evaluation-corpus/README.md",
            "line": 0,
            "severity": "major",
            "rule": "eval-corpus-readme-missing",
            "message": "evaluation-corpus/README.md not found",
        })
    return issues


def check_expected_outcomes_exists(root: Path) -> list[dict]:
    """Check that expected_outcomes.yml exists."""
    issues = []
    outcomes = root / "examples" / "evaluation-corpus" / "expected_outcomes.yml"
    if not outcomes.exists():
        issues.append({
            "file": "examples/evaluation-corpus/expected_outcomes.yml",
            "line": 0,
            "severity": "major",
            "rule": "expected-outcomes-missing",
            "message": "expected_outcomes.yml not found",
        })
    return issues


def check_eval_reports_exist(root: Path) -> list[dict]:
    """Check that evaluation reports exist."""
    issues = []
    reports_dir = root / "examples" / "reports"
    required = ["evaluation_summary.json", "evaluation_summary.md", "evaluation_summary.html"]
    for report in required:
        if not (reports_dir / report).exists():
            issues.append({
                "file": f"examples/reports/{report}",
                "line": 0,
                "severity": "major",
                "rule": "eval-report-missing",
                "message": f"{report} not found",
            })
    return issues


def check_no_corpus_overclaim(root: Path) -> list[dict]:
    """Check docs don't claim corpus represents all real repos."""
    issues = []
    docs_to_check = [
        "README.md", "README.zh-CN.md", "README.ja.md",
        "docs/evaluation.md", "docs/evaluation-corpus.md",
        "docs/benchmark-methodology.md",
    ]

    overclaim_patterns = [
        "represent all",
        "covers all",
        "exhaustive",
        "comprehensive coverage of all",
        "all real-world",
        "all scientific",
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in overclaim_patterns:
                if pattern in content:
                    issues.append({
                        "file": doc_path,
                        "line": 0,
                        "severity": "major",
                        "rule": "corpus-overclaim",
                        "message": f"{doc_path} contains overclaim: '{pattern}'",
                    })
    return issues


def check_no_correctness_claim(root: Path) -> list[dict]:
    """Check docs don't claim benchmark proves scientific correctness."""
    issues = []
    docs_to_check = [
        "README.md", "README.zh-CN.md", "README.ja.md",
        "docs/evaluation.md", "docs/benchmark-methodology.md",
    ]

    correctness_patterns = [
        "proves correctness",
        "scientifically correct",
        "validates scientific",
        "proves the paper",
        "confirms the results are correct",
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in correctness_patterns:
                if pattern in content:
                    issues.append({
                        "file": doc_path,
                        "line": 0,
                        "severity": "blocker",
                        "rule": "correctness-claim",
                        "message": f"{doc_path} claims correctness: '{pattern}'",
                    })
    return issues


def check_i18n_eval_section(root: Path) -> list[dict]:
    """Check that i18n READMEs have eval section."""
    issues = []
    readmes = {
        "zh-CN": "README.zh-CN.md",
        "ja": "README.ja.md",
    }

    for lang, readme_name in readmes.items():
        path = root / readme_name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if lang == "zh-CN":
                if "评估" not in content and "eval" not in content.lower():
                    issues.append({
                        "file": readme_name,
                        "line": 0,
                        "severity": "major",
                        "rule": "i18n-eval-section-missing",
                        "message": f"{readme_name} missing eval section",
                    })
            elif lang == "ja":
                if "評価" not in content and "eval" not in content.lower():
                    issues.append({
                        "file": readme_name,
                        "line": 0,
                        "severity": "major",
                        "rule": "i18n-eval-section-missing",
                        "message": f"{readme_name} missing eval section",
                    })
    return issues


def check_no_absolute_paths_in_reports(root: Path) -> list[dict]:
    """Check evaluation reports don't contain absolute paths."""
    issues = []
    reports_dir = root / "examples" / "reports"
    if reports_dir.exists():
        for report in reports_dir.glob("evaluation_*"):
            if report.is_file():
                content = report.read_text(encoding="utf-8")
                if "C:\\" in content or "/home/" in content or "/Users/" in content:
                    issues.append({
                        "file": f"examples/reports/{report.name}",
                        "line": 0,
                        "severity": "major",
                        "rule": "absolute-path-in-report",
                        "message": f"{report.name} contains absolute paths",
                    })
    return issues


def check_synthetic_fixtures_documented(root: Path) -> list[dict]:
    """Check that synthetic fixtures have documentation."""
    issues = []
    corpus_readme = root / "examples" / "evaluation-corpus" / "README.md"
    if corpus_readme.exists():
        content = corpus_readme.read_text(encoding="utf-8").lower()
        if "synthetic" not in content:
            issues.append({
                "file": "examples/evaluation-corpus/README.md",
                "line": 0,
                "severity": "major",
                "rule": "synthetic-not-documented",
                "message": "corpus README doesn't mention synthetic nature",
            })
    return issues


def check_unsafe_script_not_executed(root: Path) -> list[dict]:
    """Check that unsafe script fixture warns about not executing."""
    issues = []
    unsafe_readme = root / "examples" / "evaluation-corpus" / "unsafe_script_project" / "README.md"
    if unsafe_readme.exists():
        content = unsafe_readme.read_text(encoding="utf-8").lower()
        if not any(word in content for word in ["not executed", "dry-run", "dry run", "testing only"]):
            issues.append({
                "file": "examples/evaluation-corpus/unsafe_script_project/README.md",
                "line": 0,
                "severity": "major",
                "rule": "unsafe-script-no-warning",
                "message": "unsafe_script_project README doesn't warn about execution",
            })
    return issues


# --- Distribution check functions ---

def check_quickstart_command_exists(root: Path) -> list[dict]:
    """Check that quickstart CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "quickstart" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "quickstart-command-missing",
                "message": "quickstart command not found in cli.py",
            })
    return issues


def check_try_demo_command_exists(root: Path) -> list[dict]:
    """Check that try-demo CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "try-demo" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "try-demo-command-missing",
                "message": "try-demo command not found in cli.py",
            })
    return issues


def check_dockerfile_docs(root: Path) -> list[dict]:
    """Check that Dockerfile has corresponding docs."""
    issues = []
    if (root / "Dockerfile").exists():
        if not (root / "docs" / "docker.md").exists():
            issues.append({
                "file": "docs/",
                "line": 0,
                "severity": "major",
                "rule": "docker-docs-missing",
                "message": "Dockerfile exists but docs/docker.md missing",
            })
    return issues


def check_devcontainer_docs(root: Path) -> list[dict]:
    """Check that devcontainer has corresponding docs."""
    issues = []
    if (root / ".devcontainer" / "devcontainer.json").exists():
        if not (root / "docs" / "devcontainer.md").exists():
            issues.append({
                "file": "docs/",
                "line": 0,
                "severity": "major",
                "rule": "devcontainer-docs-missing",
                "message": "devcontainer exists but docs/devcontainer.md missing",
            })
    return issues


def check_install_smoke_workflow(root: Path) -> list[dict]:
    """Check that install-smoke workflow exists."""
    issues = []
    workflow = root / ".github" / "workflows" / "install-smoke.yml"
    if not workflow.exists():
        issues.append({
            "file": ".github/workflows/",
            "line": 0,
            "severity": "major",
            "rule": "install-smoke-missing",
            "message": "install-smoke.yml workflow not found",
        })
    return issues


def check_no_pypi_published_claim(root: Path) -> list[dict]:
    """Check that docs don't claim PyPI is published."""
    issues = []
    docs_to_check = [
        "README.md", "README.zh-CN.md", "README.ja.md",
        "docs/installation.md",
    ]

    pypi_published_patterns = [
        "published on pypi",
        "available on pypi",
        "install from pypi",
        "pip install oss-paper-ci",  # Without "after PyPI" qualifier
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in pypi_published_patterns:
                if pattern in content:
                    # Check if it has proper qualifier
                    if "after pypi" not in content and "not yet" not in content:
                        issues.append({
                            "file": doc_path,
                            "line": 0,
                            "severity": "blocker",
                            "rule": "pypi-claim-without-qualifier",
                            "message": f"{doc_path} claims PyPI without 'after PyPI' qualifier",
                        })

    return issues


def check_no_docker_hub_claim(root: Path) -> list[dict]:
    """Check that docs don't claim Docker Hub publishing."""
    issues = []
    docs_to_check = [
        "README.md", "README.zh-CN.md", "README.ja.md",
        "docs/docker.md",
    ]

    docker_hub_patterns = [
        "docker hub",
        "docker pull",
        "published to docker",
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in docker_hub_patterns:
                if pattern in content:
                    issues.append({
                        "file": doc_path,
                        "line": 0,
                        "severity": "blocker",
                        "rule": "docker-hub-claim",
                        "message": f"{doc_path} claims Docker Hub publishing",
                    })

    return issues


def check_trust_command_exists(root: Path) -> list[dict]:
    """Check that trust CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "trust" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "trust-command-missing",
                "message": "trust command not found in cli.py",
            })
    return issues


def check_security_command_exists(root: Path) -> list[dict]:
    """Check that security CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "security" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "security-command-missing",
                "message": "security command not found in cli.py",
            })
    return issues


def check_trust_examples_exist(root: Path) -> list[dict]:
    """Check that trust examples exist."""
    issues = []
    examples_dir = root / "examples" / "trust"
    if not examples_dir.exists():
        issues.append({
            "file": "examples/trust",
            "line": 0,
            "severity": "major",
            "rule": "trust-examples-missing",
            "message": "examples/trust/ not found",
        })
    else:
        required = ["trust_report.json", "trust_report.md", "provenance.json"]
        for f in required:
            if not (examples_dir / f).exists():
                issues.append({
                    "file": f"examples/trust/{f}",
                    "line": 0,
                    "severity": "major",
                    "rule": "trust-example-missing",
                    "message": f"examples/trust/{f} not found",
                })
    return issues


def check_security_docs_no_overclaim(root: Path) -> list[dict]:
    """Check that security docs don't overclaim."""
    issues = []
    docs_to_check = [
        "README.md", "README.zh-CN.md", "README.ja.md",
        "SECURITY.md", "docs/trust.md", "docs/security-scan.md",
        "docs/supply-chain.md",
    ]

    overclaim_patterns = [
        "certified secure",
        "completely secure",
        "100% secure",
        "security certification",
        "fully slsa compliant",
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in overclaim_patterns:
                if pattern in content:
                    # Check if it's in a "not" context
                    lines_with_pattern = [l for l in content.splitlines() if pattern in l]
                    for line in lines_with_pattern:
                        if not any(neg in line for neg in ["not", "no ", "don't", "doesn't", "do not", "isn't"]):
                            issues.append({
                                "file": doc_path,
                                "line": 0,
                                "severity": "blocker",
                                "rule": "security-overclaim",
                                "message": f"{doc_path} contains overclaim: '{pattern}'",
                            })
    return issues


def check_evidence_command_exists(root: Path) -> list[dict]:
    """Check that evidence CLI command is documented."""
    issues = []
    cli_path = root / "src" / "oss_paper_ci" / "cli.py"
    if cli_path.exists():
        content = cli_path.read_text(encoding="utf-8")
        if "evidence" not in content:
            issues.append({
                "file": "src/oss_paper_ci/cli.py",
                "line": 0,
                "severity": "major",
                "rule": "evidence-command-missing",
                "message": "evidence command not found in cli.py",
            })
    return issues


def check_evidence_examples_exist(root: Path) -> list[dict]:
    """Check that evidence examples exist."""
    issues = []
    examples_dir = root / "examples" / "evidence"
    if not examples_dir.exists():
        issues.append({
            "file": "examples/evidence",
            "line": 0,
            "severity": "major",
            "rule": "evidence-examples-missing",
            "message": "examples/evidence/ not found",
        })
    else:
        required = ["README.md", "reviewer_report.md", "reviewer_report.json"]
        for f in required:
            if not (examples_dir / f).exists():
                issues.append({
                    "file": f"examples/evidence/{f}",
                    "line": 0,
                    "severity": "major",
                    "rule": "evidence-example-missing",
                    "message": f"examples/evidence/{f} not found",
                })
    return issues


def check_evidence_docs_no_overclaim(root: Path) -> list[dict]:
    """Check that evidence docs don't overclaim."""
    issues = []
    docs_to_check = [
        "docs/evidence-report.md", "docs/evidence-bundle.md",
        "docs/reviewer-pack.md", "docs/author-pack.md",
    ]

    overclaim_patterns = [
        "prove scientific",
        "prove correctness",
        "predict acceptance",
        "predict rejection",
        "guarantee reproducibility",
        "signed attestation",
        "official sbom",
    ]

    for doc_path in docs_to_check:
        path = root / doc_path
        if path.exists():
            content = path.read_text(encoding="utf-8").lower()
            for pattern in overclaim_patterns:
                if pattern in content:
                    lines_with_pattern = [l for l in content.splitlines() if pattern in l]
                    for line in lines_with_pattern:
                        if not any(neg in line for neg in ["not", "no ", "don't", "doesn't", "do not", "isn't", "does not"]):
                            issues.append({
                                "file": doc_path,
                                "line": 0,
                                "severity": "blocker",
                                "rule": "evidence-overclaim",
                                "message": f"{doc_path} contains overclaim: '{pattern}'",
                            })
    return issues


# CLI commands that oss-paper-ci supports
VALID_CLI_COMMANDS = {
    "scan", "init", "explain", "version", "list-checks",
    "graph", "baseline", "smoke", "doctor", "comment",
    "config", "diff", "rules", "validate-contract",
    "reproduce", "capsule", "guide", "dossier", "ecosystems", "data", "results",
    "wizard", "workbench", "theme",
    "adopt", "scaffold", "fix", "eval",
    "quickstart", "try-demo",
    "trust", "security", "evidence",
}

# Files that exist in the project
VALID_DOCS = set()
VALID_EXAMPLES = set()


def discover_valid_files(root: Path) -> None:
    """Discover valid doc and example files."""
    docs_dir = root / "docs"
    if docs_dir.exists():
        for f in docs_dir.rglob("*.md"):
            VALID_DOCS.add(f"docs/{f.relative_to(docs_dir)}")
            VALID_DOCS.add(str(f.relative_to(root)))

    examples_dir = root / "examples"
    if examples_dir.exists():
        for f in examples_dir.rglob("*"):
            if f.is_file():
                VALID_EXAMPLES.add(str(f.relative_to(root)))


def check_file_for_issues(filepath: Path, root: Path) -> list[dict]:
    """Check a single file for truthfulness issues."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return issues

    rel_path = str(filepath.relative_to(root))

    # Skip release infrastructure scripts (they contain patterns as deny rules)
    skip_scripts = {"check_docs_truthfulness.py", "verify_clean_package.py", "make_release_package.py"}
    if filepath.name in skip_scripts:
        return issues
    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip code comments that qualify the install
        stripped = line.strip()

        # Check for fake GitHub URL
        if FAKE_GITHUB_URL.search(line):
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "fake-github-url",
                "message": f"Fake GitHub URL: {FAKE_GITHUB_URL.search(line).group()}",
            })

        # Check for unqualified pip install oss-paper-ci
        # Skip lines that have "after PyPI" or "After PyPI" qualifier
        if UNQUALIFIED_PIP_INSTALL.search(line):
            if "after PyPI" not in line.lower() and "After PyPI" not in line:
                issues.append({
                    "file": rel_path,
                    "line": line_num,
                    "severity": "blocker",
                    "rule": "unqualified-pip-install",
                    "message": f"Unqualified 'pip install oss-paper-ci': {stripped}",
                })

        # Check for pip install . in composite action context
        if rel_path == "action.yml" and PIP_INSTALL_DOT.search(line):
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "action-pip-install-dot",
                "message": f"Composite action uses 'pip install .': {stripped}",
            })

        # Check for exaggerated claims
        match = EXAGGERATED_CLAIMS.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "major",
                "rule": "exaggerated-claim",
                "message": f"Exaggerated claim: '{match.group()}'",
            })

        # Check for external program references
        match = EXTERNAL_PROGRAM.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "external-program",
                "message": f"External program reference: '{match.group()}'",
            })

        # Check for old round references
        match = OLD_ROUND_REFERENCE.search(line)
        if match:
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "major",
                "rule": "old-round-reference",
                "message": f"Old round reference: '{match.group()}'",
            })

        # Check for Claude Code branding / misleading imitation
        if re.search(r"claude\s*code", line, re.IGNORECASE):
            issues.append({
                "file": rel_path,
                "line": line_num,
                "severity": "blocker",
                "rule": "claude-code-branding",
                "message": "References Claude Code branding — must not imitate",
            })

    # Check for referenced docs files
    doc_refs = re.findall(r"\[.*?\]\((docs/[^)]+)\)", content)
    for ref in doc_refs:
        if ref not in VALID_DOCS and ref.replace(".md", "") + ".md" not in VALID_DOCS:
            # Check if file actually exists
            ref_path = root / ref
            if not ref_path.exists():
                issues.append({
                    "file": rel_path,
                    "line": 0,
                    "severity": "major",
                    "rule": "missing-doc-reference",
                    "message": f"References non-existent doc: {ref}",
                })

    return issues


def check_workflow_cli_commands(filepath: Path, root: Path) -> list[dict]:
    """Check workflow files for references to non-existent CLI commands."""
    issues = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return issues

    rel_path = str(filepath.relative_to(root))

    # Only match oss-paper-ci when it appears as an actual command invocation
    # Must be preceded by run: |, && |, or at start of a bash-like line
    cmd_pattern = re.compile(
        r"(?:run:\s*\|?\s*|&&\s*|\|\s*|^)oss-paper-ci\s+([a-z][a-z-]*)",
        re.MULTILINE,
    )
    for match in cmd_pattern.finditer(content):
        cmd = match.group(1)
        if cmd not in VALID_CLI_COMMANDS and not cmd.startswith("-"):
            issues.append({
                "file": rel_path,
                "line": 0,
                "severity": "major",
                "rule": "invalid-cli-command",
                "message": f"References non-existent CLI command: oss-paper-ci {cmd}",
            })

    return issues


def scan_project(root: Path) -> list[dict]:
    """Scan the entire project for truthfulness issues."""
    discover_valid_files(root)
    all_issues = []

    # Files to scan
    scan_targets = []

    # README
    readme = root / "README.md"
    if readme.exists():
        scan_targets.append(readme)

    # i18n READMEs
    for readme_name in ["README.zh-CN.md", "README.ja.md"]:
        p = root / readme_name
        if p.exists():
            scan_targets.append(p)

    # docs/
    docs_dir = root / "docs"
    if docs_dir.exists():
        scan_targets.extend(docs_dir.rglob("*.md"))

    # examples/
    examples_dir = root / "examples"
    if examples_dir.exists():
        scan_targets.extend(examples_dir.rglob("*.yml"))
        scan_targets.extend(examples_dir.rglob("*.yaml"))

    # action.yml
    action_yml = root / "action.yml"
    if action_yml.exists():
        scan_targets.append(action_yml)

    # pyproject.toml
    pyproject = root / "pyproject.toml"
    if pyproject.exists():
        scan_targets.append(pyproject)

    # CONTRIBUTING.md, SECURITY.md
    for name in ["CONTRIBUTING.md", "SECURITY.md"]:
        p = root / name
        if p.exists():
            scan_targets.append(p)

    # .pre-commit-hooks.yaml
    precommit = root / ".pre-commit-hooks.yaml"
    if precommit.exists():
        scan_targets.append(precommit)

    # src/ (Python source files)
    src_dir = root / "src"
    if src_dir.exists():
        scan_targets.extend(src_dir.rglob("*.py"))

    # scripts/
    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        scan_targets.extend(scripts_dir.rglob("*.py"))

    # Scan each file
    for filepath in scan_targets:
        all_issues.extend(check_file_for_issues(filepath, root))

    # Check workflow CLI commands
    for filepath in scan_targets:
        if filepath.suffix in (".yml", ".yaml"):
            all_issues.extend(check_workflow_cli_commands(filepath, root))

    # Check i18n READMEs mention new commands
    for readme_name in ["README.zh-CN.md", "README.ja.md"]:
        readme_path = root / readme_name
        if readme_path.exists():
            content = readme_path.read_text(encoding="utf-8")
            for cmd in ["wizard", "workbench"]:
                if cmd not in content.lower():
                    all_issues.append({
                        "file": readme_name,
                        "line": 0,
                        "severity": "major",
                        "rule": "i18n-missing-command",
                        "message": f"{readme_name} does not mention '{cmd}' command",
                    })

    # Check terminal examples exist
    terminal_examples = [
        "examples/terminal/wizard_output.txt",
        "examples/terminal/workbench_plain_output.txt",
        "examples/terminal/theme_preview.md",
        "examples/terminal/README.md",
    ]
    for ex in terminal_examples:
        if not (root / ex).exists():
            all_issues.append({
                "file": ex,
                "line": 0,
                "severity": "major",
                "rule": "missing-terminal-example",
                "message": f"Terminal example file missing: {ex}",
            })

    # Check new docs exist
    new_docs = [
        "docs/terminal-workbench.md",
        "docs/wizard.md",
        "docs/themes.md",
        "docs/cli-ux.md",
        "docs/no-color-and-ci.md",
    ]
    for doc in new_docs:
        if not (root / doc).exists():
            all_issues.append({
                "file": doc,
                "line": 0,
                "severity": "major",
                "rule": "missing-doc",
                "message": f"Required doc file missing: {doc}",
            })

    # Evaluation checks
    all_issues.extend(check_eval_command_exists(root))
    all_issues.extend(check_eval_corpus_exists(root))
    all_issues.extend(check_expected_outcomes_exists(root))
    all_issues.extend(check_eval_reports_exist(root))
    all_issues.extend(check_no_corpus_overclaim(root))
    all_issues.extend(check_no_correctness_claim(root))
    all_issues.extend(check_i18n_eval_section(root))
    all_issues.extend(check_no_absolute_paths_in_reports(root))
    all_issues.extend(check_synthetic_fixtures_documented(root))
    all_issues.extend(check_unsafe_script_not_executed(root))

    # Distribution checks
    all_issues.extend(check_quickstart_command_exists(root))
    all_issues.extend(check_try_demo_command_exists(root))
    all_issues.extend(check_dockerfile_docs(root))
    all_issues.extend(check_devcontainer_docs(root))
    all_issues.extend(check_install_smoke_workflow(root))
    all_issues.extend(check_no_pypi_published_claim(root))
    all_issues.extend(check_no_docker_hub_claim(root))

    # Trust & security checks
    all_issues.extend(check_trust_command_exists(root))
    all_issues.extend(check_security_command_exists(root))
    all_issues.extend(check_trust_examples_exist(root))
    all_issues.extend(check_security_docs_no_overclaim(root))

    # Evidence report checks
    all_issues.extend(check_evidence_command_exists(root))
    all_issues.extend(check_evidence_examples_exist(root))
    all_issues.extend(check_evidence_docs_no_overclaim(root))

    return all_issues


def format_markdown(issues: list[dict]) -> str:
    """Format issues as markdown."""
    lines = [
        "# Documentation Truthfulness Report",
        "",
        f"**Total issues:** {len(issues)}",
        "",
    ]

    if not issues:
        lines.append("No issues found. Documentation is truthful.")
        return "\n".join(lines)

    blockers = [i for i in issues if i["severity"] == "blocker"]
    majors = [i for i in issues if i["severity"] == "major"]
    minors = [i for i in issues if i["severity"] == "minor"]

    if blockers:
        lines.append(f"## BLOCKER ({len(blockers)})")
        lines.append("")
        for issue in blockers:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    if majors:
        lines.append(f"## MAJOR ({len(majors)})")
        lines.append("")
        for issue in majors:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    if minors:
        lines.append(f"## MINOR ({len(minors)})")
        lines.append("")
        for issue in minors:
            loc = f"{issue['file']}:{issue['line']}" if issue["line"] else issue["file"]
            lines.append(f"- **[{issue['rule']}]** `{loc}`: {issue['message']}")
        lines.append("")

    return "\n".join(lines)


def format_json(issues: list[dict]) -> str:
    """Format issues as JSON."""
    result = {
        "total_issues": len(issues),
        "blockers": len([i for i in issues if i["severity"] == "blocker"]),
        "majors": len([i for i in issues if i["severity"] == "major"]),
        "minors": len([i for i in issues if i["severity"] == "minor"]),
        "issues": issues,
        "passed": len([i for i in issues if i["severity"] == "blocker"]) == 0,
    }
    return json.dumps(result, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Check documentation truthfulness")
    parser.add_argument(
        "--format", choices=["markdown", "json"], default="markdown",
        help="Output format",
    )
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument(
        "--check", action="store_true",
        help="Exit non-zero if any blocker issues found",
    )
    parser.add_argument(
        "--root", default=".",
        help="Project root directory (default: current directory)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issues = scan_project(root)

    if args.format == "markdown":
        output = format_markdown(issues)
    else:
        output = format_json(issues)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(output)

    if args.check:
        blockers = [i for i in issues if i["severity"] == "blocker"]
        if blockers:
            print(f"\nFAILED: {len(blockers)} blocker issues found", file=sys.stderr)
            return 1
        print("\nPASSED: No blocker issues found")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
