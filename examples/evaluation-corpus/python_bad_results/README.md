# Synthetic Test Fixture: Python Bad Results

**This is a synthetic test repository for oss-paper-ci evaluation. It is NOT a real project.**

## Overview

This fixture simulates a Python project with an invalid results file (malformed JSON). It should be flagged by oss-paper-ci as having critical issues.

## Project Structure

- `scripts/train.py` - Model training script
- `scripts/evaluate.py` - Model evaluation script
- `data/README.md` - Data documentation
- `results/metrics.json` - Experiment results (INVALID JSON)
- `requirements.txt` - Python dependencies

## Known Issues

- `results/metrics.json` contains invalid JSON (missing closing brace)

## License

MIT License - see [LICENSE](LICENSE)
