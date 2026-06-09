# oss-paper-ci

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Release](https://img.shields.io/github/v/release/Akastella/oss-paper-ci)](https://github.com/Akastella/oss-paper-ci/releases)

CI tool for checking reproducibility readiness of scientific paper repositories.

OSS-Paper-CI checks whether a scientific repository is ready for
reproducibility-oriented CI: metadata, environment files, experiment scripts,
result artifacts, evidence graph links, baseline regressions, safe smoke runs,
and GitHub/SARIF reporting.

## Quick demo

```bash
python -m pip install -e ".[dev]"
oss-paper-ci scan tests/fixtures/realistic_ml_repo --format markdown
oss-paper-ci graph tests/fixtures/realistic_ml_repo --format markdown
```

See example reports:
- [Markdown scan report](examples/reports/realistic_ml_report.md)
- [Evidence graph](examples/reports/realistic_ml_graph.md)
- [Baseline comparison](examples/reports/realistic_ml_baseline_compare.md)
- [Smoke run report](examples/reports/realistic_ml_smoke.md)
- [SARIF output](examples/reports/realistic_ml.sarif)

See [docs/demo.md](docs/demo.md) for full reproduction instructions.

## Quick path

1. **Install**: `python -m pip install -e ".[dev]"`
2. **Diagnose**: `oss-paper-ci doctor .`
3. **Initialize**: `oss-paper-ci init --all --dry-run`
4. **Scan locally**: `oss-paper-ci scan . --format html --output report.html`
5. **Generate PR comment**: `oss-paper-ci comment --input report.json --output pr-comment.md`
6. **Use in GitHub Actions**: see [examples/github-actions/](examples/github-actions/)
7. **Upload SARIF**: `oss-paper-ci scan . --format sarif --output report.sarif`

### GitHub Actions integration

```yaml
- name: Run oss-paper-ci
  run: |
    oss-paper-ci scan . --format json --output report.json
    oss-paper-ci scan . --format html --output report.html
    oss-paper-ci scan . --format sarif --output report.sarif
    oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

See [docs/github-actions.md](docs/github-actions.md) for full workflow templates.

See also:
- [docs/doctor.md](docs/doctor.md) — diagnose your repo
- [docs/init.md](docs/init.md) — scaffold reproducibility assets
- [docs/html-report.md](docs/html-report.md) — HTML report format
- [docs/pr-comment.md](docs/pr-comment.md) — PR comment generation
- [docs/sarif.md](docs/sarif.md) — SARIF export for GitHub Code Scanning
- [examples/demo-paper-repo/](examples/demo-paper-repo/) — example paper repository
- [examples/reports/demo_paper_report.html](examples/reports/demo_paper_report.html) — example HTML report
- [examples/reports/demo_paper_pr_comment.md](examples/reports/demo_paper_pr_comment.md) — example PR comment

## What it checks

Scans a repository for engineering basics needed for reproducibility: environment
files, README, citation info, data documentation, experiment scripts, and CI
configuration. Produces a scored report with actionable recommendations.

## What it does NOT check

- Paper quality or scientific merit
- Whether results are correct
- Paper acceptance likelihood
- Peer review
- Running your experiments

## Quickstart

```bash
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
python -m pip install -e ".[dev]"
oss-paper-ci version
```

Then scan a repository:

```bash
oss-paper-ci scan /path/to/your/repo
```

## GitHub Actions usage

The recommended way to use oss-paper-ci in your CI is via the GitHub Action.

After oss-paper-ci is published to GitHub with a tag (e.g. `v1`):

```yaml
name: Reproducibility Check

on:
  pull_request:
  push:
    branches: [main]

jobs:
  oss-paper-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: Akastella/oss-paper-ci@v1.0.0rc1
        with:
          path: "."
          format: "markdown"
          output: "oss-paper-ci-report.md"
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: oss-paper-ci-report
          path: oss-paper-ci-report.md
```

For more options (SARIF upload, PR comments, baseline regression), see
[examples/github-actions/](examples/github-actions/) and
[docs/github-actions.md](docs/github-actions.md).

## CLI

### Scan

```bash
# Scan current directory (markdown output)
oss-paper-ci scan

# Scan specific path, output JSON
oss-paper-ci scan /path/to/repo --format json

# Write report to file
oss-paper-ci scan --format markdown -o report.md

# SARIF output for GitHub Code Scanning
oss-paper-ci scan --format sarif -o results.sarif

# Use custom config
oss-paper-ci scan --config my-config.yml
```

### Init

Generate a default config file:

```bash
oss-paper-ci init
```

Creates `oss-paper-ci.yml` in the current directory.

### Explain

Get details about a specific check:

```bash
oss-paper-ci explain ENV001
```

### List checks

```bash
oss-paper-ci list-checks
```

### Version

```bash
oss-paper-ci version
```

## Report formats

| Format     | Flag                    | Use case                          |
|------------|-------------------------|-----------------------------------|
| Markdown   | `--format markdown`     | Human-readable, CI artifacts      |
| JSON       | `--format json`         | Programmatic access, CI gates     |
| SARIF      | `--format sarif`        | GitHub Code Scanning, VS Code     |

## Check categories

| Category    | Prefix | What it checks                                     |
|-------------|--------|----------------------------------------------------|
| Metadata    | META   | README, license, citation, contributing guidelines |
| Environment | ENV    | Dependency files, lock files, Python version       |
| Experiments | EXP    | Entry points, reproduction scripts, seeds, config  |
| Data        | DATA   | Data docs, download instructions, large files      |
| Results     | RES    | Output directories, figure generation, metrics     |
| Paper-Code  | PAP    | LaTeX/paper links, figure references, tables       |
| CI          | CI     | Workflow files, test config, linting, templates    |

## Reproducibility contract

Define expected reproduction steps in `reproducibility.yml`:

```yaml
experiments:
  - id: train
    command: python scripts/train.py
    timeout: 300
  - id: evaluate
    command: python scripts/evaluate.py
    depends_on: [train]
```

See [docs/reproducibility-contract.md](docs/reproducibility-contract.md).

## Evidence graph

Visualize file dependencies and relationships:

```bash
oss-paper-ci graph /path/to/repo --format json
oss-paper-ci graph /path/to/repo --format dot --show-orphans
```

See [docs/evidence-graph.md](docs/evidence-graph.md).

## Baseline regression

Create a score baseline and detect regressions:

```bash
oss-paper-ci baseline create /path/to/repo --output baseline.json
oss-paper-ci baseline compare /path/to/repo --baseline baseline.json
```

See [docs/baselines.md](docs/baselines.md).

## Smoke runs

Run experiment smoke tests with a security policy:

```bash
oss-paper-ci smoke /path/to/repo --dry-run
oss-paper-ci smoke /path/to/repo --experiment train --timeout 120
```

See [docs/smoke-runs.md](docs/smoke-runs.md).

## Cross-language support

Python has the deepest static analysis. R, Julia, MATLAB, Make, and Snakemake
currently receive basic reproducibility asset checks (environment files, script
entry points, data/result directories), not full semantic validation.

See [docs/cross-language.md](docs/cross-language.md) for details.

## Pre-commit hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
```

See [docs/pre-commit.md](docs/pre-commit.md) for configuration options.

## Configuration

Create `oss-paper-ci.yml` in your repo root (or run `oss-paper-ci init`):

```yaml
version: "0.1"
project:
  name: "my-paper"
  paper_dir: "paper"
  code_dirs:
    - "src"
    - "scripts"
  data_dirs:
    - "data"
  results_dirs:
    - "results"
    - "figures"
checks:
  min_score: 70
  require_license: true
  require_citation: true
  require_environment: true
  require_quickstart: true
  disabled:
    - "META005"
  severity_overrides:
    "CI001": "warning"
ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
output:
  default_format: "markdown"
```

See [docs/configuration.md](docs/configuration.md) for the full reference.

## Score interpretation

The score is 0-100. Status is determined by:

| Status | Meaning                                                     |
|--------|-------------------------------------------------------------|
| pass   | Score >= `min_score` AND no error-level failures            |
| warn   | Score >= `min_score` with warnings, OR no errors but < 80  |
| fail   | Any error-level check failed, OR score < 50                 |

A high score means good engineering practices for reproducibility. It does not
mean the science is correct. A low score means missing engineering basics, not
bad research.

## Limitations

- No deep LaTeX compilation -- detects `.tex` files but does not compile them.
- No experiment execution -- checks for scripts but does not run them.
- No result value verification -- checks for output directories, not correctness.
- Cross-language checks are shallow: Python has the deepest static analysis;
  R, Julia, MATLAB, Make, and Snakemake currently receive basic reproducibility
  asset checks, not full semantic validation.
- Score is readiness, not quality.

See [docs/limitations.md](docs/limitations.md) for the full list.

## Development

```bash
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
python -m pip install -e ".[dev]"
python -m pytest tests/ -v
```

To add a new check, see [docs/check-authoring.md](docs/check-authoring.md).

## License

MIT -- see [LICENSE](LICENSE).
