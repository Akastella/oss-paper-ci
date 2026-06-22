# Repository Intake Report

**Tool:** oss-paper-ci 3.2.0rc1
**Schema:** 0.1

## Source

- **Input:** `tests/fixtures/intake_python_repo`
- **Kind:** local
- **Cloned:** no

## Detected Information

**Languages:** python

### Ecosystems

- **Python** (native)

### Environment Files

- `requirements.txt`
- `pyproject.toml`

### Scripts

- `scripts\evaluate.py`
- `scripts\train.py`

### Data Paths

- `data/`

### Result Paths

- `results/`

## Command Candidates

Found **5** candidate command(s).

| ID | Kind | Command | Source | Confidence |
|-----|------|---------|--------|------------|
| install | install | `pip install -r requirements.txt` | README.md:7 | 0.70 |
| train | train | `python scripts/train.py --epochs 10` | README.md:13 | 0.70 |
| evaluate | evaluate | `python scripts/evaluate.py --data data/test.csv` | README.md:19 | 0.70 |
| cmd | unknown | `train` | pyproject.toml:7 | 0.50 |
| cmd_2 | unknown | `evaluate` | pyproject.toml:8 | 0.50 |

## Confidence Scores

| Dimension | Score |
|-----------|-------|
| overall | 0.87 |
| environment | 1.00 |
| commands | 0.90 |
| artifacts | 0.70 |
| metrics | 0.70 |

## Limitations

- Intake analysis is read-only; no commands are executed.
- Command candidates are inferred from documentation and config files.
- Confidence scores indicate detection quality, not correctness.
- Review all candidates before using them in a reproducibility plan.
- Paper URLs are recognized but not fetched; provide a repository path.
