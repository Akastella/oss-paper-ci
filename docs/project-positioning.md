# oss-paper-ci -- Project Positioning

## Project

**Name:** oss-paper-ci
**Repository:** https://github.com/Akastella/oss-paper-ci
**Description:** CI tool for checking reproducibility readiness of scientific paper repositories

## Mission

Help scientific repositories meet reproducibility standards by automating
the detection of engineering gaps that make research hard to reproduce.

## Why this matters

Scientific research increasingly depends on software, but most paper repositories
lack basic engineering practices. Reviewers, collaborators, and future researchers
waste hours figuring out how to set up environments, find data, or run experiments.

A 2024 study found that over 70% of machine learning paper repositories could not
be reproduced from the provided instructions alone. Common issues:

- No `requirements.txt` or environment specification
- No license, so code cannot be legally reused
- No data download instructions
- No citation information
- Missing reproduction scripts

These are not science problems -- they are engineering problems. oss-paper-ci
addresses them at the repository level, before a paper is submitted or reviewed.

## Who benefits

- **Researchers:** Get a clear checklist of what to fix before submission.
- **Reviewers:** Quickly assess whether a repository is set up for reproduction.
- **Reproducers:** Identify the engineering gaps that block re-running experiments.
- **Maintainers:** Enforce reproducibility standards across a lab or organization.

## Design philosophy

- **Deterministic checks.** Same input always produces the same output. No LLM, no heuristics that drift.
- **No external dependencies.** Runs entirely locally. No network calls, no API keys.
- **CI-native.** Exit codes map to pipeline states (pass/warn/fail). Designed to run in GitHub Actions, GitLab CI, or any CI system.
- **Explainable.** Every check result includes the specific files or patterns that triggered it, plus a concrete recommendation.
- **Non-judgmental.** Evaluates repository engineering, not research quality. A low score means missing engineering practices, not bad science.
- **Extensible.** New checkers are added by subclassing `BaseChecker` and registering with `@register`.

## Current state

- **Version:** 0.1.0
- **Checks:** 41 checks across 8 categories (Metadata, Environment, Experiments, Data, Results, Paper-Code, CI)
- **CLI:** 4 commands -- `scan`, `init`, `explain`, `version`
- **Output:** JSON and Markdown report formats
- **Configuration:** YAML-based with sensible defaults
- **Integration:** GitHub Actions workflow examples included
- **License:** MIT

## Limitations

See [limitations.md](limitations.md) for a full list.

In brief: this tool checks for files and patterns. It does not compile LaTeX,
run experiments, verify result values, or assess scientific quality. It is
static analysis for repository engineering readiness.

## No exaggeration

This is a practical engineering tool, not a research contribution. It checks for
files and patterns. It does not understand the science. It will not make bad
research good. It will make well-intentioned research easier to reproduce.
