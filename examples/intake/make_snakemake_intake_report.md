# Repository Intake Report

**Tool:** oss-paper-ci 3.2.0rc1
**Schema:** 0.1

## Source

- **Input:** `tests/fixtures/intake_make_repo`
- **Kind:** local
- **Cloned:** no

## Detected Information

**Languages:** python, cpp, make, snakemake

### Ecosystems

- **Python** (native)
- **C/C++** (execute-if-runtime-present)
- **Make** (execute-if-runtime-present)
- **Snakemake** (dry-run)

### Workflow Files

- `Makefile`
- `Snakefile`

### Scripts

- `scripts\evaluate.py`
- `scripts\make_figures.py`
- `scripts\train.py`

## Command Candidates

Found **7** candidate command(s).

| ID | Kind | Command | Source | Confidence |
|-----|------|---------|--------|------------|
| cmd | unknown | `make all` | README.md:5 | 0.70 |
| cmd_2 | unknown | `make reproduce` | README.md:11 | 0.70 |
| train_2 | train | `make train` | Makefile:5 | 0.60 |
| evaluate | evaluate | `make evaluate` | Makefile:8 | 0.60 |
| figure | figure | `make figures` | Makefile:11 | 0.60 |
| train_4 | train | `snakemake --cores 1 train` | Snakefile:6 | 0.50 |
| train_5 | train | `snakemake --cores 1 figures` | Snakefile:12 | 0.50 |

## Confidence Scores

| Dimension | Score |
|-----------|-------|
| overall | 0.60 |
| environment | 0.70 |
| commands | 0.90 |
| artifacts | 0.10 |
| metrics | 0.10 |

## Limitations

- Intake analysis is read-only; no commands are executed.
- Command candidates are inferred from documentation and config files.
- Confidence scores indicate detection quality, not correctness.
- Review all candidates before using them in a reproducibility plan.
- Paper URLs are recognized but not fetched; provide a repository path.
