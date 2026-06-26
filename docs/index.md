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
| Repository intake | `oss-paper-ci intake .` | Analyze repo structure, extract commands |
| Autoplan | `oss-paper-ci autoplan .` | Generate candidate reproducibility plan |
| Ecosystem detection | `oss-paper-ci ecosystems detect .` | Multi-language detection |
| Terminal workbench | `oss-paper-ci workbench .` | Full pipeline with progress |
| Evaluation | `oss-paper-ci eval run examples/evaluation-corpus` | Run benchmark evaluation |
| Quickstart | `oss-paper-ci quickstart` | Show first steps |
| Try demo | `oss-paper-ci try-demo` | Run built-in demo |
| Trust audit | `oss-paper-ci trust audit .` | Local static trust audit |
| Security scan | `oss-paper-ci security scan .` | Scan for secrets and dangerous patterns |
| Dependency inventory | `oss-paper-ci trust inventory .` | SBOM-like dependency inventory |
| Provenance manifest | `oss-paper-ci trust provenance .` | Generate provenance manifest |
| Artifact verification | `oss-paper-ci trust verify-artifacts .` | Verify SHA256 checksums |

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
- [Adapter registry](adapter-registry.md) — multi-language adapter system
- [Adapter schema](adapter-schema.md) — adapter report JSON format
- [Adapter safety](adapter-safety.md) — safety boundaries per adapter
- [Adapter limitations](adapter-limitations.md) — what adapters can and cannot do

### Features

- [Data diagnostics](data-diagnostics.md) — data availability and documentation checks
- [Result validation](result-validation.md) — result artifact existence and format
- [Evidence scores](evidence-scores.md) — score components and meaning
- [Language ecosystems](language-ecosystems.md) — multi-language detection and support
- [Language adapters](language-adapters.md) — adapter framework overview
- [Python adapter](python-adapter.md) — Python detection and planning
- [R adapter](r-adapter.md) — R detection and planning
- [Julia adapter](julia-adapter.md) — Julia detection and planning
- [Node.js adapter](node-adapter.md) — Node.js detection and planning
- [Rust adapter](rust-adapter.md) — Rust detection and planning
- [Java adapter](java-adapter.md) — Java detection and planning
- [C/C++ adapter](cpp-adapter.md) — C/C++ detection and planning
- [Make adapter](make-adapter.md) — Make detection and planning
- [Snakemake adapter](snakemake-adapter.md) — Snakemake detection (dry-run only)
- [Nextflow adapter](nextflow-adapter.md) — Nextflow detection (dry-run only)
- [Shell adapter](shell-adapter.md) — Shell script detection with safety blocking
- [Repository intake](repository-intake.md) — analyze repo structure, extract commands
- [Autoplan](autoplan.md) — generate candidate reproducibility plan
- [Reproduction](reproduce.md) — one-command reproduction attempt
- [Reproduction sessions](reproduction-sessions.md) — track, resume, and bundle reproduction attempts
- [Reproduction matrix](reproduction-matrix.md) — run across Python versions and profiles
- [Reproduction capsules](reproduction-capsules.md) — verifiable evidence packages
- [Batch scanning](batch-scan.md) — scan multiple projects
- [Workspace](workspace.md) — workspace configuration
- [Evidence graph](evidence-graph.md) — file dependency visualization

### Human-centered

- [Failure taxonomy](failure-taxonomy.md) — structured failure guidance
- [Roles](roles.md) — guidance for authors, reviewers, maintainers
- [Reproducibility dossier](dossier.md) — structured reproducibility assessment
- [Glossary](glossary.md) — terminology definitions

### Trust & Security

- [Trust & Security](trust.md) — overview of trust and security commands
- [Security scan](security-scan.md) — secret and dangerous pattern detection
- [Workflow audit](workflow-audit.md) — GitHub Actions workflow analysis
- [Dependency inventory](dependency-inventory.md) — SBOM-like inventory
- [Provenance manifest](provenance.md) — local provenance generation
- [Release verification](release-verification.md) — SHA256SUMS verification
- [Supply-chain security](supply-chain.md) — supply-chain considerations
- [Security limitations](security-limitations.md) — what checks can and cannot do

### Evidence Reports

- [Evidence report](evidence-report.md) — unified evidence report overview
- [Evidence bundle](evidence-bundle.md) — shareable evidence packages
- [Reviewer pack](reviewer-pack.md) — reviewer-focused guidance
- [Author pack](author-pack.md) — author-focused guidance
- [Maintainer pack](maintainer-pack.md) — maintainer-focused guidance
- [Evidence schema](evidence-schema.md) — JSON schema reference
- [Evidence limitations](evidence-limitations.md) — what reports do NOT verify

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
