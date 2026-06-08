# Changelog

## 1.2.0rc1 (2026-06-08)

### Added
- Example reports in `examples/reports/` generated from realistic_ml_repo fixture
- Demo GitHub Actions workflow (`demo-report.yml`) with SARIF and PR comments
- `docs/demo.md` with reproduction instructions
- `docs/report-formats.md` explaining all output formats
- `docs/action-usage.md` with three usage paths
- README "Quick demo" section with links to example reports

### Changed
- Version bumped to 1.2.0rc1

## 1.1.0rc1 (2026-06-08)

### Added
- README badges: CI status, License, Python version, Release tag
- GitHub issue templates: bug report, feature request, reproducibility check problem
- Pull request template
- Dependabot configuration for Python dependencies and GitHub Actions
- Release workflow triggered on version tags (`v*`)

### Changed
- Version bumped to 1.1.0rc1

## 1.0.0rc1 (2026-06-07)

### Changed
- README rewritten for first public release with clear GitHub Action usage
- GitHub Actions examples reorganized: use-action, source-checkout, pypi-after-publication
- Pre-commit example updated to use `<tag>` placeholder instead of stale v0.2.0
- Limitations section updated to accurately reflect cross-language support depth
- `full-ci.yml` uses GitHub Action (`uses: <owner>/<repo>@v1`) instead of `pip install .`
- `local-checkout.yml` renamed to `source-checkout.yml` with proper tool repo checkout

### Fixed
- README GitHub Actions example no longer uses misleading `pip install -e .`
- Limitations no longer contradict cross-language documentation

## 0.9.0rc1 (2026-06-07)

### Fixed
- Removed fake GitHub URLs from source code (contract.py, sarif_report.py)
- Fixed README quickstart to use consistent placeholder paths
- Fixed README CLI command: `explain --list` → `list-checks`
- Fixed release package denylist to exclude stage report files
- Fixed clean-room verification to check for stage files and stale content
- SARIF `informationUri` now uses placeholder instead of unconfirmed URL

## 0.8.0rc1 (2026-06-07)

### Added
- Cross-language support: R, Julia, MATLAB, Make, Snakemake detection and basic checks
- Evidence graph (`oss-paper-ci graph`) for dependency and file relationship visualization
- Baseline regression detection (`oss-paper-ci baseline create/compare`)
- Smoke test runner (`oss-paper-ci smoke`) with security policy
- Reproducibility contract support (`reproducibility.yml`)
- `scripts/check_docs_truthfulness.py` for automated documentation auditing
- Test fixtures: r_ready_repo, julia_ready_repo, matlab_minimal_repo, make_snakemake_repo
- Documentation: cross-language.md, evidence-graph.md, baselines.md, smoke-runs.md, troubleshooting.md, clean-room-verification.md
- Clean-room verification pipeline with `scripts/verify_clean_package.py`
- Release package builder with `scripts/make_release_package.py`

### Changed
- Documentation uses `<owner>/<repo>` placeholders instead of unconfirmed URLs
- Example workflows clearly distinguish local checkout vs PyPI install (after publication)
- `action.yml` uses `${{ github.action_path }}` for composite action installation
- Version bumped to 0.8.0rc1

### Fixed
- Removed fake GitHub repository URLs from documentation and examples
- Clarified `pip install .` as local-only in all documentation
- Fixed stale dogfooding summary content

## 0.2.0 (2026-06-07)

### Added
- SARIF output format (`--format sarif`) for GitHub Code Scanning integration
- Pre-commit hook support (`.pre-commit-hooks.yaml`)
- `checks.enabled`, `checks.disabled`, and `checks.severity_overrides` config options
- `category` field on all check results
- `score_breakdown` in summary showing per-check deductions
- `metadata` object in JSON reports (generated_at, scanned_files, ignored_paths)
- `recommendations` and `blocking_issues` top-level fields in JSON reports
- `list-checks` subcommand via `explain --list`
- Test fixtures: broken_paper_repo, realistic_ml_repo, minimal_bad_repo
- Documentation: check-authoring.md, sarif.md, pre-commit.md, dogfooding.md, release-checklist.md

### Changed
- Scoring system redesigned with deduction model and per-category caps
- Score and status are now consistent (score < 50 = fail, error-level fail = fail)
- Enhanced checker depth for path validation (PAP002, PAP003, RES002)
- README restructured to engineering style
- All check documentation updated with category field
- Report schema updated to version 0.2
- Configuration documentation expanded with new fields

### Removed
- Codex application document (replaced with neutral positioning)
- Roadmap section from README (features now tracked in issues)

## 0.1.0 (2026-06-07)

### Added
- CLI with scan, init, explain, version commands
- 41 reproducibility checks across 8 categories
- JSON and Markdown report formats
- Configuration via oss-paper-ci.yml
- GitHub Actions workflow examples
- Scoring system (0-100 reproducibility readiness)
