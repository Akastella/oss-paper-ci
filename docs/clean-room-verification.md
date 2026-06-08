# Clean Room Verification

Clean room verification ensures the release package works in a fresh environment.

## What It Does

The `scripts/verify_clean_package.py` script:

1. Extracts the clean ZIP to a temporary directory
2. Checks for forbidden files (`.git/`, `__pycache__/`, `*.egg-info/`, etc.)
3. Checks for required files (`README.md`, `LICENSE`, `pyproject.toml`, etc.)
4. Runs in the extracted directory:
   - `pip install -e ".[dev]"`
   - `oss-paper-ci version`
   - `oss-paper-ci list-checks`
   - `oss-paper-ci scan tests/fixtures/realistic_ml_repo`
   - `oss-paper-ci graph tests/fixtures/realistic_ml_repo`
   - `oss-paper-ci baseline create`
   - `oss-paper-ci smoke --dry-run`
   - `python -m pytest`

## Usage

```bash
python scripts/verify_clean_package.py --zip release-artifacts/oss-paper-ci-v1.0.0rc1-github-clean.zip
```

Options:
- `--keep-temp` — Keep the temporary directory after verification
- `--output-dir` — Directory for verification reports (default: release-artifacts)

## Output

- `release-artifacts/CLEAN_ROOM_VERIFY.md` — Human-readable report
- `release-artifacts/clean-room-result.json` — Machine-readable result

## When to Run

- Before every release
- After significant changes
- In CI to catch packaging issues
