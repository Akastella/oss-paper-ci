# Changelog

## 2.6.0rc1 (2026-06-15)

### Added
- `oss-paper-ci adopt PATH` — generate adoption plan with missing files and recommended scaffolds
- `oss-paper-ci scaffold PATH` — scaffold missing reproducibility files (dry-run by default)
- `oss-paper-ci scaffold PATH --apply` — apply scaffold and create files
- `oss-paper-ci fix preview PATH` — preview recommended fixes
- `oss-paper-ci fix apply PATH --yes` — apply safe fixes with explicit confirmation
- Safe write utilities: path validation, force guards, forbidden path protection
- Ecosystem-aware templates: reproducibility.yml, data/README.md, results/README.md, GitHub Actions workflow
- Adoption plan integration with workbench and dossier
- `safe_write.py` — atomic write with path traversal protection
- `templates.py` — ecosystem-aware file templates
- `adoption.py` — adoption plan generation from repo analysis
- `scaffold.py` — scaffold engine with dry-run and apply modes
- Tests for safe write, adoption plan, scaffold CLI, fix CLI

### Changed
- Version bumped to 2.6.0rc1

## 2.5.0rc1 (2026-06-11)

### Added
- `oss-paper-ci wizard` — guided setup for new users with safe next-step recommendations
- `oss-paper-ci workbench PATH` — multi-step pipeline: detect ecosystems → scan → data diagnose → results validate → dossier
- `oss-paper-ci theme list` — list available terminal themes
- `oss-paper-ci theme preview` — preview a theme with sample output
- TTY-aware terminal rendering with automatic CI/non-TTY fallback
- Spinner and progress indicators (animated in TTY, static in non-TTY)
- Theme system: classic, minimal, contrast
- `--plain` global flag — force plain text output (no color, no animation)
- `--no-color` global flag — disable color output
- `--no-animate` global flag — disable animation
- `--theme {classic|minimal|contrast}` global flag — select terminal theme
- `--debug` global flag — show tracebacks on error
- `NO_COLOR` environment variable support
- `OSS_PAPER_CI_NO_ANIMATE` environment variable support
- `OSS_PAPER_CI_PLAIN` environment variable support
- Terminal UI components: panels, tables, status indicators, score display, next actions
- Structured error experience with error codes, explanations, and suggested fixes
- Workbench output directory with scan.json, data-diagnostics.json, result-validation.json, dossier.md, summary.md, workbench.json
- `examples/terminal/` with workbench, wizard, and theme previews
- `docs/terminal-workbench.md`, `docs/wizard.md`, `docs/themes.md`, `docs/cli-ux.md`, `docs/no-color-and-ci.md`
- `rich>=13.0` added as runtime dependency (graceful fallback if unavailable)
- Terminal UI tests: wizard, workbench, themes, plain mode, no-color, error messages

### Changed
- Version bumped to 2.5.0rc1
- All terminal output now TTY-aware with automatic degradation

## 2.4.0rc1 (2026-06-11)

### Added
- `oss-paper-ci data diagnose PATH` — data availability and documentation diagnostics
- `oss-paper-ci results validate PATH` — result and artifact existence/format validation
- Evidence score components: readiness_score, data_evidence_score, execution_evidence_score, artifact_evidence_score, provenance_score
- `score_components` field in scan JSON report (backward compatible with `score`)
- Deeper runtime adapters for R, Julia, Node, Make, Snakemake, Nextflow, C++, Rust, Java
- Data diagnostics: checks data/README, availability statements, external data declarations, sample data, large files, checksums
- Result validation: checks metrics.json existence/format, figures/, tables/, expected artifacts, artifact size
- `docs/data-diagnostics.md`, `docs/result-validation.md`, `docs/evidence-scores.md`
- Limitations docs rewritten: "what can be reduced vs what must be retained"
- Example reports in examples/reports/ for diagnostics and validation
- Tests for data diagnostics, result validation, score components, runtime adapters

### Changed
- Version bumped to 2.4.0rc1
- Limitations section updated to reflect new capabilities while retaining honest boundaries

## 2.3.0rc1 (2026-06-11)

### Added
- `oss-paper-ci ecosystems detect PATH` — detect language ecosystems in a repository
- `oss-paper-ci ecosystems explain LANG` — explain a language ecosystem's support level
- Multi-language ecosystem detection: Python, R, Julia, MATLAB/Octave, Node, Rust, Java, C/C++, Snakemake, Nextflow, Make, shell
- `--ecosystem LANG` flag for reproduce command to select target ecosystem
- Runtime availability detection (checks if R, Julia, etc. are installed)
- Support levels: native, execute-if-runtime-present, dry-run, detect-only
- Scan report includes ecosystem detection results
- Dossier evidence map includes language_ecosystem category
- Multi-language fixtures for testing (R, Julia, MATLAB, Node, Rust, Java, C++, workflow repos)
- `docs/language-ecosystems.md` — language ecosystem documentation
- `examples/ecosystems/` — per-language ecosystem guides
- GitHub Action examples for ecosystem detection
- Tests for ecosystem detection, reproduce integration, scan integration

### Changed
- Version bumped to 2.3.0rc1

## 2.2.0rc1 (2026-06-10)

### Added
- `oss-paper-ci dossier` — generate reproducibility dossier from scan/reproduce/capsule reports
- `--audience author|reviewer|maintainer` — role-specific dossier output
- `--language en|zh-CN|ja` — multilingual dossier generation
- `--format markdown|json|html|issue|pr-comment` — multiple output formats
- Evidence map: structured inventory of reproducibility evidence by category
- Risk register: prioritized list of reproducibility risks
- Remediation plan: actionable steps to improve reproducibility
- Author checklist: what to fix in the repository
- Reviewer summary: how to interpret the evidence
- Maintainer roadmap: batch governance recommendations
- Issue and PR comment text generation (text only, no auto-posting)
- `docs/dossier.md`, `docs/evidence-map.md`, `docs/remediation-plan.md`
- Examples in `examples/dossiers/` (author, reviewer, maintainer, i18n, issue, pr-comment)
- Tests for dossier CLI, model, evidence map, risk register, remediation, i18n, reports

### Changed
- Version bumped to 2.2.0rc1

## 2.1.0rc1 (2026-06-10)

### Added
- `oss-paper-ci guide` — guided entry point with role-based and topic-based guidance
- `guide --role author|reviewer|maintainer` — role-specific recommendations
- `guide --topic scan|reproduce|capsule` — topic-specific walkthrough
- Failure taxonomy: 10 structured failure types with causes, next steps, and role guidance
- Plain-language summary in reproduction reports
- `docs/failure-taxonomy.md` — structured failure reference
- `docs/glossary.md` — terminology glossary
- `docs/human-centered-reproducibility.md` — human-centered design principles
- `docs/roles.md` — role-based guidance for authors, reviewers, maintainers
- `docs/i18n.md` — internationalization guide
- `README.zh-CN.md` — Simplified Chinese README
- `README.ja.md` — Japanese README
- `scripts/check_i18n_readmes.py` — i18n consistency checker
- Language links in README (English | 简体中文 | 日本語)
- HTML reports include `lang` attribute for accessibility
- Tests for guide CLI, failure taxonomy, i18n, plain-language summary

### Changed
- Version bumped to 2.1.0rc1

## 2.0.0rc1 (2026-06-10)

### Added
- README restructured for quick onboarding (one-liner, what-it-does, quickstart, 3 commands)
- `docs/index.md` — documentation site index
- `docs/getting-started.md` — new user guide
- `docs/installation.md` — pip/pipx/source install paths with troubleshooting
- `docs/cli-reference.md` — auto-generated CLI reference
- `docs/demo-gallery.md` — gallery of example reports and outputs
- `docs/security-model.md` — consolidated security documentation
- `docs/release-process.md` — release process and checklist
- `scripts/build_docs_site.py` — static HTML docs site generator
- `scripts/generate_cli_reference.py` — CLI reference auto-generation
- `scripts/release_gate.py` — release validation checks
- `.github/workflows/docs.yml` — GitHub Pages deployment workflow
- `RELEASE_CHECKLIST.md` — pre-release checklist
- `CODE_OF_CONDUCT.md` — contributor code of conduct
- `SUPPORT.md` — support and issue guidelines
- `CONTRIBUTING.md` — contribution guidelines
- `SECURITY.md` — security policy
- Tests for docs site, CLI reference, release gate, README, PyPI metadata

### Changed
- Version bumped to 2.0.0rc1
- pyproject.toml description updated, added Documentation/Changelog URLs

## 1.9.0rc1 (2026-06-10)

### Added
- `oss-paper-ci reproduce ... --capsule repro.zip` — generate a verifiable reproduction capsule
- `oss-paper-ci capsule verify CAPSULE.zip` — verify capsule integrity (SHA256 hashes, structure, required files)
- `oss-paper-ci capsule inspect CAPSULE.zip` — display capsule metadata and execution summary
- `oss-paper-ci capsule diff OLD.zip NEW.zip` — compare two capsules (score delta, command status, artifacts)
- Capsule format: `oss-paper-ci-capsule/` root with `capsule.json` manifest, `SHA256SUMS`, reports, logs, artifacts, metadata
- Capsule manifest schema v0.1 with source, execution, reports, integrity sections
- SHA256 integrity verification for all capsule files
- Path traversal and zip slip detection in capsule verification
- Capsule artifact size limits and exclusion of venv/.git/cache
- GitHub Action example: `reproduce-capsule.yml` with verify and artifact upload
- Documentation: reproduction-capsules.md, capsule-format.md, capsule-verify.md, capsule-security.md
- Tests: capsule format, builder, verify, inspect, diff, security, CLI, docs truthfulness

### Changed
- Version bumped to 1.9.0rc1

## 1.8.0rc1 (2026-06-10)

### Added
- `oss-paper-ci reproduce` — one-command reproduction runner for scientific paper repositories
- `reproduce URL --dry-run` — show what would happen without executing (default behavior)
- `reproduce URL --execute` — clone, install, run, and scan a paper repository
- `reproduce URL --install` — install dependencies into isolated venv
- `reproduce URL --command "..."` — override the reproduction command
- `reproduce URL --workdir PATH` — use a specific working directory
- `reproduce URL --output FILE --format markdown|json|html` — generate reproduction report
- `reproduce URL --timeout N` — per-command timeout in seconds
- `reproduce URL --keep-workdir` — preserve working directory after run
- URL resolver: GitHub repo URLs, local paths, paper URLs with --repo fallback
- Environment detection: requirements.txt, pyproject.toml, setup.py, environment.yml, conda.yml, Pipfile, poetry.lock
- Reproduction entry detection from reproducibility.yml, .oss-paper-ci.yml, and common script paths
- Reproduction report: Markdown, JSON, HTML formats with full audit trail
- Demo reproduce repository (`examples/demo-reproduce-repo/`) with runnable scripts
- GitHub Action examples: `reproduce-repo.yml`, `reproduce-dry-run.yml`
- Documentation: reproduce.md, reproduce-security.md, environment-detection.md, reproduction-report.md
- Tests: reproduce CLI, resolver, environment detection, runner, reports, security, docs truthfulness

### Changed
- Version bumped to 1.8.0rc1

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
