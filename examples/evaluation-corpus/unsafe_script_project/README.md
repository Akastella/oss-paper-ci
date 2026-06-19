# Synthetic Test Fixture: Unsafe Script Project

**This is a synthetic test repository for oss-paper-ci evaluation. It is NOT a real project.**

**WARNING: This fixture contains intentionally risky patterns for testing dry-run detection. DO NOT EXECUTE any scripts in this repository.**

## Overview

This fixture simulates a project with potentially unsafe scripts. It is designed to test oss-paper-ci's ability to detect risky patterns without executing them.

## Project Structure

- `scripts/download_and_run.sh` - Contains `curl | bash` pattern (TEXT ONLY)
- `scripts/unsafe_eval.py` - Contains `eval()` usage (TEXT ONLY)
- `requirements.txt` - Python dependencies
- `data/README.md` - Data documentation

## Safety Notice

This repository is a **test fixture only**. The scripts contain patterns that should be flagged as risky:

1. `curl | bash` - Downloads and executes remote code
2. `eval()` - Dynamic code execution

These patterns are included as text for testing oss-paper-ci's detection capabilities. They should NEVER be executed.

## License

MIT License - see [LICENSE](LICENSE)
