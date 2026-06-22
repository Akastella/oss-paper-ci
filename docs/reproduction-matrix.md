# Reproduction Matrix

Matrix execution runs reproduction across multiple configurations: Python versions, profiles, or config files. Each variant creates an independent session.

## Usage

```bash
# Plan a matrix with Python versions
oss-paper-ci matrix plan . --python 3.10,3.11,3.12

# Plan a matrix with profiles
oss-paper-ci matrix plan . --profile lenient,strict

# Run a matrix (dry-run by default)
oss-paper-ci matrix run . --python 3.10,3.11,3.12

# Run with execution
oss-paper-ci matrix run . --python 3.10,3.11,3.12 --execute

# Generate matrix report
oss-paper-ci matrix report .oss-paper-ci-matrix --format markdown

# Compare variants
oss-paper-ci matrix compare .oss-paper-ci-matrix --format markdown
```

## Matrix Plan

The plan shows which variants will be run and which are available:

```
| Variant | Python | Profile | Available |
|---------|--------|---------|-----------|
| python-3.10 | 3.10 | - | ❌ |
| python-3.11 | 3.11 | - | ❌ |
| python-3.12 | 3.12 | - | ✅ |
```

## Matrix Run

Each variant creates an independent session:

```
.oss-paper-ci-matrix/
  python-3.10/
    session.json
    runs/...
  python-3.11/
    session.json
    runs/...
  python-3.12/
    session.json
    runs/...
```

## Matrix Report

The matrix report compares results across variants:

```
| Variant | Total | Passed | Failed |
|---------|-------|--------|--------|
| python-3.10 | 3 | 3 | 0 |
| python-3.11 | 3 | 3 | 0 |
| python-3.12 | 3 | 3 | 0 |
```

## Missing Runtimes

When a Python version is not available on the system:
- The variant is marked as `unavailable`
- A warning is generated
- The tool does **not** crash
- The tool does **not** auto-install the runtime

## Safety

- Matrix run is **dry-run by default**; `--execute` is required
- Each variant inherits the same safety rules as sessions
- Dangerous commands are blocked in all variants
- No auto-installation of runtimes
- No network access

## See Also

- [Reproduction Sessions](reproduction-sessions.md) — Session management
- [Session Safety](session-safety.md) — Detailed safety model
