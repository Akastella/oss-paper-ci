# First Run

This guide helps you get started with oss-paper-ci in under 60 seconds.

## Quick Start

After installing oss-paper-ci, run:

```bash
oss-paper-ci quickstart
```

This detects your current directory and recommends next steps.

## Try the Built-in Demo

oss-paper-ci includes a self-contained demo that requires no external dependencies:

```bash
oss-paper-ci try-demo
```

This runs:
1. Scan of the built-in demo-paper-repo
2. Dry-run reproduction of demo-reproduce-repo
3. Evaluation of the synthetic corpus

## What to Try Next

### For a new project

```bash
# Scan your repository
oss-paper-ci scan .

# Get a full pipeline with progress
oss-paper-ci workbench .

# Generate an adoption plan
oss-paper-ci adopt .
```

### For existing projects

```bash
# Guided recommendations
oss-paper-ci wizard

# Safe reproduction attempt
oss-paper-ci reproduce . --dry-run

# Generate a reproducibility dossier
oss-paper-ci dossier .
```

### For CI/CD integration

```bash
# Add to GitHub Actions
# See docs/github-actions.md for workflow templates
```

## Command Reference

| Command | Purpose |
|---------|---------|
| `quickstart` | Show recommended first steps |
| `try-demo` | Run built-in demo |
| `scan .` | Scan current directory |
| `wizard` | Guided setup |
| `workbench .` | Full pipeline |
| `adopt .` | Adoption plan |
| `reproduce . --dry-run` | Safe reproduction |
| `dossier .` | Reproducibility summary |

## Getting Help

```bash
# General help
oss-paper-ci --help

# Topic-specific help
oss-paper-ci quickstart --topic install
oss-paper-ci quickstart --topic github-action
oss-paper-ci quickstart --topic reproduce
oss-paper-ci quickstart --topic eval

# Role-based guidance
oss-paper-ci guide --role author
oss-paper-ci guide --role reviewer
oss-paper-ci guide --role maintainer
```

## Troubleshooting

If you encounter issues:

```bash
# Diagnose environment
oss-paper-ci doctor

# Check Python version
python --version  # Requires 3.10+

# Verify installation
oss-paper-ci version
```

See [Troubleshooting](troubleshooting.md) for common issues.
