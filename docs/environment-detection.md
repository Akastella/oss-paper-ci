# Environment Detection

The reproduce command detects environment files in a repository and
generates an installation plan.

## Detection Priority

Files are detected in this order:

| Priority | File | Install Command |
|----------|------|-----------------|
| 1 | `requirements.txt` | `python -m pip install -r requirements.txt` |
| 2 | `pyproject.toml` | `python -m pip install -e .` |
| 3 | `setup.py` | `python -m pip install -e .` |
| 4 | `setup.cfg` | `python -m pip install -e .` |
| 5 | `environment.yml` | Detected, not auto-installed |
| 6 | `conda.yml` | Detected, not auto-installed |
| 7 | `Pipfile` | `pip install pipenv && pipenv install --system` |
| 8 | `poetry.lock` | Falls back to pyproject.toml if present |

## Conda Support

Conda environments (`environment.yml`, `conda.yml`) are detected but
**not automatically installed**. The tool will:

1. Report the file as detected
2. Check if `requirements.txt` also exists as a fallback
3. If no fallback exists, report as "unsupported" and suggest manual
   conda installation

## Python Version

The Python version is extracted from `environment.yml` if present
(looking for `python=X.Y` in dependencies).

## Installation Isolation

When `--install` is used:

- A virtual environment is created at `.oss-paper-ci-repro/venv/`
- Dependencies are installed into this venv
- The venv is created inside the working directory (temp or `--workdir`)
- The venv is cleaned up unless `--keep-workdir` is used

## Limitations

- Only Python environments are supported
- Conda must be installed manually
- Poetry/Pipenv support is best-effort
- Complex multi-package setups may not be detected correctly
- System-level dependencies (C libraries, etc.) are not installed
