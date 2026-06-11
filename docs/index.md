# Documentation Index

## Getting Started

- [Getting Started](getting-started.md) — first steps with oss-paper-ci
- [Installation](installation.md) — pip, pipx, source install
- [Quickstart](demo.md) — run your first scan

## Core Concepts

- [CLI Reference](cli-reference.md) — all commands and options
- [Configuration](configuration.md) — `.oss-paper-ci.yml` reference
- [Policy Profiles](policy-profiles.md) — lenient, default, strict, publication
- [Report Formats](report-formats.md) — Markdown, JSON, SARIF, HTML
- [Security Model](security-model.md) — dry-run, execute, capsule safety

## Features

- [Data Diagnostics](data-diagnostics.md) — data availability and documentation checks
- [Result Validation](result-validation.md) — result artifact existence and format
- [Evidence Scores](evidence-scores.md) — score components and meaning
- [Language Ecosystems](language-ecosystems.md) — multi-language detection and support
- [Reproduction](reproduce.md) — one-command reproduction attempt
- [Reproduction Capsules](reproduction-capsules.md) — verifiable evidence packages
- [Capsule Format](capsule-format.md) — capsule structure specification
- [Capsule Verification](capsule-verify.md) — integrity checking
- [Batch Scanning](batch-scan.md) — scan multiple projects
- [Workspace](workspace.md) — workspace configuration
- [Cache](cache.md) — incremental scanning
- [Batch Diff](batch-diff.md) — compare batch reports
- [Evidence Graph](evidence-graph.md) — file dependency visualization
- [Baselines](baselines.md) — regression detection
- [Smoke Runs](smoke-runs.md) — safe experiment execution
- [Custom Rules](rule-sdk.md) — extend without Python code

## Human-Centered

- [Human-Centered Reproducibility](human-centered-reproducibility.md) — design principles
- [Failure Taxonomy](failure-taxonomy.md) — structured failure guidance
- [Roles](roles.md) — guidance for authors, reviewers, maintainers
- [Glossary](glossary.md) — terminology definitions
- [Internationalization](i18n.md) — multilingual READMEs

## Dossier

- [Reproducibility Dossier](dossier.md) — structured reproducibility assessment
- [Evidence Map](evidence-map.md) — evidence inventory
- [Remediation Plan](remediation-plan.md) — actionable improvement steps

## Reference

- [Check Categories](checks.md) — what gets checked
- [Check Authoring](check-authoring.md) — write custom checks
- [Rule Pack Manifest](rule-pack-manifest.md) — YAML rule format
- [Report Schema](report-schema.md) — JSON report structure
- [Cross-Language](cross-language.md) — R, Julia, MATLAB support
- [Limitations](limitations.md) — what this tool does NOT do

## GitHub Actions

- [GitHub Actions Guide](github-actions.md) — CI integration
- [GitHub Annotations](github-upload.md) — SARIF and annotations

## Examples

- [Demo Gallery](demo-gallery.md) — example reports and outputs
- [Demo Paper Repo](demo-paper-repo.md) — example repository
- [Rule Packs](../examples/rule-packs/) — example custom rules
- [Workspaces](../examples/workspaces/) — example workspace configs

## Release

- [Release Process](release-process.md) — how to release
- [Release Checklist](../RELEASE_CHECKLIST.md) — pre-release checks
- [Packaging](packaging.md) — package structure
