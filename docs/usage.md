# Usage Guide

## Installation

### From PyPI

```bash
pip install oss-paper-ci  # After PyPI publication
```

### Editable install (development)

```bash
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"
```

### Requirements

- Python 3.10 or later
- PyYAML (installed automatically)

## CLI Commands

### `oss-paper-ci scan`

Scan a repository for reproducibility checks.

```bash
oss-paper-ci scan [PATH] [OPTIONS]
```

**Arguments:**

| Argument/Option   | Default | Description                              |
|-------------------|---------|------------------------------------------|
| `PATH`            | `.`     | Path to the repository root              |
| `--config`        | (auto)  | Path to `oss-paper-ci.yml` config file   |
| `--format`        | `markdown` | Output format: `json` or `markdown`   |
| `--output`, `-o`  | stdout  | Write report to a file instead of stdout |

**Examples:**

```bash
# Scan current directory, markdown to stdout
oss-paper-ci scan

# Scan a specific repo, output JSON
oss-paper-ci scan ~/my-paper --format json

# Write markdown report to file
oss-paper-ci scan -o report.md

# Use a custom config file
oss-paper-ci scan --config custom.yml
```

### `oss-paper-ci init`

Generate a default `oss-paper-ci.yml` configuration file in the current directory.

```bash
oss-paper-ci init
```

Fails with exit code 1 if the file already exists.

### `oss-paper-ci explain`

Print an explanation of a specific check ID.

```bash
oss-paper-ci explain ENV001
```

Output:

```
Check: ENV001
Title: Environment specification file exists
Severity: error
Description: Environment specification file exists
```

### `oss-paper-ci version`

Print the tool version.

```bash
oss-paper-ci version
# oss-paper-ci 0.1.0
```

## Output Formats

### Markdown

The default format. Produces a human-readable report with:

- Repository path and detected languages
- Overall score (0-100) and status
- Table of all check results
- Recommendations for failed/warned checks

### JSON

Structured output suitable for CI parsing and tooling integration.

```bash
oss-paper-ci scan --format json
```

See [report-schema.md](report-schema.md) for the full JSON schema.

## Exit Codes

| Code | Meaning                                         |
|------|-------------------------------------------------|
| 0    | All checks passed (status: `pass`)              |
| 1    | Warnings present, no failures (status: `warn`)  |
| 2    | At least one check failed (status: `fail`)      |

## Using in CI Pipelines

### GitHub Actions

```yaml
- name: Reproducibility check
  run: |
    pip install oss-paper-ci  # After PyPI publication
    oss-paper-ci scan --format json -o report.json
    oss-paper-ci scan --format markdown -o report.md
```

The step will fail if any check produces an error-level failure (exit code 2).

### GitLab CI

```yaml
reproducibility:
  script:
    - pip install oss-paper-ci  # After PyPI publication
    - oss-paper-ci scan --format markdown -o report.md
  artifacts:
    paths:
      - report.md
```

### Interpreting exit codes in CI

```bash
oss-paper-ci scan
exit_code=$?

if [ $exit_code -eq 0 ]; then
  echo "All checks passed"
elif [ $exit_code -eq 1 ]; then
  echo "Warnings found -- review recommended"
elif [ $exit_code -eq 2 ]; then
  echo "Failures found -- must fix before merging"
fi
```

## Python API

You can use oss-paper-ci as a library:

```python
from oss_paper_ci.scanner import scan
from oss_paper_ci.config import load_config
from oss_paper_ci.reporting.json_report import generate_json_report
from oss_paper_ci.reporting.markdown_report import generate_markdown_report

# Load config (uses defaults if no file found)
config = load_config(repo_root="/path/to/repo")

# Run the scan
report = scan("/path/to/repo", config)

# Access results
print(f"Score: {report.summary.score}")
print(f"Status: {report.summary.status}")
print(f"Checks: {len(report.checks)}")

for check in report.checks:
    print(f"  {check.id}: {check.status.value} - {check.message}")

# Generate output
json_text = generate_json_report(report)
md_text = generate_markdown_report(report)
```

### Key classes

- `scan(path, config)` -- runs all checks, returns a `Report`
- `load_config(config_path, repo_root)` -- loads YAML config or returns defaults
- `Report` -- top-level report with `summary`, `checks`, `repository`
- `CheckResult` -- individual check result with `id`, `status`, `severity`, `message`, `evidence`, `recommendation`
