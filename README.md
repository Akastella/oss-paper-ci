# oss-paper-ci

[![CI](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/Akastella/oss-paper-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

CLI toolkit for checking, attempting, and packaging scientific repository reproducibility evidence.

## What it does

- **scan** a paper repository for reproducibility readiness (environment files, scripts, data docs, CI config)
- **reproduce** a repository by cloning, installing, and running commands (default: dry-run)
- **capsule** a reproduction attempt into a verifiable, archivable evidence package
- **batch** scan multiple projects from a workspace configuration
- **diff** scan reports to track changes over time

## Install

```bash
# From source (recommended for development)
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# Verify
oss-paper-ci version
```

## Three useful commands

```bash
# 1. Scan a repository
oss-paper-ci scan examples/demo-paper-repo --format markdown

# 2. Attempt reproduction (safe: dry-run by default)
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run

# 3. Verify a reproduction capsule
oss-paper-ci capsule verify repro-capsule.zip
```

## Quickstart

```bash
# Scan your repo
oss-paper-ci scan /path/to/your/repo

# Get a scored report with recommendations
oss-paper-ci scan . --format html --output report.html

# Use in CI with GitHub Actions
oss-paper-ci scan . --format github --github-step-summary "$GITHUB_STEP_SUMMARY"
```

## One-command reproduction attempt

```bash
# Dry-run: see what would happen (safe, no code executed)
oss-paper-ci reproduce https://github.com/owner/paper-repo --dry-run

# Execute: clone, install, run, and generate a report
oss-paper-ci reproduce https://github.com/owner/paper-repo \
  --execute --install --format html --output repro-report.html

# Generate a verifiable capsule
oss-paper-ci reproduce examples/demo-reproduce-repo \
  --execute --install --capsule repro-capsule.zip
```

The reproduce command clones a repository, detects environment files,
installs dependencies (in an isolated venv), runs reproduction commands,
and generates a structured report. Default mode is dry-run -- `--execute`
is required to actually run code.

**Important:** This is an *attempted reproduction*, not guaranteed reproduction.
The tool records what was done, not whether the results are correct.

## Reproduction capsules

```bash
# Verify capsule integrity
oss-paper-ci capsule verify repro-capsule.zip

# Inspect capsule contents
oss-paper-ci capsule inspect repro-capsule.zip

# Compare two capsules
oss-paper-ci capsule diff old.zip new.zip
```

A capsule is a self-contained evidence package with manifest, reports,
logs, artifacts, metadata, and SHA256 integrity checksums. It is NOT
proof that a paper is correct.

## GitHub Actions

```yaml
- uses: actions/checkout@v4
- uses: Akastella/oss-paper-ci@v1
  with:
    path: "."
    format: "markdown"
```

See [examples/github-actions/](examples/github-actions/) for full workflow templates.

## Documentation

| Topic | Link |
|-------|------|
| Getting started | [docs/getting-started.md](docs/getting-started.md) |
| Installation | [docs/installation.md](docs/installation.md) |
| CLI reference | [docs/cli-reference.md](docs/cli-reference.md) |
| Security model | [docs/security-model.md](docs/security-model.md) |
| Demo gallery | [docs/demo-gallery.md](docs/demo-gallery.md) |
| Reproduction | [docs/reproduce.md](docs/reproduce.md) |
| Capsules | [docs/reproduction-capsules.md](docs/reproduction-capsules.md) |
| GitHub Actions | [docs/github-actions.md](docs/github-actions.md) |
| Configuration | [docs/configuration.md](docs/configuration.md) |
| Policy profiles | [docs/policy-profiles.md](docs/policy-profiles.md) |
| Limitations | [docs/limitations.md](docs/limitations.md) |
| Full index | [docs/index.md](docs/index.md) |

## Security model

- Default mode is **dry-run**: no code executed, no dependencies installed
- `--execute` is required to run reproduction commands
- `--install` is required to install dependencies (into an isolated venv)
- Dangerous commands are blocked (rm -rf, sudo, fork bombs)
- Every command has a configurable timeout
- See [docs/security-model.md](docs/security-model.md) and [docs/reproduce-security.md](docs/reproduce-security.md)

## Limitations

- Checks reproducibility *readiness*, not scientific correctness
- Does not verify paper quality, novelty, or acceptance likelihood
- Does not run experiments (unless explicitly `--execute`)
- Does not resolve missing data or fix broken code
- Cross-language checks are shallow outside Python
- Score is engineering completeness, not a scientific judgment

See [docs/limitations.md](docs/limitations.md).

## Development

```bash
pip install -e ".[dev]"
python -m pytest
python -m build
python -m twine check dist/*
python scripts/check_docs_truthfulness.py --check
```

## License

MIT -- see [LICENSE](LICENSE).
