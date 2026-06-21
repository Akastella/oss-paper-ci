# OSS-Paper-CI

**English** | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

CLI toolkit for checking, attempting, packaging, and explaining reproducibility evidence for scientific repositories.

```bash
# Not sure where to start?
oss-paper-ci wizard

# Run the full pipeline
oss-paper-ci workbench .

# Safe reproduction attempt (dry-run by default)
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
```

OSS-Paper-CI records and explains reproducibility evidence. It does not prove scientific correctness, judge paper quality, or predict acceptance.

## Quick start

```bash
# 1. Install from GitHub
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e .

# 2. Try it in 60 seconds
oss-paper-ci try-demo

# 3. Scan your repository
oss-paper-ci scan .
```

**Alternative install methods:** See [Installation](docs/installation.md) for pipx, wheel, and source options.

> **Note:** oss-paper-ci is not yet published on PyPI. Install from GitHub source.

## First run

```bash
# Get personalized recommendations
oss-paper-ci quickstart

# Topic-specific guidance
oss-paper-ci quickstart --topic install
oss-paper-ci quickstart --topic github-action
oss-paper-ci quickstart --topic reproduce
oss-paper-ci quickstart --topic eval
```

## Evaluation

The project includes a **synthetic-but-realistic evaluation corpus** to verify output stability across different repository states.

```bash
# Run evaluation against the corpus
oss-paper-ci eval run examples/evaluation-corpus

# Generate JSON report
oss-paper-ci eval run examples/evaluation-corpus --format json --output report.json

# Compare against baseline
oss-paper-ci eval compare --baseline tests/golden/evaluation_summary.json --current report.json
```

The evaluation corpus contains 12+ synthetic repositories covering:
- Python (well-reproducible, missing data, missing environment, bad results)
- R, Julia, Node.js, Make, Snakemake, C++ projects
- Unsafe script detection
- Before/after adoption comparison

**Important:** These are synthetic test fixtures, not real-world repositories. The benchmark demonstrates tool stability, not scientific correctness.

## What it does

| Feature | Command | Description |
|---------|---------|-------------|
| Readiness scan | `oss-paper-ci scan .` | Score reproducibility readiness with recommendations |
| Data diagnostics | `oss-paper-ci data diagnose .` | Check data documentation and availability |
| Result validation | `oss-paper-ci results validate .` | Verify claimed results trace to evidence |
| Safe reproduction | `oss-paper-ci reproduce URL --dry-run` | Attempt reproduction without executing code |
| Reproduction orchestrator | `oss-paper-ci reproduce plan/run/report` | Plan, execute, and verify reproduction workflow |
| Reproduction capsule | `oss-paper-ci capsule verify out.zip` | Verify and inspect evidence packages |
| Reproducibility dossier | `oss-paper-ci dossier .` | Generate author/reviewer/maintainer summaries |
| Workspace batch | `oss-paper-ci batch scan --workspace ws.yml` | Scan multiple projects from a config |
| Ecosystem detection | `oss-paper-ci ecosystems detect .` | Detect Python, R, Julia, MATLAB, Node, and more |
| Terminal workbench | `oss-paper-ci workbench .` | Multi-step pipeline with progress display |
| Guided wizard | `oss-paper-ci wizard` | Safe next-step recommendations for new users |
| Trust audit | `oss-paper-ci trust audit .` | Local static trust and workflow audit |
| Security scan | `oss-paper-ci security scan .` | Scan for secrets, dangerous patterns, Docker risks |
| Dependency inventory | `oss-paper-ci trust inventory .` | SBOM-like dependency inventory |
| Provenance manifest | `oss-paper-ci trust provenance .` | Generate local provenance manifest |
| Artifact verification | `oss-paper-ci trust verify-artifacts .` | Verify SHA256 checksums |
| Evidence report | `oss-paper-ci evidence .` | Unified evidence report (all checks) |
| Evidence bundle | `oss-paper-ci evidence bundle .` | Shareable evidence package |

## Safety model

- Default mode is **dry-run**: no code executed, no dependencies installed
- `--execute` is required to run reproduction commands
- `--install` is required to install dependencies (into an isolated venv)
- Dangerous commands are blocked (rm -rf, sudo, fork bombs)
- Every command has a configurable timeout
- Configurable policy profiles: lenient, default, strict, publication
- See [docs/security-model.md](docs/security-model.md)

## Example workflows

```bash
# Score a repository
oss-paper-ci scan .

# Full pipeline with output files
oss-paper-ci workbench . --output-dir results

# Safe reproduction attempt
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# CI integration
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

See [examples/github-actions/](examples/github-actions/) for workflow templates.

## Trust & Security

OSS-Paper-CI includes local static checks for supply-chain trust and security:

```bash
# Trust audit (workflow risks, permissions, action pinning)
oss-paper-ci trust audit .

# Security scan (secrets, dangerous patterns, Docker risks)
oss-paper-ci security scan .

# Dependency inventory (SBOM-like)
oss-paper-ci trust inventory .

# Provenance manifest
oss-paper-ci trust provenance .

# Verify release artifacts
oss-paper-ci trust verify-artifacts release-artifacts/
```

**Important:** These are local static analysis checks only. They are not a security certification, do not verify third-party integrity, and do not claim SLSA, Sigstore, or SPDX compliance. See [SECURITY.md](SECURITY.md) for the full threat model and limitations.

## Evidence Report

The unified evidence report aggregates all checks into a single shareable document:

```bash
# Reviewer-focused report
oss-paper-ci evidence . --profile reviewer --format html --output evidence.html

# Author-focused report with next steps
oss-paper-ci evidence . --profile author --format markdown

# Create shareable bundle
oss-paper-ci evidence bundle . --output evidence-bundle.zip

# Verify bundle integrity
oss-paper-ci evidence verify evidence-bundle.zip
```

The evidence report helps authors and reviewers communicate "what reproducibility evidence exists" — it does not prove scientific correctness or predict acceptance. See [docs/evidence-report.md](docs/evidence-report.md).

## Reproduction Orchestrator

The reproduction orchestrator reads `reproducibility.yml`, generates an execution plan, runs declared commands (with explicit authorization), collects artifacts and metrics, and generates verification reports.

```bash
# Generate a plan (never executes code)
oss-paper-ci reproduce plan examples/repro-system-demo

# Execute with safety gates
oss-paper-ci reproduce run examples/repro-system-demo --execute --sandbox local

# Generate HTML report
oss-paper-ci reproduce report .oss-paper-ci-repro-run --format html --output reproduction.html

# Compare against expected values
oss-paper-ci reproduce compare .oss-paper-ci-repro-run --expected examples/repro-system-demo/reproducibility.yml

# Create evidence bundle
oss-paper-ci reproduce bundle .oss-paper-ci-repro-run --output reproduction-evidence.zip
```

The orchestrator defaults to dry-run. It does not prove scientific correctness — it only verifies that declared reproduction steps can be executed and that artifacts and metrics match expectations. See [docs/reproduction-orchestrator.md](docs/reproduction-orchestrator.md).

## Documentation

| Topic | Link |
|-------|------|
| Getting started | [docs/getting-started.md](docs/getting-started.md) |
| CLI reference | [docs/cli-reference.md](docs/cli-reference.md) |
| Terminal workbench | [docs/terminal-workbench.md](docs/terminal-workbench.md) |
| Project summary | [docs/project-summary.md](docs/project-summary.md) |
| Demo gallery | [docs/demo-gallery.md](docs/demo-gallery.md) |
| Full index | [docs/index.md](docs/index.md) |

## Limitations

- Checks reproducibility *readiness*, not scientific correctness
- Does not verify paper quality, novelty, or acceptance likelihood
- Does not run experiments (unless explicitly `--execute`)
- Does not resolve missing data or fix broken code
- Score is engineering completeness, not a scientific judgment

See [docs/limitations.md](docs/limitations.md).

## Development

```bash
pip install -e ".[dev]"
python -m pytest
python scripts/check_docs_truthfulness.py --check
```

## License

MIT -- see [LICENSE](LICENSE).
