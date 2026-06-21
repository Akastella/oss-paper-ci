# Reproduction Plan

**Project:** repro-system-demo
**Type:** ml
**Schema:** 0.2
**Generated:** 2026-06-21T01:29:27Z

## Environment

- **Type:** python
- **Python:** >=3.10

## Safety Constraints

- **Network:** blocked
- **Shell:** blocked
- **Max runtime:** 120s
- **Max artifact size:** 10 MB

## Execution Steps

| # | ID | Command | Timeout | Dependencies | Artifacts | Status |
|---|-----|---------|---------|--------------|-----------|--------|
| 1 | `train` | `python scripts/train.py` | 30s | — | results/model.json, results/train_metrics.json | ✅ safe |
| 2 | `evaluate` | `python scripts/evaluate.py` | 30s | train | results/metrics.json | ✅ safe |
| 3 | `make_figures` | `python scripts/make_figures.py` | 30s | evaluate | figures/summary.txt | ✅ safe |

**Total timeout:** 90s

## Expected Artifacts

| Path | Type |
|------|------|
| `results/model.json` | file |
| `results/metrics.json` | metrics |
| `figures/summary.txt` | figure-placeholder |

## Expected Metrics

| File | Key | Min | Max |
|------|-----|-----|-----|
| `results/metrics.json` | `accuracy` | 0.0 | 1.0 |
| `results/metrics.json` | `loss` | 0.0 | — |

---

*This plan describes declared reproduction steps. It does not execute code or verify scientific correctness.*