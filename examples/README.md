# Examples

This directory contains example configurations for integrating oss-paper-ci
into your workflow.

## GitHub Actions

### Recommended: Use the GitHub Action

After oss-paper-ci is published to GitHub with a tag (e.g. `v1`):

```bash
mkdir -p .github/workflows
cp examples/github-actions/use-action.yml .github/workflows/
```

Replace `Akastella/oss-paper-ci` with the actual repository after publication.

### Source checkout (before Action/PyPI publication)

Check out the oss-paper-ci tool repository and install from source:

```bash
mkdir -p .github/workflows
cp examples/github-actions/source-checkout.yml .github/workflows/
```

### PyPI installation (after publication)

After oss-paper-ci is published to PyPI:

```bash
mkdir -p .github/workflows
cp examples/github-actions/pypi-after-publication.yml .github/workflows/
```

### SARIF upload

Uploads results to GitHub Code Scanning:

```bash
mkdir -p .github/workflows
cp examples/github-actions/sarif-upload.yml .github/workflows/
```

Requires `security-events: write` permission.

### PR comment

Posts the report as a PR comment:

```bash
mkdir -p .github/workflows
cp examples/github-actions/pr-comment.yml .github/workflows/
```

Requires `pull-requests: write` permission. Note: fork PRs may not have
permission to post comments.

### Baseline regression

Creates a baseline from main and compares the PR against it:

```bash
mkdir -p .github/workflows
cp examples/github-actions/baseline-regression.yml .github/workflows/
```

### Full CI pipeline

Complete pipeline with SARIF, PR comments, and artifacts:

```bash
mkdir -p .github/workflows
cp examples/github-actions/full-ci.yml .github/workflows/
```

## Composite Action

The repository root includes an `action.yml` composite action:

```yaml
- uses: Akastella/oss-paper-ci@v1
  with:
    path: "."
    format: "markdown"
    output: "report.md"
```

## Pre-commit

Add oss-paper-ci as a [pre-commit](https://pre-commit.com/) hook:

```bash
pip install pre-commit
cp examples/pre-commit/.pre-commit-config.yaml .
pre-commit install
```

Or add to an existing `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
```

Replace `v1.0.0rc1` with the actual release tag after publication.
