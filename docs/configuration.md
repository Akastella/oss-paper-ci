# Configuration

oss-paper-ci is configured via a YAML file. The tool searches for the config file
in this order:

1. Explicit `--config` path passed to `oss-paper-ci scan`
2. `oss-paper-ci.yml` in the repository root
3. `oss-paper-ci.yaml` in the repository root
4. `.oss-paper-ci.yml` in the repository root
5. Built-in defaults (no config file needed)

## Generating a config file

```bash
oss-paper-ci init
```

This creates `oss-paper-ci.yml` with all default values.

## Full reference

```yaml
# Config schema version (currently "0.1")
version: "0.1"

# Project-specific settings
project:
  # Project name (informational)
  name: ""

  # Directory containing the paper/LaTeX source
  paper_dir: "paper"

  # Directories containing source code
  code_dirs:
    - "src"
    - "scripts"

  # Directories containing data
  data_dirs:
    - "data"

  # Directories containing results/outputs
  results_dirs:
    - "results"
    - "figures"

# Check configuration
checks:
  # Minimum acceptable score (0-100). Used for status determination.
  min_score: 70

  # Whether a LICENSE file is required (META002)
  require_license: true

  # Whether citation info is required (META003)
  require_citation: true

  # Whether environment spec is required (ENV001)
  require_environment: true

  # Whether reproduction instructions are required (META004)
  require_quickstart: true

# Paths to ignore during scanning
ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"

# Output settings
output:
  # Default output format: "markdown" or "json"
  default_format: "markdown"
```

## Sections

### `project`

Project metadata used for context in reports.

| Field         | Type     | Default                    | Description                        |
|---------------|----------|----------------------------|------------------------------------|
| `name`        | string   | `""`                       | Project name                       |
| `paper_dir`   | string   | `"paper"`                  | Paper/LaTeX source directory       |
| `code_dirs`   | list     | `["src", "scripts"]`       | Source code directories            |
| `data_dirs`   | list     | `["data"]`                 | Data directories                   |
| `results_dirs`| list     | `["results", "figures"]`   | Results/figures directories        |

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

### `output`

| Field            | Type   | Default      | Description             |
|------------------|--------|--------------|-------------------------|
| `default_format` | string | `"markdown"` | Default output format   |

## Minimal config

A config file only needs the fields you want to override. Everything else uses defaults:

```yaml
version: "0.1"
checks:
  min_score: 80
```

## Disabling specific checks

Use `checks.disabled` to skip specific checks by ID:

```yaml
checks:
  disabled:
    - "META005"  # skip contributing guidelines check
    - "CI005"    # skip security policy check
```

Use `checks.enabled` to run only a specific set of checks (all others are
skipped):

```yaml
checks:
  enabled:
    - "META001"
    - "META002"
    - "ENV001"
```

If `enabled` is empty (the default), all registered checks run.

## Overriding severity

Use `checks.severity_overrides` to change the severity level of individual
checks. Valid values are `info`, `warning`, and `error`.

```yaml
checks:
  severity_overrides:
    "CI001": "warning"   # elevate GitHub Actions check to warning
    "META005": "info"    # demote contributing check to info
```

Severity overrides affect scoring: higher-severity failures cause larger
score deductions.
