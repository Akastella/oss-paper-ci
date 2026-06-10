# Installation

## From source (recommended)

```bash
git clone https://github.com/Akastella/oss-paper-ci.git
cd oss-paper-ci
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies.

## pip install (after PyPI publication)

```bash
pip install oss-paper-ci  # after PyPI publication
```

## pipx install (after PyPI publication)

```bash
pipx install oss-paper-ci
```

## Verify installation

```bash
oss-paper-ci version
oss-paper-ci --help
```

## Requirements

- Python 3.10 or later
- pip (or pipx)
- git (for clone-based reproduction)

## Platform notes

### Windows

Works with standard Python installation. Use PowerShell or Git Bash.

### Linux / macOS

Standard pip install works. No system dependencies required beyond Python and git.

## Troubleshooting

### "No module named oss_paper_ci"

The package is not installed. Run:

```bash
pip install -e ".[dev]"
```

### "command not found: oss-paper-ci"

The pip scripts directory may not be in your PATH. Try:

```bash
python -m oss_paper_ci --help
```

### Encoding errors on Windows

The CLI handles UTF-8 automatically. If you see encoding errors, ensure
your terminal supports UTF-8.
