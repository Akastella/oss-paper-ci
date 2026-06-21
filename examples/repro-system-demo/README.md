# Reproduction System Demo

A minimal, self-contained demo repository for testing the reproduction orchestrator.

## What this does

This demo simulates a simple ML pipeline:
1. **train** — generates a model and training metrics
2. **evaluate** — generates evaluation metrics
3. **make_figures** — generates a text-based summary

All scripts use only the Python standard library. No external dependencies, no network access, no data downloads. Completes in under 1 second.

## How to reproduce

```bash
# Plan only (never executes code)
oss-paper-ci reproduce plan .

# Execute with safety gates
oss-paper-ci reproduce run . --execute --sandbox local

# Generate report
oss-paper-ci reproduce report .oss-paper-ci-repro-run --format html --output reproduction.html

# Compare against expected values
oss-paper-ci reproduce compare .oss-paper-ci-repro-run --expected reproducibility.yml

# Create evidence bundle
oss-paper-ci reproduce bundle .oss-paper-ci-repro-run --output reproduction-evidence.zip
```

## Safety

- All scripts are deterministic (seed=42)
- No network access required
- No external data dependencies
- No dangerous commands
- Completes in under 1 second
- All artifacts are small text files

## Files

- `reproducibility.yml` — reproduction contract (schema v0.2)
- `scripts/train.py` — training script
- `scripts/evaluate.py` — evaluation script
- `scripts/make_figures.py` — figure generation script
- `results/` — output directory for metrics and model
- `figures/` — output directory for figures
- `data/` — data directory (empty, no external data needed)
