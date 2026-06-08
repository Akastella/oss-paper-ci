# GitHub Upload Guide

This guide explains how to upload oss-paper-ci to a GitHub repository using the clean release package.

## Using the Clean ZIP

1. Download `oss-paper-ci-v1.0.0rc1-github-clean.zip` from the release artifacts
2. Extract the ZIP file
3. The extracted folder contains the complete repository structure

```bash
unzip oss-paper-ci-v1.0.0rc1-github-clean.zip
cd oss-paper-ci
```

4. Initialize a new git repository:

```bash
git init
git add .
git commit -m "Initial oss-paper-ci release v1.0.0rc1"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Important Notes

- The clean ZIP does **not** contain `.git/` history — you must initialize a fresh repository
- The ZIP is audit-verified to exclude: `__pycache__/`, `*.egg-info/`, `.pytest_cache/`, `dist/`, `build/`, development history files
- All files in the ZIP are ready for public GitHub hosting

## Verifying the Package

After extracting, verify the package works:

```bash
pip install -e ".[dev]"
oss-paper-ci version
python -m pytest
```

## SHA256 Verification

Verify the ZIP integrity using `SHA256SUMS.txt`:

```bash
sha256sum -c SHA256SUMS.txt
```

## What's Included

- `src/` — Python package source
- `tests/` — Test suite
- `docs/` — Documentation
- `examples/` — Usage examples
- `scripts/` — Utility scripts
- `dogfooding/` — Self-scan results
- `.github/` — CI workflows
- `action.yml` — GitHub Action definition
- `pyproject.toml` — Package metadata

## What's Excluded

- `.git/` — Git history
- `__pycache__/`, `*.pyc` — Python cache
- `*.egg-info/` — Build metadata
- `.pytest_cache/` — Test cache
- `dist/`, `build/` — Build artifacts
- `dev-history/` — Development history
- `round*.json`, `ROUND*.md` — Temporary reports
