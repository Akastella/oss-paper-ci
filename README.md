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

## Quickstart

```bash
# Install
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"

# Get guided recommendations
oss-paper-ci wizard

# Run the full pipeline
oss-paper-ci workbench .

# Score a repository
oss-paper-ci scan .

# Safe reproduction attempt
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
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
| Reproduction capsule | `oss-paper-ci capsule verify out.zip` | Verify and inspect evidence packages |
| Reproducibility dossier | `oss-paper-ci dossier .` | Generate author/reviewer/maintainer summaries |
| Workspace batch | `oss-paper-ci batch scan --workspace ws.yml` | Scan multiple projects from a config |
| Ecosystem detection | `oss-paper-ci ecosystems detect .` | Detect Python, R, Julia, MATLAB, Node, and more |
| Terminal workbench | `oss-paper-ci workbench .` | Multi-step pipeline with progress display |
| Guided wizard | `oss-paper-ci wizard` | Safe next-step recommendations for new users |

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
