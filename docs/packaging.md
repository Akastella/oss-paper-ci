# Packaging Guide

This document describes how to build and distribute oss-paper-ci.

## Development Installation

```bash
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies (pytest, build, twine).

## Building

```bash
python -m build
```

This creates:
- `dist/oss_paper_ci-1.0.0rc1.tar.gz` — Source distribution
- `dist/oss_paper_ci-1.0.0rc1-py3-none-any.whl` — Wheel distribution

## Checking

```bash
python -m twine check dist/*
```

This validates the package metadata and structure.

## Creating a Clean Release Package

```bash
python scripts/make_release_package.py --version 1.0.0rc1
```

This creates in `release-artifacts/`:
- `oss-paper-ci-v1.0.0rc1-github-clean.zip` — Clean GitHub-ready ZIP
- `oss-paper_ci-1.0.0rc1-sdist.tar.gz` — Source distribution
- `oss_paper_ci-1.0.0rc1-py3-none-any.whl` — Wheel
- `SHA256SUMS.txt` — Checksums
- `RELEASE_PACKAGE_AUDIT.md` — Audit report

## Version Numbers

Version follows Python packaging conventions:
- `1.0.0rc1` — Release candidate
- `0.4.0` — Final release
- `0.4.1` — Patch release

Version is defined in:
- `src/oss_paper_ci/__init__.py`
- `pyproject.toml`

## Dependencies

Runtime:
- `pyyaml>=6.0`

Development:
- `pytest>=7.0`
- `pytest-cov>=4.0`
- `build>=1.0`
- `twine>=5.0`

## Publishing to PyPI (Future)

When ready to publish:

```bash
python -m build
python -m twine upload dist/*
```

Note: oss-paper-ci is not yet published to PyPI. Install from GitHub or local source.
