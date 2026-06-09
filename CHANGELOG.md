# Changelog

## 1.7.0rc1 (2026-06-09)

### Added
- Workspace configuration (`oss-paper-ci-workspace.yml`) for multi-project batch scanning
- `oss-paper-ci workspace validate` — validate workspace file
- `oss-paper-ci workspace list` — list projects in workspace
- `oss-paper-ci batch scan` — scan all projects in a workspace
- `oss-paper-ci batch diff` — compare two batch scan reports
- `oss-paper-ci cache clean` — remove all cached results
- `oss-paper-ci cache info` — show cache statistics
- `--jobs N` flag for parallel batch scanning (default: 1)
- `--cache` flag for incremental scanning with file/config/rules hashing
- Batch report JSON schema v0.5 with workspace summary, per-project results, and cache stats
- Aggregate Markdown report with project table, status counts, and cache summary
- Aggregate HTML report (single file, no external CDN)
- Batch diff with project_added, project_removed, score_delta, status_delta, new_failures, resolved_failures
- Error isolation: single project failure does not crash batch
- Deterministic output order matching workspace project order
- `.oss-paper-ci-cache/` directory with JSON cache files
- Cache invalidation on file/config/rules/profile/version changes
- Corrupt cache auto-recovery (treats as miss)
- Workspace examples: demo, strict-publication, mixed-fixtures
- GitHub Action `workspace`, `jobs`, `cache` inputs
- GitHub Action batch scan step (conditional on workspace input)
- GitHub Actions examples: workspace-batch, workspace-cache, workspace-publication-gate
- Synthetic corpus generator (`scripts/generate_synthetic_corpus.py`)
- Scale gate benchmark (`scripts/scale_gate.py`)
- Documentation: workspace.md, batch-scan.md, cache.md, parallelism.md, batch-diff.md, scale-gate.md
- Tests: workspace config, batch scan, batch reports, batch diff, cache, parallel batch, scale gate, action inputs, docs truthfulness

### Changed
- Version bumped to 1.7.0rc1
- Report schema updated to version 0.5 (batch reports)
- `.gitignore` updated to exclude `.oss-paper-ci-cache/`

## 1.6.0rc1 (2026-06-09)

### Added
- Manifest-based rule packs: define custom checks in YAML without Python code
- `oss-paper-ci rules validate` and `rules list` commands
- `--rules` flag for scan command to load rule packs
- Config `rule_packs` field for persistent rule pack loading
- Config `suppressions` field for finding-level suppression with reason
- Suppressed findings tracked in report JSON (`suppressed_findings` field)
- Report JSON schema v0.4 with `suppressed_findings` and `rule_packs` fields
- Rule types: file_exists, any_file_exists, forbidden_path, forbidden_glob, text_contains, regex_contains, yaml_key_exists
- Performance gate script (`scripts/performance_gate.py`) for runtime benchmarking
- Golden report compatibility tests (`scripts/update_golden_reports.py`)
- Example rule packs: lab-reproducibility, citation-required, no-large-data
- GitHub Action `rules` and `performance-gate` inputs
- Documentation: rule-sdk.md, rule-pack-manifest.md, suppressions.md, performance-gate.md, golden-reports.md, compatibility-policy.md

### Changed
- Version bumped to 1.6.0rc1
- Report schema updated to version 0.4

## 1.5.0rc1 (2026-06-09)

### Added
- Policy profiles: `lenient`, `default`, `strict`, `publication` with per-profile thresholds and severity overrides
- `.oss-paper-ci.yml` config schema v1 with `profile`, `thresholds`, `severity`, `paths`, `reports`, `ci` sections
- `--profile` CLI flag for `scan` command to override config file profile
- `oss-paper-ci config validate` — validate config file with schema checking
- `oss-paper-ci config init` — generate config with `--profile`, `--force`, `--dry-run`
- `oss-paper-ci config explain` — show resolved configuration
- `oss-paper-ci explain policy <name>` — explain a policy profile's parameters
- `oss-paper-ci diff` — compare two scan report JSON files without live scan
- Report JSON includes `policy` field with active profile and thresholds
- Markdown and HTML reports show active profile
- GitHub Action `profile`, `github-annotations`, `step-summary` inputs
- Example config files in `examples/configs/` (lenient, strict, publication)
- Example GitHub Actions workflows for policy profiles and diff regression
- Benchmark fixture matrix generation
- Schema validation module with clear error messages

### Changed
- Version bumped to 1.5.0rc1
- Report schema updated to version 0.3 (adds `policy` field)
- Scoring engine accepts optional `PolicyProfile` for threshold overrides
- Config system supports both v0.1 (legacy) and v1 format
- `init` command defaults to `.oss-paper-ci.yml` with `--force` support

## 1.4.0rc1 (2026-06-09)

### Added
- `--format github` for GitHub Actions annotation output
- `--github-step-summary` to write Markdown summary to `$GITHUB_STEP_SUMMARY`
- `--max-annotations` to limit annotation count
- SARIF 2.1.0 export with rules, results, and physical locations
- HTML report improvements: section anchors, metadata, no external CDN
- PR comment improvements: collapsible details, markdown table, score badge
- Demo paper repo GitHub Actions workflow example
- GitHub Actions workflow template in docs and examples
- CI dogfooding tests

### Changed
- Version bumped to 1.4.0rc1

## 1.3.0rc1 (2026-06-08)

### Added
- `oss-paper-ci doctor` command to diagnose repository and environment
- `oss-paper-ci comment` command to generate PR comments from scan results
- `--format html` for scan command to generate static HTML reports
- `examples/demo-paper-repo/` as a toy-but-realistic example paper repository
- `docs/doctor.md`, `docs/init.md`, `docs/html-report.md`, `docs/pr-comment.md`, `docs/demo-paper-repo.md`

### Changed
- Version bumped to 1.3.0rc1

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
