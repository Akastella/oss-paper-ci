# OSS-Paper-CI

Scientific reproducibility evidence, from terminal to shareable reports.

## Start in three commands

```bash
# 1. Get guided recommendations
oss-paper-ci wizard

# 2. Run the full pipeline
oss-paper-ci workbench .

# 3. Safe reproduction attempt
oss-paper-ci reproduce examples/demo-reproduce-repo --dry-run
```

## Core workflows

| Workflow | Command | What it does |
|----------|---------|--------------|
| Readiness scan | `oss-paper-ci scan .` | Score and recommend improvements |
| Data diagnostics | `oss-paper-ci data diagnose .` | Check data documentation |
| Result validation | `oss-paper-ci results validate .` | Verify result claims |
| Safe reproduction | `oss-paper-ci reproduce URL --dry-run` | Attempt without executing |
| Reproduction capsule | `oss-paper-ci reproduce URL --execute --capsule out.zip` | Package evidence |
| Reproducibility dossier | `oss-paper-ci dossier .` | Human-readable summary |
| Workspace batch | `oss-paper-ci batch scan --workspace ws.yml` | Multi-project scan |
| Ecosystem detection | `oss-paper-ci ecosystems detect .` | Multi-language detection |
| Terminal workbench | `oss-paper-ci workbench .` | Full pipeline with progress |
| Evaluation | `oss-paper-ci eval run examples/evaluation-corpus` | Run benchmark evaluation |
| Quickstart | `oss-paper-ci quickstart` | Show first steps |
| Try demo | `oss-paper-ci try-demo` | Run built-in demo |

## Evaluation

The project includes a **synthetic-but-realistic evaluation corpus** to verify output stability across different repository states.

```bash
# Run evaluation
oss-paper-ci eval run examples/evaluation-corpus --format json --output report.json

# Compare against baseline
oss-paper-ci eval compare --baseline tests/golden/evaluation_summary.json --current report.json
```

See [Evaluation](evaluation.md) for details.

## Demo gallery

- [Demo paper repo](demo-paper-repo.md) — example repository
- [Demo gallery](demo-gallery.md) — example reports and outputs
- [Terminal examples](../examples/terminal/) — workbench, wizard, and theme previews
- [Example reports](../examples/reports/) — scan, reproduce, and dossier reports

## Documentation

### Getting started

- [Getting started](getting-started.md) — first steps
- [First run](first-run.md) — 60-second getting started guide
- [Installation](installation.md) — pip, pipx, source install
- [CLI reference](cli-reference.md) — all commands and options

### Core concepts

- [Terminal workbench](terminal-workbench.md) — multi-step pipeline
- [Project summary](project-summary.md) — what and why
- [Wizard](wizard.md) — guided setup for new users
- [Themes](themes.md) — terminal color themes
- [CLI UX](cli-ux.md) — output modes and components
- [No-color and CI](no-color-and-ci.md) — CI-friendly output
- [Configuration](configuration.md) — `.oss-paper-ci.yml` reference
- [Policy profiles](policy-profiles.md) — lenient, default, strict, publication
- [Report formats](report-formats.md) — Markdown, JSON, SARIF, HTML
- [Security model](security-model.md) — dry-run, execute, capsule safety

### Features

- [Data diagnostics](data-diagnostics.md) — data availability and documentation checks
- [Result validation](result-validation.md) — result artifact existence and format
- [Evidence scores](evidence-scores.md) — score components and meaning
- [Language ecosystems](language-ecosystems.md) — multi-language detection and support
- [Reproduction](reproduce.md) — one-command reproduction attempt
- [Reproduction capsules](reproduction-capsules.md) — verifiable evidence packages
- [Batch scanning](batch-scan.md) — scan multiple projects
- [Workspace](workspace.md) — workspace configuration
- [Evidence graph](evidence-graph.md) — file dependency visualization

### Human-centered

- [Failure taxonomy](failure-taxonomy.md) — structured failure guidance
- [Roles](roles.md) — guidance for authors, reviewers, maintainers
- [Reproducibility dossier](dossier.md) — structured reproducibility assessment
- [Glossary](glossary.md) — terminology definitions

### Reference

- [Check categories](checks.md) — what gets checked
- [Docker](docker.md) — container-based usage
- [Dev Container](devcontainer.md) — VS Code development environment
- [Troubleshooting](troubleshooting.md) — common issues and solutions
- [Limitations](limitations.md) — what this tool does NOT do
- [Full index](index.md) — this page

## Safety and limitations

OSS-Paper-CI records and explains reproducibility evidence. It does not prove scientific correctness, judge paper quality, or predict acceptance.

- Default mode is **dry-run**: no code executed, no dependencies installed
- `--execute` is required to run reproduction commands
- Dangerous commands are blocked
- Score is engineering completeness, not a scientific judgment
- See [limitations.md](limitations.md) and [security-model.md](security-model.md)
