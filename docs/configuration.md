# Configuration

oss-paper-ci is configured via a YAML file.  The tool searches for the
config file in this order:

1. Explicit `--config` path passed to `oss-paper-ci scan`
2. `oss-paper-ci.yml` in the repository root
3. `oss-paper-ci.yaml` in the repository root
4. `.oss-paper-ci.yml` in the repository root
5. Built-in defaults (no config file needed)

## Generating a config file

```bash
# Default config
oss-paper-ci config init

# Config for a specific profile
oss-paper-ci config init --profile strict

# Print to stdout without writing
oss-paper-ci config init --profile publication --dry-run

# Overwrite existing file
oss-paper-ci config init --force
```

## Validating a config file

```bash
oss-paper-ci config validate
oss-paper-ci config validate --config .oss-paper-ci.yml
```

Returns exit code 0 if valid, 1 if there are errors.

## Showing resolved config

```bash
oss-paper-ci config explain
oss-paper-ci config explain --config .oss-paper-ci.yml
```

## Config file versions

### v1 (current)

```yaml
version: 1
profile: default

paths:
  include:
    - "."
  exclude:
    - ".git/"
    - "dist/"
    - "build/"

thresholds:
  pass_score: 85
  warn_score: 60
  fail_under: 50

severity:
  fail_on:
    - blocking
  treat_as_blocking: []

checks:
  disabled: []
  severity_overrides: {}

reports:
  default_format: markdown
  include_recommendations: true
  max_findings: 50

ci:
  github_annotations: true
  step_summary: true

project:
  name: ""
  paper_dir: "paper"
  code_dirs:
    - "src"
    - "scripts"
  data_dirs:
    - "data"
  results_dirs:
    - "results"
    - "figures"

ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
```

### v0.1 (legacy, still supported)

```yaml
version: "0.1"
project:
  name: ""
  paper_dir: "paper"
  code_dirs:
    - "src"
    - "scripts"
  data_dirs:
    - "data"
  results_dirs:
    - "results"
    - "figures"
checks:
  min_score: 70
  require_license: true
  require_citation: true
  require_environment: true
  require_quickstart: true
ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
output:
  default_format: "markdown"
```

## Sections

### `profile`

Selects a [policy profile](policy-profiles.md) that sets default
thresholds and severity rules.  Valid values: `lenient`, `default`,
`strict`, `publication`.

| Field    | Type   | Default     | Description           |
|----------|--------|-------------|-----------------------|
| `profile`| string | `"default"` | Policy profile name   |

### `project`

Project metadata used for context in reports.

| Field         | Type     | Default                    | Description                        |
|---------------|----------|----------------------------|------------------------------------|
| `name`        | string   | `""`                       | Project name                       |
| `paper_dir`   | string   | `"paper"`                  | Paper/LaTeX source directory       |
| `code_dirs`   | list     | `["src", "scripts"]`       | Source code directories            |
| `data_dirs`   | list     | `["data"]`                 | Data directories                   |
| `results_dirs`| list     | `["results", "figures"]`   | Results/figures directories        |

### `thresholds`

Scoring thresholds.  These are set by the profile but can be overridden.

| Field         | Type | Default | Description                           |
|---------------|------|---------|---------------------------------------|
| `pass_score`  | int  | `85`    | Minimum score for pass status (0-100) |
| `warn_score`  | int  | `60`    | Score below which status is warn      |
| `fail_under`  | int  | `50`    | Score below which status is fail      |

### `checks`

Controls which checks are enforced and scoring thresholds.

| Field               | Type   | Default | Description                                |
|---------------------|--------|---------|--------------------------------------------|
| `min_score`          | int    | `70`    | Minimum score for pass status (0-100)      |
| `require_license`    | bool   | `true`  | Treat missing license as failure           |
| `require_citation`   | bool   | `true`  | Treat missing citation as warning          |
| `require_environment`| bool   | `true`  | Treat missing env spec as failure          |
| `require_quickstart` | bool   | `true`  | Treat missing reproduction guide as warning|
| `enabled`            | list   | `[]`    | Only run these checks (empty = all)        |
| `disabled`           | list   | `[]`    | Skip these checks                          |
| `severity_overrides` | dict   | `{}`    | Override severity per check ID             |

### `ignore`

| Field   | Type | Default                                      | Description              |
|---------|------|----------------------------------------------|--------------------------|
| `paths` | list | `[".git", ".venv", "node_modules", "__pycache__"]` | Paths to skip during scan |

### `paths`

Path include/exclude patterns (v1 format).

| Field     | Type | Default | Description              |
|-----------|------|---------|--------------------------|
| `include` | list | `["."]` | Paths to include         |
| `exclude` | list | (see above) | Paths to exclude    |

### `reports`

Report output configuration.

| Field                   | Type   | Default      | Description             |
|-------------------------|--------|--------------|-------------------------|
| `default_format`        | string | `"markdown"` | Default output format   |
| `include_recommendations`| bool  | `true`       | Include recommendations |
| `max_findings`          | int    | `50`         | Max findings to show    |

### `ci`

CI integration settings.

| Field               | Type | Default | Description                    |
|---------------------|------|---------|--------------------------------|
| `github_annotations`| bool | `true`  | Emit GitHub workflow annotations|
| `step_summary`      | bool | `true`  | Write GitHub step summary      |

## Minimal config

A config file only needs the fields you want to override.  Everything
else uses defaults:

```yaml
version: 1
profile: strict
```

## Disabling specific checks

Use `checks.disabled` to skip specific checks by ID:

```yaml
checks:
  disabled:
    - "META005"  # skip contributing guidelines check
    - "CI005"    # skip security policy check
```

## Overriding severity

Use `checks.severity_overrides` to change the severity level of
individual checks:

```yaml
checks:
  severity_overrides:
    "CI001": "warning"   # elevate GitHub Actions check to warning
    "META005": "info"    # demote contributing check to info
```

## `.oss-paper-ci.yml` vs `reproducibility.yml`

These are two different files with different purposes:

| File | Purpose |
|------|---------|
| `.oss-paper-ci.yml` | Tool configuration: profile, thresholds, ignore paths, output format |
| `reproducibility.yml` | Reproduction contract: data, scripts, environment, seeds, expected outputs |

The tool config controls *how* the tool runs.  The reproduction contract
describes *what* the repository contains for reproducibility.
