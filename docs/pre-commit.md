# Pre-commit Integration

oss-paper-ci can run as a [pre-commit](https://pre-commit.com/) hook so that
reproducibility checks run automatically before each commit.

## Quick setup

Add this to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
```

Then install the hook:

```bash
pip install pre-commit
pre-commit install
```

Now `oss-paper-ci scan .` runs on every commit. If any error-level check fails,
the commit is blocked.

## Configuration options

The hook accepts arguments to customize behavior:

```yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
        args: ["--config", "my-config.yml"]
```

### Available arguments

| Argument                  | Description                              | Default     |
|---------------------------|------------------------------------------|-------------|
| `--config <path>`         | Path to config file                      | Auto-detect |
| `--format <format>`       | Output format (`markdown`, `json`, `sarif`)| `markdown`|

Arguments are passed after the hook's default entry point, which is
`oss-paper-ci scan . --format markdown`.

## Example: block on failures only

By default, the hook uses exit code semantics:

- Exit 0: All checks pass. Commit proceeds.
- Exit 1: Warnings only. Commit proceeds (pre-commit treats 0 and 1 as success
  by default).
- Exit 2: Error-level failures. Commit is blocked.

To make the hook non-blocking (report only):

```yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
        entry: oss-paper-ci scan . --format markdown || true
```

## Example: write report to file

```yaml
repos:
  - repo: https://github.com/Akastella/oss-paper-ci
    rev: v1.0.0rc1
    hooks:
      - id: oss-paper-ci
        entry: bash -c 'oss-paper-ci scan . --format markdown -o report.md; exit 0'
```

## How it works

The hook definition in `.pre-commit-hooks.yaml`:

```yaml
- id: oss-paper-ci
  name: oss-paper-ci reproducibility check
  description: Check reproducibility readiness of scientific paper repositories
  entry: oss-paper-ci scan . --format markdown
  language: python
  pass_filenames: false
  always_run: true
```

- `pass_filenames: false` -- the tool scans the entire repo, not individual files.
- `always_run: true` -- runs on every commit, not just when specific files change.

## Troubleshooting

### Hook not found

Ensure the repo URL and `rev` match an actual release tag. For local
development, use a local path:

```yaml
repos:
  - repo: local
    hooks:
      - id: oss-paper-ci
        name: oss-paper-ci
        entry: oss-paper-ci scan . --format markdown
        language: system
        pass_filenames: false
        always_run: true
```

### Slow on large repos

The tool scans all files on every commit. For large repositories, use the
`ignore.paths` config option to exclude directories:

```yaml
# oss-paper-ci.yml
ignore:
  paths:
    - ".git"
    - ".venv"
    - "node_modules"
    - "__pycache__"
    - "data"
    - "large_output_dir"
```
