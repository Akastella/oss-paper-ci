# Dependency Inventory

**Project:** oss-paper-ci v2.9.0rc1
**Python:** >=3.10
**License:** MIT

## Ecosystems Detected

- python
- github-actions
- docker

## Runtime Dependencies

- `pyyaml>=6.0`
- `rich>=13.0`

## Dev Dependencies

- `pytest>=7.0`
- `pytest-cov>=4.0`
- `build>=1.0`
- `twine>=5.0`

## Optional Dependencies

### dev
- `pytest>=7.0`
- `pytest-cov>=4.0`
- `build>=1.0`
- `twine>=5.0`

## Scripts / Entry Points

- `oss-paper-ci` → `oss_paper_ci.cli:main`

## GitHub Actions Used

- `actions/checkout@v6` (in ci.yml)
- `actions/setup-python@v6` (in ci.yml)
- `actions/checkout@v6` (in ci.yml)
- `actions/setup-python@v6` (in ci.yml)
- `actions/checkout@v6` (in docs.yml)
- `actions/setup-python@v6` (in docs.yml)
- `actions/upload-pages-artifact@v5` (in docs.yml)
- `actions/deploy-pages@v5` (in docs.yml)
- `actions/checkout@v4` (in install-smoke.yml)
- `actions/setup-python@v5` (in install-smoke.yml)
- `actions/checkout@v6` (in release.yml)
- `actions/setup-python@v6` (in release.yml)
- `actions/upload-artifact@v7` (in release.yml)

## Docker Base Images

- `python:3.12-slim`

## Limitations

- Lightweight local inventory; not an official SPDX or CycloneDX SBOM.
- Based on declared metadata, not resolved dependency tree.
- Does not include transitive dependencies.
- GitHub Actions versions are as declared in workflow files.
